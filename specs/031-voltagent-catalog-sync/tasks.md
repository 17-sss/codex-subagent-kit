# Tasks: VoltAgent Catalog Sync

## Implementation

- [x] Replace custom built-in category assets with a vendored VoltAgent `categories/` snapshot.
- [x] Add project/global synced source-root discovery alongside existing user-authored catalog injection roots.
- [x] Implement `catalog sync` for Python and TypeScript with local `--source-root` support and VoltAgent upstream fetch defaults.
- [x] Switch the default root orchestrator preference to a VoltAgent-backed meta-orchestration agent (`multi-agent-coordinator`).

## Validation

- [x] Update Python and TypeScript tests, golden fixtures, and docs for the VoltAgent-backed default catalog.
- [x] Verify `catalog`, `install --validate`, `catalog import`, `template init`, and `catalog sync` flows in both runtimes.
