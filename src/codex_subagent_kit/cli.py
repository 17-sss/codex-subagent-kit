from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .control_plane import (
    ControlPlaneError,
    apply_result,
    begin_dispatch,
    enqueue_command,
    open_dispatch,
    render_dispatch_handoff,
)
from .dashboard import DashboardError, render_role_board
from .catalog import get_agents, get_categories
from .catalog_import import CatalogImportError, import_catalog
from .doctor import render_doctor_report, run_doctor
from .generator import GenerationError, install_agents, resolve_target_dir
from .launch_runtime import LaunchError, build_launch_plan, execute_launch_plan, render_launch_preview
from .panel import PanelError, render_panel
from .templates import TemplateError, init_template
from .tui import run_tui
from .usage import UsageError, render_usage_guide


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="codex-subagent-kit",
        description=(
            "Install and manage Codex subagent definitions. "
            "Stable core: catalog, install, doctor, template, tui. "
            "Control-plane commands remain experimental."
        ),
    )
    subparsers = parser.add_subparsers(dest="command")

    catalog_parser = subparsers.add_parser("catalog", help="Print the available subagent catalog.")
    catalog_parser.add_argument("--project-root", default=".")
    catalog_parser.add_argument("--scope", choices=("project", "global"), default="project")
    catalog_parser.add_argument("--catalog-root", action="append", default=[])
    catalog_subparsers = catalog_parser.add_subparsers(dest="catalog_command")

    catalog_import_parser = catalog_subparsers.add_parser(
        "import",
        help="Persist selected external category or agent templates into a project/global catalog.",
    )
    catalog_import_parser.add_argument("--project-root", default=".")
    catalog_import_parser.add_argument("--scope", choices=("project", "global"), default="project")
    catalog_import_parser.add_argument("--catalog-root", action="append", default=[])
    catalog_import_parser.add_argument("--agents")
    catalog_import_parser.add_argument("--categories")
    catalog_import_parser.add_argument("--overwrite", action="store_true")

    install_parser = subparsers.add_parser("install", help="Install selected subagents without the TUI.")
    install_parser.add_argument("--scope", choices=("project", "global"), required=True)
    install_parser.add_argument("--agents", required=True, help="Comma-separated agent keys.")
    install_parser.add_argument("--project-root", default=".")
    install_parser.add_argument("--catalog-root", action="append", default=[])
    install_parser.add_argument("--overwrite", action="store_true")
    install_parser.add_argument(
        "--validate",
        action="store_true",
        help="Run doctor immediately after a successful install.",
    )

    doctor_parser = subparsers.add_parser(
        "doctor",
        help="Validate installed agent definitions and injected catalog roots.",
    )
    doctor_parser.add_argument("--project-root", default=".")
    doctor_parser.add_argument("--scope", choices=("project", "global"), default="project")
    doctor_parser.add_argument("--catalog-root", action="append", default=[])

    usage_parser = subparsers.add_parser(
        "usage",
        help="Render starter prompts for the installed agents visible in the selected scope.",
    )
    usage_parser.add_argument("--project-root", default=".")
    usage_parser.add_argument("--scope", choices=("project", "global"), default="project")
    usage_parser.add_argument("--task")

    panel_parser = subparsers.add_parser(
        "panel",
        help="[experimental] Render the current project control-panel topology.",
    )
    panel_parser.add_argument("--project-root", default=".")

    board_parser = subparsers.add_parser(
        "board",
        help="[experimental] Render a role-specific terminal board.",
    )
    board_parser.add_argument("--project-root", default=".")
    board_parser.add_argument("--role", required=True)

    launch_parser = subparsers.add_parser(
        "launch",
        help="[experimental] Launch a project-local terminal backend.",
    )
    launch_parser.add_argument("--project-root", default=".")
    launch_parser.add_argument("--backend", choices=("tmux", "cmux"), required=True)
    launch_parser.add_argument("--name")
    launch_parser.add_argument("--no-attach", action="store_true")
    launch_parser.add_argument("--dry-run", action="store_true")

    dispatch_prepare_parser = subparsers.add_parser(
        "dispatch-prepare",
        help="[experimental] Render the handoff package for a ready dispatch.",
    )
    dispatch_prepare_parser.add_argument("--project-root", default=".")
    dispatch_prepare_parser.add_argument("--dispatch-id", required=True)

    dispatch_begin_parser = subparsers.add_parser(
        "dispatch-begin",
        help="[experimental] Mark a ready dispatch as in-flight after the real send step.",
    )
    dispatch_begin_parser.add_argument("--project-root", default=".")
    dispatch_begin_parser.add_argument("--dispatch-id", required=True)

    enqueue_parser = subparsers.add_parser(
        "enqueue",
        help="[experimental] Enqueue an operator command into the project queue.",
    )
    enqueue_parser.add_argument("--project-root", default=".")
    enqueue_parser.add_argument("--summary", required=True)
    enqueue_parser.add_argument("--role")
    enqueue_parser.add_argument("--source", default="operator")
    enqueue_parser.add_argument("--priority", choices=("low", "normal", "high"), default="normal")

    dispatch_open_parser = subparsers.add_parser(
        "dispatch-open",
        help="[experimental] Promote a pending queue command into a dispatch ticket.",
    )
    dispatch_open_parser.add_argument("--project-root", default=".")
    dispatch_open_parser.add_argument("--command-id")

    apply_result_parser = subparsers.add_parser(
        "apply-result",
        help="[experimental] Apply a completed, failed, or cancelled result to a dispatch ticket.",
    )
    apply_result_parser.add_argument("--project-root", default=".")
    apply_result_parser.add_argument("--dispatch-id", required=True)
    apply_result_parser.add_argument("--outcome", choices=("completed", "failed", "cancelled"), required=True)
    apply_result_parser.add_argument("--summary", required=True)

    tui_parser = subparsers.add_parser("tui", help="Run the interactive TUI installer.")
    tui_parser.add_argument("--project-root", default=".")
    tui_parser.add_argument("--catalog-root", action="append", default=[])

    template_parser = subparsers.add_parser("template", help="Scaffold custom catalog templates.")
    template_subparsers = template_parser.add_subparsers(dest="template_command")

    template_init_parser = template_subparsers.add_parser(
        "init",
        help="Create a category README and agent TOML skeleton.",
    )
    template_init_parser.add_argument("--project-root", default=".")
    template_init_parser.add_argument("--scope", choices=("project", "global"), default="project")
    template_init_parser.add_argument("--catalog-root")
    template_init_parser.add_argument("--category", required=True, help="Category key, for example custom-ops.")
    template_init_parser.add_argument("--category-prefix", help="Numeric category prefix, for example 11.")
    template_init_parser.add_argument("--category-title")
    template_init_parser.add_argument("--category-description")
    template_init_parser.add_argument("--agent", required=True, help="Agent key, for example custom-coordinator.")
    template_init_parser.add_argument("--agent-name")
    template_init_parser.add_argument("--agent-description")
    template_init_parser.add_argument("--model", default="gpt-5.4")
    template_init_parser.add_argument("--reasoning-effort", default="medium")
    template_init_parser.add_argument("--sandbox-mode", default="read-only")
    template_init_parser.add_argument("--orchestrator", action="store_true")
    template_init_parser.add_argument("--overwrite", action="store_true")

    return parser


