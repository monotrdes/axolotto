// app.js — Core application logic for Axolotto Taskboard
// Global state, data fetching, board rendering, utilities

let tasks = [];
let activeTaskId = null;
let aiPollIntervals = {};
let doneLimitExpanded = false;
let gitHealthData = null;

// ── Filter State ───────────────────────────────────────────────────
let activeFilters = { priority: '', category: '', scope: '', worktreeStatus: '' };

function setFilter(type, value) {
    activeFilters[type] = value;
    updateFilterButtons();
    renderBoard();
}

function applyFilters(taskList) {
    return taskList.filter(t => {
        if (activeFilters.priority && t.priority !== activeFilters.priority) return false;
        if (activeFilters.category && t.category !== activeFilters.category) return false;
        if (activeFilters.scope) {
            const scope = t.scope || 'axolotto';
            if (scope !== activeFilters.scope) return false;
        }
        if (activeFilters.worktreeStatus) {
            const wt = gitHealthData?.worktrees?.find(w => w.task_id === t.id);
            const ws = activeFilters.worktreeStatus;
            if (ws === 'limpiables') {
                // no_commits, orphaned, or merged
                if (!wt || !['no_commits', 'orphaned', 'merged'].includes(wt.status)) return false;
            } else if (ws === 'worktrees') {
                if (!wt) return false;
            } else if (ws === 'reposucio') {
                // repo dirty is global, show all on click
            } else if (ws === 'stale') {
                if (!wt || wt.status !== 'stale') return false;
            } else if (ws === 'mergeables') {
                if (!wt || wt.status !== 'mergeable') return false;
            } else if (ws === 'conflictos') {
                if (!wt || wt.status !== 'conflicts') return false;
            }
        }
        return true;
    });
}

function updateFilterButtons() {
    ['priority', 'category', 'scope'].forEach(type => {
        document.querySelectorAll(`[data-filter="${type}"]`).forEach(btn => {
            const isActive = btn.dataset.value === activeFilters[type];
            btn.classList.toggle('filter-btn-active', isActive);
        });
    });
}

function updateCategoryFilterButtons() {
    const group = document.getElementById('filter-category-group');
    if (!group) return;
    const categories = [...new Set(tasks.map(t => t.category).filter(Boolean))].sort();
    const current = activeFilters.category;
    // Keep the "Todas" button, rebuild the rest
    group.innerHTML = `<span class="filter-label">Categoría:</span>
        <button class="filter-btn ${current === '' ? 'filter-btn-active' : ''}" onclick="setFilter('category', '')" data-filter="category" data-value="">Todas</button>
        ${categories.map(c => `<button class="filter-btn ${current === c ? 'filter-btn-active' : ''}" onclick="setFilter('category', '${c}')" data-filter="category" data-value="${c}">${escapeHtml(c)}</button>`).join('')}
    `;
}

async function fetchTasks() {
    try {
        const response = await fetch('/api/tasks');
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        tasks = data.tasks || [];
        updateCategoryFilterButtons();
        renderBoard();
        if (activeTaskId) loadTaskDetails(activeTaskId);
        _fetchErrorShown = false;

    } catch (err) {
        console.error("Error cargando tareas:", err);
        if (!_fetchErrorShown) {
            showToast("No pude cargar las tareas del servidor. ¿Está corriendo en :8181?", 'error', 8000);
            _fetchErrorShown = true;
        }
    }
}


// ── Board Rendering ────────────────────────────────────────────────

function isTaskBlocked(task) {
    const deps = task.planning_data?.dependencies || [];
    if (deps.length === 0) return false;
    for (const depId of deps) {
        const depTask = tasks.find(t => t.id === depId);
        if (depTask && depTask.status !== 'done') {
            return true;
        }
    }
    return false;
}

