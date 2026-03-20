from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from codex_orchestrator.control_plane import ControlPlaneError, enqueue_command, load_queue_commands
from codex_orchestrator.generator import install_agents


class ControlPlaneTests(unittest.TestCase):
    def test_enqueue_defaults_to_orchestrator(self) -> None:
        with TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            install_agents(
                scope="project",
                project_root=project_root,
                agent_keys=["cto-coordinator", "reviewer"],
            )

            command_id, queue_path = enqueue_command(
                project_root=project_root,
                summary="Investigate the failing review flow",
            )

            self.assertEqual(command_id, "cmd-001")
            self.assertTrue(queue_path.exists())
            commands = load_queue_commands(project_root)
            self.assertEqual(len(commands), 1)
            self.assertEqual(commands[0]["role"], "cto-coordinator")
            self.assertEqual(commands[0]["status"], "pending")

    def test_enqueue_rejects_unknown_role(self) -> None:
        with TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            install_agents(
                scope="project",
                project_root=project_root,
                agent_keys=["cto-coordinator", "reviewer"],
            )

            with self.assertRaises(ControlPlaneError):
                enqueue_command(
                    project_root=project_root,
                    summary="Investigate the failing review flow",
                    role="missing-role",
                )


if __name__ == "__main__":
    unittest.main()
