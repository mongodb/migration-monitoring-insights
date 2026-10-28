"""Tests for data-source toolbar badge payloads."""
from lib.data_sources import STATUS_ACTIVE, STATUS_UNAVAILABLE, build_data_sources


class TestBuildDataSources:
    def test_none_when_nothing_configured(self):
        assert build_data_sources(
            progress_configured=False,
            metadata_configured=False,
            progress_status=None,
            metadata_status=None,
        ) is None

    def test_endpoint_only_active(self):
        result = build_data_sources(
            progress_configured=True,
            metadata_configured=False,
            progress_status=STATUS_ACTIVE,
            metadata_status=None,
        )
        assert result["mode"] == "endpoint"
        assert len(result["badges"]) == 1
        assert result["badges"][0] == {
            "id": "progress",
            "label": "Progress API",
            "status": STATUS_ACTIVE,
            "color": "green",
        }

    def test_metadata_only_unavailable(self):
        result = build_data_sources(
            progress_configured=False,
            metadata_configured=True,
            progress_status=None,
            metadata_status=STATUS_UNAVAILABLE,
        )
        assert result["mode"] == "metadata"
        assert len(result["badges"]) == 1
        assert result["badges"][0]["id"] == "metadata"
        assert result["badges"][0]["color"] == "yellow"

    def test_both_sources(self):
        result = build_data_sources(
            progress_configured=True,
            metadata_configured=True,
            progress_status=STATUS_ACTIVE,
            metadata_status=STATUS_UNAVAILABLE,
        )
        assert result["mode"] == "both"
        assert len(result["badges"]) == 2
        assert result["badges"][0]["id"] == "progress"
        assert result["badges"][1]["id"] == "metadata"

    def test_custom_labels(self):
        result = build_data_sources(
            progress_configured=True,
            metadata_configured=True,
            progress_status=STATUS_ACTIVE,
            metadata_status=STATUS_ACTIVE,
            progress_label="Progress API",
            metadata_label="Verifier metadata",
        )
        assert result["badges"][1]["label"] == "Verifier metadata"

    def test_none_status_omits_unevaluated_badges(self):
        result = build_data_sources(
            progress_configured=True,
            metadata_configured=True,
            progress_status=None,
            metadata_status=None,
        )
        assert result is None

    def test_progress_slice_omits_unevaluated_metadata(self):
        result = build_data_sources(
            progress_configured=True,
            metadata_configured=True,
            progress_status=STATUS_ACTIVE,
            metadata_status=None,
        )
        assert result["mode"] == "both"
        assert len(result["badges"]) == 1
        assert result["badges"][0]["id"] == "progress"
        assert result["badges"][0]["status"] == STATUS_ACTIVE

    def test_metadata_slice_omits_unevaluated_progress(self):
        result = build_data_sources(
            progress_configured=True,
            metadata_configured=True,
            progress_status=None,
            metadata_status=STATUS_ACTIVE,
        )
        assert result["mode"] == "both"
        assert len(result["badges"]) == 1
        assert result["badges"][0]["id"] == "metadata"
        assert result["badges"][0]["status"] == STATUS_ACTIVE

    def test_explicit_unavailable_still_emitted(self):
        result = build_data_sources(
            progress_configured=True,
            metadata_configured=True,
            progress_status=STATUS_UNAVAILABLE,
            metadata_status=STATUS_ACTIVE,
        )
        assert len(result["badges"]) == 2
        assert result["badges"][0]["status"] == STATUS_UNAVAILABLE
        assert result["badges"][0]["color"] == "yellow"
        assert result["badges"][1]["status"] == STATUS_ACTIVE
