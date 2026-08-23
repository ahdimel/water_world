# water_world — Requirements & Scope (v2, re-aimed)

**Status:** scoping. Phase 0 desk-check complete — see [PHASE0_FINDINGS.md](PHASE0_FINDINGS.md).
**Date:** 2026-08-22
**Supersedes:** v1 (desal-merchant framing, retired after Phase 0)

---

## 1. Thesis

> **Water in the American West is allocated by right rather than price. Correct pricing would
> buy the cheap options first — and the expensive option we actually build costs five times
> what it should, for reasons that are institutional rather than physical.**

Three acts, each independently falsifiable:

**Act I — The mispricing.** Allocation and tariffs were set when rivers were not under
pressure. Physical scarcity changed; the price signal did not. Agricultural water is frozen in
nominal terms (~$20/AF at IID) — *falling* in real terms — while urban ratepayers absorbed a
207% increase against 93% inflation since 2000. Neither price encodes scarcity: the urban rise
is pipes-and-treatment cost recovery, not a scarcity signal. The burden is being redistributed
toward the small user rather than aimed at the large one.

**Act II — The supply stack.** If water were priced correctly, the options would be bought in
cost order. Empirically they are not. Anchors after Phase 0.5: fallowing/transfer ~$280/AF
direct but **~$477/AF (380–575) once the socialised Salton Sea dust externality is
internalised**;
Sorek-cost desalination ~$505–715/AF; Carlsbad desalination ~$3,500/AF *(revised by
Phase 2 to **$2,302–2,559/AF** — see HANDOFF §4a)*. Those ranges **overlap**
— reallocation's apparent 12x advantage over desal survives only against *unreformed* desal.
**The ranking that comes out of the model — not our prior — determines the paper's framing**
(see §3).

The unifying observation: Act II's cheap alternative is cheap for **the same reason** Act I's
ag water is cheap — California is the statutory backstop for Salton Sea restoration, so the
cost is pushed onto the public rather than the buyer. The mispricing thesis applies to the
remedy as well as the disease.

**Act III — The 5x gap.** *(Promoted to decisive by Phase 0.5: since internalising the Salton
Sea externality brings reallocation and reformed desal to rough parity, whether California can
close this gap now determines whether desalination is competitive at all.)* After adjusting for
scale, California builds desalination at ~5x
Israeli cost, consistently across plants differing 10x in size. The residual is permitting
duration, rejection risk, and bespoke one-off procurement — not engineering. Israel and
California use the *same* take-or-pay contract structure; the difference is that Israel
pre-permits, standardises, and repeats. **That makes the fix legislative rather than
entrepreneurial**, which is why this project ends in policy artifacts rather than a startup
pitch.

### Explicit normative prior

The project argues from the position that markets price scarcity better than the current US
water regime. This is stated openly rather than smuggled in, and the analysis must be capable
of returning results against it — see the motivated-reasoning risk in §7.

---

## 2. The two novel contributions

Most of this project is synthesis. Two pieces appear to be genuinely new and should carry the
weight:

### 2.1 Scale-adjusted international capex decomposition

Nobody appears to have stripped scale economies out of the Israel/California desalination cost
gap and attributed the residual. Phase 0 gets ~5x across two plants an order of magnitude apart
in size. Publishing that decomposition, with a sensitivity on the scaling exponent, is a
contribution on its own.

### 2.2 Permitting priced as a financial instrument

Huntington Beach ran **24 years** and was unanimously rejected; the capital returned zero. A
project facing a long approval with material rejection probability carries an implied
risk-adjusted discount rate, and that premium can be converted into $/AF of delivered water.

This turns "permitting is slow" into a number, and yields the sentence a legislator can act on:

> *Cutting approval time from 15 years to 4 and rejection risk from 40% to 5% lowers the cost of
> desalinated water by $X per acre-foot.*

Model as a real-option / expected-NPV problem over approval duration and success probability,
calibrated against the observed California project population (Carlsbad, Huntington Beach,
Doheny, and the other projects in the UC Davis four-project comparison).

---

## 3. The framing gate

**Decision deferred to the model, by explicit choice.** The desal-vs-reallocation tension is not
pre-judged. Phase 3 builds the supply stack with honest uncertainty bands, and the resulting
ranking decides which of these the paper argues:

| If the model shows | The paper argues |
|---|---|
| Reallocation dominates across its plausible range, with a hard ceiling | Fallowing is the baseline; desal is the backstop for what reallocation cannot reach, and it should cost ~$700/AF not $3,500 |
| Reallocation is cheap but tightly capped | The ceiling *is* the story; desal's institutional cost gap becomes urgent because the backstop arrives sooner |
| Uncertainty bands overlap substantially | Portfolio framing: the ordering is genuinely uncertain and the policy value is in preserving optionality — and in not paying 5x for the expensive option regardless |

