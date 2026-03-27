#!/usr/bin/env node

import { resolve } from "node:path";

import { Command } from "commander";

import { renderCatalogOutput } from "./catalog";
import { CatalogImportError, importCatalog } from "./catalog-import";
import { CatalogSyncError, syncCatalog } from "./catalog-sync";
import { renderDoctorReport, runDoctor } from "./doctor";
import { GenerationError, installAgents, resolveTargetDir } from "./generator";
import { STABLE_COMMANDS } from "./meta";
import { initTemplate, TemplateError } from "./templates";
import { runTui } from "./tui";
import { renderUsageGuide, UsageError } from "./usage";

type StringArrayOption = string[];

function collectRepeatedOption(value: string, previous: StringArrayOption = []): StringArrayOption {
  return [...previous, value];
}

function buildCatalogCommand(): Command {
  const catalog = new Command("catalog")
    .description("Browse the stable subagent catalog.")
    .argument("[operation]", "Optional operation. Use 'import' for persistent catalog imports.")
    .option("--project-root <path>", "Project root used for project-scope catalog discovery.", ".")
    .option("--scope <scope>", "Catalog visibility scope: project or global.", "project")
    .option(
      "--catalog-root <path>",
      "One external awesome-style categories root. Repeat to provide more than one.",
      collectRepeatedOption,
      [],
    )
    .option("--source-name <name>", "Synced source name for catalog sync.", "voltagent")
    .option("--source-root <path>", "Local awesome-style categories root used for catalog sync.")
    .option("--agents <keys>", "Comma-separated agent keys to import.")
    .option("--categories <keys>", "Comma-separated category keys to import.")
    .option("--overwrite", "Overwrite existing imported templates.")
    .action(async (operation: string | undefined, options: { projectRoot: string; scope: string; catalogRoot: string[]; sourceName: string; sourceRoot?: string; agents?: string; categories?: string; overwrite?: boolean }) => {
      if (!operation) {
        console.log(
          renderCatalogOutput({
            projectRoot: options.projectRoot,
            includeProject: options.scope === "project",
            includeGlobal: true,
            catalogRoots: options.catalogRoot ?? [],
          }),
        );
        return;
      }

      if (operation === "sync") {
        try {
          const result = await syncCatalog({
            projectRoot: options.projectRoot,
            scope: options.scope as "project" | "global",
            sourceName: options.sourceName,
            sourceRoot: options.sourceRoot,
          });
          console.log(`source: ${result.sourceName}`);
          console.log(`origin: ${result.sourceLabel}`);
          console.log(`target: ${result.targetRoot}`);
          console.log(`files: ${result.copiedPaths.length}`);
          for (const path of result.copiedPaths.slice(0, 10)) {
            console.log(`synced: ${path}`);
          }
          if (result.copiedPaths.length > 10) {
            console.log(`... ${result.copiedPaths.length - 10} more`);
          }
        } catch (error) {
          const message = error instanceof CatalogSyncError ? error.message : String(error);
          console.error(`error: ${message}`);
          process.exitCode = 1;
        }
        return;
      }

      if (operation !== "import") {
        console.error(`error: unknown catalog operation: ${operation}`);
        process.exitCode = 1;
        return;
      }

      try {
        const result = importCatalog({
          projectRoot: options.projectRoot,
          scope: options.scope as "project" | "global",
          catalogRoots: options.catalogRoot ?? [],
          agentKeys: (options.agents ?? "")
            .split(",")
            .map((item) => item.trim())
            .filter(Boolean),
          categoryKeys: (options.categories ?? "")
            .split(",")
            .map((item) => item.trim())
            .filter(Boolean),
          overwrite: options.overwrite,
        });

        console.log(`target: ${result.targetRoot}`);
        if (result.importedCategoryKeys.length > 0) {
          console.log(`categories: ${result.importedCategoryKeys.join(", ")}`);
        }
        if (result.importedAgentKeys.length > 0) {
          console.log(`agents: ${result.importedAgentKeys.join(", ")}`);
        }
        for (const path of result.createdPaths) {
          console.log(`created: ${path}`);
        }
        for (const path of result.preservedPaths) {
          console.log(`preserved: ${path}`);
        }
      } catch (error) {
        const message = error instanceof CatalogImportError ? error.message : String(error);
        console.error(`error: ${message}`);
        process.exitCode = 1;
      }
    });

  return catalog;
}

