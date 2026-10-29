"""Build the article: prose template + model numbers + chart data -> one HTML file.

    python -m ww article            # writes docs/article.html

The template (`template.html`) holds the prose with `$name` placeholders. Every
placeholder is filled from `figures.numbers()` here, and the build fails if the template
asks for a value the model does not provide, so the text cannot quote a number the model
did not produce. A literal dollar sign in the prose is written `$$`. The output
is self-contained (inline CSS, SVG drawn by inline JS, data as embedded JSON) and is
imported into ahdimel.com by that repo's tools/import_water_article.py.
"""

from __future__ import annotations

import base64
import html
import json
from pathlib import Path
from string import Template

from ww.article import figures as F
from ww.model import stack

HERE = Path(__file__).resolve().parent
OUT = HERE.parents[1] / "docs" / "article.html"

#: Option key -> (categorical slot, short label). Slot 1 blue = city-local supply,
#: 2 orange = desalination, 3 aqua = farm water. Colour follows the family, never rank.
FAMILY = {
    "ag": (3, "Paying farmers, delivered"),
    "ag_unmitigated": (3, "Paying farmers, dust never controlled"),
    "conservation": (1, "Urban conservation"),
    "stormwater": (1, "Stormwater capture"),
    "reuse": (1, "Potable reuse (Pure Water SoCal)"),
    "desal_israeli": (2, "Desal at Israeli construction cost"),
    "desal_permit_reform": (2, "Desal, permitting reformed"),
    "desal_public": (2, "Desal at Carlsbad cost, public finance"),
    "desal_as_built": (2, "Desal as built (Carlsbad)"),
}
SHORT = {"ag": "Farms", "stormwater": "Stormwater", "conservation": "Conservation",
         "desal_public": "Desal (Carlsbad cost)", "reuse": "Reuse"}


# --------------------------------------------------------------------------------------
# Formatting
# --------------------------------------------------------------------------------------


def money(v: float, step: int = 10) -> str:
    return f"${round(v / step) * step:,.0f}"


def pct(v: float) -> str:
    return f"{v * 100:.0f}%"


def mdate(d) -> str:
    return f"{d:%B} {d.day}, {d.year}"


def maf(v: float) -> str:
    return f"{v:.2f} million acre-feet"


# --------------------------------------------------------------------------------------
# Chart payload
# --------------------------------------------------------------------------------------


