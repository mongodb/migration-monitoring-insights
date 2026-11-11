"""Packaging constraints for the systemd install."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_install_tree_is_not_service_writable():
    unit = (ROOT / "migration-monitoring-insights.service").read_text()
    assert "ReadWritePaths=/var/log/migration-monitoring-insights\n" in unit
    assert "/opt/migration-monitoring-insights" not in unit.split("ReadWritePaths=", 1)[1].split("\n", 1)[0]
    log_env = "Environment=MI_LOG_FILE=/var/log/migration-monitoring-insights/insights.log"
    assert log_env in unit
    assert unit.index(log_env) < unit.index("EnvironmentFile=")

    script = (ROOT / "_build_linux_common.sh").read_text()
    assert "chown -R root:root /opt/migration-monitoring-insights" in script
    assert "chown -R migration-monitoring-insights:migration-monitoring-insights /opt/migration-monitoring-insights" not in script
    assert "MI_LOG_FILE=/var/log/${PACKAGE_NAME}/insights.log" in script
