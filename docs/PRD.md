# PRD: codex-subagent-kit

Korean version: [PRD.ko.md](./PRD.ko.md)

## Goal

`codex-subagent-kit` is a Codex-native toolkit for installing and managing subagent definitions under project-local and global `.codex` directories.

The product is intentionally centered on preparation, not replacement:

- `codex-subagent-kit` curates catalogs, scaffolds templates, and installs agent TOML files
- `codex` remains the runtime that spawns, routes, and manages agent threads

## Stable Product Core

The stable product identity is:

1. choose an install target
   - `Project`
   - `Global`
2. browse built-in or injected catalogs
   - vendored VoltAgent snapshot
   - synced source roots
   - user-authored injection roots
3. select subagents
4. generate compatible `.codex/agents/*.toml`
5. run `codex` in that workspace

Stable capabilities:

- prompt-based install-first TUI
- non-interactive install CLI
- `doctor` validation CLI
- VoltAgent-backed built-in catalog snapshot
- project/global synced source-root discovery and refresh
- project/global discovery with precedence
- external awesome-style catalog injection
- persistent import into project/global catalog injection paths
- project/global template scaffolding
- Codex-compatible TOML output using `developer_instructions`

## Product Principles

- Codex-native first
- local over global
- static definitions before runtime abstractions
- VoltAgent-backed by default without locking users to VoltAgent
- explicit, inspectable TOML templates
- no company-specific default assets

## Non-Goals For Now

- replacing Codex as the runtime owner of agent threads
- building a standalone multi-agent broker outside Codex
- forcing users to depend only on a single third-party catalog repository

## Near-Term Priorities

- strengthen install, catalog, and template workflows
- keep the vendored VoltAgent snapshot and `catalog sync` flow current
- add compatibility checks and validation around generated TOML
- improve import and extension paths for user-authored catalogs
- document how installed agents are best used from inside Codex sessions
- keep the TypeScript package aligned to the stable command scope
