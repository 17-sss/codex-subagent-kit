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


if __name__ == "__main__":
    unittest.main()
