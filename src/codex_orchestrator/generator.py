from __future__ import annotations

from pathlib import Path

from .catalog import get_agent_map
from .launchers import (
    render_cmux_launcher,
    render_run_board_script,
    render_run_monitor_script,
    render_tmux_launcher,
)
from .models import AgentSpec, InstallResult


class GenerationError(RuntimeError):
    """Raised when agent generation fails."""


ORCHESTRATOR_CATEGORY = "meta-orchestration"
DEFAULT_ORCHESTRATOR_KEY = "cto-coordinator"


def resolve_target_dir(scope: str, project_root: Path) -> Path:
    if scope == "project":
        return project_root / ".codex" / "agents"
    if scope == "global":
        return Path.home() / ".codex" / "agents"
    raise GenerationError(f"unsupported scope: {scope}")


def resolve_scaffold_dir(project_root: Path) -> Path:
    return project_root / ".codex" / "orchestrator"


def render_agent_file(agent: AgentSpec) -> str:
    instructions_text = agent.developer_instructions.rstrip()
    return f"""name = "{agent.name}"
description = "{agent.description}"
model = "{agent.model}"
model_reasoning_effort = "{agent.reasoning_effort}"
sandbox_mode = "{agent.sandbox_mode}"
instructions = \"\"\"
{instructions_text}
\"\"\"
"""


def _render_string_list(items: list[str]) -> str:
    return "[" + ", ".join(f'"{item}"' for item in items) + "]"


def render_team_manifest(*, orchestrator_key: str, worker_keys: list[str]) -> str:
    return f"""version = 1

[operator]
label = "user"

[team]
orchestrator = "{orchestrator_key}"
workers = {_render_string_list(worker_keys)}

[control_panel]
topology = "operator-orchestrator-workers"
"""


def render_runtime_state(*, orchestrator_key: str, worker_keys: list[str]) -> str:
    worker_blocks = "\n".join(
        f'[[workers]]\nkey = "{worker_key}"\nstatus = "idle"\n'
        for worker_key in worker_keys
    )
    if worker_blocks:
        worker_blocks = "\n" + worker_blocks.rstrip() + "\n"
    return f"""version = 1

[orchestrator]
key = "{orchestrator_key}"
status = "idle"
{worker_blocks}"""


def render_queue_seed() -> str:
    return """version = 1
"""


def render_dispatch_ledger_seed() -> str:
    return """version = 1
"""


def render_scaffold_readme(*, orchestrator_key: str, worker_keys: list[str]) -> str:
    worker_summary = ", ".join(f"`{worker_key}`" for worker_key in worker_keys) or "none yet"
    return f"""# orchestrator scaffold

This folder is the project-local seed for the future control-plane.

## Team topology

- operator/user
- root orchestrator: `{orchestrator_key}`
- workers: {worker_summary}

## Notes

- `.codex/agents/` keeps static agent definitions.
- `.codex/orchestrator/` keeps team and runtime-oriented assets.
- `runtime/agents.toml` tracks orchestrator/worker runtime status.
- `queue/commands.toml` is the queue seed for future operator commands.
- `ledger/dispatches.toml` is the dispatch ledger seed.
"""


def resolve_orchestrator_key(agent_keys: list[str]) -> str:
    agent_map = get_agent_map()
    candidates = sorted(
        key for key in agent_keys if agent_map[key].category == ORCHESTRATOR_CATEGORY
    )
    if not candidates:
        raise GenerationError(
            "project installs require at least one meta-orchestration agent for the root orchestrator"
        )
    if DEFAULT_ORCHESTRATOR_KEY in candidates:
        return DEFAULT_ORCHESTRATOR_KEY
    return candidates[0]


def _ensure_directory(path: Path, *, created_paths: list[Path], preserved_paths: list[Path]) -> None:
    if path.exists():
        if not path.is_dir():
            raise GenerationError(f"expected directory but found file: {path}")
        preserved_paths.append(path)
        return

    path.mkdir(parents=True, exist_ok=False)
    created_paths.append(path)


def _write_seed_file(
    path: Path,
    content: str,
    *,
    created_paths: list[Path],
    preserved_paths: list[Path],
    executable: bool = False,
) -> None:
    if path.exists():
        if path.is_dir():
            raise GenerationError(f"expected file but found directory: {path}")
        preserved_paths.append(path)
        return

    path.write_text(content, encoding="utf-8")
    if executable:
        path.chmod(0o755)
    created_paths.append(path)


