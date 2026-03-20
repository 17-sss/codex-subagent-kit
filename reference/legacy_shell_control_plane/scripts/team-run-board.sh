#!/bin/bash

set -euo pipefail

TEAM_INPUT="${1:?team is required}"
ROLE_NAME="${2:?role is required}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS_DIR="$SCRIPT_DIR"
# shellcheck disable=SC1091
source "$SCRIPTS_DIR/load-team-manifest.sh"

TEAM_INPUT="$TEAM_INPUT"
ROLE_NAME="$ROLE_NAME"

STATE_MODE="manifest-default"
STATE_AGENT_ID="-"
STATE_MODEL="-"
STATE_STATUS="not-connected"
STATE_LAST_UPDATED="-"
STATE_CURRENT_TASK="-"
STATE_LAST_MESSAGE="-"
STATE_OWNER="-"
STATE_BRANCH="-"

load_state() {
  local state_file=""

  state_file="$TEAM_RUNTIME_SUBAGENTS_DIR/$ROLE_NAME.env"

  STATE_MODE="manifest-default"
  STATE_AGENT_ID="-"
  STATE_MODEL="${ROLE_DEFAULT_MODEL:-$TEAM_DEFAULT_MODEL}"
  STATE_STATUS="${ROLE_DEFAULT_STATUS:-not-started}"
  STATE_LAST_UPDATED="-"
  STATE_CURRENT_TASK="${ROLE_DEFAULT_TASK:-"-"}"
  STATE_LAST_MESSAGE="${ROLE_DEFAULT_MESSAGE:-"-"}"
  STATE_OWNER="$ROLE_WORKDIR_REL"
  STATE_BRANCH="${ROLE_DEFAULT_BRANCH:-"-"}"

  if [[ ! -f "$state_file" ]]; then
    return
  fi

  # shellcheck disable=SC1090
  source "$state_file"

  STATE_MODE="${MODE:-$STATE_MODE}"
  STATE_AGENT_ID="${AGENT_ID:-$STATE_AGENT_ID}"
  STATE_MODEL="${MODEL:-$STATE_MODEL}"
  STATE_STATUS="${STATUS:-$STATE_STATUS}"
  STATE_LAST_UPDATED="${LAST_UPDATED:-$STATE_LAST_UPDATED}"
  STATE_CURRENT_TASK="${CURRENT_TASK:-$STATE_CURRENT_TASK}"
  STATE_LAST_MESSAGE="${LAST_MESSAGE:-$STATE_LAST_MESSAGE}"
  STATE_OWNER="${OWNER:-$STATE_OWNER}"
  STATE_BRANCH="${BRANCH:-$STATE_BRANCH}"
}

print_handoff_excerpt() {
  if [[ -f "$ROLE_HANDOFF" ]]; then
    sed -n '1,22p' "$ROLE_HANDOFF"
    return
  fi

  echo "handoff file not found: $ROLE_HANDOFF"
}

print_workspace_handoff_excerpt() {
  if [[ -f "$TEAM_WORKSPACE_HANDOFF" ]]; then
    sed -n '1,22p' "$TEAM_WORKSPACE_HANDOFF"
    return
  fi

  echo "workspace handoff file not found: $TEAM_WORKSPACE_HANDOFF"
}

print_repo_state() {
  if git -C "$ROLE_WORKDIR" rev-parse --show-toplevel >/dev/null 2>&1; then
    git -C "$ROLE_WORKDIR" status --short
    echo
    git -C "$ROLE_WORKDIR" --no-pager log --oneline -3
    return
  fi

  echo "git: n/a"
}

