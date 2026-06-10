// modules/modal.js — Modal dialogs for Taskboard

// ── Modals ─────────────────────────────────────────────────────────

function openNewIdeaModal() {
    document.getElementById('new-idea-form').reset();
    document.getElementById('new-idea-modal').classList.add('open');
}

function closeNewIdeaModal(e) {
    if (!e || e.target === document.getElementById('new-idea-modal') || e.target.closest('.action-btn')) {
        document.getElementById('new-idea-modal').classList.remove('open');
    }
}

async function submitNewIdea(e) {
    e.preventDefault();
    const prompt = document.getElementById('idea-prompt-field').value.trim();
    const column = document.getElementById('idea-column-field').value;
    const scope = document.getElementById('idea-scope-field').value;
    if (!prompt) return;

    // 1. Close modal immediately
    closeNewIdeaModal(null);

    // 2. Create fake card with "generating..." state
    const fakeId = 'fake-' + Date.now();
    const fakeTask = {
        id: fakeId,
        title: prompt.length > 50 ? prompt.substring(0, 50) + '...' : prompt,
        description: prompt,
        scope: scope,
        status: column,
        assigned_to: 'unassigned',
        priority: column === 'wishes' ? 'low' : 'medium',
        category: 'tools',
        test_command: '',
        git_branch: '',
        planning_data: { requirements: [], notes: '', approved: false, verification_guide: '' },
        comments: [],
        stage_history: [],
        ai_analysis: {},
        needs_agent_generation: false,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
    };
    insertFakeCard(fakeTask);

    // 3. Fire API in background
    try {
        const response = await fetch('/api/tasks/create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt, column, scope })
        });
        if (response.ok) {
            const realTask = await response.json();
            // Remove fake card
            removeFakeCard(fakeId);
            // Add real task to local list and start polling
            tasks.push(realTask);
            renderBoard();
        } else {
            removeFakeCard(fakeId);
            showToast("Error al crear la idea", 'error');
        }
    } catch (err) {
        removeFakeCard(fakeId);
        console.error("Error:", err);
        showToast("Error de conexión al crear la idea. Recarga la página.", 'error');
    }
}

function insertFakeCard(task) {
    const columnId = `list-${task.status}`;
    const column = document.getElementById(columnId);
    if (!column) return;

    // Update count
    const countEl = document.getElementById(`count-${task.status}`);
    if (countEl) countEl.innerText = parseInt(countEl.innerText) + 1;

    // Remove empty state if present
    const emptyState = column.querySelector('.empty-state');
    if (emptyState) emptyState.remove();

    const card = document.createElement('div');
    card.className = `task-card ${task.status} ai-processing`;
    card.id = task.id;
    card.innerHTML = `
        <div class="card-header">
            <div class="card-title">${escapeHtml(task.title)}</div>
        </div>
        <span class="ai-processing-badge"><span class="spinner-mini"></span> Generando con IA...</span>
        <div class="card-desc">${escapeHtml(task.description)}</div>
        <div class="card-tags">
            <span class="badge badge-priority ${task.priority}">${task.priority}</span>
            <span class="badge badge-category">generando...</span>
        </div>
        <div class="card-footer">
            <span class="model-badge model-unassigned">...</span>
            <div class="card-actions">
                <button class="action-btn action-delete" onclick="removeFakeCard('${task.id}')" title="Cancelar">
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
                </button>
            </div>
        </div>
    `;
    column.insertBefore(card, column.firstChild);
}

function removeFakeCard(fakeId) {
    const card = document.getElementById(fakeId);
    if (!card) return;
    const column = card.closest('.cards-list');
    card.remove();
    // Update count
    if (column) {
        const colId = column.id.replace('list-', '');
        const remaining = column.querySelectorAll('.task-card').length;
        const countEl = document.getElementById(`count-${colId}`);
        if (countEl) countEl.innerText = remaining;
        if (remaining === 0) {
            const icons = { wishes: '💭', concepts: '💡', planning: '📋', doing: '⚡', review: '🔍', done: '✅' };
            column.innerHTML = `<div class="empty-state"><span style="font-size: 24px;">${icons[colId] || '📋'}</span><span>Sin tareas</span></div>`;
        }
    }
}

