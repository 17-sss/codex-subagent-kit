from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from codex_subagent_kit.generator import install_agents
from codex_subagent_kit.usage import UsageError, render_usage_guide


class UsageTests(unittest.TestCase):
    def test_usage_renders_starter_prompt_for_project_install(self) -> None:
        with TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            temp_home = project_root / "home"
            temp_home.mkdir()

            with patch.object(Path, "home", return_value=temp_home):
                install_agents(
                    scope="project",
                    project_root=project_root,
                    agent_keys=["multi-agent-coordinator", "reviewer"],
                )
                rendered = render_usage_guide(project_root=project_root, scope="project")

            self.assertIn("visible installed agents:", rendered)
            self.assertIn("multi-agent-coordinator", rendered)
            self.assertIn("starter prompt:", rendered)
            self.assertIn("Use multi-agent-coordinator as the root orchestrator", rendered)

    def test_usage_injects_task_text(self) -> None:
        with TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            temp_home = project_root / "home"
            temp_home.mkdir()

            with patch.object(Path, "home", return_value=temp_home):
                install_agents(
                    scope="project",
                    project_root=project_root,
                    agent_keys=["multi-agent-coordinator", "reviewer"],
                )
                rendered = render_usage_guide(
                    project_root=project_root,
                    scope="project",
                    task="Review the failing auth flow",
                )

            self.assertIn("Review the failing auth flow", rendered)

    def test_usage_fails_without_installed_agents(self) -> None:
        with TemporaryDirectory() as temp_dir:
            with self.assertRaises(UsageError):
                render_usage_guide(project_root=Path(temp_dir), scope="project")
