# HANDOFF

Korean version: [HANDOFF.ko.md](./HANDOFF.ko.md)

## Metadata

- Project: codex-orchestrator
- Project ID: codex-orchestrator
- Repo Root: /Users/hoyoungson/Code/Project/Personal/codex-orchestrator
- Branch: 001-orchestrator-scaffold
- Last Updated: 2026-03-23T00:16:05+09:00
- Updated By: hoyoungson

## TL;DR

- `codex-orchestrator` is now a standalone project with working project/global installs, canonical TOML agent generation, project-scope orchestrator scaffold seeds, and external `.toml` discovery.
- built-in agent output is aligned to the VoltAgent-style Codex-compatible `[instructions].text` structure.
- project-scope installs create `.codex/agents/*.toml` plus `.codex/orchestrator/team.toml`, runtime/queue/dispatch seeds, and the control-plane scaffold directories.
- `catalog` and the selection flow discover project/global `.toml` sources and apply `project > global > built-in` precedence.
- `panel` now reads `team.toml`, `runtime/agents.toml`, `queue/commands.toml`, and `ledger/dispatches.toml` to render a seeded runtime summary.
- `board` renders a read-only terminal board for either the orchestrator or a worker role.
- `enqueue` writes operator commands into the project queue and defaults the target to the root orchestrator.
- `dispatch-open` promotes the next `pending` queue command into a `ready` dispatch ticket and changes the queue status to `claimed`.
- `dispatch-prepare` renders the handoff brief and suggested `send_input` payload for a ready dispatch.
- `dispatch-begin` moves queue, ledger, and runtime state into `dispatched` immediately after the real send step.
- `apply-result` writes dispatch outcomes back into queue, ledger, and runtime state and updates panel summary.
- project installs generate board/monitor/`tmux`/`cmux` launcher seeds under `.codex/orchestrator/launchers/`.
- `launch` can execute or dry-run the generated `tmux` / `cmux` launcher seeds.
- `scripts/install.sh` and `scripts/uninstall.sh` standardize repo-local editable install and removal.
- running bare `codex-orchestrator` now enters the TUI by default.

## Current Objective

- connect the next thin slice after the file-based control-plane handoff to actual agent I/O boundaries

## Current State

Done
- implemented the built-in subagent catalog, installer, and curses TUI under `src/codex_orchestrator/`
- can generate `.codex/agents/*.toml` after choosing `Project` or `Global` scope
- aligned built-in agent TOML output to a VoltAgent-style Codex-compatible structure
- generate a project-scope `.codex/orchestrator` scaffold and `team.toml` seed with a root orchestrator
- generate `runtime/agents.toml`, `queue/commands.toml`, and `ledger/dispatches.toml` seeds for project installs
- preserve existing agent and scaffold seeds on rerun and report the result
- support project/global `.toml` discovery with `project > global > built-in` precedence
- render topology plus queue/dispatch summary via `panel --project-root <path>`
- render role-specific boards via `board --project-root <path> --role <role>`
- enqueue `pending` project queue commands via `enqueue --project-root <path> --summary ...`
- promote one `pending` command into a `ready` dispatch via `dispatch-open --project-root <path>`
- render a main-Codex handoff package via `dispatch-prepare --project-root <path> --dispatch-id ...`
- mark a live send as `dispatched` via `dispatch-begin --project-root <path> --dispatch-id ...`
- complete the active lifecycle via `apply-result --project-root <path> --dispatch-id ... --outcome ... --summary ...`
- backfill launcher seeds during project install
- expose generated launcher seeds through `launch --project-root <path> --backend tmux|cmux [--dry-run]`
- provide `./scripts/install.sh` for repo-local editable install plus optional `~/.local/bin/codex-orchestrator` symlink
- provide `./scripts/uninstall.sh` to remove the repo-managed symlink and `.venv`
- keep the TUI in the selection flow instead of exiting when a project install is missing a root orchestrator
- migrated generic shell control-plane docs and scripts from `__codex_agents` into `reference/legacy_shell_control_plane/`
- organized `specs/001-orchestrator-scaffold/` with spec/plan/tasks/quickstart
- established the SDD and testing baseline with `.specify/memory/constitution.md`, `docs/TESTING.md`, `scripts/test.sh`, and `tests/`
In progress
- deciding where the first thin slice for actual `send_input` / `wait_agent` integration should start
To confirm
- how live Codex agent I/O should map onto the file-based queue/dispatch model
- the minimum threshold for introducing live session binding or a broker layer

## Recent Changes

