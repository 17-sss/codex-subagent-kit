import { existsSync, readdirSync } from "node:fs";
import { homedir } from "node:os";
import { resolve } from "node:path";

export const TOOL_NAME = "codex-subagent-kit";
export const TOOL_DIR_NAME = "subagent-kit";
export const PACKAGE_NAME = "codex_subagent_kit";
export const CATEGORY_OVERRIDE_KEY = "codex_subagent_kit_category";
export const DEFAULT_SYNC_SOURCE_NAME = "voltagent";

export function resolveProjectToolDir(projectRoot: string): string {
  return resolve(projectRoot, ".codex", TOOL_DIR_NAME);
}

export function resolveGlobalToolDir(home: string = homedir()): string {
  return resolve(home, ".codex", TOOL_DIR_NAME);
}

export function resolveProjectCatalogDir(projectRoot: string): string {
  return resolve(resolveProjectToolDir(projectRoot), "catalog", "categories");
}

export function resolveGlobalCatalogDir(home?: string): string {
  return resolve(resolveGlobalToolDir(home), "catalog", "categories");
}

export function resolveProjectSourcesDir(projectRoot: string): string {
  return resolve(resolveProjectToolDir(projectRoot), "sources");
}

export function resolveGlobalSourcesDir(home?: string): string {
  return resolve(resolveGlobalToolDir(home), "sources");
}

export function resolveProjectSourceCategoriesDir(
  projectRoot: string,
  sourceName = DEFAULT_SYNC_SOURCE_NAME,
): string {
  return resolve(resolveProjectSourcesDir(projectRoot), sourceName, "categories");
}

export function resolveGlobalSourceCategoriesDir(
  sourceName = DEFAULT_SYNC_SOURCE_NAME,
  home?: string,
): string {
  return resolve(resolveGlobalSourcesDir(home), sourceName, "categories");
}

function resolveSourceCategoryDirs(root: string): string[] {
  try {
    return normalizeCatalogRoots(
      readdirSync(root, { withFileTypes: true })
        .filter((entry: { isDirectory(): boolean; name: string }) => entry.isDirectory())
        .map((entry: { name: string }) => resolve(root, entry.name, "categories"))
        .filter((categoriesRoot: string) => existsSync(categoriesRoot)),
    );
  } catch {
    return [];
  }
}

export function resolveProjectSourceCategoriesDirs(projectRoot: string): string[] {
  return resolveSourceCategoryDirs(resolveProjectSourcesDir(projectRoot));
}

export function resolveGlobalSourceCategoriesDirs(home?: string): string[] {
  return resolveSourceCategoryDirs(resolveGlobalSourcesDir(home));
}

export function resolveProjectAgentsDir(projectRoot: string): string {
  return resolve(projectRoot, ".codex", "agents");
}

export function resolveGlobalAgentsDir(home: string = homedir()): string {
  return resolve(home, ".codex", "agents");
}

export function normalizeCatalogRoots(roots?: readonly string[]): string[] {
  if (!roots) {
    return [];
  }
  return roots.filter((root) => root.trim()).map((root) => resolve(root));
}
