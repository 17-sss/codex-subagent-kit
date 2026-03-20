#!/bin/bash

set -euo pipefail

TEAM_INPUT="${1:?team is required}"
ROLE_FILTER="${2:-all}"
OUTPUT_FORMAT="${3:-summary}"
INCLUDE_CLAIMED="${INCLUDE_CLAIMED:-0}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS_DIR="$SCRIPT_DIR"
# shellcheck disable=SC1091
source "$SCRIPTS_DIR/load-team-manifest.sh"

load_team_manifest "$TEAM_INPUT"
init_team_runtime_state

priority_rank() {
  case "${1:-normal}" in
    critical) echo "0" ;;
    high) echo "1" ;;
    normal) echo "2" ;;
    low) echo "3" ;;
    *) echo "4" ;;
  esac
}

emit_candidate() {
  local file_path="$1"

  (
    # shellcheck disable=SC1090
    source "$file_path"

    if [[ "$ROLE_FILTER" != "all" && "$ROLE" != "$ROLE_FILTER" ]]; then
      exit 0
    fi

    if [[ "${STATUS:-pending}" == "claimed" && "$INCLUDE_CLAIMED" != "1" ]]; then
      exit 0
    fi

    if [[ "${STATUS:-pending}" != "pending" && "${STATUS:-pending}" != "queued" && "${STATUS:-pending}" != "claimed" ]]; then
      exit 0
    fi

    printf '%s|%s|%s\n' \
      "$(priority_rank "${PRIORITY:-normal}")" \
      "${CREATED_AT:-$ID}" \
      "$file_path"
  )
}

best_candidate="$(
  shopt -s nullglob
  for file_path in "$TEAM_RUNTIME_QUEUE_PENDING_DIR"/*.env; do
    emit_candidate "$file_path"
  done | sort -t'|' -k1,1n -k2,2 | head -n 1
)"

if [[ -z "$best_candidate" ]]; then
  echo "no pending command matched the filter" >&2
  exit 1
fi

command_file="${best_candidate##*|}"

case "$OUTPUT_FORMAT" in
  id)
    (
      # shellcheck disable=SC1090
      source "$command_file"
      echo "$ID"
    )
    ;;
  path)
    echo "$command_file"
    ;;
  env)
    cat "$command_file"
    ;;
  summary)
    (
      # shellcheck disable=SC1090
      source "$command_file"
      printf '%s | role=%s | status=%s | priority=%s | claimed_by=%s | %s\n' \
        "$ID" \
        "$ROLE" \
        "${STATUS:-pending}" \
        "${PRIORITY:-normal}" \
        "${CLAIMED_BY:-"-"}" \
        "$COMMAND"
    )
    ;;
  *)
    echo "unsupported output format: $OUTPUT_FORMAT" >&2
    exit 1
    ;;
esac
