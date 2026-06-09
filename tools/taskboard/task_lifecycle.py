#!/usr/bin/env python3
from __future__ import annotations
"""Task lifecycle module for Axolotto Kanban Taskboard.

Handles AI processing triggers, stage transitions, dependency validation,
and task state machine logic.
"""

import json
import os
import shlex
import sys
import threading
import time
from datetime import datetime, timezone

# Local imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from db import read_tasks, write_tasks, write_task
from agent_runner import (
    AGENT_LOG_DIR, now_iso, _read_log_tail, run_test_command,
    get_current_git_branch, safe_git_run, slugify,
    _ensure_worktree, _remove_worktree, _work_dir_for, _git, _worktree_path,
)
from agy_client import is_plan_a


def detect_category_from_text(title: str, desc: str) -> str | None:
    combined = f"{title} {desc}".lower()
    
    keywords = {
        "security": ["security", "seguridad", "auth", "login", "vulnerability", "password", "jwt", "permission", "permiso", "hack", "cifrado", "encrypt"],
        "finance": ["finance", "finanzas", "pay", "payment", "compra", "venta", "economía", "coin", "tokens", "price", "precio", "shop", "tienda", "jackpot", "vault", "bank", "banco", "comisión", "fee"],
        "gamedesign": ["game design", "diseño de juego", "balance", "gameplay", "mecánica", "jugabilidad", "gashapon", "rate", "probabilidad", "player", "enemigo", "enemy", "level", "nivel"],
        "blockchain": ["solidity", "smart contract", "contrato", "web3", "metamask", "wallet", "abi", "blockchain", "chain", "transaction", "transacción"],
        "infra": ["docker", "deploy", "despliegue", "kubernetes", "ci/cd", "github actions", "nginx", "dns", "aws", "cloud", "infraestructura", "infra", "port", "puerto"],
        "frontend": ["frontend", "ui", "ux", "css", "html", "react", "nextjs", "next.js", "tailwind", "design", "diseño", "botón", "button", "modal", "view", "vista", "pantalla", "canvas", "render", "client", "cliente"],
        "backend": ["backend", "api", "fastapi", "python", "endpoint", "database", "db", "sqlite", "postgresql", "model", "query", "sql", "migration", "router", "route", "server", "logic", "lógica"],
        "bug": ["bug", "error", "fail", "fix", "issue", "crash", "fallo", "defect", "corregir"],
        "docs": ["docs", "documentation", "documentación", "readme", "guide", "guía", "tutorial", "comentario", "comment", "explicar"],
    }
    
    scores = {cat: 0 for cat in keywords}
    for cat, kws in keywords.items():
        for kw in kws:
            if kw in combined:
                scores[cat] += 1
                
    best_cat = max(scores, key=lambda c: scores[c])
    if scores[best_cat] > 0:
        return best_cat
    return None


def assign_category_if_missing(task: dict):
    category = task.get("category", "").strip().lower()
    valid_categories = {
        "backend", "frontend", "tools", "bug", "docs",
        "security", "finance", "gamedesign", "blockchain", "infra"
    }
    
    if not category or category not in valid_categories or category == "tools":
        title = task.get("title", "")
        desc = task.get("description", "")
        detected = detect_category_from_text(title, desc)
        if detected:
            task["category"] = detected
        else:
            if not category or category not in valid_categories:
                scope = task.get("scope", "axolotto")
                task["category"] = "tools" if scope == "taskboard" else "backend"




def validate_dependencies(task: dict, new_status: str, all_tasks: list) -> tuple[bool, str]:
    """Check if task can move to new_status given its dependencies.
    Returns (allowed, message).
    """
    if new_status not in ("doing", "review", "done"):
        return True, ""

    planning_data = task.get("planning_data", {})
    dependencies = planning_data.get("dependencies", []) if isinstance(planning_data, dict) else []
    if not dependencies:
        return True, ""

    incomplete_deps = []
    missing_deps = []
    for dep_id in dependencies:
        dep_task = next((t for t in all_tasks if t["id"] == dep_id), None)
        if dep_task is None:
            missing_deps.append(dep_id)
        elif dep_task.get("status") != "done":
            incomplete_deps.append(dep_task.get("title", dep_id))

    if missing_deps:
        return False, f"Esta tarea depende de las siguientes tareas que ya no existen: {', '.join(missing_deps)}"
    if incomplete_deps:
        return False, f"Esta tarea depende de las siguientes tareas no completadas: {', '.join(incomplete_deps)}"

    return True, ""


