// modules/task-card.js — Task card detail loading, log viewer, manual exec

// ── Manual execution (legacy paste-command flow, for unassigned tasks) ──

function copyExecCommand(taskId) {
    const task = tasks.find(t => t.id === taskId);
    const cmd = task?.ai_analysis?.execution?.command;
    if (!cmd) return;
    navigator.clipboard.writeText(cmd).then(
        () => showToast('Comando copiado al portapapeles', 'success', 2500),
        () => showToast('No se pudo copiar (copia manual)', 'warn')
    );
}

async function markExecDone(taskId) {
    showLoading(true, "Marcando como terminado…");
    try {
        const r = await fetch('/api/tasks/exec-done', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id: taskId })
        });
        showLoading(false);
        const data = await r.json();
        if (r.ok && data.success) {
            showToast(data.notice || 'Pasada a review', 'success');
            fetchTasks();
        } else {
            showToast('Error al marcar terminado', 'error');
        }
    } catch (e) {
        showLoading(false);
        showToast('Error de conexión', 'error');
    }
}

function showTestFailure(id, status, output) {
    document.getElementById('test-error-output').innerText = output;
    document.getElementById('test-fail-modal').classList.add('open');
    document.getElementById('force-done-btn').onclick = async () => {
        await moveTaskWithTestCheck(id, status, true);
    };
}

function closeTestFailModal(e) {
    if (!e || e.target === document.getElementById('test-fail-modal') || e.target.closest('.action-btn') || e.target.innerText.includes("Volver")) {
        document.getElementById('test-fail-modal').classList.remove('open');
        fetchTasks();
    }
}


// ── Agent Log Viewer ──────────────────────────────────────────────

let logAutoRefreshInterval = null;

async function loadAgentLog(taskId) {
    const logEl = document.getElementById('detail-log-box');
    const statusEl = document.getElementById('log-status');
    logEl.textContent = 'Cargando log...';
    try {
        const response = await fetch(`/api/agent-log/${taskId}?lines=100`);
        const data = await response.json();
        if (data.log_exists) {
            logEl.textContent = data.log_tail || '(log vacío)';
            const lineCount = data.log_tail ? data.log_tail.split('\n').length : 0;
            let statusText = `${(data.log_size / 1024).toFixed(1)} KB · ${lineCount} líneas`;
            if (data.fallback_agent) {
                statusText += ` · via ${data.fallback_agent} (live)`;
            }
            statusEl.textContent = statusText;
        } else {
            logEl.textContent = '⚠️ No hay archivo de log para esta tarea.\n\nEl agente aún no ha comenzado a escribir, o la tarea no ha sido ejecutada.';
            statusEl.textContent = 'sin log';
        }
        logEl.scrollTop = logEl.scrollHeight;
    } catch (err) {
        logEl.textContent = 'Error al cargar el log.';
        statusEl.textContent = 'error';
    }
}

function refreshAgentLog() {
    if (activeTaskId) loadAgentLog(activeTaskId);
}

function toggleLogAutoRefresh() {
    const btn = document.getElementById('btn-log-auto');
    if (logAutoRefreshInterval) {
        clearInterval(logAutoRefreshInterval);
        logAutoRefreshInterval = null;
        btn.textContent = '▶ Auto';
        btn.style.background = '';
    } else {
        logAutoRefreshInterval = setInterval(() => {
            if (activeTaskId) loadAgentLog(activeTaskId);
        }, 2000);
        btn.textContent = '⏸ Auto';
        btn.style.background = 'var(--done-color)';
        btn.style.color = '#000';
    }
}

