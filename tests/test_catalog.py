from __future__ import annotations

import unittest

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


if __name__ == "__main__":
    unittest.main()
