"""Readable labels for mongosync ``commitBlockers`` (MIGRATION-1201).

mongosync 1.23 lists every reason ``canCommit`` is false in the ``/progress``
body, but only while the state is RUNNING, ``canCommit`` is false and the
info is change event application. Older versions never send the field.
"""
from __future__ import annotations

from typing import Any

COMMIT_BLOCKER_LABELS = {
    "mongosync_lag_too_high": "Mongosync lag above 30 s",
    "verifier_source_not_in_stream_hashing": "Verifier: source not yet in stream hashing",
    "verifier_source_lag_too_high": "Verifier: source lag above 30 s",
    "verifier_destination_not_in_stream_hashing": "Verifier: destination not yet in stream hashing",
    "verifier_destination_lag_too_high": "Verifier: destination lag above 30 s",
    "building_indexes": "Indexes still building",
}


def commit_blocker_items(progress: Any) -> list[dict[str, str]]:
    """Return ``[{"raw": ..., "label": ...}]`` for a /progress body, in reported order.

    Empty when ``canCommit`` is true, or when the field is missing or malformed.
    An unknown raw value keeps its raw string as the label, so a blocker added
    in a later mongosync still shows.
    """
    if not isinstance(progress, dict) or progress.get("canCommit"):
        return []
    raw_values = progress.get("commitBlockers")
    if not isinstance(raw_values, list):
        return []
    items: list[dict[str, str]] = []
    for value in raw_values:
        if not isinstance(value, str) or not value.strip():
            continue
        raw = value.strip()
        items.append({"raw": raw, "label": COMMIT_BLOCKER_LABELS.get(raw, raw)})
    return items
