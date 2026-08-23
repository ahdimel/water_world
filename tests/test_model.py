"""Tests for the Phase 2 desalination cost engine.

Three kinds of test here, and the third is the important one:

1. Mechanical — the maths does what it says (annuities, scaling, percentiles).
2. Validation — the model reproduces published figures it was not fitted to.
3. Guard — results that go AGAINST the project's thesis are pinned in place, so that a
   later edit cannot quietly improve them. The engine is allowed to embarrass the
   thesis; it is not allowed to stop doing so by accident.
"""

from __future__ import annotations

import random
from dataclasses import replace

import pytest

from ww import params
from ww.model import finance, lcow, montecarlo, permitting, plants, scale


# --------------------------------------------------------------------------------------
# Mechanical
# --------------------------------------------------------------------------------------


class TestFinance:
    def test_annuity_factor_matches_closed_form(self):
        # $1,000 over 10 years at 5% is a well-known ~$129.50 payment.
        assert 1000 * finance.annuity_factor(0.05, 10) == pytest.approx(129.50, abs=0.05)

    def test_annuity_factor_handles_zero_rate(self):
        assert finance.annuity_factor(0.0, 20) == pytest.approx(0.05)

    def test_annuity_factor_rejects_nonpositive_periods(self):
        with pytest.raises(ValueError):
            finance.annuity_factor(0.05, 0)

    def test_wacc_is_the_weighted_average(self):
        assert finance.wacc(0.8, 0.05, 0.12) == pytest.approx(0.8 * 0.05 + 0.2 * 0.12)

    def test_wacc_rejects_impossible_gearing(self):
        with pytest.raises(ValueError):
            finance.wacc(1.4, 0.05, 0.12)

    def test_tenor_cannot_exceed_asset_life(self):
        with pytest.raises(ValueError):
            finance.FinanceSpec(0.8, 0.05, 0.12, debt_tenor_years=40, asset_life_years=30)

    def test_capital_charge_splits_debt_and_equity(self):
        spec = finance.FinanceSpec(0.8, 0.05, 0.12, 20, 25)
        charge = finance.capital_recovery(1_000_000, spec)
        assert charge.debt_service > 0
        assert charge.equity_return > 0
        assert charge.total == charge.debt_service + charge.equity_return

    def test_financing_share_is_most_of_the_capital_charge(self):
        """The point of keeping financing explicit: for a 30-year asset at these rates,
        more of the annual charge is the cost of money than the return of principal."""
        spec = finance.FinanceSpec(0.809, 0.0478, 0.12, 30, 30)
        charge = finance.capital_recovery(1_000_000, spec)
        assert charge.financing_share > 0.5
        assert charge.principal_share + charge.financing_share == pytest.approx(1.0)

    def test_zero_capex_produces_zero_charge(self):
        spec = finance.FinanceSpec(0.8, 0.05, 0.12, 20, 25)
        charge = finance.capital_recovery(0.0, spec)
        assert charge.total == 0.0
        assert charge.principal_share == 0.0


class TestLCOWMechanics:
    def test_rejects_impossible_utilisation(self):
        with pytest.raises(ValueError):
            plants.carlsbad(utilisation=0.0)
        with pytest.raises(ValueError):
            plants.carlsbad(utilisation=1.5)

    def test_legs_sum_to_the_total(self):
        r = lcow.lcow(plants.carlsbad(), plants.carlsbad_finance())
        assert r.fixed_usd_m3 + r.variable_usd_m3 == pytest.approx(r.plant_usd_m3)
        assert r.plant_usd_m3 + r.conveyance_usd_m3 == pytest.approx(r.total_usd_m3)

    def test_energy_leg_is_invariant_to_utilisation(self):
        """Energy is consumed per cubic metre produced, so it must not move when the
        plant runs less. If this fails, fixed and variable costs have been confused."""
        fin = plants.carlsbad_finance()
        full = lcow.lcow(plants.carlsbad(utilisation=1.0), fin)
        half = lcow.lcow(plants.carlsbad(utilisation=0.5), fin)
        assert full.energy_usd_m3 == pytest.approx(half.energy_usd_m3)

    def test_capital_recovery_leg_rises_as_utilisation_falls(self):
        fin = plants.carlsbad_finance()
        full = lcow.lcow(plants.carlsbad(utilisation=1.0), fin)
        half = lcow.lcow(plants.carlsbad(utilisation=0.5), fin)
        assert half.capital_recovery_usd_m3 == pytest.approx(
            2 * full.capital_recovery_usd_m3
        )

    def test_conveyance_is_separable(self):
        fin = plants.carlsbad_finance()
        with_pipe = lcow.lcow(plants.carlsbad(include_conveyance=True), fin)
        without = lcow.lcow(plants.carlsbad(include_conveyance=False), fin)
        assert with_pipe.conveyance_usd_m3 > 0
        assert without.conveyance_usd_m3 == 0
        assert with_pipe.plant_usd_m3 == pytest.approx(without.plant_usd_m3)