function openEditTaskModal(id) {
    const task = tasks.find(t => t.id === id);
    if (!task) return;

    document.getElementById('task-id-field').value = task.id;
    document.getElementById('task-title-field').value = task.title;
    document.getElementById('task-desc-field').value = task.description || '';
    document.getElementById('task-test-field').value = task.test_command || '';
    document.getElementById('task-assignee-field').value = task.assigned_to || 'unassigned';
    document.getElementById('task-priority-field').value = task.priority || 'medium';
    document.getElementById('task-category-field').value = task.category || 'backend';
    document.getElementById('task-scope-field').value = task.scope || 'axolotto';
    document.getElementById('task-status-field').value = task.status || 'concepts';

    // Populate dependencies dropdown
    const depSelect = document.getElementById('task-dependencies-field');
    depSelect.innerHTML = '<option value="">(Ninguna)</option>';
    tasks.forEach(t => {
        if (t.id !== id) {
            depSelect.innerHTML += `<option value="${t.id}">${escapeHtml(t.title)} (${t.status})</option>`;
        }
    });
    const currentDeps = task.planning_data?.dependencies || [];
    depSelect.value = currentDeps.length > 0 ? currentDeps[0] : '';

    document.getElementById('task-modal').classList.add('open');
}

function closeModal(e) {
    if (!e || e.target === document.getElementById('task-modal') || e.target.closest('.action-btn')) {
        document.getElementById('task-modal').classList.remove('open');
    }
}

async function saveTask(e) {
    e.preventDefault();
    const id = document.getElementById('task-id-field').value;
    const depVal = document.getElementById('task-dependencies-field').value;
    const dependencies = depVal ? [depVal] : [];
    const body = {
        id,
        title: document.getElementById('task-title-field').value,
        description: document.getElementById('task-desc-field').value,
        test_command: document.getElementById('task-test-field').value,
        assigned_to: document.getElementById('task-assignee-field').value,
        priority: document.getElementById('task-priority-field').value,
        category: document.getElementById('task-category-field').value,
        scope: document.getElementById('task-scope-field').value,
        status: document.getElementById('task-status-field').value,
        dependencies: dependencies
    };

    showLoading(true, "Guardando...");
    try {
        const response = await fetch('/api/tasks/edit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });
        showLoading(false);
        const data = await response.json();
        if (response.ok) {
            document.getElementById('task-modal').classList.remove('open');
            showToast("Cambios guardados", 'success', 2500);
            fetchTasks();
        } else {
            showToast(data.message || "Error al guardar cambios", 'error');
        }
    } catch (err) {
        showLoading(false);
        console.error("Error:", err);
    }
}

function openDetailModal(id) {
    activeTaskId = id;
    switchTab('planning');
    loadTaskDetails(id);
    // Reset move dropdown
    const moveSelect = document.getElementById('detail-move-select');
    if (moveSelect) moveSelect.value = '';

    // Wire up refine plan button visibility
    const refineBtn = document.getElementById('btn-refine-plan');
    if (refineBtn) {
        const t = tasks.find(x => x.id === id);
        refineBtn.style.display = (t && t.status === 'planning') ? 'inline-block' : 'none';
    }

    // Wire up cancel planning button
    const cancelBtn = document.getElementById('btn-cancel-planning');
    if (cancelBtn) {
        const isActivePlanning = window._loadingAgents && window._loadingAgents[activeTaskId];
        cancelBtn.style.display = isActivePlanning ? 'inline-block' : 'none';
        cancelBtn.onclick = async () => {
            if (!confirm('Cancelar la planificacion en curso?')) return;
            await fetch('/api/tasks/plan/cancel', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({id: activeTaskId})
            });
            fetchTasks();
            closeDetailModal();
        };
    }

    document.getElementById('detail-modal').classList.add('open');
}

