import { CATEGORY_OVERRIDE_KEY } from "./paths";

export const ORCHESTRATOR_CATEGORY = "meta-orchestration";

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
    lines.push(`${CATEGORY_OVERRIDE_KEY} = ${JSON.stringify(agent.categoryOverride)}`);
  }

  return `${lines.join("\n")}\n`;
}
