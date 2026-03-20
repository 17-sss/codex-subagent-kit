from __future__ import annotations

import tomllib
from pathlib import Path


class PanelError(RuntimeError):
    """Raised when the control panel cannot be rendered."""


def resolve_team_manifest_path(project_root: Path) -> Path:
    return project_root / ".codex" / "orchestrator" / "team.toml"


def load_team_manifest(project_root: Path) -> tuple[str, str, list[str]]:
    manifest_path = resolve_team_manifest_path(project_root)
    if not manifest_path.exists():
        raise PanelError(f"team manifest not found: {manifest_path}")

    with manifest_path.open("rb") as handle:
        data = tomllib.load(handle)

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


def render_panel(project_root: Path) -> str:
    operator_label, orchestrator, workers = load_team_manifest(project_root)

    lines = [f"Operator: {operator_label}", f"`- Orchestrator: {orchestrator}"]
    if workers:
        for index, worker in enumerate(workers):
            branch = "|- " if index < len(workers) - 1 else "`- "
            lines.append(f"   {branch}{worker}")
    else:
        lines.append("   `- (no workers)")

    return "\n".join(lines)