async function refinePlanWithFeedback() {
    const input = document.getElementById('chat-input');
    const feedback = input.value.trim();
    if (!feedback || !activeTaskId) return;
    input.value = '';

    // Show thinking
    const chatEl = document.getElementById('detail-chat-list');
    const thinkingId = 'thinking-' + Date.now();
    const thinkingBubble = document.createElement('div');
    thinkingBubble.id = thinkingId;
    thinkingBubble.className = 'comment-bubble agent thinking';
    thinkingBubble.innerHTML = '<span class="spinner-mini" style="display:inline-block;width:12px;height:12px;"></span> Refinando plan...';
    thinkingBubble.style.opacity = '0.7';
    chatEl.appendChild(thinkingBubble);
    chatEl.scrollTop = chatEl.scrollHeight;

    try {
        // Post comment first
        await fetch('/api/tasks/comment', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id: activeTaskId, author: 'user', text: feedback })
        });

        // Trigger plan regeneration with feedback
        await fetch('/api/tasks/plan/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id: activeTaskId, feedback: feedback })
        });

        const bubble = document.getElementById(thinkingId);
        if (bubble) { bubble.innerHTML = 'Plan regenerado. Revisa los requisitos actualizados.'; bubble.style.opacity = '0.8'; }
        setTimeout(() => { fetchTasks(); openDetailModal(activeTaskId); }, 2000);
    } catch (err) {
        const bubble = document.getElementById(thinkingId);
        if (bubble) { bubble.innerHTML = 'Error al refinar plan.'; bubble.style.color = '#ff5252'; }
        console.error('refinePlanWithFeedback error:', err);
    }
}

function closeDetailModal(e) {
    if (!e || e.target === document.getElementById('detail-modal') || e.target.closest('.action-btn')) {
        document.getElementById('detail-modal').classList.remove('open');
        activeTaskId = null;
        // Stop log auto-refresh
        if (logAutoRefreshInterval) {
            clearInterval(logAutoRefreshInterval);
            logAutoRefreshInterval = null;
        }
        fetchTasks();
    }
}

function switchTab(tab) {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

    if (tab === 'planning') {
        document.getElementById('btn-tab-planning').classList.add('active');
        document.getElementById('tab-planning').classList.add('active');
    } else if (tab === 'review') {
        document.getElementById('btn-tab-review').classList.add('active');
        document.getElementById('tab-review').classList.add('active');
        loadGitDiff(activeTaskId);
        loadAIReview(activeTaskId);
    } else if (tab === 'log') {
        document.getElementById('btn-tab-log').classList.add('active');
        document.getElementById('tab-log').classList.add('active');
        loadAgentLog(activeTaskId);
    }
}


// ── Interactions ──────────────────────────────────────────────────

async function toggleRequirement(taskId, reqId, completed) {
    try {
        await fetch('/api/tasks/requirements/toggle', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id: taskId, req_id: reqId, completed })
        });
        fetchTasks();
    } catch (err) { console.error("Error:", err); }
}

async function togglePlanApproval() {
    const task = tasks.find(t => t.id === activeTaskId);
    if (!task) return;
    const newVal = !(task.planning_data?.approved || false);
    try {
        await fetch('/api/tasks/plan/approve', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id: activeTaskId, approved: newVal })
        });
        fetchTasks();
    } catch (err) { console.error("Error:", err); }
}

