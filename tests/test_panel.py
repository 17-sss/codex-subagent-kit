from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from codex_subagent_kit.panel import PanelError, render_panel


class PanelTests(unittest.TestCase):
    def test_render_panel_from_generated_team_manifest(self) -> None:
        with TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            manifest_path = project_root / ".codex" / "subagent-kit" / "team.toml"
            manifest_path.parent.mkdir(parents=True)
            manifest_path.write_text(
                """
version = 1

[operator]
label = "user"

[team]
orchestrator = "cto-coordinator"
workers = ["reviewer", "code-mapper"]
""".strip()
                + "\n",
                encoding="utf-8",
            )

            rendered = render_panel(project_root)

            self.assertIn("Operator: user", rendered)
            self.assertIn("Orchestrator: cto-coordinator [idle]", rendered)
            self.assertIn("reviewer [idle]", rendered)
            self.assertIn("code-mapper [idle]", rendered)
            self.assertIn("Queue", rendered)
            self.assertIn("- pending: 0", rendered)
            self.assertIn("- dispatched: 0", rendered)
            self.assertIn("- failed: 0", rendered)
            self.assertIn("- cancelled: 0", rendered)
            self.assertIn("Dispatch Ledger", rendered)
            self.assertIn("- ready: 0", rendered)

    def test_render_panel_reads_runtime_queue_and_dispatch_state(self) -> None:
        with TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            orchestrator_root = project_root / ".codex" / "subagent-kit"
            (orchestrator_root / "runtime").mkdir(parents=True)
            (orchestrator_root / "queue").mkdir()
            (orchestrator_root / "ledger").mkdir()
            (orchestrator_root / "team.toml").write_text(
                """
version = 1

[operator]
label = "user"

[team]
orchestrator = "cto-coordinator"
workers = ["reviewer", "code-mapper"]
""".strip()
                + "\n",
                encoding="utf-8",
            )
            (orchestrator_root / "runtime" / "agents.toml").write_text(
                """
version = 1

[orchestrator]
key = "cto-coordinator"
status = "busy"

[[workers]]
key = "reviewer"
status = "busy"

[[workers]]
key = "code-mapper"
status = "idle"
""".strip()
                + "\n",
                encoding="utf-8",
            )
            (orchestrator_root / "queue" / "commands.toml").write_text(
                """
version = 1

[[commands]]
id = "cmd-1"
role = "reviewer"
status = "pending"

[[commands]]
id = "cmd-2"
role = "code-mapper"
status = "claimed"

[[commands]]
id = "cmd-3"
role = "reviewer"
status = "dispatched"

[[commands]]
id = "cmd-4"
role = "reviewer"
status = "completed"
""".strip()
                + "\n",
                encoding="utf-8",
            )
            (orchestrator_root / "ledger" / "dispatches.toml").write_text(
                """
version = 1

[[dispatches]]
id = "dispatch-1"
role = "reviewer"
status = "ready"

[[dispatches]]
id = "dispatch-2"
role = "reviewer"
status = "dispatched"

[[dispatches]]
id = "dispatch-3"
role = "code-mapper"
status = "completed"

[[dispatches]]
id = "dispatch-4"
role = "code-mapper"
status = "failed"
""".strip()
                + "\n",
                encoding="utf-8",
            )

            rendered = render_panel(project_root)

            self.assertIn("Orchestrator: cto-coordinator [busy]", rendered)
            self.assertIn("reviewer [busy]", rendered)
            self.assertIn("code-mapper [idle]", rendered)
            self.assertIn("- pending: 1", rendered)
            self.assertIn("- claimed: 1", rendered)
            self.assertIn("- dispatched: 1", rendered)
            self.assertIn("- completed: 1", rendered)
            self.assertIn("- failed: 0", rendered)
            self.assertIn("- cancelled: 0", rendered)
            self.assertIn("- ready: 1", rendered)
            self.assertIn("- dispatched: 1", rendered)
            self.assertIn("- completed: 1", rendered)
            self.assertIn("- failed: 1", rendered)

    def test_render_panel_requires_team_manifest(self) -> None:
        with TemporaryDirectory() as temp_dir:
            with self.assertRaises(PanelError):
                render_panel(Path(temp_dir))


if __name__ == "__main__":
    unittest.main()
