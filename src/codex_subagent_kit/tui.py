from __future__ import annotations

import curses
from pathlib import Path

from .catalog import get_agents_by_category, get_categories
from .doctor import DoctorReport, run_doctor
from .generator import (
    GenerationError,
    install_agents,
    resolve_target_dir,
)
from .models import AgentSpec, InstallResult


HELP_TEXT = "Up/Down 이동  Space 토글  Enter 다음  b 뒤로  a 전체토글  q 종료"


class BackNavigation(RuntimeError):
    """Raised when the user navigates to the previous TUI step."""


def _draw_title(stdscr: curses.window, title: str, subtitle: str | None = None) -> None:
    stdscr.clear()
    stdscr.addstr(0, 2, "codex-subagent-kit", curses.A_BOLD)
    stdscr.addstr(2, 2, title, curses.A_UNDERLINE)
    if subtitle:
        stdscr.addstr(3, 2, subtitle)


def _single_select(
    stdscr: curses.window,
    *,
    title: str,
    subtitle: str,
    options: list[tuple[str, str]],
) -> str:
    index = 0
    while True:
        _draw_title(stdscr, title, subtitle)
        for row, (_, label) in enumerate(options, start=5):
            attr = curses.A_REVERSE if row - 5 == index else curses.A_NORMAL
            stdscr.addstr(row, 4, label, attr)
        stdscr.addstr(curses.LINES - 2, 2, "Enter 선택  q 종료")
        stdscr.refresh()

        key = stdscr.getch()
        if key in (ord("q"), 27):
            raise KeyboardInterrupt
        if key in (curses.KEY_UP, ord("k")):
            index = (index - 1) % len(options)
        elif key in (curses.KEY_DOWN, ord("j")):
            index = (index + 1) % len(options)
        elif key in (curses.KEY_ENTER, 10, 13):
            return options[index][0]


def _multi_select(
    stdscr: curses.window,
    *,
    title: str,
    subtitle: str,
    items: list[tuple[str, str]],
    selected: set[str] | None = None,
) -> set[str]:
    index = 0
    current = set(selected or set())
    while True:
        _draw_title(stdscr, title, subtitle)
        for row, (value, label) in enumerate(items, start=5):
            marker = "[x]" if value in current else "[ ]"
            attr = curses.A_REVERSE if row - 5 == index else curses.A_NORMAL
            stdscr.addstr(row, 4, f"{marker} {label}", attr)
        stdscr.addstr(curses.LINES - 2, 2, HELP_TEXT)
        stdscr.refresh()

        key = stdscr.getch()
        if key in (ord("q"), 27):
            raise KeyboardInterrupt
        if key in (curses.KEY_UP, ord("k")):
            index = (index - 1) % len(items)
        elif key in (curses.KEY_DOWN, ord("j")):
            index = (index + 1) % len(items)
        elif key == ord(" "):
            value = items[index][0]
            if value in current:
                current.remove(value)
            else:
                current.add(value)
        elif key == ord("a"):
            values = {value for value, _ in items}
            current = values if current != values else set()
        elif key == ord("b"):
            raise BackNavigation("back")
        elif key in (curses.KEY_ENTER, 10, 13):
            return current


def _summary_screen(
    stdscr: curses.window,
    *,
    scope: str,
    project_root: Path,
    category_titles: list[str],
    agent_labels: list[str],
) -> bool:
    target_dir = resolve_target_dir(scope, project_root)
    while True:
        _draw_title(
            stdscr,
            "설치 요약",
            "Enter로 생성, b로 뒤로, q로 종료",
        )
        stdscr.addstr(5, 4, f"scope: {scope}")
        stdscr.addstr(6, 4, f"target: {target_dir}")
        stdscr.addstr(8, 4, f"categories ({len(category_titles)}):")
        for idx, label in enumerate(category_titles[:6], start=9):
            stdscr.addstr(idx, 6, f"- {label}")
        agent_row = 16
        stdscr.addstr(agent_row, 4, f"agents ({len(agent_labels)}):")
        for idx, label in enumerate(agent_labels[:10], start=agent_row + 1):
            stdscr.addstr(idx, 6, f"- {label}")
        stdscr.refresh()

        key = stdscr.getch()
        if key in (ord("q"), 27):
            raise KeyboardInterrupt
        if key == ord("b"):
            return False
        if key in (curses.KEY_ENTER, 10, 13):
            return True