async function sendComment() {
    const input = document.getElementById('chat-input');
    const text = input.value.trim();
    if (!text || !activeTaskId) return;
    input.value = '';

    // Show thinking indicator
    const chatEl = document.getElementById('detail-chat-list');
    const thinkingId = 'thinking-' + Date.now();
    const thinkingBubble = document.createElement('div');
    thinkingBubble.id = thinkingId;
    thinkingBubble.className = 'comment-bubble agent thinking';
    thinkingBubble.innerHTML = '<span class="spinner-mini" style="display:inline-block;"></span> Pensando...';
    thinkingBubble.style.opacity = '0.7';
    thinkingBubble.style.fontStyle = 'italic';
    chatEl.appendChild(thinkingBubble);
    chatEl.scrollTop = chatEl.scrollHeight;

    try {
        await fetch('/api/tasks/comment', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id: activeTaskId, author: 'user', text })
        });

        // Poll a few times to catch the AI response (background thread takes 10-30s)
        let attempts = 0;
        const pollForResponse = async () => {
            if (attempts >= 5) {
                const bubble = document.getElementById(thinkingId);
                if (bubble) { bubble.innerHTML = 'Sin respuesta del AI.'; bubble.style.opacity = '0.5'; }
                return;
            }
            attempts++;
            await new Promise(r => setTimeout(r, 3000));
            await fetchTasks();
            // Check if a new AI comment appeared (last comment author is not 'user')
            if (activeTaskId && typeof tasks !== 'undefined') {
                const t = tasks.find(x => x.id === activeTaskId);
                if (t && t.comments && t.comments.length > 0) {
                    const last = t.comments[t.comments.length - 1];
                    if (last.author !== 'user' && last.author !== 'system') {
                        const bubble = document.getElementById(thinkingId);
                        if (bubble) bubble.remove();
                        openDetailModal(activeTaskId); // refresh detail view
                        return;
                    }
                }
            }
            await pollForResponse();
        };
        pollForResponse();
    } catch (err) {
        const bubble = document.getElementById(thinkingId);
        if (bubble) { bubble.innerHTML = 'Error al enviar.'; bubble.style.color = 'var(--priority-high)'; }
        console.error("sendComment error:", err);
    }
}

async function sendReviewFeedback() {
    const input = document.getElementById('review-feedback-input');
    const feedback = input.value.trim();
    const requestChanges = document.getElementById('review-request-changes')?.checked || false;
    if (!feedback || !activeTaskId) return;
    input.value = '';

    const responseEl = document.getElementById('review-feedback-response');
    if (responseEl) {
        responseEl.innerHTML = '<span class="spinner-mini" style="display:inline-block;"></span> Pensando...';
        responseEl.style.color = 'var(--text-muted)';
    }

    try {
        const response = await fetch('/api/tasks/review-feedback', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id: activeTaskId, feedback, request_changes: requestChanges })
        });
        const data = await response.json();

        if (responseEl) {
            if (data.ai_response) {
                responseEl.innerText = data.ai_response;
                responseEl.style.color = 'var(--text-main)';
            } else {
                responseEl.innerText = data.notice || 'Feedback enviado.';
            }
        }
        if (data.notice && typeof showToast !== 'undefined') {
            showToast(data.notice, 'info', 5000);
        }
        // Uncheck the request changes checkbox
        const cb = document.getElementById('review-request-changes');
        if (cb) cb.checked = false;

        fetchTasks(); // Refresh board to show status change
    } catch (err) {
        console.error("sendReviewFeedback error:", err);
        if (responseEl) {
            responseEl.innerText = 'Error al enviar feedback.';
            responseEl.style.color = 'var(--priority-high)';
        }
    }
}

async function addNewRequirementPrompt() {
    const text = prompt("Ingresa el texto para el nuevo requisito:");
    if (!text || !text.trim() || !activeTaskId) return;
    const task = tasks.find(t => t.id === activeTaskId);
    if (!task) return;
    const reqs = task.planning_data ? [...(task.planning_data.requirements || [])] : [];
    reqs.push({ id: `req-${Date.now()}`, text: text.trim(), completed: false });
    try {
        await fetch('/api/tasks/requirements/edit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id: activeTaskId, requirements: reqs })
        });
        fetchTasks();
    } catch (err) { console.error("Error:", err); }
}

async function saveTestCommand() {
    if (!activeTaskId) return;
    const text = document.getElementById('detail-test-command').value.trim();
    try {
        await fetch('/api/tasks/edit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id: activeTaskId, test_command: text })
        });
        const t = tasks.find(t => t.id === activeTaskId);
        if (t) t.test_command = text;
    } catch (err) { console.error("Error:", err); }
}

