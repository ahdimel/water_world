# CLAUDE.md — water_world

Operational reference: layout, commands, and traps.

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
ww/__main__.py         CLI
data/parameters/       COMMITTED evidence: literature.yaml
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
```

## Current state — Phase 1 complete

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
- **`econ.capex_scaling_exponent` drives the 5x headline.** Always report it with the
  0.75-0.9 sensitivity. A test enforces that the result survives both extremes.
- **`salton.externality` is the most contested load-bearing number.** It assumes all QSA
  transfer drives playa exposure and all restoration spend is dust-driven. Neither is
  strictly true. Sensitivity-test before it carries a conclusion.
- **`desal.carlsbad.price_current` ($3,500/AF) is low-confidence** and is the headline
  comparison figure. Confirm against SDCWA primary documents before publication.
- **BLS blocks `download.bls.gov` without a contact email in the User-Agent.** We use the
  key-free API instead precisely so no personal data goes to a third party. The flat-file
  route exists but is opt-in via `WW_CONTACT_EMAIL`.
- **CAISO puts the price in the `MW` column.** Not a typo — an OASIS naming artefact.

## Next

**Phase 2 — desal cost engine**: parameterised techno-economic model, the scale-adjusted
international comparison, and the permitting-risk module that prices approval delay and
rejection probability as a financial instrument. Monte Carlo over the ranges in
`literature.yaml`, producing a distribution rather than a point estimate.

Open decisions still unanswered: comparator basins (Spain/Israel/Murray-Darling) in or out,
and how much national affordability material survives into the paper.
