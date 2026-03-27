import { existsSync, mkdirSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";

import { getAgentMap } from "./catalog";
import type { InstallResult } from "./models";
import { resolveGlobalAgentsDir, resolveProjectAgentsDir } from "./paths";

export class GenerationError extends Error {}

export const ORCHESTRATOR_CATEGORY = "meta-orchestration";
export const DEFAULT_ORCHESTRATOR_KEY = "multi-agent-coordinator";

export interface InstallAgentsOptions {
  scope: "project" | "global";
  projectRoot: string;
  agentKeys: string[];
  homeDir?: string;
  catalogRoots?: readonly string[];
  overwrite?: boolean;
}

export interface RenderableAgentFile {
  name: string;
  description: string;
  model: string;
  reasoningEffort: string;
  sandboxMode: string;
  developerInstructions: string;
  categoryOverride?: string;
}

export function renderAgentFile(agent: RenderableAgentFile): string {
  const lines = [
    `name = ${JSON.stringify(agent.name)}`,
    `description = ${JSON.stringify(agent.description)}`,
    `model = ${JSON.stringify(agent.model)}`,
    `model_reasoning_effort = ${JSON.stringify(agent.reasoningEffort)}`,
    `sandbox_mode = ${JSON.stringify(agent.sandboxMode)}`,
    'developer_instructions = """',
    agent.developerInstructions.trimEnd(),
    '"""',
  ];

  if (agent.categoryOverride) {
    lines.push(`codex_subagent_kit_category = ${JSON.stringify(agent.categoryOverride)}`);
  }

  return `${lines.join("\n")}\n`;
}

export function resolveTargetDir(scope: "project" | "global", projectRoot: string, homeDir?: string): string {
  if (scope === "project") {
    return resolveProjectAgentsDir(projectRoot);
  }
  if (scope === "global") {
    return resolveGlobalAgentsDir(homeDir);
  }
  throw new GenerationError(`unsupported scope: ${scope}`);
}

export function installAgents(options: InstallAgentsOptions): InstallResult {
  const agentMap = getAgentMap({
    projectRoot: options.projectRoot,
    homeDir: options.homeDir,
    includeProject: options.scope === "project",
    includeGlobal: true,
    catalogRoots: options.catalogRoots,
  });
  const missing = options.agentKeys.filter((key) => !agentMap.has(key));
  if (missing.length > 0) {
    throw new GenerationError(`unknown agent keys: ${missing.join(", ")}`);
  }

  const targetDir = resolveTargetDir(options.scope, options.projectRoot, options.homeDir);
  mkdirSync(targetDir, { recursive: true });

  const agentPaths: string[] = [];
  const agentPreservedPaths: string[] = [];

  for (const key of options.agentKeys) {
    const agent = agentMap.get(key);
    if (!agent) {
      continue;
    }

    const filePath = resolve(targetDir, `${agent.key}.toml`);
    if (existsSync(filePath) && !options.overwrite) {
      agentPreservedPaths.push(filePath);
      continue;
    }

    writeFileSync(
      filePath,
      renderAgentFile({
        name: agent.name,
        description: agent.description,
        model: agent.model,
        reasoningEffort: agent.reasoningEffort,
        sandboxMode: agent.sandboxMode,
        developerInstructions: agent.developerInstructions,
      }),
      "utf8",
    );
    agentPaths.push(filePath);
  }

  return {
    agentPaths,
    agentPreservedPaths,
  };
}
