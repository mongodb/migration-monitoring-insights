#!/usr/bin/env bash
# =============================================================================
# build_macos.sh — Build single-file Migration Insights executable for macOS
#
# Produces one self-contained Apple Silicon (arm64) binary (no Python install
# needed on the target Mac). PyInstaller bundles the interpreter and dependencies.
#
# Prerequisites (build machine: Apple Silicon macOS only):
#   - Python 3.11+ (arm64)
#
# Usage:
#   chmod +x build_macos.sh
#   ./build_macos.sh
#   ./build_macos.sh --arch arm64
#
# Output (example):
#   dist/migration-insights-0.9.3.9-macos-arm64
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

ARCH_CHOICE="arm64"
while [[ $# -gt 0 ]]; do
    case "$1" in
        --arch)
            ARCH_CHOICE="${2:?--arch requires arm64}"
            shift 2
            ;;
        -h | --help)
            sed -n '2,18p' "$0" | sed 's/^# \{0,1\}//'
            exit 0
            ;;
        *)
            echo "ERROR: unknown argument: $1 (try --help)" >&2
            exit 1
            ;;
    esac
done

if [[ "$(uname -s)" != "Darwin" ]]; then
    echo "ERROR: build_macos.sh must be run on macOS." >&2
    exit 1
fi

if [[ "$ARCH_CHOICE" != "arm64" && "$ARCH_CHOICE" != "native" ]]; then
    echo "ERROR: only Apple Silicon (arm64) builds are supported (got --arch ${ARCH_CHOICE})." >&2
    exit 1
fi

if [[ "$(uname -m)" != "arm64" ]]; then
    echo "ERROR: arm64 builds require an Apple Silicon Mac." >&2
    exit 1
fi

APP_VERSION=$(
    python3 -c "
import re, pathlib
m = re.search(
    r'APP_VERSION\s*=\s*\"([^\"]+)\"',
    pathlib.Path('lib/app_config.py').read_text(),
)
print(m.group(1))
"
)
echo "==> Building Migration Insights v${APP_VERSION} for macOS arm64"

actual_arch=$(python3 -c "import platform; print(platform.machine())")
if [[ "$actual_arch" != "arm64" ]]; then
    echo "ERROR: python3 must be an arm64 interpreter (found ${actual_arch})." >&2
    exit 1
fi

if ! python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)" 2>/dev/null; then
    ver=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null || echo "?")
    echo "ERROR: Python 3.11+ required (found ${ver})." >&2
    exit 1
fi

venv_dir="${SCRIPT_DIR}/.build_venv_macos_arm64"
rm -rf "$venv_dir"
python3 -m venv "$venv_dir"
# shellcheck disable=SC1091
source "${venv_dir}/bin/activate"

pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
pip install pyinstaller

rm -rf build dist/migration-insights
pyinstaller --clean --noconfirm migration_insights_onefile.spec

deactivate 2>/dev/null || true
rm -rf "$venv_dir"

if [[ ! -f "${SCRIPT_DIR}/dist/migration-insights" ]]; then
    echo "ERROR: PyInstaller did not produce dist/migration-insights" >&2
    exit 1
fi

dist_name="migration-insights-${APP_VERSION}-macos-arm64"
output_path="${SCRIPT_DIR}/dist/${dist_name}"
mv "${SCRIPT_DIR}/dist/migration-insights" "$output_path"
chmod 755 "$output_path"

# Clear quarantine bit if present (e.g. after copying from another machine)
xattr -cr "$output_path" 2>/dev/null || true

echo "==> Built: ${output_path}"
file "$output_path"
echo ""
echo "Run:"
echo "  ./dist/${dist_name}"
echo ""
echo "  MI_HOST=127.0.0.1 MI_PORT=3030 ./dist/${dist_name}"