function renderBoard() {
    const columns = {
        wishes: document.getElementById('list-wishes'),
        concepts: document.getElementById('list-concepts'),
        planning: document.getElementById('list-planning'),
        doing: document.getElementById('list-doing'),
        review: document.getElementById('list-review'),
        done: document.getElementById('list-done')
    };

    const counts = { wishes: 0, concepts: 0, planning: 0, doing: 0, review: 0, done: 0 };

    Object.values(columns).forEach(el => el.innerHTML = '');

    const visibleTasks = applyFilters(tasks);

    // First pass: Calculate accurate counts (and fix legacy statuses on task objects)
    visibleTasks.forEach(task => {
        let status = task.status || 'concepts';
        if (!counts.hasOwnProperty(status)) {
            if (status === 'todo') { task.status = 'concepts'; status = 'concepts'; }
            else { task.status = 'concepts'; status = 'concepts'; }
        }
        counts[status]++;
    });

    const maxOtherCount = Math.max(
        counts.wishes,
        counts.concepts,
        counts.planning,
        counts.doing,
        counts.review
    );
    const doneLimit = Math.max(10, maxOtherCount);
    let renderedDoneCount = 0;

    visibleTasks.forEach(task => {
        const finalStatus = task.status || 'concepts';

        // Limit the rendering of the done column
        if (finalStatus === 'done' && !doneLimitExpanded) {
            renderedDoneCount++;
            if (renderedDoneCount > doneLimit) {
                return; // Skip rendering this task card
            }
        }

        const card = document.createElement('div');
        const isBlocked = isTaskBlocked(task);

        let cardClass = `task-card ${finalStatus}`;
        if (task.planning_data && task.planning_data.approved) cardClass += ' glow-approved';
        if (isBlocked) cardClass += ' blocked-task';
        const isPlanning = task.status === 'planning';
        const isAiPlanning = isPlanning && (
            (window._loadingAgents && window._loadingAgents[task.id]) ||
            (task.ai_analysis && task.ai_analysis.planning && task.ai_analysis.planning.in_progress)
        );
        if (isAiPlanning) cardClass += ' task-card--planning-active';

        card.className = cardClass;
        card.id = task.id;
        card.draggable = !isBlocked;
        card.ondragstart = (e) => dragStart(e, task.id);
        card.ondragend = dragEnd;
        card.onclick = (e) => {
            if (e.target.closest('.action-btn') || e.target.closest('.badge')) {
                return;
            }
            openDetailModal(task.id);
        };
        card.ondblclick = (e) => {
            if (e.target.closest('.action-btn') || e.target.closest('.badge')) {
                return;
            }
            openDetailModal(task.id);
        };

        // Model label
        let modelLabel = task.assigned_to || "Manual";
        let modelClass = modelLabel === 'unassigned' ? 'model-unassigned' : `model-${modelLabel}`;
        if (!['claude','deepclaude','agy','unassigned'].includes(modelLabel)) {
            modelClass = 'model-unassigned';
        }

        // Test badge
        const testBadge = task.test_command ? `<span class="badge badge-test" title="${escapeHtml(task.test_command)}">🧪 test</span>` : '';

        // Progress badge (requirements only — clean and simple)
        let progressBadge = '';
        if (task.planning_data?.requirements?.length > 0) {
            const total = task.planning_data.requirements.length;
            const done = task.planning_data.requirements.filter(r => r.completed).length;
            progressBadge = `<span class="badge badge-progress">${done}/${total} reqs</span>`;
        }

        // Git Sync Status (siempre trabajaremos en dev)
        let gitSyncBadge = '';
        if (task.status === 'done' && task.git_branch) {
            const inDev = task.git_in_dev !== false && task.git_in_dev !== 0;
            if (!inDev) {
                const errorMsg = task.git_commit_error || 'Error desconocido';
                gitSyncBadge = `<span class="badge" style="background: rgba(255,82,82,0.12); color: var(--review-color); border: 1px solid rgba(255,82,82,0.3);" title="Error de Git: ${escapeHtml(errorMsg)}. Ejecuta el merge manualmente desde la terminal.">⚠️ No en dev</span>`;
            } else {
                gitSyncBadge = `<span class="badge" style="background: rgba(29,209,161,0.08); color: var(--done-color); border: 1px solid rgba(29,209,161,0.2);" title="Cambios integrados con éxito en la rama base (dev)">✓ en dev</span>`;
            }
        }

        // Wiki sync badge
        let wikiSyncBadge = '';
        if (task.status === 'done' && task.wiki_sync_data) {
            const wsd = task.wiki_sync_data;
            if (wsd.status === 'pending') {
                const alertPreview = (wsd.alerts || []).slice(0, 2).join('; ');
                wikiSyncBadge = `<span class="badge badge-wiki-pending" title="Wiki necesita actualización: ${escapeHtml(alertPreview)}">📝 wiki pendiente</span>`;
            } else if (wsd.status === 'done') {
                wikiSyncBadge = `<span class="badge badge-wiki-done" title="Wiki actualizado y changelog registrado">📝 wiki OK</span>`;
            }
        }

        // Git badge
        const gitBadge = task.git_branch ? `<span class="badge badge-git" title="${escapeHtml(task.git_branch)}">🌿 ${escapeHtml(task.git_branch.split('/').pop())}</span>` : '';

        // Dependency badge
        let dependencyBadge = '';
        if (isBlocked) {
            const incompleteDeps = [];
            const deps = task.planning_data?.dependencies || [];
            deps.forEach(depId => {
                const depTask = tasks.find(t => t.id === depId);
                if (depTask && depTask.status !== 'done') {
                    incompleteDeps.push(depTask.title);
                }
            });
            const depText = incompleteDeps.join(', ');
            dependencyBadge = `<span class="badge" style="background: rgba(255,82,82,0.1); color: var(--review-color); border: 1px solid rgba(255,82,82,0.25);" title="Depende de: ${escapeHtml(depText)}">🔒 Bloqueada</span>`;
        } else if (task.planning_data?.dependencies?.length > 0) {
            dependencyBadge = `<span class="badge" style="background: rgba(29,209,161,0.1); color: var(--done-color); border: 1px solid rgba(29,209,161,0.25);">🔗 Desbloqueada</span>`;
        }

        // Agent status badge for doing tasks (manual execution)
        let statusBadge = '';
        if (finalStatus === 'doing') {
            const agent = task.assigned_to !== 'unassigned' ? task.assigned_to : 'manual';
            statusBadge = `<span class="badge agent-elapsed" style="background:rgba(255,159,67,0.1);color:var(--doing-color);border:1px solid rgba(255,159,67,0.25);">⚡ ${escapeHtml(agent)}</span>`;
        }

        // AI processing badge
        let aiBadgeHtml = '';
        const aiAnalysis = task.ai_analysis || {};
        const planningInfo = aiAnalysis.planning || {};
        const conceptInfo = aiAnalysis.concept || {};
        const modelUsed = planningInfo.model_used || conceptInfo.model_used || '';

        if (modelUsed) {
            const modelLabel = modelUsed.length > 30 ? modelUsed.split('[')[0].trim() : modelUsed;
            aiBadgeHtml = `<span class="task-badge task-ai-badge" title="Procesado por: ${escapeHtml(modelUsed)}">AI: ${escapeHtml(modelLabel)}</span>`;
        } else if (window._loadingAgents && window._loadingAgents[task.id]) {
            aiBadgeHtml = `<span class="task-badge task-ai-badge task-ai-badge--planning" title="AI planificando..."><span class="spinner-mini-inline"></span> Planificando...</span>`;
        }

        // Doc badge
        let docBadgeHtml = '';
        const planDocPath = (task.planning_data && task.planning_data.plan_doc_path) || '';
        if (planDocPath) {
            docBadgeHtml = `<span class="task-badge task-doc-badge" onclick="event.stopPropagation(); openDocFromBadge('${escapeHtml(planDocPath)}')" title="Ver plan: ${escapeHtml(planDocPath)}" style="cursor:pointer;">Plan</span>`;
        }

        // Determine if we're in Plan A (Agy orchestrator) or Plan B (Chat AI)
        const isPlanA = (window.AgyGateway && window.AgyGateway.connected);
        const activePlan = (window.AgyGateway && window.AgyGateway.activePlan) || 'B';

        // Execution command box for doing tasks
        let execCmdHtml = '';
        if (task.status === 'doing') {
            const execAgent = (task.ai_analysis && task.ai_analysis.execution && task.ai_analysis.execution.agent) || task.assigned_to || 'claude';
            const execCmd = (task.ai_analysis && task.ai_analysis.execution && task.ai_analysis.execution.command) || '';

            if (isPlanA && execCmd) {
                // Plan A: show terminal command with copy button
                execCmdHtml = `<div class="card-exec-cmd" onclick="event.stopPropagation()" title="Ejecuta este comando en tu terminal para que el agente trabaje en esta tarea">
                    <span class="exec-cmd-icon">${{claude:'🧠',deepclaude:'🔮',agy:'🌿',ollama:'🖥️'}[execAgent] || '🤖'}</span>
                    <code class="exec-cmd-text">${escapeHtml(execCmd)}</code>
                    <button class="exec-cmd-copy" onclick="event.stopPropagation(); navigator.clipboard.writeText('${escapeHtml(execCmd).replace(/'/g, "\\'")}'); this.textContent='Copiado!'; setTimeout(()=>this.textContent='Copy',1500)" title="Copiar comando">Copy</button>
                </div>`;
            } else if (isPlanA) {
                // Plan A without command: show hint
                execCmdHtml = `<div class="card-exec-cmd card-exec-cmd--hint" onclick="event.stopPropagation()">
                    <span class="exec-cmd-icon">💻</span>
                    <span class="exec-cmd-text">Abre la tarea y ejecuta el agente <strong>${escapeHtml(execAgent)}</strong> manualmente en tu terminal</span>
                </div>`;
            } else {
                // Plan B (Chat AI): show friendly message
                const agentIcons = {claude:'🧠', deepclaude:'🔮', agy:'🌿', ollama:'🖥️'};
                const icon = agentIcons[execAgent] || '💬';
                execCmdHtml = `<div class="card-exec-cmd card-exec-cmd--chat" onclick="event.stopPropagation()">
                    <span class="exec-cmd-icon">${icon}</span>
                    <span class="exec-cmd-text-chat">Trabajando con IA en chat — <strong>${execAgent}</strong> procesa esta tarea</span>
                </div>`;
            }
        }

        // Git health badge from worktree scan
        let gitHealthBadge = '';
        if (gitHealthData && task.git_branch) {
            const wt = gitHealthData.worktrees?.find(w => w.task_id === task.id);
            if (wt) {
                if (wt.status === 'mergeable') {
                    gitHealthBadge = `<span class="badge badge-git-mergeable" title="Rama lista para merge — ${wt.commits_ahead} commits ahead" onclick="event.stopPropagation(); mergeTaskBranch('${task.id}')">🔀 merge listo</span>`;
                } else if (wt.status === 'stale') {
                    gitHealthBadge = `<span class="badge badge-git-stale" title="Worktree sin actividad por ${wt.days_since_last_commit}días">🕐 stale ${Math.round(wt.days_since_last_commit)}d</span>`;
                } else if (wt.status === 'conflicts') {
                    gitHealthBadge = `<span class="badge badge-git-conflict" title="Merge base divergió — posible conflicto">⚠️ conflicto</span>`;
                }
            } else if (task.status === 'done' && task.git_in_dev === 0) {
                // Task done but branch not merged and no worktree found
                gitHealthBadge = `<span class="badge badge-git-stale" title="Rama sin worktree, posiblemente abandonada">👻 sin WT</span>`;
            }
        }

        card.innerHTML = `
            <div class="card-header">
                <div class="card-title">${escapeHtml(task.title)}</div>
            </div>
            <div class="card-desc">${escapeHtml(task.description || 'Sin descripción')}</div>
            <div class="card-tags">
                <span class="badge badge-priority ${task.priority}">${task.priority}</span>
                <span class="badge badge-category category-${escapeHtml(task.category)}">${escapeHtml(task.category)}</span>
                ${task.scope === 'taskboard' ? '<span class="badge" style="background:rgba(67,100,247,0.12);color:#6FB1FC;border:1px solid rgba(67,100,247,0.2);font-size:9px;">🔧 taskboard</span>' : ''}
                ${task.scope === 'axolotto' || !task.scope ? '<span class="badge badge-axolotto" title="Tarea del proyecto Axolotto">👾 axolotto</span>' : ''}
                ${testBadge}
                ${progressBadge}
                ${gitSyncBadge}
                ${wikiSyncBadge}
                ${statusBadge}
                ${aiBadgeHtml}
                ${docBadgeHtml}
                ${gitHealthBadge}
                ${gitBadge}
                ${dependencyBadge}
            </div>
            ${execCmdHtml}
            <div class="card-footer" onclick="event.stopPropagation()">
                <span class="model-badge ${modelClass}">${modelLabel}</span>
                <span class="task-id-badge" onclick="copyTaskId('${escapeHtml(task.id)}')" title="Copiar ID: ${escapeHtml(task.id)}">#${escapeHtml(task.id.split('-').pop())}</span>
                <div class="card-actions">
                    <button class="action-btn" onclick="openEditTaskModal('${task.id}')" title="Editar">
                        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 20h9"></path><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path></svg>
                    </button>
                    <button class="action-btn action-delete" onclick="deleteTask('${task.id}')" title="Eliminar">
                        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg>
                    </button>
                </div>
            </div>
        `;
        columns[finalStatus].appendChild(card);
    });

    // Update counts and empty states
    Object.keys(counts).forEach(col => {
        document.getElementById(`count-${col}`).innerText = counts[col];
        if (counts[col] === 0) {
            const icons = { wishes: '💭', concepts: '📌', planning: '📋', doing: '⚡', review: '🔍', done: '✅' };
            columns[col].innerHTML = `
                <div class="empty-state">
                    <span style="font-size: 24px;">${icons[col]}</span>
                    <span>Sin tareas</span>
                </div>
            `;
        }
    });

    // Add show more / show less button for done column if needed
    if (counts.done > doneLimit) {
        const showMoreContainer = document.createElement('div');
        showMoreContainer.className = 'done-show-more';
        if (!doneLimitExpanded) {
            showMoreContainer.innerHTML = `
                <button class="btn btn-secondary btn-sm" onclick="expandDoneColumn(event)">
                    👁️ Ver más (${counts.done - doneLimit} ocultas)
                </button>
            `;
        } else {
            showMoreContainer.innerHTML = `
                <button class="btn btn-secondary btn-sm" onclick="collapseDoneColumn(event)">
                    ▲ Ver menos
                </button>
            `;
        }
        columns.done.appendChild(showMoreContainer);
    }

}

