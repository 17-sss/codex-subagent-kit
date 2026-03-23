from __future__ import annotations

import unittest

from codex_subagent_kit.release_versioning import bump_semver, classify_bump, compute_next_version, parse_semver


class ReleaseVersioningTests(unittest.TestCase):
    def test_parse_semver_accepts_standard_versions(self) -> None:
        self.assertEqual(parse_semver("0.1.0"), (0, 1, 0))
        self.assertEqual(parse_semver("1.12.3"), (1, 12, 3))

    def test_parse_semver_rejects_invalid_versions(self) -> None:
        with self.assertRaises(ValueError):
            parse_semver("v1.0.0")

    def test_classify_bump_returns_major_for_breaking_change_footer(self) -> None:
        bump = classify_bump(["feat: add release automation\n\nBREAKING CHANGE: release tags now follow semver"])

        self.assertEqual(bump, "major")

    def test_classify_bump_returns_major_for_bang_subject(self) -> None:
        bump = classify_bump(["feat!: change install contract"])

        self.assertEqual(bump, "major")

    def test_classify_bump_returns_minor_for_feat(self) -> None:
        bump = classify_bump(["feat: add usage helper", "docs: update readme"])

        self.assertEqual(bump, "minor")

    def test_classify_bump_returns_patch_otherwise(self) -> None:
        bump = classify_bump(["fix: escape generated metadata strings", "docs: update testing guide"])

        self.assertEqual(bump, "patch")

    def test_bump_semver_increments_expected_component(self) -> None:
        self.assertEqual(bump_semver("0.1.0", "patch"), "0.1.1")
        self.assertEqual(bump_semver("0.1.0", "minor"), "0.2.0")
        self.assertEqual(bump_semver("0.1.0", "major"), "1.0.0")

    def test_compute_next_version_uses_classified_bump(self) -> None:
        version = compute_next_version("0.1.0", ["feat: add persistent catalog import"])

        self.assertEqual(version, "0.2.0")
