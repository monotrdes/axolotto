#!/usr/bin/env python3
"""route_handlers/get_routes.py — All GET route handlers."""
import concurrent.futures
import json, os, subprocess, sys, time, urllib.request, urllib.error, urllib.parse
from db import read_tasks, REPO_ROOT, CURRENT_DIR
from agent_runner import get_agent_status, _read_log_tail, AGENT_LOG_DIR, safe_git_run, get_current_git_branch, now_iso, _git, WORKTREE_DIR, _worktree_path
# Imported lazily to avoid circular import
_run_usage_command = None

def _get_run_usage_command():
    global _run_usage_command
    if _run_usage_command is None:
        from routes import run_usage_command
        _run_usage_command = run_usage_command
    return _run_usage_command

def handle_get(handler, path, query):
    """Dispatch GET request to the appropriate handler."""
    parsed_url = urllib.parse.urlparse(handler.path)
    path = parsed_url.path
    query = urllib.parse.parse_qs(parsed_url.query)

    # GET /api/health-proxy — proxy request to backend health endpoint to avoid CORS issues
    if path == "/api/health-proxy":
        try:
            with urllib.request.urlopen("http://localhost:8001/api/v1/health", timeout=2) as response:
                status = response.getcode()
                body = response.read().decode('utf-8')
            handler.send_response(status)
            handler.send_header("Content-Type", "application/json; charset=utf-8")
            handler.end_headers()
            handler.wfile.write(body.encode('utf-8'))
        except Exception as e:
            handler.send_response(502)
            handler.send_header("Content-Type", "application/json; charset=utf-8")
            handler.end_headers()
            handler.wfile.write(json.dumps({"online": False, "error": str(e)}, ensure_ascii=False).encode('utf-8'))
        return

    # GET /api/docs — list all .md files under docs/
    if path == "/api/docs":
        docs_dir = os.path.join(REPO_ROOT, "docs")
        files = []
        if os.path.isdir(docs_dir):
            for root, dirs, fnames in os.walk(docs_dir):
                # Skip hidden dirs
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                for fname in sorted(fnames):
                    if fname.endswith(".md"):
                        full = os.path.join(root, fname)
                        rel  = os.path.relpath(full, REPO_ROOT).replace("\\", "/")
                        stat = os.stat(full)
                        files.append({
                            "path": rel,
                            "name": fname,
                            "folder": os.path.relpath(root, docs_dir).replace("\\", "/"),
                            "size": stat.st_size,
                            "mtime": stat.st_mtime,
                        })
        files.sort(key=lambda f: f["mtime"], reverse=True)
        handler.send_response(200)
        handler.send_header("Content-Type", "application/json; charset=utf-8")
        handler.end_headers()
        handler.wfile.write(json.dumps({"files": files}, ensure_ascii=False).encode("utf-8"))
        return

    # GET /api/docs/content?path=docs/foo.md — return file content
    elif path == "/api/docs/content":
        rel_path = query.get("path", [None])[0]
        if not rel_path:
            handler.send_response(400); handler.end_headers(); return
        # Security: must stay inside REPO_ROOT/docs
        abs_path = os.path.normpath(os.path.join(REPO_ROOT, rel_path))
        docs_dir = os.path.normpath(os.path.join(REPO_ROOT, "docs"))
        if not abs_path.startswith(docs_dir) or not abs_path.endswith(".md"):
            handler.send_response(403); handler.end_headers(); return
        if not os.path.isfile(abs_path):
            handler.send_response(404); handler.end_headers(); return
        try:
            content = open(abs_path, encoding="utf-8", errors="replace").read()
        except Exception:
            handler.send_response(500); handler.end_headers(); return
        handler.send_response(200)
        handler.send_header("Content-Type", "application/json; charset=utf-8")
        handler.end_headers()
        handler.wfile.write(json.dumps({"path": rel_path, "content": content}, ensure_ascii=False).encode("utf-8"))
        return

    # GET /api/tasks
    if path == "/api/tasks":
        handler.send_response(200)
        handler.send_header("Content-Type", "application/json; charset=utf-8")
        handler.end_headers()
        tasks_data = read_tasks()
        for t in tasks_data["tasks"]:
            if t.get("status") == "doing":
                t["_agent_status"] = "manual"
                t["_agent_elapsed"] = 0
                t["_agent_elapsed_human"] = "manual"
                t["_agent_log_tail"] = ""
                t["_queue_position"] = 0
        handler.wfile.write(json.dumps(tasks_data, ensure_ascii=False).encode('utf-8'))
        return

    # GET /api/context-status — check context freshness
    elif path == "/api/context-status":
        from project_context import load_cached, CONTEXT_CACHE_TTL_SECONDS
        import time as _time
        scopes = ["axolotto", "taskboard"]
        statuses = []
        for s in scopes:
            cached = load_cached(s)
            cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".context_cache")
            path_ = os.path.join(cache_dir, f"{s}.txt")
            if os.path.exists(path_):
                age = _time.time() - os.path.getmtime(path_)
                ttl = CONTEXT_CACHE_TTL_SECONDS
                statuses.append({
                    "scope": s, "exists": True,
                    "age_seconds": round(age),
                    "age_human": f"{int(age // 3600)}h {int((age % 3600) // 60)}m",
                    "ttl_seconds": ttl,
                    "stale": age > ttl,
                    "size_chars": len(cached) if cached else 0,
                    "lines": cached.count('\n') if cached else 0,
                    "recommend_refresh": age > (ttl * 0.5),
                })
            else:
                statuses.append({"scope": s, "exists": False, "stale": True, "recommend_refresh": True})
        try:
            git_log = subprocess.run(
                ["git", "log", "--oneline", "--since=24 hours ago", "--no-decorate"],
                cwd=REPO_ROOT, capture_output=True, text=True, timeout=3
            )
            recent = len([l for l in git_log.stdout.strip().split('\n') if l]) if git_log.returncode == 0 else 0
        except Exception:
            recent = 0
        result = {
            "scopes": statuses,
            "any_stale": any(s["stale"] for s in statuses),
            "any_recommend": any(s.get("recommend_refresh", False) for s in statuses),
            "recent_git_commits_24h": recent,
            "recommend_refresh": any(s.get("recommend_refresh", False) for s in statuses) or recent > 3,
            "recommend_reasons": [],
        }
        if any(s.get("recommend_refresh", False) for s in statuses):
            result["recommend_reasons"].append("context_cache_older_than_12h")
        if recent > 3:
            result["recommend_reasons"].append(f"high_git_activity ({recent} commits in 24h)")
        handler.send_response(200)
        handler.send_header("Content-Type", "application/json; charset=utf-8")
        handler.end_headers()
        handler.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
        return

    # GET /api/usage
    elif path == "/api/usage":
        handler.send_response(200)
        handler.send_header("Content-Type", "application/json; charset=utf-8")
        handler.end_headers()
        results = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = {
                executor.submit(_get_run_usage_command(), name): name
                for name in ("claude", "deepclaude", "agy")
            }
            for future in concurrent.futures.as_completed(futures):
                data = future.result()
                results[data.get("provider", futures[future])] = data
        results["refreshed_at"] = now_iso()
        handler.wfile.write(json.dumps(results, ensure_ascii=False).encode('utf-8'))
        return

    # GET /api/agent-status/<task_id>
    elif path.startswith("/api/agent-status/"):
        task_id = path.split("/api/agent-status/")[-1]
        agent = get_agent_status(task_id)
        handler.send_response(200)
        handler.send_header("Content-Type", "application/json; charset=utf-8")
        handler.end_headers()
        if agent:
            handler.wfile.write(json.dumps(agent, ensure_ascii=False).encode('utf-8'))
        else:
            handler.wfile.write(json.dumps({
                "task_id": task_id, "running": False, "status": "idle"
            }, ensure_ascii=False).encode('utf-8'))
        return

    # GET /api/agent-log/<task_id>?lines=50
    elif path.startswith("/api/agent-log/"):
        task_id = path.split("/api/agent-log/")[-1]
        lines = int(query.get("lines", [50])[0])
        log_path = os.path.join(AGENT_LOG_DIR, f"{task_id}.log")
        log_tail = _read_log_tail(log_path, lines)
        log_exists = os.path.exists(log_path)
        log_size = os.path.getsize(log_path) if log_exists else 0

        handler.send_response(200)
        handler.send_header("Content-Type", "application/json; charset=utf-8")
        handler.end_headers()
        handler.wfile.write(json.dumps({
            "task_id": task_id,
            "log_path": log_path,
            "log_exists": log_exists,
            "log_size": log_size,
            "log_tail": log_tail,
            "lines_requested": lines,
        }, ensure_ascii=False).encode('utf-8'))
        return

    # GET /api/tasks/diff
    elif path == "/api/tasks/diff":
        task_id = query.get("id", [None])[0]
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

        branch = task.get("git_branch", "")
        base = task.get("git_base_branch", "develop")

        diff_cmd = f"git diff {base}...{branch}" if branch else "git diff"
        ok, stdout, stderr = safe_git_run(diff_cmd)

        if not ok or not stdout:
            ok, stdout, stderr = safe_git_run("git diff")

        handler.send_response(200)
        handler.send_header("Content-Type", "application/json; charset=utf-8")
        handler.end_headers()
        handler.wfile.write(json.dumps({
            "success": ok,
            "diff": stdout if ok else f"No se pudo generar diff: {stderr}"
        }, ensure_ascii=False).encode('utf-8'))
        return

    # GET /api/agents — agent availability (display only, no auto-execution)
    elif path == "/api/agents":
        handler.send_response(200)
        handler.send_header("Content-Type", "application/json; charset=utf-8")
        handler.end_headers()
        import shutil
        agents_out = {}

        # Determine active plan: last_used > gateway > available providers
        active_plan = 'B'  # default: assume Claude via REST
        try:
            from ai_router import AIRouter
            if not getattr(AIRouter, '_registry', None):
                AIRouter.initialize()
            providers = AIRouter._providers if hasattr(AIRouter, '_providers') else {}

            # 1. Check agy gateway first (Plan A)
            try:
                from agy_client import agy_client
                if agy_client and agy_client.gateway_available:
                    active_plan = 'A'
            except Exception:
                pass

            # 2. _last_used_provider is the TRUTH — it tells us which provider actually worked
            if active_plan != 'A':
                try:
                    last = AIRouter.get_last_provider() if hasattr(AIRouter, 'get_last_provider') else None
                    if last:
                        lp = last[0]  # provider name: claude, deepclaude, ollama
                        lm = last[1] if len(last) > 1 else ''  # model name
                        pmap = {'claude': 'B', 'deepclaude': 'B', 'deepseek': 'B', 'ollama': 'B', 'gemini': 'A', 'agy': 'A'}
                        active_plan = pmap.get(lp, 'B')
                except Exception:
                    pass

            # 3. If still no clue, find first available provider in chain
            if active_plan == 'B':  # default, not confirmed by gateway or last_used
                # Check providers in order: deepclaude > claude > ollama
                for pkey, plan in [('deepclaude', 'B'), ('claude', 'B'), ('ollama', 'B')]:
                    p = providers.get(pkey)
                    if p and getattr(p, 'available', False):
                        active_plan = plan
                        break
        except Exception:
            pass

        # 4. Determine active provider name and model for display
        active_provider = ""
        active_model = ""
        plan_provider_info = {
            'A': ('gemini', 'Gemini 3.5 Flash'),
            'B': ('chat', 'Chat IA (Claude / DeepSeek / Ollama)'),
        }
        if active_plan in plan_provider_info:
            active_provider, active_model = plan_provider_info[active_plan]

        for name in ("claude", "deepclaude", "agy"):
            binary_ok = shutil.which(name) is not None
            # Check actual provider availability
            provider_available = binary_ok
            try:
                if name == "claude":
                    from ai_router import AIRouter
                    cp = AIRouter._providers.get("claude") if hasattr(AIRouter, '_providers') else None
                    provider_available = cp.available if cp else binary_ok
                elif name == "deepclaude":
                    from ai_router import AIRouter
                    dp = AIRouter._providers.get("deepseek") if hasattr(AIRouter, '_providers') else None
                    provider_available = dp.available if dp else binary_ok
                elif name == "agy":
                    # Check both binary and agy_client gateway
                    try:
                        from agy_client import agy_client
                        provider_available = agy_client.gateway_available if agy_client else binary_ok
                    except Exception:
                        provider_available = binary_ok
            except Exception:
                pass

            agents_out[name] = {
                "pane": name,
                "busy": False,
                "current_task": None,
                "available": provider_available,
                "binary_installed": binary_ok,
                "log_tail": "",
                "active_model": "",
                "active_stage": "",
            }
        # Read active AI calls from AIRouter
        active_calls = {}
        try:
            from ai_router import AIRouter
            if hasattr(AIRouter, '_active_calls') and AIRouter._active_calls:
                active_calls = AIRouter._active_calls
        except Exception:
            pass

        # Build active_ai list and update agent busy states
        active_ai_list = []
        for task_id, call_info in active_calls.items():
            provider_name = call_info.get("provider", "")
            model_name = call_info.get("model", "")
            stage = call_info.get("stage", "")
            started_at = call_info.get("started_at", 0)

            # Map provider to agent key
            agent_key = provider_name
            if provider_name == "deepseek":
                agent_key = "deepclaude"
            elif provider_name == "gemini":
                agent_key = "agy"

            active_ai_list.append({
                "task_id": task_id,
                "agent": agent_key,
                "provider": provider_name,
                "model": model_name,
                "stage": stage,
                "started_at": started_at,
            })

            # Update agent busy state
            if agent_key in agents_out:
                agents_out[agent_key]["busy"] = True
                agents_out[agent_key]["current_task"] = task_id
                agents_out[agent_key]["active_model"] = model_name
                agents_out[agent_key]["active_stage"] = stage

        response = {
            "session_alive": True,
            "active_ai": active_ai_list,
            "active_plan": active_plan,
            "active_provider": active_provider,
            "active_model": active_model,
            "gateway_status": "connected" if active_plan == 'A' else "disconnected",
            "plan_chain": ["A: Gemini 3.5 Flash (agy gateway)", "B: Chat IA (Claude, DeepSeek, Ollama)"],
            "agents": agents_out,
        }
        handler.wfile.write(json.dumps(response, ensure_ascii=False).encode("utf-8"))
        return

    # GET /api/git — repo info
    elif path == "/api/git":
        handler.send_response(200)
        handler.send_header("Content-Type", "application/json; charset=utf-8")
        handler.end_headers()
        branch = get_current_git_branch()
        _, status_out, _ = safe_git_run("git status --porcelain")
        dirty = bool(status_out.strip())
        uncommitted_lines = [l for l in status_out.splitlines() if l.strip()]
        uncommitted_count = len(uncommitted_lines)
        _, ahead_out, _ = safe_git_run(
            f"git rev-list --count @{{u}}..HEAD 2>/dev/null || echo 0"
        )
        try:
            ahead = int(ahead_out.strip())
        except (ValueError, AttributeError):
            ahead = 0
        handler.wfile.write(json.dumps({
            "branch": branch,
            "dirty": dirty,
            "uncommitted_count": uncommitted_count,
            "ahead": ahead,
        }, ensure_ascii=False).encode("utf-8"))
        return

    # GET /api/git/worktrees — worktree health dashboard data
    elif path == "/api/git/worktrees":
        import datetime as _dt
        handler.send_response(200)
        handler.send_header("Content-Type", "application/json; charset=utf-8")
        handler.end_headers()

        tasks_data = read_tasks()
        tasks_by_id = {t["id"]: t for t in tasks_data.get("tasks", [])}
        current_branch = get_current_git_branch()

        worktrees = []
        if os.path.isdir(WORKTREE_DIR):
            for entry in sorted(os.listdir(WORKTREE_DIR)):
                wt_path = os.path.join(WORKTREE_DIR, entry)
                if not os.path.isdir(wt_path):
                    continue
                if not os.path.exists(os.path.join(wt_path, ".git")):
                    # Might be a git worktree file (points to main repo)
                    if not os.path.isfile(os.path.join(wt_path, ".git")):
                        continue

                task_id = entry  # worktree dirs are named by task_id
                task = tasks_by_id.get(task_id)

                # Determine branch
                branch_ok, branch_name, _ = _git(
                    ["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=wt_path, timeout=5
                )
                if not branch_ok:
                    branch_name = "unknown"

                # Commits ahead of base branch
                base = task.get("git_base_branch", current_branch) if task else current_branch
                commits_ahead = 0
                ahead_ok, ahead_out, _ = _git(
                    ["git", "rev-list", "--count", f"{base}..HEAD"], cwd=wt_path, timeout=5
                )
                if ahead_ok:
                    try:
                        commits_ahead = int(ahead_out.strip())
                    except ValueError:
                        commits_ahead = 0

                # Days since last commit
                days_since = None
                last_ok, last_out, _ = _git(
                    ["git", "log", "-1", "--format=%ct", "HEAD"], cwd=wt_path, timeout=5
                )
                if last_ok and last_out.strip():
                    try:
                        last_ts = int(last_out.strip())
                        days_since = (_dt.datetime.now(_dt.timezone.utc).timestamp() - last_ts) / 86400
                    except (ValueError, OSError):
                        pass

                # Check if mergeable (merge-base is ancestor of current branch)
                is_ancestor = False
                if branch_name != "unknown":
                    anc_ok, _, _ = _git(
                        ["git", "merge-base", "--is-ancestor",
                         branch_name, current_branch],
                        cwd=REPO_ROOT, timeout=5
                    )
                    # Branches are already merged if ancestor check fails
                    # Actually: is_ancestor checks if branch_name is ancestor of current_branch
                    # If branch features ARE already in current branch, it's already merged!
                    # We want: mergeable = commits exist AND branch tip is NOT ancestor of current
                    is_ancestor = anc_ok

                # Classification
                if not task:
                    status = "orphaned"
                elif commits_ahead == 0:
                    status = "no_commits"
                elif is_ancestor:
                    status = "merged"
                elif days_since is not None and days_since > 7:
                    status = "stale"
                else:
                    # Check if merge-base is ancestor of branch (clean merge possible)
                    mb_ok, merge_base, _ = _git(
                        ["git", "merge-base", current_branch, branch_name],
                        cwd=REPO_ROOT, timeout=5
                    )
                    if mb_ok and merge_base.strip():
                        # Branch is built on top of current — clean merge
                        status = "mergeable"
                    else:
                        status = "conflicts"

                worktrees.append({
                    "task_id": task_id,
                    "path": wt_path,
                    "branch": branch_name,
                    "commits_ahead": commits_ahead,
                    "base_branch": base,
                    "days_since_last_commit": round(days_since, 1) if days_since is not None else None,
                    "status": status,
                    "git_in_dev": task.get("git_in_dev", 1) if task else 0,
                    "task_status": task.get("status", "unknown") if task else "unknown",
                })

        # Summaries
        mergeable_count = sum(1 for w in worktrees if w["status"] == "mergeable")
        conflict_count = sum(1 for w in worktrees if w["status"] == "conflicts")
        no_commits_count = sum(1 for w in worktrees if w["status"] == "no_commits")
        stale_count = sum(1 for w in worktrees if w["status"] == "stale")
        orphaned_count = sum(1 for w in worktrees if w["status"] == "orphaned")
        merged_count = sum(1 for w in worktrees if w["status"] == "merged")
        cleanable_count = no_commits_count + orphaned_count + merged_count

        # Unmerged branches (from git branch list)
        unmerged_branches = []
        br_ok, br_out, _ = _git(
            ["git", "branch", "--list", "task/task-*", "--no-merged", current_branch],
            timeout=5
        )
        if br_ok and br_out.strip():
            unmerged_branches = [b.strip().lstrip("* ") for b in br_out.splitlines() if b.strip()]

        _, status_out, _ = safe_git_run("git status --porcelain")
        repo_dirty = bool(status_out.strip())

        handler.wfile.write(json.dumps({
            "worktree_count": len(worktrees),
            "worktrees": worktrees,
            "mergeable_count": mergeable_count,
            "conflict_count": conflict_count,
            "cleanable_count": cleanable_count,
            "no_commits_count": no_commits_count,
            "stale_count": stale_count,
            "orphaned_count": orphaned_count,
            "merged_count": merged_count,
            "unmerged_branches": unmerged_branches,
            "unmerged_branch_count": len(unmerged_branches),
            "repo_dirty": repo_dirty,
            "current_branch": current_branch,
        }, ensure_ascii=False).encode("utf-8"))
        return

    # GET /api/server/status — production server health check
    elif path == "/api/server/status":
        health_url = os.environ.get(
            "AXO_PROD_HEALTH_URL",
            "http://192.168.100.15:8001/api/v1/health",
        )
        try:
            req = urllib.request.Request(
                health_url,
                headers={"User-Agent": "AxolottoTaskboard/1.0"},
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                body = json.loads(resp.read().decode("utf-8"))
                handler.send_response(200)
                handler.send_header("Content-Type", "application/json; charset=utf-8")
                handler.end_headers()
                handler.wfile.write(json.dumps({
                    "online": True,
                    "status_code": resp.status,
                    "health": body,
                    "checked_at": now_iso(),
                }, ensure_ascii=False).encode("utf-8"))
                return
        except urllib.error.HTTPError as e:
            handler.send_response(200)
            handler.send_header("Content-Type", "application/json; charset=utf-8")
            handler.end_headers()
            handler.wfile.write(json.dumps({
                "online": False,
                "status_code": e.code,
                "error": f"HTTP {e.code}",
                "checked_at": now_iso(),
            }, ensure_ascii=False).encode("utf-8"))
            return
        except Exception as e:
            handler.send_response(200)
            handler.send_header("Content-Type", "application/json; charset=utf-8")
            handler.end_headers()
            handler.wfile.write(json.dumps({
                "online": False,
                "error": str(e),
                "checked_at": now_iso(),
            }, ensure_ascii=False).encode("utf-8"))
            return

    # GET /api/server/info — collect git+docker+pm2 status from production via SSH
    elif path == "/api/server/info":
        host = os.environ.get("AXO_PROD_HOST", "192.168.100.15")
        # Run a lightweight info-collection script on the NUC
        remote_script = (
            "cd ~/axolotto && "
            "echo '---GIT---' && git log --oneline -5 && "
            "echo '---BRANCH---' && git rev-parse --abbrev-ref HEAD && "
            "echo '---DIRTY---' && (git status --porcelain | head -5) && "
            "echo '---DOCKER---' && docker ps --format '{{.Names}}|{{.Status}}' 2>/dev/null && "
            "echo '---PM2---' && pm2 jlist 2>/dev/null"
        )
        try:
            result = subprocess.run(
                ["ssh", "-o", "StrictHostKeyChecking=accept-new",
                 "-o", "ConnectTimeout=5", host, remote_script],
                capture_output=True, text=True,
                encoding="utf-8", errors="replace",
                timeout=10,
            )
            output = result.stdout or ""

            # Parse sections
            sections = {}
            current = None
            for line in output.splitlines():
                if line.startswith("---") and line.endswith("---"):
                    current = line.strip("-").strip()
                    sections[current] = []
                elif current:
                    sections[current].append(line)

            # Parse GIT
            git_commits = [l.strip() for l in sections.get("GIT", []) if l.strip()]
            git_branch = ""
            git_dirty = False
            if sections.get("BRANCH"):
                git_branch = sections["BRANCH"][0].strip() if sections["BRANCH"] else ""
            if sections.get("DIRTY"):
                git_dirty = any(l.strip() for l in sections["DIRTY"])

            # Parse DOCKER
            docker_containers = []
            for line in sections.get("DOCKER", []):
                if "|" in line:
                    name, status = line.split("|", 1)
                    if "axolotto" in name.lower():
                        docker_containers.append({"name": name.strip(), "status": status.strip()})

            # Parse PM2
            pm2_procs = []
            try:
                raw_pm2 = "\n".join(sections.get("PM2", []))
                if raw_pm2.strip():
                    pm2_data = json.loads(raw_pm2)
                    for p in pm2_data:
                        if "axolotto" in p.get("name", "").lower():
                            pm2_procs.append({
                                "name": p.get("name", ""),
                                "status": p.get("pm2_env", {}).get("status", "unknown"),
                                "uptime": p.get("pm2_env", {}).get("pm_uptime", 0),
                                "memory": p.get("monit", {}).get("memory", 0),
                            })
            except (json.JSONDecodeError, Exception):
                pass

            handler.send_response(200)
            handler.send_header("Content-Type", "application/json; charset=utf-8")
            handler.end_headers()
            handler.wfile.write(json.dumps({
                "online": True,
                "git": {
                    "branch": git_branch,
                    "commits": git_commits,
                    "dirty": git_dirty,
                },
                "docker": docker_containers,
                "pm2": pm2_procs,
                "checked_at": now_iso(),
            }, ensure_ascii=False).encode("utf-8"))
            return
        except Exception as e:
            handler.send_response(200)
            handler.send_header("Content-Type", "application/json; charset=utf-8")
            handler.end_headers()
            handler.wfile.write(json.dumps({
                "online": False,
                "error": str(e),
                "checked_at": now_iso(),
            }, ensure_ascii=False).encode("utf-8"))
            return

    # GET /api/docs — list markdown files in docs/
    elif path == "/api/docs":
        docs_dir = os.path.join(REPO_ROOT, "docs")
        if not os.path.exists(docs_dir):
            os.makedirs(docs_dir, exist_ok=True)
        
        files_list = []
        for root, dirs, files in os.walk(docs_dir):
            for file in files:
                if file.endswith(".md"):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, docs_dir)
                    # Normalize path separators for frontend URL/display consistency
                    rel_path = rel_path.replace("\\", "/")
                    
                    # Find the folder name relative to docs_dir
                    rel_dir = os.path.relpath(root, docs_dir)
                    folder = rel_dir.replace("\\", "/") if rel_dir != "." else "."
                    
                    size = os.path.getsize(full_path)
                    mtime = os.path.getmtime(full_path)
                    
                    files_list.append({
                        "name": file,
                        "path": rel_path,
                        "folder": folder,
                        "size": size,
                        "mtime": mtime
                    })
        
        # Sort alphabetically by path
        files_list.sort(key=lambda x: x["path"].lower())
        
        handler.send_response(200)
        handler.send_header("Content-Type", "application/json; charset=utf-8")
        handler.end_headers()
        handler.wfile.write(json.dumps({"files": files_list}, ensure_ascii=False).encode('utf-8'))
        return

    # GET /api/docs/content — get content of a single markdown file
    elif path == "/api/docs/content":
        file_name = query.get("path", [None])[0]
        if not file_name:
            handler.send_response(400)
            handler.send_header("Content-Type", "application/json; charset=utf-8")
            handler.end_headers()
            handler.wfile.write(json.dumps({"error": "Falta el parámetro 'path'"}, ensure_ascii=False).encode('utf-8'))
            return
        
        # Prevent directory traversal
        if ".." in file_name or file_name.startswith("/"):
            handler.send_response(400)
            handler.send_header("Content-Type", "application/json; charset=utf-8")
            handler.end_headers()
            handler.wfile.write(json.dumps({"error": "Nombre de archivo inválido"}, ensure_ascii=False).encode('utf-8'))
            return
        
        docs_dir = os.path.abspath(os.path.join(REPO_ROOT, "docs"))
        target_path = os.path.abspath(os.path.join(docs_dir, file_name))
        if not target_path.startswith(docs_dir):
            handler.send_response(403)
            handler.send_header("Content-Type", "application/json; charset=utf-8")
            handler.end_headers()
            handler.wfile.write(json.dumps({"error": "Acceso denegado"}, ensure_ascii=False).encode('utf-8'))
            return
        
        if not os.path.exists(target_path) or not os.path.isfile(target_path):
            handler.send_response(404)
            handler.send_header("Content-Type", "application/json; charset=utf-8")
            handler.end_headers()
            handler.wfile.write(json.dumps({"error": "Archivo no encontrado"}, ensure_ascii=False).encode('utf-8'))
            return
        
        try:
            with open(target_path, "r", encoding="utf-8") as f:
                content = f.read()
            handler.send_response(200)
            handler.send_header("Content-Type", "application/json; charset=utf-8")
            handler.end_headers()
            handler.wfile.write(json.dumps({"content": content, "path": file_name}, ensure_ascii=False).encode('utf-8'))
        except Exception as e:
            handler.send_response(500)
            handler.send_header("Content-Type", "application/json; charset=utf-8")
            handler.end_headers()
            handler.wfile.write(json.dumps({"error": f"Error al leer archivo: {str(e)}"}, ensure_ascii=False).encode('utf-8'))
        return

    # Serve static files
    if path == "/":
        path = "/index.html"

    file_path = os.path.normpath(os.path.join(CURRENT_DIR, path.lstrip("/")))
    if not file_path.startswith(CURRENT_DIR):
        handler.send_error(403, "Access Denied")
        return

    if os.path.exists(file_path) and os.path.isfile(file_path):
        content_type = "text/plain"
        if file_path.endswith(".html"):
            content_type = "text/html; charset=utf-8"
        elif file_path.endswith(".css"):
            content_type = "text/css; charset=utf-8"
        elif file_path.endswith(".js"):
            content_type = "application/javascript; charset=utf-8"
        elif file_path.endswith(".json"):
            content_type = "application/json; charset=utf-8"
        elif file_path.endswith(".svg"):
            content_type = "image/svg+xml"

        handler.send_response(200)
        handler.send_header("Content-Type", content_type)
        handler.end_headers()
        with open(file_path, 'rb') as f:
            handler.wfile.write(f.read())
    else:
        handler.send_error(404, "File Not Found")

# ── POST ───────────────────────────────────────────────────────────
