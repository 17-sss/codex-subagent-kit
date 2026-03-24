import { existsSync, readFileSync, readdirSync } from "node:fs";
import { basename, extname, resolve } from "node:path";

import * as TOML from "@iarna/toml";

import type { AgentSpec, CatalogOptions, Category } from "./models";
import {
  CATEGORY_OVERRIDE_KEY,
  normalizeCatalogRoots,
  resolveGlobalAgentsDir,
  resolveGlobalCatalogDir,
  resolveProjectAgentsDir,
  resolveProjectCatalogDir,
} from "./paths";

export const BUILTIN_CATEGORIES_DIR = resolve(__dirname, "..", "builtin_catalog", "categories");

export const IMPORTED_AGENTS_CATEGORY: Category = {
  key: "imported-agents",
  title: "Imported & External",
  description: "Portable TOML agent definitions discovered from project/global agent directories.",
};

type CatalogState = {
  categories: Map<string, Category>;
  agents: Map<string, AgentSpec>;
};

type ParsedToml = Record<string, unknown>;

let builtinCatalogCache: CatalogState | null = null;

function readToml(path: string): ParsedToml {
  return TOML.parse(readFileSync(path, "utf8")) as ParsedToml;
}

function listDirectories(path: string): string[] {
  if (!existsSync(path)) {
    return [];
  }
  return readdirSync(path, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => resolve(path, entry.name))
    .sort();
}

function listTomlFiles(path: string): string[] {
  if (!existsSync(path)) {
    return [];
  }
  return readdirSync(path, { withFileTypes: true })
    .filter((entry) => entry.isFile() && extname(entry.name) === ".toml")
    .map((entry) => resolve(path, entry.name))
    .sort();
}

function categoryKeyFromDir(directoryName: string): string {
  const match = directoryName.match(/^(\d+)-(.*)$/);
  return match ? match[2] : directoryName;
}

