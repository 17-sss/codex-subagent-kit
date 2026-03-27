# codex-subagent-kit

Korean version: [README.ko.md](./README.ko.md)

`codex-subagent-kit` is a local-first toolkit for installing and managing Codex subagent definitions in project and global `.codex` directories.

Implementation tracks:

- TypeScript package: the active npm-targeted implementation under [`packages/codex-subagent-kit/`](/Users/hoyoungson/Code/Project/Personal/codex-orchestrator/packages/codex-subagent-kit)
- Python app: a legacy implementation kept under [`src/codex_subagent_kit/`](/Users/hoyoungson/Code/Project/Personal/codex-orchestrator/src/codex_subagent_kit) for reference, experimental commands, and fallback development workflows

The stable product core is simple:

- browse the VoltAgent-backed default catalog plus external/user-authored catalogs
- install compatible `.codex/agents/*.toml` files
- scaffold new category and agent templates
- sync upstream catalog content into project/global source roots
- use a TUI for the install-first workflow

`codex-subagent-kit` prepares the workspace. `codex` remains the runtime that spawns and manages agent threads.

## Quick Start

If you want to try the current TypeScript implementation from this repository:

```bash
npm install
npm run build:ts
node packages/codex-subagent-kit/dist/cli.js
```

That bare command opens the install-first TUI.

If you prefer the non-interactive path:

```bash
node packages/codex-subagent-kit/dist/cli.js install \
  --scope project \
  --project-root /tmp/codex-subagent-kit-demo \
  --agents reviewer,code-mapper \
  --validate
```

## 5-Minute Test Drive

Use this if you want one copy-paste flow to verify the tool end to end:

```bash
mkdir -p /tmp/codex-subagent-kit-demo
node packages/codex-subagent-kit/dist/cli.js install \
  --scope project \
  --project-root /tmp/codex-subagent-kit-demo \
  --agents reviewer,code-mapper \
  --validate
node packages/codex-subagent-kit/dist/cli.js usage \
  --scope project \
  --project-root /tmp/codex-subagent-kit-demo \
  --task "Review the failing auth flow"
cd /tmp/codex-subagent-kit-demo
codex
```

Expected result:

- `.codex/agents/reviewer.toml` and `.codex/agents/code-mapper.toml` exist
- `doctor` reports `status: ok`
- `usage` prints a starter prompt you can paste into Codex

## Stable Workflow

1. Choose `Project` or `Global`.
2. Browse the vendored VoltAgent snapshot, synced source roots, or injected `categories/` trees.
3. Select the agents you want.
4. Install `.codex/agents/*.toml`.
5. Run `codex` in that project and ask it to use those subagents.

This matches the current Codex-native model: custom agent definitions live under `~/.codex/agents/` or `.codex/agents/`, while actual agent threads are spawned and managed inside Codex.

## Stable Commands

Running `codex-subagent-kit` without a subcommand opens the TUI by default.

```bash
codex-subagent-kit
```

Most users only need these stable commands:

```bash
codex-subagent-kit catalog
codex-subagent-kit catalog sync --scope project --source-root /path/to/awesome-codex-subagents
codex-subagent-kit catalog import --scope project --catalog-root /path/to/categories --agents custom-helper
codex-subagent-kit catalog --catalog-root /path/to/categories
codex-subagent-kit install --scope project --agents reviewer,code-mapper --validate
codex-subagent-kit doctor --scope project --project-root .
codex-subagent-kit usage --scope project --project-root . --task "Review the failing auth flow"
codex-subagent-kit template init --project-root . --category custom-ops --agent custom-coordinator
```

If you are not sure which command to run:

- `catalog`: browse the currently visible agents
- `catalog sync`: refresh the VoltAgent-backed source catalog
- `install`: write `.codex/agents/*.toml` into a project or global scope
- `doctor`: validate installed TOML files and visible catalog roots
- `usage`: generate a starter prompt for Codex based on installed agents
- `template init`: scaffold your own category and agent template

