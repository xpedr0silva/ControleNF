/**
 * Relatórios Module
 */
const Relatorios = {
    async render() {
        const container = document.getElementById('page-relatorios');
        container.innerHTML = `
            <div class="kpi-grid" style="grid-template-columns:repeat(3,1fr)">
                <div class="chart-card" style="cursor:pointer" onclick="API.exportarExcel(App.mesSelecionado, App.anoSelecionado)">
                    <div style="text-align:center;padding:30px 0">
                        <div style="font-size:2.5rem;margin-bottom:12px">📥</div>
                        <h3 style="font-size:1rem;margin-bottom:6px">Exportar Mês Atual</h3>
                        <p style="font-size:0.8rem;color:var(--text-muted)">Excel do mês selecionado</p>
                    </div>
                </div>
                <div class="chart-card" style="cursor:pointer" onclick="API.exportarExcel(null, App.anoSelecionado)">
                    <div style="text-align:center;padding:30px 0">
                        <div style="font-size:2.5rem;margin-bottom:12px">📊</div>
                        <h3 style="font-size:1rem;margin-bottom:6px">Exportar Ano Completo</h3>
                        <p style="font-size:0.8rem;color:var(--text-muted)">Todas as abas mensais</p>
                    </div>
                </div>
                <div class="chart-card" id="card-resumo-anual">
                    <div style="text-align:center;padding:30px 0">
                        <div style="font-size:2.5rem;margin-bottom:12px">📈</div>
                        <h3 style="font-size:1rem;margin-bottom:6px">Resumo Anual</h3>
                        <p style="font-size:0.8rem;color:var(--text-muted)" id="resumo-total">Carregando...</p>
                    </div>
                </div>
            </div>
            <div class="chart-card" style="margin-top:20px">
                <h3>📊 Comparativo Mensal - ${App.anoSelecionado}</h3>
                <div class="chart-container" style="height:320px"><canvas id="chart-relatorio"></canvas></div>
            </div>
            <div class="charts-grid" style="margin-top:20px">
                <div class="chart-card">
                    <h3>🏢 Gastos por Empresa do Grupo</h3>
                    <div id="rel-empresas"></div>
                </div>
                <div class="chart-card">
                    <h3>🏪 Top Fornecedores</h3>
                    <div id="rel-fornecedores"></div>
                </div>
            </div>
        `;
        await this.loadData();
    },

    async loadData() {
        const ano = App.anoSelecionado;
        try {
            const [mensais, empresas, fornecedores] = await Promise.all([
                API.getGastosMensais(ano),
                API.getGastosEmpresa(ano),
                API.getGastosFornecedor(ano),
            ]);
            this.renderChart(mensais);
            this.renderEmpresas(empresas);
            this.renderFornecedores(fornecedores);
            const total = mensais.reduce((s, m) => s + m.valor_total, 0);
            document.getElementById('resumo-total').textContent = total.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
        } catch (e) { console.error(e); }
    },

    renderChart(data) {
        const ctx = document.getElementById('chart-relatorio');
        if (!ctx) return;
        const meses = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'];
        const valores = new Array(12).fill(0);
        const qtds = new Array(12).fill(0);
        data.forEach(d => { valores[d.mes - 1] = d.valor_total; qtds[d.mes - 1] = d.quantidade; });
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: meses,
                datasets: [
                    { label: 'Valor (R$)', data: valores, borderColor: '#6366f1', backgroundColor: 'rgba(99,102,241,0.1)', fill: true, tension: 0.4, borderWidth: 2 },
                    { label: 'Qtd NFs', data: qtds, borderColor: '#10b981', backgroundColor: 'rgba(16,185,129,0.1)', fill: false, tension: 0.4, borderWidth: 2, yAxisID: 'y1' },
                ],
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { labels: { color: '#94a3b8' } } },
                scales: {
                    y: { ticks: { color: '#94a3b8', callback: v => 'R$ ' + (v/1000).toFixed(0) + 'k' }, grid: { color: 'rgba(45,51,72,0.5)' } },
                    y1: { position: 'right', ticks: { color: '#10b981' }, grid: { display: false } },
                    x: { ticks: { color: '#94a3b8' }, grid: { display: false } },
                },
            },
        });
    },

    renderEmpresas(data) {
        const el = document.getElementById('rel-empresas');
        const fmt = v => v.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
        const max = data.length ? data[0].valor_total : 1;
        el.innerHTML = data.map(d => `
            <div style="margin-bottom:12px">
                <div style="display:flex;justify-content:space-between;font-size:0.85rem;margin-bottom:4px">
                    <span style="font-weight:600">${d.empresa}</span>
                    <span style="color:var(--text-muted)">${fmt(d.valor_total)} (${d.quantidade} NFs)</span>
                </div>
                <div class="progress-bar"><div class="progress-fill" style="width:${(d.valor_total / max * 100)}%"></div></div>
            </div>
        `).join('');
    },

    renderFornecedores(data) {
        const el = document.getElementById('rel-fornecedores');
        const fmt = v => v.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
        el.innerHTML = '<div class="alert-list">' + data.slice(0, 10).map((d, i) => `
            <div class="alert-item">
                <div style="width:24px;height:24px;border-radius:6px;background:var(--accent-soft);color:var(--accent);display:flex;align-items:center;justify-content:center;font-size:0.75rem;font-weight:700">${i + 1}</div>
                <div class="alert-info"><div class="alert-title">${d.fornecedor}</div><div class="alert-sub">${d.quantidade} NFs</div></div>
                <div class="alert-value">${fmt(d.valor_total)}</div>
            </div>
        `).join('') + '</div>';
    },
};
