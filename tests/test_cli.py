from __future__ import annotations

import io
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory

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
                    "reviewer,code-mapper",
                ]
            )

            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            self.assertIn("target:", stdout)
            self.assertIn("reviewer.toml", stdout)
            self.assertTrue((Path(temp_dir) / ".codex" / "agents" / "reviewer.toml").exists())

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


if __name__ == "__main__":
    unittest.main()
