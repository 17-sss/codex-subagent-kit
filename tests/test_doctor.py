from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from codex_orchestrator.doctor import render_doctor_report, run_doctor
from codex_orchestrator.generator import install_agents


class DoctorTests(unittest.TestCase):
    def test_doctor_reports_ok_for_fresh_project_install(self) -> None:
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
                report = run_doctor(project_root=project_root, scope="project")

            self.assertTrue(report.ok)
            rendered = render_doctor_report(report)
            self.assertIn("status: ok", rendered)
            self.assertIn("Issues: none", rendered)

    def test_doctor_reports_malformed_project_agent(self) -> None:
        with TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            temp_home = project_root / "home"
            project_agents_dir = project_root / ".codex" / "agents"
            project_agents_dir.mkdir(parents=True)
            temp_home.mkdir()

            (project_agents_dir / "broken.toml").write_text(
                """
name = "broken"
description = "Broken agent"
model = "gpt-5.4"
model_reasoning_effort = "medium"
sandbox_mode = "read-only"
""".strip()
                + "\n",
                encoding="utf-8",
            )

            with patch.object(Path, "home", return_value=temp_home):
                report = run_doctor(project_root=project_root, scope="project")

            self.assertFalse(report.ok)
            rendered = render_doctor_report(report)
            self.assertIn("broken.toml", rendered)
            self.assertIn("missing instructions text", rendered)

    def test_doctor_reports_missing_explicit_catalog_root(self) -> None:
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
                missing_root = project_root / "missing-categories"
                report = run_doctor(
                    project_root=project_root,
                    scope="project",
                    catalog_roots=(missing_root,),
                )

            self.assertFalse(report.ok)
            rendered = render_doctor_report(report)
            self.assertIn(str(missing_root), rendered)
            self.assertIn("catalog root does not exist", rendered)
