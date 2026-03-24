import assert from "node:assert/strict";
import { existsSync, mkdtempSync, rmSync } from "node:fs";
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
      "cto-coordinator,reviewer",
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
