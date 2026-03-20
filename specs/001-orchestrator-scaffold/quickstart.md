# Quickstart: Orchestrator Scaffold Generation

## Validate current behavior

```bash
./scripts/test.sh
PYTHONPATH=src python3 -m codex_orchestrator.cli catalog
```

## Validate project-scope install

```bash
PYTHONPATH=src python3 -m codex_orchestrator.cli install \
  --scope project \
  --project-root .tmp-smoke \
  --agents cto-coordinator,reviewer,code-mapper
```

Expected outcomes:

- `.tmp-smoke/.codex/agents/*.toml` created in canonical TOML format
- `.tmp-smoke/.codex/orchestrator/` scaffold created
- generated team manifest includes one root orchestrator and the remaining worker agents

## Validate global install

```bash
PYTHONPATH=src python3 -m codex_orchestrator.cli install \
  --scope global \
  --agents reviewer
```

Expected outcomes:

- `~/.codex/agents/reviewer.toml` created
- no project-local `.codex/orchestrator` scaffold generated

## Validate TUI

```bash
PYTHONPATH=src python3 -m codex_orchestrator.cli tui --project-root .tmp-tui
```

Expected outcomes:

- scope and agent selection still work
- install completes with scaffold generation for project scope
- no regressions in install summary/result screens
