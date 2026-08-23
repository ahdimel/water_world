"""Tests over the real literature file.

The important ones re-derive every `confidence: derived` parameter from its components.
That guards the failure mode this file exists to prevent: someone corrects an input
(a payment, a volume, a cost) and the headline derived number silently keeps its old
value into the paper.
"""

from __future__ import annotations

import pytest

from ww import params


@pytest.fixture(scope="module")
def ps():
    return params.load()


class TestFileIntegrity:
    def test_loads_and_validates(self, ps):
        assert len(ps.parameters) > 30
        assert len(ps.citations) > 15

    def test_every_parameter_is_cited_or_derived(self):
        assert params.uncited() == []

    def test_every_derived_parameter_has_resolvable_lineage(self, ps):
        for p in ps.parameters.values():
            if p.confidence == "derived":
                assert params.lineage(p.id), f"{p.id} has empty lineage"

    def test_parameter_keys_match_their_ids(self, ps):
        for key, p in ps.parameters.items():
            assert key == p.id

    def test_citations_carry_a_url(self, ps):
        missing = [c.id for c in ps.citations.values() if not c.url]
        assert missing == [], f"citations without a url: {missing}"


class TestUnitConversion:
    def test_acre_foot_round_trip(self):
        assert params.m3_to_af(params.af_to_m3(3.0)) == pytest.approx(3.0)

    def test_known_conversion(self):
        assert params.af_to_m3(1.0) == pytest.approx(1233.48, rel=1e-6)

    def test_price_conversion_matches_sorek_reporting(self):
        # $0.58/m3 is widely reported as roughly $715/AF.
        assert params.usd_per_m3_to_af(0.58) == pytest.approx(715, abs=5)

    def test_price_round_trip(self):
        assert params.usd_per_af_to_m3(params.usd_per_m3_to_af(1.5)) == pytest.approx(1.5)


class TestDerivedArithmetic:
    """Re-derive each stated value from its components."""

    def test_fallowing_direct_cost(self):
        conserved = params.value("fallowing.pvid.conserved")
        acres = params.value("fallowing.pvid.acres")
        entry = params.value("fallowing.pvid.entry_payment")
        annual = params.value("fallowing.pvid.annual_payment")
        rate = params.value("econ.discount_rate")

        af_per_acre = conserved / acres
        crf = rate / (1 - (1 + rate) ** -10)
        recomputed = annual / af_per_acre + (entry * crf) / af_per_acre

        stated = params.get("fallowing.direct_cost")
        assert recomputed == pytest.approx(stated.value, rel=0.05)
        assert stated.low <= recomputed <= stated.high

    def test_pvid_implied_water_duty_is_plausible(self):
        # ~4.5 AF/acre. Alfalfa in the low desert is water-hungry but this should stay
        # inside a sane agronomic range; a wild value means a component is wrong.
        duty = params.value("fallowing.pvid.conserved") / params.value("fallowing.pvid.acres")
        assert 3.0 < duty < 7.0

    def test_salton_externality_low_end_is_phase1_as_planned(self):
        cost = params.value("salton.phase1_cost")
        volume = params.value("salton.qsa_transfer_volume")
        low = cost / 10 / volume
        assert low == pytest.approx(params.get("salton.externality").low, rel=0.05)

    def test_salton_externality_high_end_is_full_coverage_plus_om(self):
        cost = params.value("salton.phase1_cost")
        covered = params.value("salton.playa_covered")
        projected = params.value("salton.playa_projected")
        om = params.value("salton.om_annual")
        volume = params.value("salton.qsa_transfer_volume")

        full = cost / (covered / projected)
        high = full / 10 / volume + om / volume
        assert high == pytest.approx(params.get("salton.externality").high, rel=0.05)

    def test_salton_coverage_fraction_is_about_62_percent(self):
        frac = params.value("salton.playa_covered") / params.value("salton.playa_projected")
        assert frac == pytest.approx(0.62, abs=0.01)

    def test_fallowing_social_cost_is_direct_plus_externality(self):
        direct = params.get("fallowing.direct_cost")
        ext = params.get("salton.externality")
        social = params.get("fallowing.social_cost")

        assert social.value == pytest.approx(direct.value + ext.value, rel=0.02)
        assert social.low == pytest.approx(direct.low + ext.low, rel=0.05)
        assert social.high == pytest.approx(direct.high + ext.high, rel=0.05)

    def test_real_cpi_change(self):
        water = 1 + params.value("cpi.water_sewer_trash.pct_change_2000_2025") / 100
        allitems = 1 + params.value("cpi.all_items.pct_change_2000_2025") / 100
        real = (water / allitems - 1) * 100
        assert real == pytest.approx(params.value("cpi.water.real_pct_change_2000_2025"), abs=1.0)


