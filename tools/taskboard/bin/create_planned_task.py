#!/usr/bin/env python3
"""Create a fully planned task in the Kanban board.
Accepts JSON from stdin.
"""
import sys
import os
import json
import time

# Ensure we can import from tools/taskboard
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(CURRENT_DIR, "..")))

from db import read_tasks, write_task
from agent_runner import now_iso, slugify

def main():
    try:
        raw_input = sys.stdin.read().strip()
        if not raw_input:
            print("ERROR: No input received on stdin", file=sys.stderr)
            sys.exit(1)
        
        data = json.loads(raw_input)
    except Exception as e:
        print(f"ERROR: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)

    title = data.get("title", "").strip()
    description = data.get("description", "").strip()
    if not title or not description:
        print("ERROR: title and description are required", file=sys.stderr)
        sys.exit(1)

    scope = data.get("scope", "axolotto")
    category = data.get("category", "backend")
    priority = data.get("priority", "medium")
    assigned_to = data.get("assigned_to", "claude")
    requirements = data.get("requirements", [])
    files_to_modify = data.get("files_to_modify", [])
    design_notes = data.get("design_notes", "")
    verification_guide = data.get("verification_guide", "")
    test_command = data.get("test_command", "")

    # Format requirements with IDs if missing
    formatted_reqs = []
    for i, req in enumerate(requirements):
        if isinstance(req, str):
            formatted_reqs.append({
                "id": f"req-{int(time.time())}-{i}",
                "text": req,
                "completed": False
            })
        elif isinstance(req, dict):
            formatted_reqs.append({
                "id": req.get("id") or f"req-{int(time.time())}-{i}",
                "text": req.get("text", ""),
                "completed": req.get("completed", False)
            })

    # Prepare task dictionary
    tasks_data = read_tasks()
    task_id = f"task-{int(time.time())}-{len(tasks_data.get('tasks', []))}"
    slug = slugify(title)

    # Docs path
    rel_path = os.path.join("docs", f"plan_{task_id}_{slug}.md")
    abs_path = os.path.abspath(os.path.join(CURRENT_DIR, "..", "..", "..", rel_path))
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)

    # Write plan document
    try:
        lines = [
            f"# Plan: {title}",
            "",
            f"> Generado por **antigravity** · tarea `{task_id}` · {now_iso()}",
            "",
            "## Descripción",
            description or "_(sin descripción)_",
            "",
            "## Archivos a crear/modificar",
        ]
        lines += [f"- `{f}`" for f in files_to_modify] or ["- _(no especificado)_"]
        lines += ["", "## Checklist de criterios de aceptación"]
        lines += [
            f"- [ ] {r['text']}"
            for r in formatted_reqs
        ] or ["- _(sin criterios)_"]
        lines += [
            "",
            "## Notas de diseño",
            design_notes.strip() or "_(sin notas)_",
            "",
            "## Guía de verificación",
            verification_guide.strip() or "_(sin guía)_",
            "",
        ]
        with open(abs_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        
        preview = "\n".join(lines)[:600] + ("…" if len("\n".join(lines)) > 600 else "")
    except Exception as e:
        print(f"WARNING: Failed to write plan doc: {e}", file=sys.stderr)
        rel_path = ""
        preview = ""

    new_task = {
        "id": task_id,
        "title": title,
        "description": description,
        "status": "planning",
        "assigned_to": assigned_to,
        "priority": priority,
        "category": category,
        "scope": scope,
        "test_command": test_command,
        "git_branch": "",
        "git_base_branch": "",
        "needs_agent_generation": False,
        "planning_data": {
            "requirements": formatted_reqs,
            "notes": design_notes,
            "approved": False,
            "verification_guide": verification_guide,
            "plan_doc_path": rel_path,
            "plan_preview": preview
        },
        "comments": [{
            "author": "system",
            "text": f"Plan inicial inyectado por el orquestador AI Antigravity.",
            "timestamp": now_iso()
        }],
        "stage_history": [{
            "stage": "planning",
            "entered_at": now_iso(),
            "ai_triggered": False
        }],
        "ai_analysis": {
            "planning": {
                "is_multi": False,
                "generated_requirements": formatted_reqs,
                "recommended_agent": assigned_to,
                "design_notes": design_notes,
                "verification_guide": verification_guide,
                "files_to_modify": files_to_modify,
                "model_used": "antigravity",
                "processed_at": now_iso(),
                "plan_doc_path": rel_path,
                "plan_preview": preview
            }
        },
        "created_at": now_iso(),
        "updated_at": now_iso()
    }

    # Write to database
    from db import write_task as single_write
    if single_write(new_task):
        print(json.dumps({
            "success": True,
            "task_id": task_id,
            "plan_doc_path": rel_path
        }))
    else:
        print(json.dumps({
            "success": False,
            "error": "Failed to write task to SQLite"
        }), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
