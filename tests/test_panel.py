from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from codex_orchestrator.panel import PanelError, render_panel


class PanelTests(unittest.TestCase):
    def test_render_panel_from_generated_team_manifest(self) -> None:
        with TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            manifest_path = project_root / ".codex" / "orchestrator" / "team.toml"
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
            self.assertIn("Orchestrator: cto-coordinator", rendered)
            self.assertIn("reviewer", rendered)
            self.assertIn("code-mapper", rendered)

    def test_render_panel_requires_team_manifest(self) -> None:
        with TemporaryDirectory() as temp_dir:
            with self.assertRaises(PanelError):
                render_panel(Path(temp_dir))


if __name__ == "__main__":
    unittest.main()
