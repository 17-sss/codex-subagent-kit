import assert from "node:assert/strict";
import { mkdtempSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import test from "node:test";

import { renderDoctorReport, runDoctor } from "../src/doctor";
import { installAgents } from "../src/generator";
import { renderUsageGuide } from "../src/usage";

const GOLDEN_FIXTURES_DIR = resolve(__dirname, "..", "..", "..", "tests", "fixtures", "golden");

function createTempRoot(): string {
  return mkdtempSync(join(tmpdir(), "codex-subagent-kit-ts-parity-"));
}

function cleanup(path: string): void {
  rmSync(path, { recursive: true, force: true });
}

function loadFixture(name: string): string {
  return readFileSync(join(GOLDEN_FIXTURES_DIR, name), "utf8");
}

test("TypeScript install output matches the reviewer golden TOML fixture", () => {
  const root = createTempRoot();

  try {
    const homeDir = join(root, "home");
    installAgents({
      scope: "project",
      projectRoot: root,
      homeDir,
      agentKeys: ["cto-coordinator", "reviewer"],
    });

    const rendered = readFileSync(join(root, ".codex", "agents", "reviewer.toml"), "utf8");
    assert.equal(rendered, loadFixture("generated_reviewer.toml"));
  } finally {
    cleanup(root);
  }
});

test("TypeScript usage output matches the shared project usage fixture", () => {
  const root = createTempRoot();

  try {
    const homeDir = join(root, "home");
    installAgents({
      scope: "project",
      projectRoot: root,
      homeDir,
      agentKeys: ["cto-coordinator", "reviewer"],
    });

    const rendered = renderUsageGuide({
      projectRoot: root,
      homeDir,
      scope: "project",
      task: "Review the failing auth flow",
    });

    assert.equal(rendered, loadFixture("usage_project.txt").trimEnd());
  } finally {
    cleanup(root);
  }
});

test("TypeScript doctor output matches the shared project doctor fixture", () => {
  const root = createTempRoot();

  try {
    const homeDir = join(root, "home");
    installAgents({
      scope: "project",
      projectRoot: root,
      homeDir,
      agentKeys: ["cto-coordinator", "reviewer"],
    });

    const rendered = renderDoctorReport(
      runDoctor({
        projectRoot: root,
        homeDir,
        scope: "project",
      }),
    );
    const normalized = rendered.replaceAll(root, "<PROJECT_ROOT>");

    assert.equal(normalized, loadFixture("doctor_project_ok.txt").trimEnd());
  } finally {
    cleanup(root);
  }
});
