/**
 * Diretório de Códigos - Consulta rápida unificada de todos os códigos
 * de fornecedores e contratos TOTVS cadastrados no sistema.
 */
const Diretorio = {
    dados: [],
    dadosFiltrados: [],

    async render() {
        const container = document.getElementById('page-diretorio');
        container.innerHTML = `
            <div class="table-toolbar">
                <div style="display:flex;align-items:center;gap:12px">
                    <h3 style="font-size:1rem;font-weight:600">📖 Diretório de Códigos</h3>
                    <span style="font-size:0.78rem;color:var(--text-muted)">
                        Consulta rápida de todos os códigos de fornecedores e contratos.
                    </span>
                </div>
            </div>

            <div class="diretorio-filtros" style="display:flex; gap:12px; margin-bottom:20px; background:var(--glass); padding:15px; border-radius:8px; flex-wrap:wrap; align-items:flex-end;">
                <div class="form-group" style="flex:2; min-width:220px; margin:0;">
                    <label class="form-label" style="font-size:0.78rem;">🔍 Busca rápida</label>
                    <input type="text" class="form-input" id="dir-busca" placeholder="Digite fornecedor, empresa, código ou contrato...">
                </div>
                <div class="form-group" style="flex:1; min-width:140px; margin:0;">
                    <label class="form-label" style="font-size:0.78rem;">Tipo</label>
                    <select class="form-select" id="dir-filter-tipo">
                        <option value="">Todos</option>
                        <option value="COMUM">Comum</option>
                        <option value="TOTVS">TOTVS</option>
                    </select>
                </div>
                <div class="form-group" style="flex:1; min-width:140px; margin:0;">
                    <label class="form-label" style="font-size:0.78rem;">Status</label>
                    <select class="form-select" id="dir-filter-status">
                        <option value="ativos">Somente Ativos</option>
                        <option value="todos">Todos</option>
                        <option value="encerrados">Encerrados / Inativos</option>
                    </select>
                </div>
                <div style="display:flex; align-items:center; gap:8px; padding-bottom:2px;">
                    <span id="dir-contador" style="font-size:0.78rem; color:var(--text-muted);"></span>
                </div>
            </div>

            <div class="data-table-wrapper" style="overflow-x:auto">
                <table class="data-table" id="dir-tabela">
                    <thead>
                        <tr>
                            <th>Fornecedor</th>
                            <th>Empresa</th>
                            <th>Tipo</th>
                            <th>Cód. Fornecedor</th>
                            <th>Cód. Contrato</th>
                            <th>Descrição</th>
                            <th>Status</th>
                            <th style="width:80px">Ação</th>
                        </tr>
                    </thead>
                    <tbody id="dir-tbody"></tbody>
                </table>
            </div>
        `;

        this.bindEvents();
        await this.loadData();
    },

    bindEvents() {
        let timer;
        document.getElementById('dir-busca').addEventListener('input', () => {
            clearTimeout(timer);
            timer = setTimeout(() => this.filtrar(), 150);
        });
        document.getElementById('dir-filter-tipo').addEventListener('change', () => this.filtrar());
        document.getElementById('dir-filter-status').addEventListener('change', () => this.filtrar());
    },

    async loadData() {
        try {
            this.dados = await API.get('/api/cadastros/diretorio');
            this.filtrar();
        } catch (e) {
            App.toast('Erro ao carregar diretório', 'error');
            console.error(e);
        }
    },

    filtrar() {
        const busca = (document.getElementById('dir-busca')?.value || '').toLowerCase().trim();
        const tipo = document.getElementById('dir-filter-tipo')?.value || '';
        const status = document.getElementById('dir-filter-status')?.value || 'ativos';

        this.dadosFiltrados = this.dados.filter(item => {
            // Filtro de tipo
            if (tipo && item.tipo !== tipo) return false;

            // Filtro de status
            if (status === 'ativos' && (!item.ativo || item.mes_encerramento)) return false;
            if (status === 'encerrados' && item.ativo && !item.mes_encerramento) return false;

            // Filtro de busca textual
            if (busca) {
                const texto = [
                    item.fornecedor, item.empresa, item.codigo_fornecedor,
                    item.codigo_contrato, item.descricao, item.tipo
                ].filter(Boolean).join(' ').toLowerCase();
                return texto.includes(busca);
            }
            return true;
        });

        this.renderTable();
    },

    renderTable() {
        const tbody = document.getElementById('dir-tbody');
        const contador = document.getElementById('dir-contador');

        if (!this.dadosFiltrados.length) {
            tbody.innerHTML = `
                <tr><td colspan="8">
                    <div class="empty-state" style="padding:40px">
                        <div class="empty-icon">🔍</div>
                        <h3>Nenhum resultado encontrado</h3>
                        <p>Tente ajustar os filtros ou a busca.</p>
                    </div>
                </td></tr>`;
            contador.textContent = '0 resultados';
            return;
        }

        contador.textContent = `${this.dadosFiltrados.length} resultado${this.dadosFiltrados.length > 1 ? 's' : ''}`;

        const MESES_ABREV = ['', 'Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];

        tbody.innerHTML = this.dadosFiltrados.map(item => {
            const inativo = !item.ativo;
            const encerrado = item.mes_encerramento && item.ano_encerramento;
            const rowClass = inativo ? 'style="opacity:0.45; text-decoration:line-through;"' :
                             encerrado ? 'style="opacity:0.7; border-left:3px solid var(--cancelado-color, #a855f7);"' : '';

            const tipoBadge = item.tipo === 'TOTVS'
                ? '<span class="badge badge-faturado" style="font-size:0.7rem;">TOTVS</span>'
                : '<span class="badge badge-pendente" style="font-size:0.7rem;">Comum</span>';

            let statusBadge;
            if (inativo) {
                statusBadge = '<span class="badge badge-vencido" style="font-size:0.7rem;">Inativo</span>';
            } else if (encerrado) {
                statusBadge = `<span class="badge badge-cancelado" style="font-size:0.7rem;">Encerra ${MESES_ABREV[item.mes_encerramento]}/${item.ano_encerramento}</span>`;
            } else {
                statusBadge = '<span class="badge badge-ok" style="font-size:0.7rem;">Ativo</span>';
            }

            const codForn = item.codigo_fornecedor || '<span style="color:var(--text-muted)">—</span>';
            const codContrato = item.codigo_contrato || '<span style="color:var(--text-muted)">—</span>';

            // Botões de copiar: só exibe se tiver código
            let acoes = '';
            if (item.codigo_fornecedor) {
                acoes += `<button class="btn btn-secondary btn-sm btn-icon" onclick="Diretorio.copiar('${item.codigo_fornecedor}')" title="Copiar Cód. Fornecedor">📋</button> `;
            }
            if (item.codigo_contrato) {
                acoes += `<button class="btn btn-secondary btn-sm btn-icon" onclick="Diretorio.copiar('${item.codigo_contrato}')" title="Copiar Cód. Contrato">📋</button>`;
            }

            return `
                <tr ${rowClass}>
                    <td><strong>${item.fornecedor}</strong></td>
                    <td>${item.empresa}</td>
                    <td>${tipoBadge}</td>
                    <td style="font-family:monospace; font-weight:600;">${codForn}</td>
                    <td style="font-family:monospace; font-weight:600;">${codContrato}</td>
                    <td style="font-size:0.82rem; color:var(--text-secondary);">${item.descricao || '—'}</td>
                    <td>${statusBadge}</td>
                    <td>${acoes || '—'}</td>
                </tr>`;
        }).join('');
    },

    async copiar(texto) {
        try {
            await navigator.clipboard.writeText(texto);
            App.toast(`📋 "${texto}" copiado!`, 'success');
        } catch (e) {
            // Fallback para navegadores que não suportam clipboard API
            const ta = document.createElement('textarea');
            ta.value = texto;
            ta.style.position = 'fixed';
            ta.style.left = '-9999px';
            document.body.appendChild(ta);
            ta.select();
            document.execCommand('copy');
            document.body.removeChild(ta);
            App.toast(`📋 "${texto}" copiado!`, 'success');
        }
    }
};
