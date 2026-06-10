#!/usr/bin/env python3
"""route_handlers/post_routes.py — All POST route handlers."""
import json, os, subprocess, sys, threading, time, urllib.parse, urllib.request, urllib.error
from db import read_tasks, write_tasks, write_task, delete_task_from_db, REPO_ROOT
from agent_runner import (
    get_agent_status, _read_log_tail, AGENT_LOG_DIR,
    safe_git_run, get_current_git_branch, slugify,
    _ensure_worktree, _remove_worktree, _work_dir_for, _git,
    now_iso, run_test_command, _keyword_assign, specialization_assign, _worktree_path,
)
from task_lifecycle import (
    validate_dependencies, handle_move_stage_transition,
    assign_category_if_missing,
)
from agy_client import is_plan_a

def handle_post(handler, path, body):
    """Dispatch POST request to the appropriate handler.
    `body` is already parsed from JSON by the caller (routes.py)."""

    # ── CREATE TASK ────────────────────────────────────────────────

    if path == "/api/tasks/create":
        tasks_data = read_tasks()
        prompt = body.get("prompt", "").strip()
        column = body.get("column", "concepts")

        if not prompt:
            handler.send_response(400)
            handler.end_headers()
            return

        if column not in ("wishes", "concepts"):
            column = "concepts"

        default_priority = "low" if column == "wishes" else "medium"

        new_task = {
            "id": f"task-{int(time.time())}-{len(tasks_data.get('tasks', []))}",
            "title": prompt[:50] + ("..." if len(prompt) > 50 else ""),
            "description": prompt,
            "status": column,
            "assigned_to": "unassigned",
            "priority": body.get("priority", default_priority),
            "category": body.get("category", "tools"),
            "scope": body.get("scope", "axolotto"),
            "test_command": "",
            "git_branch": "",
            "git_base_branch": "",
            "needs_agent_generation": False,
            "planning_data": {
                "requirements": [],
                "notes": "",
                "approved": False,
                "verification_guide": ""
            },
            "comments": [{
                "author": "user",
                "text": prompt,
                "timestamp": now_iso()
            }],
            "stage_history": [{
                "stage": column,
                "entered_at": now_iso(),
                "ai_triggered": False
            }],
            "ai_analysis": {},
            "created_at": now_iso(),
            "updated_at": now_iso()
        }

        if is_plan_a():
            try:
                agent_name, spec_key, provider, model, score = specialization_assign(new_task)
                if spec_key:
                    # Weighted scoring assignment succeeded
                    new_task["ai_analysis"]["recommended_agent"] = agent_name
                    new_task["ai_analysis"]["recommended_confidence"] = f"specialization({spec_key},{score:.1f})"
                    new_task["ai_analysis"]["assigned_specialization"] = spec_key
                    new_task["ai_analysis"]["assigned_provider"] = provider
                    new_task["ai_analysis"]["assigned_model"] = model
                else:
                    # Fallback to keyword assignment
                    rec_agent, rec_conf = _keyword_assign(
                        new_task["title"], new_task["description"], new_task["category"]
                    )
                    new_task["ai_analysis"]["recommended_agent"] = rec_agent
                    new_task["ai_analysis"]["recommended_confidence"] = rec_conf
            except Exception:
                try:
                    rec_agent, rec_conf = _keyword_assign(
                        new_task["title"], new_task["description"], new_task["category"]
                    )
                    new_task["ai_analysis"]["recommended_agent"] = rec_agent
                    new_task["ai_analysis"]["recommended_confidence"] = rec_conf
                except Exception:
                    pass
        # In Plan B: stays "unassigned" — the chat AI handles assignment

        tasks_data["tasks"].append(new_task)
        write_tasks(tasks_data)

        handler.send_response(201)
        handler.send_header("Content-Type", "application/json")
        handler.end_headers()
        handler.wfile.write(json.dumps(new_task, ensure_ascii=False).encode('utf-8'))

    # ── MOVE TASK ──────────────────────────────────────────────────

    elif path == "/api/tasks/move":
        task_id = body.get("id")
        new_status = body.get("status")
        force = body.get("force", False)
        skip_ai = body.get("skip_ai", False)
        force_merge = body.get("force_merge", False)

        if not task_id or not new_status:
            handler.send_response(400)
            handler.end_headers()
            return

        tasks_data = read_tasks()
        task_to_update = next((t for t in tasks_data["tasks"] if t["id"] == task_id), None)

        if not task_to_update:
            handler.send_response(404)
            handler.end_headers()
            return

        # Dependency validation — skip when force=True (escape hatch for stuck tasks)
        if not force:
            allowed, dep_msg = validate_dependencies(task_to_update, new_status, tasks_data["tasks"])
            if not allowed:
                handler.send_response(400)
                handler.send_header("Content-Type", "application/json")
                handler.end_headers()
                handler.wfile.write(json.dumps({
                    "success": False,
                    "reason": "blocked_by_dependency",
                    "message": dep_msg
                }, ensure_ascii=False).encode('utf-8'))
                return

        old_status = task_to_update.get("status", "planning")

        # When force=True, also skip AI to avoid re-triggering a stuck AI cycle
        effective_skip_ai = skip_ai or force

        # Handle stage transition side effects
        result = handle_move_stage_transition(
            task_to_update, old_status, new_status,
            force, effective_skip_ai, force_merge, tasks_data["tasks"]
        )

        if result["blocked"]:
            status_code, resp_dict = result["blocked"]
            handler.send_response(status_code)
            handler.send_header("Content-Type", "application/json")
            handler.end_headers()
            handler.wfile.write(json.dumps(resp_dict, ensure_ascii=False).encode('utf-8'))
            return

        git_notice = result["git_notice"]
        ai_triggered = result["ai_triggered"]
        wiki_alerts = result.get("wiki_alerts")

        # Update status
        task_to_update["status"] = new_status
        if new_status == "planning":
            task_to_update.setdefault("ai_analysis", {}).setdefault("planning", {})
            task_to_update["ai_analysis"]["planning"]["in_progress"] = True
        task_to_update["updated_at"] = now_iso()

        if write_tasks(tasks_data):
            handler.send_response(200)
            handler.send_header("Content-Type", "application/json")
            handler.end_headers()
            resp = {
                "success": True,
                "notice": git_notice,
                "ai_triggered": ai_triggered,
            }
            if wiki_alerts:
                resp["wiki_alerts"] = wiki_alerts
            handler.wfile.write(json.dumps(resp, ensure_ascii=False).encode('utf-8'))
        else:
            handler.send_response(500)
            handler.end_headers()

    # ── MOVE TASK BATCH ────────────────────────────────────────────

    elif path == "/api/tasks/move-batch":
        task_ids = body.get("ids", [])
        new_status = body.get("status")
        force = body.get("force", False)
        skip_ai = body.get("skip_ai", False)
        force_merge = body.get("force_merge", False)

        if not task_ids or not new_status:
            handler.send_response(400)
            handler.end_headers()
            return

        tasks_data = read_tasks()
        results = []
        any_success = False

        for task_id in task_ids:
            task_to_update = next((t for t in tasks_data["tasks"] if t["id"] == task_id), None)
            if not task_to_update:
                results.append({"id": task_id, "success": False, "reason": "not_found"})
                continue

            # Dependency validation — skip when force=True
            if not force:
                allowed, dep_msg = validate_dependencies(task_to_update, new_status, tasks_data["tasks"])
                if not allowed:
                    results.append({"id": task_id, "success": False, "reason": "blocked_by_dependency", "message": dep_msg})
                    continue

            old_status = task_to_update.get("status", "planning")

            # Skip move if status is already the target
            if old_status == new_status:
                results.append({"id": task_id, "success": True, "notice": "Already in status"})
                continue

            # When force=True, also skip AI to avoid re-triggering a stuck AI cycle
            effective_skip_ai = skip_ai or force

            # Handle stage transition side effects
            result = handle_move_stage_transition(
                task_to_update, old_status, new_status,
                force, effective_skip_ai, force_merge, tasks_data["tasks"]
            )

            if result["blocked"]:
                status_code, resp_dict = result["blocked"]
                results.append({"id": task_id, "success": False, "blocked": resp_dict, "status_code": status_code})
                continue

            git_notice = result["git_notice"]
            ai_triggered = result["ai_triggered"]
            wiki_alerts = result.get("wiki_alerts")

            # Update status
            task_to_update["status"] = new_status
            task_to_update["updated_at"] = now_iso()
            any_success = True

            res_entry = {
                "id": task_id,
                "success": True,
                "notice": git_notice,
                "ai_triggered": ai_triggered,
            }
            if wiki_alerts:
                res_entry["wiki_alerts"] = wiki_alerts
            results.append(res_entry)

        if any_success:
            write_tasks(tasks_data)

        handler.send_response(200)
        handler.send_header("Content-Type", "application/json")
        handler.end_headers()
        handler.wfile.write(json.dumps({
            "success": True,
            "results": results
        }, ensure_ascii=False).encode('utf-8'))


    # ── EDIT TASK DETAILS ──────────────────────────────────────────

    elif path == "/api/tasks/edit":
        task_id = body.get("id")
        if not task_id:
            handler.send_response(400)
            handler.end_headers()
            return

        tasks_data = read_tasks()
        task_to_update = next((t for t in tasks_data["tasks"] if t["id"] == task_id), None)

        if not task_to_update:
            handler.send_response(404)
            handler.end_headers()
            return

        new_status = body.get("status", task_to_update.get("status"))
        if new_status in ("doing", "review", "done") and new_status != task_to_update.get("status"):
            allowed, dep_msg = validate_dependencies(task_to_update, new_status, tasks_data["tasks"])
            if not allowed:
                handler.send_response(400)
                handler.send_header("Content-Type", "application/json")
                handler.end_headers()
                handler.wfile.write(json.dumps({
                    "success": False,
                    "reason": "blocked_by_dependency",
                    "message": dep_msg
                }, ensure_ascii=False).encode('utf-8'))
                return

        if "dependencies" in body:
            planning_data = task_to_update.get("planning_data", {})
            if not isinstance(planning_data, dict):
                planning_data = {}
            planning_data["dependencies"] = body["dependencies"]
            task_to_update["planning_data"] = planning_data

        if "plan_doc_path" in body:
            planning_data = task_to_update.get("planning_data", {})
            if not isinstance(planning_data, dict):
                planning_data = {}
            doc_rel = (body["plan_doc_path"] or "").strip().replace("\\", "/")
            if doc_rel:
                # Security: must be an existing .md inside REPO_ROOT/docs
                abs_doc = os.path.normpath(os.path.join(REPO_ROOT, doc_rel))
                docs_dir = os.path.normpath(os.path.join(REPO_ROOT, "docs"))
                if not abs_doc.startswith(docs_dir) or not doc_rel.endswith(".md") or not os.path.isfile(abs_doc):
                    handler.send_response(400)
                    handler.send_header("Content-Type", "application/json; charset=utf-8")
                    handler.end_headers()
                    handler.wfile.write(json.dumps({
                        "success": False,
                        "message": f"Doc no encontrado o fuera de docs/: {doc_rel}"
                    }, ensure_ascii=False).encode('utf-8'))
                    return
                planning_data["plan_doc_path"] = doc_rel
            else:
                planning_data.pop("plan_doc_path", None)
            task_to_update["planning_data"] = planning_data

        task_to_update["title"] = body.get("title", task_to_update["title"])
        task_to_update["description"] = body.get("description", task_to_update["description"])
        task_to_update["assigned_to"] = body.get("assigned_to", task_to_update["assigned_to"])
        task_to_update["priority"] = body.get("priority", task_to_update["priority"])
        task_to_update["category"] = body.get("category", task_to_update["category"])
        task_to_update["scope"] = body.get("scope", task_to_update.get("scope", "axolotto"))
        task_to_update["test_command"] = body.get("test_command", task_to_update.get("test_command", ""))
        task_to_update["status"] = body.get("status", task_to_update["status"])
        task_to_update["updated_at"] = now_iso()

        if task_to_update["status"] in ("planning", "doing"):
            assign_category_if_missing(task_to_update)

        if "needs_agent_generation" in task_to_update:
            del task_to_update["needs_agent_generation"]

        if write_tasks(tasks_data):
            handler.send_response(200)
            handler.send_header("Content-Type", "application/json")
            handler.end_headers()
            handler.wfile.write(json.dumps({"success": True}).encode('utf-8'))
        else:
            handler.send_response(500)
            handler.end_headers()

    # ── TOGGLE REQUIREMENT ─────────────────────────────────────────

    elif path == "/api/tasks/requirements/toggle":
        task_id = body.get("id")
        req_id = body.get("req_id")
        completed = body.get("completed")

        if not task_id or req_id is None:
            handler.send_response(400)
            handler.end_headers()
            return

        tasks_data = read_tasks()
        task = next((t for t in tasks_data["tasks"] if t["id"] == task_id), None)

        if not task:
            handler.send_response(404)
            handler.end_headers()
            return

        found = False
        if "planning_data" in task:
            for req in task["planning_data"].get("requirements", []):
                if req["id"] == req_id:
                    req["completed"] = completed
                    found = True
                    break

        if found and write_tasks(tasks_data):
            handler.send_response(200)
            handler.send_header("Content-Type", "application/json")
            handler.end_headers()
            handler.wfile.write(json.dumps({"success": True}).encode('utf-8'))
        else:
            handler.send_response(500)
            handler.end_headers()

    # ── EDIT REQUIREMENTS LIST ─────────────────────────────────────

    elif path == "/api/tasks/requirements/edit":
        task_id = body.get("id")
        reqs = body.get("requirements")
        notes = body.get("notes")
        guide = body.get("verification_guide")

        if not task_id:
            handler.send_response(400)
            handler.end_headers()
            return

        tasks_data = read_tasks()
        task = next((t for t in tasks_data["tasks"] if t["id"] == task_id), None)

        if not task:
            handler.send_response(404)
            handler.end_headers()
            return

        if "planning_data" not in task:
            task["planning_data"] = {"requirements": [], "notes": "", "approved": False, "verification_guide": ""}

        if reqs is not None:
            task["planning_data"]["requirements"] = reqs
            if task.get("ai_analysis", {}).get("planning"):
                task["ai_analysis"]["planning"]["generated_requirements"] = reqs
        if notes is not None:
            task["planning_data"]["notes"] = notes
        if guide is not None:
            task["planning_data"]["verification_guide"] = guide

        task["updated_at"] = now_iso()

        if write_tasks(tasks_data):
            handler.send_response(200)
            handler.send_header("Content-Type", "application/json")
            handler.end_headers()
            handler.wfile.write(json.dumps({"success": True}).encode('utf-8'))
        else:
            handler.send_response(500)
            handler.end_headers()

    # ── TOGGLE PLAN APPROVAL ───────────────────────────────────────

    elif path == "/api/tasks/plan/approve":
        task_id = body.get("id")
        approved = body.get("approved", False)

        if not task_id:
            handler.send_response(400)
            handler.end_headers()
            return

        tasks_data = read_tasks()
        task = next((t for t in tasks_data["tasks"] if t["id"] == task_id), None)

        if not task:
            handler.send_response(404)
            handler.end_headers()
            return

        if "planning_data" in task:
            task["planning_data"]["approved"] = approved
            task["updated_at"] = now_iso()

        if write_tasks(tasks_data):
            handler.send_response(200)
            handler.send_header("Content-Type", "application/json")
            handler.end_headers()
            handler.wfile.write(json.dumps({"success": True}).encode('utf-8'))
        else:
            handler.send_response(500)
            handler.end_headers()

    # ── GENERATE PLAN WITH AI ──────────────────────────────────────
    elif path == "/api/tasks/plan/generate":
        task_id = body.get("id")
        feedback = body.get("feedback", "").strip()
        if not task_id:
            handler.send_response(400)
            handler.end_headers()
            return

        tasks_data = read_tasks()
        task = next((t for t in tasks_data["tasks"] if t["id"] == task_id), None)
        if not task:
            handler.send_response(404)
            handler.end_headers()
            return

        # Start background planning thread
        def _bg_planning():
            try:
                from ai_router import AIRouter
                log_path = os.path.join(AGENT_LOG_DIR, f"{task_id}.log")

                # Mark planning start
                fresh_data = read_tasks()
                fresh_task = next((t for t in fresh_data["tasks"] if t["id"] == task_id), None)
                if fresh_task:
                    msg = "[AI PLANNING] Iniciando refinamiento del plan..." if feedback else "[AI PLANNING] Iniciando planificación con IA..."
                    fresh_task.setdefault("comments", []).append({
                        "author": "system",
                        "text": msg,
                        "timestamp": now_iso()
                    })
                    # If feedback provided, append it as context the AI will see
                    if feedback:
                        fresh_task["description"] = (fresh_task.get("description", "") + "\n\n[FEEDBACK DEL USUARIO]: " + feedback)
                    write_task(fresh_task)

                updated_task = AIRouter.process_stage(task, "planning", log_path=log_path)
                if updated_task:
                    # Load fresh again to avoid conflicts
                    fresh_data = read_tasks()
                    fresh_task = next((t for t in fresh_data["tasks"] if t["id"] == task_id), None)
                    if fresh_task:
                        fresh_task["planning_data"] = updated_task["planning_data"]
                        fresh_task["ai_analysis"] = updated_task["ai_analysis"]
                        fresh_task["assigned_to"] = updated_task["assigned_to"]
                        fresh_task["title"] = updated_task["title"]
                        fresh_task["category"] = updated_task["category"]
                        fresh_task["needs_agent_generation"] = False
                        
                        # Generate execution details
                        agent = updated_task.get("assigned_to", "claude")
                        wt_path = _worktree_path(task_id)
                        execution_cmd = f'cd "{wt_path}" ; {agent}'
                        fresh_task.setdefault("ai_analysis", {}).setdefault("execution", {})
                        fresh_task["ai_analysis"]["execution"] = {
                            "agent": agent,
                            "command": execution_cmd,
                            "awaiting": True
                        }
                        
                        fresh_task.setdefault("ai_analysis", {}).setdefault("planning", {})["in_progress"] = False
                        write_task(fresh_task)
                        print(f"  AI Planning: Task {task_id} planned successfully.")
            except Exception as e:
                print(f"  AI Planning Error: {e}", file=sys.stderr)
                # Clear in_progress on failure too
                try:
                    fresh_data = read_tasks()
                    fresh_task2 = next((t for t in fresh_data["tasks"] if t["id"] == task_id), None)
                    if fresh_task2:
                        fresh_task2.setdefault("ai_analysis", {}).setdefault("planning", {})["in_progress"] = False
                        write_task(fresh_task2)
                except Exception:
                    pass

        threading.Thread(target=_bg_planning, daemon=True).start()

        handler.send_response(200)
        handler.send_header("Content-Type", "application/json")
        handler.end_headers()
        handler.wfile.write(json.dumps({"success": True, "message": "Planificación iniciada en background."}, ensure_ascii=False).encode('utf-8'))

    # ── CANCEL PLANNING ─────────────────────────────────────────────

    elif path == "/api/tasks/plan/cancel":
        task_id = body.get("id", "").strip()

        if not task_id:
            handler.send_response(400)
            handler.send_header("Content-Type", "application/json")
            handler.end_headers()
            handler.wfile.write(json.dumps({"error": "task id required"}).encode('utf-8'))
            return

        tasks_data = read_tasks()
        task = next((t for t in tasks_data["tasks"] if t["id"] == task_id), None)
        if not task:
            handler.send_response(404)
            handler.send_header("Content-Type", "application/json")
            handler.end_headers()
            handler.wfile.write(json.dumps({"error": "task not found"}).encode('utf-8'))
            return

        # Remove from active AI calls
        try:
            from ai_router import AIRouter
            if hasattr(AIRouter, '_active_calls'):
                AIRouter._active_calls.pop(task_id, None)
        except Exception:
            pass

        # Revert to concepts
        task["status"] = "concepts"
        task.setdefault("stage_history", []).append({
            "stage": "concepts",
            "entered_at": now_iso(),
            "ai_triggered": False,
        })
        task.setdefault("comments", []).append({
            "author": "system",
            "text": "Planificacion cancelada por el usuario.",
            "timestamp": now_iso()
        })
        task["updated_at"] = now_iso()

        write_tasks(tasks_data)

        handler.send_response(200)
        handler.send_header("Content-Type", "application/json")
        handler.end_headers()
        handler.wfile.write(json.dumps({"success": True, "status": "concepts"}).encode('utf-8'))
        return

    # ── POST COMMENT ───────────────────────────────────────────────

    elif path == "/api/tasks/comment":
        task_id = body.get("id")
        author = body.get("author", "user")
        text = body.get("text", "").strip()

        if not task_id or not text:
            handler.send_response(400)
            handler.end_headers()
            return

        tasks_data = read_tasks()
        task = next((t for t in tasks_data["tasks"] if t["id"] == task_id), None)

        if not task:
            handler.send_response(404)
            handler.end_headers()
            return

        new_comment = {
            "author": author,
            "text": text,
            "timestamp": now_iso()
        }
        if "comments" not in task:
            task["comments"] = []
        task["comments"].append(new_comment)

        if write_tasks(tasks_data):
            handler.send_response(200)
            handler.send_header("Content-Type", "application/json")
            handler.end_headers()
            handler.wfile.write(json.dumps({"success": True, "task": task}, ensure_ascii=False).encode('utf-8'))

            # TRIGGER REFINE PLAN BACKGROUND PROCESS (Plan A only)
            if is_plan_a() and task.get("status") in ("planning", "concepts", "review") and author == "user":
                def _bg_refine():
                    try:
                        from ai_router import AIRouter
                        log_path = os.path.join(AGENT_LOG_DIR, f"{task_id}.log")
                        ai_response = AIRouter.process_comment(
                            task, text, stage=task.get("status", "planning"),
                            log_path=log_path
                        )
                        if ai_response:
                            fresh_data = read_tasks()
                            fresh_task = next((t for t in fresh_data["tasks"] if t["id"] == task_id), None)
                            if fresh_task:
                                agent_name = "ai"
                                for n in ["deepclaude", "claude"]:
                                    p = AIRouter._providers.get(n)
                                    if p and getattr(p, 'available', False):
                                        agent_name = n
                                        break
                                fresh_task.setdefault("comments", []).append({
                                    "author": agent_name,
                                    "text": ai_response,
                                    "timestamp": now_iso()
                                })
                                write_task(fresh_task)
                    except Exception as e:
                        print(f"  AI Comment Response Error: {e}", file=sys.stderr)
                
                threading.Thread(target=_bg_refine, daemon=True).start()
        else:
            handler.send_response(500)
            handler.end_headers()

    # ── REVIEW FEEDBACK ────────────────────────────────────────────

    elif path == "/api/tasks/review-feedback":
        task_id = body.get("id")
        feedback = body.get("feedback", "").strip()

        if not task_id or not feedback:
            handler.send_response(400)
            handler.end_headers()
            return

        tasks_data = read_tasks()
        task = next((t for t in tasks_data["tasks"] if t["id"] == task_id), None)

        if not task:
            handler.send_response(404)
            handler.end_headers()
            return

        task.setdefault("comments", []).append({
            "author": "user",
            "text": f"[REVIEW FEEDBACK] {feedback}",
            "timestamp": now_iso()
        })

        task["updated_at"] = now_iso()

        # Generate AI response to review feedback
        ai_response = None
        try:
            from ai_router import AIRouter
            log_path = os.path.join(AGENT_LOG_DIR, f"{task_id}.log")
            ai_response = AIRouter.process_comment(
                task, feedback, stage="review", log_path=log_path
            )
            if ai_response:
                agent_name = "ai"
                for n in ["deepclaude", "claude"]:
                    p = AIRouter._providers.get(n)
                    if p and getattr(p, 'available', False):
                        agent_name = n
                        break
                task.setdefault("comments", []).append({
                    "author": agent_name,
                    "text": ai_response,
                    "timestamp": now_iso()
                })
        except Exception as e:
            print(f"  AI Review Chat Error: {e}", file=sys.stderr)

        # Optionally move back to doing
        move_notice = None
        request_changes = body.get("request_changes", False)
        if request_changes and task.get("status") == "review":
            task["status"] = "doing"
            task.setdefault("stage_history", []).append({
                "stage": "doing",
                "entered_at": now_iso(),
                "ai_triggered": False,
            })
            move_notice = "Tarea devuelta a Doing para aplicar los cambios solicitados."

        if write_tasks(tasks_data):
            handler.send_response(200)
            handler.send_header("Content-Type", "application/json")
            handler.end_headers()
            resp = {"success": True}
            if ai_response:
                resp["ai_response"] = ai_response
            if move_notice:
                resp["notice"] = move_notice
            handler.wfile.write(json.dumps(resp, ensure_ascii=False).encode('utf-8'))
        else:
            handler.send_response(500)
            handler.end_headers()

    # ── DELETE TASK ────────────────────────────────────────────────

    elif path == "/api/tasks/delete":
        task_id = body.get("id")
        if not task_id:
            handler.send_response(400)
            handler.end_headers()
            return

        if delete_task_from_db(task_id):
            try:
                _remove_worktree(task_id)
            except Exception as e:
                print(f"  Git: worktree cleanup failed for {task_id}: {e}", file=sys.stderr)
            handler.send_response(200)
            handler.send_header("Content-Type", "application/json")
            handler.end_headers()
            handler.wfile.write(json.dumps({"success": True}).encode('utf-8'))
        else:
            handler.send_response(404)
            handler.end_headers()

    # ── STATUS UPDATE (move + comment in one call) ──────────────────

    elif path == "/api/tasks/status":
        task_id = body.get("id")
        new_status = body.get("status")
        comment_text = body.get("comment", "").strip()
        assigned_to_override = body.get("assigned_to", "").strip()

        if not task_id or not new_status:
            handler.send_response(400)
            handler.end_headers()
            return

        tasks_data = read_tasks()
        task = next((t for t in tasks_data["tasks"] if t["id"] == task_id), None)
        if not task:
            handler.send_response(404)
            handler.end_headers()
            return

        old_status = task.get("status", "planning")

        # Apply explicit agent assignment before lifecycle (so lifecycle sees the right agent)
        known_agents = {"claude", "deepclaude", "agy"}
        if assigned_to_override and assigned_to_override in known_agents:
            task["assigned_to"] = assigned_to_override

        # Add comment if provided
        if comment_text:
            task.setdefault("comments", []).append({
                "author": task.get("assigned_to", "agent"),
                "text": comment_text,
                "timestamp": now_iso(),
            })

        # Handle stage transition
        result = handle_move_stage_transition(
            task, old_status, new_status,
            force=False, skip_ai=False, force_merge=False,
            all_tasks=tasks_data["tasks"]
        )

        if result["blocked"]:
            status_code, resp_dict = result["blocked"]
            handler.send_response(status_code)
            handler.send_header("Content-Type", "application/json")
            handler.end_headers()
            handler.wfile.write(json.dumps(resp_dict, ensure_ascii=False).encode("utf-8"))
            return

        task["status"] = new_status
        task["updated_at"] = now_iso()

        write_tasks(tasks_data)

        handler.send_response(200)
        handler.send_header("Content-Type", "application/json")
        handler.end_headers()
        status_resp = {
            "success": True,
            "notice": f"Tarea movida a {new_status}",
            "ai_triggered": result.get("ai_triggered", False),
        }
        wiki_alerts = result.get("wiki_alerts")
        if wiki_alerts:
            status_resp["wiki_alerts"] = wiki_alerts
        handler.wfile.write(json.dumps(status_resp, ensure_ascii=False).encode("utf-8"))

    # ── CANCEL QUEUED TASK ─────────────────────────────────────────

    elif path == "/api/tasks/cancel-queue":
        # Manual execution mode — just move task back to planning
        task_id = body.get("id")
        if not task_id:
            handler.send_response(400)
            handler.end_headers()
            return

        tasks_data = read_tasks()
        task = next((t for t in tasks_data["tasks"] if t["id"] == task_id), None)
        if not task:
            handler.send_response(404)
            handler.end_headers()
            return

        task["status"] = "planning"
        assign_category_if_missing(task)
        task.setdefault("stage_history", []).append({
            "stage": "planning", "entered_at": now_iso(), "ai_triggered": False,
        })
        task.setdefault("comments", []).append({
            "author": "system",
            "text": "[CANCELADO] Tarea devuelta a planning por el usuario.",
            "timestamp": now_iso()
        })
        task["updated_at"] = now_iso()
        write_tasks(tasks_data)

        handler.send_response(200)
        handler.send_header("Content-Type", "application/json")
        handler.end_headers()
        handler.wfile.write(json.dumps({
            "success": True,
            "notice": "Tarea devuelta a planning."
        }, ensure_ascii=False).encode("utf-8"))

    # ── MANUAL AGENT ASSIGN ────────────────────────────────────────

    elif path == "/api/tasks/assign":
        task_id = body.get("id")
        agent   = body.get("agent", "").strip()
        known   = ("claude", "deepclaude", "agy")
        if not task_id or agent not in known:
            handler.send_response(400)
            handler.end_headers()
            return
        tasks_data = read_tasks()
        task = next((t for t in tasks_data["tasks"] if t["id"] == task_id), None)
        if not task:
            handler.send_response(404)
            handler.end_headers()
            return
        task["assigned_to"] = agent
        task["updated_at"] = now_iso()
        if write_tasks(tasks_data):
            handler.send_response(200)
            handler.send_header("Content-Type", "application/json")
            handler.end_headers()
            handler.wfile.write(json.dumps({"success": True}).encode('utf-8'))
        else:
            handler.send_response(500)
            handler.end_headers()

    # ── RESTART AXOLOTTO ECOSYSTEM ─────────────────────────────────

    elif path == "/api/restart-axo":
        def _run_restart():
            try:
                is_windows = sys.platform == "win32"

                if is_windows:
                    script = os.path.join(REPO_ROOT, "reiniciar.ps1")
                    cmd = ["powershell", "-ExecutionPolicy", "Bypass",
                           "-File", script, "axo"]
                else:
                    script = os.path.join(REPO_ROOT, "reiniciar.sh")
                    cmd = ["bash", script, "axo"]

                result = subprocess.run(
                    cmd,
                    cwd=REPO_ROOT if not is_windows else None,
                    capture_output=True, text=True,
                    encoding="utf-8", errors="replace",
                    timeout=180
                )
                print(f"  Restart axo completed: {result.returncode}")
                if result.stdout:
                    print(result.stdout[-500:])
                if result.stderr:
                    print(result.stderr[-500:], file=sys.stderr)
            except Exception as e:
                print(f"  Restart axo error: {e}", file=sys.stderr)

        threading.Thread(target=_run_restart, daemon=True).start()
        handler.send_response(202)
        handler.send_header("Content-Type", "application/json")
        handler.end_headers()
        handler.wfile.write(json.dumps({
            "processing": True,
            "message": "Reiniciando ecosistema Axolotto (sin Taskboard)...",
        }).encode('utf-8'))

    # ── PRODUCTION SERVER ────────────────────────────────────────

    elif path == "/api/server/pull":
        def _run_server_pull():
            try:
                host = os.environ.get("AXO_PROD_HOST", "192.168.100.15")
                ssh_cmd = [
                    "ssh", "-o", "StrictHostKeyChecking=accept-new",
                    host,
                    "cd ~/axolotto && git pull origin master",
                ]
                result = subprocess.run(
                    ssh_cmd,
                    capture_output=True, text=True,
                    encoding="utf-8", errors="replace",
                    timeout=60,
                )
                print(f"  Server pull completed: {result.returncode}")
                if result.stdout:
                    print(result.stdout[-500:])
                if result.stderr:
                    print(result.stderr[-500:], file=sys.stderr)
            except Exception as e:
                print(f"  Server pull error: {e}", file=sys.stderr)

        threading.Thread(target=_run_server_pull, daemon=True).start()
        handler.send_response(202)
        handler.send_header("Content-Type", "application/json")
        handler.end_headers()
        handler.wfile.write(json.dumps({
            "processing": True,
            "message": "Ejecutando git pull en el servidor de produccion...",
        }).encode("utf-8"))

    elif path == "/api/server/restart":
        command_arg = body.get("command", "axo")

        def _run_server_restart():
            try:
                host = os.environ.get("AXO_PROD_HOST", "192.168.100.15")
                if command_arg == "full":
                    remote_cmd = "cd ~/axolotto && ./reiniciar.sh"
                else:
                    remote_cmd = "cd ~/axolotto && ./reiniciar.sh axo"

                ssh_cmd = [
                    "ssh", "-o", "StrictHostKeyChecking=accept-new",
                    host, remote_cmd,
                ]
                result = subprocess.run(
                    ssh_cmd,
                    capture_output=True, text=True,
                    encoding="utf-8", errors="replace",
                    timeout=180,
                )
                print(f"  Server restart ({command_arg}) completed: {result.returncode}")
                if result.stdout:
                    print(result.stdout[-500:])
                if result.stderr:
                    print(result.stderr[-500:], file=sys.stderr)
            except Exception as e:
                print(f"  Server restart error: {e}", file=sys.stderr)

        threading.Thread(target=_run_server_restart, daemon=True).start()
        msg = (
            "Reiniciando todo el ecosistema en produccion..."
            if command_arg == "full"
            else "Reiniciando Axolotto en produccion (sin Taskboard)..."
        )
        handler.send_response(202)
        handler.send_header("Content-Type", "application/json")
        handler.end_headers()
        handler.wfile.write(json.dumps({
            "processing": True,
            "command": command_arg,
            "message": msg,
        }).encode("utf-8"))

    # ── MARK MANUAL EXECUTION DONE ─────────────────────────────────

    elif path == "/api/tasks/exec-done":
        task_id = body.get("id")
        if not task_id:
            handler.send_response(400)
            handler.end_headers()
            return
        tasks_data = read_tasks()
        task = next((t for t in tasks_data["tasks"] if t["id"] == task_id), None)
        if not task:
            handler.send_response(404)
            handler.end_headers()
            return

        ai = task.setdefault("ai_analysis", {})
        if isinstance(ai.get("execution"), dict):
            ai["execution"]["awaiting"] = False
            ai["execution"]["finished_at"] = now_iso()
        agent = (ai.get("execution") or {}).get("agent", task.get("assigned_to", "ai"))
        task.setdefault("comments", []).append({
            "author": agent,
            "text": f"[Ejecución manual marcada como terminada por el usuario]",
            "timestamp": now_iso(),
        })
        task["status"] = "review"
        task.setdefault("stage_history", []).append({
            "stage": "review", "entered_at": now_iso(),
            "ai_triggered": False, "ai_model": agent,
        })
        task["updated_at"] = now_iso()
        write_tasks(tasks_data)
        handler.send_response(200)
        handler.send_header("Content-Type", "application/json")
        handler.end_headers()
        handler.wfile.write(json.dumps({
            "success": True,
            "notice": "Ejecución marcada terminada. Tarea lista para revisión.",
            "ai_triggered": False,
        }, ensure_ascii=False).encode('utf-8'))

    # ── CONTEXT STATUS (check staleness without refreshing) ────────

    elif path == "/api/context-status":
        from project_context import load_cached, CONTEXT_CACHE_TTL_SECONDS
        import time as _time
        scopes = ["axolotto", "taskboard"]
        statuses = []
        for s in scopes:
            cached = load_cached(s)
            path_ = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                ".context_cache", f"{s}.txt"
            )
            if os.path.exists(path_):
                age = _time.time() - os.path.getmtime(path_)
                ttl = CONTEXT_CACHE_TTL_SECONDS
                statuses.append({
                    "scope": s,
                    "exists": True,
                    "age_seconds": round(age),
                    "age_human": f"{int(age // 3600)}h {int((age % 3600) // 60)}m",
                    "ttl_seconds": ttl,
                    "stale": age > ttl,
                    "size_chars": len(cached) if cached else 0,
                    "lines": cached.count('\n') if cached else 0,
                    "recommend_refresh": age > (ttl * 0.5),  # recommend after 12h
                })
            else:
                statuses.append({
                    "scope": s,
                    "exists": False,
                    "stale": True,
                    "recommend_refresh": True,
                })
        # Check git activity as a heuristic for "should refresh"
        try:
            git_log = subprocess.run(
                ["git", "log", "--oneline", "--since=24 hours ago", "--no-decorate"],
                cwd=REPO_ROOT, capture_output=True, text=True, timeout=3
            )
            recent_commits = len([l for l in git_log.stdout.strip().split('\n') if l]) if git_log.returncode == 0 else 0
        except Exception:
            recent_commits = 0

        result = {
            "scopes": statuses,
            "any_stale": any(s["stale"] for s in statuses),
            "any_recommend": any(s.get("recommend_refresh", False) for s in statuses),
            "recent_git_commits_24h": recent_commits,
            "recommend_refresh": any(s.get("recommend_refresh", False) for s in statuses) or recent_commits > 3,
            "recommend_reasons": [],
        }
        if any(s.get("recommend_refresh", False) for s in statuses):
            result["recommend_reasons"].append("context_cache_older_than_12h")
        if recent_commits > 3:
            result["recommend_reasons"].append(f"high_git_activity ({recent_commits} commits in 24h)")
        handler.send_response(200)
        handler.send_header("Content-Type", "application/json")
        handler.end_headers()
        handler.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))

    # ── REFRESH PROJECT CONTEXT CACHE ──────────────────────────────

    elif path == "/api/refresh-context":
        scope = body.get("scope") if isinstance(body, dict) else None
        from ai_router import refresh_context_cache
        result = refresh_context_cache(scope)
        handler.send_response(200)
        handler.send_header("Content-Type", "application/json")
        handler.end_headers()
        handler.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))

    # ── GIT MERGE TASK BRANCH ───────────────────────────────────────

    elif path == "/api/git/merge":
        task_id = body.get("task_id", "").strip() if isinstance(body, dict) else ""
        force = body.get("force", False) if isinstance(body, dict) else False
        if not task_id:
            handler.send_response(400)
            handler.send_header("Content-Type", "application/json; charset=utf-8")
            handler.end_headers()
            handler.wfile.write(json.dumps({
                "success": False, "error": "task_id requerido"
            }, ensure_ascii=False).encode("utf-8"))
            return

        tasks_data = read_tasks()
        task = next((t for t in tasks_data["tasks"] if t["id"] == task_id), None)
        if not task:
            handler.send_response(404)
            handler.send_header("Content-Type", "application/json; charset=utf-8")
            handler.end_headers()
            handler.wfile.write(json.dumps({
                "success": False, "error": "Tarea no encontrada"
            }, ensure_ascii=False).encode("utf-8"))
            return

        branch = task.get("git_branch", "")
        base = task.get("git_base_branch", get_current_git_branch())
        if not branch:
            handler.send_response(400)
            handler.send_header("Content-Type", "application/json; charset=utf-8")
            handler.end_headers()
            handler.wfile.write(json.dumps({
                "success": False, "error": "La tarea no tiene rama git asignada"
            }, ensure_ascii=False).encode("utf-8"))
            return

        current_branch = get_current_git_branch()
        _, status_out, _ = safe_git_run("git status --porcelain")
        if status_out.strip():
            handler.send_response(409)
            handler.send_header("Content-Type", "application/json; charset=utf-8")
            handler.end_headers()
            handler.wfile.write(json.dumps({
                "success": False,
                "error": "Repo sucio — haz stash o commit de tus cambios antes de mergear",
                "dirty": True,
            }, ensure_ascii=False).encode("utf-8"))
            return

        work = _work_dir_for(task_id)
        has_worktree = os.path.isdir(work)

        # Stage + commit in worktree if it exists
        if has_worktree:
            _git(["git", "add", "-A"], cwd=work)
            cat = task.get("category", "feat")
            prefix = "fix" if cat == "bug" else "docs" if cat == "docs" else "feat"
            commit_msg = f"{prefix}({task_id}): {task['title']}"
            commit_ok, commit_out, commit_err = _git(
                ["git", "commit", "-m", commit_msg], cwd=work
            )
            combined = (commit_err + " " + commit_out).lower()
            if not commit_ok and "nothing to commit" not in combined and "clean" not in combined:
                handler.send_response(500)
                handler.send_header("Content-Type", "application/json; charset=utf-8")
                handler.end_headers()
                handler.wfile.write(json.dumps({
                    "success": False,
                    "error": f"git commit falló: {commit_err or commit_out}",
                }, ensure_ascii=False).encode("utf-8"))
                return

        # Switch to base branch
        if current_branch != base:
            checkout_ok, _, checkout_err = _git(["git", "checkout", base])
            if not checkout_ok:
                handler.send_response(500)
                handler.send_header("Content-Type", "application/json; charset=utf-8")
                handler.end_headers()
                handler.wfile.write(json.dumps({
                    "success": False,
                    "error": f"No se pudo cambiar a '{base}': {checkout_err}",
                }, ensure_ascii=False).encode("utf-8"))
                return

        # Merge
        merge_msg = f"merge {branch}"
        merge_ok, merge_out, merge_err = _git(
            ["git", "merge", "--no-ff", branch, "-m", merge_msg]
        )

        if merge_ok:
            # Cleanup
            cleanup_msgs = []
            if has_worktree:
                clean_ok, clean_msg = _remove_worktree(task_id)
                if not clean_ok:
                    cleanup_msgs.append(f"worktree: {clean_msg}")
            branch_ok, _, branch_err = _git(["git", "branch", "-d", branch])
            if not branch_ok:
                cleanup_msgs.append(f"rama: {branch_err}")

            task["git_in_dev"] = True
            task["git_commit_error"] = ""
            write_task(task)

            handler.send_response(200)
            handler.send_header("Content-Type", "application/json; charset=utf-8")
            handler.end_headers()
            handler.wfile.write(json.dumps({
                "success": True,
                "message": f"Fusionado '{branch}' en '{base}'",
                "cleanup_notes": cleanup_msgs if cleanup_msgs else None,
            }, ensure_ascii=False).encode("utf-8"))
        else:
            _git(["git", "merge", "--abort"])
            task["git_commit_error"] = f"Conflicto: {merge_err}"
            task["git_in_dev"] = False
            write_task(task)

            handler.send_response(409)
            handler.send_header("Content-Type", "application/json; charset=utf-8")
            handler.end_headers()
            handler.wfile.write(json.dumps({
                "success": False,
                "error": f"Conflicto de merge: {merge_err}. Rama '{branch}' conservada.",
                "conflict": True,
            }, ensure_ascii=False).encode("utf-8"))

    # ── GIT CLEANUP STALE WORKTREES ──────────────────────────────────

    elif path == "/api/git/cleanup":
        import datetime as _dt
        if not os.path.isdir(WORKTREE_DIR):
            handler.send_response(200)
            handler.send_header("Content-Type", "application/json; charset=utf-8")
            handler.end_headers()
            handler.wfile.write(json.dumps({
                "success": True, "removed": [], "message": "No hay worktrees para limpiar"
            }, ensure_ascii=False).encode("utf-8"))
            return

        tasks_data = read_tasks()
        tasks_by_id = {t["id"]: t for t in tasks_data.get("tasks", [])}
        current_branch = get_current_git_branch()
        removed = []
        errors = []

        for entry in sorted(os.listdir(WORKTREE_DIR)):
            wt_path = os.path.join(WORKTREE_DIR, entry)
            if not os.path.isdir(wt_path):
                continue
            if not os.path.exists(os.path.join(wt_path, ".git")) and not os.path.isfile(os.path.join(wt_path, ".git")):
                continue

            task_id = entry
            task = tasks_by_id.get(task_id)

            # Determine if cleanable
            branch_ok, branch_name, _ = _git(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=wt_path, timeout=5
            )
            if not branch_ok:
                # Corrupted worktree — force remove
                clean_ok, clean_msg = _remove_worktree(task_id)
                if clean_ok:
                    removed.append({"task_id": task_id, "branch": "corrupt", "reason": "corrupted"})
                else:
                    errors.append(f"{task_id}: {clean_msg}")
                continue

            # Commits ahead
            base = task.get("git_base_branch", current_branch) if task else current_branch
            ahead_ok, ahead_out, _ = _git(
                ["git", "rev-list", "--count", f"{base}..HEAD"], cwd=wt_path, timeout=5
            )
            commits_ahead = 0
            if ahead_ok:
                try:
                    commits_ahead = int(ahead_out.strip())
                except ValueError:
                    commits_ahead = 0

            # Check if already merged
            anc_ok, _, _ = _git(
                ["git", "merge-base", "--is-ancestor", branch_name, current_branch],
                cwd=REPO_ROOT, timeout=5
            )

            should_remove = False
            reason = ""
            if not task:
                should_remove = True
                reason = "orphaned (no task in DB)"
            elif commits_ahead == 0:
                should_remove = True
                reason = "no commits ahead"
            elif anc_ok:
                should_remove = True
                reason = "already merged into current branch"
            elif task.get("status") == "done" and task.get("git_in_dev", 0) == 1:
                should_remove = True
                reason = "task done + merged"

            if should_remove:
                clean_ok, clean_msg = _remove_worktree(task_id)
                if clean_ok:
                    # Also try to delete the branch
                    if branch_name != "unknown":
                        _git(["git", "branch", "-d", branch_name])
                    removed.append({
                        "task_id": task_id,
                        "branch": branch_name,
                        "reason": reason,
                    })
                else:
                    errors.append(f"{task_id}: {clean_msg}")

        handler.send_response(200)
        handler.send_header("Content-Type", "application/json; charset=utf-8")
        handler.end_headers()
        handler.wfile.write(json.dumps({
            "success": True,
            "removed": removed,
            "removed_count": len(removed),
            "errors": errors,
            "message": f"{len(removed)} worktrees eliminados" + (f", {len(errors)} errores" if errors else ""),
        }, ensure_ascii=False).encode("utf-8"))

    else:
        handler.send_response(404)
        handler.end_headers()
