"""CAISO OASIS locational marginal prices at SP15 — input to the flexibility question.

Phase 0.5 left the SWRO flexible-operation question genuinely open: the storage-medium
argument favours it (a water tank beats a battery roughly 6:1 per unit of energy shifted)
while the whole-system argument opposes it (idling strands capital-intensive RO trains).
Resolving that needs a real price-duration curve, not an assumed spread — which is what
this source provides.

SP15 is the Southern California trading hub, and is where Phase 0 found negative midday
prices concentrating as solar builds out.

OASIS quirks worth knowing:

* Responses are ZIP archives containing one CSV, even for a single day.
* The window is capped at 31 days per query, so long histories must be chunked.
* The price lives in the ``MW`` column — an OASIS naming artefact, not a typo here.
  Units are $/MWh.
* ``LMP_TYPE`` splits the price into components; ``LMP`` is the total, and the others
  (``MCC`` congestion, ``MCE`` energy, ``MCL`` loss, ``MGHG`` GHG) sum into it.
"""

from __future__ import annotations

import csv
import io
import zipfile
from datetime import datetime

from ww.schemas import SourceSpec, Timeseries, TimeseriesPoint
from ww.sources.base import SimpleSource

OASIS_URL = "https://oasis.caiso.com/oasisapi/SingleZip"

#: Southern California trading hub. The Phase 0 curtailment and negative-price evidence
#: is specific to SP15, so the model should not silently use a different hub.
SP15_NODE = "TH_SP15_GEN-APND"

#: Day-ahead market. Real-time (RTM) is noisier and a plant scheduling around a
#: reservoir buys day-ahead, so DAM is the right default.
DEFAULT_MARKET = "DAM"

MAX_DAYS_PER_QUERY = 31


def _stamp(d: datetime) -> str:
    """OASIS wants compact GMT timestamps: YYYYMMDDTHH:MM-0000."""
    return d.strftime("%Y%m%dT%H:%M-0000")


def build_url(
    start: datetime,
    end: datetime,
    *,
    node: str = SP15_NODE,
    market: str = DEFAULT_MARKET,
) -> str:
    span_days = (end - start).days
    if span_days > MAX_DAYS_PER_QUERY:
        raise ValueError(
            f"OASIS caps queries at {MAX_DAYS_PER_QUERY} days; got {span_days}. "
            "Chunk the range and register one source per chunk."
        )
    params = (
        f"?queryname=PRC_LMP&startdatetime={_stamp(start)}&enddatetime={_stamp(end)}"
        f"&version=12&market_run_id={market}&node={node}&resultformat=6"
    )
    return OASIS_URL + params


def parse_lmp_zip(
    raw: bytes, source_id: str, label: str, lmp_type: str = "LMP"
) -> list[Timeseries]:
    """Extract the total LMP series from an OASIS ZIP payload.

    Returns a single series filtered to `lmp_type`, sorted ascending by interval start.
    """
    with zipfile.ZipFile(io.BytesIO(raw)) as zf:
        names = [n for n in zf.namelist() if n.lower().endswith(".csv")]
        if not names:
            raise ValueError(f"OASIS payload for {source_id} contained no CSV")
        text = zf.read(names[0]).decode("utf-8", errors="replace")

    points: list[TimeseriesPoint] = []
    for row in csv.DictReader(io.StringIO(text)):
        if row.get("LMP_TYPE") != lmp_type:
            continue
        stamp, price = row.get("INTERVALSTARTTIME_GMT"), row.get("MW")
        if not stamp or price in (None, ""):
            continue
        try:
            points.append(
                TimeseriesPoint(when=datetime.fromisoformat(stamp), value=float(price))
            )
        except (ValueError, TypeError):
            continue
    points.sort(key=lambda p: p.when)
    return [
        Timeseries(source_id=source_id, label=label, units="USD/MWh", points=points)
    ]


def make_window(
    start: datetime,
    end: datetime,
    *,
    node: str = SP15_NODE,
    market: str = DEFAULT_MARKET,
) -> SimpleSource:
    """One cacheable source covering a single OASIS-legal window."""
    source_id = f"caiso.lmp.{market.lower()}.{start:%Y%m%d}_{end:%Y%m%d}"
    label = f"CAISO {market} LMP at {node}"
    spec = SourceSpec(
        id=source_id,
        title=f"{label}, {start:%Y-%m-%d} to {end:%Y-%m-%d}",
        tier="api",
        url=build_url(start, end, node=node, market=market),
        units="USD/MWh",
        cadence="hourly",
        notes=(
            "CAISO OASIS SingleZip. Returns a ZIP-wrapped CSV; price is in the MW column. "
            f"Windows capped at {MAX_DAYS_PER_QUERY} days. Throttled — fetch politely."
        ),
    )
    return SimpleSource(spec, lambda raw: parse_lmp_zip(raw, source_id, label))


def build() -> list[SimpleSource]:
    """No windows are pre-registered.

    A price-duration curve needs a full year, which is ~12 chunked queries against a
    throttled endpoint — a Phase 2 decision about how much history to pull, not
    something Phase 1 should trigger on every `fetch --all`. Construct windows
    explicitly with :func:`make_window`.
    """
    return []
