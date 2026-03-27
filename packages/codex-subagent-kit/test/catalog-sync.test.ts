import assert from "node:assert/strict";
import { existsSync, mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import test from "node:test";

import { getAgentMap } from "../src/catalog";
import { syncCatalog } from "../src/catalog-sync";

function createTempRoot(): string {
  return mkdtempSync(join(tmpdir(), "codex-subagent-kit-ts-sync-"));
}

function cleanup(path: string): void {
  rmSync(path, { recursive: true, force: true });
}

test("catalog sync copies a local categories tree into the project source root", async () => {
  const root = createTempRoot();

  try {
    const sourceRoot = join(root, "awesome-codex-subagents", "categories", "11-custom-ops");
    mkdirSync(sourceRoot, { recursive: true });
    writeFileSync(sourceRoot + "/README.md", "# 11. Custom Ops\n\nCustom synced operators.\n", "utf8");
    writeFileSync(
      sourceRoot + "/custom-syncer.toml",
      [
        'name = "custom-syncer"',
        'description = "Custom synced agent"',
        'model = "gpt-5.4"',
        'model_reasoning_effort = "medium"',
        'sandbox_mode = "read-only"',
        'developer_instructions = "custom sync instructions"',
        "",
      ].join("\n"),
      "utf8",
    );

    const result = await syncCatalog({
      projectRoot: root,
      scope: "project",
      sourceRoot: join(root, "awesome-codex-subagents"),
    });

    assert.equal(result.sourceName, "voltagent");
    assert.equal(result.copiedPaths.length, 2);
    assert.ok(existsSync(join(result.targetRoot, "11-custom-ops", "custom-syncer.toml")));
  } finally {
    cleanup(root);
  }
});

test("synced project sources are auto-discovered by the catalog loader", async () => {
  const root = createTempRoot();

  try {
    const sourceRoot = join(root, "categories", "11-custom-ops");
    mkdirSync(sourceRoot, { recursive: true });
    writeFileSync(sourceRoot + "/README.md", "# 11. Custom Ops\n\nCustom synced operators.\n", "utf8");
    writeFileSync(
      sourceRoot + "/custom-syncer.toml",
      [
        'name = "custom-syncer"',
        'description = "Custom synced agent"',
        'model = "gpt-5.4"',
        'model_reasoning_effort = "medium"',
        'sandbox_mode = "read-only"',
        'developer_instructions = "custom sync instructions"',
        "",
      ].join("\n"),
      "utf8",
    );

    await syncCatalog({
      projectRoot: root,
      scope: "project",
      sourceRoot: join(root, "categories"),
    });

    const agentMap = getAgentMap({
      projectRoot: root,
      includeProject: true,
      includeGlobal: false,
    });

    assert.equal(agentMap.get("custom-syncer")?.source, "project-source:voltagent");
    assert.equal(agentMap.get("custom-syncer")?.category, "custom-ops");
  } finally {
    cleanup(root);
  }
});