function fallbackTitleFromKey(key: string): string {
  return key
    .split("-")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

export function parseCategoryDir(categoryDir: string): Category {
  const key = categoryKeyFromDir(basename(categoryDir));
  let title = fallbackTitleFromKey(key);
  let description = title;
  const readmePath = resolve(categoryDir, "README.md");

  if (!existsSync(readmePath)) {
    return { key, title, description };
  }

  const lines = readFileSync(readmePath, "utf8")
    .split(/\r?\n/)
    .map((line) => line.trim());

  for (const line of lines) {
    if (!line.startsWith("#")) {
      continue;
    }
    const parsedTitle = line.replace(/^#+\s*/, "").trim();
    const numericTitle = parsedTitle.match(/^\d+\.\s+(.*)$/);
    title = numericTitle ? numericTitle[1].trim() : parsedTitle || title;
    break;
  }

  for (const line of lines) {
    if (!line || line.startsWith("#") || line === "Included agents:") {
      continue;
    }
    description = line;
    break;
  }

  return { key, title, description };
}

function readInstructions(data: ParsedToml): string {
  const developerInstructions = data.developer_instructions;
  if (typeof developerInstructions === "string" && developerInstructions.trim()) {
    return developerInstructions.trimEnd();
  }

  const instructions = data.instructions;
  if (typeof instructions === "string" && instructions.trim()) {
    return instructions.trimEnd();
  }

  if (
    instructions &&
    typeof instructions === "object" &&
    "text" in instructions &&
    typeof instructions.text === "string" &&
    instructions.text.trim()
  ) {
    return instructions.text.trimEnd();
  }

  throw new Error("missing instructions text");
}

function requiredString(data: ParsedToml, key: string): string {
  const value = data[key];
  if (typeof value !== "string" || !value.trim()) {
    throw new Error(`missing required string field: ${key}`);
  }
  return value.trim();
}

export function parseAgentFile(
  path: string,
  source: string,
  inheritedCategory?: string,
): AgentSpec {
  const data = readToml(path);
  const explicitCategory = data[CATEGORY_OVERRIDE_KEY];

  if (
    explicitCategory !== undefined &&
    (typeof explicitCategory !== "string" || !explicitCategory.trim())
  ) {
    throw new Error(`invalid ${CATEGORY_OVERRIDE_KEY}`);
  }

  return {
    key: basename(path, ".toml"),
    category:
      typeof explicitCategory === "string" && explicitCategory.trim()
        ? explicitCategory.trim()
        : inheritedCategory ?? IMPORTED_AGENTS_CATEGORY.key,
    name: requiredString(data, "name"),
    description: requiredString(data, "description"),
    model: requiredString(data, "model"),
    reasoningEffort: requiredString(data, "model_reasoning_effort"),
    sandboxMode: requiredString(data, "sandbox_mode"),
    developerInstructions: readInstructions(data),
    source,
    definitionPath: path,
  };
}

function loadCatalogRoot(root: string, source: string): CatalogState {
  const categories = new Map<string, Category>();
  const agents = new Map<string, AgentSpec>();

  if (!existsSync(root)) {
    return { categories, agents };
  }

  for (const categoryDir of listDirectories(root)) {
    const category = parseCategoryDir(categoryDir);
    categories.set(category.key, category);
    for (const file of listTomlFiles(categoryDir)) {
      const agent = parseAgentFile(file, source, category.key);
      agents.set(agent.key, agent);
    }
  }

  return { categories, agents };
}

function getBuiltinCatalog(): CatalogState {
  if (builtinCatalogCache) {
    return builtinCatalogCache;
  }

  const builtin = loadCatalogRoot(BUILTIN_CATEGORIES_DIR, "builtin");
  if (builtin.categories.size === 0) {
    throw new Error(`builtin catalog is empty: ${BUILTIN_CATEGORIES_DIR}`);
  }
  builtinCatalogCache = builtin;
  return builtin;
}

function mergeCatalogInto(target: CatalogState, incoming: CatalogState): void {
  for (const [key, category] of incoming.categories) {
    target.categories.set(key, category);
  }
  for (const [key, agent] of incoming.agents) {
    target.agents.set(key, agent);
  }
}

function loadExternalAgents(
  directory: string,
  source: string,
  inheritedAgents: Map<string, AgentSpec>,
): AgentSpec[] {
  if (!existsSync(directory)) {
    return [];
  }

  const loaded: AgentSpec[] = [];
  for (const file of listTomlFiles(directory)) {
    try {
      const inheritedCategory = inheritedAgents.get(basename(file, ".toml"))?.category;
      loaded.push(parseAgentFile(file, source, inheritedCategory));
    } catch {
      continue;
    }
  }
  return loaded;
}

function buildCatalogState(options: CatalogOptions = {}): CatalogState {
  const includeProject = options.includeProject ?? false;
  const includeGlobal = options.includeGlobal ?? false;
  const homeDir = options.homeDir;
  const catalogRoots = normalizeCatalogRoots(options.catalogRoots);

  const builtin = getBuiltinCatalog();
  const state: CatalogState = {
    categories: new Map(builtin.categories),
    agents: new Map(builtin.agents),
  };

  if (includeGlobal) {
    mergeCatalogInto(state, loadCatalogRoot(resolveGlobalCatalogDir(homeDir), "global-catalog"));
  }

  if (includeProject && options.projectRoot) {
    mergeCatalogInto(
      state,
      loadCatalogRoot(resolveProjectCatalogDir(options.projectRoot), "project-catalog"),
    );
  }

  for (const root of catalogRoots) {
    mergeCatalogInto(state, loadCatalogRoot(root, "catalog-root"));
  }

  state.categories.set(IMPORTED_AGENTS_CATEGORY.key, IMPORTED_AGENTS_CATEGORY);

  if (includeGlobal) {
    for (const agent of loadExternalAgents(
      resolveGlobalAgentsDir(homeDir),
      "global",
      state.agents,
    )) {
      state.agents.set(agent.key, agent);
    }
  }

  if (includeProject && options.projectRoot) {
    for (const agent of loadExternalAgents(
      resolveProjectAgentsDir(options.projectRoot),
      "project",
      state.agents,
    )) {
      state.agents.set(agent.key, agent);
    }
  }

  return state;
}

export function getAgentMap(options: CatalogOptions = {}): Map<string, AgentSpec> {
  return buildCatalogState(options).agents;
}

export function getCategories(options: CatalogOptions = {}): Category[] {
  const state = buildCatalogState(options);
  const usedCategories = new Set([...state.agents.values()].map((agent) => agent.category));
  return [...state.categories.values()].filter((category) => usedCategories.has(category.key));
}

export function getAgents(options: CatalogOptions = {}): AgentSpec[] {
  const categories = getCategories(options);
  const agents = [...getAgentMap(options).values()];
  const categoryOrder = new Map(categories.map((category, index) => [category.key, index]));

  return agents.sort((left, right) => {
    const leftOrder = categoryOrder.get(left.category) ?? categoryOrder.size;
    const rightOrder = categoryOrder.get(right.category) ?? categoryOrder.size;
    if (leftOrder !== rightOrder) {
      return leftOrder - rightOrder;
    }
    const byName = left.name.localeCompare(right.name, undefined, { sensitivity: "base" });
    if (byName !== 0) {
      return byName;
    }
    return left.key.localeCompare(right.key);
  });
}

export function getAgentsByCategory(
  categoryKeys: Set<string> | undefined,
  options: CatalogOptions = {},
): AgentSpec[] {
  const agents = getAgents(options);
  if (!categoryKeys || categoryKeys.size === 0) {
    return agents;
  }
  return agents.filter((agent) => categoryKeys.has(agent.category));
}

export function renderCatalogOutput(options: CatalogOptions = {}): string {
  const categories = getCategories(options);
  const agents = getAgents(options);
  const lines: string[] = [];

  for (const category of categories) {
    lines.push(`[${category.title}]`);
    lines.push(`  key: ${category.key}`);
    lines.push(`  description: ${category.description}`);

    for (const agent of agents) {
      if (agent.category !== category.key) {
        continue;
      }
      const sourceSuffix = agent.source === "builtin" ? "" : ` [${agent.source}]`;
      lines.push(`  - ${agent.key}: ${agent.description}${sourceSuffix}`);
    }

    lines.push("");
  }

  return lines.join("\n").trimEnd();
}
