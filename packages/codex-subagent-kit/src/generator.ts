import { chmodSync, existsSync, mkdirSync, statSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";

import { getAgentMap } from "./catalog";
import {
  renderCmuxLauncher,
  renderRunBoardScript,
  renderRunMonitorScript,
  renderTmuxLauncher,
} from "./launchers";
import type { AgentSpec, InstallResult } from "./models";
import {
  resolveGlobalAgentsDir,
  resolveProjectAgentsDir,
  resolveProjectToolDir,
} from "./paths";

export class GenerationError extends Error {}

export const ORCHESTRATOR_CATEGORY = "meta-orchestration";
export const DEFAULT_ORCHESTRATOR_KEY = "cto-coordinator";

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

export function resolveScaffoldDir(projectRoot: string): string {
  return resolveProjectToolDir(projectRoot);
}

export function resolveScaffoldCatalogDir(projectRoot: string): string {
  return resolve(resolveScaffoldDir(projectRoot), "catalog", "categories");
}

function renderStringList(items: string[]): string {
  return `[${items.map((item) => JSON.stringify(item)).join(", ")}]`;
}

export function renderTeamManifest(orchestratorKey: string, workerKeys: string[]): string {
  return `version = 1

[operator]
label = "user"

[team]
orchestrator = ${JSON.stringify(orchestratorKey)}
workers = ${renderStringList(workerKeys)}

[control_panel]
topology = "operator-orchestrator-workers"
`;
}

export function renderRuntimeState(orchestratorKey: string, workerKeys: string[]): string {
  const workerBlocks = workerKeys
    .map((workerKey) => `[[workers]]
key = ${JSON.stringify(workerKey)}
status = "idle"
`)
    .join("\n");

  return `version = 1

[orchestrator]
key = ${JSON.stringify(orchestratorKey)}
status = "idle"
${workerBlocks ? `\n${workerBlocks}` : ""}
`;
}

export function renderQueueSeed(): string {
  return "version = 1\n";
}

export function renderDispatchLedgerSeed(): string {
  return "version = 1\n";
}

export function renderScaffoldReadme(orchestratorKey: string, workerKeys: string[]): string {
  const workerSummary = workerKeys.length > 0 ? workerKeys.map((workerKey) => `\`${workerKey}\``).join(", ") : "none yet";

  return `# orchestrator scaffold

This folder is the project-local seed for the future control-plane.

## Team topology

- operator/user
- root orchestrator: \`${orchestratorKey}\`
- workers: ${workerSummary}

## Notes

- \`.codex/agents/\` keeps static agent definitions.
- \`.codex/subagent-kit/\` keeps team and runtime-oriented assets.
- \`.codex/subagent-kit/catalog/categories/\` is the project-local catalog injection point for custom category directories and agent templates.
- \`runtime/agents.toml\` tracks orchestrator/worker runtime status.
- \`queue/commands.toml\` is the queue seed for future operator commands.
- \`ledger/dispatches.toml\` is the dispatch ledger seed.
`;
}

export function resolveOrchestratorKey(agentMap: Map<string, AgentSpec>, agentKeys: string[]): string {
  const candidates = agentKeys
    .filter((key) => agentMap.get(key)?.category === ORCHESTRATOR_CATEGORY)
    .sort();

  if (candidates.length === 0) {
    throw new GenerationError(
      "project installs require at least one meta-orchestration agent for the root orchestrator",
    );
  }

  return candidates.includes(DEFAULT_ORCHESTRATOR_KEY) ? DEFAULT_ORCHESTRATOR_KEY : candidates[0];
}

function ensureDirectory(
  path: string,
  createdPaths: string[],
  preservedPaths: string[],
): void {
  if (existsSync(path)) {
    if (!statSync(path).isDirectory()) {
      throw new GenerationError(`expected directory but found file: ${path}`);
    }
    preservedPaths.push(path);
    return;
  }

  mkdirSync(path, { recursive: true });
  createdPaths.push(path);
}

function writeSeedFile(
  path: string,
  content: string,
  createdPaths: string[],
  preservedPaths: string[],
  executable = false,
): void {
  if (existsSync(path)) {
    if (statSync(path).isDirectory()) {
      throw new GenerationError(`expected file but found directory: ${path}`);
    }
    preservedPaths.push(path);
    return;
  }

  writeFileSync(path, content, "utf8");
  if (executable) {
    chmodSync(path, 0o755);
  }
  createdPaths.push(path);
}

export function generateProjectScaffold(
  projectRoot: string,
  agentMap: Map<string, AgentSpec>,
  agentKeys: string[],
): { orchestratorKey: string; createdPaths: string[]; preservedPaths: string[] } {
  const orchestratorKey = resolveOrchestratorKey(agentMap, agentKeys);
  const workerKeys = [...agentKeys].sort().filter((key) => key !== orchestratorKey);
  const scaffoldRoot = resolveScaffoldDir(projectRoot);
  const createdPaths: string[] = [];
  const preservedPaths: string[] = [];

  ensureDirectory(scaffoldRoot, createdPaths, preservedPaths);
  ensureDirectory(resolve(scaffoldRoot, "runtime"), createdPaths, preservedPaths);
  ensureDirectory(resolve(scaffoldRoot, "queue"), createdPaths, preservedPaths);
  ensureDirectory(resolve(scaffoldRoot, "ledger"), createdPaths, preservedPaths);
  ensureDirectory(resolve(scaffoldRoot, "launchers"), createdPaths, preservedPaths);
  ensureDirectory(resolve(scaffoldRoot, "catalog"), createdPaths, preservedPaths);
  ensureDirectory(resolve(scaffoldRoot, "catalog", "categories"), createdPaths, preservedPaths);

  writeSeedFile(
    resolve(scaffoldRoot, "team.toml"),
    renderTeamManifest(orchestratorKey, workerKeys),
    createdPaths,
    preservedPaths,
  );
  writeSeedFile(
    resolve(scaffoldRoot, "README.md"),
    renderScaffoldReadme(orchestratorKey, workerKeys),
    createdPaths,
    preservedPaths,
  );
  writeSeedFile(
    resolve(scaffoldRoot, "runtime", "agents.toml"),
    renderRuntimeState(orchestratorKey, workerKeys),
    createdPaths,
    preservedPaths,
  );
  writeSeedFile(
    resolve(scaffoldRoot, "queue", "commands.toml"),
    renderQueueSeed(),
    createdPaths,
    preservedPaths,
  );
  writeSeedFile(
    resolve(scaffoldRoot, "ledger", "dispatches.toml"),
    renderDispatchLedgerSeed(),
    createdPaths,
    preservedPaths,
  );
  writeSeedFile(
    resolve(scaffoldRoot, "launchers", "run-board.sh"),
    renderRunBoardScript(projectRoot),
    createdPaths,
    preservedPaths,
    true,
  );
  writeSeedFile(
    resolve(scaffoldRoot, "launchers", "run-monitor.sh"),
    renderRunMonitorScript(projectRoot),
    createdPaths,
    preservedPaths,
    true,
  );
  writeSeedFile(
    resolve(scaffoldRoot, "launchers", "launch-tmux.sh"),
    renderTmuxLauncher(projectRoot, orchestratorKey, workerKeys),
    createdPaths,
    preservedPaths,
    true,
  );
  writeSeedFile(
    resolve(scaffoldRoot, "launchers", "launch-cmux.sh"),
    renderCmuxLauncher(projectRoot, orchestratorKey, workerKeys),
    createdPaths,
    preservedPaths,
    true,
  );

  return { orchestratorKey, createdPaths, preservedPaths };
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

  let scaffoldCreatedPaths: string[] = [];
  let scaffoldPreservedPaths: string[] = [];
  let orchestratorKey: string | undefined;

  if (options.scope === "project") {
    const scaffold = generateProjectScaffold(options.projectRoot, agentMap, options.agentKeys);
    scaffoldCreatedPaths = scaffold.createdPaths;
    scaffoldPreservedPaths = scaffold.preservedPaths;
    orchestratorKey = scaffold.orchestratorKey;
  }

  return {
    agentPaths,
    agentPreservedPaths,
    scaffoldCreatedPaths,
    scaffoldPreservedPaths,
    orchestratorKey,
  };
}
