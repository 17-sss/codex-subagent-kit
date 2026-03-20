#!/bin/bash

set -euo pipefail

TEAM_INPUT="${1:?team is required}"
COMMAND_ID="${2:?command id is required}"
CLAIMER_NAME="${3:-}"
CLAIM_NOTE="${4:-claimed for coordinator dispatch}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS_DIR="$SCRIPT_DIR"
# shellcheck disable=SC1091
source "$SCRIPTS_DIR/load-team-manifest.sh"

load_team_manifest "$TEAM_INPUT"
init_team_runtime_state

if [[ -z "$CLAIMER_NAME" ]]; then
  CLAIMER_NAME="$TEAM_COORDINATOR_ROLE"
fi

command_file="$TEAM_RUNTIME_QUEUE_PENDING_DIR/$COMMAND_ID.env"
if [[ ! -f "$command_file" ]]; then
  echo "pending command not found: $COMMAND_ID" >&2
  exit 1
fi

# shellcheck disable=SC1090
source "$command_file"

case "${STATUS:-pending}" in
  pending|queued) ;;
  claimed)
    if [[ "${CLAIMED_BY:-"-"}" != "$CLAIMER_NAME" ]]; then
      echo "command is already claimed by ${CLAIMED_BY:-"-"}: $COMMAND_ID" >&2
      exit 1
    fi
    ;;
  *)
    echo "command is not claimable in status ${STATUS:-"-"}: $COMMAND_ID" >&2
    exit 1
    ;;
esac

NEW_CLAIMED_BY="$CLAIMER_NAME" \
NEW_CLAIMED_AT="$(date '+%Y-%m-%dT%H:%M:%S%z')" \
"$SCRIPTS_DIR/team-update-command.sh" "$TEAM_INPUT" "$COMMAND_ID" "claimed" "$CLAIM_NOTE" "${AGENT_ID:-"-"}"

"$SCRIPTS_DIR/team-append-event.sh" \
  "$TEAM_INPUT" \
  "$TEAM_COORDINATOR_ROLE" \
  "claimed" \
  "command=$COMMAND_ID role=${ROLE:-"-"} claimer=$CLAIMER_NAME"

echo "$COMMAND_ID"
