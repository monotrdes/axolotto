#!/usr/bin/env python3
from __future__ import annotations
"""AgyClient — WebSocket bridge between Axolotto Taskboard and Agy Gateway.

Connects to ``agy run --watch`` at ws://localhost:8642 for real-time
agent orchestration, file monitoring, and context sync.

Uses ONLY Python stdlib — no pip dependencies.
"""

import base64
import hashlib
import json
import logging
import os
import socket
import struct
import threading
import time
from collections import deque
from http.client import HTTPConnection
from urllib.parse import urlparse

# ── Logger ────────────────────────────────────────────────────────────

logger = logging.getLogger("agy-client")
logger.setLevel(logging.DEBUG if os.environ.get("AGY_CLIENT_DEBUG") else logging.INFO)
if not logger.handlers:
    _h = logging.StreamHandler()
    _h.setFormatter(logging.Formatter("[agy-client] %(levelname)s %(message)s"))
    logger.addHandler(_h)

# ── WebSocket Constants (RFC 6455) ────────────────────────────────────

_WS_GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

class _WS:
    """WebSocket opcodes and protocol constants."""
    CONT    = 0x0
    TEXT    = 0x1
    CLOSE   = 0x8
    PING    = 0x9
    PONG    = 0xA

# ── AgyClient ──────────────────────────────────────────────────────────

