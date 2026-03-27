from __future__ import annotations

import tomllib
from functools import lru_cache
from pathlib import Path

from .app_paths import (
    CATEGORY_OVERRIDE_KEY,
    resolve_global_catalog_dir,
    resolve_global_source_categories_dirs,
    resolve_project_catalog_dir,
    resolve_project_source_categories_dirs,
)
from .models import AgentSpec, Category


BUILTIN_CATEGORIES_DIR = Path(__file__).resolve().parent / "builtin_catalog" / "categories"
IMPORTED_AGENTS_CATEGORY = Category(
    key="imported-agents",
    title="Imported & External",
    description="Portable TOML agent definitions discovered from project/global agent directories.",
)


def resolve_project_agents_dir(project_root: Path) -> Path:
    return project_root / ".codex" / "agents"


def resolve_global_agents_dir() -> Path:
    return Path.home() / ".codex" / "agents"


def normalize_catalog_roots(catalog_roots: tuple[Path, ...] | None = None) -> tuple[Path, ...]:
    if not catalog_roots:
        return ()
    return tuple(root.resolve() for root in catalog_roots)


def _category_key_from_dir(directory_name: str) -> str:
    prefix, separator, remainder = directory_name.partition("-")
    if separator and prefix.isdigit():
        return remainder
    return directory_name


def _fallback_title_from_key(key: str) -> str:
    return " ".join(part.capitalize() for part in key.split("-"))


def _parse_category_dir(category_dir: Path) -> Category:
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


