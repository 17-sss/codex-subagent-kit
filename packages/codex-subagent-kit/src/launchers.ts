import { basename, resolve } from "node:path";

function slugifyProjectName(projectRoot: string): string {
  const name = basename(projectRoot).replace(/[^a-zA-Z0-9_-]+/g, "-").replace(/^-+|-+$/g, "");
  return name || "project";
}

function defaultBackendTitle(projectRoot: string): string {
  const name = slugifyProjectName(projectRoot);
  return name.startsWith("codex-subagent-kit") ? name : `codex-subagent-kit-${name}`;
}

export function renderRunBoardScript(projectRoot: string): string {
  return `#!/bin/bash

set -euo pipefail

ROLE="\${1:?role is required}"
INTERVAL="\${2:-2}"
PROJECT_ROOT=${JSON.stringify(projectRoot)}
CODEX_SUBAGENT_KIT_BIN="\${CODEX_SUBAGENT_KIT_BIN:-codex-subagent-kit}"

while true; do
  clear
  "$CODEX_SUBAGENT_KIT_BIN" board --project-root "$PROJECT_ROOT" --role "$ROLE"
  sleep "$INTERVAL"
done
`;
}

export function renderRunMonitorScript(projectRoot: string): string {
  return `#!/bin/bash

set -euo pipefail

INTERVAL="\${1:-2}"
PROJECT_ROOT=${JSON.stringify(projectRoot)}
CODEX_SUBAGENT_KIT_BIN="\${CODEX_SUBAGENT_KIT_BIN:-codex-subagent-kit}"

while true; do
  clear
  "$CODEX_SUBAGENT_KIT_BIN" panel --project-root "$PROJECT_ROOT"
  sleep "$INTERVAL"
done
`;
}

export function renderTmuxLauncher(
  projectRoot: string,
  orchestratorKey: string,
  workerKeys: string[],
): string {
  const sessionName = defaultBackendTitle(projectRoot);
  const workerWindows = workerKeys
    .map(
      (workerKey) => `  tmux new-window -t "\${SESSION}:" -n "${workerKey}" -c "$PROJECT_ROOT" \\
    "/bin/zsh -lc '$LAUNCHER_DIR/run-board.sh ${workerKey}'" `,
    )
    .join("\n");

  return `#!/bin/bash

set -euo pipefail

SESSION="\${1:-${sessionName}}"
ATTACH_MODE="\${2:-attach}"
PROJECT_ROOT=${JSON.stringify(projectRoot)}
LAUNCHER_DIR="$(cd "$(dirname "\${BASH_SOURCE[0]}")" && pwd)"

if ! command -v tmux >/dev/null 2>&1; then
  echo "SKIP: tmux is not installed on this machine"
  exit 0
fi

if tmux has-session -t "$SESSION" 2>/dev/null; then
  echo "tmux session '$SESSION' already exists"
else
  tmux new-session -d -s "$SESSION" -n "${orchestratorKey}" -c "$PROJECT_ROOT" \\
    "/bin/zsh -lc '$LAUNCHER_DIR/run-board.sh ${orchestratorKey}'"${workerWindows ? `\n${workerWindows}` : ""}

  tmux new-window -t "\${SESSION}:" -n monitor -c "$PROJECT_ROOT" \\
    "/bin/zsh -lc '$LAUNCHER_DIR/run-monitor.sh'"

  tmux select-window -t "\${SESSION}:${orchestratorKey}"
fi

if [[ "$ATTACH_MODE" == "--no-attach" ]]; then
  exit 0
fi

if [[ -n "\${TMUX:-}" ]]; then
  tmux switch-client -t "$SESSION"
else
  tmux attach-session -t "$SESSION"
fi
`;
}

export function renderCmuxLauncher(
  projectRoot: string,
  orchestratorKey: string,
  workerKeys: string[],
): string {
  const workspaceTitle = defaultBackendTitle(projectRoot);
  const workerRoleList = workerKeys.map((workerKey) => JSON.stringify(workerKey)).join(" ");

  return `#!/bin/bash

set -euo pipefail

WORKSPACE_TITLE="\${1:-${workspaceTitle}}"
PROJECT_ROOT=${JSON.stringify(projectRoot)}
LAUNCHER_DIR="$(cd "$(dirname "\${BASH_SOURCE[0]}")" && pwd)"
WORKER_ROLES=(${workerRoleList})

if ! command -v cmux >/dev/null 2>&1; then
  echo "SKIP: cmux is not installed on this machine"
  exit 0
fi

quote_command() {
  local quoted

  printf -v quoted '%q ' "$@"
  printf '%s' "\${quoted% }"
}

respawn_surface() {
  local workspace_ref="$1"
  local surface_ref="$2"
  local command_text="$3"

  cmux respawn-pane --workspace "$workspace_ref" --surface "$surface_ref" --command "$command_text" >/dev/null
}

workspace_ref="$(cmux new-workspace --cwd "$PROJECT_ROOT" | awk '{print $2}')"
cmux rename-workspace --workspace "$workspace_ref" "$WORKSPACE_TITLE" >/dev/null

coordinator_pane="$(cmux list-panes --workspace "$workspace_ref" | sed -n '1s/^[*[:space:]]*\\(pane:[0-9]\\+\\).*/\\1/p')"
coordinator_surface="$(cmux list-pane-surfaces --workspace "$workspace_ref" --pane "$coordinator_pane" | sed -n '1s/^[*[:space:]]*\\(surface:[0-9]\\+\\).*/\\1/p')"

respawn_surface "$workspace_ref" "$coordinator_surface" "$(quote_command "$LAUNCHER_DIR/run-board.sh" "${orchestratorKey}")"

anchor_surface="$coordinator_surface"
for role_name in "\${WORKER_ROLES[@]}"; do
  [[ -n "$role_name" ]] || continue
  new_surface="$(cmux new-split right --workspace "$workspace_ref" --surface "$anchor_surface" | awk '{print $2}')"
  respawn_surface "$workspace_ref" "$new_surface" "$(quote_command "$LAUNCHER_DIR/run-board.sh" "$role_name")"
  anchor_surface="$new_surface"
done

monitor_surface="$(cmux new-split down --workspace "$workspace_ref" --surface "$anchor_surface" | awk '{print $2}')"
respawn_surface "$workspace_ref" "$monitor_surface" "$(quote_command "$LAUNCHER_DIR/run-monitor.sh")"

cmux select-workspace --workspace "$workspace_ref" >/dev/null

echo "OK $workspace_ref $WORKSPACE_TITLE"
`;
}