def chart_data(n: dict) -> dict:
    res = n["res"]
    pr = F.prices()
    ladder = n["ladder"]
    ag = n["ag"]
    st = n["st"]
    stack_rows = [
        {"key": k, "label": FAMILY[k][1], "slot": FAMILY[k][0], **{
            kk: st[k][kk] for kk in ("median", "lo", "hi", "on_stack")}}
        for k in sorted(FAMILY, key=lambda k: st[k]["median"])
    ]
    curve = [{"key": r["key"], "label": r["label"], "short": SHORT[r["key"]],
              "slot": FAMILY[r["key"]][0], "cost": r["cost"],
              "qty": None if r["qty"] == float("inf") else r["qty"]} for r in F.supply_curve()]
    water_max = max(v for _, v in pr["water"])
    return {
        "basemap": json.loads((HERE / "basemap.json").read_text()),
        "relief": "data:image/jpeg;base64," + base64.b64encode((HERE / "relief.jpg").read_bytes()).decode(),
        "map": MAP,
        "n": {"imported": n["imported"]},
        "lines": {
            "reservoirs": {
                "height": 340, "y0": 0, "y1": 32,
                "series": [
                    {"name": "Lake Mead", "slot": 1, "pts": res["mead"]["monthly"]},
                    {"name": "Lake Powell", "slot": 2, "pts": res["powell"]["monthly"], "labelDy": 10},
                ],
                "notes": [
                    # One note above all the data (the series peak at 29.9M in 1942,
                    # far left), ringing both record lows, which are five weeks apart.
                    {"date": res["mead"]["low_date"].isoformat(), "value": res["mead"]["low_maf"],
                     "text": "Both at record lows, autumn 2026", "lead": 31,
                     "rings": [[res["powell"]["low_date"].isoformat(), res["powell"]["low_maf"]]]},
                ],
            },
            "prices": {
                "height": 300, "y0": 80, "y1": round(water_max / 20 + 1) * 20,
                "series": [
                    {"name": "Water, sewer & trash", "slot": 1, "pts": pr["water"][::1]},
                    {"name": "Everything", "slot": 2, "pts": pr["all"][::1]},
                ],
            },
        },
        "bars": {
            "delivered": {
                "xmax": 3400,
                "rows": [
                    {"label": "Paid to farmers today", "to": ag["payment"], "cls": "s3"},
                    {"label": "+ moving and treating it", "from": ag["payment"],
                     "to": ag["payment"] + ag["conveyance"], "cls": "s1",
                     "valueLabel": "+" + money(ag["conveyance"]),
                     "tip": f"+{money(ag['conveyance'])}/AF (range {money(n['conveyance_band'][0])}–{money(n['conveyance_band'][1])})"},
                    {"label": "+ Salton Sea dust", "from": ag["payment"] + ag["conveyance"],
                     "to": n["ag_total"], "cls": "s2", "valueLabel": "+" + money(ag["dust"]),
                     "tip": f"+{money(ag['dust'])}/AF, spread across all California farm conservation"},
                    {"label": "Delivered to a coastal city", "to": n["ag_total"], "cls": "ink"},
                ],
                "refs": [
                    {"value": ladder[3][1], "label": "Desal at Israeli cost", "anchor": "end"},
                    {"value": ladder[0][1], "label": "Desal as built", "anchor": "end"},
                ],
            },
            "salton": {
                "xmax": 5000,
                "rows": [
                    {"label": "If the state controls the dust", "to": n["salton"].after_dust_share, "cls": "s3",
                     "tip": f"{money(n['salton'].after_dust_share, 5)}/AF: the transfer's share of dust-control spending"},
                    {"label": "If it never does", "to": n["salton"].damage_basis, "cls": "s2",
                     "tip": f"{money(n['salton'].damage_basis)}/AF: the Pacific Institute's cost of inaction, attributed the same way"},
                ],
            },
            "ladder": {
                "xmax": 3400,
                "rows": [{"label": lbl, "to": v, "cls": "s2"} for lbl, v in ladder]
                + [{"label": "Paying farmers, delivered", "to": n["ag_total"], "cls": "s3"}],
                "refs": [{"value": n["imported"], "label": "Imported water today", "anchor": "end"}],
            },
        },
        "stack": stack_rows,
        "curve": curve,
        "cuts": [
            {"af": n["cut"], "label": "California's cut, 2027–28"},
            {"af": n["cut_hi"], "label": "Extreme case", "dy": 14},
        ],
        "timeline": TIMELINE,
    }


