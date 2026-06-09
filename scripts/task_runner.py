#!/usr/bin/env python3
import sys
import os
import json
import subprocess
import re
from datetime import datetime

# Paths
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
TASKS_FILE = os.path.join(REPO_ROOT, "tasks.json")

def load_tasks():
    if not os.path.exists(TASKS_FILE):
        return {"tasks": []}
    try:
        with open(TASKS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error cargando tasks.json: {e}")
        return {"tasks": []}

def save_tasks(data):
    try:
        with open(TASKS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error guardando tasks.json: {e}")
        return False

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s-]+', '-', text)
    return text.strip('-')

# Git Helpers
def safe_git_run(cmd):
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True
        )
        return (result.returncode == 0), (result.stdout or "").strip(), (result.stderr or "").strip()
    except Exception as e:
        return False, "", str(e)

def get_current_git_branch():
    ok, stdout, _ = safe_git_run("git rev-parse --abbrev-ref HEAD")
    return stdout if ok else "main"

def show_help():
    print("""
🤖 Axolotto Task Runner CLI 🤖
Uso:
  python3 scripts/task_runner.py          - Muestra las tareas activas ('doing') y da instrucciones
  python3 scripts/task_runner.py list     - Lista las tareas agrupadas por las 5 columnas del tablero
  python3 scripts/task_runner.py plan <id> - Muestra el checklist de requisitos de una tarea
  python3 scripts/task_runner.py approve <id> - Aprueba el plan de una tarea en Planning (la hace brillar)
  python3 scripts/task_runner.py start    - Toma la primera tarea de 'todo' (o plan aprobada), crea rama Git y pasa a 'doing'
  python3 scripts/task_runner.py review   - Pasa la tarea de 'doing' a 'review' (ejecuta tests locales)
  python3 scripts/task_runner.py review <id>
  python3 scripts/task_runner.py done     - Marca en 'done' (corre tests, hace conventional commit y merge)
  python3 scripts/task_runner.py done <id>
  python3 scripts/task_runner.py help     - Muestra esta ayuda
""")

def print_task(task):
    print(f"\n==================================================")
    print(f"📌 TAREA: {task['title']}")
    print(f"🆔 ID:    {task['id']}")
    print(f"🤖 AGENTE: {task['assigned_to'].upper()}")
    print(f"🔥 PRIO:   {task['priority'].upper()} | 📂 CAT: {task['category'].upper()}")
    if task.get("git_branch"):
        print(f"🌿 RAMA:   {task['git_branch']}")
    if task.get("test_command"):
        print(f"🧪 TEST:   {task['test_command']}")
    
    plan = task.get("planning_data", {})
    approved = plan.get("approved", False)
    print(f"📋 PLAN:   {'APROBADO (Brillando ✨)' if approved else 'PENDIENTE DE APROBACIÓN'}")
    
    print(f"==================================================")
    print(f"📝 DESCRIPCIÓN:")
    print(f"{task['description']}")
    print(f"==================================================")

def get_agent_prompt(task):
    requirements_text = ""
    plan = task.get("planning_data", {})
    for req in plan.get("requirements", []):
        check = "[x]" if req.get("completed") else "[ ]"
        requirements_text += f"\n  {check} {req['text']}"

    if task['assigned_to'] == 'agy':
        return f"""
👉 [INSTRUCCIÓN PARA AGY / GEMINI]
Escribe esto en tu chat con agy:
--------------------------------------------------
agy ejecuta la tarea activa '{task['title']}' (ID: {task['id']}).
Por favor trabaja en la rama Git '{task.get('git_branch')}' y completa estos requisitos:{requirements_text}
--------------------------------------------------
"""
    elif task['assigned_to'] == 'claude':
        return f"""
👉 [INSTRUCCIÓN PARA CLAUDE]
Inicia Claude en la terminal (`claude`) y escribe:
--------------------------------------------------
Hola Claude, ejecuta la tarea '{task['title']}' (ID: {task['id']}).
Por favor trabaja en la rama Git '{task.get('git_branch')}' y completa estos requisitos:{requirements_text}
Al terminar, ejecuta `python3 scripts/task_runner.py review {task['id']}`.
--------------------------------------------------
"""
    elif task['assigned_to'] == 'deepclaude':
        return f"""
👉 [INSTRUCCIÓN PARA DEEPCLAUDE]
Inicia Deepclaude (`deepclaude`) y escribe:
--------------------------------------------------
Implementa la tarea '{task['title']}' (ID: {task['id']}) en la rama '{task.get('git_branch')}'.
Requisitos a programar:{requirements_text}
--------------------------------------------------
"""
    else:
        return "👉 Tarea asignada de forma manual. Ejecútala tú mismo."

def run_test_command(cmd):
    if not cmd:
        return True, ""
    try:
        print(f"🧪 Ejecutando pruebas de validación: {cmd}...")
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=25
        )
        success = (result.returncode == 0)
        output = (result.stdout or "") + "\n" + (result.stderr or "")
        return success, output
    except subprocess.TimeoutExpired:
        return False, "TIMEOUT: La ejecución de pruebas excedió el límite de 25 segundos."
    except Exception as e:
        return False, f"ERROR: No se pudo ejecutar el comando de pruebas: {e}"