function expandDoneColumn(event) {
    if (event) event.stopPropagation();
    doneLimitExpanded = true;
    renderBoard();
}

function collapseDoneColumn(event) {
    if (event) event.stopPropagation();
    doneLimitExpanded = false;
    renderBoard();
}

// ── Toasts ─────────────────────────────────────────────────────────

function showToast(msg, type = 'info', timeout = 5000) {
    if (!msg) return;
    const container = document.getElementById('toast-container');
    if (!container) return;
    const icons = { success: '✅', error: '❌', warn: '⚠️', info: 'ℹ️' };
    const el = document.createElement('div');
    el.className = `toast ${type}`;
    el.innerHTML = `
        <span class="toast-icon">${icons[type] || icons.info}</span>
        <span class="toast-msg">${escapeHtml(String(msg))}</span>
        <span class="toast-close">✕</span>
    `;
    const remove = () => {
        el.classList.remove('show');
        setTimeout(() => el.remove(), 240);
    };
    el.querySelector('.toast-close').onclick = remove;
    container.appendChild(el);
    requestAnimationFrame(() => el.classList.add('show'));
    if (timeout > 0) setTimeout(remove, timeout);
}

let _fetchErrorShown = false;

// ── Loading ────────────────────────────────────────────────────────

function showLoading(active, text = "Cargando...") {
    const el = document.getElementById('loading-indicator');
    document.getElementById('loading-text').innerText = text;
    if (active) el.classList.add('active');
    else el.classList.remove('active');
}