Changes
- initial Spec Kit feature/spec/plan/tasks foundation
- `unittest`-based test workflow and validation docs
- canonical agent TOML alignment
- project install scaffold and root orchestrator seed
- external `.toml` source discovery and precedence
- runtime / queue / dispatch seeds
- seeded runtime summary terminal panel renderer
- project queue enqueue flow
- queue-to-dispatch open flow
- dispatch result apply flow
- role-specific terminal board
- board/monitor/`tmux`/`cmux` launcher seeds
- first-class `launch` CLI
- dispatch handoff bridge
- development install/uninstall scripts
- bare-command TUI default plus project-scope TUI validation improvements
Validation run
- `python3 -m compileall src`
- `./scripts/test.sh`
- `PYTHONPATH=src python3 -m codex_orchestrator.cli catalog`
- validated that external `.toml` files appear in `catalog --scope project` for a temp project
- `PYTHONPATH=src python3 -m codex_orchestrator.cli install --scope project --project-root .tmp-smoke --agents cto-coordinator,reviewer,code-mapper`
- `PYTHONPATH=src python3 -m codex_orchestrator.cli panel --project-root <tmp-project>`
- confirmed fresh `.codex/orchestrator/team.toml` seed generation
- confirmed fresh `runtime/agents.toml`, `queue/commands.toml`, and `ledger/dispatches.toml` seed generation
- `PYTHONPATH=src python3 -m codex_orchestrator.cli enqueue --project-root <tmp-project> --summary "..."`
- `PYTHONPATH=src python3 -m codex_orchestrator.cli dispatch-open --project-root <tmp-project>`
- `PYTHONPATH=src python3 -m codex_orchestrator.cli dispatch-prepare --project-root <tmp-project> --dispatch-id dispatch-001`
- `PYTHONPATH=src python3 -m codex_orchestrator.cli dispatch-begin --project-root <tmp-project> --dispatch-id dispatch-001`
- `PYTHONPATH=src python3 -m codex_orchestrator.cli apply-result --project-root <tmp-project> --dispatch-id dispatch-001 --outcome completed --summary "..."`
- `PYTHONPATH=src python3 -m codex_orchestrator.cli board --project-root <tmp-project> --role <role>`
- `PYTHONPATH=src python3 -m codex_orchestrator.cli launch --project-root <tmp-project> --backend tmux --dry-run`
- `env PATH="/usr/bin:/bin" PYTHONPATH=src python3 -m codex_orchestrator.cli launch --project-root <tmp-project> --backend cmux`
- `bash -n scripts/install.sh`
- `bash -n scripts/uninstall.sh`
- temp venv/link-dir smoke: `./scripts/install.sh -> codex-orchestrator --help -> ./scripts/uninstall.sh`
- verified through CLI unit tests that bare `codex-orchestrator` enters the TUI
- `bash -n` syntax checks for generated launcher scripts
- PTY smoke for `PYTHONPATH=src python3 -m codex_orchestrator.cli tui --project-root .tmp-tui`
Impact
- the installer no longer behaves like a simple agent-file generator; it now creates a root-orchestrator scaffold seed
- built-in agents and external `.toml` agents can coexist in a single catalog ecosystem
- the generated scaffold now has an immediate terminal topology and state summary view
- operator commands can be written into the queue and seen from the panel immediately
- queue commands can be promoted into dispatch ledger tickets and observed in the panel
- a handoff package now exists for moving a ready dispatch into the main Codex conversation
- live sends can now be represented explicitly as `dispatched`
- a minimal result lifecycle now writes back into queue / ledger / runtime state
- launcher panes and windows now have a role-specific board to display
- project-local launcher seeds now give the optional dashboard backend a concrete entrypoint
- generated launcher seeds now have a first-class CLI entrypoint
- developers can now prepare repo-local editable installs through a single script
- bare-command UX now matches the installer use case, and project TUI validation is less brittle

## Known Issues / Watch List

Issue
- the current TUI still depends on curses and will not behave identically across every terminal / PTY environment
Risk
- the shell reference assets still contain `.env`-era assumptions and path conventions from `__codex_agents`
- the reference folder is a seed/reference area, not a runtime entrypoint
- TUI end-to-end coverage still relies on manual PTY smoke
- built-in sources still live in Python data structures rather than a packaged TOML library
- the current panel/control-plane stops at the handoff bridge and first-class launch CLI; live pane status and actual `send_input` / `wait_agent` integration are still missing
Workaround
- treat `src/codex_orchestrator/` as the product source of truth
- when extending the control panel, rebuild from generated scaffold and team metadata instead of reusing shell reference assets directly

## Quick Reference

