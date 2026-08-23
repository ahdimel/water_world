"""Cache behaviour. Network is stubbed — these tests never touch the wire."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from ww import cache
from ww.schemas import SourceSpec

SPEC = SourceSpec(id="test.source", title="Test", tier="api", url="https://example.test/x")
MANUAL = SourceSpec(id="test.manual", title="Manual", tier="manual")
KEYED = SourceSpec(
    id="test.keyed", title="Keyed", tier="api", url="https://example.test/k", requires_key=True
)


@pytest.fixture
def root(tmp_path):
    return tmp_path / "raw"


@pytest.fixture
def counter(monkeypatch):
    """Stub the downloader and count calls, so we can assert on re-fetch behaviour."""
    calls = {"n": 0, "last_post": None}

    def fake(url, timeout=60, post_json=None):
        calls["n"] += 1
        calls["last_post"] = post_json
        return f"payload-{calls['n']}".encode()

    monkeypatch.setattr(cache, "_download", fake)
    return calls


class TestFetch:
    def test_fetch_writes_blob_and_provenance(self, root, counter):
        path = cache.fetch(SPEC, root=root)
        assert path.read_bytes() == b"payload-1"
        rec = cache.read_record(SPEC, root)
        assert rec is not None
        assert rec.source_id == "test.source"
        assert rec.n_bytes == 9
        assert len(rec.sha256) == 64

    def test_second_fetch_uses_cache(self, root, counter):
        cache.fetch(SPEC, root=root)
        cache.fetch(SPEC, root=root)
        assert counter["n"] == 1

    def test_force_refetches(self, root, counter):
        cache.fetch(SPEC, root=root)
        cache.fetch(SPEC, root=root, force=True)
        assert counter["n"] == 2

    def test_stale_cache_refetches(self, root, counter, monkeypatch):
        cache.fetch(SPEC, root=root)
        rec = cache.read_record(SPEC, root)
        aged = rec.model_copy(
            update={"fetched_at": datetime.now(timezone.utc) - timedelta(days=10)}
        )
        _, meta = cache._paths(SPEC, root)
        meta.write_text(aged.model_dump_json())

        cache.fetch(SPEC, root=root, max_age_days=5)
        assert counter["n"] == 2

    def test_fresh_cache_within_max_age_is_kept(self, root, counter):
        cache.fetch(SPEC, root=root)
        cache.fetch(SPEC, root=root, max_age_days=5)
        assert counter["n"] == 1

    def test_post_body_is_forwarded(self, root, counter):
        spec = SPEC.model_copy(update={"id": "test.post", "post_json": {"a": 1}})
        cache.fetch(spec, root=root)
        assert counter["last_post"] == {"a": 1}

    def test_manual_source_refuses_with_a_pointer(self, root, counter):
        with pytest.raises(cache.FetchError, match="literature.yaml"):
            cache.fetch(MANUAL, root=root)
        assert counter["n"] == 0

    def test_keyed_source_refuses(self, root, counter):
        with pytest.raises(cache.FetchError, match="API key"):
            cache.fetch(KEYED, root=root)


class TestIntegrity:
    def test_blob_without_provenance_is_not_cached(self, root, counter):
        cache.fetch(SPEC, root=root)
        _, meta = cache._paths(SPEC, root)
        meta.unlink()
        # A blob we cannot date or hash is not evidence.
        assert not cache.is_cached(SPEC, root)

    def test_corrupt_provenance_is_not_cached(self, root, counter):
        cache.fetch(SPEC, root=root)
        _, meta = cache._paths(SPEC, root)
        meta.write_text("{ not json")
        assert not cache.is_cached(SPEC, root)

    def test_load_before_fetch_is_actionable(self, root):
        with pytest.raises(cache.FetchError, match="python -m ww fetch"):
            cache.load(SPEC, root)

    def test_sha256_matches_content(self, root, counter):
        import hashlib

        cache.fetch(SPEC, root=root)
        blob = cache.load(SPEC, root)
        assert cache.read_record(SPEC, root).sha256 == hashlib.sha256(blob).hexdigest()


class TestManifest:
    def test_empty_when_nothing_cached(self, root):
        assert cache.manifest(root) == []

    def test_lists_every_cached_source(self, root, counter):
        cache.fetch(SPEC, root=root)
        cache.fetch(SPEC.model_copy(update={"id": "test.other"}), root=root)
        assert {r.source_id for r in cache.manifest(root)} == {"test.source", "test.other"}

    def test_write_manifest_emits_json(self, root, counter, tmp_path):
        cache.fetch(SPEC, root=root)
        out = cache.write_manifest(tmp_path / "m.json", root=root)
        import json

        assert json.loads(out.read_text())[0]["source_id"] == "test.source"
