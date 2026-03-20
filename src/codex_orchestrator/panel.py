from __future__ import annotations

import tomllib
from collections import Counter
from pathlib import Path


class PanelError(RuntimeError):
    """Raised when the control panel cannot be rendered."""


def resolve_team_manifest_path(project_root: Path) -> Path:
    return project_root / ".codex" / "orchestrator" / "team.toml"


def resolve_runtime_state_path(project_root: Path) -> Path:
    return project_root / ".codex" / "orchestrator" / "runtime" / "agents.toml"


def resolve_queue_path(project_root: Path) -> Path:
    return project_root / ".codex" / "orchestrator" / "queue" / "commands.toml"


def resolve_dispatch_ledger_path(project_root: Path) -> Path:
    return project_root / ".codex" / "orchestrator" / "ledger" / "dispatches.toml"


def _load_toml(path: Path) -> dict[str, object]:
    with path.open("rb") as handle:
        return tomllib.load(handle)


def _load_optional_toml(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    return _load_toml(path)


def _clean_status(value: object, *, default: str) -> str:
    if not isinstance(value, str) or not value.strip():
        return default
    return value.strip()


def load_team_manifest(project_root: Path) -> tuple[str, str, list[str]]:
    manifest_path = resolve_team_manifest_path(project_root)
    if not manifest_path.exists():
        raise PanelError(f"team manifest not found: {manifest_path}")

    data = _load_toml(manifest_path)
    operator_label = data.get("operator", {}).get("label")
    orchestrator = data.get("team", {}).get("orchestrator")
    workers = data.get("team", {}).get("workers")

    if not isinstance(operator_label, str) or not operator_label.strip():
        raise PanelError(f"invalid operator label in: {manifest_path}")
    if not isinstance(orchestrator, str) or not orchestrator.strip():
        raise PanelError(f"invalid orchestrator key in: {manifest_path}")
    if not isinstance(workers, list) or not all(isinstance(item, str) for item in workers):
        raise PanelError(f"invalid workers list in: {manifest_path}")

    return operator_label.strip(), orchestrator.strip(), [worker.strip() for worker in workers]


def load_runtime_statuses(project_root: Path) -> dict[str, str]:
    data = _load_optional_toml(resolve_runtime_state_path(project_root))
    statuses: dict[str, str] = {}

    orchestrator_data = data.get("orchestrator")
    if isinstance(orchestrator_data, dict):
        key = orchestrator_data.get("key")
        if isinstance(key, str) and key.strip():
            statuses[key.strip()] = _clean_status(orchestrator_data.get("status"), default="idle")

    worker_items = data.get("workers")
    if isinstance(worker_items, list):
        for worker_item in worker_items:
            if not isinstance(worker_item, dict):
                continue
            key = worker_item.get("key")
            if not isinstance(key, str) or not key.strip():
                continue
            statuses[key.strip()] = _clean_status(worker_item.get("status"), default="idle")

    return statuses


def _count_statuses(items: object) -> Counter[str]:
    counts: Counter[str] = Counter()
    if not isinstance(items, list):
        return counts

    for item in items:
        if not isinstance(item, dict):
            continue
        counts[_clean_status(item.get("status"), default="unknown")] += 1

    return counts


def load_queue_counts(project_root: Path) -> Counter[str]:
    data = _load_optional_toml(resolve_queue_path(project_root))
    return _count_statuses(data.get("commands"))


def load_dispatch_counts(project_root: Path) -> Counter[str]:
    data = _load_optional_toml(resolve_dispatch_ledger_path(project_root))
    return _count_statuses(data.get("dispatches"))


def _format_counter_line(label: str, value: int) -> str:
    return f"- {label}: {value}"


def render_panel(project_root: Path) -> str:
    operator_label, orchestrator, workers = load_team_manifest(project_root)
    runtime_statuses = load_runtime_statuses(project_root)
    queue_counts = load_queue_counts(project_root)
    dispatch_counts = load_dispatch_counts(project_root)

    lines = [
        f"Operator: {operator_label}",
        f"`- Orchestrator: {orchestrator} [{runtime_statuses.get(orchestrator, 'idle')}]",
    ]
    if workers:
        for index, worker in enumerate(workers):
            branch = "|- " if index < len(workers) - 1 else "`- "
            status = runtime_statuses.get(worker, "idle")
            lines.append(f"   {branch}{worker} [{status}]")
    else:
        lines.append("   `- (no workers)")

    lines.extend(
        [
            "",
            "Queue",
            _format_counter_line("pending", queue_counts.get("pending", 0)),
            _format_counter_line("claimed", queue_counts.get("claimed", 0)),
            _format_counter_line("completed", queue_counts.get("completed", 0)),
            "",
            "Dispatch Ledger",
            _format_counter_line("ready", dispatch_counts.get("ready", 0)),
            _format_counter_line("dispatched", dispatch_counts.get("dispatched", 0)),
            _format_counter_line("completed", dispatch_counts.get("completed", 0)),
            _format_counter_line("failed", dispatch_counts.get("failed", 0)),
            _format_counter_line("cancelled", dispatch_counts.get("cancelled", 0)),
        ]
    )

    return "\n".join(lines)
