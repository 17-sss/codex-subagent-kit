import assert from "node:assert/strict";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import test from "node:test";

import { installAgents } from "../src/generator";
import { renderUsageGuide, UsageError } from "../src/usage";

function createTempRoot(): string {
  return mkdtempSync(join(tmpdir(), "codex-subagent-kit-ts-usage-"));
}

function cleanup(path: string): void {
  rmSync(path, { recursive: true, force: true });
}

test("renderUsageGuide shows starter prompts for a project install", () => {
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
    });

    assert.match(rendered, /visible installed agents:/);
    assert.match(rendered, /cto-coordinator/);
    assert.match(rendered, /starter prompt:/);
    assert.match(rendered, /Use cto-coordinator as the root orchestrator/);
  } finally {
    cleanup(root);
  }
});

test("renderUsageGuide injects the requested task text", () => {
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

    assert.match(rendered, /Review the failing auth flow/);
  } finally {
    cleanup(root);
  }
});

test("renderUsageGuide fails when no installed agents are visible", () => {
  const root = createTempRoot();

  try {
    assert.throws(
      () =>
        renderUsageGuide({
          projectRoot: root,
          homeDir: join(root, "home"),
          scope: "project",
        }),
      UsageError,
    );
  } finally {
    cleanup(root);
  }
});