# --------------------------------------------------------------------------------------
# Validation against published figures the model was not fitted to
# --------------------------------------------------------------------------------------


class TestValidation:
    def test_carlsbad_reproduces_the_sdcwa_price(self):
        """The strongest evidence the engine is sound. Nothing here was tuned: capex,
        80.9% gearing, the observed 4.78% bond rate, California industrial power and
        generic SWRO O&M are all independent inputs, and they land within a few percent
        of the price the Water Authority actually reports paying."""
        modelled = lcow.lcow(plants.carlsbad(), plants.carlsbad_finance()).total_usd_af
        lo, hi = params.band("desal.carlsbad.price_sdcwa")
        assert lo * 0.95 <= modelled <= hi * 1.05

    def test_sorek_reproduces_the_published_fixed_leg(self):
        """The Israeli WDA publishes Sorek's fixed price at $0.25/m3. The model builds
        it from capex, 80% gearing and a 22-year tenor and gets within a couple of
        percent — which is what licenses using the same machinery on both countries."""
        modelled = lcow.lcow(plants.sorek(), plants.sorek_finance()).fixed_usd_m3
        assert modelled == pytest.approx(params.value("desal.sorek.price_fixed"), rel=0.10)

    def test_sorek_variable_leg_overshoots_the_published_tariff(self):
        """A DISAGREEMENT WE KEEP. Using Israel's general industrial electricity tariff,
        the model puts Sorek's variable leg well above the published $0.27/m3. The
        likeliest explanation is that Israeli desalination does not pay the general
        industrial rate (Sorek has dedicated generation) and that the published tariffs
        are of an earlier vintage than our 2025 energy price.

        Pinned as a known limitation so nobody 'fixes' it by tuning the energy price
        until it matches — that would destroy the independence of the Carlsbad
        validation above, which uses the same O&M and SEC assumptions.
        """
        modelled = lcow.lcow(plants.sorek(), plants.sorek_finance()).variable_usd_m3
        published = params.value("desal.sorek.price_variable")
        assert modelled > published * 1.3


# --------------------------------------------------------------------------------------
# Scale-adjusted comparison
# --------------------------------------------------------------------------------------


class TestScale:
    def test_scaling_is_neutral_at_equal_capacity(self):
        assert scale.scale_capex(100.0, 50.0, 50.0, 0.8) == pytest.approx(100.0)

    def test_exponent_of_one_removes_all_scale_economy(self):
        assert scale.scale_capex(100.0, 10.0, 20.0, 1.0) == pytest.approx(200.0)

    def test_lower_exponent_means_stronger_scale_economy(self):
        strong = scale.scale_capex(100.0, 10.0, 100.0, 0.75)
        weak = scale.scale_capex(100.0, 10.0, 100.0, 0.9)
        assert strong < weak

    def test_scaling_rejects_nonpositive_capacity(self):
        with pytest.raises(ValueError):
            scale.scale_capex(100.0, 0.0, 50.0, 0.8)

    def _carlsbad_gap(self, exponent: float, include_conveyance: bool = False):
        cb = plants.carlsbad(include_conveyance=include_conveyance)
        sk = plants.sorek()
        return scale.gap(
            reference_capex=sk.capex_usd,
            reference_capacity=sk.capacity_m3_day,
            subject_capex=cb.total_capex_usd,
            subject_capacity=cb.capacity_m3_day,
            exponent=exponent,
            reference_name="Sorek",
            subject_name="Carlsbad",
        )

    def test_gap_survives_the_full_exponent_sensitivity(self):
        """The project's standing rule: the headline must hold at both ends of the
        0.75-0.9 range, or it is an artefact of the exponent."""
        for e in (0.75, 0.8, 0.9):
            assert self._carlsbad_gap(e).gap > 3.5

    def test_gap_across_exponents_covers_the_stated_range(self):
        p = params.get("econ.capex_scaling_exponent")
        cb, sk = plants.carlsbad(include_conveyance=False), plants.sorek()
        gaps = scale.gap_across_exponents(
            reference_capex=sk.capex_usd,
            reference_capacity=sk.capacity_m3_day,
            subject_capex=cb.capex_usd,
            subject_capacity=cb.capacity_m3_day,
        )
        assert set(gaps) == {p.low, p.value, p.high}

    def test_stripping_conveyance_materially_shrinks_the_headline(self):
        """FINDING AGAINST THE THESIS. Carlsbad's $203M pipeline has no counterpart in
        Sorek's capex, and removing it takes the scale-adjusted gap from ~5.3x to
        ~4.2x. The '5x' headline is therefore partly a conveyance artefact, and the
        honest figure is roughly 4x."""
        with_pipe = self._carlsbad_gap(0.8, include_conveyance=True).gap
        without = self._carlsbad_gap(0.8, include_conveyance=False).gap
        assert with_pipe > 5.0
        assert without < 4.5
        assert (with_pipe - without) / with_pipe > 0.15

    def test_decompose_defaults_to_no_intake_premium(self):
        """Carlsbad has an open intake and a co-located outfall — the cheap options.
        Applying a subsurface-intake premium to it would be wrong, so the default is
        zero and the residual is the whole scale-adjusted gap."""
        g = self._carlsbad_gap(0.8)
        d = scale.decompose(g)
        assert d.institutional_residual == pytest.approx(g.gap)

    def test_decompose_applies_an_explicit_intake_premium(self):
        g = self._carlsbad_gap(0.8)
        d = scale.decompose(g, intake_premium=0.45)
        assert d.institutional_residual < g.gap


