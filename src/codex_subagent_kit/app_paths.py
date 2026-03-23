from __future__ import annotations

from pathlib import Path


TOOL_NAME = "codex-subagent-kit"
TOOL_DIR_NAME = "subagent-kit"
LEGACY_TOOL_DIR_NAME = "orchestrator"
PACKAGE_NAME = "codex_subagent_kit"
CATEGORY_OVERRIDE_KEY = "codex_subagent_kit_category"
LEGACY_CATEGORY_OVERRIDE_KEY = "codex_orchestrator_category"


def _resolve_tool_dir(*, root: Path, legacy_root: Path) -> Path:
    if legacy_root.exists() and not root.exists():
        return legacy_root
    return root


def project_tool_dir(project_root: Path) -> Path:
    return project_root / ".codex" / TOOL_DIR_NAME


def global_tool_dir() -> Path:
    return Path.home() / ".codex" / TOOL_DIR_NAME


def legacy_project_tool_dir(project_root: Path) -> Path:
    return project_root / ".codex" / LEGACY_TOOL_DIR_NAME


def legacy_global_tool_dir() -> Path:
    return Path.home() / ".codex" / LEGACY_TOOL_DIR_NAME


def resolve_project_tool_dir(project_root: Path) -> Path:
    return _resolve_tool_dir(
        root=project_tool_dir(project_root),
        legacy_root=legacy_project_tool_dir(project_root),
    )


def resolve_global_tool_dir() -> Path:
    return _resolve_tool_dir(
        root=global_tool_dir(),
        legacy_root=legacy_global_tool_dir(),
    )
