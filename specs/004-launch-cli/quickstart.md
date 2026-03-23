# Quickstart: Launch CLI

## Validate current baseline

```bash
./scripts/test.sh
```

## Prepare a fresh project

```bash
PYTHONPATH=src python3 -m codex_subagent_kit.cli install \
  --scope project \
  --project-root .tmp-launch-cli \
  --agents cto-coordinator,reviewer,code-mapper
```

## Preview a tmux launch

```bash
PYTHONPATH=src python3 -m codex_subagent_kit.cli launch \
  --project-root .tmp-launch-cli \
  --backend tmux \
  --dry-run
```

Expected outcomes:

- backend is reported as `tmux`
- the resolved launcher path points to `.codex/subagent-kit/launchers/launch-tmux.sh`
- the final command is printed without executing

## Preview a named cmux launch

```bash
PYTHONPATH=src python3 -m codex_subagent_kit.cli launch \
  --project-root .tmp-launch-cli \
  --backend cmux \
  --name demo-workspace \
  --dry-run
```

Expected outcomes:

- backend is reported as `cmux`
- the printed command includes `demo-workspace`
- no terminal backend is opened during dry-run
