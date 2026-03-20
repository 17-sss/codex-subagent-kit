from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from codex_orchestrator.generator import install_agents
from codex_orchestrator.launch_runtime import LaunchError, build_launch_plan, render_launch_preview


class LaunchRuntimeTests(unittest.TestCase):
    def test_build_tmux_launch_plan_uses_generated_script(self) -> None:
        with TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            install_agents(
                scope="project",
                project_root=project_root,
                agent_keys=["cto-coordinator", "reviewer"],
            )

            plan = build_launch_plan(
                project_root=project_root,
                backend="tmux",
            )

            self.assertEqual(plan.backend, "tmux")
            self.assertTrue(plan.script_path.exists())
            self.assertEqual(plan.argv, [str(plan.script_path)])

    def test_build_tmux_launch_plan_supports_no_attach_without_name(self) -> None:
        with TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            install_agents(
                scope="project",
                project_root=project_root,
                agent_keys=["cto-coordinator", "reviewer"],
            )

            plan = build_launch_plan(
                project_root=project_root,
                backend="tmux",
                attach=False,
            )

            self.assertEqual(plan.argv[0], str(plan.script_path))
            self.assertEqual(plan.argv[1], f"codex-orchestrator-{project_root.name}")
            self.assertEqual(plan.argv[2], "--no-attach")

    def test_build_cmux_launch_plan_supports_custom_name(self) -> None:
        with TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            install_agents(
                scope="project",
                project_root=project_root,
                agent_keys=["cto-coordinator", "reviewer"],
            )

            plan = build_launch_plan(
                project_root=project_root,
                backend="cmux",
                name="demo-workspace",
            )

            self.assertEqual(plan.argv, [str(plan.script_path), "demo-workspace"])
            preview = render_launch_preview(plan)
            self.assertIn("backend: cmux", preview)
            self.assertIn("demo-workspace", preview)

    def test_build_launch_plan_rejects_missing_scaffold(self) -> None:
        with TemporaryDirectory() as temp_dir:
            with self.assertRaises(LaunchError):
                build_launch_plan(
                    project_root=Path(temp_dir),
                    backend="tmux",
                )

    def test_build_launch_plan_rejects_backend_incompatible_no_attach(self) -> None:
        with TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            install_agents(
                scope="project",
                project_root=project_root,
                agent_keys=["cto-coordinator", "reviewer"],
            )

            with self.assertRaises(LaunchError):
                build_launch_plan(
                    project_root=project_root,
                    backend="cmux",
                    attach=False,
                )


if __name__ == "__main__":
    unittest.main()
