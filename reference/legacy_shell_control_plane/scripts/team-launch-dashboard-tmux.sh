#!/bin/bash

set -euo pipefail

TEAM_INPUT="${1:?team is required}"
SESSION="${2:-team-subagents}"
ATTACH_MODE="${3:-attach}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS_DIR="$SCRIPT_DIR"
# shellcheck disable=SC1091
source "$SCRIPTS_DIR/load-team-manifest.sh"

load_team_manifest "$TEAM_INPUT"
init_team_runtime_state

if ! command -v tmux >/dev/null 2>&1; then
  echo "SKIP: tmux is not installed on this machine"
  exit 0
fi

open_board_window() {
  local role_name="$1"

  tmux new-window -t "${SESSION}:" -n "$role_name" -c "$TEAM_ROOT" \
    "/bin/zsh -lc '$SCRIPTS_DIR/team-run-board.sh \"$TEAM_INPUT\" \"$role_name\"'"
}

if tmux has-session -t "$SESSION" 2>/dev/null; then
  echo "tmux session '$SESSION' already exists"
else
  tmux new-session -d -s "$SESSION" -n "${TEAM_COORDINATOR_ROLE}" -c "$TEAM_ROOT" \
    "/bin/zsh -lc '$SCRIPTS_DIR/team-run-board.sh \"$TEAM_INPUT\" \"$TEAM_COORDINATOR_ROLE\"'"

  for role_name in "${TEAM_ROLE_ORDER[@]}"; do
    if [[ "$role_name" == "$TEAM_COORDINATOR_ROLE" ]]; then
      continue
    fi
    open_board_window "$role_name"
  done

  tmux new-window -t "${SESSION}:" -n monitor -c "$TEAM_ROOT" \
    "/bin/zsh -lc '$SCRIPTS_DIR/team-run-monitor.sh \"$TEAM_INPUT\"'"

  tmux select-window -t "${SESSION}:$TEAM_COORDINATOR_ROLE"
fi

if [[ "$ATTACH_MODE" == "--no-attach" ]]; then
  exit 0
fi

if [[ -n "${TMUX:-}" ]]; then
  tmux switch-client -t "$SESSION"
else
  tmux attach-session -t "$SESSION"
fi
