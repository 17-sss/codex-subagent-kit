#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REFERENCE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
REFERENCE_TEAMS_ROOT="${CODEX_ORCHESTRATOR_REFERENCE_TEAMS_ROOT:-$REFERENCE_ROOT/teams}"
REFERENCE_RUNTIME_ROOT="${CODEX_ORCHESTRATOR_REFERENCE_RUNTIME_ROOT:-$REFERENCE_ROOT/runtime}"

resolve_team_dir() {
  local team_input="${1:?team input is required}"
  local manifest_root="$REFERENCE_TEAMS_ROOT"

  if [[ -d "$team_input" ]]; then
    echo "$team_input"
    return 0
  fi

  if [[ -d "$manifest_root/$team_input" ]]; then
    echo "$manifest_root/$team_input"
    return 0
  fi

  echo "team manifest not found: $team_input" >&2
  return 1
}

load_team_manifest() {
  TEAM_DIR="$(resolve_team_dir "$1")"

  # shellcheck disable=SC1090
  source "$TEAM_DIR/team.env"

  TEAM_WORKSPACE_HANDOFF="$TEAM_ROOT/$TEAM_WORKSPACE_HANDOFF_REL"
  TEAM_AGENT_OPS_HANDOFF="$TEAM_ROOT/$TEAM_AGENT_OPS_HANDOFF_REL"
  TEAM_RUNTIME_ROOT="$REFERENCE_RUNTIME_ROOT/teams/$TEAM_ID"
  TEAM_RUNTIME_SUBAGENTS_DIR="$TEAM_RUNTIME_ROOT/subagents"
  TEAM_RUNTIME_QUEUE_PENDING_DIR="$TEAM_RUNTIME_ROOT/queue/pending"
  TEAM_RUNTIME_QUEUE_ARCHIVE_DIR="$TEAM_RUNTIME_ROOT/queue/archive"
  TEAM_RUNTIME_EVENTS_DIR="$TEAM_RUNTIME_ROOT/events"
  TEAM_RUNTIME_DISPATCH_ROOT="$TEAM_RUNTIME_ROOT/dispatch"
  TEAM_RUNTIME_DISPATCH_READY_DIR="$TEAM_RUNTIME_DISPATCH_ROOT/ready"
  TEAM_RUNTIME_DISPATCH_ACTIVE_DIR="$TEAM_RUNTIME_DISPATCH_ROOT/active"
  TEAM_RUNTIME_DISPATCH_ARCHIVE_DIR="$TEAM_RUNTIME_DISPATCH_ROOT/archive"
}

load_role_manifest() {
  local role_name="${1:?role name is required}"
  local role_file="$TEAM_DIR/roles/$role_name.env"

  if [[ ! -f "$role_file" ]]; then
    echo "role manifest not found: $role_file" >&2
    return 1
  fi

  # shellcheck disable=SC1090
  source "$role_file"

  ROLE_WORKDIR="$TEAM_ROOT/$ROLE_WORKDIR_REL"
  ROLE_HANDOFF="$TEAM_ROOT/$ROLE_HANDOFF_REL"
}

ensure_team_runtime_dirs() {
  mkdir -p \
    "$TEAM_RUNTIME_SUBAGENTS_DIR" \
    "$TEAM_RUNTIME_QUEUE_PENDING_DIR" \
    "$TEAM_RUNTIME_QUEUE_ARCHIVE_DIR" \
    "$TEAM_RUNTIME_EVENTS_DIR" \
    "$TEAM_RUNTIME_DISPATCH_READY_DIR" \
    "$TEAM_RUNTIME_DISPATCH_ACTIVE_DIR" \
    "$TEAM_RUNTIME_DISPATCH_ARCHIVE_DIR"
}

init_team_role_state_file() {
  local role_name="${1:?role name is required}"
  local state_file=""

  load_role_manifest "$role_name"
  state_file="$TEAM_RUNTIME_SUBAGENTS_DIR/$role_name.env"

  if [[ -f "$state_file" ]]; then
    return 0
  fi

  cat >"$state_file" <<EOF
ROLE=$role_name
MODE="manifest-default"
OWNER="$ROLE_WORKDIR_REL"
AGENT_ID="-"
MODEL="${ROLE_DEFAULT_MODEL:-$TEAM_DEFAULT_MODEL}"
STATUS="${ROLE_DEFAULT_STATUS:-not-started}"
BRANCH="${ROLE_DEFAULT_BRANCH:-"-"}"
LAST_UPDATED="$(date '+%Y-%m-%dT%H:%M:%S%z')"
CURRENT_TASK="${ROLE_DEFAULT_TASK:-"Waiting for spawn_agent from the main Codex conversation."}"
LAST_MESSAGE="${ROLE_DEFAULT_MESSAGE:-"No live spawned agent connected yet."}"
EOF
}

init_team_runtime_state() {
  local role_name

  ensure_team_runtime_dirs
  for role_name in "${TEAM_ROLE_ORDER[@]}"; do
    init_team_role_state_file "$role_name"
  done
}
