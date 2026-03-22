from __future__ import annotations

import tomllib
from pathlib import Path

from .models import AgentSpec, Category


CATEGORIES: tuple[Category, ...] = (
    Category(
        key="meta-orchestration",
        title="Meta & Orchestration",
        description="Coordinator, task routing, parallel work planning.",
    ),
    Category(
        key="code-understanding",
        title="Code Understanding",
        description="Code mapping, docs research, architecture reading.",
    ),
    Category(
        key="product-engineering",
        title="Product Engineering",
        description="Project-specific implementation owners across frontend/backend/core/api.",
    ),
    Category(
        key="quality-safety",
        title="Quality & Safety",
        description="Review, release validation, regression checks.",
    ),
    Category(
        key="platform-ops",
        title="Platform & Ops",
        description="Infra, runtime, debugging, deployment-facing tasks.",
    ),
    Category(
        key="imported-agents",
        title="Imported & External",
        description="Portable TOML agent definitions discovered from project/global agent directories.",
    ),
)


AGENTS: tuple[AgentSpec, ...] = (
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
        key="task-distributor",
        category="meta-orchestration",
        name="task-distributor",
        description="Use when a large implementation or review task needs to be split into safe, disjoint sub-tasks.",
        model="gpt-5.4",
        reasoning_effort="high",
        sandbox_mode="read-only",
        developer_instructions="""Break a parent task into parallelizable sub-tasks.
Optimize for disjoint ownership, low merge conflict risk, and clear output contracts.
Do not write code. Produce an execution plan with:
- task slices
- suggested owner type
- dependencies
- validation checkpoints""",
    ),
    AgentSpec(
        key="code-mapper",
        category="code-understanding",
        name="code-mapper",
        description="Use when a developer needs a fast structural read of a codebase slice before changing it.",
        model="gpt-5.4",
        reasoning_effort="high",
        sandbox_mode="read-only",
        developer_instructions="""Map the relevant code paths for the requested task.
Prioritize:
- entry points
- data flow
- ownership boundaries
- risky coupling
- likely test surface
Return concise file references and a recommended read order.""",
    ),
    AgentSpec(
        key="docs-researcher",
        category="code-understanding",
        name="docs-researcher",
        description="Use when implementation depends on external library or platform docs and the parent agent needs concise primary-source guidance.",
        model="gpt-5.4",
        reasoning_effort="high",
        sandbox_mode="read-only",
        developer_instructions="""Research primary documentation and extract implementation-relevant guidance.
Prefer official docs and standards.
Return:
- exact concept summary
- key constraints
- minimal implementation checklist
- source links""",
    ),
    AgentSpec(
        key="reviewer",
        category="quality-safety",
        name="reviewer",
        description="Use when changes need a correctness, regression, and risk-focused code review.",
        model="gpt-5.4",
        reasoning_effort="high",
        sandbox_mode="read-only",
        developer_instructions="""Review code with a bug-finding mindset.
Focus on behavioral regressions, security risks, missing validation, and test gaps.
Return findings first, ordered by severity, with file references.
Do not rewrite the code unless explicitly asked.""",
    ),
    AgentSpec(
        key="release-guard",
        category="quality-safety",
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
        key="frontend-owner",
        category="product-engineering",
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
        key="backend-owner",
        category="product-engineering",
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
        key="core-owner",
        category="product-engineering",
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
        category="product-engineering",
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
        key="browser-debugger",
        category="platform-ops",
        name="browser-debugger",
        description="Use when a web flow needs runtime reproduction, browser inspection, or interaction-level debugging.",
        model="gpt-5.4",
        reasoning_effort="high",
        sandbox_mode="workspace-write",
        developer_instructions="""Reproduce browser-visible issues and gather concrete evidence.
Focus on:
- reproduction steps
- console/network symptoms
- likely failing component or endpoint
- smallest next fix candidate
Return evidence before hypotheses.""",
    ),
    AgentSpec(
        key="platform-ops",
        category="platform-ops",
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


def _parse_external_agent(
    path: Path,
    *,
    inherited_category: str | None = None,
    source: str,
) -> AgentSpec:
    with path.open("rb") as handle:
        data = tomllib.load(handle)

    raw_instructions = data.get("instructions")
    instructions: str | None
    if isinstance(raw_instructions, str):
        instructions = raw_instructions
    elif isinstance(raw_instructions, dict):
        nested_text = raw_instructions.get("text")
        instructions = nested_text if isinstance(nested_text, str) else None
    else:
        instructions = None
    if instructions is None:
        legacy_instructions = data.get("developer_instructions")
        instructions = legacy_instructions if isinstance(legacy_instructions, str) else None
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
    agent_map = {agent.key: agent for agent in AGENTS}

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
    category_order = {category.key: index for index, category in enumerate(CATEGORIES)}
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
    return tuple(category for category in CATEGORIES if category.key in used_categories)


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