async function saveVerificationGuide() {
    if (!activeTaskId) return;
    const text = document.getElementById('detail-verification-guide').value.trim();
    try {
        await fetch('/api/tasks/requirements/edit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id: activeTaskId, verification_guide: text })
        });
        const t = tasks.find(t => t.id === activeTaskId);
        if (t?.planning_data) t.planning_data.verification_guide = text;
    } catch (err) { console.error("Error:", err); }
}

async function loadGitDiff(id) {
    const diffEl = document.getElementById('detail-diff-box');
    diffEl.innerText = "Calculando Git Diff...";
    try {
        const response = await fetch(`/api/tasks/diff?id=${id}`);
        const data = await response.json();
        if (data.success && data.diff) {
            const lines = data.diff.split('\n');
            diffEl.innerHTML = '';
            lines.forEach(line => {
                const div = document.createElement('div');
                if (line.startsWith('+') && !line.startsWith('+++')) div.className = 'diff-added';
                else if (line.startsWith('-') && !line.startsWith('---')) div.className = 'diff-removed';
                div.innerText = line;
                diffEl.appendChild(div);
            });
        } else {
            diffEl.innerText = "No hay diferencias de Git para esta rama.";
        }
    } catch (err) {
        diffEl.innerText = "Error al obtener el diff.";
        console.error("Diff error:", err);
    }
}

async function deleteTask(id) {
    if (!confirm("¿Estás seguro de que deseas eliminar esta tarea?")) return;
    try {
        const response = await fetch('/api/tasks/delete', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id })
        });
        if (response.ok) { showToast("Tarea eliminada", 'success', 2500); fetchTasks(); }
        else showToast("Error al eliminar la tarea", 'error');
    } catch (err) { console.error("Error:", err); showToast("Error de conexión al eliminar", 'error'); }
}


// ── Move task from detail modal ────────────────────────────────────

async function moveTaskFromDetail(force = false) {
    if (!activeTaskId) return;
    const select = document.getElementById('detail-move-select');
    if (!select) return;
    const newStatus = select.value;
    if (!newStatus) {
        showToast('Selecciona una columna de destino', 'warn', 3000);
        return;
    }
    const task = tasks.find(t => t.id === activeTaskId);
    if (!task) return;
    if (task.status === newStatus) {
        showToast('La tarea ya está en esa columna', 'info', 2500);
        return;
    }

    showLoading(true, `Moviendo a ${newStatus}${force ? ' (forzado)' : ''}...`);
    try {
        const response = await fetch('/api/tasks/move', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id: activeTaskId, status: newStatus, force: force, skip_ai: force })
        });
        showLoading(false);
        const data = await response.json();
        if (response.ok && data.success) {
            select.value = '';
            if (data.notice) showToast(data.notice, 'info', 6000);
            showToast(`Tarea movida a ${newStatus}`, 'success', 2500);
            // Wiki sync alerts
            if (data.wiki_alerts && data.wiki_alerts.alerts && data.wiki_alerts.alerts.length > 0) {
                const hasEconomy = data.wiki_alerts.alerts.some(a => a.includes('ECONOMÍA'));
                data.wiki_alerts.alerts.forEach(alert => {
                    showToast(alert, hasEconomy ? 'error' : 'warn', hasEconomy ? 12000 : 6000);
                });
            }
            fetchTasks();
        } else {
            if (data.reason === 'test_failed') {
                if (typeof showTestFailure !== 'undefined') {
                    showTestFailure(activeTaskId, newStatus, data.output);
                } else {
                    showToast('Fallaron las pruebas. Usa "Forzar" para omitir.', 'error', 6000);
                }
            } else if (data.reason === 'confirm_merge_main') {
                if (confirm(`⚠️ Esto fusionará la rama '${data.branch}' directamente en '${data.base}'.\n\n¿Continuar con el merge?`)) {
                    moveTaskFromDetail(true);  // retry with force_merge implied via force
                }
            } else if (data.reason === 'blocked_by_dependency') {
                showToast(`Tarea bloqueada: ${data.message}`, 'error', 6000);
            } else {
                showToast(data.message || data.reason || 'Error al mover la tarea', 'error', 5000);
            }
        }
    } catch (err) {
        showLoading(false);
        console.error('Error moving task from detail:', err);
        showToast('Error de conexión al mover', 'error');
        fetchTasks();
    }
}


