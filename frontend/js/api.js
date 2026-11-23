/**
 * API Client - Comunicação com o backend FastAPI
 */
const API = {
    baseUrl: '',

    async request(path, options = {}) {
        try {
            const res = await fetch(`${this.baseUrl}${path}`, {
                headers: { 'Content-Type': 'application/json', ...options.headers },
                ...options,
            });
            if (!res.ok) {
                const err = await res.json().catch(() => ({ detail: res.statusText }));
                throw new Error(err.detail || `Erro ${res.status}`);
            }
            if (res.headers.get('content-type')?.includes('application/json')) {
                return await res.json();
            }
            return res;
        } catch (e) {
            console.error(`[API] ${path}:`, e);
            throw e;
        }
    },

    get(path) { return this.request(path); },
    post(path, data) { return this.request(path, { method: 'POST', body: JSON.stringify(data) }); },
    put(path, data) { return this.request(path, { method: 'PUT', body: JSON.stringify(data) }); },
    patch(path, data) { return this.request(path, { method: 'PATCH', body: data ? JSON.stringify(data) : undefined }); },
    del(path) { return this.request(path, { method: 'DELETE' }); },

    // Dashboard
    getKPIs(mes, ano) { return this.get(`/api/dashboard/kpis?mes=${mes}&ano=${ano}`); },
    getGastosFornecedor(ano, mes) { return this.get(`/api/dashboard/gastos-por-fornecedor?ano=${ano}${mes ? '&mes=' + mes : ''}`); },
    getGastosEmpresa(ano, mes) { return this.get(`/api/dashboard/gastos-por-empresa?ano=${ano}${mes ? '&mes=' + mes : ''}`); },
    getGastosMensais(ano) { return this.get(`/api/dashboard/gastos-mensais?ano=${ano}`); },
    getProximosVencimentos(limit = 10) { return this.get(`/api/dashboard/proximos-vencimentos?limit=${limit}`); },
    getNotificacoes() { return this.get('/api/dashboard/notificacoes'); },

    // Notas Fiscais
    getNotas(params = {}) {
        const q = new URLSearchParams(params).toString();
        return this.get(`/api/notas-fiscais/?${q}`);
    },
    getNota(id) { return this.get(`/api/notas-fiscais/${id}`); },
    criarNota(data) { return this.post('/api/notas-fiscais/', data); },
    atualizarNota(id, data) { return this.put(`/api/notas-fiscais/${id}`, data); },
    deletarNota(id) { return this.del(`/api/notas-fiscais/${id}`); },
    atualizarStatusNota(id, status) { return this.patch(`/api/notas-fiscais/${id}/status?status=${status}`); },
    toggleEmail(id) { return this.patch(`/api/notas-fiscais/${id}/email`); },
    atualizarProtocolo(id, protocolo) { return this.patch(`/api/notas-fiscais/${id}/protocolo?protocolo=${encodeURIComponent(protocolo)}`); },

    // Contratos
    getContratos(params = {}) { const q = new URLSearchParams(params).toString(); return this.get(`/api/contratos/?${q}`); },
    criarContrato(data) { return this.post('/api/contratos/', data); },
    atualizarContrato(id, data) { return this.put(`/api/contratos/${id}`, data); },
    deletarContrato(id) { return this.del(`/api/contratos/${id}`); },
    getMatriz(ano, mes) { return this.get(`/api/contratos/matriz/${ano}${mes ? '?mes=' + mes : ''}`); },
  getNotasDoLancamento(lancamentoId) { return this.get(`/api/contratos/lancamentos/${lancamentoId}/notas`); },
    getLancamentos(params = {}) { const q = new URLSearchParams(params).toString(); return this.get(`/api/contratos/lancamentos/?${q}`); },
    atualizarLancamento(id, data) { return this.put(`/api/contratos/lancamentos/${id}`, data); },
    atualizarStatusLancamento(id, status) { return this.patch(`/api/contratos/lancamentos/${id}/status?status=${encodeURIComponent(status)}`); },
    atualizarVencimentoLancamento(id, dataVencimento, replicarMeses = false, replicarEmpresas = false) { 
        return this.patch(`/api/contratos/lancamentos/${id}/vencimento?data_vencimento=${encodeURIComponent(dataVencimento)}&replicar_meses=${replicarMeses}&replicar_empresas=${replicarEmpresas}`); 
    },
    getContratosPorFornecedor(fornecedorId) { return this.get(`/api/contratos/fornecedor/${fornecedorId}`); },
    gerarLancamentos(ano) { return this.post(`/api/contratos/gerar-lancamentos/${ano}`); },
    getNotasCandidatas(lancamentoId) { return this.get(`/api/contratos/lancamentos/${lancamentoId}/notas-candidatas`); },
    vincularNotaManual(lancamentoId, notaId) { return this.post(`/api/contratos/lancamentos/${lancamentoId}/vincular-nota?nota_id=${notaId}`); },

    // Empresas
    getEmpresas() { return this.get('/api/empresas/?ativo=true'); },
    criarEmpresa(data) { return this.post('/api/empresas/', data); },
    atualizarEmpresa(id, data) { return this.put(`/api/empresas/${id}`, data); },
    deletarEmpresa(id) { return this.del(`/api/empresas/${id}`); },

    // Fornecedores
    getFornecedores(categoria) { return this.get(`/api/fornecedores/${categoria ? '?categoria=' + categoria : ''}`); },
    criarFornecedor(data) { return this.post('/api/fornecedores/', data); },
    atualizarFornecedor(id, data) { return this.put(`/api/fornecedores/${id}`, data); },
    deletarFornecedor(id) { return this.del(`/api/fornecedores/${id}`); },

    // Exportação
    exportarExcel(mes, ano) {
        const q = `ano=${ano}${mes ? '&mes=' + mes : ''}`;
        window.open(`/api/exportacao/excel?${q}`, '_blank');
    },
};
