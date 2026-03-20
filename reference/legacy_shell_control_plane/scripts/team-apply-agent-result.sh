#!/bin/bash

set -euo pipefail

TEAM_INPUT="${1:?team is required}"
DISPATCH_ID="${2:?dispatch id is required}"
OUTCOME="${3:?outcome is required}"
RESULT_SUMMARY="${4:?result summary is required}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS_DIR="$SCRIPT_DIR"
# shellcheck disable=SC1091
source "$SCRIPTS_DIR/load-team-manifest.sh"

load_team_manifest "$TEAM_INPUT"
init_team_runtime_state

dispatch_file=""
if [[ -f "$TEAM_RUNTIME_DISPATCH_ACTIVE_DIR/$DISPATCH_ID.env" ]]; then
  dispatch_file="$TEAM_RUNTIME_DISPATCH_ACTIVE_DIR/$DISPATCH_ID.env"
elif [[ -f "$TEAM_RUNTIME_DISPATCH_READY_DIR/$DISPATCH_ID.env" ]]; then
  dispatch_file="$TEAM_RUNTIME_DISPATCH_READY_DIR/$DISPATCH_ID.env"
else
  echo "dispatch not found in ready/active state: $DISPATCH_ID" >&2
  exit 1
fi

# shellcheck disable=SC1090
source "$dispatch_file"

queue_status="completed"
agent_status="completed"

case "$OUTCOME" in
  completed) ;;
  failed)
    queue_status="failed"
    agent_status="blocked"
    ;;
  cancelled)
    queue_status="cancelled"
    agent_status="completed"
    ;;
  *)
    echo "unsupported outcome: $OUTCOME" >&2
    exit 1
    ;;
esac

"$SCRIPTS_DIR/team-update-dispatch.sh" \
  "$TEAM_INPUT" \
  "$DISPATCH_ID" \
  "$OUTCOME" \
  "$RESULT_SUMMARY" \
  "${TARGET_AGENT_ID:-"-"}" >/dev/null

"$SCRIPTS_DIR/team-update-command.sh" \
  "$TEAM_INPUT" \
  "$COMMAND_ID" \
  "$queue_status" \
  "$RESULT_SUMMARY" \
  "${TARGET_AGENT_ID:-"-"}" >/dev/null

NEW_STATUS="$agent_status" \
NEW_CURRENT_TASK="Await the next dispatch from $TEAM_COORDINATOR_ROLE." \
NEW_LAST_MESSAGE="$RESULT_SUMMARY" \
"$SCRIPTS_DIR/team-update-agent-state.sh" "$TEAM_INPUT" "$ROLE"

"$SCRIPTS_DIR/team-append-event.sh" \
  "$TEAM_INPUT" \
  "$TEAM_COORDINATOR_ROLE" \
  "dispatch-$OUTCOME" \
  "dispatch=$DISPATCH_ID command=$COMMAND_ID role=$ROLE summary=$RESULT_SUMMARY"

"$SCRIPTS_DIR/team-append-event.sh" \
  "$TEAM_INPUT" \
  "$ROLE" \
  "dispatch-$OUTCOME" \
  "dispatch=$DISPATCH_ID summary=$RESULT_SUMMARY"

echo "$DISPATCH_ID"
