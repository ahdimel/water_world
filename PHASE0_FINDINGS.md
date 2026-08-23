# Phase 0 — Desk-check findings

**Date:** 2026-08-22
**Status:** pre-pipeline gotcha check. Figures are from published/secondary sources and are
order-of-magnitude anchors, not audited data. Everything marked ⚠ needs primary-source
confirmation before it appears in the paper.

**Bottom line: the desal thesis is in serious trouble on cost, the pricing thesis needs
re-aiming, and a better investable thesis emerged from the wreckage.**

> ### ⚠ SUPERSEDED IN PLACES — read this before quoting any number below
>
> This document is the **Phase 0 record**, kept as written. Later phases corrected some
> of it. Do not lift figures from here without checking:
>
> - **Carlsbad at ~$3,500/AF is wrong.** Phase 2 checked it against primary sources:
>   SDCWA's own figure is **$2,302–2,559/AF**. Every ratio in this document with $3,500
>   on one side is overstated, including the "12x cheaper to pay farmers" comparison
>   (~8.7x against direct fallowing cost, ~5.1x against its social cost).
> - **The ~5x Israel/California capex gap is ~4.2x.** Carlsbad's $203M pipeline has no
>   counterpart in Sorek's capex; removing it drops the scale-adjusted gap from 5.3x.
> - **The fallowing social-cost band is 380–575, not 420–535** (corrected in Phase 1).
>
> The current state of every number is `data/parameters/literature.yaml`, and the
> reasoning is in [HANDOFF.md](HANDOFF.md) §4a. **That file, not this one, is
> authoritative.**

Unit note: 1 acre-foot (AF) = 1,233 m³.

---

## Finding 1 — The US water-price-vs-income claim is falsified as stated

The hypothesis was that US water prices have not kept pace with earnings — that water got
cheaper in real, income-relative terms even as it got scarcer.

For **residential** water, the opposite is true:

| Measure | Value |
|---|---|
| Water/sewer/trash price growth, Jan 2000 – Dec 2025 | **+207%** |
| Overall inflation, same period | **+93%** |
| 2025 household water & sewer bill increase | +5.1% (five-year high; +24.2% since 2020) |
| Households paying >4.5% of monthly income on water | **1 in 7** |
| Poorest decile share of monthly income | 8.1% |

Residential water has gotten *substantially* more expensive in real terms. There is a
recognized affordability crisis. Stated as written, the claim would not survive review.

### The corrected version is stronger

Two facts rescue and sharpen it:

1. **Agricultural water is flat in nominal terms — which is falling in real terms.** IID has
   charged farmers "the same rate for years: **$20/AF**." ⚠ Confirm the length of the freeze.
   Californian ag districts average **~$30/AF**; city utilities pay **~$512/AF** — a ~17x gap.
2. **The rising urban bill is not a scarcity signal.** It is cost recovery for pipes,
   treatment, and regulatory compliance. Nothing in it says "the river is running out."

So the revised thesis is not "water is too cheap for everyone." It is:

> **Households absorb steeply rising costs while the user consuming 70–80% of the water pays a
> nominally frozen price — and neither price encodes scarcity.** The burden is being
> redistributed toward the small user, not aimed at the large one.

That is more defensible *and* more damning than the original framing.

---

## Finding 2 — The alfalfa export example needs a different farm

The flag was correct. The famous Fondomonte case is **Butler Valley groundwater** on Arizona
state land — **not Colorado River water**. Arizona declined to renew three leases and cancelled
the fourth in Oct 2023; the company had stopped pumping there by Mar 2024. Using it as a
Colorado River example would be wrong on the facts and the leases are dead anyway.

**The fix:** Fondomonte *also* farms the **Palo Verde Valley** in Southern California, which is
supplied by the Colorado River. Same company, same crop, same export destination — correct
water source. Use Palo Verde. ⚠ Confirm current acreage and operational status.

---

