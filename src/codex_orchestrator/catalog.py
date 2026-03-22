from __future__ import annotations

import tomllib
from functools import lru_cache
from pathlib import Path

from .models import AgentSpec, Category


BUILTIN_CATALOG_ROOT = (
    Path(__file__).resolve().parent / "builtin_catalog" / "awesome-codex-subagents"
)
BUILTIN_CATEGORIES_DIR = BUILTIN_CATALOG_ROOT / "categories"
IMPORTED_AGENTS_CATEGORY = Category(
    key="imported-agents",
    title="Imported & External",
    description="Portable TOML agent definitions discovered from project/global agent directories.",
)


EXTRA_BUILTIN_AGENTS: tuple[AgentSpec, ...] = (
    AgentSpec(
        key="cto-coordinator",
        category="meta-orchestration",
        name="cto-coordinator",
        description="Use when a parent agent must coordinate multi-repo work, preserve the critical path, and delegate bounded tasks to owner agents.",
        model="gpt-5.4",
        reasoning_effort="xhigh",
        sandbox_mode="read-only",
        developer_instructions="""Act as the coordinator for a multi-agent software team.
Own sequencing, critical-path decisions, role assignment, and result integration.
Prefer local execution for urgent blockers.
Delegate only bounded, materially useful tasks with explicit ownership and non-overlapping write scopes.
Always return:
- local vs delegated split
- per-agent objective
- dependency and wait points
- integration checklist
- top coordination risk and mitigation""",
    ),
    AgentSpec(
        key="backend-owner",
        category="core-development",
        name="backend-owner",
        description="Use when work belongs to API, service, schema, or domain logic on the backend side.",
        model="gpt-5.4",
        reasoning_effort="xhigh",
        sandbox_mode="workspace-write",
        developer_instructions="""Own backend implementation within the assigned service or module.
Preserve API contracts unless the task explicitly includes contract change.
Call out migration or compatibility risk early.
Return changed files, contract impact, and verification run.""",
    ),
    AgentSpec(
        key="frontend-owner",
        category="core-development",
        name="frontend-owner",
        description="Use when work belongs to a React or web UI surface with local ownership and validation responsibility.",
        model="gpt-5.4",
        reasoning_effort="xhigh",
        sandbox_mode="workspace-write",
        developer_instructions="""Own frontend implementation within the assigned repo or package.
Respect existing design and state-management patterns.
Do not touch backend or shared contracts unless explicitly assigned.
Return changed files, user-visible impact, and verification run.""",
    ),
    AgentSpec(
        key="core-owner",
        category="core-development",
        name="core-owner",
        description="Use when work belongs to shared core modules, schema source-of-truth, or foundational domain logic.",
        model="gpt-5.4",
        reasoning_effort="xhigh",
        sandbox_mode="workspace-write",
        developer_instructions="""Own shared core logic and schema-first changes.
Prefer source-of-truth handling over downstream patching.
Surface downstream synchronization needs explicitly.
Return changed files, downstream impact, and verification run.""",
    ),
    AgentSpec(
        key="api-owner",
        category="core-development",
        name="api-owner",
        description="Use when work belongs to an external API service, integration adapter, or infrastructure-facing application API.",
        model="gpt-5.4",
        reasoning_effort="xhigh",
        sandbox_mode="workspace-write",
        developer_instructions="""Own API-facing implementation with attention to runtime behavior, credentials, and integration contracts.
Surface operational risks early.
Return changed files, runtime impact, and verification run.""",
    ),
    AgentSpec(
        key="release-guard",
        category="quality-security",
        name="release-guard",
        description="Use when a change needs a release checklist across build, test, contracts, and runtime assumptions.",
        model="gpt-5.4",
        reasoning_effort="high",
        sandbox_mode="read-only",
        developer_instructions="""Evaluate whether a change is release-safe.
Check:
- build/test coverage
- contract drift risk
- environment assumptions
- rollback visibility
- missing release notes
Return a ship / hold recommendation with reasons.""",
    ),
    AgentSpec(
        key="platform-ops",
        category="infrastructure",
        name="platform-ops",
        description="Use when work touches runtime configuration, environment setup, scripts, containers, or deployment-facing tooling.",
        model="gpt-5.4",
        reasoning_effort="high",
        sandbox_mode="workspace-write",
        developer_instructions="""Own platform and tooling changes.
Prefer explicit, reversible changes.
Call out environment assumptions, secrets handling, and rollback path.
Return changed files, operational impact, and verification run.""",
    ),
)


def _resolve_project_agents_dir(project_root: Path) -> Path:
    return project_root / ".codex" / "agents"


def _resolve_global_agents_dir() -> Path:
    return Path.home() / ".codex" / "agents"


def _category_key_from_dir(directory_name: str) -> str:
    prefix, separator, remainder = directory_name.partition("-")
    if separator and prefix.isdigit():
        return remainder
    return directory_name


def _fallback_title_from_key(key: str) -> str:
    return " ".join(part.capitalize() for part in key.split("-"))


def _parse_builtin_category(category_dir: Path) -> Category:
    key = _category_key_from_dir(category_dir.name)
    title = _fallback_title_from_key(key)
    description = title
    readme_path = category_dir / "README.md"
    if not readme_path.exists():
        return Category(key=key, title=title, description=description)

    lines = [line.strip() for line in readme_path.read_text(encoding="utf-8").splitlines()]
    for line in lines:
        if line.startswith("#"):
            parsed_title = line.lstrip("#").strip()
            numeric_prefix, separator, remainder = parsed_title.partition(". ")
            if separator and numeric_prefix.isdigit():
                title = remainder.strip()
            elif parsed_title:
                title = parsed_title
            break

    for line in lines:
        if not line or line.startswith("#") or line == "Included agents:":
            continue
        description = line
        break

    return Category(key=key, title=title, description=description)


