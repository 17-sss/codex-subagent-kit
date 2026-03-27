import { getAgents } from "./catalog";
import { DEFAULT_ORCHESTRATOR_KEY, ORCHESTRATOR_CATEGORY } from "./generator";

export class UsageError extends Error {}

export interface RenderUsageGuideOptions {
  projectRoot: string;
  scope: "project" | "global";
  task?: string;
  homeDir?: string;
}

function visibleInstalledAgents(options: RenderUsageGuideOptions) {
  const agents = getAgents({
    projectRoot: options.projectRoot,
    homeDir: options.homeDir,
    includeProject: options.scope === "project",
    includeGlobal: true,
  });
  const visible = agents.filter((agent) => agent.source === "project" || agent.source === "global");
  if (visible.length === 0) {
    throw new UsageError("no installed agents were found for the selected scope");
  }
  return visible;
}

function starterPrompt(task: string, orchestratorKey: string | undefined, workerKeys: string[]): string {
  if (orchestratorKey) {
    if (workerKeys.length > 0) {
      return `Use ${orchestratorKey} to coordinate this task: "${task}". Delegate to ${workerKeys.join(", ")} when appropriate.`;
    }
    return `Use ${orchestratorKey} for this task: "${task}".`;
  }

  if (workerKeys.length > 0) {
    return `For this task: "${task}", use these installed agents as needed: ${workerKeys.join(", ")}.`;
  }

  throw new UsageError("no installed agents were found for the selected scope");
}

export function renderUsageGuide(options: RenderUsageGuideOptions): string {
  const visibleAgents = visibleInstalledAgents(options);
  const taskText = (options.task ?? "<describe the task here>").trim();

  const orchestrators = visibleAgents.filter((agent) => agent.category === ORCHESTRATOR_CATEGORY);
  let orchestratorKey: string | undefined;
  if (orchestrators.length > 0) {
    orchestratorKey =
      orchestrators.find((agent) => agent.key === DEFAULT_ORCHESTRATOR_KEY)?.key ??
      orchestrators[0]?.key;
  }

  const workerKeys = visibleAgents
    .filter((agent) => agent.key !== orchestratorKey)
    .map((agent) => agent.key);

  const lines = [
    `scope: ${options.scope}`,
    "visible installed agents:",
    ...visibleAgents.map((agent) => `- ${agent.key} [${agent.source}] - ${agent.description}`),
    "",
    "starter prompt:",
    starterPrompt(taskText, orchestratorKey, workerKeys),
    "",
    "direct prompt ideas:",
    ...visibleAgents.slice(0, 6).map(
      (agent) => `- Use ${agent.key} for this task: "${taskText}". Focus on: ${agent.description}`,
    ),
    "",
    "session tip:",
    "- If Codex spawns a subagent thread, use /agent to inspect or continue that thread.",
  ];

  return lines.join("\n");
}
