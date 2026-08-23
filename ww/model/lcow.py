"""Levelised cost of water for a seawater reverse osmosis plant.

The output deliberately mirrors the structure the Israeli Water Desalination
Administration publishes its tariffs in — a fixed leg and a variable leg — because that
is what makes an Israeli plant and a Californian one comparable line by line. Sorek's
published $0.25 fixed + $0.27 variable is the check this model has to be able to meet.

Two distinctions are load-bearing and easy to lose:

* **Availability is not utilisation.** A plant can be technically able to run and still
  not be dispatched. Carlsbad is contracted at a 48,000 AF/yr take-or-pay minimum
  against 56,000 AF/yr of nameplate, and when the buyer wants less, the fixed cost is
  spread over less water. That wedge is computed here, not asserted.
* **Conveyance is not the plant.** Carlsbad's financing included a separate $203M bond
  for a 10-mile pipeline; Israel books grid connection separately at $0.04-0.30/m3.
  Comparing one country's plant-plus-pipeline against the other's plant alone would
  manufacture a gap.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from ww import params
from ww.model.finance import CapitalCharge, FinanceSpec, capital_recovery

DAYS_PER_YEAR = 365.0


@dataclass(frozen=True)
class PlantSpec:
    """The physical and commercial description of one plant."""

    name: str
    capacity_m3_day: float
    capex_usd: float
    sec_kwh_m3: float
    energy_price_usd_kwh: float
    om_nonenergy_usd_m3: float
    utilisation: float
    conveyance_capex_usd: float = 0.0
    #: Fixed O&M as a share of non-energy O&M. Labour, maintenance and permit
    #: compliance do not scale with output; chemicals, membranes and solids do.
    om_fixed_share: float = 0.0

    def __post_init__(self) -> None:
        if not 0.0 < self.utilisation <= 1.0:
            raise ValueError(
                f"{self.name}: utilisation must be in (0, 1], got {self.utilisation}"
            )
        if self.capacity_m3_day <= 0:
            raise ValueError(f"{self.name}: capacity must be positive")

    @property
    def nameplate_m3_year(self) -> float:
        return self.capacity_m3_day * DAYS_PER_YEAR

    @property
    def production_m3_year(self) -> float:
        """Water actually delivered. The denominator of every unit cost below."""
        return self.nameplate_m3_year * self.utilisation

    @property
    def total_capex_usd(self) -> float:
        return self.capex_usd + self.conveyance_capex_usd


@dataclass(frozen=True)
class LCOW:
    """A levelised cost, broken into legs that can be compared internationally."""

    plant: str
    capital_recovery_usd_m3: float
    fixed_om_usd_m3: float
    energy_usd_m3: float
    variable_om_usd_m3: float
    conveyance_usd_m3: float
    charge: CapitalCharge

    @property
    def fixed_usd_m3(self) -> float:
        """Capital recovery plus fixed O&M — the leg Israel publishes as 'fixed price'."""
        return self.capital_recovery_usd_m3 + self.fixed_om_usd_m3

    @property
    def variable_usd_m3(self) -> float:
        return self.energy_usd_m3 + self.variable_om_usd_m3

    @property
    def plant_usd_m3(self) -> float:
        """Cost at the plant fence, excluding conveyance. The like-for-like figure."""
        return self.fixed_usd_m3 + self.variable_usd_m3

    @property
    def total_usd_m3(self) -> float:
        return self.plant_usd_m3 + self.conveyance_usd_m3

    @property
    def total_usd_af(self) -> float:
        return params.usd_per_m3_to_af(self.total_usd_m3)

    @property
    def plant_usd_af(self) -> float:
        return params.usd_per_m3_to_af(self.plant_usd_m3)

    def as_dict(self) -> dict[str, float]:
        return {
            "capital_recovery": self.capital_recovery_usd_m3,
            "fixed_om": self.fixed_om_usd_m3,
            "energy": self.energy_usd_m3,
            "variable_om": self.variable_om_usd_m3,
            "conveyance": self.conveyance_usd_m3,
            "fixed": self.fixed_usd_m3,
            "variable": self.variable_usd_m3,
            "plant": self.plant_usd_m3,
            "total": self.total_usd_m3,
        }


def lcow(plant: PlantSpec, finance: FinanceSpec) -> LCOW:
    """Levelised cost of water, in $/m3, by cost leg."""
    production = plant.production_m3_year

    plant_charge = capital_recovery(plant.capex_usd, finance)
    conveyance_charge = capital_recovery(plant.conveyance_capex_usd, finance)

    om_total = plant.om_nonenergy_usd_m3 * production
    fixed_om = om_total * plant.om_fixed_share
    variable_om = om_total - fixed_om

    return LCOW(
        plant=plant.name,
        capital_recovery_usd_m3=plant_charge.total / production,
        fixed_om_usd_m3=fixed_om / production,
        # Energy is charged on water produced, so it is invariant to utilisation.
        energy_usd_m3=plant.sec_kwh_m3 * plant.energy_price_usd_kwh,
        variable_om_usd_m3=variable_om / production,
        conveyance_usd_m3=conveyance_charge.total / production,
        charge=plant_charge,
    )


@dataclass(frozen=True)
class UtilisationWedge:
    """What under-delivery does to unit cost.

    This is the mechanism that most plausibly reconciles Carlsbad's ~$2,430/AF contract
    price with the ~$3,500/AF that gets reported: fixed costs do not shrink when the
    buyer takes less water.
    """

    at_nameplate_usd_af: float
    at_actual_usd_af: float

    @property
    def wedge_usd_af(self) -> float:
        return self.at_actual_usd_af - self.at_nameplate_usd_af

    @property
    def ratio(self) -> float:
        return self.at_actual_usd_af / self.at_nameplate_usd_af


def utilisation_wedge(
    plant: PlantSpec, finance: FinanceSpec, utilisation: float
) -> UtilisationWedge:
    """Compare a plant's unit cost at full output against a lower delivered volume."""
    full = replace(plant, utilisation=1.0)
    actual = replace(plant, utilisation=utilisation)
    return UtilisationWedge(
        at_nameplate_usd_af=lcow(full, finance).total_usd_af,
        at_actual_usd_af=lcow(actual, finance).total_usd_af,
    )
