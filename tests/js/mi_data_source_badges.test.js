'use strict';

const { describe, it, before } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const SCRIPT_PATH = path.join(
    __dirname,
    '..',
    '..',
    'static',
    'js',
    'mi-data-source-badges.js',
);

function loadHelpers() {
    const sandbox = { globalThis: {} };
    sandbox.globalThis = sandbox;
    sandbox.window = sandbox;
    vm.runInNewContext(fs.readFileSync(SCRIPT_PATH, 'utf8'), sandbox);
    return sandbox;
}

function activeBadge(id) {
    return { id: id, label: id, status: 'active', color: 'green' };
}

function unavailableBadge(id) {
    return { id: id, label: id, status: 'unavailable', color: 'yellow' };
}

describe('mi-data-source-badges', () => {
    let merge;
    let buildMerged;

    before(() => {
        const helpers = loadHelpers();
        merge = helpers.miMergeDataSourceBadges;
        buildMerged = helpers.miBuildMergedDataSources;
    });

    it('progress poll updates only progress and leaves metadata intact', () => {
        const byId = {
            progress: activeBadge('progress'),
            metadata: activeBadge('metadata'),
        };
        const payload = {
            dataSources: {
                mode: 'both',
                badges: [activeBadge('progress'), unavailableBadge('metadata')],
            },
        };

        merge(byId, payload, 'progress');

        assert.equal(byId.progress.status, 'active');
        assert.equal(byId.metadata.status, 'active');
        assert.equal(byId.metadata.color, 'green');
    });

    it('metadata poll updates only metadata and leaves progress intact', () => {
        const byId = {
            progress: activeBadge('progress'),
            metadata: activeBadge('metadata'),
        };
        const payload = {
            dataSources: {
                mode: 'both',
                badges: [unavailableBadge('progress'), activeBadge('metadata')],
            },
        };

        merge(byId, payload, 'metadata');

        assert.equal(byId.progress.status, 'active');
        assert.equal(byId.metadata.status, 'active');
    });

    it('explicit unavailable on current source overwrites that badge', () => {
        const byId = {
            progress: activeBadge('progress'),
            metadata: activeBadge('metadata'),
        };
        const payload = {
            dataSources: {
                badges: [unavailableBadge('progress')],
            },
        };

        merge(byId, payload, 'progress');

        assert.equal(byId.progress.status, 'unavailable');
        assert.equal(byId.progress.color, 'yellow');
        assert.equal(byId.metadata.status, 'active');
    });

    it('buildMergedDataSources reports mode both when both badges present', () => {
        const merged = buildMerged({
            progress: activeBadge('progress'),
            metadata: activeBadge('metadata'),
        });
        assert.equal(merged.mode, 'both');
        assert.equal(merged.badges.length, 2);
    });

    it('buildMergedDataSources reports mode endpoint for progress only', () => {
        const merged = buildMerged({
            progress: activeBadge('progress'),
        });
        assert.equal(merged.mode, 'endpoint');
        assert.equal(merged.badges.length, 1);
    });

    it('buildMergedDataSources reports mode metadata for metadata only', () => {
        const merged = buildMerged({
            metadata: activeBadge('metadata'),
        });
        assert.equal(merged.mode, 'metadata');
        assert.equal(merged.badges.length, 1);
    });

    it('buildMergedDataSources returns null when empty', () => {
        assert.equal(buildMerged({}), null);
    });
});
