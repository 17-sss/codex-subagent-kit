#!/bin/bash

set -euo pipefail

TEAM_INPUT="${1:?team is required}"
ROLE_NAME="${2:?role is required}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS_DIR="$SCRIPT_DIR"
# shellcheck disable=SC1091
source "$SCRIPTS_DIR/load-team-manifest.sh"

load_team_manifest "$TEAM_INPUT"
init_team_runtime_state
load_role_manifest "$ROLE_NAME"

echo "You are the \`$TEAM_NAME\` workspace \`$ROLE_TITLE\` owner."
echo
echo "You are not alone in the codebase."
echo "Do not revert changes made by others."
echo "For now, respect repo ownership and surface blockers early."
echo
echo "Read these first:"
for path_rel in "${ROLE_READ_PATHS[@]}"; do
  echo "- $TEAM_ROOT/$path_rel"
done
echo
echo "Working root:"
echo "- $ROLE_WORKDIR"
echo
echo "Owner scope:"
echo "- $ROLE_OWNER_SCOPE"
echo
echo "Sync rule:"
echo "- $ROLE_SYNC_RULE"
echo
echo "Onboarding goal:"
echo "- $ROLE_ONBOARDING_GOAL"
echo
echo "Output format:"
echo "- branch and dirty files"
echo "- current owner scope"
echo "- immediate risks or blockers"
echo "- recommended next action"
