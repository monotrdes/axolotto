#!/usr/bin/env python3
from __future__ import annotations
"""AI Router — multi-provider AI integration for the Axolotto taskboard.

Uses CLI binaries (agy, claude) for AI processing instead of API keys.
agy authenticates via Google login (Pro account).
"""

import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rate_limiter import RateLimitTracker
from project_context import get_context as get_cached_project_context
from project_context import refresh as refresh_context_cache


def load_workspace_registry(config_path: str = None) -> dict:
    """Load the workspace.json registry. Returns the parsed JSON or a minimal default."""
    if config_path is None:
        candidates = [
            os.path.join(os.path.dirname(__file__), '..', '..', 'workspace.json'),
            os.path.join(os.path.dirname(__file__), 'workspace.json'),
        ]
        for c in candidates:
            if os.path.exists(c):
                config_path = c
                break
    if config_path and os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "routing": {"strategy": "weighted_scoring", "weights": {}, "fallback_chain": []},
        "specializations": {},
        "agent_mappings": {},
        "providers": {},
    }


rate_tracker = RateLimitTracker()
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


# ── System Prompts (español) ─────────────────────────────────────────────────

SYSTEM_CONCEPT = (
    "Eres un analista de producto experto. Tu tarea es convertir una idea o requerimiento "
    "descrito por el usuario en un título profesional resumido y un comentario inicial de alcance.\n\n"
    "Responde ÚNICAMENTE con un objeto JSON con las siguientes llaves:\n"
    '  "title": título profesional resumido (max 80 chars),\n'
    '  "initial_comment": comentario de alcance explicando qué implica la tarea (2-4 frases),\n'
    '  "category": "backend"|"frontend"|"bug"|"docs"|"tools"|"security"|"finance"|"gamedesign"|"blockchain"|"infra",\n'
    '  "priority": "high"|"medium"|"low".\n\n'
    "Sé conciso y preciso. No añadas texto fuera del JSON."
)

SYSTEM_PLANNING = (
    "Eres un arquitecto de software senior analizando un proyecto real. "
    "Vas a recibir una idea de tarea junto con contexto del proyecto "
    "(estructura de archivos, stack tecnológico).\n\n"
    "PRIMERO: Determina si esta idea es UNA sola tarea o necesita dividirse en MÚLTIPLES tareas.\n"
    "Una idea debe dividirse cuando:\n"
    "- Involucra cambios en backend Y frontend simultáneamente\n"
    "- Menciona \"y\" uniendo features independientes\n"
    "- Requiere trabajo en diferentes módulos o servicios\n\n"
    "Si es MÚLTIPLE, determina si las subtareas tienen dependencias secuenciales entre sí "
    "(por ejemplo, si la subtarea B depende de que la subtarea A se complete primero). Responde con:\n"
    '{\n'
    '  "is_multi": true,\n'
    '  "title": "título profesional para la tarea padre (max 80 chars)",\n'
    '  "subtasks": [\n'
    '    {"title": "...", "description": "...", "category": "backend|frontend|bug|docs|tools|security|finance|gamedesign|blockchain|infra",\n'
    '     "recommended_agent": "claude"|"deepclaude", "priority": "high|medium|low",\n'
    '     "depends_on_index": null|number (índice 0-based de la subtarea de la cual depende directamente en esta lista, o null si es independiente o la primera)}\n'
    '    ...\n'
    '  ]\n'
    '}\n\n'
    "Si es UNA sola tarea, analiza el flujo real del proyecto y entrega un PLAN COMPLETO:\n"
    "1. title: Título profesional y descriptivo para la tarjeta (max 80 chars). DEBE reflejar con precisión qué se va a hacer.\n"
    "2. Checklist de criterios de aceptación (4-8 items)\n"
    "3. Archivos concretos a crear/modificar (rutas reales del repo)\n"
    "4. Análisis de impacto arquitectónico (qué se toca y riesgos)\n"
    "5. Propuestas: ideas o mejoras adicionales que valga la pena considerar\n"
    "6. Recomendar agente AI:\n"
    '   - "claude": frontend, diseño, razonamiento\n'
    '   - "deepclaude": backend, bugs, análisis de código, planificación\n'
    "7. Notas de diseño técnico\n"
    "8. Guía de verificación paso a paso\n\n"
    '{"is_multi": false, "title": "título profesional (max 80 chars)",'
    ' "requirements": [{"id": "req-1", "text": "criterio"}, ...],'
    ' "files_to_modify": ["ruta/archivo.py", ...], "impact_analysis": "...",'
    ' "proposals": ["idea 1", "mejora 2"],'
    ' "recommended_agent": "claude"|"deepclaude", "design_notes": "...", "verification_guide": "..."}'
)

SYSTEM_REVIEW = (
    "Eres un revisor de código experto. Vas a recibir el diff de git de una tarea completada "
    "junto con el contexto de la tarea.\n\n"
    "Tu trabajo:\n"
    "1. Generar un resumen conciso de los cambios realizados\n"
    "2. Proporcionar instrucciones de prueba manuales (3-5 pasos)\n"
    "3. Identificar 2-4 edge cases o riesgos potenciales\n\n"
    "Responde ÚNICAMENTE con un objeto JSON:\n"
    '{"summary": "resumen de cambios", "test_instructions": "pasos para verificar", "edge_cases": ["caso 1", "caso 2"]}'
)


# ── Provider Implementations (CLI-based) ─────────────────────────────────────

