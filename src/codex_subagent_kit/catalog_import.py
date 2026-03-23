from __future__ import annotations

import shutil
import tomllib
from dataclasses import dataclass
from pathlib import Path

from .catalog import (
    _parse_agent_file,
    _parse_category_dir,
    normalize_catalog_roots,
    resolve_global_catalog_dir,
    resolve_project_catalog_dir,
)


class CatalogImportError(RuntimeError):
    """Raised when importing external catalog content fails."""


@dataclass(frozen=True)
class CatalogImportResult:
    target_root: Path
    imported_category_keys: list[str]
    imported_agent_keys: list[str]
    created_paths: list[Path]
    preserved_paths: list[Path]


@dataclass(frozen=True)
class _CategorySource:
    key: str
    directory: Path
    readme_path: Path | None


@dataclass(frozen=True)
class _AgentSource:
    key: str
    path: Path
    category_key: str
    category_directory: Path
    readme_path: Path | None


def _category_key_from_dir(directory_name: str) -> str:
    prefix, separator, remainder = directory_name.partition("-")
    if separator and prefix.isdigit():
        return remainder
    return directory_name


def _resolve_target_root(*, project_root: Path, scope: str) -> Path:
    if scope == "project":
        return resolve_project_catalog_dir(project_root)
    if scope == "global":
        return resolve_global_catalog_dir()
    raise CatalogImportError(f"unsupported scope: {scope}")


def _parse_csv(raw_value: str | None) -> list[str]:
    if raw_value is None:
        return []
    return [item.strip() for item in raw_value.split(",") if item.strip()]


def _resolve_target_category_dir(target_root: Path, source_category_dir: Path) -> Path:
    source_key = _category_key_from_dir(source_category_dir.name)
    if target_root.exists():
        for child in sorted(target_root.iterdir()):
            if child.is_dir() and _category_key_from_dir(child.name) == source_key:
                return child
    return target_root / source_category_dir.name


def _ensure_directory(path: Path, *, created_paths: list[Path], preserved_paths: list[Path]) -> None:
    if path.exists():
        if not path.is_dir():
            raise CatalogImportError(f"expected directory but found file: {path}")
        preserved_paths.append(path)
        return

    path.mkdir(parents=True, exist_ok=False)
    created_paths.append(path)


def _copy_file(
    source: Path,
    destination: Path,
    *,
    overwrite: bool,
    created_paths: list[Path],
    preserved_paths: list[Path],
) -> None:
    if destination.exists() and not overwrite:
        if destination.is_dir():
            raise CatalogImportError(f"expected file but found directory: {destination}")
        preserved_paths.append(destination)
        return

    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    created_paths.append(destination)


def _scan_source_roots(
    catalog_roots: tuple[Path, ...],
) -> tuple[dict[str, _CategorySource], dict[str, _AgentSource]]:
    normalized_roots = normalize_catalog_roots(catalog_roots)
    if not normalized_roots:
        raise CatalogImportError("catalog import requires at least one --catalog-root")

    categories: dict[str, _CategorySource] = {}
    agents: dict[str, _AgentSource] = {}
    issues: list[str] = []

    for root in normalized_roots:
        if not root.exists():
            raise CatalogImportError(f"catalog root does not exist: {root}")

        for category_dir in sorted(root.iterdir()):
            if not category_dir.is_dir():
                continue

            category = _parse_category_dir(category_dir)
            readme_path = category_dir / "README.md"
            categories[category.key] = _CategorySource(
                key=category.key,
                directory=category_dir,
                readme_path=readme_path if readme_path.exists() else None,
            )
            for path in sorted(category_dir.glob("*.toml")):
                try:
                    agent = _parse_agent_file(path, inherited_category=category.key, source="catalog-root")
                except (OSError, ValueError, tomllib.TOMLDecodeError) as exc:
                    issues.append(f"{path}: {exc}")
                    continue
                agents[agent.key] = _AgentSource(
                    key=agent.key,
                    path=path,
                    category_key=category.key,
                    category_directory=category_dir,
                    readme_path=readme_path if readme_path.exists() else None,
                )

    if issues:
        rendered = "\n".join(f"- {issue}" for issue in issues)
        raise CatalogImportError(f"source catalog contains malformed templates:\n{rendered}")

    return categories, agents


def import_catalog(
    *,
    project_root: Path,
    scope: str,
    catalog_roots: tuple[Path, ...],
    agent_keys: list[str],
    category_keys: list[str],
    overwrite: bool = False,
) -> CatalogImportResult:
    if not agent_keys and not category_keys:
        raise CatalogImportError("catalog import requires --agents, --categories, or both")

    categories, agents = _scan_source_roots(catalog_roots)

    missing_categories = [key for key in category_keys if key not in categories]
    if missing_categories:
        raise CatalogImportError(f"unknown category keys: {', '.join(missing_categories)}")

    missing_agents = [key for key in agent_keys if key not in agents]
    if missing_agents:
        raise CatalogImportError(f"unknown agent keys: {', '.join(missing_agents)}")

    target_root = _resolve_target_root(project_root=project_root, scope=scope)
    created_paths: list[Path] = []
    preserved_paths: list[Path] = []
    _ensure_directory(target_root, created_paths=created_paths, preserved_paths=preserved_paths)

    selected_categories: set[str] = set(category_keys)
    selected_agents: set[str] = set(agent_keys)
    copy_plan: dict[Path, Path] = {}

    for category_key in category_keys:
        category_source = categories[category_key]
        target_category_dir = _resolve_target_category_dir(target_root, category_source.directory)
        _ensure_directory(target_category_dir, created_paths=created_paths, preserved_paths=preserved_paths)
        if category_source.readme_path is not None:
            copy_plan[category_source.readme_path] = target_category_dir / "README.md"
        for agent_source in agents.values():
            if agent_source.category_directory != category_source.directory:
                continue
            selected_agents.add(agent_source.key)
            copy_plan[agent_source.path] = target_category_dir / agent_source.path.name

    for agent_key in agent_keys:
        agent_source = agents[agent_key]
        selected_categories.add(agent_source.category_key)
        target_category_dir = _resolve_target_category_dir(target_root, agent_source.category_directory)
        _ensure_directory(target_category_dir, created_paths=created_paths, preserved_paths=preserved_paths)
        if agent_source.readme_path is not None:
            copy_plan[agent_source.readme_path] = target_category_dir / "README.md"
        copy_plan[agent_source.path] = target_category_dir / agent_source.path.name

    for source, destination in sorted(copy_plan.items(), key=lambda item: str(item[1])):
        _copy_file(
            source,
            destination,
            overwrite=overwrite,
            created_paths=created_paths,
            preserved_paths=preserved_paths,
        )

    return CatalogImportResult(
        target_root=target_root,
        imported_category_keys=sorted(selected_categories),
        imported_agent_keys=sorted(selected_agents),
        created_paths=created_paths,
        preserved_paths=preserved_paths,
    )
