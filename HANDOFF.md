# HANDOFF — water_world

For the agent picking this up cold. [CLAUDE.md](CLAUDE.md) is the operational reference
(layout, commands, gotchas). **This document is the reasoning**: how the thesis got here,
what the owner has decided, what is still contested, and what to do next.

Read this first, then CLAUDE.md, then [PHASE0_FINDINGS.md](PHASE0_FINDINGS.md) when you
need the evidence itself.

> **STATUS, 2026-10-28: Phase 3 is done and the project is closing.** The owner chose to
> finish with the full supply stack (§4b) and then end the project with ONE deliverable:
> a long-form, data-driven article on ahdimel.com, co-authored by ahdimel and Claude. The
> model bill, legislator deck and Colorado submission are dropped. Comparators: Colorado
> and Israel only. SWRO flexibility and ship-mounted desal were cut from scope and are
> named in the article as open questions. Sections 4a and earlier are kept as history;
> where Phase 3 overturned them it says so in place.

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

**Phase 2 trimmed it, twice.** The engine (§4a) revised **the 5x gap down to ~4.2x** —
the rest was a conveyance artefact — and showed that **priced permitting risk explains
only about 1.38x of it**, leaving ~3x unattributed. Both v1 sentences above therefore
need care: "5x" should read ~4x, and "the residual is institutional" is still the best
available reading but is *not* the same claim as "the residual is permitting". Act III
survives, with a smaller headline and a more honest attribution.
Phase 2 also **retired the ~$3,500/AF Carlsbad figure** used in v0 above: SDCWA's own
number is $2,302–2,559/AF. Every ratio quoted against $3,500 shrinks accordingly — v0's
"12x cheaper to pay farmers" ($3,500 against $280 direct fallowing) becomes **~8.7x**,
and against fallowing's *social* cost of $477/AF it is **~5.1x**, not 7.3x. Nothing in
Act II's conclusion changes, but the numbers in it do. Re-check any ratio in the older
documents that has $3,500 on one side.

---

## 3. What the owner has decided

| Decision | Choice |
|---|---|
| Thesis | Combined arc: mispricing → supply stack → 5x gap |
| Deliverables | ~~All four~~ → **one article on ahdimel.com, then close** (2026-10-28) |
| Framing (desal-forward vs fallowing-baseline) | **Decided by the model** — §4b |
| Comparators | **Colorado + Israel only** (2026-10-28) |
| Byline | "ahdimel and Claude" |

**Deliverables, original:** D1 HTML findings paper, D2 California desal procurement
model bill + memo, D3 legislator pitch deck, D4′ Colorado River submission. Only D1
survives, as the ahdimel.com article.

### The framing gate — the one rule not to break

The owner chose "let the model decide." **Do not write narrative that presumes a ranking**
until the Phase 3 supply stack exists with real uncertainty bands. Phase 0.5 vindicated
this: once the Salton Sea externality landed, the ranking became genuinely uncertain
rather than obvious. §3 of [REQUIREMENTS.md](REQUIREMENTS.md) has the decision table
mapping each possible model outcome to the argument the paper would then make.

This is also the main defence against motivated reasoning, which is a live risk — the
project now has both a stated prior *and* a preferred villain (permitting).

### Answered 2026-10-28

1. Comparator basins: **Colorado + Israel only.**
2. National affordability material: compresses to a single exhibit in the article
   (water bills vs CPI since 2000).

---

## 4. State: Phases 0, 0.5, 1 and 2 complete

Phase 1 built the data layer: 14 live key-free sources, all offline-testable. Phase 2
built the cost engine on top of it — see §4a, which is where the interesting results are.

**Verified from primary data:**

- **Both major reservoirs hit all-time lows in autumn 2026** (re-fetched 2026-10-28,
  data to 10-27). Mead's lowest reading ever is 2026-10-22 (6.78 MAF, 22.7% of its 1942
  peak) and it is still near there. Powell's lowest since first filling is 2026-09-15
  (5.07 MAF); a freak October storm (San Juan River flooding, ~65,000 cfs inflow on
  Oct 20-22, second-highest October on record) has since lifted it ~10 ft to 5.84 MAF,
  still ~23% full — "a drop in the bucket" per hydrologists. Do not write "still
  falling" for Powell. The August claim ("six lowest readings are the last six days")
  is stale.
- **The water-price claim, re-verified against BLS directly:** +207% water/sewer/trash vs
  +92% CPI, Jan 2000 – Dec 2025. A 60% real increase.

