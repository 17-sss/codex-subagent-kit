import { copyFileSync, existsSync, mkdirSync, readdirSync, statSync } from "node:fs";
import { basename, dirname, resolve } from "node:path";

import { parseAgentFile, parseCategoryDir } from "./catalog";
import type { CatalogImportResult } from "./models";
import {
  normalizeCatalogRoots,
  resolveGlobalCatalogDir,
  resolveProjectCatalogDir,
} from "./paths";

export class CatalogImportError extends Error {}

interface CategorySource {
  key: string;
  directory: string;
  readmePath?: string;
}

interface AgentSource {
  key: string;
  path: string;
  categoryKey: string;
  categoryDirectory: string;
  readmePath?: string;
}

function resolveTargetRoot(projectRoot: string, scope: "project" | "global", homeDir?: string): string {
  if (scope === "project") {
    return resolveProjectCatalogDir(projectRoot);
  }
  if (scope === "global") {
    return resolveGlobalCatalogDir(homeDir);
  }
  throw new CatalogImportError(`unsupported scope: ${scope}`);
}

function categoryKeyFromDir(directoryName: string): string {
  const match = directoryName.match(/^(\d+)-(.*)$/);
  return match ? match[2] : directoryName;
}

function resolveTargetCategoryDir(targetRoot: string, sourceCategoryDir: string): string {
  const sourceKey = categoryKeyFromDir(basename(sourceCategoryDir));
  if (existsSync(targetRoot)) {
    for (const entry of readdirSync(targetRoot, { withFileTypes: true })) {
      if (!entry.isDirectory()) {
        continue;
      }
      if (categoryKeyFromDir(entry.name) === sourceKey) {
        return resolve(targetRoot, entry.name);
      }
    }
  }
  return resolve(targetRoot, basename(sourceCategoryDir));
}

function ensureDirectory(path: string, createdPaths: string[], preservedPaths: string[]): void {
  if (existsSync(path)) {
    if (!statSync(path).isDirectory()) {
      throw new CatalogImportError(`expected directory but found file: ${path}`);
    }
    preservedPaths.push(path);
    return;
  }

  mkdirSync(path, { recursive: true });
  createdPaths.push(path);
}

function copyFile(
  source: string,
  destination: string,
  overwrite: boolean,
  createdPaths: string[],
  preservedPaths: string[],
): void {
  if (existsSync(destination) && !overwrite) {
    if (statSync(destination).isDirectory()) {
      throw new CatalogImportError(`expected file but found directory: ${destination}`);
    }
    preservedPaths.push(destination);
    return;
  }

  mkdirSync(dirname(destination), { recursive: true });
  copyFileSync(source, destination);
  createdPaths.push(destination);
}

function scanSourceRoots(catalogRoots: readonly string[]): {
  categories: Map<string, CategorySource>;
  agents: Map<string, AgentSource>;
} {
  const normalizedRoots = normalizeCatalogRoots(catalogRoots);
  if (normalizedRoots.length === 0) {
    throw new CatalogImportError("catalog import requires at least one --catalog-root");
  }

  const categories = new Map<string, CategorySource>();
  const agents = new Map<string, AgentSource>();
  const issues: string[] = [];

  for (const root of normalizedRoots) {
    if (!existsSync(root)) {
      throw new CatalogImportError(`catalog root does not exist: ${root}`);
    }

    for (const entry of readdirSync(root, { withFileTypes: true })) {
      if (!entry.isDirectory()) {
        continue;
      }
      const categoryDir = resolve(root, entry.name);
      const category = parseCategoryDir(categoryDir);
      const readmePath = resolve(categoryDir, "README.md");
      categories.set(category.key, {
        key: category.key,
        directory: categoryDir,
        readmePath: existsSync(readmePath) ? readmePath : undefined,
      });

      for (const file of readdirSync(categoryDir, { withFileTypes: true })) {
        if (!file.isFile() || !file.name.endsWith(".toml")) {
          continue;
        }
        const path = resolve(categoryDir, file.name);
        try {
          const agent = parseAgentFile(path, "catalog-root", category.key);
          agents.set(agent.key, {
            key: agent.key,
            path,
            categoryKey: category.key,
            categoryDirectory: categoryDir,
            readmePath: existsSync(readmePath) ? readmePath : undefined,
          });
        } catch (error) {
          issues.push(`${path}: ${error instanceof Error ? error.message : String(error)}`);
        }
      }
    }
  }

  if (issues.length > 0) {
    throw new CatalogImportError(
      `source catalog contains malformed templates:\n${issues.map((issue) => `- ${issue}`).join("\n")}`,
    );
  }

  return { categories, agents };
}

