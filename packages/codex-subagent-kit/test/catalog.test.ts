import assert from "node:assert/strict";
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import test from "node:test";

import { getAgentMap, getCategories, renderCatalogOutput } from "../src/catalog";

function createTempRoot(): string {
  return mkdtempSync(join(tmpdir(), "codex-subagent-kit-ts-"));
}

function cleanup(path: string): void {
  rmSync(path, { recursive: true, force: true });
}

test("builtin catalog exposes known stable agents", () => {
  const agentMap = getAgentMap();
  const categories = getCategories();

  assert.equal(agentMap.get("cto-coordinator")?.source, "builtin");
  assert.ok(categories.some((category) => category.key === "meta-orchestration"));
  assert.ok(categories.some((category) => category.key === "core-development"));
});

test("external catalog roots are loaded into the rendered catalog output", () => {
  const root = createTempRoot();

  try {
    const catalogRoot = join(root, "categories");
    const categoryDir = join(catalogRoot, "11-custom-ops");
    mkdirSync(categoryDir, { recursive: true });
    writeFileSync(
      join(categoryDir, "README.md"),
      "# 11. Custom Ops\n\nCustom externally injected operators.\n",
      "utf8",
    );
    writeFileSync(
      join(categoryDir, "custom-operator.toml"),
      [
        'name = "custom-operator"',
        'description = "Custom injected agent"',
        'model = "gpt-5.4"',
        'model_reasoning_effort = "medium"',
        'sandbox_mode = "read-only"',
        'developer_instructions = "custom injected instructions"',
        "",
      ].join("\n"),
      "utf8",
    );

    const agentMap = getAgentMap({ catalogRoots: [catalogRoot] });
    const output = renderCatalogOutput({ catalogRoots: [catalogRoot] });

    assert.equal(agentMap.get("custom-operator")?.source, "catalog-root");
    assert.equal(agentMap.get("custom-operator")?.category, "custom-ops");
    assert.match(output, /\[Custom Ops\]/);
    assert.match(output, /custom-operator: Custom injected agent \[catalog-root\]/);
  } finally {
    cleanup(root);
  }
});

test("project agent definitions override global agent definitions", () => {
  const root = createTempRoot();

  try {
    const projectRoot = join(root, "project");
    const homeDir = join(root, "home");
    const projectAgentsDir = join(projectRoot, ".codex", "agents");
    const globalAgentsDir = join(homeDir, ".codex", "agents");
    mkdirSync(projectAgentsDir, { recursive: true });
    mkdirSync(globalAgentsDir, { recursive: true });

    writeFileSync(
      join(globalAgentsDir, "reviewer.toml"),
      [
        'name = "reviewer"',
        'description = "Global reviewer override"',
        'model = "gpt-5.4"',
        'model_reasoning_effort = "high"',
        'sandbox_mode = "read-only"',
        'developer_instructions = "global instructions"',
        "",
      ].join("\n"),
      "utf8",
    );
    writeFileSync(
      join(projectAgentsDir, "reviewer.toml"),
      [
        'name = "reviewer"',
        'description = "Project reviewer override"',
        'model = "gpt-5.4"',
        'model_reasoning_effort = "high"',
        'sandbox_mode = "read-only"',
        'developer_instructions = "project instructions"',
        "",
      ].join("\n"),
      "utf8",
    );
    writeFileSync(
      join(projectAgentsDir, "custom-helper.toml"),
      [
        'name = "custom-helper"',
        'description = "Project custom helper"',
        'model = "gpt-5.4"',
        'model_reasoning_effort = "medium"',
        'sandbox_mode = "workspace-write"',
        'developer_instructions = "custom helper instructions"',
        "",
      ].join("\n"),
      "utf8",
    );

    const agentMap = getAgentMap({
      projectRoot,
      homeDir,
      includeProject: true,
      includeGlobal: true,
    });
    const categories = getCategories({
      projectRoot,
      homeDir,
      includeProject: true,
      includeGlobal: true,
    });

    assert.equal(agentMap.get("reviewer")?.description, "Project reviewer override");
    assert.equal(agentMap.get("reviewer")?.source, "project");
    assert.equal(agentMap.get("custom-helper")?.category, "imported-agents");
    assert.ok(categories.some((category) => category.key === "imported-agents"));
  } finally {
    cleanup(root);
  }
});
