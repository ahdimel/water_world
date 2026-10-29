"""How much of the Salton Sea's dust bill belongs to a transferred acre-foot.

Phase 0.5 costed the externality at ~$140-255/AF by dividing the state's dust and
habitat programme by the QSA transfer volume. That carried three assumptions, each of
which pushes the number UP, and this module prices each one instead of assuming it:

1. **All of the Sea's decline is the transfer's.** It is not. The LAO projects inflow
   falling from ~1.25 MAF to ~0.75 MAF "due to both the QSA transfers and longer-term
   reduction trends". The transfer is ~303,000 AF of a ~500,000 AF decline.
2. **All restoration spend is dust spend.** The programme builds combined habitat and
   dust-suppression projects; the split is not published.
3. **It applies to fallowing in general.** It applies only to the Imperial Valley,
   which drains to the Sea. Palo Verde drains back to the Colorado River. Phase 0.5
   attached the Imperial externality to Palo Verde's price.

One assumption Phase 2 flagged turns out NOT to cut the number: IID's ~2012 shift from
fallowing to on-farm efficiency. Efficiency cuts tailwater and drain flow just as
fallowing does, so the conserved water still never reaches the Sea.

Two bases are kept apart, deliberately:

* **Mitigation** (central): what it costs to suppress the dust. The right price for a
  transferred acre-foot IF the state builds what it is legally on the hook for.
* **Damage** (stress case): the Pacific Institute's cost of inaction. The right price if
  it does not. Mitigation is far cheaper, which is the whole argument for building it —
  and the reason the reallocation story hinges on whether California keeps that promise.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from ww import params
from ww.model import deflate, montecarlo

#: Years of damage in the Pacific Institute's cost-of-inaction estimate.
DAMAGE_HORIZON_YEARS = 30.0


def qsa_share(rng: random.Random | None = None) -> float:
    """Fraction of the Sea's inflow decline attributable to the QSA transfers."""
    if rng is None:
        before = params.value("salton.inflow_2003")
        after = params.value("salton.inflow_post2020")
        transfer = params.value("salton.qsa_transfer_volume")
    else:
        before = montecarlo.sample("salton.inflow_2003", rng)
        after = montecarlo.sample("salton.inflow_post2020", rng)
        transfer = montecarlo.sample("salton.qsa_transfer_volume", rng)
    return min(1.0, transfer / (before - after))


def _draw(pid: str, rng: random.Random | None) -> float:
    return params.value(pid) if rng is None else montecarlo.sample(pid, rng)


def mitigation_externality(
    rng: random.Random | None = None, *, year: int = deflate.BASE_YEAR
) -> float:
    """Dust mitigation cost per Imperial acre-foot transferred, in `year` dollars."""
    full = _draw("salton.externality", rng)
    dust = _draw("salton.dust_share_of_spend", rng)
    value = full * qsa_share(rng) * dust
    return value * deflate.factor(params.get("salton.externality").year, year)


def damage_externality(
    rng: random.Random | None = None, *, year: int = deflate.BASE_YEAR
) -> float:
    """Unmitigated damage per Imperial acre-foot transferred, in `year` dollars."""
    damage = _draw("salton.damage_noaction", rng)
    transfer = params.value("salton.qsa_transfer_volume")
    value = damage / DAMAGE_HORIZON_YEARS * qsa_share(rng) / transfer
    return value * deflate.factor(params.get("salton.damage_noaction").year, year)


@dataclass(frozen=True)
class Attribution:
    """The Phase 0.5 figure next to what survives each correction, $/AF, 2025 dollars."""

    full_attribution: float
    after_qsa_share: float
    after_dust_share: float
    per_blended_ag_af: float
    damage_basis: float


def walk() -> Attribution:
    """Point estimates, one correction at a time — the chart the paper needs."""
    f = deflate.factor(params.get("salton.externality").year)
    full = params.value("salton.externality") * f
    after_share = full * qsa_share()
    after_dust = after_share * params.value("salton.dust_share_of_spend")
    return Attribution(
        full_attribution=full,
        after_qsa_share=after_share,
        after_dust_share=after_dust,
        per_blended_ag_af=after_dust * params.value("ag.iid_share_of_conservation"),
        damage_basis=damage_externality(),
    )
