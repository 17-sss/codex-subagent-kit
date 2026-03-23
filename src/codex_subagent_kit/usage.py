from __future__ import annotations

from pathlib import Path

from .catalog import get_agents
from .generator import DEFAULT_ORCHESTRATOR_KEY, ORCHESTRATOR_CATEGORY


class UsageError(RuntimeError):
    """Raised when usage guidance cannot be rendered."""


def _visible_installed_agents(*, project_root: Path, scope: str):
    include_project = scope == "project"
    agents = get_agents(
        project_root=project_root,
        include_project=include_project,
        include_global=True,
    )
    visible = [agent for agent in agents if agent.source in {"project", "global"}]
    if not visible:
        raise UsageError("no installed agents were found for the selected scope")
    return visible


def _starter_prompt(*, task: str, orchestrator_key: str | None, worker_keys: list[str]) -> str:
    if orchestrator_key:
        if worker_keys:
            worker_list = ", ".join(worker_keys)
            return (
                f'Use {orchestrator_key} as the root orchestrator for this task: "{task}". '
                f"Delegate to {worker_list} when appropriate."
            )
        return f'Use {orchestrator_key} for this task: "{task}".'

    if worker_keys:
        worker_list = ", ".join(worker_keys)
        return f'For this task: "{task}", use these installed agents as needed: {worker_list}.'

    raise UsageError("no installed agents were found for the selected scope")


def render_usage_guide(*, project_root: Path, scope: str, task: str | None = None) -> str:
    visible_agents = _visible_installed_agents(project_root=project_root, scope=scope)
    task_text = (task or "<describe the task here>").strip()

    orchestrators = [agent for agent in visible_agents if agent.category == ORCHESTRATOR_CATEGORY]
    orchestrator_key: str | None = None
    if orchestrators:
        preferred = next((agent for agent in orchestrators if agent.key == DEFAULT_ORCHESTRATOR_KEY), None)
        orchestrator_key = (preferred or orchestrators[0]).key

    worker_keys = [agent.key for agent in visible_agents if agent.key != orchestrator_key]

    lines = [
        f"scope: {scope}",
        "visible installed agents:",
    ]
    for agent in visible_agents:
        lines.append(f"- {agent.key} [{agent.source}] - {agent.description}")

    lines.extend(
        [
            "",
            "starter prompt:",
            _starter_prompt(
                task=task_text,
                orchestrator_key=orchestrator_key,
                worker_keys=worker_keys,
            ),
            "",
            "direct prompt ideas:",
        ]
    )
    for agent in visible_agents[:6]:
        lines.append(f'- Use {agent.key} for this task: "{task_text}". Focus on: {agent.description}')

    lines.extend(
        [
            "",
            "session tip:",
            "- If Codex spawns a subagent thread, use /agent to inspect or continue that thread.",
        ]
    )
    return "\n".join(lines)
