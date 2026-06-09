#!/usr/bin/env python3
from __future__ import annotations
"""HTTP routes for Axolotto Kanban Taskboard Server.

Thin entrypoint that delegates to modular components:
  db.py         — database layer
  agent_runner.py  — agent execution, queue, worktree
  task_lifecycle.py — task state machine, AI triggers
  ai_router.py  — AI provider routing
  rate_limiter.py  — rate limit tracking
"""

import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.parse
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn

# Local imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from db import init_db, CURRENT_DIR, REPO_ROOT
from agent_runner import _git

PORT = 8181
PIDFILE = os.path.join(CURRENT_DIR, ".taskboard.pid")


# ── Helpers ────────────────────────────────────────────────────────────────

def load_dotenv():
    dotenv_path = os.path.join(REPO_ROOT, ".env")
    if os.path.exists(dotenv_path):
        try:
            with open(dotenv_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, val = line.split("=", 1)
                        val = val.strip().strip('"').strip("'")
                        os.environ[key.strip()] = val
        except Exception as e:
            print(f"Error loading .env file: {e}", file=sys.stderr)

load_dotenv()


# ── Usage parsing ──────────────────────────────────────────────────────────

def parse_usage_output(text: str) -> dict:
    """Parse output of `claude /usage` or `deepclaude /usage` into structured dict."""
    data = {
        "total_cost": None,
        "total_cost_usd": None,
        "duration_api_seconds": None,
        "duration_wall_seconds": None,
        "lines_added": None,
        "lines_removed": None,
        "tokens_input": None,
        "tokens_output": None,
        "tokens_cache_read": None,
        "tokens_cache_write": None,
        "quotas": [],
        "raw": text,
    }

    def _parse_duration(val: str) -> int | None:
        val = val.strip().lower()
        total = 0
        for part in val.split():
            part = part.strip()
            if part.endswith("h"):
                try: total += int(part[:-1]) * 3600
                except ValueError: pass
            elif part.endswith("m"):
                try: total += int(part[:-1]) * 60
                except ValueError: pass
            elif part.endswith("s"):
                try: total += int(part[:-1])
                except ValueError: pass
        return total if val else None

    # Parsear línea por línea para campos estándar
    lines = text.splitlines()
    for line in lines:
        line = line.strip()
        if not line:
            continue

        m = re.match(r'Total cost:\s*\$?([\d.]+)', line, re.IGNORECASE)
        if m:
            try:
                cost = float(m.group(1))
                data["total_cost_usd"] = cost
                data["total_cost"] = f"${cost:.4f}"
            except ValueError:
                pass
            continue

        m = re.match(r'Total duration\s*\(API\):\s*(.+)', line, re.IGNORECASE)
        if m:
            data["duration_api_seconds"] = _parse_duration(m.group(1))
            continue

        m = re.match(r'Total duration\s*\(wall\):\s*(.+)', line, re.IGNORECASE)
        if m:
            data["duration_wall_seconds"] = _parse_duration(m.group(1))
            continue

        m = re.match(r'Total code changes:\s*(\d+)\s*lines?\s*added,?\s*(\d+)\s*lines?\s*removed', line, re.IGNORECASE)
        if m:
            data["lines_added"] = int(m.group(1))
            data["lines_removed"] = int(m.group(2))
            continue

        m = re.match(r'Usage:\s*([\d,.]+)\s*input,?\s*([\d,.]+)\s*output,?\s*([\d,.]+)\s*cache\s*read,?\s*([\d,.]+)\s*cache\s*write', line, re.IGNORECASE)
        if m:
            try:
                data["tokens_input"] = int(m.group(1).replace(",", ""))
                data["tokens_output"] = int(m.group(2).replace(",", ""))
                data["tokens_cache_read"] = int(m.group(3).replace(",", ""))
                data["tokens_cache_write"] = int(m.group(4).replace(",", ""))
            except ValueError:
                pass
            continue

    # Parsear cuotas de modelos (ej. Gemini Model Quotas con barras de progreso)
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        # Detectar patrones de barras de progreso como '█████' o '░░░░░' y un porcentaje al final
        if ('█' in line or '░' in line or '▒' in line or '▓' in line or '■' in line) and re.search(r'\d+%', line):
            pct_match = re.search(r'(\d+)%', line)
            pct = int(pct_match.group(1)) if pct_match else 0
            
            # El nombre del modelo es la línea anterior
            model_name = "Unknown Model"
            if i > 0:
                model_name = lines[i-1].strip()
                # Limpiar viñetas o caracteres extra
                model_name = re.sub(r'^[•\-\*\s└├│\s]+', '', model_name)
            
            # La línea siguiente suele dar el detalle (ej. "40% remaining · Refreshes in 2h 42m")
            detail = ""
            if i + 1 < len(lines):
                next_line = lines[i+1].strip()
                if "remaining" in next_line.lower() or "refresh" in next_line.lower():
                    detail = next_line
                    i += 1  # Consumir la línea de detalle
            
            data["quotas"].append({
                "model": model_name,
                "percent": pct,
                "detail": detail
            })
        i += 1

    return data


def run_usage_command(binary_name: str) -> dict:
    """Return rate-limit / usage info WITHOUT spawning the full CLI binary.

    WARNING: Do NOT run `claude --print /usage` or PS1 wrappers — they can start
    full agent sessions that explore the codebase and leak output to the console.
    We use the rate tracker instead, which is safe and non-blocking.
    """
    # deepclaude is a PS1 wrapper — never execute it just for usage stats
    if binary_name == "deepclaude":
        return {
            "provider": binary_name,
            "available": True,
            "notice": "Usage via PS1 wrapper disabled (would spawn full Claude session). See /api/rates.",
            "exit_code": 0,
        }

    is_windows = sys.platform == "win32"
    binary_path = shutil.which(binary_name)
    if not binary_path and is_windows:
        paths_to_check = [
            os.path.expanduser(f"~/AppData/Local/{binary_name}/bin/{binary_name}.exe"),
            os.path.expanduser(f"~/AppData/Local/{binary_name}/bin/{binary_name}.cmd"),
        ]
        for p in paths_to_check:
            if os.path.isfile(p):
                binary_path = p
                break
    if not binary_path:
        binary_path = os.path.expanduser(f"~/.local/bin/{binary_name}")

    if not binary_path or not os.path.isfile(binary_path):
        return {
            "provider": binary_name,
            "available": False,
            "error": f"Binary '{binary_name}' not found",
        }

    # Only run direct executables (NOT PS1 wrappers which spawn full CLI sessions)
    if binary_path.lower().endswith(".ps1"):
        return {
            "provider": binary_name,
            "available": False,
            "error": "PS1 wrapper — usage not available (would spawn full agent session)",
        }

    # Try --help first (safe, quick, no API call)
    try:
        result = subprocess.run(
            [binary_path, "--help"],
            capture_output=True, text=True, timeout=10,
            cwd=REPO_ROOT,
            stdin=subprocess.DEVNULL,
            creationflags=0x08000000 if is_windows else 0,  # CREATE_NO_WINDOW
        )
        output = (result.stdout or result.stderr or "").strip()
        parsed = parse_usage_output(output)
        parsed["provider"] = binary_name
        parsed["available"] = result.returncode == 0
        parsed["exit_code"] = result.returncode
        return parsed
    except subprocess.TimeoutExpired:
        return {"provider": binary_name, "available": False, "error": "Timed out after 10s"}
    except Exception as e:
        return {"provider": binary_name, "available": False, "error": str(e)}


# ── HTTP Server ────────────────────────────────────────────────────────────

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True


class KanbanHandler(BaseHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, DELETE, PUT')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        try:
            super().end_headers()
        except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError):
            # Client disconnected — silently ignore
            pass

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    # ── GET ─────────────────────────────────────────────────────────

    def do_GET(self):
        try:
            self._do_get_impl()
        except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError):
            pass

    def _do_get_impl(self):
        from route_handlers.get_routes import handle_get
        import urllib.parse
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query = urllib.parse.parse_qs(parsed_url.query)
        handle_get(self, path, query)

    # ── POST ────────────────────────────────────────────────────────

    def do_POST(self):
        try:
            self._do_post_impl()
        except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError):
            pass

    def _do_post_impl(self):
        from route_handlers.post_routes import handle_post
        import urllib.parse, json
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        content_length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(content_length) if content_length > 0 else b"{}"
        try:
            post_data = raw.decode("utf-8")
        except UnicodeDecodeError:
            post_data = raw.decode("latin-1")
        try:
            body = json.loads(post_data)
        except json.JSONDecodeError:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode("utf-8"))
            return
        handle_post(self, path, body)