export function importCatalog(options: {
  projectRoot: string;
  scope: "project" | "global";
  homeDir?: string;
  catalogRoots: readonly string[];
  agentKeys: string[];
  categoryKeys: string[];
  overwrite?: boolean;
}): CatalogImportResult {
  if (options.agentKeys.length === 0 && options.categoryKeys.length === 0) {
    throw new CatalogImportError("catalog import requires --agents, --categories, or both");
  }

  const { categories, agents } = scanSourceRoots(options.catalogRoots);

  const missingCategories = options.categoryKeys.filter((key) => !categories.has(key));
  if (missingCategories.length > 0) {
    throw new CatalogImportError(`unknown category keys: ${missingCategories.join(", ")}`);
  }

  const missingAgents = options.agentKeys.filter((key) => !agents.has(key));
  if (missingAgents.length > 0) {
    throw new CatalogImportError(`unknown agent keys: ${missingAgents.join(", ")}`);
  }

  const targetRoot = resolveTargetRoot(options.projectRoot, options.scope, options.homeDir);
  const createdPaths: string[] = [];
  const preservedPaths: string[] = [];
  ensureDirectory(targetRoot, createdPaths, preservedPaths);

  const selectedCategories = new Set<string>(options.categoryKeys);
  const selectedAgents = new Set<string>(options.agentKeys);
  const copyPlan = new Map<string, string>();

  for (const categoryKey of options.categoryKeys) {
    const categorySource = categories.get(categoryKey);
    if (!categorySource) {
      continue;
    }
    const targetCategoryDir = resolveTargetCategoryDir(targetRoot, categorySource.directory);
    ensureDirectory(targetCategoryDir, createdPaths, preservedPaths);
    if (categorySource.readmePath) {
      copyPlan.set(categorySource.readmePath, resolve(targetCategoryDir, "README.md"));
    }
    for (const agentSource of agents.values()) {
      if (agentSource.categoryDirectory !== categorySource.directory) {
        continue;
      }
      selectedAgents.add(agentSource.key);
      copyPlan.set(agentSource.path, resolve(targetCategoryDir, basename(agentSource.path)));
    }
  }

  for (const agentKey of options.agentKeys) {
    const agentSource = agents.get(agentKey);
    if (!agentSource) {
      continue;
    }
    selectedCategories.add(agentSource.categoryKey);
    const targetCategoryDir = resolveTargetCategoryDir(targetRoot, agentSource.categoryDirectory);
    ensureDirectory(targetCategoryDir, createdPaths, preservedPaths);
    if (agentSource.readmePath) {
      copyPlan.set(agentSource.readmePath, resolve(targetCategoryDir, "README.md"));
    }
    copyPlan.set(agentSource.path, resolve(targetCategoryDir, basename(agentSource.path)));
  }

  for (const [source, destination] of [...copyPlan.entries()].sort((left, right) =>
    left[1].localeCompare(right[1]),
  )) {
    copyFile(source, destination, options.overwrite ?? false, createdPaths, preservedPaths);
  }

  return {
    targetRoot,
    importedCategoryKeys: [...selectedCategories].sort(),
    importedAgentKeys: [...selectedAgents].sort(),
    createdPaths,
    preservedPaths,
  };
}