class TestHeadlineClaims:
    """Guard the numbers the paper's argument actually rests on."""

    def test_capex_intensity_gap_carlsbad_vs_sorek(self):
        sorek = params.value("desal.sorek.capex") / params.value("desal.sorek.capacity")
        carlsbad = params.value("desal.carlsbad.capex") / params.value("desal.carlsbad.capacity")
        assert sorek == pytest.approx(784, abs=15)
        assert carlsbad == pytest.approx(5283, abs=50)
        assert carlsbad / sorek == pytest.approx(6.7, abs=0.3)

    def test_scale_adjusted_gap_is_about_five(self):
        exponent = params.value("econ.capex_scaling_exponent")
        sorek_q = params.value("desal.sorek.capacity")
        carlsbad_q = params.value("desal.carlsbad.capacity")

        sorek_unit = params.value("desal.sorek.capex") / sorek_q
        carlsbad_unit = params.value("desal.carlsbad.capex") / carlsbad_q

        # Re-base Sorek to Carlsbad's scale: capex/unit scales as Q^(exponent-1).
        rebased = sorek_unit * (sorek_q / carlsbad_q) ** (1 - exponent)
        assert carlsbad_unit / rebased == pytest.approx(5.3, abs=0.4)

    def test_scale_adjusted_gap_survives_exponent_sensitivity(self):
        """The 5x headline must not be an artefact of one exponent choice."""
        sorek_q = params.value("desal.sorek.capacity")
        carlsbad_q = params.value("desal.carlsbad.capacity")
        sorek_unit = params.value("desal.sorek.capex") / sorek_q
        carlsbad_unit = params.value("desal.carlsbad.capex") / carlsbad_q

        lo, hi = params.band("econ.capex_scaling_exponent")
        for exponent in (lo, hi):
            rebased = sorek_unit * (sorek_q / carlsbad_q) ** (1 - exponent)
            # Even at the extremes the residual stays firmly in "institutional" territory.
            assert 4.0 < carlsbad_unit / rebased < 6.5

    def test_doheny_lands_at_the_same_residual_as_carlsbad(self):
        """Two plants an order of magnitude apart in size should agree — that
        agreement is the reason the 5x result is believable at all."""
        exponent = params.value("econ.capex_scaling_exponent")
        sorek_q = params.value("desal.sorek.capacity")
        sorek_unit = params.value("desal.sorek.capex") / sorek_q

        doheny_q = params.value("desal.doheny.capacity")
        doheny_unit = params.value("desal.doheny.capex") / doheny_q
        rebased = sorek_unit * (sorek_q / doheny_q) ** (1 - exponent)
        assert doheny_unit / rebased == pytest.approx(4.7, abs=0.5)

    def test_fallowing_social_cost_overlaps_sorek_cost_desal(self):
        """The Phase 0.5 result that made Act III decisive."""
        social = params.get("fallowing.social_cost")
        sorek_af = params.usd_per_m3_to_af(params.value("desal.sorek.water_price"))
        sorek_b_af = params.usd_per_m3_to_af(params.value("desal.sorek_b.water_price"))

        assert sorek_b_af == pytest.approx(505, abs=10)
        assert sorek_af == pytest.approx(715, abs=10)
        # Overlap: reformed desal's cheap end sits inside the fallowing band.
        assert social.low <= sorek_b_af <= social.high

    def test_fallowing_still_beats_unreformed_carlsbad_by_a_wide_margin(self):
        social = params.value("fallowing.social_cost")
        carlsbad = params.value("desal.carlsbad.price_current")
        assert carlsbad / social > 6.0

    def test_ag_urban_rate_disparity(self):
        ag = params.value("rates.ca_ag_districts.average")
        urban = params.value("rates.ca_city_utilities.average")
        assert urban / ag == pytest.approx(17, abs=2)

    def test_swro_energy_headroom_is_small(self):
        """Energy cannot carry the flexibility thesis: practice is only ~2x the floor."""
        practical = params.value("swro.sec")
        floor = params.value("swro.sec_thermodynamic_min")
        assert practical / floor < 2.5


class TestAuditHelpers:
    def test_band_falls_back_to_point_value(self):
        lo, hi = params.band("desal.carlsbad.capacity")
        assert lo == hi == params.value("desal.carlsbad.capacity")

    def test_band_returns_bounds_when_present(self):
        lo, hi = params.band("swro.sec")
        assert lo < params.value("swro.sec") < hi

    def test_load_balancing_parameters_are_flagged_low_confidence(self):
        """The exponent and discount rate drive headline results; keeping them marked
        low-confidence is what forces sensitivity analysis downstream."""
        low = set(params.low_confidence())
        assert "econ.capex_scaling_exponent" in low
        assert "econ.discount_rate" in low


