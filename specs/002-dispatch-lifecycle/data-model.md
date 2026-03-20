# Data Model: Dispatch Lifecycle

## QueueCommand

- **Purpose**: represent one operator-issued work request before dispatch.
- **Fields**:
  - `id`
  - `role`
  - `status`
  - `summary`
  - `source`
  - `priority`
  - `created_at`
  - optional `dispatch_id`
- **States**:
  - `pending`
  - `claimed`
  - `completed`
  - `failed`
  - `cancelled`

## DispatchTicket

- **Purpose**: represent one concrete assignment attempt derived from a queue command.
- **Fields**:
  - `id`
  - `command_id`
  - `role`
  - `status`
  - `created_at`
  - optional `result_summary`
- **States**:
  - `ready`
  - `dispatched`
  - `completed`
  - `failed`
  - `cancelled`

## RuntimeAgentState

- **Purpose**: represent the current operating status of the orchestrator and workers.
- **Fields**:
  - `key`
  - `status`
  - optional `active_dispatch_id`
- **States**:
  - `idle`
  - `busy`
  - future states may include `needs-rebind` or `offline`

## LifecycleMutationResult

- **Purpose**: describe the visible outcome of one CLI mutation.
- **Fields**:
  - `updated_path`
  - `entity_id`
  - `new_status`
  - optional `related_ids`
