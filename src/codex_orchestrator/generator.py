from __future__ import annotations

from pathlib import Path

from .catalog import get_agent_map
from .models import AgentSpec


class GenerationError(RuntimeError):
    """Raised when agent generation fails."""


def resolve_target_dir(scope: str, project_root: Path) -> Path:
    if scope == "project":
        return project_root / ".codex" / "agents"
    if scope == "global":
        return Path.home() / ".codex" / "agents"
    raise GenerationError(f"unsupported scope: {scope}")


def render_agent_file(agent: AgentSpec) -> str:
    return f"""name = "{agent.name}"
description = "{agent.description}"
model = "{agent.model}"
model_reasoning_effort = "{agent.reasoning_effort}"
sandbox_mode = "{agent.sandbox_mode}"
developer_instructions = \"\"\"
{agent.developer_instructions}
\"\"\"
"""


def install_agents(
    *,
    scope: str,
    project_root: Path,
    agent_keys: list[str],
    overwrite: bool = False,
) -> list[Path]:
    agent_map = get_agent_map()
    missing = [key for key in agent_keys if key not in agent_map]
    if missing:
        raise GenerationError(f"unknown agent keys: {', '.join(missing)}")

    target_dir = resolve_target_dir(scope, project_root)
    target_dir.mkdir(parents=True, exist_ok=True)

    created_paths: list[Path] = []
    for key in agent_keys:
        agent = agent_map[key]
        file_path = target_dir / f"{agent.key}.toml"
        if file_path.exists() and not overwrite:
            raise GenerationError(f"target already exists: {file_path}")

        file_path.write_text(render_agent_file(agent), encoding="utf-8")
        created_paths.append(file_path)

    return created_paths
