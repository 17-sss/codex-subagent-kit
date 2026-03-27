from __future__ import annotations

import io
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from codex_subagent_kit import cli
from codex_subagent_kit.catalog import get_agent_map
from codex_subagent_kit.catalog_sync import sync_catalog


class CatalogSyncTests(unittest.TestCase):
    def test_project_sync_copies_local_categories_tree(self) -> None:
        with TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            source_repo = project_root / "awesome-codex-subagents"
            categories_root = source_repo / "categories" / "11-custom-ops"
            categories_root.mkdir(parents=True)
            (categories_root / "README.md").write_text(
                "# 11. Custom Ops\n\nCustom synced operators.\n",
                encoding="utf-8",
            )
            (categories_root / "custom-syncer.toml").write_text(
                """
name = "custom-syncer"
description = "Custom synced agent"
model = "gpt-5.4"
model_reasoning_effort = "medium"
sandbox_mode = "read-only"
developer_instructions = "custom sync instructions"
""".strip()
                + "\n",
                encoding="utf-8",
            )

            result = sync_catalog(
                project_root=project_root,
                scope="project",
                source_root=source_repo,
            )

            self.assertEqual(result.source_name, "voltagent")
            self.assertEqual(len(result.copied_paths), 2)
            self.assertTrue((result.target_root / "11-custom-ops" / "custom-syncer.toml").exists())

    def test_synced_project_source_is_auto_discovered(self) -> None:
        with TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            source_root = project_root / "categories"
            category_dir = source_root / "11-custom-ops"
            category_dir.mkdir(parents=True)
            (category_dir / "README.md").write_text(
                "# 11. Custom Ops\n\nCustom synced operators.\n",
                encoding="utf-8",
            )
            (category_dir / "custom-syncer.toml").write_text(
                """
name = "custom-syncer"
description = "Custom synced agent"
model = "gpt-5.4"
model_reasoning_effort = "medium"
sandbox_mode = "read-only"
developer_instructions = "custom sync instructions"
""".strip()
                + "\n",
                encoding="utf-8",
            )

            sync_catalog(
                project_root=project_root,
                scope="project",
                source_root=source_root,
            )

            with patch.object(Path, "home", return_value=project_root / "home"):
                agent_map = get_agent_map(
                    project_root=project_root,
                    include_project=True,
                    include_global=True,
                )

            self.assertEqual(agent_map["custom-syncer"].source, "project-source:voltagent")
            self.assertEqual(agent_map["custom-syncer"].category, "custom-ops")

    def test_catalog_sync_cli_writes_project_source_root(self) -> None:
        with TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            categories_root = project_root / "categories" / "11-custom-ops"
            categories_root.mkdir(parents=True)
            (categories_root / "README.md").write_text(
                "# 11. Custom Ops\n\nCustom synced operators.\n",
                encoding="utf-8",
            )
            (categories_root / "custom-syncer.toml").write_text(
                """
name = "custom-syncer"
description = "Custom synced agent"
model = "gpt-5.4"
model_reasoning_effort = "medium"
sandbox_mode = "read-only"
developer_instructions = "custom sync instructions"
""".strip()
                + "\n",
                encoding="utf-8",
            )

            stdout_buffer = io.StringIO()
            stderr_buffer = io.StringIO()
            with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
                exit_code = cli.main(
                    [
                        "catalog",
                        "sync",
                        "--scope",
                        "project",
                        "--project-root",
                        temp_dir,
                        "--source-root",
                        str(project_root / "categories"),
                    ]
                )

            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr_buffer.getvalue(), "")
            self.assertIn("source: voltagent", stdout_buffer.getvalue())
            self.assertTrue(
                (
                    project_root
                    / ".codex"
                    / "subagent-kit"
                    / "sources"
                    / "voltagent"
                    / "categories"
                    / "11-custom-ops"
                    / "custom-syncer.toml"
                ).exists()
            )
