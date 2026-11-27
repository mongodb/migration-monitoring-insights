"""Tests for connection string sanitization."""
import logging
from unittest.mock import patch

import pytest
from pymongo.errors import InvalidURI, PyMongoError

from lib import app_config
from lib.connection_validator import sanitize_for_display

SECRET = "Fak3S3cretPw"
# Unescaped '@' and ':' put pieces of the password where the parser expects
# the host or port, which is where error text could echo it. Every URI here
# must fail while parsing, so the tests never touch the network.
LEAKY_PASSWORD = f"{SECRET}@{SECRET}:{SECRET}"
MALFORMED_URIS = [
    f"mongodb://alice:{SECRET}@host:notaport/",
    f"mongodb://alice:{LEAKY_PASSWORD}@host/",
    f"mongodb://alice:{LEAKY_PASSWORD}@host:27017/",
    f"mongodb://alice:{SECRET}@/",
    f"mongodb://alice:{SECRET}@host1,/",
    f"mongodb+srv://alice:{SECRET}@cluster0.example.net:27017/",
    f"mongodb+srv://alice:{LEAKY_PASSWORD}@cluster0.example.net/",
    f"notmongodb://alice:{SECRET}@host/",
]


class TestSanitizeForDisplay:
    def test_strips_credentials_and_shows_host(self):
        uri = "mongodb://user:secret@host1.example.com:27017,host2.example.com:27018/mydb"
        result = sanitize_for_display(uri)
        assert "user" not in result
        assert "secret" not in result
        assert "host1.example.com:27017" in result
        assert "host2.example.com:27018" in result
        assert "database: mydb" in result

    def test_uri_without_database(self):
        uri = "mongodb://user:pass@host.example.com:27017/"
        result = sanitize_for_display(uri)
        assert "pass" not in result
        assert "host.example.com:27017" in result
        assert "database:" not in result

    def test_escapes_html_in_host(self):
        uri = "mongodb://user:pass@host<script>:27017/db"
        result = sanitize_for_display(uri)
        assert "<script>" not in result
        assert "&lt;script&gt;" in result

    def test_malformed_uri_returns_fallback(self):
        assert sanitize_for_display("not a valid uri") == "[Connection String Provided]"

    def test_empty_string_returns_fallback(self):
        assert sanitize_for_display("") == "[Connection String Provided]"


class TestMalformedUriPasswordStaysOutOfLogs:
    @pytest.mark.parametrize("uri", MALFORMED_URIS)
    def test_sanitize_for_display(self, caplog, uri):
        with caplog.at_level(logging.ERROR):
            assert sanitize_for_display(uri) == "[Connection String Provided]"
        assert "Error sanitizing connection string" in caplog.text
        assert SECRET not in caplog.text

    @pytest.mark.parametrize("uri", MALFORMED_URIS)
    def test_create_mongo_client(self, caplog, uri):
        with caplog.at_level(logging.ERROR):
            with pytest.raises(InvalidURI) as exc_info:
                app_config._create_mongo_client(uri, timeout_ms=1000)
        assert "Invalid MongoDB connection string" in caplog.text
        assert SECRET not in caplog.text
        assert SECRET not in str(exc_info.value)
        assert exc_info.value.__cause__ is None

    @pytest.mark.parametrize("uri", MALFORMED_URIS)
    def test_live_connection_check(self, app_client, caplog, uri):
        from blueprints.live import _validate_connection_or_error

        app_config.clear_connection_cache()
        with app_client.application.test_request_context():
            with caplog.at_level(logging.ERROR):
                page = _validate_connection_or_error(uri)
        assert "Invalid Connection String" in page
        assert SECRET not in page
        assert SECRET not in caplog.text

    @pytest.mark.parametrize("error", [
        PyMongoError(f"auth failed for {SECRET}"),
        ValueError(f"bad value {SECRET}"),
    ], ids=["pymongo_error", "generic_error"])
    def test_live_connection_check_hides_driver_error_text(self, app_client, caplog, error):
        from blueprints.live import _validate_connection_or_error

        valid_uri = f"mongodb://alice:{SECRET}@host1.example.com:27017/"
        app_config.clear_connection_cache()
        with app_client.application.test_request_context():
            with patch("lib.app_config.MongoClient", side_effect=error):
                with caplog.at_level(logging.ERROR):
                    page = _validate_connection_or_error(valid_uri)
        # _create_mongo_client wraps any non-parse error in PyMongoError,
        # so both cases reach the "Connection Failed" page.
        assert "Connection Failed" in page
        assert SECRET not in page
        assert SECRET not in caplog.text
        assert type(error).__name__ in caplog.text

    def test_metadata_probe_logs_type_only(self, caplog):
        from blueprints.live import _probe_connection_flags

        error = PyMongoError(f"list_database_names failed for {SECRET}")
        with patch("blueprints.live.probe_metadata_databases", side_effect=error):
            with caplog.at_level(logging.WARNING):
                flags = _probe_connection_flags(f"mongodb://alice:{SECRET}@host1/")
        assert flags == {
            "mongosync_metadata_available": False,
            "verifier_metadata_available": False,
        }
        assert "PyMongoError" in caplog.text
        assert SECRET not in caplog.text