## Finding 3 — Carlsbad costs ~5–7x Sorek, and the gap is institutional

The single most useful result of the check.

| Plant | Cost | $/AF equivalent |
|---|---|---|
| Sorek B (Israel, contracted) | $0.41/m³ | **~$505** |
| Sorek (Israel) | $0.58/m³ | **~$715** |
| Carlsbad, original contract (56k AF) | — | ~$2,041 |
| Carlsbad, original contract (48k AF min) | — | ~$2,290 |
| Carlsbad, what SDCWA pays today | ~$2.84/m³ | **~$3,500** ⚠ |

**Carlsbad water costs roughly five to seven times Sorek water using the same technology.**
That difference is not physics — it is permitting, environmental review, financing structure,
and contract terms.

Contract structure confirms outcome B is what actually happened in the real world: a 30-year
**take-or-pay** deal, minimum 48,000 AF/yr, ~$115M/yr, ~$3.5B over the term. SDCWA has been
billed ~$35M for water it did not take. This is a public-backstopped monopoly purchase, not a
merchant plant.

**Implication:** the interesting question is not "can desal get cheaper by chasing cheap
power." It is **"why does an American plant cost 5–7x an Israeli one, and is that gap
capturable?"** A private developer who closed even half of it would be at ~$1,700/AF without
touching the energy strategy.

---

## Finding 4 — The flexible-operation dark horse: real, quantified, and modest

Someone has already published the exact study — flexible operation of desalination in Southern
California (*Desalination*, 2026). Findings:

| Scenario | LCOW reduction |
|---|---|
| Current electricity tariffs | **none** |
| Aggressive real-time pricing tariff | up to **16.1%** |
| Plus plant *designed* for flexibility (larger feed pumps, lower minimum flow) | up to **47%** |

The supporting conditions are real: CAISO midday negative prices are growing and concentrated
in **SP15** (Southern California), with record curtailments March–May and midday net demand
down 45% since 2020.

**But the headroom is bounded.** SWRO practical SEC is 2.5–4.0 kWh/m³ against a thermodynamic
floor around 1–1.6 kWh/m³. Energy is not the dominant cost term, so squeezing it cannot move
the total the way the thesis needs.

**Verdict: the mechanism is real, and the intuition about storing water instead of electricity
is sound — but it is a 16–47% lever, not a step change.** Best case, it takes Carlsbad from
~$3,500/AF to ~$1,855/AF.

⚠ Major caveat: that study is **brackish** desalination, not seawater. Brackish is less
capex-intensive per m³, so the capacity-factor penalty is *smaller* there than it would be for
SWRO. The 16–47% figures are therefore probably an **optimistic** bound for our case. This
needs its own SWRO-specific modelling.

---

## Finding 5 — Outcome D dominates on cost by roughly 12x

The test: what does it actually cost to pay a farmer to stop, versus to desalinate?

Palo Verde Valley fallowing programme (PVID / Metropolitan / Reclamation, 2023 agreement):

| Quantity | Value |
|---|---|
| Land fallowed | ~26,000 acres (~30% of the valley) |
| Water conserved | 117,000 AF/yr |
| Implied water per acre | 4.5 AF/acre |
| Entry payment | $3,170/acre (one-time) |
| Annual payment | ~$800/acre, escalating |

Derived cost of conserved water:

```
annual payment      $800/acre ÷ 4.5 AF/acre           = ~$178/AF/yr
entry, amortised    $3,170/acre @ 7% over 10y (CRF .142)
                    = $451/acre/yr ÷ 4.5 AF/acre      = ~$100/AF/yr
                                                        ----------
                    total                               ~$280/AF
```

| Supply option | $/AF |
|---|---|
| Paying farmers to fallow (PVID) | **~$280** |
| Sorek-cost desal, if achievable in CA | ~$505–715 |
| Best-case flexible desal from Carlsbad baseline | ~$1,855 |
| Carlsbad desal, actual | ~$3,500 |