// ── Restart Axolotto Ecosystem ────────────────────────────────────

async function restartAxo() {
    const btn = document.getElementById('btn-restart-axo');
    if (!confirm('¿Reiniciar todo el ecosistema Axolotto (backend + frontend + anvil)?\n\nEl taskboard se mantendrá funcionando.')) return;

    btn.disabled = true;
    btn.classList.add('btn-restart-loading');
    btn.innerHTML = '<span class="spinner-mini"></span> Reiniciando...';

    try {
        const response = await fetch('/api/restart-axo', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: '{}' });
        if (response.ok) {
            // Poll until restart completes (check backend health)
            let attempts = 0;
            const checkInterval = setInterval(async () => {
                attempts++;
                try {
                    const resp = await fetch('/api/health-proxy', { signal: AbortSignal.timeout(2000) });
                    if (resp.ok) {
                        clearInterval(checkInterval);
                        btn.classList.remove('btn-restart-loading');
                        btn.classList.add('btn-restart-success');
                        btn.innerHTML = '✓ Reiniciado';
                        showToast('Ecosistema Axolotto reiniciado. Backend :8000 · Frontend :3000', 'success', 8000);
                        setTimeout(() => {
                            btn.classList.remove('btn-restart-success');
                            btn.disabled = false;
                            btn.innerHTML = '⚡ Reiniciar Axo';
                        }, 800);
                    }
                } catch (e) {
                    // Still starting
                }
                if (attempts > 40) {
                    clearInterval(checkInterval);
                    btn.classList.remove('btn-restart-loading');
                    btn.classList.add('btn-restart-error');
                    btn.innerHTML = '⚠️ Timeout';
                    showToast('El reinicio puede seguir en background. Revisa la terminal.', 'warn', 8000);
                    setTimeout(() => {
                        btn.classList.remove('btn-restart-error');
                        btn.disabled = false;
                        btn.innerHTML = '⚡ Reiniciar Axo';
                    }, 700);
                }
            }, 3000);
        } else {
            throw new Error('API error');
        }
    } catch (err) {
        btn.classList.remove('btn-restart-loading');
        btn.classList.add('btn-restart-error');
        btn.innerHTML = '⚠️ Error';
        showToast('Error al iniciar el reinicio. Intenta: ./reiniciar.sh axo', 'error', 8000);
        setTimeout(() => {
            btn.classList.remove('btn-restart-error');
            btn.disabled = false;
            btn.innerHTML = '⚡ Reiniciar Axo';
        }, 700);
    }
}

