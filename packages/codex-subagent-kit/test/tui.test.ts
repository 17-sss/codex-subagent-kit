import assert from "node:assert/strict";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import test from "node:test";

import type { AgentSpec, DoctorReport, InstallResult } from "../src/models";
import { defaultAgentSelection, runTui, validateAgentSelection, type PromptAdapter } from "../src/tui";

function createTempRoot(): string {
  return mkdtempSync(join(tmpdir(), "codex-subagent-kit-ts-tui-"));
}

function cleanup(path: string): void {
  rmSync(path, { recursive: true, force: true });
}

function createAgent(overrides: Partial<AgentSpec> & Pick<AgentSpec, "key" | "category">): AgentSpec {
  return {
    key: overrides.key,
    category: overrides.category,
    name: overrides.name ?? overrides.key,
    description: overrides.description ?? `${overrides.key} description`,
    model: overrides.model ?? "gpt-5.4",
    reasoningEffort: overrides.reasoningEffort ?? "medium",
    sandboxMode: overrides.sandboxMode ?? "read-only",
    developerInstructions: overrides.developerInstructions ?? `${overrides.key} instructions`,
    source: overrides.source ?? "builtin",
    definitionPath: overrides.definitionPath,
  };
}

function withCapturedConsole<T>(run: () => Promise<T> | T): Promise<T> {
  const originalLog = console.log;
  const originalError = console.error;
  console.log = () => undefined;
  console.error = () => undefined;
  return Promise.resolve()
    .then(run)
    .finally(() => {
      console.log = originalLog;
      console.error = originalError;
    });
}

test("defaultAgentSelection prefers multi-agent-coordinator for project installs", () => {
  const selection = defaultAgentSelection("project", [
    createAgent({ key: "reviewer", category: "quality" }),
    createAgent({ key: "multi-agent-coordinator", category: "meta-orchestration" }),
    createAgent({ key: "multi-agent-coordinator", category: "meta-orchestration" }),
  ]);

  assert.deepEqual([...selection], ["multi-agent-coordinator"]);
});

test("validateAgentSelection requires an orchestrator for project installs", () => {
  const agents = [
    createAgent({ key: "reviewer", category: "quality" }),
    createAgent({ key: "multi-agent-coordinator", category: "meta-orchestration" }),
  ];

  assert.match(
    validateAgentSelection("project", agents, new Set(["reviewer"])) ?? "",
    /meta-orchestration agent/i,
  );
  assert.equal(validateAgentSelection("global", agents, new Set(["reviewer"])), undefined);
});

test("runTui installs selected agents and returns success when doctor is clean", async () => {
  const root = createTempRoot();
  const selectCalls: Array<{ message: string; choices: Array<{ value: string; name: string; checked?: boolean }> }> =
    [];
  const checkboxCalls: Array<{ message: string; choices: Array<{ value: string; name: string; checked?: boolean }> }> =
    [];
  const confirmCalls: Array<{ message: string; default?: boolean }> = [];
  const installCalls: Array<{ scope: "project" | "global"; agentKeys: string[]; projectRoot: string }> = [];

  const promptAdapter: PromptAdapter = {
    async select(config) {
      selectCalls.push(config as never);
      return "project";
    },
    async checkbox(config) {
      checkboxCalls.push(config as never);
      if (checkboxCalls.length === 1) {
        return [];
      }
      return ["reviewer", "multi-agent-coordinator"];
    },
    async confirm(config) {
      confirmCalls.push(config);
      return true;
    },
  };

  const installResult: InstallResult = {
    agentPaths: [join(root, ".codex", "agents", "multi-agent-coordinator.toml")],
    agentPreservedPaths: [],
    scaffoldCreatedPaths: [join(root, ".codex", "subagent-kit", "team.toml")],
    scaffoldPreservedPaths: [],
    orchestratorKey: "multi-agent-coordinator",
  };
  const doctorReport: DoctorReport = {
    scope: "project",
    targetDir: join(root, ".codex", "agents"),
    catalogCounts: [],
    installedCounts: [],
    issues: [],
  };

  try {
    const exitCode = await withCapturedConsole(() =>
      runTui(root, {
        promptAdapter,
        deps: {
          installAgentsImpl(options) {
            installCalls.push({
              scope: options.scope,
              agentKeys: [...options.agentKeys],
              projectRoot: options.projectRoot,
            });
            return installResult;
          },
          runDoctorImpl() {
            return doctorReport;
          },
        },
      }),
    );

    assert.equal(exitCode, 0);
    assert.equal(selectCalls.length, 1);
    assert.equal(checkboxCalls.length, 2);
    assert.equal(confirmCalls.length, 1);
    assert.equal(installCalls.length, 1);
    assert.deepEqual(installCalls[0], {
      scope: "project",
      agentKeys: ["multi-agent-coordinator", "reviewer"],
      projectRoot: root,
    });

    const agentCheckbox = checkboxCalls[1];
    const ctoChoice = agentCheckbox.choices.find((choice) => choice.value === "multi-agent-coordinator");
    assert.equal(ctoChoice?.checked, true);
  } finally {
    cleanup(root);
  }
});

test("runTui returns failure when doctor reports issues", async () => {
  const root = createTempRoot();

  try {
    const exitCode = await withCapturedConsole(() =>
      runTui(root, {
        promptAdapter: {
          async select() {
            return "global";
          },
          async checkbox(config) {
            if (config.message.includes("categories")) {
              return [];
            }
            return ["reviewer"];
          },
          async confirm() {
            return true;
          },
        },
        deps: {
          installAgentsImpl() {
            return {
              agentPaths: [],
              agentPreservedPaths: [],
              scaffoldCreatedPaths: [],
              scaffoldPreservedPaths: [],
            };
          },
          runDoctorImpl() {
            return {
              scope: "global",
              targetDir: join(root, ".codex", "agents"),
              catalogCounts: [],
              installedCounts: [],
              issues: [{ message: "broken agent" }],
            };
          },
        },
      }),
    );

    assert.equal(exitCode, 1);
  } finally {
    cleanup(root);
  }
});

test("runTui returns 130 when the prompt adapter exits early", async () => {
  const root = createTempRoot();
  const error = new Error("prompt aborted");
  error.name = "ExitPromptError";

  try {
    const exitCode = await withCapturedConsole(() =>
      runTui(root, {
        promptAdapter: {
          async select() {
            throw error;
          },
          async checkbox() {
            return [];
          },
          async confirm() {
            return false;
          },
        },
      }),
    );

    assert.equal(exitCode, 130);
  } finally {
    cleanup(root);
  }
});
