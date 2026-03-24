#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(CDPATH="" cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

KEEP_TMP="${KEEP_TMP:-0}"
WORK_DIR="$(mktemp -d "${TMPDIR:-/tmp}/codex-subagent-kit-consumer.XXXXXX")"
PACK_DIR="$WORK_DIR/pack"
PREFIX_DIR="$WORK_DIR/prefix"
PROJECT_DIR="$WORK_DIR/project"

cleanup() {
  if [[ "$KEEP_TMP" -eq 1 ]]; then
    printf '[smoke] keeping temp workspace: %s\n' "$WORK_DIR"
    return
  fi
  rm -rf "$WORK_DIR"
}

trap cleanup EXIT

mkdir -p "$PACK_DIR" "$PREFIX_DIR" "$PROJECT_DIR"

printf '[smoke] repo root: %s\n' "$REPO_ROOT"
printf '[smoke] temp workspace: %s\n' "$WORK_DIR"

cd "$REPO_ROOT"

printf '[smoke] building TypeScript package\n'
npm run build:ts >/dev/null

printf '[smoke] creating package tarball\n'
TARBALL_NAME="$(npm pack --workspace codex-subagent-kit --pack-destination "$PACK_DIR" | tail -n 1)"
TARBALL_PATH="$PACK_DIR/$TARBALL_NAME"

printf '[smoke] installing tarball into isolated prefix\n'
npm install --prefix "$PREFIX_DIR" "$TARBALL_PATH" >/dev/null

BIN_PATH="$PREFIX_DIR/node_modules/.bin/codex-subagent-kit"

printf '[smoke] checking CLI help\n'
"$BIN_PATH" --help >/dev/null

printf '[smoke] checking catalog output\n'
"$BIN_PATH" catalog >/dev/null

printf '[smoke] checking project install + validation\n'
"$BIN_PATH" install \
  --scope project \
  --project-root "$PROJECT_DIR" \
  --agents cto-coordinator,reviewer \
  --validate >/dev/null

printf '[smoke] checking doctor output\n'
"$BIN_PATH" doctor --scope project --project-root "$PROJECT_DIR" >/dev/null

printf '[smoke] checking usage helper\n'
"$BIN_PATH" usage \
  --scope project \
  --project-root "$PROJECT_DIR" \
  --task "Review the failing auth flow" >/dev/null

printf '[smoke] npm consumer smoke passed\n'
