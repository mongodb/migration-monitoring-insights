# Release Notes

User- and operator-facing changes, newest first. Download links for each release are in [ci/RELEASE_DOWNLOADS.md](ci/RELEASE_DOWNLOADS.md).

## Unreleased

- **pymongo upgraded from 4.19.0 to 4.20.2 and certifi from 2026.10.23 to 2026.11.20 ([MIGRATION-1203](https://jira.mongodb.org/browse/MIGRATION-1203)).** pymongo 4.20.1 fixes two security issues in connection string parsing: error messages are sanitized (CVE-2026-129927) and credential validation is stricter (CVE-2026-129926). pymongo 4.20.2 fixes two more: a read past the end of the buffer in the C BSON decoder (CVE-2026-135898) and stricter handling of stapled OCSP responses (CVE-2026-135146). certifi refreshes the CA bundle used for TLS connections to the destination cluster. MMI also no longer writes parser error text to the log when a connection string is malformed. It logs only the error type, so a password with an unescaped `@` or `:` cannot end up in `insights.log`. Every malformed connection string now shows the "Invalid Connection String" page. Before, some showed "Connection Failed" or "Connection Error". The .deb and .rpm packages and the macOS binary freeze both libraries at build time, so install this release to get them. No other action required.
