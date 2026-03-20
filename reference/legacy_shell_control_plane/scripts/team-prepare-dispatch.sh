#!/bin/bash

set -euo pipefail

TEAM_INPUT="${1:?team is required}"
ROLE_FILTER="${2:-all}"
CLAIMER_NAME="${3:-}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS_DIR="$SCRIPT_DIR"
# shellcheck disable=SC1091
source "$SCRIPTS_DIR/load-team-manifest.sh"

load_team_manifest "$TEAM_INPUT"
init_team_runtime_state

if [[ -z "$CLAIMER_NAME" ]]; then
  CLAIMER_NAME="$TEAM_COORDINATOR_ROLE"
fi

dispatch_id="$("$SCRIPTS_DIR/team-open-dispatch.sh" "$TEAM_INPUT" "$ROLE_FILTER" "$CLAIMER_NAME")"
dispatch_file="$TEAM_RUNTIME_DISPATCH_READY_DIR/$dispatch_id.env"

if [[ ! -f "$dispatch_file" ]]; then
  echo "ready dispatch not found after open: $dispatch_id" >&2
  exit 1
fi

# shellcheck disable=SC1090
source "$dispatch_file"

echo "[dispatch]"
echo "$dispatch_id"
echo
"$SCRIPTS_DIR/team-render-dispatch-brief.sh" "$TEAM_INPUT" "$COMMAND_ID"
echo
echo "[send_input message]"
"$SCRIPTS_DIR/team-render-dispatch-message.sh" "$TEAM_INPUT" "$dispatch_id"
