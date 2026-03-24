import { homedir } from "node:os";
import { resolve } from "node:path";

export const TOOL_NAME = "codex-subagent-kit";
export const TOOL_DIR_NAME = "subagent-kit";
export const PACKAGE_NAME = "codex_subagent_kit";
export const CATEGORY_OVERRIDE_KEY = "codex_subagent_kit_category";

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
