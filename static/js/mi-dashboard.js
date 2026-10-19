/**
 * Combined live monitoring dashboard (progress-only sections).
 */
(function (global) {
    'use strict';

    function fetchJson(url) {
        return fetch(url, {
            method: 'POST',
            credentials: 'same-origin',
        }).then(function (response) {
            return response.json().then(function (payload) {
                return { response: response, payload: payload };
            });
        });
    }

    function startPolling(refreshFn, refreshMs, baseRefreshSec, onIntervalSecChanged) {
        var inflight = false;
        var intervalId = null;
        var currentMs = refreshMs;
        var ratio = baseRefreshSec > 0 ? (refreshMs / 1000) / baseRefreshSec : 1;

        function refresh() {
            if (inflight) {
                return;
            }
            inflight = true;
            refreshFn()
                .catch(function (err) {
                    console.error(err);
                })
                .finally(function () {
                    inflight = false;
                });
        }

        function arm(ms) {
            if (intervalId) {
                clearInterval(intervalId);
                intervalId = null;
            }
            currentMs = ms;
            intervalId = setInterval(refresh, ms);
        }

        function onRefreshChanged(e) {
            var sec = e.detail && e.detail.refreshSec;
            if (!(sec > 0)) {
                return;
            }
            var newMs = sec * ratio * 1000;
            if (newMs === currentMs) {
                return;
            }
            arm(newMs);
            if (typeof onIntervalSecChanged === 'function') {
                onIntervalSecChanged(newMs / 1000);
            }
        }

        function teardown(event) {
            if (event && event.persisted) {
                return;
            }
            if (intervalId) {
                clearInterval(intervalId);
                intervalId = null;
            }
            window.removeEventListener('mi-refresh-changed', onRefreshChanged);
            window.removeEventListener('pagehide', teardown);
        }

        refresh();
        arm(refreshMs);
        window.addEventListener('mi-refresh-changed', onRefreshChanged);
        window.addEventListener('pagehide', teardown);
        return { refresh: refresh, teardown: teardown };
    }

    function initMigrationSection(config, baseRefreshSec, onIntervalSecChanged) {
        var loading = document.getElementById(config.loadingId);
        var root = document.getElementById(config.rootId);
        if (!loading || !root) return;

        var renderOptions = { syncOnly: true };
        if (config.fullViewLink) {
            renderOptions.fullViewLink = config.fullViewLink;
        }

        startPolling(function () {
            return fetchJson(config.pollUrl).then(function (result) {
                if (!result.response.ok) {
                    var msg = (result.payload && result.payload.error) || 'Request failed';
                    throw new Error(msg);
                }
                var payload = result.payload;
                loading.style.display = 'none';
                root.style.display = 'block';
                if (typeof global.miRenderProgressMonitor === 'function') {
                    global.miRenderProgressMonitor(root, payload, renderOptions);
                }
            }).catch(function (err) {
                console.error('Error fetching migration dashboard data:', err);
                loading.style.display = 'none';
                root.style.display = 'block';
                if (typeof global.miRenderProgressMonitor === 'function') {
                    global.miRenderProgressMonitor(root, {
                        warnings: [],
                        display: null,
                        error: 'Error loading data: ' + err.message,
                    }, renderOptions);
                }
            });
        }, config.refreshMs, baseRefreshSec, onIntervalSecChanged);
    }

    function initVerifierSection(config, baseRefreshSec, onIntervalSecChanged) {
        var loading = document.getElementById(config.loadingId);
        var root = document.getElementById(config.rootId);
        if (!loading || !root) return;

        var slots = null;
        if (typeof global.miInitVerifierMonitorShell === 'function') {
            slots = global.miInitVerifierMonitorShell(root);
        }

        var toolbarOptions = config.fullViewLink ? { fullViewLink: config.fullViewLink } : null;

        startPolling(function () {
            return fetchJson(config.pollUrl).then(function (result) {
                if (!result.response.ok) {
                    var msg = (result.payload && result.payload.error) || 'Request failed';
                    throw new Error(msg);
                }
                var payload = result.payload;
                loading.style.display = 'none';
                root.style.display = 'block';

                if (!slots) return;

                var display = payload.display || {};
                var progress = display.verificationProgress || null;
                if (typeof global.miUpdateVerifierToolbar === 'function') {
                    global.miUpdateVerifierToolbar(
                        slots,
                        progress,
                        null,
                        null,
                        display.stateBadge,
                        payload.dataSources,
                        toolbarOptions
                    );
                }
                if (typeof global.miUpdateVerifierProgressSection === 'function') {
                    global.miUpdateVerifierProgressSection(slots, progress);
                }
                if (typeof global.miUpdateVerifierWarnings === 'function') {
                    global.miUpdateVerifierWarnings(slots, payload.warnings);
                }
            }).catch(function (err) {
                console.error('Error fetching verifier dashboard data:', err);
                loading.style.display = 'none';
                root.style.display = 'block';
                if (slots && typeof global.miUpdateVerifierWarnings === 'function') {
                    global.miUpdateVerifierWarnings(
                        slots,
                        ['Error loading verifier data: ' + err.message]
                    );
                }
            });
        }, config.refreshMs, baseRefreshSec, onIntervalSecChanged);
    }

    function storedBaseRefreshSec(fallback) {
        if (typeof global.miParseRefreshSec !== 'function') {
            return fallback;
        }
        var stored = global.miParseRefreshSec(sessionStorage.getItem('mi_refresh_time'));
        return stored == null ? fallback : stored;
    }

    function miInitDashboard(config) {
        var serverBase = config.baseRefreshSec || 10;
        var baseRefreshSec = storedBaseRefreshSec(serverBase);
        var scale = serverBase > 0 ? baseRefreshSec / serverBase : 1;
        if (config.migration && config.migration.refreshMs) {
            config.migration.refreshMs = Math.round(config.migration.refreshMs * scale);
        }
        if (config.verifier && config.verifier.refreshMs) {
            config.verifier.refreshMs = Math.round(config.verifier.refreshMs * scale);
        }
        var migrationSec = config.migration
            ? (config.migration.refreshMs / 1000)
            : null;
        var verifierSec = config.verifier
            ? (config.verifier.refreshMs / 1000)
            : null;

        function updateFooter() {
            var parts = [];
            if (migrationSec != null) {
                parts.push('Migration refresh: ' + migrationSec + 's');
            }
            if (verifierSec != null) {
                parts.push('Verifier refresh: ' + verifierSec + 's');
            }
            var footerP = document.querySelector('footer p');
            if (footerP && parts.length) {
                footerP.textContent = parts.join(' · ');
            }
        }

        if (config.migration) {
            initMigrationSection(config.migration, baseRefreshSec, function (sec) {
                migrationSec = sec;
                updateFooter();
            });
        }
        if (config.verifier) {
            initVerifierSection(config.verifier, baseRefreshSec, function (sec) {
                verifierSec = sec;
                updateFooter();
            });
        }
    }

    global.miInitDashboard = miInitDashboard;
})(typeof window !== 'undefined' ? window : this);
