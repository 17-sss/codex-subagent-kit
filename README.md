# codex-orchestrator

Korean version: [README.ko.md](./README.ko.md)

`codex-orchestrator` is a project-local tool for installing Codex subagents under `.codex`, with an architecture that can grow into a control-plane and terminal dashboard.

Current MVP scope:

- choose a `Project` or `Global` install location
- browse a category-based subagent catalog
- generate multiple `.codex/agents/*.toml` files
- generate a project-scope `.codex/orchestrator` scaffold and `team.toml`
- generate runtime, queue, and dispatch ledger seeds for project installs
- render role-specific terminal boards
- generate project-local board, monitor, `tmux`, and `cmux` launcher seeds
- provide a first-class `launch` CLI
- provide a curses-based TUI
- provide a non-interactive install CLI
- keep migrated control-plane reference assets from `__codex_agents`

Next scope:

- recovery and bootstrap improvements
- live pane and session status sync
- live agent integration

## Running

Running `codex-orchestrator` without a subcommand opens the TUI by default.

```bash
codex-orchestrator
```

During development you can also run the CLI directly from the repo root.

If you install with `pip install -e .`, the same entrypoint becomes available as `codex-orchestrator ...`.

Examples from the project root:

```bash
PYTHONPATH=src python3 -m codex_orchestrator.cli catalog
PYTHONPATH=src python3 -m codex_orchestrator.cli catalog --project-root . --scope project
PYTHONPATH=src python3 -m codex_orchestrator.cli panel --project-root .
PYTHONPATH=src python3 -m codex_orchestrator.cli board --project-root . --role cto-coordinator
PYTHONPATH=src python3 -m codex_orchestrator.cli launch --project-root . --backend tmux --dry-run
PYTHONPATH=src python3 -m codex_orchestrator.cli enqueue --project-root . --summary "Investigate the failing review flow"
PYTHONPATH=src python3 -m codex_orchestrator.cli dispatch-open --project-root .
PYTHONPATH=src python3 -m codex_orchestrator.cli dispatch-prepare --project-root . --dispatch-id dispatch-001
PYTHONPATH=src python3 -m codex_orchestrator.cli dispatch-begin --project-root . --dispatch-id dispatch-001
PYTHONPATH=src python3 -m codex_orchestrator.cli apply-result --project-root . --dispatch-id dispatch-001 --outcome completed --summary "Done"
PYTHONPATH=src python3 -m codex_orchestrator.cli tui
```

## Development Install / Uninstall

For development, use the repo-local editable install flow.

```bash
./scripts/install.sh
codex-orchestrator --help
./scripts/uninstall.sh
```

Default behavior:

- `install.sh` creates `.venv/` in the repo root and runs `pip install -e .`
- it attempts to create a `~/.local/bin/codex-orchestrator` symlink by default
- if `~/.local/bin` is not on `PATH`, use `source .venv/bin/activate` or `.venv/bin/codex-orchestrator`
- useful options include `install.sh --dry-run`, `install.sh --no-link`, and `uninstall.sh --keep-venv`

Non-interactive install:

```bash
PYTHONPATH=src python3 -m codex_orchestrator.cli install \
  --scope project \
  --agents cto-coordinator,reviewer,code-mapper
```

## Testing / Validation

Default automated validation:

```bash
./scripts/test.sh
```

Run the underlying commands directly if needed:

```bash
python3 -m compileall src
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Manual smoke examples:

```bash
PYTHONPATH=src python3 -m codex_orchestrator.cli catalog
PYTHONPATH=src python3 -m codex_orchestrator.cli install \
  --scope project \
  --project-root .tmp-smoke \
  --agents cto-coordinator,reviewer