class AgyClient:
    """WebSocket client for the Agy Gateway.

    Connects the taskboard to the orchestrator daemon at ws://localhost:8642.
    Provides methods for task assignment, planning requests, agent status
    queries, activity log retrieval, and real-time event listening.

    Typical usage::

        from agy_client import agy_client

        if agy_client.gateway_available:
            agy_client.send_task(my_task)
        else:
            # Fall back to ai_router.py direct provider calls
            pass
    """

    # ── constructor ───────────────────────────────────────────────────

    def __init__(self, gateway_url: str = "ws://localhost:8642",
                 workspace_config_path: str | None = None):
        """Initialize the Agy client.

        Args:
            gateway_url: WebSocket URL of the agy gateway.
            workspace_config_path: Optional path to workspace.json for
                the gateway config (informational — the gateway reads it
                when launched, not from this client).
        """
        self._url = gateway_url
        parsed = urlparse(gateway_url)
        self._host = parsed.hostname or "localhost"
        self._port = parsed.port or 8642
        self._ws_path = parsed.path or "/"
        self._workspace_config_path = workspace_config_path

        # ── connection state ─────────────────────────────────────────
        self._sock: socket.socket | None = None
        self._running = False
        self._connected = False
        self.gateway_available = False  # Set True after successful connect+health

        # ── threading ────────────────────────────────────────────────
        self._send_lock = threading.Lock()
        self._queue_lock = threading.Lock()
        self._pending_lock = threading.Lock()
        self._state_lock = threading.Lock()

        self._reader_thread: threading.Thread | None = None
        self._reconnect_thread: threading.Thread | None = None

        # ── message queue (flushed on reconnect) ─────────────────────
        self._outgoing_queue: deque[dict] = deque(maxlen=100)

        # ── pending request-response matches ─────────────────────────
        # corr_id -> {"event": threading.Event, "result": any}
        self._pending: dict[str, dict] = {}

        # ── listener callback ────────────────────────────────────────
        self._callback: callable | None = None

        # ── status cache (populated by gateway messages) ─────────────
        self._status_cache: dict = {
            "connected": False,
            "active_plan": None,
            "agent_count": 0,
            "monitored_files": 0,
            "last_delta": None,
        }
        self._activity_log: deque[dict] = deque(maxlen=200)
        self._agent_cache: dict[str, dict] = {}  # agent_name -> status dict

        # ── reconnect policy ─────────────────────────────────────────
        self._reconnect_base = 1.0   # seconds
        self._reconnect_max = 30.0   # seconds

    # ── public API ─────────────────────────────────────────────────────

    def connect(self) -> bool:
        """Connect to the Agy Gateway WebSocket.

        Returns True on successful connection, False otherwise.
        Safe to call multiple times (no-op if already connected).
        """
        with self._state_lock:
            if self._connected and self._sock:
                return True
            self._running = True

        # Perform the handshake
        if not self._do_handshake():
            self._running = False
            self.gateway_available = False
            return False

        # Health check
        if not self._health_check():
            self._cleanup_socket()
            self._running = False
            self.gateway_available = False
            return False

        self._connected = True
        self.gateway_available = True
        self._status_cache["connected"] = True

        # Flush queued messages
        self._flush_queue()

        # Start reader thread
        self._reader_thread = threading.Thread(
            target=self._read_loop, name="agy-reader", daemon=True
        )
        self._reader_thread.start()

        logger.info("Connected to Agy Gateway at %s:%d", self._host, self._port)
        return True

    def disconnect(self):
        """Disconnect from the gateway.

        Stops the reader thread, sends a close frame, and cleans up
        the socket. Safe to call when not connected.
        """
        self._running = False
        self._connected = False
        self.gateway_available = False
        self._status_cache["connected"] = False

        # Send close frame if socket is still alive
        sock = self._sock
        if sock:
            try:
                self._send_frame(_WS.CLOSE, b"")
            except Exception:
                pass
            self._cleanup_socket()

        logger.info("Disconnected from Agy Gateway")

    @property
    def is_connected(self) -> bool:
        """Check if the WebSocket is currently connected."""
        return self._connected and self._sock is not None

    @property
    def gateway_status(self) -> dict:
        """Get cached gateway status.

        Returns a dict with keys: connected, active_plan, agent_count,
        monitored_files, last_delta.
        """
        return dict(self._status_cache)

    def send_task(self, task: dict) -> bool:
        """Send a task to the orchestrator for decomposition and assignment.

        The task dict should include: id, title, description, category,
        priority, stage.

        Returns True if the message was sent (or queued for later delivery).
        Returns False if the gateway is not available and the message was
        dropped (queue full).
        """
        payload = {
            "task": {
                "id": task.get("id", ""),
                "title": task.get("title", ""),
                "description": task.get("description", ""),
                "category": task.get("category", "tools"),
                "priority": task.get("priority", "medium"),
                "stage": task.get("status", task.get("stage", "planning")),
            }
        }
        return self._send_message("task.assign", payload)

    def send_status_update(self, task_id: str, status: str,
                           metadata: dict | None = None) -> bool:
        """Notify the orchestrator of a task status change.

        Args:
            task_id: The task identifier.
            status: New status string (e.g. "doing", "review", "done").
            metadata: Optional extra data about the status change.

        Returns True if sent/queued, False if dropped.
        """
        payload = {"task_id": task_id, "status": status}
        if metadata:
            payload["metadata"] = metadata
        return self._send_message("task.status", payload)

    def request_planning(self, task: dict) -> dict | None:
        """Request the orchestrator to plan a task.

        Sends a planning.request and waits up to 60s for a task.decomposed
        response from the gateway.

        Args:
            task: Task dict with at least id, title, description.

        Returns:
            The decomposed plan dict from the gateway, or None on
            timeout / gateway unavailable.
        """
        if not self.gateway_available:
            return None

        task_id = task.get("id", str(int(time.time())))
        corr_id = f"plan_{task_id}"
        event = threading.Event()
        with self._pending_lock:
            self._pending[corr_id] = {"event": event, "result": None}

        ok = self._send_message("planning.request", {"task": task})
        if not ok:
            with self._pending_lock:
                self._pending.pop(corr_id, None)
            return None

        if event.wait(timeout=60):
            with self._pending_lock:
                entry = self._pending.pop(corr_id, None)
                return entry["result"] if entry else None
        else:
            with self._pending_lock:
                self._pending.pop(corr_id, None)
            logger.warning("request_planning timed out for task %s", task_id)
            return None

    def get_agent_status(self, agent_name: str | None = None) -> list[dict]:
        """Get status of all agents or a specific agent.

        If the gateway is available, sends an agent.status_request and
        waits for the response. Falls back to the local cache if the
        gateway is unavailable.

        Args:
            agent_name: Specific agent to query, or None for all.

        Returns:
            List of agent status dicts. Each dict has keys:
            name, provider, model, specialization, status, current_task,
            files_modified.
        """
        if not self.gateway_available:
            return list(self._agent_cache.values()) if not agent_name else [
                a for a in self._agent_cache.values()
                if a.get("name") == agent_name
            ]

        corr_id = f"agent_st_{agent_name or 'all'}_{int(time.time() * 1000)}"
        event = threading.Event()
        with self._pending_lock:
            self._pending[corr_id] = {"event": event, "result": None}

        payload: dict = {}
        if agent_name:
            payload["agent"] = agent_name
        ok = self._send_message("agent.status_request", payload)
        if not ok:
            with self._pending_lock:
                self._pending.pop(corr_id, None)
            return list(self._agent_cache.values()) if not agent_name else []

        if event.wait(timeout=15):
            with self._pending_lock:
                entry = self._pending.pop(corr_id, None)
                result = entry["result"] if entry else None
                if result:
                    return result if isinstance(result, list) else [result]
            return []
        else:
            with self._pending_lock:
                self._pending.pop(corr_id, None)
            logger.warning("get_agent_status timed out")
            return list(self._agent_cache.values()) if not agent_name else []

    def get_activity_log(self, limit: int = 20) -> list[dict]:
        """Get recent activity log entries from the gateway.

        If gateway is available, sends an activity.request and waits for
        the response. Otherwise returns local cache.

        Args:
            limit: Maximum number of entries to return.

        Returns:
            List of activity log entry dicts.
        """
        if not self.gateway_available:
            items = list(self._activity_log)
            return items[-limit:] if len(items) > limit else items

        corr_id = f"activity_{int(time.time() * 1000)}"
        event = threading.Event()
        with self._pending_lock:
            self._pending[corr_id] = {"event": event, "result": None}

        ok = self._send_message("activity.request", {"limit": limit})
        if not ok:
            with self._pending_lock:
                self._pending.pop(corr_id, None)
            return list(self._activity_log)[-limit:]

        if event.wait(timeout=15):
            with self._pending_lock:
                entry = self._pending.pop(corr_id, None)
                result = entry["result"] if entry else None
                if result and isinstance(result, list):
                    return result
            return []
        else:
            with self._pending_lock:
                self._pending.pop(corr_id, None)
            logger.warning("get_activity_log timed out")
            return list(self._activity_log)[-limit:]

    def listen(self, callback: callable):
        """Start listening for gateway messages.

        The callback is called as ``callback(topic, data)`` for every
        incoming message from the gateway that is not consumed by an
        internal pending request.

        The *topic* is the ``type`` field from the gateway message
        (e.g. ``"agent.progress"``, ``"file.delta"``). The *data* is
        the full message dict.

        Only one callback is supported — subsequent calls replace the
        previous one. Pass ``None`` to stop listening.
        """
        self._callback = callback

    # ── helpers (also public — can be called directly) ─────────────────

    def _send_message(self, msg_type: str, payload: dict) -> bool:
        """Send a JSON message over WebSocket.

        If disconnected, queues the message for later delivery (max 100).
        Returns True if the message was sent or queued successfully.
        """
        message = {"type": msg_type}
        message.update(payload)

        with self._send_lock:
            if self._connected and self._sock:
                try:
                    data = json.dumps(message, ensure_ascii=False).encode("utf-8")
                    return self._send_frame(_WS.TEXT, data)
                except (socket.error, BrokenPipeError, OSError) as e:
                    logger.warning("Send failed, queuing: %s", e)
                    self._connected = False
                    # gateway_available stays True — reconnect will restore
                    self._status_cache["connected"] = False

        # Queue the message
        with self._queue_lock:
            try:
                self._outgoing_queue.append(message)
                logger.debug("Queued message type=%s (queue size=%d)",
                             msg_type, len(self._outgoing_queue))
                return True
            except Exception:
                logger.warning("Queue full — dropped message type=%s", msg_type)
                return False

    def _health_check(self) -> bool:
        """Quick health check to the gateway via HTTP.

        Tries GET /health on the same host:port. Returns True if the
        gateway responds with a 200 status.
        """
        try:
            conn = HTTPConnection(self._host, self._port, timeout=5)
            conn.request("GET", "/health")
            resp = conn.getresponse()
            body = resp.read()
            conn.close()

            if resp.status == 200:
                logger.debug("Health check OK: %s", body.decode("utf-8", errors="replace")[:120])
                return True

            # Also try / (some gateways serve health info at root)
            conn2 = HTTPConnection(self._host, self._port, timeout=5)
            conn2.request("GET", "/")
            resp2 = conn2.getresponse()
            conn2.close()
            return resp2.status < 500

        except (socket.error, OSError, Exception) as e:
            logger.debug("Health check failed: %s", e)
            return False

    # ── internal: WebSocket protocol ───────────────────────────────────

    def _do_handshake(self) -> bool:
        """Perform the WebSocket opening handshake.

        Returns True if the server responded with 101 Switching Protocols.
        """
        try:
            # Generate a random 16-byte key for the handshake
            key_bytes = os.urandom(16)
            ws_key = base64.b64encode(key_bytes).decode("ascii")

            # Build the HTTP upgrade request
            request_lines = [
                f"GET {self._ws_path} HTTP/1.1",
                f"Host: {self._host}:{self._port}",
                "Upgrade: websocket",
                "Connection: Upgrade",
                f"Sec-WebSocket-Key: {ws_key}",
                "Sec-WebSocket-Version: 13",
                "",
                "",
            ]
            request = "\r\n".join(request_lines).encode("utf-8")

            # Connect TCP socket
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.settimeout(10)
            self._sock.connect((self._host, self._port))
            self._sock.sendall(request)

            # Read the HTTP response
            response = b""
            while b"\r\n\r\n" not in response:
                chunk = self._sock.recv(4096)
                if not chunk:
                    logger.warning("Handshake: connection closed before response")
                    return False
                response += chunk

            response_str = response.decode("utf-8", errors="replace")
            status_line = response_str.split("\r\n")[0]

            if "101" not in status_line:
                logger.warning("Handshake rejected: %s", status_line)
                return False

            # Verify Sec-WebSocket-Accept header
            expected_accept = base64.b64encode(
                hashlib.sha1((ws_key + _WS_GUID).encode("ascii")).digest()
            ).decode("ascii")

            # Loose verification — if header is missing, still accept
            if f"Sec-WebSocket-Accept: {expected_accept}" not in response_str:
                logger.debug("Handshake: Accept header mismatch or missing, proceeding anyway")

            # Set a shorter timeout for data frames
            self._sock.settimeout(1.0)
            logger.debug("WebSocket handshake complete")
            return True

        except (socket.error, OSError) as e:
            logger.warning("Handshake socket error: %s", e)
            self._cleanup_socket()
            return False

    def _send_frame(self, opcode: int, payload: bytes) -> bool:
        """Send a single WebSocket frame (client side, with masking).

        Client-to-server frames MUST be masked per RFC 6455 Section 5.3.
        """
        if not self._sock:
            return False

        try:
            # Byte 0: FIN (1) + RSV (0) + opcode
            frame = bytes([0x80 | (opcode & 0x0F)])

            # Byte 1: MASK (1) + payload length
            length = len(payload)
            if length < 126:
                frame += bytes([0x80 | length])
            elif length < 65536:
                frame += struct.pack("!BH", 0x80 | 126, length)
            else:
                frame += struct.pack("!BQ", 0x80 | 127, length)

            # 4-byte masking key
            mask_key = os.urandom(4)
            frame += mask_key

            # Masked payload: each byte XOR with mask_key[i % 4]
            masked = bytes(p ^ mask_key[i % 4] for i, p in enumerate(payload))
            frame += masked

            self._sock.sendall(frame)
            return True

        except (socket.error, BrokenPipeError, OSError) as e:
            logger.debug("Send frame error: %s", e)
            return False

    def _recv_exact(self, n: int) -> bytes:
        """Receive exactly *n* bytes from the socket.

        Returns fewer bytes if the connection closes or times out.
        """
        data = b""
        while len(data) < n:
            try:
                chunk = self._sock.recv(n - len(data))  # type: ignore[union-attr]
                if not chunk:
                    break  # Connection closed
                data += chunk
            except socket.timeout:
                break
            except (socket.error, OSError):
                break
        return data

    def _read_frame(self) -> tuple[bool | None, int | None, bytes | None]:
        """Read one WebSocket frame from the wire.

        Returns ``(fin, opcode, payload)``. Returns ``(None, None, None)``
        on connection error or close.
        """
        if not self._sock:
            return None, None, None

        try:
            header = self._recv_exact(2)
            if len(header) < 2:
                return None, None, None

            byte0, byte1 = header[0], header[1]
            fin = (byte0 & 0x80) != 0
            opcode = byte0 & 0x0F
            masked = (byte1 & 0x80) != 0
            length = byte1 & 0x7F

            # Extended payload length
            if length == 126:
                ext = self._recv_exact(2)
                if len(ext) < 2:
                    return None, None, None
                length = struct.unpack("!H", ext)[0]
            elif length == 127:
                ext = self._recv_exact(8)
                if len(ext) < 8:
                    return None, None, None
                length = struct.unpack("!Q", ext)[0]

            # Mask key (server frames should NOT be masked, but handle it)
            mask_key = b""
            if masked:
                mask_key = self._recv_exact(4)
                if len(mask_key) < 4:
                    return None, None, None

            # Payload
            payload = b""
            if length > 0:
                payload = self._recv_exact(length)

            # Unmask if the server sent a masked frame (non-conforming)
            if masked and mask_key and payload:
                payload = bytes(p ^ mask_key[i % 4] for i, p in enumerate(payload))

            return fin, opcode, payload

        except (socket.error, BrokenPipeError, OSError, struct.error) as e:
            logger.debug("Read frame error: %s", e)
            return None, None, None

    def _read_loop(self):
        """Background thread: read and process WebSocket frames.

        Handles fragmentation, control frames, and JSON message dispatch.
        """
        msg_buffer = bytearray()
        msg_opcode: int | None = None  # opcode of first fragment

        while self._running and self._sock:
            fin, opcode, payload = self._read_frame()

            if fin is None or opcode is None or payload is None:
                # Connection lost
                self._handle_disconnect()
                return

            # ── control frames ──────────────────────────────────────
            if opcode == _WS.CLOSE:
                # Echo back the close frame, then shutdown
                try:
                    # Build a proper close frame: status code (2 bytes) + reason
                    code = b"\x03\xe8"  # 1000 = Normal Closure
                    reason = b""
                    if len(payload) >= 2:
                        code = payload[:2]
                        reason = payload[2:]
                    self._send_frame(_WS.CLOSE,  code + reason)
                except Exception:
                    pass
                self._handle_disconnect()
                return

            if opcode == _WS.PING:
                try:
                    self._send_frame(_WS.PONG, payload)
                except Exception:
                    pass
                continue

            if opcode == _WS.PONG:
                # We could track latency here; current implementation ignores
                continue

            # ── data frames ─────────────────────────────────────────
            if opcode == _WS.TEXT:
                msg_buffer = bytearray(payload)
                msg_opcode = opcode
            elif opcode == _WS.CONT:
                msg_buffer.extend(payload)
            else:
                # Binary or reserved — skip
                continue

            # If this is the final fragment, process the complete message
            if fin and msg_opcode is not None and len(msg_buffer) > 0:
                try:
                    text = msg_buffer.decode("utf-8")
                except UnicodeDecodeError:
                    msg_buffer.clear()
                    msg_opcode = None
                    continue

                msg_buffer.clear()
                msg_opcode = None

                # Parse JSON
                try:
                    data: dict = json.loads(text)
                except json.JSONDecodeError:
                    logger.debug("Non-JSON message received: %s", text[:120])
                    continue

                self._process_message(data)

        # If we exit the loop naturally (running became False, user called disconnect)
        self._cleanup_socket()
        self._connected = False
        # NOTE: gateway_available stays True so queued messages are
        # preserved for potential reconnect — only explicit disconnect()
        # clears it.
        self._status_cache["connected"] = False

    def _process_message(self, data: dict):
        """Route an incoming parsed message to the right handler."""
        msg_type = data.get("type", "")
        task_id = data.get("task_id", "")

        # ── internal response matching ──────────────────────────────
        if msg_type == "task.decomposed" and task_id:
            corr_id = f"plan_{task_id}"
            with self._pending_lock:
                if corr_id in self._pending:
                    self._pending[corr_id]["result"] = data
                    self._pending[corr_id]["event"].set()
                    return

        elif msg_type == "agent.status":
            with self._pending_lock:
                for cid, entry in list(self._pending.items()):
                    if cid.startswith("agent_st_"):
                        agents = data.get("agents")
                        if agents is not None:
                            entry["result"] = agents
                        elif "agent" in data:
                            entry["result"] = [data["agent"]]
                        else:
                            entry["result"] = [data]
                        entry["event"].set()
                        break

            # Update local cache
            agents = data.get("agents", [data] if "name" in data else [])
            for agent in agents:
                name = agent.get("name", "")
                if name:
                    self._agent_cache[name] = agent
            self._status_cache["agent_count"] = len(self._agent_cache)
            return

        elif msg_type == "activity.log":
            entries = data.get("entries", [])
            with self._pending_lock:
                for cid, entry in list(self._pending.items()):
                    if cid.startswith("activity_"):
                        entry["result"] = entries
                        entry["event"].set()
                        break
            # Also append to local cache
            for e in entries:
                self._activity_log.append(e)
            return

        # ── status updates (keep local cache fresh) ─────────────────
        if msg_type == "agent.progress":
            agent_name = data.get("agent", "")
            if agent_name:
                self._agent_cache.setdefault(agent_name, {})
                self._agent_cache[agent_name].update({
                    "name": agent_name,
                    "status": data.get("status", "working"),
                    "current_task": data.get("task_id", ""),
                    "files": data.get("files", []),
                })
            # Add to activity log
            self._activity_log.append({
                "type": msg_type, "timestamp": time.time(), "data": data,
            })

        elif msg_type == "agent.idle":
            agent_name = data.get("agent", "")
            if agent_name:
                self._agent_cache.setdefault(agent_name, {})
                self._agent_cache[agent_name]["status"] = "idle"
                self._agent_cache[agent_name]["current_task"] = None

        elif msg_type == "agent.rate_limited":
            agent_name = data.get("agent", "")
            if agent_name:
                self._agent_cache.setdefault(agent_name, {})
                self._agent_cache[agent_name]["status"] = "rate_limited"
                self._agent_cache[agent_name]["retry_after"] = data.get("retry_after", 30)

        elif msg_type == "file.delta":
            self._status_cache["last_delta"] = {
                "added": data.get("added", 0),
                "removed": data.get("removed", 0),
                "files": data.get("files", []),
            }
            self._status_cache["monitored_files"] = (
                self._status_cache.get("monitored_files", 0) + 1
            )

        elif msg_type == "context.sync":
            self._status_cache["agent_count"] = len(data.get("agents", []))

        elif msg_type == "error":
            logger.warning("Gateway error: %s", data.get("message", "unknown"))

        # ── user callback ───────────────────────────────────────────
        if self._callback:
            try:
                self._callback(msg_type, data)
            except Exception:
                logger.exception("Unhandled error in agy client callback")

    # ── internal: lifecycle ───────────────────────────────────────────

    def _handle_disconnect(self):
        """Called when the WebSocket connection drops unexpectedly.

        Does NOT clear gateway_available — that would cause in-flight
        messages to be dropped instead of queued. The flag is only
        cleared on explicit disconnect().
        """
        self._cleanup_socket()
        self._connected = False
        # gateway_available stays True so the queue preserves messages
        self._status_cache["connected"] = False
        logger.warning("WebSocket connection lost")

        # Attempt auto-reconnect if still running
        if self._running:
            t = threading.Thread(target=self._auto_reconnect, name="agy-reconnect", daemon=True)
            t.start()
            self._reconnect_thread = t

    def _auto_reconnect(self):
        """Reconnect loop with exponential backoff."""
        attempt = 0
        while self._running and not self._connected:
            delay = min(self._reconnect_base * (2 ** attempt), self._reconnect_max)
            jitter = delay * 0.2 * (hash(str(time.time())) % 100 / 100.0)  # noqa: S324
            total_delay = delay + jitter
            logger.info("Reconnecting in %.1fs (attempt %d)...", total_delay, attempt + 1)

            # Sleep with polling so we can exit cleanly on disconnect()
            deadline = time.time() + total_delay
            while self._running and time.time() < deadline:
                time.sleep(0.1)

            if not self._running:
                return

            attempt += 1

            if self.connect():
                logger.info("Reconnected successfully (attempt %d)", attempt)
                return

        logger.warning("Reconnect aborted — running=%s", self._running)

    def _flush_queue(self):
        """Send all queued messages over the live connection."""
        with self._send_lock:
            with self._queue_lock:
                if not self._outgoing_queue:
                    return
                messages = list(self._outgoing_queue)
                self._outgoing_queue.clear()

            count = len(messages)
            sent = 0
            for msg in messages:
                try:
                    data = json.dumps(msg, ensure_ascii=False).encode("utf-8")
                    if self._send_frame(_WS.TEXT, data):
                        sent += 1
                    else:
                        # Put failed back into queue
                        with self._queue_lock:
                            self._outgoing_queue.appendleft(msg)
                        break
                except Exception:
                    with self._queue_lock:
                        self._outgoing_queue.appendleft(msg)
                    break

            logger.info("Flushed %d/%d queued messages", sent, count)

    def _cleanup_socket(self):
        """Close and discard the current socket, if any."""
        sock = self._sock
        self._sock = None
        if sock:
            try:
                sock.shutdown(socket.SHUT_RDWR)
            except (socket.error, OSError):
                pass
            try:
                sock.close()
            except (socket.error, OSError):
                pass


# ── Module-level singleton ─────────────────────────────────────────────

agy_client = AgyClient()
"""Module-level singleton AgyClient instance.

Import and use directly::

    from agy_client import agy_client

    if agy_client.gateway_available:
        agy_client.send_task(task)
"""


def is_plan_a() -> bool:
    """Return True if Agy Gateway is connected and orchestrating (Plan A).
    When False, the system operates in Plan B (chat AI mode) —
    auto-planning, worktree creation, and auto-assignment are disabled.
    """
    try:
        return agy_client is not None and agy_client.gateway_available
    except Exception:
        return False