# --------------------------------------------------------------------------------------
# Permitting priced as capital
# --------------------------------------------------------------------------------------


class TestPermitting:
    def test_costless_regime_is_neutral(self):
        instant = permitting.Regime("instant", years=0.0, success_probability=1.0)
        assert permitting.risk_multiplier(instant) == pytest.approx(1.0)

    def test_multiplier_rises_with_delay(self):
        short = permitting.Regime("short", 4.0, 0.9)
        long = permitting.Regime("long", 20.0, 0.9)
        assert permitting.risk_multiplier(long) > permitting.risk_multiplier(short)

    def test_multiplier_rises_as_rejection_risk_rises(self):
        safe = permitting.Regime("safe", 10.0, 0.95)
        risky = permitting.Regime("risky", 10.0, 0.5)
        assert permitting.risk_multiplier(risky) > permitting.risk_multiplier(safe)

    def test_regime_rejects_impossible_probability(self):
        with pytest.raises(ValueError):
            permitting.Regime("bad", 10.0, 0.0)
        with pytest.raises(ValueError):
            permitting.Regime("bad", 10.0, 1.5)

    def test_reform_produces_a_positive_saving_and_a_sentence(self):
        rb = permitting.reform_benefit(
            plants.carlsbad(),
            plants.carlsbad_finance(),
            permitting.california_regime(),
            permitting.reformed_regime(),
        )
        assert rb.saving_usd_af > 0
        text = rb.sentence()
        assert "acre-foot" in text and "15" in text and "4" in text

    def test_permitting_explains_only_a_minority_of_the_gap(self):
        """THE MOST IMPORTANT TEST IN THIS FILE, and it goes against the thesis.

        Priced as capital at risk, California's permitting regime adds roughly 1.4x to
        capex against a reformed one. The scale-adjusted gap is roughly 4x. So even
        abolishing permitting risk entirely leaves a ~3x gap unexplained, and the
        project's preferred villain accounts for well under half the residual.

        Act III's legislative recommendation still has real value — $400+/AF — but the
        paper must not claim permitting explains the 5x. If a future change makes
        permitting look sufficient, this test should fail and be argued with, not
        deleted.
        """
        before = permitting.california_regime()
        after = permitting.reformed_regime()
        explained = permitting.risk_multiplier(before) / permitting.risk_multiplier(after)

        cb, sk = plants.carlsbad(include_conveyance=False), plants.sorek()
        residual = scale.gap(
            reference_capex=sk.capex_usd,
            reference_capacity=sk.capacity_m3_day,
            subject_capex=cb.capex_usd,
            subject_capacity=cb.capacity_m3_day,
            exponent=0.8,
        ).gap

        assert explained < 1.6
        assert residual / explained > 2.5

    def test_denial_rate_posterior_is_wide_and_centred_below_a_half(self):
        """Beta(2, 4) from one denial in four decisions: uncertain, not precise."""
        rng = random.Random(1)
        draws = [permitting.denial_rate_posterior(rng) for _ in range(5000)]
        mean = sum(draws) / len(draws)
        assert 0.25 < mean < 0.40
        assert min(draws) < 0.10
        assert max(draws) > 0.70


# --------------------------------------------------------------------------------------
# Monte Carlo
# --------------------------------------------------------------------------------------