**Fallowing is ~12x cheaper than Carlsbad desal, and ~6.7x cheaper than the most optimistic
flexible-desal case.** This is the strongest quantitative result of the check and it points
away from outcome A.

It also directly vindicates the project's own free-market premise: price water properly and the
first thing that happens is alfalfa fields going idle, not desal plants getting built.

### What could still cap fallowing

Fallowing is cheap but not unbounded, and the ceiling is where desal re-enters:

- **Salton Sea.** IID conservation shrinks the sea and exposes playa, creating dust and
  air-quality liability. This is a real, costed constraint on how far Imperial conservation can
  go. ⚠ Needs quantifying — it may be the single most important number for outcome A.
- Rural community and local economy effects — 30% of a valley is already fallowed.
- Food production and political limits on how much farmland can be idled.
- Fallowing conserves existing supply; it does not add new supply. It buys decades, not
  permanence.

---

## Finding 6 — Ship-based desal exists, at emergency scale

The assumption that it does not exist at scale was half wrong.

**Real precedents:** Saudi barge-mounted plants operating since 2008 — moored at Shuaibah, moved
to Shuqaiq in 2009, then to Yanbu-Madinah in 2011. The relocations are the interesting part:
they demonstrate the mobility option in practice. India's NIOT commissioned a barge-mounted
prototype off Chennai in 2007.

**Caution:** at least one heavily-promoted recent floating-desal concept (*Aqua Solaire*) was
debunked by desalination experts in 2026, with doubts the vessel exists at all. This space
attracts vaporware — cite operating plants only.

**Revised question:** not "is it possible" (it is) but "why has it stayed at emergency scale for
18 years?" That is a more informative question, and the answer probably lies in shore
interconnection, berth costs, and onboard power economics.

---

## Finding 7 — What "build at Israeli capex rates" actually means: a ~5x institutional gap

Capital cost per unit of daily capacity, the cleanest way to compare plants:

| Plant | Capex | Capacity (m³/day) | **$ per m³/day** |
|---|---|---|---|
| Sorek (Israel, 2013) | $489M | 624,000 | **$784** |
| Carlsbad (CA, 2015) | $1.0B | 189,270 (50 MGD) | **$5,283** |
| Huntington Beach (CA, *rejected 2022*) | $1.4B | 189,270 (50 MGD) | **$7,397** |
| Doheny (CA, Ocean-Plan-compliant) | $140M | 18,927 (5 MGD) | **$7,397** |

Raw gap: Carlsbad is **6.7x** Sorek per unit capacity.

### Stripping out scale

Sorek is 3.3x larger than Carlsbad, so some of the gap is ordinary economies of scale. Using a
standard capex scaling exponent of 0.8 (capex ∝ Q^0.8, so capex per unit ∝ Q^−0.2):

```
Carlsbad vs Sorek:  scale factor 3.30^0.2 = 1.27
  Sorek cost re-based to Carlsbad's size: $784 × 1.27  = ~$996 /m³/day
  Carlsbad actual                                       = $5,283 /m³/day
  → residual gap                                        = 5.3x

Doheny vs Sorek:    scale factor 32.97^0.2 = 2.01
  Sorek cost re-based to Doheny's size:  $784 × 2.01   = ~$1,578 /m³/day
  Doheny actual                                         = $7,397 /m³/day
  → residual gap                                        = 4.7x
```

**Two plants that differ 10x in size both land at a residual gap of roughly 5x.** That
consistency is the strongest signal in this whole check: scale explains only ~1.3–2x of the raw
difference. **After scale, California builds desalination at about five times Israeli cost, and
that residual is institutional.**

⚠ The 0.8 exponent is a literature convention and drives the split; a sensitivity on 0.75–0.9
should accompany any published version of this.

### What is inside the 5x

Ranked by suspected contribution, all requiring proper attribution work:

