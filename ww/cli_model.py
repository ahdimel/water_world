"""CLI commands for the Phase 2 cost engine.

Kept out of `__main__` so the reporting logic — which is where the analytical caveats
live — is testable without going through argparse.

Every command prints its caveats alongside its numbers. That is deliberate: these
results are going to be read out of a terminal and pasted into a document, and the
figures that most need a caveat (the 5x, the permitting premium) are exactly the ones
most likely to travel without one.
"""

from __future__ import annotations

import argparse
import random
from dataclasses import replace

from ww import params
from ww.model import deflate, lcow, montecarlo, permitting, plants, salton, scale, stack

#: Parameters the Monte Carlo varies. Everything else is held at its stated value.
_SAMPLED = (
    "swro.sec",
    "swro.om_nonenergy",
    "finance.cost_of_equity",
)


def _rule(title: str) -> None:
    print(f"\n  {title}")
    print("  " + "-" * max(len(title), 40))


def cmd_lcow(args: argparse.Namespace) -> int:
    """Levelised cost for one or all reference plants."""
    names = [args.plant] if args.plant else list(plants.REFERENCE_PLANTS)
    finance_for = {"sorek": plants.sorek_finance}

    _rule(f"Levelised cost of water, {deflate.BASE_YEAR} dollars")
    print(f"  {'plant':<18}{'fixed':>9}{'variable':>10}{'conveyance':>12}"
          f"{'$/m3':>9}{'$/AF':>10}")
    for name in names:
        if name not in plants.REFERENCE_PLANTS:
            print(f"  unknown plant: {name}")
            return 2
        spec = plants.REFERENCE_PLANTS[name](utilisation=args.utilisation)
        fin = finance_for.get(name, plants.carlsbad_finance)()
        r = lcow.lcow(spec, fin)
        print(f"  {r.plant:<18}{r.fixed_usd_m3:>9.3f}{r.variable_usd_m3:>10.3f}"
              f"{r.conveyance_usd_m3:>12.3f}{r.total_usd_m3:>9.3f}"
              f"{r.total_usd_af:>10,.0f}")

    print()
    print("  fixed = capital recovery + fixed O&M; the leg Israel publishes separately.")
    print("  Sorek's published tariff is $0.25 fixed + $0.27 variable = $0.52/m3.")
    print("  NOTE: the model's Israeli VARIABLE leg overshoots that published figure.")
    print("        Israeli desalination likely does not pay the general industrial")
    print("        tariff, and the published prices are of an earlier vintage. The")
    print("        FIXED leg — the one Act III depends on — matches to ~2%.")
    print()
    print("  CAVEAT ON DOHENY: every Californian plant here is run on Carlsbad's")
    print("  PRIVATE financing (80.9% geared, private equity return). Doheny is a")
    print("  public district project with no equity return; `ww stack` prices every")
    print("  plant on public finance instead. Treat Doheny's figure here as an upper bound.")
    return 0


def cmd_gap(args: argparse.Namespace) -> int:
    """The scale-adjusted international capex comparison."""
    cb = plants.carlsbad(include_conveyance=args.include_conveyance)
    sk = plants.sorek()

    _rule("Scale-adjusted capex gap, Carlsbad against Sorek")
    print(f"  Carlsbad unit capex : ${scale.unit_capex(cb.total_capex_usd, cb.capacity_m3_day):,.0f} per m3/day")
    print(f"  Sorek unit capex    : ${scale.unit_capex(sk.capex_usd, sk.capacity_m3_day):,.0f} per m3/day")
    print(f"  capacity ratio      : {sk.capacity_m3_day / cb.capacity_m3_day:.1f}x in Sorek's favour")
    print()

    gaps = scale.gap_across_exponents(
        reference_capex=sk.capex_usd,
        reference_capacity=sk.capacity_m3_day,
        subject_capex=cb.total_capex_usd,
        subject_capacity=cb.capacity_m3_day,
        reference_name="Sorek",
        subject_name="Carlsbad",
    )
    print(f"  {'exponent':<12}{'gap':>8}")
    for exponent, g in gaps.items():
        print(f"  {exponent:<12.2f}{g.gap:>7.2f}x")

    print()
    if args.include_conveyance:
        print("  INCLUDES Carlsbad's $203M pipeline. Sorek's capex has no equivalent")
        print("  inside it, so this OVERSTATES the gap. Re-run without --include-conveyance.")
    else:
        print("  Excludes Carlsbad's $203M pipeline, which has no counterpart in Sorek's")
        print("  capex. Including it would raise the gap to ~5.3x — the headline '5x' is")
        print("  partly a conveyance artefact, and ~4x is the defensible figure.")
    print()
    print("  Carlsbad had an OPEN intake and a co-located outfall — the cheap options —")
    print("  so the mandated-subsurface-intake hypothesis does not explain this gap.")
    return 0


