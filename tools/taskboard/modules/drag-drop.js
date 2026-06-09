// modules/drag-drop.js — Drag and drop handlers for Taskboard

// ── Drag & Drop ────────────────────────────────────────────────────

function dragStart(e, id) {
    // Planning lock: prevent drag if AI is actively planning this task
    if (window._loadingAgents && window._loadingAgents[id]) {
        if (typeof showToast !== 'undefined') {
            showToast('No se puede mover: la IA esta planificando esta tarea', 'warning', 3000);
        }
        e.preventDefault();
        return;
    }

    let selectedIds = typeof getSelectedTaskIds !== 'undefined' ? getSelectedTaskIds() : [];

    // Clear selection if the dragged card itself is NOT part of the selection
    if (!selectedIds.includes(id)) {
        if (typeof clearTaskSelection !== 'undefined') {
            clearTaskSelection();
        }
        selectedIds = [];
    }

    let idsToDrag = selectedIds.includes(id) ? selectedIds : [id];

    // Filter out tasks that are blocked or currently being processed by AI
    if (typeof tasks !== 'undefined') {
        idsToDrag = idsToDrag.filter(dragId => {
            const task = tasks.find(t => t.id === dragId);
            if (!task) return false;
            const isBlocked = typeof isTaskBlocked !== 'undefined' ? isTaskBlocked(task) : false;
            return !isBlocked;
        });
    }

    // Ensure we drag at least the clicked item if it somehow got filtered out
    if (idsToDrag.length === 0) {
        idsToDrag = [id];
    }

    e.dataTransfer.setData('application/json', JSON.stringify({ ids: idsToDrag, sourceId: id }));
    e.dataTransfer.setData('text/plain', id);

    idsToDrag.forEach(dragId => {
        const el = document.getElementById(dragId);
        if (el) el.classList.add('dragging');
    });

    // Show drag count badge on the cursor
    if (idsToDrag.length > 1) {
        const badge = document.createElement('div');
        badge.id = 'drag-count-badge';
        badge.className = 'drag-count-badge';
        badge.textContent = idsToDrag.length;
        document.body.appendChild(badge);
        // Position near cursor
        const moveHandler = (ev) => {
            badge.style.left = (ev.clientX + 15) + 'px';
            badge.style.top = (ev.clientY - 10) + 'px';
        };
        document.addEventListener('dragover', moveHandler);
        // Clean up
        const cleanup = () => {
            document.removeEventListener('dragover', moveHandler);
            const b = document.getElementById('drag-count-badge');
            if (b) b.remove();
        };
        e.target.addEventListener('dragend', cleanup, { once: true });
    }

}

function dragEnd(e) {
    document.querySelectorAll('.task-card.dragging').forEach(el => {
        el.classList.remove('dragging');
    });
}

function allowDrop(e) {
    e.preventDefault();
    e.currentTarget.classList.add('drag-over');
}

function dragLeave(e) {
    e.currentTarget.classList.remove('drag-over');
}

async function drop(e, status) {
    // Terminal pane drops are handled by TerminalPanel.onDrop — skip column logic
    if (e.currentTarget.dataset && e.currentTarget.dataset.terminalAgent) return;
    e.preventDefault();
    e.currentTarget.classList.remove('drag-over');

    let ids = [];
    try {
        const jsonStr = e.dataTransfer.getData('application/json');
        if (jsonStr) {
            const data = JSON.parse(jsonStr);
            ids = data.ids || [];
        }
    } catch (err) {
        console.error("Error parsing drag data:", err);
    }

    if (ids.length === 0) {
        const id = e.dataTransfer.getData('text/plain');
        if (id) ids = [id];
    }

    if (ids.length === 0) return;

    // Filter out tasks that are already in the target status
    const tasksToMove = tasks.filter(t => ids.includes(t.id) && t.status !== status);
    if (tasksToMove.length === 0) return;

    // Planning → Doing: require approved plan
    let confirmMove = false;
    for (const task of tasksToMove) {
        if (task.status === 'planning' && status === 'doing') {
            if (!(task.planning_data?.approved)) {
                confirmMove = true;
                break;
            }
        }
    }

    if (confirmMove) {
        if (!confirm('Uno o más planes no están aprobados. ¿Quieres mover las tareas a Doing de todas formas?')) return;
    }

    await moveTasksBatch(tasksToMove.map(t => t.id), status);
}

