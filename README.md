# codex-orchestrator

Korean version: [README.ko.md](./README.ko.md)

`codex-orchestrator` is a local-first toolkit for installing and managing Codex subagent definitions in project and global `.codex` directories.

The stable product core is simple:

- browse built-in and external agent catalogs
- install compatible `.codex/agents/*.toml` files
- scaffold new category and agent templates
- use a TUI for the install-first workflow

`codex-orchestrator` prepares the workspace. `codex` remains the runtime that spawns and manages agent threads.

## Stable Workflow

1. Choose `Project` or `Global`.
2. Browse built-in templates or inject an external `categories/` tree.
3. Select the agents you want.
4. Install `.codex/agents/*.toml`.
5. Run `codex` in that project and ask it to use those subagents.

This matches the current Codex-native model: custom agent definitions live under `~/.codex/agents/` or `.codex/agents/`, while actual agent threads are spawned and managed inside Codex.

## Stable Commands

Running `codex-orchestrator` without a subcommand opens the TUI by default.

```bash
codex-orchestrator
```

Most users only need these stable commands:

```bash
codex-orchestrator catalog
codex-orchestrator catalog --catalog-root /path/to/categories
codex-orchestrator install --scope project --agents cto-coordinator,reviewer,code-mapper
codex-orchestrator template init --project-root . --category custom-ops --agent custom-coordinator
```

Development-only direct execution from the repo root is also supported:

```bash
PYTHONPATH=src python3 -m codex_orchestrator.cli catalog
PYTHONPATH=src python3 -m codex_orchestrator.cli install --scope project --agents cto-coordinator,reviewer
PYTHONPATH=src python3 -m codex_orchestrator.cli template init --project-root . --category custom-ops --agent custom-coordinator
```

## Catalog Model

- the app ships a small app-owned built-in catalog
- the app does not vendor `awesome-codex-subagents` wholesale
- project-local injection lives under `.codex/orchestrator/catalog/categories/`
- global injection lives under `~/.codex/orchestrator/catalog/categories/`
- `--catalog-root <path>` accepts any awesome-style `categories/` tree
- user-authored templates can follow the same folder format and participate in the same install flow

When agent keys conflict, precedence is:

- `project`
- `global`
- `built-in`

## Template Scaffolding

Create a new category and agent template in the project-local injection path:

```bash
codex-orchestrator template init \
  --project-root . \
  --category custom-ops \
  --agent custom-coordinator
```

Create one directly in an external `categories/` tree:

```bash
codex-orchestrator template init \
  --catalog-root /path/to/categories \
  --category custom-ops \
  --agent custom-coordinator \
  --orchestrator
```

Generated agent files use a Codex-compatible TOML shape:

- `name`
- `description`
- `model`
- `model_reasoning_effort`
- `sandbox_mode`
- `developer_instructions`

## Experimental Commands

The repository currently also contains control-plane-oriented commands. These are kept available as experiments, but they are not the primary product identity and may change more aggressively.

Experimental commands:

- `panel`
- `board`
- `launch`
- `enqueue`
- `dispatch-open`
- `dispatch-prepare`
- `dispatch-begin`
- `apply-result`

These commands are best understood as a session-companion or prototype layer around Codex usage, not as a standalone multi-agent runtime that replaces Codex.

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

If you touch the curses TUI, keep a PTY-based manual smoke in addition to automated tests.

## References

- product direction: [docs/PRD.md](./docs/PRD.md)
- product understanding / workflow: [docs/UNDERSTANDING_AND_WORKFLOW.md](./docs/UNDERSTANDING_AND_WORKFLOW.md)
- testing workflow: [docs/TESTING.md](./docs/TESTING.md)
