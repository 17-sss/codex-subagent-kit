# Tasks: Catalog Injection

## Phase 1: Catalog Source Model

- [x] Replace the vendored awesome catalog with app-owned built-in template files.
- [x] Load built-in categories and agents from package files instead of Python-only hardcoding.
- [x] Support explicit and auto-discovered external `categories/` roots in catalog resolution.

## Phase 2: Install / TUI Integration

- [x] Thread catalog-root selection through `catalog`, `install`, and `tui`.
- [x] Ensure project scaffold creates a project-local catalog injection path.
- [x] Keep installed `.codex/agents` precedence and compatibility behavior intact.

## Phase 3: Validation / Docs

- [x] Add tests for built-in templates, external catalog roots, and injected install flow.
- [x] Update README to explain built-in templates and external catalog injection.
