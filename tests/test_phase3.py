"""Tests for Phase 3: the deflator, the Salton Sea attribution and the supply stack.

Same three kinds as test_model.py — mechanical, validation, guard — and the guards
matter most. Phase 3 overturned or shrank several earlier headlines (the 12x, the
$477/AF fallowing cost, the retired $3,500). Each correction is pinned here so it cannot
quietly un-correct itself.
"""

from __future__ import annotations

import math
import random

import pytest

from ww import params
from ww.model import deflate, salton, stack


@pytest.fixture(scope="module")
def draws():
    return stack.simulate(n=4000, seed=20261028)


# --------------------------------------------------------------------------------------
# Deflator
# --------------------------------------------------------------------------------------


class TestDeflator:
    def test_base_year_factor_is_one(self):
        assert deflate.factor(deflate.BASE_YEAR) == pytest.approx(1.0)

    def test_cpi_doubled_roughly_since_2000_ish(self):
        """Matches cpi.all_items.pct_change_2000_2025 (Jan-to-Dec) to within a few
        points; annual averages and month endpoints differ slightly by construction."""
        assert deflate.factor(2000) == pytest.approx(1.92, abs=0.06)

    def test_fractional_year_interpolates(self):
        mid = deflate.factor(2020.5)
        assert deflate.factor(2021) < mid < deflate.factor(2020)

    def test_undated_dollar_parameter_refuses_to_deflate(self):
        with pytest.raises(ValueError):
            deflate.real("desal.carlsbad.price_sdcwa")

    def test_october_2025_gap_is_recorded_not_hidden(self):
        import yaml

        doc = yaml.safe_load(deflate.CPI_PATH.read_text())
        assert 10 in doc["missing_months"][2025]

    def test_committed_table_matches_the_cache(self):
        """Guard against the committed table drifting from the source it claims."""
        from ww import cache, sources

        if not cache.is_cached(sources.get("bls.cpi.2020s").spec):
            pytest.skip("BLS cache not populated")
        table, _ = deflate.annual_from_cache()
        committed = deflate.load()
        for year in range(1990, deflate.BASE_YEAR + 1):
            assert committed[year] == pytest.approx(table[year], abs=0.01)


# --------------------------------------------------------------------------------------
# Salton Sea attribution
# --------------------------------------------------------------------------------------


class TestSaltonDerivedArithmetic:
    def test_qsa_share_of_decline(self):
        p = params.get("salton.qsa_share_of_decline")
        assert salton.qsa_share() == pytest.approx(p.value, abs=0.005)
        transfer = params.value("salton.qsa_transfer_volume")
        decline = params.band("salton.inflow_2003"), params.band("salton.inflow_post2020")
        widest = decline[0][1] - decline[1][0]
        narrowest = decline[0][0] - decline[1][1]
        assert p.low == pytest.approx(transfer / widest, abs=0.005)
        assert p.high == pytest.approx(transfer / narrowest, abs=0.005)

    def test_attributed_externality(self):
        p = params.get("salton.externality_attributed")
        full = params.get("salton.externality")
        share = params.get("salton.qsa_share_of_decline")
        dust = params.get("salton.dust_share_of_spend")
        assert p.value == pytest.approx(full.value * share.value * dust.value, rel=0.01)
        assert p.low == pytest.approx(full.low * share.low * dust.low, rel=0.01)
        assert p.high == pytest.approx(full.high * share.high * dust.high, rel=0.01)

    def test_damage_basis_externality(self):
        p = params.get("salton.externality_damage_basis")
        dmg = params.get("salton.damage_noaction")
        share = params.get("salton.qsa_share_of_decline")
        vol = params.value("salton.qsa_transfer_volume")
        assert p.value == pytest.approx(dmg.value / 30 * share.value / vol, rel=0.01)
        assert p.low == pytest.approx(dmg.low / 30 * share.low / vol, rel=0.01)
        assert p.high == pytest.approx(dmg.high / 30 * share.high / vol, rel=0.01)

    def test_conveyance_band_is_power_only_to_full_wheeling(self):
        p = params.get("conveyance.colorado_to_coast")
        power = params.value("mwd.rate.system_power_2026")
        full = power + params.value("mwd.rate.system_access_2026") + params.value(
            "mwd.rate.treatment_2026"
        )
        assert p.low == power
        assert p.high == full
        assert p.value == pytest.approx((power + full) / 2, abs=1)

    def test_treated_rate_components_sum(self):
        parts = 492 + 179 + 313 + 544
        assert params.value("mwd.rate.full_service_treated_2026") == parts


class TestSaltonGuards:
    def test_attribution_cuts_the_phase_05_figure_by_more_than_half(self):
        """The Phase 0.5 externality assumed the transfer caused all of the decline and
        that all restoration is dust. Correcting both more than halves it."""
        w = salton.walk()
        assert w.after_dust_share < 0.5 * w.full_attribution

    def test_externality_survives_attribution(self):
        """...but it does not vanish. The transfer is most of the Sea's decline."""
        assert salton.qsa_share() > 0.5
        assert salton.walk().after_dust_share > 50

    def test_unmitigated_damage_dwarfs_mitigation(self):
        """The reason the central case prices mitigation, and the hinge of the story:
        if the state does not build it, the acre-foot carries tens of times more."""
        w = salton.walk()
        assert w.damage_basis > 20 * w.after_dust_share

    def test_mitigation_draws_respect_bounds(self):
        rng = random.Random(1)
        lo = params.get("salton.externality_attributed").low
        hi = params.get("salton.externality_attributed").high
        f = deflate.factor(2018)
        for _ in range(500):
            v = salton.mitigation_externality(rng)
            assert lo * f * 0.95 <= v <= hi * f * 1.05