class AIProvider:
    """Base class for AI providers using CLI binaries."""

    name: str = "base"
    gradient_class: str = "model-unassigned"
    binary: str = ""

    @staticmethod
    def _write_log(log_path: str | None, msg: str):
        """Append a timestamped message to the log file, if log_path is set."""
        if not log_path:
            return
        try:
            line = f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] {msg}"
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            with open(log_path, "a", encoding="utf-8") as lf:
                lf.write(line + "\n")
        except Exception:
            pass

    def __init__(self, strengths: list[str]):
        self.strengths = strengths
        self._binary_path = None
        self._last_rate_limit_msg = None

    def _find_binary(self) -> str | None:
        if self._binary_path:
            return self._binary_path
        path = shutil.which(self.binary) or os.path.expanduser(f"~/.local/bin/{self.binary}")
        if os.path.isfile(path) and os.access(path, os.X_OK):
            self._binary_path = path
            return path
        return None

    @property
    def available(self) -> bool:
        return self._find_binary() is not None and rate_tracker.is_available(self.name)

    def _parse_json_response(self, text: str) -> dict | None:
        text = text.strip()
        # 1. Extract from outermost markdown code block: ```json ... ```
        # Use rfind to get last ``` — JSON string values may contain nested ```
        if "```" in text:
            first_tick = text.find("```")
            last_tick = text.rfind("```")
            if first_tick != last_tick:
                inner = text[first_tick + 3:last_tick].strip()
                # Strip language tag like "json" from first line if present
                if not inner.startswith("{"):
                    nl = inner.find("\n")
                    if nl != -1:
                        inner = inner[nl + 1:].strip()
                if inner.startswith("{"):
                    text = inner
        # 2. Extract first JSON object if text has extra surrounding content
        if not text.startswith("{"):
            import re as _re
            m = _re.search(r'\{.*\}', text, _re.DOTALL)
            if m:
                text = m.group(0)
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return None

    def _run_cli(self, args: list[str], timeout: int, add_repo: bool = False,
                 extra_env: dict | None = None, log_path: str | None = None) -> str | None:
        binary = self._find_binary()
        if not binary:
            return None
        cmd = [binary] + args
        if add_repo:
            cmd += ["--add-dir", REPO_ROOT]
        cmd += ["--dangerously-skip-permissions"]
        env = os.environ.copy()
        if extra_env:
            env.update(extra_env)

        # Use Popen with streaming so we can write to log in real-time
        try:
            proc = subprocess.Popen(
                cmd, cwd=REPO_ROOT,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, env=env,
            )
        except FileNotFoundError:
            print(f"  {self.name} CLI: binary not found", file=sys.stderr)
            return None
        except Exception as e:
            print(f"  {self.name} CLI error: {e}", file=sys.stderr)
            rate_tracker.record_error(self.name, 500)
            return None

        # Read stdout/stderr in threads to avoid deadlocks
        stdout_chunks = []
        stderr_chunks = []

        def _read(stream, chunks, label):
            try:
                for line in iter(stream.readline, ""):
                    chunks.append(line)
                    if log_path and line.strip():
                        self._write_log(log_path, f"[{label}] {line.rstrip()}")
            except Exception:
                pass
            finally:
                stream.close()

        import threading
        t_out = threading.Thread(target=_read, args=(proc.stdout, stdout_chunks, "out"), daemon=True)
        t_err = threading.Thread(target=_read, args=(proc.stderr, stderr_chunks, "err"), daemon=True)
        t_out.start()
        t_err.start()

        try:
            proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            proc.kill()
            t_out.join(timeout=2)
            t_err.join(timeout=2)
            print(f"  {self.name} CLI: timeout after {timeout}s", file=sys.stderr)
            if log_path:
                self._write_log(log_path, f"⏰ Timeout después de {timeout}s — proceso cancelado")
            rate_tracker.record_error(self.name, 408)
            return None

        t_out.join(timeout=5)
        t_err.join(timeout=5)
        rate_tracker.record_call(self.name)

        stdout = "".join(stdout_chunks)
        stderr = "".join(stderr_chunks)

        # Write full raw output summary to log
        if log_path:
            if stdout.strip():
                self._write_log(log_path, f"─── RAW OUTPUT ({self.name}, {len(stdout)} chars) ───")
                for line in stdout.strip().splitlines()[-30:]:
                    self._write_log(log_path, f"  {line}")
                self._write_log(log_path, "─── END RAW OUTPUT ───")
            if stderr.strip():
                self._write_log(log_path, f"─── STDERR ({self.name}) ───")
                for line in stderr.strip().splitlines()[-20:]:
                    self._write_log(log_path, f"  {line}")

        if stdout:
            preview = stdout.strip()[:200].replace("\n", "\\n")
            print(f"  {self.name} CLI raw ({len(stdout)} chars): {preview}", file=sys.stderr)
        if stderr:
            print(f"  {self.name} CLI stderr: {stderr.strip()[:200]}", file=sys.stderr)

        # Detect rate limit / session limit in output
        combined = (stdout + " " + stderr).lower()
        if any(p in combined for p in ("session limit", "rate limit", "too many requests", "quota")):
            self._last_rate_limit_msg = (stdout or stderr).strip()[:200]
            if log_path:
                self._write_log(log_path, f"🚫 RATE LIMITED: {self._last_rate_limit_msg}")
            print(f"  {self.name} CLI: rate limited — {self._last_rate_limit_msg}", file=sys.stderr)
            rate_tracker.record_error(self.name, 429, cooldown_seconds=60)
            return None
        return stdout

    def call(self, model: str, system_prompt: str, user_prompt: str,
             response_json: bool = True, temperature: float = 0.3,
             timeout: int = 60) -> str | dict | None:
        raise NotImplementedError


class ClaudeProvider(AIProvider):
    """Anthropic Claude — CLI primary, API key fallback."""

    name = "claude"
    gradient_class = "model-claude"
    binary = "claude"

    def __init__(self):
        super().__init__(strengths=["frontend", "design", "reasoning", "planning", "review"])
        self.api_key = os.environ.get("ANTHROPIC_API_KEY", "")

    def call(self, model: str, system_prompt: str, user_prompt: str,
             response_json: bool = True, temperature: float = 0.3,
             timeout: int = 60, log_path: str | None = None) -> str | dict | None:

        # 1. Try CLI
        if self._find_binary():
            result = self._call_cli(system_prompt, user_prompt, response_json, timeout)
            if result is not None:
                return result

        # 2. Try API key
        if self.api_key:
            result = self._call_api(system_prompt, user_prompt, response_json, timeout)
            if result is not None:
                return result

        return None

    def _call_cli(self, system_prompt: str, user_prompt: str,
                  response_json: bool, timeout: int) -> str | dict | None:
        full = user_prompt
        if response_json:
            full += "\n\nIMPORTANTE: Responde ÚNICAMENTE con el JSON solicitado. Sin markdown ni texto extra."
        if system_prompt:
            full = f"SYSTEM: {system_prompt}\n\n---\n\n{full}"

        output = self._run_cli(["-p", full], timeout, add_repo=False)
        if output is None:
            return None
        if response_json:
            parsed = self._parse_json_response(output)
            return parsed if parsed is not None else None
        return output.strip()

    def _call_api(self, system_prompt: str, user_prompt: str,
                  response_json: bool, timeout: int) -> str | dict | None:
        if not self.api_key:
            return None
        sp = system_prompt
        if response_json:
            sp += "\n\nIMPORTANTE: Responde SOLO con el JSON, sin markdown ni texto adicional."

        payload = {
            "model": "claude-sonnet-4-20250514", "max_tokens": 4096,
            "system": sp, "messages": [{"role": "user", "content": user_prompt}],
            "temperature": 0.3,
        }
        try:
            req = urllib.request.Request(
                "https://api.anthropic.com/v1/messages",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json", "x-api-key": self.api_key,
                         "anthropic-version": "2023-06-01"}, method="POST")
            with urllib.request.urlopen(req, timeout=min(timeout, 30)) as resp:
                text = json.loads(resp.read().decode("utf-8"))["content"][0]["text"]
                rate_tracker.record_call(self.name)
                if response_json:
                    return self._parse_json_response(text)
                return text
        except urllib.error.HTTPError as e:
            if e.code == 429:
                rate_tracker.record_error(self.name, 429, cooldown_seconds=60)
            return None
        except Exception as e:
            print(f"  Claude API error: {e}", file=sys.stderr)
            return None


