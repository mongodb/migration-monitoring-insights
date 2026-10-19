## Downloads

| Platform | Download |
|----------|----------|
| macOS Apple Silicon | `migration-insights-<version>-macos-arm64` |
| Ubuntu 20.04 / 22.04 / 24.04 amd64 | `migration-insights_<version>-1.ubuntu_amd64.deb` |
| Amazon Linux 2023 x86_64 | `migration-insights-<version>-1.amzn.x86_64.rpm` |
| Amazon Linux 2023 aarch64 | `migration-insights-<version>-1.amzn.aarch64.rpm` |
| RHEL 8 family x86_64 (Rocky, Alma, CentOS 8) | `migration-insights-<version>-1.el8.x86_64.rpm` |
| RHEL 9 family x86_64 (Rocky, Alma, RHEL 9) | `migration-insights-<version>-1.el9.x86_64.rpm` |

Release version: `<version>`.

The Ubuntu `.deb` is built on **20.04** and is intended for 20.04, 22.04, and 24.04. Use the RHEL RPM that matches your major version (`el8` / `el9`); an el9 RPM is not expected to run on el8.

### Quick start

* macOS: `chmod +x migration-insights-<version>-macos-arm64 && ./migration-insights-<version>-macos-arm64`
  * **First run:** If macOS blocks the app, right-click the file → **Open**, or run `xattr -cr ./migration-insights-<version>-macos-arm64` before launching. This is expected for unsigned binaries downloaded from GitHub.
* Ubuntu: `sudo apt install ./migration-insights_<version>-1.ubuntu_amd64.deb`
* Amazon Linux 2023 / RHEL 8+: `sudo dnf install ./migration-insights-<version>-1.*.rpm` (pick the matching arch / `el*` file)
* Source: use GitHub’s **Source code (zip)** or **Source code (tar.gz)** on the release page

Full installation, upgrade, and build-from-source instructions are in [PACKAGING.md](https://github.com/mongodb/migration-insights/blob/master/PACKAGING.md).
