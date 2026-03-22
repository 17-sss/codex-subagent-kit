# legacy_shell_control_plane

Korean version: [README.ko.md](./README.ko.md)

This folder is a reference area that keeps only the shell-based control-plane assets from the old `__codex_agents` workspace that are still useful for `codex-orchestrator`.

## Purpose

- preserve seed assets that help implement control-panel features in the new Python project
- keep earlier shell implementations of queue, dispatch, recovery, and dashboard flows
- avoid losing validated design and behavior examples when removing `__codex_agents`

## Included Here

- `scripts/`
  - generic shell control-plane scripts driven by a team manifest
  - queue, dispatch ledger, runtime state, and dashboard launch flows
- `docs/`
  - `TEAM_MANIFEST.md`
  - `TEAM_CONTROL_PLANE.md`
  - `SUBAGENT_DASHBOARD.md`

## Not Included

- session-local runtime state
- event log
- pending/archive queue files
- current state snapshots for a specific workspace

Those values are intentionally excluded because they must not become the new project's source of truth.

## Usage Rules

- this folder is not the current product runtime entrypoint
- the actual runtime entrypoint lives in the Python code under `src/codex_orchestrator/`
- use this folder as reference material when implementing control panel, recovery, queue, and dispatch features

## Next Step

- re-express the shell concepts through Python code and template-based scaffold generation
- replace `.env` manifests with `.toml` manifests
- connect `tmux` / `cmux` launchers to the installer flow
