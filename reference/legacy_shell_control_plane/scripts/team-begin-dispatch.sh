#!/bin/bash

set -euo pipefail

TEAM_INPUT="${1:?team is required}"
DISPATCH_ID="${2:?dispatch id is required}"
TASK_NOTE="${3:-dispatch sent to live sub-agent}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS_DIR="$SCRIPT_DIR"
# shellcheck disable=SC1091
source "$SCRIPTS_DIR/load-team-manifest.sh"

load_team_manifest "$TEAM_INPUT"
init_team_runtime_state

dispatch_file="$TEAM_RUNTIME_DISPATCH_READY_DIR/$DISPATCH_ID.env"
if [[ ! -f "$dispatch_file" ]]; then
  echo "ready dispatch not found: $DISPATCH_ID" >&2
  exit 1
fi

# shellcheck disable=SC1090
source "$dispatch_file"

command_file="$TEAM_RUNTIME_QUEUE_PENDING_DIR/$COMMAND_ID.env"
if [[ ! -f "$command_file" ]]; then
  echo "pending command not found for dispatch: $COMMAND_ID" >&2
  exit 1
fi

# shellcheck disable=SC1090
source "$command_file"

"$SCRIPTS_DIR/team-update-dispatch.sh" \
  "$TEAM_INPUT" \
  "$DISPATCH_ID" \
  "dispatched" \
  "$TASK_NOTE" \
  "${TARGET_AGENT_ID:-"-"}" >/dev/null

"$SCRIPTS_DIR/team-update-command.sh" \
  "$TEAM_INPUT" \
  "$COMMAND_ID" \
  "dispatched" \
  "dispatch=$DISPATCH_ID sent to agent ${TARGET_AGENT_ID:-"-"}" \
  "${TARGET_AGENT_ID:-"-"}" >/dev/null

NEW_STATUS="running" \
NEW_CURRENT_TASK="$COMMAND" \
NEW_LAST_MESSAGE="Dispatch $DISPATCH_ID is in flight." \
"$SCRIPTS_DIR/team-update-agent-state.sh" "$TEAM_INPUT" "$ROLE"

"$SCRIPTS_DIR/team-append-event.sh" \
  "$TEAM_INPUT" \
  "$TEAM_COORDINATOR_ROLE" \
  "dispatch-sent" \
  "dispatch=$DISPATCH_ID command=$COMMAND_ID role=$ROLE agent=${TARGET_AGENT_ID:-"-"}"

"$SCRIPTS_DIR/team-append-event.sh" \
  "$TEAM_INPUT" \
  "$ROLE" \
  "dispatch-sent" \
  "dispatch=$DISPATCH_ID command=$COMMAND_ID"

echo "$DISPATCH_ID"
