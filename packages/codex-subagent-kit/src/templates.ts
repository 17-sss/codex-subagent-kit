import { mkdirSync, readdirSync, statSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";

import { renderAgentFile } from "./generator";
import {
  resolveGlobalCatalogDir,
  resolveProjectCatalogDir,
} from "./paths";

export const DEFAULT_MODEL = "gpt-5.4";
export const DEFAULT_REASONING_EFFORT = "medium";
export const DEFAULT_SANDBOX_MODE = "read-only";
export const ORCHESTRATOR_CATEGORY = "meta-orchestration";

const SLUG_PATTERN = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;

export class TemplateError extends Error {}

export interface InitTemplateOptions {
  projectRoot: string;
  scope: "project" | "global";
  categoryKey: string;
  agentKey: string;
  catalogRoot?: string;
  categoryPrefix?: string;
  categoryTitle?: string;
  categoryDescription?: string;
  agentName?: string;
  agentDescription?: string;
  model?: string;
  reasoningEffort?: string;
  sandboxMode?: string;
  orchestrator?: boolean;
  overwrite?: boolean;
}

export interface TemplateInitResult {
  targetRoot: string;
  categoryDir: string;
  readmePath: string;
  agentPath: string;
  createdPaths: string[];
  preservedPaths: string[];
}

function validateSlug(value: string, fieldName: string): string {
  const normalized = value.trim().toLowerCase();
  if (!SLUG_PATTERN.test(normalized)) {
    throw new TemplateError(
      `${fieldName} must be a lowercase slug using letters, numbers, and hyphens`,
    );
  }
  return normalized;
}

function titleFromSlug(value: string): string {
  return value
    .split("-")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function categoryKeyFromDir(directoryName: string): string {
  const match = directoryName.match(/^(\d+)-(.*)$/);
  return match ? match[2] : directoryName;
}

function normalizePrefix(prefix?: string): string | undefined {
  if (prefix === undefined) {
    return undefined;
  }

  const stripped = prefix.trim();
  if (!stripped) {
    return undefined;
  }
  if (!/^\d+$/.test(stripped)) {
    throw new TemplateError("category prefix must be numeric");
  }
  return stripped.padStart(2, "0");
}

function nextPrefix(root: string): string {
  if (!existsDirectory(root)) {
    return "11";
  }

  const numericPrefixes = readdirSync(root, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => entry.name.match(/^(\d+)-/))
    .filter((match): match is RegExpMatchArray => Boolean(match))
    .map((match) => Number.parseInt(match[1], 10));

  return String(Math.max(10, ...numericPrefixes) + 1).padStart(2, "0");
}

function existsDirectory(path: string): boolean {
  try {
    return statSync(path).isDirectory();
  } catch {
    return false;
  }
}

function ensureDirectory(
  path: string,
  createdPaths: string[],
  preservedPaths: string[],
): void {
  if (existsDirectory(path)) {
    preservedPaths.push(path);
    return;
  }

  try {
    mkdirSync(path, { recursive: false });
  } catch (error) {
    if (error instanceof Error && "code" in error && error.code === "ENOENT") {
      mkdirSync(path, { recursive: true });
    } else {
      throw error;
    }
  }
  createdPaths.push(path);
}

function writeFile(
  path: string,
  content: string,
  overwrite: boolean,
  createdPaths: string[],
  preservedPaths: string[],
): void {
  try {
    const stats = statSync(path);
    if (stats.isDirectory()) {
      throw new TemplateError(`expected file but found directory: ${path}`);
    }
    if (!overwrite) {
      preservedPaths.push(path);
      return;
    }
  } catch (error) {
    if (!(error instanceof Error) || !("code" in error) || error.code !== "ENOENT") {
      if (error instanceof TemplateError) {
        throw error;
      }
      throw error;
    }
  }

  writeFileSync(path, content, "utf8");
  createdPaths.push(path);
}

function resolveTargetRoot(options: InitTemplateOptions): string {
  if (options.catalogRoot) {
    return resolve(options.catalogRoot);
  }
  if (options.scope === "project") {
    return resolveProjectCatalogDir(options.projectRoot);
  }
  if (options.scope === "global") {
    return resolveGlobalCatalogDir();
  }
  throw new TemplateError(`unsupported scope: ${options.scope}`);
}

function resolveCategoryDir(
  root: string,
  categoryKey: string,
  categoryPrefix?: string,
): { categoryDir: string; resolvedPrefix: string } {
  if (existsDirectory(root)) {
    for (const entry of readdirSync(root, { withFileTypes: true })) {
      if (!entry.isDirectory()) {
        continue;
      }
      if (categoryKeyFromDir(entry.name) === categoryKey) {
        const match = entry.name.match(/^(\d+)-/);
        return {
          categoryDir: resolve(root, entry.name),
          resolvedPrefix: match ? match[1] : "",
        };
      }
    }
  }

  const effectivePrefix = categoryPrefix ?? nextPrefix(root);
  return {
    categoryDir: resolve(root, `${effectivePrefix}-${categoryKey}`),
    resolvedPrefix: effectivePrefix,
  };
}

export function renderCategoryReadme(options: {
  categoryTitle: string;
  categoryDescription: string;
  categoryPrefix: string;
}): string {
  const headingNumber = options.categoryPrefix
    ? `${Number.parseInt(options.categoryPrefix, 10)}. `
    : "";
  return `# ${headingNumber}${options.categoryTitle}\n\n${options.categoryDescription}\n`;
}

export function renderAgentTemplate(options: {
  agentKey: string;
  agentName: string;
  agentDescription: string;
  model: string;
  reasoningEffort: string;
  sandboxMode: string;
  categoryOverride?: string;
}): string {
  return renderAgentFile({
    name: options.agentName,
    description: options.agentDescription,
    model: options.model,
    reasoningEffort: options.reasoningEffort,
    sandboxMode: options.sandboxMode,
    developerInstructions: [
      `You are \`${options.agentKey}\`.`,
      "",
      "Responsibilities:",
      "- TODO: define the primary ownership boundary.",
      "- TODO: define what inputs to expect.",
      "- TODO: define what outputs to return.",
      "",
      "Constraints:",
      "- Stay within the assigned scope.",
      "- Escalate when requirements are ambiguous or cross ownership boundaries.",
    ].join("\n"),
    categoryOverride: options.categoryOverride,
  });
}

export function initTemplate(options: InitTemplateOptions): TemplateInitResult {
  const normalizedCategoryKey = validateSlug(options.categoryKey, "category key");
  const normalizedAgentKey = validateSlug(options.agentKey, "agent key");
  const normalizedPrefix = normalizePrefix(options.categoryPrefix);

  const targetRoot = resolveTargetRoot(options);
  const createdPaths: string[] = [];
  const preservedPaths: string[] = [];

  ensureDirectory(targetRoot, createdPaths, preservedPaths);

  const { categoryDir, resolvedPrefix } = resolveCategoryDir(
    targetRoot,
    normalizedCategoryKey,
    normalizedPrefix,
  );
  ensureDirectory(categoryDir, createdPaths, preservedPaths);

  const resolvedCategoryTitle = (options.categoryTitle ?? titleFromSlug(normalizedCategoryKey)).trim();
  const resolvedCategoryDescription = (
    options.categoryDescription ??
    `Custom templates for the ${resolvedCategoryTitle.toLowerCase()} workflow.`
  ).trim();
  const resolvedAgentName = (options.agentName ?? normalizedAgentKey).trim();
  const resolvedAgentDescription = (
    options.agentDescription ?? `TODO: describe when to use ${normalizedAgentKey}.`
  ).trim();

  const readmePath = resolve(categoryDir, "README.md");
  writeFile(
    readmePath,
    renderCategoryReadme({
      categoryTitle: resolvedCategoryTitle,
      categoryDescription: resolvedCategoryDescription,
      categoryPrefix: resolvedPrefix,
    }),
    options.overwrite ?? false,
    createdPaths,
    preservedPaths,
  );

  let categoryOverride = options.orchestrator ? ORCHESTRATOR_CATEGORY : undefined;
  if (normalizedCategoryKey === ORCHESTRATOR_CATEGORY) {
    categoryOverride = undefined;
  }

  const agentPath = resolve(categoryDir, `${normalizedAgentKey}.toml`);
  writeFile(
    agentPath,
    renderAgentTemplate({
      agentKey: normalizedAgentKey,
      agentName: resolvedAgentName,
      agentDescription: resolvedAgentDescription,
      model: (options.model ?? DEFAULT_MODEL).trim(),
      reasoningEffort: (options.reasoningEffort ?? DEFAULT_REASONING_EFFORT).trim(),
      sandboxMode: (options.sandboxMode ?? DEFAULT_SANDBOX_MODE).trim(),
      categoryOverride,
    }),
    options.overwrite ?? false,
    createdPaths,
    preservedPaths,
  );

  return {
    targetRoot,
    categoryDir,
    readmePath,
    agentPath,
    createdPaths,
    preservedPaths,
  };
}
