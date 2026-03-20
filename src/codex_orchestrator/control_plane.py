from __future__ import annotations

from datetime import datetime
from pathlib import Path

from .panel import PanelError, load_team_manifest, resolve_queue_path


class ControlPlaneError(RuntimeError):
    """Raised when a control-plane mutation fails."""


def _escape_toml_string(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def _render_command_block(command: dict[str, str]) -> str:
    return "\n".join(
        [
            "[[commands]]",
            f'id = "{_escape_toml_string(command["id"])}"',
            f'role = "{_escape_toml_string(command["role"])}"',
            f'status = "{_escape_toml_string(command["status"])}"',
            f'summary = "{_escape_toml_string(command["summary"])}"',
            f'source = "{_escape_toml_string(command["source"])}"',
            f'priority = "{_escape_toml_string(command["priority"])}"',
            f'created_at = "{_escape_toml_string(command["created_at"])}"',
        ]
    )


def _render_queue(commands: list[dict[str, str]]) -> str:
    lines = ["version = 1"]
    for command in commands:
        lines.extend(["", _render_command_block(command)])
    return "\n".join(lines) + "\n"


def _next_command_id(commands: list[dict[str, str]]) -> str:
    max_suffix = 0
    for command in commands:
        command_id = command.get("id", "")
        if not command_id.startswith("cmd-"):
            continue
        suffix = command_id[4:]
        if suffix.isdigit():
            max_suffix = max(max_suffix, int(suffix))
    return f"cmd-{max_suffix + 1:03d}"


def load_queue_commands(project_root: Path) -> list[dict[str, str]]:
    queue_path = resolve_queue_path(project_root)
    if not queue_path.exists():
        return []

    from .panel import _load_toml  # imported lazily to avoid widening the public panel surface

    data = _load_toml(queue_path)
    raw_commands = data.get("commands")
    if not isinstance(raw_commands, list):
        return []

    commands: list[dict[str, str]] = []
    for raw_command in raw_commands:
        if not isinstance(raw_command, dict):
            continue
        command: dict[str, str] = {}
        for key in ("id", "role", "status", "summary", "source", "priority", "created_at"):
            value = raw_command.get(key)
            if isinstance(value, str):
                command[key] = value
        if {"id", "role", "status", "summary", "source", "priority", "created_at"} <= command.keys():
            commands.append(command)
    return commands


def resolve_target_role(project_root: Path, requested_role: str | None) -> str:
    try:
        _, orchestrator, workers = load_team_manifest(project_root)
    except PanelError as exc:
        raise ControlPlaneError(str(exc)) from exc

    if requested_role is None:
        return orchestrator

    candidate = requested_role.strip()
    valid_roles = {orchestrator, *workers}
    if candidate not in valid_roles:
        raise ControlPlaneError(f"unknown role for this team: {candidate}")
    return candidate


def enqueue_command(
    *,
    project_root: Path,
    summary: str,
    role: str | None = None,
    source: str = "operator",
    priority: str = "normal",
) -> tuple[str, Path]:
    summary_text = summary.strip()
    if not summary_text:
        raise ControlPlaneError("summary must not be empty")

    queue_path = resolve_queue_path(project_root)
    queue_path.parent.mkdir(parents=True, exist_ok=True)

    commands = load_queue_commands(project_root)
    target_role = resolve_target_role(project_root, role)
    command_id = _next_command_id(commands)
    commands.append(
        {
            "id": command_id,
            "role": target_role,
            "status": "pending",
            "summary": summary_text,
            "source": source.strip() or "operator",
            "priority": priority.strip() or "normal",
            "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        }
    )
    queue_path.write_text(_render_queue(commands), encoding="utf-8")
    return command_id, queue_path
