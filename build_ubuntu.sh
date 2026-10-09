#!/usr/bin/env bash
# =============================================================================
# build_ubuntu.sh — .deb for Ubuntu
#
# Official CI builds on Ubuntu 20.04 so one .deb covers 20.04 / 22.04 / 24.04
# (older glibc can run on newer hosts). Build on the same or older LTS as your
# oldest deployment target.
#
# Prerequisites:
#   sudo apt-get update
#   # On 20.04: use deadsnakes for Python 3.11
#   sudo apt-get install -y python3.11 python3.11-venv python3-pip ruby-rubygems build-essential
#   sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
#   sudo gem install fpm
#
# Usage:
#   ./build_ubuntu.sh
#
# Output:
#   dist/migration-insights_<version>-1.ubuntu_<arch>.deb
# =============================================================================
set -euo pipefail

LINUX_DISTRO=ubuntu
PACKAGE_FORMAT=deb

# shellcheck disable=SC1091
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/_build_linux_common.sh"
linux_build_main