class TestPhase2OMStructure:
    """The WateReuse O&M share table must stay internally consistent."""

    SHARES = [
        "swro.om_share_energy",
        "swro.om_share_membranes",
        "swro.om_share_other",
        "swro.om_share_labor",
        "swro.om_share_maintenance",
        "swro.om_share_chemicals",
        "swro.om_share_solids",
        "swro.om_share_permitting",
    ]

    def test_shares_sum_to_one(self):
        total = sum(params.value(p) for p in self.SHARES)
        assert total == pytest.approx(1.0, abs=1e-9)

    def test_nonenergy_share_is_the_complement_of_energy(self):
        assert params.value("swro.om_nonenergy_share") == pytest.approx(
            1.0 - params.value("swro.om_share_energy"), abs=1e-9
        )

    def test_nonenergy_share_equals_the_sum_of_its_components(self):
        components = [p for p in self.SHARES if p != "swro.om_share_energy"]
        assert params.value("swro.om_nonenergy_share") == pytest.approx(
            sum(params.value(p) for p in components), abs=1e-9
        )

    def test_energy_is_the_dominant_om_line(self):
        """If this ever fails, the flexibility question changes shape entirely."""
        energy = params.value("swro.om_share_energy")
        assert energy > max(
            params.value(p) for p in self.SHARES if p != "swro.om_share_energy"
        )


class TestPhase2DerivedArithmetic:
    """Re-derive every Phase 2 `derived` parameter from its components."""

    def test_energy_price_ratio(self):
        ca = params.get("energy.price_industrial_ca")
        il = params.get("energy.price_industrial_israel")
        ratio = params.get("energy.price_ratio_ca_israel")

        assert ratio.value == pytest.approx(ca.value / il.value, abs=1e-3)
        # Band propagates both uncertainties, not one against the other's point value.
        # This is the mistake Phase 1 caught in fallowing.social_cost.
        assert ratio.low == pytest.approx(ca.low / il.high, abs=1e-3)
        assert ratio.high == pytest.approx(ca.high / il.low, abs=1e-3)

    def test_carlsbad_gearing(self):
        debt = params.value("finance.carlsbad.debt_total")
        equity = params.value("finance.carlsbad.equity")
        assert params.value("finance.carlsbad.gearing") == pytest.approx(
            debt / (debt + equity), abs=1e-3
        )

    def test_carlsbad_debt_tranches_reconcile_to_the_total(self):
        plant = params.value("finance.carlsbad.debt_plant")
        pipeline = params.value("finance.carlsbad.debt_pipeline")
        total = params.value("finance.carlsbad.debt_total")
        # $530M + $203M = $733M against a $734M headline; the release rounds.
        assert plant + pipeline == pytest.approx(total, rel=0.005)

    @pytest.mark.parametrize(
        "plant", ["ashkelon", "palmachim", "hadera", "sorek"]
    )
    def test_israeli_tariff_legs_sum_to_the_total(self, plant):
        fixed = params.value(f"desal.{plant}.price_fixed")
        variable = params.value(f"desal.{plant}.price_variable")
        total = params.value(f"desal.{plant}.price_total")
        assert fixed + variable == pytest.approx(total, abs=1e-9)

    def test_ca_denial_rate(self):
        denied = params.value("permitting.ca.decisions_denied")
        total = params.value("permitting.ca.decisions_total")
        assert params.value("permitting.ca.denial_rate") == pytest.approx(
            denied / total, abs=1e-9
        )

    def test_denial_rate_band_is_honest_about_n_equals_four(self):
        """Four observations cannot support a precise rejection probability. The band
        must stay wide enough that nobody quotes the point estimate as if it were one."""
        p = params.get("permitting.ca.denial_rate")
        assert p.low <= p.value <= p.high
        assert p.high - p.low > 0.4


