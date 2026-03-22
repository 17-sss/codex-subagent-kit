# PRD: codex-orchestrator

Korean version: [PRD.ko.md](./PRD.ko.md)

## Goal

`codex-orchestrator` is a multi-agent operations tool for project-local `.codex` workspaces. It starts by making subagent installation easy, then grows into queue, dispatch, and control-panel workflows.

## Current Phase

The current implementation targets this vertical slice:

1. choose an install location
   - `Project`
   - `Global`
2. choose subagents by category
3. generate canonical `.codex/agents/*.toml`
4. generate project-scope `.codex/orchestrator` scaffold seeds

Currently implemented:

- curses-based TUI
- non-interactive install CLI
- category-based built-in subagent catalog
- project/global `.toml` discovery with precedence
- VoltAgent-style Codex-compatible TOML output
- project-scope `team.toml` with a root orchestrator
- runtime, queue, and dispatch ledger seeds
- terminal panel renderer based on `team.toml` and seeded state
- role-specific terminal board renderer
- minimal control-plane mutation for queue enqueue
- minimal control-plane mutation for opening `ready` dispatch tickets
- ready dispatch handoff package rendering and `dispatched` lifecycle transition
- minimal control-plane mutation for applying dispatch results back to queue, ledger, and runtime state
- project-local board, monitor, `tmux`, and `cmux` launcher seeds
- first-class `launch` CLI for generated launchers
- migrated shell control-plane reference assets from `__codex_agents`

## Target Direction

- `.codex/agents`
  - Codex-native subagent definitions
- `.codex/orchestrator`
  - team manifest
  - runtime state
  - queue and dispatch ledger
  - bootstrap and recovery
  - `tmux` / `cmux` control panel

## Product Principles

- Codex-native first
- local over global
- explicit delegation
- clear separation between static definitions and runtime state
- dashboard is optional
- no company-specific or product-specific default examples

## Post-MVP

- role-specific project owner agent generation
- actual `send_input` / `wait_agent` integration
- live session binding or broker layer
- integrated queue / dispatch / recovery
- seeded panel evolved into a live runtime control panel
- gradual migration from reference shell assets into a Python-native control-plane