def cmd_permitting(args: argparse.Namespace) -> int:
    """Price the difference between the observed and a reformed permitting regime."""
    before = permitting.california_regime()
    after = permitting.reformed_regime()
    spec = plants.carlsbad()
    fin = plants.carlsbad_finance()

    _rule("Permitting priced as capital at risk")
    for regime in (before, after):
        m = permitting.risk_multiplier(regime)
        print(f"  {regime.name:<24} {regime.years:>5.1f} yrs  "
              f"{regime.rejection_probability:>6.0%} rejection  "
              f"capex x{m:.3f}")

    rb = permitting.reform_benefit(spec, fin, before, after)
    print()
    print(f"  {rb.sentence()}")

    explained = permitting.risk_multiplier(before) / permitting.risk_multiplier(after)
    cb = plants.carlsbad(include_conveyance=False)
    sk = plants.sorek()
    residual = scale.gap(
        reference_capex=sk.capex_usd,
        reference_capacity=sk.capacity_m3_day,
        subject_capex=cb.capex_usd,
        subject_capacity=cb.capacity_m3_day,
        exponent=params.value("econ.capex_scaling_exponent"),
    ).gap

    print()
    print("  How much of the gap does this explain?")
    print(f"    scale-adjusted capex gap        {residual:.2f}x")
    print(f"    explained by permitting risk    {explained:.2f}x")
    print(f"    still unexplained after reform  {residual / explained:.2f}x")
    print()
    print("  READ THIS BEFORE QUOTING THE ABOVE. Priced as capital at risk, permitting")
    print("  accounts for well under half the gap. Reform is worth real money, but the")
    print("  paper cannot claim permitting explains 5x.")
    print("  This is a LOWER BOUND: it prices only projects actually attempted, and")
    print("  cannot see those never proposed because the risk was obvious in advance.")
    return 0


def cmd_montecarlo(args: argparse.Namespace) -> int:
    """LCOW as a distribution rather than a point estimate."""

    def draw(rng: random.Random) -> float:
        spec = replace(
            plants.carlsbad(utilisation=args.utilisation),
            sec_kwh_m3=montecarlo.sample("swro.sec", rng),
            energy_price_usd_kwh=montecarlo.sample("energy.price_industrial_ca", rng),
            om_nonenergy_usd_m3=montecarlo.sample("swro.om_nonenergy", rng),
        )
        fin = replace(
            plants.carlsbad_finance(),
            cost_of_equity=montecarlo.sample("finance.cost_of_equity", rng),
        )
        return lcow.lcow(spec, fin).total_usd_af

    dist = montecarlo.run(draw, n=args.n, seed=args.seed, name="Carlsbad LCOW $/AF")

    _rule(f"Monte Carlo, n={args.n}, seed={args.seed}")
    print(f"  sampled: {', '.join(_SAMPLED)}, energy.price_industrial_ca")
    print()
    lo, hi = dist.band_90
    print(f"  median            ${dist.median:,.0f}/AF")
    print(f"  90% band          ${lo:,.0f} to ${hi:,.0f}/AF")
    print(f"  mean              ${dist.mean:,.0f}/AF")
    today = params.value("desal.carlsbad.price_current")
    print(f"  P(cost > SDCWA's current ${today:,.0f}/AF) = "
          f"{dist.probability_above(today):.0%}   (model at full output; SDCWA pays")
    print("  for the 48,000 AF minimum, so the model should sit somewhat below it)")
    print()
    print("  Range-less parameters contribute no spread by design, so this band is a")
    print("  LOWER bound on true uncertainty. Capex itself carries no stated range.")
    return 0


def cmd_deflator(args: argparse.Namespace) -> int:
    """Show (or rebuild) the CPI-U table every dollar is restated with."""
    if args.rebuild:
        print(f"  wrote {deflate.rebuild()}")
    table = deflate.load()
    _rule(f"CPI-U annual averages, factor to {deflate.BASE_YEAR} dollars")
    for year in sorted(table)[-16:]:
        print(f"  {year}  {table[year]:>8.3f}   x{deflate.factor(year):.3f}")
    return 0


