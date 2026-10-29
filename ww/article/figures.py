"""Every number the article prints, computed from the model in one place.

The article must not carry a number the model does not. So the prose template only
interpolates names from `numbers()`, and the charts only draw what `series()` returns.
A correction in literature.yaml therefore reaches the published page on the next build.

The seed and draw count are fixed, so the article is reproducible to the dollar.
"""

from __future__ import annotations

import statistics
from dataclasses import replace
from datetime import date
from functools import lru_cache

from ww import cache, params, sources
from ww.model import deflate, lcow, permitting, plants, salton, scale, stack

N_DRAWS = 10_000
SEED = 20261028


@lru_cache(maxsize=1)
def draws() -> list[stack.Draw]:
    return stack.simulate(n=N_DRAWS, seed=SEED)


# --------------------------------------------------------------------------------------
# Series for charts
# --------------------------------------------------------------------------------------


def _series(source_id: str):
    src = sources.get(source_id)
    return src.normalise(cache.load(src.spec))


def reservoirs() -> dict:
    """Monthly storage (first reading of each month), MAF, plus the record lows."""
    out = {}
    for key, sid, since in (("mead", "usbr.reservoir.lake_mead", 1937),
                            ("powell", "usbr.reservoir.lake_powell", 1964)):
        pts = [p for p in _series(sid)[0].points if p.value > 0 and p.when.year >= since]
        monthly, seen = [], set()
        for p in pts:
            ym = (p.when.year, p.when.month)
            if ym not in seen:
                seen.add(ym)
                monthly.append((p.when.date().isoformat(), round(p.value / 1e6, 3)))
        # Powell's record low is reported after its first fill (1980) — the 1960s
        # filling period is lower but is not a drought.
        tail = [p for p in pts if key == "mead" or p.when.year >= 1980]
        low = min(tail, key=lambda p: p.value)
        peak = max(pts, key=lambda p: p.value)
        last = pts[-1]
        out[key] = {
            "monthly": monthly + [(last.when.date().isoformat(), round(last.value / 1e6, 3))],
            "low_date": low.when.date(), "low_maf": low.value / 1e6,
            "peak_date": peak.when.date(), "peak_maf": peak.value / 1e6,
            "last_date": last.when.date(), "last_maf": last.value / 1e6,
        }
    return out


def prices() -> dict:
    """Water/sewer/trash CPI and all-items CPI, monthly, indexed Jan 2000 = 100."""
    ids = {"bls.cpi.CUUR0000SEHG": "water", "bls.cpi.CUUR0000SA0": "all"}
    raw: dict[str, dict] = {"water": {}, "all": {}}
    for sid in ("bls.cpi.2000s", "bls.cpi.2010s", "bls.cpi.2020s"):
        for ts in _series(sid):
            if ts.source_id in ids:
                for p in ts.points:
                    raw[ids[ts.source_id]][p.when.date()] = p.value
    out = {}
    for k, s in raw.items():
        base = s[date(2000, 1, 1)]
        out[k] = [(d.isoformat(), round(v / base * 100, 1)) for d, v in sorted(s.items())]
    return out


def option_stats() -> dict[str, dict]:
    out = {}
    for k, o in stack.OPTIONS.items():
        d = stack.distribution(draws(), k)
        lo, hi = d.band_90
        out[k] = {"label": o.label, "median": d.median, "lo": lo, "hi": hi,
                  "on_stack": o.on_stack}
    return out


def supply_curve() -> list[dict]:
    """Median cost and median quantity per on-stack option, cheapest first. Uses the
    status-quo desal variant (Carlsbad cost, public finance) as the unbounded backstop."""
    ds = draws()
    keys = [k for k, o in stack.OPTIONS.items()
            if o.on_stack and (k == "desal_public" or k not in stack.DESAL_VARIANTS)]
    rows = []
    for k in keys:
        q = [d.quantity[k] for d in ds]
        rows.append({"key": k, "label": stack.OPTIONS[k].label,
                     "cost": statistics.median(d.cost[k] for d in ds),
                     "qty": statistics.median(q)})
    return sorted(rows, key=lambda r: r["cost"])


def ag_breakdown() -> dict:
    return {
        "payment": stack.ag_direct(),
        "conveyance": deflate.real("conveyance.colorado_to_coast"),
        "dust": salton.walk().per_blended_ag_af,
    }