class DeepClaudeProvider(AIProvider):
    """DeepSeek models via the claude CLI with DeepSeek API env vars.

    Uses the same claude binary but with ANTHROPIC_BASE_URL pointing to
    DeepSeek's Anthropic-compatible API and ANTHROPIC_AUTH_TOKEN for auth.
    """

    name = "deepclaude"
    gradient_class = "model-deepclaude"
    binary = "claude"

    @property
    def _deepseek_env(self) -> dict:
        """DeepSeek env vars — read fresh from environment each time."""
        api_key = os.environ.get("DEEPSEEK_API_KEY", "")
        return {
            "ANTHROPIC_BASE_URL": os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com/anthropic"),
            "ANTHROPIC_API_KEY": api_key,  # Standard Claude Code API key env var
            "ANTHROPIC_AUTH_TOKEN": api_key,  # Also used by some setups
            "ANTHROPIC_MODEL": os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-pro[1m]"),
            "ANTHROPIC_DEFAULT_OPUS_MODEL": os.environ.get("DEEPSEEK_MODEL_OPUS", "deepseek-v4-pro[1m]"),
            "ANTHROPIC_DEFAULT_SONNET_MODEL": os.environ.get("DEEPSEEK_MODEL_SONNET", "deepseek-v4-pro[1m]"),
            "ANTHROPIC_DEFAULT_HAIKU_MODEL": os.environ.get("DEEPSEEK_MODEL_HAIKU", "deepseek-v4-flash"),
            "CLAUDE_CODE_SUBAGENT_MODEL": os.environ.get("DEEPSEEK_SUBAGENT_MODEL", "deepseek-v4-flash"),
            "CLAUDE_CODE_EFFORT_LEVEL": os.environ.get("DEEPSEEK_EFFORT", "max"),
        }

    @property
    def available(self) -> bool:
        # Only available if binary exists AND DeepSeek API key is configured
        has_key = bool(os.environ.get("DEEPSEEK_API_KEY", ""))
        return (self._find_binary() is not None
                and has_key
                and rate_tracker.is_available(self.name))

    def __init__(self):
        super().__init__(strengths=["backend", "bug", "code-analysis", "refactoring", "planning"])

    def _find_binary(self) -> str | None:
        """Try deepclaude first, then claude as fallback."""
        if self._binary_path:
            return self._binary_path
        # Try explicit deepclaude binary first (wrapper script)
        path = shutil.which("deepclaude") or os.path.expanduser("~/.local/bin/deepclaude")
        if os.path.isfile(path) and os.access(path, os.X_OK):
            self._binary_path = path
            return path
        # Fallback: claude binary (env vars handle DeepSeek routing)
        path = shutil.which("claude") or os.path.expanduser("~/.local/bin/claude")
        if os.path.isfile(path) and os.access(path, os.X_OK):
            self._binary_path = path
            return path
        return None

    def call(self, model: str, system_prompt: str, user_prompt: str,
             response_json: bool = True, temperature: float = 0.3,
             timeout: int = 60, log_path: str | None = None) -> str | dict | None:
        if not self._find_binary():
            return None
        full = user_prompt
        if response_json:
            full += "\n\nIMPORTANTE: Responde ÚNICAMENTE con el JSON solicitado. Sin markdown ni texto extra."
        if system_prompt:
            full = f"SYSTEM: {system_prompt}\n\n---\n\n{full}"
        output = self._run_cli(["-p", full], timeout, add_repo=False,
                               extra_env=self._deepseek_env, log_path=log_path)
        if output is None:
            return None
        if response_json:
            return self._parse_json_response(output)
        return output.strip()