// ── Production Server Status & Control ────────────────────────────

let _serverOnline = null; // null = unknown, true/false = known

async function fetchServerStatus() {
    try {
        const resp = await fetch('/api/server/status');
        const data = await resp.json();
        _serverOnline = data.online;
        updateServerStatusUI(data);
    } catch (err) {
        _serverOnline = false;
        updateServerStatusUI({ online: false, error: 'taskboard unreachable' });
    }
}

function updateServerStatusUI(data) {
    const dot = document.getElementById('server-status-dot');
    const label = document.getElementById('server-status-label');
    if (!dot || !label) return;

    if (data.online) {
        dot.className = 'server-status-dot server-status-dot--online';
        label.textContent = 'Prod Online';
        label.style.color = 'var(--done-color)';
    } else {
        dot.className = 'server-status-dot server-status-dot--offline';
        label.textContent = 'Prod Offline';
        label.style.color = 'var(--review-color)';
    }
}

async function serverPull() {
    const btn = document.getElementById('btn-server-pull');
    if (!confirm('Hacer git pull en el servidor de produccion?\n\nEsto actualizara el codigo desde master en el NUC.')) return;

    btn.disabled = true;
    btn.classList.add('btn-restart-loading');
    const origHTML = btn.innerHTML;
    btn.innerHTML = '<span class="spinner-mini"></span>';

    try {
        const resp = await fetch('/api/server/pull', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: '{}'
        });
        if (resp.ok) {
            btn.classList.remove('btn-restart-loading');
            btn.classList.add('btn-restart-success');
            btn.innerHTML = 'OK';
            showToast('Git pull ejecutado en produccion. Verificando...', 'info', 4000);
        } else {
            throw new Error('API error');
        }
    } catch (err) {
        btn.classList.remove('btn-restart-loading');
        btn.classList.add('btn-restart-error');
        btn.innerHTML = 'Err';
        showToast('Error al ejecutar git pull', 'error', 5000);
    }
    setTimeout(() => {
        btn.classList.remove('btn-restart-success', 'btn-restart-error');
        btn.disabled = false;
        btn.innerHTML = origHTML;
        setTimeout(fetchServerStatus, 3000);
    }, 800);
}

async function serverRestart(commandType) {
    const label = commandType === 'full' ? 'TODO el ecosistema' : 'solo Axo (sin Taskboard)';
    const btnId = commandType === 'full' ? 'btn-server-restart' : 'btn-server-restart-axo';

    if (!confirm(`Reiniciar ${label} en produccion?\n\nEl servicio estara indisponible durante el reinicio.`)) return;

    const btn = document.getElementById(btnId);
    if (!btn) return;
    btn.disabled = true;
    btn.classList.add('btn-restart-loading');
    const origHTML = btn.innerHTML;
    btn.innerHTML = '<span class="spinner-mini"></span>';

    try {
        const resp = await fetch('/api/server/restart', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ command: commandType })
        });
        if (resp.ok) {
            btn.classList.remove('btn-restart-loading');
            btn.classList.add('btn-restart-success');
            btn.innerHTML = 'OK';
            showToast(`Reinicio (${label}) iniciado en produccion. Esperando que vuelva...`, 'info', 5000);

            // Poll until server comes back
            let attempts = 0;
            const checkInterval = setInterval(async () => {
                attempts++;
                try {
                    const resp = await fetch('/api/server/status');
                    const data = await resp.json();
                    if (data.online) {
                        clearInterval(checkInterval);
                        showToast('Servidor de produccion recuperado! Esta online.', 'success', 8000);
                        fetchServerStatus();
                    }
                } catch (e) { /* still starting */ }
                if (attempts > 60) {
                    clearInterval(checkInterval);
                    showToast('Timeout (3 min) esperando al servidor. Revisa manualmente.', 'warn', 10000);
                    fetchServerStatus();
                }
            }, 3000);
        } else {
            throw new Error('API error');
        }
    } catch (err) {
        btn.classList.remove('btn-restart-loading');
        btn.classList.add('btn-restart-error');
        btn.innerHTML = 'Err';
        showToast('Error al iniciar el reinicio en produccion', 'error', 5000);
    }
    setTimeout(() => {
        btn.classList.remove('btn-restart-success', 'btn-restart-error');
        btn.disabled = false;
        btn.innerHTML = origHTML;
    }, 800);
}