function loadTaskDetails(id) {
    const task = tasks.find(t => t.id === id);
    if (!task) return;

    document.getElementById('detail-title').innerText = task.title;
    document.getElementById('detail-description').innerText = task.description || 'Sin descripción.';
    const categoryBadge = document.getElementById('detail-category-badge');
    categoryBadge.innerText = task.category;
    categoryBadge.className = 'badge badge-category';
    if (task.category) {
        categoryBadge.classList.add(`category-${task.category}`);
    }
    document.getElementById('detail-branch-badge').innerText = task.git_branch ? `Rama: ${task.git_branch}` : 'Rama: sin crear (mueve a Doing)';
    document.getElementById('detail-test-command').value = task.test_command || '';
    document.getElementById('detail-verification-guide').value = task.planning_data?.verification_guide || '';

    // Show review iteration count
    try {
        const reviewBadge = document.getElementById('detail-review-iterations');
        if (reviewBadge) {
            const stageHistory = task.stage_history || [];
            const reviewCount = stageHistory.filter(h => h.stage === 'review').length;
            if (task.status === 'review' && reviewCount > 0) {
                reviewBadge.innerText = 'Revision #' + (reviewCount + 1);
                reviewBadge.style.display = 'inline-block';
            } else if (task.status === 'review') {
                reviewBadge.innerText = 'Revision #1';
                reviewBadge.style.display = 'inline-block';
            } else {
                reviewBadge.style.display = 'none';
            }
        }
    } catch(e) { /* silently ignore */ }

    // Requirements
    const reqListEl = document.getElementById('detail-requirements-list');
    const approvePanel = document.getElementById('approve-plan-panel');
    const btnAddReq = document.getElementById('btn-add-requirement-inline');
    reqListEl.innerHTML = '';

    if (task.needs_agent_generation && task.status !== 'planning') {
        reqListEl.innerHTML = `
            <div style="background: rgba(255,159,67,0.06); padding: 14px; border-radius: 8px; border: 1px solid rgba(255,159,67,0.18); color: #ff9f43; font-size:12.5px; line-height:1.5;">
                <strong>⏳ Pendiente de Planificar por IA</strong><br>
                Esta tarea fue creada desde un prompt y necesita que un agente AI la analice.<br><br>
                👉 Arrastra esta tarjeta a <strong>Planning</strong> para que la IA genere el plan.
            </div>
        `;
        approvePanel.style.display = 'none';
        btnAddReq.style.display = 'none';
    } else if (task.status === 'wishes' || task.status === 'concepts') {
        reqListEl.innerHTML = `
            <div style="background: rgba(162,155,254,0.06); padding: 14px; border-radius: 8px; border: 1px solid rgba(162,155,254,0.15); color: var(--wishes-color); font-size:12.5px; line-height:1.5;">
                <strong>💡 Idea en etapa ${task.status === 'wishes' ? 'Wishes' : 'Tasks'}</strong><br>
                Arrastrá a <strong>Planning</strong> para generar plan detallado, o directo a <strong>Doing</strong> para ejecutar ya.
                ${task.ai_analysis?.concept?.processed_at ? '<br><br>🤖 Ya analizada por IA: título y alcance generados.' : ''}
            </div>
        `;
        approvePanel.style.display = 'none';
        btnAddReq.style.display = 'none';
    } else {
        approvePanel.style.display = 'flex';
        btnAddReq.style.display = 'inline-block';

        // Plan preview (planning) + paste-command (doing awaiting manual run)
        let extraHtml = '';
        const planPrev = task.planning_data?.plan_preview;
        const planDoc = task.planning_data?.plan_doc_path;
        if (planPrev && task.status === 'planning') {
            extraHtml += `<div class="plan-preview-block">
                <strong>📋 Plan generado por IA</strong>
                ${planDoc ? `<div style="font-size:11px;color:var(--text-muted);margin-top:4px;">📄 ${escapeHtml(planDoc)}</div>` : ''}
                <pre>${escapeHtml(planPrev)}</pre>
            </div>`;
        }
        const exec = task.ai_analysis?.execution;
        if (exec && exec.awaiting && task.status === 'doing') {
            extraHtml += `<div class="exec-cmd-block">
                <strong>⚡ Ejecuta este comando en tu consola (${escapeHtml(exec.agent)})</strong>
                ${exec.binary_present === false ? `<div style="color:#ff9f43;font-size:11px;margin-top:4px;">⚠️ Binario '${escapeHtml(exec.agent)}' no encontrado en PATH.</div>` : ''}
                <code>${escapeHtml(exec.command)}</code>
                <div style="display:flex;gap:8px;">
                    <button class="btn btn-sm btn-secondary" onclick="copyExecCommand('${task.id}')">📋 Copiar</button>
                    <button class="btn btn-sm btn-primary" onclick="markExecDone('${task.id}')">✓ Marcar terminado → Review</button>
                </div>
            </div>`;
        }
        reqListEl.innerHTML = extraHtml;

        const reqs = task.planning_data?.requirements || [];
        if (reqs.length === 0) {
            reqListEl.innerHTML += '<div style="font-size:12px; color:var(--text-muted);">No hay requisitos. Agrégalos con "+ Añadir" o arrastra la tarjeta de vuelta a Planning para regenerar.</div>';
        } else {
            reqs.forEach(req => {
                const item = document.createElement('div');
                item.className = `checklist-item ${req.completed ? 'completed' : ''}`;
                item.innerHTML = `
                    <input type="checkbox" ${req.completed ? 'checked' : ''} onchange="toggleRequirement('${task.id}', '${req.id}', this.checked)">
                    <span>${escapeHtml(req.text)}</span>
                `;
                reqListEl.appendChild(item);
            });
        }
    }

    // Chat
    const chatEl = document.getElementById('detail-chat-list');
    const prevCount = parseInt(chatEl?.dataset?.lastCount || '0');
    const currentCount = (task.comments || []).length;
    chatEl.innerHTML = '';
    const comments = task.comments || [];
    if (comments.length === 0) {
        chatEl.innerHTML = '<div style="font-size:11.5px; color:var(--text-muted); text-align:center; margin-top:20px;">Sin comentarios. Envía uno para iniciar el debate.</div>';
    } else {
        comments.forEach(c => {
            const bubble = document.createElement('div');
            const isUser = (c.author === 'user');
            let agentClass = '';
            if (!isUser && c.author) {
                if (c.author === 'claude') agentClass = 'claude';
                else if (c.author === 'deepclaude') agentClass = 'deepseek';
            }
            bubble.className = `comment-bubble ${isUser ? 'user' : 'agent'} ${agentClass}`;
            const time = c.timestamp ? new Date(c.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '';
            bubble.innerHTML = `
                <span class="comment-meta">${isUser ? 'Tú' : escapeHtml(c.author).toUpperCase()} • ${time}</span>
                <span>${escapeHtml(c.text)}</span>
            `;
            chatEl.appendChild(bubble);
        });
        chatEl.scrollTop = chatEl.scrollHeight;
    }

    // Track new comments for highlighting
    try {
        if (currentCount > prevCount) {
            setTimeout(() => {
                const bubbles = chatEl.querySelectorAll('.comment-bubble');
                const newCount = currentCount - prevCount;
                for (let i = Math.max(0, bubbles.length - newCount); i < bubbles.length; i++) {
                    bubbles[i].classList.add('new-message');
                }
            }, 100);
        }
        chatEl.dataset.lastCount = currentCount;
    } catch(e) { /* silently ignore */ }

    // Approval button
    const approved = task.planning_data?.approved || false;
    const btnApprove = document.getElementById('btn-approve-plan');
    if (approved) {
        btnApprove.innerText = '✓ Plan Aprobado';
        btnApprove.className = 'btn';
        btnApprove.style.background = 'var(--done-color)';
        btnApprove.style.color = '#000';
    } else {
        btnApprove.innerText = 'Aprobar Plan';
        btnApprove.className = 'btn btn-primary';
        btnApprove.style.background = '';
        btnApprove.style.color = '';
    }
}

function loadAIReview(id) {
    const task = tasks.find(t => t.id === id);
    const summaryDiv = document.getElementById('review-ai-summary');
    if (!task?.ai_analysis?.review?.processed_at) {
        summaryDiv.style.display = 'none';
        return;
    }
    summaryDiv.style.display = 'block';
    const review = task.ai_analysis.review;
    document.getElementById('review-summary-text').innerText = review.summary || 'Sin resumen.';
    const edgeList = document.getElementById('review-edge-cases');
    edgeList.innerHTML = '';
    (review.edge_cases || []).forEach(ec => {
        const li = document.createElement('li');
        li.innerText = ec;
        edgeList.appendChild(li);
    });
}

