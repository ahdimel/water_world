"""The source registry — a complete inventory of what the analysis rests on.

Manual-tier entries are listed deliberately. Several load-bearing numbers in this project
(desalination capex, irrigation district tariffs, Salton Sea programme costs) exist only
in PDFs, rate schedules, or paywalled databases. Recording them here — rather than
quietly hardcoding the figures — keeps the registry an honest map of provenance, and
each one points at the ``data/parameters/literature.yaml`` entry that carries its value
and citation.
"""

from __future__ import annotations

from ww.schemas import SourceSpec
from ww.sources import bls, caiso, usbr
from ww.sources.base import ManualSource, Source

# --------------------------------------------------------------------------------------
# Manual sources — declared so the inventory is complete
# --------------------------------------------------------------------------------------

_MANUAL = [
    SourceSpec(
        id="manual.desal.capex",
        title="Desalination plant capital costs (Sorek, Carlsbad, Huntington Beach, Doheny)",
        tier="manual",
        notes=(
            "Plant capex and contracted water prices come from filings, press reporting "
            "and project profiles rather than any dataset. See literature.yaml "
            "desal.* parameters. Commercial databases (GWI/DesalData) are paywalled."
        ),
    ),
    SourceSpec(
        id="manual.rates.ag_vs_urban",
        title="Agricultural vs municipal water tariffs (IID, MWD, SDCWA)",
        tier="manual",
        notes=(
            "District rate schedules are published as PDFs on irregular URLs. "
            "See literature.yaml rates.* parameters."
        ),
    ),
    SourceSpec(
        id="manual.fallowing.pvid",
        title="Palo Verde fallowing programme payments and conserved volumes",
        tier="manual",
        notes="MWD/PVID programme terms. See literature.yaml fallowing.* parameters.",
    ),
    SourceSpec(
        id="manual.salton_sea",
        title="Salton Sea mitigation programme costs and playa exposure",
        tier="manual",
        notes=(
            "California LAO status report and QSA settlement terms. "
            "See literature.yaml salton.* parameters."
        ),
    ),
    SourceSpec(
        id="manual.permitting.ca",
        title="California desalination permitting timelines and outcomes",
        tier="manual",
        notes=(
            "Coastal Commission records and case-study literature. Feeds the "
            "permitting-risk model. See literature.yaml permitting.* parameters."
        ),
    ),
]


def _all_sources() -> list[Source]:
    out: list[Source] = []
    out.extend(usbr.build())
    out.extend(bls.build())
    out.extend(caiso.build())
    out.extend(ManualSource(spec) for spec in _MANUAL)
    return out


#: id -> Source, built once at import.
REGISTRY: dict[str, Source] = {s.spec.id: s for s in _all_sources()}


def get(source_id: str) -> Source:
    try:
        return REGISTRY[source_id]
    except KeyError:
        raise KeyError(
            f"unknown source {source_id!r}. Run `python -m ww sources` to list them."
        ) from None


def fetchable() -> list[Source]:
    """Sources that can actually be pulled over the network."""
    return [s for s in REGISTRY.values() if s.spec.tier != "manual" and not s.spec.requires_key]


def by_tier(tier: str) -> list[Source]:
    return [s for s in REGISTRY.values() if s.spec.tier == tier]


__all__ = ["REGISTRY", "get", "fetchable", "by_tier", "usbr", "bls", "caiso"]
