# Research: Launch CLI

## Decision 1: Wrap generated launcher scripts instead of re-implementing backend logic

- **Decision**: the new CLI will resolve and execute the generated `launch-tmux.sh` or `launch-cmux.sh` file directly.
- **Rationale**: backend-specific behavior already lives in generated scripts, including soft-fail for missing `tmux` / `cmux`. Re-implementing that logic in Python would create drift.
- **Alternatives considered**:
  - Rebuild `tmux` / `cmux` commands directly in Python: rejected because it duplicates launcher logic and weakens the "seed becomes runtime entrypoint" goal.
  - Tell users to run scripts manually: rejected because it keeps the product feeling like a scaffold, not a CLI.

## Decision 2: Support dry-run as the primary automated validation path

- **Decision**: `launch` will support `--dry-run` and tests will assert the resolved command without opening terminal backends.
- **Rationale**: automated tests should stay deterministic and not depend on installed terminal multiplexers.
- **Alternatives considered**:
  - Run real `tmux` / `cmux` in CI: rejected because backend availability is optional and environment-dependent.

## Decision 3: Treat `--no-attach` as tmux-only

- **Decision**: `--no-attach` will be accepted for `tmux` and rejected for `cmux`.
- **Rationale**: current generated `tmux` launcher already has an attach mode argument, while `cmux` launcher does not. Pretending the option is generic would hide backend differences.
- **Alternatives considered**:
  - Ignore `--no-attach` for `cmux`: rejected because silent no-op behavior is harder to reason about.