**A test caught an error in our own arithmetic.** The fallowing social-cost band had been
built by adding the externality's *range* to the direct cost's *point* value. Correct band
is 380–575, not 420–535. This is the intended behaviour of `tests/test_params.py`, which
re-derives every `confidence: derived` parameter from its components — **keep that pattern
when adding derived numbers.**

---

## 4a. Phase 2 — the cost engine, and what it did to the thesis

The engine is built (`ww/model/`), 148 tests pass, and it **validates against two
published figures it was never fitted to**: Carlsbad lands at $2,456/AF against SDCWA's
reported ~$2,430 (1.1% error), and Sorek's fixed tariff leg at $0.244/m3 against a
published $0.25. Those two numbers come from opposite ends of the world through the same
code, which is the main reason to trust anything below.

**Phase 2 was harder on the thesis than Phase 0.5 was.** Four results, all pinned by
tests so a later edit cannot quietly improve them:

1. **The 5x is really about 4.2x.** Carlsbad's financing included a separate $203M bond
   for a 10-mile pipeline. Sorek's $489M capex contains no equivalent — Israel books
   grid connection separately, at $0.04-0.30/m3 depending on the plant. Comparing
   Carlsbad-with-pipeline against Sorek-without gives 5.3x; like-for-like gives **4.23x**
   at the central exponent, 3.99-4.77x across the 0.75-0.9 sensitivity. The headline was
   partly a conveyance artefact. **Use ~4x, and say why it moved.**

2. **The preferred villain explains under half the gap.** Priced properly — development
   capital at risk, compounded over the approval period, divided by the success
   probability — California's regime adds 1.45x to capex against a reformed 1.05x. That
   is ~1.38x of a 4.23x gap. **About 3x survives complete permitting reform.** Reform is
   still worth ~$428/AF (15% of the water price), which is a real legislative prize and
   enough to carry D2/D3. But the sentence "permitting explains the 5x gap" is now
   *false by our own model* and must not appear in the paper.
   Caveat in the other direction, and it is a real one: this is a **lower bound**. It
   prices only projects actually attempted. It cannot see the projects never proposed
   because the risk was obvious in advance, and that deterrence effect is plausibly
   larger than the priced one.

3. **Two more rival explanations died, which is good for Act III.** Sorek is 80% geared,
   Carlsbad 80.9% — capital structure is not the difference, exactly as take-or-pay was
   not. And Carlsbad drew through an *open* intake and discharged through the
   *co-located* Encina outfall: on the WateReuse figures those are the two cheapest
   options available (a power-plant outfall is $0.2-0.6M/MGD against $2.0-5.5M for a new
   diffuser outfall). So the mandated-subsurface-intake hypothesis cannot explain
   Carlsbad's gap. Doheny is the case where that mandate actually binds — and Doheny
   still prices *below* Carlsbad at a tenth the scale.

4. **The $3,500/AF headline did not survive contact with primary sources.** SDCWA's own
   figure, via the UC Davis review, is **$2,302-2,559/AF**, which independently
   corroborates the Surfrider reading of the Water Purchase Agreement ($2,290/AF). The
   modelled utilisation wedge — fixed costs spread over the 48,000 AF take-or-pay
   minimum instead of 56,050 nameplate — is only about **1.09x**, which gets to ~$2,680,
   not $3,500. So under-delivery is part of the story but not all of it. **That
   reconciliation is unfinished and the $3,500 figure should not be used as the headline
   comparator until it is.**

### The methodological trap Phase 2 walked into, and how it was handled

The obvious move was to treat "the US just builds everything more expensively" as a
rival hypothesis, subtract it, and claim the remainder for permitting. **That would have
been double-counting.** The literature on American construction costs (Urban Institute,
Construction Physics) attributes the premium primarily to administrative overhead,
procurement practice and non-standard design — and notes that US *low-oversight*
construction is internationally competitive. Those are the same mechanisms Act III
blames. The premium is not a rival to the institutional story; it is largely a restatement
of it.

So the engine reports **one combined institutional residual** and states explicitly that
the split between "permitting duration and risk" and "general US administrative
construction premium" is **not identified** by our data. `scale.decompose` is written to
make the honest version the easy one. Do not undo this to get a sharper headline.

### Useful things the sourcing pass turned up

- **A documented start date for Carlsbad**: Poseidon's CEO, at financial close — "We
  began developing this project in 1998." The UC Davis review agrees. So 1998 to full
  permitting and financial close in Dec 2012 is 14.5 years; to operation, 17.5.
- **The natural experiment at the centre of Act III**: Huntington Beach also began in
  1998, same developer, same state, same 50 MGD nameplate — and was unanimously denied
  in 2022 after ~$100M of development spend. Whatever explains the difference between
  the two, it is not technology, scale, or vintage.