1. **Permitting duration and rejection risk.** Carlsbad took ~15 years. Huntington Beach ran
   **24 years, cost $1.4B on paper, and was unanimously rejected** in May 2022 after an
   eight-hour hearing with 200 speakers. Capital sits at risk for decades with a real
   probability of total loss, and every project must price that in.
2. **Bespoke one-off projects vs. a repeated template.** Israel tendered the same standardized
   design repeatedly; California negotiates each plant from scratch.
3. **Mandated intake technology.** The Ocean Plan prefers subsurface intakes. Doheny — the
   first fully compliant plant — has the *worst* capex intensity in the table.
4. **Stacked environmental review**: CEQA + Coastal Act + Ocean Plan + NPDES, sequential rather
   than concurrent.
5. **US construction cost premium** (prevailing wage, labour, materials) — real, but plausibly
   1.3–1.5x on civil works, not 5x.

### The correction that changes the policy recommendation

**Israel's plants are also take-or-pay.** Israeli desal runs on 26.5-year BOT concessions with
a government availability payment — a take-or-pay contract — financed non-recourse against
projected cash flows, with Mekorot as guaranteed offtaker.

So the earlier read of Carlsbad's take-or-pay as the villain was wrong. **Both countries use
take-or-pay; one gets $0.58/m³ and the other $2.84/m³.** Take-or-pay is not the problem — it is
the mechanism that makes cheap non-recourse project finance possible in the first place.

The difference is **permitting risk and standardisation**, not contract structure. California
already has the guaranteed-offtake half of the Israeli model. It is missing the pre-permitted,
standardised, repeatedly-tendered half.

**Therefore "build at Israeli capex rates" is a procurement and permitting problem, not an
engineering one — which makes it a legislative target rather than a startup target.**

### There is an open policy window right now

- The **State Water Board is actively considering Ocean Plan amendments** to streamline permits
  for projects meeting siting/design standards **in identified priority areas** — which is
  substantially the pre-permitted-site concept. Public scoping meeting held Oct 2024; DWR's
  2023 Water Plan Update recommends concurrent rather than sequential agency review.
- The **Colorado River post-2026 guidelines are being decided now.** The seven basin states
  missed successive deadlines and reached no consensus; Interior is proceeding through NEPA to
  finalise operating guidelines by **1 October 2026** — roughly six weeks out. Arizona,
  California and Nevada filed a Lower Basin proposal on 1 May.

Both windows are open simultaneously, at state and federal level. That is unusually good timing
for a policy-directed output.

---

## Consequences for scope

1. **Outcome A (merchant desal on energy arbitrage) is unlikely on these numbers.** The energy
   lever is 16–47%, and the competing option is 12x cheaper. Phase 5 should be treated as
   improbable pending the SWRO-specific model.
2. **Outcome D should be the baseline, not a fourth option.** Ag reallocation is the incumbent
   solution on cost. A/B/C must beat it, and currently none of them do.
3. **A better investable thesis surfaced — the Carlsbad/Sorek gap.** The pitch is not "chase
   free electrons." It is **"build at Israeli cost structure in California."** That gap is 5–7x,
   institutional rather than physical, and therefore potentially capturable — and it is worth
   more than the energy strategy by an order of magnitude. Energy flexibility becomes a
   margin-improver layered on top, not the core.
4. **Re-aim the pricing section** at the ag/urban divergence and the fact that neither price
   signals scarcity, rather than at "water is too cheap."
5. **Two numbers now gate everything** and should be nailed before the pipeline: the Salton Sea
   /fallowing ceiling (how much reallocation is actually available), and an SWRO-specific
   capacity-factor-vs-capex curve to replace the brackish proxy.

---

# Phase 0.5 — Gating questions

Run 2026-08-22. Three questions that gated the build. All three answered; two changed the plan.

---

## Gate 1 — D4 is dead. The Colorado River decision was made yesterday.