def cmd_salton(args: argparse.Namespace) -> int:  # noqa: ARG001
    """The Salton Sea externality, one correction at a time."""
    w = salton.walk()
    _rule(f"Salton Sea dust cost per Imperial acre-foot, {deflate.BASE_YEAR} dollars")
    dust = params.value("salton.dust_share_of_spend")
    iid = params.value("ag.iid_share_of_conservation")
    lines = [
        ("Phase 0.5 (all decline is the transfer's, all spend is dust)", w.full_attribution),
        (f"x QSA share of the inflow decline ({salton.qsa_share():.0%})", w.after_qsa_share),
        (f"x dust share of restoration spend ({dust:.0%})", w.after_dust_share),
        (f"per AF of California ag conservation ({iid:.0%} Imperial)", w.per_blended_ag_af),
        ("", None),
        ("stress case, dust never mitigated (damage basis)", w.damage_basis),
    ]
    for label, v in lines:
        print(f"  {label:<62}${v:>7,.0f}" if v is not None else "")
    print()
    print("  Applies only to Imperial Valley water: Palo Verde drains to the river,")
    print("  not the Sea. Phase 0.5 attached this cost to Palo Verde's price.")
    print("  The damage basis is the Pacific Institute's cost of inaction; mitigation")
    print("  is the cheaper path by a factor of ~40, IF the state builds it.")
    return 0


def cmd_stack(args: argparse.Namespace) -> int:
    """Phase 3: every option on one axis, and the framing gate."""
    draws = stack.simulate(n=args.n, seed=args.seed)
    _rule(f"Supply stack, {deflate.BASE_YEAR} dollars, delivered treated, n={args.n}")
    print(f"  {'option':<50}{'median':>9}{'90% band':>20}")
    rows = sorted(stack.OPTIONS, key=lambda k: stack.distribution(draws, k).median)
    for k in rows:
        d = stack.distribution(draws, k)
        lo, hi = d.band_90
        mark = "" if stack.OPTIONS[k].on_stack else "  (off stack)"
        print(f"  {stack.OPTIONS[k].label:<50}{d.median:>9,.0f}{lo:>10,.0f} - {hi:<7,.0f}{mark}")
    print()
    for t in (params.value("ca.colorado_cut"), params.get("ca.colorado_cut").high):
        _rule(f"Framing gate at a {t:,.0f} AF/yr cut")
        for comp in ("desal_israeli", "desal_permit_reform"):
            g = stack.gate(draws, comparator=comp, target=t)
            print(f"  vs {stack.OPTIONS[comp].label}")
            print(f"    P(reallocation cheaper)       {g.p_cheaper:.3f}")
            print(f"    P(ag capacity covers the cut) {g.p_capacity:.3f}")
            print(f"    -> row {g.row}: {g.verdict}")
    print()
    print("  Rule fixed before the first run (see ww/model/stack.py). Ag capacity is a")
    print("  LOW-confidence assumption; at 440k AF it sits on the row 1/2 boundary.")
    return 0


def register(sub: argparse._SubParsersAction) -> None:
    """Attach the Phase 2 commands to the main parser."""
    p_lcow = sub.add_parser("lcow", help="levelised cost of water for reference plants")
    p_lcow.add_argument("plant", nargs="?", help="carlsbad, sorek, huntington_beach, doheny")
    p_lcow.add_argument("--utilisation", type=float, default=1.0)
    p_lcow.set_defaults(func=cmd_lcow)

    p_gap = sub.add_parser("gap", help="scale-adjusted international capex comparison")
    p_gap.add_argument(
        "--include-conveyance",
        action="store_true",
        help="include Carlsbad's pipeline (overstates the gap; off by default)",
    )
    p_gap.set_defaults(func=cmd_gap)

    p_permit = sub.add_parser("permitting", help="price approval delay and rejection risk")
    p_permit.set_defaults(func=cmd_permitting)

    p_mc = sub.add_parser("montecarlo", help="LCOW as a distribution")
    p_mc.add_argument("-n", type=int, default=10_000)
    p_mc.add_argument("--seed", type=int, default=20260822)
    p_mc.add_argument("--utilisation", type=float, default=1.0)
    p_mc.set_defaults(func=cmd_montecarlo)

    p_defl = sub.add_parser("deflator", help="CPI-U table used to restate dollars")
    p_defl.add_argument("--rebuild", action="store_true", help="regenerate from the BLS cache")
    p_defl.set_defaults(func=cmd_deflator)

    p_salton = sub.add_parser("salton", help="Salton Sea externality attribution")
    p_salton.set_defaults(func=cmd_salton)

    p_stack = sub.add_parser("stack", help="Phase 3 supply stack and framing gate")
    p_stack.add_argument("-n", type=int, default=10_000)
    p_stack.add_argument("--seed", type=int, default=20261028)
    p_stack.set_defaults(func=cmd_stack)