```

If you touch the curses TUI, keep a PTY-based manual smoke in addition to automated tests.

## Current Install Behavior

- `project` scope requires at least one meta-orchestration agent
- `project` scope creates both `.codex/agents` and `.codex/orchestrator`
- `project` scope also creates board, monitor, and backend launcher seeds under `.codex/orchestrator/launchers/`
- in the TUI, project installs preselect a root orchestrator candidate and return to selection instead of exiting if the orchestrator is missing
- `global` scope only manages `~/.codex/agents` and does not create project-local scaffold data

## Current Discovery Behavior

- `catalog --scope project` shows built-in, global, and project `.toml` agents together
- `catalog --scope global` shows built-in and global `.toml` agents
- conflicts follow `project > global > built-in` precedence
- if an external `.toml` overrides a built-in key, it keeps the inherited category; new keys land under `Imported & External`

## Current Panel Behavior

- `panel --project-root <path>` reads `.codex/orchestrator/team.toml` and seeded state to render an `operator -> orchestrator -> workers` text topology
- orchestrator and worker status come from `runtime/agents.toml`
- queue summary comes from `queue/commands.toml`, dispatch summary from `ledger/dispatches.toml`
- `enqueue --summary ...` pushes an operator command into the project queue and targets the root orchestrator by default
- `dispatch-open` promotes the next `pending` queue item into a `ready` dispatch ticket and changes the queue status to `claimed`
- `dispatch-prepare --dispatch-id ...` renders the handoff brief and suggested `send_input` payload for a ready dispatch
- `dispatch-begin --dispatch-id ...` moves queue, ledger, and runtime state into the in-flight `dispatched` state immediately after the real send step
- `apply-result` applies `completed`, `failed`, or `cancelled` to queue, ledger, and runtime state together
- roles are `busy` during `dispatch-open` and `dispatch-begin`, then return to `idle` or `blocked` after `apply-result`
- actual `send_input` and `wait_agent` calls still live outside the current product runtime

## Current Board / Launcher Behavior

- `board --role <role>` renders a read-only terminal board for a specific orchestrator or worker role
- project installs generate `.codex/orchestrator/launchers/run-board.sh`, `run-monitor.sh`, `launch-tmux.sh`, and `launch-cmux.sh`
- `launch --backend tmux|cmux` is the first-class entrypoint for generated launcher seeds
- `launch --dry-run` prints the backend, launcher path, and final command without executing it
- `--no-attach` is currently supported only for the `tmux` backend
- generated `tmux` and `cmux` launchers soft-fail with `SKIP` when the backend is unavailable
- live queue draining and actual `spawn_agent` / `send_input` / `wait_agent` integration are still pending

## Current Output Format

Generated subagent files follow a Codex-compatible TOML structure influenced by VoltAgent:

- `name`
- `description`
- `model`
- `model_reasoning_effort`
- `sandbox_mode`
- `[instructions].text`

## References

- current status / handoff: [docs/HANDOFF.md](./docs/HANDOFF.md)
- product direction: [docs/PRD.md](./docs/PRD.md)
- product understanding / workflow: [docs/UNDERSTANDING_AND_WORKFLOW.md](./docs/UNDERSTANDING_AND_WORKFLOW.md)
- migration notes: [docs/MIGRATION_FROM__CODEX_AGENTS.md](./docs/MIGRATION_FROM__CODEX_AGENTS.md)
- testing workflow: [docs/TESTING.md](./docs/TESTING.md)
- shell control-plane reference assets: [reference/legacy_shell_control_plane/README.md](./reference/legacy_shell_control_plane/README.md)
- Korean docs: [README.ko.md](./README.ko.md), [docs/HANDOFF.ko.md](./docs/HANDOFF.ko.md), [docs/PRD.ko.md](./docs/PRD.ko.md), [docs/UNDERSTANDING_AND_WORKFLOW.ko.md](./docs/UNDERSTANDING_AND_WORKFLOW.ko.md), [docs/TESTING.ko.md](./docs/TESTING.ko.md), [docs/MIGRATION_FROM__CODEX_AGENTS.ko.md](./docs/MIGRATION_FROM__CODEX_AGENTS.ko.md)
- this repository does not ship company-specific or product-specific example assets