function buildTemplateCommand(): Command {
  const template = new Command("template").description("Scaffold custom catalog templates.");

  template
    .command("init")
    .description("Create a category README and agent TOML skeleton.")
    .option("--project-root <path>", "Project root used for project-scope templates.", ".")
    .option("--scope <scope>", "Template target scope: project or global.", "project")
    .option("--catalog-root <path>", "Explicit external categories root.")
    .requiredOption("--category <key>", "Category key, for example custom-ops.")
    .option("--category-prefix <prefix>", "Numeric category prefix, for example 11.")
    .option("--category-title <title>", "Display title for the category.")
    .option("--category-description <description>", "Short category description.")
    .requiredOption("--agent <key>", "Agent key, for example custom-coordinator.")
    .option("--agent-name <name>", "Human-friendly agent name.")
    .option("--agent-description <description>", "Short agent description.")
    .option("--model <model>", "Model name used in the generated TOML.", "gpt-5.4")
    .option("--reasoning-effort <level>", "Model reasoning effort.", "medium")
    .option("--sandbox-mode <mode>", "Sandbox mode stored in the generated TOML.", "read-only")
    .option("--orchestrator", "Mark the generated agent as a root orchestrator template.")
    .option("--overwrite", "Overwrite existing template files.")
    .action((options: {
      projectRoot: string;
      scope: "project" | "global";
      catalogRoot?: string;
      category: string;
      categoryPrefix?: string;
      categoryTitle?: string;
      categoryDescription?: string;
      agent: string;
      agentName?: string;
      agentDescription?: string;
      model: string;
      reasoningEffort: string;
      sandboxMode: string;
      orchestrator?: boolean;
      overwrite?: boolean;
    }) => {
      try {
        const result = initTemplate({
          projectRoot: options.projectRoot,
          scope: options.scope,
          catalogRoot: options.catalogRoot,
          categoryKey: options.category,
          categoryPrefix: options.categoryPrefix,
          categoryTitle: options.categoryTitle,
          categoryDescription: options.categoryDescription,
          agentKey: options.agent,
          agentName: options.agentName,
          agentDescription: options.agentDescription,
          model: options.model,
          reasoningEffort: options.reasoningEffort,
          sandboxMode: options.sandboxMode,
          orchestrator: options.orchestrator,
          overwrite: options.overwrite,
        });

        console.log(`target: ${result.targetRoot}`);
        console.log(`category: ${result.categoryDir}`);
        console.log(`agent: ${result.agentPath}`);
        for (const path of result.createdPaths) {
          console.log(`created: ${path}`);
        }
        for (const path of result.preservedPaths) {
          console.log(`preserved: ${path}`);
        }
      } catch (error) {
        const message = error instanceof TemplateError ? error.message : String(error);
        console.error(`error: ${message}`);
        process.exitCode = 1;
      }
    });

  return template;
}

