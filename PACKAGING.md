# Packaging Migration Insights

Self-contained builds bundle Python and dependencies so target machines do not need `pip install`. Package name remains **`migration-insights`**.

## Official GitHub Release matrix

| Platform | Script / CI | Output |
|---|---|---|
| **macOS Apple Silicon** | `build_macos.sh --arch arm64` | `dist/migration-insights-<version>-macos-arm64` |
| **Amazon Linux 2023 x86_64** | `build_amazonlinux.sh` | `dist/migration-insights-<version>-1.amzn.x86_64.rpm` |
| **Amazon Linux 2023 aarch64** | `build_amazonlinux.sh` (on arm64 host) | `dist/migration-insights-<version>-1.amzn.aarch64.rpm` |
| **Ubuntu 20.04 / 22.04 / 24.04 amd64** | `build_ubuntu.sh` (CI: `ubuntu:20.04` container) | `dist/migration-insights_<version>-1.ubuntu_amd64.deb` |
| **RHEL 8 family x86_64** | `build_rhel.sh --el-major 8` | `dist/migration-insights-<version>-1.el8.x86_64.rpm` |
| **RHEL 9 family x86_64** | `build_rhel.sh --el-major 9` | `dist/migration-insights-<version>-1.el9.x86_64.rpm` |

Shared implementation: Linux scripts source `_build_linux_common.sh`. macOS uses `migration_insights_onefile.spec`; Linux packages use `migration_insights.spec` (directory bundle under `/opt/migration-insights`).

> **Cross-compile:** PyInstaller targets the OS and CPU it runs on. You cannot build macOS binaries from Linux, or Linux packages from macOS. Use a VM, native host, or CI for each platform/arch.

For not official release targets, run from source on those platforms if needed.

---

## GitHub Releases (CI)

Official release builds are published automatically when a **version tag** is pushed. Pull requests run tests only; they do **not** create releases or upload artifacts.

### Published assets (6 files per release)

| Platform | File |
|----------|------|
| macOS Apple Silicon | `migration-insights-<version>-macos-arm64` |
| Ubuntu 20.04 / 22.04 / 24.04 amd64 | `migration-insights_<version>-1.ubuntu_amd64.deb` |
| Amazon Linux 2023 x86_64 | `migration-insights-<version>-1.amzn.x86_64.rpm` |
| Amazon Linux 2023 aarch64 | `migration-insights-<version>-1.amzn.aarch64.rpm` |
| RHEL 8 family x86_64 | `migration-insights-<version>-1.el8.x86_64.rpm` |
| RHEL 9 family x86_64 | `migration-insights-<version>-1.el9.x86_64.rpm` |

**Linux packages** install under `/opt/migration-insights` with systemd support (see below). Packages declare **no** OS `Depends`/`Requires`; the PyInstaller bundle includes Python and application dependencies.

- Ubuntu: one `.deb` built on **20.04** covers 20.04, 22.04, and 24.04.
- RHEL: use **el8** / **el9** matching your major. An el9 build is not expected to run on el8.
- Amazon Linux: **2023 only**; pick `x86_64` or `aarch64`.

Source code is available from GitHub’s automatic **Source code (zip)** and **Source code (tar.gz)** links on each release.

---

## macOS (single-file executable)

Official releases ship **Apple Silicon (arm64)** only. Use `build_macos.sh` on a Mac:

```bash
./build_macos.sh --arch arm64
chmod +x dist/migration-insights-*-macos-arm64
./dist/migration-insights-*-macos-arm64
```

### Prerequisites

| Requirement | Notes |
|---|---|
| macOS build host | Script refuses to run on Linux/Windows |
| Python 3.11+ (arm64) | System or Homebrew `python3` on Apple Silicon |

Environment variables: `MI_HOST`, `MI_PORT`, `MI_CONNECTION_STRING`, `MI_PROGRESS_ENDPOINT_URL`, etc. See [CONFIGURATION.md](CONFIGURATION.md) and [MIGRATION_MONITORING.md](MIGRATION_MONITORING.md).

If macOS blocks the binary (“damaged” / unidentified developer):