# ── Singleton guard ──────────────────────────────────────────────────────

def _acquire_singleton():
    """Refuse to start if another taskboard is already alive."""
    try:
        if os.path.exists(PIDFILE):
            try:
                with open(PIDFILE) as f:
                    old = int((f.read() or "0").strip() or 0)
            except (ValueError, OSError):
                old = 0
            if old and old != os.getpid():
                alive = True
                try:
                    os.kill(old, 0)
                except ProcessLookupError:
                    alive = False
                except PermissionError:
                    alive = True
                if alive:
                    print(
                        f"  ERROR: Taskboard ya está corriendo (PID {old}). "
                        "Aborto para evitar instancias duplicadas. "
                        f"Si es un pidfile obsoleto, borra {PIDFILE} y reintenta.",
                        file=sys.stderr,
                    )
                    sys.exit(1)
        with open(PIDFILE, "w") as f:
            f.write(str(os.getpid()))
        import atexit
        atexit.register(
            lambda: os.path.exists(PIDFILE) and os.remove(PIDFILE)
        )
    except SystemExit:
        raise
    except Exception as e:
        print(f"  Aviso: no se pudo gestionar el pidfile: {e}", file=sys.stderr)


# ── Startup worktree sweep ──────────────────────────────────────────────

def _sweep_worktrees_on_startup():
    """Scan WORKTREE_DIR on startup, auto-remove no_commits worktrees of done tasks."""
    import os as _os
    from agent_runner import WORKTREE_DIR, _remove_worktree, _git
    from db import read_tasks

    if not _os.path.isdir(WORKTREE_DIR):
        return

    tasks_data = read_tasks()
    tasks_by_id = {t["id"]: t for t in tasks_data.get("tasks", [])}
    removed = 0
    errors = 0

    for entry in sorted(_os.listdir(WORKTREE_DIR)):
        wt_path = _os.path.join(WORKTREE_DIR, entry)
        if not _os.path.isdir(wt_path):
            continue
        if not _os.path.exists(_os.path.join(wt_path, ".git")) and not _os.path.isfile(_os.path.join(wt_path, ".git")):
            continue

        task = tasks_by_id.get(entry)
        branch_ok, branch_name, _ = _git(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=wt_path, timeout=5
        )

        # Auto-remove: orphaned or no-commits on done tasks
        should_remove = False
        if not task:
            should_remove = True
        elif task.get("status") == "done" and task.get("git_in_dev", 0) == 1:
            # Commits ahead check
            ahead_ok, ahead_out, _ = _git(
                ["git", "rev-list", "--count",
                 f"{task.get('git_base_branch', 'develop')}..HEAD"],
                cwd=wt_path, timeout=5
            )
            commits_ahead = 0
            if ahead_ok:
                try:
                    commits_ahead = int(ahead_out.strip())
                except ValueError:
                    pass
            if commits_ahead == 0:
                should_remove = True

        if should_remove:
            clean_ok, _ = _remove_worktree(entry)
            if clean_ok:
                if branch_ok and branch_name != "unknown":
                    _git(["git", "branch", "-d", branch_name])
                removed += 1
            else:
                errors += 1

    if removed > 0 or errors > 0:
        print(f"  🧹 Startup sweep: {removed} worktrees eliminados" +
              (f", {errors} errores" if errors else ""))


# ── Entrypoint ───────────────────────────────────────────────────────────

def run_server():
    _acquire_singleton()
    init_db()
    _git(["git", "worktree", "prune"])

    # ── Startup: sweep stale worktrees ──────────────────────────────
    _sweep_worktrees_on_startup()

    server_address = ('', PORT)
    httpd = ThreadingHTTPServer(server_address, KanbanHandler)
    print(f"  Taskboard v6 iniciado en http://localhost:{PORT}")
    print(f"  Modo: Dashboard visual — agentes se ejecutan manualmente en terminal")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n  Apagando el servidor...")
        httpd.server_close()


if __name__ == '__main__':
    run_server()
