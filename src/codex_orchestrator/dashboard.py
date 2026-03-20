from __future__ import annotations

from pathlib import Path

from .control_plane import ControlPlaneError, load_dispatches, load_queue_commands, load_runtime_agents
from .panel import PanelError, load_team_manifest


class DashboardError(RuntimeError):
    """Raised when a terminal board cannot be rendered."""


def render_role_board(project_root: Path, role: str) -> str:
    try:
        operator_label, orchestrator_key, worker_keys = load_team_manifest(project_root)
    except PanelError as exc:
        raise DashboardError(str(exc)) from exc

    requested_role = role.strip()
    valid_roles = {orchestrator_key, *worker_keys}
    if requested_role not in valid_roles:
        raise DashboardError(f"unknown role for this team: {requested_role}")

    try:
        orchestrator_state, worker_states = load_runtime_agents(project_root)
    except ControlPlaneError as exc:
        raise DashboardError(str(exc)) from exc

    runtime_map = {orchestrator_state["key"]: orchestrator_state}
    runtime_map.update({worker_state["key"]: worker_state for worker_state in worker_states})
    role_state = runtime_map[requested_role]

    role_commands = [command for command in load_queue_commands(project_root) if command["role"] == requested_role]
    role_dispatches = [dispatch for dispatch in load_dispatches(project_root) if dispatch["role"] == requested_role]

    role_kind = "orchestrator" if requested_role == orchestrator_key else "worker"
    lines = [
        f"Role: {requested_role}",
        f"Kind: {role_kind}",
        f"Operator: {operator_label}",
        f"Status: {role_state['status']}",
        f"Active Dispatch: {role_state.get('active_dispatch_id', '-')}",
        "",
        "Queue Commands",
    ]

    if role_commands:
        for command in role_commands:
            lines.append(f"- {command['id']} [{command['status']}] {command['summary']}")
    else:
        lines.append("- none")

    lines.extend(["", "Dispatches"])
    if role_dispatches:
        for dispatch in role_dispatches:
            suffix = f" <- {dispatch['command_id']}"
            if "result_summary" in dispatch:
                suffix += f": {dispatch['result_summary']}"
            lines.append(f"- {dispatch['id']} [{dispatch['status']}] {suffix}")
    else:
        lines.append("- none")

    return "\n".join(lines)
