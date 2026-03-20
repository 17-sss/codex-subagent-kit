#!/bin/bash

set -euo pipefail

TEAM_INPUT="${1:?team is required}"
ROLE_FILTER="${2:-all}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS_DIR="$SCRIPT_DIR"
# shellcheck disable=SC1091
source "$SCRIPTS_DIR/load-team-manifest.sh"

load_team_manifest "$TEAM_INPUT"
init_team_runtime_state

shopt -s nullglob

print_command_file() {
  local file_path="$1"

  (
    # shellcheck disable=SC1090
    source "$file_path"

    if [[ "$ROLE_FILTER" != "all" && "$ROLE" != "$ROLE_FILTER" ]]; then
      exit 0
    fi

    printf '%s | role=%s | status=%s | source=%s | priority=%s | agent=%s | claimed_by=%s | updated=%s | %s\n' \
      "$ID" \
      "$ROLE" \
      "$STATUS" \
      "${SOURCE:-manual}" \
      "${PRIORITY:-normal}" \
      "${AGENT_ID:-"-"}" \
      "${CLAIMED_BY:-"-"}" \
      "${UPDATED_AT:-"-"}" \
      "$COMMAND"
  )
}

echo "[pending]"
for file_path in "$TEAM_RUNTIME_QUEUE_PENDING_DIR"/*.env; do
  print_command_file "$file_path"
done

echo
echo "[archive]"
for file_path in "$TEAM_RUNTIME_QUEUE_ARCHIVE_DIR"/*.env; do
  print_command_file "$file_path"
done
