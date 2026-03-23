from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from codex_orchestrator.catalog_import import CatalogImportError, import_catalog


class CatalogImportTests(unittest.TestCase):
    def test_import_catalog_can_copy_selected_agents_into_project_catalog(self) -> None:
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

            result = import_catalog(
                project_root=project_root,
                scope="project",
                catalog_roots=(source_root,),
                agent_keys=["custom-helper"],
                category_keys=[],
            )

            target_dir = project_root / ".codex" / "orchestrator" / "catalog" / "categories" / "11-custom-ops"
            self.assertEqual(result.target_root, project_root / ".codex" / "orchestrator" / "catalog" / "categories")
            self.assertIn("custom-helper", result.imported_agent_keys)
            self.assertTrue((target_dir / "README.md").exists())
            self.assertTrue((target_dir / "custom-helper.toml").exists())

    def test_import_catalog_can_copy_full_category(self) -> None:
        with TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            temp_home = project_root / "home"
            temp_home.mkdir()
            source_root = project_root / "source-categories"
            category_dir = source_root / "11-custom-ops"
            category_dir.mkdir(parents=True)
            (category_dir / "README.md").write_text(
                "# 11. Custom Ops\n\nCustom external operators.\n",
                encoding="utf-8",
            )
            for key in ("custom-helper", "custom-reviewer"):
                (category_dir / f"{key}.toml").write_text(
                    f"""
name = "{key}"
description = "Imported {key}"
model = "gpt-5.4"
model_reasoning_effort = "medium"
sandbox_mode = "read-only"
developer_instructions = "instructions for {key}"
""".strip()
                    + "\n",
                    encoding="utf-8",
                )

            with patch.object(Path, "home", return_value=temp_home):
                result = import_catalog(
                    project_root=project_root,
                    scope="global",
                    catalog_roots=(source_root,),
                    agent_keys=[],
                    category_keys=["custom-ops"],
                )

            target_dir = temp_home / ".codex" / "orchestrator" / "catalog" / "categories" / "11-custom-ops"
            self.assertIn("custom-ops", result.imported_category_keys)
            self.assertTrue((target_dir / "custom-helper.toml").exists())
            self.assertTrue((target_dir / "custom-reviewer.toml").exists())

    def test_import_catalog_preserves_existing_files_without_overwrite(self) -> None:
        with TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            source_root = project_root / "source-categories"
            category_dir = source_root / "11-custom-ops"
            target_dir = project_root / ".codex" / "orchestrator" / "catalog" / "categories" / "11-custom-ops"
            category_dir.mkdir(parents=True)
            target_dir.mkdir(parents=True)
            (category_dir / "README.md").write_text("# 11. Custom Ops\n\nCustom external operators.\n", encoding="utf-8")
            (category_dir / "custom-helper.toml").write_text(
                """
name = "custom-helper"
description = "Updated helper"
model = "gpt-5.4"
model_reasoning_effort = "medium"
sandbox_mode = "read-only"
developer_instructions = "updated helper instructions"
""".strip()
                + "\n",
                encoding="utf-8",
            )
            existing_path = target_dir / "custom-helper.toml"
            existing_path.write_text("existing\n", encoding="utf-8")

            result = import_catalog(
                project_root=project_root,
                scope="project",
                catalog_roots=(source_root,),
                agent_keys=["custom-helper"],
                category_keys=[],
            )

            self.assertIn(existing_path, result.preserved_paths)
            self.assertEqual(existing_path.read_text(encoding="utf-8"), "existing\n")

    def test_import_catalog_rejects_missing_requested_agent(self) -> None:
        with TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            source_root = project_root / "source-categories"
            source_root.mkdir()

            with self.assertRaises(CatalogImportError):
                import_catalog(
                    project_root=project_root,
                    scope="project",
                    catalog_roots=(source_root,),
                    agent_keys=["missing-agent"],
                    category_keys=[],
                )
