#!/bin/bash

set -euo pipefail

TEAM_INPUT="${1:?team is required}"
DISPATCH_ID="${2:?dispatch id is required}"
NEW_STATE="${3:?dispatch state is required}"
NEW_NOTE_VALUE="${4:-}"
NEW_AGENT_VALUE="${5:-}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS_DIR="$SCRIPT_DIR"
# shellcheck disable=SC1091
source "$SCRIPTS_DIR/load-team-manifest.sh"

load_team_manifest "$TEAM_INPUT"
init_team_runtime_state

current_file=""
if [[ -f "$TEAM_RUNTIME_DISPATCH_READY_DIR/$DISPATCH_ID.env" ]]; then
  current_file="$TEAM_RUNTIME_DISPATCH_READY_DIR/$DISPATCH_ID.env"
elif [[ -f "$TEAM_RUNTIME_DISPATCH_ACTIVE_DIR/$DISPATCH_ID.env" ]]; then
  current_file="$TEAM_RUNTIME_DISPATCH_ACTIVE_DIR/$DISPATCH_ID.env"
elif [[ -f "$TEAM_RUNTIME_DISPATCH_ARCHIVE_DIR/$DISPATCH_ID.env" ]]; then
  current_file="$TEAM_RUNTIME_DISPATCH_ARCHIVE_DIR/$DISPATCH_ID.env"
else
  echo "dispatch file not found: $DISPATCH_ID" >&2
  exit 1
fi

# shellcheck disable=SC1090
source "$current_file"

STATE="$NEW_STATE"
UPDATED_AT="$(date '+%Y-%m-%dT%H:%M:%S%z')"

if [[ -n "$NEW_NOTE_VALUE" ]]; then
  NOTE="$NEW_NOTE_VALUE"
fi

if [[ -n "$NEW_AGENT_VALUE" ]]; then
  TARGET_AGENT_ID="$NEW_AGENT_VALUE"
fi

destination_file="$TEAM_RUNTIME_DISPATCH_READY_DIR/$DISPATCH_ID.env"
if [[ "$STATE" == "dispatched" ]]; then
  destination_file="$TEAM_RUNTIME_DISPATCH_ACTIVE_DIR/$DISPATCH_ID.env"
elif [[ "$STATE" != "ready" ]]; then
  destination_file="$TEAM_RUNTIME_DISPATCH_ARCHIVE_DIR/$DISPATCH_ID.env"
fi

{
  printf 'DISPATCH_ID=%q\n' "$DISPATCH_ID"
  printf 'COMMAND_ID=%q\n' "$COMMAND_ID"
  printf 'ROLE=%q\n' "$ROLE"
  printf 'STATE=%q\n' "$STATE"
  printf 'CREATED_AT=%q\n' "${CREATED_AT:-$UPDATED_AT}"
  printf 'UPDATED_AT=%q\n' "$UPDATED_AT"
  printf 'CLAIMER=%q\n' "${CLAIMER:-$TEAM_COORDINATOR_ROLE}"
  printf 'TARGET_AGENT_ID=%q\n' "${TARGET_AGENT_ID:-"-"}"
  printf 'TARGET_MODE=%q\n' "${TARGET_MODE:-manifest-default}"
  printf 'TARGET_MODEL=%q\n' "${TARGET_MODEL:-$TEAM_DEFAULT_MODEL}"
  printf 'TARGET_BRANCH=%q\n' "${TARGET_BRANCH:-"-"}"
  printf 'SOURCE=%q\n' "${SOURCE:-manual}"
  printf 'PRIORITY=%q\n' "${PRIORITY:-normal}"
  printf 'NOTE=%q\n' "${NOTE:-"-"}"
} >"$destination_file"

if [[ "$current_file" != "$destination_file" ]]; then
  rm -f "$current_file"
fi