def _resolve_catalog_roots(raw_paths: list[str]) -> tuple[Path, ...]:
    return tuple(Path(path).resolve() for path in raw_paths if path.strip())


def run_catalog(args: argparse.Namespace) -> int:
    project_root = Path(args.project_root).resolve()
    include_project = args.scope == "project"
    catalog_roots = _resolve_catalog_roots(args.catalog_root)
    categories = get_categories(
        project_root=project_root,
        include_project=include_project,
        include_global=True,
        catalog_roots=catalog_roots,
    )
    agents = get_agents(
        project_root=project_root,
        include_project=include_project,
        include_global=True,
        catalog_roots=catalog_roots,
    )
    for category in categories:
        print(f"[{category.title}]")
        print(f"  key: {category.key}")
        print(f"  description: {category.description}")
        for agent in agents:
            if agent.category != category.key:
                continue
            source_suffix = f" [{agent.source}]" if agent.source != "builtin" else ""
            print(f"  - {agent.key}: {agent.description}{source_suffix}")
        print()
    return 0


def run_catalog_import(args: argparse.Namespace) -> int:
    project_root = Path(args.project_root).resolve()
    catalog_roots = _resolve_catalog_roots(args.catalog_root)
    agent_keys = [item.strip() for item in (args.agents or "").split(",") if item.strip()]
    category_keys = [item.strip() for item in (args.categories or "").split(",") if item.strip()]
    try:
        result = import_catalog(
            project_root=project_root,
            scope=args.scope,
            catalog_roots=catalog_roots,
            agent_keys=agent_keys,
            category_keys=category_keys,
            overwrite=args.overwrite,
        )
    except CatalogImportError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"target: {result.target_root}")
    if result.imported_category_keys:
        print(f"categories: {', '.join(result.imported_category_keys)}")
    if result.imported_agent_keys:
        print(f"agents: {', '.join(result.imported_agent_keys)}")
    for path in result.created_paths:
        print(f"created: {path}")
    for path in result.preserved_paths:
        print(f"preserved: {path}")
    return 0


