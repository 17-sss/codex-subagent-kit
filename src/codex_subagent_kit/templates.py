from __future__ import annotations

import json
import re
from pathlib import Path

from .app_paths import CATEGORY_OVERRIDE_KEY
from .catalog import resolve_global_catalog_dir, resolve_project_catalog_dir
from .generator import ORCHESTRATOR_CATEGORY
from .models import TemplateInitResult


SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
DEFAULT_MODEL = "gpt-5.4"
DEFAULT_REASONING_EFFORT = "medium"
DEFAULT_SANDBOX_MODE = "read-only"


class TemplateError(RuntimeError):
    """Raised when template scaffolding fails."""


def _validate_slug(value: str, *, field_name: str) -> str:
    normalized = value.strip().lower()
    if not SLUG_PATTERN.fullmatch(normalized):
        raise TemplateError(
            f"{field_name} must be a lowercase slug using letters, numbers, and hyphens"
        )
    return normalized


def _title_from_slug(value: str) -> str:
    return " ".join(part.capitalize() for part in value.split("-"))


def _category_key_from_dir(directory_name: str) -> str:
    prefix, separator, remainder = directory_name.partition("-")
    if separator and prefix.isdigit():
        return remainder
    return directory_name


def _normalize_prefix(prefix: str | None) -> str | None:
    if prefix is None:
        return None
    stripped = prefix.strip()
    if not stripped:
        return None
    if not stripped.isdigit():
        raise TemplateError("category prefix must be numeric")
    return stripped.zfill(2)


def _next_prefix(root: Path) -> str:
    numeric_prefixes: list[int] = []
    if root.exists():
        for child in root.iterdir():
            if not child.is_dir():
                continue
            prefix, separator, _ = child.name.partition("-")
            if separator and prefix.isdigit():
                numeric_prefixes.append(int(prefix))
    return str(max(numeric_prefixes, default=10) + 1).zfill(2)


def _ensure_directory(path: Path, *, created_paths: list[Path], preserved_paths: list[Path]) -> None:
    if path.exists():
        if not path.is_dir():
            raise TemplateError(f"expected directory but found file: {path}")
        preserved_paths.append(path)
        return

    path.mkdir(parents=True, exist_ok=False)
    created_paths.append(path)


def _write_file(
    path: Path,
    content: str,
    *,
    overwrite: bool,
    created_paths: list[Path],
    preserved_paths: list[Path],
) -> None:
    if path.exists() and not overwrite:
        if path.is_dir():
            raise TemplateError(f"expected file but found directory: {path}")
        preserved_paths.append(path)
        return

    path.write_text(content, encoding="utf-8")
    created_paths.append(path)


def _resolve_target_root(*, project_root: Path, scope: str, catalog_root: Path | None) -> Path:
    if catalog_root is not None:
        return catalog_root.resolve()
    if scope == "project":
        return resolve_project_catalog_dir(project_root)
    if scope == "global":
        return resolve_global_catalog_dir()
    raise TemplateError(f"unsupported scope: {scope}")


def _resolve_category_dir(root: Path, *, category_key: str, category_prefix: str | None) -> tuple[Path, str]:
    if root.exists():
        for child in sorted(root.iterdir()):
            if child.is_dir() and _category_key_from_dir(child.name) == category_key:
                prefix, separator, _ = child.name.partition("-")
                return child, prefix if separator and prefix.isdigit() else ""

    effective_prefix = category_prefix or _next_prefix(root)
    return root / f"{effective_prefix}-{category_key}", effective_prefix


def render_category_readme(
    *,
    category_title: str,
    category_description: str,
    category_prefix: str,
) -> str:
    heading_number = f"{int(category_prefix)}. " if category_prefix else ""
    return f"""# {heading_number}{category_title}

{category_description}
"""


