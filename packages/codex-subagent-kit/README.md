# codex-subagent-kit

`codex-subagent-kit` is the TypeScript CLI package for installing and managing Codex subagent definitions, catalogs, and templates.

The current TypeScript package covers the stable command surface:

- `catalog`
- `catalog import`
- `template init`
- `install`
- `doctor`
- `usage`
- `tui`
- bare command entrypoint for the install-first interactive flow

The TypeScript package is the active npm-targeted implementation. The Python app remains in the repository as a legacy implementation, a fallback development path, and the home for experimental commands that are outside the npm-first surface.

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

Browse the built-in and injected catalog:

```bash
node packages/codex-subagent-kit/dist/cli.js catalog
```

Import external awesome-style `categories/` content into the project catalog:

```bash
node packages/codex-subagent-kit/dist/cli.js catalog import \
  --scope project \
  --project-root /tmp/example \
  --catalog-root /tmp/categories \
  --agents custom-helper
```

Install project-scoped agents and validate them immediately:

```bash
node packages/codex-subagent-kit/dist/cli.js install \
  --scope project \
  --project-root /tmp/example \
  --agents cto-coordinator,reviewer \
  --validate
```

Render a Codex starter prompt from the installed agents:

```bash
node packages/codex-subagent-kit/dist/cli.js usage \
  --scope project \
  --project-root /tmp/example \
  --task "Review the failing auth flow"
```

## Packaging

The repository includes a dry-run packaging command:

```bash
npm run pack:ts
npm run smoke:ts:consumer
```

See the repository-level TypeScript migration notes in `docs/TYPESCRIPT_PORT.md` for current parity status and release readiness.
