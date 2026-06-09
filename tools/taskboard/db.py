#!/usr/bin/env python3
from __future__ import annotations
"""Database layer for Axolotto Kanban Taskboard.

Thread-safe SQLite operations with WAL mode.
"""

import json
import os
import sqlite3
import sys
import threading

# Paths
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Load .env before computing REPO_ROOT so AXOLOTTO_REPO can override it
_DEFAULT_REPO = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
_DOTENV = os.path.join(_DEFAULT_REPO, ".env")
if os.path.exists(_DOTENV):
    try:
        with open(_DOTENV, "r", encoding="utf-8") as _f:
            for _line in _f:
                _line = _line.strip()
                if _line and not _line.startswith("#") and "=" in _line:
                    _key, _val = _line.split("=", 1)
                    _val = _val.strip().strip('"').strip("'")
                    if _key.strip() not in os.environ:
                        os.environ[_key.strip()] = _val
    except Exception:
        pass

REPO_ROOT = os.environ.get("AXOLOTTO_REPO") or _DEFAULT_REPO

# DB_FILE must stay on a local filesystem — SQLite locks don't work over WSL/network paths.
# Default: alongside the taskboard server (CURRENT_DIR). Override with AXOLOTTO_DB.
DB_FILE = os.environ.get("AXOLOTTO_DB") or os.path.join(CURRENT_DIR, "tasks.db")

# Thread-safe DB lock
_db_lock = threading.RLock()


def get_db():
    """Get a new SQLite connection (SQLite is thread-safe with WAL)."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    return conn


def init_db():
    """Create tables if not exist."""
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL DEFAULT '',
            description TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'concepts',
            assigned_to TEXT NOT NULL DEFAULT 'unassigned',
            priority TEXT NOT NULL DEFAULT 'medium',
            category TEXT NOT NULL DEFAULT 'tools',
            scope TEXT NOT NULL DEFAULT 'axolotto',
            test_command TEXT NOT NULL DEFAULT '',
            git_branch TEXT NOT NULL DEFAULT '',
            git_base_branch TEXT NOT NULL DEFAULT '',
            needs_agent_generation INTEGER NOT NULL DEFAULT 0,
            planning_data TEXT NOT NULL DEFAULT '{}',
            comments TEXT NOT NULL DEFAULT '[]',
            stage_history TEXT NOT NULL DEFAULT '[]',
            ai_analysis TEXT NOT NULL DEFAULT '{}',
            created_at TEXT NOT NULL DEFAULT '',
            updated_at TEXT NOT NULL DEFAULT '',
            git_in_dev INTEGER NOT NULL DEFAULT 1,
            git_commit_error TEXT NOT NULL DEFAULT ''
        )
    """)
    # Migration: add scope column if missing
    try:
        conn.execute("ALTER TABLE tasks ADD COLUMN scope TEXT NOT NULL DEFAULT 'axolotto'")
    except Exception:
        pass  # column already exists
    # Migration: add git_in_dev and git_commit_error if missing
    try:
        conn.execute("ALTER TABLE tasks ADD COLUMN git_in_dev INTEGER NOT NULL DEFAULT 1")
    except Exception:
        pass
    try:
        conn.execute("ALTER TABLE tasks ADD COLUMN git_commit_error TEXT NOT NULL DEFAULT ''")
    except Exception:
        pass
    # Migration: add wiki_sync_data if missing
    try:
        conn.execute("ALTER TABLE tasks ADD COLUMN wiki_sync_data TEXT NOT NULL DEFAULT '{}'")
    except Exception:
        pass
    conn.commit()
    conn.close()


def _row_to_task(row) -> dict:
    """Convert a DB row to a task dict."""
    t = dict(row) if not isinstance(row, dict) else row.copy()
    # Deserialize JSON fields (handle double-encoding from old migrations)
    for field in ("planning_data", "comments", "stage_history", "ai_analysis", "wiki_sync_data"):
        val = t.get(field)
        if isinstance(val, str) and val.strip():
            try:
                parsed = json.loads(val)
                # Handle double-encoding (old migration artifact)
                if isinstance(parsed, str):
                    parsed = json.loads(parsed)
                t[field] = parsed
            except (json.JSONDecodeError, TypeError):
                t[field] = {} if field in ("planning_data", "ai_analysis") else []
        elif not isinstance(val, (dict, list)):
            t[field] = {} if field in ("planning_data", "ai_analysis") else []
    t["needs_agent_generation"] = bool(t.get("needs_agent_generation", 0))
    return t


