"""Phase 3 — the supply stack, and the framing gate.

Every way Southern California could find the water California is about to lose, on one
$/AF axis, with uncertainty bands and quantities. The ranking that comes out of this
module decides which argument the paper makes (REQUIREMENTS.md §3). That is why the
decision rule below was written BEFORE the stack was first run, and is pinned by tests.

**Common basis.** Every option is priced:

* in **2025 dollars** (`deflate`),
* **delivered treated into the regional system** — Colorado River water left in the
  river at Palo Verde or Imperial is charged the cost of getting it to the coast
  (`conveyance.colorado_to_coast`); desal, reuse, stormwater and conservation already
  sit inside the urban system,
* with capital on **public finance**, 100% debt at 4% over 30 years — Metropolitan's
  own convention for Pure Water — so that financing structure does not decide the
  ranking. The as-built private Carlsbad deal is reported alongside, off the stack.

**Options.** Urban conservation (landscape-led), stormwater capture, paid ag
conservation (with the Salton Sea dust bill on its Imperial share), potable reuse at
Pure Water Southern California's published cost, and seawater desalination in three
forms: as Carlsbad cost on public finance, with permitting reformed, and at Israeli
capex scaled to Carlsbad's size (Act III's counterfactual). Brackish desal is costed
in the literature file but kept off the stack: it is inland and its quantity was not
assessed.

**The framing gate — the rule, fixed before the first run.**

Let *R* be paid ag reallocation delivered to the coast with the dust bill mitigated,
and *D* the reformed-procurement desal point (Israeli capex at Carlsbad's scale, the
most favourable case for desal the project defines). Let *T* = California's cut.

* **Row 1, "reallocation dominates, hard ceiling"** — P(R < D) >= 0.9 and
  P(ag capacity >= T) >= 0.5.
* **Row 2, "reallocation cheap but tightly capped"** — P(R < D) >= 0.9 and
  P(ag capacity >= T) < 0.5.
* **Row 3, "bands overlap"** — P(R < D) < 0.9.

**Added after the first run, and only as a disclosure:** when P(ag capacity >= T) lands
within `UNDECIDED_BAND` of 0.5, the gate says rows 1 and 2 are not separable rather than
reporting whichever side Monte Carlo noise fell on. At T = 440,000 AF it does exactly
that: the exact probability is 0.5007 (row 1 by 0.0007, inside the noise). The
thresholds themselves are unchanged.

The gate is reported against the permitting-only reform as well, because "Israeli
cost" is an aspiration California has not shown it can reach, and a ranking that only
holds against the aspiration is a weaker claim than one that holds against the reform
on offer.
"""

from __future__ import annotations

import math
import random
from collections.abc import Callable
from dataclasses import dataclass, replace

from ww import params
from ww.model import deflate, lcow, montecarlo, permitting, plants, salton, scale
from ww.model.finance import FinanceSpec

GATE_PROBABILITY = 0.9
CAPACITY_PROBABILITY = 0.5
UNDECIDED_BAND = 0.05

Sampler = Callable[[random.Random | None], float]


def _real(pid: str, rng: random.Random | None) -> float:
    """A dollar parameter, sampled (or central if rng is None), in 2025 dollars."""
    v = params.value(pid) if rng is None else montecarlo.sample(pid, rng)
    return v * deflate.factor(params.get(pid).year)


def _qty(pid: str, rng: random.Random | None) -> float:
    return params.value(pid) if rng is None else montecarlo.sample(pid, rng)


# --------------------------------------------------------------------------------------
# Desalination on the common basis
# --------------------------------------------------------------------------------------


def public_finance(rng: random.Random | None = None) -> FinanceSpec:
    """100% debt, Metropolitan's 4% / 30-year convention."""
    rate = params.value("finance.public.rate") if rng is None else montecarlo.sample(
        "finance.public.rate", rng
    )
    term = params.value("finance.public.term")
    return FinanceSpec(
        gearing=1.0, cost_of_debt=rate, cost_of_equity=rate,
        debt_tenor_years=term, asset_life_years=term,
    )


def _carlsbad(rng: random.Random | None) -> lcow.PlantSpec:
    spec = plants.carlsbad()
    if rng is None:
        return spec
    return replace(
        spec,
        sec_kwh_m3=montecarlo.sample("swro.sec", rng),
        energy_price_usd_kwh=_real("energy.price_industrial_ca", rng),
        om_nonenergy_usd_m3=_real("swro.om_nonenergy", rng),
    )


