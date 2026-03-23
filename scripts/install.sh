#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(CDPATH="" cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV_DIR="$REPO_ROOT/.venv"
LINK_DIR="${LINK_DIR:-$HOME/.local/bin}"
LINK_PATH=""
DRY_RUN=0
NO_LINK=0

usage() {
  cat <<EOF
Usage: ./scripts/install.sh [options]

Install codex-subagent-kit for development using a repo-local editable virtualenv.

Options:
  --python <bin>     Python executable to use (default: ${PYTHON_BIN})
  --venv-dir <path>  Virtualenv directory (default: ${VENV_DIR})
  --link-dir <path>  Directory for the optional codex-subagent-kit symlink (default: ${LINK_DIR})
  --no-link          Do not create a symlink in the link directory
  --dry-run          Print planned actions without changing anything
  -h, --help         Show this help
EOF
}

log() {
  printf '[install] %s\n' "$1"
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
    --python)
      shift
      [[ $# -gt 0 ]] || {
        echo "error: --python requires a value" >&2
        exit 1
      }
      PYTHON_BIN="$1"
      ;;
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
    --no-link)
      NO_LINK=1
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

LINK_PATH="$LINK_DIR/codex-subagent-kit"
VENV_BIN_DIR="$VENV_DIR/bin"
VENV_PYTHON="$VENV_BIN_DIR/python"
ENTRYPOINT_PATH="$VENV_BIN_DIR/codex-subagent-kit"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "error: python executable not found: $PYTHON_BIN" >&2
  exit 1
fi

log "repo root: $REPO_ROOT"
log "python: $PYTHON_BIN"
log "venv dir: $VENV_DIR"

if [[ ! -d "$VENV_DIR" ]]; then
  log "creating virtualenv"
  run "$PYTHON_BIN" -m venv "$VENV_DIR"
else
  log "virtualenv already exists"
fi

log "installing editable package into virtualenv"
run "$VENV_PYTHON" -m pip install -e "$REPO_ROOT"

if [[ "$NO_LINK" -eq 0 ]]; then
  log "ensuring link directory exists: $LINK_DIR"
  run mkdir -p "$LINK_DIR"
  if [[ -L "$LINK_PATH" ]]; then
    current_target="$(readlink "$LINK_PATH")"
    if [[ "$current_target" != "$ENTRYPOINT_PATH" ]]; then
      echo "warning: existing symlink at $LINK_PATH points elsewhere: $current_target" >&2
      echo "warning: leaving it unchanged; rerun with a different --link-dir or remove it manually" >&2
    else
      log "symlink already points to this repo entrypoint"
    fi
  elif [[ -e "$LINK_PATH" ]]; then
    echo "warning: existing file at $LINK_PATH is not a symlink; leaving it unchanged" >&2
  else
    log "creating symlink: $LINK_PATH -> $ENTRYPOINT_PATH"
    run ln -s "$ENTRYPOINT_PATH" "$LINK_PATH"
  fi
else
  log "skipping symlink creation"
fi

cat <<EOF

Install complete.

- Virtualenv: $VENV_DIR
- Entrypoint: $ENTRYPOINT_PATH
EOF

if [[ "$NO_LINK" -eq 0 ]]; then
  cat <<EOF
- Symlink path: $LINK_PATH
EOF
fi

if [[ ":$PATH:" == *":$LINK_DIR:"* ]]; then
  cat <<EOF

You can now run:
  codex-subagent-kit --help
EOF
else
  cat <<EOF

Your PATH does not currently include:
  $LINK_DIR

Use one of these:
  source "$VENV_BIN_DIR/activate"
  "$ENTRYPOINT_PATH" --help
EOF
fi
