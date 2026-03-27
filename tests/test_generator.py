from __future__ import annotations

import tomllib
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from codex_subagent_kit.generator import (
    GenerationError,
    install_agents,
    render_agent_file,
    resolve_scaffold_catalog_dir,
    resolve_scaffold_dir,
    resolve_target_dir,
)
from codex_subagent_kit.models import AgentSpec


class GeneratorTests(unittest.TestCase):
    def test_project_install_creates_agent_files_and_scaffold(self) -> None:
        with TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)

            result = install_agents(
                scope="project",
                project_root=project_root,
                agent_keys=["multi-agent-coordinator", "reviewer", "code-mapper"],
            )

            self.assertEqual(
                result.agent_paths,
                [
                    project_root / ".codex" / "agents" / "multi-agent-coordinator.toml",
                    project_root / ".codex" / "agents" / "reviewer.toml",
                    project_root / ".codex" / "agents" / "code-mapper.toml",
                ],
            )
            self.assertTrue(all(path.exists() for path in result.agent_paths))
            self.assertEqual(result.orchestrator_key, "multi-agent-coordinator")
            self.assertTrue(result.scaffold_created_paths)

            reviewer_contents = (project_root / ".codex" / "agents" / "reviewer.toml").read_text(
                encoding="utf-8"
            )
            self.assertIn('developer_instructions = """', reviewer_contents)
            self.assertNotIn('\ninstructions = """', reviewer_contents)
            self.assertNotIn("[instructions]", reviewer_contents)

            team_manifest = (resolve_scaffold_dir(project_root) / "team.toml").read_text(encoding="utf-8")
            self.assertIn('orchestrator = "multi-agent-coordinator"', team_manifest)
            self.assertIn('"reviewer"', team_manifest)
            self.assertIn('"code-mapper"', team_manifest)

            runtime_state = (resolve_scaffold_dir(project_root) / "runtime" / "agents.toml").read_text(
                encoding="utf-8"
            )
            self.assertIn('key = "multi-agent-coordinator"', runtime_state)
            self.assertIn('status = "idle"', runtime_state)

            queue_seed = (resolve_scaffold_dir(project_root) / "queue" / "commands.toml").read_text(
                encoding="utf-8"
            )
            self.assertEqual(queue_seed, "version = 1\n")

            dispatch_seed = (resolve_scaffold_dir(project_root) / "ledger" / "dispatches.toml").read_text(
                encoding="utf-8"
            )
            self.assertEqual(dispatch_seed, "version = 1\n")

            tmux_launcher = resolve_scaffold_dir(project_root) / "launchers" / "launch-tmux.sh"
            self.assertTrue(tmux_launcher.exists())
            self.assertIn("run-board.sh multi-agent-coordinator", tmux_launcher.read_text(encoding="utf-8"))
            self.assertTrue(tmux_launcher.stat().st_mode & 0o111)

            board_runner = resolve_scaffold_dir(project_root) / "launchers" / "run-board.sh"
            self.assertTrue(board_runner.exists())
            self.assertIn("codex-subagent-kit", board_runner.read_text(encoding="utf-8"))

            self.assertTrue(resolve_scaffold_catalog_dir(project_root).exists())

    def test_existing_agent_file_is_preserved_on_rerun(self) -> None:
        with TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            install_agents(
                scope="project",
                project_root=project_root,
                agent_keys=["multi-agent-coordinator", "reviewer"],
            )

            second_result = install_agents(
                scope="project",
                project_root=project_root,
                agent_keys=["multi-agent-coordinator", "reviewer"],
            )
            self.assertEqual(second_result.agent_paths, [])
            self.assertEqual(
                second_result.agent_preserved_paths,
                [
                    project_root / ".codex" / "agents" / "multi-agent-coordinator.toml",
                    project_root / ".codex" / "agents" / "reviewer.toml",
                ],
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

    def test_project_install_without_orchestrator_skips_scaffold(self) -> None:
        with TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            result = install_agents(
                scope="project",
                project_root=project_root,
                agent_keys=["reviewer"],
            )

            self.assertEqual(
                result.agent_paths,
                [project_root / ".codex" / "agents" / "reviewer.toml"],
            )
            self.assertIsNone(result.orchestrator_key)
            self.assertEqual(result.scaffold_created_paths, [])
            self.assertEqual(result.scaffold_preserved_paths, [])
            self.assertFalse(resolve_scaffold_dir(project_root).exists())

    def test_global_install_skips_scaffold(self) -> None:
        with TemporaryDirectory() as temp_dir:
            temp_home = Path(temp_dir) / "home"
            temp_home.mkdir()
            with patch.object(Path, "home", return_value=temp_home):
                result = install_agents(
                    scope="global",
                    project_root=Path(temp_dir),
                    agent_keys=["reviewer"],
                )

            self.assertIsNone(result.orchestrator_key)
            self.assertEqual(
                result.agent_paths,
                [temp_home / ".codex" / "agents" / "reviewer.toml"],
            )
            self.assertEqual(result.agent_preserved_paths, [])
            self.assertEqual(result.scaffold_created_paths, [])
            self.assertEqual(result.scaffold_preserved_paths, [])

    def test_existing_scaffold_is_preserved_on_rerun(self) -> None:
        with TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            first_result = install_agents(
                scope="project",
                project_root=project_root,
                agent_keys=["multi-agent-coordinator", "reviewer"],
            )
            self.assertTrue(first_result.scaffold_created_paths)

            reviewer_path = project_root / ".codex" / "agents" / "reviewer.toml"
            reviewer_path.unlink()

            second_result = install_agents(
                scope="project",
                project_root=project_root,
                agent_keys=["multi-agent-coordinator", "reviewer"],
            )
            self.assertEqual(
                second_result.agent_preserved_paths,
                [
                    project_root / ".codex" / "agents" / "multi-agent-coordinator.toml",
                ],
            )
            self.assertFalse(second_result.scaffold_created_paths)
            self.assertTrue(second_result.scaffold_preserved_paths)

    def test_rerun_backfills_new_runtime_seed_files(self) -> None:
        with TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            scaffold_root = resolve_scaffold_dir(project_root)
            (scaffold_root / "runtime").mkdir(parents=True)
            (scaffold_root / "queue").mkdir()
            (scaffold_root / "ledger").mkdir()
            (scaffold_root / "launchers").mkdir()
            (scaffold_root / "team.toml").write_text(
                """
version = 1

[operator]
label = "user"

[team]
orchestrator = "multi-agent-coordinator"
workers = ["reviewer"]
""".strip()
                + "\n",
                encoding="utf-8",
            )
            (scaffold_root / "README.md").write_text("legacy\n", encoding="utf-8")

            result = install_agents(
                scope="project",
                project_root=project_root,
                agent_keys=["multi-agent-coordinator", "reviewer"],
            )

            self.assertIn(scaffold_root / "runtime" / "agents.toml", result.scaffold_created_paths)
            self.assertIn(scaffold_root / "queue" / "commands.toml", result.scaffold_created_paths)
            self.assertIn(scaffold_root / "ledger" / "dispatches.toml", result.scaffold_created_paths)
            self.assertIn(scaffold_root / "launchers" / "run-board.sh", result.scaffold_created_paths)
            self.assertIn(scaffold_root / "launchers" / "run-monitor.sh", result.scaffold_created_paths)
            self.assertIn(scaffold_root / "launchers" / "launch-tmux.sh", result.scaffold_created_paths)
            self.assertIn(scaffold_root / "launchers" / "launch-cmux.sh", result.scaffold_created_paths)
            self.assertIn(scaffold_root / "catalog" / "categories", result.scaffold_created_paths)

    def test_render_agent_file_escapes_basic_string_fields(self) -> None:
        rendered = render_agent_file(
            AgentSpec(
                key="quoted-agent",
                category="custom-ops",
                name='quoted "agent"',
                description='Handles the "critical" path.',
                model="gpt-5.4",
                reasoning_effort="medium",
                sandbox_mode="read-only",
                developer_instructions="Line 1\nLine 2",
            )
        )

        parsed = tomllib.loads(rendered)
        self.assertEqual(parsed["name"], 'quoted "agent"')
        self.assertEqual(parsed["description"], 'Handles the "critical" path.')


if __name__ == "__main__":
    unittest.main()