def desal_as_built(rng: random.Random | None = None) -> float:
    """Carlsbad as financed (private, 80.9% geared), 2025 dollars, full output.
    OFF the stack: reported to show what the financing structure alone is worth."""
    fin = plants.carlsbad_finance()
    if rng is not None:
        fin = replace(fin, cost_of_equity=montecarlo.sample("finance.cost_of_equity", rng))
    return lcow.lcow(_carlsbad(rng), fin).total_usd_af


def desal_public(rng: random.Random | None = None) -> float:
    """Carlsbad's capex and pipeline, on public finance."""
    return lcow.lcow(_carlsbad(rng), public_finance(rng)).total_usd_af


def _permitting_ratio(rng: random.Random | None) -> float:
    if rng is None:
        before = permitting.california_regime()
    else:
        before = permitting.california_regime(1.0 - permitting.denial_rate_posterior(rng))
    after = permitting.reformed_regime()
    return permitting.risk_multiplier(after) / permitting.risk_multiplier(before)


def desal_permit_reform(rng: random.Random | None = None) -> float:
    """Carlsbad with priced permitting risk moved to the reformed regime, public finance.
    The reform actually on offer; it leaves the ~3x unexplained residual in place."""
    spec = _carlsbad(rng)
    spec = replace(spec, capex_usd=spec.capex_usd * _permitting_ratio(rng))
    return lcow.lcow(spec, public_finance(rng)).total_usd_af


def desal_israeli(rng: random.Random | None = None) -> float:
    """Act III's counterfactual: Sorek's capex scaled to Carlsbad's size, built in
    California — Californian power, O&M and Carlsbad's pipeline — on public finance."""
    cb = _carlsbad(rng)
    sk = plants.sorek()
    exponent = (
        params.value("econ.capex_scaling_exponent")
        if rng is None
        else montecarlo.sample("econ.capex_scaling_exponent", rng)
    )
    capex = scale.scale_capex(sk.capex_usd, sk.capacity_m3_day, cb.capacity_m3_day, exponent)
    return lcow.lcow(replace(cb, capex_usd=capex), public_finance(rng)).total_usd_af


# --------------------------------------------------------------------------------------
# The other options
# --------------------------------------------------------------------------------------


def ag_direct(rng: random.Random | None = None) -> float:
    """What the farm district is paid, at the river."""
    return _real("ag.conservation_price", rng)


def ag_at_coast(rng: random.Random | None = None) -> float:
    """Paid ag water delivered treated to a coastal city — no dust bill."""
    return ag_direct(rng) + _real("conveyance.colorado_to_coast", rng)


def ag_reallocation(rng: random.Random | None = None) -> float:
    """R: delivered, with mitigated dust cost on the Imperial share."""
    share = _qty("ag.iid_share_of_conservation", rng)
    return ag_at_coast(rng) + share * salton.mitigation_externality(rng)


def ag_unmitigated(rng: random.Random | None = None) -> float:
    """Stress case: R if the state never builds the dust mitigation."""
    share = _qty("ag.iid_share_of_conservation", rng)
    return ag_at_coast(rng) + share * salton.damage_externality(rng)


def conservation(rng: random.Random | None = None) -> float:
    return _real("conservation.cost", rng)


def stormwater(rng: random.Random | None = None) -> float:
    return _real("stormwater.cost", rng)


def reuse(rng: random.Random | None = None) -> float:
    return _real("reuse.pwsc.unit_cost", rng)


def imported_reference(rng: random.Random | None = None) -> float:  # noqa: ARG001
    """Metropolitan's treated full-service rate: the water being cut. Reference only."""
    return deflate.real("mwd.rate.full_service_treated_2026")


# --------------------------------------------------------------------------------------
# Options
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Option:
    key: str
    label: str
    cost: Sampler
    quantity: Sampler
    on_stack: bool = True

    def unbounded(self) -> bool:
        return math.isinf(self.quantity(None))


def _inf(rng: random.Random | None) -> float:  # noqa: ARG001
    return math.inf