def _parse_external_agent(
    path: Path,
    *,
    inherited_category: str | None = None,
    source: str,
) -> AgentSpec:
    with path.open("rb") as handle:
        data = tomllib.load(handle)

    instructions: str | None = None
    developer_instructions = data.get("developer_instructions")
    if isinstance(developer_instructions, str):
        instructions = developer_instructions
    else:
        raw_instructions = data.get("instructions")
        if isinstance(raw_instructions, str):
            instructions = raw_instructions
        elif isinstance(raw_instructions, dict):
            nested_text = raw_instructions.get("text")
            instructions = nested_text if isinstance(nested_text, str) else None
    if not isinstance(instructions, str) or not instructions.strip():
        raise ValueError("missing instructions text")

    name = data.get("name")
    description = data.get("description")
    model = data.get("model")
    reasoning_effort = data.get("model_reasoning_effort")
    sandbox_mode = data.get("sandbox_mode")
    if not all(
        isinstance(value, str) and value.strip()
        for value in (name, description, model, reasoning_effort, sandbox_mode)
    ):
        raise ValueError("missing required string fields")

    category = inherited_category or data.get("codex_orchestrator_category") or "imported-agents"
    return AgentSpec(
        key=path.stem,
        category=category,
        name=name.strip(),
        description=description.strip(),
        model=model.strip(),
        reasoning_effort=reasoning_effort.strip(),
        sandbox_mode=sandbox_mode.strip(),
        developer_instructions=instructions.rstrip(),
        source=source,
        definition_path=path,
    )


@lru_cache(maxsize=1)
def _get_builtin_categories() -> tuple[Category, ...]:
    categories = [
        _parse_builtin_category(category_dir)
        for category_dir in sorted(BUILTIN_CATEGORIES_DIR.iterdir())
        if category_dir.is_dir()
    ]
    categories.append(IMPORTED_AGENTS_CATEGORY)
    return tuple(categories)


@lru_cache(maxsize=1)
def _get_builtin_agents() -> tuple[AgentSpec, ...]:
    loaded: dict[str, AgentSpec] = {}

    for category_dir in sorted(BUILTIN_CATEGORIES_DIR.iterdir()):
        if not category_dir.is_dir():
            continue
        category_key = _category_key_from_dir(category_dir.name)
        for path in sorted(category_dir.glob("*.toml")):
            try:
                agent = _parse_external_agent(
                    path,
                    inherited_category=category_key,
                    source="builtin",
                )
            except (OSError, ValueError, tomllib.TOMLDecodeError) as exc:
                raise RuntimeError(f"invalid vendored builtin agent at {path}: {exc}") from exc
            loaded[agent.key] = agent

    for agent in EXTRA_BUILTIN_AGENTS:
        loaded[agent.key] = agent

    category_order = {
        category.key: index for index, category in enumerate(_get_builtin_categories())
    }
    return tuple(
        sorted(
            loaded.values(),
            key=lambda agent: (
                category_order.get(agent.category, len(category_order)),
                agent.name.lower(),
                agent.key,
            ),
        )
    )


def _load_external_agents(
    *,
    directory: Path,
    source: str,
    builtins: dict[str, AgentSpec],
) -> list[AgentSpec]:
    if not directory.exists():
        return []

    loaded: list[AgentSpec] = []
    for path in sorted(directory.glob("*.toml")):
        inherited_category = builtins.get(path.stem).category if path.stem in builtins else None
        try:
            loaded.append(_parse_external_agent(path, inherited_category=inherited_category, source=source))
        except (OSError, ValueError, tomllib.TOMLDecodeError):
            continue
    return loaded


def get_agent_map(
    *,
    project_root: Path | None = None,
    include_project: bool = False,
    include_global: bool = False,
) -> dict[str, AgentSpec]:
    agent_map = {agent.key: agent for agent in _get_builtin_agents()}

    if include_global:
        for agent in _load_external_agents(
            directory=_resolve_global_agents_dir(),
            source="global",
            builtins=agent_map,
        ):
            agent_map[agent.key] = agent

    if include_project and project_root is not None:
        for agent in _load_external_agents(
            directory=_resolve_project_agents_dir(project_root),
            source="project",
            builtins=agent_map,
        ):
            agent_map[agent.key] = agent

    return agent_map


def get_agents(
    *,
    project_root: Path | None = None,
    include_project: bool = False,
    include_global: bool = False,
) -> tuple[AgentSpec, ...]:
    agent_map = get_agent_map(
        project_root=project_root,
        include_project=include_project,
        include_global=include_global,
    )
    category_order = {
        category.key: index for index, category in enumerate(_get_builtin_categories())
    }
    return tuple(
        sorted(
            agent_map.values(),
            key=lambda agent: (
                category_order.get(agent.category, len(category_order)),
                agent.name.lower(),
                agent.key,
            ),
        )
    )


def get_categories(
    *,
    project_root: Path | None = None,
    include_project: bool = False,
    include_global: bool = False,
) -> tuple[Category, ...]:
    used_categories = {
        agent.category
        for agent in get_agents(
            project_root=project_root,
            include_project=include_project,
            include_global=include_global,
        )
    }
    return tuple(category for category in _get_builtin_categories() if category.key in used_categories)


def get_agents_by_category(
    category_keys: set[str] | None = None,
    *,
    project_root: Path | None = None,
    include_project: bool = False,
    include_global: bool = False,
) -> list[AgentSpec]:
    agents = list(
        get_agents(
            project_root=project_root,
            include_project=include_project,
            include_global=include_global,
        )
    )
    if not category_keys:
        return agents
    return [agent for agent in agents if agent.category in category_keys]
