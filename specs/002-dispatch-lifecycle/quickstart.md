# Quickstart: Dispatch Lifecycle

## Validate current baseline

```bash
./scripts/test.sh
```

## Prepare a fresh project

```bash
PYTHONPATH=src python3 -m codex_subagent_kit.cli install \
  --scope project \
  --project-root .tmp-dispatch \
  --agents cto-coordinator,reviewer,code-mapper
```

## Enqueue a command

```bash
PYTHONPATH=src python3 -m codex_subagent_kit.cli enqueue \
  --project-root .tmp-dispatch \
  --summary "Investigate the failing review flow"
```

## Open a dispatch

```bash
PYTHONPATH=src python3 -m codex_subagent_kit.cli dispatch-open \
  --project-root .tmp-dispatch
```

Expected outcomes:

- one queue command moves out of the plain `pending` state
- one dispatch ticket is created in `ledger/dispatches.toml`
- panel reflects updated queue and dispatch counts

## Apply a result

```bash
PYTHONPATH=src python3 -m codex_subagent_kit.cli apply-result \
  --project-root .tmp-dispatch \
  --dispatch-id dispatch-001 \
  --outcome completed \
  --summary "Review finished and reported back"
```

Expected outcomes:

- queue, ledger, and runtime files are updated consistently
- panel shows the new result counts
