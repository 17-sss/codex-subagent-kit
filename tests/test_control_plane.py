from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from codex_orchestrator.control_plane import (
    apply_result,
    ControlPlaneError,
    enqueue_command,
    load_dispatches,
    load_queue_commands,
    load_runtime_agents,
    open_dispatch,
)
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

    def test_open_dispatch_promotes_first_pending_command(self) -> None:
        with TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            install_agents(
                scope="project",
                project_root=project_root,
                agent_keys=["cto-coordinator", "reviewer"],
            )
            enqueue_command(
                project_root=project_root,
                summary="Investigate the failing review flow",
            )

            dispatch_id, command_id, queue_path, ledger_path = open_dispatch(project_root=project_root)

            self.assertEqual(dispatch_id, "dispatch-001")
            self.assertEqual(command_id, "cmd-001")
            self.assertTrue(queue_path.exists())
            self.assertTrue(ledger_path.exists())

            commands = load_queue_commands(project_root)
            self.assertEqual(commands[0]["status"], "claimed")
            self.assertEqual(commands[0]["dispatch_id"], "dispatch-001")

            dispatches = load_dispatches(project_root)
            self.assertEqual(len(dispatches), 1)
            self.assertEqual(dispatches[0]["id"], "dispatch-001")
            self.assertEqual(dispatches[0]["command_id"], "cmd-001")
            self.assertEqual(dispatches[0]["status"], "ready")

            orchestrator_state, _ = load_runtime_agents(project_root)
            self.assertEqual(orchestrator_state["status"], "busy")
            self.assertEqual(orchestrator_state["active_dispatch_id"], "dispatch-001")

    def test_open_dispatch_rejects_missing_pending_command(self) -> None:
        with TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            install_agents(
                scope="project",
                project_root=project_root,
                agent_keys=["cto-coordinator", "reviewer"],
            )

            with self.assertRaises(ControlPlaneError):
                open_dispatch(project_root=project_root)

    def test_apply_result_updates_queue_dispatch_and_runtime(self) -> None:
        with TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            install_agents(
                scope="project",
                project_root=project_root,
                agent_keys=["cto-coordinator", "reviewer"],
            )
            enqueue_command(
                project_root=project_root,
                summary="Investigate the failing review flow",
            )
            open_dispatch(project_root=project_root)

            dispatch_id, command_id, queue_path, ledger_path, runtime_path = apply_result(
                project_root=project_root,
                dispatch_id="dispatch-001",
                outcome="completed",
                summary="Review finished and reported back",
            )

            self.assertEqual(dispatch_id, "dispatch-001")
            self.assertEqual(command_id, "cmd-001")
            self.assertTrue(queue_path.exists())
            self.assertTrue(ledger_path.exists())
            self.assertTrue(runtime_path.exists())

            commands = load_queue_commands(project_root)
            self.assertEqual(commands[0]["status"], "completed")

            dispatches = load_dispatches(project_root)
            self.assertEqual(dispatches[0]["status"], "completed")
            self.assertEqual(dispatches[0]["result_summary"], "Review finished and reported back")

            orchestrator_state, _ = load_runtime_agents(project_root)
            self.assertEqual(orchestrator_state["status"], "idle")
            self.assertNotIn("active_dispatch_id", orchestrator_state)

    def test_apply_result_rejects_finalized_dispatch(self) -> None:
        with TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            install_agents(
                scope="project",
                project_root=project_root,
                agent_keys=["cto-coordinator", "reviewer"],
            )
            enqueue_command(
                project_root=project_root,
                summary="Investigate the failing review flow",
            )
            open_dispatch(project_root=project_root)
            apply_result(
                project_root=project_root,
                dispatch_id="dispatch-001",
                outcome="completed",
                summary="Review finished and reported back",
            )

            with self.assertRaises(ControlPlaneError):
                apply_result(
                    project_root=project_root,
                    dispatch_id="dispatch-001",
                    outcome="failed",
                    summary="late retry should fail",
                )


if __name__ == "__main__":
    unittest.main()