def handle_move_stage_transition(task: dict, old_status: str, new_status: str,
                                  force: bool, skip_ai: bool, force_merge: bool,
                                  all_tasks: list) -> dict:
    """Handle all side effects of moving a task between stages.

    Returns a dict with:
      - git_notice: str
      - ai_triggered: bool
      - blocked: None or (status_code, response_dict) — if set, caller should return immediately
    """
    git_notice = ""
    wiki_alerts = None
    task_id = task["id"]

    if new_status in ("planning", "doing"):
        assign_category_if_missing(task)

    # Record stage transition
    task.setdefault("stage_history", []).append({
        "stage": new_status,
        "entered_at": now_iso(),
        "ai_triggered": False,
    })

    # ── Plan A gate: require approved plan before moving planning → doing ──
    if is_plan_a() and new_status == "doing" and old_status == "planning":
        if not task.get("planning_data", {}).get("approved"):
            return {
                "git_notice": "",
                "ai_triggered": False,
                "blocked": (400, {
                    "success": False,
                    "reason": "plan_not_approved",
                    "message": "El plan debe ser aprobado antes de mover a Doing. Revisa y aprueba el plan en Planning."
                })
            }

    # ── Git side effects ──────────────────────────────────────────────

    if new_status == "doing" and old_status != "doing":
        if not task.get("git_branch"):
            base = get_current_git_branch()
            task["git_base_branch"] = base
            slug = slugify(task["title"])
            branch_name = f"task/{task_id}-{slug}"
            task["git_branch"] = branch_name
        else:
            branch_name = task["git_branch"]
            base = task.get("git_base_branch") or get_current_git_branch()

        if is_plan_a():
            print(f"  Git: worktree for '{branch_name}' (base '{base}')")
            ok, wt, msg = _ensure_worktree(task_id, branch_name, base)
            if ok:
                git_notice = (f"Worktree aislado creado para '{branch_name}'. "
                              "El árbol principal no se toca.")
            else:
                git_notice = f"Advertencia: no se pudo crear el worktree ({msg})."
                print(f"  Git: worktree FAILED for {task_id}: {msg}", file=sys.stderr)

            # Set execution block so the user can easily copy the command!
            agent = task.get("assigned_to", "claude")
            if agent == "unassigned":
                agent = "claude"
                task["assigned_to"] = agent  # persist auto-assignment
            wt_path = _worktree_path(task_id)

            # Format command to work perfectly on Windows (PowerShell compatible)
            execution_cmd = f'cd "{wt_path}" ; {agent}'

            task.setdefault("ai_analysis", {})["execution"] = {
                "agent": agent,
                "command": execution_cmd,
                "awaiting": True,
                "started_at": now_iso()
            }

            # Agent execution is now manual — the user runs Claude/DeepClaude/AGY
            # directly in their terminal. The taskboard is a visual tracker.
            git_notice += (
                " Worktree listo. Ejecuta el agente manualmente en tu terminal."
            )
        # In Plan B, AI works in main repo from chat — no worktree needed

    elif new_status == "review" and not force:
        test_cmd = task.get("test_command", "")
        if test_cmd:
            test_success, test_output = run_test_command(test_cmd)
            if not test_success:
                return {
                    "git_notice": git_notice,
                    "ai_triggered": False,
                    "blocked": (400, {
                        "success": False,
                        "reason": "test_failed",
                        "output": test_output
                    })
                }

        # ── Ollama QA check (non-blocking) ────────────────────────────────
        # Trigger in background thread so it doesn't block the transition.
        # Best-effort: if Ollama is down, silently skip.
        try:
            threading.Thread(
                target=_run_ollama_qa_check, args=(task,), daemon=True
            ).start()
        except Exception:
            pass  # Never block the transition

    elif new_status == "done":
        # Tests: only run when not forced (force=True skips test re-runs)
        if not force:
            test_cmd = task.get("test_command", "")
            if test_cmd:
                test_success, test_output = run_test_command(test_cmd)
                if not test_success:
                    return {
                        "git_notice": git_notice,
                        "ai_triggered": False,
                        "blocked": (400, {
                            "success": False,
                            "reason": "test_failed",
                            "output": test_output
                        })
                    }

        # Git operations: ALWAYS run when moving to Done, regardless of force.
        # force only skips tests; the git commit/merge is the core purpose of Done.
        branch_name = task.get("git_branch", "")
        base_branch = task.get("git_base_branch", "develop")

        if branch_name and base_branch in ("main", "master") and not force_merge:
            return {
                "git_notice": git_notice,
                "ai_triggered": False,
                "blocked": (400, {
                    "success": False,
                    "reason": "confirm_merge_main",
                    "branch": branch_name,
                    "base": base_branch,
                })
            }

        if branch_name:
            print(f"  Git: finalizing task {task_id} (worktree-based)")
            work = _work_dir_for(task_id)

            # Generate commit message — try Ollama first, fall back to generic
            commit_msg = _generate_ollama_commit_message(task, work)
            if not commit_msg:
                commit_msg = _generic_commit_message(task)

            # Inicializar variables de estado de Git en Done
            task["git_in_dev"] = False
            task["git_commit_error"] = ""

            # Verify worktree exists before attempting git operations
            if not os.path.isdir(work):
                task["git_commit_error"] = (
                    f"Worktree no encontrado en '{work}'. "
                    "La tarea se movió a Done sin worktree — posiblemente el directorio "
                    "fue limpiado manualmente. Para resolver: mueve la tarea de vuelta a "
                    "Doing para crear un nuevo worktree, o haz commit manual."
                )
                write_task(task)
                git_notice = f"Worktree no encontrado. Mueve a Doing para recrearlo."
                print(f"  Git: worktree missing for {task_id} at {work}", file=sys.stderr)
                return {"git_notice": git_notice, "ai_triggered": False, "blocked": None, "wiki_alerts": wiki_alerts}

            # Check if branch exists in the worktree
            branch_check_ok, branch_check_out, _ = _git(
                ["git", "rev-parse", "--verify", "--quiet", branch_name], cwd=work
            )
            if not branch_check_ok:
                task["git_commit_error"] = (
                    f"Rama '{branch_name}' no encontrada en el worktree. "
                    "Posiblemente fue eliminada. Mueve la tarea de vuelta a Doing para recrearla."
                )
                write_task(task)
                git_notice = f"Rama '{branch_name}' no encontrada en worktree."
                print(f"  Git: branch {branch_name} missing in worktree {work}", file=sys.stderr)
                return {"git_notice": git_notice, "ai_triggered": False, "blocked": None, "wiki_alerts": wiki_alerts}

            add_ok, add_out, add_err = _git(["git", "add", "-A"], cwd=work)
            if not add_ok:
                task["git_commit_error"] = f"git add falló: {add_err or add_out or 'error desconocido'}"
                write_task(task)
                git_notice = f"Error en git add: {add_err or add_out}"
                print(f"  Git: add failed for {task_id}: {add_err}", file=sys.stderr)
                return {"git_notice": git_notice, "ai_triggered": False, "blocked": None, "wiki_alerts": wiki_alerts}

            commit_ok, commit_out, commit_err = _git(["git", "commit", "-m", commit_msg], cwd=work)
            # Check both stdout+stderr: on Windows, "nothing to commit" goes to stdout
            _combined = (commit_err + " " + commit_out).lower()
            if not commit_ok and "nothing to commit" not in _combined and "clean" not in _combined and "no hay cambios" not in _combined:
                error_detail = commit_err or commit_out or 'error desconocido (posiblemente no hay cambios o el worktree está corrupto)'
                task["git_commit_error"] = f"git commit falló: {error_detail}"
                write_task(task)
                git_notice = f"Error en git commit: {error_detail}"
                print(f"  Git: commit failed for {task_id}: commit_err={commit_err}, commit_out={commit_out}", file=sys.stderr)
                return {"git_notice": git_notice, "ai_triggered": False, "blocked": None, "wiki_alerts": wiki_alerts}

            main_branch = get_current_git_branch()
            main_dirty = bool(safe_git_run("git status --porcelain")[1])

            # Si la rama principal está en otro lugar, cambiar a la esperada
            if main_branch != base_branch:
                if not main_dirty:
                    checkout_ok, _, checkout_err = _git(["git", "checkout", base_branch])
                    if checkout_ok:
                        main_branch = base_branch
                    else:
                        task["git_commit_error"] = f"No se pudo cambiar a '{base_branch}': {checkout_err}"
                        write_task(task)
                        git_notice = f"No se pudo cambiar a '{base_branch}': {checkout_err}"
                        return {"git_notice": git_notice, "ai_triggered": False, "blocked": None, "wiki_alerts": wiki_alerts}
                else:
                    task["git_commit_error"] = f"El repositorio principal está sucio en '{main_branch}'. No se puede cambiar a '{base_branch}'."
                    write_task(task)
                    git_notice = f"Repo principal sucio. No se puede fusionar en '{base_branch}'."
                    return {"git_notice": git_notice, "ai_triggered": False, "blocked": None, "wiki_alerts": wiki_alerts}

            if main_branch == base_branch and not main_dirty:
                print(f"  Git: merging '{branch_name}' into '{base_branch}'")
                merge_ok, _, merge_err = _git(
                    ["git", "merge", "--no-ff", branch_name, "-m", f"merge {branch_name}"]
                )
                if merge_ok:
                    # ── Wiki Sync (non-blocking) ──────────────────────
                    wiki_alerts = None
                    try:
                        from wiki_sync import analyze_task_for_wiki, commit_wiki_updates
                        wiki_result = analyze_task_for_wiki(task)
                        task.setdefault("wiki_sync_data", {})
                        task["wiki_sync_data"] = {
                            "status": "pending" if wiki_result["wiki_updates_needed"] else "done",
                            "affected_files": wiki_result["affected_wiki_files"],
                            "alerts": wiki_result["alerts"],
                            "validation_gaps": wiki_result["validation_gaps"],
                            "unplanned_changes": wiki_result["unplanned_changes"],
                            "last_run": now_iso(),
                        }
                        if wiki_result.get("changelog_entry"):
                            commit_ok, commit_msg = commit_wiki_updates(task, wiki_result)
                            if commit_ok:
                                task["wiki_sync_data"]["status"] = "done"
                                task["wiki_sync_data"]["changelog_committed"] = True
                            else:
                                task["wiki_sync_data"]["changelog_error"] = commit_msg
                                wiki_result["alerts"].append(f"Wiki changelog commit falló: {commit_msg}")
                        wiki_alerts = wiki_result
                    except Exception as e:
                        wiki_alerts = {
                            "error": str(e),
                            "alerts": [f"Wiki sync falló (no bloquea el merge): {e}"],
                        }
                        task.setdefault("wiki_sync_data", {})["error"] = str(e)
                    # ──────────────────────────────────────────────────

                    clean_ok, clean_msg = _remove_worktree(task_id)
                    branch_ok, _, branch_err = _git(["git", "branch", "-d", branch_name])
                    if clean_ok and branch_ok:
                        git_notice = f"Fusionado en '{base_branch}'. Worktree y rama limpiados."
                    else:
                        issues = []
                        if not clean_ok: issues.append(f"worktree: {clean_msg}")
                        if not branch_ok: issues.append(f"rama: {branch_err}")
                        git_notice = (
                            f"Fusionado en '{base_branch}', pero la limpieza falló: {'; '.join(issues)}. "
                            "Ejecuta 'git worktree prune' y 'git branch -d' manualmente."
                        )
                        print(f"  Git: cleanup failed for {task_id}: {issues}", file=sys.stderr)
                    task["git_in_dev"] = True
                    task["git_commit_error"] = ""
                    write_task(task)
                else:
                    _git(["git", "merge", "--abort"])
                    task["git_commit_error"] = f"Conflicto de fusión al mezclar '{branch_name}' en '{base_branch}': {merge_err}"
                    write_task(task)
                    git_notice = (f"El merge falló por conflictos: {merge_err}. "
                                  f"Rama '{branch_name}' y worktree conservados.")
            else:
                reason = ("el árbol principal tiene cambios sin guardar"
                          if main_dirty else
                          f"el árbol principal está en '{main_branch}', no en '{base_branch}'")
                task["git_commit_error"] = f"No fusionado porque {reason}."
                write_task(task)
                git_notice = (f"Cambios commiteados en '{branch_name}'. No fusiono porque "
                              f"{reason}. Fusiona tú: git merge {branch_name}")
        else:
            # Task has no git_branch — it was never in "doing", so there's nothing to commit.
            git_notice = (
                "Tarea movida a Done sin rama git (nunca estuvo en Doing). "
                "No hay cambios que commitear."
            )

    ai_triggered = False
    if new_status == "planning" and old_status != "planning" and not skip_ai:
        has_requirements = bool(task.get("planning_data", {}).get("requirements"))
        if not has_requirements:
            if is_plan_a():
                ai_triggered = True

                def _auto_plan():
                    import time, threading, urllib.request, json
                    # Retry loop: DB write happens after this function returns,
                    # so we may need a few attempts before the task is readable
                    max_retries = 5
                    for attempt in range(max_retries):
                        time.sleep(0.5)
                        try:
                            body = json.dumps({"id": task_id}).encode('utf-8')
                            req = urllib.request.Request(
                                "http://localhost:8181/api/tasks/plan/generate",
                                data=body,
                                headers={"Content-Type": "application/json"},
                                method="POST"
                            )
                            response = urllib.request.urlopen(req, timeout=5)
                            if response.status == 200:
                                break
                        except Exception:
                            if attempt == max_retries - 1:
                                print(f"  Auto-plan trigger failed after {max_retries} attempts for task {task_id}", file=sys.stderr)
                            continue

                threading.Thread(target=_auto_plan, daemon=True).start()
            # In Plan B, the AI in chat plans manually — don't auto-trigger

    return {"git_notice": git_notice, "ai_triggered": ai_triggered, "blocked": None, "wiki_alerts": wiki_alerts}


