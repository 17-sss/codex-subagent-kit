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
from .generator import GenerationError, install_agents, resolve_target_dir
from .launch_runtime import LaunchError, build_launch_plan, execute_launch_plan, render_launch_preview
from .panel import PanelError, render_panel
from .tui import run_tui


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="codex-orchestrator")
    subparsers = parser.add_subparsers(dest="command", required=True)

    catalog_parser = subparsers.add_parser("catalog", help="Print the available subagent catalog.")
    catalog_parser.add_argument("--project-root", default=".")
    catalog_parser.add_argument("--scope", choices=("project", "global"), default="project")

    install_parser = subparsers.add_parser("install", help="Install selected subagents without the TUI.")
    install_parser.add_argument("--scope", choices=("project", "global"), required=True)
    install_parser.add_argument("--agents", required=True, help="Comma-separated agent keys.")
    install_parser.add_argument("--project-root", default=".")
    install_parser.add_argument("--overwrite", action="store_true")

    panel_parser = subparsers.add_parser("panel", help="Render the current project control-panel topology.")
    panel_parser.add_argument("--project-root", default=".")

    board_parser = subparsers.add_parser("board", help="Render a role-specific terminal board.")
    board_parser.add_argument("--project-root", default=".")
    board_parser.add_argument("--role", required=True)

    launch_parser = subparsers.add_parser("launch", help="Launch a project-local terminal backend.")
    launch_parser.add_argument("--project-root", default=".")
    launch_parser.add_argument("--backend", choices=("tmux", "cmux"), required=True)
    launch_parser.add_argument("--name")
    launch_parser.add_argument("--no-attach", action="store_true")
    launch_parser.add_argument("--dry-run", action="store_true")

    dispatch_prepare_parser = subparsers.add_parser(
        "dispatch-prepare",
        help="Render the handoff package for a ready dispatch.",
    )
    dispatch_prepare_parser.add_argument("--project-root", default=".")
    dispatch_prepare_parser.add_argument("--dispatch-id", required=True)

    dispatch_begin_parser = subparsers.add_parser(
        "dispatch-begin",
        help="Mark a ready dispatch as in-flight after the real send step.",
    )
    dispatch_begin_parser.add_argument("--project-root", default=".")
    dispatch_begin_parser.add_argument("--dispatch-id", required=True)

    enqueue_parser = subparsers.add_parser("enqueue", help="Enqueue an operator command into the project queue.")
    enqueue_parser.add_argument("--project-root", default=".")
    enqueue_parser.add_argument("--summary", required=True)
    enqueue_parser.add_argument("--role")
    enqueue_parser.add_argument("--source", default="operator")
    enqueue_parser.add_argument("--priority", choices=("low", "normal", "high"), default="normal")

    dispatch_open_parser = subparsers.add_parser(
        "dispatch-open",
        help="Promote a pending queue command into a dispatch ticket.",
    )
    dispatch_open_parser.add_argument("--project-root", default=".")
    dispatch_open_parser.add_argument("--command-id")

    apply_result_parser = subparsers.add_parser(
        "apply-result",
        help="Apply a completed, failed, or cancelled result to a dispatch ticket.",
    )
    apply_result_parser.add_argument("--project-root", default=".")
    apply_result_parser.add_argument("--dispatch-id", required=True)
    apply_result_parser.add_argument("--outcome", choices=("completed", "failed", "cancelled"), required=True)
    apply_result_parser.add_argument("--summary", required=True)

    tui_parser = subparsers.add_parser("tui", help="Run the interactive TUI installer.")
    tui_parser.add_argument("--project-root", default=".")

    return parser


def run_catalog(args: argparse.Namespace) -> int:
    project_root = Path(args.project_root).resolve()
    include_project = args.scope == "project"
    categories = get_categories(
        project_root=project_root,
        include_project=include_project,
        include_global=True,
    )
    agents = get_agents(
        project_root=project_root,
        include_project=include_project,
        include_global=True,
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


def run_install(args: argparse.Namespace) -> int:
    project_root = Path(args.project_root).resolve()
    agent_keys = [item.strip() for item in args.agents.split(",") if item.strip()]
    try:
        result = install_agents(
            scope=args.scope,
            project_root=project_root,
            agent_keys=agent_keys,
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

    if args.command == "catalog":
        return run_catalog(args)
    if args.command == "install":
        return run_install(args)
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
    if args.command == "tui":
        return run_tui(Path(args.project_root).resolve())

    parser.error(f"unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
