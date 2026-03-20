#!/bin/bash

set -euo pipefail

TEAM_INPUT="${1:?team is required}"
COMMAND_ID="${2:?command id is required}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS_DIR="$SCRIPT_DIR"
# shellcheck disable=SC1091
source "$SCRIPTS_DIR/load-team-manifest.sh"

load_team_manifest "$TEAM_INPUT"
init_team_runtime_state

command_file=""
if [[ -f "$TEAM_RUNTIME_QUEUE_PENDING_DIR/$COMMAND_ID.env" ]]; then
  command_file="$TEAM_RUNTIME_QUEUE_PENDING_DIR/$COMMAND_ID.env"
elif [[ -f "$TEAM_RUNTIME_QUEUE_ARCHIVE_DIR/$COMMAND_ID.env" ]]; then
  command_file="$TEAM_RUNTIME_QUEUE_ARCHIVE_DIR/$COMMAND_ID.env"
else
  echo "command file not found: $COMMAND_ID" >&2
  exit 1
fi

# shellcheck disable=SC1090
source "$command_file"

COMMAND_ROLE="$ROLE"
COMMAND_STATUS="${STATUS:-"-"}"
COMMAND_PRIORITY="${PRIORITY:-normal}"
COMMAND_SOURCE="${SOURCE:-manual}"
COMMAND_CLAIMED_BY="${CLAIMED_BY:-"-"}"
COMMAND_CLAIMED_AT="${CLAIMED_AT:-"-"}"
COMMAND_BODY="$COMMAND"

load_role_manifest "$COMMAND_ROLE"

state_file="$TEAM_RUNTIME_SUBAGENTS_DIR/$COMMAND_ROLE.env"
if [[ -f "$state_file" ]]; then
  # shellcheck disable=SC1090
  source "$state_file"
fi

echo "[dispatch brief]"
echo "team: $TEAM_NAME"
echo "command_id: $COMMAND_ID"
echo "role: $COMMAND_ROLE"
echo "status: $COMMAND_STATUS"
echo "priority: $COMMAND_PRIORITY"
echo "source: $COMMAND_SOURCE"
echo "claimed_by: $COMMAND_CLAIMED_BY"
echo "claimed_at: $COMMAND_CLAIMED_AT"
echo
echo "[target runtime]"
echo "agent_id: ${AGENT_ID:-"-"}"
echo "mode: ${MODE:-manifest-default}"
echo "model: ${MODEL:-${ROLE_DEFAULT_MODEL:-$TEAM_DEFAULT_MODEL}}"
echo "branch: ${BRANCH:-"-"}"
echo "current_task: ${CURRENT_TASK:-"-"}"
echo
echo "[repo context]"
echo "workdir: $ROLE_WORKDIR"
echo "handoff: $ROLE_HANDOFF"
echo "owner_scope: $ROLE_OWNER_SCOPE"
echo "sync_rule: $ROLE_SYNC_RULE"
echo
echo "[command]"
echo "$COMMAND_BODY"
echo
echo "[recommended send_input payload]"
echo "You own the \`$COMMAND_ROLE\` role for the \`$TEAM_NAME\` workspace."
echo "Stay within this scope: $ROLE_OWNER_SCOPE"
echo "Keep this sync rule in mind: $ROLE_SYNC_RULE"
echo "Working root: $ROLE_WORKDIR"
echo "Read handoff before changing anything if context is stale: $ROLE_HANDOFF"
echo
echo "New command:"
echo "$COMMAND_BODY"
echo
echo "Reply with:"
echo "- what you checked or changed"
echo "- blockers or contract mismatches"
echo "- files touched and verification run"
