#!/bin/bash

set -euo pipefail

TEAM_INPUT="${1:?team is required}"
WORKSPACE_TITLE="${2:-team-subagents}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS_DIR="$SCRIPT_DIR"
# shellcheck disable=SC1091
source "$SCRIPTS_DIR/load-team-manifest.sh"

load_team_manifest "$TEAM_INPUT"
init_team_runtime_state

if ! command -v cmux >/dev/null 2>&1; then
  echo "SKIP: cmux is not installed on this machine"
  exit 0
fi

quote_command() {
  local quoted

  printf -v quoted '%q ' "$@"
  printf '%s' "${quoted% }"
}

respawn_surface() {
  local workspace_ref="$1"
  local surface_ref="$2"
  local command_text="$3"

  cmux respawn-pane --workspace "$workspace_ref" --surface "$surface_ref" --command "$command_text" >/dev/null
}

run_board_surface() {
  local workspace_ref="$1"
  local surface_ref="$2"
  local role_name="$3"

  respawn_surface "$workspace_ref" "$surface_ref" "$(quote_command "$SCRIPTS_DIR/team-run-board.sh" "$TEAM_INPUT" "$role_name")"
}

run_monitor_surface() {
  local workspace_ref="$1"
  local surface_ref="$2"

  respawn_surface "$workspace_ref" "$surface_ref" "$(quote_command "$SCRIPTS_DIR/team-run-monitor.sh" "$TEAM_INPUT")"
}

workspace_ref="$(cmux new-workspace --cwd "$TEAM_ROOT" | awk '{print $2}')"
cmux rename-workspace --workspace "$workspace_ref" "$WORKSPACE_TITLE" >/dev/null

coordinator_pane="$(cmux list-panes --workspace "$workspace_ref" | sed -n '1s/^[*[:space:]]*\(pane:[0-9]\+\).*/\1/p')"
coordinator_surface="$(cmux list-pane-surfaces --workspace "$workspace_ref" --pane "$coordinator_pane" | sed -n '1s/^[*[:space:]]*\(surface:[0-9]\+\).*/\1/p')"

run_board_surface "$workspace_ref" "$coordinator_surface" "$TEAM_COORDINATOR_ROLE"

left_anchor="$coordinator_surface"
right_anchor=""
surface_index=0

for role_name in "${TEAM_ROLE_ORDER[@]}"; do
  new_surface=""

  if [[ "$role_name" == "$TEAM_COORDINATOR_ROLE" ]]; then
    continue
  fi

  if [[ -z "$right_anchor" ]]; then
    new_surface="$(cmux new-split right --workspace "$workspace_ref" --surface "$coordinator_surface" | awk '{print $2}')"
    right_anchor="$new_surface"
    run_board_surface "$workspace_ref" "$new_surface" "$role_name"
    continue
  fi

  if (( surface_index % 2 == 0 )); then
    new_surface="$(cmux new-split down --workspace "$workspace_ref" --surface "$left_anchor" | awk '{print $2}')"
    left_anchor="$new_surface"
  else
    new_surface="$(cmux new-split down --workspace "$workspace_ref" --surface "$right_anchor" | awk '{print $2}')"
    right_anchor="$new_surface"
  fi

  run_board_surface "$workspace_ref" "$new_surface" "$role_name"
  surface_index=$((surface_index + 1))
done

monitor_surface="$(cmux new-split down --workspace "$workspace_ref" --surface "${right_anchor:-$coordinator_surface}" | awk '{print $2}')"
run_monitor_surface "$workspace_ref" "$monitor_surface"

cmux select-workspace --workspace "$workspace_ref" >/dev/null

echo "OK $workspace_ref $WORKSPACE_TITLE"
