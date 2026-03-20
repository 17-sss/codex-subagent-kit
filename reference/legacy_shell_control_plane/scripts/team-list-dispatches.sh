#!/bin/bash

set -euo pipefail

TEAM_INPUT="${1:?team is required}"
STATE_FILTER="${2:-all}"
ROLE_FILTER="${3:-all}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS_DIR="$SCRIPT_DIR"
# shellcheck disable=SC1091
source "$SCRIPTS_DIR/load-team-manifest.sh"

load_team_manifest "$TEAM_INPUT"
init_team_runtime_state

print_dispatch_file() {
  local file_path="$1"

  (
    # shellcheck disable=SC1090
    source "$file_path"

    if [[ "$ROLE_FILTER" != "all" && "$ROLE" != "$ROLE_FILTER" ]]; then
      exit 0
    fi

    printf '%s | role=%s | state=%s | priority=%s | agent=%s | updated=%s | command=%s\n' \
      "$DISPATCH_ID" \
      "$ROLE" \
      "$STATE" \
      "${PRIORITY:-normal}" \
      "${TARGET_AGENT_ID:-"-"}" \
      "${UPDATED_AT:-"-"}" \
      "$COMMAND_ID"
  )
}

print_section() {
  local label="$1"
  local dir_path="$2"
  local normalized="$3"
  local file_path

  if [[ "$STATE_FILTER" != "all" && "$STATE_FILTER" != "$normalized" ]]; then
    return
  fi

  echo "[$label]"
  shopt -s nullglob
  for file_path in "$dir_path"/*.env; do
    print_dispatch_file "$file_path"
  done
  echo
}

print_section "ready" "$TEAM_RUNTIME_DISPATCH_READY_DIR" "ready"
print_section "active" "$TEAM_RUNTIME_DISPATCH_ACTIVE_DIR" "active"
print_section "archive" "$TEAM_RUNTIME_DISPATCH_ARCHIVE_DIR" "archive"
