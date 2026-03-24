import assert from "node:assert/strict";
import { mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import test from "node:test";

import { CatalogImportError, importCatalog } from "../src/catalog-import";

function createTempRoot(): string {
  return mkdtempSync(join(tmpdir(), "codex-subagent-kit-ts-catalog-import-"));
}

function cleanup(path: string): void {
  rmSync(path, { recursive: true, force: true });
}

test("importCatalog can copy selected agents into the project catalog", () => {
  const root = createTempRoot();

  try {
    const sourceRoot = join(root, "source-categories");
    const categoryDir = join(sourceRoot, "11-custom-ops");
    mkdirSync(categoryDir, { recursive: true });
    writeFileSync(join(categoryDir, "README.md"), "# 11. Custom Ops\n\nCustom external operators.\n", "utf8");
    writeFileSync(
      join(categoryDir, "custom-helper.toml"),
      [
        'name = "custom-helper"',
        'description = "Custom helper"',
        'model = "gpt-5.4"',
        'model_reasoning_effort = "medium"',
        'sandbox_mode = "read-only"',
        'developer_instructions = "custom helper instructions"',
        "",
      ].join("\n"),
      "utf8",
    );

    const result = importCatalog({
      projectRoot: root,
      scope: "project",
      catalogRoots: [sourceRoot],
      agentKeys: ["custom-helper"],
      categoryKeys: [],
    });

    const targetDir = join(root, ".codex", "subagent-kit", "catalog", "categories", "11-custom-ops");
    assert.equal(result.targetRoot, join(root, ".codex", "subagent-kit", "catalog", "categories"));
    assert.ok(result.importedAgentKeys.includes("custom-helper"));
    assert.ok(readFileSync(join(targetDir, "README.md"), "utf8").includes("Custom external operators."));
  } finally {
    cleanup(root);
  }
});

test("importCatalog can copy a full category into the global catalog", () => {
  const root = createTempRoot();

  try {
    const sourceRoot = join(root, "source-categories");
    const homeDir = join(root, "home");
    const categoryDir = join(sourceRoot, "11-custom-ops");
    mkdirSync(categoryDir, { recursive: true });
    writeFileSync(join(categoryDir, "README.md"), "# 11. Custom Ops\n\nCustom external operators.\n", "utf8");
    for (const key of ["custom-helper", "custom-reviewer"]) {
      writeFileSync(
        join(categoryDir, `${key}.toml`),
        [
          `name = "${key}"`,
          `description = "Imported ${key}"`,
          'model = "gpt-5.4"',
          'model_reasoning_effort = "medium"',
          'sandbox_mode = "read-only"',
          `developer_instructions = "instructions for ${key}"`,
          "",
        ].join("\n"),
        "utf8",
      );
    }

    const result = importCatalog({
      projectRoot: root,
      scope: "global",
      homeDir,
      catalogRoots: [sourceRoot],
      agentKeys: [],
      categoryKeys: ["custom-ops"],
    });

    const targetDir = join(homeDir, ".codex", "subagent-kit", "catalog", "categories", "11-custom-ops");
    assert.ok(result.importedCategoryKeys.includes("custom-ops"));
    assert.ok(readFileSync(join(targetDir, "custom-helper.toml"), "utf8").includes("Imported custom-helper"));
    assert.ok(readFileSync(join(targetDir, "custom-reviewer.toml"), "utf8").includes("Imported custom-reviewer"));
  } finally {
    cleanup(root);
  }
});

test("importCatalog preserves existing files without overwrite", () => {
  const root = createTempRoot();

  try {
    const sourceRoot = join(root, "source-categories");
    const categoryDir = join(sourceRoot, "11-custom-ops");
    const targetDir = join(root, ".codex", "subagent-kit", "catalog", "categories", "11-custom-ops");
    mkdirSync(categoryDir, { recursive: true });
    mkdirSync(targetDir, { recursive: true });
    writeFileSync(join(categoryDir, "README.md"), "# 11. Custom Ops\n\nCustom external operators.\n", "utf8");
    writeFileSync(
      join(categoryDir, "custom-helper.toml"),
      [
        'name = "custom-helper"',
        'description = "Updated helper"',
        'model = "gpt-5.4"',
        'model_reasoning_effort = "medium"',
        'sandbox_mode = "read-only"',
        'developer_instructions = "updated helper instructions"',
        "",
      ].join("\n"),
      "utf8",
    );
    const existingPath = join(targetDir, "custom-helper.toml");
    writeFileSync(existingPath, "existing\n", "utf8");

    const result = importCatalog({
      projectRoot: root,
      scope: "project",
      catalogRoots: [sourceRoot],
      agentKeys: ["custom-helper"],
      categoryKeys: [],
    });

    assert.ok(result.preservedPaths.includes(existingPath));
    assert.equal(readFileSync(existingPath, "utf8"), "existing\n");
  } finally {
    cleanup(root);
  }
});

test("importCatalog rejects missing requested agent keys", () => {
  const root = createTempRoot();

  try {
    const sourceRoot = join(root, "source-categories");
    mkdirSync(sourceRoot, { recursive: true });

    assert.throws(
      () =>
        importCatalog({
          projectRoot: root,
          scope: "project",
          catalogRoots: [sourceRoot],
          agentKeys: ["missing-agent"],
          categoryKeys: [],
        }),
      CatalogImportError,
    );
  } finally {
    cleanup(root);
  }
});
