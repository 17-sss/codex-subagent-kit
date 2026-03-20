# Research: Orchestrator Scaffold Generation

## Decision 1: Canonical built-in agent output should move to VoltAgent-style Codex-compatible TOML

- **Decision**: built-in generated agent files will use a canonical TOML shape aligned with VoltAgent-style Codex agent definitions, especially an `[instructions]` block with text content instead of the current top-level `developer_instructions`.
- **Rationale**: future external `.toml` intake is a product goal, so the built-in writer should not diverge from the format ecosystem we want to interoperate with.
- **Alternatives considered**:
  - Keep `developer_instructions` as-is: rejected because it makes future external `.toml` coexistence harder.
  - Add a second export mode: rejected for now because the project is small and a single canonical writer is clearer.

## Decision 2: Project-scope install should generate orchestrator scaffold; global install should not

- **Decision**: `.codex/orchestrator` scaffold is only generated for `project` scope.
- **Rationale**: runtime/control-plane state is project-local by nature, while global install is only for reusable static agent definitions.
- **Alternatives considered**:
  - Generate global scaffold in `~/.codex/orchestrator`: rejected because team runtime is not meaningfully global.
  - Make scaffold generation a separate mandatory command: rejected because the product flow is install-first and scaffold is part of that flow.

## Decision 3: Team seed must declare exactly one root orchestrator

- **Decision**: generated team metadata will include exactly one explicit root orchestrator and zero or more worker subagents.
- **Rationale**: without an explicit root orchestrator, the product collapses into a subagent file generator and loses its control-plane identity.
- **Alternatives considered**:
  - No explicit orchestrator in metadata: rejected because it weakens control-panel topology.
  - Allow multiple roots: rejected because the intended mental model is operator -> orchestrator -> workers.

## Decision 4: Current feature stops at seed topology, not full runtime control panel

- **Decision**: this feature only generates the scaffold and manifest seed needed for later control panel work.
- **Rationale**: full terminal panel, queue/dispatch runtime, and launcher integration are a larger slice and would blur the current boundary.
- **Alternatives considered**:
  - Implement control panel immediately: rejected for this feature slice because it expands scope too much.
