export interface Category {
  key: string;
  title: string;
  description: string;
}

export interface AgentSpec {
  key: string;
  category: string;
  name: string;
  description: string;
  model: string;
  reasoningEffort: string;
  sandboxMode: string;
  developerInstructions: string;
  source: string;
  definitionPath?: string;
}

export interface CatalogOptions {
  projectRoot?: string;
  homeDir?: string;
  includeProject?: boolean;
  includeGlobal?: boolean;
  catalogRoots?: readonly string[];
}
