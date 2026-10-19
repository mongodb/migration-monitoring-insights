"""Tests for Flask app factory."""
from unittest.mock import patch


class TestCreateApp:
    @patch("lib.app_config.validate_config", return_value=True)
    @patch("lib.app_config.setup_logging")
    def test_create_app_returns_flask_app(self, mock_log, _validate):
        mock_log.return_value = __import__("logging").getLogger("test")
        from migration_insights import create_app

        app = create_app()
        assert app is not None

    @patch("lib.app_config.validate_config", return_value=True)
    @patch("lib.app_config.setup_logging")
    def test_blueprints_registered(self, mock_log, _validate):
        mock_log.return_value = __import__("logging").getLogger("test")
        from migration_insights import create_app

        app = create_app()
        rules = {rule.rule for rule in app.url_map.iter_rules()}
        assert "/live/" in rules
        assert "/logs/" not in rules

    def test_home_is_monitoring_setup(self, app_client):
        r = app_client.get("/")
        assert r.status_code == 200
        assert b"Migration monitoring setup" in r.data
        assert b"Open log analyzer" not in r.data

    def test_settings_refresh_defaults_to_mi_refresh_time(self, app_client):
        from lib.app_config import REFRESH_TIME

        ctx = {
            "endpoint_url": "h:27182/api/v1/progress",
            "connection_string": None,
            "embedded_verifier": True,
            "verifier_endpoint_url": None,
            "verifier_connection_string": None,
            "mongosync_metadata_available": False,
            "verifier_metadata_available": False,
        }
        with patch("blueprints.live._live_session_context", return_value=ctx), patch(
            "blueprints.live._enforce_monitor_destination", return_value=None,
        ), patch("blueprints.live._live_nav_context", return_value=None):
            r = app_client.get("/live/migration")
        html = r.get_data(as_text=True)
        assert 'id="settingsRefresh"' in html
        assert f'data-default-refresh="{REFRESH_TIME}"' in html
        assert f'value="{REFRESH_TIME}"' in html

    def test_live_home_still_available(self, app_client):
        r = app_client.get("/live/")
        assert r.status_code == 200
        assert b"Migration monitoring setup" in r.data

    def test_health_route(self, app_client):
        r = app_client.get("/health")
        assert r.status_code == 200
        assert r.get_data(as_text=True) == "ok"

    def test_logout_clears_index_build_destination_cache(self, app_client):
        from lib import index_build_destination_cache as ib_cache

        ib_cache._entries["mongodb://user:secret@host/"] = ib_cache.DestinationScanEntry()
        r = app_client.post("/logout")
        assert r.status_code == 200
        assert ib_cache._entries == {}


class TestSecurityHeaders:
    def test_img_src_does_not_allow_arbitrary_remote_hosts(self, app_client):
        """Blanket https: in img-src would leave an exfiltration beacon open."""
        csp = app_client.get("/").headers["Content-Security-Policy"]
        img_src = next(
            part.strip()
            for part in csp.split(";")
            if part.strip().startswith("img-src")
        )
        assert img_src == "img-src 'self' data: blob:"

    def test_font_src_allows_mongodb_cdn_only(self, app_client):
        """Euclid fonts load from assets.mongodb-cdn.com; do not open font-src to all https."""
        csp = app_client.get("/").headers["Content-Security-Policy"]
        font_src = next(
            part.strip()
            for part in csp.split(";")
            if part.strip().startswith("font-src")
        )
        assert font_src == (
            "font-src 'self' data: https://assets.mongodb-cdn.com"
        )
        assert "https:" not in font_src.replace("https://assets.mongodb-cdn.com", "")

    def test_script_src_does_not_allow_plotly_cdn(self, app_client):
        csp = app_client.get("/").headers["Content-Security-Policy"]
        script_src = next(
            part.strip()
            for part in csp.split(";")
            if part.strip().startswith("script-src")
        )
        assert "cdn.plot.ly" not in script_src
