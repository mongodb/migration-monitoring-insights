"""Tests for destination index build cache."""
import time

import pytest

from lib.index_build_destination_cache import (
    DestinationScanEntry,
    _cache_key,
    _entries,
    clear_all,
    coll_uuid_key,
    resolve_extra_built_with_cache,
    scan_is_due,
)


@pytest.fixture(autouse=True)
def _clear_cache():
    clear_all()
    yield
    clear_all()


class TestCacheKey:
    def test_sha256_hex_differs_from_raw_uri(self):
        uri = "mongodb://user:secret@host/"
        key = _cache_key(uri)
        assert len(key) == 64
        assert all(c in "0123456789abcdef" for c in key)
        assert key != uri
        assert "secret" not in key
        assert key == _cache_key(uri)


class TestCollUuidKey:
    def test_bytes_hex(self):
        assert coll_uuid_key(b"\x01\x02") == "0102"

    def test_string_passthrough(self):
        assert coll_uuid_key("abc") == "abc"


class TestScanIsDue:
    def test_first_scan_always_due(self):
        entry = DestinationScanEntry()
        assert scan_is_due(entry, 60, frozenset({"a"}), time.monotonic()) is True

    def test_not_due_within_refresh_interval(self):
        now = time.monotonic()
        entry = DestinationScanEntry(last_scan_at=now, known_coll_uuids=frozenset({"a"}))
        assert scan_is_due(entry, 60, frozenset({"a"}), now + 10) is False

    def test_due_when_collection_set_changes(self):
        now = time.monotonic()
        entry = DestinationScanEntry(last_scan_at=now, known_coll_uuids=frozenset({"a"}))
        assert scan_is_due(entry, 60, frozenset({"b"}), now + 1) is True


class TestResolveExtraBuiltWithCache:
    def test_invokes_compute_on_miss(self):
        calls = []

        def compute():
            calls.append(1)
            return {"uuid1": 3}

        groups = [{"_id": "uuid1", "indexesPending": 2}]
        result = resolve_extra_built_with_cache(
            "mongodb://localhost",
            groups,
            refresh_sec=60,
            compute_extra_built=compute,
            now=100.0,
        )
        assert calls == [1]
        assert result == {"uuid1": 3}

    def test_cache_hit_skips_compute(self):
        def compute():
            return {"uuid1": 5}

        groups = [{"_id": "uuid1", "indexesPending": 1}]
        resolve_extra_built_with_cache(
            "mongodb://localhost", groups, 60, compute, now=100.0
        )
        calls = []

        def compute_again():
            calls.append(1)
            return {"uuid1": 9}

        result = resolve_extra_built_with_cache(
            "mongodb://localhost", groups, 60, compute_again, now=101.0
        )
        assert calls == []
        assert result == {"uuid1": 5}

    def test_empty_pending_groups_clears_cache(self):
        result = resolve_extra_built_with_cache(
            "mongodb://localhost",
            [{"_id": "uuid1", "indexesPending": 0}],
            60,
            lambda: {"uuid1": 1},
            now=100.0,
        )
        assert result == {}

    def test_entries_keyed_by_digest_not_raw_uri(self):
        uri = "mongodb://user:secret@host/"
        resolve_extra_built_with_cache(
            uri,
            [{"_id": "uuid1", "indexesPending": 1}],
            60,
            lambda: {"uuid1": 2},
            now=100.0,
        )
        assert uri not in _entries
        assert list(_entries.keys()) == [_cache_key(uri)]
