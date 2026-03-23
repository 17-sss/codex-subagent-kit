from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path

from .catalog import (
    BUILTIN_CATEGORIES_DIR,
    IMPORTED_AGENTS_CATEGORY,
    _parse_agent_file,
    _parse_category_dir,
    normalize_catalog_roots,
    resolve_global_agents_dir,
    resolve_global_catalog_dir,
    resolve_project_agents_dir,
    resolve_project_catalog_dir,
)
from .generator import resolve_target_dir
from .models import AgentSpec, Category


@dataclass(frozen=True)
class DoctorIssue:
    path: Path | None
    message: str


@dataclass(frozen=True)
class DoctorReport:
    scope: str
    target_dir: Path
    catalog_counts: list[tuple[str, int]]
    installed_counts: list[tuple[str, int]]
    issues: list[DoctorIssue]

    @property
    def ok(self) -> bool:
        return not self.issues


def _scan_catalog_root(
    root: Path,
    *,
    source: str,
    missing_is_issue: bool = False,
) -> tuple[dict[str, Category], dict[str, AgentSpec], list[DoctorIssue], int]:
    if not root.exists():
        issues = [DoctorIssue(root, "catalog root does not exist")] if missing_is_issue else []
        return {}, {}, issues, 0

    categories: dict[str, Category] = {}
    agents: dict[str, AgentSpec] = {}
    issues: list[DoctorIssue] = []
    checked_templates = 0

    for category_dir in sorted(root.iterdir()):
        if not category_dir.is_dir():
            continue
        category = _parse_category_dir(category_dir)
        categories[category.key] = category
        for path in sorted(category_dir.glob("*.toml")):
            checked_templates += 1
            try:
                agent = _parse_agent_file(path, inherited_category=category.key, source=source)
            except (OSError, ValueError, tomllib.TOMLDecodeError) as exc:
                issues.append(DoctorIssue(path, str(exc)))
                continue
            agents[agent.key] = agent

    return categories, agents, issues, checked_templates


def _scan_installed_agents(
    directory: Path,
    *,
    source: str,
    inherited_agents: dict[str, AgentSpec],
) -> tuple[list[AgentSpec], list[DoctorIssue], int]:
    if not directory.exists():
        return [], [], 0

    agents: list[AgentSpec] = []
    issues: list[DoctorIssue] = []
    checked_files = 0

    for path in sorted(directory.glob("*.toml")):
        checked_files += 1
        inherited_category = inherited_agents.get(path.stem).category if path.stem in inherited_agents else None
        try:
            agent = _parse_agent_file(path, inherited_category=inherited_category, source=source)
        except (OSError, ValueError, tomllib.TOMLDecodeError) as exc:
            issues.append(DoctorIssue(path, str(exc)))
            continue
        agents.append(agent)

    return agents, issues, checked_files


def run_doctor(
    *,
    project_root: Path,
    scope: str,
    catalog_roots: tuple[Path, ...] = (),
) -> DoctorReport:
    normalized_catalog_roots = normalize_catalog_roots(catalog_roots)

    catalog_counts: list[tuple[str, int]] = []
    installed_counts: list[tuple[str, int]] = []
    issues: list[DoctorIssue] = []

    categories, agent_map, builtin_issues, builtin_checked = _scan_catalog_root(
        BUILTIN_CATEGORIES_DIR,
        source="builtin",
    )
    issues.extend(builtin_issues)
    catalog_counts.append(("built-in", builtin_checked))

    if scope == "project":
        global_categories, global_agents, global_issues, global_checked = _scan_catalog_root(
            resolve_global_catalog_dir(),
            source="global-catalog",
        )
        categories.update(global_categories)
        agent_map.update(global_agents)
        issues.extend(global_issues)
        catalog_counts.append(("global catalog", global_checked))

        project_categories, project_agents, project_issues, project_checked = _scan_catalog_root(
            resolve_project_catalog_dir(project_root),
            source="project-catalog",
        )
        categories.update(project_categories)
        agent_map.update(project_agents)
        issues.extend(project_issues)
        catalog_counts.append(("project catalog", project_checked))
    else:
        global_categories, global_agents, global_issues, global_checked = _scan_catalog_root(
            resolve_global_catalog_dir(),
            source="global-catalog",
        )
        categories.update(global_categories)
        agent_map.update(global_agents)
        issues.extend(global_issues)
        catalog_counts.append(("global catalog", global_checked))

    for root in normalized_catalog_roots:
        extra_categories, extra_agents, extra_issues, extra_checked = _scan_catalog_root(
            root,
            source="catalog-root",
            missing_is_issue=True,
        )
        categories.update(extra_categories)
        agent_map.update(extra_agents)
        issues.extend(extra_issues)
        catalog_counts.append((f"catalog root: {root}", extra_checked))

    categories[IMPORTED_AGENTS_CATEGORY.key] = IMPORTED_AGENTS_CATEGORY
    del categories

    global_installed, global_installed_issues, global_installed_checked = _scan_installed_agents(
        resolve_global_agents_dir(),
        source="global",
        inherited_agents=agent_map,
    )
    issues.extend(global_installed_issues)

    if scope == "project":
        installed_counts.append(("global agents", global_installed_checked))
        for agent in global_installed:
            agent_map[agent.key] = agent

        project_installed_dir = resolve_project_agents_dir(project_root)
        project_installed, project_installed_issues, project_installed_checked = _scan_installed_agents(
            project_installed_dir,
            source="project",
            inherited_agents=agent_map,
        )
        issues.extend(project_installed_issues)
        installed_counts.append(("project agents", project_installed_checked))

        target_dir = resolve_target_dir("project", project_root)
        if project_installed_checked == 0:
            issues.append(DoctorIssue(target_dir, "no installed agent definitions found in target scope"))
    else:
        installed_counts.append(("global agents", global_installed_checked))
        target_dir = resolve_target_dir("global", project_root)
        if global_installed_checked == 0:
            issues.append(DoctorIssue(target_dir, "no installed agent definitions found in target scope"))

    return DoctorReport(
        scope=scope,
        target_dir=target_dir,
        catalog_counts=catalog_counts,
        installed_counts=installed_counts,
        issues=issues,
    )


def render_doctor_report(report: DoctorReport) -> str:
    lines = [
        f"status: {'ok' if report.ok else 'issues found'}",
        f"scope: {report.scope}",
        f"target: {report.target_dir}",
        "",
        "Catalog templates checked:",
    ]
    for label, count in report.catalog_counts:
        lines.append(f"- {label}: {count}")

    lines.append("")
    lines.append("Installed agent files checked:")
    for label, count in report.installed_counts:
        lines.append(f"- {label}: {count}")

    lines.append("")
    if report.issues:
        lines.append("Issues:")
        for issue in report.issues:
            if issue.path is None:
                lines.append(f"- {issue.message}")
            else:
                lines.append(f"- {issue.path}: {issue.message}")
    else:
        lines.append("Issues: none")

    return "\n".join(lines)
