"""BLS Consumer Price Index — the deflator behind Act I.

Act I claims water got more expensive in *real* terms for households while agricultural
water stayed nominally flat. That needs two CPI series:

* ``CUUR0000SEHG`` — water, sewer and trash collection services
* ``CUUR0000SA0``  — all items (the deflator)

Two access routes exist and we deliberately take the second:

1. ``download.bls.gov`` flat files carry full history in one GET, but BLS rejects the
   request unless the User-Agent contains a contact email address. We do not put the
   owner's email into third-party request headers by default, so this route is opt-in
   via the ``WW_CONTACT_EMAIL`` environment variable.
2. The **public API v2 without registration** accepts POST queries of up to ten years.
   No key, no email. We chunk by decade and stitch. Unregistered callers get 25 queries
   a day, and one decade of both series costs a single query, so a full rebuild of
   1990-present costs four.

Route 2 is the default precisely because it needs no personal data.
"""

from __future__ import annotations

import json
import os
from datetime import date

from ww.schemas import SourceSpec, Timeseries, TimeseriesPoint
from ww.sources.base import SimpleSource

API_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"

FLATFILE_URL_TEMPLATE = "https://download.bls.gov/pub/time.series/cu/{file}"

#: series id -> (label, units)
SERIES: dict[str, tuple[str, str]] = {
    "CUUR0000SEHG": ("CPI: water, sewer & trash collection services", "index 1982-84=100"),
    "CUUR0000SA0": ("CPI: all items", "index 1982-84=100"),
}

#: Decade chunks. The API caps unregistered queries at ten years each.
DECADES: tuple[tuple[int, int], ...] = (
    (1990, 1999),
    (2000, 2009),
    (2010, 2019),
    (2020, 2029),
)

#: Month code -> month number. BLS uses M01..M12, plus M13 for annual averages
#: which we drop: mixing an annual average into a monthly series corrupts the shape.
_MONTHS = {f"M{i:02d}": i for i in range(1, 13)}


def parse_api_json(raw: bytes) -> list[Timeseries]:
    """Parse a BLS v2 API response into one Timeseries per series id returned.

    Observations are dated to the first of their month. BLS returns newest-first; we
    sort ascending because every consumer downstream assumes chronological order.
    """
    doc = json.loads(raw.decode("utf-8"))
    status = doc.get("status")
    if status != "REQUEST_SUCCEEDED":
        msg = "; ".join(doc.get("message") or []) or status
        raise ValueError(f"BLS request did not succeed: {msg}")

    out: list[Timeseries] = []
    for series in doc.get("Results", {}).get("series", []):
        sid = series["seriesID"]
        label, units = SERIES.get(sid, (sid, "index"))
        points: list[TimeseriesPoint] = []
        for row in series.get("data", []):
            month = _MONTHS.get(row.get("period", ""))
            if month is None:
                continue
            try:
                points.append(
                    TimeseriesPoint(
                        when=date(int(row["year"]), month, 1), value=float(row["value"])
                    )
                )
            except (ValueError, KeyError, TypeError):
                continue
        points.sort(key=lambda p: p.when)
        out.append(
            Timeseries(source_id=f"bls.cpi.{sid}", label=label, units=units, points=points)
        )
    return out


def _make_decade(start: int, end: int) -> SimpleSource:
    spec = SourceSpec(
        id=f"bls.cpi.{start}s",
        title=f"BLS CPI {start}-{end}: water/sewer/trash and all-items",
        tier="api",
        url=API_URL,
        units="index 1982-84=100",
        cadence="monthly",
        post_json={
            "seriesid": list(SERIES),
            "startyear": str(start),
            "endyear": str(end),
        },
        notes=(
            "Unregistered BLS API v2 POST. Ten-year cap per query, 25 queries/day. "
            "Requires no API key and no contact email."
        ),
    )
    return SimpleSource(spec, parse_api_json)


def build() -> list[SimpleSource]:
    return [_make_decade(a, b) for a, b in DECADES]


def flatfile_spec(file: str = "cu.data.1.AllItems") -> SourceSpec:
    """Opt-in full-history route. Requires ``WW_CONTACT_EMAIL`` to be set.

    BLS returns 403 to requests whose User-Agent lacks a contact address, so this
    source only becomes usable when the operator supplies one explicitly. It is not
    part of the default registry.
    """
    email = os.environ.get("WW_CONTACT_EMAIL")
    if not email:
        raise RuntimeError(
            "BLS flat files require a contact email in the User-Agent. "
            "Set WW_CONTACT_EMAIL to opt in, or use the default bls.cpi.* API sources, "
            "which need no personal data."
        )
    return SourceSpec(
        id=f"bls.flatfile.{file}",
        title=f"BLS CPI flat file {file} (full history)",
        tier="file",
        url=FLATFILE_URL_TEMPLATE.format(file=file),
        units="index 1982-84=100",
        cadence="monthly",
        notes=f"Opt-in; identifies the caller as {email} to BLS.",
    )


def stitch(chunks: list[list[Timeseries]], series_id: str) -> Timeseries:
    """Merge decade chunks into one continuous series for `series_id`.

    Later chunks win on overlapping dates, which matters because BLS revises recent
    months. Raises if the series is absent from every chunk rather than returning an
    empty series, since a silent empty deflator would corrupt Act I quietly.
    """
    target = f"bls.cpi.{series_id}"
    merged: dict[date, float] = {}
    label = units = None
    for chunk in chunks:
        for ts in chunk:
            if ts.source_id != target:
                continue
            label, units = ts.label, ts.units
            for p in ts.points:
                merged[p.when] = p.value
    if label is None or units is None:
        raise KeyError(f"series {series_id!r} not present in any cached BLS chunk")
    points = [TimeseriesPoint(when=w, value=v) for w, v in sorted(merged.items())]
    return Timeseries(source_id=target, label=label, units=units, points=points)