# ═══════════════════════════════════════════════════════════════════════════════
#  Ollama-powered helpers (best-effort, local fallback)
# ═══════════════════════════════════════════════════════════════════════════════

def _get_worktree_diff(work_dir: str) -> str:
    """Get the git diff from a worktree directory.

    Returns HEAD diff (all working changes vs last commit).
    Silently returns empty string on any error.
    """
    try:
        ok, out, _ = _git(["git", "diff", "HEAD"], cwd=work_dir)
        if ok and out.strip():
            return out
        # Fallback to unstaged changes if HEAD diff returns empty
        ok, out, _ = _git(["git", "diff"], cwd=work_dir)
        return out if ok and out.strip() else ""
    except Exception:
        return ""


def _generic_commit_message(task: dict) -> str:
    """Build a generic conventional commit message (existing behavior fallback)."""
    cat = task.get("category", "feat")
    prefix = "fix" if cat == "bug" else "docs" if cat == "docs" else "feat"
    task_id = task.get("id", "?")

    msg = f"{prefix}({task_id}): {task['title']}\n\nRequisitos completados:\n"
    if "planning_data" in task:
        for req in task["planning_data"].get("requirements", []):
            check = "[x]" if req.get("completed") else "[ ]"
            msg += f"- {check} {req['text']}\n"
    return msg


