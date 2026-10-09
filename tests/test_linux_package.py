"""Packaging constraints for the systemd install."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_install_tree_is_not_service_writable():
    unit = (ROOT / "migration-insights.service").read_text()
    assert "ReadWritePaths=/var/log/migration-insights\n" in unit
    assert "/opt/migration-insights" not in unit.split("ReadWritePaths=", 1)[1].split("\n", 1)[0]
    log_env = "Environment=MI_LOG_FILE=/var/log/migration-insights/insights.log"
    assert log_env in unit
    assert unit.index(log_env) < unit.index("EnvironmentFile=")

    script = (ROOT / "_build_linux_common.sh").read_text()
    assert "chown -R root:root /opt/migration-insights" in script
    assert "chown -R migration-insights:migration-insights /opt/migration-insights" not in script
    assert "MI_LOG_FILE=/var/log/migration-insights/insights.log" in script
