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


@dataclass(frozen=True)
class InstallResult:
    agent_paths: list[Path]
    agent_preserved_paths: list[Path]
    scaffold_created_paths: list[Path]
    scaffold_preserved_paths: list[Path]
    orchestrator_key: str | None
