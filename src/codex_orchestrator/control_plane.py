from __future__ import annotations

from datetime import datetime
from pathlib import Path

from .panel import (
    PanelError,
    _load_toml,
    load_team_manifest,
    resolve_dispatch_ledger_path,
    resolve_queue_path,
)


class ControlPlaneError(RuntimeError):
    """Raised when a control-plane mutation fails."""


def _escape_toml_string(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def _render_command_block(command: dict[str, str]) -> str:
    lines = [
        "[[commands]]",
        f'id = "{_escape_toml_string(command["id"])}"',
        f'role = "{_escape_toml_string(command["role"])}"',
        f'status = "{_escape_toml_string(command["status"])}"',
        f'summary = "{_escape_toml_string(command["summary"])}"',
        f'source = "{_escape_toml_string(command["source"])}"',
        f'priority = "{_escape_toml_string(command["priority"])}"',
        f'created_at = "{_escape_toml_string(command["created_at"])}"',
    ]
    if "dispatch_id" in command:
        lines.append(f'dispatch_id = "{_escape_toml_string(command["dispatch_id"])}"')
    return "\n".join(lines)


def _render_dispatch_block(dispatch: dict[str, str]) -> str:
    lines = [
        "[[dispatches]]",
        f'id = "{_escape_toml_string(dispatch["id"])}"',
        f'command_id = "{_escape_toml_string(dispatch["command_id"])}"',
        f'role = "{_escape_toml_string(dispatch["role"])}"',
        f'status = "{_escape_toml_string(dispatch["status"])}"',
        f'created_at = "{_escape_toml_string(dispatch["created_at"])}"',
    ]
    if "result_summary" in dispatch:
        lines.append(f'result_summary = "{_escape_toml_string(dispatch["result_summary"])}"')
    return "\n".join(lines)


def _render_queue(commands: list[dict[str, str]]) -> str:
    lines = ["version = 1"]
    for command in commands:
        lines.extend(["", _render_command_block(command)])
    return "\n".join(lines) + "\n"


def _render_dispatches(dispatches: list[dict[str, str]]) -> str:
    lines = ["version = 1"]
    for dispatch in dispatches:
        lines.extend(["", _render_dispatch_block(dispatch)])
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


def _next_dispatch_id(dispatches: list[dict[str, str]]) -> str:
    max_suffix = 0
    for dispatch in dispatches:
        dispatch_id = dispatch.get("id", "")
        if not dispatch_id.startswith("dispatch-"):
            continue
        suffix = dispatch_id[9:]
        if suffix.isdigit():
            max_suffix = max(max_suffix, int(suffix))
    return f"dispatch-{max_suffix + 1:03d}"


def load_queue_commands(project_root: Path) -> list[dict[str, str]]:
    queue_path = resolve_queue_path(project_root)
    if not queue_path.exists():
        return []

    data = _load_toml(queue_path)
    raw_commands = data.get("commands")
    if not isinstance(raw_commands, list):
        return []

    commands: list[dict[str, str]] = []
    for raw_command in raw_commands:
        if not isinstance(raw_command, dict):
            continue
        command: dict[str, str] = {}
        for key in (
            "id",
            "role",
            "status",
            "summary",
            "source",
            "priority",
            "created_at",
            "dispatch_id",
        ):
            value = raw_command.get(key)
            if isinstance(value, str):
                command[key] = value
        if {"id", "role", "status", "summary", "source", "priority", "created_at"} <= command.keys():
            commands.append(command)
    return commands


def load_dispatches(project_root: Path) -> list[dict[str, str]]:
    ledger_path = resolve_dispatch_ledger_path(project_root)
    if not ledger_path.exists():
        return []

    data = _load_toml(ledger_path)
    raw_dispatches = data.get("dispatches")
    if not isinstance(raw_dispatches, list):
        return []

    dispatches: list[dict[str, str]] = []
    for raw_dispatch in raw_dispatches:
        if not isinstance(raw_dispatch, dict):
            continue
        dispatch: dict[str, str] = {}
        for key in ("id", "command_id", "role", "status", "created_at", "result_summary"):
            value = raw_dispatch.get(key)
            if isinstance(value, str):
                dispatch[key] = value
        if {"id", "command_id", "role", "status", "created_at"} <= dispatch.keys():
            dispatches.append(dispatch)
    return dispatches


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


def open_dispatch(
    *,
    project_root: Path,
    command_id: str | None = None,
) -> tuple[str, str, Path, Path]:
    queue_path = resolve_queue_path(project_root)
    ledger_path = resolve_dispatch_ledger_path(project_root)

    commands = load_queue_commands(project_root)
    if not commands:
        raise ControlPlaneError(f"queue not found or empty: {queue_path}")

    selected_command: dict[str, str] | None = None
    for command in commands:
        if command.get("status") != "pending":
            continue
        if command_id is not None and command.get("id") != command_id:
            continue
        selected_command = command
        break

    if selected_command is None:
        if command_id is not None:
            raise ControlPlaneError(f"pending command not found: {command_id}")
        raise ControlPlaneError("no pending queue command available for dispatch")

    dispatches = load_dispatches(project_root)
    dispatch_id = _next_dispatch_id(dispatches)
    dispatches.append(
        {
            "id": dispatch_id,
            "command_id": selected_command["id"],
            "role": selected_command["role"],
            "status": "ready",
            "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        }
    )

    selected_command["status"] = "claimed"
    selected_command["dispatch_id"] = dispatch_id

    queue_path.parent.mkdir(parents=True, exist_ok=True)
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    queue_path.write_text(_render_queue(commands), encoding="utf-8")
    ledger_path.write_text(_render_dispatches(dispatches), encoding="utf-8")
    return dispatch_id, selected_command["id"], queue_path, ledger_path
