# CLAUDE.md — water_world

Operational reference: layout, commands, and traps.

> **2026-10-28: Phase 3 done; project closing with one article on ahdimel.com.** See
> HANDOFF.md status block and §4b. Everything below "Current state" is history unless
> it says otherwise.

**Picking this up cold? Read [HANDOFF.md](HANDOFF.md) first** — it carries the reasoning
(how the thesis got here, what the owner decided, what is contested, what to do next).
This file assumes you already have that context.

The authoritative spec is [REQUIREMENTS.md](REQUIREMENTS.md); the evidence base is
[PHASE0_FINDINGS.md](PHASE0_FINDINGS.md).

## Purpose

An analysis project, ending in a findings paper and policy artifacts — not a product.

**Thesis:** water in the American West is allocated by right rather than price; correct
pricing would buy the cheap options first; and the expensive option we actually build
(desalination) costs ~5x what it should, for institutional rather than physical reasons.

Three acts: **mispricing → supply stack → the 5x gap.**

## The two rules that override convenience

1. **The framing gate.** The paper's argument is decided by the Phase 3 supply-stack
   model, not in advance. Do not write narrative that presumes a ranking. The owner
   chose this explicitly. Phase 0.5 justified it — the ranking is genuinely uncertain.
2. **Every number is defensible.** Observed numbers come from a registered source;
   document-sourced numbers live in `data/parameters/literature.yaml` with a citation
   and, wherever possible, a range. Nothing enters the analysis uncited.

## Layout

```
ww/schemas.py          pydantic contracts (sources, provenance, series, parameters)
ww/cache.py            fetch-once provenance-stamped cache; nothing downstream hits the network
ww/params.py           literature loader + unit conversion + audit helpers
ww/sources/            source registry: usbr (reservoirs), bls (CPI), caiso (LMP), manual decls
ww/model/              PHASE 2 cost engine
  finance.py             cost of capital, debt and equity legs kept apart
  lcow.py                levelised cost, split fixed/variable like the Israeli tariffs
  scale.py               scale-adjusted international capex comparison (§2.1)
  permitting.py          approval delay + rejection risk priced as capital (§2.2)
  plants.py              reference plants assembled from literature.yaml
  montecarlo.py          parameter ranges -> outcome distributions
  deflate.py             PHASE 3: CPI-U restatement into 2025 dollars (table committed)
  salton.py              PHASE 3: Salton Sea externality, attributed + damage stress case
  stack.py               PHASE 3: supply stack, joint Monte Carlo, the framing gate
ww/cli_model.py        Phase 2 CLI commands (kept out of __main__ so caveats are testable)
ww/__main__.py         CLI
data/parameters/       COMMITTED evidence: literature.yaml, cpi_u_annual.yaml (generated)
data/raw/              gitignored cache
tests/                 offline; parsers run against fixtures, cache against a stubbed downloader
```

## Commands

```
python -m ww sources              # registry, with cached/not status
python -m ww fetch --all          # populate the cache (14 live sources)
python -m ww show <source_id>     # summarise a normalised series
python -m ww params --audit       # uncited / low-confidence / point-estimate review
python -m ww params <id>          # one parameter with its citation and lineage
python -m ww status               # what is cached and how stale

python -m ww lcow [plant]         # levelised cost by leg: carlsbad, sorek, doheny, ...
python -m ww gap                  # scale-adjusted Carlsbad/Sorek capex comparison
python -m ww permitting           # approval delay and rejection risk, priced in $/AF
python -m ww montecarlo -n 10000  # LCOW as a distribution
python -m ww deflator [--rebuild] # CPI-U table; --rebuild regenerates it from the cache
python -m ww salton               # the Salton externality, one correction at a time
python -m ww stack                # Phase 3 supply stack + framing gate
```

## Current state — Phase 3 complete (history of Phases 0-1 follows)

**Phase 0 and 0.5 (desk research) and Phase 1 (data layer) are done. 76 tests pass.**

Phase 0 killed the original thesis ("merchant desal wins by chasing cheap solar") and
Phase 0.5 reshaped what remained. Load-bearing results:

- The owner's original US water-price claim was **falsified**; the corrected version
  (ag frozen nominally while urban ratepayers absorb the rise) is stronger. Now
  **verified against primary BLS series**: +207% vs +92% CPI, 2000-2025.
- **Salton Sea dust is a socialised externality** worth ~$140-255/AF on transferred
  water. It takes fallowing from ~$280/AF to ~$477/AF (380-575), overlapping Sorek-cost
  desal (~$505-715/AF). This **promoted Act III from decorative to decisive.**
- **Scale-adjusted Israel/California capex gap ≈ 5x**, consistent across plants 10x apart
  in size. Israel uses take-or-pay too, so contract structure is not the villain —
  permitting risk and bespoke procurement are.
- **D4 was missed**: the Colorado post-2026 Record of Decision issued 21 Aug 2026, one day
  before we checked. Replaced by D4′ targeting the next guidelines cycle. No deadlines
  remain anywhere in the project.

### Phase 1 additions

- 14 live sources, all key-free: 10 USBR reservoirs (daily storage, some back to 1937)
  and 4 BLS CPI decade chunks. CAISO LMP is implemented and tested but registers no
  windows by default — pulling a year is a throttled 12-query job and a Phase 2 decision.
- `literature.yaml`: 44 parameters, 21 citations, every Phase 0/0.5 number machine-readable.
- **A test caught a real error**: the fallowing social-cost band had been computed by
  adding the externality's *range* to the direct cost's *point* value. Corrected from
  380-575 and propagated to both markdown docs.

### Verified from primary data, worth using

