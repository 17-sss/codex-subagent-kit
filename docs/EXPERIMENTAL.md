# EXPERIMENTAL

Korean version: [EXPERIMENTAL.ko.md](./EXPERIMENTAL.ko.md)

This document tracks the commands and ideas that exist in the repository as experimental companion features rather than as the stable product core.

## Why This Exists

The stable identity of `codex-subagent-kit` is:

- catalog management
- TOML installation
- template scaffolding
- install-first TUI flow
- validation through `doctor`

Some adjacent features were explored while shaping the product. They may still be useful later, but they are not the default promise of the tool today.

## Current Experimental Commands

- `panel`
- `board`
- `launch`
- `enqueue`
- `dispatch-open`
- `dispatch-prepare`
- `dispatch-begin`
- `apply-result`

## How To Think About Them

These features are best understood as a `Codex session companion` or prototype layer:

- they can help inspect or simulate a possible workflow around Codex usage
- they do not replace Codex as the runtime owner of agent threads
- they are allowed to evolve more aggressively than the stable core

## What Is Not Promised Yet

- a standalone orchestration runtime outside Codex
- live `spawn_agent` / `send_input` / `wait_agent` integration
- production-grade queue draining and dispatch automation
- live pane and session synchronization

## If We Revisit This Later

The most natural future sequence is:

1. clarify the user story for a session companion
2. decide whether the feature should remain optional or become first-class
3. reconnect it to current Codex-native capabilities only where the runtime model still fits
