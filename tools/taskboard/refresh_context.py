#!/usr/bin/env python3
"""Refresh all project context caches and the knowledge base.

Run this after major architecture changes, new modules, or after merges
that change the project structure. This ensures AI agents get fresh context.

Usage:
    python3 tools/taskboard/refresh_context.py
    python3 tools/taskboard/refresh_context.py --scope axolotto
    python3 tools/taskboard/refresh_context.py --scope taskboard
"""

import os
import sys
from datetime import datetime, timezone

# Ensure we can import from tools/taskboard
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "taskboard"))

from project_context import refresh as refresh_project_context

def main():
    scope = None
    if "--scope" in sys.argv:
        idx = sys.argv.index("--scope")
        if idx + 1 < len(sys.argv):
            scope = sys.argv[idx + 1]

    print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] Refreshing context caches...")
    if scope:
        print(f"  Scope: {scope}")
    else:
        print("  Scope: all (axolotto + taskboard)")

    result = refresh_project_context(scope)

    for s in result["scopes"]:
        status = "OK" if s["ok"] else "FAILED"
        size = s.get("size", 0)
        print(f"  {s['scope']}: {status} ({size:,} chars)")

    if result["ok"]:
        print("Context refresh complete. AI agents will now use fresh context.")
    else:
        print("WARNING: Some scopes failed to refresh.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
