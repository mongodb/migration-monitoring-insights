#!/usr/bin/env bash
# =============================================================================
# build_amazonlinux.sh — RPM for Amazon Linux 2023
#
# Official CI publishes separate x86_64 and aarch64 RPMs built on AL2023.
# Amazon Linux 2 is not a supported release target.
#
# Prerequisites:
#   sudo dnf install -y python3.11 python3.11-pip ruby rubygems rpm-build gcc
#   sudo gem install fpm
#
# Usage:
#   ./build_amazonlinux.sh
#
# Output:
#   dist/migration-insights-<version>-1.amzn.<arch>.rpm
# =============================================================================
set -euo pipefail

LINUX_DISTRO=amazonlinux
PACKAGE_FORMAT=rpm

# shellcheck disable=SC1091
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/_build_linux_common.sh"
linux_build_main