#: Map overlays, as (lon, lat). Aqueduct routes are schematic, through documented
#: waypoints, and labelled as approximate. Label placement was checked for collisions at
#: 358, 736 and 900 px: `short` replaces a name below 520 px, `labelMinW` hides only the
#: label below that width, `minW` hides the place entirely.
MAP = {
    "canals": [
        {"name": "Colorado River Aqueduct", "note": "Lake Havasu to Lake Mathews, 242 miles (Metropolitan). Route approximate.",
         "pts": [[-114.14, 34.30], [-114.75, 34.20], [-115.13, 34.13], [-115.63, 33.70],
                 [-116.25, 33.86], [-116.64, 33.92], [-116.95, 33.80], [-117.45, 33.85]]},
        {"name": "All-American Canal", "note": "Imperial Dam to the Imperial Valley. Route approximate.",
         "pts": [[-114.47, 32.88], [-114.70, 32.73], [-115.00, 32.70], [-115.30, 32.68], [-115.50, 32.80]]},
    ],
    "basins": [
        {"name": "Upper Basin", "at": [-107.4, 38.3], "narrow": [-107.1, 37.9]},
        {"name": "Lower Basin", "at": [-111.6, 34.25]},
    ],
    "states": [
        {"name": "California", "at": [-119.0, 36.4]}, {"name": "Nevada", "at": [-116.9, 39.4]},
        {"name": "Utah", "at": [-113.0, 39.6]}, {"name": "Arizona", "at": [-112.7, 35.3]},
        {"name": "Colorado", "at": [-105.35, 39.15]}, {"name": "New Mexico", "at": [-106.0, 33.8]},
        {"name": "Wyoming", "at": [-107.7, 43.25]}, {"name": "Mexico", "at": [-113.8, 31.6]},
    ],
    # dx/dy are screen pixels. `narrow` overrides placement below 520 px, where Southern
    # California is ~46 px across; `short` replaces the name below `shortBelow` (520).
    "places": [
        {"name": "Lake Powell", "at": [-110.55, 37.55], "kind": "lake", "dx": 4, "dy": 4,
         "note": "Record low since first filling: Sept. 15, 2026"},
        {"name": "Lees Ferry", "at": [-111.59, 36.87], "kind": "divide", "dx": -9, "dy": 4, "anchor": "end",
         "labelMinW": 520,
         "note": "Where the 1922 Compact divides the river between the Upper and Lower Basins"},
        {"name": "Lake Mead", "at": [-114.45, 36.2], "kind": "lake", "dx": -8, "dy": -6, "anchor": "end",
         "note": "Lowest in a record back to 1937: Oct. 22, 2026"},
        {"name": "Salton Sea", "at": [-116.05, 33.55], "kind": "lake", "dx": -6, "dy": -2, "anchor": "end",
         "narrow": {"dy": 3}, "note": "Fed mostly by Imperial Valley farm drainage. Shrinking."},
        {"name": "Los Angeles", "short": "L.A.", "at": [-118.24, 34.05], "big": True, "dx": 9, "dy": -7},
        {"name": "San Diego", "at": [-117.16, 32.72], "big": True, "dx": -6, "anchor": "end", "dy": 17,
         "narrow": {"dx": 0, "anchor": "middle", "dy": 17}},
        {"name": "Carlsbad desal plant", "at": [-117.34, 33.14], "kind": "desal",
         "dx": -9, "anchor": "end", "dy": 3, "labelMinW": 820,
         "note": "50 million gallons a day. Development began 1998; water from December 2015."},
        {"name": "Huntington Beach", "at": [-118.0, 33.66], "kind": "denied", "minW": 520, "labelMinW": 99999,
         "note": "Proposed desal plant. Same developer, size and start year as Carlsbad. Denied unanimously, May 2022."},
        {"name": "Palo Verde Valley", "short": "Palo Verde", "shortBelow": 820, "at": [-114.60, 33.60], "kind": "farm",
         "dx": 9, "dy": 4, "labelMinW": 520,
         "note": "Farmers paid to fallow ~26,000 acres. Drains back to the river, not the Salton Sea."},
        {"name": "Imperial Valley", "short": "Imperial", "shortBelow": 99999, "at": [-115.45, 32.85],
         "kind": "farm", "dx": 0, "dy": 18, "anchor": "middle", "labelMinW": 520,
         "note": "Largest user of Colorado River water. Drains to the Salton Sea."},
        {"name": "Phoenix", "at": [-112.07, 33.45], "minW": 520, "dx": 8, "dy": 4},
        {"name": "Denver", "at": [-104.99, 39.74], "minW": 520, "dx": -8, "anchor": "end"},
    ],
}