async function moveTaskDirect(id, status) {
    showLoading(true, "Actualizando...");
    try {
        const response = await fetch('/api/tasks/move', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id, status })
        });
        showLoading(false);
        const data = await response.json();
        if (data.notice) showToast(data.notice, 'info');
        showToast(`Tarjeta → ${status}`, 'success', 2500);
        fetchTasks();
    } catch (err) {
        showLoading(false);
        console.error("Error al mover tarea:", err);
        showToast("Error al mover la tarjeta", 'error');
        fetchTasks();
    }
}

async function moveTaskWithTestCheck(id, status, force, forceMerge) {
    showLoading(true, force ? "Forzando cambio..." : "Ejecutando pruebas...");
    try {
        const response = await fetch('/api/tasks/move', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id, status, force, force_merge: forceMerge || false })
        });
        showLoading(false);
        const data = await response.json();
        if (response.ok) {
            closeTestFailModal(null);
            if (data.notice) showToast(data.notice, 'info', 7000);
            showToast(`Tarjeta → ${status}`, 'success', 2500);
            fetchTasks();
        } else {
            if (data.reason === 'test_failed') {
                showTestFailure(id, status, data.output);
            } else if (data.reason === 'confirm_merge_main') {
                if (confirm(`⚠️ Esto fusionará la rama '${data.branch}' directamente en '${data.base}'.\n\n¿Continuar con el merge a ${data.base}?`)) {
                    await moveTaskWithTestCheck(id, status, force, true);
                } else {
                    showToast('Merge cancelado. La tarjeta sigue en su columna.', 'warn');
                    fetchTasks();
                }
            } else {
                showToast("Error al actualizar la tarea", 'error');
                fetchTasks();
            }
        }
    } catch (err) {
        showLoading(false);
        console.error("Error:", err);
        showToast("Error de conexión al mover la tarjeta", 'error');
        fetchTasks();
    }
}

async function moveTasksBatch(ids, status, force, forceMerge) {
    showLoading(true, "Actualizando tareas...");
    try {
        const response = await fetch('/api/tasks/move-batch', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ids, status, force, force_merge: forceMerge || false })
        });
        showLoading(false);
        const data = await response.json();
        if (response.ok && data.success) {
            let successCount = 0;
            let blockedTask = null;
            let gitNotices = [];
            
            data.results.forEach(res => {
                if (res.success) {
                    successCount++;
                    if (res.notice) gitNotices.push(res.notice);
                } else {
                    if (res.blocked) {
                        blockedTask = { id: res.id, blocked: res.blocked, status_code: res.status_code };
                    } else if (res.reason === 'blocked_by_dependency') {
                        showToast(`Tarea bloqueada: ${res.message}`, 'error', 5000);
                    } else {
                        showToast(`Error al mover tarea: ${res.reason || 'desconocido'}`, 'error');
                    }
                }
            });
            
            if (successCount > 0) {
                showToast(`${successCount} tareas movidas a ${status}`, 'success', 2500);
                if (gitNotices.length > 0) {
                    showToast(gitNotices.join('\n'), 'info', 7000);
                }
            }
            
            if (typeof clearTaskSelection !== 'undefined') {
                clearTaskSelection();
            }
            
            if (blockedTask) {
                const b = blockedTask.blocked;
                if (b.reason === 'test_failed') {
                    showTestFailure(blockedTask.id, status, b.output);
                } else if (b.reason === 'confirm_merge_main') {
                    if (confirm(`⚠️ Esto fusionará la rama '${b.branch}' directamente en '${b.base}'.\n\n¿Continuar con el merge a ${b.base}?`)) {
                        await moveTasksBatch([blockedTask.id], status, force, true);
                    } else {
                        showToast('Merge cancelado. La tarjeta sigue en su columna.', 'warn');
                        fetchTasks();
                    }
                } else {
                    showToast("Error al actualizar alguna tarea", 'error');
                    fetchTasks();
                }
            } else {
                fetchTasks();
            }
        } else {
            showToast("Error al realizar movimiento por lotes", 'error');
            fetchTasks();
        }
    } catch (err) {
        showLoading(false);
        console.error("Error batch moving:", err);
        showToast("Error de conexión al mover las tarjetas", 'error');
        fetchTasks();
    }
}


