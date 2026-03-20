from __future__ import annotations

import io
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from codex_orchestrator import cli


class CLITests(unittest.TestCase):
    def run_cli(self, argv: list[str]) -> tuple[int, str, str]:
        stdout_buffer = io.StringIO()
        stderr_buffer = io.StringIO()

        with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
            exit_code = cli.main(argv)

        return exit_code, stdout_buffer.getvalue(), stderr_buffer.getvalue()

    def test_catalog_command_lists_known_sections(self) -> None:
        exit_code, stdout, stderr = self.run_cli(["catalog"])

        self.assertEqual(exit_code, 0)
        self.assertEqual(stderr, "")
        self.assertIn("[Meta & Orchestration]", stdout)
        self.assertIn("reviewer", stdout)

    def test_catalog_command_discovers_external_agents(self) -> None:
        with TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            temp_home = project_root / "home"
            project_agents_dir = project_root / ".codex" / "agents"
            project_agents_dir.mkdir(parents=True)
            temp_home.mkdir()
            (project_agents_dir / "custom-helper.toml").write_text(
                """
name = "custom-helper"
description = "Project custom helper"
model = "gpt-5.4"
model_reasoning_effort = "medium"
sandbox_mode = "workspace-write"
[instructions]
text = "custom helper instructions"
""".strip()
                + "\n",
                encoding="utf-8",
            )

            with patch.object(Path, "home", return_value=temp_home):
                exit_code, stdout, stderr = self.run_cli(
                    [
                        "catalog",
                        "--project-root",
                        temp_dir,
                        "--scope",
                        "project",
                    ]
                )

            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            self.assertIn("[Imported & External]", stdout)
            self.assertIn("custom-helper", stdout)
            self.assertIn("[project]", stdout)

    def test_install_command_creates_files_and_reports_target(self) -> None:
        with TemporaryDirectory() as temp_dir:
            exit_code, stdout, stderr = self.run_cli(
                [
                    "install",
                    "--scope",
                    "project",
                    "--project-root",
                    temp_dir,
                    "--agents",
                    "cto-coordinator,reviewer,code-mapper",
                ]
            )

            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            self.assertIn("target:", stdout)
            self.assertIn("reviewer.toml", stdout)
            self.assertIn("orchestrator: cto-coordinator", stdout)
            self.assertIn("scaffold created:", stdout)
            self.assertTrue((Path(temp_dir) / ".codex" / "agents" / "reviewer.toml").exists())

            second_exit_code, second_stdout, second_stderr = self.run_cli(
                [
                    "install",
                    "--scope",
                    "project",
                    "--project-root",
                    temp_dir,
                    "--agents",
                    "cto-coordinator,reviewer,code-mapper",
                ]
            )
            self.assertEqual(second_exit_code, 0)
            self.assertEqual(second_stderr, "")
            self.assertIn("agent preserved:", second_stdout)
            self.assertIn("scaffold preserved:", second_stdout)

    def test_install_command_returns_error_for_unknown_agent(self) -> None:
        with TemporaryDirectory() as temp_dir:
            exit_code, stdout, stderr = self.run_cli(
                [
                    "install",
                    "--scope",
                    "project",
                    "--project-root",
                    temp_dir,
                    "--agents",
                    "missing-agent",
                ]
            )

            self.assertEqual(exit_code, 1)
            self.assertEqual(stdout, "")
            self.assertIn("unknown agent keys", stderr)

    def test_project_install_without_orchestrator_returns_error(self) -> None:
        with TemporaryDirectory() as temp_dir:
            exit_code, stdout, stderr = self.run_cli(
                [
                    "install",
                    "--scope",
                    "project",
                    "--project-root",
                    temp_dir,
                    "--agents",
                    "reviewer",
                ]
            )

            self.assertEqual(exit_code, 1)
            self.assertEqual(stdout, "")
            self.assertIn("meta-orchestration agent", stderr)

    def test_panel_command_renders_generated_team_manifest(self) -> None:
        with TemporaryDirectory() as temp_dir:
            install_exit_code, _, install_stderr = self.run_cli(
                [
                    "install",
                    "--scope",
                    "project",
                    "--project-root",
                    temp_dir,
                    "--agents",
                    "cto-coordinator,reviewer,code-mapper",
                ]
            )
            self.assertEqual(install_exit_code, 0)
            self.assertEqual(install_stderr, "")

            exit_code, stdout, stderr = self.run_cli(
                [
                    "panel",
                    "--project-root",
                    temp_dir,
                ]
            )

            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            self.assertIn("Operator: user", stdout)
            self.assertIn("Orchestrator: cto-coordinator", stdout)
            self.assertIn("reviewer", stdout)
            self.assertIn("code-mapper", stdout)
            self.assertIn("Queue", stdout)
            self.assertIn("Dispatch Ledger", stdout)

    def test_enqueue_command_updates_queue_and_panel_counts(self) -> None:
        with TemporaryDirectory() as temp_dir:
            install_exit_code, _, install_stderr = self.run_cli(
                [
                    "install",
                    "--scope",
                    "project",
                    "--project-root",
                    temp_dir,
                    "--agents",
                    "cto-coordinator,reviewer",
                ]
            )
            self.assertEqual(install_exit_code, 0)
            self.assertEqual(install_stderr, "")

            enqueue_exit_code, enqueue_stdout, enqueue_stderr = self.run_cli(
                [
                    "enqueue",
                    "--project-root",
                    temp_dir,
                    "--summary",
                    "Review the regression report",
                ]
            )
            self.assertEqual(enqueue_exit_code, 0)
            self.assertEqual(enqueue_stderr, "")
            self.assertIn("command-id: cmd-001", enqueue_stdout)

            panel_exit_code, panel_stdout, panel_stderr = self.run_cli(
                [
                    "panel",
                    "--project-root",
                    temp_dir,
                ]
            )
            self.assertEqual(panel_exit_code, 0)
            self.assertEqual(panel_stderr, "")
            self.assertIn("- pending: 1", panel_stdout)

    def test_dispatch_open_updates_queue_and_ledger_counts(self) -> None:
        with TemporaryDirectory() as temp_dir:
            install_exit_code, _, install_stderr = self.run_cli(
                [
                    "install",
                    "--scope",
                    "project",
                    "--project-root",
                    temp_dir,
                    "--agents",
                    "cto-coordinator,reviewer",
                ]
            )
            self.assertEqual(install_exit_code, 0)
            self.assertEqual(install_stderr, "")

            enqueue_exit_code, _, enqueue_stderr = self.run_cli(
                [
                    "enqueue",
                    "--project-root",
                    temp_dir,
                    "--summary",
                    "Review the regression report",
                ]
            )
            self.assertEqual(enqueue_exit_code, 0)
            self.assertEqual(enqueue_stderr, "")

            dispatch_exit_code, dispatch_stdout, dispatch_stderr = self.run_cli(
                [
                    "dispatch-open",
                    "--project-root",
                    temp_dir,
                ]
            )
            self.assertEqual(dispatch_exit_code, 0)
            self.assertEqual(dispatch_stderr, "")
            self.assertIn("dispatch-id: dispatch-001", dispatch_stdout)
            self.assertIn("status: ready", dispatch_stdout)

            panel_exit_code, panel_stdout, panel_stderr = self.run_cli(
                [
                    "panel",
                    "--project-root",
                    temp_dir,
                ]
            )
            self.assertEqual(panel_exit_code, 0)
            self.assertEqual(panel_stderr, "")
            self.assertIn("- pending: 0", panel_stdout)
            self.assertIn("- claimed: 1", panel_stdout)
            self.assertIn("- ready: 1", panel_stdout)

    def test_apply_result_updates_panel_counts_and_runtime(self) -> None:
        with TemporaryDirectory() as temp_dir:
            install_exit_code, _, install_stderr = self.run_cli(
                [
                    "install",
                    "--scope",
                    "project",
                    "--project-root",
                    temp_dir,
                    "--agents",
                    "cto-coordinator,reviewer",
                ]
            )
            self.assertEqual(install_exit_code, 0)
            self.assertEqual(install_stderr, "")

            enqueue_exit_code, _, enqueue_stderr = self.run_cli(
                [
                    "enqueue",
                    "--project-root",
                    temp_dir,
                    "--summary",
                    "Review the regression report",
                ]
            )
            self.assertEqual(enqueue_exit_code, 0)
            self.assertEqual(enqueue_stderr, "")

            dispatch_exit_code, _, dispatch_stderr = self.run_cli(
                [
                    "dispatch-open",
                    "--project-root",
                    temp_dir,
                ]
            )
            self.assertEqual(dispatch_exit_code, 0)
            self.assertEqual(dispatch_stderr, "")

            result_exit_code, result_stdout, result_stderr = self.run_cli(
                [
                    "apply-result",
                    "--project-root",
                    temp_dir,
                    "--dispatch-id",
                    "dispatch-001",
                    "--outcome",
                    "completed",
                    "--summary",
                    "Review finished and reported back",
                ]
            )
            self.assertEqual(result_exit_code, 0)
            self.assertEqual(result_stderr, "")
            self.assertIn("status: completed", result_stdout)

            panel_exit_code, panel_stdout, panel_stderr = self.run_cli(
                [
                    "panel",
                    "--project-root",
                    temp_dir,
                ]
            )
            self.assertEqual(panel_exit_code, 0)
            self.assertEqual(panel_stderr, "")
            self.assertIn("Orchestrator: cto-coordinator [idle]", panel_stdout)
            self.assertIn("- completed: 1", panel_stdout)
            self.assertIn("- ready: 0", panel_stdout)


if __name__ == "__main__":
    unittest.main()