def main():
    if len(sys.argv) > 1 and sys.argv[1] in ['help', '--help', '-h']:
        show_help()
        return

    data = load_tasks()
    tasks = data.get("tasks", [])

    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"

    if cmd == "status":
        doing_tasks = [t for t in tasks if t["status"] == "doing"]
        if not doing_tasks:
            print("\nℹ️ No hay ninguna tarea activa en 'doing' actualmente.")
            todo_tasks = [t for t in tasks if t["status"] == "todo"]
            planning_approved = [t for t in tasks if t["status"] == "planning" and t.get("planning_data", {}).get("approved")]
            
            if todo_tasks or planning_approved:
                print(f"Tienes {len(todo_tasks)} tareas listas en 'todo' y {len(planning_approved)} planes aprobados en 'planning'.")
                print("Ejecuta `python3 scripts/task_runner.py start` para comenzar a trabajar en la siguiente.")
            else:
                print("¡Todo está al día! Puedes crear o planificar más tareas en el tablero local.")
            return

        print(f"\n🚀 Hay {len(doing_tasks)} tarea(s) en ejecución:")
        for t in doing_tasks:
            print_task(t)
            print(get_agent_prompt(t))

    elif cmd == "list":
        cols = {
            "planning": [],
            "todo": [],
            "doing": [],
            "review": [],
            "done": []
        }
        for t in tasks:
            status = t.get("status", "planning")
            if status in cols:
                cols[status].append(t)
                
        print("\n📋 TABLERO KANBAN DE TAREAS (5 Columnas)")
        for col_name, list_tasks in cols.items():
            print(f"\n📁 {col_name.upper()}:")
            for t in list_tasks:
                glow = " ✨" if col_name == "planning" and t.get("planning_data", {}).get("approved") else ""
                branch = f" [{t.get('git_branch')}]" if t.get("git_branch") else ""
                print(f"  - [{t['id']}] ({t['assigned_to']}){branch} {t['title']}{glow}")
            if not list_tasks: print("  (Vacío)")

    elif cmd == "plan":
        target_id = sys.argv[2] if len(sys.argv) > 2 else None
        if not target_id:
            print("Uso: python3 scripts/task_runner.py plan <id>")
            return
            
        task = next((t for t in tasks if t["id"] == target_id), None)
        if not task:
            print(f"❌ No se encontró la tarea {target_id}")
            return
            
        print_task(task)
        print("\n📋 CHECKLIST DE REQUISITOS:")
        plan = task.get("planning_data", {})
        for req in plan.get("requirements", []):
            check = "[x]" if req.get("completed") else "[ ]"
            print(f"  {check} ({req['id']}) {req['text']}")
            
        comments = task.get("comments", [])
        if comments:
            print("\n💬 COMENTARIOS:")
            for c in comments:
                print(f"  [{c['author'].upper()}]: {c['text']}")

    elif cmd == "approve":
        target_id = sys.argv[2] if len(sys.argv) > 2 else None
        if not target_id:
            print("Uso: python3 scripts/task_runner.py approve <id>")
            return
            
        task = next((t for t in tasks if t["id"] == target_id), None)
        if not task:
            print(f"❌ No se encontró la tarea {target_id}")
            return
            
        if "planning_data" not in task:
            task["planning_data"] = {"requirements": [], "notes": "", "approved": False}
        task["planning_data"]["approved"] = True
        task["updated_at"] = datetime.now().isoformat() + "Z"
        
        if save_tasks(data):
            print(f"✨ Plan aprobado con éxito para '{task['title']}'. La tarjeta comenzará a brillar en el tablero.")

    elif cmd == "start":
        # Get next task to start (either in todo, or planning and approved)
        todo_tasks = [t for t in tasks if t["status"] == "todo"]
        if not todo_tasks:
            todo_tasks = [t for t in tasks if t["status"] == "planning" and t.get("planning_data", {}).get("approved")]
            
        if not todo_tasks:
            print("\n❌ No hay tareas listas o aprobadas para iniciar en 'todo' o 'planning'.")
            return
        
        task_to_start = todo_tasks[0]
        task_id = task_to_start["id"]
        
        # Git Branching
        current_branch = get_current_git_branch()
        task_to_start["git_base_branch"] = current_branch
        
        slug = slugify(task_to_start["title"])
        branch_name = f"task/{task_id}-{slug}"
        task_to_start["git_branch"] = branch_name
        
        print(f"🌿 Git: Creando rama '{branch_name}' desde '{current_branch}'...")
        ok, _, err = safe_git_run(f"git checkout -b {branch_name}")
        if not ok:
            ok, _, err = safe_git_run(f"git checkout {branch_name}")
            
        if not ok:
            print(f"⚠️ Advertencia Git: No se pudo crear/cambiar a rama '{branch_name}' ({err}).")
            print("El desarrollo continuará en la rama actual.")
            
        task_to_start["status"] = "doing"
        task_to_start["updated_at"] = datetime.now().isoformat() + "Z"
        
        if save_tasks(data):
            print(f"\n🚀 Tarea '{task_to_start['title']}' iniciada con éxito y movida a DOING!")
            print_task(task_to_start)
            print(get_agent_prompt(task_to_start))
        
    elif cmd == "review":
        target_id = sys.argv[2] if len(sys.argv) > 2 else None
        
        if not target_id:
            doing_tasks = [t for t in tasks if t["status"] == "doing"]
            if not doing_tasks:
                print("\n❌ No hay ninguna tarea activa en 'doing' para pasar a review.")
                return
            target_id = doing_tasks[0]["id"]
            
        found_task = next((t for t in tasks if t["id"] == target_id), None)
        if not found_task:
            print(f"\n❌ No se encontró la tarea {target_id}")
            return

        # Execute tests if set
        test_cmd = found_task.get("test_command", "")
        if test_cmd:
            success, output = run_test_command(test_cmd)
            if not success:
                print("\n==================================================")
                print("⚠️  ¡LAS PRUEBAS FALLARON PARA ESTA TAREA! ⚠️")
                print("==================================================")
                print(output)
                print("==================================================")
                confirm = input("¿Deseas forzar mover a REVIEW de todas formas? [s/N]: ").strip().lower()
                if confirm not in ['s', 'si', 'y', 'yes']:
                    print("\n🛑 Cancelado. La tarea permanece en DOING.")
                    return

        found_task["status"] = "review"
        found_task["updated_at"] = datetime.now().isoformat() + "Z"
            
        if save_tasks(data):
            print(f"\n🔍 Tarea '{found_task['title']}' movida a REVIEW con éxito.")
            guide = found_task.get("planning_data", {}).get("verification_guide", "")
            if guide:
                print("\n🎮 GUÍA DE VERIFICACIÓN MANUAL:")
                print(guide)

    elif cmd == "done":
        target_id = sys.argv[2] if len(sys.argv) > 2 else None
        
        if not target_id:
            review_tasks = [t for t in tasks if t["status"] == "review"]
            if not review_tasks:
                print("\n❌ No hay tareas en 'review' listas para completar.")
                return
            target_id = review_tasks[0]["id"]
            
        found_task = next((t for t in tasks if t["id"] == target_id), None)
        if not found_task:
            print(f"\n❌ No se encontró la tarea {target_id}")
            return

        # Run tests check
        test_cmd = found_task.get("test_command", "")
        if test_cmd:
            success, output = run_test_command(test_cmd)
            if not success:
                print("\n==================================================")
                print("⚠️  ¡LAS PRUEBAS FALLARON! ⚠️")
                print("==================================================")
                print(output)
                print("==================================================")
                confirm = input("¿Deseas forzar marcar la tarea como DONE de todas formas? [s/N]: ").strip().lower()
                if confirm not in ['s', 'si', 'y', 'yes']:
                    print("\n🛑 Cancelado. La tarea permanece en REVIEW.")
                    return

        # Conventional commit and Merge
        branch_name = found_task.get("git_branch", "")
        base_branch = found_task.get("git_base_branch", "main")
        
        if branch_name:
            print(f"📦 Git: Creando commit para la tarea {target_id}")
            cat = found_task.get("category", "feat")
            prefix = "fix" if cat == "bug" else "docs" if cat == "docs" else "feat"
            
            commit_msg = f"{prefix}({target_id}): {found_task['title']}\n\nRequisitos completados:\n"
            plan = found_task.get("planning_data", {})
            for req in plan.get("requirements", []):
                check = "[x]" if req.get("completed") else "[ ]"
                commit_msg += f"- {check} {req['text']}\n"
                
            safe_git_run("git add .")
            commit_ok, _, err = safe_git_run(f'git commit -m "{commit_msg}"')
            if commit_ok:
                print(f"🔀 Git: Fusionando rama '{branch_name}' en '{base_branch}'")
                checkout_ok, _, err = safe_git_run(f"git checkout {base_branch}")
                if checkout_ok:
                    merge_ok, _, err = safe_git_run(f"git merge {branch_name}")
                    if merge_ok:
                        safe_git_run(f"git branch -d {branch_name}")
                        print("✓ Integración Git completada con éxito.")
                    else:
                        print(f"⚠️ Error al fusionar en Git: {err}. Los cambios siguen en la rama '{branch_name}'.")
                else:
                    print(f"⚠️ Error al regresar a la rama '{base_branch}': {err}.")
            else:
                print(f"⚠️ Advertencia Git: No había cambios nuevos o el commit falló: {err}.")

        found_task["status"] = "done"
        found_task["updated_at"] = datetime.now().isoformat() + "Z"
            
        if save_tasks(data):
            print(f"\n🟢 Tarea '{found_task['title']}' marcada como DONE e integrada exitosamente.")
            
    else:
        print(f"\n❌ Comando desconocido: {cmd}")
        show_help()

if __name__ == '__main__':
    main()
