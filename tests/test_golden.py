from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from codex_orchestrator.doctor import render_doctor_report, run_doctor
from codex_orchestrator.generator import install_agents
from codex_orchestrator.usage import render_usage_guide


FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures" / "golden"


def _load_fixture(name: str) -> str:
    return (FIXTURES_DIR / name).read_text(encoding="utf-8")


class GoldenContractTests(unittest.TestCase):
    maxDiff = None

    def test_generated_reviewer_toml_matches_golden_fixture(self) -> None:
        with TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            temp_home = project_root / "home"
            temp_home.mkdir()

            with patch.object(Path, "home", return_value=temp_home):
                install_agents(
                    scope="project",
                    project_root=project_root,
                    agent_keys=["cto-coordinator", "reviewer"],
                )
                rendered = (project_root / ".codex" / "agents" / "reviewer.toml").read_text(encoding="utf-8")

        self.assertEqual(rendered, _load_fixture("generated_reviewer.toml"))

    def test_usage_output_matches_golden_fixture(self) -> None:
        with TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            temp_home = project_root / "home"
            temp_home.mkdir()

            with patch.object(Path, "home", return_value=temp_home):
                install_agents(
                    scope="project",
                    project_root=project_root,
                    agent_keys=["cto-coordinator", "reviewer"],
                )
                rendered = render_usage_guide(
                    project_root=project_root,
                    scope="project",
                    task="Review the failing auth flow",
                )

        self.assertEqual(rendered, _load_fixture("usage_project.txt").rstrip("\n"))

    def test_doctor_output_matches_golden_fixture(self) -> None:
        with TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            temp_home = project_root / "home"
            temp_home.mkdir()

            with patch.object(Path, "home", return_value=temp_home):
                install_agents(
                    scope="project",
                    project_root=project_root,
                    agent_keys=["cto-coordinator", "reviewer"],
                )
                rendered = render_doctor_report(run_doctor(project_root=project_root, scope="project"))

        normalized = rendered.replace(str(project_root), "<PROJECT_ROOT>")
        self.assertEqual(normalized, _load_fixture("doctor_project_ok.txt").rstrip("\n"))
