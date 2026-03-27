#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(CDPATH="" cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$REPO_ROOT"

npm run test:ts
npm run typecheck:ts
npm run build:ts
npm run pack:ts
SKIP_BUILD=1 npm run smoke:ts:consumer