TIMELINE = [
    {"label": "Carlsbad, California", "end": "Water: Dec. 2015",
     "segs": [{"from": 1998, "to": 2012.95, "cls": "muted", "tip": "Development and permitting, 1998 to financial close in December 2012 (14½ years)"},
              {"from": 2012.95, "to": 2015.95, "cls": "s2", "tip": "Construction, 2013 to December 2015"}]},
    {"label": "Huntington Beach, California", "end": "Denied, May 2022",
     "segs": [{"from": 1998, "to": 2022.37, "cls": "muted", "tip": "Development and permitting, 1998 to a unanimous denial in May 2022 (~$100M spent)"}]},
    {"label": "Sorek, Israel", "end": "Water: 2013",
     "segs": [{"from": 2011.0, "to": 2013.5, "cls": "s2", "tip": "Construction, about 2½ years. Israel tenders plants on pre-designated sites."}]},
]


# --------------------------------------------------------------------------------------
# Data tables (the accessible, no-JS view of every chart)
# --------------------------------------------------------------------------------------


def _table(head: list[str], rows: list[list[str]]) -> str:
    th = "".join(f"<th>{html.escape(h)}</th>" for h in head)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return (f'<details class="data"><summary>Show the data</summary>'
            f'<div class="table-wrap"><table><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table></div></details>')


def tables(n: dict, data: dict) -> dict[str, str]:
    res = n["res"]
    yearly = {}
    for key in ("mead", "powell"):
        for d, v in res[key]["monthly"]:
            if d[5:7] == "01" or d == res[key]["monthly"][-1][0]:
                yearly.setdefault(d[:4] if d[5:7] == "01" else d[:7], {})[key] = v
    rows = [[y, f"{v.get('mead', ''):.2f}" if "mead" in v else "–", f"{v['powell']:.2f}" if "powell" in v else "–"]
            for y, v in sorted(yearly.items())]
    pr = F.prices()
    pw = {d: v for d, v in pr["water"]}
    prow = [[d[:4], f"{pw[d]:.0f}", f"{v:.0f}"] for d, v in pr["all"] if d.endswith("-01-01")]
    st = n["st"]
    out = {
        "reservoirs": _table(["January of", "Lake Mead (million AF)", "Lake Powell (million AF)"], rows),
        "prices": _table(["January of", "Water, sewer & trash (2000 = 100)", "All items (2000 = 100)"], prow),
        "delivered": _table(["Step", "$/AF (2025 $)"],
                            [[html.escape(r["label"]), money(r["to"] - r.get("from", 0))] for r in data["bars"]["delivered"]["rows"]]),
        "salton": _table(["Basis", "$ per acre-foot (2025 $)"],
                         [[html.escape(r["label"]), money(r["to"])] for r in data["bars"]["salton"]["rows"]]),
        "ladder": _table(["Version of the plant", "$/AF (2025 $)"], [[html.escape(l), money(v)] for l, v in n["ladder"]]),
        "stack": _table(["Option", "Median $/AF", "5th pct", "95th pct", "On the stack?"],
                        [[html.escape(FAMILY[k][1]), money(st[k]["median"]), money(st[k]["lo"]),
                          money(st[k]["hi"]), "yes" if st[k]["on_stack"] else "no, comparison"]
                         for k in sorted(FAMILY, key=lambda k: st[k]["median"])]),
        "curve": _table(["Option, cheapest first", "Median $/AF", "Median volume (AF/yr)"],
                        [[html.escape(c["label"]), money(c["cost"]),
                          "no practical limit" if c["qty"] is None else f"{c['qty']:,.0f}"] for c in data["curve"]]),
        "timeline": _table(["Project", "Milestones"], [
            ["Carlsbad", "Development began 1998; permits and financing Dec. 2012; water Dec. 2015"],
            ["Huntington Beach", "Development began 1998; denied by the Coastal Commission May 2022"],
            ["Sorek", "Built in about 2½ years; water 2013"]]),
        "validation": _table(["Published figure", "Dollar year", "Published", "Model"], [
            [html.escape(v["what"]), str(v["year"]),
             (f"${v['published']:.2f}" if v["published"] < 10 else money(v["published"], 1)),
             (f"${v['model']:.2f}" if v["model"] < 10 else money(v["model"], 1))] for v in n["validation"]]),
    }
    return out


