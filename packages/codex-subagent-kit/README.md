# codex-subagent-kit

`codex-subagent-kit` is the npm CLI package for installing and managing Codex subagent definitions, catalogs, and templates.

The current TypeScript package covers the stable command surface:

- `catalog`
- `catalog sync`
- `catalog import`
- `template init`
- `install`
- `doctor`
- `usage`
- `tui`
- bare command entrypoint for the install-first interactive flow

This package is the active source of truth for the product and the npm release target.

## Quick Start

Run the published CLI directly:

```bash
npx codex-subagent-kit
```

That bare command opens the install-first TUI.
For first-time use, prefer `npx codex-subagent-kit` over a bare `codex-subagent-kit` shell command.

If you want one quick non-interactive npm check:

```bash
npx codex-subagent-kit install \
  --scope project \
  --project-root /tmp/codex-subagent-kit-demo \
  --agents reviewer,code-mapper \
  --validate
npx codex-subagent-kit usage \
  --scope project \
  --project-root /tmp/codex-subagent-kit-demo \
  --task "Review the failing auth flow"
```

From the repository root:

```bash
npm install
npm run build:ts
node packages/codex-subagent-kit/dist/cli.js
```

## Local Development

From the repository root:

```bash
npm install
npm run test:ts
npm run typecheck:ts
npm run build:ts
npm run smoke:ts:consumer
node packages/codex-subagent-kit/dist/cli.js --help
node packages/codex-subagent-kit/dist/cli.js
```

## Stable Commands

Browse the VoltAgent-backed built-in snapshot and any injected catalogs:

```bash
npx codex-subagent-kit catalog
```

Refresh a project-local synced source root from a local clone or from VoltAgent upstream:

```bash
npx codex-subagent-kit catalog sync --scope project --project-root /tmp/example --source-root /tmp/awesome-codex-subagents
npx codex-subagent-kit catalog sync --scope project --project-root /tmp/example
```

Import external awesome-style `categories/` content into the project catalog:

```bash
npx codex-subagent-kit catalog import \
  --scope project \
  --project-root /tmp/example \
  --catalog-root /tmp/categories \
  --agents custom-helper
```

Install project-scoped agents and validate them immediately:

```bash
npx codex-subagent-kit install \
  --scope project \
  --project-root /tmp/example \
  --agents reviewer,code-mapper \
  --validate
```

Use `doctor` if you want to re-check the generated files later:

```bash
npx codex-subagent-kit doctor --scope project --project-root /tmp/example
```

Render a Codex starter prompt from the installed agents:

```bash
npx codex-subagent-kit usage \
  --scope project \
  --project-root /tmp/example \
  --task "Review the failing auth flow"
```

Common Codex-side prompts:

- `Use reviewer to review the current changes for bugs, regressions, and missing tests.`
- `Use code-mapper to map the auth flow before we change it.`

## Troubleshooting

If `codex-subagent-kit` fails with `ModuleNotFoundError: No module named 'codex_subagent_kit'`, your shell is using an old Python shim instead of the npm CLI.

Check the current binary:

```bash
which codex-subagent-kit
head -n 5 "$(which codex-subagent-kit)"
```

If it points to `~/.local/bin/codex-subagent-kit` and imports `codex_subagent_kit.cli`, remove it and use the npm CLI:

```bash
rm -f ~/.local/bin/codex-subagent-kit
npx codex-subagent-kit --help
```

If you want a persistent shell command after cleanup:

```bash
npm install -g codex-subagent-kit
codex-subagent-kit --help
```

## Packaging

The repository includes a dry-run packaging command:

```bash
npm run pack:ts
npm run smoke:ts:consumer
```

See the repository-level notes in `docs/TYPESCRIPT_PORT.md` for the final migration summary and release readiness.