- **IDE Technologies built Sorek AND designed and operates Carlsbad.** The same firm,
  both plants. That badly weakens any "engineering capability" explanation for the gap.
- **Israeli construction is a solved 2-3 year exercise** (Ashkelon 2003-05, Palmachim
  2005-07, Hadera 2007-09, Sorek 2.5 years). The schedule difference between the
  countries is almost entirely *pre-construction*.
- **The Israeli WDA publishes tariffs split fixed/variable** (Sorek $0.25 + $0.27).
  That split is what lets the capex gap be separated from the energy-price gap — and it
  matters, because California industrial power runs ~2x Israel's.

---

## 4b. Phase 3 — the supply stack, and what the gate said

Built 2026-10-28. `ww/model/deflate.py`, `ww/model/salton.py`, `ww/model/stack.py`;
CLI `ww deflator | salton | stack`; tests in `tests/test_phase3.py` (180 total pass).
Every option is priced in **2025 dollars**, **delivered treated into the Southern
California system**, on **public finance** (100% debt, 4%, 30 yr — Metropolitan's own
convention for Pure Water).

**The stack (medians, 90% bands, n=10,000):**

| Option | $/AF |
|---|---|
| Paying farmers, delivered, dust mitigated | **1,134** (791–1,475) |
| Stormwater capture | 1,397 (880–1,980) |
| Urban conservation (landscape-led) | 1,423 (907–2,156) |
| *Imported water today (MWD treated rate, reference)* | *1,481* |
| Desal at Israeli capex, built in California | 1,788 (1,614–1,976) |
| Desal, permitting reformed | 2,294 (2,027–2,527) |
| Desal at Carlsbad cost, public finance | 2,653 (2,461–2,854) |
| *Desal as built (Carlsbad, private finance)* | *3,043* |
| *Paying farmers, dust NEVER controlled* | *3,916* (2,975–5,026) |
| Potable reuse, Pure Water SoCal | 5,677 (5,242–6,445) |

**The gate (rule fixed before the first run; see the stack.py docstring).** Reallocation
beats even the Israeli-cost desal counterfactual with P = 0.999. Whether ag capacity alone
covers California's 440,000 AF/yr cut is a **coin flip** — exact P = 0.5007, which puts
it on the row 1 / row 2 boundary, and the gate says so rather than reporting the side the
noise fell on. At the extreme cut (1.056 MAF) it is **decisively row 2: cheap but
capped.** So the paper argues REQUIREMENTS row 2, with the caveat that at today's cut
the ceiling is roughly the size of the need. Conservation and stormwater are also below
any desal: options cheaper than Israeli-cost desal total ~1.24 MAF median and cover the
440k cut in 98% of draws; at 440k the marginal acre-foot is never desal.

**Six corrections to earlier phases, each pinned by a test:**

1. **The "12x" was river water against tap water.** Phase 0 priced fallowing at the
   river and desal delivered. Delivered treated, paying farmers is $402 (payment) +
   $675 (getting it to the coast) + $72 (dust) = ~$1,150. Against Carlsbad as built
   that is ~2.6x, against Israeli-cost desal ~1.6x. **Conveyance is the biggest line.**
2. **The $477/AF "social cost of fallowing" used the wrong district.** The Salton Sea
   dust cost belongs to Imperial Valley water; Palo Verde drains back to the river.
3. **The Salton externality, attributed:** $253 (full, 2025$) → $153 after the QSA's 61%
   share of the inflow decline → **$115** after a 75% dust share of spend. IID's shift to
   efficiency does NOT remove it (efficiency cuts drain flow too). Unmitigated, the
   damage basis is **~$4,500/AF** — at which paying farmers loses to every reformed desal.
   The whole reallocation case rests on the state building the dust control it owes.
