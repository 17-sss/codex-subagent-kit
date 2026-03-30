import assert from "node:assert/strict";
import test from "node:test";

import {
  bumpSemver,
  classifyReleaseLabels,
  computeNextVersionFromLabels,
  parseSemver,
} from "../src/release-versioning";

test("parseSemver accepts standard versions", () => {
  assert.deepEqual(parseSemver("0.1.0"), [0, 1, 0]);
  assert.deepEqual(parseSemver("1.12.3"), [1, 12, 3]);
});

test("parseSemver rejects invalid versions", () => {
  assert.throws(() => parseSemver("v1.0.0"));
});

test("classifyReleaseLabels returns patch when no label is provided", () => {
  assert.equal(classifyReleaseLabels([]), "patch");
});

test("classifyReleaseLabels returns major for release:major", () => {
  assert.equal(classifyReleaseLabels(["release:major"]), "major");
});

test("classifyReleaseLabels returns minor for release:minor", () => {
  assert.equal(classifyReleaseLabels(["release:minor"]), "minor");
});

test("classifyReleaseLabels returns patch for release:patch", () => {
  assert.equal(classifyReleaseLabels(["release:patch"]), "patch");
});

test("classifyReleaseLabels returns none for release:none", () => {
  assert.equal(classifyReleaseLabels(["release:none"]), "none");
});

test("classifyReleaseLabels rejects conflicting labels", () => {
  assert.throws(() => classifyReleaseLabels(["release:minor", "release:patch"]));
});

test("bumpSemver increments the expected component", () => {
  assert.equal(bumpSemver("0.1.0", "patch"), "0.1.1");
  assert.equal(bumpSemver("0.1.0", "minor"), "0.2.0");
  assert.equal(bumpSemver("0.1.0", "major"), "1.0.0");
});

test("computeNextVersionFromLabels uses the classified label", () => {
  assert.equal(computeNextVersionFromLabels("0.2.0", ["release:minor"]), "0.3.0");
});

test("computeNextVersionFromLabels can skip a release", () => {
  assert.equal(computeNextVersionFromLabels("0.2.0", ["release:none"]), null);
});

test("computeNextVersionFromLabels keeps the base version for the first release", () => {
  assert.equal(computeNextVersionFromLabels("0.2.0", [], { initialRelease: true }), "0.2.0");
});
