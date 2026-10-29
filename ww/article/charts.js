// Charts for the water_world article. Vanilla JS, no dependencies.
//
// Every chart is drawn at the container's real pixel width (and redrawn on resize), so
// text stays a readable size on a phone instead of shrinking with a scaled viewBox.
// Data comes from the JSON block the build step embeds; nothing here invents a number.
// Colours are CSS custom properties, so light/dark and the site's theme toggle just work.
(function () {
  "use strict";
  const DATA = JSON.parse(document.getElementById("article-data").textContent);
  const NS = "http://www.w3.org/2000/svg";

  // ---------------------------------------------------------------- helpers
  function el(tag, attrs, parent) {
    const e = document.createElementNS(NS, tag);
    for (const k in attrs || {}) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  }
  function text(parent, x, y, str, cls, anchor) {
    const t = el("text", { x: x, y: y, class: cls || "t-axis", "text-anchor": anchor || "start" }, parent);
    t.textContent = str;
    return t;
  }
  // Rough rendered width of a label, for collision decisions (~0.58em per character).
  const tw = (str, px) => String(str).length * (px || 13) * 0.58;
  const usd = (v) => "$" + Math.round(v).toLocaleString("en-US");
  const usd10 = (v) => "$" + (Math.round(v / 10) * 10).toLocaleString("en-US");
  const af = (v) => (v >= 1e6 ? (v / 1e6).toFixed(2) + "M" : Math.round(v / 1000) + "k") + " AF";
  const linear = (d0, d1, r0, r1) => (v) => r0 + ((v - d0) / (d1 - d0)) * (r1 - r0);
  function niceTicks(lo, hi, n) {
    const span = hi - lo, step0 = span / n, mag = Math.pow(10, Math.floor(Math.log10(step0)));
    const step = [1, 2, 2.5, 5, 10].map((m) => m * mag).find((s) => span / s <= n) || 10 * mag;
    const out = [];
    for (let v = Math.ceil(lo / step) * step; v <= hi + 1e-9; v += step) out.push(+v.toFixed(6));
    return out;
  }
  function svgFor(node, height) {
    node.querySelectorAll("svg").forEach((s) => s.remove());
    const w = Math.max(280, node.clientWidth);
    const svg = el("svg", { width: w, height: height, viewBox: `0 0 ${w} ${height}`, role: "img" });
    svg.setAttribute("aria-label", node.dataset.label || "");
    node.appendChild(svg);
    return { svg, w, narrow: w < 520 };
  }

  // ---------------------------------------------------------------- tooltip
  const tip = document.createElement("div");
  tip.className = "viz-tip";
  tip.setAttribute("role", "status");
  document.body.appendChild(tip);
  function showTip(html, x, y) {
    tip.innerHTML = html;
    tip.style.display = "block";
    const r = tip.getBoundingClientRect();
    let left = x + 14, top = y + 14;
    if (left + r.width > window.innerWidth - 8) left = x - r.width - 14;
    if (top + r.height > window.innerHeight - 8) top = y - r.height - 14;
    tip.style.left = Math.max(8, left) + "px";
    tip.style.top = Math.max(8, top) + "px";
  }
  function hideTip() { tip.style.display = "none"; }
  function hover(target, html) {
    target.classList.add("hit");
    target.addEventListener("pointermove", (e) => showTip(html, e.clientX, e.clientY));
    target.addEventListener("pointerleave", hideTip);
  }
  window.addEventListener("scroll", hideTip, { passive: true });

  // ---------------------------------------------------------------- 1. map
  // Shaded relief (a JPEG rendered in exactly this frame by relief.py) under vector
  // layers. Everything outside the Colorado basin sits under a veil, so the basin reads.
  function drawMap(node) {
    const m = DATA.basemap, W = m.width, H = m.height;
    node.querySelectorAll("svg").forEach((s) => s.remove());
    const w = Math.max(280, node.clientWidth), k = w / W, h = H * k, narrow = w < 520;
    const svg = el("svg", { width: w, height: h, viewBox: `0 0 ${W} ${H}`, role: "img", class: "map" }, node);
    svg.setAttribute("aria-label", node.dataset.label);
    const fs = (px) => px / k; // font size in viewBox units that renders at `px`
    el("image", { href: DATA.relief, x: 0, y: 0, width: W, height: H, preserveAspectRatio: "none", class: "map-relief" }, svg);
    el("path", { d: `M0,0H${W}V${H}H0Z` + m.basins.upper + m.basins.lower, class: "map-veil", "fill-rule": "evenodd" }, svg);
    el("path", { d: m.basins.upper, class: "map-upper" }, svg);
    for (const name in m.states) el("path", { d: m.states[name], class: "map-state-line", "stroke-width": 1 / k }, svg);
    for (const b of ["upper", "lower"]) el("path", { d: m.basins[b], class: "map-basin", "stroke-width": 1.6 / k }, svg);
    for (const name in m.rivers) {
      const r = el("path", { d: m.rivers[name], class: name === "Colorado" ? "map-river main" : "map-river", "stroke-width": (name === "Colorado" ? 2.6 : 1.4) / k }, svg);
      hover(r, `<b>${name === "Colorado" ? "Colorado River" : name + " River"}</b>`);
    }
    for (const name in m.lakes) hover(el("path", { d: m.lakes[name], class: "map-lake" }, svg), `<b>${name}</b>`);
    for (const c of DATA.map.canals) {
      const d = "M" + c.pts.map((p) => DATA.proj(p).join(",")).join("L");
      const path = el("path", { d: d, class: "map-canal", "stroke-width": 2.5 / k, "stroke-dasharray": `${6 / k} ${4 / k}` }, svg);
      hover(path, `<b>${c.name}</b><br>${c.note}`);
    }
    const g = el("g", {}, svg);
    if (!narrow) for (const s of DATA.map.states) {
      const [x, y] = DATA.proj(s.at);
      text(g, x, y, s.name.toUpperCase(), "map-state", "middle").setAttribute("font-size", fs(10));
    }
    for (const b of DATA.map.basins) {
      const [x, y] = DATA.proj(narrow && b.narrow ? b.narrow : b.at);
      text(g, x, y, b.name.toUpperCase(), "map-basin-label", "middle").setAttribute("font-size", fs(narrow ? 11.5 : 14));
    }
    for (const p of DATA.map.places) {
      if (p.minW && w < p.minW) continue; // dot and label both
      const [x, y] = DATA.proj(p.at);
      const dot = el("circle", { cx: x, cy: y, r: (p.big ? 5 : 4) / k, class: "map-dot " + (p.kind || ""), "stroke-width": 1.5 / k }, g);
      if (p.note) hover(dot, `<b>${p.name}</b><br>${p.note}`);
      if (p.labelMinW && w < p.labelMinW) continue; // dot only
      const name = p.short && w < (p.shortBelow || 520) ? p.short : p.name;
      const o = Object.assign({}, p, narrow ? p.narrow || {} : {});
      const dx = o.dx === undefined ? 8 : o.dx, dy = o.dy === undefined ? 4 : o.dy;
      const t = text(g, x + dx / k, y + dy / k, name, "map-label", o.anchor || "start");
      t.setAttribute("font-size", fs(p.big ? 12.5 : 11.5));
      t.setAttribute("stroke-width", 3 / k);
    }
  }

  // ---------------------------------------------------------------- 2/3. line charts
  function drawLines(node, cfg) {
    const H = cfg.height || 340;
    const { svg, w, narrow } = svgFor(node, H);
    const longest = Math.max(...cfg.series.map((s) => tw(s.name, 13.5)));
    const m = { l: 44, r: narrow ? 12 : longest + 18, t: 16, b: 30 };
    const all = cfg.series.flatMap((s) => s.pts);
    const t0 = Date.parse(cfg.x0 || all[0][0]), t1 = Date.parse(all[all.length - 1][0]);
    const x = linear(t0, Math.max(...cfg.series.map((s) => Date.parse(s.pts[s.pts.length - 1][0]))), m.l, w - m.r);
    const y = linear(cfg.y0, cfg.y1, H - m.b, m.t);
    for (const v of niceTicks(cfg.y0, cfg.y1, 5)) {
      if (v === cfg.y0) continue;
      el("line", { x1: m.l, x2: w - m.r, y1: y(v), y2: y(v), class: "grid" }, svg);
      text(svg, m.l - 6, y(v) + 4, cfg.yfmt(v), "t-axis", "end");
    }
    el("line", { x1: m.l, x2: w - m.r, y1: y(cfg.y0), y2: y(cfg.y0), class: "axis" }, svg);
    text(svg, m.l - 6, y(cfg.y0) + 4, cfg.yfmt(cfg.y0), "t-axis", "end");
    const years = niceTicks(new Date(t0).getUTCFullYear(), new Date(t1).getUTCFullYear(), narrow ? 4 : 8);
    for (const yr of years) {
      const xx = x(Date.UTC(yr, 0, 1));
      if (xx < m.l - 1) continue;
      text(svg, xx, H - m.b + 18, String(yr), "t-axis", "middle");
    }
    cfg.series.forEach((s, i) => {
      const d = s.pts.map((p, j) => (j ? "L" : "M") + x(Date.parse(p[0])).toFixed(1) + "," + y(p[1]).toFixed(1)).join("");
      el("path", { d: d, class: "line s" + (s.slot || i + 1) }, svg);
      const last = s.pts[s.pts.length - 1];
      el("circle", { cx: x(Date.parse(last[0])), cy: y(last[1]), r: 4, class: "dot s" + (s.slot || i + 1) }, svg);
      if (!narrow) text(svg, x(Date.parse(last[0])) + 8, y(last[1]) + 4 + (s.labelDy || 0), s.name, "t-label");
    });
    for (const a of cfg.notes || []) {
      // Leader line from the point up into clear space, label to its left.
      const xx = x(Date.parse(a.date)), yy = y(a.value), ly = y(a.lead);
      el("line", { x1: xx, x2: xx, y1: yy - 5, y2: ly, class: "leader" }, svg);
      el("circle", { cx: xx, cy: yy, r: 4, class: "dot ring" }, svg);
      for (const [d, v] of a.rings || []) el("circle", { cx: x(Date.parse(d)), cy: y(v), r: 4, class: "dot ring" }, svg);
      text(svg, xx - 5, ly + 4, a.text, "t-note", "end");
    }
    // crosshair
    const cross = el("line", { y1: m.t, y2: H - m.b, class: "cross", visibility: "hidden" }, svg);
    const hit = el("rect", { x: m.l, y: m.t, width: w - m.l - m.r, height: H - m.t - m.b, fill: "transparent" }, svg);
    hit.addEventListener("pointermove", (e) => {
      const r = svg.getBoundingClientRect(), px = e.clientX - r.left;
      const tt = t0 + ((px - m.l) / (w - m.r - m.l)) * (Math.max(...cfg.series.map((s) => Date.parse(s.pts[s.pts.length - 1][0]))) - t0);
      cross.setAttribute("x1", px); cross.setAttribute("x2", px); cross.setAttribute("visibility", "visible");
      const rows = cfg.series.map((s, i) => {
        let best = null;
        for (const p of s.pts) { const dt = Math.abs(Date.parse(p[0]) - tt); if (!best || dt < best.dt) best = { dt, p }; }
        if (!best || best.dt > 1000 * 86400 * 62) return "";
        return `<span class="k s${s.slot || i + 1}"></span>${s.name}: <b>${cfg.yfmt(best.p[1], true)}</b>`;
      }).filter(Boolean);
      const when = new Date(tt).toLocaleDateString("en-US", { year: "numeric", month: "short", timeZone: "UTC" });
      showTip(`<div class="tip-h">${when}</div>${rows.join("<br>")}`, e.clientX, e.clientY);
    });
    hit.addEventListener("pointerleave", () => { cross.setAttribute("visibility", "hidden"); hideTip(); });
  }

  // ---------------------------------------------------------------- horizontal bars
  // Used by the waterfall, the Salton walk and the desal ladder.
  function drawBars(node, cfg) {
    const refs = cfg.refs || [];
    const rowH = 44, head = refs.length * 16 + (refs.length ? 6 : 0);
    const H = cfg.rows.length * rowH + 40 + head;
    const { svg, w, narrow } = svgFor(node, H);
    const m = { l: 12, r: 24, t: 8 + head, b: 26 };
    const xmax = cfg.xmax;
    const x = linear(0, xmax, m.l, w - m.r);
    for (const v of niceTicks(0, xmax, narrow ? 3 : 6)) {
      el("line", { x1: x(v), x2: x(v), y1: m.t, y2: H - m.b, class: v === 0 ? "axis" : "grid" }, svg);
      text(svg, x(v), H - m.b + 16, usd(v), "t-axis", "middle");
    }
    refs.forEach((ref, i) => {
      // Each reference line gets its own label row above the bars, so labels never collide.
      const ly = 12 + i * 16;
      el("line", { x1: x(ref.value), x2: x(ref.value), y1: ly + 4, y2: H - m.b, class: "ref" }, svg);
      const str = ref.label + " " + usd10(ref.value), sw = tw(str, 12.5), rx = x(ref.value);
      if (rx - 4 - sw > m.l) text(svg, rx - 4, ly, str, "t-note", "end");
      else if (rx + 4 + sw < w - 2) text(svg, rx + 4, ly, str, "t-note");
      else text(svg, w - 2, ly, str, "t-note", "end");
    });
    cfg.rows.forEach((r, i) => {
      const y0 = m.t + i * rowH;
      text(svg, m.l, y0 + 13, r.label, "t-label");
      const a = x(r.from || 0), b = x(Math.min(r.to, xmax));
      const bar = el("rect", { x: Math.min(a, b), y: y0 + 19, width: Math.max(2, Math.abs(b - a)), height: 16, rx: 3, class: "bar " + (r.cls || "s1") }, svg);
      hover(bar, `<b>${r.label}</b><br>${r.tip || usd(r.to)}`);
      const val = r.valueLabel || usd10(r.to);
      const tx = Math.max(a, b) + 6;
      if (r.to > xmax) {
        text(svg, w - m.r - 6, y0 + 32, val + " →", "t-in", "end");
      } else if (tx + tw(val) > w - 2) {
        text(svg, Math.max(a, b) - 6, y0 + 32, val, "t-in", "end");
      } else {
        text(svg, tx, y0 + 32, val, "t-value");
      }
    });
  }

  // ---------------------------------------------------------------- the stack (dot + band)
  function drawStack(node) {
    const rows = DATA.stack;
    const rowH = 40, H = rows.length * rowH + 48;
    const { svg, w, narrow } = svgFor(node, H);
    const m = { l: 12, r: 24, t: 26, b: 26 };
    const xmax = 7000, x = linear(0, xmax, m.l, w - m.r);
    for (const v of niceTicks(0, xmax, narrow ? 3 : 7)) {
      el("line", { x1: x(v), x2: x(v), y1: m.t - 6, y2: H - m.b, class: v === 0 ? "axis" : "grid" }, svg);
      text(svg, x(v), H - m.b + 16, usd(v), "t-axis", "middle");
    }
    const imp = DATA.n.imported;
    el("line", { x1: x(imp), x2: x(imp), y1: m.t - 14, y2: H - m.b, class: "ref" }, svg);
    text(svg, x(imp) + 4, m.t - 14, "Imported water today " + usd10(imp), "t-note");
    rows.forEach((r, i) => {
      const y0 = m.t + i * rowH;
      text(svg, m.l, y0 + 12, r.label + (r.on_stack ? "" : " *"), r.on_stack ? "t-label" : "t-label off");
      const yy = y0 + 24;
      const band = el("line", { x1: x(r.lo), x2: x(Math.min(r.hi, xmax)), y1: yy, y2: yy, class: "band s" + r.slot + (r.on_stack ? "" : " off") }, svg);
      const dot = el("circle", { cx: x(r.median), cy: yy, r: 5.5, class: "dot s" + r.slot + (r.on_stack ? "" : " hollow") }, svg);
      const html = `<b>${r.label}</b><br>Best estimate <b>${usd10(r.median)}</b>/AF<br>Likely range: ${usd10(r.lo)}–${usd10(r.hi)}` + (r.on_stack ? "" : "<br><i>Off the stack: shown for comparison</i>");
      hover(dot, html); hover(band, html);
      const v = usd10(r.median);
      if (x(Math.min(r.hi, xmax)) + 8 + tw(v) < w) text(svg, x(Math.min(r.hi, xmax)) + 8, yy + 4, v, "t-value");
      else text(svg, x(r.lo) - 8, yy + 4, v, "t-value", "end");
    });
  }

  // ---------------------------------------------------------------- supply curve (steps)
  function drawCurve(node) {
    const H = 360;
    const { svg, w, narrow } = svgFor(node, H);
    const m = { l: 52, r: 14, t: 18, b: 40 };
    const steps = DATA.curve, xmax = 2.0e6, ymax = 6500;
    const x = linear(0, xmax, m.l, w - m.r), y = linear(0, ymax, H - m.b, m.t);
    for (const v of niceTicks(0, ymax, 5)) {
      el("line", { x1: m.l, x2: w - m.r, y1: y(v), y2: y(v), class: v === 0 ? "axis" : "grid" }, svg);
      text(svg, m.l - 6, y(v) + 4, usd(v), "t-axis", "end");
    }
    for (const v of niceTicks(0, xmax, narrow ? 4 : 8)) {
      text(svg, x(v), H - m.b + 16, v === 0 ? "0" : (v / 1e6).toFixed(v % 1e6 ? 2 : 0).replace(/0$/, "") + "M", "t-axis", "middle");
    }
    text(svg, (m.l + w - m.r) / 2, H - 6, "Acre-feet a year, cumulative, cheapest first", "t-axis", "middle");
    let cum = 0;
    for (const s of steps) {
      const width = s.qty === null ? xmax - cum : s.qty;
      const a = x(cum), b = x(Math.min(cum + width, xmax));
      const r = el("rect", { x: a + 1, y: y(s.cost), width: Math.max(1, b - a - 2), height: y(0) - y(s.cost), rx: 3, class: "step s" + s.slot }, svg);
      hover(r, `<b>${s.label}</b><br>${usd10(s.cost)}/AF (median)<br>` + (s.qty === null ? "No practical volume limit" : "About " + af(s.qty) + " a year"));
      const lbl = s.short || s.label, cx = Math.min((a + b) / 2, w - m.r - tw(lbl, 12.5) / 2);
      if (tw(lbl, 12.5) < b - a + 8 || s.qty === null) text(svg, cx, y(s.cost) - 6, lbl, "t-note", "middle");
      cum += width;
      if (cum >= xmax) break;
    }
    DATA.cuts.forEach((c, i) => {
      el("line", { x1: x(c.af), x2: x(c.af), y1: m.t, y2: y(0), class: "ref" }, svg);
      const left = x(c.af) - 4 - tw(c.label, 12.5) > m.l;
      text(svg, x(c.af) + (left ? -4 : 4), m.t + 10 + i * 16, c.label, "t-note", left ? "end" : "start");
    });
  }

  // ---------------------------------------------------------------- timeline
  function drawTimeline(node) {
    const rows = DATA.timeline, rowH = 52, H = rows.length * rowH + 34;
    const { svg, w, narrow } = svgFor(node, H);
    const m = { l: 12, r: 18, t: 8, b: 24 };
    const x = linear(1997, 2026, m.l, w - m.r);
    for (const yr of niceTicks(1997, 2026, narrow ? 4 : 7)) {
      el("line", { x1: x(yr), x2: x(yr), y1: m.t, y2: H - m.b, class: "grid" }, svg);
      text(svg, x(yr), H - m.b + 16, String(yr), "t-axis", "middle");
    }
    rows.forEach((r, i) => {
      const y0 = m.t + i * rowH;
      text(svg, m.l, y0 + 13, r.label, "t-label");
      for (const seg of r.segs) {
        const b = el("rect", { x: x(seg.from), y: y0 + 20, width: Math.max(3, x(seg.to) - x(seg.from)), height: 14, rx: 3, class: "bar " + seg.cls }, svg);
        hover(b, `<b>${r.label}</b><br>${seg.tip}`);
      }
      const end = r.segs[r.segs.length - 1];
      const ex = x(end.to) + 6;
      if (ex + 110 < w) text(svg, ex, y0 + 32, r.end, "t-value");
      else text(svg, x(r.segs[0].from) - 0, y0 + 48, r.end, "t-value");
    });
  }

  // ---------------------------------------------------------------- wiring
  const DRAW = {
    map: drawMap,
    reservoirs: (n) => drawLines(n, DATA.lines.reservoirs),
    prices: (n) => drawLines(n, DATA.lines.prices),
    delivered: (n) => drawBars(n, DATA.bars.delivered),
    salton: (n) => drawBars(n, DATA.bars.salton),
    ladder: (n) => drawBars(n, DATA.bars.ladder),
    stack: drawStack,
    curve: drawCurve,
    timeline: drawTimeline,
  };
  // y-axis formatters cannot travel in JSON.
  DATA.lines.reservoirs.yfmt = (v, tip) => (tip ? v.toFixed(2) + " million AF" : v + "M");
  DATA.lines.prices.yfmt = (v) => String(Math.round(v));
  const [W, E, S, N] = DATA.basemap.window;
  const Hm = DATA.basemap.height;
  DATA.proj = ([lon, lat]) => [((lon - W) / (E - W)) * 1000, ((N - lat) / (N - S)) * Hm];

  function drawAll() {
    document.querySelectorAll("[data-chart]").forEach((n) => {
      try { DRAW[n.dataset.chart](n); } catch (err) { console.error("chart", n.dataset.chart, err); }
    });
  }
  let last = 0;
  window.addEventListener("resize", () => {
    const wNow = document.documentElement.clientWidth;
    if (wNow === last) return;
    last = wNow;
    clearTimeout(drawAll.t);
    drawAll.t = setTimeout(drawAll, 120);
  });
  last = document.documentElement.clientWidth;
  drawAll();
})();
