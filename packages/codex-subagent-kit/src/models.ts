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

export interface InstallResult {
  agentPaths: string[];
  agentPreservedPaths: string[];
}

export interface DoctorIssue {
  path?: string;
  message: string;
}

export interface CatalogImportResult {
  targetRoot: string;
  importedCategoryKeys: string[];
  importedAgentKeys: string[];
  createdPaths: string[];
  preservedPaths: string[];
}

export interface DoctorReport {
  scope: string;
  targetDir: string;
  catalogCounts: Array<[string, number]>;
  installedCounts: Array<[string, number]>;
  issues: DoctorIssue[];
}
