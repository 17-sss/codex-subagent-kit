import assert from "node:assert/strict";
import { mkdtempSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import test from "node:test";

import * as TOML from "@iarna/toml";

import { renderAgentFile } from "../src/generator";
import { initTemplate } from "../src/templates";

function createTempRoot(): string {
  return mkdtempSync(join(tmpdir(), "codex-subagent-kit-ts-template-"));
}

function cleanup(path: string): void {
  rmSync(path, { recursive: true, force: true });
}

test("initTemplate creates a project-local category and agent scaffold", () => {
  const root = createTempRoot();

  try {
    const result = initTemplate({
      projectRoot: root,
      scope: "project",
      categoryKey: "custom-ops",
      agentKey: "custom-coordinator",
    });

    assert.equal(
      result.targetRoot,
      join(root, ".codex", "subagent-kit", "catalog", "categories"),
    );
    assert.equal(result.categoryDir.endsWith("11-custom-ops"), true);
    assert.match(readFileSync(result.readmePath, "utf8"), /# 11\. Custom Ops/);
    assert.match(readFileSync(result.agentPath, "utf8"), /developer_instructions = """/);
  } finally {
    cleanup(root);
  }
});

test("initTemplate supports an explicit catalog root and orchestrator override", () => {
  const root = createTempRoot();

  try {
    const projectRoot = join(root, "project");
    const catalogRoot = join(root, "external-categories");

    const result = initTemplate({
      projectRoot,
      scope: "project",
      catalogRoot,
      categoryKey: "custom-ops",
      agentKey: "custom-coordinator",
      orchestrator: true,
    });

    assert.equal(result.targetRoot, catalogRoot);
    assert.match(
      readFileSync(result.agentPath, "utf8"),
      /codex_subagent_kit_category = "meta-orchestration"/,
    );
  } finally {
    cleanup(root);
  }
});

test("initTemplate preserves existing files when overwrite is false", () => {
  const root = createTempRoot();

  try {
    const first = initTemplate({
      projectRoot: root,
      scope: "project",
      categoryKey: "custom-ops",
      agentKey: "custom-coordinator",
    });
    const second = initTemplate({
      projectRoot: root,
      scope: "project",
      categoryKey: "custom-ops",
      agentKey: "custom-coordinator",
    });

    assert.ok(second.preservedPaths.includes(first.readmePath));
    assert.ok(second.preservedPaths.includes(first.agentPath));
  } finally {
    cleanup(root);
  }
});

test("renderAgentFile escapes quoted strings safely", () => {
  const rendered = renderAgentFile({
    name: 'quoted "agent"',
    description: 'Handles the "critical" path.',
    model: "gpt-5.4",
    reasoningEffort: "medium",
    sandboxMode: "read-only",
    developerInstructions: "Line 1\nLine 2",
  });

  const parsed = TOML.parse(rendered) as Record<string, unknown>;
  assert.equal(parsed.name, 'quoted "agent"');
  assert.equal(parsed.description, 'Handles the "critical" path.');
});
