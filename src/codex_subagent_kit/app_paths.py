from __future__ import annotations

from pathlib import Path


TOOL_NAME = "codex-subagent-kit"
TOOL_DIR_NAME = "subagent-kit"
PACKAGE_NAME = "codex_subagent_kit"
CATEGORY_OVERRIDE_KEY = "codex_subagent_kit_category"
DEFAULT_SYNC_SOURCE_NAME = "voltagent"


def project_tool_dir(project_root: Path) -> Path:
    return project_root / ".codex" / TOOL_DIR_NAME


def global_tool_dir() -> Path:
    return Path.home() / ".codex" / TOOL_DIR_NAME


def resolve_project_tool_dir(project_root: Path) -> Path:
    return project_tool_dir(project_root)


def resolve_global_tool_dir() -> Path:
    return global_tool_dir()


def resolve_project_catalog_dir(project_root: Path) -> Path:
    return resolve_project_tool_dir(project_root) / "catalog" / "categories"


def resolve_global_catalog_dir() -> Path:
    return resolve_global_tool_dir() / "catalog" / "categories"


def resolve_project_sources_dir(project_root: Path) -> Path:
    return resolve_project_tool_dir(project_root) / "sources"


def resolve_global_sources_dir() -> Path:
    return resolve_global_tool_dir() / "sources"


def resolve_project_source_categories_dir(
    project_root: Path,
    source_name: str = DEFAULT_SYNC_SOURCE_NAME,
) -> Path:
    return resolve_project_sources_dir(project_root) / source_name / "categories"


def resolve_global_source_categories_dir(
    source_name: str = DEFAULT_SYNC_SOURCE_NAME,
) -> Path:
    return resolve_global_sources_dir() / source_name / "categories"


def _resolve_source_category_dirs(root: Path) -> tuple[Path, ...]:
    if not root.exists():
        return ()

    discovered: list[Path] = []
    for source_dir in sorted(root.iterdir()):
        if not source_dir.is_dir():
            continue
        categories_dir = source_dir / "categories"
        if categories_dir.is_dir():
            discovered.append(categories_dir)
    return tuple(discovered)


def resolve_project_source_categories_dirs(project_root: Path) -> tuple[Path, ...]:
    return _resolve_source_category_dirs(resolve_project_sources_dir(project_root))


def resolve_global_source_categories_dirs() -> tuple[Path, ...]:
    return _resolve_source_category_dirs(resolve_global_sources_dir())
