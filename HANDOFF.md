# HANDOFF — water_world

For the agent picking this up cold. [CLAUDE.md](CLAUDE.md) is the operational reference
(layout, commands, gotchas). **This document is the reasoning**: how the thesis got here,
what the owner has decided, what is still contested, and what to do next.

Read this first, then CLAUDE.md, then [PHASE0_FINDINGS.md](PHASE0_FINDINGS.md) when you
need the evidence itself.

---

## 1. Where this came from

The owner was reading about the Colorado River crisis — reservoirs at record lows while
alfalfa is grown in the desert and exported — and the contradiction started the project.
That framing is worth keeping in view: **the project began from an observed absurdity, not
from a literature gap.**

The owner is an engineer who models things for himself, works in phases, and expects
analysis rather than recommendations. He states his priors openly (he believes markets
price scarcity better than the current US water regime) and has been explicit that he
wants the work **grounded in reality before any framing or recommendation comes out of
it.** Treat that as the governing standard. He has twice accepted findings that went
against his stated position; do not soften results to fit the prior.

---

## 2. The thesis, and the two times it changed

**v0 (owner's opening idea).** Water is mispriced; the Colorado basin will mismanage
itself into collapse; desalination becomes viable because solar is nearly free at midday
and a desal plant with a big reservoir can chase cheap electrons — storing water instead
of electricity. Intended output: findings paper plus an investor pitch deck.

**Phase 0 killed it.** Three independent lines of evidence:

- Desal is capex-dominated, so idling to chase cheap power strands RO trains. The energy
  saving is smaller than the capex penalty.
- Published work already covers flexible operation: **zero saving under current tariffs,
  16% under aggressive real-time pricing, 47% only if the plant is purpose-built for
  cycling** — and that study is *brackish*, which is less capex-heavy than seawater, so
  it is an optimistic bound for our case.
- Worse for the thesis: **paying farmers to stop is ~12x cheaper than desalinating.**
  Palo Verde fallowing works out to ~$280/AF against Carlsbad's ~$3,500/AF.

**v1 (re-aim).** The owner chose a combined arc: **mispricing → supply stack → the 5x
gap.** The interesting finding was no longer "desal wins" but that **California builds
desal at ~5x Israeli cost after adjusting for scale, and the residual is institutional.**
That makes the fix legislative, not entrepreneurial — which is why the deliverables are
policy artifacts rather than a startup pitch.

**Phase 0.5 reshaped it again.** The Salton Sea dust liability is a *socialised*
externality: under the 2003 QSA the water agencies' liability is capped at $133M and
**California is the statutory backstop for everything beyond.** Costing it out adds
~$140–255/AF to transferred water, taking fallowing from ~$280/AF to **~$477/AF
(380–575)** — which **overlaps Sorek-cost desalination at ~$505–715/AF.**

**Consequence: Act III went from decorative to decisive.** Reallocation's 12x advantage
survives only against *unreformed* desal. Whether California can close the 5x gap now
determines whether desal is competitive at all.

**The unifying insight, and the best line in the project:** Act II's cheap alternative is
cheap for *exactly the same reason* Act I's agricultural water is cheap — the cost sits
with the public rather than the buyer. The mispricing thesis applies to the remedy as
well as to the disease.

---

## 3. What the owner has decided

| Decision | Choice |
|---|---|
| Thesis | Combined arc: mispricing → supply stack → 5x gap |
| Deliverables | **All four** — see below |
| Framing (desal-forward vs fallowing-baseline) | **Deferred to the model.** Explicitly. |

**Deliverables:** D1 HTML findings paper (GitHub Pages), D2 California desal procurement
model bill + memo, D3 legislator pitch deck, D4′ Colorado River submission at the next
operating-guidelines cycle.

### The framing gate — the one rule not to break

The owner chose "let the model decide." **Do not write narrative that presumes a ranking**
until the Phase 3 supply stack exists with real uncertainty bands. Phase 0.5 vindicated
this: once the Salton Sea externality landed, the ranking became genuinely uncertain
rather than obvious. §3 of [REQUIREMENTS.md](REQUIREMENTS.md) has the decision table
mapping each possible model outcome to the argument the paper would then make.

This is also the main defence against motivated reasoning, which is a live risk — the
project now has both a stated prior *and* a preferred villain (permitting).

### Still unanswered — ask before assuming

1. Comparator basins (Spain, Israel, Murray–Darling) in the paper, or Colorado-only?
2. How much of the national water-affordability material survives into D1 versus
   compressing to a single exhibit?

---

## 4. State: Phases 0, 0.5 and 1 complete

Phase 1 built the data layer. 76 tests pass, all offline. 14 live key-free sources.

**Verified from primary data:**

- **Both major reservoirs are at all-time lows and still falling.** As of 2026-08-21 the
  six lowest readings in each record are the last six days. Mead at 23% of its historic
  maximum, Powell at 20% (excluding its 1963 filling). The owner already knew this — it
  is what started the project — but it is now sourced from USBR rather than journalism.
- **The water-price claim, re-verified against BLS directly:** +207% water/sewer/trash vs
  +92% CPI, Jan 2000 – Dec 2025. A 60% real increase.

**A test caught an error in our own arithmetic.** The fallowing social-cost band had been
built by adding the externality's *range* to the direct cost's *point* value. Correct band
is 380–575, not 420–535. This is the intended behaviour of `tests/test_params.py`, which
re-derives every `confidence: derived` parameter from its components — **keep that pattern
when adding derived numbers.**

---

## 5. What is contested — handle with care

Ranked by how much damage being wrong would do:

1. **`salton.externality` (~$140–255/AF).** The most load-bearing *and* most contested
   number in the project. It assumes all QSA transfer drives playa exposure and all
   restoration spend is dust-driven. Neither is strictly true: IID shifted from fallowing
   to efficiency measures around 2012, some exposure would have happened anyway, and
   restoration ≠ dust mitigation. **If the attributable share is much smaller,
   reallocation dominates again and Act III loses its urgency.** Build a real attribution
   model in Phase 2; do not let the current figure carry a conclusion unsensitised.
2. **The 5x gap is a residual, not a measurement.** We showed a gap survives scale
   adjustment; we have *not* shown what fills it. Attributing it to permitting is a
   hypothesis. If US construction premium and mandated subsurface intakes explain most of
   it, the legislative recommendation weakens badly. §2.2 of REQUIREMENTS exists to test
   this, not to assume it.
3. **`econ.capex_scaling_exponent` (0.8) drives the 5x headline.** Always report with the
   0.75–0.9 sensitivity. A test enforces the result survives both extremes.
4. **`desal.carlsbad.price_current` ($3,500/AF) is low-confidence** and is the headline
   comparison figure. Confirm against SDCWA primary documents before publication.
5. **SWRO flexibility is an open question, not a settled one.** The literature splits, and
   the split is explained by system boundary: a water tank beats a battery ~6:1 per unit
   of energy shifted, but idling strands RO capex. The binding term is capacity-factor
   utilisation. An SWRO-specific model would resolve a real disagreement — that is why it
   survives as a secondary contribution rather than being cut.

---

## 6. Phase 2 — the next block of work

**Desal cost engine.** Parameterised techno-economic model reading from
`data/parameters/literature.yaml`:

- LCOW with capex, SEC, O&M, membrane replacement, brine disposal, and financing —
  financing is often the largest single line for a capex-heavy asset, so do not fold it
  into a hand-waved discount rate.
- **Scale-adjusted international comparison** with the exponent sensitivity built in.
- **Permitting-risk module — the novel contribution.** Price approval delay and rejection
  probability as a financial instrument. Huntington Beach ran 24 years and was rejected
  unanimously; the capital returned zero. Model as expected-NPV / real-option over
  approval duration and success probability, calibrated against the observed California
  project population. The output should be a sentence a legislator can act on: *"cutting
  approval time from 15 to 4 years and rejection risk from 40% to 5% lowers water cost by
  $X/AF."*
- **Monte Carlo over the ranges in literature.yaml** — a distribution, not a point
  estimate. `params.band()` exists for exactly this and degrades safely for range-less
  parameters.
- Salton Sea attribution model (see §5.1).
- Ship-mounted desal as a bounded extension. It exists at emergency scale (Saudi barges
  since 2008, NIOT Chennai 2007), so the question is why it never scaled. **Cite operating
  plants only** — this space attracts vaporware; one heavily-promoted concept was debunked
  in 2026 with doubts the vessel exists.

If CAISO hourly prices are needed, `ww/sources/caiso.py` is implemented and tested but
registers no windows by default — a year is ~12 chunked queries against a throttled
endpoint. Use `caiso.make_window()` and decide deliberately how much history to pull.

**Then Phase 3** (supply stack, and the framing gate opens), **Phase 4** (D1),
**Phase 5** (D2/D3).

---

## 7. Traps that have already bitten

- **Never cite Fondomonte/Butler Valley as a Colorado River example.** That is Arizona
  *groundwater* and those leases were cancelled in 2023. Fondomonte's **Palo Verde Valley**
  operation is Colorado River water — use that one. Getting this wrong would discredit the
  most vivid example in the paper.
- **Take-or-pay is not the villain.** Israel uses it too and gets $0.58/m³. It is what
  makes cheap non-recourse project finance possible. The difference is permitting risk and
  standardisation. An earlier draft got this backwards.
- **Do not compare desal to agricultural water rates.** Desal will never beat $20/AF and is
  not meant to. The buyer is a city facing its marginal supply cost. That ~100x spread is
  the *mispricing argument*, not a refutation of desal.
- **D4 was missed.** The Colorado post-2026 Record of Decision issued 21 Aug 2026, one day
  before we checked; the comment window had closed in March. D4′ targets the next
  guidelines cycle under the 2027–2036 framework. **No deadlines remain anywhere in the
  project** — do not manufacture urgency.
- **BLS blocks `download.bls.gov` without a contact email in the User-Agent.** We
  deliberately use the key-free API instead so no personal data goes to a third party.
  Do not "fix" this by hardcoding the owner's email.
- **CAISO stores the price in a column named `MW`.** An OASIS artefact, not a bug.

---

## 8. Standing instructions

- Every number gets a citation and, wherever possible, a range. `python -m ww params
  --audit` reviews uncited, low-confidence, and point-estimate parameters.
- Derived parameters get a test that re-derives them from components.
- Report findings that go against the thesis as findings. The owner has taken three such
  results without complaint and the project is better for each one.
- The owner asked for plain language when jargon accumulates. Phases and gates confused
  him once; if a term is load-bearing, define it in a line.