print_recent_pending_commands() {
  local shown=0
  local command_files=()

  shopt -s nullglob
  command_files=("$TEAM_RUNTIME_QUEUE_PENDING_DIR"/*.env)

  if (( ${#command_files[@]} == 0 )); then
    echo "no pending commands"
    return
  fi

  for (( idx=${#command_files[@]} - 1; idx>=0 && shown<5; idx-- )); do
    local file_path="${command_files[idx]}"
    local line

    line="$(
      (
        # shellcheck disable=SC1090
        source "$file_path"
        if [[ "$ROLE_NAME" == "$TEAM_COORDINATOR_ROLE" || "$ROLE" == "$ROLE_NAME" ]]; then
          printf '%s [%s/%s/%s/claimed:%s] %s\n' \
            "$ID" \
            "$ROLE" \
            "$STATUS" \
            "${PRIORITY:-normal}" \
            "${CLAIMED_BY:-"-"}" \
            "$COMMAND"
        fi
      )
    )"

    if [[ -n "$line" ]]; then
      echo "$line"
      shown=$((shown + 1))
    fi
  done

  if (( shown == 0 )); then
    echo "no pending commands"
  fi
}

print_recent_events() {
  local event_file="$TEAM_RUNTIME_EVENTS_DIR/$ROLE_NAME.log"

  if [[ ! -f "$event_file" ]]; then
    echo "no events"
    return
  fi

  tail -n 5 "$event_file"
}

print_next_candidate() {
  local role_filter="${1:-all}"
  local candidate=""

  if candidate="$("$SCRIPTS_DIR/team-pick-command.sh" "$TEAM_INPUT" "$role_filter" summary 2>/dev/null)"; then
    echo "$candidate"
    return
  fi

  echo "no pickable pending command"
}

count_dispatch_dir() {
  local dir_path="$1"
  local count=0
  local file_path

  shopt -s nullglob
  for file_path in "$dir_path"/*.env; do
    count=$((count + 1))
  done

  echo "$count"
}

print_recent_dispatches() {
  local shown=0
  local dispatch_files=()
  local file_path
  local line

  shopt -s nullglob
  dispatch_files=(
    "$TEAM_RUNTIME_DISPATCH_ACTIVE_DIR"/*.env
    "$TEAM_RUNTIME_DISPATCH_READY_DIR"/*.env
    "$TEAM_RUNTIME_DISPATCH_ARCHIVE_DIR"/*.env
  )

  if (( ${#dispatch_files[@]} == 0 )); then
    echo "no dispatch records"
    return
  fi

  for (( idx=${#dispatch_files[@]} - 1; idx>=0 && shown<5; idx-- )); do
    file_path="${dispatch_files[idx]}"
    line="$(
      (
        # shellcheck disable=SC1090
        source "$file_path"
        if [[ "$ROLE_NAME" == "$TEAM_COORDINATOR_ROLE" || "$ROLE" == "$ROLE_NAME" ]]; then
          printf '%s [%s/%s/agent:%s] command=%s\n' \
            "$DISPATCH_ID" \
            "$ROLE" \
            "$STATE" \
            "${TARGET_AGENT_ID:-"-"}" \
            "$COMMAND_ID"
        fi
      )
    )"

    if [[ -n "$line" ]]; then
      echo "$line"
      shown=$((shown + 1))
    fi
  done

  if (( shown == 0 )); then
    echo "no dispatch records"
  fi
}

render_coordinator_board() {
  echo "[team]"
  echo "$TEAM_NAME"
  echo
  echo "[mode]"
  echo "manifest-based sub-agent dashboard"
  echo
  echo "[important]"
  echo "this pane does not host the real sub-agents."
  echo "the main Codex conversation is the coordinator and uses spawn_agent to create the live team."
  echo
  echo "[runtime state]"
  echo "mode: $STATE_MODE"
  echo "agent_id: $STATE_AGENT_ID"
  echo "model: $STATE_MODEL"
  echo "status: $STATE_STATUS"
  echo "last_updated: $STATE_LAST_UPDATED"
  echo "current_task: $STATE_CURRENT_TASK"
  echo "last_message: $STATE_LAST_MESSAGE"
  echo
  echo "[command inbox]"
  print_recent_pending_commands
  echo
  echo "[next dispatch candidate]"
  print_next_candidate "all"
  echo
  echo "[dispatch summary]"
  printf 'ready=%s active=%s archive=%s\n' \
    "$(count_dispatch_dir "$TEAM_RUNTIME_DISPATCH_READY_DIR")" \
    "$(count_dispatch_dir "$TEAM_RUNTIME_DISPATCH_ACTIVE_DIR")" \
    "$(count_dispatch_dir "$TEAM_RUNTIME_DISPATCH_ARCHIVE_DIR")"
  echo
  echo "[recent dispatches]"
  print_recent_dispatches
  echo
  echo "[control commands]"
  echo "bootstrap: $SCRIPTS_DIR/team-bootstrap-runtime.sh $TEAM_INPUT"
  echo "recover: $SCRIPTS_DIR/team-recover-runtime.sh $TEAM_INPUT disconnect"
  echo "prepare dispatch: $SCRIPTS_DIR/team-prepare-dispatch.sh $TEAM_INPUT"
  echo
  echo "[recent events]"
  print_recent_events
  echo
  echo "[workspace handoff]"
  print_workspace_handoff_excerpt
  echo
  echo "[role handoff]"
  print_handoff_excerpt
}

render_repo_board() {
  echo "[team]"
  echo "$TEAM_NAME"
  echo
  echo "[mode]"
  echo "manifest-based sub-agent dashboard"
  echo
  echo "[role]"
  echo "$ROLE_TITLE"
  echo
  echo "[stack]"
  echo "$ROLE_STACK_INFO"
  echo
  echo "[owner scope]"
  echo "$ROLE_OWNER_SCOPE"
  echo
  echo "[runtime state]"
  echo "mode: $STATE_MODE"
  echo "owner: $STATE_OWNER"
  echo "agent_id: $STATE_AGENT_ID"
  echo "model: $STATE_MODEL"
  echo "status: $STATE_STATUS"
  echo "branch: $STATE_BRANCH"
  echo "last_updated: $STATE_LAST_UPDATED"
  echo "current_task: $STATE_CURRENT_TASK"
  echo "last_message: $STATE_LAST_MESSAGE"
  echo
  echo "[pending commands]"
  print_recent_pending_commands
  echo
  echo "[next role candidate]"
  print_next_candidate "$ROLE_NAME"
  echo
  echo "[recent dispatches]"
  print_recent_dispatches
  echo
  echo "[recent events]"
  print_recent_events
  echo
  echo "[sync rule]"
  echo "$ROLE_SYNC_RULE"
  echo
  echo "[repo]"
  echo "$ROLE_WORKDIR"
  echo
  echo "[handoff]"
  echo "$ROLE_HANDOFF"
  echo
  echo "[repo state]"
  print_repo_state
  echo
  echo "[handoff excerpt]"
  print_handoff_excerpt
}

load_team_manifest "$TEAM_INPUT"
init_team_runtime_state
load_role_manifest "$ROLE_NAME"
load_state

while true; do
  clear
  date
  echo
  load_state

  if [[ "$ROLE_KIND" == "coordinator" ]]; then
    render_coordinator_board
  else
    render_repo_board
  fi

  sleep 5
done
