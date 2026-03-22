from __future__ import annotations

import unittest

from codex_orchestrator.catalog import get_agents_by_category
from codex_orchestrator.tui import _default_agent_selection, _validate_agent_selection


class TuiTests(unittest.TestCase):
    def test_default_project_selection_prefers_cto_coordinator(self) -> None:
        agent_specs = get_agents_by_category()

        selected = _default_agent_selection("project", agent_specs)

        self.assertEqual(selected, {"cto-coordinator"})

    def test_project_selection_requires_meta_orchestration_agent(self) -> None:
        agent_specs = get_agents_by_category()

        message = _validate_agent_selection("project", agent_specs, {"reviewer"})

        self.assertIsNotNone(message)
        self.assertIn("meta-orchestration", message)
        self.assertIn("cto-coordinator", message)

    def test_project_selection_accepts_root_orchestrator(self) -> None:
        agent_specs = get_agents_by_category()

        message = _validate_agent_selection("project", agent_specs, {"cto-coordinator", "reviewer"})

        self.assertIsNone(message)

    def test_global_selection_does_not_require_meta_orchestration_agent(self) -> None:
        agent_specs = get_agents_by_category()

        message = _validate_agent_selection("global", agent_specs, {"reviewer"})

        self.assertIsNone(message)


if __name__ == "__main__":
    unittest.main()
