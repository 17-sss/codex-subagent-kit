# Quickstart: Launcher Flow

## Validate current baseline

```bash
./scripts/test.sh
```

## Prepare a fresh project

```bash
PYTHONPATH=src python3 -m codex_subagent_kit.cli install \
  --scope project \
  --project-root .tmp-launcher \
  --agents multi-agent-coordinator,reviewer,code-mapper
```

## Render a role board

```bash
PYTHONPATH=src python3 -m codex_subagent_kit.cli board \
  --project-root .tmp-launcher \
  --role multi-agent-coordinator
```

Expected outcomes:

- the role board shows orchestrator status
- related queue/dispatch items are listed

## Inspect generated launchers

```bash
ls .tmp-launcher/.codex/subagent-kit/launchers
sed -n '1,120p' .tmp-launcher/.codex/subagent-kit/launchers/launch-tmux.sh
```

Expected outcomes:

- board/monitor launcher helpers exist
- optional backend scripts exist for `tmux` and `cmux`
- scripts refer to the current team topology
