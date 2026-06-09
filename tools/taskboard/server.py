#!/usr/bin/env python3
"""
Axolotto Kanban Taskboard Server — v5
6-column AI-powered Kanban board with real-time agent console.

Columns: wishes → concepts → planning → doing → review → done

Modular architecture:
  db.py              — Database layer (SQLite with WAL)
  agent_runner.py    — Agent prompt building, worktree isolation, dispatch
  executor.py        — Subprocess agent execution + SSE streaming
  task_lifecycle.py  — Task state machine, AI triggers
  routes.py          — HTTP routes + server entrypoint
  ai_router.py       — Multi-provider AI routing
  rate_limiter.py    — Rate limit tracking (shared utility)
"""

import sys
import os

# Ensure local imports work — modules live alongside this file
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from routes import run_server


if __name__ == '__main__':
    run_server()