def desal_breakdown() -> dict:
    r = lcow.lcow(plants.carlsbad(), plants.carlsbad_finance())
    af = params.usd_per_m3_to_af
    return {
        "capital": af(r.capital_recovery_usd_m3),
        "energy": af(r.energy_usd_m3),
        "om": af(r.fixed_om_usd_m3 + r.variable_om_usd_m3),
        "pipeline": af(r.conveyance_usd_m3),
    }


def desal_ladder() -> list[tuple[str, float]]:
    """Medians across the draws, so the chart and the prose agree with the stack chart."""
    med = {k: stack.distribution(draws(), k).median
           for k in ("desal_as_built", "desal_public", "desal_permit_reform", "desal_israeli")}
    return [
        ("Carlsbad as built", med["desal_as_built"]),
        ("Same plant, public finance", med["desal_public"]),
        ("+ permitting reform", med["desal_permit_reform"]),
        ("At Israeli construction cost", med["desal_israeli"]),
    ]


# --------------------------------------------------------------------------------------
# Scalars for the prose
# --------------------------------------------------------------------------------------


def _gap() -> dict:
    cb = plants.carlsbad(include_conveyance=False)
    sk = plants.sorek()
    gaps = scale.gap_across_exponents(
        reference_capex=sk.capex_usd, reference_capacity=sk.capacity_m3_day,
        subject_capex=cb.capex_usd, subject_capacity=cb.capacity_m3_day)
    vals = sorted(g.gap for g in gaps.values())
    central = gaps[params.value("econ.capex_scaling_exponent")].gap
    explained = (permitting.risk_multiplier(permitting.california_regime())
                 / permitting.risk_multiplier(permitting.reformed_regime()))
    raw = (scale.unit_capex(cb.capex_usd, cb.capacity_m3_day)
           / scale.unit_capex(sk.capex_usd, sk.capacity_m3_day))
    return {"gap": central, "gap_lo": vals[0], "gap_hi": vals[-1], "permit_x": explained,
            "residual_x": central / explained, "raw_x": raw,
            "cb_unit": scale.unit_capex(cb.capex_usd, cb.capacity_m3_day),
            "sk_unit": scale.unit_capex(sk.capex_usd, sk.capacity_m3_day)}


def _validation() -> list[dict]:
    nameplate_af = plants.carlsbad().nameplate_m3_year / params.value("unit.acre_foot_m3")
    u = params.value("desal.carlsbad.min_volume") / nameplate_af

    def at(year: int, util: float) -> float:
        return lcow.lcow(plants.carlsbad(year=year, utilisation=util),
                         plants.carlsbad_finance()).total_usd_af

    return [
        {"what": "Carlsbad contract price, 48,000 AF minimum", "year": 2012,
         "published": params.value("desal.carlsbad.contract_price_min_volume"), "model": at(2012, u)},
        {"what": "Carlsbad, Water Authority projection", "year": 2013,
         "published": params.value("desal.carlsbad.price_projected_total_2013"), "model": at(2013, 1.0)},
        {"what": "Carlsbad, what the Water Authority pays today", "year": 2025,
         "published": params.value("desal.carlsbad.price_current"), "model": at(2025, u)},
        {"what": "Sorek fixed charge, $/m³", "year": 2013,
         "published": params.value("desal.sorek.price_fixed"),
         "model": lcow.lcow(plants.sorek(year=2013), plants.sorek_finance()).fixed_usd_m3},
    ]