def run_install(args: argparse.Namespace) -> int:
    project_root = Path(args.project_root).resolve()
    agent_keys = [item.strip() for item in args.agents.split(",") if item.strip()]
    catalog_roots = _resolve_catalog_roots(args.catalog_root)
    try:
        result = install_agents(
            scope=args.scope,
            project_root=project_root,
            agent_keys=agent_keys,
            catalog_roots=catalog_roots,
            overwrite=args.overwrite,
        )
    except GenerationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"target: {resolve_target_dir(args.scope, project_root)}")
    for path in result.agent_paths:
        print(path)
    for path in result.agent_preserved_paths:
        print(f"agent preserved: {path}")
    if result.orchestrator_key:
        print(f"orchestrator: {result.orchestrator_key}")
    for path in result.scaffold_created_paths:
        print(f"scaffold created: {path}")
    for path in result.scaffold_preserved_paths:
        print(f"scaffold preserved: {path}")
    if not args.validate:
        return 0

    report = run_doctor(
        project_root=project_root,
        scope=args.scope,
        catalog_roots=catalog_roots,
    )
    print()
    print(render_doctor_report(report))
    return 0 if report.ok else 1


def run_template_init(args: argparse.Namespace) -> int:
    project_root = Path(args.project_root).resolve()
    explicit_catalog_root = Path(args.catalog_root).resolve() if args.catalog_root else None
    try:
        result = init_template(
            project_root=project_root,
            scope=args.scope,
            catalog_root=explicit_catalog_root,
            category_key=args.category,
            category_prefix=args.category_prefix,
            category_title=args.category_title,
            category_description=args.category_description,
            agent_key=args.agent,
            agent_name=args.agent_name,
            agent_description=args.agent_description,
            model=args.model,
            reasoning_effort=args.reasoning_effort,
            sandbox_mode=args.sandbox_mode,
            orchestrator=args.orchestrator,
            overwrite=args.overwrite,
        )
    except TemplateError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"target: {result.target_root}")
    print(f"category: {result.category_dir}")
    print(f"agent: {result.agent_path}")
    for path in result.created_paths:
        print(f"created: {path}")
    for path in result.preserved_paths:
        print(f"preserved: {path}")
    return 0


def run_doctor_command(args: argparse.Namespace) -> int:
    project_root = Path(args.project_root).resolve()
    report = run_doctor(
        project_root=project_root,
        scope=args.scope,
        catalog_roots=_resolve_catalog_roots(args.catalog_root),
    )
    print(render_doctor_report(report))
    return 0 if report.ok else 1


def run_usage_command(args: argparse.Namespace) -> int:
    project_root = Path(args.project_root).resolve()
    try:
        print(render_usage_guide(project_root=project_root, scope=args.scope, task=args.task))
    except UsageError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


def run_panel(args: argparse.Namespace) -> int:
    project_root = Path(args.project_root).resolve()
    try:
        print(render_panel(project_root))
    except PanelError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