OPTIONS: dict[str, Option] = {
    o.key: o
    for o in (
        Option("conservation", "Urban conservation (landscape-led)", conservation,
               lambda r: _qty("conservation.quantity_socal", r)),
        Option("stormwater", "Stormwater capture", stormwater,
               lambda r: _qty("stormwater.quantity_socal", r)),
        Option("ag", "Paying farmers, delivered to the coast", ag_reallocation,
               lambda r: _qty("ag.conservation_capacity", r)),
        Option("desal_israeli", "Desal at Israeli cost (counterfactual)", desal_israeli, _inf),
        Option("desal_permit_reform", "Desal, permitting reformed", desal_permit_reform, _inf),
        Option("desal_public", "Desal at Carlsbad cost, public finance", desal_public, _inf),
        Option("reuse", "Potable reuse (Pure Water SoCal)", reuse,
               lambda r: _qty("reuse.pwsc.yield", r)),
        Option("ag_unmitigated", "Paying farmers, if the dust is never controlled",
               ag_unmitigated, lambda r: _qty("ag.conservation_capacity", r), on_stack=False),
        Option("desal_as_built", "Desal as built (Carlsbad, private finance)",
               desal_as_built, _inf, on_stack=False),
        Option("imported", "Imported water today (Metropolitan treated rate)",
               imported_reference, _inf, on_stack=False),
    )
}

#: Which desal variant stands in for "the desal the region can actually buy" in each
#: stack scenario. The status quo is Carlsbad cost on public finance.
DESAL_VARIANTS = ("desal_public", "desal_permit_reform", "desal_israeli")


# --------------------------------------------------------------------------------------
# Simulation
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Draw:
    """One draw of every option's cost and quantity.

    Options are drawn INDEPENDENTLY: each gets its own child-seeded rng, so an input
    two options share (the CA power price, the public rate) is drawn separately for
    each. Paid ag water and desal share no inputs, so the gate is unaffected; between
    desal variants it widens their overlap, which is the conservative direction."""

    cost: dict[str, float]
    quantity: dict[str, float]


def draw(rng: random.Random) -> Draw:
    # A fresh child seed per option keeps every option's draws reproducible even if
    # another option's sampler changes how many numbers it consumes.
    seeds = {k: rng.random() for k in OPTIONS}
    cost, qty = {}, {}
    for k, o in OPTIONS.items():
        r = random.Random(seeds[k])
        cost[k] = o.cost(r)
        qty[k] = o.quantity(r)
    return Draw(cost, qty)


def simulate(n: int = 10_000, seed: int = 20261028) -> list[Draw]:
    rng = random.Random(seed)
    return [draw(rng) for _ in range(n)]


def distribution(draws: list[Draw], key: str) -> montecarlo.Distribution:
    return montecarlo.Distribution(name=OPTIONS[key].label, values=[d.cost[key] for d in draws])


def p_cheaper(draws: list[Draw], a: str, b: str) -> float:
    """P(cost of a < cost of b), from the joint draws."""
    return sum(d.cost[a] < d.cost[b] for d in draws) / len(draws)


def marginal_cost(d: Draw, target: float, desal: str = "desal_public") -> float:
    """Cost of the last acre-foot needed to cover `target`, buying cheapest first.

    Only on-stack options take part, and only ONE desal variant (the scenario's), since
    the variants are alternative versions of the same plant, not separate supplies."""
    keys = [k for k, o in OPTIONS.items() if o.on_stack and (k == desal or k not in DESAL_VARIANTS)]
    total = 0.0
    for k in sorted(keys, key=lambda k: d.cost[k]):
        total += d.quantity[k]
        if total >= target:
            return d.cost[k]
    return math.inf


@dataclass(frozen=True)
class Gate:
    comparator: str
    p_cheaper: float
    p_capacity: float

    @property
    def row(self) -> int:
        if self.p_cheaper < GATE_PROBABILITY:
            return 3
        return 1 if self.p_capacity >= CAPACITY_PROBABILITY else 2

    @property
    def capacity_decisive(self) -> bool:
        """False when rows 1 and 2 cannot honestly be told apart."""
        return abs(self.p_capacity - CAPACITY_PROBABILITY) >= UNDECIDED_BAND

    @property
    def verdict(self) -> str:
        if self.row != 3 and not self.capacity_decisive:
            return (
                "Reallocation dominates on cost; whether it alone covers the cut is a "
                "coin flip (rows 1 and 2 not separable)"
            )
        return {
            1: "Reallocation dominates, with a hard ceiling",
            2: "Reallocation is cheap but tightly capped",
            3: "Uncertainty bands overlap substantially",
        }[self.row]


def gate(draws: list[Draw], *, comparator: str = "desal_israeli",
         target: float | None = None) -> Gate:
    """Apply the pre-registered framing-gate rule."""
    t = params.value("ca.colorado_cut") if target is None else target
    cap = sum(d.quantity["ag"] >= t for d in draws) / len(draws)
    return Gate(comparator=comparator, p_cheaper=p_cheaper(draws, "ag", comparator), p_capacity=cap)
