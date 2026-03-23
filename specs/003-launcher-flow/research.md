# Research: Launcher Flow

## Decision 1: Use read-only boards, not interactive panes

- **Decision**: terminal launcher panes will render read-only board/monitor views driven by shared state files.
- **Rationale**: legacy dashboard docs make it clear that `tmux` / `cmux` are status boards, while real `spawn_agent` and `send_input` stay in the main Codex thread.
- **Alternatives considered**:
  - interactive per-pane Codex sessions: visually tempting, but breaks the control-plane model.

## Decision 2: Generate project-local scripts instead of copying legacy shell assets

- **Decision**: launcher scripts will be rendered from Python templates using current project metadata.
- **Rationale**: the new product uses `.toml` team metadata, not the old `.env` manifest scheme.
- **Alternatives considered**:
  - direct shell script reuse: faster initially, but keeps old assumptions alive.

## Decision 3: Treat backend launchers as optional

- **Decision**: generated `tmux` / `cmux` launchers should soft-fail when those tools are unavailable.
- **Rationale**: dashboard backend availability should not block core project-local orchestration flows.
- **Alternatives considered**:
  - hard dependency on a single backend: simpler, but not aligned with local-first optional tooling.
