from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from codex_orchestrator.generator import GenerationError, install_agents, resolve_target_dir


class GeneratorTests(unittest.TestCase):
    def test_project_install_creates_agent_files(self) -> None:
        with TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)

            created_paths = install_agents(
                scope="project",
                project_root=project_root,
                agent_keys=["reviewer", "code-mapper"],
            )

            self.assertEqual(
                created_paths,
                [
                    project_root / ".codex" / "agents" / "reviewer.toml",
                    project_root / ".codex" / "agents" / "code-mapper.toml",
                ],
            )
            self.assertTrue(all(path.exists() for path in created_paths))

    def test_existing_file_requires_overwrite(self) -> None:
        with TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            install_agents(
                scope="project",
                project_root=project_root,
                agent_keys=["reviewer"],
            )

            with self.assertRaises(GenerationError):
                install_agents(
                    scope="project",
                    project_root=project_root,
                    agent_keys=["reviewer"],
                )

    def test_unknown_agent_raises_error(self) -> None:
        with TemporaryDirectory() as temp_dir:
            with self.assertRaises(GenerationError):
                install_agents(
                    scope="project",
                    project_root=Path(temp_dir),
                    agent_keys=["missing-agent"],
                )

    def test_resolve_target_dir_rejects_unknown_scope(self) -> None:
        with TemporaryDirectory() as temp_dir:
            with self.assertRaises(GenerationError):
                resolve_target_dir("invalid", Path(temp_dir))


if __name__ == "__main__":
    unittest.main()
