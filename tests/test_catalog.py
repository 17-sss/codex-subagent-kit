from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from codex_orchestrator.catalog import (
    get_agent_map,
    get_agents,
    get_agents_by_category,
    get_categories,
)


class CatalogTests(unittest.TestCase):
    def test_category_keys_are_unique(self) -> None:
        category_keys = [category.key for category in get_categories()]
        self.assertEqual(len(category_keys), len(set(category_keys)))

    def test_agent_keys_are_unique_and_indexed(self) -> None:
        agents = get_agents()
        agent_keys = [agent.key for agent in agents]

        self.assertEqual(len(agent_keys), len(set(agent_keys)))
        self.assertEqual(set(agent_keys), set(get_agent_map().keys()))

    def test_filtering_by_category_returns_matching_agents_only(self) -> None:
        filtered = get_agents_by_category({"quality-safety"})

        self.assertTrue(filtered)
        self.assertTrue(all(agent.category == "quality-safety" for agent in filtered))

    def test_external_agents_are_discovered_with_project_precedence(self) -> None:
        with TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            temp_home = project_root / "home"
            global_agents_dir = temp_home / ".codex" / "agents"
            project_agents_dir = project_root / ".codex" / "agents"
            global_agents_dir.mkdir(parents=True)
            project_agents_dir.mkdir(parents=True)

            (global_agents_dir / "reviewer.toml").write_text(
                """
name = "reviewer"
description = "Global reviewer override"
model = "gpt-5.4"
model_reasoning_effort = "high"
sandbox_mode = "read-only"
developer_instructions = "global instructions"
""".strip()
                + "\n",
                encoding="utf-8",
            )
            (project_agents_dir / "reviewer.toml").write_text(
                """
name = "reviewer"
description = "Project reviewer override"
model = "gpt-5.4"
model_reasoning_effort = "high"
sandbox_mode = "read-only"
developer_instructions = "project instructions"
""".strip()
                + "\n",
                encoding="utf-8",
            )
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
                agent_map = get_agent_map(
                    project_root=project_root,
                    include_project=True,
                    include_global=True,
                )
                categories = get_categories(
                    project_root=project_root,
                    include_project=True,
                    include_global=True,
                )

            self.assertEqual(agent_map["reviewer"].description, "Project reviewer override")
            self.assertEqual(agent_map["reviewer"].source, "project")
            self.assertEqual(agent_map["reviewer"].category, "quality-safety")
            self.assertEqual(agent_map["custom-helper"].source, "project")
            self.assertEqual(agent_map["custom-helper"].category, "imported-agents")
            self.assertIn("imported-agents", {category.key for category in categories})

    def test_flat_instructions_string_is_still_supported(self) -> None:
        with TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            project_agents_dir = project_root / ".codex" / "agents"
            project_agents_dir.mkdir(parents=True)

            (project_agents_dir / "flat-helper.toml").write_text(
                """
name = "flat-helper"
description = "Flat instructions field"
model = "gpt-5.4"
model_reasoning_effort = "medium"
sandbox_mode = "workspace-write"
instructions = "flat instructions"
""".strip()
                + "\n",
                encoding="utf-8",
            )

            agent_map = get_agent_map(
                project_root=project_root,
                include_project=True,
                include_global=False,
            )

            self.assertEqual(agent_map["flat-helper"].developer_instructions, "flat instructions")

    def test_legacy_nested_instructions_are_still_supported(self) -> None:
        with TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            project_agents_dir = project_root / ".codex" / "agents"
            project_agents_dir.mkdir(parents=True)

            (project_agents_dir / "legacy-helper.toml").write_text(
                """
name = "legacy-helper"
description = "Legacy nested instructions"
model = "gpt-5.4"
model_reasoning_effort = "medium"
sandbox_mode = "workspace-write"
[instructions]
text = "legacy instructions"
""".strip()
                + "\n",
                encoding="utf-8",
            )

            agent_map = get_agent_map(
                project_root=project_root,
                include_project=True,
                include_global=False,
            )

            self.assertEqual(agent_map["legacy-helper"].developer_instructions, "legacy instructions")


if __name__ == "__main__":
    unittest.main()