def sources_html() -> str:
    items = []
    for c in F.used_citations():
        pub = f" — {html.escape(c.publisher)}" if c.publisher else ""
        items.append(f'<li><a href="{html.escape(c.url or "")}" rel="noopener">{html.escape(c.title)}</a>{pub}</li>')
    return "<ol class=\"sources\">" + "".join(items) + "</ol>"


# --------------------------------------------------------------------------------------
# Prose values
# --------------------------------------------------------------------------------------


def prose(n: dict) -> dict[str, str]:
    res, st, g, w = n["res"], n["st"], n["gap"], n["salton"]
    d = {
        "mead_low_date": mdate(res["mead"]["low_date"]),
        "mead_low": maf(res["mead"]["low_maf"]),
        "mead_low_pct": pct(n["mead_low_pct"]),
        "powell_low_date": mdate(res["powell"]["low_date"]),
        "powell_low": maf(res["powell"]["low_maf"]),
        "powell_last": f"{res['powell']['last_maf']:.2f}",
        "powell_last_pct": pct(n["powell_last_pct"]),
        "cpi_water": f"{n['cpi_water']:.0f}",
        "cpi_all": f"{n['cpi_all']:.0f}",
        "cpi_real": f"{n['cpi_real']:.0f}",
        "iid_rate": money(n["iid_rate"], 1),
        "city_rate": money(n["city_rate"], 1),
        "city_ag_ratio": f"{n['city_rate'] / n['ag_avg_rate']:.0f}",
        "cut": f"{n['cut']:,.0f}",
        "cut_hi": f"{n['cut_hi'] / 1e6:.1f} million",
        "phase0_ratio": f"{n['phase0_ratio']:.0f}",
        "ag_payment": money(n["ag"]["payment"]),
        "ag_conveyance": money(n["ag"]["conveyance"]),
        "conv_lo": money(n["conveyance_band"][0]),
        "conv_hi": money(n["conveyance_band"][1]),
        "ag_dust": money(n["ag"]["dust"]),
        "ag_total": money(n["ag_total"], 50),
        "delivered_ratio": f"{n['delivered_ratio']:.1f}",
        "israeli_ratio": f"{n['israeli_ratio']:.1f}",
        "iid_hist": money(n["iid_hist_per_af"]),
        "qsa_cap": f"${n['qsa_cap'] / 1e6:.0f} million",
        "qsa_volume": f"{n['qsa_volume']:,.0f}",
        "qsa_share": pct(n["qsa_share"]),
        "dust_share": pct(n["dust_share"]),
        "iid_share": pct(n["iid_share"]),
        "salton_full": money(w.full_attribution),
        "salton_share": money(w.after_qsa_share),
        "salton_dust": money(w.after_dust_share, 5),
        "salton_blend": money(w.per_blended_ag_af, 5),
        "salton_damage": money(w.damage_basis, 100),
        "salton_ratio": f"{w.damage_basis / w.after_dust_share:.0f}",
        "playa_2023": f"{n['playa_2023']:,.0f}",
        "gap": f"{g['gap']:.1f}",
        "gap_lo": f"{g['gap_lo']:.1f}",
        "gap_hi": f"{g['gap_hi']:.1f}",
        "raw_gap": f"{g['raw_x']:.1f}",
        "cb_unit": money(g["cb_unit"]),
        "sk_unit": money(g["sk_unit"]),
        "permit_x": f"{g['permit_x']:.1f}",
        "residual_x": f"{g['residual_x']:.0f}",
        "energy_af": money(n["ca_energy_af"]),
        "energy_ratio": f"{n['energy_ratio']:.0f}",
        "public_saving": money(n["public_saving"]),
        "reform_saving": money(n["reform_saving"]),
        "pwsc_mgd": f"${n['pwsc_per_mgd'] / 1e6:.0f} million",
        "cb_mgd": f"${n['cb_per_mgd'] / 1e6:.0f} million",
        "pwsc_cost": money(n["pwsc_cost"], 100),
        "pwsc_life": money(n["pwsc_life"], 100),
        "ipr_2015": money(n["pwsc_ipr_2015"], 100),
        "contract_2012": money(n["contract_2012"], 1),
        "contract_2025": money(n["contract_2025"], 10),
        "press_price": money(n["press_price"], 1),
        "hb_spend": f"${n['hb_spend'] / 1e6:.0f} million",
        "pvid_acres": f"{n['pvid_acres']:,.0f}",
        "imported": money(n["imported"]),
        "imported_nominal": money(n["imported_nominal"], 1),
        "pwsc_hi": money(n["pwsc_hi"], 100),
        "p_cheaper": f"{n['gate'].p_cheaper * 100:.1f}",
        "p_capacity": f"{n['gate'].p_capacity * 100:.0f}",
        "p_cheap_cut": pct(n["p_cheap_covers_cut"]),
        "p_cheap_hi": pct(n["p_cheap_covers_hi"]),
        "cheap_median": f"{n['cheap_median'] / 1e6:.1f} million",
        "n_draws": f"{n['n_draws']:,}",
        "built": mdate(n["today"]),
    }
    for k in ("ag", "conservation", "stormwater", "desal_israeli", "desal_permit_reform",
              "desal_public", "desal_as_built", "reuse", "ag_unmitigated"):
        d[f"{k}_med"] = money(st[k]["median"])
        d[f"{k}_lo"] = money(st[k]["lo"])
        d[f"{k}_hi"] = money(st[k]["hi"])
    for i, (_, v) in enumerate(n["ladder"]):
        d[f"ladder{i}"] = money(v)
    return d


