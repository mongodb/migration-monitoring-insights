/**
 * Shared shell UI: settings, logout, credits overlays (base.html).
 */
(function (global) {
    'use strict';

    var REFRESH_MIN_SEC = 1;
    var REFRESH_MAX_SEC = 60;

    function parseRefreshSec(raw) {
        var text = raw == null ? '' : String(raw).trim();
        if (!/^\d+$/.test(text)) {
            return null;
        }
        var sec = Number(text);
        if (!Number.isInteger(sec) || sec < REFRESH_MIN_SEC || sec > REFRESH_MAX_SEC) {
            return null;
        }
        return sec;
    }

    function serverRefreshDefault(input) {
        return (
            (input && (input.getAttribute('data-default-refresh') || input.defaultValue)) ||
            '10'
        );
    }

    function openSettingsDialog() {
        var input = document.getElementById('settingsRefresh');
        var serverDefault = serverRefreshDefault(input);
        var stored = sessionStorage.getItem('mi_refresh_time');
        var sec = parseRefreshSec(stored);
        if (sec == null) {
            if (stored != null) {
                sessionStorage.removeItem('mi_refresh_time');
            }
            sec = parseRefreshSec(serverDefault);
            if (sec == null) {
                sec = 10;
            }
        }
        if (input) {
            input.value = String(sec);
        }
        if (typeof global.miOpenModal === 'function') {
            global.miOpenModal('settingsOverlay', document.getElementById('settingsBtn'));
        } else {
            document.getElementById('settingsOverlay').classList.add('active');
        }
    }

    function closeSettingsDialog() {
        if (typeof global.miCloseModal === 'function') {
            global.miCloseModal('settingsOverlay');
        } else {
            document.getElementById('settingsOverlay').classList.remove('active');
        }
    }

    function applySettings() {
        var input = document.getElementById('settingsRefresh');
        var sec = parseRefreshSec(input && input.value);
        if (sec == null) {
            alert(
                'Refresh must be an integer between ' +
                    REFRESH_MIN_SEC +
                    ' and ' +
                    REFRESH_MAX_SEC +
                    ' seconds.'
            );
            return;
        }
        sessionStorage.setItem('mi_refresh_time', String(sec));
        if (input) {
            input.value = String(sec);
        }
        closeSettingsDialog();
        global.dispatchEvent(new CustomEvent('mi-refresh-changed', {
            detail: { refreshSec: sec },
        }));
    }

    function confirmLogout() {
        if (typeof global.miOpenModal === 'function') {
            global.miOpenModal('logoutOverlay', document.getElementById('logoutBtn'));
        } else {
            document.getElementById('logoutOverlay').classList.add('active');
        }
    }

    function closeLogoutDialog() {
        if (typeof global.miCloseModal === 'function') {
            global.miCloseModal('logoutOverlay');
        } else {
            document.getElementById('logoutOverlay').classList.remove('active');
        }
    }

    function doLogout() {
        fetch('/logout', { method: 'POST', credentials: 'same-origin' })
            .then(function () { global.location.href = '/'; })
            .catch(function () { global.location.href = '/'; });
    }

    function openCreditsOverlay() {
        if (typeof global.miOpenModal === 'function') {
            global.miOpenModal('creditsOverlay', document.getElementById('creditsInfoBtn'));
        } else {
            document.getElementById('creditsOverlay').classList.add('active');
        }
    }

    function closeCreditsOverlay() {
        if (typeof global.miCloseModal === 'function') {
            global.miCloseModal('creditsOverlay');
        } else {
            document.getElementById('creditsOverlay').classList.remove('active');
        }
    }

    function registerShellModals() {
        if (typeof global.miRegisterModal !== 'function') return;
        global.miRegisterModal('settingsOverlay', closeSettingsDialog, { labelledBy: 'settingsDialogTitle' });
        global.miRegisterModal('logoutOverlay', closeLogoutDialog, { labelledBy: 'logoutDialogTitle' });
        global.miRegisterModal('creditsOverlay', closeCreditsOverlay, { labelledBy: 'creditsDialogTitle' });
    }

    global.miParseRefreshSec = parseRefreshSec;
    global.openSettingsDialog = openSettingsDialog;
    global.closeSettingsDialog = closeSettingsDialog;
    global.applySettings = applySettings;
    global.confirmLogout = confirmLogout;
    global.closeLogoutDialog = closeLogoutDialog;
    global.doLogout = doLogout;
    global.openCreditsOverlay = openCreditsOverlay;
    global.closeCreditsOverlay = closeCreditsOverlay;

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', registerShellModals);
    } else {
        registerShellModals();
    }
})(typeof window !== 'undefined' ? window : this);