Key files
- `src/codex_orchestrator/cli.py`
- `src/codex_orchestrator/tui.py`
- `src/codex_orchestrator/catalog.py`
- `src/codex_orchestrator/generator.py`
- `src/codex_orchestrator/panel.py`
- `tests/test_cli.py`
- `tests/test_generator.py`
- `tests/test_panel.py`
- `docs/PRD.md`
- `docs/TESTING.md`
- `docs/UNDERSTANDING_AND_WORKFLOW.md`
- `reference/legacy_shell_control_plane/README.md`
Commands
- `cd codex-orchestrator`
- `./scripts/test.sh`
- `PYTHONPATH=src python3 -m codex_orchestrator.cli catalog`
- `PYTHONPATH=src python3 -m codex_orchestrator.cli catalog --project-root . --scope project`
- `PYTHONPATH=src python3 -m codex_orchestrator.cli panel --project-root .`
- `PYTHONPATH=src python3 -m codex_orchestrator.cli launch --project-root . --backend tmux --dry-run`
- `PYTHONPATH=src python3 -m codex_orchestrator.cli dispatch-prepare --project-root . --dispatch-id dispatch-001`
- `PYTHONPATH=src python3 -m codex_orchestrator.cli dispatch-begin --project-root . --dispatch-id dispatch-001`
- `./scripts/install.sh`
- `./scripts/uninstall.sh`
- `codex-orchestrator`
- `PYTHONPATH=src python3 -m codex_orchestrator.cli tui`
- `PYTHONPATH=src python3 -m codex_orchestrator.cli install --scope project --agents cto-coordinator,reviewer`
Links / dashboards
- the minimal text panel and first-class launch CLI exist; a live runtime-aware control panel is still a future step

## Validation

Checks run
- `compileall`
- `unittest` suite via `./scripts/test.sh`
- catalog output
- external `.toml` discovery
- project-scope install
- orchestrator scaffold seed generation
- seeded runtime summary terminal panel renderer
- queue enqueue flow
- dispatch-open flow
- apply-result flow
- role-board flow
- launcher seed generation
- curses TUI smoke flow
Results
- all passed
- `.toml` output is generated correctly using the VoltAgent-influenced `[instructions].text` structure
- project installs generate a `team.toml` seed with a root orchestrator
- project installs generate runtime / queue / dispatch seeds
- `panel` renders the `operator -> orchestrator -> workers` topology and seeded state summary
- `enqueue` records `pending` commands in `queue/commands.toml` and updates panel counters
- `dispatch-open` changes `pending` queue items to `claimed` and records `ready` dispatches in `ledger/dispatches.toml`
- `dispatch-prepare` renders handoff text from the ready dispatch, queue command, and role definition
- `dispatch-begin` transitions queue / ledger / runtime into in-flight `dispatched`
- target roles become `busy` during dispatch and return to `idle` or `blocked` after `apply-result`
- `apply-result` updates queue / ledger / runtime together and feeds panel counters
- `board` renders role-level queue / dispatch / runtime state in a read-only terminal view
- project installs generate runnable shell seeds under `.codex/orchestrator/launchers/`
- generated launcher scripts soft-fail when `tmux` / `cmux` is unavailable
- `launch` resolves generated launcher paths and can dry-run or execute them
Not run yet
- actual `send_input` / `wait_agent` integration flow

## Next Actions

1. define the next thin slice for actual `send_input` / `wait_agent` integration
2. define the minimum state model required for live pane/session status sync
3. optionally move the built-in catalog into a portable file-based source

## Resume Checklist

- read `README.md`, `docs/PRD.md`, `docs/UNDERSTANDING_AND_WORKFLOW.md`, and `docs/HANDOFF.md`
- verify current state with `./scripts/test.sh`, `PYTHONPATH=src python3 -m codex_orchestrator.cli install --scope project --agents cto-coordinator,reviewer`, `PYTHONPATH=src python3 -m codex_orchestrator.cli board --project-root . --role cto-coordinator`, `PYTHONPATH=src python3 -m codex_orchestrator.cli panel --project-root .`, `PYTHONPATH=src python3 -m codex_orchestrator.cli launch --project-root . --backend tmux --dry-run`, and `PYTHONPATH=src python3 -m codex_orchestrator.cli dispatch-prepare --project-root . --dispatch-id dispatch-001`
- use `reference/legacy_shell_control_plane/` as reference only, and define the next thin slice around actual agent I/O calling or session-binding criteria

## Resume Prompt

Continue this project from `docs/HANDOFF.md`. First verify that the repo still matches the notes, then implement the next unfinished action: decide and implement the next minimal bridge from the file-based dispatch handoff into actual agent I/O or session binding, using the migrated legacy control-plane assets only as reference and not as the primary runtime.