// ── Usage Modal ─────────────────────────────────────────────────────

let _usageData = null;

function openUsageModal() {
    document.getElementById('usage-modal').classList.add('open');
    if (!_usageData) {
        refreshUsage();
    } else {
        renderUsageCards(_usageData);
    }
}

async function initUsagePreload() {
    try {
        const r = await fetch('/api/usage');
        const data = await r.json();
        _usageData = data;
        const refreshedEl = document.getElementById('usage-refreshed');
        if (refreshedEl) {
            refreshedEl.textContent = 'Actualizado: ' + new Date(data.refreshed_at).toLocaleTimeString();
        }
        renderUsageCards(data);
    } catch (err) {
        console.error("Error al precargar el uso de IAs:", err);
    }
}

function closeUsageModal(e) {
    if (!e || e.target === document.getElementById('usage-modal') || e.target.closest('.action-btn')) {
        document.getElementById('usage-modal').classList.remove('open');
    }
}

async function refreshUsage() {
    const grid = document.getElementById('usage-grid');
    const refreshedEl = document.getElementById('usage-refreshed');
    const btn = document.getElementById('btn-refresh-usage');

    grid.innerHTML = '<div class="usage-card" style="grid-column: 1/-1; text-align: center; padding: 40px;"><span class="spinner-mini"></span> Consultando usage...</div>';
    if (btn) btn.disabled = true;
    refreshedEl.textContent = '—';

    try {
        const r = await fetch('/api/usage');
        const data = await r.json();
        _usageData = data;
        refreshedEl.textContent = 'Actualizado: ' + new Date(data.refreshed_at).toLocaleTimeString();
        renderUsageCards(data);
    } catch (err) {
        grid.innerHTML = '<div class="usage-card" style="grid-column: 1/-1; text-align: center; padding: 40px; color: var(--priority-high);">❌ Error al consultar /api/usage: ' + escapeHtml(err.message) + '</div>';
        refreshedEl.textContent = 'Error';
    } finally {
        if (btn) btn.disabled = false;
    }
}

