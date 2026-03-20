#!/bin/bash

set -euo pipefail

TEAM_INPUT="${1:?team is required}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS_DIR="$SCRIPT_DIR"
# shellcheck disable=SC1091
source "$SCRIPTS_DIR/load-team-manifest.sh"

load_team_manifest "$TEAM_INPUT"
init_team_runtime_state

print_role_line() {
  local role_name="$1"
  local state_file="$TEAM_RUNTIME_SUBAGENTS_DIR/$role_name.env"
  local mode="manifest-default"
  local agent_id="-"
  local status="not-connected"
  local last_updated="-"
  local branch="-"

  load_role_manifest "$role_name"

  echo "[$role_name]"
  if [[ -f "$state_file" ]]; then
    # shellcheck disable=SC1090
    source "$state_file"
    mode="${MODE:-$mode}"
    agent_id="${AGENT_ID:-$agent_id}"
    status="${STATUS:-$status}"
    last_updated="${LAST_UPDATED:-$last_updated}"
    branch="${BRANCH:-$branch}"
  fi
  echo "mode: $mode"
  echo "agent_id: $agent_id"
  echo "status: $status"
  echo "branch: $branch"
  echo "last_updated: $last_updated"
  if git -C "$ROLE_WORKDIR" rev-parse --show-toplevel >/dev/null 2>&1; then
    git -C "$ROLE_WORKDIR" status --short
    git -C "$ROLE_WORKDIR" --no-pager log --oneline -1
  else
    echo "git: n/a"
  fi
  echo
}

print_queue_summary() {
  local file_path
  local role_name

  for role_name in "${TEAM_ROLE_ORDER[@]}"; do
    local count=0
    shopt -s nullglob
    for file_path in "$TEAM_RUNTIME_QUEUE_PENDING_DIR"/*.env; do
      if (
        # shellcheck disable=SC1090
        source "$file_path"
        [[ "$ROLE" == "$role_name" ]]
      ); then
        count=$((count + 1))
      fi
    done
    printf '%s=%s ' "$role_name" "$count"
  done
  echo
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

while true; do
  clear
  date
  echo
  echo "[team]"
  echo "$TEAM_NAME"
  echo
  echo "[mode]"
  echo "manifest-based sub-agent dashboard monitor"
  echo
  echo "[note]"
  echo "actual sub-agents are spawned from the main Codex conversation."
  echo "these panes expose shared state, queue, event log, repo status, and handoff context."
  echo
  echo "[queue summary]"
  print_queue_summary
  echo
  echo "[dispatch summary]"
  printf 'ready=%s active=%s archive=%s\n' \
    "$(count_dispatch_dir "$TEAM_RUNTIME_DISPATCH_READY_DIR")" \
    "$(count_dispatch_dir "$TEAM_RUNTIME_DISPATCH_ACTIVE_DIR")" \
    "$(count_dispatch_dir "$TEAM_RUNTIME_DISPATCH_ARCHIVE_DIR")"
  echo
  echo "[workspace handoff]"
  sed -n '1,30p' "$TEAM_WORKSPACE_HANDOFF"
  echo

  for role_name in "${TEAM_MONITOR_ROLES[@]}"; do
    print_role_line "$role_name"
  done

  sleep 5
done