def _result_screen(
    stdscr: curses.window,
    result: InstallResult,
    *,
    validation_report: DoctorReport | None = None,
) -> None:
    _draw_title(stdscr, "생성 완료", "아무 키나 누르면 종료됩니다.")
    row = 5
    for path in result.agent_paths[:8]:
        stdscr.addstr(row, 4, str(path))
        row += 1
    for path in result.agent_preserved_paths[:4]:
        stdscr.addstr(row, 4, f"agent preserved: {path}")
        row += 1
    if result.orchestrator_key:
        stdscr.addstr(row, 4, f"orchestrator: {result.orchestrator_key}")
        row += 1
    for path in result.scaffold_created_paths[:4]:
        stdscr.addstr(row, 4, f"created: {path}")
        row += 1
    for path in result.scaffold_preserved_paths[:4]:
        stdscr.addstr(row, 4, f"preserved: {path}")
        row += 1
    if validation_report is not None:
        stdscr.addstr(row, 4, f"validation: {'ok' if validation_report.ok else 'issues found'}")
        row += 1
        for issue in validation_report.issues[:3]:
            message = issue.message if issue.path is None else f"{issue.path.name}: {issue.message}"
            stdscr.addstr(row, 6, message[: max(curses.COLS - 8, 20)])
            row += 1
    stdscr.refresh()
    stdscr.getch()


def _error_screen(stdscr: curses.window, message: str) -> None:
    _draw_title(stdscr, "오류", "아무 키나 누르면 이전 화면으로 돌아갑니다.")
    stdscr.addstr(5, 4, message)
    stdscr.refresh()
    stdscr.getch()


def _default_agent_selection(scope: str, agent_specs: list[AgentSpec]) -> set[str]:
    del scope, agent_specs
    return set()


def _validate_agent_selection(scope: str, agent_specs: list[AgentSpec], selected_agents: set[str]) -> str | None:
    del scope, agent_specs
    if not selected_agents:
        return "최소 1개 이상의 subagent를 선택해야 합니다."
    return None


def run_tui(project_root: Path, *, catalog_roots: tuple[Path, ...] = ()) -> int:
    def _catalog_for_scope(scope: str) -> tuple[list[tuple[str, str]], dict[str, str]]:
        include_project = scope == "project"
        categories = list(
            get_categories(
                project_root=project_root,
                include_project=include_project,
                include_global=True,
                catalog_roots=catalog_roots,
            )
        )
        items = [(item.key, f"{item.title} - {item.description}") for item in categories]
        title_map = {item.key: item.title for item in categories}
        return items, title_map

    def _app(stdscr: curses.window) -> int:
        try:
            curses.curs_set(0)
        except curses.error:
            pass
        stdscr.keypad(True)

        scope = _single_select(
            stdscr,
            title="설치 위치 선택",
            subtitle=f"project root: {project_root}",
            options=[
                ("project", "Project (.codex/agents in current project)"),
                ("global", "Global (~/.codex/agents)"),
            ],
        )
        category_items, category_title_map = _catalog_for_scope(scope)
        selected_categories: set[str] = set()

        while True:
            try:
                selected_categories = _multi_select(
                    stdscr,
                    title="카테고리 선택",
                    subtitle="필요한 카테고리를 고르세요. 선택이 없으면 전체 agent를 보여줍니다.",
                    items=category_items,
                    selected=selected_categories,
                )
            except BackNavigation:
                scope = _single_select(
                    stdscr,
                    title="설치 위치 선택",
                    subtitle=f"project root: {project_root}",
                    options=[
                        ("project", "Project (.codex/agents in current project)"),
                        ("global", "Global (~/.codex/agents)"),
                    ],
                )
                category_items, category_title_map = _catalog_for_scope(scope)
                selected_categories = set()
                continue

            agent_specs = get_agents_by_category(
                selected_categories,
                project_root=project_root,
                include_project=(scope == "project"),
                include_global=True,
                catalog_roots=catalog_roots,
            )
            agent_items = [(agent.key, f"{agent.name} - {agent.description}") for agent in agent_specs]
            selected_agents = _default_agent_selection(scope, agent_specs)
            while True:
                try:
                    selected_agents = _multi_select(
                        stdscr,
                        title="Subagent 선택",
                        subtitle=(
                            "Space로 토글하세요. meta-orchestration agent를 포함하면 "
                            "experimental scaffold도 함께 생성됩니다."
                        ),
                        items=agent_items,
                        selected=selected_agents,
                    )
                except BackNavigation:
                    break

                validation_error = _validate_agent_selection(scope, agent_specs, selected_agents)
                if validation_error:
                    _error_screen(stdscr, validation_error)
                    continue

                confirmed = _summary_screen(
                    stdscr,
                    scope=scope,
                    project_root=project_root,
                    category_titles=[category_title_map[key] for key in sorted(selected_categories)],
                    agent_labels=[agent.key for agent in agent_specs if agent.key in selected_agents],
                )
                if not confirmed:
                    continue

                try:
                    result = install_agents(
                        scope=scope,
                        project_root=project_root,
                        agent_keys=sorted(selected_agents),
                        catalog_roots=catalog_roots,
                    )
                except GenerationError as exc:
                    _error_screen(stdscr, str(exc))
                    continue

                validation_report = run_doctor(
                    project_root=project_root,
                    scope=scope,
                    catalog_roots=catalog_roots,
                )
                _result_screen(stdscr, result, validation_report=validation_report)
                return 0 if validation_report.ok else 1

    try:
        return curses.wrapper(_app)
    except KeyboardInterrupt:
        return 130
