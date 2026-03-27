import assert from "node:assert/strict";
import { existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import test from "node:test";

import * as TOML from "@iarna/toml";

import { GenerationError, installAgents, resolveScaffoldDir } from "../src/generator";

function createTempRoot(): string {
  return mkdtempSync(join(tmpdir(), "codex-subagent-kit-ts-install-"));
}

function cleanup(path: string): void {
  rmSync(path, { recursive: true, force: true });
}

test("installAgents creates project agent files and scaffold", () => {
  const root = createTempRoot();

  try {
    const result = installAgents({
      scope: "project",
      projectRoot: root,
      homeDir: join(root, "home"),
      agentKeys: ["multi-agent-coordinator", "reviewer", "code-mapper"],
    });

    assert.equal(result.orchestratorKey, "multi-agent-coordinator");
    assert.ok(result.agentPaths.some((path) => path.endsWith("reviewer.toml")));
    assert.ok(result.scaffoldCreatedPaths.some((path) => path.endsWith("team.toml")));
    assert.ok(existsSync(join(root, ".codex", "agents", "reviewer.toml")));
    assert.match(
      readFileSync(join(root, ".codex", "agents", "reviewer.toml"), "utf8"),
      /developer_instructions = """/,
    );
    assert.match(
      readFileSync(join(resolveScaffoldDir(root), "team.toml"), "utf8"),
      /orchestrator = "multi-agent-coordinator"/,
    );
  } finally {
    cleanup(root);
  }
});

test("installAgents supports project installs without an orchestrator and skips scaffold", () => {
  const root = createTempRoot();

  try {
    const result = installAgents({
      scope: "project",
      projectRoot: root,
      homeDir: join(root, "home"),
      agentKeys: ["reviewer"],
    });

    assert.equal(result.orchestratorKey, undefined);
    assert.equal(result.scaffoldCreatedPaths.length, 0);
    assert.equal(result.scaffoldPreservedPaths.length, 0);
    assert.ok(existsSync(join(root, ".codex", "agents", "reviewer.toml")));
  } finally {
    cleanup(root);
  }
});

test("installAgents supports external catalog roots", () => {
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
      join(categoryDir, "custom-coordinator.toml"),
      [
        'name = "custom-coordinator"',
        'description = "Custom orchestrator"',
        'model = "gpt-5.4"',
        'model_reasoning_effort = "high"',
        'sandbox_mode = "read-only"',
        'developer_instructions = "Coordinate custom injected work."',
        'codex_subagent_kit_category = "meta-orchestration"',
        "",
      ].join("\n"),
      "utf8",
    );

    const result = installAgents({
      scope: "project",
      projectRoot: root,
      homeDir: join(root, "home"),
      catalogRoots: [catalogRoot],
      agentKeys: ["custom-coordinator"],
    });

    assert.ok(result.agentPaths.some((path) => path.endsWith("custom-coordinator.toml")));
    assert.ok(existsSync(join(root, ".codex", "agents", "custom-coordinator.toml")));
  } finally {
    cleanup(root);
  }
});

test("rendered installed TOML remains parseable", () => {
  const root = createTempRoot();

  try {
    installAgents({
      scope: "project",
      projectRoot: root,
      homeDir: join(root, "home"),
      agentKeys: ["multi-agent-coordinator", "reviewer"],
    });

    const parsed = TOML.parse(readFileSync(join(root, ".codex", "agents", "reviewer.toml"), "utf8")) as Record<
      string,
      unknown
    >;
    assert.equal(parsed.name, "reviewer");
    assert.equal(typeof parsed.developer_instructions, "string");
  } finally {
    cleanup(root);
  }
});