class OllamaProvider(AIProvider):
    """Ollama local LLM — REST API at localhost:11434.

    No CLI binary needed. Uses urllib to call Ollama's HTTP API.
    Designed for code QA, linting, and commit message generation.
    Local fallback when remote providers are unavailable.
    """

    name = "ollama"
    gradient_class = "model-ollama"
    binary = ""  # No binary — pure HTTP API

    def __init__(self):
        super().__init__(strengths=["code-qa", "linting", "commits"])
        self.base_url = os.environ.get("OLLAMA_API_BASE", "http://localhost:11434")
        self.model = os.environ.get("OLLAMA_MODEL", "qwen2.5-coder:7b")
        self._available = False
        self._check_availability()

    @property
    def available(self) -> bool:
        return self._available

    def _check_availability(self):
        """Check if Ollama is running and the configured model is available via GET /api/tags."""
        try:
            req = urllib.request.Request(
                f"{self.base_url}/api/tags",
                method="GET",
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                models = [m.get("name", "") for m in data.get("models", [])]
                # Match exact model name, or prefix match without tag
                # (e.g. "qwen2.5-coder" matches "qwen2.5-coder:7b")
                model_prefix = self.model.split(":")[0]
                self._available = (
                    self.model in models
                    or any(m.startswith(model_prefix) for m in models)
                )
                if self._available:
                    print(
                        f"  Ollama: model '{self.model}' available "
                        f"({len(models)} models total)",
                        file=sys.stderr,
                    )
                else:
                    print(
                        f"  Ollama: model '{self.model}' NOT found. "
                        f"Available: {models}",
                        file=sys.stderr,
                    )
        except urllib.error.URLError as e:
            print(
                f"  Ollama: connection refused at {self.base_url} — {e.reason}",
                file=sys.stderr,
            )
            self._available = False
        except Exception as e:
            print(f"  Ollama: unavailable — {e}", file=sys.stderr)
            self._available = False

    def process(self, prompt: str, system: str = None) -> str:
        """Send prompt to Ollama /api/generate and return the response text.

        Args:
            prompt: The user prompt to send.
            system: Optional system prompt (passed as 'system' field in payload).

        Returns:
            The response text from the model.

        Raises:
            Exception on network or API errors (caller should catch).
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
            },
        }
        if system:
            payload["system"] = system

        try:
            req = urllib.request.Request(
                f"{self.base_url}/api/generate",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                rate_tracker.record_call(self.name)
                return data.get("response", "")
        except Exception as e:
            print(f"  Ollama process error: {e}", file=sys.stderr)
            raise

    def call(self, model: str, system_prompt: str, user_prompt: str,
             response_json: bool = True, temperature: float = 0.3,
             timeout: int = 120, log_path: str | None = None) -> str | dict | None:
        """Router-compatible call interface wrapping process().

        Matches the AIProvider.call() signature so Ollama can serve as a
        fallback provider in AIRouter.process_stage().
        """
        if not self.available:
            return None
        try:
            result = self.process(user_prompt, system=system_prompt)
            if result:
                if response_json:
                    parsed = self._parse_json_response(result)
                    if parsed is not None:
                        return parsed
                    # If JSON parse fails, return raw text for non-critical stages
                    return result
                return result
            return None
        except Exception as e:
            print(f"  Ollama call error: {e}", file=sys.stderr)
            rate_tracker.record_error(self.name, 500)
            return None


# ── AI Router ────────────────────────────────────────────────────────────────

class AIRouter:
    """Routes AI requests to the best available CLI provider."""

    _providers: dict = {}
    _initialized: bool = False
    _registry: dict = {}
    _last_used_provider = None  # (provider_name, model_name, stage) of last successful AI call
    _last_used_timestamp = None
    _active_calls = {}  # task_id → {provider, model, stage, started_at}

    @classmethod
    def initialize(cls):
        if cls._initialized:
            return
        cls._providers = {
            "claude": ClaudeProvider(),
            "deepclaude": DeepClaudeProvider(),
            "ollama": OllamaProvider(),
        }
        # Load workspace registry once at init time
        if not cls._registry:
            cls._registry = load_workspace_registry()
        cls._initialized = True

    @classmethod
    def _get_git_diff_stat(cls, task: dict) -> str:
        """Return 1-line diff stat (files changed, +N -M lines). Token-efficient."""
        branch = task.get("git_branch", "")
        base = task.get("git_base_branch", "develop")
        if not branch:
            return "[Sin rama git]"
        try:
            import subprocess, os
            repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            result = subprocess.run(
                f"git diff --stat {base}...{branch}",
                shell=True, cwd=repo_root, capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                lines = result.stdout.strip().split("\n")
                summary = lines[-1].strip() if lines else result.stdout.strip()
                return summary[:200]
        except Exception:
            pass
        return "[Diff no disponible]"

    @classmethod
    def process_comment(cls, task: dict, comment_text: str,
                        stage: str = "review",
                        log_path: str | None = None) -> str | None:
        """Lightweight AI response to a user comment. ~500 token prompt, cheapest provider first.
        Returns AI response text or None if all providers fail."""

        if not cls._initialized:
            cls.initialize()

        # Build token-efficient prompt — NO project context
        task_title = task.get("title", "")
        category = task.get("category", "tools")

        # Last 5 comments, truncated
        comments = task.get("comments", []) if isinstance(task.get("comments"), list) else []
        recent = comments[-5:]
        comment_lines = []
        for c in recent:
            author = c.get("author", "?")
            text = c.get("text", "")
            if len(text) > 150:
                text = text[:150] + "..."
            comment_lines.append(f"[{author}]: {text}")
        comment_context = "\n".join(comment_lines) if comment_lines else "(sin comentarios previos)"

        # Diff stat only
        diff_stat = cls._get_git_diff_stat(task)

        # Review iteration count from stage_history
        stage_history = task.get("stage_history", []) if isinstance(task.get("stage_history"), list) else []
        review_iterations = sum(1 for e in stage_history if e.get("stage") == "review")

        system = (
            "Eres un asistente de desarrollo colaborando en la revision de una tarea. "
            "El usuario dejo feedback. Responde en espanol, 3-6 frases, con sugerencias concretas "
            "y accionables. Menciona archivos especificos si puedes. "
            "Se practico: que cambios hacer, en que archivos, por que. "
            "NO repitas contexto que el usuario ya conoce. Solo texto plano."
        )

        user_prompt = (
            f"TAREA: {task_title}\n"
            f"Categoria: {category} | Estado: {stage}\n"
            f"Revision #: {review_iterations + 1}\n\n"
            f"ULTIMOS COMENTARIOS:\n{comment_context}\n\n"
            f"DIFF STAT: {diff_stat}\n\n"
            f"NUEVO COMENTARIO DEL USUARIO:\n{comment_text}\n\n"
            "Responde con sugerencias concretas para esta tarea."
        )

        # Provider priority: cheapest first (deepclaude Flash, claude Haiku, ollama Qwen)
        providers_to_try = []
        deepclaude = cls._providers.get("deepclaude") or cls._providers.get("deepseek")
        claude = cls._providers.get("claude")
        ollama = cls._providers.get("ollama")

        if deepclaude and deepclaude.available:
            providers_to_try.append(("deepclaude", deepclaude, "deepseek-v4-flash"))
        if claude and claude.available:
            providers_to_try.append(("claude", claude, "claude-haiku-4-5"))
        if ollama and ollama.available:
            providers_to_try.append(("ollama", ollama, None))

        for name, provider, model in providers_to_try:
            try:
                result = provider.call(
                    model, system, user_prompt,
                    response_json=False,
                    temperature=0.5,
                    timeout=45 if name != "ollama" else 120,
                    log_path=log_path,
                )
                if isinstance(result, str) and result.strip():
                    if name == "ollama":
                        return "[Respuesta local — puede ser mas lenta]\n\n" + result.strip()
                    return result.strip()
            except Exception as e:
                print(f"  process_comment: {name} failed: {e}")
                continue

        return None

    @classmethod
    def _preference_order(cls, category: str = "", stage: str = "planning") -> list[str]:
        """Get provider preference order for a stage, using workspace.json if available.
        Ollama is always appended as the final local fallback."""
        result = None
        fallback_chain = cls._registry.get("routing", {}).get("fallback_chain", [])
        if fallback_chain:
            providers = []
            for spec_key in fallback_chain:
                spec = cls._registry.get("specializations", {}).get(spec_key, {})
                provider = spec.get("provider", "")
                if provider and provider not in providers:
                    providers.append(provider)
            if providers:
                # Map provider names to taskboard agent names used in _providers
                agent_providers = []
                for p in providers:
                    if p == "deepseek":
                        agent_providers.append("deepclaude")
                    elif p == "gemini":
                        agent_providers.append("agy")
                    elif p in cls._providers:
                        agent_providers.append(p)
                    else:
                        agent_providers.append(p)
                if agent_providers:
                    result = agent_providers
        # Default fallback (original behavior)
        if result is None:
            if stage == "planning":
                result = ["deepclaude", "claude"]
            else:
                result = ["claude", "deepclaude"]
        # Ollama is always the lowest-priority local fallback
        if "ollama" not in result:
            result.append("ollama")
        return result

    @classmethod
    def score_specialization(cls, task: dict, specialization_key: str, spec: dict) -> float:
        """Calculate a weighted score for a specialization against a task.
        Returns a float score (higher = better fit)."""
        weights = cls._registry.get("routing", {}).get("weights", {})

        score = 0.0
        category = task.get("category", "")
        title = (task.get("title", "") + " " + task.get("description", "")).lower()

        # 1. Specialization match (weight: 3)
        preferred = spec.get("preferred_for", [])
        strengths = spec.get("strengths", [])

        for pref in preferred:
            if pref in category or pref in title:
                score += 3 * weights.get("specialization_match", 3)
                break

        for strength in strengths:
            if strength in title:
                score += 1 * weights.get("specialization_match", 3)

        # 2. Availability (weight: 2) — checked by caller
        # This is applied by the caller when filtering

        # 3. Cost efficiency (weight: 1)
        provider_key = spec.get("provider", "")
        provider = cls._registry.get("providers", {}).get(provider_key, {})
        cost = provider.get("cost_per_1k_output", 0)
        if cost == 0:
            score += 1 * weights.get("cost_efficiency", 1)  # Free = best
        elif cost < 0.001:
            score += 0.5 * weights.get("cost_efficiency", 1)

        # 4. Complexity match (weight: 2)
        priority = task.get("priority", "medium")
        if priority == "critical" and provider_key == "claude" and spec.get("model_key") == "opus":
            score += 2 * weights.get("complexity_match", 2)
        elif priority in ("high", "medium") and provider_key == "deepseek" and spec.get("model_key") == "v4_pro":
            score += 1 * weights.get("complexity_match", 2)

        return score

    @classmethod
    def select(cls, category: str, stage: str) -> AIProvider | None:
        if not cls._initialized:
            cls.initialize()
        preferred = cls._preference_order(category, stage)
        for name in preferred:
            provider = cls._providers.get(name)
            if provider and provider.available:
                return provider
        return None

    @classmethod
    def get_last_provider(cls):
        """Return (provider_name, model, timestamp) or None"""
        if cls._last_used_provider:
            return (*cls._last_used_provider, cls._last_used_timestamp)
        return None

    @classmethod
    def process_stage(cls, task: dict, stage: str, log_path: str | None = None) -> dict | None:
        if not cls._initialized:
            cls.initialize()
        if "ai_analysis" not in task:
            task["ai_analysis"] = {}
        category = task.get("category", "tools")

        def _log(msg: str):
            """Write to log file and print to stdout."""
            line = f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] {msg}"
            print(f"  AI: {msg}")
            if log_path:
                try:
                    os.makedirs(os.path.dirname(log_path), exist_ok=True)
                    with open(log_path, "a", encoding="utf-8") as lf:
                        lf.write(line + "\n")
                except Exception:
                    pass

        task_id = task.get("id", "?")
        cls._active_calls[task_id] = {"provider": "pending", "model": "", "stage": stage, "started_at": time.time()}
        stage_label = {"concept": "Concepto", "planning": "Plan", "review": "Review"}.get(stage, stage)
        _log(f"═══ Iniciando {stage_label} para tarea {task_id} ═══")
        _log(f"Título: {task.get('title', '')[:80]}")
        _log(f"Categoría: {category}")

        preferred = cls._preference_order(category, stage)
        tried = []
        last_error = None
        mark_ai_start(task_id, stage, preferred[0] if preferred else "?")

        for name in preferred:
            provider = cls._providers.get(name)
            if not provider:
                continue
            if not provider.available:
                tried.append({"provider": name, "available": False, "reason": "rate_limited_or_missing"})
                _log(f"⏭ Omitiendo {name}: no disponible (rate limit o binario ausente)")
                continue

            _log(f"🤖 Intentando provider: {provider.name}")
            tried.append({"provider": name, "available": True})
            cls._active_calls[task_id] = {"provider": name, "model": provider.name, "stage": stage, "started_at": time.time()}

            try:
                if stage == "concept":
                    result = cls._process_concept(task, provider, log_path=log_path)
                elif stage == "planning":
                    result = cls._process_planning(task, provider, log_path=log_path)
                elif stage == "review":
                    result = cls._process_review(task, provider, log_path=log_path)
                else:
                    cls._active_calls.pop(task_id, None)
                    return None

                if result is not None:
                    _log(f"✅ {provider.name} completó {stage_label} exitosamente")
                    AIRouter._last_used_provider = (name, provider.name, stage)
                    AIRouter._last_used_timestamp = time.time()
                    task["ai_analysis"].pop("all_providers_failed", None)
                    task["ai_analysis"].pop("provider_errors", None)
                    task["ai_analysis"].pop("failed_stage", None)
                    mark_ai_done(task_id)
                    return result

                _log(f"❌ {provider.name} no devolvió resultado para {stage_label}, intentando siguiente…")
                last_error = f"{provider.name}: no output (likely rate limited or API error)"
            except Exception as e:
                _log(f"💥 {provider.name} excepción: {e}")
                last_error = f"{provider.name}: {e}"

        # ── Ollama local fallback ──────────────────────────────────────────
        # If all remote providers failed, try Ollama as a best-effort local
        # fallback before resorting to heuristic generation.
        ollama = cls._providers.get("ollama")
        if ollama and ollama.available:
            _log("🔄 Todos los providers remotos fallaron. Intentando Ollama (local)...")
            tried.append({"provider": "ollama", "available": True})
            try:
                if stage == "concept":
                    result = cls._process_concept(task, ollama, log_path=log_path)
                elif stage == "planning":
                    result = cls._process_planning(task, ollama, log_path=log_path)
                elif stage == "review":
                    result = cls._process_review(task, ollama, log_path=log_path)
                else:
                    result = None

                if result is not None:
                    _log(f"✅ Ollama (local) completó {stage_label} exitosamente")
                    AIRouter._last_used_provider = ("ollama", ollama.name, stage)
                    AIRouter._last_used_timestamp = time.time()
                    task["ai_analysis"].pop("all_providers_failed", None)
                    task["ai_analysis"].pop("provider_errors", None)
                    task["ai_analysis"].pop("failed_stage", None)
                    mark_ai_done(task_id)
                    return result
                _log(f"❌ Ollama no devolvió resultado para {stage_label}")
            except Exception as e:
                _log(f"💥 Ollama excepción: {e}")

        # All providers failed — save error state and fall back to heuristic
        # Check if rate limited and extract reset time
        rate_limit_msg = None
        for name in preferred:
            p = cls._providers.get(name)
            if p and getattr(p, '_last_rate_limit_msg', None):
                rate_limit_msg = p._last_rate_limit_msg
                break

        if rate_limit_msg:
            _log(f"🚫 Rate limit: {rate_limit_msg}")
            last_error = f"Rate limit: {rate_limit_msg}"
        else:
            _log(f"🚫 Todos los providers fallaron: {last_error}")
        _log(f"⚙ Generando plan heurístico (placeholder)…")

        task.setdefault("ai_analysis", {})
        task["ai_analysis"]["all_providers_failed"] = True
        task["ai_analysis"]["provider_errors"] = tried
        task["ai_analysis"]["failed_stage"] = stage
        task["ai_analysis"]["last_error"] = last_error or "No providers available"
        task["ai_analysis"]["failed_at"] = datetime.now(timezone.utc).isoformat()
        if rate_limit_msg:
            task["ai_analysis"]["rate_limit_msg"] = rate_limit_msg

        # Heuristic fallback so the task isn't left empty
        if stage == "planning":
            cls._heuristic_planning(task, "heuristic")
        elif stage == "review":
            cls._heuristic_review(task, "heuristic")
        elif stage == "concept":
            cls._heuristic_concept(task)

        mark_ai_done(task_id)
        cls._active_calls.pop(task_id, None)
        return task

    # ── Stage Processors ─────────────────────────────────────────────────

    @classmethod
    def _process_concept(cls, task: dict, provider: AIProvider, log_path: str | None = None) -> dict | None:
        desc = task.get("description", "")
        up = f"Descripción de la idea:\n{desc}\n\nCategoría sugerida: {task.get('category', 'tools')}\nGenera título profesional y comentario de alcance."
        result = provider.call(None, SYSTEM_CONCEPT, up, response_json=True, timeout=60)
        if isinstance(result, dict):
            task.setdefault("ai_analysis", {})
            task["ai_analysis"]["concept"] = {
                "generated_title": result.get("title", task.get("title", "")),
                "initial_comment": result.get("initial_comment", ""),
                "model_used": provider.name,
                "processed_at": datetime.now(timezone.utc).isoformat(),
            }
            if result.get("title"):
                task["title"] = result["title"]
            if result.get("category"):
                task["category"] = result["category"]
            if result.get("priority"):
                task["priority"] = result["priority"]
            if result.get("initial_comment"):
                task.setdefault("comments", []).append({
                    "author": provider.name,
                    "text": f"[AI Concept Analysis] {result['initial_comment']}",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
        else:
            cls._heuristic_concept(task)
        return task

    @classmethod
    def _heuristic_concept(cls, task: dict):
        desc = task.get("description", task.get("title", ""))
        title = desc[:60].strip()
        if len(desc) > 60:
            title = title.rsplit(" ", 1)[0] + "..."
        task["title"] = title
        task["category"] = "tools"
        task["priority"] = "medium"
        task.setdefault("ai_analysis", {})
        task["ai_analysis"]["concept"] = {
            "generated_title": title,
            "initial_comment": "Título generado por heurística (CLI no disponible).",
            "model_used": "heuristic",
            "processed_at": datetime.now(timezone.utc).isoformat(),
        }

    @classmethod
    def _process_planning(cls, task: dict, provider: AIProvider, log_path: str | None = None) -> dict | None:
        scope = task.get("scope", "axolotto")
        project_context = cls._get_project_context(scope)
        if scope == "taskboard":
            scope_note = (
                "\n⚠️ IMPORTANTE: Esta tarea es para la HERRAMIENTA TASKBOARD (tools/taskboard/), "
                "NO para el juego Axolotto. Todos los cambios deben limitarse a tools/taskboard/.\n"
                "El Taskboard usa Python stdlib + vanilla JS, sin frameworks.\n"
            )
        else:
            scope_note = (
                "\n⚠️ IMPORTANTE: Esta tarea es para el JUEGO AXOLOTTO. Los cambios van en "
                "backend/ (FastAPI), frontend/ (Next.js) o contracts/ (Solidity), NO en "
                "tools/taskboard/. Aunque el título o la categoría mencionen 'taskboard' o "
                "'tools', el ámbito es autoritativo: planifica para el juego Axolotto.\n"
            )
        up = (
            f"TAREA:\nTítulo: {task.get('title', '')}\nDescripción: {task.get('description', '')}\n"
            f"Categoría: {task.get('category', 'tools')}\n"
            f"Ámbito (AUTORITATIVO): {scope}\n"
            f"{scope_note}\n"
            f"CONTEXTO DEL PROYECTO:\n{project_context}\n\n"
            "Determina si es una tarea única o múltiple. Genera el plan correspondiente."
        )

        # Log what we're sending (truncated)
        cls._write_log(log_path, f"Enviando prompt a {provider.name} ({len(up)} chars)…")
        cls._write_log(log_path, f"Prompt preview: {up[:300]}…")

        result = provider.call(None, SYSTEM_PLANNING, up, response_json=True, timeout=180, log_path=log_path)
        if not isinstance(result, dict):
            cls._write_log(log_path, f"{provider.name} devolvió respuesta inválida (no JSON o vacío)")
            return None

        # Validate response has actual content (not just empty JSON from Ollama fallback)
        json_size = len(json.dumps(result))
        if json_size < 100:
            cls._write_log(log_path, f"{provider.name} respuesta demasiado corta ({json_size} bytes), intentando siguiente...")
            return None
        if not result.get("title") and not result.get("requirements"):
            cls._write_log(log_path, f"{provider.name} respuesta sin title ni requirements, intentando siguiente...")
            return None

        cls._write_log(log_path, f"{provider.name} respondió con JSON válido ({json_size} bytes)")

        if result.get("is_multi"):
            subtasks = result.get("subtasks", [])
            if subtasks:
                cls._write_log(log_path, f"AI decidió dividir en {len(subtasks)} subtareas:")
                for s in subtasks:
                    cls._write_log(log_path, f"  - {s.get('title', '?')} [{s.get('recommended_agent', '?')}]")
                # Update parent title if AI provided one
                ai_title = result.get("title", "").strip()
                if ai_title:
                    task["title"] = ai_title
                    cls._write_log(log_path, f"Título actualizado: {ai_title}")
                task.setdefault("ai_analysis", {})
                task["ai_analysis"]["planning"] = {
                    "is_multi": True, "subtask_count": len(subtasks),
                    "subtasks": subtasks, "model_used": provider.name,
                    "processed_at": datetime.now(timezone.utc).isoformat(),
                }
                return task
            # If is_multi but no subtasks, fall through to single-task processing

        # Apply AI-generated title
        ai_title = result.get("title", "").strip()
        if ai_title:
            old_title = task.get("title", "")
            task["title"] = ai_title
            cls._write_log(log_path, f"Título: '{old_title[:50]}' → '{ai_title}'")

        reqs = result.get("requirements", [])
        cls._write_log(log_path, f"Plan generado: {len(reqs)} requisitos, {len(result.get('files_to_modify', []))} archivos a modificar")
        cls._write_log(log_path, f"Agente recomendado: {result.get('recommended_agent', '?')}")
        cls._write_log(log_path, f"Impacto: {(result.get('impact_analysis', '') or '')[:150]}")

        if result.get("is_multi"):
            subtasks = result.get("subtasks", [])
            if subtasks:
                task.setdefault("ai_analysis", {})
                task["ai_analysis"]["planning"] = {
                    "is_multi": True, "subtask_count": len(subtasks),
                    "subtasks": subtasks, "model_used": provider.name,
                    "processed_at": datetime.now(timezone.utc).isoformat(),
                }
                return task
            # If is_multi but no subtasks, fall through to single-task processing

        reqs = result.get("requirements", [])
        task.setdefault("ai_analysis", {})
        task["ai_analysis"]["planning"] = {
            "is_multi": False, "generated_requirements": reqs,
            "recommended_agent": result.get("recommended_agent", "unassigned"),
            "design_notes": result.get("design_notes", ""),
            "verification_guide": result.get("verification_guide", ""),
            "files_to_modify": result.get("files_to_modify", []),
            "impact_analysis": result.get("impact_analysis", ""),
            "proposals": result.get("proposals", []),
            "model_used": provider.name,
            "processed_at": datetime.now(timezone.utc).isoformat(),
        }
        task["planning_data"] = {
            "requirements": reqs, "notes": result.get("design_notes", ""),
            "approved": False, "verification_guide": result.get("verification_guide", ""),
        }
        agent = cls._normalize_agent(result.get("recommended_agent", "unassigned"))
        task["assigned_to"] = agent
        cls._write_plan_doc(task, result, provider.name)
        return task

    @classmethod
    def _heuristic_planning(cls, task: dict, model_name: str):
        """Generate basic planning when AI unavailable."""
        title = task.get("title", "")
        category = task.get("category", "tools")
        reqs = [
            {"id": "req-1", "text": f"Implementar: {title}", "completed": False},
            {"id": "req-2", "text": "Verificar que los cambios funcionan correctamente", "completed": False},
            {"id": "req-3", "text": "Ejecutar tests relevantes", "completed": False},
        ]
        task.setdefault("ai_analysis", {})
        task["ai_analysis"]["planning"] = {
            "is_multi": False, "generated_requirements": reqs,
            "recommended_agent": "claude" if category == "frontend" else "agy",
            "design_notes": f"Plan heurístico para: {title}",
            "verification_guide": f"1. Abrir la app\n2. Verificar que {title[:50]} funciona\n3. Revisar logs",
            "model_used": model_name,
            "processed_at": datetime.now(timezone.utc).isoformat(),
        }
        task["planning_data"] = {
            "requirements": reqs, "notes": f"Plan heurístico",
            "approved": False, "verification_guide": task["ai_analysis"]["planning"]["verification_guide"],
        }
        task["assigned_to"] = task["ai_analysis"]["planning"]["recommended_agent"]

    @classmethod
    def _process_review(cls, task: dict, provider: AIProvider, log_path: str | None = None) -> dict | None:
        branch = task.get("git_branch", "")
        base = task.get("git_base_branch", "develop")
        diff = cls._get_git_diff(branch, base)
        if not diff:
            diff = "[No hay diff disponible]"
        if len(diff) > 8000:
            diff = diff[:8000] + "\n... [diff truncado]"

        cls._write_log(log_path, f"Enviando diff ({len(diff)} chars) a {provider.name} para review…")
        up = (
            f"TAREA:\nTítulo: {task.get('title', '')}\nDescripción: {task.get('description', '')}\n"
            f"Categoría: {task.get('category', 'tools')}\n\nGIT DIFF:\n{diff}\n\n"
            "Analiza el diff y genera: resumen, instrucciones de prueba manual, edge cases."
        )
        result = provider.call(None, SYSTEM_REVIEW, up, response_json=True, timeout=90)
        if not isinstance(result, dict):
            cls._write_log(log_path, f"{provider.name} devolvió respuesta inválida para review")
            return None

        cls._write_log(log_path, f"Review generada: {len(result.get('edge_cases', []))} edge cases encontrados")

        task.setdefault("ai_analysis", {})
        task["ai_analysis"]["review"] = {
            "summary": result.get("summary", ""),
            "test_instructions": result.get("test_instructions", ""),
            "edge_cases": result.get("edge_cases", []),
            "model_used": provider.name,
            "processed_at": datetime.now(timezone.utc).isoformat(),
        }
        return task

    @classmethod
    def _heuristic_review(cls, task: dict, model_name: str):
        """Generate basic review when AI unavailable."""
        task.setdefault("ai_analysis", {})
        task["ai_analysis"]["review"] = {
            "summary": f"Cambios realizados para: {task.get('title', '')}",
            "test_instructions": "1. Revisar el diff\n2. Probar la funcionalidad manualmente\n3. Verificar que no haya regresiones",
            "edge_cases": ["Verificar en diferentes navegadores", "Probar con datos vacíos"],
            "model_used": model_name,
            "processed_at": datetime.now(timezone.utc).isoformat(),
        }

    # ── Helpers ──────────────────────────────────────────────────────────

    @classmethod
    def _normalize_agent(cls, agent: str) -> str:
        """Normalize agent name and resolve specializations to providers."""
        a = (agent or "").lower().strip()

        # Check if it's a specialization key in workspace.json
        spec = cls._registry.get("specializations", {}).get(a)
        if spec:
            provider = spec.get("provider", "claude")
            if provider == "gemini":
                return "agy"
            if provider == "deepseek":
                return "deepclaude"
            if provider == "ollama":
                return "ollama"
            return provider

        # Existing mappings
        if a in ("claude", "sonnet", "opus", "haiku", "anthropic"):
            return "claude"
        if a in ("deepclaude", "deepseek", "v4_pro", "v4_flash"):
            return "deepclaude"
        if a in ("agy", "gemini", "google", "antigravity"):
            return "agy"
        if a in ("ollama", "qwen", "local"):
            return "ollama"

        # Agent name -> specialization -> provider
        mapping = cls._registry.get("agent_mappings", {}).get(a)
        if mapping:
            primary_spec = mapping.get("primary", "")
            spec = cls._registry.get("specializations", {}).get(primary_spec, {})
            provider = spec.get("provider", "claude")
            if provider == "gemini":
                return "agy"
            if provider == "deepseek":
                return "deepclaude"
            if provider == "ollama":
                return "ollama"
            return provider

        return "unassigned"

    @staticmethod
    def _slug(text: str) -> str:
        import re as _re
        text = (text or "").lower()
        text = _re.sub(r"[^a-z0-9\s-]", "", text)
        text = _re.sub(r"[\s-]+", "-", text)
        return text.strip("-")[:50] or "tarea"

    @classmethod
    def _write_plan_doc(cls, task: dict, result: dict, model_name: str):
        """Write the full plan to docs/plan_<id>_<slug>.md and stash a preview.

        Stores `plan_doc_path` (repo-relative) + `plan_preview` on planning_data
        and ai_analysis.planning so the card can show it.
        """
        try:
            task_id = task.get("id", "task")
            title = task.get("title", "")
            slug = cls._slug(title)
            docs_dir = os.path.join(REPO_ROOT, "docs")
            os.makedirs(docs_dir, exist_ok=True)
            rel_path = os.path.join("docs", f"plan_{task_id}_{slug}.md")
            abs_path = os.path.join(REPO_ROOT, rel_path)

            reqs = result.get("requirements", [])
            files = result.get("files_to_modify", [])
            proposals = result.get("proposals", [])
            now = datetime.now(timezone.utc).isoformat()

            lines = [
                f"# Plan: {title}",
                "",
                f"> Generado por **{model_name}** · tarea `{task_id}` · {now}",
                "",
                "## Descripción",
                task.get("description", "").strip() or "_(sin descripción)_",
                "",
                "## Análisis de impacto",
                (result.get("impact_analysis") or "_(no especificado)_").strip(),
                "",
                "## Archivos a crear/modificar",
            ]
            lines += [f"- `{f}`" for f in files] or ["- _(no especificado)_"]
            lines += ["", "## Checklist de criterios de aceptación"]
            lines += [
                f"- [{'x' if r.get('completed') else ' '}] {r.get('text', '')}"
                for r in reqs
            ] or ["- _(sin criterios)_"]
            lines += ["", "## Propuestas / mejoras"]
            lines += [f"- {p}" for p in proposals] or ["- _(ninguna)_"]
            lines += [
                "",
                "## Notas de diseño",
                (result.get("design_notes") or "_(sin notas)_").strip(),
                "",
                "## Guía de verificación",
                (result.get("verification_guide") or "_(sin guía)_").strip(),
                "",
            ]
            doc = "\n".join(lines)
            with open(abs_path, "w", encoding="utf-8") as f:
                f.write(doc)

            preview = doc[:600] + ("…" if len(doc) > 600 else "")
            task.setdefault("planning_data", {})
            task["planning_data"]["plan_doc_path"] = rel_path
            task["planning_data"]["plan_preview"] = preview
            task.setdefault("ai_analysis", {}).setdefault("planning", {})
            task["ai_analysis"]["planning"]["plan_doc_path"] = rel_path
            task["ai_analysis"]["planning"]["plan_preview"] = preview
            print(f"  AI: Plan doc written → {rel_path}")
        except Exception as e:
            print(f"  AI: Failed to write plan doc: {e}", file=sys.stderr)

    @classmethod
    def _get_project_context(cls, scope: str = "axolotto") -> str:
        """Return cached project context — delegates to module-level cache."""
        return get_cached_project_context(scope)

    @classmethod
    def _get_git_diff(cls, branch: str, base: str) -> str:
        cmd = f"git diff {base}...{branch}" if branch else "git diff"
        try:
            result = subprocess.run(cmd, shell=True, cwd=REPO_ROOT, capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout
            result2 = subprocess.run("git diff", shell=True, cwd=REPO_ROOT, capture_output=True, text=True, timeout=5)
            return result2.stdout if result2.returncode == 0 else ""
        except Exception:
            return ""

    @staticmethod
    def _write_log(log_path: str | None, msg: str):
        """Append a timestamped message to the log file, if log_path is set."""
        if not log_path:
            return
        try:
            line = f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] {msg}"
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            with open(log_path, "a", encoding="utf-8") as lf:
                lf.write(line + "\n")
        except Exception:
            pass


def get_router() -> AIRouter:
    AIRouter.initialize()
    return AIRouter


def get_rate_tracker() -> RateLimitTracker:
    return rate_tracker


# ── Active AI call tracking (for UI feedback) ────────────────────────────────

import threading as _threading
_active_lock = _threading.Lock()
_active_calls: dict[str, dict] = {}  # task_id → {stage, provider, started_at}


def mark_ai_start(task_id: str, stage: str, provider: str):
    with _active_lock:
        _active_calls[task_id] = {
            "stage": stage, "provider": provider,
            "started_at": datetime.now(timezone.utc).isoformat(),
        }


def mark_ai_done(task_id: str):
    with _active_lock:
        _active_calls.pop(task_id, None)


def get_active_ai_calls() -> list[dict]:
    with _active_lock:
        return [{"task_id": tid, **info} for tid, info in _active_calls.items()]