4. **$3,500 is reinstated.** Phase 2 retired it by comparing it with older nominal
   figures. The 2012 contract price is ~$3,210 in 2025 dollars; the model at the
   take-or-pay minimum gives ~$3,330. The engine now validates against FOUR figures in
   their own dollar years (2012 contract, 2013 projection, today's ~$3,500, Sorek 2013).
   Phase 2's 1.1% match was partly two vintage errors cancelling.
5. **The gap in 2025 dollars is 4.13x** (3.89–4.65x); permitting still explains 1.38x;
   ~3x is still unexplained. Permitting reform is worth ~$576/AF on private finance.
   Public finance alone takes Carlsbad from ~$3,040 to ~$2,650.
6. **Potable reuse is now the most expensive option.** Pure Water SoCal at Metropolitan's
   own published $5,200/AF (30-yr basis) costs more than Carlsbad. Its capex is ~$75M per
   MGD against Carlsbad's ~$27M, both including conveyance (2025$). **The Californian premium is not desal-specific** —
   which supports the "combined institutional residual" reading in §4a.

**Weakest inputs, in order:** `ag.conservation_capacity` (decides row 1 vs 2; an
assumption anchored on one programme), the urban quantities (`*.quantity_socal`, both
assumptions), `salton.dust_share_of_spend` (our allowance), and the conveyance band
($179 power-only to $1,215 full wheeling — the widest single term in delivered ag cost).

---

## 5. What is contested — handle with care

Ranked by how much damage being wrong would do:

1. **`salton.externality` (~$140–255/AF)** — *superseded in Phase 3 by
   `salton.externality_attributed` (~$115/AF in 2025$, §4b). Kept as history:* the most load-bearing *and* most contested
   number in the project. It assumes all QSA transfer drives playa exposure and all
   restoration spend is dust-driven. Neither is strictly true: IID shifted from fallowing
   to efficiency measures around 2012, some exposure would have happened anyway, and
   restoration ≠ dust mitigation. **If the attributable share is much smaller,
   reallocation dominates again and Act III loses its urgency.** Build a real attribution
   model in Phase 2; do not let the current figure carry a conclusion unsensitised.
2. **The gap is a residual, not a measurement — and Phase 2 tested it.** Partly
   resolved, partly worse. Resolved: it is ~4.2x not 5x once conveyance comes out;
   mandated intakes cannot explain Carlsbad (it used the cheap open intake and a
   co-located outfall); capital structure cannot explain it (80.9% vs 80% gearing).
   Worse: **priced permitting risk only accounts for ~1.38x of the 4.23x**, so ~3x is
   still unexplained by anything we have named. The residual remains a residual. Do not
   let the paper imply otherwise, and see §4a on why the US-construction-premium
   hypothesis is not an independent rival that can be subtracted.
3. **`econ.capex_scaling_exponent` (0.8) drives the 5x headline.** Always report with the
   0.75–0.9 sensitivity. A test enforces the result survives both extremes.
4. **REVERSED IN PHASE 3: $3,500 is today's price (§4b item 4).** What Phase 2 said:
   ~~checked in Phase 2, and it did not hold up.~~ SDCWA's own figure is $2,302-2,559/AF, which
   independently corroborates the Surfrider reading of the WPA ($2,290/AF) and the
   model's own $2,456/AF. The $3,500 press figure is ~1.44x that, and the modelled
   utilisation wedge only accounts for ~1.09x. **Use `desal.carlsbad.price_sdcwa` as the
   comparator**; keep $3,500 in the file, flagged, until the remainder is explained.
5. **SWRO flexibility is an open question, not a settled one.** The literature splits, and
   the split is explained by system boundary: a water tank beats a battery ~6:1 per unit
   of energy shifted, but idling strands RO capex. The binding term is capacity-factor
   utilisation. An SWRO-specific model would resolve a real disagreement — that is why it
   survives as a secondary contribution rather than being cut.

---

## 6. What is left

**The article — "The Price of Water"** — the project's only deliverable. Source is
`ww/article/` (`template.html` = the prose with `$placeholders`, `figures.py` = every
number, computed from the model with a fixed seed, `charts.js` = 9 client-side charts,
`basemap.py`/`basemap.json` = Natural Earth geometry, generated once and committed).
`python -m ww article` writes `docs/article.html` (committed); the build fails if the
prose asks for a number the model does not provide. ahdimel.com imports it with
`tools/import_water_article.py` (reads HEAD, so commit first) to `/water/`. To change a
sentence, edit the template; to change a number, fix the model or literature.yaml and
rebuild — never hand-edit numbers in the HTML. A literal `$` in the prose is `$$`.

Deliberately NOT done, named in the article as open questions: SWRO flexible operation,
ship-mounted desal, an ENR-based construction deflator (CPI-U is used; it understates
post-2020 construction inflation), a Salton attribution that uses bathymetry rather than
inflow shares, and the Israeli variable-leg overshoot (still pinned, still not tuned).

If CAISO hourly prices are ever needed, `ww/sources/caiso.py` is implemented and tested
but registers no windows by default. Use `caiso.make_window()`.

---

## 7. Traps that have already bitten

- **Never compare water at the river with water at the tap.** Phase 0's "12x" did. Any
  Colorado River option needs `conveyance.colorado_to_coast` before it meets desal.
- **Never compare dollar figures without their years.** Phase 2 retired a correct price
  this way. Every dollar parameter carries `year:`; `deflate.real()` refuses one that
  does not.
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
