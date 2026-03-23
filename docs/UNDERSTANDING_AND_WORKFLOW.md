# Understanding And Workflow

Korean version: [UNDERSTANDING_AND_WORKFLOW.ko.md](./UNDERSTANDING_AND_WORKFLOW.ko.md)

## Current Product Understanding

- this project is primarily a Codex subagent installer and catalog manager
- its job is to make `.codex/agents/*.toml` setup easy and safe
- it can also act as a lightweight session companion around Codex usage
- it is not currently defined as a standalone orchestration runtime outside Codex

In short:

- `codex-orchestrator` prepares the workspace
- `codex` runs the session
- `codex` spawns and manages subagent threads

## Core Principles

- support both `Project` and `Global` install scopes
- keep agent definitions in `.codex/agents`
- use Codex-compatible TOML as the canonical format
- support built-in and user-injected catalog sources
- let users author their own category and agent templates
- keep experimental control-plane work clearly separated from the stable core

## Stable Commands Today

- `catalog`
- `install`
- `doctor`
- `template init`
- `tui`

These commands define the main product value.

## Experimental Commands Today

- `panel`
- `board`
- `launch`
- `enqueue`
- `dispatch-open`
- `dispatch-prepare`
- `dispatch-begin`
- `apply-result`

These commands are useful prototypes and companion utilities, but they are not the canonical product workflow.

## Main Workflow

```mermaid
flowchart LR
    A["1. Choose Scope<br/>Project or Global"]
    B["2. Browse Catalogs<br/>Built-in + external categories"]
    C["3. Select Agents"]
    D["4. Install TOML Files<br/>.codex/agents/*.toml"]
    E["5. Run Codex<br/>inside that workspace"]
    F["6. Ask Codex to use those agents"]

    A --> B --> C --> D --> E --> F
```

## Session Model

```mermaid
flowchart TD
    U["User"]
    CO["codex-orchestrator"]
    FS[".codex/agents/*.toml"]
    CX["Codex session"]
    SA["Subagent threads"]

    U -->|catalog / install / template| CO
    CO -->|writes definitions| FS
    U -->|runs codex| CX
    CX -->|loads project or global agents| FS
    CX -->|spawns and manages| SA
```

## Directory Model

```text
.codex/
└── agents/
    ├── cto-coordinator.toml
    ├── reviewer.toml
    ├── code-mapper.toml
    └── ...
```

Optional experimental companion assets may also exist under `.codex/orchestrator/`, but they are not required for the stable install flow.

## Next Priorities

1. improve compatibility validation for installed TOML files
2. improve catalog import and user-authored template workflows
3. document recommended Codex-side usage patterns after install
