#!/bin/bash

set -euo pipefail

TEAM_INPUT="${1:?team is required}"
COMMAND_ID="${2:?command id is required}"
NEW_STATUS_VALUE="${3:?status is required}"
NEW_NOTE_VALUE="${4:-}"
NEW_AGENT_VALUE="${5:-}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS_DIR="$SCRIPT_DIR"
# shellcheck disable=SC1091
source "$SCRIPTS_DIR/load-team-manifest.sh"

load_team_manifest "$TEAM_INPUT"
init_team_runtime_state

current_file=""

if [[ -f "$TEAM_RUNTIME_QUEUE_PENDING_DIR/$COMMAND_ID.env" ]]; then
  current_file="$TEAM_RUNTIME_QUEUE_PENDING_DIR/$COMMAND_ID.env"
elif [[ -f "$TEAM_RUNTIME_QUEUE_ARCHIVE_DIR/$COMMAND_ID.env" ]]; then
  current_file="$TEAM_RUNTIME_QUEUE_ARCHIVE_DIR/$COMMAND_ID.env"
else
  echo "command file not found: $COMMAND_ID" >&2
  exit 1
fi

# shellcheck disable=SC1090
source "$current_file"

STATUS="$NEW_STATUS_VALUE"
UPDATED_AT="$(date '+%Y-%m-%dT%H:%M:%S%z')"
CLAIMED_BY="${NEW_CLAIMED_BY:-${CLAIMED_BY:-"-"}}"
CLAIMED_AT="${NEW_CLAIMED_AT:-${CLAIMED_AT:-"-"}}"

if [[ -n "$NEW_NOTE_VALUE" ]]; then
  NOTE="$NEW_NOTE_VALUE"
fi

if [[ -n "$NEW_AGENT_VALUE" ]]; then
  AGENT_ID="$NEW_AGENT_VALUE"
fi

destination_file="$TEAM_RUNTIME_QUEUE_PENDING_DIR/$COMMAND_ID.env"
if [[ "$STATUS" != "pending" && "$STATUS" != "queued" && "$STATUS" != "claimed" && "$STATUS" != "dispatched" ]]; then
  destination_file="$TEAM_RUNTIME_QUEUE_ARCHIVE_DIR/$COMMAND_ID.env"
fi

{
  printf 'ID=%q\n' "$ID"
  printf 'ROLE=%q\n' "$ROLE"
  printf 'STATUS=%q\n' "$STATUS"
  printf 'SOURCE=%q\n' "${SOURCE:-manual}"
  printf 'PRIORITY=%q\n' "${PRIORITY:-normal}"
  printf 'CREATED_AT=%q\n' "${CREATED_AT:-$UPDATED_AT}"
  printf 'UPDATED_AT=%q\n' "$UPDATED_AT"
  printf 'COMMAND=%q\n' "$COMMAND"
  printf 'NOTE=%q\n' "${NOTE:-"-"}"
  printf 'AGENT_ID=%q\n' "${AGENT_ID:-"-"}"
  printf 'CLAIMED_BY=%q\n' "$CLAIMED_BY"
  printf 'CLAIMED_AT=%q\n' "$CLAIMED_AT"
} >"$destination_file"

if [[ "$current_file" != "$destination_file" ]]; then
  rm -f "$current_file"
fi