def _generate_ollama_commit_message(task: dict, work_dir: str) -> str | None:
    """Generate a conventional commit message via Ollama based on the worktree diff.

    Returns the commit message string on success, or None if Ollama is unavailable
    or fails (caller should fall back to _generic_commit_message).
    """
    try:
        from ai_router import AIRouter
        provider = AIRouter._providers.get("ollama")
        if not provider or not provider.available:
            return None

        diff = _get_worktree_diff(work_dir)
        if not diff or not diff.strip():
            return None

        # Truncate diff for local models that have smaller context windows
        max_diff = int(os.environ.get("OLLAMA_MAX_DIFF_CHARS", "6000"))
        if len(diff) > max_diff:
            diff = diff[:max_diff] + "\n... [diff truncado]"

        system_prompt = (
            "Genera un mensaje de commit convencional para este diff. Formato:\n"
            "type(scope): descripcion breve\n\n"
            "Tipos: feat, fix, refactor, docs, chore, test\n"
            "Scopes: backend, frontend, contracts, taskboard, wiki, docs\n\n"
            "Responde SOLO con el mensaje, sin explicaciones."
        )
        prompt = f"Genera un mensaje de commit para este diff:\n\n{diff}"

        result = provider.process(prompt, system=system_prompt)
        if not result or not result.strip():
            return None

        # Clean up the response
        msg = result.strip()
        # Strip markdown code fences if present
        if msg.startswith("```"):
            lines = msg.split("\n")
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            msg = "\n".join(lines).strip()

        # Validate it looks like a conventional commit
        valid_types = ("feat", "fix", "refactor", "docs", "chore", "test")
        has_valid_prefix = any(
            msg.startswith(t + "(") or msg.startswith(t + ":")
            for t in valid_types
        )

        if has_valid_prefix:
            print(f"  Ollama: generated commit message: {msg.split(chr(10))[0]}")
            return msg

        # Doesn't match conventional commit format — fall back
        print(f"  Ollama: response didn't match conventional commit format: {msg[:80]}")
        return None
    except Exception as e:
        print(f"  Ollama commit message error (non-blocking): {e}", file=sys.stderr)
        return None


