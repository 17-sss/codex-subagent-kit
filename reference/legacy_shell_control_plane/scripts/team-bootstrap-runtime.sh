#!/bin/bash

set -euo pipefail

TEAM_INPUT="${1:?team is required}"
RECOVERY_MODE="${2:-preserve}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS_DIR="$SCRIPT_DIR"
# shellcheck disable=SC1091
source "$SCRIPTS_DIR/load-team-manifest.sh"

load_team_manifest "$TEAM_INPUT"
init_team_runtime_state
"$SCRIPTS_DIR/team-recover-runtime.sh" "$TEAM_INPUT" "$RECOVERY_MODE" >/dev/null

print_role_summary() {
  local role_name="$1"
  local state_file="$TEAM_RUNTIME_SUBAGENTS_DIR/$role_name.env"

  load_role_manifest "$role_name"
  # shellcheck disable=SC1090
  source "$state_file"

  printf '%s | status=%s | branch=%s | agent_id=%s | workdir=%s\n' \
    "$role_name" \
    "${STATUS:-"-"}" \
    "${BRANCH:-"-"}" \
    "${AGENT_ID:-"-"}" \
    "$ROLE_WORKDIR"
}

echo "[team]"
echo "$TEAM_NAME"
echo
echo "[bootstrap]"
echo "runtime initialized in $RECOVERY_MODE mode"
echo
echo "[roles]"
for role_name in "${TEAM_ROLE_ORDER[@]}"; do
  print_role_summary "$role_name"
done
echo
echo "[next steps]"
echo "dashboard (cmux): $SCRIPTS_DIR/team-launch-dashboard-cmux.sh $TEAM_INPUT"
echo "dashboard (tmux): $SCRIPTS_DIR/team-launch-dashboard-tmux.sh $TEAM_INPUT"
echo "pick next command: $SCRIPTS_DIR/team-pick-command.sh $TEAM_INPUT"
echo "prepare dispatch: $SCRIPTS_DIR/team-prepare-dispatch.sh $TEAM_INPUT"
echo "recover with disconnect: $SCRIPTS_DIR/team-recover-runtime.sh $TEAM_INPUT disconnect"
echo
echo "[prompt render examples]"
for role_name in "${TEAM_ROLE_ORDER[@]}"; do
  echo "$role_name: $SCRIPTS_DIR/team-render-role-prompt.sh $TEAM_INPUT $role_name"
done
