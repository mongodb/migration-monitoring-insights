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
#   sudo apt-get install -y \
#     ca-certificates curl build-essential \
#     libssl-dev zlib1g-dev libffi-dev libsqlite3-dev \
#     libreadline-dev libbz2-dev liblzma-dev libncurses-dev xz-utils \
#     ruby-rubygems
#   # On 20.04 (Focal EOL): build Python 3.11 from source (deadsnakes no longer ships packages)
#   PYTHON_VERSION=3.11.17
#   curl -fsSL "https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz" \
#     | tar -xz -C /tmp
#   (
#     cd "/tmp/Python-${PYTHON_VERSION}"
#     ./configure --prefix=/usr/local --enable-shared --with-ensurepip=install
#     make -j"$(nproc)" && sudo make altinstall
#   )
#   echo /usr/local/lib | sudo tee /etc/ld.so.conf.d/python3.11-local.conf
#   sudo ldconfig
#   sudo update-alternatives --install /usr/bin/python3 python3 /usr/local/bin/python3.11 1
#   sudo gem install fpm
#
# Usage:
#   ./build_ubuntu.sh
#
# Output:
#   dist/migration-monitoring-insights_<version>-1.ubuntu_<arch>.deb
# =============================================================================
set -euo pipefail

LINUX_DISTRO=ubuntu
PACKAGE_FORMAT=deb

# shellcheck disable=SC1091
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/_build_linux_common.sh"
linux_build_main