class TestPhase2CrossChecks:
    """Independent corroboration between sources, and discrepancies we refuse to hide."""

    def test_carlsbad_annual_energy_implies_the_stated_intensity(self):
        """246,156 MWh/yr over nameplate output should land inside the 4,100-5,100
        kWh/AF band taken from a different page of a different source."""
        af_per_year = params.m3_to_af(params.value("desal.carlsbad.capacity") * 365)
        implied = params.value("desal.carlsbad.energy_annual") * 1000 / af_per_year
        lo, hi = params.band("desal.carlsbad.energy_intensity")
        assert lo <= implied <= hi

    def test_sdcwa_price_corroborates_the_contract_unit_price(self):
        """Two independent routes to Carlsbad's contract price — SDCWA's own figure via
        the UC Davis review, and the Surfrider reading of the WPA — must agree."""
        contract = params.value("desal.carlsbad.contract_price_min_volume")
        lo, _ = params.band("desal.carlsbad.price_sdcwa")
        assert contract == pytest.approx(lo, rel=0.05)

    def test_the_3500_headline_does_not_reconcile_with_the_contract_price(self):
        """Deliberately asserts the DISAGREEMENT. The press figure and the contract
        price differ by far too much to be the same quantity, which is the evidence
        that one is an effective cost inflated by under-delivery. If a future edit ever
        makes these agree, someone has quietly conflated them."""
        press = params.value("desal.carlsbad.price_current")
        contract = params.value("desal.carlsbad.price_sdcwa")
        assert press / contract > 1.3

    def test_conveyance_wedge_is_observable_from_the_2013_projections(self):
        """Plant-only vs with-pipeline gives a directly measured conveyance cost, which
        is what makes the Carlsbad/Sorek capex comparison like-for-like."""
        plant = params.get("desal.carlsbad.price_projected_plant_2013")
        total = params.get("desal.carlsbad.price_projected_total_2013")
        assert total.value > plant.value
        assert total.value - plant.value == pytest.approx(179, abs=5)
        assert 150 < total.high - plant.high < 210

    def test_sorek_price_sources_disagree_but_within_a_bounded_margin(self):
        """The Israeli WDA says $0.52/m3; MIT reporting says $0.58. Both stay in the
        file. This bounds the discrepancy rather than picking a winner."""
        wda = params.value("desal.sorek.price_total")
        mit = params.value("desal.sorek.water_price")
        assert 0.85 < wda / mit < 1.0

    def test_capital_structure_is_not_the_explanation_for_the_gap(self):
        """Carlsbad ~80.9% geared, Sorek 80%. Like take-or-pay, gearing is eliminated
        as a candidate explanation for the cost difference."""
        assert params.value("finance.carlsbad.gearing") == pytest.approx(
            params.value("finance.sorek.gearing"), abs=0.02
        )

    def test_subsurface_intake_mandate_does_not_dominate_the_gap(self):
        """Doheny carries a subsurface intake and full Ocean Plan compliance, and is
        10x SMALLER than Carlsbad — so scale economies work against it — yet it still
        prices below Carlsbad. Evidence that mandated intake technology is not the
        dominant term in the residual."""
        doheny = params.value("desal.doheny.price_first_year")
        carlsbad = params.value("desal.carlsbad.price_sdcwa")
        assert doheny < carlsbad
        assert params.value("desal.doheny.capacity") < params.value(
            "desal.carlsbad.capacity"
        )

    def test_israeli_construction_is_fast_and_consistent(self):
        """The schedule difference between the two countries is pre-construction, not
        construction. This is the load-bearing contrast in Act III."""
        israeli_build = params.get("permitting.israel.construction_years")
        assert israeli_build.high <= 3.0
        carlsbad_permitting = params.value("permitting.carlsbad.years")
        assert carlsbad_permitting / israeli_build.value > 4.0


class TestPhase2MethodGuards:
    """Guards against the specific analytical errors this phase could make."""

    def test_the_rival_hypotheses_stay_low_confidence(self):
        """Both alternative explanations for the 5x gap must keep forcing sensitivity
        analysis. Promoting either to medium/high without new evidence would let the
        model quietly assume its own conclusion."""
        low = set(params.low_confidence())
        assert "construction.us_admin_premium" in low
        assert "finance.cost_of_equity" in low

    def test_us_construction_premium_band_spans_the_interesting_range(self):
        """If the premium is near its low end it explains little of the gap; near its
        high end it explains most of it. The band must contain both worlds so the
        result is not baked in."""
        p = params.get("construction.us_admin_premium")
        assert p.low < 1.5
        assert p.high >= 3.0

    def test_energy_price_gap_cannot_explain_a_capex_gap(self):
        """Structural guard, not arithmetic. The CA/Israel energy ratio applies to the
        variable leg; the 5x headline is capex. Sorek's own tariff split proves the two
        legs are separable, so the engine has no excuse for mixing them."""
        fixed = params.value("desal.sorek.price_fixed")
        variable = params.value("desal.sorek.price_variable")
        assert fixed > 0 and variable > 0
        # Capital recovery is roughly half of Sorek's tariff: an energy-price argument
        # can move the other half at most.
        assert 0.4 < fixed / (fixed + variable) < 0.6
