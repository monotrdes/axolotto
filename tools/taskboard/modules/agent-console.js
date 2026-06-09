// modules/agent-console.js — Agent status cards (v7, super-informativo)
// Shows agent availability, gateway connection, activity log, and plan status.

(function () {
    let _started = false;
    let _rawMessagesVisible = false;
    window._loadingAgents = {};

    const AGENT_LABELS = { claude: 'Claude', deepclaude: 'DeepClaude', agy: 'Agy', ollama: 'Qwen' };
    const AGENT_ICONS = { claude: '🧠', deepclaude: '🔮', agy: '🌿', ollama: '🖥️' };
    const AGENT_PROVIDER = {
        claude:     { provider: 'Anthropic', model: 'Claude Opus 4.8', gradient: 'claude-gradient' },
        deepclaude: { provider: 'DeepSeek',   model: 'DeepSeek V4 Pro', gradient: 'deepseek-gradient' },
        agy:        { provider: 'Google',     model: 'Gemini 3.5 Flash', gradient: 'agy-gradient' },
        ollama:     { provider: 'Ollama',     model: 'Qwen 2.5 Coder 7B', gradient: 'ollama-gradient' },
    };
    const AGENTS = ['claude', 'deepclaude', 'agy', 'ollama'];

    // Keywords for client-side recommendation
    const KEYWORDS = {
        claude:     ['frontend','ui','diseño','css','hook','modal','component','contrato','solidity','security','auth','wallet'],
        deepclaude: ['backend','api','sql','db','query','refactor','test','bug','endpoint','migration','docker','fastapi'],
        agy:        ['docs','research','investigar','analizar','game','balance','economía','plan'],
        ollama:     ['qa','lint','test','commit','format','local'],
    };

    // Specialization mapping from keyword sets
    const SPECIALIZATIONS = {
        claude:     'frontend_ux',
        deepclaude: 'backend_critical',
        agy:        'orchestrator_research',
        ollama:     'local_qa',
    };

    function escHtml(s) {
        return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
    }

    function getTaskTitle(taskId) {
        if (typeof tasks !== 'undefined' && Array.isArray(tasks)) {
            const t = tasks.find(x => x.id === taskId);
            if (t) return (t.title || taskId).slice(0, 60);
        }
        return taskId;
    }

    function getRecommended(task) {
        if (!task) return 'claude';
        const text = `${task.title||''} ${task.description||''}`.toLowerCase();
        const scores = {claude:0, deepclaude:0, agy:0};
        for (const [a, kws] of Object.entries(KEYWORDS))
            for (const kw of kws) if (text.includes(kw)) scores[a]++;
        return Object.entries(scores).sort((a,b)=>b[1]-a[1])[0][0];
    }

    // ─────────────────────────────────────────────────────────────
    // Activity Log
    // ─────────────────────────────────────────────────────────────

    const ActivityLog = {
        entries: [],
        maxEntries: 100,

        addEntry(level, agent, message, rawData) {
            if (!document.getElementById('agent-activity-log')) return;
            const entry = {
                timestamp: new Date(),
                level,
                agent,
                message,
                rawData: rawData || null
            };
            this.entries.unshift(entry);
            if (this.entries.length > this.maxEntries) this.entries.pop();
            this.renderEntry(entry);
        },

        renderEntry(entry) {
            const logEl = document.getElementById('log-entries');
            if (!logEl) return;
            const icon = (entry.agent && entry.agent.icon) ? entry.agent.icon : '🫧';
            const name = (entry.agent && entry.agent.name) ? entry.agent.name : '?';
            const timeStr = entry.timestamp.toTimeString().slice(0, 8);
            const rawToggle = _rawMessagesVisible && entry.rawData
                ? `<pre class="log-raw">${escHtml(JSON.stringify(entry.rawData, null, 2))}</pre>`
                : '';

            const div = document.createElement('div');
            div.className = `log-entry log-entry--${entry.level}`;
            div.innerHTML = `
                <span class="log-time">[${timeStr}]</span>
                <span class="log-agent-icon">${icon}</span>
                <span class="log-agent-name">${escHtml(name)}</span>
                <span class="log-arrow">→</span>
                <span class="log-message">${escHtml(entry.message)}</span>
                ${rawToggle}`;
            logEl.insertBefore(div, logEl.firstChild);

            // Cap DOM entries too
            while (logEl.children.length > this.maxEntries) {
                logEl.removeChild(logEl.lastChild);
            }
        },

        setRawVisible(visible) {
            _rawMessagesVisible = visible;
            // Re-render all entries
            const logEl = document.getElementById('log-entries');
            if (!logEl) return;
            logEl.innerHTML = '';
            const reversed = this.entries.slice().reverse();
            for (const e of reversed) {
                this.renderEntry(e);
            }
        }
    };

    // ─────────────────────────────────────────────────────────────
    // Agy Gateway
    // ─────────────────────────────────────────────────────────────

    const AgyGateway = {
        connected: false,
        url: 'ws://localhost:8642',
        activePlan: null,
        agentCount: 0,
        queueCount: 0,
        monitoredFiles: 0,
        lastDelta: null,
        activeProvider: '',
        activeModel: '',
        ws: null,
        reconnectTimer: null,
        reconnectAttempts: 0,
        maxReconnectAttempts: 3,

        connect() {
            this.disconnect();
            this.reconnectAttempts = 0;
            this._tryConnect();
        },

        _tryConnect() {
            if (this.reconnectAttempts >= this.maxReconnectAttempts) {
                this.connected = false;
                this.activePlan = 'B';
                this.updateUI();
                this._logFallback('Max reconnect attempts reached, Plan B active (REST polling)');
                return;
            }
            try {
                this.ws = new WebSocket(this.url);
                this.ws.onopen = () => {
                    this.connected = true;
                    this.reconnectAttempts = 0;
                    this.activePlan = 'A';
                    this._onConnect();
                    this.updateUI();
                    ActivityLog.addEntry('success',
                        { name: 'agy:gateway', icon: '🌐' },
                        'Gateway conectado — Plan A activo (WebSocket)');
                };
                this.ws.onmessage = (event) => {
                    try {
                        const msg = JSON.parse(event.data);
                        this._handleMessage(msg);
                    } catch (e) {
                        this._handleMessage({ type: 'raw', data: event.data });
                    }
                };
                this.ws.onclose = () => {
                    this.connected = false;
                    this.updateUI();
                    this._scheduleReconnect();
                };
                this.ws.onerror = () => {
                    this.ws.close();
                };
            } catch (e) {
                this.connected = false;
                this.reconnectAttempts++;
                this.updateUI();
                this._scheduleReconnect();
            }
        },

        _scheduleReconnect() {
            if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
            if (this.reconnectAttempts >= this.maxReconnectAttempts) {
                this.activePlan = 'B';
                this.updateUI();
                this._logFallback('Gateway unreachable, switching to Plan B (REST polling)');
                return;
            }
            this.reconnectAttempts++;
            const delay = 3000 * this.reconnectAttempts;
            this.reconnectTimer = setTimeout(() => this._tryConnect(), delay);
        },

        _onConnect() {
            if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                this.ws.send(JSON.stringify({
                    type: 'subscribe',
                    channels: ['agent_status', 'queue_updates', 'file_watch', 'plan_info']
                }));
            }
        },

        _handleMessage(msg) {
            const interpreted = interpretAgyMessage(msg);
            let level = 'info';
            let agentInfo = { name: 'agy:gateway', icon: '🌐', specialization: 'orchestrator' };

            if (msg.type === 'agent_status') {
                level = 'success';
                agentInfo = {
                    name: msg.agent || 'agy:worker',
                    icon: AGENT_ICONS[msg.agent] || '🤖',
                    specialization: msg.specialization || 'worker'
                };
                if (msg.status === 'busy') { level = 'info'; }
                if (msg.status === 'error') { level = 'error'; }
                if (msg.files_modified) {
                    this.lastDelta = { count: msg.files_modified, agent: msg.agent };
                }
                this.agentCount = msg.active_agents || this.agentCount;
                this.queueCount = msg.queue_size || this.queueCount;
                this.monitoredFiles = msg.monitored_files || this.monitoredFiles;
            } else if (msg.type === 'queue_update') {
                this.queueCount = msg.size || this.queueCount;
                agentInfo = { name: 'agy:queue', icon: '📬' };
            } else if (msg.type === 'file_change') {
                level = 'warning';
                agentInfo = { name: 'agy:watcher', icon: '📁' };
                this.monitoredFiles = msg.total || this.monitoredFiles;
            } else if (msg.type === 'error') {
                level = 'error';
            }

            ActivityLog.addEntry(level, agentInfo, interpreted, msg);
            this.updateUI();
        },

        _logFallback(reason) {
            ActivityLog.addEntry('warning',
                { name: 'agy:gateway', icon: '🌐' },
                reason);
        },

        disconnect() {
            if (this.reconnectTimer) { clearTimeout(this.reconnectTimer); this.reconnectTimer = null; }
            if (this.ws) {
                try { this.ws.close(); } catch (e) {}
                this.ws = null;
            }
            this.connected = false;
        },

        updateUI() {
            const bar = document.getElementById('agy-gateway-bar');
            if (!bar) return;
            bar.style.display = 'flex';

            const dot = document.getElementById('gateway-dot');
            const label = document.getElementById('gateway-label');
            const url = document.getElementById('gateway-url');
            const plan = document.getElementById('gateway-active-plan');
            const fallback = document.getElementById('gateway-fallback-info');
            const agCount = document.getElementById('gateway-agent-count');
            const qCount = document.getElementById('gateway-queue-count');
            const fCount = document.getElementById('gateway-file-count');
            const delta = document.getElementById('gateway-delta');

            const planLabels = {
                'A': { label: 'AGY GATEWAY', color: '#1dd1a1', dotClass: 'gateway-dot--connected', desc: 'Orquestación automática' },
                'B': { label: 'MODO CHAT', color: '#ff9f43', dotClass: 'gateway-dot--plan-b', desc: 'IA en chat controlando taskboard' },
            };
            const pl = planLabels[this.activePlan] || planLabels['B'];
            if (dot) { dot.className = 'gateway-dot ' + (pl.dotClass || 'gateway-dot--disconnected'); }
            if (label) { label.textContent = pl.label; label.style.color = pl.color; }
            if (url) { url.textContent = this.url; }

            if (this.activePlan) {
                if (plan) { plan.textContent = `Plan ${this.activePlan}`; }
                const planInfo = {
                    'A': { color: '#1dd1a1', desc: 'Gemini 3.5 Flash (agy gateway :8642)', icon: '🌿' },
                    'B': { color: '#ff9f43', desc: 'Chat IA — Claude / DeepSeek / Ollama', icon: '💬' },
                };
                const p = planInfo[this.activePlan] || { color: '#ff5252', desc: 'Sin conexión', icon: '❌' };
                if (plan) { plan.style.color = p.color; }
                if (fallback) {
                    fallback.innerHTML = `${p.icon} ${p.desc}`;
                    fallback.style.color = p.color;
                    // Add plan chain indicator
                    const allPlans = ['A','B'];
                    const chainHtml = allPlans.map(pln => {
                        const isActive = pln === this.activePlan;
                        const pinfo = planInfo[pln] || { color: '#666', desc: '' };
                        return `<span style="color:${isActive ? pinfo.color : '#444'};font-weight:${isActive ? 'bold' : 'normal'}">${pln}</span>`;
                    }).join(' → ');
                    fallback.innerHTML += ` <span style="color:#555;font-size:0.75em;margin-left:8px;">[${chainHtml}]</span>`;
                }
            } else {
                if (plan) { plan.textContent = '--'; plan.style.color = ''; }
                if (fallback) { fallback.textContent = 'Intentando conectar...'; fallback.style.color = '#9ba0be'; }
            }

            // Show provider/model info from REST response
            const providerInfo = document.getElementById('gateway-provider-info');
            if (providerInfo && this.activeProvider) {
                providerInfo.textContent = ' | ' + this.activeProvider + ' / ' + (this.activeModel || '');
                providerInfo.style.display = '';
            }

            if (agCount) { agCount.textContent = this.agentCount; }
            if (qCount) { qCount.textContent = this.queueCount; }
            if (fCount) { fCount.textContent = this.monitoredFiles > 0 ? this.monitoredFiles : '--'; }

            if (delta) {
                if (this.lastDelta) {
                    delta.innerHTML = ` | <span class="gateway-delta-info">Delta: <strong>${this.lastDelta.count}</strong> archivos (${escHtml(this.lastDelta.agent||'?')})</span>`;
                } else {
                    delta.innerHTML = '';
                }
            }
        }
    };

    // ─────────────────────────────────────────────────────────────
    // Message Interpreter
    // ─────────────────────────────────────────────────────────────

    function interpretAgyMessage(msg) {
        if (!msg || !msg.type) return 'Mensaje recibido del gateway';

        const type = msg.type;
        const detail = msg.data || msg.message || '';

        const patterns = [
            { re: /re-?index/i,        text: 'Agy detectó cambios en archivos, actualizando contexto...' },
            { re: /context.*sync/i,    text: 'Sincronizando conocimiento entre agentes...' },
            { re: /task.*decompos/i,   text: 'Agy está dividiendo la tarea en subtareas...' },
            { re: /agent.*assign/i,    text: `Agy asignó especialista a la tarea: ${detail}` },
            { re: /delta/i,             text: `Cambios detectados: ${detail || 're-indexando delta'}` },
            { re: /pr.*review/i,       text: 'Agy inició revisión de PR...' },
            { re: /merge/i,             text: 'Agy preparando merge de ramas...' },
            { re: /plan.*generat/i,    text: 'Agy generando plan de implementación...' },
            { re: /error/i,             text: `Error en gateway: ${detail || 'sin detalles'}` },
        ];

        if (type === 'agent_status' && msg.status === 'busy') {
            return `Agente ${msg.agent||'?'} comenzó a trabajar: ${msg.current_task||'tarea en progreso'}`;
        }
        if (type === 'agent_status' && msg.status === 'idle') {
            return `Agente ${msg.agent||'?'} terminó y está disponible`;
        }
        if (type === 'file_change') {
            return `Archivos modificados: ${msg.files||msg.count||'?'} (${msg.path||'desconocido'})`;
        }
        if (type === 'queue_update') {
            return `Cola de tareas actualizada: ${msg.size||'?'} pendientes`;
        }

        for (const p of patterns) {
            if (p.re.test(type + ' ' + detail)) return p.text;
        }

        return `${type}: ${detail || 'sin detalles'}`;
    }

    // ─────────────────────────────────────────────────────────────
    // Specialization helpers
    // ─────────────────────────────────────────────────────────────

    const SPEC_LABELS = {
        frontend_ux:          'Frontend & UX',
        backend_critical:     'Backend Critical',
        orchestrator_research:'Orchestrator & Research',
        security_audit:       'Security Audit',
        game_design:          'Game Design',
        blockchain_dev:       'Blockchain Dev',
        infra_devops:         'Infra & DevOps',
    };

    const SPEC_COLORS = {
        frontend_ux:           { bg: 'rgba(235,104,160,0.12)', color: '#ec87c0', border: 'rgba(235,104,160,0.25)' },
        backend_critical:      { bg: 'rgba(52,152,219,0.12)',  color: '#5dade2', border: 'rgba(52,152,219,0.25)' },
        orchestrator_research: { bg: 'rgba(29,209,161,0.12)',  color: '#1dd1a1', border: 'rgba(29,209,161,0.25)' },
        security_audit:        { bg: 'rgba(254,202,87,0.12)',  color: '#feca57', border: 'rgba(254,202,87,0.25)' },
        game_design:           { bg: 'rgba(255,159,243,0.12)', color: '#ff9ff3', border: 'rgba(255,159,243,0.25)' },
        blockchain_dev:        { bg: 'rgba(165,94,234,0.12)',  color: '#a55eea', border: 'rgba(165,94,234,0.25)' },
        infra_devops:          { bg: 'rgba(255,159,67,0.12)',  color: '#ff9f43', border: 'rgba(255,159,67,0.25)' },
    };

    function getSpecInfo(agentName, state) {
        if (state && state.specialization) {
            const s = state.specialization;
            return { key: s, label: SPEC_LABELS[s] || s, colors: SPEC_COLORS[s] || SPEC_COLORS.orchestrator_research };
        }
        const key = SPECIALIZATIONS[agentName] || 'orchestrator_research';
        return { key, label: SPEC_LABELS[key] || key, colors: SPEC_COLORS[key] || SPEC_COLORS.orchestrator_research };
    }

    function getStatusInfo(agentName, state) {
        if (!state) return { class: 'ac-dot--offline', badgeClass: 'ac-badge--offline', badgeText: 'OFFLINE', cssClass: 'ac-card--offline', isBusy: false };
        const busy = state.busy;
        const rateLimited = state.rate_limited || state.rate_limit_hit;
        if (rateLimited) return { class: 'ac-dot--rate-limited', badgeClass: 'ac-badge--rate-limited', badgeText: 'RATE LIMITED', cssClass: 'ac-card--rate-limited', isBusy: false };
        if (busy) return { class: 'ac-dot--busy', badgeClass: 'ac-badge--busy', badgeText: 'BUSY', cssClass: 'ac-card--busy', isBusy: true };
        return { class: 'ac-dot--idle', badgeClass: 'ac-badge--idle', badgeText: 'IDLE', cssClass: 'ac-card--idle', isBusy: false };
    }

    // ─────────────────────────────────────────────────────────────
    // Card render
    // ─────────────────────────────────────────────────────────────

    function renderCard(name, state) {
        const providerInfo = AGENT_PROVIDER[name] || { provider: '?', model: '?', gradient: '' };
        const specInfo = getSpecInfo(name, state);
        const statusInfo = getStatusInfo(name, state);
        const isLoading = statusInfo.isBusy;

        const busy = state && state.busy;
        const taskId = state ? state.current_task : null;
        const filesModified = (state && state.files_modified) ? state.files_modified : 0;
        const label = AGENT_LABELS[name] || name;

        let taskHtml = '';
        if (taskId) {
            const title = getTaskTitle(taskId);
            const taskClick = taskId.length > 8
                ? `onclick="if(typeof openDetailModal==='function')openDetailModal('${escHtml(taskId)}')" style="cursor:pointer;" title="Click para ver detalles"`
                : '';
            taskHtml = `<div class="ac-task" ${taskClick}>${escHtml(title)}</div>`;
        }

        const filesBadge = filesModified > 0
            ? `<span class="ac-files-badge" title="${filesModified} archivos modificados">📁 ${filesModified}</span>`
            : '';

        const specBadge = `<span class="specialization-badge" style="background:${specInfo.colors.bg};color:${specInfo.colors.color};border:1px solid ${specInfo.colors.border};">${escHtml(specInfo.label)}</span>`;

        // Model list chips
        const modelsForProvider = {
            claude: ['Opus 4.8', 'Sonnet 4.6', 'Haiku 4.5'],
            deepclaude: ['V4 Pro [1m]', 'V4 Flash'],
            agy: ['Flash 2.5', 'Pro 2.5'],
            ollama: ['Qwen 2.5 Coder 7B'],
        };
        const models = modelsForProvider[name] || [];
        const activeModel = (state && state.active_model) || '';
        const modelsHtml = models.map(m => {
            const isActive = activeModel && activeModel.toLowerCase().includes(m.toLowerCase().split(' ').pop().replace(/[\[\]]/g,''));
            return `<span class="ac-model-chip${isActive ? ' ac-model-chip--active' : ''}">${escHtml(m)}</span>`;
        }).join('');

        // Busy indicator line
        const busyLine = (statusInfo.isBusy && taskId)
            ? `<div class="ac-busy-line"><span class="spinner-mini-inline"></span> ${escHtml(getTaskTitle(taskId))}</div>`
            : '';

        return `
        <div class="ac-card ${statusInfo.cssClass}" data-agent="${name}">
            <div class="ac-card-top">
                <span class="ac-dot ${statusInfo.class}"></span>
                <span class="ac-icon">${AGENT_ICONS[name]}</span>
                <span class="ac-name">${escHtml(label)}</span>
                <span class="ac-badge ${statusInfo.badgeClass}">${statusInfo.badgeText}</span>
            </div>
            <div class="ac-card-meta">
                <span class="ac-provider-model" title="${escHtml(providerInfo.provider)}: ${escHtml(providerInfo.model)}">
                    <span class="ac-provider">${escHtml(providerInfo.provider)}</span>
                    <span class="ac-model">${escHtml(providerInfo.model)}</span>
                </span>
            </div>
            ${busyLine}
            ${taskHtml}
            <div class="ac-card-footer-row">
                ${specBadge}
                ${filesBadge}
            </div>
            <div class="ac-models-row">${modelsHtml}</div>
        </div>`;
    }

    // ─────────────────────────────────────────────────────────────
    // Main render
    // ─────────────────────────────────────────────────────────────

    function render(agentData, gitData) {
        const el = document.getElementById('agent-console');
        if (!el) return;

        const agentsMap = (agentData && agentData.agents) ? agentData.agents : (agentData || {});
        const branch = gitData && gitData.branch ? gitData.branch : '?';
        const dirty  = gitData && gitData.dirty
            ? `<span class="ac-git-dirty"> · ${gitData.uncommitted_count||'?'} sin commit</span>`
            : '';

        const activeAi = agentData && agentData.active_ai ? agentData.active_ai : [];
        const aiHtml = activeAi.map(c => {
            const title = c.task_id ? getTaskTitle(c.task_id) : c.task_id;
            const lbl   = {concept:'Concepto',planning:'Plan',review:'Review'}[c.stage]||c.stage;
            return `<span class="ac-ai-activity"><span class="ac-ai-spinner"></span>${escHtml(c.provider)}: <em>${escHtml(lbl)}</em> — ${escHtml(title)}</span>`;
        }).join('');

        // Populate loading agents from active AI calls (global, shared with app.js/modal.js/drag-drop.js)
        window._loadingAgents = {};
        if (agentData && agentData.active_ai) {
            for (const call of agentData.active_ai) {
                if (call.task_id) window._loadingAgents[call.task_id] = true;
            }
        }

        // Build agent summary counts for the bar
        const boCount = Object.values(agentsMap).filter(s => s && s.busy).length;

        el.innerHTML = `
        <div class="ac-bar">
            <div class="ac-bar-left">
                <span class="ac-bar-title">Agentes</span>
                <span class="ac-bar-summary">${AGENTS.length} total · ${boCount} trabajando</span>
                ${aiHtml}
            </div>
            <div class="ac-bar-right">
                <span class="ac-git-branch">⎇&nbsp;${escHtml(branch)}</span>${dirty}
            </div>
        </div>
        <div class="ac-cards">
            ${AGENTS.map(n => renderCard(n, agentsMap[n])).join('')}
        </div>`;

        // Show activity log
        const logContainer = document.getElementById('agent-activity-log');
        if (logContainer) logContainer.style.display = 'block';

        // Defer gateway connection — poll() will decide based on server active_plan
        if (!AgyGateway.connected && AgyGateway.reconnectAttempts === 0 && !AgyGateway.ws) {
            // Don't connect yet — wait for first poll to check server plan
        }
    }

    // ─────────────────────────────────────────────────────────────
    // Polling (enhanced)
    // ─────────────────────────────────────────────────────────────

    async function poll() {
        try {
            const [aRes, gRes] = await Promise.allSettled([
                fetch('/api/agents').then(r => r.ok ? r.json() : null),
                fetch('/api/git').then(r => r.ok ? r.json() : null),
            ]);

            const agentData = aRes.status === 'fulfilled' ? aRes.value : null;
            const gitData   = gRes.status === 'fulfilled' ? gRes.value : null;

            // Only attempt WebSocket if server reports Plan A (agy gateway actually running)
            if (agentData && agentData.active_plan === 'A' && !AgyGateway.connected && !AgyGateway.ws) {
                AgyGateway.connect();
            }

            // Update gateway stats from REST fallback
            if (!AgyGateway.connected && agentData && agentData.agents) {
                const agentStates = Object.values(agentData.agents).filter(Boolean);
                AgyGateway.agentCount = agentStates.filter(s => s.busy).length;
                AgyGateway.queueCount = agentStates.filter(s => s.busy && !s.current_task).length;
                // Use server-determined active plan, fallback based on agent availability
                const serverPlan = agentData.active_plan;
                if (serverPlan) {
                    AgyGateway.activePlan = serverPlan;
                } else if (!AgyGateway.activePlan) {
                    // If no server info, guess based on available agents
                    const anyAvailable = agentStates.some(s => s.available);
                    AgyGateway.activePlan = anyAvailable ? 'B' : 'D';
                }
                if (agentData && agentData.active_provider) {
                    AgyGateway.activeProvider = agentData.active_provider;
                    AgyGateway.activeModel = agentData.active_model;
                }
                AgyGateway.updateUI();
            }

            render(agentData, gitData);
        } catch (_) {}
    }

    function start() {
        if (_started) return;
        _started = true;

        // Wire up raw messages toggle
        const rawCheckbox = document.getElementById('show-raw-messages');
        if (rawCheckbox) {
            rawCheckbox.addEventListener('change', function () {
                ActivityLog.setRawVisible(this.checked);
            });
        }

        // Note: WebSocket connection is deferred until first poll()
        // checks server active_plan — avoids unnecessary errors when
        // agy gateway isn't running (no Gemini tokens/quota).
        // poll() will call AgyGateway.connect() only if active_plan === 'A'.

        poll();
        setInterval(poll, 5000);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', start);
    } else {
        start();
    }
})();
