"""Render the shaded-relief background for the basin map.

A one-off generator, run by hand like `basemap.py`; its output (`relief.jpg`) is
committed and embedded in the article. It needs numpy and Pillow, which the project
does not otherwise depend on, so run it from any environment that has them:

    <python-with-numpy-pillow> ww/article/relief.py <terrarium-tile-dir> <natural-earth-dir>

Elevation: Mapzen/AWS Terrain Tiles, "terrarium" encoding, zoom 7 (from USGS NED and
NASA SRTM). Land mask: Natural Earth admin-0 countries. The image is drawn in exactly
the frame `basemap.py` projects into, so the SVG layers line up.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ww.article.basemap import EAST, HEIGHT, NORTH, SOUTH, WEST, WIDTH  # noqa: E402

OUT = Path(__file__).with_name("relief.jpg")
ZOOM = 7
SCALE = 1.2  # image pixels per SVG unit: 1200 px wide, sharp enough on a 900 px frame

#: Hypsometric tint (metres -> RGB): pale desert floor to tan uplands to pale peaks.
STOPS = [(-100, (233, 229, 214)), (0, (233, 229, 214)), (800, (226, 218, 192)),
         (1600, (210, 196, 160)), (2400, (190, 172, 138)), (3200, (176, 160, 136)),
         (4200, (236, 233, 228))]
OCEAN = (207, 223, 236)


def mosaic(tiles: Path) -> tuple[np.ndarray, int, int]:
    files = sorted(tiles.glob(f"{ZOOM}-*-*.png"))
    xs = sorted({int(f.stem.split("-")[1]) for f in files})
    ys = sorted({int(f.stem.split("-")[2]) for f in files})
    elev = np.zeros((len(ys) * 256, len(xs) * 256), dtype=np.float32)
    for f in files:
        _, x, y = (int(v) for v in f.stem.split("-"))
        rgb = np.asarray(Image.open(f).convert("RGB"), dtype=np.float32)
        e = rgb[..., 0] * 256 + rgb[..., 1] + rgb[..., 2] / 256 - 32768
        r, c = ys.index(y) * 256, xs.index(x) * 256
        elev[r:r + 256, c:c + 256] = e
    return elev, xs[0], ys[0]


def sample(elev: np.ndarray, x0: int, y0: int, lon: np.ndarray, lat: np.ndarray) -> np.ndarray:
    n = 2 ** ZOOM
    px = (lon + 180) / 360 * n * 256 - x0 * 256
    lr = np.radians(lat)
    py = (1 - np.log(np.tan(lr) + 1 / np.cos(lr)) / math.pi) / 2 * n * 256 - y0 * 256
    i = np.clip(py.astype(int), 0, elev.shape[0] - 1)
    j = np.clip(px.astype(int), 0, elev.shape[1] - 1)
    return elev[i, j]


def land_mask(ne: Path, w: int, h: int) -> np.ndarray:
    countries = json.loads((ne / "ne_50m_admin_0_countries.geojson").read_text())
    img = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(img)
    for f in countries["features"]:
        if f["properties"].get("ADMIN") not in ("United States of America", "Mexico"):
            continue
        g = f["geometry"]
        polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        for poly in polys:
            ring = [((x - WEST) / (EAST - WEST) * w, (NORTH - y) / (NORTH - SOUTH) * h)
                    for x, y in poly[0]]
            draw.polygon(ring, fill=255)
    return np.asarray(img) > 0


def tint(e: np.ndarray) -> np.ndarray:
    out = np.zeros(e.shape + (3,), dtype=np.float32)
    levels = [s[0] for s in STOPS]
    for ch in range(3):
        out[..., ch] = np.interp(e, levels, [s[1][ch] for s in STOPS])
    return out


def hillshade(e: np.ndarray, lat: np.ndarray, deg_per_px: float, exaggerate: float = 6.0) -> np.ndarray:
    dy_m = deg_per_px * 111_320
    dx_m = dy_m * np.cos(np.radians(lat))
    gy, gx = np.gradient(e * exaggerate)
    slope = np.arctan(np.hypot(gx / dx_m, gy / dy_m))
    aspect = np.arctan2(-gx / dx_m, gy / dy_m)
    az, alt = math.radians(315), math.radians(45)
    shade = np.sin(alt) * np.cos(slope) + np.cos(alt) * np.sin(slope) * np.cos(az - aspect)
    return np.clip(shade, 0, 1)


def main(tiles: Path, ne: Path) -> None:
    w, h = int(WIDTH * SCALE), int(HEIGHT * SCALE)
    lon = WEST + (np.arange(w) + 0.5) / w * (EAST - WEST)
    lat = NORTH - (np.arange(h) + 0.5) / h * (NORTH - SOUTH)
    lon2, lat2 = np.meshgrid(lon, lat)
    elev, x0, y0 = mosaic(tiles)
    e = sample(elev, x0, y0, lon2, lat2)
    land = land_mask(ne, w, h)
    shade = hillshade(np.where(land, e, 0), lat2, (NORTH - SOUTH) / h)
    rgb = tint(e) * (0.62 + 0.45 * shade[..., None])
    rgb = np.where(land[..., None], rgb, np.array(OCEAN, dtype=np.float32))
    img = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8))
    img.save(OUT, quality=62, optimize=True, progressive=True)
    print(f"wrote {OUT} ({OUT.stat().st_size:,} bytes, {w}x{h})")


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
