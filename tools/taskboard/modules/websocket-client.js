// modules/websocket-client.js — Auto-advance detection + AI polling + retry logic
// v6: Manual agent execution — taskboard is a visual dashboard

// ── Doing Task Auto-Advance Detection ──────────────────────────────────

async function refreshDoingTasks() {
    const doingTasks = tasks.filter(t => t.status === 'doing');
    if (doingTasks.length === 0) return;

    try {
        const response = await fetch('/api/tasks');
        const data = await response.json();
        const freshTasks = data.tasks || [];

        // Detect agent auto-advance: doing → review
        const advanced = [];
        for (const local of doingTasks) {
            const ft = freshTasks.find(t => t.id === local.id);
            if (ft && ft.status !== 'doing') {
                advanced.push(ft);
            }
        }
        if (advanced.length > 0) {
            await fetchTasks();
            for (const ft of advanced) {
                if (ft.status === 'review') {
                    showToast(`Tarea completada: ${ft.title || ft.id} (Review)`, 'success', 5000);
                }
            }
            return;
        }

        // Update doing task metadata
        for (const ft of freshTasks) {
            if (ft.status === 'doing') {
                const local = tasks.find(t => t.id === ft.id);
                if (local) {
                    local._agent_elapsed = ft._agent_elapsed;
                    local._agent_status = ft._agent_status;
                    local._agent_elapsed_human = ft._agent_elapsed_human;
                    local._agent_log_tail = ft._agent_log_tail;
                    local._queue_position = ft._queue_position || 0;
                }
            }
        }
    } catch (e) { /* silent */ }
}



// ── Cancel Queued Task ────────────────────────────────────────────────

async function cancelQueuedTask(taskId) {
    if (!confirm('¿Cancelar esta tarea? Si está corriendo, el proceso será terminado. Volverá a planning.')) return;
    showLoading(true, 'Cancelando...');
    try {
        const response = await fetch('/api/tasks/cancel-queue', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id: taskId })
        });
        showLoading(false);
        const data = await response.json();
        if (response.ok && data.success) {
            showToast(data.notice || 'Tarea cancelada y devuelta a planning', 'success', 3000);
            fetchTasks();
        } else {
            showToast(data.message || 'Error al cancelar tarea', 'error');
            fetchTasks();
        }
    } catch (err) {
        showLoading(false);
        console.error('Error cancelando:', err);
        showToast('Error de conexión al cancelar', 'error');
        fetchTasks();
    }
}

