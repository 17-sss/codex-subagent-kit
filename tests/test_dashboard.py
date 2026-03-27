from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from codex_subagent_kit.control_plane import apply_result, enqueue_command, open_dispatch
from codex_subagent_kit.dashboard import DashboardError, render_role_board
from codex_subagent_kit.generator import install_agents


class DashboardTests(unittest.TestCase):
    def test_render_role_board_for_orchestrator(self) -> None:
        with TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            install_agents(
                scope="project",
                project_root=project_root,
                agent_keys=["multi-agent-coordinator", "reviewer"],
            )
            enqueue_command(
                project_root=project_root,
                summary="Review the regression report",
            )
            open_dispatch(project_root=project_root)

            rendered = render_role_board(project_root, "multi-agent-coordinator")

            self.assertIn("Role: multi-agent-coordinator", rendered)
            self.assertIn("Kind: orchestrator", rendered)
            self.assertIn("Status: busy", rendered)
            self.assertIn("Active Dispatch: dispatch-001", rendered)
            self.assertIn("cmd-001 [claimed]", rendered)
            self.assertIn("dispatch-001 [ready]", rendered)

    def test_render_role_board_for_worker_after_completion(self) -> None:
        with TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            install_agents(
                scope="project",
                project_root=project_root,
                agent_keys=["multi-agent-coordinator", "reviewer"],
            )
            enqueue_command(
                project_root=project_root,
                summary="Worker-specific review follow-up",
                role="reviewer",
            )
            open_dispatch(project_root=project_root)
            apply_result(
                project_root=project_root,
                dispatch_id="dispatch-001",
                outcome="completed",
                summary="Worker finished the review",
            )

            rendered = render_role_board(project_root, "reviewer")

            self.assertIn("Role: reviewer", rendered)
            self.assertIn("Kind: worker", rendered)
            self.assertIn("Status: idle", rendered)
            self.assertIn("cmd-001 [completed]", rendered)
            self.assertIn("dispatch-001 [completed]", rendered)
            self.assertIn("Worker finished the review", rendered)

    def test_render_role_board_rejects_unknown_role(self) -> None:
        with TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            install_agents(
                scope="project",
                project_root=project_root,
                agent_keys=["multi-agent-coordinator", "reviewer"],
            )

            with self.assertRaises(DashboardError):
                render_role_board(project_root, "missing-role")


if __name__ == "__main__":
    unittest.main()
