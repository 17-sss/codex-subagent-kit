#!/bin/bash

set -euo pipefail

TEAM_INPUT="${1:?team is required}"
ROLE_NAME="${2:?role is required}"
COMMAND_TEXT="${3:?command text is required}"
SOURCE_NAME="${4:-manual}"
PRIORITY_NAME="${5:-normal}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS_DIR="$SCRIPT_DIR"
# shellcheck disable=SC1091
source "$SCRIPTS_DIR/load-team-manifest.sh"

load_team_manifest "$TEAM_INPUT"
init_team_runtime_state
load_role_manifest "$ROLE_NAME" >/dev/null

timestamp="$(date '+%Y%m%dT%H%M%S%z')"
random_suffix="$(
  set +o pipefail
  LC_ALL=C tr -dc 'a-z0-9' </dev/urandom | head -c 6
)"
command_id="${timestamp}_${ROLE_NAME}_${random_suffix}"
created_at="$(date '+%Y-%m-%dT%H:%M:%S%z')"
command_file="$TEAM_RUNTIME_QUEUE_PENDING_DIR/$command_id.env"

{
  printf 'ID=%q\n' "$command_id"
  printf 'ROLE=%q\n' "$ROLE_NAME"
  printf 'STATUS=%q\n' "pending"
  printf 'SOURCE=%q\n' "$SOURCE_NAME"
  printf 'PRIORITY=%q\n' "$PRIORITY_NAME"
  printf 'CREATED_AT=%q\n' "$created_at"
  printf 'UPDATED_AT=%q\n' "$created_at"
  printf 'COMMAND=%q\n' "$COMMAND_TEXT"
  printf 'NOTE=%q\n' "-"
  printf 'AGENT_ID=%q\n' "-"
  printf 'CLAIMED_BY=%q\n' "-"
  printf 'CLAIMED_AT=%q\n' "-"
} >"$command_file"

echo "$command_id"
