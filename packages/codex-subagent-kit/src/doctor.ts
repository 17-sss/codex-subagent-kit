import { existsSync, readdirSync } from "node:fs";
import { resolve } from "node:path";

import {
  BUILTIN_CATEGORIES_DIR,
  getAgentMap,
  IMPORTED_AGENTS_CATEGORY,
  parseAgentFile,
  parseCategoryDir,
} from "./catalog";
import type { AgentSpec, Category, DoctorIssue, DoctorReport } from "./models";
import {
  normalizeCatalogRoots,
  resolveGlobalAgentsDir,
  resolveGlobalCatalogDir,
  resolveProjectCatalogDir,
} from "./paths";
import { resolveTargetDir } from "./generator";

function scanCatalogRoot(
  root: string,
  source: string,
  missingIsIssue = false,
): {
  categories: Map<string, Category>;
  agents: Map<string, AgentSpec>;
  issues: DoctorIssue[];
  checkedTemplates: number;
} {
  const categories = new Map<string, Category>();
  const agents = new Map<string, AgentSpec>();
  const issues: DoctorIssue[] = [];
  let checkedTemplates = 0;

  if (!existsSync(root)) {
    if (missingIsIssue) {
      issues.push({ path: root, message: "catalog root does not exist" });
    }
    return { categories, agents, issues, checkedTemplates };
  }

  for (const entry of readdirSync(root, { withFileTypes: true })) {
    if (!entry.isDirectory()) {
      continue;
    }
    const categoryDir = resolve(root, entry.name);
    const category = parseCategoryDir(categoryDir);
    categories.set(category.key, category);

    for (const file of readdirSync(categoryDir, { withFileTypes: true })) {
      if (!file.isFile() || !file.name.endsWith(".toml")) {
        continue;
      }
      const path = resolve(categoryDir, file.name);
      checkedTemplates += 1;
      try {
        const agent = parseAgentFile(path, source, category.key);
        agents.set(agent.key, agent);
      } catch (error) {
        issues.push({ path, message: error instanceof Error ? error.message : String(error) });
      }
    }
  }

  return { categories, agents, issues, checkedTemplates };
}

function scanInstalledAgents(
  directory: string,
  source: string,
  inheritedAgents: Map<string, AgentSpec>,
): { agents: AgentSpec[]; issues: DoctorIssue[]; checkedFiles: number } {
  const agents: AgentSpec[] = [];
  const issues: DoctorIssue[] = [];
  let checkedFiles = 0;

  if (!existsSync(directory)) {
    return { agents, issues, checkedFiles };
  }

  for (const file of readdirSync(directory, { withFileTypes: true })) {
    if (!file.isFile() || !file.name.endsWith(".toml")) {
      continue;
    }
    const path = resolve(directory, file.name);
    checkedFiles += 1;
    try {
      const inheritedCategory = inheritedAgents.get(file.name.replace(/\.toml$/, ""))?.category;
      agents.push(parseAgentFile(path, source, inheritedCategory));
    } catch (error) {
      issues.push({ path, message: error instanceof Error ? error.message : String(error) });
    }
  }

  return { agents, issues, checkedFiles };
}

export function runDoctor(options: {
  projectRoot: string;
  scope: "project" | "global";
  homeDir?: string;
  catalogRoots?: readonly string[];
}): DoctorReport {
  const catalogCounts: Array<[string, number]> = [];
  const installedCounts: Array<[string, number]> = [];
  const issues: DoctorIssue[] = [];

  const builtin = scanCatalogRoot(BUILTIN_CATEGORIES_DIR, "builtin");
  catalogCounts.push(["built-in", builtin.checkedTemplates]);
  issues.push(...builtin.issues);

  const categories = new Map(builtin.categories);
  const agentMap = new Map(builtin.agents);

  const globalCatalog = scanCatalogRoot(resolveGlobalCatalogDir(options.homeDir), "global-catalog");
  catalogCounts.push(["global catalog", globalCatalog.checkedTemplates]);
  issues.push(...globalCatalog.issues);
  for (const [key, category] of globalCatalog.categories) categories.set(key, category);
  for (const [key, agent] of globalCatalog.agents) agentMap.set(key, agent);

  if (options.scope === "project") {
    const projectCatalog = scanCatalogRoot(
      resolveProjectCatalogDir(options.projectRoot),
      "project-catalog",
    );
    catalogCounts.push(["project catalog", projectCatalog.checkedTemplates]);
    issues.push(...projectCatalog.issues);
    for (const [key, category] of projectCatalog.categories) categories.set(key, category);
    for (const [key, agent] of projectCatalog.agents) agentMap.set(key, agent);
  }

  for (const root of normalizeCatalogRoots(options.catalogRoots)) {
    const extra = scanCatalogRoot(root, "catalog-root", true);
    catalogCounts.push([`catalog root: ${root}`, extra.checkedTemplates]);
    issues.push(...extra.issues);
    for (const [key, category] of extra.categories) categories.set(key, category);
    for (const [key, agent] of extra.agents) agentMap.set(key, agent);
  }

  categories.set(IMPORTED_AGENTS_CATEGORY.key, IMPORTED_AGENTS_CATEGORY);

  const globalInstalled = scanInstalledAgents(
    resolveGlobalAgentsDir(options.homeDir),
    "global",
    agentMap,
  );
  installedCounts.push(["global agents", globalInstalled.checkedFiles]);
  issues.push(...globalInstalled.issues);
  for (const agent of globalInstalled.agents) {
    agentMap.set(agent.key, agent);
  }

  let targetDir: string;
  if (options.scope === "project") {
    const projectInstalledDir = resolveTargetDir("project", options.projectRoot);
    const projectInstalled = scanInstalledAgents(projectInstalledDir, "project", agentMap);
    installedCounts.push(["project agents", projectInstalled.checkedFiles]);
    issues.push(...projectInstalled.issues);
    targetDir = projectInstalledDir;
    if (projectInstalled.checkedFiles === 0) {
      issues.push({ path: targetDir, message: "no installed agent definitions found in target scope" });
    }
  } else {
    targetDir = resolveTargetDir("global", options.projectRoot, options.homeDir);
    if (globalInstalled.checkedFiles === 0) {
      issues.push({ path: targetDir, message: "no installed agent definitions found in target scope" });
    }
  }

  return {
    scope: options.scope,
    targetDir,
    catalogCounts,
    installedCounts,
    issues,
  };
}

export function renderDoctorReport(report: DoctorReport): string {
  const lines = [
    `status: ${report.issues.length === 0 ? "ok" : "issues found"}`,
    `scope: ${report.scope}`,
    `target: ${report.targetDir}`,
    "",
    "Catalog templates checked:",
  ];

  for (const [label, count] of report.catalogCounts) {
    lines.push(`- ${label}: ${count}`);
  }

  lines.push("");
  lines.push("Installed agent files checked:");
  for (const [label, count] of report.installedCounts) {
    lines.push(`- ${label}: ${count}`);
  }

  lines.push("");
  if (report.issues.length === 0) {
    lines.push("Issues: none");
  } else {
    lines.push("Issues:");
    for (const issue of report.issues) {
      lines.push(issue.path ? `- ${issue.path}: ${issue.message}` : `- ${issue.message}`);
    }
  }

  return lines.join("\n");
}