def generate_orchestrator_scaffold(*, project_root: Path, agent_keys: list[str]) -> tuple[str, list[Path], list[Path]]:
    orchestrator_key = resolve_orchestrator_key(agent_keys)
    worker_keys = [key for key in sorted(agent_keys) if key != orchestrator_key]

    scaffold_root = resolve_scaffold_dir(project_root)
    created_paths: list[Path] = []
    preserved_paths: list[Path] = []

    _ensure_directory(scaffold_root, created_paths=created_paths, preserved_paths=preserved_paths)
    _ensure_directory(scaffold_root / "runtime", created_paths=created_paths, preserved_paths=preserved_paths)
    _ensure_directory(scaffold_root / "queue", created_paths=created_paths, preserved_paths=preserved_paths)
    _ensure_directory(scaffold_root / "ledger", created_paths=created_paths, preserved_paths=preserved_paths)
    _ensure_directory(scaffold_root / "launchers", created_paths=created_paths, preserved_paths=preserved_paths)

    _write_seed_file(
        scaffold_root / "team.toml",
        render_team_manifest(orchestrator_key=orchestrator_key, worker_keys=worker_keys),
        created_paths=created_paths,
        preserved_paths=preserved_paths,
    )
    _write_seed_file(
        scaffold_root / "README.md",
        render_scaffold_readme(orchestrator_key=orchestrator_key, worker_keys=worker_keys),
        created_paths=created_paths,
        preserved_paths=preserved_paths,
    )
    _write_seed_file(
        scaffold_root / "runtime" / "agents.toml",
        render_runtime_state(orchestrator_key=orchestrator_key, worker_keys=worker_keys),
        created_paths=created_paths,
        preserved_paths=preserved_paths,
    )
    _write_seed_file(
        scaffold_root / "queue" / "commands.toml",
        render_queue_seed(),
        created_paths=created_paths,
        preserved_paths=preserved_paths,
    )
    _write_seed_file(
        scaffold_root / "ledger" / "dispatches.toml",
        render_dispatch_ledger_seed(),
        created_paths=created_paths,
        preserved_paths=preserved_paths,
    )
    _write_seed_file(
        scaffold_root / "launchers" / "run-board.sh",
        render_run_board_script(project_root=project_root),
        created_paths=created_paths,
        preserved_paths=preserved_paths,
        executable=True,
    )
    _write_seed_file(
        scaffold_root / "launchers" / "run-monitor.sh",
        render_run_monitor_script(project_root=project_root),
        created_paths=created_paths,
        preserved_paths=preserved_paths,
        executable=True,
    )
    _write_seed_file(
        scaffold_root / "launchers" / "launch-tmux.sh",
        render_tmux_launcher(
            project_root=project_root,
            orchestrator_key=orchestrator_key,
            worker_keys=worker_keys,
        ),
        created_paths=created_paths,
        preserved_paths=preserved_paths,
        executable=True,
    )
    _write_seed_file(
        scaffold_root / "launchers" / "launch-cmux.sh",
        render_cmux_launcher(
            project_root=project_root,
            orchestrator_key=orchestrator_key,
            worker_keys=worker_keys,
        ),
        created_paths=created_paths,
        preserved_paths=preserved_paths,
        executable=True,
    )

    return orchestrator_key, created_paths, preserved_paths


def install_agents(
    *,
    scope: str,
    project_root: Path,
    agent_keys: list[str],
    overwrite: bool = False,
) -> InstallResult:
    agent_map = get_agent_map(
        project_root=project_root,
        include_project=(scope == "project"),
        include_global=True,
    )
    missing = [key for key in agent_keys if key not in agent_map]
    if missing:
        raise GenerationError(f"unknown agent keys: {', '.join(missing)}")

    target_dir = resolve_target_dir(scope, project_root)
    target_dir.mkdir(parents=True, exist_ok=True)

    created_paths: list[Path] = []
    preserved_agent_paths: list[Path] = []
    for key in agent_keys:
        agent = agent_map[key]
        file_path = target_dir / f"{agent.key}.toml"
        if file_path.exists() and not overwrite:
            preserved_agent_paths.append(file_path)
            continue
        file_path.write_text(render_agent_file(agent), encoding="utf-8")
        created_paths.append(file_path)

    scaffold_created_paths: list[Path] = []
    scaffold_preserved_paths: list[Path] = []
    orchestrator_key: str | None = None
    if scope == "project":
        orchestrator_key, scaffold_created_paths, scaffold_preserved_paths = generate_orchestrator_scaffold(
            project_root=project_root,
            agent_keys=agent_keys,
        )

    return InstallResult(
        agent_paths=created_paths,
        agent_preserved_paths=preserved_agent_paths,
        scaffold_created_paths=scaffold_created_paths,
        scaffold_preserved_paths=scaffold_preserved_paths,
        orchestrator_key=orchestrator_key,
    )
