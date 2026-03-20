# Quickstart: Dispatch Handoff

## Validate current baseline

```bash
./scripts/test.sh
```

## Prepare a fresh project and queue item

```bash
PYTHONPATH=src python3 -m codex_orchestrator.cli install \
  --scope project \
  --project-root .tmp-dispatch-handoff \
  --agents cto-coordinator,reviewer

PYTHONPATH=src python3 -m codex_orchestrator.cli enqueue \
  --project-root .tmp-dispatch-handoff \
  --summary "Review the control-plane regression"

PYTHONPATH=src python3 -m codex_orchestrator.cli dispatch-open \
  --project-root .tmp-dispatch-handoff
```

## Render the handoff package

```bash
PYTHONPATH=src python3 -m codex_orchestrator.cli dispatch-prepare \
  --project-root .tmp-dispatch-handoff \
  --dispatch-id dispatch-001
```

Expected outcomes:

- the output shows `dispatch-001`
- the role and command summary are visible
- the suggested send_input message is ready to reuse

## Mark it in-flight

```bash
PYTHONPATH=src python3 -m codex_orchestrator.cli dispatch-begin \
  --project-root .tmp-dispatch-handoff \
  --dispatch-id dispatch-001

PYTHONPATH=src python3 -m codex_orchestrator.cli panel \
  --project-root .tmp-dispatch-handoff
```

Expected outcomes:

- queue summary includes `dispatched`
- dispatch ledger includes `dispatched`
- role remains busy until `apply-result`
