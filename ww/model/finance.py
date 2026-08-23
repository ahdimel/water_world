"""Financing primitives for a capex-heavy asset.

Financing is usually the largest single line in desalinated water, so this module keeps
it explicit rather than burying it in a chosen discount rate. `capital_recovery` returns
the debt and equity legs separately, so a result can always answer "how much of this
water price is the money?".

The convention throughout: rates are fractions per year, periods are years, and every
function is pure.
"""

from __future__ import annotations

from dataclasses import dataclass


def annuity_factor(rate: float, periods: float) -> float:
    """Capital recovery factor: the level annual payment that repays 1.0 over `periods`.

    Handles the zero-rate case, which is otherwise a division by zero and does turn up
    when someone sensitivity-tests down to a real rate of zero.
    """
    if periods <= 0:
        raise ValueError(f"periods must be positive, got {periods}")
    if rate == 0:
        return 1.0 / periods
    growth = (1.0 + rate) ** periods
    return rate * growth / (growth - 1.0)


def wacc(gearing: float, cost_of_debt: float, cost_of_equity: float) -> float:
    """Weighted average cost of capital.

    No tax shield term: both reference projects are financed with tax-exempt debt
    (Carlsbad's private-activity bonds) or by an international lender consortium, so a
    corporate-tax adjustment would be modelling a deduction neither project takes.
    """
    if not 0.0 <= gearing <= 1.0:
        raise ValueError(f"gearing must be in [0, 1], got {gearing}")
    return gearing * cost_of_debt + (1.0 - gearing) * cost_of_equity


@dataclass(frozen=True)
class FinanceSpec:
    """How a project is paid for."""

    gearing: float
    cost_of_debt: float
    cost_of_equity: float
    debt_tenor_years: float
    asset_life_years: float

    def __post_init__(self) -> None:
        if self.debt_tenor_years > self.asset_life_years:
            raise ValueError(
                "debt tenor exceeds asset life: "
                f"{self.debt_tenor_years} > {self.asset_life_years}"
            )

    @property
    def wacc(self) -> float:
        return wacc(self.gearing, self.cost_of_debt, self.cost_of_equity)


@dataclass(frozen=True)
class CapitalCharge:
    """The annual cost of capital, split so the financing story stays visible."""

    debt_service: float
    equity_return: float
    capex: float
    years: float

    @property
    def total(self) -> float:
        return self.debt_service + self.equity_return

    @property
    def principal_share(self) -> float:
        """Fraction of the charge that is simply returning the capital spent."""
        if self.total == 0:
            return 0.0
        return (self.capex / self.years) / self.total

    @property
    def financing_share(self) -> float:
        """Fraction that is the cost of money rather than repayment of principal.

        Reported because it is the quantity de-risking actually buys: permitting reform
        cannot make a plant cheaper to build, only cheaper to fund.
        """
        return 0.0 if self.total == 0 else 1.0 - self.principal_share


def capital_recovery(capex: float, spec: FinanceSpec) -> CapitalCharge:
    """Annual capital charge, with the debt and equity legs kept apart.

    Debt amortises over its tenor; equity is levelised over the asset's life. Splitting
    them this way matters because the two reference projects differ on tenor (Sorek 22
    years against Carlsbad's 30-year agreement) even though their gearing is nearly
    identical, and a single blended annuity would hide that.
    """
    if capex < 0:
        raise ValueError(f"capex must be non-negative, got {capex}")
    debt = capex * spec.gearing
    equity = capex - debt
    return CapitalCharge(
        debt_service=debt * annuity_factor(spec.cost_of_debt, spec.debt_tenor_years),
        equity_return=equity
        * annuity_factor(spec.cost_of_equity, spec.asset_life_years),
        capex=capex,
        years=spec.asset_life_years,
    )