# --------------------------------------------------------------------------------------
# Build
# --------------------------------------------------------------------------------------


def build(out: Path = OUT) -> Path:
    n = F.numbers()
    data = chart_data(n)
    values = prose(n)
    values |= {f"table_{k}": v for k, v in tables(n, data).items()}
    values["sources"] = sources_html()
    values["alt_delivered"] = (
        f"Bar chart building the delivered cost of farm water: "
        f"{values['ag_payment']} paid to farmers, plus {values['ag_conveyance']} to move and "
        f"treat it, plus {values['ag_dust']} for Salton Sea dust, about {values['ag_total']} in all, "
        f"against {values['ladder3']} for desal at Israeli cost and {values['ladder0']} for desal as built."
    )
    values["alt_ladder"] = (
        f"Bar chart: Carlsbad as built {values['ladder0']}; on public finance {values['ladder1']}; "
        f"with permitting reform {values['ladder2']}; at Israeli construction cost {values['ladder3']}; "
        f"paying farmers about {values['ag_total']}.")
    values["alt_salton"] = (
        f"Bar chart: the Salton Sea dust cost is about {values['salton_dust']} per Imperial "
        f"acre-foot if the state controls the dust, and about {values['salton_damage']} if it never does.")
    for k in ("alt_delivered", "alt_ladder", "alt_salton"):
        values[k] = html.escape(values[k])  # substituted values are not re-parsed
    values["data_json"] = json.dumps(data, separators=(",", ":")).replace("</", "<\\/")
    values["charts_js"] = (HERE / "charts.js").read_text()
    tpl = (HERE / "template.html").read_text()
    template = Template(tpl)
    if not template.is_valid():
        raise ValueError("template has a malformed placeholder (a literal $ must be written $$)")
    missing = set(template.get_identifiers()) - values.keys()
    if missing:
        raise KeyError(f"template uses values the model does not provide: {sorted(missing)}")
    page = template.substitute(values)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page)
    return out


__all__ = ["build", "stack"]
