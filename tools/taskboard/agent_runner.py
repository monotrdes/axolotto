#!/usr/bin/env python3
from __future__ import annotations
"""Agent runner module for Axolotto Kanban Taskboard.

Handles git worktree isolation, agent prompt building, keyword-based
auto-assignment, and agent dispatch via executor.py.
"""

import os
import re
import subprocess
import sys
from datetime import datetime, timezone

# Local imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from db import read_tasks, write_tasks, REPO_ROOT

# Paths
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
AGENT_LOG_DIR = os.path.join(CURRENT_DIR, "agent_logs")
os.makedirs(AGENT_LOG_DIR, exist_ok=True)

# Resource limits
def _env_int(name: str, default: int) -> int:
    try:
        v = (os.environ.get(name, "") or "").strip()
        return max(1, int(v)) if v else default
    except (ValueError, TypeError):
        return default

MAX_CONCURRENT_AGENTS = _env_int("TASKBOARD_MAX_AGENTS", 1)
AGENT_TIMEOUT_SECONDS = _env_int("TASKBOARD_AGENT_TIMEOUT", 1800)
AGENT_NICE = _env_int("TASKBOARD_AGENT_NICE", 10)
WORKTREE_DIR = os.path.join(os.path.dirname(REPO_ROOT), ".axolotto_worktrees")


def now_iso():
    return datetime.now(timezone.utc).isoformat()


# ── Git helpers ────────────────────────────────────────────────────────────────

def _git(cmd, cwd=REPO_ROOT, timeout=60):
    """Run a git command in cwd. Returns (ok, stdout, stderr)."""
    try:
        is_shell = isinstance(cmd, str)
        r = subprocess.run(cmd, shell=is_shell, cwd=cwd,
                           capture_output=True, text=True, timeout=timeout)
        return (r.returncode == 0), (r.stdout or "").strip(), (r.stderr or "").strip()
    except subprocess.TimeoutExpired:
        return False, "", f"TIMEOUT tras {timeout}s"
    except Exception as e:
        return False, "", str(e)


def safe_git_run(cmd):
    """Legacy git helper: 5s timeout, used by routes for diff generation."""
    try:
        is_shell = isinstance(cmd, str)
        result = subprocess.run(
            cmd, shell=is_shell, cwd=REPO_ROOT,
            capture_output=True, text=True, timeout=5
        )
        return (result.returncode == 0), (result.stdout or "").strip(), (result.stderr or "").strip()
    except subprocess.TimeoutExpired:
        return False, "", "TIMEOUT: El comando Git excedió el límite de 5 segundos."
    except Exception as e:
        return False, "", str(e)


def get_current_git_branch():
    ok, stdout, _ = safe_git_run("git rev-parse --abbrev-ref HEAD")
    if ok and stdout and stdout != "HEAD":
        return stdout
    # Fallback to checking existing branches in the repo
    for branch in ("develop", "dev", "master", "main"):
        ok_chk, _, _ = safe_git_run(f"git rev-parse --verify --quiet {branch}")
        if ok_chk:
            return branch
    return "develop"



# ── Git worktree isolation ─────────────────────────────────────────────────────

def _worktree_path(task_id: str) -> str:
    return os.path.join(WORKTREE_DIR, task_id)


def _is_valid_worktree(path: str) -> bool:
    return os.path.isdir(path) and _git(["git", "rev-parse", "--is-inside-work-tree"], cwd=path)[0]


def _ensure_worktree(task_id: str, branch: str, base: str):
    """Create or reuse an isolated worktree for a task."""
    os.makedirs(WORKTREE_DIR, exist_ok=True)
    path = _worktree_path(task_id)
    if _is_valid_worktree(path):
        return True, path, "worktree reutilizado"
    if os.path.exists(path):
        _git(["git", "worktree", "remove", "--force", path])
        _git(["git", "worktree", "prune"])
    branch_exists = _git(["git", "rev-parse", "--verify", "--quiet", f"refs/heads/{branch}"])[0]
    if branch_exists:
        ok, out, err = _git(["git", "worktree", "add", path, branch])
    else:
        ok, out, err = _git(["git", "worktree", "add", "-b", branch, path, base])
    return ok, path, (err or out or "ok")


def _remove_worktree(task_id: str) -> tuple[bool, str]:
    """Remove a task's worktree (keeps the branch).

    Returns (ok, message).
    """
    path = _worktree_path(task_id)
    if not os.path.exists(path):
        return True, "worktree already gone"

    # First try: normal force-remove
    ok, out, err = _git(["git", "worktree", "remove", "--force", path])
    if ok:
        _git(["git", "worktree", "prune"])
        return True, "worktree removed"

    # Second try: check if it's still registered and try harder
    still_registered = _is_valid_worktree(path)
    if not still_registered:
        # Worktree is not valid but dir exists — manually delete it
        try:
            import shutil as _shutil
            _shutil.rmtree(path, ignore_errors=True)
            _git(["git", "worktree", "prune"])
            return True, "worktree dir deleted (was not a valid worktree)"
        except Exception as e:
            return False, f"failed to delete worktree dir: {e}"

    # Third try: the worktree is valid but locked — try unlocking
    lock_file = os.path.join(path, ".git", "worktree.lock")
    if os.path.exists(lock_file):
        try:
            os.remove(lock_file)
            ok2, _, err2 = _git(["git", "worktree", "remove", "--force", path])
            if ok2:
                _git(["git", "worktree", "prune"])
                return True, "worktree removed after unlocking"
        except Exception:
            pass

    return False, f"failed to remove worktree: {err or out or 'unknown error'}"


