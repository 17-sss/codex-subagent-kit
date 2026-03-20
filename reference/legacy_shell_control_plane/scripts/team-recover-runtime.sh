#!/bin/bash

set -euo pipefail

TEAM_INPUT="${1:?team is required}"
RECOVERY_MODE="${2:-preserve}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS_DIR="$SCRIPT_DIR"
# shellcheck disable=SC1091
source "$SCRIPTS_DIR/load-team-manifest.sh"

if [[ "$RECOVERY_MODE" != "preserve" && "$RECOVERY_MODE" != "disconnect" ]]; then
  echo "unsupported recovery mode: $RECOVERY_MODE" >&2
  echo "expected one of: preserve, disconnect" >&2
  exit 1
fi

load_team_manifest "$TEAM_INPUT"
init_team_runtime_state

repo_branch() {
  local workdir="$1"

  if git -C "$workdir" rev-parse --show-toplevel >/dev/null 2>&1; then
    git -C "$workdir" rev-parse --abbrev-ref HEAD
    return 0
  fi

  echo "-"
}

repo_dirty_count() {
  local workdir="$1"

  if git -C "$workdir" rev-parse --show-toplevel >/dev/null 2>&1; then
    git -C "$workdir" status --short | wc -l | tr -d ' '
    return 0
  fi

  echo "-"
}

repo_head_line() {
  local workdir="$1"

  if git -C "$workdir" rev-parse --show-toplevel >/dev/null 2>&1; then
    git -C "$workdir" --no-pager log --oneline -1
    return 0
  fi

  echo "git: n/a"
}

refresh_coordinator_state() {
  local current_task=""
  local last_message=""

  current_task="Inspect pending commands, prepare the next dispatch brief, and keep repo owners synchronized."
  last_message="Runtime recovered in $RECOVERY_MODE mode. Live agent bindings may need to be reattached from the main Codex conversation."

  if [[ "$RECOVERY_MODE" == "disconnect" ]]; then
    NEW_MODE="recovery-snapshot" \
    NEW_AGENT_ID="-" \
    NEW_STATUS="needs-attach" \
    NEW_CURRENT_TASK="$current_task" \
    NEW_LAST_MESSAGE="$last_message" \
    "$SCRIPTS_DIR/team-update-agent-state.sh" "$TEAM_INPUT" "$TEAM_COORDINATOR_ROLE"
  else
    NEW_CURRENT_TASK="$current_task" \
    NEW_LAST_MESSAGE="$last_message" \
    "$SCRIPTS_DIR/team-update-agent-state.sh" "$TEAM_INPUT" "$TEAM_COORDINATOR_ROLE"
  fi

  "$SCRIPTS_DIR/team-append-event.sh" \
    "$TEAM_INPUT" \
    "$TEAM_COORDINATOR_ROLE" \
    "recovered" \
    "runtime recovered in $RECOVERY_MODE mode"

  # shellcheck disable=SC1090
  source "$TEAM_RUNTIME_SUBAGENTS_DIR/$TEAM_COORDINATOR_ROLE.env"
  printf '%s | status=%s | agent_id=%s\n' "$TEAM_COORDINATOR_ROLE" "${STATUS:-"-"}" "${AGENT_ID:-"-"}"
}

refresh_repo_state() {
  local role_name="$1"
  local branch=""
  local dirty_count=""
  local head_line=""
  local current_task=""
  local last_message=""
  local dirty_label="unknown"

  load_role_manifest "$role_name"

  branch="$(repo_branch "$ROLE_WORKDIR")"
  dirty_count="$(repo_dirty_count "$ROLE_WORKDIR")"
  head_line="$(repo_head_line "$ROLE_WORKDIR")"

  if [[ "$dirty_count" == "0" ]]; then
    dirty_label="clean"
  elif [[ "$dirty_count" == "-" ]]; then
    dirty_label="git:n/a"
  else
    dirty_label="dirty:$dirty_count"
  fi

  current_task="Review pending commands, then continue $role_name owner work within the declared repo scope."
  last_message="Recovered repo snapshot: branch=$branch, $dirty_label, head=$head_line"

  if [[ "$RECOVERY_MODE" == "disconnect" ]]; then
    NEW_MODE="recovery-snapshot" \
    NEW_AGENT_ID="-" \
    NEW_STATUS="needs-rebind" \
    NEW_BRANCH="$branch" \
    NEW_CURRENT_TASK="$current_task" \
    NEW_LAST_MESSAGE="$last_message" \
    "$SCRIPTS_DIR/team-update-agent-state.sh" "$TEAM_INPUT" "$role_name"
  else
    NEW_BRANCH="$branch" \
    NEW_CURRENT_TASK="$current_task" \
    NEW_LAST_MESSAGE="$last_message" \
    "$SCRIPTS_DIR/team-update-agent-state.sh" "$TEAM_INPUT" "$role_name"
  fi

  "$SCRIPTS_DIR/team-append-event.sh" \
    "$TEAM_INPUT" \
    "$role_name" \
    "recovered" \
    "runtime recovered in $RECOVERY_MODE mode; branch=$branch; $dirty_label; head=$head_line"

  # shellcheck disable=SC1090
  source "$TEAM_RUNTIME_SUBAGENTS_DIR/$role_name.env"
  printf '%s | status=%s | branch=%s | agent_id=%s | %s\n' \
    "$role_name" \
    "${STATUS:-"-"}" \
    "${BRANCH:-"-"}" \
    "${AGENT_ID:-"-"}" \
    "$head_line"
}

refresh_coordinator_state
for role_name in "${TEAM_ROLE_ORDER[@]}"; do
  if [[ "$role_name" == "$TEAM_COORDINATOR_ROLE" ]]; then
    continue
  fi

  refresh_repo_state "$role_name"
done
