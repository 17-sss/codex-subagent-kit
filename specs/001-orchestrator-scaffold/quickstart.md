# Quickstart: Orchestrator Scaffold Generation

## Validate current behavior

```bash
./scripts/test.sh
PYTHONPATH=src python3 -m codex_subagent_kit.cli catalog
```

## Validate project-scope install

```bash
PYTHONPATH=src python3 -m codex_subagent_kit.cli install \
  --scope project \
  --project-root .tmp-smoke \
  --agents multi-agent-coordinator,reviewer,code-mapper
```

Expected outcomes:

- `.tmp-smoke/.codex/agents/*.toml` created in canonical TOML format
- `.tmp-smoke/.codex/subagent-kit/` scaffold created
- generated team manifest includes one root orchestrator and the remaining worker agents

## Validate global install

```bash
PYTHONPATH=src python3 -m codex_subagent_kit.cli install \
  --scope global \
  --agents reviewer
```

Expected outcomes:

- `~/.codex/agents/reviewer.toml` created
- no project-local `.codex/subagent-kit` scaffold generated

## Validate TUI

```bash
PYTHONPATH=src python3 -m codex_subagent_kit.cli tui --project-root .tmp-tui
```

Expected outcomes:

- scope and agent selection still work
- install completes with scaffold generation for project scope
- no regressions in install summary/result screens
