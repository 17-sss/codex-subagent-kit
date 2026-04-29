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
  description?: string;
  checked?: boolean;
}

interface SelectPromptConfig<T> {
  message: string;
  choices: Array<PromptChoice<T>>;
}

interface CheckboxPromptConfig<T> {
  message: string;
  choices: Array<PromptChoice<T>>;
}

interface ConfirmPromptConfig {
  message: string;
  default?: boolean;
}

interface PromptRuntimeContext {
  signal?: AbortSignal;
}

export interface PromptAdapter {
  select<T>(config: SelectPromptConfig<T>, context?: PromptRuntimeContext): Promise<T>;
  checkbox<T>(config: CheckboxPromptConfig<T>, context?: PromptRuntimeContext): Promise<T[]>;
  confirm(config: ConfirmPromptConfig, context?: PromptRuntimeContext): Promise<boolean>;
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

const BACK = Symbol("back");

class BackNavigationError extends Error {
  override name = "BackNavigationError";

  constructor() {
    super("Back navigation requested");
  }
}

type TuiStep = "scope" | "categories" | "agents" | "confirm";

function isBackKey(key: { name?: string } | undefined): boolean {
  return key?.name === "escape" || key?.name === "left";
}

function isBackNavigationError(error: unknown): boolean {
  if (!(error instanceof Error)) {
    return false;
  }
  if (error.name === "BackNavigationError") {
    return true;
  }
  if (error.name === "AbortPromptError") {
    return isBackNavigationError(error.cause);
  }
  return false;
}

async function promptWithBack<T>(
  runPrompt: (context: PromptRuntimeContext) => Promise<T>,
): Promise<T | typeof BACK> {
  const controller = new AbortController();
  const handleKeypress = (_input: string, key: { name?: string } | undefined) => {
    if (isBackKey(key) && !controller.signal.aborted) {
      controller.abort(new BackNavigationError());
    }
  };

  process.stdin.on("keypress", handleKeypress);
  try {
    return await runPrompt({ signal: controller.signal });
  } catch (error) {
    if (isBackNavigationError(error)) {
      return BACK;
    }
    throw error;
  } finally {
    process.stdin.off("keypress", handleKeypress);
  }
}

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
    let step: TuiStep = "scope";
    let scope: "project" | "global" = "project";
    let selectedCategoryKeys: string[] = [];
    let selectedAgentKeys: string[] = [];

    while (true) {
      if (step === "scope") {
        scope = await prompt.select<"project" | "global">({
          message: `Choose an install target for ${projectRoot}`,
          choices: [
            {
              value: "project",
              name: "Project",
              description: ".codex/agents in current project",
            },
            {
              value: "global",
              name: "Global",
              description: "~/.codex/agents",
            },
          ],
        });
        step = "categories";
      }

      const categories = getCategories({
        projectRoot,
        includeProject: scope === "project",
        includeGlobal: true,
        catalogRoots: options.catalogRoots,
      });

      if (step === "categories") {
        const selectedCategorySet = new Set(selectedCategoryKeys);
        const categoryResult = await promptWithBack((context) =>
          prompt.checkbox<string>(
            {
              message: "Select categories. Leave empty to browse all agents. Esc to go back.",
              choices: categories.map((category) => ({
                value: category.key,
                name: category.title,
                description: category.description,
                checked: selectedCategorySet.has(category.key) ? true : undefined,
              })),
            },
            context,
          ),
        );
        if (categoryResult === BACK) {
          step = "scope";
          continue;
        }
        selectedCategoryKeys = categoryResult;
        step = "agents";
      }

      const categorySet = new Set(selectedCategoryKeys);
      const agentSpecs = getAgentsByCategory(categorySet, {
        projectRoot,
        includeProject: scope === "project",
        includeGlobal: true,
        catalogRoots: options.catalogRoots,
      });

      const defaultSelected = defaultAgentSelection(scope, agentSpecs);
      const availableAgentKeys = new Set(agentSpecs.map((agent) => agent.key));
      selectedAgentKeys = selectedAgentKeys.filter((key) => availableAgentKeys.has(key));

      if (step === "agents") {
        const selectedAgentSet =
          selectedAgentKeys.length > 0 ? new Set(selectedAgentKeys) : defaultSelected;
        const agentResult = await promptWithBack((context) =>
          prompt.checkbox<string>(
            {
              message: "Select subagents. Esc to go back.",
              choices: agentSpecs.map((agent) => ({
                value: agent.key,
                name: agent.name,
                description: agent.description,
                checked: selectedAgentSet.has(agent.key) ? true : undefined,
              })),
            },
            context,
          ),
        );
        if (agentResult === BACK) {
          step = "categories";
          continue;
        }

        selectedAgentKeys = agentResult;
        const selectedAgents = new Set(selectedAgentKeys);
        const validationError = validateAgentSelection(scope, agentSpecs, selectedAgents);
        if (validationError) {
          console.error(validationError);
          step = "agents";
          continue;
        }
        step = "confirm";
      }

      const selectedAgents = new Set(selectedAgentKeys);
      const confirmed = await promptWithBack((context) =>
        prompt.confirm(
          {
            message: `Install ${selectedAgents.size} agent(s) into ${resolveTargetDir(scope, projectRoot)}? Esc to go back.`,
            default: true,
          },
          context,
        ),
      );
      if (confirmed === BACK) {
        step = "agents";
        continue;
      }
      if (!confirmed) {
        step = "agents";
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
