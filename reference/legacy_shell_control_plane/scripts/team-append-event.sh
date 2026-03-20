#!/bin/bash

set -euo pipefail

TEAM_INPUT="${1:?team is required}"
ROLE_NAME="${2:?role is required}"
EVENT_TYPE="${3:?event type is required}"
MESSAGE="${4:?message is required}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS_DIR="$SCRIPT_DIR"
# shellcheck disable=SC1091
source "$SCRIPTS_DIR/load-team-manifest.sh"

load_team_manifest "$TEAM_INPUT"
init_team_runtime_state

EVENT_FILE="$TEAM_RUNTIME_EVENTS_DIR/$ROLE_NAME.log"
sanitized_message="${MESSAGE//$'\n'/ }"

printf '%s | %s | %s\n' "$(date '+%Y-%m-%dT%H:%M:%S%z')" "$EVENT_TYPE" "$sanitized_message" >>"$EVENT_FILE"