// ── Environments Dashboard ────────────────────────────────────────

let _prodWasOnline = null;
let _prodPendingDeploy = false;

async function fetchEnvDashboard() {
    // Fetch local git status
    try {
        const gitResp = await fetch('/api/git');
        const gitData = await gitResp.json();
        updateLocalEnv(gitData);
    } catch (e) { /* silent */ }

    // Fetch production info (cached 30s on backend via quick health)
    try {
        const statusResp = await fetch('/api/server/status');
        const statusData = await statusResp.json();
        updateProdDot(statusData.online);

        // Alert on prod going down
        if (_prodWasOnline === true && !statusData.online) {
            showToast('🔴 PROD CAÍDO — El servidor de producción no responde', 'error', 0);
        }
        _prodWasOnline = statusData.online;

        // Fetch detailed server info
        if (statusData.online) {
            try {
                const infoResp = await fetch('/api/server/info');
                const infoData = await infoResp.json();
                updateProdEnv(infoData);
            } catch (e) { /* info fetch can fail independently */ }
        }
    } catch (e) { /* silent */ }
}

function updateLocalEnv(gitData) {
    const dot = document.getElementById('env-local-dot');
    const branch = document.getElementById('env-local-branch');
    const status = document.getElementById('env-local-status');
    if (!dot || !branch || !status) return;

    dot.className = 'env-dot online';
    branch.textContent = gitData.branch || '?';
    if (gitData.dirty) {
        status.textContent = `${gitData.uncommitted_count} files dirty`;
        status.style.color = 'var(--warn-color, #f59e0b)';
    } else if (gitData.ahead > 0) {
        status.textContent = `${gitData.ahead} commits ahead`;
        status.style.color = 'var(--text-muted)';
    } else {
        status.textContent = 'clean';
        status.style.color = 'var(--done-color)';
    }
}

function updateProdDot(online) {
    const dot = document.getElementById('env-prod-dot');
    if (!dot) return;
    dot.className = online ? 'env-dot online' : 'env-dot offline';
}

function updateProdEnv(infoData) {
    const branch = document.getElementById('env-prod-branch');
    const status = document.getElementById('env-prod-status');
    const deployBtn = document.getElementById('btn-env-deploy');
    const svcDiv = document.getElementById('env-services');
    if (!branch || !status) return;

    // Git info
    const git = infoData.git || {};
    branch.textContent = git.branch || '?';

    // Check if NUC is behind origin
    if (git.commits && git.commits.length > 0) {
        const nucHead = git.commits[0];
        // Compare with what we know from local — rough heuristic:
        // if the oldest NUC commit is older than what we just pushed, it needs deploy
        if (git.dirty) {
            status.textContent = 'dirty!';
            status.style.color = 'var(--warn-color, #f59e0b)';
        } else {
            status.textContent = 'synced';
            status.style.color = 'var(--done-color)';
        }
    }

    // Glow deploy button if NUC has fewer commits than local
    if (deployBtn && _prodPendingDeploy) {
        deployBtn.classList.add('btn-pending-deploy');
    } else if (deployBtn) {
        deployBtn.classList.remove('btn-pending-deploy');
    }

    // Service badges
    if (svcDiv) {
        const docker = infoData.docker || [];
        const pm2 = infoData.pm2 || [];
        let svcHtml = '';

        const backend = docker.find(d => d.name && d.name.includes('backend'));
        const db = docker.find(d => d.name && d.name.includes('db'));
        svcHtml += `<span class="env-service-badge ${backend ? 'up' : 'down'}">🐳 ${backend ? backend.status : 'down'}</span>`;
        svcHtml += `<span class="env-service-badge ${db ? 'up' : 'down'}">🐘 ${db ? db.status : 'down'}</span>`;

        const fe = pm2.find(p => p.name && p.name.includes('frontend'));
        svcHtml += `<span class="env-service-badge ${fe && fe.status === 'online' ? 'up' : 'down'}">⚡ ${fe ? fe.status : 'down'}</span>`;

        svcDiv.innerHTML = svcHtml;
        svcDiv.style.display = 'flex';
    }
}

async function deployToProd() {
    if (!confirm('Hacer deploy a produccion?\n\nEsto hara git pull + restart en el NUC (192.168.100.15).\nEl servicio estara indisponible unos segundos.')) return;

    const btn = document.getElementById('btn-env-deploy');
    if (!btn) return;
    btn.disabled = true;
    btn.classList.add('btn-restart-loading');
    const origHTML = btn.innerHTML;
    btn.innerHTML = '<span class="spinner-mini"></span> Deploying...';

    try {
        // Step 1: git pull on NUC
        const host = '192.168.100.15';
        const pullResp = await fetch('/api/server/pull', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: '{}'
        });

        if (!pullResp.ok) throw new Error('Pull failed');

        // Step 2: restart axo on NUC
        const restartResp = await fetch('/api/server/restart', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ command: 'axo' })
        });

        if (restartResp.ok) {
            showToast('Deploy iniciado. Esperando que prod vuelva...', 'info', 4000);

            // Poll until prod comes back
            let attempts = 0;
            const checkInterval = setInterval(async () => {
                attempts++;
                try {
                    const resp = await fetch('/api/server/status');
                    const data = await resp.json();
                    if (data.online) {
                        clearInterval(checkInterval);
                        showToast('✅ Deploy completado — Produccion online!', 'success', 8000);
                        btn.classList.remove('btn-restart-loading');
                        btn.classList.add('btn-restart-success');
                        btn.innerHTML = 'OK';
                        fetchEnvDashboard();
                    }
                } catch (e) { /* still starting */ }
                if (attempts > 60) {
                    clearInterval(checkInterval);
                    showToast('Timeout esperando a prod. Revisa manualmente.', 'warn', 10000);
                    btn.classList.remove('btn-restart-loading');
                    btn.innerHTML = origHTML;
                    btn.disabled = false;
                    fetchEnvDashboard();
                }
            }, 3000);
        } else {
            throw new Error('Restart failed');
        }
    } catch (err) {
        btn.classList.remove('btn-restart-loading');
        btn.classList.add('btn-restart-error');
        btn.innerHTML = 'Err';
        showToast('Error en el deploy: ' + err.message, 'error', 5000);
        setTimeout(() => {
            btn.classList.remove('btn-restart-error');
            btn.disabled = false;
            btn.innerHTML = origHTML;
        }, 800);
    }
}