def read_tasks():
    """Read all tasks from DB. Returns {'tasks': [...]} for backward compat."""
    with _db_lock:
        conn = get_db()
        try:
            rows = conn.execute("SELECT * FROM tasks ORDER BY created_at DESC").fetchall()
            tasks = [_row_to_task(dict(r)) for r in rows]
            return {"tasks": tasks}
        except Exception as e:
            print(f"Error reading tasks: {e}", file=sys.stderr)
            return {"tasks": []}
        finally:
            conn.close()


def write_task(task: dict):
    """Insert or update a single task in DB."""
    with _db_lock:
        conn = get_db()
        try:
            t = task.copy()
            # Serialize JSON fields
            for field in ("planning_data", "comments", "stage_history", "ai_analysis", "wiki_sync_data"):
                t[field] = json.dumps(t.get(field, {} if field in ("planning_data", "ai_analysis") else []), ensure_ascii=False)
            t["needs_agent_generation"] = 1 if t.get("needs_agent_generation") else 0
            conn.execute("""
                INSERT OR REPLACE INTO tasks
                (id, title, description, status, assigned_to, priority, category,
                 scope, test_command, git_branch, git_base_branch, needs_agent_generation,
                 planning_data, comments, stage_history, ai_analysis, wiki_sync_data,
                 created_at, updated_at,
                 git_in_dev, git_commit_error)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                t.get("id", ""), t.get("title", ""), t.get("description", ""),
                t.get("status", "concepts"), t.get("assigned_to", "unassigned"),
                t.get("priority", "medium"), t.get("category", "tools"),
                t.get("scope", "axolotto"),
                t.get("test_command", ""), t.get("git_branch", ""),
                t.get("git_base_branch", ""), t.get("needs_agent_generation", 0),
                t.get("planning_data", "{}"), t.get("comments", "[]"),
                t.get("stage_history", "[]"), t.get("ai_analysis", "{}"),
                t.get("wiki_sync_data", "{}"),
                t.get("created_at", ""), t.get("updated_at", ""),
                1 if t.get("git_in_dev", True) else 0, t.get("git_commit_error", ""),
            ))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error writing task {task.get('id')}: {e}", file=sys.stderr)
            return False
        finally:
            conn.close()


def delete_task_from_db(task_id: str):
    """Delete a task from DB."""
    with _db_lock:
        conn = get_db()
        try:
            conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting task {task_id}: {e}", file=sys.stderr)
            return False
        finally:
            conn.close()


def write_tasks(data: dict):
    """Write all tasks to DB. Used by AI threads that modify the full list."""
    # Only write if 'tasks' key exists (backward compat)
    if "tasks" not in data:
        return False
    with _db_lock:
        conn = get_db()
        try:
            for task in data["tasks"]:
                t = task.copy()
                for field in ("planning_data", "comments", "stage_history", "ai_analysis", "wiki_sync_data"):
                    t[field] = json.dumps(t.get(field, {} if field in ("planning_data", "ai_analysis") else []), ensure_ascii=False)
                t["needs_agent_generation"] = 1 if t.get("needs_agent_generation") else 0
                conn.execute("""
                    INSERT OR REPLACE INTO tasks
                    (id, title, description, status, assigned_to, priority, category, scope,
                     test_command, git_branch, git_base_branch, needs_agent_generation,
                     planning_data, comments, stage_history, ai_analysis, wiki_sync_data,
                     created_at, updated_at,
                     git_in_dev, git_commit_error)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    t.get("id", ""), t.get("title", ""), t.get("description", ""),
                    t.get("status", "concepts"), t.get("assigned_to", "unassigned"),
                    t.get("priority", "medium"), t.get("category", "tools"),
                    t.get("scope", "axolotto"),
                    t.get("test_command", ""), t.get("git_branch", ""),
                    t.get("git_base_branch", ""), t.get("needs_agent_generation", 0),
                    t.get("planning_data", "{}"), t.get("comments", "[]"),
                    t.get("stage_history", "[]"), t.get("ai_analysis", "{}"),
                    t.get("wiki_sync_data", "{}"),
                    t.get("created_at", ""), t.get("updated_at", ""),
                    1 if t.get("git_in_dev", True) else 0, t.get("git_commit_error", ""),
                ))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error bulk writing tasks: {e}", file=sys.stderr)
            return False
        finally:
            conn.close()
