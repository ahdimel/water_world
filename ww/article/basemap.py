"""Build the article's basin map geometry (vector layers over the relief image).

Run once, by hand, against downloaded public-domain data; the projected, simplified
result (`basemap.json`) is committed so the article build never touches the network:

    python -m ww.article.basemap <natural-earth-geojson-dir> <wbd-dir>

Sources: Natural Earth (states, countries, coast, rivers, lakes) and the USGS Watershed
Boundary Dataset hydrologic regions 14 (Upper Colorado) and 15 (Lower Colorado), queried
from hydro.nationalmap.gov as `huc14.geojson` / `huc15.geojson`.

Projection: equirectangular scaled by cos(37°N), adequate for a region this size and
easy to reason about. Coordinates are SVG units in a 1000-wide frame. `relief.py` renders
the shaded-relief image in exactly this frame.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

OUT = Path(__file__).with_name("basemap.json")

#: lon/lat window: the whole basin, from Wyoming to the Gulf, plus the Southern
#: California coast its water is carried to.
WEST, EAST, SOUTH, NORTH = -120.0, -104.6, 31.0, 43.7
WIDTH = 1000.0
_K = math.cos(math.radians(37.0))
HEIGHT = WIDTH * (NORTH - SOUTH) / ((EAST - WEST) * _K)

STATES = {"California", "Nevada", "Arizona", "Utah", "Colorado", "New Mexico", "Wyoming",
          "Oregon", "Idaho"}
COUNTRIES = {"United States of America", "Mexico"}
RIVERS = {"Colorado", "Green", "San Juan", "Gila"}
LAKES = {"Lake Powell", "Lake Mead", "Lake Havasu", "Lake Mohave",
         "Flaming Gorge Reservoir", "Salton Sea"}


def project(lon: float, lat: float) -> tuple[float, float]:
    x = (lon - WEST) / (EAST - WEST) * WIDTH
    y = (NORTH - lat) / (NORTH - SOUTH) * HEIGHT
    return round(x, 1), round(y, 1)


def _simplify(pts: list[tuple[float, float]], tol: float) -> list[tuple[float, float]]:
    """Douglas-Peucker in projected units."""
    if len(pts) < 3:
        return pts
    (x1, y1), (x2, y2) = pts[0], pts[-1]
    dx, dy = x2 - x1, y2 - y1
    norm = math.hypot(dx, dy) or 1e-9
    worst, idx = 0.0, 0
    for i, (x, y) in enumerate(pts[1:-1], 1):
        d = abs(dy * x - dx * y + x2 * y1 - y2 * x1) / norm
        if d > worst:
            worst, idx = d, i
    if worst <= tol:
        return [pts[0], pts[-1]]
    return _simplify(pts[: idx + 1], tol)[:-1] + _simplify(pts[idx:], tol)


def _lines(geom: dict) -> list[list]:
    t, c = geom["type"], geom["coordinates"]
    if t == "LineString":
        return [c]
    if t in ("MultiLineString", "Polygon"):
        return c
    if t == "MultiPolygon":
        return [ring for poly in c for ring in poly]
    return []


def _path(rings: list[list], tol: float, closed: bool) -> str:
    out = []
    for ring in rings:
        proj = [project(x, y) for x, y in ring]
        if closed and len(proj) > 3:
            # A closed ring starts and ends on one point, which degenerates the
            # Douglas-Peucker baseline; simplify the two halves separately.
            mid = len(proj) // 2
            pts = _simplify(proj[: mid + 1], tol)[:-1] + _simplify(proj[mid:], tol)
        else:
            pts = _simplify(proj, tol)
        if len(pts) < 2:
            continue
        d = "M" + "L".join(f"{x:g},{y:g}" for x, y in pts)
        out.append(d + ("Z" if closed else ""))
    return "".join(out)


def _inside(geom: dict) -> bool:
    pts = [p for ring in _lines(geom) for p in ring]
    return any(WEST - 2 < x < EAST + 2 and SOUTH - 2 < y < NORTH + 2 for x, y in pts)


def build(ne: Path, wbd: Path) -> dict:
    load = lambda p: json.loads(p.read_text())  # noqa: E731
    states = load(ne / "ne_50m_admin_1_states_provinces_lakes.geojson")
    rivers = load(ne / "ne_10m_rivers_lake_centerlines.geojson")
    lakes = load(ne / "ne_10m_lakes.geojson")

    out: dict = {"width": WIDTH, "height": round(HEIGHT, 1), "states": {}, "rivers": {},
                 "lakes": {}, "basins": {}, "window": [WEST, EAST, SOUTH, NORTH], "k_lat": 37.0,
                 "source": "Natural Earth (public domain); USGS Watershed Boundary Dataset"}
    for f in states["features"]:
        name = f["properties"].get("name")
        if name in STATES and _inside(f["geometry"]):
            out["states"][name] = _path(_lines(f["geometry"]), 1.0, True)
    for f in rivers["features"]:
        name = f["properties"].get("name")
        if name in RIVERS and _inside(f["geometry"]):
            out["rivers"][name] = out["rivers"].get(name, "") + _path(_lines(f["geometry"]), 0.8, False)
    for f in lakes["features"]:
        name = f["properties"].get("name")
        if name in LAKES:
            out["lakes"][name] = _path(_lines(f["geometry"]), 0.4, True)
    for huc, name in (("14", "upper"), ("15", "lower")):
        g = load(wbd / f"huc{huc}.geojson")
        out["basins"][name] = "".join(_path(_lines(f["geometry"]), 0.8, True) for f in g["features"])
    return out


if __name__ == "__main__":
    data = build(Path(sys.argv[1]), Path(sys.argv[2]))
    OUT.write_text(json.dumps(data, separators=(",", ":")))
    print(f"wrote {OUT} ({OUT.stat().st_size:,} bytes), {data['width']:g} x {data['height']:g}")