def _work_dir_for(task_id: str) -> str:
    """Worktree path if it exists, else the main repo root (fallback)."""
    path = _worktree_path(task_id)
    return path if _is_valid_worktree(path) else REPO_ROOT


def _read_log_tail(log_path: str, lines: int = 30) -> str:
    """Read last N lines from a log file."""
    try:
        if not log_path or not os.path.exists(log_path):
            return ""
        with open(log_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        all_lines = content.splitlines()
        return "\n".join(all_lines[-lines:])
    except Exception:
        return ""


def get_agent_status(task_id: str) -> dict | None:
    """Return basic agent status — execution is manual now, no subprocess tracking."""
    return None


def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s-]+', '-', text)
    return text.strip('-')


# ── Keyword-based agent assignment ───────────────────────────────────────────

_KEYWORD_AGENT: dict[str, list[str]] = {
    "claude": [
        "frontend", "ui", "diseño", "css", "hook", "modal",
        "component", "contrato", "solidity", "security", "auth", "wallet",
        "blockchain",
    ],
    "deepclaude": [
        "backend", "api", "sql", "db", "query", "refactor",
        "test", "bug", "endpoint", "migration", "docker", "fastapi",
        "finance", "finanzas", "infra", "infraestructura",
    ],
    "agy": [
        "docs", "research", "investigar", "analizar", "game",
        "mecánica", "balance", "economía", "plan", "diseño de juego",
        "gamedesign",
    ],
}

_CATEGORY_AGENT: dict[str, str] = {
    "frontend": "claude", "design": "claude", "security": "claude",
    "contracts": "claude", "blockchain": "claude",
    "backend": "deepclaude", "bug": "deepclaude", "refactor": "deepclaude",
    "devops": "deepclaude", "sql": "deepclaude", "tests": "deepclaude",
    "finance": "deepclaude", "infra": "deepclaude",
    "docs": "agy", "research": "agy", "game": "agy", "gamedesign": "agy",
}


def _keyword_assign(title: str, desc: str, category: str) -> tuple[str, str]:
    """Return (agent_name, confidence: 'keyword'|'category'|'default')."""
    combined = f"{title} {desc}".lower()
    scores: dict[str, int] = {"claude": 0, "deepclaude": 0, "agy": 0}
    for agent, kws in _KEYWORD_AGENT.items():
        for kw in kws:
            if kw in combined:
                scores[agent] += 1
    best = max(scores, key=lambda a: scores[a])
    if scores[best] > 0:
        return best, "keyword"
    cat = (category or "").lower()
    if cat in _CATEGORY_AGENT:
        return _CATEGORY_AGENT[cat], "category"
    return "claude", "default"


def specialization_assign(task: dict) -> tuple:
    """
    Assign the best specialization to a task using weighted scoring.
    Returns (agent_name, specialization_key, provider, model, confidence_score).
    Falls back to keyword-based assignment if workspace.json is unavailable.
    """
    try:
        from ai_router import AIRouter
        AIRouter.initialize()
        registry = AIRouter._registry
    except Exception:
        registry = {"specializations": {}, "agent_mappings": {}}

    specializations = registry.get("specializations", {})
    if not specializations:
        # No workspace.json — fall back to keyword assignment
        agent, conf = _keyword_assign(
            task.get("title", ""), task.get("description", ""), task.get("category", "")
        )
        return (agent, "", agent, "", 0.0)

    # Calculate scores for all specializations
    scored = []
    for spec_key, spec_def in specializations.items():
        # Skip orchestrator fallbacks for normal task assignment
        if "fallback" in spec_key:
            continue

        score = AIRouter.score_specialization(task, spec_key, spec_def)

        # Apply availability penalty (weight: 2)
        provider_key = spec_def.get("provider", "")
        provider = AIRouter._providers.get(provider_key)
        if provider and hasattr(provider, 'available') and not provider.available:
            score -= 2 * registry.get("routing", {}).get("weights", {}).get("availability", 2)

        scored.append((spec_key, spec_def, score))

    # Sort by score descending
    scored.sort(key=lambda x: x[2], reverse=True)

    if scored:
        best_spec_key, best_spec, best_score = scored[0]
        provider_key = best_spec.get("provider", "claude")
        model_key = best_spec.get("model_key", "")
        provider = registry.get("providers", {}).get(provider_key, {})
        model = provider.get("models", {}).get(model_key, provider.get("default_model", ""))

        # Map specialization to agent name
        agent_name = provider_key
        if provider_key == "gemini":
            agent_name = "agy"
        elif provider_key == "deepseek":
            agent_name = "deepclaude"
        elif provider_key == "ollama":
            agent_name = "ollama"

        return (agent_name, best_spec_key, provider_key, model, best_score)

    # No specializations matched — fall back to keyword assignment
    agent, conf = _keyword_assign(
        task.get("title", ""), task.get("description", ""), task.get("category", "")
    )
    return (agent, "", agent, "", 0.0)


def run_test_command(cmd):
    """Run a test command. Returns (success, output)."""
    if not cmd:
        return True, ""
    try:
        result = subprocess.run(
            cmd, shell=True, cwd=REPO_ROOT,
            capture_output=True, text=True, timeout=25
        )
        success = (result.returncode == 0)
        output = (result.stdout or "") + "\n" + (result.stderr or "")
        return success, output
    except subprocess.TimeoutExpired:
        return False, "TIMEOUT: La ejecución de pruebas excedió el límite de 25 segundos."
    except Exception as e:
        return False, f"ERROR: No se pudo ejecutar el comando de pruebas: {e}"
