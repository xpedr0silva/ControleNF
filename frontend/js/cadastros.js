/**
 * Cadastros Base - Mapeamento de Fornecedores e Contratos (TOTVS)
 */
const Cadastros = {
    empresas: [],
    fornecedores: [],
    identificadores: [],

    async render() {
        const container = document.getElementById('page-cadastros');
        container.innerHTML = `
            <div class="table-toolbar">
                <div style="display:flex;align-items:center;gap:12px">
                    <h3 style="font-size:1rem;font-weight:600">Mapeamento Mestre de Fornecedores</h3>
                    <span style="font-size:0.78rem;color:var(--text-muted)">
                        Vincule códigos ou contratos a cada empresa.
                    </span>
                </div>
            </div>
            
            <div class="form-row" style="margin-bottom: 20px; background: var(--glass); padding: 15px; border-radius: 8px;">
                <div class="form-group" style="max-width: 400px; margin: 0;">
                    <label class="form-label">Selecione o Fornecedor:</label>
                    <select class="form-select" id="cadastros-fornecedor-select">
                        <option value="">Carregando...</option>
                    </select>
                </div>
            </div>

            <div id="cadastros-content">
                <div class="empty-state">
                    <p>Selecione um fornecedor acima para configurar.</p>
                </div>
            </div>
        `;

        await this.loadData();
        
        document.getElementById('cadastros-fornecedor-select').addEventListener('change', (e) => {
            this.renderContent(e.target.value);
        });
    },

    async loadData() {
        try {
            [this.empresas, this.fornecedores, this.identificadores] = await Promise.all([
                API.getEmpresas(),
                API.getFornecedores(),
                this.getIdentificadores()
            ]);

            const select = document.getElementById('cadastros-fornecedor-select');
            select.innerHTML = '<option value="">Selecione...</option>' + 
                this.fornecedores.map(f => `<option value="${f.id}">${f.nome}</option>`).join('');

        } catch (e) {
            App.toast('Erro ao carregar dados', 'error');
            console.error(e);
        }
    },

    async getIdentificadores() {
        return await API.get('/api/cadastros/identificadores');
    },

    async renderContent(fornecedorId) {
        const contentDiv = document.getElementById('cadastros-content');
        if (!fornecedorId) {
            contentDiv.innerHTML = '<div class="empty-state"><p>Selecione um fornecedor acima para configurar.</p></div>';
            return;
        }

        const fornecedor = this.fornecedores.find(f => f.id == fornecedorId);
        const isTotvs = fornecedor.nome.toUpperCase().includes('TOTVS');

        if (isTotvs) {
            await this.renderTotvsView(fornecedor, contentDiv);
        } else {
            this.renderComumView(fornecedor, contentDiv);
        }
    },

    // --- VIEW COMUM (Identificadores Planilha) ---
    renderComumView(fornecedor, container) {
        let html = `
            <div style="background: var(--glass); border-radius: 8px; padding: 20px;">
                <h4 style="margin-bottom: 15px; font-weight: 600;">Códigos de Identificação (Planilha) - ${fornecedor.nome}</h4>
                <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 20px;">
                    Digite o código de planilha usado para este fornecedor em cada empresa.
                </p>
                <div class="data-table-wrapper">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Empresa</th>
                                <th>Código Identificador</th>
                                <th style="width: 100px;">Ações</th>
                            </tr>
                        </thead>
                        <tbody>
        `;

        this.empresas.forEach(emp => {
            const ident = this.identificadores.find(i => i.fornecedor_id === fornecedor.id && i.empresa_grupo_id === emp.id);
            const codigo = ident ? ident.codigo_identificador : '';
            
            html += `
                <tr>
                    <td><strong>${emp.sigla}</strong> <span style="font-size:0.75rem; color:var(--text-muted)">- ${emp.nome_completo}</span></td>
                    <td>
                        <input type="text" class="form-input" id="ident_${emp.id}" value="${codigo || ''}" placeholder="Ex: 11366-01">
                    </td>
                    <td>
                        <button class="btn btn-secondary btn-sm" onclick="Cadastros.salvarIdentificador(${fornecedor.id}, ${emp.id})">Salvar</button>
                    </td>
                </tr>
            `;
        });

        html += `</tbody></table></div></div>`;
        container.innerHTML = html;
    },

    async salvarIdentificador(fornecedorId, empresaId) {
        const codigo = document.getElementById(`ident_${empresaId}`).value.trim();
        try {
            await API.post('/api/cadastros/identificadores', {
                fornecedor_id: fornecedorId,
                empresa_grupo_id: empresaId,
                codigo_identificador: codigo || null
            });
            
            // Update local state
            this.identificadores = await this.getIdentificadores();
            App.toast('Código salvo com sucesso!', 'success');
        } catch (e) {
            App.toast(e.message, 'error');
        }
    },

    // --- VIEW TOTVS (Contratos/Propostas) ---
    async renderTotvsView(fornecedor, container) {
        container.innerHTML = '<div class="empty-state"><p>Carregando contratos TOTVS...</p></div>';
        
        try {
            const contratos = await API.getContratosPorFornecedor(fornecedor.id);

            let html = `
                <div style="background: var(--glass); border-radius: 8px; padding: 20px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 20px;">
                        <div>
                            <h4 style="font-weight: 600;">Contratos / Propostas TOTVS</h4>
                            <p style="font-size: 0.85rem; color: var(--text-muted);">
                                Adicione os números de contrato para cada empresa.
                            </p>
                        </div>
                    </div>
                    <div style="display: flex; flex-direction: column; gap: 20px;">
            `;

            this.empresas.forEach(emp => {
                const contratosEmpresa = contratos.filter(c => c.empresa_grupo_id === emp.id);
                
                html += `
                    <div style="border: 1px solid var(--border); border-radius: 8px; padding: 15px; background: rgba(0,0,0,0.2);">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 15px;">
                            <h5 style="font-weight: 600; font-size: 0.95rem;">🏢 ${emp.sigla}</h5>
                            <button class="btn btn-primary btn-sm" onclick="Cadastros.abrirModalContrato(${fornecedor.id}, ${emp.id}, '${emp.sigla}')">
                                ➕ Adicionar Contrato
                            </button>
                        </div>
                `;

                if (contratosEmpresa.length === 0) {
                    html += `<p style="font-size:0.8rem; color:var(--text-muted); text-align:center; padding: 10px;">Nenhum contrato cadastrado.</p>`;
                } else {
                    html += `
                        <table class="data-table" style="font-size: 0.85rem;">
                            <thead>
                                <tr>
                                    <th>Cód. Contrato (Proposta)</th>
                                    <th>Cód. Fornecedor</th>
                                    <th>Descrição</th>
                                    <th>Valor</th>
                                    <th>Dia Venc.</th>
                                    <th>Encerramento</th>
                                    <th>Ações</th>
                                </tr>
                            </thead>
                            <tbody>
                    `;
                    contratosEmpresa.forEach(c => {
                        const MESES_ABREV = ['', 'Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];
                        let encerrBadge = '<span style="color:var(--text-muted); font-size:0.8rem;">—</span>';
                        if (c.mes_encerramento && c.ano_encerramento) {
                            encerrBadge = `<span class="badge badge-cancelado" style="font-size:0.7rem;">Encerra ${MESES_ABREV[c.mes_encerramento]}/${c.ano_encerramento}</span>`;
                        }
                        html += `
                            <tr>
                                <td><strong>${c.codigo_contrato || '—'}</strong></td>
                                <td>${c.codigo_fornecedor || '—'}</td>
                                <td>${c.descricao || '—'}</td>
                                <td>${c.valor_mensal ? c.valor_mensal.toLocaleString('pt-BR', {style:'currency', currency:'BRL'}) : '—'}</td>
                                <td>Dia ${c.dia_vencimento}</td>
                                <td>${encerrBadge}</td>
                                <td style="white-space:nowrap;">
                                    <button class="btn btn-secondary btn-sm btn-icon" onclick="Cadastros.abrirModalEditarContrato(${c.id}, ${fornecedor.id})" title="Editar Contrato">✏️</button>
                                    <button class="btn btn-secondary btn-sm btn-icon" onclick="Cadastros.abrirModalEncerramento(${c.id}, '${c.codigo_contrato || ''}', ${c.mes_encerramento || 'null'}, ${c.ano_encerramento || 'null'}, ${fornecedor.id})" title="Definir Encerramento">📅</button>
                                    <button class="btn btn-danger btn-sm btn-icon" onclick="Cadastros.deletarContrato(${c.id}, ${fornecedor.id})" title="Remover">🗑️</button>
                                </td>
                            </tr>
                        `;
                    });
                    html += `</tbody></table>`;
                }

                html += `</div>`;
            });

            html += `</div></div>`;
            container.innerHTML = html;

        } catch (e) {
            container.innerHTML = '<div class="empty-state"><p>Erro ao carregar contratos.</p></div>';
            console.error(e);
        }
    },

    abrirModalContrato(fornecedorId, empresaId, empresaSigla) {
        App.openModal(`Novo Contrato - ${empresaSigla}`, `
            <input type="hidden" id="novo-ct-forn" value="${fornecedorId}">
            <input type="hidden" id="novo-ct-emp" value="${empresaId}">
            <div class="form-row">
                <div class="form-group" style="flex: 1;">
                    <label class="form-label">Cód. Contrato / Proposta *</label>
                    <input type="text" class="form-input" id="novo-ct-codigo" placeholder="Ex: AAJR37">
                </div>
                <div class="form-group" style="flex: 1;">
                    <label class="form-label">Cód. Fornecedor (Planilha)</label>
                    <input type="text" class="form-input" id="novo-ct-cod-forn" placeholder="Ex: 02320-01">
                </div>
            </div>
            <div class="form-group">
                <label class="form-label">Descrição Breve</label>
                <input type="text" class="form-input" id="novo-ct-desc" placeholder="Ex: Licença T-Cloud">
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label class="form-label">Valor Mensal Previsto</label>
                    <input type="number" step="0.01" class="form-input" id="novo-ct-valor" value="0">
                </div>
                <div class="form-group">
                    <label class="form-label">Dia de Vencimento</label>
                    <input type="number" class="form-input" id="novo-ct-dia" value="15" min="1" max="31">
                </div>
            </div>
        `, [
            { text: 'Cancelar', class: 'btn btn-secondary', action: () => App.closeModal() },
            { text: 'Salvar Contrato', class: 'btn btn-primary', action: () => this.salvarNovoContrato() }
        ]);
    },

    async salvarNovoContrato() {
        const fornecedorId = document.getElementById('novo-ct-forn').value;
        const data = {
            fornecedor_id: parseInt(fornecedorId),
            empresa_grupo_id: parseInt(document.getElementById('novo-ct-emp').value),
            codigo_contrato: document.getElementById('novo-ct-codigo').value || null,
            codigo_fornecedor: document.getElementById('novo-ct-cod-forn').value || null,
            descricao: document.getElementById('novo-ct-desc').value || null,
            valor_mensal: parseFloat(document.getElementById('novo-ct-valor').value) || 0,
            dia_vencimento: parseInt(document.getElementById('novo-ct-dia').value) || 15
        };

        if (!data.codigo_contrato) {
            App.toast('Informe o código do contrato', 'error');
            return;
        }

        try {
            await API.criarContrato(data);
            App.closeModal();
            App.toast('Contrato adicionado!', 'success');
            this.renderContent(fornecedorId); // reload view
        } catch (e) {
            App.toast('Erro ao adicionar contrato: ' + e.message, 'error');
        }
    },

    async deletarContrato(contratoId, fornecedorId) {
        if (!confirm('Tem certeza que deseja remover este contrato? NFs passadas vinculadas a ele não serão alteradas.')) return;
        try {
            await API.deletarContrato(contratoId);
            App.toast('Contrato removido', 'success');
            this.renderContent(fornecedorId);
        } catch (e) {
            App.toast('Erro: ' + e.message, 'error');
        }
    },

    abrirModalEncerramento(contratoId, codigoContrato, mesAtual, anoAtual, fornecedorId) {
        const MESES = ['Janeiro','Fevereiro','Março','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro'];
        const mesOptions = MESES.map((m, i) =>
            `<option value="${i + 1}" ${mesAtual == (i + 1) ? 'selected' : ''}>${m}</option>`
        ).join('');

        const anoCorrente = new Date().getFullYear();
        let anoOptions = '';
        for (let y = anoCorrente; y <= anoCorrente + 3; y++) {
            anoOptions += `<option value="${y}" ${anoAtual == y ? 'selected' : ''}>${y}</option>`;
        }

        App.openModal(`📅 Encerramento — ${codigoContrato || 'Contrato'}`, `
            <p style="font-size:0.85rem; color:var(--text-secondary); margin-bottom:15px;">
                Ao definir o mês de encerramento, todos os lançamentos mensais <strong>a partir desse mês</strong> 
                serão automaticamente marcados como <span class="badge badge-cancelado" style="font-size:0.7rem;">CANCELADO</span> 
                na matriz de contratos.
            </p>
            <input type="hidden" id="enc-contrato-id" value="${contratoId}">
            <input type="hidden" id="enc-fornecedor-id" value="${fornecedorId}">
            <div class="form-row">
                <div class="form-group" style="flex:1;">
                    <label class="form-label">Mês de Encerramento</label>
                    <select class="form-select" id="enc-mes">
                        <option value="">Sem encerramento</option>
                        ${mesOptions}
                    </select>
                </div>
                <div class="form-group" style="flex:1;">
                    <label class="form-label">Ano</label>
                    <select class="form-select" id="enc-ano">
                        ${anoOptions}
                    </select>
                </div>
            </div>
            <div class="form-group" style="margin-top:10px;">
                <label style="display:flex;align-items:center;gap:8px;cursor:pointer;">
                    <input type="checkbox" id="enc-remover" style="width:16px;height:16px;accent-color:var(--danger);">
                    <span style="font-size:0.82rem; color:var(--text-secondary);">Remover encerramento (manter contrato ativo indefinidamente)</span>
                </label>
            </div>
        `, [
            { text: 'Cancelar', class: 'btn btn-secondary', action: () => App.closeModal() },
            { text: 'Salvar Encerramento', class: 'btn btn-primary', action: () => this.salvarEncerramento() }
        ]);

        // Se marcar "remover", desabilitar selects
        document.getElementById('enc-remover').addEventListener('change', (e) => {
            document.getElementById('enc-mes').disabled = e.target.checked;
            document.getElementById('enc-ano').disabled = e.target.checked;
        });
    },

    async salvarEncerramento() {
        const contratoId = document.getElementById('enc-contrato-id').value;
        const fornecedorId = document.getElementById('enc-fornecedor-id').value;
        const remover = document.getElementById('enc-remover').checked;

        let mes = null;
        let ano = null;

        if (!remover) {
            mes = document.getElementById('enc-mes').value;
            ano = document.getElementById('enc-ano').value;
            if (!mes) {
                App.toast('Selecione o mês de encerramento ou marque "Remover"', 'error');
                return;
            }
            mes = parseInt(mes);
            ano = parseInt(ano);
        }

        try {
            const params = new URLSearchParams();
            if (mes) params.set('mes', mes);
            if (ano) params.set('ano', ano);
            
            await API.patch(`/api/cadastros/contratos/${contratoId}/encerramento?${params.toString()}`);
            App.closeModal();
            App.toast(remover ? 'Encerramento removido!' : `Encerramento definido para ${mes}/${ano}. Lançamentos cancelados automaticamente!`, 'success');
            this.renderContent(fornecedorId);
        } catch (e) {
            App.toast('Erro: ' + e.message, 'error');
        }
    },

    async abrirModalEditarContrato(contratoId, fornecedorId) {
        try {
            const contrato = await API.get(`/api/contratos/${contratoId}`);
            
            const empresaOptions = this.empresas.map(emp => 
                `<option value="${emp.id}" ${emp.id === contrato.empresa_grupo_id ? 'selected' : ''}>${emp.sigla} - ${emp.nome_completo}</option>`
            ).join('');

            App.openModal(`✏️ Editar Contrato - ${contrato.codigo_contrato || ''}`, `
                <input type="hidden" id="edit-ct-id" value="${contrato.id}">
                <input type="hidden" id="edit-ct-forn" value="${fornecedorId}">
                <div class="form-group">
                    <label class="form-label">Empresa *</label>
                    <select class="form-select" id="edit-ct-empresa">
                        ${empresaOptions}
                    </select>
                </div>
                <div class="form-row">
                    <div class="form-group" style="flex: 1;">
                        <label class="form-label">Cód. Contrato / Proposta *</label>
                        <input type="text" class="form-input" id="edit-ct-codigo" value="${contrato.codigo_contrato || ''}" placeholder="Ex: AAJR37">
                    </div>
                    <div class="form-group" style="flex: 1;">
                        <label class="form-label">Cód. Fornecedor (Planilha)</label>
                        <input type="text" class="form-input" id="edit-ct-cod-forn" value="${contrato.codigo_fornecedor || ''}" placeholder="Ex: 02320-01">
                    </div>
                </div>
                <div class="form-group">
                    <label class="form-label">Descrição Breve</label>
                    <input type="text" class="form-input" id="edit-ct-desc" value="${contrato.descricao || ''}" placeholder="Ex: Licença T-Cloud">
                </div>
                <div class="form-row">
                    <div class="form-group" style="flex: 1;">
                        <label class="form-label">Valor Mensal Previsto</label>
                        <input type="number" step="0.01" class="form-input" id="edit-ct-valor" value="${contrato.valor_mensal !== null && contrato.valor_mensal !== undefined ? contrato.valor_mensal : 0}">
                    </div>
                    <div class="form-group" style="flex: 1;">
                        <label class="form-label">Dia de Vencimento</label>
                        <input type="number" class="form-input" id="edit-ct-dia" value="${contrato.dia_vencimento || 15}" min="1" max="31">
                    </div>
                </div>
                <div class="form-group">
                    <label class="form-label">Condição de Pagamento</label>
                    <input type="text" class="form-input" id="edit-ct-condicao" value="${contrato.condicao_pagamento || 'MENSAL'}" placeholder="Ex: MENSAL">
                </div>
            `, [
                { text: 'Cancelar', class: 'btn btn-secondary', action: () => App.closeModal() },
                { text: 'Salvar Alterações', class: 'btn btn-primary', action: () => this.salvarEdicaoContrato() }
            ]);
        } catch (e) {
            App.toast('Erro ao carregar dados do contrato: ' + e.message, 'error');
        }
    },

    async salvarEdicaoContrato() {
        const contratoId = document.getElementById('edit-ct-id').value;
        const fornecedorId = document.getElementById('edit-ct-forn').value;
        const empresaId = parseInt(document.getElementById('edit-ct-empresa').value);
        const codigoContrato = document.getElementById('edit-ct-codigo').value.trim();
        const codigoFornecedor = document.getElementById('edit-ct-cod-forn').value.trim() || null;
        const descricao = document.getElementById('edit-ct-desc').value.trim() || null;
        const valorMensal = parseFloat(document.getElementById('edit-ct-valor').value) || 0;
        const diaVencimento = parseInt(document.getElementById('edit-ct-dia').value) || 15;
        const condicaoPagamento = document.getElementById('edit-ct-condicao').value.trim() || 'MENSAL';

        if (!codigoContrato) {
            App.toast('Informe o código do contrato', 'error');
            return;
        }

        try {
            await API.atualizarContrato(contratoId, {
                empresa_grupo_id: empresaId,
                codigo_contrato: codigoContrato,
                codigo_fornecedor: codigoFornecedor,
                descricao: descricao,
                valor_mensal: valorMensal,
                dia_vencimento: diaVencimento,
                condicao_pagamento: condicaoPagamento
            });
            App.closeModal();
            App.toast('Contrato atualizado com sucesso!', 'success');
            this.renderContent(fornecedorId);
        } catch (e) {
            App.toast('Erro ao salvar contrato: ' + e.message, 'error');
        }
    }
};