```bash
xattr -cr dist/migration-insights-*-macos-arm64
```

---

## Linux packages (RPM / DEB)

Packages install under `/opt/migration-insights` with systemd and `/etc/migration-insights/env`. The target needs **no pip install**.

> **Important:** Build on **Linux**, on the **same or older** OS/glibc as your deployment. A binary built on RHEL 9 or Ubuntu 24.04 may not run on older releases. When in doubt, build on the oldest target you support.

### Prerequisites (all Linux scripts)

| Tool | RPM distros | Ubuntu |
|---|---|---|
| Python 3.11+ | `python3.11`, `python3.11-pip` (el8/el9/AL2023) | `python3.11` (deadsnakes on 20.04), `python3.11-venv`; point `python3` at 3.11 via `update-alternatives` |
| fpm | `sudo gem install fpm` | `sudo gem install fpm` |
| Ruby | `ruby`, `rubygems` | `ruby-rubygems` |
| rpmbuild | `rpm-build` (RPM only) | not required for `.deb` |
| Compiler | `gcc` / `build-essential` | `build-essential` |

### Amazon Linux 2023

```bash
sudo dnf install -y python3.11 python3.11-pip ruby rubygems rpm-build gcc
sudo gem install fpm
./build_amazonlinux.sh
```

Build on an aarch64 AL2023 host (or the CI arm64 job) for `…amzn.aarch64.rpm`.

### Red Hat / CentOS (RHEL family)

```bash
# el8 / el9
sudo dnf install -y python3.11 python3.11-pip ruby rubygems rpm-build gcc
sudo gem install fpm
./build_rhel.sh --el-major 8   # or 9
```

### Ubuntu

Build on **20.04** if you want one `.deb` that also runs on 22.04 and 24.04:

```bash
sudo apt-get update
# 20.04: sudo add-apt-repository -y ppa:deadsnakes/ppa && sudo apt-get update
sudo apt-get install -y python3.11 python3.11-venv python3-pip ruby-rubygems build-essential
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
sudo gem install fpm
./build_ubuntu.sh
```

### What the Linux scripts do

1. Read the app version from `lib/app_config.py`
2. Create a temporary virtual environment and install dependencies
3. Run PyInstaller (`migration_insights.spec`)
4. Stage files under `/opt/migration-insights`, systemd unit, and config
5. Build RPM or DEB with **fpm**
6. Clean up the venv and staging directory

### Installing on target

**RPM (Amazon Linux 2023, RHEL, CentOS):**

```bash
# Pick the matching file (el8 / el9 / amzn + arch)
sudo dnf install ./migration-insights-<version>-1.el8.x86_64.rpm
```

**DEB (Ubuntu):**

```bash
sudo apt install ./migration-insights_*-1.ubuntu_amd64.deb
```

No internet is required on the target beyond installing the package.

**Installed files:**

| Path | Description |
|---|---|
| `/opt/migration-insights/` | Application (binary + bundled Python + deps) |
| `/usr/local/bin/migration-insights` | Wrapper on `$PATH` |
| `/usr/lib/systemd/system/migration-insights.service` | Systemd unit |
| `/etc/migration-insights/env` | Configuration (preserved on upgrade) |

### Configuration (Linux packages)

Edit `/etc/migration-insights/env`:

```bash
MI_HOST=0.0.0.0
MI_PORT=8080

# Mongosync monitoring
MI_PROGRESS_ENDPOINT_URL=localhost:27182
# Optional: metadata fallback — destination cluster connection string
MI_CONNECTION_STRING=mongodb+srv://user:pass@cluster.mongodb.net/

# Migration Verifier
MI_VERIFIER_PROGRESS_ENDPOINT_URL=localhost:27020
# Optional: metadata fallback on a different cluster (falls back to MI_CONNECTION_STRING when omitted)
MI_VERIFIER_CONNECTION_STRING=mongodb+srv://user:pass@verifier-cluster.mongodb.net/
MI_MIGRATION_VERIFIER_DB_NAME=__mdb_internal_migration_verifier

MI_REFRESH_TIME=5
MI_INDEX_BUILD_REFRESH_TIME=60
MI_MONGOSYNC_PROGRESS_TIMEOUT_SECS=10
MI_VERIFIER_PROGRESS_TIMEOUT_SECS=30
MI_VERIFIER_HEAVY_API_TIMEOUT_SECS=600
MI_VERIFIER_METADATA_TIMEOUT_MS=120000
MI_SSL_ENABLED=true
MI_SSL_CERT=/etc/migration-insights/cert.pem
MI_SSL_KEY=/etc/migration-insights/key.pem
LOG_LEVEL=DEBUG
```