function renderUsageCards(data) {
    const grid = document.getElementById('usage-grid');
    const providers = [
        { key: 'claude', name: 'Claude', icon: '🧡', gradient: 'model-claude' },
        { key: 'deepclaude', name: 'deepclaude', icon: '💙', gradient: 'model-deepclaude' },
        { key: 'agy', name: 'agy', icon: '💚', gradient: 'model-agy' }
    ];

    let html = '';
    for (const p of providers) {
        const d = data[p.key] || {};
        const available = d.available === true;

        if (!available) {
            const errMsg = d.error || 'No disponible';
            html += `
                <div class="usage-card">
                    <div class="usage-card-header">
                        <span class="usage-card-icon">${p.icon}</span>
                        <span class="usage-card-name">${p.name}</span>
                        <span class="usage-card-badge offline">OFFLINE</span>
                    </div>
                    <div class="usage-error">⚠️ ${escapeHtml(errMsg)}</div>
                </div>`;
            continue;
        }

        const cost = d.total_cost_usd != null ? '$' + d.total_cost_usd.toFixed(4) : '—';
        const tokensIn = d.tokens_input != null ? d.tokens_input.toLocaleString() : '—';
        const tokensOut = d.tokens_output != null ? d.tokens_output.toLocaleString() : '—';
        const tokensCacheRead = d.tokens_cache_read != null ? d.tokens_cache_read.toLocaleString() : '—';
        const tokensCacheWrite = d.tokens_cache_write != null ? d.tokens_cache_write.toLocaleString() : '—';
        const apiDur = d.duration_api_seconds != null ? formatDuration(d.duration_api_seconds) : '—';
        const wallDur = d.duration_wall_seconds != null ? formatDuration(d.duration_wall_seconds) : '—';
        const linesAdd = d.lines_added != null ? d.lines_added.toLocaleString() : '—';
        const linesRem = d.lines_removed != null ? d.lines_removed.toLocaleString() : '—';

        let quotasHtml = '';
        if (d.quotas && d.quotas.length > 0) {
            quotasHtml += '<hr class="usage-divider"><div class="usage-quotas-section">';
            quotasHtml += '<div style="font-size: 11px; font-weight: 600; color: var(--text-muted); margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px;">Model Quota</div>';
            for (const q of d.quotas) {
                const pct = q.percent;
                let barColor = '#4cd137'; // verde
                if (pct < 30) {
                    barColor = '#e84118'; // rojo
                } else if (pct < 60) {
                    barColor = '#fbc531'; // naranja
                }
                
                quotasHtml += `
                    <div class="quota-row" style="margin-bottom: 10px;">
                        <div class="quota-model-name" style="font-size: 12px; font-weight: 500; color: var(--text-main); margin-bottom: 4px; display: flex; justify-content: space-between;">
                            <span>${escapeHtml(q.model)}</span>
                            <span style="font-weight: 600; color: ${barColor}">${pct}%</span>
                        </div>
                        <div class="quota-progress-container" style="background: rgba(255,255,255,0.06); height: 6px; border-radius: 3px; overflow: hidden; margin-bottom: 3px;">
                            <div class="quota-progress-bar" style="background: ${barColor}; height: 100%; width: ${pct}%; border-radius: 3px; transition: width 0.8s ease-out;"></div>
                        </div>
                        <div class="quota-detail" style="font-size: 10px; color: var(--text-muted); text-align: right;">
                            ${escapeHtml(q.detail)}
                        </div>
                    </div>
                `;
            }
            quotasHtml += '</div>';
        }

        html += `
            <div class="usage-card">
                <div class="usage-card-header">
                    <span class="usage-card-icon">${p.icon}</span>
                    <span class="usage-card-name">${p.name}</span>
                    <span class="usage-card-badge online">ONLINE</span>
                </div>
                <div class="usage-stat-row">
                    <span class="usage-stat-label">Costo Total</span>
                    <span class="usage-stat-value cost">${cost}</span>
                </div>
                <hr class="usage-divider">
                <div class="usage-stat-row">
                    <span class="usage-stat-label">Tokens Input</span>
                    <span class="usage-stat-value">${tokensIn}</span>
                </div>
                <div class="usage-stat-row">
                    <span class="usage-stat-label">Tokens Output</span>
                    <span class="usage-stat-value">${tokensOut}</span>
                </div>
                <div class="usage-stat-row">
                    <span class="usage-stat-label">Cache Read</span>
                    <span class="usage-stat-value">${tokensCacheRead}</span>
                </div>
                <div class="usage-stat-row">
                    <span class="usage-stat-label">Cache Write</span>
                    <span class="usage-stat-value">${tokensCacheWrite}</span>
                </div>
                <hr class="usage-divider">
                <div class="usage-stat-row">
                    <span class="usage-stat-label">Duración API</span>
                    <span class="usage-stat-value">${apiDur}</span>
                </div>
                <div class="usage-stat-row">
                    <span class="usage-stat-label">Duración Wall</span>
                    <span class="usage-stat-value">${wallDur}</span>
                </div>
                <hr class="usage-divider">
                <div class="usage-stat-row">
                    <span class="usage-stat-label">Líneas Añadidas</span>
                    <span class="usage-stat-value">${linesAdd}</span>
                </div>
                <div class="usage-stat-row">
                    <span class="usage-stat-label">Líneas Eliminadas</span>
                    <span class="usage-stat-value">${linesRem}</span>
                </div>
                ${quotasHtml}
            </div>`;
    }

    grid.innerHTML = html;
}


// ── Docs Modal ──────────────────────────────────────────────────────────────

let _allDocs = [];
let _activeDocPath = null;

function openDocsModal() {
    document.getElementById('docs-modal').classList.add('open');
    document.getElementById('docs-search').value = '';
    loadDocsList();
}

