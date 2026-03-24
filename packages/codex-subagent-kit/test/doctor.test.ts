import assert from "node:assert/strict";
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import test from "node:test";

import { runDoctor, renderDoctorReport } from "../src/doctor";
import { installAgents } from "../src/generator";

function createTempRoot(): string {
  return mkdtempSync(join(tmpdir(), "codex-subagent-kit-ts-doctor-"));
}

function cleanup(path: string): void {
  rmSync(path, { recursive: true, force: true });
}

test("runDoctor reports ok for a fresh project install", () => {
  const root = createTempRoot();

  try {
    const homeDir = join(root, "home");
    installAgents({
      scope: "project",
      projectRoot: root,
      homeDir,
      agentKeys: ["cto-coordinator", "reviewer"],
    });

    const report = runDoctor({
      projectRoot: root,
      scope: "project",
      homeDir,
    });

    assert.equal(report.issues.length, 0);
    assert.match(renderDoctorReport(report), /status: ok/);
    assert.match(renderDoctorReport(report), /Issues: none/);
  } finally {
    cleanup(root);
  }
});

test("runDoctor reports malformed installed agents", () => {
  const root = createTempRoot();

  try {
    const homeDir = join(root, "home");
    mkdirSync(join(root, ".codex", "agents"), { recursive: true });
    writeFileSync(
      join(root, ".codex", "agents", "broken.toml"),
      [
        'name = "broken"',
        'description = "Broken agent"',
        'model = "gpt-5.4"',
        'model_reasoning_effort = "medium"',
        'sandbox_mode = "read-only"',
        "",
      ].join("\n"),
      "utf8",
    );

    const report = runDoctor({
      projectRoot: root,
      scope: "project",
      homeDir,
    });

    assert.ok(report.issues.some((issue) => issue.path?.endsWith("broken.toml")));
    assert.match(renderDoctorReport(report), /status: issues found/);
  } finally {
    cleanup(root);
  }
});
