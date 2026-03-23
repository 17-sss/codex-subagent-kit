# Data Model: Launch CLI

## Launch Request

- **Purpose**: describe one CLI launch invocation before it becomes a subprocess command.
- **Fields**:
  - `project_root`: absolute project path
  - `backend`: `tmux` or `cmux`
  - `name_override`: optional session/workspace title override
  - `attach`: boolean for whether the runtime should attach immediately
  - `dry_run`: boolean for preview-only execution

## Launcher Target

- **Purpose**: represent the resolved project-local launcher script and argv.
- **Fields**:
  - `backend`: selected backend
  - `script_path`: absolute path to `launch-<backend>.sh`
  - `argv`: final subprocess argument vector

## Validation Rules

- `project_root/.codex/subagent-kit/launchers/launch-<backend>.sh` must exist before execution or dry-run succeeds.
- `attach = false` is valid only for `tmux`.
- `name_override` is optional for both backends.
