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

COMMAND_ID="${COMMAND_ID_OVERRIDE:-}"
if [[ -z "$COMMAND_ID" ]]; then
  COMMAND_ID="$("$SCRIPTS_DIR/team-pick-command.sh" "$TEAM_INPUT" "$ROLE_FILTER" id)"
fi

command_file="$TEAM_RUNTIME_QUEUE_PENDING_DIR/$COMMAND_ID.env"
if [[ ! -f "$command_file" ]]; then
  echo "pending command not found: $COMMAND_ID" >&2
  exit 1
fi

# shellcheck disable=SC1090
source "$command_file"
load_role_manifest "$ROLE"

state_file="$TEAM_RUNTIME_SUBAGENTS_DIR/$ROLE.env"
if [[ ! -f "$state_file" ]]; then
  echo "runtime state not found for role: $ROLE" >&2
  exit 1
fi

# shellcheck disable=SC1090
source "$state_file"

TARGET_AGENT_ID="${AGENT_ID:-"-"}"
TARGET_MODE="${MODE:-manifest-default}"
TARGET_MODEL="${MODEL:-${ROLE_DEFAULT_MODEL:-$TEAM_DEFAULT_MODEL}}"
TARGET_BRANCH="${BRANCH:-"-"}"

if [[ "$TARGET_AGENT_ID" == "-" || -z "$TARGET_AGENT_ID" ]]; then
  echo "role $ROLE has no live agent_id; recover or rebind before opening a dispatch" >&2
  exit 1
fi

"$SCRIPTS_DIR/team-claim-command.sh" \
  "$TEAM_INPUT" \
  "$COMMAND_ID" \
  "$CLAIMER_NAME" \
  "claimed by $CLAIMER_NAME for dispatch open" >/dev/null

timestamp="$(date '+%Y%m%dT%H%M%S%z')"
random_suffix="$(
  set +o pipefail
  LC_ALL=C tr -dc 'a-z0-9' </dev/urandom | head -c 6
)"
dispatch_id="${timestamp}_${ROLE}_${random_suffix}"
created_at="$(date '+%Y-%m-%dT%H:%M:%S%z')"
dispatch_file="$TEAM_RUNTIME_DISPATCH_READY_DIR/$dispatch_id.env"

{
  printf 'DISPATCH_ID=%q\n' "$dispatch_id"
  printf 'COMMAND_ID=%q\n' "$COMMAND_ID"
  printf 'ROLE=%q\n' "$ROLE"
  printf 'STATE=%q\n' "ready"
  printf 'CREATED_AT=%q\n' "$created_at"
  printf 'UPDATED_AT=%q\n' "$created_at"
  printf 'CLAIMER=%q\n' "$CLAIMER_NAME"
  printf 'TARGET_AGENT_ID=%q\n' "$TARGET_AGENT_ID"
  printf 'TARGET_MODE=%q\n' "$TARGET_MODE"
  printf 'TARGET_MODEL=%q\n' "$TARGET_MODEL"
  printf 'TARGET_BRANCH=%q\n' "$TARGET_BRANCH"
  printf 'SOURCE=%q\n' "${SOURCE:-manual}"
  printf 'PRIORITY=%q\n' "${PRIORITY:-normal}"
  printf 'NOTE=%q\n' "dispatch opened"
} >"$dispatch_file"

"$SCRIPTS_DIR/team-update-command.sh" \
  "$TEAM_INPUT" \
  "$COMMAND_ID" \
  "claimed" \
  "dispatch=$dispatch_id opened by $CLAIMER_NAME" \
  "$TARGET_AGENT_ID" >/dev/null

"$SCRIPTS_DIR/team-append-event.sh" \
  "$TEAM_INPUT" \
  "$TEAM_COORDINATOR_ROLE" \
  "dispatch-opened" \
  "dispatch=$dispatch_id command=$COMMAND_ID role=$ROLE agent=$TARGET_AGENT_ID"

printf '%s\n' "$dispatch_id"