Both Colorado reservoirs are at **all-time lows and still falling** as of 2026-08-21 —
their six lowest readings ever are the last six days. Mead at 23% of its historic maximum,
Powell at 20% (excluding its 1963 filling period).

## Gotchas that have already bitten

- **Do not cite Fondomonte/Butler Valley as a Colorado River example.** That is Arizona
  *groundwater*, and those leases were cancelled in 2023. Use Fondomonte's **Palo Verde
  Valley** operation, which is Colorado River water.
- **`econ.capex_scaling_exponent` drives the gap headline.** Always report it with the
  0.75-0.9 sensitivity. A test enforces that the result survives both extremes.
- **`salton.externality` is the most contested load-bearing number.** It assumes all QSA
  transfer drives playa exposure and all restoration spend is dust-driven. Neither is
  strictly true. Sensitivity-test before it carries a conclusion.
- **SUPERSEDED (Phase 3): $3,500 IS the current price** — the bullet below was a
  dollar-year error. Kept as history. ~~Do not use `desal.carlsbad.price_current`
  ($3,500/AF) as the Carlsbad comparator.~~
  Phase 2 checked it against primary sources and it did not hold: SDCWA's own figure is
  **$2,302-2,559/AF** (`desal.carlsbad.price_sdcwa`), independently corroborated by the
  WPA reading and by the model. The $3,500 press figure stays in the file, flagged, only
  until the residual is explained. **Any ratio with $3,500 on one side is overstated** —
  including several in PHASE0_FINDINGS.md and REQUIREMENTS.md.
- **The gap is ~4x, not 5x.** Carlsbad's $203M pipeline has no counterpart in Sorek's
  capex; strip conveyance before comparing or the headline inflates to 5.3x.
- **Permitting does not explain the gap.** It accounts for ~1.38x of ~4.23x. Reform is
  worth ~$428/AF, which is the defensible claim; "permitting explains 5x" is not.
- **BLS blocks `download.bls.gov` without a contact email in the User-Agent.** We use the
  key-free API instead precisely so no personal data goes to a third party. The flat-file
  route exists but is opt-in via `WW_CONTACT_EMAIL`.
- **CAISO puts the price in the `MW` column.** Not a typo — an OASIS naming artefact.

## Phase 2 — cost engine built

**148 tests pass. 118 parameters, 34 citations.** The engine reproduces two published
figures it was not fitted to: Carlsbad at **$2,456/AF against SDCWA's reported ~$2,430**
(1.1% error), and Sorek's **fixed tariff leg at $0.244/m3 against the published $0.25**.

Four results that cut AGAINST the thesis, all pinned by tests so they cannot be
quietly improved away:

1. **The 5x is ~4.2x.** Carlsbad's $203M pipeline has no counterpart inside Sorek's
   capex. Including it gives 5.3x; excluding it, 4.23x at the central exponent
   (3.99-4.77x across 0.75-0.9). The headline was partly a conveyance artefact.
2. **Permitting explains a minority of the gap.** Priced as capital at risk, California's
   regime adds 1.45x to capex against a reformed 1.05x — so ~1.38x of a 4.23x gap.
   **Roughly 3x survives full permitting reform.** Reform is worth ~$428/AF (15%), which
   is real, but the paper cannot claim permitting explains the gap.
3. **Two more rival explanations died.** Sorek is 80% geared, Carlsbad 80.9% — capital
   structure is not the difference, just as take-or-pay was not. And Carlsbad used an
   *open* intake with a *co-located* outfall, the cheap options, so the mandated
   subsurface-intake hypothesis cannot explain ITS gap.
4. **The utilisation wedge is only ~1.09x**, so under-delivery alone does not get from
   the ~$2,430/AF contract price to the ~$3,500/AF press figure. That reconciliation is
   still open.

**The US-construction-premium hypothesis is not a clean rival.** The literature
attributes the American premium mainly to administrative overhead, procurement practice
and non-standard design — the same mechanisms Act III blames. So the residual is
reported as ONE combined institutional quantity; the split between "permitting" and
"general US administrative premium" is **not identified** by our data. `scale.decompose`
enforces this.

## Phase 3 — supply stack built (2026-10-28)

180 tests. Every option in 2025 dollars, delivered treated, on public finance. The gate:
reallocation beats even Israeli-cost desal (P = 0.999); whether ag capacity alone covers
the 440k AF cut is a coin flip (rows 1/2 not separable); at the extreme cut it is row 2,
cheap but capped. Full table and the six corrections to earlier phases: HANDOFF §4b.

Phase 3 gotchas:

- **Dollar parameters need `year:`.** `deflate.real()` raises without one. Plant
  builders take `year=` and default to 2025; validations pass the figure's own year.
- **CPI-U October 2025 does not exist** (federal shutdown). The table averages 11 months
  for 2025 and records the gap; 2026 is a provisional year-to-date average.
- **Stack options are drawn independently** (child-seeded rng per option), so adding a
  sampler does not reshuffle the others — but shared inputs (CA power, public rate) do
  NOT co-move across options. Harmless for ag vs desal (no shared inputs).
- **Python urllib downloads from usbr.gov intermittently truncate** (IncompleteRead) in
  this sandbox; retry single sources (`ww fetch <id> --force`) rather than `--all`.

## Next (historical)

**Phase 3 — supply stack, and the framing gate opens.**

Still outstanding inside Phase 2: the Salton Sea attribution model (§5.1 of HANDOFF),
ship-mounted desal as a bounded extension, and the SWRO flexibility question.

Open decisions still unanswered: comparator basins (Spain/Israel/Murray-Darling) in or out,
and how much national affordability material survives into the paper.
