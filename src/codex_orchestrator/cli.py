from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .catalog import get_agents, get_categories
from .generator import GenerationError, install_agents, resolve_target_dir
from .tui import run_tui


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="codex-orchestrator")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("catalog", help="Print the built-in subagent catalog.")

    install_parser = subparsers.add_parser("install", help="Install selected subagents without the TUI.")
    install_parser.add_argument("--scope", choices=("project", "global"), required=True)
    install_parser.add_argument("--agents", required=True, help="Comma-separated agent keys.")
    install_parser.add_argument("--project-root", default=".")
    install_parser.add_argument("--overwrite", action="store_true")

    tui_parser = subparsers.add_parser("tui", help="Run the interactive TUI installer.")
    tui_parser.add_argument("--project-root", default=".")

    return parser


def run_catalog() -> int:
    categories = {category.key: category for category in get_categories()}
    for category in get_categories():
        print(f"[{category.title}]")
        print(f"  key: {category.key}")
        print(f"  description: {category.description}")
        for agent in get_agents():
            if agent.category != category.key:
                continue
            print(f"  - {agent.key}: {agent.description}")
        print()
    return 0


def run_install(args: argparse.Namespace) -> int:
    project_root = Path(args.project_root).resolve()
    agent_keys = [item.strip() for item in args.agents.split(",") if item.strip()]
    try:
        created_paths = install_agents(
            scope=args.scope,
            project_root=project_root,
            agent_keys=agent_keys,
            overwrite=args.overwrite,
        )
    except GenerationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"target: {resolve_target_dir(args.scope, project_root)}")
    for path in created_paths:
        print(path)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "catalog":
        return run_catalog()
    if args.command == "install":
        return run_install(args)
    if args.command == "tui":
        return run_tui(Path(args.project_root).resolve())

    parser.error(f"unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