class TestMonteCarlo:
    def test_sampling_respects_a_stated_band(self):
        rng = random.Random(7)
        lo, hi = params.band("swro.sec")
        draws = [montecarlo.sample("swro.sec", rng) for _ in range(500)]
        assert all(lo <= d <= hi for d in draws)

    def test_rangeless_parameter_is_returned_unchanged(self):
        rng = random.Random(7)
        pid = "desal.carlsbad.capacity"
        assert montecarlo.sample(pid, rng) == params.value(pid)

    def test_runs_are_reproducible_from_the_seed(self):
        draw = lambda rng: montecarlo.sample("swro.sec", rng)  # noqa: E731
        a = montecarlo.run(draw, n=200, seed=42)
        b = montecarlo.run(draw, n=200, seed=42)
        assert list(a.values) == list(b.values)

    def test_different_seeds_differ(self):
        draw = lambda rng: montecarlo.sample("swro.sec", rng)  # noqa: E731
        a = montecarlo.run(draw, n=200, seed=1)
        b = montecarlo.run(draw, n=200, seed=2)
        assert list(a.values) != list(b.values)

    def test_percentiles_are_ordered_and_bounded(self):
        d = montecarlo.Distribution("t", [float(i) for i in range(101)])
        assert d.percentile(0) == 0
        assert d.percentile(100) == 100
        assert d.percentile(50) == pytest.approx(50)
        lo, hi = d.band_90
        assert lo < d.median < hi

    def test_percentile_rejects_out_of_range(self):
        d = montecarlo.Distribution("t", [1.0, 2.0])
        with pytest.raises(ValueError):
            d.percentile(101)

    def test_probability_above(self):
        d = montecarlo.Distribution("t", [1.0, 2.0, 3.0, 4.0])
        assert d.probability_above(2.0) == pytest.approx(0.5)

    def test_run_rejects_zero_draws(self):
        with pytest.raises(ValueError):
            montecarlo.run(lambda rng: 1.0, n=0)

    def test_lcow_distribution_brackets_the_deterministic_result(self):
        """The whole point of Phase 2's Monte Carlo: a band, not a point. The
        deterministic answer must sit inside its own uncertainty."""

        def draw(rng: random.Random) -> float:
            spec = replace(
                plants.carlsbad(),
                sec_kwh_m3=montecarlo.sample("swro.sec", rng),
                energy_price_usd_kwh=montecarlo.sample("energy.price_industrial_ca", rng),
                om_nonenergy_usd_m3=montecarlo.sample("swro.om_nonenergy", rng),
            )
            return lcow.lcow(spec, plants.carlsbad_finance()).total_usd_af

        dist = montecarlo.run(draw, n=1000, seed=99, name="Carlsbad LCOW")
        point = lcow.lcow(plants.carlsbad(), plants.carlsbad_finance()).total_usd_af
        lo, hi = dist.band_90
        assert lo < point < hi
        assert "median" in dist.summary()


class TestCLI:
    """Smoke tests: each command runs, exits 0, and prints its caveat.

    The caveat assertions matter more than they look. These figures get read out of a
    terminal and pasted into documents, and the ones most likely to travel without
    their qualification are exactly the ones that most need it.
    """

    def test_lcow_runs_and_warns_about_doheny_financing(self, capsys):
        from ww.__main__ import main

        assert main(["lcow"]) == 0
        out = capsys.readouterr().out
        assert "Carlsbad" in out and "Sorek" in out
        assert "upper bound" in out

    def test_lcow_rejects_an_unknown_plant(self, capsys):
        from ww.__main__ import main

        assert main(["lcow", "atlantis"]) == 2

    def test_gap_reports_every_exponent_and_the_conveyance_caveat(self, capsys):
        from ww.__main__ import main

        assert main(["gap"]) == 0
        out = capsys.readouterr().out
        for exponent in ("0.75", "0.80", "0.90"):
            assert exponent in out
        assert "conveyance artefact" in out

    def test_gap_with_conveyance_says_it_overstates(self, capsys):
        from ww.__main__ import main

        assert main(["gap", "--include-conveyance"]) == 0
        assert "OVERSTATES" in capsys.readouterr().out

    def test_permitting_prints_the_sentence_and_the_limitation(self, capsys):
        from ww.__main__ import main

        assert main(["permitting"]) == 0
        out = capsys.readouterr().out
        assert "per acre-foot" in out
        assert "LOWER BOUND" in out
        assert "cannot claim permitting explains 5x" in out

    def test_montecarlo_reports_a_band_not_a_point(self, capsys):
        from ww.__main__ import main

        assert main(["montecarlo", "-n", "200"]) == 0
        out = capsys.readouterr().out
        assert "90% band" in out
        assert "LOWER bound on true uncertainty" in out
