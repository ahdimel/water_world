"""Bureau of Reclamation reservoir storage — the physical state of the Colorado system.

USBR's Upper Colorado hydrodata service publishes daily end-of-period storage per
reservoir as plain CSV, no key required:

    https://www.usbr.gov/uc/water/hydrodata/reservoir_data/<site_id>/csv/17.csv

Datatype 17 is "storage, end of period reading", in acre-feet. Site ids below were
resolved against the service's own ``meta.csv`` catalogue rather than guessed.

Together these nine reservoirs are effectively the entire storage capacity of the
Colorado River system; Powell and Mead alone hold the large majority of it.
"""

from __future__ import annotations

import csv
import io
from datetime import date

from ww.schemas import SourceSpec, Timeseries, TimeseriesPoint
from ww.sources.base import SimpleSource

STORAGE_DATATYPE = 17

#: site_id -> human label, verified against the USBR hydrodata meta.csv catalogue.
RESERVOIRS: dict[int, str] = {
    913: "Blue Mesa Reservoir",
    914: "Morrow Point Reservoir",
    915: "Crystal Reservoir",
    916: "Fontenelle Reservoir",
    917: "Flaming Gorge Reservoir",
    919: "Lake Powell",
    920: "Navajo Reservoir",
    921: "Lake Mead",
    922: "Lake Mohave",
    923: "Lake Havasu",
}

#: The two that carry the story: ~90% of system storage between them.
HEADLINE = (919, 921)


def _slug(label: str) -> str:
    return label.lower().replace(" reservoir", "").replace(" ", "_")


def _url(site_id: int) -> str:
    return (
        "https://www.usbr.gov/uc/water/hydrodata/reservoir_data/"
        f"{site_id}/csv/{STORAGE_DATATYPE}.csv"
    )


def parse_storage_csv(raw: bytes, source_id: str, label: str) -> list[Timeseries]:
    """Parse USBR's two-column ``datetime,storage`` CSV into a normalised series.

    Blank and unparseable rows are skipped rather than raising: the historical tail of
    these files contains occasional gaps, and one bad row should not cost us 63 years
    of daily observations.
    """
    text = raw.decode("utf-8", errors="replace")
    reader = csv.DictReader(io.StringIO(text))
    points: list[TimeseriesPoint] = []
    for row in reader:
        stamp, value = row.get("datetime"), row.get("storage")
        if not stamp or value in (None, "", "NaN"):
            continue
        try:
            points.append(
                TimeseriesPoint(when=date.fromisoformat(stamp.strip()[:10]), value=float(value))
            )
        except (ValueError, TypeError):
            continue
    return [Timeseries(source_id=source_id, label=label, units="acre-feet", points=points)]


def _make(site_id: int, label: str) -> SimpleSource:
    source_id = f"usbr.reservoir.{_slug(label)}"
    spec = SourceSpec(
        id=source_id,
        title=f"{label} — daily end-of-period storage (USBR hydrodata)",
        tier="api",
        url=_url(site_id),
        units="acre-feet",
        cadence="daily",
        notes=f"USBR Upper Colorado hydrodata site {site_id}, datatype {STORAGE_DATATYPE}.",
    )
    return SimpleSource(spec, lambda raw: parse_storage_csv(raw, source_id, label))


def build() -> list[SimpleSource]:
    """All reservoir sources, headline reservoirs first."""
    ordered = sorted(RESERVOIRS.items(), key=lambda kv: (kv[0] not in HEADLINE, kv[1]))
    return [_make(site_id, label) for site_id, label in ordered]
