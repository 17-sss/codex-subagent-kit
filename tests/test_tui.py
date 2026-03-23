from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from codex_orchestrator.catalog import get_agents_by_category
from codex_orchestrator.doctor import DoctorIssue, DoctorReport
from codex_orchestrator.models import InstallResult
from codex_orchestrator.tui import BackNavigation, _default_agent_selection, _validate_agent_selection, run_tui


class _FakeWindow:
    def keypad(self, _flag: bool) -> None:
        return None


class TuiTests(unittest.TestCase):
    def _doctor_report(self, *, ok: bool) -> DoctorReport:
        issues = [] if ok else [DoctorIssue(path=Path("/tmp/project/.codex/agents/broken.toml"), message="missing instructions text")]
        return DoctorReport(
            scope="project",
            target_dir=Path("/tmp/project/.codex/agents"),
            catalog_counts=[("built-in", 1)],
            installed_counts=[("project agents", 1)],
            issues=issues,
        )

    def test_default_project_selection_prefers_cto_coordinator(self) -> None:
        agent_specs = get_agents_by_category()

        selected = _default_agent_selection("project", agent_specs)

        self.assertEqual(selected, {"cto-coordinator"})

    def test_project_selection_requires_meta_orchestration_agent(self) -> None:
        agent_specs = get_agents_by_category()

        message = _validate_agent_selection("project", agent_specs, {"reviewer"})

        self.assertIsNotNone(message)
        self.assertIn("meta-orchestration", message)
        self.assertIn("cto-coordinator", message)

    def test_project_selection_accepts_root_orchestrator(self) -> None:
        agent_specs = get_agents_by_category()

        message = _validate_agent_selection("project", agent_specs, {"cto-coordinator", "reviewer"})

        self.assertIsNone(message)

    def test_global_selection_does_not_require_meta_orchestration_agent(self) -> None:
        agent_specs = get_agents_by_category()

        message = _validate_agent_selection("global", agent_specs, {"reviewer"})

        self.assertIsNone(message)

    def test_back_navigation_from_agents_to_scope_does_not_crash(self) -> None:
        fake_result = InstallResult(
            agent_paths=[],
            agent_preserved_paths=[],
            scaffold_created_paths=[],
            scaffold_preserved_paths=[],
            orchestrator_key=None,
        )

        def fake_wrapper(func):
            return func(_FakeWindow())

        with (
            patch("codex_orchestrator.tui.curses.wrapper", side_effect=fake_wrapper),
            patch("codex_orchestrator.tui.curses.curs_set", return_value=None),
            patch(
                "codex_orchestrator.tui._single_select",
                side_effect=["project", "global"],
            ) as single_select_mock,
            patch(
                "codex_orchestrator.tui._multi_select",
                side_effect=[
                    set(),
                    BackNavigation("back"),
                    BackNavigation("back"),
                    set(),
                    {"reviewer"},
                ],
            ),
            patch("codex_orchestrator.tui._summary_screen", return_value=True),
            patch("codex_orchestrator.tui.install_agents", return_value=fake_result),
            patch("codex_orchestrator.tui.run_doctor", return_value=self._doctor_report(ok=True)),
            patch("codex_orchestrator.tui._result_screen", return_value=None),
        ):
            exit_code = run_tui(Path("/tmp/project"))

        self.assertEqual(exit_code, 0)
        self.assertEqual(single_select_mock.call_count, 2)

    def test_tui_forwards_catalog_roots_to_install(self) -> None:
        fake_result = InstallResult(
            agent_paths=[],
            agent_preserved_paths=[],
            scaffold_created_paths=[],
            scaffold_preserved_paths=[],
            orchestrator_key="cto-coordinator",
        )
        catalog_root = Path("/tmp/custom-catalog")

        def fake_wrapper(func):
            return func(_FakeWindow())

        with (
            patch("codex_orchestrator.tui.curses.wrapper", side_effect=fake_wrapper),
            patch("codex_orchestrator.tui.curses.curs_set", return_value=None),
            patch("codex_orchestrator.tui._single_select", return_value="project"),
            patch(
                "codex_orchestrator.tui._multi_select",
                side_effect=[
                    {"meta-orchestration"},
                    {"cto-coordinator"},
                ],
            ),
            patch("codex_orchestrator.tui._summary_screen", return_value=True),
            patch("codex_orchestrator.tui.install_agents", return_value=fake_result) as install_mock,
            patch("codex_orchestrator.tui.run_doctor", return_value=self._doctor_report(ok=True)) as doctor_mock,
            patch("codex_orchestrator.tui._result_screen", return_value=None),
        ):
            exit_code = run_tui(Path("/tmp/project"), catalog_roots=(catalog_root,))

        self.assertEqual(exit_code, 0)
        install_mock.assert_called_once()
        doctor_mock.assert_called_once()
        self.assertEqual(install_mock.call_args.kwargs["catalog_roots"], (catalog_root,))

    def test_tui_returns_nonzero_when_validation_fails(self) -> None:
        fake_result = InstallResult(
            agent_paths=[],
            agent_preserved_paths=[],
            scaffold_created_paths=[],
            scaffold_preserved_paths=[],
            orchestrator_key="cto-coordinator",
        )

        def fake_wrapper(func):
            return func(_FakeWindow())

        with (
            patch("codex_orchestrator.tui.curses.wrapper", side_effect=fake_wrapper),
            patch("codex_orchestrator.tui.curses.curs_set", return_value=None),
            patch("codex_orchestrator.tui._single_select", return_value="project"),
            patch(
                "codex_orchestrator.tui._multi_select",
                side_effect=[
                    {"meta-orchestration"},
                    {"cto-coordinator"},
                ],
            ),
            patch("codex_orchestrator.tui._summary_screen", return_value=True),
            patch("codex_orchestrator.tui.install_agents", return_value=fake_result),
            patch("codex_orchestrator.tui.run_doctor", return_value=self._doctor_report(ok=False)),
            patch("codex_orchestrator.tui._result_screen", return_value=None),
        ):
            exit_code = run_tui(Path("/tmp/project"))

        self.assertEqual(exit_code, 1)


if __name__ == "__main__":
    unittest.main()
