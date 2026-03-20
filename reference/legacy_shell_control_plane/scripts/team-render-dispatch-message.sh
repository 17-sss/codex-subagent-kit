#!/bin/bash

set -euo pipefail

TEAM_INPUT="${1:?team is required}"
DISPATCH_ID="${2:?dispatch id is required}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS_DIR="$SCRIPT_DIR"
# shellcheck disable=SC1091
source "$SCRIPTS_DIR/load-team-manifest.sh"

load_team_manifest "$TEAM_INPUT"
init_team_runtime_state

dispatch_file=""
if [[ -f "$TEAM_RUNTIME_DISPATCH_READY_DIR/$DISPATCH_ID.env" ]]; then
  dispatch_file="$TEAM_RUNTIME_DISPATCH_READY_DIR/$DISPATCH_ID.env"
elif [[ -f "$TEAM_RUNTIME_DISPATCH_ACTIVE_DIR/$DISPATCH_ID.env" ]]; then
  dispatch_file="$TEAM_RUNTIME_DISPATCH_ACTIVE_DIR/$DISPATCH_ID.env"
elif [[ -f "$TEAM_RUNTIME_DISPATCH_ARCHIVE_DIR/$DISPATCH_ID.env" ]]; then
  dispatch_file="$TEAM_RUNTIME_DISPATCH_ARCHIVE_DIR/$DISPATCH_ID.env"
else
  echo "dispatch file not found: $DISPATCH_ID" >&2
  exit 1
fi

# shellcheck disable=SC1090
source "$dispatch_file"

command_file=""
if [[ -f "$TEAM_RUNTIME_QUEUE_PENDING_DIR/$COMMAND_ID.env" ]]; then
  command_file="$TEAM_RUNTIME_QUEUE_PENDING_DIR/$COMMAND_ID.env"
elif [[ -f "$TEAM_RUNTIME_QUEUE_ARCHIVE_DIR/$COMMAND_ID.env" ]]; then
  command_file="$TEAM_RUNTIME_QUEUE_ARCHIVE_DIR/$COMMAND_ID.env"
else
  echo "command file not found for dispatch: $COMMAND_ID" >&2
  exit 1
fi

# shellcheck disable=SC1090
source "$command_file"
load_role_manifest "$ROLE"

echo "You own the \`$ROLE\` role for the \`$TEAM_NAME\` workspace."
echo "Stay within this scope: $ROLE_OWNER_SCOPE"
echo "Keep this sync rule in mind: $ROLE_SYNC_RULE"
echo "Working root: $ROLE_WORKDIR"
echo "Read handoff before changing anything if context is stale: $ROLE_HANDOFF"
echo
echo "Dispatch id: $DISPATCH_ID"
echo "Command id: $COMMAND_ID"
echo "Priority: ${PRIORITY:-normal}"
echo "Source: ${SOURCE:-manual}"
echo
echo "New command:"
echo "$COMMAND"
echo
echo "Reply with:"
echo "- what you checked or changed"
echo "- blockers or contract mismatches"
echo "- files touched and verification run"