No narrative gets written before Phase 3 completes. This is a real gate, not a formality.

---

## 4. Deliverables

All four are in scope.

| # | Artifact | Audience | Depends on |
|---|---|---|---|
| **D1** | **HTML findings paper**, published to GitHub Pages | General / technical | Phases 1–3 |
| **D2** | **California desal procurement bill** — model bill + legislative memo: standardised state tender, pre-permitted priority sites, concurrent agency review, guaranteed offtake | CA legislators, Water Board staff | Act III + §2.2 |
| **D3** | **Legislator pitch deck** — short and visual: the 5x gap, what it costs ratepayers, the three changes that close it | CA legislators, agency staff | D2 |
| **D4′** | **Colorado River operating-guidelines submission**, aimed at the next cycle under the 2027–2036 framework | Interior / Reclamation | Acts I–II |

### D4 was missed; D4′ replaces it — and the clock is gone

Phase 0.5 established that the post-2026 process **concluded on 21 August 2026** with the
Record of Decision, one day before we checked. The comment period ran 16 Jan – 2 Mar 2026 and
drew 18,127 submissions. We missed it by five and a half months.

The ROD adopts a **Decision Framework for 2027–2036** and issued the first 2027–2028 Operating
Guidelines under it. Guidelines are issued in sets, so **recurring decision points exist** —
D4′ targets the next one, by which time the full supply-stack model will be ready.

**Consequence: there is no longer any deadline pressure anywhere in this project.** The
six-week crunch is gone, and D1 gains a sharp news hook instead — the guidelines were decided
this week, without seven-state consensus, after two years of failed negotiation. A paper on
what the new framework does and does not do about pricing lands into a live conversation.

D2/D3 never had a comparable clock; the Ocean Plan amendment process is ongoing.

---

## 5. Scope

### In

- **Act I:** ag vs. urban price divergence; real-terms analysis of both; demonstration that
  neither price encodes scarcity. US and California, with IID/MWD as the worked example.
- **Act II:** marginal cost curve for new water in Southern California — fallowing, deficit
  irrigation, recycling, stormwater, conservation, imported, desalination — with uncertainty
  bands.
- **Act III:** desalination techno-economic model; scale-adjusted international comparison;
  permitting-risk model; the counterfactual "reformed-procurement" cost point.
- **Colorado basin** as the physical setting: allocation structure, deliveries, reservoir
  trajectory, crop mix and crop water use.
- **Flexible operation** as a secondary margin-improver on the desal model, not the core thesis
  — SWRO-specific, replacing the brackish proxy.
- **Ship/barge desal** as a bounded section: it exists at emergency scale (Saudi barges since
  2008, NIOT Chennai 2007); the question is why it never scaled. Operating plants only — this
  space attracts vaporware.

### Out

- Global gridded hydrology.
- Basins beyond the Colorado, except as comparators (Israel, Spain, Murray–Darling).
- Plant process engineering. We model costs, not flowsheets.
- Partisan advocacy. D2–D4 argue from cost and mechanism, not political alignment.

### Must verify, never assume

- Salton Sea externality attribution — Phase 0.5 derived ~$140–255/AF, but that assumes all QSA
  transfer drives playa exposure and all restoration spend is dust-driven. Needs a proper
  attribution model: IID shifted from fallowing to efficiency measures ~2012, some exposure
  would have occurred anyway, and restoration ≠ dust mitigation.
- Length of the IID $20/AF nominal freeze.
- Service-cost vs. subsidy split in the ag/urban price gap.
- Fondomonte Palo Verde acreage and current status (**not** Butler Valley — that is groundwater
  and those leases are dead).
- ~~Carlsbad's current $3,500/AF figure against SDCWA primary documents.~~ **DONE in
  Phase 2 — it failed.** SDCWA's own figure is $2,302–2,559/AF. Use
  `desal.carlsbad.price_sdcwa`. See HANDOFF §4a.
- Capex scaling exponent sensitivity (0.75–0.9) on the 5x result.

---

## 6. Data sources