// ── Context Refresh ─────────────────────────────────────────────────────

async function checkContextStatus() {
    try {
        const resp = await fetch('/api/context-status');
        if (!resp.ok) return;
        const data = await resp.json();
        const btn = document.getElementById('btn-refresh-context');
        if (!btn) return;

        if (data.recommend_refresh) {
            btn.classList.add('btn-context-stale');
            btn.title = 'Contexto desactualizado! ' + (data.recommend_reasons || []).join(', ') + '. Click para regenerar.';
            // Show a subtle pulse animation
            if (!btn.querySelector('.stale-dot')) {
                const dot = document.createElement('span');
                dot.className = 'stale-dot';
                dot.textContent = ' ●';
                dot.style.color = 'var(--warn, #f59e0b)';
                btn.appendChild(dot);
            }
        } else {
            btn.classList.remove('btn-context-stale');
            const dot = btn.querySelector('.stale-dot');
            if (dot) dot.remove();
        }
    } catch (e) {
        // Silently ignore — status check is non-critical
    }
}

async function refreshContext() {
    const btn = document.getElementById('btn-refresh-context');
    if (!btn) return;

    btn.disabled = true;
    const originalHTML = btn.innerHTML;
    btn.innerHTML = '<span class="spinner-mini"></span> Regenerando...';
    btn.classList.add('btn-refresh-loading');

    try {
        const resp = await fetch('/api/refresh-context', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: '{}'
        });
        if (resp.ok) {
            const data = await resp.json();
            const scopes = (data.scopes || []).map(s =>
                `${s.scope}: ${s.ok ? 'OK (' + (s.size/1024).toFixed(1) + ' KB)' : 'FAILED'}`
            ).join(', ');

            btn.classList.remove('btn-refresh-loading');
            btn.classList.add('btn-refresh-success');
            btn.innerHTML = '✓ Contexto Actualizado';
            btn.title = 'Contexto regenerado: ' + scopes;

            // Remove stale indicator
            btn.classList.remove('btn-context-stale');
            const dot = btn.querySelector('.stale-dot');
            if (dot) dot.remove();

            showToast('Contexto AI regenerado: ' + scopes, 'success', 6000);
        } else {
            throw new Error('API error ' + resp.status);
        }
    } catch (err) {
        btn.classList.remove('btn-refresh-loading');
        btn.classList.add('btn-refresh-error');
        btn.innerHTML = '⚠️ Error';
        btn.title = 'Error al regenerar. Intenta: python3 tools/taskboard/refresh_context.py';
        showToast('Error al regenerar contexto. Revisa el servidor.', 'error', 6000);
    }

    setTimeout(() => {
        btn.classList.remove('btn-refresh-success', 'btn-refresh-error');
        btn.disabled = false;
        btn.innerHTML = originalHTML;
        btn.title = 'Regenera el contexto que usan los agentes AI para planificar tareas';
        // Re-check status after a moment
        setTimeout(checkContextStatus, 2000);
    }, 3000);
}

// Auto-check context status on page load and periodically
setTimeout(checkContextStatus, 5000);  // After initial load
setInterval(checkContextStatus, 15 * 60 * 1000);  // Every 15 minutes


function formatDuration(seconds) {
    if (seconds < 60) return seconds + 's';
    if (seconds < 3600) {
        const m = Math.floor(seconds / 60);
        const s = seconds % 60;
        return m + 'm ' + s + 's';
    }
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    return h + 'h ' + m + 'm';
}

// ── Git Health Filter ──────────────────────────────────────────────

function filterByWorktreeStatus(labelKey) {
    // Map the cleaned label (no emoji/accents) to a worktree status filter
    if (labelKey === 'reposucio') {
        showToast('📝 El repositorio tiene cambios sin commitear. Haz commit o stash antes de mergear.', 'warn', 5000);
        return;
    }
    if (labelKey === 'ramassinmerge') {
        showToast('📋 Ramas task/task-* que no han sido mergeadas a la rama actual. Usa Merge All o merge individual.', 'info', 5000);
        return;
    }
    // Toggle off if already active
    if (activeFilters.worktreeStatus === labelKey) {
        activeFilters.worktreeStatus = '';
    } else {
        activeFilters.worktreeStatus = labelKey;
    }
    // Update stat button styling
    document.querySelectorAll('.git-health-stat').forEach(btn => {
        const label = (btn.textContent || '').replace(/[^a-zA-Z]/g, '').toLowerCase();
        btn.classList.toggle('git-health-stat--active', label === activeFilters.worktreeStatus);
    });
    renderBoard();
}