def _run_ollama_qa_check(task: dict):
    """Run an Ollama-powered QA check on the task's worktree diff.

    Designed to be called in a background thread — never raises exceptions.
    Adds findings as task comments. Best-effort: silently exits if Ollama is down.
    """
    import re as _re
    try:
        from ai_router import AIRouter
        provider = AIRouter._providers.get("ollama")
        if not provider or not provider.available:
            return

        work = _work_dir_for(task["id"])
        if not work or not os.path.isdir(work):
            return

        diff = _get_worktree_diff(work)
        if not diff or not diff.strip():
            return

        # Truncate for local model context limits
        max_diff = int(os.environ.get("OLLAMA_MAX_DIFF_CHARS", "6000"))
        if len(diff) > max_diff:
            diff = diff[:max_diff] + "\n... [diff truncado]"

        system_prompt = (
            "Eres un revisor de codigo para Axolotto, un juego de loteria Web3. "
            "Revisa el siguiente diff y reporta SOLO problemas reales (no estilo/nits). "
            'Formato: { "issues": [{"severity": "high|medium|low", "file": "...", "line": N, "description": "..."}] } '
            'Si no hay issues, responde: { "issues": [] }'
        )

        result = provider.process(diff, system=system_prompt)
        if not result:
            return

        # Extract JSON from the response (may include markdown wrapping)
        json_match = _re.search(r'\{.*\}', result, _re.DOTALL)
        if not json_match:
            return

        data = json.loads(json_match.group(0))
        issues = data.get("issues", [])

        if not issues:
            print(f"  Ollama QA: no issues found for task {task.get('id', '?')}")
            return

        # Add each issue as a comment
        for issue in issues:
            sev = issue.get("severity", "low")
            fname = issue.get("file", "?")
            line_num = issue.get("line", "?")
            desc = issue.get("description", "")
            comment_text = (
                f"[QA] [{sev.upper()}] {fname}:{line_num} — {desc}"
            )
            task.setdefault("comments", []).append({
                "author": "ollama-qa",
                "text": comment_text,
                "timestamp": now_iso(),
            })

        print(
            f"  Ollama QA: {len(issues)} issue(s) found for task {task.get('id', '?')}"
        )
        write_task(task)
    except Exception as e:
        print(f"  Ollama QA check error (non-blocking): {e}", file=sys.stderr)


