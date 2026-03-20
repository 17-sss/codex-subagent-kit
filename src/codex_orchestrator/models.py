from __future__ import annotations

from dataclasses import dataclass


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

