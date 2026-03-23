from __future__ import annotations

import re
import shlex
from pathlib import Path


def _slugify_project_name(project_root: Path) -> str:
    name = re.sub(r"[^a-zA-Z0-9_-]+", "-", project_root.name).strip("-")
    return name or "project"


def _default_backend_title(project_root: Path) -> str:
    name = _slugify_project_name(project_root)
    if name.startswith("codex-subagent-kit"):
        return name
    return f"codex-subagent-kit-{name}"


def default_backend_title(project_root: Path) -> str:
    return _default_backend_title(project_root)


def _quote(value: str) -> str:
    return shlex.quote(value)


def render_run_board_script(*, project_root: Path) -> str:
    quoted_project_root = _quote(str(project_root))
    return f"""#!/bin/bash

set -euo pipefail

ROLE="${{1:?role is required}}"
INTERVAL="${{2:-2}}"
PROJECT_ROOT={quoted_project_root}
CODEX_SUBAGENT_KIT_BIN="${{CODEX_SUBAGENT_KIT_BIN:-codex-subagent-kit}}"

while true; do
  clear
  "$CODEX_SUBAGENT_KIT_BIN" board --project-root "$PROJECT_ROOT" --role "$ROLE"
  sleep "$INTERVAL"
done
"""


def render_run_monitor_script(*, project_root: Path) -> str:
    quoted_project_root = _quote(str(project_root))
    return f"""#!/bin/bash

set -euo pipefail

INTERVAL="${{1:-2}}"
PROJECT_ROOT={quoted_project_root}
CODEX_SUBAGENT_KIT_BIN="${{CODEX_SUBAGENT_KIT_BIN:-codex-subagent-kit}}"

while true; do
  clear
  "$CODEX_SUBAGENT_KIT_BIN" panel --project-root "$PROJECT_ROOT"
  sleep "$INTERVAL"
done
"""


def render_tmux_launcher(*, project_root: Path, orchestrator_key: str, worker_keys: list[str]) -> str:
    quoted_project_root = _quote(str(project_root))
    session_name = _default_backend_title(project_root)
    worker_windows = "\n".join(
        f"""  tmux new-window -t "${{SESSION}}:" -n "{worker_key}" -c "$PROJECT_ROOT" \\
    "/bin/zsh -lc '$LAUNCHER_DIR/run-board.sh {worker_key}'" """
        for worker_key in worker_keys
    )
    if worker_windows:
        worker_windows = "\n" + worker_windows

    return f"""#!/bin/bash

set -euo pipefail

SESSION="${{1:-{session_name}}}"
ATTACH_MODE="${{2:-attach}}"
PROJECT_ROOT={quoted_project_root}
LAUNCHER_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"

if ! command -v tmux >/dev/null 2>&1; then
  echo "SKIP: tmux is not installed on this machine"
  exit 0
fi

if tmux has-session -t "$SESSION" 2>/dev/null; then
  echo "tmux session '$SESSION' already exists"
else
  tmux new-session -d -s "$SESSION" -n "{orchestrator_key}" -c "$PROJECT_ROOT" \\
    "/bin/zsh -lc '$LAUNCHER_DIR/run-board.sh {orchestrator_key}'"{worker_windows}

  tmux new-window -t "${{SESSION}}:" -n monitor -c "$PROJECT_ROOT" \\
    "/bin/zsh -lc '$LAUNCHER_DIR/run-monitor.sh'"

  tmux select-window -t "${{SESSION}}:{orchestrator_key}"
fi

if [[ "$ATTACH_MODE" == "--no-attach" ]]; then
  exit 0
fi

if [[ -n "${{TMUX:-}}" ]]; then
  tmux switch-client -t "$SESSION"
else
  tmux attach-session -t "$SESSION"
fi
"""


def render_cmux_launcher(*, project_root: Path, orchestrator_key: str, worker_keys: list[str]) -> str:
    quoted_project_root = _quote(str(project_root))
    workspace_title = _default_backend_title(project_root)
    worker_role_list = " ".join(_quote(worker_key) for worker_key in worker_keys)

    return f"""#!/bin/bash

set -euo pipefail

WORKSPACE_TITLE="${{1:-{workspace_title}}}"
PROJECT_ROOT={quoted_project_root}
LAUNCHER_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"
WORKER_ROLES=({worker_role_list})

if ! command -v cmux >/dev/null 2>&1; then
  echo "SKIP: cmux is not installed on this machine"
  exit 0
fi

quote_command() {{
  local quoted

  printf -v quoted '%q ' "$@"
  printf '%s' "${{quoted% }}"
}}

respawn_surface() {{
  local workspace_ref="$1"
  local surface_ref="$2"
  local command_text="$3"

  cmux respawn-pane --workspace "$workspace_ref" --surface "$surface_ref" --command "$command_text" >/dev/null
}}

workspace_ref="$(cmux new-workspace --cwd "$PROJECT_ROOT" | awk '{{print $2}}')"
cmux rename-workspace --workspace "$workspace_ref" "$WORKSPACE_TITLE" >/dev/null

coordinator_pane="$(cmux list-panes --workspace "$workspace_ref" | sed -n '1s/^[*[:space:]]*\\(pane:[0-9]\\+\\).*/\\1/p')"
coordinator_surface="$(cmux list-pane-surfaces --workspace "$workspace_ref" --pane "$coordinator_pane" | sed -n '1s/^[*[:space:]]*\\(surface:[0-9]\\+\\).*/\\1/p')"

respawn_surface "$workspace_ref" "$coordinator_surface" "$(quote_command "$LAUNCHER_DIR/run-board.sh" "{orchestrator_key}")"

anchor_surface="$coordinator_surface"
for role_name in "${{WORKER_ROLES[@]}}"; do
  [[ -n "$role_name" ]] || continue
  new_surface="$(cmux new-split right --workspace "$workspace_ref" --surface "$anchor_surface" | awk '{{print $2}}')"
  respawn_surface "$workspace_ref" "$new_surface" "$(quote_command "$LAUNCHER_DIR/run-board.sh" "$role_name")"
  anchor_surface="$new_surface"
done

monitor_surface="$(cmux new-split down --workspace "$workspace_ref" --surface "$anchor_surface" | awk '{{print $2}}')"
respawn_surface "$workspace_ref" "$monitor_surface" "$(quote_command "$LAUNCHER_DIR/run-monitor.sh")"

cmux select-workspace --workspace "$workspace_ref" >/dev/null

echo "OK $workspace_ref $WORKSPACE_TITLE"
"""
