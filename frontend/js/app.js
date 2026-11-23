/**
 * App Core - Router, Modal, Toast, Inicialização
 */
const App = {
    mesSelecionado: new Date().getMonth() + 1,
    anoSelecionado: new Date().getFullYear(),
    currentPage: 'dashboard',
    MESES: ['Janeiro','Fevereiro','Março','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro'],

    init() {
        this.setupMonthSelector();
        this.setupNavigation();
        this.setupModal();
        this.setupSidebar();
        this.setupNotifications();
        this.setupDailyAlert();
        this.navigateTo('dashboard');
    },

    setupMonthSelector() {
        const selMes = document.getElementById('select-mes');
        const selAno = document.getElementById('select-ano');
        this.MESES.forEach((m, i) => {
            const o = document.createElement('option');
            o.value = i + 1; o.textContent = m;
            if (i + 1 === this.mesSelecionado) o.selected = true;
            selMes.appendChild(o);
        });
        for (let y = 2025; y <= 2030; y++) {
            const o = document.createElement('option');
            o.value = y; o.textContent = y;
            if (y === this.anoSelecionado) o.selected = true;
            selAno.appendChild(o);
        }
        selMes.addEventListener('change', () => { this.mesSelecionado = parseInt(selMes.value); this.refreshPage(); });
        selAno.addEventListener('change', () => { this.anoSelecionado = parseInt(selAno.value); this.refreshPage(); });
    },

    setupNavigation() {
        document.querySelectorAll('.nav-item[data-page]').forEach(item => {
            item.addEventListener('click', () => this.navigateTo(item.dataset.page));
        });
    },

    navigateTo(page) {
        this.currentPage = page;
        // Update nav
        document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
        const navItem = document.querySelector(`.nav-item[data-page="${page}"]`);
        if (navItem) navItem.classList.add('active');
        // Update pages
        document.querySelectorAll('.page-section').forEach(s => s.classList.remove('active'));
        const section = document.getElementById(`page-${page}`);
        if (section) section.classList.add('active');
        // Update title
        const titles = { dashboard: 'Dashboard', notas: 'Notas Fiscais', contratos: 'Contratos Mensais', cadastros: 'Cadastros Base', diretorio: 'Consulta de Códigos', empresas: 'Empresas do Grupo', fornecedores: 'Fornecedores', relatorios: 'Relatórios' };
        document.getElementById('page-title').textContent = titles[page] || page;
        // Render page
        this.renderPage(page);
    },

    async renderPage(page) {
        switch (page) {
            case 'dashboard': await Dashboard.render(); break;
            case 'notas': await Notas.render(); break;
            case 'contratos': await Contratos.render(); break;
            case 'cadastros': await Cadastros.render(); break;
            case 'diretorio': await Diretorio.render(); break;
            case 'empresas': await this.renderCadastro('empresas'); break;
            case 'fornecedores': await this.renderCadastro('fornecedores'); break;
            case 'relatorios': await Relatorios.render(); break;
        }
    },

    refreshPage() { this.renderPage(this.currentPage); },

    // === Cadastros genéricos (Empresas e Fornecedores) ===
    async renderCadastro(tipo) {
        const container = document.getElementById(`page-${tipo}`);
        const isEmpresa = tipo === 'empresas';
        const data = isEmpresa ? await API.getEmpresas() : await API.getFornecedores();
        container.innerHTML = `
            <div class="table-toolbar">
                <h3 style="font-size:1rem">${isEmpresa ? 'Empresas do Grupo Emalto' : 'Fornecedores Cadastrados'}</h3>
                <button class="btn btn-primary" onclick="App.openCadastroModal('${tipo}')">➕ ${isEmpresa ? 'Nova Empresa' : 'Novo Fornecedor'}</button>
            </div>
            <div class="data-table-wrapper">
                <table class="data-table"><thead><tr>
                    ${isEmpresa ? '<th>Sigla</th><th>Nome Completo</th><th>Status</th><th>Ações</th>' : '<th>Nome</th><th>Categoria</th><th>Descrição</th><th>Status</th><th>Ações</th>'}
                </tr></thead><tbody>
                ${data.map(d => `<tr>
                    ${isEmpresa ? `<td><strong>${d.sigla}</strong></td><td>${d.nome_completo}</td>` : `<td><strong>${d.nome}</strong></td><td><span class="badge ${d.categoria === 'SOFTWARE_MENSAL' ? 'badge-faturado' : 'badge-pendente'}">${d.categoria}</span></td><td>${d.descricao || '-'}</td>`}
                    <td><span class="badge ${d.ativo ? 'badge-ok' : 'badge-vencido'}">${d.ativo ? 'Ativo' : 'Inativo'}</span></td>
                    <td><button class="btn btn-secondary btn-sm btn-icon" onclick="App.openCadastroModal('${tipo}', ${d.id})" title="Editar">✏️</button></td>
                </tr>`).join('')}
                </tbody></table>
            </div>
        `;
    },

    async openCadastroModal(tipo, id = null) {
        const isEmpresa = tipo === 'empresas';
        const isEdit = !!id;
        let data = {};
        if (isEdit) data = isEmpresa ? (await API.getEmpresas()).find(e => e.id === id) : (await API.getFornecedores()).find(f => f.id === id);
        const body = isEmpresa ? `
            <div class="form-group"><label class="form-label">Sigla *</label><input class="form-input" id="cad-sigla" value="${data.sigla || ''}"></div>
            <div class="form-group"><label class="form-label">Nome Completo *</label><input class="form-input" id="cad-nome" value="${data.nome_completo || ''}"></div>
        ` : `
            <div class="form-group"><label class="form-label">Nome *</label><input class="form-input" id="cad-nome" value="${data.nome || ''}"></div>
            <div class="form-group"><label class="form-label">Categoria</label><select class="form-select" id="cad-cat"><option value="SOFTWARE_MENSAL" ${data.categoria === 'SOFTWARE_MENSAL' ? 'selected' : ''}>Software Mensal</option><option value="AVULSO" ${data.categoria === 'AVULSO' ? 'selected' : ''}>Avulso</option></select></div>
            <div class="form-group"><label class="form-label">Descrição</label><input class="form-input" id="cad-desc" value="${data.descricao || ''}"></div>
        `;
        this.openModal(isEdit ? 'Editar' : 'Novo', body, [
            { text: 'Cancelar', class: 'btn btn-secondary', action: () => this.closeModal() },
            { text: 'Salvar', class: 'btn btn-primary', action: () => this.salvarCadastro(tipo, id) },
        ]);
    },

    async salvarCadastro(tipo, id) {
        try {
            if (tipo === 'empresas') {
                const d = { sigla: document.getElementById('cad-sigla').value, nome_completo: document.getElementById('cad-nome').value };
                if (!d.sigla) { this.toast('Informe a sigla', 'error'); return; }
                id ? await API.atualizarEmpresa(id, d) : await API.criarEmpresa(d);
            } else {
                const d = { nome: document.getElementById('cad-nome').value, categoria: document.getElementById('cad-cat').value, descricao: document.getElementById('cad-desc').value || null };
                if (!d.nome) { this.toast('Informe o nome', 'error'); return; }
                id ? await API.atualizarFornecedor(id, d) : await API.criarFornecedor(d);
            }
            this.closeModal();
            this.toast('Salvo com sucesso!', 'success');
            this.renderCadastro(tipo);
        } catch (e) { this.toast(`Erro: ${e.message}`, 'error'); }
    },

    // === Modal ===
    setupModal() {
        document.getElementById('modal-close').addEventListener('click', () => this.closeModal());
        document.getElementById('modal-overlay').addEventListener('click', (e) => { if (e.target === e.currentTarget) this.closeModal(); });
    },
    openModal(title, bodyHtml, buttons = []) {
        document.getElementById('modal-title').textContent = title;
        document.getElementById('modal-body').innerHTML = bodyHtml;
        const footer = document.getElementById('modal-footer');
        footer.innerHTML = '';
        buttons.forEach(b => { const btn = document.createElement('button'); btn.className = b.class; btn.textContent = b.text; btn.addEventListener('click', b.action); footer.appendChild(btn); });
        document.getElementById('modal-overlay').classList.add('active');
    },
    closeModal() { document.getElementById('modal-overlay').classList.remove('active'); },
    
    // === Sidebar ===
    setupSidebar() {
        const toggle = document.getElementById('sidebar-toggle');
        const sidebar = document.getElementById('sidebar');
        if (!toggle || !sidebar) return;

        // Restore state
        const isCollapsed = localStorage.getItem('sidebar-collapsed') === 'true';
        if (isCollapsed) sidebar.classList.add('collapsed');

        toggle.addEventListener('click', () => {
            const collapsed = sidebar.classList.toggle('collapsed');
            localStorage.setItem('sidebar-collapsed', collapsed);
        });
    },

    // === Notifications ===
    setupNotifications() {
        document.getElementById('btn-notificacoes').addEventListener('click', () => this.toggleNotifications());
        document.getElementById('notif-close').addEventListener('click', () => this.toggleNotifications(false));
        document.getElementById('notif-backdrop').addEventListener('click', () => this.toggleNotifications(false));
        this.loadNotifications();
    },
    async loadNotifications() {
        try {
            const data = await API.getNotificacoes();
            if (data.total_alertas > 0) {
                document.getElementById('notif-dot').style.display = 'block';
                const badge = document.getElementById('contratos-pendentes-badge');
                badge.style.display = 'inline'; badge.textContent = data.total_alertas;
            }
            this._notifData = data;
        } catch (e) { console.error(e); }
    },
    toggleNotifications(show) {
        const panel = document.getElementById('notif-panel');
        const backdrop = document.getElementById('notif-backdrop');
        const isOpen = show !== undefined ? show : !panel.classList.contains('open');
        panel.classList.toggle('open', isOpen);
        backdrop.classList.toggle('active', isOpen);
        if (isOpen && this._notifData) this.renderNotifications(this._notifData);
    },
    renderNotifications(data) {
        const body = document.getElementById('notif-body');
        if (!data.items.length) { body.innerHTML = '<div class="empty-state" style="padding:40px"><p>✅ Nenhuma pendência!</p></div>'; return; }
        body.innerHTML = data.items.map(n => {
            const dot = n.tipo === 'vencida' ? 'red' : n.tipo === 'vencendo_hoje' ? 'yellow' : 'green';
            const label = n.tipo === 'vencida' ? '🔴 Vencida' : n.tipo === 'vencendo_hoje' ? '⚠️ Vence hoje' : '⏳ Esta semana';
            const fmt = n.valor ? n.valor.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }) : '';
            return `<div class="alert-item"><div class="alert-dot ${dot}"></div><div class="alert-info"><div class="alert-title">${n.fornecedor}</div><div class="alert-sub">${n.empresa} • ${label}</div></div><div style="text-align:right"><div class="alert-value">${fmt}</div><div class="alert-date">${new Date(n.data_vencimento + (n.data_vencimento.includes('T') ? '' : 'T12:00:00')).toLocaleDateString('pt-BR')}</div></div></div>`;
        }).join('');
    },

    // === Toast ===
    toast(message, type = 'info') {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        const icons = { success: '✅', error: '❌', warning: '⚠️', info: 'ℹ️' };
        toast.innerHTML = `<span>${icons[type] || ''}</span> ${message}`;
        container.appendChild(toast);
        setTimeout(() => { toast.style.opacity = '0'; setTimeout(() => toast.remove(), 300); }, 3500);
    },

    // === Alerta Diário de Vencimentos (8h, Seg-Sex) ===
    setupDailyAlert() {
        const HORA_ALERTA = 8; // 8:00 AM
        const STORAGE_KEY = 'alerta_vencimentos_visto';

        const getTodayKey = () => {
            const d = new Date();
            return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
        };

        const isDiaUtil = () => {
            const dow = new Date().getDay();
            return dow >= 1 && dow <= 5; // Seg(1) a Sex(5)
        };

        const jaViuHoje = () => localStorage.getItem(STORAGE_KEY) === getTodayKey();
        const marcarVisto = () => localStorage.setItem(STORAGE_KEY, getTodayKey());

        const dispararAlerta = async () => {
            if (jaViuHoje()) return;
            marcarVisto();
            try {
                const data = await API.getNotificacoes();
                if (!data.items || data.items.length === 0) return;

                const fmtDate = d => d ? new Date(d + (d.includes('T') ? '' : 'T12:00:00')).toLocaleDateString('pt-BR') : '-';
                const fmt = v => v ? v.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }) : '';

                // Agrupar por tipo
                const vencidas = data.items.filter(i => i.tipo === 'vencida');
                const hoje = data.items.filter(i => i.tipo === 'vencendo_hoje');
                const semana = data.items.filter(i => i.tipo === 'vencendo_semana');

                let html = `<div style="max-height:420px;overflow-y:auto;padding-right:4px">`;

                if (vencidas.length > 0) {
                    html += `<div style="margin-bottom:16px">
                        <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px">
                            <span style="font-size:1.2rem">🔴</span>
                            <span style="font-weight:700;color:var(--danger);font-size:0.9rem">${vencidas.length} NF(s) VENCIDA(S)</span>
                        </div>`;
                    vencidas.forEach(n => {
                        html += `<div style="display:flex;justify-content:space-between;align-items:center;padding:8px 12px;background:var(--danger-soft);border-radius:var(--radius-md);margin-bottom:6px;font-size:0.84rem">
                            <div><strong>${n.fornecedor}</strong> <span style="color:var(--text-muted)">• ${n.empresa}</span></div>
                            <div style="text-align:right"><div style="font-weight:600">${fmt(n.valor)}</div><div style="font-size:0.75rem;color:var(--danger)">${fmtDate(n.data_vencimento)} (${Math.abs(n.dias_restantes)}d atrás)</div></div>
                        </div>`;
                    });
                    html += `</div>`;
                }

                if (hoje.length > 0) {
                    html += `<div style="margin-bottom:16px">
                        <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px">
                            <span style="font-size:1.2rem">⚠️</span>
                            <span style="font-weight:700;color:var(--warning);font-size:0.9rem">${hoje.length} NF(s) VENCEM HOJE</span>
                        </div>`;
                    hoje.forEach(n => {
                        html += `<div style="display:flex;justify-content:space-between;align-items:center;padding:8px 12px;background:var(--warning-soft);border-radius:var(--radius-md);margin-bottom:6px;font-size:0.84rem">
                            <div><strong>${n.fornecedor}</strong> <span style="color:var(--text-muted)">• ${n.empresa}</span></div>
                            <div style="text-align:right"><div style="font-weight:600">${fmt(n.valor)}</div><div style="font-size:0.75rem;color:var(--warning)">Vence hoje!</div></div>
                        </div>`;
                    });
                    html += `</div>`;
                }

                if (semana.length > 0) {
                    html += `<div style="margin-bottom:16px">
                        <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px">
                            <span style="font-size:1.2rem">⏳</span>
                            <span style="font-weight:700;color:var(--accent);font-size:0.9rem">${semana.length} NF(s) vencem esta semana</span>
                        </div>`;
                    semana.forEach(n => {
                        html += `<div style="display:flex;justify-content:space-between;align-items:center;padding:8px 12px;background:var(--accent-soft);border-radius:var(--radius-md);margin-bottom:6px;font-size:0.84rem">
                            <div><strong>${n.fornecedor}</strong> <span style="color:var(--text-muted)">• ${n.empresa}</span></div>
                            <div style="text-align:right"><div style="font-weight:600">${fmt(n.valor)}</div><div style="font-size:0.75rem;color:var(--text-muted)">${fmtDate(n.data_vencimento)} (${n.dias_restantes}d)</div></div>
                        </div>`;
                    });
                    html += `</div>`;
                }

                html += `</div>`;

                // Resumo rápido no topo
                const resumo = `<div style="text-align:center;margin-bottom:16px;padding:14px;background:var(--glass);border-radius:var(--radius-md)">
                    <div style="font-size:1.5rem;margin-bottom:6px">📋</div>
                    <div style="font-size:0.9rem;font-weight:600;color:var(--text-primary)">Resumo de Vencimentos — ${new Date().toLocaleDateString('pt-BR')}</div>
                    <div style="display:flex;justify-content:center;gap:18px;margin-top:10px;font-size:0.82rem">
                        ${vencidas.length ? `<span style="color:var(--danger)">🔴 ${vencidas.length} vencida(s)</span>` : ''}
                        ${hoje.length ? `<span style="color:var(--warning)">⚠️ ${hoje.length} hoje</span>` : ''}
                        ${semana.length ? `<span style="color:var(--accent)">⏳ ${semana.length} esta semana</span>` : ''}
                    </div>
                </div>`;

                App.openModal('🔔 Alerta de Vencimentos', resumo + html, [
                    { text: 'OK, Entendi', class: 'btn btn-primary', action: () => App.closeModal() }
                ]);
            } catch (e) {
                console.error('[Alerta Diário] Erro ao carregar notificações:', e);
            }
        };

        // Verificar a cada 30 segundos se chegou a hora
        setInterval(() => {
            const now = new Date();
            if (isDiaUtil() && now.getHours() === HORA_ALERTA && now.getMinutes() === 0 && !jaViuHoje()) {
                dispararAlerta();
            }
        }, 30000);

        // Ao abrir a página: se é dia útil, já passou das 8h e ainda não viu hoje → exibe
        setTimeout(() => {
            const now = new Date();
            if (isDiaUtil() && now.getHours() >= HORA_ALERTA && !jaViuHoje()) {
                dispararAlerta();
            }
        }, 2000); // 2s para dar tempo dos dados carregarem
    },
};

// Initialize
document.addEventListener('DOMContentLoaded', () => App.init());
