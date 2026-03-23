from __future__ import annotations

import io
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from codex_subagent_kit import cli


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

    def test_empty_command_defaults_to_tui(self) -> None:
        with patch("codex_subagent_kit.cli.run_tui", return_value=0) as run_tui_mock:
            exit_code, stdout, stderr = self.run_cli([])

        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout, "")
        self.assertEqual(stderr, "")
        run_tui_mock.assert_called_once()

    def test_help_text_marks_experimental_commands(self) -> None:
        help_text = cli.build_parser().format_help()

        self.assertIn("Install and manage Codex subagent definitions.", help_text)
        self.assertIn("Control-plane commands remain experimental.", help_text)
        self.assertIn("[experimental] Render the current project control-", help_text)
        self.assertIn("[experimental] Promote a pending queue command into a", help_text)

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
developer_instructions = "custom helper instructions"
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

    def test_catalog_import_command_persists_selected_agent(self) -> None:
        with TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            source_root = project_root / "source-categories"
            category_dir = source_root / "11-custom-ops"
            category_dir.mkdir(parents=True)
            (category_dir / "README.md").write_text(
                "# 11. Custom Ops\n\nCustom external operators.\n",
                encoding="utf-8",
            )
            (category_dir / "custom-helper.toml").write_text(
                """
name = "custom-helper"
description = "Custom helper"
model = "gpt-5.4"
model_reasoning_effort = "medium"
sandbox_mode = "read-only"
developer_instructions = "custom helper instructions"
""".strip()
                + "\n",
                encoding="utf-8",
            )

            exit_code, stdout, stderr = self.run_cli(
                [
                    "catalog",
                    "import",
                    "--project-root",
                    temp_dir,
                    "--scope",
                    "project",
                    "--catalog-root",
                    str(source_root),
                    "--agents",
                    "custom-helper",
                ]
            )

            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            self.assertIn("categories: custom-ops", stdout)
            self.assertIn("agents: custom-helper", stdout)
            self.assertTrue(
                (
                    project_root
                    / ".codex"
                    / "subagent-kit"
                    / "catalog"
                    / "categories"
                    / "11-custom-ops"
                    / "custom-helper.toml"
                ).exists()
            )

    def test_doctor_command_reports_project_install_status(self) -> None:
        with TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            temp_home = project_root / "home"
            temp_home.mkdir()

            with patch.object(Path, "home", return_value=temp_home):
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

                exit_code, stdout, stderr = self.run_cli(
                    [
                        "doctor",
                        "--scope",
                        "project",
                        "--project-root",
                        temp_dir,
                    ]
                )

            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            self.assertIn("status: ok", stdout)
            self.assertIn("Installed agent files checked:", stdout)

    def test_usage_command_renders_starter_prompt(self) -> None:
        with TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            temp_home = project_root / "home"
            temp_home.mkdir()

            with patch.object(Path, "home", return_value=temp_home):
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

                exit_code, stdout, stderr = self.run_cli(
                    [
                        "usage",
                        "--scope",
                        "project",
                        "--project-root",
                        temp_dir,
                        "--task",
                        "Review the failing auth flow",
                    ]
                )

            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            self.assertIn("starter prompt:", stdout)
            self.assertIn("Review the failing auth flow", stdout)
            self.assertIn("cto-coordinator", stdout)

    def test_catalog_command_supports_catalog_root(self) -> None:
        with TemporaryDirectory() as temp_dir:
            catalog_root = Path(temp_dir) / "categories"
            category_dir = catalog_root / "11-custom-ops"
            category_dir.mkdir(parents=True)
            (category_dir / "README.md").write_text(
                "# 11. Custom Ops\n\nCustom externally injected operators.\n",
                encoding="utf-8",
            )
            (category_dir / "custom-operator.toml").write_text(
                """
name = "custom-operator"
description = "Custom injected agent"
model = "gpt-5.4"
model_reasoning_effort = "medium"
sandbox_mode = "read-only"
developer_instructions = "custom injected instructions"
""".strip()
                + "\n",
                encoding="utf-8",
            )

            exit_code, stdout, stderr = self.run_cli(
                [
                    "catalog",
                    "--catalog-root",
                    str(catalog_root),
                ]
            )

            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            self.assertIn("[Custom Ops]", stdout)
            self.assertIn("custom-operator", stdout)

    def test_install_command_can_use_catalog_root(self) -> None:
        with TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            catalog_root = project_root / "categories"
            category_dir = catalog_root / "11-custom-ops"
            category_dir.mkdir(parents=True)
            (category_dir / "README.md").write_text(
                "# 11. Custom Ops\n\nCustom externally injected operators.\n",
                encoding="utf-8",
            )
            (category_dir / "custom-coordinator.toml").write_text(
                """
name = "custom-coordinator"
description = "Custom orchestrator"
model = "gpt-5.4"
model_reasoning_effort = "high"
sandbox_mode = "read-only"
developer_instructions = "Coordinate custom injected work."
codex_subagent_kit_category = "meta-orchestration"
""".strip()
                + "\n",
                encoding="utf-8",
            )

            exit_code, stdout, stderr = self.run_cli(
                [
                    "install",
                    "--scope",
                    "project",
                    "--project-root",
                    temp_dir,
                    "--catalog-root",
                    str(catalog_root),
                    "--agents",
                    "custom-coordinator",
                ]
            )

            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            self.assertIn("custom-coordinator.toml", stdout)
            self.assertTrue((project_root / ".codex" / "agents" / "custom-coordinator.toml").exists())

    def test_install_command_can_validate_successfully(self) -> None:
        with TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            temp_home = project_root / "home"
            temp_home.mkdir()

            with patch.object(Path, "home", return_value=temp_home):
                exit_code, stdout, stderr = self.run_cli(
                    [
                        "install",
                        "--scope",
                        "project",
                        "--project-root",
                        temp_dir,
                        "--agents",
                        "cto-coordinator,reviewer",
                        "--validate",
                    ]
                )

            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            self.assertIn("reviewer.toml", stdout)
            self.assertIn("status: ok", stdout)
            self.assertIn("Issues: none", stdout)

    def test_install_command_returns_error_when_validate_finds_issues(self) -> None:
        with TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            temp_home = project_root / "home"
            temp_home.mkdir()
            project_agents_dir = project_root / ".codex" / "agents"
            project_agents_dir.mkdir(parents=True)
            (project_agents_dir / "broken.toml").write_text(
                """
name = "broken"
description = "Broken agent"
model = "gpt-5.4"
model_reasoning_effort = "medium"
sandbox_mode = "read-only"
""".strip()
                + "\n",
                encoding="utf-8",
            )

            with patch.object(Path, "home", return_value=temp_home):
                exit_code, stdout, stderr = self.run_cli(
                    [
                        "install",
                        "--scope",
                        "project",
                        "--project-root",
                        temp_dir,
                        "--agents",
                        "cto-coordinator,reviewer",
                        "--validate",
                    ]
                )

            self.assertEqual(exit_code, 1)
            self.assertEqual(stderr, "")
            self.assertIn("reviewer.toml", stdout)
            self.assertIn("status: issues found", stdout)
            self.assertIn("broken.toml", stdout)

    def test_template_init_command_creates_project_local_scaffold(self) -> None:
        with TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)

            exit_code, stdout, stderr = self.run_cli(
                [
                    "template",
                    "init",
                    "--project-root",
                    temp_dir,
                    "--category",
                    "custom-ops",
                    "--agent",
                    "custom-coordinator",
                ]
            )

            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            self.assertIn("target:", stdout)
            self.assertIn("created:", stdout)
            self.assertTrue(
                (
                    project_root
                    / ".codex"
                    / "subagent-kit"
                    / "catalog"
                    / "categories"
                    / "11-custom-ops"
                    / "custom-coordinator.toml"
                ).exists()
            )

    def test_template_init_command_supports_explicit_catalog_root(self) -> None:
        with TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "project"
            catalog_root = Path(temp_dir) / "external-categories"

            exit_code, stdout, stderr = self.run_cli(
                [
                    "template",
                    "init",
                    "--project-root",
                    str(project_root),
                    "--catalog-root",
                    str(catalog_root),
                    "--category",
                    "custom-ops",
                    "--agent",
                    "custom-coordinator",
                    "--orchestrator",
                ]
            )

            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr, "")
            self.assertIn(str(catalog_root), stdout)
            self.assertTrue((catalog_root / "11-custom-ops" / "custom-coordinator.toml").exists())

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

    def test_board_command_renders_role_specific_view(self) -> None:
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

            board_exit_code, board_stdout, board_stderr = self.run_cli(
                [
                    "board",
                    "--project-root",
                    temp_dir,
                    "--role",
                    "cto-coordinator",
                ]
            )
            self.assertEqual(board_exit_code, 0)
            self.assertEqual(board_stderr, "")
            self.assertIn("Role: cto-coordinator", board_stdout)
            self.assertIn("Kind: orchestrator", board_stdout)
            self.assertIn("dispatch-001 [ready]", board_stdout)

    def test_launch_command_supports_dry_run_preview(self) -> None:
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

            launch_exit_code, launch_stdout, launch_stderr = self.run_cli(
                [
                    "launch",
                    "--project-root",
                    temp_dir,
                    "--backend",
                    "tmux",
                    "--dry-run",
                ]
            )

            self.assertEqual(launch_exit_code, 0)
            self.assertEqual(launch_stderr, "")
            self.assertIn("backend: tmux", launch_stdout)
            self.assertIn("launch-tmux.sh", launch_stdout)
            self.assertIn("command:", launch_stdout)

    def test_launch_command_rejects_backend_incompatible_option(self) -> None:
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

            launch_exit_code, launch_stdout, launch_stderr = self.run_cli(
                [
                    "launch",
                    "--project-root",
                    temp_dir,
                    "--backend",
                    "cmux",
                    "--no-attach",
                ]
            )

            self.assertEqual(launch_exit_code, 1)
            self.assertEqual(launch_stdout, "")
            self.assertIn("--no-attach", launch_stderr)

    def test_launch_command_requires_project_launcher_scaffold(self) -> None:
        with TemporaryDirectory() as temp_dir:
            launch_exit_code, launch_stdout, launch_stderr = self.run_cli(
                [
                    "launch",
                    "--project-root",
                    temp_dir,
                    "--backend",
                    "tmux",
                    "--dry-run",
                ]
            )

            self.assertEqual(launch_exit_code, 1)
            self.assertEqual(launch_stdout, "")
            self.assertIn("project install first", launch_stderr)

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

    def test_dispatch_prepare_renders_handoff_package(self) -> None:
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
                    "--role",
                    "reviewer",
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

            prepare_exit_code, prepare_stdout, prepare_stderr = self.run_cli(
                [
                    "dispatch-prepare",
                    "--project-root",
                    temp_dir,
                    "--dispatch-id",
                    "dispatch-001",
                ]
            )
            self.assertEqual(prepare_exit_code, 0)
            self.assertEqual(prepare_stderr, "")
            self.assertIn("[dispatch]", prepare_stdout)
            self.assertIn("dispatch-001", prepare_stdout)
            self.assertIn("role: reviewer", prepare_stdout)
            self.assertIn("[suggested send_input message]", prepare_stdout)

    def test_dispatch_begin_updates_panel_counts(self) -> None:
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

            begin_exit_code, begin_stdout, begin_stderr = self.run_cli(
                [
                    "dispatch-begin",
                    "--project-root",
                    temp_dir,
                    "--dispatch-id",
                    "dispatch-001",
                ]
            )
            self.assertEqual(begin_exit_code, 0)
            self.assertEqual(begin_stderr, "")
            self.assertIn("status: dispatched", begin_stdout)

            panel_exit_code, panel_stdout, panel_stderr = self.run_cli(
                [
                    "panel",
                    "--project-root",
                    temp_dir,
                ]
            )
            self.assertEqual(panel_exit_code, 0)
            self.assertEqual(panel_stderr, "")
            self.assertIn("- dispatched: 1", panel_stdout)

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

            begin_exit_code, _, begin_stderr = self.run_cli(
                [
                    "dispatch-begin",
                    "--project-root",
                    temp_dir,
                    "--dispatch-id",
                    "dispatch-001",
                ]
            )
            self.assertEqual(begin_exit_code, 0)
            self.assertEqual(begin_stderr, "")

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
