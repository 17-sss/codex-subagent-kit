# codex-subagent-kit

Korean version: [README.ko.md](./README.ko.md)

`codex-subagent-kit` is a local-first toolkit for installing and managing Codex subagent definitions in project and global `.codex` directories.

Use it when you want to:

- browse the VoltAgent-backed default catalog plus external or user-authored catalogs
- install compatible `.codex/agents/*.toml` files into a project or global scope
- scaffold your own category and agent templates
- sync upstream catalog content into project or global source roots
- use a simple install-first TUI when you do not want to memorize commands

In practice, the flow is simple: choose agents, generate TOML files, then open `codex` in that workspace and ask it to use those subagents.

`codex-subagent-kit` prepares the workspace. `codex` remains the runtime that spawns and manages agent threads.

Package note: the active implementation and npm release target live under [`packages/codex-subagent-kit/`](./packages/codex-subagent-kit/).

## Quick Start

If you want to use the published CLI right away:

```bash
npx codex-subagent-kit
```

That bare command opens the install-first TUI without a local clone.
For first-time use, prefer `npx codex-subagent-kit` over a bare `codex-subagent-kit` shell command.

If you prefer the non-interactive npm path:

```bash
npx codex-subagent-kit install \
  --scope project \
  --project-root /tmp/codex-subagent-kit-demo \
  --agents reviewer,code-mapper \
  --validate
```

If you want to work from this repository:

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
npx codex-subagent-kit install \
  --scope project \
  --project-root /tmp/codex-subagent-kit-demo \
  --agents reviewer,code-mapper \
  --validate
npx codex-subagent-kit usage \
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
npx codex-subagent-kit catalog
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

## Troubleshooting

If `codex-subagent-kit` fails with a Python error such as `ModuleNotFoundError: No module named 'codex_subagent_kit'`, your shell is probably finding an old Python-era shim before the npm CLI.

Check which command is currently being used:

```bash
which codex-subagent-kit
head -n 5 "$(which codex-subagent-kit)"
```

If that path points to `~/.local/bin/codex-subagent-kit` and the file imports `codex_subagent_kit.cli`, remove the stale shim and use the npm CLI instead:

```bash
rm -f ~/.local/bin/codex-subagent-kit
npx codex-subagent-kit --help
```

If you want a persistent shell command after cleanup:

```bash
npm install -g codex-subagent-kit
codex-subagent-kit --help
```

## TypeScript Package Status

The TypeScript package is now the source of truth for the stable CLI surface: `catalog`, `catalog sync`, `catalog import`, `template init`, `install`, `doctor`, `usage`, and the install-first interactive `tui`. The bare command entrypoint also opens the interactive install flow, and shared golden fixtures validate generated TOML plus `usage` and `doctor` output.

Published npm version examples:

```bash
npx codex-subagent-kit --help
npx codex-subagent-kit catalog
npx codex-subagent-kit install --scope project --project-root /tmp/example --agents reviewer,code-mapper --validate
```

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
npm run test:ts
npm run typecheck:ts
npm run build:ts
npm run pack:ts
npm run smoke:ts:consumer
```

If you touch the TUI, keep one interactive smoke in addition to the automated checks.

## References

- product direction: [docs/PRD.md](./docs/PRD.md)
- product understanding / workflow: [docs/UNDERSTANDING_AND_WORKFLOW.md](./docs/UNDERSTANDING_AND_WORKFLOW.md)
- testing workflow: [docs/TESTING.md](./docs/TESTING.md)
- PR CI workflow: [docs/TESTING.md](./docs/TESTING.md)
- release workflow: [docs/RELEASING.md](./docs/RELEASING.md)
- TypeScript/npm port plan: [docs/TYPESCRIPT_PORT.md](./docs/TYPESCRIPT_PORT.md)