def render_agent_template(
    *,
    agent_key: str,
    agent_name: str,
    agent_description: str,
    model: str,
    reasoning_effort: str,
    sandbox_mode: str,
    category_override: str | None,
) -> str:
    lines = [
        f"name = {json.dumps(agent_name)}",
        f"description = {json.dumps(agent_description)}",
        f"model = {json.dumps(model)}",
        f"model_reasoning_effort = {json.dumps(reasoning_effort)}",
        f"sandbox_mode = {json.dumps(sandbox_mode)}",
        'developer_instructions = """',
        f"You are `{agent_key}`.",
        "",
        "Responsibilities:",
        "- TODO: define the primary ownership boundary.",
        "- TODO: define what inputs to expect.",
        "- TODO: define what outputs to return.",
        "",
        "Constraints:",
        "- Stay within the assigned scope.",
        "- Escalate when requirements are ambiguous or cross ownership boundaries.",
        '"""',
    ]
    if category_override:
        lines.append(f"{CATEGORY_OVERRIDE_KEY} = {json.dumps(category_override)}")
    return "\n".join(lines) + "\n"


def init_template(
    *,
    project_root: Path,
    scope: str,
    category_key: str,
    agent_key: str,
    catalog_root: Path | None = None,
    category_prefix: str | None = None,
    category_title: str | None = None,
    category_description: str | None = None,
    agent_name: str | None = None,
    agent_description: str | None = None,
    model: str = DEFAULT_MODEL,
    reasoning_effort: str = DEFAULT_REASONING_EFFORT,
    sandbox_mode: str = DEFAULT_SANDBOX_MODE,
    orchestrator: bool = False,
    overwrite: bool = False,
) -> TemplateInitResult:
    normalized_category_key = _validate_slug(category_key, field_name="category key")
    normalized_agent_key = _validate_slug(agent_key, field_name="agent key")
    normalized_prefix = _normalize_prefix(category_prefix)

    target_root = _resolve_target_root(
        project_root=project_root,
        scope=scope,
        catalog_root=catalog_root,
    )

    created_paths: list[Path] = []
    preserved_paths: list[Path] = []
    _ensure_directory(target_root, created_paths=created_paths, preserved_paths=preserved_paths)

    category_dir, resolved_prefix = _resolve_category_dir(
        target_root,
        category_key=normalized_category_key,
        category_prefix=normalized_prefix,
    )
    _ensure_directory(category_dir, created_paths=created_paths, preserved_paths=preserved_paths)

    resolved_category_title = (category_title or _title_from_slug(normalized_category_key)).strip()
    resolved_category_description = (
        category_description
        or f"Custom templates for the {resolved_category_title.lower()} workflow."
    ).strip()
    resolved_agent_name = (agent_name or normalized_agent_key).strip()
    resolved_agent_description = (
        agent_description or f"TODO: describe when to use {normalized_agent_key}."
    ).strip()

    readme_path = category_dir / "README.md"
    _write_file(
        readme_path,
        render_category_readme(
            category_title=resolved_category_title,
            category_description=resolved_category_description,
            category_prefix=resolved_prefix,
        ),
        overwrite=overwrite,
        created_paths=created_paths,
        preserved_paths=preserved_paths,
    )

    category_override = ORCHESTRATOR_CATEGORY if orchestrator else None
    if normalized_category_key == ORCHESTRATOR_CATEGORY:
        category_override = None

    agent_path = category_dir / f"{normalized_agent_key}.toml"
    _write_file(
        agent_path,
        render_agent_template(
            agent_key=normalized_agent_key,
            agent_name=resolved_agent_name,
            agent_description=resolved_agent_description,
            model=model.strip(),
            reasoning_effort=reasoning_effort.strip(),
            sandbox_mode=sandbox_mode.strip(),
            category_override=category_override,
        ),
        overwrite=overwrite,
        created_paths=created_paths,
        preserved_paths=preserved_paths,
    )

    return TemplateInitResult(
        target_root=target_root,
        category_dir=category_dir,
        readme_path=readme_path,
        agent_path=agent_path,
        created_paths=created_paths,
        preserved_paths=preserved_paths,
    )