| Milestone | Date |
|---|---|
| Draft EIS released | 9 Jan 2026 |
| **Public comment period** | **16 Jan – 2 Mar 2026 — CLOSED** |
| Comments received | 18,127 submissions (785 unique) |
| Final EIS | 31 Jul 2026 |
| **Record of Decision** | **21 August 2026 — one day before this check** |

The ROD adopts the Preferred Alternative's "Decision Framework" for coordinated operation of
Lake Powell and Lake Mead across **2027–2036**, and simultaneously issued the first
**2027–2028 Operating Guidelines** under it. Reclamation describes the process as concluding.
No further formal comment period exists; only an informal channel remains
(crbpost2026@usbr.gov).

**D4 as scoped is impossible.** We missed the window by five and a half months.

### Re-aim rather than delete

The ROD created a **framework**, not a final rule — operating guidelines are issued in sets
under it through 2036, so there will be recurring decision points. Recommended replacement:

- **D4′:** target the *next* operating-guidelines cycle under the 2027–2036 framework, where
  the full supply-stack analysis will be ready rather than rushed.
- **Silver lining for D1:** the paper now has an unusually sharp news hook. The guidelines were
  decided *this week*, without seven-state consensus, after two years of failed negotiation.
  A paper analysing what the new framework does and does not do about pricing lands into a live
  conversation with no deadline pressure.

**Net effect: the six-week crunch disappears.** That is a scheduling gift, not a loss.

---

## Gate 2 — The Salton Sea externality is real, quantifiable, and it moves the answer

### The structural finding

Under the 2003 QSA the three water agencies' mitigation liability is **capped** at $133M in 2003
dollars (~$288M with interest). **California assumed responsibility for everything beyond that**
— legislation makes future Salton Sea restoration the sole responsibility of the state.

So the dust cost of transferring water out of Imperial is **socialised, not borne by the buyer.**
That is an externality in the strict sense, and it means the ~$280/AF fallowing figure from
Finding 5 is **not the true social cost.**

### The numbers

| Quantity | Value |
|---|---|
| Phase I management plan (2018–2028) | $420M |
| Playa exposure projected over the decade | 48,300 acres |
| Playa the plan actually covers | 29,800 acres (**62%**) |
| Ongoing O&M after Phase I | $8–10M/yr |
| QSA transfers driving exposure | ~303,000 AF/yr (IID→SDCWA 200k + IID→CVWD 103k) |

### Derived externality ⚠ *our arithmetic, not a published figure*

```
Phase I as planned (62% coverage):
  $420M ÷ 10 yr = $42M/yr ÷ 303,000 AF   = ~$139/AF

Extrapolated to full 48,300-acre coverage:
  $420M ÷ 0.62 = $677M ÷ 10 yr = $67.7M/yr ÷ 303,000 AF = ~$223/AF

Plus ongoing O&M ($8–10M/yr ÷ 303,000 AF)  = ~$26–33/AF
                                              ------------
Dust externality range                        ~$140–255/AF
```

### What this does to the supply stack

| Option | $/AF |
|---|---|
| Fallowing/transfer, **direct cost only** | ~$280 (240–320) |
| Fallowing/transfer, **social cost incl. dust** | **~$477 (380–575)** |
| Sorek-cost desalination | **~$505–715** |
| Carlsbad desalination | ~$3,500 |

> **Band corrected in Phase 1.** This section originally quoted $420–535, which added the
> externality's *range* to the direct cost's *point* value. Propagating both uncertainties
> gives $380–575. Caught by a test that re-derives every stated figure from its components.
> The conclusion is unchanged and slightly strengthened: Sorek B at ~$505/AF sits inside
> the band.

**The ranges overlap.** Once the Salton Sea externality is internalised, reallocation and
Israeli-cost desalination are roughly at parity — the 12x advantage collapses to something
between 1x and 1.7x.

This is the most consequential result so far, for three reasons:

