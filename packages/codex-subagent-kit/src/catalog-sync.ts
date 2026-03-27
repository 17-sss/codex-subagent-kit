import { cpSync, existsSync, mkdirSync, readdirSync, rmSync, writeFileSync } from "node:fs";
import { basename, resolve } from "node:path";

import {
  DEFAULT_SYNC_SOURCE_NAME,
  resolveGlobalSourceCategoriesDir,
  resolveProjectSourceCategoriesDir,
} from "./paths";

const VOLTAGENT_TREE_API_URL =
  "https://api.github.com/repos/VoltAgent/awesome-codex-subagents/git/trees/main?recursive=1";
const VOLTAGENT_RAW_BASE_URL =
  "https://raw.githubusercontent.com/VoltAgent/awesome-codex-subagents/main/";

export class CatalogSyncError extends Error {}

export interface CatalogSyncResult {
  sourceName: string;
  targetRoot: string;
  sourceLabel: string;
  copiedPaths: string[];
}

function normalizeSourceName(sourceName: string): string {
  const candidate = sourceName.trim().toLowerCase();
  if (!candidate) {
    throw new CatalogSyncError("catalog sync requires a non-empty source name");
  }
  if (!/^[a-z0-9][a-z0-9_-]*$/.test(candidate)) {
    throw new CatalogSyncError(
      "source names may contain only lowercase letters, digits, hyphens, and underscores",
    );
  }
  return candidate;
}

function resolveCategoriesRoot(sourceRoot: string): string {
  const root = resolve(sourceRoot);
  if (existsSync(root) && basename(root) === "categories") {
    return root;
  }
  const nested = resolve(root, "categories");
  if (existsSync(nested)) {
    return nested;
  }
  throw new CatalogSyncError(`expected a categories/ directory but found: ${sourceRoot}`);
}

function prepareTargetRoot(targetRoot: string): void {
  mkdirSync(resolve(targetRoot, ".."), { recursive: true });
  if (existsSync(targetRoot)) {
    rmSync(targetRoot, { recursive: true, force: true });
  }
  mkdirSync(targetRoot, { recursive: true });
}

function listRelativeCatalogFiles(root: string): string[] {
  const discovered: string[] = [];

  function walk(current: string): void {
    for (const entry of readdirSync(current, { withFileTypes: true })) {
      const absolutePath = resolve(current, entry.name);
      if (entry.isDirectory()) {
        walk(absolutePath);
        continue;
      }
      if (!entry.isFile()) {
        continue;
      }
      if (entry.name === "README.md" || entry.name.endsWith(".toml")) {
        discovered.push(absolutePath.slice(root.length + 1));
      }
    }
  }

  walk(root);
  return discovered.sort();
}

function copyLocalSource(sourceRoot: string, targetRoot: string): string[] {
  const categoriesRoot = resolveCategoriesRoot(sourceRoot);
  const copiedPaths: string[] = [];
  for (const relativePath of listRelativeCatalogFiles(categoriesRoot)) {
    const sourcePath = resolve(categoriesRoot, relativePath);
    const destination = resolve(targetRoot, relativePath);
    mkdirSync(resolve(destination, ".."), { recursive: true });
    cpSync(sourcePath, destination);
    copiedPaths.push(destination);
  }
  return copiedPaths;
}

async function fetchJson(url: string): Promise<Record<string, unknown>> {
  const response = await fetch(url, {
    headers: {
      Accept: "application/vnd.github+json",
      "User-Agent": "codex-subagent-kit",
    },
  });
  if (!response.ok) {
    throw new CatalogSyncError(`failed to fetch upstream catalog metadata: ${response.status}`);
  }
  return (await response.json()) as Record<string, unknown>;
}

async function fetchText(url: string): Promise<string> {
  const response = await fetch(url, {
    headers: { "User-Agent": "codex-subagent-kit" },
  });
  if (!response.ok) {
    throw new CatalogSyncError(`failed to fetch upstream catalog file: ${url}`);
  }
  return response.text();
}

async function downloadVoltAgentSource(targetRoot: string): Promise<string[]> {
  const payload = await fetchJson(VOLTAGENT_TREE_API_URL);
  const tree = payload.tree;
  if (!Array.isArray(tree)) {
    throw new CatalogSyncError("unexpected upstream catalog metadata payload");
  }

  const upstreamPaths = tree
    .map((entry) => (entry && typeof entry === "object" ? entry.path : undefined))
    .filter((path): path is string => typeof path === "string" && path.startsWith("categories/"))
    .filter((path) => path.endsWith(".toml") || path.endsWith("README.md"))
    .sort();

  if (upstreamPaths.length === 0) {
    throw new CatalogSyncError("upstream catalog did not expose any categories files");
  }

  const copiedPaths: string[] = [];
  for (const upstreamPath of upstreamPaths) {
    const relativePath = upstreamPath.replace(/^categories\//, "");
    const destination = resolve(targetRoot, relativePath);
    mkdirSync(resolve(destination, ".."), { recursive: true });
    writeFileSync(destination, await fetchText(`${VOLTAGENT_RAW_BASE_URL}${upstreamPath}`), "utf8");
    copiedPaths.push(destination);
  }

  return copiedPaths;
}

export async function syncCatalog(options: {
  projectRoot: string;
  scope: "project" | "global";
  homeDir?: string;
  sourceName?: string;
  sourceRoot?: string;
}): Promise<CatalogSyncResult> {
  const sourceName = normalizeSourceName(options.sourceName ?? DEFAULT_SYNC_SOURCE_NAME);
  const targetRoot =
    options.scope === "project"
      ? resolveProjectSourceCategoriesDir(options.projectRoot, sourceName)
      : resolveGlobalSourceCategoriesDir(sourceName, options.homeDir);

  prepareTargetRoot(targetRoot);

  let copiedPaths: string[];
  let sourceLabel: string;
  if (options.sourceRoot) {
    copiedPaths = copyLocalSource(options.sourceRoot, targetRoot);
    sourceLabel = resolveCategoriesRoot(options.sourceRoot);
  } else {
    if (sourceName !== DEFAULT_SYNC_SOURCE_NAME) {
      throw new CatalogSyncError(
        "remote sync is only supported for the default voltagent source without --source-root",
      );
    }
    copiedPaths = await downloadVoltAgentSource(targetRoot);
    sourceLabel = "VoltAgent/awesome-codex-subagents@main";
  }

  if (copiedPaths.length === 0) {
    throw new CatalogSyncError("catalog sync did not copy any README or TOML files");
  }

  return {
    sourceName,
    targetRoot,
    sourceLabel,
    copiedPaths,
  };
}