See [CONFIGURATION.md](CONFIGURATION.md) for the full reference.

### Running (Linux packages)

The systemd unit runs as the `migration-insights` system user created on install. `/etc/migration-insights/env` stays owned by root and is group-readable by that user (`640`). Keep that mode when editing the file so the service can still read it.

On install, certificate and key files named by `MI_SSL_CERT` and `MI_SSL_KEY` are also made group-readable when they already exist under `/etc/migration-insights/`. Paths outside that directory, including Let's Encrypt, are left unchanged. Grant the `migration-insights` group read access to those files yourself.

`/opt/migration-insights` stays owned by root and is not writable by the service. File logs go to `/var/log/migration-insights/insights.log`, which the package creates for the service user. The unit sets that path; a `MI_LOG_FILE` line in the env file overrides it. `ProtectSystem=strict` blocks writes anywhere else, including a custom `MI_LOG_FILE` outside `/var/log/migration-insights`.

```bash
sudo systemctl start migration-insights
sudo systemctl enable migration-insights
sudo systemctl status migration-insights
journalctl -u migration-insights -f
```

Manual run:

```bash
MI_HOST=0.0.0.0 MI_PORT=8080 /opt/migration-insights/migration-insights
```

### Uninstalling

**RPM:**

```bash
sudo rpm -e migration-insights
```

**DEB:**

```bash
sudo apt remove migration-insights
```

### Upgrading

**RPM:**

```bash
sudo rpm -U migration-insights-<new-version>-1.el8.x86_64.rpm
```

**DEB:**

```bash
sudo apt install ./migration-insights_<new-version>-1.ubuntu_amd64.deb
```

---

## Architecture notes

- Packages are **CPU-specific** (`x86_64`, `aarch64`/`arm64`). Build on the same architecture as the target.
- Linux binaries are **glibc-specific**. Build on the same or older distro major version as production.
- One Ubuntu **20.04** build covers newer Ubuntu LTS hosts; RHEL majors are published separately.
- macOS one-file builds extract to a temp directory at runtime; Linux packages use `/opt/migration-insights`.
- Bundled `certifi` CA certificates are frozen at build time; rebuild to update them.

## Troubleshooting

### Fast "GLIBC_x.xx not found" (Linux)

The package was built on a newer OS than the target. Rebuild on the same or older release (or install the matching `el8`/`el9` / Ubuntu artifact).

### Service fails to start (Linux)

```bash
journalctl -u migration-insights --no-pager -n 50
```

Common causes: port in use (`MI_PORT`), missing SSL cert paths in `/etc/migration-insights/env`.

### macOS "damaged" or won't open

```bash
xattr -cr dist/migration-insights-*-macos-arm64
```

### License

[Apache 2.0](http://www.apache.org/licenses/LICENSE-2.0)

DISCLAIMER
----------
Please note: all tools/ scripts in this repo are released for use "AS IS" **without any warranties of any kind**,
including, but not limited to their installation, use, or performance.  We disclaim any and all warranties, either 
express or implied, including but not limited to any warranty of noninfringement, merchantability, and/ or fitness 
for a particular purpose.  We do not warrant that the technology will meet your requirements, that the operation 
thereof will be uninterrupted or error-free, or that any errors will be corrected.

Any use of these scripts and tools is **at your own risk**.  There is no guarantee that they have been through 
thorough testing in a comparable environment and we are not responsible for any damage or data loss incurred with 
their use.

You are responsible for reviewing and testing any scripts you run *thoroughly* before use in any non-testing 
environment.

Thanks,  
The MongoDB Support Team
