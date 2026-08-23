"""Fetch-once, provenance-stamped local cache.

Design rules:

* Nothing downstream ever hits the network. Analysis reads the cache, and the cache is
  rebuildable from the source registry alone.
* Every cached blob gets a sibling ``.meta.json`` holding a :class:`FetchRecord`.
  If the meta is missing the blob is treated as absent — a blob without provenance is
  not evidence.
* Re-fetching is explicit (``force=True``) or age-based (``max_age_days``). We never
  silently refresh, because a number in the paper must be traceable to a dated pull.
"""

from __future__ import annotations

import hashlib
import json
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

from ww import __version__
from ww.schemas import FetchRecord, SourceSpec

#: Repo-root-relative cache location. Gitignored.
CACHE_ROOT = Path(__file__).resolve().parent.parent / "data" / "raw"

USER_AGENT = f"water_world/{__version__} (research; contact via repo)"

DEFAULT_TIMEOUT = 60


class FetchError(RuntimeError):
    """Raised when a source cannot be retrieved."""


def _paths(spec: SourceSpec, root: Path | None = None) -> tuple[Path, Path]:
    """Return (blob_path, meta_path) for a source."""
    base = (root or CACHE_ROOT) / spec.id.replace(".", "/")
    return base.with_suffix(".data"), base.with_suffix(".meta.json")


def read_record(spec: SourceSpec, root: Path | None = None) -> FetchRecord | None:
    """Return the provenance record for a cached source, or None if not cached."""
    blob, meta = _paths(spec, root)
    if not (blob.exists() and meta.exists()):
        return None
    try:
        return FetchRecord.model_validate_json(meta.read_text())
    except Exception:
        # Corrupt provenance means the blob is not trustworthy.
        return None


def is_cached(spec: SourceSpec, root: Path | None = None) -> bool:
    return read_record(spec, root) is not None


def _download(
    url: str, timeout: int = DEFAULT_TIMEOUT, post_json: dict | None = None
) -> bytes:
    headers = {"User-Agent": USER_AGENT}
    data = None
    if post_json is not None:
        data = json.dumps(post_json).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read()
    except urllib.error.HTTPError as e:
        raise FetchError(f"HTTP {e.code} fetching {url}") from e
    except urllib.error.URLError as e:
        raise FetchError(f"network error fetching {url}: {e.reason}") from e


def fetch(
    spec: SourceSpec,
    *,
    force: bool = False,
    max_age_days: int | None = None,
    root: Path | None = None,
    timeout: int = DEFAULT_TIMEOUT,
) -> Path:
    """Ensure `spec` is present in the cache and return the path to its blob.

    Manual-tier sources are never fetched; they raise, because their values are
    curated into ``data/parameters/literature.yaml`` by hand instead.
    """
    if spec.tier == "manual":
        raise FetchError(
            f"{spec.id!r} is a manual source: it has no machine-fetchable form. "
            "Its value belongs in data/parameters/literature.yaml with a citation."
        )
    if spec.requires_key:
        raise FetchError(
            f"{spec.id!r} requires an API key. Key handling is not implemented in Phase 1."
        )

    blob, meta = _paths(spec, root)
    existing = read_record(spec, root)

    if existing and not force:
        stale = False
        if max_age_days is not None:
            age = datetime.now(timezone.utc) - existing.fetched_at
            stale = age > timedelta(days=max_age_days)
        if not stale:
            return blob

    assert spec.url is not None  # guaranteed by SourceSpec validation
    payload = _download(spec.url, timeout=timeout, post_json=spec.post_json)

    blob.parent.mkdir(parents=True, exist_ok=True)
    blob.write_bytes(payload)

    record = FetchRecord(
        source_id=spec.id,
        url=spec.url,
        fetched_at=datetime.now(timezone.utc),
        sha256=hashlib.sha256(payload).hexdigest(),
        n_bytes=len(payload),
        ww_version=__version__,
    )
    meta.write_text(record.model_dump_json(indent=2))
    return blob


def load(spec: SourceSpec, root: Path | None = None) -> bytes:
    """Read a cached blob. Raises if it was never fetched."""
    blob, _ = _paths(spec, root)
    if not is_cached(spec, root):
        raise FetchError(f"{spec.id!r} is not cached; run `python -m ww fetch {spec.id}` first")
    return blob.read_bytes()


def manifest(root: Path | None = None) -> list[FetchRecord]:
    """Every provenance record currently in the cache, newest first."""
    base = root or CACHE_ROOT
    if not base.exists():
        return []
    out: list[FetchRecord] = []
    for meta in base.rglob("*.meta.json"):
        try:
            out.append(FetchRecord.model_validate_json(meta.read_text()))
        except Exception:
            continue
    return sorted(out, key=lambda r: r.fetched_at, reverse=True)


def write_manifest(path: Path | None = None, root: Path | None = None) -> Path:
    """Dump the cache manifest to JSON so a run can be reproduced or audited."""
    target = path or ((root or CACHE_ROOT).parent / "manifest.json")
    records = manifest(root)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps([json.loads(r.model_dump_json()) for r in records], indent=2)
    )
    return target
