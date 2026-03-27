import assert from "node:assert/strict";
import { existsSync, mkdtempSync, mkdirSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import test from "node:test";

import { buildProgram } from "../src/cli";

function createTempRoot(): string {
  return mkdtempSync(join(tmpdir(), "codex-subagent-kit-ts-cli-"));
}

function cleanup(path: string): void {
  rmSync(path, { recursive: true, force: true });
}

test("install command honors explicit project-root options", async () => {
  const root = createTempRoot();
  const output: string[] = [];
  const localRepoDotCodex = join(process.cwd(), ".codex");
  const originalLog = console.log;
  const originalExitCode = process.exitCode;

  console.log = (...args: unknown[]) => {
    output.push(args.map(String).join(" "));
  };
  process.exitCode = undefined;
  cleanup(localRepoDotCodex);

  try {
    const program = buildProgram();
    await program.parseAsync([
      "node",
      "codex-subagent-kit",
      "install",
      "--scope",
      "project",
      "--project-root",
      root,
      "--agents",
      "multi-agent-coordinator,reviewer",
    ]);

    assert.equal(process.exitCode ?? 0, 0);
    assert.ok(existsSync(join(root, ".codex", "agents", "reviewer.toml")));
    assert.ok(!existsSync(join(localRepoDotCodex, "agents", "reviewer.toml")));
    assert.ok(output.some((line) => line.includes(resolve(root, ".codex", "agents"))));
  } finally {
    console.log = originalLog;
    process.exitCode = originalExitCode;
    cleanup(localRepoDotCodex);
    cleanup(root);
  }
});

test("catalog sync command honors explicit project-root options", async () => {
  const root = createTempRoot();
  const output: string[] = [];
  const originalLog = console.log;
  const originalExitCode = process.exitCode;
  const sourceRoot = join(root, "categories", "11-custom-ops");

  mkdirSync(sourceRoot, { recursive: true });
  writeFileSync(join(sourceRoot, "README.md"), "# 11. Custom Ops\n\nCustom synced operators.\n", "utf8");
  writeFileSync(
    join(sourceRoot, "custom-syncer.toml"),
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

  console.log = (...args: unknown[]) => {
    output.push(args.map(String).join(" "));
  };
  process.exitCode = undefined;

  try {
    const program = buildProgram();
    await program.parseAsync([
      "node",
      "codex-subagent-kit",
      "catalog",
      "sync",
      "--scope",
      "project",
      "--project-root",
      root,
      "--source-root",
      join(root, "categories"),
    ]);

    assert.equal(process.exitCode ?? 0, 0);
    assert.ok(
      existsSync(
        join(
          root,
          ".codex",
          "subagent-kit",
          "sources",
          "voltagent",
          "categories",
          "11-custom-ops",
          "custom-syncer.toml",
        ),
      ),
    );
    assert.ok(output.some((line) => line.includes("source: voltagent")));
  } finally {
    console.log = originalLog;
    process.exitCode = originalExitCode;
    cleanup(root);
  }
});
