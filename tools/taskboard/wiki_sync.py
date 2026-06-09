#!/usr/bin/env python3
"""Wiki synchronization module for the Axolotto taskboard DONE transition.

Called after a successful git merge to develop. Analyzes the merged changes,
determines which wiki files are affected, generates changelog entries, and
detects validation gaps.

Non-blocking: all failures are captured as alerts — never blocks the merge.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

# Local imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from db import REPO_ROOT

WIKI_DIR = os.path.join(REPO_ROOT, "wiki")
CHANGELOG_PATH = os.path.join(WIKI_DIR, "CHANGELOG.md")

# ── Economy-signature paths ───────────────────────────────────────────
# If any changed file matches one of these, the task IS an economy change
# and ALL wiki/economia/ files must be flagged.
ECONOMY_PATH_PATTERNS = [
    "backend/app/core/prices.py",
    "backend/app/core/config.py",
    "backend/app/services/shop_service.py",
    "backend/app/services/bank_service.py",
    "backend/app/services/vip_scheduler.py",
    "backend/app/services/vip_service.py",
    "backend/app/api/v1/endpoints/shop.py",
    "backend/app/api/v1/endpoints/bank.py",
    "backend/app/api/v1/endpoints/checkout.py",
    "backend/app/models/economy.py",
]

# ── Category → wiki sections mapping ──────────────────────────────────
CATEGORY_TO_WIKI_SECTIONS = {
    "backend":    ["api/", "arquitectura/backend.md"],
    "frontend":   ["arquitectura/frontend.md"],
    "finance":    ["economia/tablas_precios.md", "economia/monedas.md",
                   "economia/vip_tiers.md", "economia/economia_general.md"],
    "gamedesign": ["mecanicas/", "jugadores/"],
    "blockchain": ["arquitectura/contratos.md"],
    "bug":        [],   # dynamic — depends on actual changed files
    "docs":       [],   # wiki/ itself — too meta, handled separately
    "infra":      ["arquitectura/backend.md"],
    "security":   ["arquitectura/backend.md"],
    "tools":      [],   # taskboard changes don't touch game wiki
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── Frontmatter parsing (no PyYAML dependency) ────────────────────────

def _parse_frontmatter_source_files(md_path: str) -> list:
    """Extract source_files list from a markdown file's YAML frontmatter."""
    try:
        with open(md_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return []

    # Match YAML frontmatter between --- delimiters
    m = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not m:
        return []

    frontmatter = m.group(1)
    # Find source_files line: source_files: [...]
    sf_match = re.search(r'^source_files\s*:\s*\[(.*?)\]', frontmatter, re.MULTILINE)
    if not sf_match:
        return []

    raw = sf_match.group(1)
    # Parse quoted strings from the list
    files = re.findall(r'"([^"]*)"', raw)
    return files


def _parse_frontmatter_last_modified(md_path: str) -> str | None:
    """Extract last_modified from frontmatter."""
    try:
        with open(md_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return None
    m = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not m:
        return None
    lm_match = re.search(r'^last_modified\s*:\s*"(.*?)"', m.group(1), re.MULTILINE)
    return lm_match.group(1) if lm_match else None


# ── Source map builder ────────────────────────────────────────────────

def _build_wiki_source_map() -> dict:
    """Scan all wiki/*.md files, extract source_files frontmatter,
    return inverted map: {source_code_path: [wiki_file_relpath, ...]}"""
    source_map = {}
    if not os.path.isdir(WIKI_DIR):
        return source_map

    for root, dirs, files in os.walk(WIKI_DIR):
        # Skip .obsidian and nested vaults
        dirs[:] = [d for d in dirs if not d.startswith(".") and d != "axolotto-wiki"]
        for fname in files:
            if not fname.endswith(".md"):
                continue
            full_path = os.path.join(root, fname)
            sources = _parse_frontmatter_source_files(full_path)
            if not sources:
                continue
            rel_path = os.path.relpath(full_path, REPO_ROOT).replace("\\", "/")
            for src in sources:
                src_normalized = src.replace("\\", "/")
                source_map.setdefault(src_normalized, []).append(rel_path)
    return source_map


# ── Git diff helpers ──────────────────────────────────────────────────

def _get_actual_changes(branch_name: str, base_branch: str) -> list:
    """Get list of files changed in the task branch vs merge-base.
    Uses three-dot syntax: base...branch = changes from merge-base to branch HEAD."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", f"{base_branch}...{branch_name}"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode != 0:
            return []
        files = [f.strip().replace("\\", "/") for f in result.stdout.strip().split("\n") if f.strip()]
        return files
    except Exception:
        return []


def _get_merge_commit_changes() -> list:
    """Fallback: get files changed in the most recent merge commit (HEAD)."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode != 0:
            return []
        files = [f.strip().replace("\\", "/") for f in result.stdout.strip().split("\n") if f.strip()]
        return files
    except Exception:
        return []


# ── File → wiki mapping ───────────────────────────────────────────────

def _files_to_wiki_files(files: list, source_map: dict) -> list:
    """For a list of changed source files, return which wiki files claim them."""
    wiki_files = set()
    for f in files:
        f_norm = f.replace("\\", "/")
        # Exact match
        if f_norm in source_map:
            wiki_files.update(source_map[f_norm])
        # Prefix match (directory-level)
        for src, wikis in source_map.items():
            if f_norm.startswith(src.rstrip("/") + "/"):
                wiki_files.update(wikis)
            # Also check if source path contains the changed file pattern
            if src.rstrip("/") in f_norm:
                wiki_files.update(wikis)
    return sorted(wiki_files)


def _category_to_wiki_files(category: str) -> list:
    """Get wiki files/sections associated with a task category."""
    sections = CATEGORY_TO_WIKI_SECTIONS.get(category, [])
    result = []
    for sec in sections:
        if sec.endswith("/"):
            # Directory — expand to all .md files inside
            dir_path = os.path.join(WIKI_DIR, sec)
            if os.path.isdir(dir_path):
                for fname in sorted(os.listdir(dir_path)):
                    if fname.endswith(".md"):
                        rel = f"wiki/{sec}{fname}"
                        result.append(rel)
        else:
            result.append(f"wiki/{sec}")
    return result


# ── Economy sensitivity ───────────────────────────────────────────────

def _is_economy_change(files: list) -> bool:
    """Check if any changed file matches economy-signature paths."""
    for f in files:
        f_norm = f.replace("\\", "/")
        for pat in ECONOMY_PATH_PATTERNS:
            if f_norm == pat or f_norm.startswith(pat.replace(".py", "/")):
                return True
    return False


# ── Validation gap detection ──────────────────────────────────────────

def _detect_validation_gaps(actual_changed: list, affected_wiki_files: list,
                            source_map: dict, planned_files: list) -> dict:
    """Detect gaps between what changed and wiki coverage.

    Returns {"gaps": [...], "unplanned": [...], "source_tracking_incomplete": [...]}
    """
    gaps = []
    unplanned = []
    source_tracking_incomplete = []

    wiki_claimed_sources = set()
    for wiki_file in affected_wiki_files:
        abs_path = os.path.join(REPO_ROOT, wiki_file)
        sources = _parse_frontmatter_source_files(abs_path)
        wiki_claimed_sources.update(s.replace("\\", "/") for s in sources)

    planned_set = {f.replace("\\", "/") for f in planned_files}

    for f in actual_changed:
        f_norm = f.replace("\\", "/")

        # Layer A: changed file has NO wiki claimant at all
        has_claimant = any(
            f_norm == src or f_norm.startswith(src.rstrip("/") + "/") or src.rstrip("/") in f_norm
            for src in source_map
        )
        if not has_claimant and not f_norm.startswith("wiki/") and not f_norm.startswith("tools/taskboard/"):
            gaps.append(f_norm)

        # Layer C: changed file NOT in planned files (surprise change)
        if planned_set and f_norm not in planned_set and not f_norm.startswith("wiki/"):
            unplanned.append(f_norm)

    # Layer D: wiki files whose source_files don't include a changed file in their domain
    # (too noisy for MVP — only flag for economy files)
    economy_files_affected = [f for f in actual_changed if f.replace("\\", "/") in ECONOMY_PATH_PATTERNS]
    if economy_files_affected:
        for wiki_file in affected_wiki_files:
            abs_path = os.path.join(REPO_ROOT, wiki_file)
            sources = _parse_frontmatter_source_files(abs_path)
            sources_norm = {s.replace("\\", "/") for s in sources}
            for ef in economy_files_affected:
                ef_norm = ef.replace("\\", "/")
                if ef_norm not in sources_norm:
                    source_tracking_incomplete.append({
                        "wiki_file": wiki_file,
                        "missing_source": ef_norm,
                    })

    return {
        "gaps": gaps,
        "unplanned": unplanned,
        "source_tracking_incomplete": source_tracking_incomplete,
    }


# ── Changelog entry builder ───────────────────────────────────────────

def _build_changelog_entry(task: dict, wiki_files: list,
                           changed_source_files: list) -> str | None:
    """Build a formatted CHANGELOG entry for this merge.

    Returns None if no wiki files affected and no notable changes.
    """
    if not wiki_files:
        return None

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    task_id = task.get("id", "???")
    title = task.get("title", "Sin título")
    category = task.get("category", "tools")
    author = task.get("assigned_to", "taskboard")
    if author == "unassigned":
        author = "taskboard"

    # Determine the most relevant wiki file
    primary_wiki = wiki_files[0]
    # For economy: always prefer tablas_precios.md
    if category == "finance" or _is_economy_change(changed_source_files):
        for wf in wiki_files:
            if "economia" in wf:
                primary_wiki = wf
                break

    # Build affected files summary
    sources_summary = ", ".join(changed_source_files[:5])
    if len(changed_source_files) > 5:
        sources_summary += f" (+{len(changed_source_files) - 5} más)"

    entry = (
        f"\n## {today} | {primary_wiki} | Merge task {task_id}\n"
        f"- **Campo**: Revisión post-merge\n"
        f"- **Anterior**: ---\n"
        f"- **Nuevo**: {title}\n"
        f"- **Motivo**: Task #{task_id.split('-')[-1] if '-' in task_id else task_id} completada y mergeada a develop\n"
        f"- **Autor**: {author}\n"
        f"- **Fuente en código**: {sources_summary}\n"
    )

    # If multiple wiki files, add secondary entries
    for wf in wiki_files[1:3]:  # max 2 extra
        entry += (
            f"\n## {today} | {wf} | Revisión sugerida por task {task_id}\n"
            f"- **Campo**: Verificar si requiere actualización\n"
            f"- **Anterior**: ---\n"
            f"- **Nuevo**: Revisar cambios de: {sources_summary}\n"
            f"- **Motivo**: Archivos fuente modificados en task #{task_id.split('-')[-1] if '-' in task_id else task_id}\n"
            f"- **Autor**: {author} (auto-sugerido)\n"
            f"- **Fuente en código**: {sources_summary}\n"
        )

    return entry


# ── Wiki update suggestion ────────────────────────────────────────────

def _generate_wiki_suggestions(task: dict, affected_wiki_files: list,
                               changed_files: list) -> dict:
    """Generate human-readable suggestions for each affected wiki file.

    Returns {wiki_file: suggestion_text}
    """
    suggestions = {}
    title = task.get("title", "Sin título")
    desc = task.get("description", "")
    category = task.get("category", "tools")

    for wf in affected_wiki_files:
        lines = [
            f"### Revisión sugerida por task {task.get('id', '???')}",
            f"",
            f"**Tarea**: {title}",
        ]
        if desc:
            lines.append(f"**Descripción**: {desc[:200]}")
        lines.append(f"**Categoría**: {category}")
        lines.append(f"**Archivos modificados**: {', '.join(changed_files[:8])}")
        lines.append(f"")
        lines.append(f"**Acción requerida**: Revisar si la información en este archivo wiki "
                      f"sigue siendo 100% correcta después de estos cambios.")
        suggestions[wf] = "\n".join(lines)

    return suggestions


# ── Commit changelog ──────────────────────────────────────────────────

def _commit_changelog_entry(entry: str) -> tuple:
    """Append entry to wiki/CHANGELOG.md and commit to current branch.

    Returns (success: bool, message: str)
    """
    if not os.path.exists(CHANGELOG_PATH):
        return False, f"CHANGELOG.md no encontrado en {CHANGELOG_PATH}"

    try:
        # Append entry
        with open(CHANGELOG_PATH, "a", encoding="utf-8") as f:
            f.write(entry)

        # Stage and commit
        result = subprocess.run(
            ["git", "add", "wiki/CHANGELOG.md"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            return False, f"git add CHANGELOG.md falló: {result.stderr}"

        result = subprocess.run(
            ["git", "commit", "-m", "docs(wiki): auto-changelog post-merge taskboard"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=10,
        )
        # "nothing to commit" is OK — means CHANGELOG was already up to date
        combined = (result.stderr + " " + result.stdout).lower()
        if result.returncode != 0 and "nothing to commit" not in combined:
            return False, f"git commit CHANGELOG falló: {result.stderr or result.stdout}"

        return True, "Changelog actualizado y commiteado"
    except Exception as e:
        return False, f"Error escribiendo CHANGELOG: {e}"


# ═══════════════════════════════════════════════════════════════════════
# PUBLIC API
# ═══════════════════════════════════════════════════════════════════════

def analyze_task_for_wiki(task: dict) -> dict:
    """Main entry point. Analyze a completed task for wiki impact.

    Args:
        task: Task dict with planning_data, ai_analysis, git_branch, etc.

    Returns:
        {
            "wiki_updates_needed": bool,
            "affected_wiki_files": [str],
            "alerts": [str],
            "validation_gaps": [str],
            "unplanned_changes": [str],
            "changelog_entry": str | None,
            "wiki_suggestions": {str: str},
            "error": str | None,
        }
    """
    result = {
        "wiki_updates_needed": False,
        "affected_wiki_files": [],
        "alerts": [],
        "validation_gaps": [],
        "unplanned_changes": [],
        "changelog_entry": None,
        "wiki_suggestions": {},
        "error": None,
    }

    try:
        # Step 1: Build wiki source map
        source_map = _build_wiki_source_map()
        if not source_map:
            result["alerts"].append(
                "Wiki source map vacío — ¿existe wiki/ con archivos .md que tengan source_files?"
            )
            return result

        # Step 2: Extract planned files
        planning = task.get("planning_data", {})
        if isinstance(planning, str):
            try:
                planning = json.loads(planning)
            except Exception:
                planning = {}
        ai = task.get("ai_analysis", {})
        if isinstance(ai, str):
            try:
                ai = json.loads(ai)
            except Exception:
                ai = {}

        # Try multiple paths for planned files
        planned_files = planning.get("files_to_modify", [])
        if not planned_files:
            ai_planning = ai.get("planning", {})
            if isinstance(ai_planning, dict):
                planned_files = ai_planning.get("files_to_modify", [])

        # Step 3: Extract actual changed files
        branch_name = task.get("git_branch", "")
        base_branch = task.get("git_base_branch", "develop")

        if branch_name:
            actual_changed = _get_actual_changes(branch_name, base_branch)
            if not actual_changed:
                # Fallback: use merge commit diff
                actual_changed = _get_merge_commit_changes()
        else:
            # No branch — try merge commit diff
            actual_changed = _get_merge_commit_changes()

        if not actual_changed:
            result["alerts"].append(
                "No se pudieron determinar los archivos modificados. "
                "El branch pudo haber sido eliminado antes del wiki-sync."
            )
            return result

        # Step 4: Determine affected wiki files
        # 4a: From planned files
        planned_wiki = _files_to_wiki_files(planned_files, source_map)
        # 4b: From actual changed files
        actual_wiki = _files_to_wiki_files(actual_changed, source_map)
        # 4c: From category
        category = task.get("category", "tools")
        category_wiki = _category_to_wiki_files(category)
        # 4d: Economy override
        economy_override = []
        is_economy = _is_economy_change(actual_changed)
        if is_economy:
            economy_override = [
                "wiki/economia/tablas_precios.md",
                "wiki/economia/monedas.md",
                "wiki/economia/vip_tiers.md",
                "wiki/economia/economia_general.md",
            ]

        # Union of all sources, deduplicated and sorted
        all_affected = sorted(set(
            planned_wiki + actual_wiki + category_wiki + economy_override
        ))

        result["affected_wiki_files"] = all_affected
        result["wiki_updates_needed"] = len(all_affected) > 0

        # Step 5: Validation gaps
        validation = _detect_validation_gaps(
            actual_changed, all_affected, source_map, planned_files
        )
        result["validation_gaps"] = validation["gaps"]
        result["unplanned_changes"] = validation["unplanned"]

        # Step 6: Build alerts
        if is_economy:
            result["alerts"].append(
                "⚠️ ECONOMÍA: Esta tarea modificó archivos de precios/economía. "
                "Los siguientes archivos wiki DEBEN ser revisados: "
                + ", ".join(economy_override)
            )

        if validation["gaps"]:
            gap_list = ", ".join(validation["gaps"][:5])
            if len(validation["gaps"]) > 5:
                gap_list += f" (+{len(validation['gaps']) - 5} más)"
            result["alerts"].append(
                f"📝 SIN COBERTURA WIKI: {gap_list} — "
                f"estos archivos fueron modificados pero ningún wiki los referencia en source_files"
            )

        if validation["unplanned"]:
            unplanned_list = ", ".join(validation["unplanned"][:5])
            if len(validation["unplanned"]) > 5:
                unplanned_list += f" (+{len(validation['unplanned']) - 5} más)"
            result["alerts"].append(
                f"🔍 CAMBIOS NO PLANEADOS: {unplanned_list} — "
                f"modificados pero no estaban en planning_data.files_to_modify"
            )

        if validation["source_tracking_incomplete"]:
            for sti in validation["source_tracking_incomplete"]:
                result["alerts"].append(
                    f"🔗 SOURCE TRACKING: {sti['wiki_file']} no lista "
                    f"{sti['missing_source']} en su source_files — considera añadirlo"
                )

        # Step 7: Generate wiki suggestions
        if all_affected:
            result["wiki_suggestions"] = _generate_wiki_suggestions(
                task, all_affected, actual_changed
            )

        # Step 8: Build changelog entry
        result["changelog_entry"] = _build_changelog_entry(
            task, all_affected, actual_changed
        )

        # Step 9: If there are affected wiki files but no alerts, add an info alert
        if all_affected and not result["alerts"]:
            result["alerts"].append(
                f"📋 Wiki files relacionados: {', '.join(all_affected[:3])}"
                + (f" (+{len(all_affected) - 3} más)" if len(all_affected) > 3 else "")
                + " — revisar si necesitan actualización"
            )

    except Exception as e:
        result["error"] = str(e)
        result["alerts"].append(f"Wiki sync error (no bloquea el merge): {e}")

    return result


def commit_wiki_updates(task: dict, wiki_result: dict) -> tuple:
    """Commit the changelog entry generated by analyze_task_for_wiki.

    Args:
        task: Task dict
        wiki_result: Result dict from analyze_task_for_wiki()

    Returns:
        (success: bool, message: str)
    """
    entry = wiki_result.get("changelog_entry")
    if not entry:
        return False, "No hay entrada de changelog para commitear"

    return _commit_changelog_entry(entry)