# --------------------------------------------------------------------------------------
# Supply stack
# --------------------------------------------------------------------------------------


class TestStackMechanics:
    def test_simulation_is_reproducible(self):
        a = stack.simulate(n=50, seed=7)
        b = stack.simulate(n=50, seed=7)
        assert [d.cost for d in a] == [d.cost for d in b]

    def test_public_finance_is_all_debt(self):
        f = stack.public_finance()
        assert f.gearing == 1.0
        assert f.wacc == pytest.approx(params.value("finance.public.rate"))

    def test_desal_variants_are_ordered(self):
        """Each reform removes cost: as built > public > permitting reform > Israeli."""
        assert (
            stack.desal_as_built()
            > stack.desal_public()
            > stack.desal_permit_reform()
            > stack.desal_israeli()
        )

    def test_marginal_cost_picks_cheapest_first(self):
        d = stack.Draw(
            cost={k: float(i) for i, k in enumerate(stack.OPTIONS)},
            quantity={k: 100.0 if not stack.OPTIONS[k].unbounded() else math.inf
                      for k in stack.OPTIONS},
        )
        assert stack.marginal_cost(d, 50) == d.cost["conservation"]
        assert stack.marginal_cost(d, 150) == d.cost["stormwater"]

    def test_only_one_desal_variant_takes_part(self):
        d = stack.Draw(
            cost={k: 1.0 for k in stack.OPTIONS} | {"desal_israeli": 0.0},
            quantity={k: 0.0 for k in stack.OPTIONS}
            | {k: math.inf for k in stack.DESAL_VARIANTS},
        )
        assert stack.marginal_cost(d, 10, desal="desal_public") == 1.0


class TestStackGuards:
    def test_delivered_ag_water_is_not_twelve_times_cheaper(self):
        """Phase 0 compared ag water AT THE RIVER with desal AT THE TAP. Delivered and
        in 2025 dollars, paying farmers beats as-built Carlsbad by under 3x."""
        ratio = stack.desal_as_built() / stack.ag_reallocation()
        assert 2.0 < ratio < 3.0

    def test_conveyance_is_the_largest_part_of_delivered_ag_water(self):
        assert params.value("conveyance.colorado_to_coast") > params.value("ag.conservation_price")

    def test_reallocation_beats_even_israeli_cost_desal(self, draws):
        assert stack.p_cheaper(draws, "ag", "desal_israeli") > 0.95

    def test_unmitigated_reallocation_loses_to_reformed_desal(self, draws):
        """The flip side, pinned so nobody can drop it: without dust control, paying
        farmers is MORE expensive than any reformed desal."""
        assert stack.p_cheaper(draws, "ag_unmitigated", "desal_permit_reform") < 0.05

    def test_potable_reuse_is_the_most_expensive_option(self, draws):
        """Pure Water SoCal at Metropolitan's own published cost costs more per AF than
        Carlsbad as built. Not desal-specific: the Californian premium is general."""
        assert stack.p_cheaper(draws, "desal_as_built", "reuse") > 0.99

    def test_gate_says_reallocation_dominates_at_the_central_cut(self, draws):
        g = stack.gate(draws)
        assert g.p_cheaper >= stack.GATE_PROBABILITY
        assert g.row in (1, 2)

    def test_gate_capacity_criterion_is_a_coin_flip(self, draws):
        """Recorded so the paper cannot present either row as decisive at 440k AF. The
        exact probability, from the triangular capacity distribution, is 0.5007."""
        a, b = params.band("ag.conservation_capacity")
        c = params.value("ag.conservation_capacity")
        t = params.value("ca.colorado_cut")
        exact = (b - t) ** 2 / ((b - a) * (b - c))
        assert exact == pytest.approx(0.5007, abs=0.0005)
        g = stack.gate(draws)
        assert g.p_capacity == pytest.approx(exact, abs=0.03)
        assert not g.capacity_decisive

    def test_gate_is_decisively_row_two_at_the_extreme_cut(self, draws):
        g = stack.gate(draws, target=params.get("ca.colorado_cut").high)
        assert g.row == 2
        assert g.capacity_decisive
        assert g.p_capacity < 0.05

    def test_ranking_holds_against_the_permitting_only_reform(self, draws):
        assert stack.gate(draws, comparator="desal_permit_reform").p_cheaper > 0.99

    def test_the_cut_never_needs_desal_at_the_central_estimate(self, draws):
        """At 440k AF, the cheaper options always cover the cut."""
        assert all(
            stack.marginal_cost(d, params.value("ca.colorado_cut")) < d.cost["desal_public"]
            for d in draws
        )
