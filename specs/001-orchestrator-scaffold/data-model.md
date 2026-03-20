# Data Model: Orchestrator Scaffold Generation

## AgentDefinition

- **Purpose**: represent one installable subagent definition that can be rendered as canonical TOML.
- **Fields**:
  - `key`
  - `category`
  - `name`
  - `description`
  - `model`
  - `reasoning_effort`
  - `sandbox_mode`
  - `instructions_text`
- **Notes**: current internal model uses `developer_instructions`; implementation should normalize that into canonical output.

## TeamManifestSeed

- **Purpose**: define the initial control-plane topology for a project.
- **Fields**:
  - `orchestrator_key`
  - `worker_keys`
  - `version`
- **Constraints**:
  - exactly one root orchestrator
  - orchestrator key must also exist in the selected agent set
  - worker keys must not include the orchestrator key

## OrchestratorScaffold

- **Purpose**: represent the generated `.codex/orchestrator` directory seed.
- **Contents**:
  - `team.toml`
  - runtime directory placeholder
  - queue directory placeholder
  - ledger directory placeholder
  - launcher directory placeholder
  - README or guidance file

## InstallResult

- **Purpose**: describe what an install command created or preserved.
- **Fields**:
  - `agent_paths`
  - `scaffold_created_paths`
  - `scaffold_preserved_paths`
  - `scope`
- **Notes**: used for user-visible output and test assertions.
