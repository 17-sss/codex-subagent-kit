from __future__ import annotations

import tomllib
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from codex_subagent_kit.templates import init_template


class TemplateInitTests(unittest.TestCase):
    def test_init_template_creates_project_local_category_and_agent(self) -> None:
        with TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)

            result = init_template(
                project_root=project_root,
                scope="project",
                category_key="custom-ops",
                agent_key="custom-coordinator",
            )

            self.assertEqual(
                result.target_root,
                project_root / ".codex" / "subagent-kit" / "catalog" / "categories",
            )
            self.assertEqual(result.category_dir.name, "11-custom-ops")
            self.assertTrue(result.readme_path.exists())
            self.assertTrue(result.agent_path.exists())
            self.assertIn("# 11. Custom Ops", result.readme_path.read_text(encoding="utf-8"))
            self.assertIn(
                'developer_instructions = """',
                result.agent_path.read_text(encoding="utf-8"),
            )

    def test_init_template_supports_explicit_catalog_root_and_orchestrator_override(self) -> None:
        with TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "project"
            catalog_root = Path(temp_dir) / "external-categories"

            result = init_template(
                project_root=project_root,
                scope="project",
                catalog_root=catalog_root,
                category_key="custom-ops",
                agent_key="custom-coordinator",
                orchestrator=True,
            )

            self.assertEqual(result.target_root, catalog_root.resolve())
            self.assertTrue(result.agent_path.exists())
            self.assertIn(
                'codex_subagent_kit_category = "meta-orchestration"',
                result.agent_path.read_text(encoding="utf-8"),
            )

    def test_init_template_preserves_existing_files_without_overwrite(self) -> None:
        with TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)

            first_result = init_template(
                project_root=project_root,
                scope="project",
                category_key="custom-ops",
                agent_key="custom-coordinator",
            )
            second_result = init_template(
                project_root=project_root,
                scope="project",
                category_key="custom-ops",
                agent_key="custom-coordinator",
            )

            self.assertTrue(first_result.agent_path.exists())
            self.assertIn(first_result.readme_path, second_result.preserved_paths)
            self.assertIn(first_result.agent_path, second_result.preserved_paths)

    def test_init_template_escapes_basic_string_fields(self) -> None:
        with TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)

            result = init_template(
                project_root=project_root,
                scope="project",
                category_key="custom-ops",
                agent_key="custom-coordinator",
                agent_name='custom "coordinator"',
                agent_description='Handles the "critical" path.',
            )

            parsed = tomllib.loads(result.agent_path.read_text(encoding="utf-8"))
            self.assertEqual(parsed["name"], 'custom "coordinator"')
            self.assertEqual(parsed["description"], 'Handles the "critical" path.')


if __name__ == "__main__":
    unittest.main()
