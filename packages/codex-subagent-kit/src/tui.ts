import { checkbox, confirm, select } from "@inquirer/prompts";

import { getAgentsByCategory, getCategories } from "./catalog";
import { runDoctor } from "./doctor";
import {
  GenerationError,
  installAgents,
  resolveTargetDir,
  type InstallAgentsOptions,
} from "./generator";
import type { AgentSpec, DoctorReport, InstallResult } from "./models";

export interface PromptChoice<T> {
  value: T;
  name: string;
  checked?: boolean;
}

export interface PromptAdapter {
  select<T>(config: { message: string; choices: Array<PromptChoice<T>> }): Promise<T>;
  checkbox<T>(config: { message: string; choices: Array<PromptChoice<T>> }): Promise<T[]>;
  confirm(config: { message: string; default?: boolean }): Promise<boolean>;
}

interface TuiDeps {
  installAgentsImpl(options: InstallAgentsOptions): InstallResult;
  runDoctorImpl(options: {
    projectRoot: string;
    scope: "project" | "global";
    catalogRoots?: readonly string[];
  }): DoctorReport;
}

const defaultPromptAdapter: PromptAdapter = {
  select,
  checkbox,
  confirm,
};

const defaultDeps: TuiDeps = {
  installAgentsImpl: installAgents,
  runDoctorImpl: runDoctor,
};

export function defaultAgentSelection(scope: "project" | "global", agentSpecs: AgentSpec[]): Set<string> {
  void scope;
  void agentSpecs;
  return new Set();
}

export function validateAgentSelection(
  scope: "project" | "global",
  agentSpecs: AgentSpec[],
  selectedAgents: Set<string>,
): string | undefined {
  void scope;
  void agentSpecs;
  if (selectedAgents.size === 0) {
    return "Select at least one subagent.";
  }
  return undefined;
}

function formatResultSummary(
  result: InstallResult,
  validationReport: DoctorReport,
): string {
  const lines = [
    "Install complete",
    `validation: ${validationReport.issues.length === 0 ? "ok" : "issues found"}`,
  ];

  for (const path of result.agentPaths.slice(0, 8)) {
    lines.push(path);
  }
  for (const path of result.agentPreservedPaths.slice(0, 4)) {
    lines.push(`agent preserved: ${path}`);
  }
  if (result.orchestratorKey) {
    lines.push(`orchestrator: ${result.orchestratorKey}`);
  }
  for (const path of result.scaffoldCreatedPaths.slice(0, 4)) {
    lines.push(`created: ${path}`);
  }
  for (const path of result.scaffoldPreservedPaths.slice(0, 4)) {
    lines.push(`preserved: ${path}`);
  }
  if (validationReport.issues.length > 0) {
    lines.push("issues:");
    for (const issue of validationReport.issues.slice(0, 4)) {
      lines.push(issue.path ? `- ${issue.path}: ${issue.message}` : `- ${issue.message}`);
    }
  }

  return lines.join("\n");
}

export async function runTui(
  projectRoot: string,
  options: {
    catalogRoots?: readonly string[];
    promptAdapter?: PromptAdapter;
    deps?: Partial<TuiDeps>;
  } = {},
): Promise<number> {
  const prompt = options.promptAdapter ?? defaultPromptAdapter;
  const deps: TuiDeps = { ...defaultDeps, ...options.deps };

  try {
    while (true) {
      const scope = await prompt.select<"project" | "global">({
        message: `Choose an install target for ${projectRoot}`,
        choices: [
          { value: "project", name: "Project (.codex/agents in current project)" },
          { value: "global", name: "Global (~/.codex/agents)" },
        ],
      });

      const categories = getCategories({
        projectRoot,
        includeProject: scope === "project",
        includeGlobal: true,
        catalogRoots: options.catalogRoots,
      });

      const selectedCategoryKeys = await prompt.checkbox<string>({
        message: "Select categories. Leave empty to browse all agents.",
        choices: categories.map((category) => ({
          value: category.key,
          name: `${category.title} - ${category.description}`,
        })),
      });

      const categorySet = new Set(selectedCategoryKeys);
      const agentSpecs = getAgentsByCategory(categorySet, {
        projectRoot,
        includeProject: scope === "project",
        includeGlobal: true,
        catalogRoots: options.catalogRoots,
      });

      const defaultSelected = defaultAgentSelection(scope, agentSpecs);
      const selectedAgentsList = await prompt.checkbox<string>({
        message:
          scope === "project"
            ? "Select subagents. Including a meta-orchestration agent also seeds the experimental scaffold."
            : "Select subagents.",
        choices: agentSpecs.map((agent) => ({
          value: agent.key,
          name: `${agent.name} - ${agent.description}`,
          checked: defaultSelected.has(agent.key),
        })),
      });
      const selectedAgents = new Set(selectedAgentsList);
      const validationError = validateAgentSelection(scope, agentSpecs, selectedAgents);
      if (validationError) {
        console.error(validationError);
        continue;
      }

      const confirmed = await prompt.confirm({
        message: `Install ${selectedAgents.size} agent(s) into ${resolveTargetDir(scope, projectRoot)}?`,
        default: true,
      });
      if (!confirmed) {
        continue;
      }

      const result = deps.installAgentsImpl({
        scope,
        projectRoot,
        agentKeys: [...selectedAgents].sort(),
        catalogRoots: options.catalogRoots,
      });
      const validationReport = deps.runDoctorImpl({
        projectRoot,
        scope,
        catalogRoots: options.catalogRoots,
      });

      console.log(formatResultSummary(result, validationReport));
      return validationReport.issues.length === 0 ? 0 : 1;
    }
  } catch (error) {
    if (error instanceof GenerationError) {
      console.error(`error: ${error.message}`);
      return 1;
    }
    const errorName = error instanceof Error ? error.name : "";
    if (errorName === "ExitPromptError") {
      return 130;
    }
    throw error;
  }
}
