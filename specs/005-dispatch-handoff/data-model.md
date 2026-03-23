# Data Model: Dispatch Handoff

## Dispatch Handoff Package

- **Purpose**: represent the text bundle a coordinator copies or uses when sending a ready dispatch to the real subagent.
- **Fields**:
  - `dispatch_id`
  - `command_id`
  - `role`
  - `role_kind`
  - `priority`
  - `source`
  - `command_summary`
  - `project_root`
  - `role_definition_path` (optional)

## Queue Command Status

- **Purpose**: reflect how far an operator request has progressed.
- **Allowed states in this slice**:
  - `pending`
  - `claimed`
  - `dispatched`
  - `completed`
  - `failed`
  - `cancelled`

## Dispatch Status

- **Purpose**: reflect lifecycle of one delivery attempt.
- **Allowed states in this slice**:
  - `ready`
  - `dispatched`
  - `completed`
  - `failed`
  - `cancelled`
