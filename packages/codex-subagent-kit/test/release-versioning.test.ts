import assert from "node:assert/strict";
import test from "node:test";

import {
  bumpSemver,
  classifyBump,
  computeNextVersion,
  parseSemver,
} from "../src/release-versioning";

test("parseSemver accepts standard versions", () => {
  assert.deepEqual(parseSemver("0.1.0"), [0, 1, 0]);
  assert.deepEqual(parseSemver("1.12.3"), [1, 12, 3]);
});

test("parseSemver rejects invalid versions", () => {
  assert.throws(() => parseSemver("v1.0.0"));
});

test("classifyBump returns major for breaking change footer", () => {
  const bump = classifyBump([
    "feat: add release automation\n\nBREAKING CHANGE: release tags now follow semver",
  ]);

  assert.equal(bump, "major");
});

test("classifyBump returns major for bang subject", () => {
  assert.equal(classifyBump(["feat!: change install contract"]), "major");
});

test("classifyBump returns minor for feat commits", () => {
  assert.equal(classifyBump(["feat: add usage helper", "docs: update readme"]), "minor");
});

test("classifyBump returns patch otherwise", () => {
  assert.equal(
    classifyBump(["fix: escape generated metadata strings", "docs: update testing guide"]),
    "patch",
  );
});

test("bumpSemver increments the expected component", () => {
  assert.equal(bumpSemver("0.1.0", "patch"), "0.1.1");
  assert.equal(bumpSemver("0.1.0", "minor"), "0.2.0");
  assert.equal(bumpSemver("0.1.0", "major"), "1.0.0");
});

test("computeNextVersion uses the classified bump", () => {
  assert.equal(computeNextVersion("0.1.0", ["feat: add persistent catalog import"]), "0.2.0");
});