1. **It makes Act III decisive rather than decorative.** Whether California can close the 5x
   institutional gap now determines whether desal is competitive at all. That was previously an
   interesting side-question; it is now *the* question.
2. **It preserves fallowing's win over Carlsbad** (~7x) while destroying its win over *reformed*
   desal. Both halves matter.
3. **It unifies the argument.** Act I says ag water is underpriced because costs are pushed onto
   the public. Act II's cheap alternative is cheap for **exactly the same reason** — the state
   is the backstop. The mispricing thesis applies to the remedy as well as the disease.

⚠ Caveats before this goes in the paper: (a) not all QSA transfer is fallowing — IID shifted
from fallowing to on-farm and system efficiency measures around 2012, though efficiency also
cuts return flows and so also shrinks the Sea; (b) restoration spending is not purely
dust-driven, so attributing all of it to water transfer overstates; (c) some exposure would have
occurred without the transfers. A proper attribution model is Phase 2 work — but the magnitude
is clearly large enough to matter.

---

## Gate 3 — SWRO flexibility: the literature is genuinely split, and the split is informative

The SWRO-specific answer did not resolve cleanly. It resolved into a *disagreement*, which is
more useful.

**Against flexible operation** — a micro-grid deferrable-load study concludes it is preferable
to run expensive SWRO plants at **baseload** for total energy-system cost reasons, and that grid
flexibility is delivered more cheaply by **solar PV plus batteries** than by SWRO plants plus
water storage.

**For flexible operation** — other work finds water storage is far cheaper than batteries as a
medium: at 2 kWh/m³, storing the energy equivalent of 1 m³ costs **~$600 in batteries versus
~$98 in a water tank**, and that upgrading a facility for energy flexibility is usually cheaper
than adding on-site batteries.

### Reconciling them — this is the useful part

Both are probably right about different system boundaries:

- The **storage medium** comparison is correct: a water tank beats a battery ~6:1 per unit of
  energy shifted. The original intuition holds *at that boundary*.
- The **whole-system** comparison is also correct: when you idle a plant to chase cheap power,
  you are not just buying a cheap tank — you are stranding capital-intensive RO trains. A
  battery lets the plant keep running at high capacity factor.

**The binding term is RO capex utilisation, not storage cost.** Which is precisely the
`LCOW(CF)` tension identified at the outset.

**Verdict: the dark horse is not dead — it is contested, and the contest turns on exactly the
term our model would compute.** Combined with the brackish study's 16%/47% bracket, this is now
a genuine open question in the literature that an SWRO-specific capacity-factor model could
resolve. That raises its value from "already answered, skip it" to "worth building as a
secondary contribution."

---

## Revised state of play after Phase 0.5

| Item | Status |
|---|---|
| Merchant desal on energy arbitrage (old Act) | Dead — killed in Phase 0 |
| D4 Colorado River comment | **Dead as scoped**; re-aim to next guidelines cycle (D4′) |
| Fallowing as runaway cheapest option | **Weakened** — parity with reformed desal once dust is counted |
| The 5x institutional gap | **Promoted to decisive** |
| SWRO flexible operation | **Revived as an open question** worth modelling |
| Framing gate (§3 of REQUIREMENTS) | Still open — and now genuinely uncertain, which vindicates deferring it |

---

## Sources