def numbers() -> dict:
    ds = draws()
    st = option_stats()
    res = reservoirs()
    g = _gap()
    w = salton.walk()
    ag = ag_breakdown()
    cut = params.value("ca.colorado_cut")
    cut_hi = params.get("ca.colorado_cut").high
    gate = stack.gate(ds)
    gate_hi = stack.gate(ds, target=cut_hi)
    cheap = [sum(d.quantity[k] for k in ("conservation", "stormwater", "ag")
                 if d.cost[k] < d.cost["desal_israeli"]) for d in ds]
    ladder = desal_ladder()
    reform_saving = ladder[1][1] - ladder[2][1]
    pwsc_per_mgd = deflate.real("reuse.pwsc.capex") / params.value("reuse.pwsc.capacity_mgd")
    cb_per_mgd = (plants.carlsbad().total_capex_usd / 50.0)
    contract_2025 = deflate.real("desal.carlsbad.contract_price_min_volume")
    phase0_ratio = params.value("desal.carlsbad.price_current") / params.value("fallowing.direct_cost")
    return {
        "today": date(2026, 10, 28),
        "n_draws": N_DRAWS,
        "res": res,
        "mead_low_pct": res["mead"]["low_maf"] / res["mead"]["peak_maf"],
        "powell_last_pct": res["powell"]["last_maf"] / res["powell"]["peak_maf"],
        "cpi_water": params.value("cpi.water_sewer_trash.pct_change_2000_2025"),
        "cpi_all": params.value("cpi.all_items.pct_change_2000_2025"),
        "cpi_real": params.value("cpi.water.real_pct_change_2000_2025"),
        "iid_rate": params.value("rates.iid.agricultural"),
        "ag_avg_rate": params.value("rates.ca_ag_districts.average"),
        "city_rate": params.value("rates.ca_city_utilities.average"),
        "st": st,
        "gate": gate, "gate_hi": gate_hi,
        "cut": cut, "cut_hi": cut_hi,
        "cheap_median": statistics.median(cheap),
        "p_cheap_covers_cut": sum(q >= cut for q in cheap) / len(cheap),
        "p_cheap_covers_hi": sum(q >= cut_hi for q in cheap) / len(cheap),
        "ag": ag, "ag_total": sum(ag.values()),
        "desal": desal_breakdown(),
        "ladder": ladder,
        "phase0_ratio": phase0_ratio,
        "delivered_ratio": stack.desal_as_built() / stack.ag_reallocation(),
        "israeli_ratio": stack.desal_israeli() / stack.ag_reallocation(),
        "salton": w,
        "qsa_share": salton.qsa_share(),
        "dust_share": params.value("salton.dust_share_of_spend"),
        "iid_share": params.value("ag.iid_share_of_conservation"),
        "qsa_cap": params.value("salton.qsa_mitigation_cap"),
        "qsa_volume": params.value("salton.qsa_transfer_volume"),
        "gap": g,
        "reform_saving": reform_saving,
        "public_saving": ladder[0][1] - ladder[1][1],
        "pwsc_per_mgd": pwsc_per_mgd, "cb_per_mgd": cb_per_mgd,
        "pwsc_cost": params.value("reuse.pwsc.unit_cost"),
        "pwsc_life": params.value("reuse.pwsc.unit_cost_lifecycle"),
        "pwsc_ipr_2015": deflate.real("reuse.ipr_large.cost"),
        "contract_2012": params.value("desal.carlsbad.contract_price_min_volume"),
        "contract_2025": contract_2025,
        "press_price": params.value("desal.carlsbad.price_current"),
        "validation": _validation(),
        "ca_energy_af": params.value("swro.sec") * deflate.real("energy.price_industrial_ca")
        * params.value("unit.acre_foot_m3"),
        "energy_ratio": params.value("energy.price_ratio_ca_israel"),
        "imported": deflate.real("mwd.rate.full_service_treated_2026"),
        "imported_nominal": params.value("mwd.rate.full_service_treated_2026"),
        "pwsc_hi": params.get("reuse.pwsc.unit_cost").high,
        "denials": (params.value("permitting.ca.decisions_denied"),
                    params.value("permitting.ca.decisions_total")),
        "hb_spend": params.value("permitting.huntington_beach.development_spend"),
        "pvid_acres": params.value("fallowing.pvid.acres"),
        "pvid_af": params.value("fallowing.pvid.conserved"),
        "ag_price_nominal": (params.band("ag.conservation_price")),
        "conveyance_band": deflate.real_band("conveyance.colorado_to_coast"),
        "iid_hist_per_af": params.value("iid.fallowing_2003_2017.payments")
        / params.value("iid.fallowing_2003_2017.volume"),
        "playa_2023": params.value("salton.playa_response_2023"),
        "gap_reform_lo": stack.distribution(ds, "desal_permit_reform").percentile(5),
    }


def used_citations() -> list:
    """Every citation behind a parameter the stack or the article touches."""
    ps = params.load()
    keep: set[str] = set()
    for p in ps.parameters.values():
        keep.update(p.citations)
    return sorted((ps.citations[c] for c in keep), key=lambda c: (c.publisher or "", c.title))


__all__ = ["numbers", "reservoirs", "prices", "option_stats", "supply_curve",
           "ag_breakdown", "desal_breakdown", "desal_ladder", "used_citations", "replace"]
