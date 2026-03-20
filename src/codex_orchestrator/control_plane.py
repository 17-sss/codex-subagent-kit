from __future__ import annotations

from datetime import datetime
from pathlib import Path

from .catalog import get_agent_map
from .panel import (
    PanelError,
    _load_toml,
    _load_optional_toml,
    load_team_manifest,
    resolve_dispatch_ledger_path,
    resolve_queue_path,
    resolve_runtime_state_path,
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


def _render_runtime_agent_block(header: str, agent: dict[str, str]) -> list[str]:
    lines = [
        header,
        f'key = "{_escape_toml_string(agent["key"])}"',
        f'status = "{_escape_toml_string(agent["status"])}"',
    ]
    active_dispatch_id = agent.get("active_dispatch_id")
    if active_dispatch_id:
        lines.append(f'active_dispatch_id = "{_escape_toml_string(active_dispatch_id)}"')
    return lines


def _render_runtime_state(orchestrator: dict[str, str], workers: list[dict[str, str]]) -> str:
    lines = ["version = 1", ""]
    lines.extend(_render_runtime_agent_block("[orchestrator]", orchestrator))
    for worker in workers:
        lines.extend(["", *_render_runtime_agent_block("[[workers]]", worker)])
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


def _find_dispatch_record(dispatches: list[dict[str, str]], dispatch_id: str) -> dict[str, str]:
    for dispatch in dispatches:
        if dispatch["id"] == dispatch_id:
            return dispatch
    raise ControlPlaneError(f"dispatch not found: {dispatch_id}")


def _find_command_for_dispatch(
    commands: list[dict[str, str]],
    dispatch: dict[str, str],
) -> dict[str, str]:
    for command in commands:
        if command.get("dispatch_id") == dispatch["id"] or command["id"] == dispatch["command_id"]:
            return command
    raise ControlPlaneError(f"queue command not found for dispatch: {dispatch['id']}")


def _resolve_role_context(project_root: Path, role: str) -> tuple[str, str, str]:
    try:
        operator_label, orchestrator_key, worker_keys = load_team_manifest(project_root)
    except PanelError as exc:
        raise ControlPlaneError(str(exc)) from exc

    if role == orchestrator_key:
        return operator_label, orchestrator_key, "orchestrator"
    if role in set(worker_keys):
        return operator_label, orchestrator_key, "worker"
    raise ControlPlaneError(f"unknown role for this team: {role}")


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


def load_runtime_agents(project_root: Path) -> tuple[dict[str, str], list[dict[str, str]]]:
    try:
        _, orchestrator_key, worker_keys = load_team_manifest(project_root)
    except PanelError as exc:
        raise ControlPlaneError(str(exc)) from exc

    data = _load_optional_toml(resolve_runtime_state_path(project_root))
    orchestrator_state = {
        "key": orchestrator_key,
        "status": "idle",
    }
    worker_states = [{"key": worker_key, "status": "idle"} for worker_key in worker_keys]

    raw_orchestrator = data.get("orchestrator")
    if isinstance(raw_orchestrator, dict):
        if isinstance(raw_orchestrator.get("status"), str) and raw_orchestrator["status"].strip():
            orchestrator_state["status"] = raw_orchestrator["status"].strip()
        if isinstance(raw_orchestrator.get("active_dispatch_id"), str) and raw_orchestrator[
            "active_dispatch_id"
        ].strip():
            orchestrator_state["active_dispatch_id"] = raw_orchestrator["active_dispatch_id"].strip()

    worker_index = {worker["key"]: worker for worker in worker_states}
    raw_workers = data.get("workers")
    if isinstance(raw_workers, list):
        for raw_worker in raw_workers:
            if not isinstance(raw_worker, dict):
                continue
            key = raw_worker.get("key")
            if not isinstance(key, str) or key not in worker_index:
                continue
            worker_state = worker_index[key]
            status = raw_worker.get("status")
            if isinstance(status, str) and status.strip():
                worker_state["status"] = status.strip()
            active_dispatch_id = raw_worker.get("active_dispatch_id")
            if isinstance(active_dispatch_id, str) and active_dispatch_id.strip():
                worker_state["active_dispatch_id"] = active_dispatch_id.strip()

    return orchestrator_state, worker_states


def render_dispatch_handoff(project_root: Path, *, dispatch_id: str) -> str:
    dispatches = load_dispatches(project_root)
    target_dispatch = _find_dispatch_record(dispatches, dispatch_id)
    if target_dispatch["status"] not in {"ready", "dispatched"}:
        raise ControlPlaneError(f"dispatch is not handoff-ready: {dispatch_id}")

    commands = load_queue_commands(project_root)
    target_command = _find_command_for_dispatch(commands, target_dispatch)

    role = target_dispatch["role"]
    operator_label, orchestrator_key, role_kind = _resolve_role_context(project_root, role)
    agent_map = get_agent_map(
        project_root=project_root,
        include_project=True,
        include_global=True,
    )
    agent = agent_map.get(role)
    if agent is None:
        raise ControlPlaneError(f"agent definition not found for role: {role}")

    role_definition = str(agent.definition_path) if agent.definition_path is not None else "(builtin catalog)"
    role_label = "root orchestrator" if role_kind == "orchestrator" else "worker"
    lines = [
        "[dispatch]",
        target_dispatch["id"],
        "",
        "[brief]",
        f"operator: {operator_label}",
        f"role: {role}",
        f"role-kind: {role_kind}",
        f"dispatch-status: {target_dispatch['status']}",
        f"command-id: {target_command['id']}",
        f"priority: {target_command.get('priority', 'normal')}",
        f"source: {target_command.get('source', 'operator')}",
        f"project-root: {project_root}",
        f"role-definition: {role_definition}",
        f"role-description: {agent.description}",
        "",
        "[suggested send_input message]",
        f"You own the `{role}` {role_label} role for this project-local codex-orchestrator team.",
        f"Operator: {operator_label}",
        f"Root orchestrator: {orchestrator_key}",
        f"Project root: {project_root}",
        f"Role definition: {role_definition}",
        f"Role description: {agent.description}",
        f"Dispatch id: {target_dispatch['id']}",
        f"Command id: {target_command['id']}",
        f"Priority: {target_command.get('priority', 'normal')}",
        f"Source: {target_command.get('source', 'operator')}",
        "",
        "New command:",
        target_command["summary"],
        "",
        "Reply with:",
        "- what you checked or changed",
        "- blockers or contract mismatches",
        "- files touched and verification run",
    ]
    return "\n".join(lines)


def _write_runtime_agents(
    project_root: Path,
    *,
    orchestrator_state: dict[str, str],
    worker_states: list[dict[str, str]],
) -> Path:
    runtime_path = resolve_runtime_state_path(project_root)
    runtime_path.parent.mkdir(parents=True, exist_ok=True)
    runtime_path.write_text(
        _render_runtime_state(orchestrator_state, worker_states),
        encoding="utf-8",
    )
    return runtime_path


def _set_role_runtime_state(
    project_root: Path,
    *,
    role_key: str,
    status: str,
    active_dispatch_id: str | None,
) -> Path:
    orchestrator_state, worker_states = load_runtime_agents(project_root)
    if orchestrator_state["key"] == role_key:
        orchestrator_state["status"] = status
        if active_dispatch_id is None:
            orchestrator_state.pop("active_dispatch_id", None)
        else:
            orchestrator_state["active_dispatch_id"] = active_dispatch_id
        return _write_runtime_agents(
            project_root,
            orchestrator_state=orchestrator_state,
            worker_states=worker_states,
        )

    for worker_state in worker_states:
        if worker_state["key"] != role_key:
            continue
        worker_state["status"] = status
        if active_dispatch_id is None:
            worker_state.pop("active_dispatch_id", None)
        else:
            worker_state["active_dispatch_id"] = active_dispatch_id
        return _write_runtime_agents(
            project_root,
            orchestrator_state=orchestrator_state,
            worker_states=worker_states,
        )

    raise ControlPlaneError(f"runtime role not found: {role_key}")


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
    _set_role_runtime_state(
        project_root,
        role_key=selected_command["role"],
        status="busy",
        active_dispatch_id=dispatch_id,
    )
    return dispatch_id, selected_command["id"], queue_path, ledger_path


def begin_dispatch(
    *,
    project_root: Path,
    dispatch_id: str,
) -> tuple[str, str, Path, Path, Path]:
    dispatches = load_dispatches(project_root)
    target_dispatch = _find_dispatch_record(dispatches, dispatch_id)
    if target_dispatch["status"] != "ready":
        raise ControlPlaneError(f"dispatch is not ready: {dispatch_id}")

    commands = load_queue_commands(project_root)
    target_command = _find_command_for_dispatch(commands, target_dispatch)

    target_dispatch["status"] = "dispatched"
    target_command["status"] = "dispatched"

    queue_path = resolve_queue_path(project_root)
    ledger_path = resolve_dispatch_ledger_path(project_root)
    queue_path.write_text(_render_queue(commands), encoding="utf-8")
    ledger_path.write_text(_render_dispatches(dispatches), encoding="utf-8")

    runtime_path = _set_role_runtime_state(
        project_root,
        role_key=target_dispatch["role"],
        status="busy",
        active_dispatch_id=dispatch_id,
    )
    return dispatch_id, target_command["id"], queue_path, ledger_path, runtime_path


def apply_result(
    *,
    project_root: Path,
    dispatch_id: str,
    outcome: str,
    summary: str,
) -> tuple[str, str, Path, Path, Path]:
    if outcome not in {"completed", "failed", "cancelled"}:
        raise ControlPlaneError(f"unsupported outcome: {outcome}")

    summary_text = summary.strip()
    if not summary_text:
        raise ControlPlaneError("summary must not be empty")

    dispatches = load_dispatches(project_root)
    target_dispatch = _find_dispatch_record(dispatches, dispatch_id)
    if target_dispatch["status"] not in {"ready", "dispatched"}:
        raise ControlPlaneError(f"dispatch is not active: {dispatch_id}")

    commands = load_queue_commands(project_root)
    target_command = _find_command_for_dispatch(commands, target_dispatch)

    target_dispatch["status"] = outcome
    target_dispatch["result_summary"] = summary_text
    target_command["status"] = outcome

    queue_path = resolve_queue_path(project_root)
    ledger_path = resolve_dispatch_ledger_path(project_root)
    queue_path.write_text(_render_queue(commands), encoding="utf-8")
    ledger_path.write_text(_render_dispatches(dispatches), encoding="utf-8")

    runtime_status = "blocked" if outcome == "failed" else "idle"
    runtime_path = _set_role_runtime_state(
        project_root,
        role_key=target_dispatch["role"],
        status=runtime_status,
        active_dispatch_id=None,
    )
    return dispatch_id, target_command["id"], queue_path, ledger_path, runtime_path
