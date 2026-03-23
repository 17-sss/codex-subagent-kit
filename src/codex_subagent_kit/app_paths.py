from __future__ import annotations

from pathlib import Path


TOOL_NAME = "codex-subagent-kit"
TOOL_DIR_NAME = "subagent-kit"
PACKAGE_NAME = "codex_subagent_kit"
CATEGORY_OVERRIDE_KEY = "codex_subagent_kit_category"


def project_tool_dir(project_root: Path) -> Path:
    return project_root / ".codex" / TOOL_DIR_NAME


def global_tool_dir() -> Path:
    return Path.home() / ".codex" / TOOL_DIR_NAME


def resolve_project_tool_dir(project_root: Path) -> Path:
    return project_tool_dir(project_root)


def resolve_global_tool_dir() -> Path:
    return global_tool_dir()
