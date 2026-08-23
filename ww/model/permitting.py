"""Permitting priced as a financial instrument — contribution §2.2.

The mechanism. A developer spends real money to get a project approved, years before
any water is sold, and may lose all of it: Huntington Beach ran from 1998 to a
unanimous denial in 2022 and returned zero on roughly $100M of development spend. That
money has to be earned back by the projects that *do* get built. So a jurisdiction with
long approvals and material rejection risk raises the cost of its own water, without
changing a single thing about the engineering.

The pricing. Development capital `D` is at risk for `T` years and survives with
probability `p`. To break even across the population of attempts, a successful project
must return

    D * (1 + r)**T / p

instead of the `D` it would return under instant, certain approval. The increment,

    D * ((1 + r)**T / p - 1)

is the permitting premium, and it is added to capex before levelising.

`r` is the cost of *equity*, not the blended cost of capital, and deliberately so:
development capital is unsecured, pre-permit and first-loss. No lender funds it.

**This is a lower bound, and must be reported as one.** It prices only the capital of
projects actually attempted. It cannot see the projects never proposed because the
approval risk was obvious in advance, and that deterrence effect is plausibly larger
than the priced one. A result from this module that fails to close the observed gap is
therefore not evidence that permitting does not matter.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from ww import params
from ww.model.finance import FinanceSpec
from ww.model.lcow import LCOW, PlantSpec, lcow


@dataclass(frozen=True)
class Regime:
    """A permitting environment: how long approval takes, and how often it comes."""

    name: str
    years: float
    success_probability: float

    def __post_init__(self) -> None:
        if not 0.0 < self.success_probability <= 1.0:
            raise ValueError(
                f"{self.name}: success probability must be in (0, 1], "
                f"got {self.success_probability}"
            )
        if self.years < 0:
            raise ValueError(f"{self.name}: years must be non-negative")

    @property
    def rejection_probability(self) -> float:
        return 1.0 - self.success_probability


def risk_multiplier(
    regime: Regime,
    *,
    development_cost_share: float | None = None,
    cost_of_risk_capital: float | None = None,
) -> float:
    """Multiplier applied to capex to carry a project's permitting risk.

    Returns 1.0 for instantaneous, certain approval, and rises with both delay and
    rejection probability.
    """
    if development_cost_share is None:
        development_cost_share = params.value("permitting.development_cost_share")
    if cost_of_risk_capital is None:
        cost_of_risk_capital = params.value("finance.cost_of_equity")

    carried = (1.0 + cost_of_risk_capital) ** regime.years / regime.success_probability
    return 1.0 + development_cost_share * (carried - 1.0)


def apply_regime(
    plant: PlantSpec,
    regime: Regime,
    *,
    development_cost_share: float | None = None,
    cost_of_risk_capital: float | None = None,
) -> PlantSpec:
    """Return the plant with its permitting premium capitalised."""
    m = risk_multiplier(
        regime,
        development_cost_share=development_cost_share,
        cost_of_risk_capital=cost_of_risk_capital,
    )
    return replace(plant, name=f"{plant.name} [{regime.name}]", capex_usd=plant.capex_usd * m)


@dataclass(frozen=True)
class ReformBenefit:
    """What moving from one permitting regime to another is worth, in $/AF."""

    before: Regime
    after: Regime
    lcow_before: LCOW
    lcow_after: LCOW

    @property
    def saving_usd_af(self) -> float:
        return self.lcow_before.total_usd_af - self.lcow_after.total_usd_af

    @property
    def saving_fraction(self) -> float:
        return self.saving_usd_af / self.lcow_before.total_usd_af

    def sentence(self) -> str:
        """The output this contribution exists to produce: one actionable claim."""
        return (
            f"Cutting approval time from {self.before.years:.0f} to "
            f"{self.after.years:.0f} years and rejection risk from "
            f"{self.before.rejection_probability:.0%} to "
            f"{self.after.rejection_probability:.0%} lowers the cost of desalinated "
            f"water by ${self.saving_usd_af:,.0f} per acre-foot "
            f"({self.saving_fraction:.0%})."
        )


def reform_benefit(
    plant: PlantSpec,
    finance: FinanceSpec,
    before: Regime,
    after: Regime,
    **kwargs: float | None,
) -> ReformBenefit:
    """Price the difference between two permitting regimes for one plant."""
    return ReformBenefit(
        before=before,
        after=after,
        lcow_before=lcow(apply_regime(plant, before, **kwargs), finance),
        lcow_after=lcow(apply_regime(plant, after, **kwargs), finance),
    )


# --------------------------------------------------------------------------------------
# Observed regimes
# --------------------------------------------------------------------------------------


def california_regime(success_probability: float | None = None) -> Regime:
    """California as observed: Carlsbad's documented 1998 start to 2012 full permitting.

    The default success probability is the point estimate from a population of four
    Coastal Commission decisions. That is far too small a sample to trust — sample
    `denial_rate_posterior` instead wherever the result matters.
    """
    if success_probability is None:
        success_probability = 1.0 - params.value("permitting.ca.denial_rate")
    return Regime(
        name="California, observed",
        years=params.value("permitting.carlsbad.years"),
        success_probability=success_probability,
    )


def reformed_regime() -> Regime:
    """The Israeli-style counterfactual: a pre-permitted site let by standard tender.

    Duration is anchored on Israeli construction (2-3 years) plus a short approval, not
    on an aspiration. Success probability is high but not certain — even a standardised
    tender process can fail to award.
    """
    return Regime(
        name="reformed procurement",
        years=4.0,
        success_probability=0.95,
    )


def denial_rate_posterior(rng, *, prior_a: float = 1.0, prior_b: float = 1.0) -> float:
    """Draw a denial probability from a Beta posterior over the observed decisions.

    Four decisions with one denial cannot support a point estimate, so the Monte Carlo
    samples the posterior instead: Beta(prior_a + denied, prior_b + approved), which
    under the default uniform prior is Beta(2, 4). This is the difference between
    honestly saying "somewhere between rare and common" and asserting 25%.
    """
    denied = params.value("permitting.ca.decisions_denied")
    total = params.value("permitting.ca.decisions_total")
    return rng.betavariate(prior_a + denied, prior_b + (total - denied))