def run_board(args: argparse.Namespace) -> int:
    project_root = Path(args.project_root).resolve()
    try:
        print(render_role_board(project_root, args.role))
    except DashboardError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


def run_launch(args: argparse.Namespace) -> int:
    project_root = Path(args.project_root).resolve()
    try:
        plan = build_launch_plan(
            project_root=project_root,
            backend=args.backend,
            name=args.name,
            attach=not args.no_attach,
        )
    except LaunchError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.dry_run:
        print(render_launch_preview(plan))
        return 0

    try:
        return execute_launch_plan(plan, project_root=project_root)
    except LaunchError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


def run_dispatch_prepare(args: argparse.Namespace) -> int:
    project_root = Path(args.project_root).resolve()
    try:
        print(render_dispatch_handoff(project_root, dispatch_id=args.dispatch_id))
    except ControlPlaneError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


def run_dispatch_begin(args: argparse.Namespace) -> int:
    project_root = Path(args.project_root).resolve()
    try:
        dispatch_id, command_id, queue_path, ledger_path, runtime_path = begin_dispatch(
            project_root=project_root,
            dispatch_id=args.dispatch_id,
        )
    except ControlPlaneError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"queue: {queue_path}")
    print(f"ledger: {ledger_path}")
    print(f"runtime: {runtime_path}")
    print(f"command-id: {command_id}")
    print(f"dispatch-id: {dispatch_id}")
    print("status: dispatched")
    return 0


def run_enqueue(args: argparse.Namespace) -> int:
    project_root = Path(args.project_root).resolve()
    try:
        command_id, queue_path = enqueue_command(
            project_root=project_root,
            summary=args.summary,
            role=args.role,
            source=args.source,
            priority=args.priority,
        )
    except ControlPlaneError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"queue: {queue_path}")
    print(f"command-id: {command_id}")
    print(f"status: pending")
    return 0


def run_dispatch_open(args: argparse.Namespace) -> int:
    project_root = Path(args.project_root).resolve()
    try:
        dispatch_id, command_id, queue_path, ledger_path = open_dispatch(
            project_root=project_root,
            command_id=args.command_id,
        )
    except ControlPlaneError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"queue: {queue_path}")
    print(f"ledger: {ledger_path}")
    print(f"command-id: {command_id}")
    print(f"dispatch-id: {dispatch_id}")
    print("status: ready")
    return 0


def run_apply_result(args: argparse.Namespace) -> int:
    project_root = Path(args.project_root).resolve()
    try:
        dispatch_id, command_id, queue_path, ledger_path, runtime_path = apply_result(
            project_root=project_root,
            dispatch_id=args.dispatch_id,
            outcome=args.outcome,
            summary=args.summary,
        )
    except ControlPlaneError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"queue: {queue_path}")
    print(f"ledger: {ledger_path}")
    print(f"runtime: {runtime_path}")
    print(f"command-id: {command_id}")
    print(f"dispatch-id: {dispatch_id}")
    print(f"status: {args.outcome}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        return run_tui(Path(".").resolve(), catalog_roots=())

    if args.command == "catalog":
        if getattr(args, "catalog_command", None) == "import":
            return run_catalog_import(args)
        return run_catalog(args)
    if args.command == "install":
        return run_install(args)
    if args.command == "doctor":
        return run_doctor_command(args)
    if args.command == "usage":
        return run_usage_command(args)
    if args.command == "panel":
        return run_panel(args)
    if args.command == "board":
        return run_board(args)
    if args.command == "launch":
        return run_launch(args)
    if args.command == "dispatch-prepare":
        return run_dispatch_prepare(args)
    if args.command == "dispatch-begin":
        return run_dispatch_begin(args)
    if args.command == "enqueue":
        return run_enqueue(args)
    if args.command == "dispatch-open":
        return run_dispatch_open(args)
    if args.command == "apply-result":
        return run_apply_result(args)
    if args.command == "template":
        if args.template_command == "init":
            return run_template_init(args)
        parser.error("template requires a subcommand")
        return 2
    if args.command == "tui":
        return run_tui(
            Path(args.project_root).resolve(),
            catalog_roots=_resolve_catalog_roots(args.catalog_root),
        )

    parser.error(f"unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
