/**
 * Notas Fiscais Module - CRUD com tabela, filtros, email e protocolo
 */
const Notas = {
    empresas: [],
    fornecedores: [],

    async render() {
        const container = document.getElementById('page-notas');
        container.innerHTML = `
            <div class="table-toolbar">
                <div class="table-search">
                    <span class="search-icon">🔍</span>
                    <input type="text" id="notas-busca" placeholder="Buscar por empresa, nº nota ou pedido...">
                </div>
                <div class="table-filters">
                    <select class="filter-select" id="notas-filter-empresa"><option value="">Todas Empresas</option></select>
                    <select class="filter-select" id="notas-filter-status">
                        <option value="">Todos Status</option>
                        <option value="OK">OK</option>
                        <option value="PENDENTE">Pendente</option>
                    </select>
                    <button class="btn btn-primary" id="btn-nova-nf">➕ Nova NF</button>
                    <button class="btn btn-secondary" id="btn-export-excel">📥 Excel</button>
                </div>
            </div>
            <div class="data-table-wrapper" style="overflow-x:auto">
                <table class="data-table">
                    <thead><tr>
                        <th>Empresa/Fornecedor</th><th>Nº Nota</th><th>Nº Pedido</th>
                        <th>Valor</th><th>Grupo</th><th>Vencimento</th>
                        <th>Pré-Nota</th><th>Email</th><th>Protocolo</th><th>Ações</th>
                    </tr></thead>
                    <tbody id="notas-tbody"></tbody>
                </table>
            </div>
        `;
        await this.loadEmpresas();
        this.bindEvents();
        await this.loadData();
    },

    async loadEmpresas() {
        this.empresas = await API.getEmpresas();
        const sel = document.getElementById('notas-filter-empresa');
        this.empresas.forEach(e => { const o = document.createElement('option'); o.value = e.id; o.textContent = e.sigla; sel.appendChild(o); });
    },

    bindEvents() {
        let timer;
        document.getElementById('notas-busca').addEventListener('input', () => { clearTimeout(timer); timer = setTimeout(() => this.loadData(), 300); });
        document.getElementById('notas-filter-empresa').addEventListener('change', () => this.loadData());
        document.getElementById('notas-filter-status').addEventListener('change', () => this.loadData());
        document.getElementById('btn-nova-nf').addEventListener('click', () => this.openModal());
        document.getElementById('btn-export-excel').addEventListener('click', () => API.exportarExcel(App.mesSelecionado, App.anoSelecionado));
    },

    async loadData() {
        const params = { mes: App.mesSelecionado, ano: App.anoSelecionado };
        const busca = document.getElementById('notas-busca')?.value;
        const empresa = document.getElementById('notas-filter-empresa')?.value;
        const status = document.getElementById('notas-filter-status')?.value;
        if (busca) params.busca = busca;
        if (empresa) params.empresa_grupo_id = empresa;
        if (status) params.status = status;

        try {
            const notas = await API.getNotas(params);
            this.renderTable(notas);
        } catch (e) { console.error(e); }
    },

    renderTable(notas) {
        const tbody = document.getElementById('notas-tbody');
        if (!notas.length) {
            tbody.innerHTML = '<tr><td colspan="12"><div class="empty-state"><div class="empty-icon">📄</div><h3>Nenhuma nota fiscal</h3><p>Adicione uma nota fiscal clicando em "Nova NF"</p></div></td></tr>';
            return;
        }
        const fmt = v => v ? v.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }) : '-';
        const fmtDate = d => d ? new Date(d + (d.includes('T') ? '' : 'T12:00:00')).toLocaleDateString('pt-BR') : '-';
        tbody.innerHTML = notas.map(n => {
            const vinculada = n.lancamento_mensal_id ? ' style="border-left:3px solid var(--success)"' : '';
            return `
            <tr${vinculada}>
                <td>
                    <strong>${n.empresa_fornecedor}</strong>
                    ${n.lancamento_mensal_id ? '<span class="badge badge-ok" style="margin-left:6px;font-size:0.65rem">MENSAL</span>' : ''}
                </td>
                <td>${n.numero_nota || '-'}</td>
                <td>${n.numero_pedido || '-'}</td>
                <td style="font-weight:600">${fmt(n.valor)}</td>
                <td>${n.empresa_grupo?.sigla || '-'}</td>
                <td>${fmtDate(n.data_vencimento)}</td>
                <td>
                    <span class="badge ${n.status_pre_nota === 'OK' ? 'badge-ok' : 'badge-pendente'}" 
                          style="cursor:pointer" onclick="Notas.toggleStatus(${n.id}, '${n.status_pre_nota}')">
                        ${n.status_pre_nota === 'OK' ? '✅ OK' : '⏳ Pendente'}
                    </span>
                </td>
                <td>
                    <span class="badge ${n.enviado_email ? 'badge-ok' : 'badge-pendente'}" 
                          style="cursor:pointer" onclick="Notas.toggleEmail(${n.id})">
                        ${n.enviado_email ? '📧 Sim' : '✉️ Não'}
                    </span>
                </td>
                <td>
                    <span class="protocolo-cell" style="cursor:pointer;font-size:0.82rem;${n.protocolo_pre_nota ? 'color:var(--text-primary)' : 'color:var(--text-muted)'}" 
                          onclick="Notas.editProtocolo(${n.id}, '${n.protocolo_pre_nota || ''}')">
                        ${n.protocolo_pre_nota || '—'}
                    </span>
                </td>
                <td>
                    <button class="btn btn-secondary btn-sm btn-icon" onclick="Notas.openModal(${n.id})" title="Editar">✏️</button>
                    <button class="btn btn-danger btn-sm btn-icon" onclick="Notas.deletar(${n.id})" title="Excluir">🗑️</button>
                </td>
            </tr>`;
        }).join('');
    },

    async toggleStatus(id, current) {
        const novo = current === 'OK' ? 'PENDENTE' : 'OK';
        try {
            await API.atualizarStatusNota(id, novo);
            App.toast(`Pré-nota: ${novo}`, 'success');
            this.loadData();
        } catch (e) { App.toast('Erro ao atualizar status', 'error'); }
    },

    async toggleEmail(id) {
        try {
            await API.toggleEmail(id);
            this.loadData();
        } catch (e) { App.toast('Erro ao atualizar email', 'error'); }
    },

    editProtocolo(id, current) {
        const protocolo = prompt('Número do protocolo da pré-nota:', current);
        if (protocolo === null) return;
        API.atualizarProtocolo(id, protocolo).then(() => {
            App.toast('Protocolo atualizado', 'success');
            this.loadData();
        }).catch(() => App.toast('Erro ao atualizar protocolo', 'error'));
    },

    async openModal(id = null) {
        const isEdit = !!id;
        let nota = {};
        if (isEdit) nota = await API.getNota(id);
        if (!this.empresas.length) this.empresas = await API.getEmpresas();

        const empresaOpts = this.empresas.map(e => `<option value="${e.id}" ${nota.empresa_grupo_id == e.id ? 'selected' : ''}>${e.sigla}</option>`).join('');

        App.openModal(isEdit ? 'Editar Nota Fiscal' : 'Nova Nota Fiscal', `
            <div class="form-row">
                <div class="form-group" style="flex:2">
                    <label class="form-label">Empresa/Fornecedor *</label>
                    <input class="form-input" id="nf-fornecedor" value="${nota.empresa_fornecedor || ''}" list="fornecedor-list">
                    <datalist id="fornecedor-list">${await this.getFornecedorOptions()}</datalist>
                </div>
                <div class="form-group" style="flex:1">
                    <label class="form-label">Grupo Emalto</label>
                    <select class="form-select" id="nf-empresa">
                        <option value="">Selecione...</option>
                        ${empresaOpts}
                    </select>
                </div>
                <div class="form-group" style="flex:1">
                    <label class="form-label">Cód. Forn.</label>
                    <input class="form-input" id="nf-cod-fornecedor" value="${nota.codigo_fornecedor || ''}" readonly placeholder="Auto">
                </div>
            </div>
            
            <div id="nf-contrato-container" class="form-group" style="display:none; background: var(--glass); padding: 10px; border-radius: 6px; margin-bottom: 15px;" data-saved-id="${nota.contrato_id || ''}">
            </div>

            <div class="form-row">
                <div class="form-group"><label class="form-label">N\u00ba da Nota</label><input class="form-input" id="nf-numero" value="${nota.numero_nota || ''}"></div>
                <div class="form-group"><label class="form-label">N\u00ba do Pedido</label><input class="form-input" id="nf-pedido" value="${nota.numero_pedido || ''}"></div>
            </div>
            <div class="form-row">
                <div class="form-group"><label class="form-label">Valor (R$)</label><input class="form-input" type="number" step="0.01" id="nf-valor" value="${nota.valor || ''}"></div>
                <div class="form-group"><label class="form-label">Vencimento</label><input class="form-input" type="date" id="nf-vencimento" value="${nota.data_vencimento || ''}"></div>
            </div>
            <div class="form-row">
                <div class="form-group"><label class="form-label">Pr\u00e9-Nota</label><select class="form-select" id="nf-status"><option value="PENDENTE" ${nota.status_pre_nota === 'PENDENTE' ? 'selected' : ''}>Pendente</option><option value="OK" ${nota.status_pre_nota === 'OK' ? 'selected' : ''}>OK</option></select></div>
                <div class="form-group"><label class="form-label">Protocolo Pr\u00e9-Nota</label><input class="form-input" id="nf-protocolo" value="${nota.protocolo_pre_nota || ''}"></div>
            </div>
            <div class="form-group">
                <label style="display:flex;align-items:center;gap:8px;cursor:pointer;padding:5px 0">
                    <input type="checkbox" id="nf-email" ${nota.enviado_email ? 'checked' : ''} style="width:18px;height:18px;accent-color:var(--accent)">
                    <span style="font-size:0.85rem;color:var(--text-secondary)">Nota enviada por Email</span>
                </label>
            </div>
            <div class="form-group"><label class="form-label">Observa\u00e7\u00e3o</label><textarea class="form-textarea" id="nf-obs">${nota.observacao || ''}</textarea></div>
        `, [
            { text: 'Cancelar', class: 'btn btn-secondary', action: () => App.closeModal() },
            { text: isEdit ? 'Salvar' : 'Criar', class: 'btn btn-primary', action: () => this.salvar(id) },
        ]);

        document.getElementById('nf-fornecedor').addEventListener('change', () => this.updateFornecedorInfo());
        document.getElementById('nf-empresa').addEventListener('change', () => this.updateFornecedorInfo());
        this.updateFornecedorInfo();
    },

    async updateFornecedorInfo() {
        const fornecedorNome = document.getElementById('nf-fornecedor').value;
        const empresaId = document.getElementById('nf-empresa').value;
        const container = document.getElementById('nf-contrato-container');
        const codInput = document.getElementById('nf-cod-fornecedor');
        
        if (!fornecedorNome || !empresaId) {
            container.style.display = 'none';
            container.innerHTML = '';
            return;
        }

        try {
            const fornecedores = await API.getFornecedores();
            const fornecedor = fornecedores.find(f => f.nome === fornecedorNome);
            if (!fornecedor) return;

            // Busca código identificador para fornecedores comuns
            if (!fornecedorNome.toUpperCase().includes('TOTVS')) {
                const identificadores = await API.get('/api/cadastros/identificadores');
                const ident = identificadores.find(i => i.fornecedor_id === fornecedor.id && i.empresa_grupo_id == empresaId);
                if (ident && ident.codigo_identificador) {
                    codInput.value = ident.codigo_identificador;
                } else {
                    codInput.value = 'Não Cadastrado';
                }
                
                container.style.display = 'none';
                container.innerHTML = '';
                return;
            }

            // Para TOTVS, o código vem do contrato
            codInput.value = 'Auto (Pelo Contrato)';

            container.style.display = 'block';
            container.innerHTML = '<label class="form-label">Vincular ao Contrato/Proposta (TOTVS) *</label><select class="form-select" id="nf-contrato-id"><option value="">Carregando...</option></select>';

            const contratos = await API.getContratosPorFornecedor(fornecedor.id);
            const contratosEmpresa = contratos.filter(c => c.empresa_grupo_id == empresaId && c.ativo);
            
            const select = document.getElementById('nf-contrato-id');
            if (contratosEmpresa.length === 0) {
                select.innerHTML = '<option value="">Nenhum contrato cadastrado</option>';
            } else {
                select.innerHTML = '<option value="">Selecione a Proposta...</option>' + 
                    contratosEmpresa.map(c => `<option value="${c.id}">${c.codigo_contrato || 'Sem Código'} - ${c.descricao || ''}</option>`).join('');
                
                const savedId = container.dataset.savedId;
                if (savedId) select.value = savedId;
            }
        } catch (e) {
            container.innerHTML = '<label class="form-label">Vincular ao Contrato/Proposta</label><select class="form-select" id="nf-contrato-id"><option value="">Erro ao carregar</option></select>';
        }
    },

    async getFornecedorOptions() {
        try {
            const fornecedores = await API.getFornecedores();
            return fornecedores.map(f => `<option value="${f.nome}">`).join('');
        } catch { return ''; }
    },

    async salvar(id) {
        const data = {
            empresa_fornecedor: document.getElementById('nf-fornecedor').value,
            numero_nota: document.getElementById('nf-numero').value || null,
            numero_pedido: document.getElementById('nf-pedido').value || null,
            valor: parseFloat(document.getElementById('nf-valor').value) || 0,
            empresa_grupo_id: parseInt(document.getElementById('nf-empresa').value) || null,
            data_vencimento: document.getElementById('nf-vencimento').value || null,
            status_pre_nota: document.getElementById('nf-status').value,
            enviado_email: document.getElementById('nf-email').checked,
            protocolo_pre_nota: document.getElementById('nf-protocolo').value || null,
            observacao: document.getElementById('nf-obs').value || null,
            mes_referencia: App.mesSelecionado,
            ano_referencia: App.anoSelecionado,
            contrato_id: document.getElementById('nf-contrato-id') ? (parseInt(document.getElementById('nf-contrato-id').value) || null) : null,
        };
        if (!data.empresa_fornecedor) { App.toast('Informe o fornecedor', 'error'); return; }
        
        if (data.empresa_fornecedor.toUpperCase().includes('TOTVS') && data.empresa_grupo_id && !data.contrato_id) {
            App.toast('Para TOTVS, é obrigatório selecionar um contrato.', 'error');
            return;
        }
        try {
            if (id) await API.atualizarNota(id, data);
            else await API.criarNota(data);
            App.closeModal();
            const vinculou = data.empresa_grupo_id ? ' (contrato vinculado automaticamente!)' : '';
            App.toast(id ? 'NF atualizada!' + vinculou : 'NF criada!' + vinculou, 'success');
            this.loadData();
        } catch (e) { App.toast(`Erro: ${e.message}`, 'error'); }
    },

    deletar(id) {
        App.openModal('Excluir Nota Fiscal', `
            <div style="text-align:center;padding:10px 0">
                <div style="font-size:2.5rem;margin-bottom:12px">🗑️</div>
                <p style="font-size:0.95rem;color:var(--text-primary);margin-bottom:6px">
                    Tem certeza que deseja excluir esta nota fiscal?
                </p>
                <p style="font-size:0.82rem;color:var(--text-muted)">
                    Esta ação não poderá ser desfeita.
                </p>
            </div>
        `, [
            { text: 'Cancelar', class: 'btn btn-secondary', action: () => App.closeModal() },
            {
                text: '🗑️ Excluir',
                class: 'btn btn-danger',
                action: async () => {
                    App.closeModal();
                    try {
                        await API.deletarNota(id);
                        App.toast('NF excluída com sucesso', 'success');
                        this.loadData();
                    } catch (e) {
                        App.toast('Erro ao excluir', 'error');
                    }
                }
            }
        ]);
    },

    async openModalPreFill(fornecedor, empresaSigla, mes) {
        if (!this.empresas.length) this.empresas = await API.getEmpresas();
        const empresa = this.empresas.find(e => e.sigla === empresaSigla);
        const nota = {
            empresa_fornecedor: fornecedor,
            empresa_grupo_id: empresa ? empresa.id : null,
        };
        App.mesSelecionado = mes;
        document.getElementById('select-mes').value = mes;

        const empresaOpts = this.empresas.map(e => `<option value="${e.id}" ${nota.empresa_grupo_id == e.id ? 'selected' : ''}>${e.sigla}</option>`).join('');
        App.openModal('Nova Nota Fiscal', `
            <div class="form-row">
                <div class="form-group" style="flex:2">
                    <label class="form-label">Empresa/Fornecedor *</label>
                    <input class="form-input" id="nf-fornecedor" value="${nota.empresa_fornecedor || ''}" list="fornecedor-list">
                    <datalist id="fornecedor-list">${await this.getFornecedorOptions()}</datalist>
                </div>
                <div class="form-group" style="flex:1">
                    <label class="form-label">Grupo Emalto</label>
                    <select class="form-select" id="nf-empresa">
                        <option value="">Selecione...</option>
                        ${empresaOpts}
                    </select>
                </div>
                <div class="form-group" style="flex:1">
                    <label class="form-label">Cód. Forn.</label>
                    <input class="form-input" id="nf-cod-fornecedor" value="" readonly placeholder="Auto">
                </div>
            </div>
            
            <div id="nf-contrato-container" class="form-group" style="display:none; background: var(--glass); padding: 10px; border-radius: 6px; margin-bottom: 15px;" data-saved-id="">
            </div>

            <div class="form-row">
                <div class="form-group"><label class="form-label">N\u00ba da Nota</label><input class="form-input" id="nf-numero" value=""></div>
                <div class="form-group"><label class="form-label">N\u00ba do Pedido</label><input class="form-input" id="nf-pedido" value=""></div>
            </div>
            <div class="form-row">
                <div class="form-group"><label class="form-label">Valor (R$)</label><input class="form-input" type="number" step="0.01" id="nf-valor" value=""></div>
                <div class="form-group"><label class="form-label">Vencimento</label><input class="form-input" type="date" id="nf-vencimento" value=""></div>
            </div>
            <div class="form-row">
                <div class="form-group"><label class="form-label">Pr\u00e9-Nota</label><select class="form-select" id="nf-status"><option value="PENDENTE" selected>Pendente</option><option value="OK">OK</option></select></div>
                <div class="form-group"><label class="form-label">Protocolo Pr\u00e9-Nota</label><input class="form-input" id="nf-protocolo" value=""></input></div>
            </div>
            <div class="form-group">
                <label style="display:flex;align-items:center;gap:8px;cursor:pointer;padding:5px 0">
                    <input type="checkbox" id="nf-email" style="width:18px;height:18px;accent-color:var(--accent)">
                    <span style="font-size:0.85rem;color:var(--text-secondary)">Nota enviada por Email</span>
                </label>
            </div>
            <div class="form-group"><label class="form-label">Observa\u00e7\u00e3o</label><textarea class="form-textarea" id="nf-obs"></textarea></div>
        `, [
            { text: 'Cancelar', class: 'btn btn-secondary', action: () => App.closeModal() },
            { text: 'Criar', class: 'btn btn-primary', action: () => this.salvar(null) },
        ]);
        
        document.getElementById('nf-fornecedor').addEventListener('change', () => this.updateFornecedorInfo());
        document.getElementById('nf-empresa').addEventListener('change', () => this.updateFornecedorInfo());
        this.updateFornecedorInfo();
    },
};