| Domain | Source |
|---|---|
| Basin allocation & deliveries | USBR Lower Colorado accounting reports; Law of the River |
| Post-2026 process | USBR Colorado River Post-2026 Operations; Lower Basin May 2026 proposal |
| Reservoir levels | USBR Mead / Powell historical elevation & storage |
| Crop acreage & water use | USDA NASS; USDA Irrigation & Water Management Survey; IID crop reports |
| Crop water footprints | Mekonnen & Hoekstra green/blue/grey |
| Ag vs. municipal rates | IID, MWD, SDCWA published rate schedules |
| Fallowing costs | PVID/Metropolitan land management program; Reclamation conservation agreements |
| Water price vs. income | Bluefield rate index; BLS CPI series; Census income; Cardoso & Wichman affordability work |
| Electricity price-duration | CAISO OASIS hourly LMP, SP15 |
| Desal plant costs | Plant financial disclosures; Carlsbad & Sorek public filings; Israeli Desalination Division; OECD financing materials; peer-reviewed TEA |
| CA permitting record | Coastal Commission records; State Water Board desal siting/streamlining report; UC Davis four-project comparison |
| Solar capex & LCOE | NREL ATB; Lazard LCOE |

---

## 7. Phases

### Phase 0 — Desk check ✅ complete
Recorded in [PHASE0_FINDINGS.md](PHASE0_FINDINGS.md). Killed the merchant-desal framing,
falsified the original pricing claim, corrected the alfalfa example, and produced the 5x result.

### Phase 0.5 — Gating questions ✅ complete
1. **D4 window** — closed 2 Mar 2026; ROD issued 21 Aug 2026. D4 → D4′, no deadline. ✅
2. **Salton Sea ceiling** — quantified at **~$140–255/AF** as a socialised externality on
   transferred water. Moves fallowing's true social cost to ~$477/AF (380–575), into overlap
   with Sorek-cost desal. ✅ **This changed the project's centre of gravity.**
3. **SWRO flexibility** — literature is *split*, and the split turns on RO capex utilisation.
   Revived as a genuine open question worth modelling as a secondary contribution. ✅

### Phase 1 — Evidence base
Reproducible fetch + normalise + cache layer. Everything downstream reads from a clean,
versioned local store. No analysis logic here.

### Phase 2 — Desal cost engine ✅ core complete
Built in `ww/model/`: LCOW with explicit financing, the scale-adjusted international
comparison with exponent sensitivity, the permitting-risk module (§2.2), and Monte Carlo.
Validates to ~1% against SDCWA's Carlsbad price and ~2% against Sorek's published fixed
tariff leg. **Results in [HANDOFF.md](HANDOFF.md) §4a — they cut the 5x headline to ~4.2x
and showed permitting explains only ~1.38x of it.**

Still open inside Phase 2: Salton Sea attribution model, the $3,500/AF reconciliation,
public-vs-private financing, SWRO flexibility, ship-mounted variant.

### Phase 3 — Supply stack  ← **framing gate (§3)**
Every marginal water option on one $/AF curve with honest uncertainty bands. The ranking that
emerges decides the paper's argument.

### Phase 4 — D1, the findings paper
HTML, charts, GitHub Pages.

### Phase 5 — D2, D3, policy artifacts
Model bill + memo, then the deck built from it.

*(D4 runs out-of-band on its own clock per §4.)*

---

## 8. Risks

- **Motivated reasoning.** The project starts from a stated prior and now also from a preferred
  villain (permitting). Both the 5x attribution and the supply stack must be able to come out
  against us and be reported that way. The framing gate (§3) exists partly to enforce this.
- **The 5x attribution is currently a residual, not a measurement.** We have shown a gap exists
  after scale; we have *not* yet shown what fills it. Attributing it to permitting is a
  hypothesis. If US construction premium and mandated intake technology explain most of it, the
  policy recommendation weakens considerably.
- **The Salton Sea attribution is the load-bearing assumption in Act II.** Phase 0.5's
  ~$140–255/AF is our own arithmetic over LAO figures, not a published number, and it is what
  brings reallocation and reformed desal to parity. If the true attributable share is much
  smaller, reallocation dominates again and Act III loses its urgency. **Sensitivity-test this
  before it carries any conclusion.**
- ~~D4 deadline risk~~ — resolved: the window closed and D4 became D4′. No deadline remains.
- **Desal cost data is commercially guarded** (GWI/DesalData paywalls). Triangulate from public
  filings and academic TEA.
- **Four deliverables is a lot.** D1 is the spine; D2/D3 derive from it cheaply. If scope has to
  give, D4 goes first, then D3.

---

## 9. Open decisions

1. Repo stack — assumed Python + HTML report per prior projects. Confirm.
2. Does the paper cover Spain/Israel/Murray–Darling as comparators, or stay Colorado-only?
3. How much of Act I's national affordability material survives into the paper vs. compresses
   into a single exhibit?
