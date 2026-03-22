# `__codex_agents` Migration Notes

Korean version: [MIGRATION_FROM__CODEX_AGENTS.ko.md](./MIGRATION_FROM__CODEX_AGENTS.ko.md)

## Goal

Before removing the legacy `__codex_agents` folder, this document records which reusable assets were migrated into the new `codex-orchestrator` project.

## Migrated Assets

### 1. Design and operations documents

- `reference/legacy_shell_control_plane/docs/TEAM_MANIFEST.md`
- `reference/legacy_shell_control_plane/docs/TEAM_CONTROL_PLANE.md`
- `reference/legacy_shell_control_plane/docs/SUBAGENT_DASHBOARD.md`

### 2. Generic shell control-plane assets

- `reference/legacy_shell_control_plane/scripts/*.sh`

Scope:

- team manifest loading
- runtime state updates
- queue
- dispatch ledger
- bootstrap / recovery
- `tmux` / `cmux` dashboard launchers

## Not Migrated

- `__codex_agents/runtime/`
- event log
- queue archive
- dispatch archive
- live agent IDs and transient state files
- workspace-specific roles, prompts, and team examples

Those values are session-generated artifacts and were intentionally left out of the product assets. The last category was also excluded on purpose because the new project targets a reusable personal tool rather than a workspace-specific setup.

## New Structure

- runtime code: `src/codex_orchestrator/`
- product docs: `docs/`
- shell-based reference assets: `reference/legacy_shell_control_plane/`

## Interpretation Rules

- `reference/` means “previously validated implementation reference”
- `src/` means “current product source of truth”

Future feature work should therefore use `src/` and `docs/` as the primary sources, while `reference/` remains an implementation reference and scaffold-design input.
