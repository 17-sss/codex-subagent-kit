# Research: Dispatch Handoff

## Decision 1: Standardize the handoff boundary, not the live tool call

- **Decision**: this feature will stop at `dispatch-prepare` and `dispatch-begin`, leaving actual `send_input` / `wait_agent` execution outside the product CLI.
- **Rationale**: legacy control-plane docs explicitly separate file/runtime management from main Codex tool calls. That boundary still exists here.
- **Alternatives considered**:
  - Attempt full agent I/O automation now: rejected because the product runtime does not own Codex tool invocation yet.

## Decision 2: Reuse the existing queue/dispatch files instead of introducing a separate handoff store

- **Decision**: handoff rendering reads current queue, dispatch, runtime, and agent definition files directly.
- **Rationale**: the current product already has a single file-based source of truth. Adding a new handoff file layer would create drift.
- **Alternatives considered**:
  - Generate temporary handoff files: rejected because the output is ephemeral and better treated as CLI-rendered text.

## Decision 3: Promote `dispatched` to a first-class queue status

- **Decision**: queue summary and lifecycle will explicitly include `dispatched`, not just dispatch ledger.
- **Rationale**: once main Codex has actually sent the work, the queue should no longer look merely `claimed`.
- **Alternatives considered**:
  - Keep queue status at `claimed` forever and rely only on ledger state: rejected because the panel would hide an important lifecycle distinction.