Legacy Python direct execution from the repo root is also supported:

```bash
PYTHONPATH=src python3 -m codex_subagent_kit.cli catalog
PYTHONPATH=src python3 -m codex_subagent_kit.cli catalog sync --scope project --source-root /path/to/awesome-codex-subagents
PYTHONPATH=src python3 -m codex_subagent_kit.cli catalog import --scope project --catalog-root /path/to/categories --agents custom-helper
PYTHONPATH=src python3 -m codex_subagent_kit.cli install --scope project --agents reviewer,code-mapper --validate
PYTHONPATH=src python3 -m codex_subagent_kit.cli doctor --scope project --project-root .
PYTHONPATH=src python3 -m codex_subagent_kit.cli usage --scope project --project-root . --task "Review the failing auth flow"
PYTHONPATH=src python3 -m codex_subagent_kit.cli template init --project-root . --category custom-ops --agent custom-coordinator
```

## Catalog Model

- the default built-in catalog is a vendored snapshot of VoltAgent [`awesome-codex-subagents/categories`](https://github.com/VoltAgent/awesome-codex-subagents/tree/main/categories)
- project-local synced source roots live under `.codex/subagent-kit/sources/<source>/categories/`
- global synced source roots live under `~/.codex/subagent-kit/sources/<source>/categories/`
- project-local injection lives under `.codex/subagent-kit/catalog/categories/`
- global injection lives under `~/.codex/subagent-kit/catalog/categories/`
- `--catalog-root <path>` accepts any awesome-style `categories/` tree
- `catalog sync` refreshes a synced source root from VoltAgent upstream or a local awesome-style clone
- `catalog import` can persist selected categories or agents into those injection paths
- user-authored templates can follow the same folder format and participate in the same install flow

Merged catalog precedence is:

- built-in VoltAgent snapshot
- global synced source roots
- global user catalog injection roots
- project synced source roots
- project user catalog injection roots
- explicit `--catalog-root` entries

Installed agent files then take final precedence by scope:

- `project`
- `global`

## Template Scaffolding

Create a new category and agent template in the project-local injection path:

```bash
codex-subagent-kit template init \
  --project-root . \
  --category custom-ops \
  --agent custom-coordinator
```

Create one directly in an external `categories/` tree:

```bash
codex-subagent-kit template init \
  --catalog-root /path/to/categories \
  --category custom-ops \
  --agent custom-coordinator \
  --orchestrator
```

Persist selected external templates into the project-local injection path:

```bash
codex-subagent-kit catalog import \
  --scope project \
  --project-root . \
  --catalog-root /path/to/categories \
  --agents custom-helper,custom-reviewer
```

Refresh the project-local VoltAgent source root from a local clone:

```bash
codex-subagent-kit catalog sync \
  --scope project \
  --project-root . \
  --source-root /path/to/awesome-codex-subagents
```

Refresh directly from VoltAgent GitHub `main/categories`:

```bash
codex-subagent-kit catalog sync --scope project --project-root .
```

Generated agent files use a Codex-compatible TOML shape:

- `name`
- `description`
- `model`
- `model_reasoning_effort`
- `sandbox_mode`
- `developer_instructions`

If the selected install set includes a `meta-orchestration` agent such as `multi-agent-coordinator`, the project install also seeds the optional experimental scaffold under `.codex/subagent-kit/`.

## Validation

Use `doctor` after install to confirm that visible agent files and any injected catalog roots are still well-formed. If you want that in one step, use `install --validate`.

```bash
codex-subagent-kit install --scope project --agents reviewer,code-mapper --validate
codex-subagent-kit doctor --scope project --project-root .
```

The TUI install flow also runs the same validation step after a successful install and surfaces the validation status on the completion screen.

## Usage Helper

Use `usage` when you want a starter prompt for Codex based on the agents actually visible in the selected scope. If a meta-orchestration agent is installed, `usage` prefers it; otherwise it suggests direct specialist prompts.

```bash
codex-subagent-kit usage \
  --scope project \
  --project-root . \
  --task "Review the failing auth flow"
```

After install, common Codex prompts look like this:

- `Use reviewer to review the current changes for bugs, regressions, and missing tests.`
- `Use code-mapper to map the auth flow before we change it.`
- `Use multi-agent-coordinator to coordinate reviewer and code-mapper for this task.`

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

See [docs/EXPERIMENTAL.md](./docs/EXPERIMENTAL.md) for the current experimental boundary.

## Legacy Python Install / Uninstall

For the legacy Python app, use the repo-local editable install flow.

```bash
./scripts/install.sh
codex-subagent-kit-legacy --help
./scripts/uninstall.sh
```

Default behavior:

- `install.sh` creates `.venv/` in the repo root and runs `pip install -e .`
- it attempts to create a `~/.local/bin/codex-subagent-kit-legacy` symlink by default
- if `~/.local/bin` is not on `PATH`, use `source .venv/bin/activate` or `.venv/bin/codex-subagent-kit-legacy`
- useful options include `install.sh --dry-run`, `install.sh --no-link`, and `uninstall.sh --keep-venv`

See [docs/LEGACY_PYTHON_APP.md](./docs/LEGACY_PYTHON_APP.md) for the current legacy-Python boundary.

## TypeScript Port Progress

The npm/TypeScript port now has a dedicated workspace under [`packages/codex-subagent-kit/`](/Users/hoyoungson/Code/Project/Personal/codex-orchestrator/packages/codex-subagent-kit).

The TypeScript package now covers most of the stable CLI surface: `catalog`, `catalog sync`, `catalog import`, `template init`, `install`, `doctor`, `usage`, and the install-first interactive `tui`. The bare command entrypoint also opens the interactive install flow, and the shared golden fixtures now validate generated TOML plus `usage` and `doctor` output. This is the current release target for npm, while the Python app remains in the repository as a legacy implementation.

Bootstrap validation commands:

```bash
npm install
npm run test:ts
npm run typecheck:ts
npm run build:ts
npm run pack:ts
node packages/codex-subagent-kit/dist/cli.js --help
node packages/codex-subagent-kit/dist/cli.js
node packages/codex-subagent-kit/dist/cli.js catalog
node packages/codex-subagent-kit/dist/cli.js catalog sync --scope project --project-root /tmp/example --source-root /tmp/awesome-codex-subagents
node packages/codex-subagent-kit/dist/cli.js catalog import --scope project --project-root /tmp/example --catalog-root /tmp/categories --agents custom-helper
node packages/codex-subagent-kit/dist/cli.js install --scope project --project-root /tmp/example --agents reviewer,code-mapper --validate
node packages/codex-subagent-kit/dist/cli.js usage --scope project --project-root /tmp/example --task "Review the failing auth flow"
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

If you touch the curses TUI, keep a PTY-based manual smoke in addition to automated tests.

## References

- product direction: [docs/PRD.md](./docs/PRD.md)
- product understanding / workflow: [docs/UNDERSTANDING_AND_WORKFLOW.md](./docs/UNDERSTANDING_AND_WORKFLOW.md)
- testing workflow: [docs/TESTING.md](./docs/TESTING.md)
- PR CI workflow: [docs/TESTING.md](./docs/TESTING.md)
- release workflow: [docs/RELEASING.md](./docs/RELEASING.md)
- TypeScript/npm port plan: [docs/TYPESCRIPT_PORT.md](./docs/TYPESCRIPT_PORT.md)
- legacy Python app: [docs/LEGACY_PYTHON_APP.md](./docs/LEGACY_PYTHON_APP.md)
- experimental boundary: [docs/EXPERIMENTAL.md](./docs/EXPERIMENTAL.md)
