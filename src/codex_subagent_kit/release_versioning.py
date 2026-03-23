from __future__ import annotations

import re
from typing import Iterable


SEMVER_PATTERN = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
BREAKING_SUBJECT_PATTERN = re.compile(r"^[a-zA-Z]+(?:\([^)]+\))?!:")
FEATURE_SUBJECT_PATTERN = re.compile(r"^feat(?:\([^)]+\))?:")


def parse_semver(value: str) -> tuple[int, int, int]:
    match = SEMVER_PATTERN.fullmatch(value.strip())
    if not match:
        raise ValueError(f"invalid semantic version: {value}")
    return tuple(int(part) for part in match.groups())


def bump_semver(version: str, bump: str) -> str:
    major, minor, patch = parse_semver(version)
    if bump == "major":
        return f"{major + 1}.0.0"
    if bump == "minor":
        return f"{major}.{minor + 1}.0"
    if bump == "patch":
        return f"{major}.{minor}.{patch + 1}"
    raise ValueError(f"unsupported bump kind: {bump}")


def classify_bump(commit_messages: Iterable[str]) -> str:
    normalized = [message.strip() for message in commit_messages if message.strip()]
    if not normalized:
        return "patch"

    for message in normalized:
        subject = message.splitlines()[0].strip()
        if "BREAKING CHANGE:" in message or BREAKING_SUBJECT_PATTERN.match(subject):
            return "major"

    for message in normalized:
        subject = message.splitlines()[0].strip()
        if FEATURE_SUBJECT_PATTERN.match(subject):
            return "minor"

    return "patch"


def compute_next_version(base_version: str, commit_messages: Iterable[str]) -> str:
    return bump_semver(base_version, classify_bump(commit_messages))
