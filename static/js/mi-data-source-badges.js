/**
 * Shared helpers for merging live/verifier toolbar data-source badges.
 */
(function (global) {
    'use strict';

    /**
     * Update only the badge for the current poll source.
     * Unevaluated badges from dual-source payloads must not overwrite the
     * other source's last known status.
     */
    function miMergeDataSourceBadges(dataSourcesById, payload, source) {
        if (!payload || !payload.dataSources || !payload.dataSources.badges) return;
        if (!source) return;
        payload.dataSources.badges.forEach(function (b) {
            if (b && b.id === source) {
                dataSourcesById[b.id] = b;
            }
        });
    }

    function miBuildMergedDataSources(dataSourcesById) {
        var badges = Object.keys(dataSourcesById).map(function (id) {
            return dataSourcesById[id];
        });
        if (badges.length === 0) return null;
        var hasProgress = dataSourcesById.progress != null;
        var hasMetadata = dataSourcesById.metadata != null;
        var mode = 'none';
        if (hasProgress && hasMetadata) mode = 'both';
        else if (hasProgress) mode = 'endpoint';
        else if (hasMetadata) mode = 'metadata';
        return { mode: mode, badges: badges };
    }

    global.miMergeDataSourceBadges = miMergeDataSourceBadges;
    global.miBuildMergedDataSources = miBuildMergedDataSources;
})(typeof window !== 'undefined' ? window : globalThis);
