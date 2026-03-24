# LEGACY PYTHON APP

Korean version: [LEGACY_PYTHON_APP.ko.md](./LEGACY_PYTHON_APP.ko.md)

The repository keeps the original Python implementation under [`src/codex_subagent_kit/`](/Users/hoyoungson/Code/Project/Personal/codex-orchestrator/src/codex_subagent_kit) as a legacy app.

## What "Legacy" Means Here

- the Python app is still available in this repository
- it remains useful as a fallback development path
- it still carries experimental commands that are not part of the first npm package
- it is no longer the primary npm release target

## Entrypoints

Direct module execution from the repository root:

```bash
PYTHONPATH=src python3 -m codex_subagent_kit.cli --help
```

Editable-install legacy command:

```bash
./scripts/install.sh
codex-subagent-kit-legacy --help
```

## Current Legacy Surface

The Python app still contains:

- the original curses-based TUI
- the experimental control-plane commands
- the original Python test suite and fixture contract

These areas stay useful as:

- a reference implementation during migration
- a fallback tool for contributors already using the Python workflow
- the home for experimental commands that are not yet carried into the npm package

## Relationship To The TypeScript Package

- the TypeScript package under [`packages/codex-subagent-kit/`](/Users/hoyoungson/Code/Project/Personal/codex-orchestrator/packages/codex-subagent-kit) is the active npm release target
- the Python app remains in-repo as a legacy implementation
- removing the Python app is now a product decision, not an immediate migration requirement
