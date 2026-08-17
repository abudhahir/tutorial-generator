# Textual TUI Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a Textual-based pre-configuration TUI that runs the shared LangGraph workflow and shows track-aware node status and live output.

**Architecture:** Keep the TUI separate from the existing Rich CLI. The orchestrator publishes small, serializable workflow events to an optional sink; the Textual app consumes those events on the UI thread and updates a fixed five-node graph, node details, and output log. The configuration form is editable only before starting a run.

**Tech Stack:** Python 3.10+, Textual, LangGraph, existing `BlogGenerator`, pytest.

### Task 1: Add the workflow event contract

**Files:**
- Create: `src/tui/events.py`
- Test: `tests/test_tui_events.py`

Write tests first for event construction, node status values, and serialization-safe payloads. Implement immutable event dataclasses and a small `EventSink` protocol/callback type. Events must include run id, runtime track, node name, event kind, timestamp, and optional text/error/details.

### Task 2: Emit events from the shared orchestrator

**Files:**
- Modify: `src/agents/agent_orchestrator.py`
- Modify: `src/agents/base_agent.py`
- Test: `tests/test_orchestrator_events.py`

Add an optional event sink to the orchestrator. Emit run start/completion/failure and node start/completion/failure events without changing behavior when no sink is provided. Route streaming callback text to the sink as node output while preserving existing verbose Rich output. Tests should use a fake sink and stub agent methods; no real API calls.

### Task 3: Build the Textual application shell

**Files:**
- Create: `src/tui/app.py`
- Create: `src/tui/widgets.py`
- Create: `src/tui/__init__.py`
- Test: `tests/test_tui_app.py`

Create a two-column layout. The left side contains runtime, backend, topic, goals, audience, tone, length, and output controls. The right side contains a static graph/status widget, selected-node details, and a scrollable live output log. Pressing Run validates required input, disables the form, starts a Textual worker, and routes events back through messages. Add a completion state and visible error state.

### Task 4: Connect the TUI to blog generation

**Files:**
- Modify: `src/core/blog_generator.py`
- Modify: `src/cli.py`
- Test: `tests/test_tui_integration.py`

Expose the existing generation request through the TUI without duplicating workflow logic. Add a `tui` command/entry path and pass the selected `AgentRuntime` and backend settings through to `BlogGenerator`. Keep the current interactive CLI and non-interactive commands working unchanged.

### Task 5: Dependency, documentation, and verification

**Files:**
- Modify: `pyproject.toml`
- Modify: `requirements.txt`
- Modify: `README.md`

Add Textual to dependencies, document the TUI command and keyboard flow, run focused TUI tests, run the full suite, and run `git diff --check`. Existing unrelated baseline failures must be reported separately.