export function buildProgram(): Command {
  const program = new Command();

  program
    .name("codex-subagent-kit")
    .description("Install and manage Codex subagent catalogs, templates, and TOML definitions.")
    .addHelpText(
      "after",
      [
        "",
        `Stable commands available: ${STABLE_COMMANDS.join(", ")}`,
      ].join("\n"),
    )
    .action(async () => {
      process.exitCode = await runTui(resolve(process.cwd()), {
        catalogRoots: [],
      });
    });

  program
    .command("install")
    .description("Install selected subagents without the TUI.")
    .requiredOption("--scope <scope>", "Install target scope: project or global.")
    .requiredOption("--agents <keys>", "Comma-separated agent keys.")
    .option("--project-root <path>", "Project root used for project-scope installs.", ".")
    .option(
      "--catalog-root <path>",
      "One external awesome-style categories root. Repeat to provide more than one.",
      collectRepeatedOption,
      [],
    )
    .option("--overwrite", "Overwrite existing generated agent files.")
    .option("--validate", "Run doctor immediately after install.")
    .action((options: {
      scope: "project" | "global";
      agents: string;
      projectRoot: string;
      catalogRoot: string[];
      overwrite?: boolean;
      validate?: boolean;
    }) => {
      try {
        const result = installAgents({
          scope: options.scope,
          projectRoot: options.projectRoot,
          agentKeys: options.agents
            .split(",")
            .map((item) => item.trim())
            .filter(Boolean),
          catalogRoots: options.catalogRoot ?? [],
          overwrite: options.overwrite,
        });

        console.log(`target: ${resolveTargetDir(options.scope, options.projectRoot)}`);
        for (const path of result.agentPaths) {
          console.log(path);
        }
        for (const path of result.agentPreservedPaths) {
          console.log(`agent preserved: ${path}`);
        }

        if (!options.validate) {
          return;
        }

        const report = runDoctor({
          projectRoot: options.projectRoot,
          scope: options.scope,
          catalogRoots: options.catalogRoot ?? [],
        });
        console.log("");
        console.log(renderDoctorReport(report));
        if (report.issues.length > 0) {
          process.exitCode = 1;
        }
      } catch (error) {
        const message = error instanceof GenerationError ? error.message : String(error);
        console.error(`error: ${message}`);
        process.exitCode = 1;
      }
    });

  program
    .command("doctor")
    .description("Validate installed agent definitions and injected catalog roots.")
    .option("--project-root <path>", "Project root used for project-scope validation.", ".")
    .option("--scope <scope>", "Validation scope: project or global.", "project")
    .option(
      "--catalog-root <path>",
      "One external awesome-style categories root. Repeat to provide more than one.",
      collectRepeatedOption,
      [],
    )
    .action((options: {
      projectRoot: string;
      scope: "project" | "global";
      catalogRoot: string[];
    }) => {
      const report = runDoctor({
        projectRoot: options.projectRoot,
        scope: options.scope,
        catalogRoots: options.catalogRoot ?? [],
      });
      console.log(renderDoctorReport(report));
      if (report.issues.length > 0) {
        process.exitCode = 1;
      }
    });

  program
    .command("usage")
    .description("Render starter prompts for the installed agents visible in the selected scope.")
    .option("--project-root <path>", "Project root used for project-scope usage output.", ".")
    .option("--scope <scope>", "Usage scope: project or global.", "project")
    .option("--task <description>", "Task description to embed in the starter prompt.")
    .action((options: {
      projectRoot: string;
      scope: "project" | "global";
      task?: string;
    }) => {
      try {
        console.log(
          renderUsageGuide({
            projectRoot: options.projectRoot,
            scope: options.scope,
            task: options.task,
          }),
        );
      } catch (error) {
        const message = error instanceof UsageError ? error.message : String(error);
        console.error(`error: ${message}`);
        process.exitCode = 1;
      }
    });

  program
    .command("tui")
    .description("Run the interactive install-first TUI.")
    .option("--project-root <path>", "Project root used for the install session.", ".")
    .option(
      "--catalog-root <path>",
      "One external awesome-style categories root. Repeat to provide more than one.",
      collectRepeatedOption,
      [],
    )
    .action(async (options: { projectRoot: string; catalogRoot: string[] }) => {
      process.exitCode = await runTui(resolve(options.projectRoot), {
        catalogRoots: options.catalogRoot ?? [],
      });
    });

  program.addCommand(buildCatalogCommand());
  program.addCommand(buildTemplateCommand());

  return program;
}

export async function main(argv: string[] = process.argv): Promise<number> {
  const program = buildProgram();
  await program.parseAsync(argv);
  return typeof process.exitCode === "number" ? process.exitCode : 0;
}

if (require.main === module) {
  void main().then((exitCode) => {
    process.exitCode = exitCode;
  });
}