def _parse_agent_file(
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

    explicit_category = data.get(CATEGORY_OVERRIDE_KEY)
    if explicit_category is not None and (not isinstance(explicit_category, str) or not explicit_category.strip()):
        raise ValueError(f"invalid {CATEGORY_OVERRIDE_KEY}")

    category = (
        explicit_category.strip()
        if isinstance(explicit_category, str) and explicit_category.strip()
        else inherited_category or IMPORTED_AGENTS_CATEGORY.key
    )
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


def _load_catalog_root(
    root: Path,
    *,
    source: str,
) -> tuple[dict[str, Category], dict[str, AgentSpec]]:
    if not root.exists():
        return {}, {}

    categories: dict[str, Category] = {}
    agents: dict[str, AgentSpec] = {}
    for category_dir in sorted(root.iterdir()):
        if not category_dir.is_dir():
            continue
        category = _parse_category_dir(category_dir)
        categories[category.key] = category
        for path in sorted(category_dir.glob("*.toml")):
            agent = _parse_agent_file(path, inherited_category=category.key, source=source)
            agents[agent.key] = agent
    return categories, agents


@lru_cache(maxsize=1)
def _get_builtin_catalog() -> tuple[dict[str, Category], dict[str, AgentSpec]]:
    categories, agents = _load_catalog_root(BUILTIN_CATEGORIES_DIR, source="builtin")
    if not categories:
        raise RuntimeError(f"builtin catalog is empty: {BUILTIN_CATEGORIES_DIR}")
    return categories, agents


def _load_external_agents(
    *,
    directory: Path,
    source: str,
    inherited_agents: dict[str, AgentSpec],
) -> list[AgentSpec]:
    if not directory.exists():
        return []

    loaded: list[AgentSpec] = []
    for path in sorted(directory.glob("*.toml")):
        inherited_category = inherited_agents.get(path.stem).category if path.stem in inherited_agents else None
        try:
            loaded.append(_parse_agent_file(path, inherited_category=inherited_category, source=source))
        except (OSError, ValueError, tomllib.TOMLDecodeError):
            continue
    return loaded


def _merge_catalog_roots(
    *,
    project_root: Path | None,
    include_project: bool,
    include_global: bool,
    catalog_roots: tuple[Path, ...],
) -> tuple[dict[str, Category], dict[str, AgentSpec]]:
    builtin_categories, builtin_agents = _get_builtin_catalog()
    categories: dict[str, Category] = dict(builtin_categories)
    agents: dict[str, AgentSpec] = dict(builtin_agents)

    if include_global:
        for root in resolve_global_source_categories_dirs():
            extra_categories, extra_agents = _load_catalog_root(
                root,
                source=f"global-source:{root.parent.name}",
            )
            categories.update(extra_categories)
            agents.update(extra_agents)

        extra_categories, extra_agents = _load_catalog_root(
            resolve_global_catalog_dir(),
            source="global-catalog",
        )
        categories.update(extra_categories)
        agents.update(extra_agents)

    if include_project and project_root is not None:
        for root in resolve_project_source_categories_dirs(project_root):
            extra_categories, extra_agents = _load_catalog_root(
                root,
                source=f"project-source:{root.parent.name}",
            )
            categories.update(extra_categories)
            agents.update(extra_agents)

        extra_categories, extra_agents = _load_catalog_root(
            resolve_project_catalog_dir(project_root),
            source="project-catalog",
        )
        categories.update(extra_categories)
        agents.update(extra_agents)

    for root in catalog_roots:
        extra_categories, extra_agents = _load_catalog_root(root, source="catalog-root")
        categories.update(extra_categories)
        agents.update(extra_agents)

    categories[IMPORTED_AGENTS_CATEGORY.key] = IMPORTED_AGENTS_CATEGORY
    return categories, agents


def get_agent_map(
    *,
    project_root: Path | None = None,
    include_project: bool = False,
    include_global: bool = False,
    catalog_roots: tuple[Path, ...] | None = None,
) -> dict[str, AgentSpec]:
    normalized_catalog_roots = normalize_catalog_roots(catalog_roots)
    categories, agent_map = _merge_catalog_roots(
        project_root=project_root,
        include_project=include_project,
        include_global=include_global,
        catalog_roots=normalized_catalog_roots,
    )
    del categories

    if include_global:
        for agent in _load_external_agents(
            directory=resolve_global_agents_dir(),
            source="global",
            inherited_agents=agent_map,
        ):
            agent_map[agent.key] = agent

    if include_project and project_root is not None:
        for agent in _load_external_agents(
            directory=resolve_project_agents_dir(project_root),
            source="project",
            inherited_agents=agent_map,
        ):
            agent_map[agent.key] = agent

    return agent_map


def get_agents(
    *,
    project_root: Path | None = None,
    include_project: bool = False,
    include_global: bool = False,
    catalog_roots: tuple[Path, ...] | None = None,
) -> tuple[AgentSpec, ...]:
    normalized_catalog_roots = normalize_catalog_roots(catalog_roots)
    categories = get_categories(
        project_root=project_root,
        include_project=include_project,
        include_global=include_global,
        catalog_roots=normalized_catalog_roots,
    )
    agent_map = get_agent_map(
        project_root=project_root,
        include_project=include_project,
        include_global=include_global,
        catalog_roots=normalized_catalog_roots,
    )
    category_order = {category.key: index for index, category in enumerate(categories)}
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
    catalog_roots: tuple[Path, ...] | None = None,
) -> tuple[Category, ...]:
    normalized_catalog_roots = normalize_catalog_roots(catalog_roots)
    categories, _ = _merge_catalog_roots(
        project_root=project_root,
        include_project=include_project,
        include_global=include_global,
        catalog_roots=normalized_catalog_roots,
    )
    used_categories = {
        agent.category
        for agent in get_agent_map(
            project_root=project_root,
            include_project=include_project,
            include_global=include_global,
            catalog_roots=normalized_catalog_roots,
        ).values()
    }
    return tuple(category for key, category in categories.items() if key in used_categories)


def get_agents_by_category(
    category_keys: set[str] | None = None,
    *,
    project_root: Path | None = None,
    include_project: bool = False,
    include_global: bool = False,
    catalog_roots: tuple[Path, ...] | None = None,
) -> list[AgentSpec]:
    agents = list(
        get_agents(
            project_root=project_root,
            include_project=include_project,
            include_global=include_global,
            catalog_roots=catalog_roots,
        )
    )
    if not category_keys:
        return agents
    return [agent for agent in agents if agent.category in category_keys]
