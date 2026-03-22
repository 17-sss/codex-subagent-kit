from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Category:
    key: str
    title: str
    description: str


@dataclass(frozen=True)
class AgentSpec:
    key: str
    category: str
    name: str
    description: str
    model: str
    reasoning_effort: str
    sandbox_mode: str
    developer_instructions: str
    source: str = "builtin"
    definition_path: Path | None = None


@dataclass(frozen=True)
class InstallResult:
    agent_paths: list[Path]
    agent_preserved_paths: list[Path]
    scaffold_created_paths: list[Path]
    scaffold_preserved_paths: list[Path]
    orchestrator_key: str | None


@dataclass(frozen=True)
class LaunchPlan:
    backend: str
    script_path: Path
    argv: list[str]


@dataclass(frozen=True)
class TemplateInitResult:
    target_root: Path
    category_dir: Path
    readme_path: Path
    agent_path: Path
    created_paths: list[Path]
    preserved_paths: list[Path]
