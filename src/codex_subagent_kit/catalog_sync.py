from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

from .app_paths import (
    DEFAULT_SYNC_SOURCE_NAME,
    resolve_global_source_categories_dir,
    resolve_project_source_categories_dir,
)


VOLTAGENT_TREE_API_URL = (
    "https://api.github.com/repos/VoltAgent/awesome-codex-subagents/git/trees/main?recursive=1"
)
VOLTAGENT_RAW_BASE_URL = "https://raw.githubusercontent.com/VoltAgent/awesome-codex-subagents/main/"
SYNCABLE_SUFFIXES = (".toml", "README.md")


class CatalogSyncError(RuntimeError):
    """Raised when catalog sync cannot complete."""


@dataclass(frozen=True)
class CatalogSyncResult:
    source_name: str
    target_root: Path
    source_label: str
    copied_paths: list[Path]


def _normalize_source_name(source_name: str) -> str:
    candidate = source_name.strip().lower()
    if not candidate:
        raise CatalogSyncError("catalog sync requires a non-empty source name")
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", candidate):
        raise CatalogSyncError("source names may contain only lowercase letters, digits, hyphens, and underscores")
    return candidate


def _resolve_categories_root(source_root: Path) -> Path:
    root = source_root.resolve()
    if root.is_dir() and root.name == "categories":
        return root
    nested = root / "categories"
    if nested.is_dir():
        return nested
    raise CatalogSyncError(f"expected a categories/ directory but found: {source_root}")


def _prepare_target_root(target_root: Path) -> None:
    target_root.parent.mkdir(parents=True, exist_ok=True)
    if target_root.exists():
        shutil.rmtree(target_root)
    target_root.mkdir(parents=True, exist_ok=True)


def _iter_relative_catalog_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if path.name == "README.md" or path.suffix == ".toml":
            files.append(path.relative_to(root))
    return files


def _copy_local_source(*, source_root: Path, target_root: Path) -> list[Path]:
    categories_root = _resolve_categories_root(source_root)
    copied_paths: list[Path] = []
    for relative_path in _iter_relative_catalog_files(categories_root):
        source_path = categories_root / relative_path
        destination = target_root / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, destination)
        copied_paths.append(destination)
    return copied_paths


def _fetch_json(url: str) -> dict[str, object]:
    request = Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "codex-subagent-kit",
        },
    )
    try:
        with urlopen(request) as response:
            return json.load(response)
    except URLError as exc:
        raise CatalogSyncError(f"failed to fetch upstream catalog metadata: {exc}") from exc


def _fetch_text(url: str) -> str:
    request = Request(url, headers={"User-Agent": "codex-subagent-kit"})
    try:
        with urlopen(request) as response:
            return response.read().decode("utf-8")
    except URLError as exc:
        raise CatalogSyncError(f"failed to fetch upstream catalog file: {url}") from exc


def _download_voltagent_source(*, target_root: Path) -> list[Path]:
    payload = _fetch_json(VOLTAGENT_TREE_API_URL)
    tree = payload.get("tree")
    if not isinstance(tree, list):
        raise CatalogSyncError("unexpected upstream catalog metadata payload")

    catalog_paths: list[str] = []
    for entry in tree:
        if not isinstance(entry, dict):
            continue
        path = entry.get("path")
        if not isinstance(path, str) or not path.startswith("categories/"):
            continue
        if path.endswith(".toml") or path.endswith("README.md"):
            catalog_paths.append(path)

    if not catalog_paths:
        raise CatalogSyncError("upstream catalog did not expose any categories files")

    copied_paths: list[Path] = []
    for upstream_path in sorted(catalog_paths):
        relative_path = Path(upstream_path).relative_to("categories")
        destination = target_root / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            _fetch_text(f"{VOLTAGENT_RAW_BASE_URL}{upstream_path}"),
            encoding="utf-8",
        )
        copied_paths.append(destination)
    return copied_paths


def sync_catalog(
    *,
    project_root: Path,
    scope: str,
    source_name: str = DEFAULT_SYNC_SOURCE_NAME,
    source_root: Path | None = None,
) -> CatalogSyncResult:
    normalized_source_name = _normalize_source_name(source_name)

    if scope == "project":
        target_root = resolve_project_source_categories_dir(project_root, normalized_source_name)
    elif scope == "global":
        target_root = resolve_global_source_categories_dir(normalized_source_name)
    else:
        raise CatalogSyncError(f"unsupported scope: {scope}")

    _prepare_target_root(target_root)
    if source_root is not None:
        copied_paths = _copy_local_source(source_root=source_root, target_root=target_root)
        source_label = str(_resolve_categories_root(source_root))
    else:
        if normalized_source_name != DEFAULT_SYNC_SOURCE_NAME:
            raise CatalogSyncError(
                "remote sync is only supported for the default voltagent source without --source-root"
            )
        copied_paths = _download_voltagent_source(target_root=target_root)
        source_label = "VoltAgent/awesome-codex-subagents@main"

    if not copied_paths:
        raise CatalogSyncError("catalog sync did not copy any README or TOML files")

    return CatalogSyncResult(
        source_name=normalized_source_name,
        target_root=target_root,
        source_label=source_label,
        copied_paths=copied_paths,
    )