// ── Git Health Dashboard ────────────────────────────────────────────

async function loadGitHealth() {
    try {
        const res = await fetch('/api/git/worktrees');
        if (!res.ok) return;
        gitHealthData = await res.json();
        renderGitHealth();
    } catch {
        gitHealthData = null;
        document.getElementById('git-health-bar').style.display = 'none';
    }
}

function renderGitHealth() {
    const bar = document.getElementById('git-health-bar');
    const stats = document.getElementById('git-health-stats');
    const mergeBtn = document.getElementById('btn-merge-all');
    const cleanupBtn = document.getElementById('btn-cleanup');
    const mergeCount = document.getElementById('mergeable-count-hdr');
    const cleanupCount = document.getElementById('cleanup-count');

    if (!gitHealthData) {
        bar.style.display = 'none';
        return;
    }

    bar.style.display = 'block';
    const d = gitHealthData;

    // Always show the bar — empty state included
    const items = [];
    if (d.worktree_count > 0) {
        items.push({ cls: 'info', label: '🌿 Worktrees', count: d.worktree_count });
    }
    if (d.mergeable_count > 0) {
        items.push({ cls: 'ok', label: '🔀 Mergeables', count: d.mergeable_count });
    }
    if (d.stale_count > 0) {
        items.push({ cls: 'warn', label: '🕐 Stale', count: d.stale_count });
    }
    if (d.conflict_count > 0) {
        items.push({ cls: 'danger', label: '⚠️ Conflictos', count: d.conflict_count });
    }
    if (d.cleanable_count > 0) {
        items.push({ cls: 'info', label: '🗑️ Limpiables', count: d.cleanable_count });
    }
    if (d.repo_dirty) {
        items.push({ cls: 'warn', label: '📝 Repo sucio', count: 0 });
    }
    if (d.unmerged_branch_count > 0) {
        items.push({ cls: 'info', label: '📋 Ramas sin merge', count: d.unmerged_branch_count });
    }

    if (items.length === 0) {
        stats.innerHTML = '<span class="git-health-stat git-health-stat--ok">✅ Git limpio — sin worktrees pendientes</span>';
    } else {
        stats.innerHTML = items.map(i => {
            const countHtml = i.count > 0 ? `<span class="git-health-count">${i.count}</span>` : '';
            return `<button class="git-health-stat git-health-stat--${i.cls}" onclick="filterByWorktreeStatus('${i.label.replace(/[^a-zA-Z]/g, '').toLowerCase()}')">${i.label} ${countHtml}</button>`;
        }).join('');
    }

    mergeCount.textContent = d.mergeable_count;
    cleanupCount.textContent = d.cleanable_count;

    mergeBtn.style.display = d.mergeable_count > 0 ? '' : 'none';
    cleanupBtn.style.display = d.cleanable_count > 0 ? '' : 'none';
}

async function runCleanup() {
    if (!confirm(`¿Eliminar ${gitHealthData?.cleanable_count || 0} worktrees sin commits, huérfanos o ya mergeados?`)) return;
    try {
        const res = await fetch('/api/git/cleanup', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({}) });
        const data = await res.json();
        if (data.success) {
            showToast(`🧹 ${data.message}`, 'ok');
            loadGitHealth();
            fetchTasks(); // re-render
        } else {
            showToast(`Error: ${data.error}`, 'error');
        }
    } catch (e) {
        showToast('Error de conexión al limpiar worktrees', 'error');
    }
}

async function runMergeAll() {
    if (!gitHealthData) return;
    const mergeable = gitHealthData.worktrees.filter(w => w.status === 'mergeable');
    if (mergeable.length === 0) return;
    if (!confirm(`¿Mergear ${mergeable.length} ramas mergeables? Se mergearán en orden.`)) return;

    let ok = 0, fail = 0;
    for (const wt of mergeable) {
        try {
            const res = await fetch('/api/git/merge', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ task_id: wt.task_id })
            });
            const data = await res.json();
            if (data.success) ok++; else fail++;
        } catch { fail++; }
    }
    showToast(`🔀 Merge completado: ${ok} ok, ${fail} fallaron`, ok > 0 ? 'ok' : 'error');
    loadGitHealth();
    fetchTasks();
}

async function mergeTaskBranch(taskId) {
    if (!confirm(`¿Mergear la rama de esta tarea en la rama base?`)) return;
    try {
        const res = await fetch('/api/git/merge', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ task_id: taskId })
        });
        const data = await res.json();
        if (data.success) {
            showToast(`✅ ${data.message}`, 'ok');
            loadGitHealth();
            fetchTasks();
        } else {
            showToast(`❌ ${data.error}`, 'error');
        }
    } catch (e) {
        showToast('Error de conexión al mergear', 'error');
    }
}

function copyTaskId(taskId) {
    navigator.clipboard.writeText(taskId).then(
        () => showToast(`ID copiado: ${taskId}`, 'success', 2000),
        () => showToast('No se pudo copiar al portapapeles', 'warn')
    );
}

function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
}

document.addEventListener('DOMContentLoaded', () => {
    fetchTasks();
    loadGitHealth();
    // Auto-refresh tasks so agent-created tasks and column moves appear without manual reload
    setInterval(fetchTasks, 5000);
    // Refresh git health every 60 seconds
    setInterval(loadGitHealth, 60000);
});