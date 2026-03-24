export const STABLE_COMMANDS = [
  "catalog",
  "catalog import",
  "install",
  "doctor",
  "usage",
  "template init",
  "tui",
] as const;

export const EXPERIMENTAL_COMMANDS = [
  "panel",
  "board",
  "launch",
  "enqueue",
  "dispatch-open",
  "dispatch-prepare",
  "dispatch-begin",
  "apply-result",
] as const;

export function renderBootstrapMessage(commandName: string): string {
  return [
    `The TypeScript port is in progress, but '${commandName}' is not implemented yet.`,
    "Use the legacy Python codex-subagent-kit app if you need a workflow outside the current TypeScript scope.",
    "See docs/TYPESCRIPT_PORT.md for the current port boundary and delivery order.",
  ].join("\n");
}
