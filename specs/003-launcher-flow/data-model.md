# Data Model: Launcher Flow

## RoleBoard

- **Purpose**: represent a read-only terminal view for one orchestrator or worker role.
- **Fields**:
  - `role_key`
  - `status`
  - optional `active_dispatch_id`
  - related `queue_commands`
  - related `dispatch_tickets`

## MonitorView

- **Purpose**: represent the team-wide summary view that aggregates topology and lifecycle counts.
- **Fields**:
  - `operator_label`
  - `orchestrator_key`
  - `worker_keys`
  - queue counts
  - dispatch counts

## LauncherSeed

- **Purpose**: represent one generated script under `.codex/subagent-kit/launchers/`.
- **Fields**:
  - `filename`
  - `backend`
  - `entry_command`
  - `preserve_on_rerun`

## BackendLaunchPlan

- **Purpose**: describe the pane/window composition for a dashboard backend.
- **Fields**:
  - `backend`
  - `orchestrator_role`
  - `worker_roles`
  - `monitor_entry`
