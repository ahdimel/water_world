"""Reference plants and finance structures, assembled from the literature file.

Nothing here invents a number. Every field traces to a parameter id, so a correction in
`literature.yaml` propagates into the model rather than sitting alongside a stale copy.

Where a plant's own value is unknown (Sorek's O&M is not published line by line) the
generic SWRO parameter is used and the difference is confined to the parameters that
*are* plant-specific — capex, capacity, energy price. That is the point of the exercise:
hold the engineering constant and let the country vary.
"""

from __future__ import annotations

from ww import params
from ww.model.finance import FinanceSpec
from ww.model.lcow import PlantSpec

#: Share of non-energy O&M that does not scale with output (labour, maintenance,
#: permit compliance), from the WateReuse O&M table.
_FIXED_OM_IDS = (
    "swro.om_share_labor",
    "swro.om_share_maintenance",
    "swro.om_share_permitting",
)


def fixed_om_share() -> float:
    """Fraction of NON-ENERGY O&M that is fixed rather than output-proportional."""
    fixed = sum(params.value(p) for p in _FIXED_OM_IDS)
    return fixed / params.value("swro.om_nonenergy_share")


def carlsbad(*, utilisation: float = 1.0, include_conveyance: bool = True) -> PlantSpec:
    """Carlsbad, California. 50 MGD, open intake, co-located outfall.

    Capex is taken net of the pipeline bond so that `capex_usd` is the plant alone and
    conveyance is carried separately — otherwise the international comparison is unfair
    before it starts.
    """
    pipeline = params.value("finance.carlsbad.debt_pipeline")
    return PlantSpec(
        name="Carlsbad",
        capacity_m3_day=params.value("desal.carlsbad.capacity"),
        capex_usd=params.value("desal.carlsbad.capex") - pipeline,
        sec_kwh_m3=params.value("swro.sec"),
        energy_price_usd_kwh=params.value("energy.price_industrial_ca"),
        om_nonenergy_usd_m3=params.value("swro.om_nonenergy"),
        utilisation=utilisation,
        conveyance_capex_usd=pipeline if include_conveyance else 0.0,
        om_fixed_share=fixed_om_share(),
    )


def sorek(*, utilisation: float = 1.0) -> PlantSpec:
    """Sorek, Israel. ~624,000 m3/day, the scale-economy benchmark.

    Conveyance is zero here by construction: Israel books grid connection separately
    (conveyance.israel.*), and Sorek's $489M capex does not include it.
    """
    return PlantSpec(
        name="Sorek",
        capacity_m3_day=params.value("desal.sorek.capacity"),
        capex_usd=params.value("desal.sorek.capex"),
        sec_kwh_m3=params.value("swro.sec"),
        energy_price_usd_kwh=params.value("energy.price_industrial_israel"),
        om_nonenergy_usd_m3=params.value("swro.om_nonenergy"),
        utilisation=utilisation,
        om_fixed_share=fixed_om_share(),
    )


def huntington_beach(*, utilisation: float = 1.0) -> PlantSpec:
    """The project that was never built. Same nameplate as Carlsbad."""
    return PlantSpec(
        name="Huntington Beach",
        capacity_m3_day=params.value("desal.huntington_beach.capacity_proposed"),
        capex_usd=params.value("desal.huntington_beach.capex_proposed"),
        sec_kwh_m3=params.value("swro.sec"),
        energy_price_usd_kwh=params.value("energy.price_industrial_ca"),
        om_nonenergy_usd_m3=params.value("swro.om_nonenergy"),
        utilisation=utilisation,
        om_fixed_share=fixed_om_share(),
    )


def doheny(*, utilisation: float = 1.0) -> PlantSpec:
    """5 MGD, subsurface intake, fully Ocean-Plan compliant. The mandated-design case."""
    return PlantSpec(
        name="Doheny",
        capacity_m3_day=params.value("desal.doheny.capacity"),
        capex_usd=params.value("desal.doheny.capex"),
        sec_kwh_m3=params.value("swro.sec"),
        energy_price_usd_kwh=params.value("energy.price_industrial_ca"),
        om_nonenergy_usd_m3=params.value("swro.om_nonenergy"),
        utilisation=utilisation,
        om_fixed_share=fixed_om_share(),
    )


REFERENCE_PLANTS = {
    "carlsbad": carlsbad,
    "sorek": sorek,
    "huntington_beach": huntington_beach,
    "doheny": doheny,
}


def carlsbad_finance() -> FinanceSpec:
    """As actually financed: 80.9% geared, bonds priced at 4.78%, 30-year agreement."""
    return FinanceSpec(
        gearing=params.value("finance.carlsbad.gearing"),
        cost_of_debt=params.value("finance.carlsbad.bond_rate"),
        cost_of_equity=params.value("finance.cost_of_equity"),
        debt_tenor_years=params.value("finance.carlsbad.term"),
        asset_life_years=params.value("finance.carlsbad.term"),
    )


def sorek_finance() -> FinanceSpec:
    """80% geared, 22-year debt tenor, 26.5-year BOT concession.

    Cost of debt is not published. Carlsbad's observed 4.78% is used so that the
    comparison does not smuggle in a financing advantage we have not evidenced — if
    Israel in fact borrows more cheaply, this understates the gap rather than
    inventing one.
    """
    return FinanceSpec(
        gearing=params.value("finance.sorek.gearing"),
        cost_of_debt=params.value("finance.carlsbad.bond_rate"),
        cost_of_equity=params.value("finance.cost_of_equity"),
        debt_tenor_years=params.value("finance.sorek.debt_tenor"),
        asset_life_years=params.value("finance.sorek.bot_term"),
    )
