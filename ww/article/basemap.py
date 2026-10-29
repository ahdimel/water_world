"""Build the article's basin map geometry from Natural Earth (public domain).

Run once, by hand, against downloaded Natural Earth GeoJSON; the projected, simplified
result (`basemap.json`) is committed so the article build never touches the network:

    python -m ww.article.basemap /path/to/natural-earth-geojson-dir

Projection: equirectangular scaled by cos(36°N), adequate for a region this size and
easy to reason about. Coordinates are SVG units in a 1000-wide frame.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

OUT = Path(__file__).with_name("basemap.json")

#: lon/lat window: the lower basin and Southern California, Lake Powell to the border.
WEST, EAST, SOUTH, NORTH = -120.0, -108.5, 31.3, 38.0
WIDTH = 1000.0
_K = math.cos(math.radians(36.0))
HEIGHT = WIDTH * (NORTH - SOUTH) / ((EAST - WEST) * _K)

STATES = {"California", "Nevada", "Arizona", "Utah", "Colorado", "New Mexico", "Wyoming",
          "Baja California", "Sonora", "Oregon", "Idaho"}
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


def build(src: Path) -> dict:
    states = json.loads((src / "ne_50m_admin_1_states_provinces_lakes.geojson").read_text())
    rivers = json.loads((src / "ne_10m_rivers_lake_centerlines.geojson").read_text())
    lakes = json.loads((src / "ne_10m_lakes.geojson").read_text())
    coast = json.loads((src / "ne_50m_coastline.geojson").read_text())

    def inside(geom: dict) -> bool:
        pts = [p for ring in _lines(geom) for p in ring]
        return any(WEST - 2 < x < EAST + 2 and SOUTH - 2 < y < NORTH + 2 for x, y in pts)

    out: dict = {"width": WIDTH, "height": round(HEIGHT, 1), "states": {}, "rivers": {},
                 "lakes": {}, "coast": "", "window": [WEST, EAST, SOUTH, NORTH],
                 "source": "Natural Earth (public domain), 1:50m states/coast, 1:10m rivers/lakes"}
    for f in states["features"]:
        name = f["properties"].get("name")
        if name in STATES and inside(f["geometry"]):
            out["states"][name] = _path(_lines(f["geometry"]), 1.2, True)
    for f in rivers["features"]:
        name = f["properties"].get("name")
        if name in RIVERS and inside(f["geometry"]):
            out["rivers"][name] = out["rivers"].get(name, "") + _path(_lines(f["geometry"]), 0.8, False)
    for f in lakes["features"]:
        name = f["properties"].get("name")
        if name in LAKES:
            out["lakes"][name] = _path(_lines(f["geometry"]), 0.4, True)
    def clip(ring: list) -> list[list]:
        """Split a line into runs that stay within the window (plus a margin)."""
        runs, cur = [], []
        for x, y in ring:
            if WEST - 0.5 < x < EAST + 0.5 and SOUTH - 0.5 < y < NORTH + 0.5:
                cur.append((x, y))
            elif cur:
                runs.append(cur)
                cur = []
        return runs + ([cur] if cur else [])

    out["coast"] = "".join(_path([run for ring in _lines(f["geometry"]) for run in clip(ring)],
                                 1.5, False) for f in coast["features"])
    return out


if __name__ == "__main__":
    data = build(Path(sys.argv[1]))
    OUT.write_text(json.dumps(data, separators=(",", ":")))
    print(f"wrote {OUT} ({OUT.stat().st_size:,} bytes)")