function closeDocsModal(e) {
    if (!e || e.target === document.getElementById('docs-modal') || e.target.closest('.action-btn')) {
        document.getElementById('docs-modal').classList.remove('open');
    }
}

async function loadDocsList() {
    try {
        const r = await fetch('/api/docs');
        const data = await r.json();
        _allDocs = data.files || [];
        renderDocsList(_allDocs);
        // Auto-open most recent
        if (_allDocs.length > 0 && !_activeDocPath) {
            loadDoc(_allDocs[0].path);
        }
    } catch (e) {
        document.getElementById('docs-file-list').innerHTML =
            '<div style="color:var(--review-color);padding:16px;font-size:12px;">Error cargando docs</div>';
    }
}

function renderDocsList(files) {
    const el = document.getElementById('docs-file-list');
    if (!files.length) {
        el.innerHTML = '<div style="color:var(--text-muted);padding:16px;font-size:12px;">No hay docs aún</div>';
        return;
    }
    // Group by folder
    const groups = {};
    for (const f of files) {
        const folder = f.folder === '.' ? 'docs' : `docs/${f.folder}`;
        if (!groups[folder]) groups[folder] = [];
        groups[folder].push(f);
    }
    let html = '';
    for (const [folder, items] of Object.entries(groups)) {
        html += `<div class="docs-group-label">${escapeHtml(folder)}</div>`;
        for (const f of items) {
            const active = f.path === _activeDocPath ? 'docs-file--active' : '';
            const age = _relTime(f.mtime * 1000);
            html += `<div class="docs-file ${active}" onclick="loadDoc('${escapeHtml(f.path)}')" title="${escapeHtml(f.path)}">
                <span class="docs-file-name">${escapeHtml(f.name.replace('.md',''))}</span>
                <span class="docs-file-age">${age}</span>
            </div>`;
        }
    }
    el.innerHTML = html;
}

function filterDocs(query) {
    const q = query.toLowerCase();
    const filtered = q ? _allDocs.filter(f => f.name.toLowerCase().includes(q) || f.path.toLowerCase().includes(q)) : _allDocs;
    renderDocsList(filtered);
}

async function loadDoc(path) {
    _activeDocPath = path;
    renderDocsList(_activeDocPath ? _allDocs : _allDocs); // re-render to update active
    const preview = document.getElementById('docs-preview');
    preview.innerHTML = '<div style="color:var(--text-muted);padding:20px;font-size:12px;">Cargando...</div>';
    try {
        const r = await fetch(`/api/docs/content?path=${encodeURIComponent(path)}`);
        const d = await r.json();
        const html = typeof marked !== 'undefined'
            ? marked.parse(d.content || '')
            : `<pre style="white-space:pre-wrap;font-size:12px;">${escapeHtml(d.content||'')}</pre>`;
        preview.innerHTML = `<div class="docs-md-content">${html}</div>`;
    } catch (e) {
        preview.innerHTML = '<div style="color:var(--review-color);padding:20px;font-size:12px;">Error cargando archivo</div>';
    }
}

function _relTime(ms) {
    const diff = Date.now() - ms;
    const m = Math.floor(diff / 60000);
    if (m < 1) return 'ahora';
    if (m < 60) return `${m}m`;
    const h = Math.floor(m / 60);
    if (h < 24) return `${h}h`;
    return `${Math.floor(h/24)}d`;
}

// ── Doc Badge Click ─────────────────────────────────────────────────

window.openDocFromBadge = function(docPath) {
    const docsModal = document.getElementById('docs-modal');
    if (docsModal) docsModal.classList.add('open');
    const search = document.getElementById('docs-search');
    if (search) search.value = '';
    // Set before loadDocsList so it doesn't auto-open the most recent doc
    _activeDocPath = docPath;
    loadDocsList().then(() => {
        const match = _allDocs.find(f => f.path === docPath || f.path.endsWith(docPath) || docPath.endsWith(f.path));
        loadDoc(match ? match.path : docPath);
    });
};

function escapeHtml(s) {
    return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