- [Voice of San Diego — San Diegans Owe a Desal Company $35 million for Unmade Water](https://voiceofsandiego.org/2025/09/22/san-diegans-owe-a-desal-company-35-million-for-unmade-water/)
- [San Diego County Water Authority — Seawater Desalination](https://www.sdcwa.org/your-water/local-water-supplies/seawater-desalination/)
- [Surfrider San Diego — Poseidon Water Purchase Agreement: Private Profit, Public Risk](https://sandiego.surfrider.org/news/poseidon-water-purchase-agreement-private-profit-public-risk)
- [MIT Technology Review — Megascale Desalination](https://www.technologyreview.com/technology/megascale-desalination/)
- [Blackridge Research — Sorek Desalination Plant Project](https://www.blackridgeresearch.com/project-profiles/all-about-sorek-desalination-plant-israel-cost-location-detail)
- [Desalination (2026) — Can flexible operation of brackish desalination facilities reduce the cost of desalted water? A case study in Southern California](https://www.sciencedirect.com/science/article/pii/S0011916426002535)
- [A comprehensive review of energy consumption of seawater reverse osmosis desalination plants](https://www.sciencedirect.com/science/article/abs/pii/S030626191931339X)
- [MDPI Membranes — Opportunities of Reducing the Energy Consumption of SWRO](https://www.mdpi.com/2077-0375/12/11/1045)
- [CalMatters — California cities pay a lot for water; some agricultural districts get it for free](https://calmatters.org/environment/2025/12/price-of-california-water-cities-growers/)
- [Imperial Irrigation District — About IID Water](https://www.iid.com/water/about-iid-water)
- [Metropolitan Water District — Funding for community improvements in Palo Verde Valley](https://www.mwdh2o.com/press-releases/metropolitans-board-supports-funding-for-community-improvements-in-palo-verde-valley)
- [Palo Verde Irrigation District / Metropolitan land management program](https://pvid.org/a1.php)
- [CNN — Foreign-owned farm no longer pumping groundwater on state land, Arizona governor says](https://www.cnn.com/2024/03/07/us/foreign-farm-fondomonte-groundwater-arizona)
- [CBS News — Arizona is canceling leases that allow Saudi-owned farm unlimited access to groundwater](https://www.cbsnews.com/news/saudi-arabia-water-access-arizona/)
- [Wiley, Water Resources Research — Water Affordability in the United States](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2022WR032206)
- [Bluefield Research — National Water and Sewer Bills Rise 5.1%](https://www.bluefieldresearch.com/ns/national-water-and-sewer-bills-rise-5-1-outpacing-inflation-as-utilities-face-rising-cost-pressures/)
- [EIA — Solar and wind power curtailments are increasing in California](https://www.eia.gov/todayinenergy/detail.php?id=65364)
- [Ascend Analytics — CAISO Market Outlook: Persistent Negative Energy Prices, Spreading Curtailment](https://www.ascendanalytics.com/blog/caiso-market-outlook-persistent-negative-energy-prices-spreading-curtailment)
- [Abunayyan Holding — Floating Desalination: barge-mounted desalination plants](https://www.abunayyanholding.com/en/casestudy/what-we-do/case-studies/floating-desalination-the-worlds-first-self-contained-barge-mounted-desalination-plants.html?sector=6)
- [Earth Magazine — Dry dock to wet tap: Old ships become floating desalination plants](https://www.earthmagazine.org/article/dry-dock-wet-tap-old-ships-become-floating-desalination-plants/)
- [Green Prophet — Desalination experts debunk Aqua Solaire, the floating desalination barge](https://www.greenprophet.com/2026/05/desalination-experts-debunk-aqua-solaire-the-floating-desalination-barge/)
- [Wikipedia — Claude "Bud" Lewis Carlsbad Desalination Plant](https://en.wikipedia.org/wiki/Claude_%22Bud%22_Lewis_Carlsbad_Desalination_Plant)
- [ENR — California Coastal Commission Rejects $1.4B Desalination Project](https://www.enr.com/articles/54116-california-coastal-commission-rejects-14b-desalination-project)
- [CalMatters — A salty dispute: California Coastal Commission unanimously rejects desalination plant](https://calmatters.org/environment/2022/05/california-desalination-plant-coastal-commission/)
- [UC Davis Environs — When Desal in California Gets the Green Light: A Comparison of Four Projects](https://environs.law.ucdavis.edu/sites/g/files/dgvnsk15356/files/2025-05/Huang%20-%20Macroed.pdf)
- [State of Israel Desalination Division — Sea Water Desalination in Israel](https://www.hidrojing.com/wp-content/uploads/2014/01/Desalination-in-Israel.pdf)
- [OECD Roundtable on Financing Water — Attracting private funding, Desalination Israel](https://www.oecd.org/content/dam/oecd/en/events/2017/9/second-meeting-of-the-roundtable-on-financing-water/Marmelshtein%20(2017)%20Attracting%20private%20funding%20-Desalination%20Israel.pdf)
- [Springer — Technologies, Incentives and Cost Recovery: Is There an Israeli Role Model?](https://link.springer.com/chapter/10.1007/978-3-319-18971-0_16)
- [Allen Matkins — DWR and Water Board Propose Key Updates to Desalination Policy Framework](https://www.allenmatkins.com/real-ideas/dwr-and-water-board-propose-key-updates-to-desalination-policy-framework.html)
- [State Water Board — Seawater Desalination Siting and Streamlining Report](https://www.waterboards.ca.gov/water_issues/programs/ocean/desalination/docs/desal-siting-streamlining-report-dec2023.pdf)
- [MDPI Water — Seawater Desalination in California: A Proposed Framework for Streamlining Permitting](https://doi.org/10.3390/w17243533)
- [South Coast Water District — Doheny Ocean Desalination Project](https://scwd.org/about/district_projects/doheny_ocean_desalination_project/index.php)
- [USBR — Colorado River Post-2026 Operations](https://www.usbr.gov/ColoradoRiverBasin/post2026/index.html)
- [WaterWorld — Colorado River states miss deadline as Lower, Upper basin tensions sharpen over post-2026 cuts](https://www.waterworld.com/water-utility-management/news/55357951/colorado-river-states-miss-deadline-as-lower-upper-basin-tensions-sharpen-over-post-2026-cuts)
- [Maven's Notebook — Colorado River update: Interior moving forward after no consensus among the seven basin states](https://mavensnotebook.com/2026/02/14/special-edition-colorado-river-update-department-of-interior-moving-forward-after-no-consensus-among-the-seven-basin-states/)

### Phase 0.5

- [USBR — Draft EIS Public Review & Comment Process, Post-2026 Colorado River Operations](https://www.usbr.gov/ColoradoRiverBasin/post2026/draft-eis/Public-Review-Comment-Process.html)
- [USBR — Final Environmental Impact Statement, Post-2026 Colorado River Operations](https://www.usbr.gov/ColoradoRiverBasin/post2026/final-eis/index.html)
- [DOI — Reclamation Publishes Final EIS for Future Colorado River Operations](https://www.doi.gov/pressreleases/reclamation-publishes-final-environmental-impact-statement-future-colorado-river)
- [California LAO — The Salton Sea: A Status Update](https://lao.ca.gov/Publications/Report/3879)
- [Congressional Research Service — Salton Sea Restoration (R46625)](https://www.congress.gov/crs-product/R46625)
- [Salton Sea Air Quality Mitigation Program](https://saltonseaprogram.com/)
- [UCSB Bren — Prioritizing Cost-Effective Dust Mitigation at the Salton Sea](https://bren.ucsb.edu/media/189)
- [Water Education Foundation — Quantification Settlement Agreement](https://www.watereducation.org/aquapedia/quantification-settlement-agreement)
- [SDCWA — Quantification Settlement Agreement fact sheet](https://www.sdcwa.org/sites/default/files/qsa-fs.pdf)
- [Seawater reverse osmosis (SWRO) as deferrable load in micro grids](https://www.sciencedirect.com/science/article/pii/S1944398624183968)
- [Nature Water — Valuing energy flexibility from water systems](https://www.nature.com/articles/s44221-024-00316-4)
- [Stanford Report — How water systems can accelerate renewable energy adoption](https://news.stanford.edu/stories/2024/09/how-water-systems-can-accelerate-renewable-energy-adoption)
