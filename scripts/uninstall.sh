#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(CDPATH="" cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

VENV_DIR="$REPO_ROOT/.venv"
LINK_DIR="${LINK_DIR:-$HOME/.local/bin}"
LINK_PATH=""
KEEP_VENV=0
DRY_RUN=0

usage() {
  cat <<EOF
Usage: ./scripts/uninstall.sh [options]

Remove the development install for the legacy Python codex-subagent-kit app.

Options:
  --venv-dir <path>  Virtualenv directory to uninstall from (default: ${VENV_DIR})
  --link-dir <path>  Directory containing the optional symlink (default: ${LINK_DIR})
  --keep-venv        Uninstall the package but keep the virtualenv directory
  --dry-run          Print planned actions without changing anything
  -h, --help         Show this help
EOF
}

log() {
  printf '[uninstall] %s\n' "$1"
}

run() {
  if [[ "$DRY_RUN" -eq 1 ]]; then
    printf '[dry-run] %q' "$1"
    shift
    for arg in "$@"; do
      printf ' %q' "$arg"
    done
    printf '\n'
    return 0
  fi
  "$@"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --venv-dir)
      shift
      [[ $# -gt 0 ]] || {
        echo "error: --venv-dir requires a value" >&2
        exit 1
      }
      VENV_DIR="$1"
      ;;
    --link-dir)
      shift
      [[ $# -gt 0 ]] || {
        echo "error: --link-dir requires a value" >&2
        exit 1
      }
      LINK_DIR="$1"
      ;;
    --keep-venv)
      KEEP_VENV=1
      ;;
    --dry-run)
      DRY_RUN=1
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "error: unknown option: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
  shift
done

LINK_PATH="$LINK_DIR/codex-subagent-kit-legacy"
VENV_BIN_DIR="$VENV_DIR/bin"
VENV_PYTHON="$VENV_BIN_DIR/python"
ENTRYPOINT_PATH="$VENV_BIN_DIR/codex-subagent-kit-legacy"

log "repo root: $REPO_ROOT"
log "venv dir: $VENV_DIR"

if [[ -L "$LINK_PATH" ]]; then
  current_target="$(readlink "$LINK_PATH")"
  if [[ "$current_target" == "$ENTRYPOINT_PATH" ]]; then
    log "removing symlink: $LINK_PATH"
    run rm -f "$LINK_PATH"
  else
    echo "warning: symlink at $LINK_PATH points elsewhere: $current_target" >&2
    echo "warning: leaving it unchanged" >&2
  fi
elif [[ -e "$LINK_PATH" ]]; then
  echo "warning: existing file at $LINK_PATH is not this repo symlink; leaving it unchanged" >&2
else
  log "no repo-managed symlink found at $LINK_PATH"
fi

if [[ -x "$VENV_PYTHON" ]]; then
  log "uninstalling editable package from virtualenv"
  if [[ "$DRY_RUN" -eq 1 ]]; then
    run "$VENV_PYTHON" -m pip uninstall -y codex-subagent-kit
  else
    "$VENV_PYTHON" -m pip uninstall -y codex-subagent-kit >/dev/null || true
  fi
else
  log "virtualenv python not found; skipping pip uninstall"
fi

if [[ "$KEEP_VENV" -eq 0 ]]; then
  if [[ -d "$VENV_DIR" ]]; then
    log "removing virtualenv directory"
    run rm -rf "$VENV_DIR"
  else
    log "virtualenv directory already absent"
  fi
else
  log "keeping virtualenv directory"
fi

cat <<EOF

Uninstall complete.

- Virtualenv: $VENV_DIR
- Symlink path: $LINK_PATH
EOF
