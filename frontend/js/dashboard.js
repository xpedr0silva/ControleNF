/**
 * Dashboard Module - KPIs, Gráficos, Vencimentos
 */
const Dashboard = {
    charts: {},

    async render() {
        const container = document.getElementById('page-dashboard');
        container.innerHTML = `
            <div class="kpi-grid" id="kpi-grid"></div>
            <div class="charts-grid">
                <div class="chart-card">
                    <h3>📊 Gastos Mensais</h3>
                    <div class="chart-container"><canvas id="chart-mensal"></canvas></div>
                </div>
                <div class="chart-card">
                    <h3>🏪 Por Fornecedor</h3>
                    <div class="chart-container"><canvas id="chart-fornecedor"></canvas></div>
                </div>
            </div>
            <div class="charts-grid">
                <div class="chart-card">
                    <h3>⏰ Próximos Vencimentos</h3>
                    <div class="alert-list" id="proximos-vencimentos"></div>
                </div>
                <div class="chart-card">
                    <h3>📋 Contratos do Mês</h3>
                    <div id="contratos-resumo"></div>
                </div>
            </div>
        `;
        await this.loadData();
    },

    async loadData() {
        const mes = App.mesSelecionado;
        const ano = App.anoSelecionado;
        try {
            const [kpis, gastosMensais, gastosForn, vencimentos] = await Promise.all([
                API.getKPIs(mes, ano),
                API.getGastosMensais(ano),
                API.getGastosFornecedor(ano, mes),
                API.getProximosVencimentos(8),
            ]);
            this.renderKPIs(kpis);
            this.renderChartMensal(gastosMensais);
            this.renderChartFornecedor(gastosForn);
            this.renderVencimentos(vencimentos);
            this.renderContratosResumo(kpis);
        } catch (e) {
            console.error('Dashboard error:', e);
        }
    },

    renderKPIs(data) {
        const fmt = v => v.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
        document.getElementById('kpi-grid').innerHTML = `
            <div class="kpi-card info">
                <div class="kpi-header"><div class="kpi-icon">📄</div></div>
                <div class="kpi-label">Total de NFs</div>
                <div class="kpi-value">${data.total_nfs}</div>
                <div class="kpi-sub">${data.nome_mes} ${data.ano}</div>
            </div>
            <div class="kpi-card success">
                <div class="kpi-header"><div class="kpi-icon">✅</div></div>
                <div class="kpi-label">NFs OK</div>
                <div class="kpi-value">${data.nfs_ok}</div>
                <div class="kpi-sub">Pré-nota confirmada</div>
            </div>
            <div class="kpi-card warning">
                <div class="kpi-header"><div class="kpi-icon">⏳</div></div>
                <div class="kpi-label">NFs Pendentes</div>
                <div class="kpi-value">${data.nfs_pendentes}</div>
                <div class="kpi-sub">Aguardando pré-nota</div>
            </div>
            <div class="kpi-card danger">
                <div class="kpi-header"><div class="kpi-icon">🔴</div></div>
                <div class="kpi-label">NFs Vencidas</div>
                <div class="kpi-value">${data.nfs_vencidas}</div>
                <div class="kpi-sub">Atenção necessária</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-header"><div class="kpi-icon">💰</div></div>
                <div class="kpi-label">Valor Total</div>
                <div class="kpi-value" style="font-size:1.4rem">${fmt(data.valor_total)}</div>
                <div class="kpi-sub">${data.nome_mes} ${data.ano}</div>
            </div>
        `;
    },

    renderChartMensal(data) {
        if (this.charts.mensal) this.charts.mensal.destroy();
        const ctx = document.getElementById('chart-mensal');
        if (!ctx) return;
        const meses = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'];
        const valores = new Array(12).fill(0);
        const qtds = new Array(12).fill(0);
        data.forEach(d => { valores[d.mes - 1] = d.valor_total; qtds[d.mes - 1] = d.quantidade; });
        this.charts.mensal = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: meses,
                datasets: [{
                    label: 'Valor Total (R$)',
                    data: valores,
                    backgroundColor: 'rgba(99,102,241,0.4)',
                    borderColor: '#6366f1',
                    borderWidth: 2, borderRadius: 6,
                }],
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { ticks: { color: '#94a3b8', callback: v => 'R$ ' + (v/1000).toFixed(0) + 'k' }, grid: { color: 'rgba(45,51,72,0.5)' } },
                    x: { ticks: { color: '#94a3b8' }, grid: { display: false } },
                },
            },
        });
    },

    renderChartFornecedor(data) {
        if (this.charts.fornecedor) this.charts.fornecedor.destroy();
        const ctx = document.getElementById('chart-fornecedor');
        if (!ctx) return;
        const top = data.slice(0, 7);
        const cores = ['#6366f1','#8b5cf6','#a78bfa','#3b82f6','#10b981','#f59e0b','#ef4444'];
        this.charts.fornecedor = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: top.map(d => d.fornecedor),
                datasets: [{ data: top.map(d => d.valor_total), backgroundColor: cores, borderWidth: 0 }],
            },
            options: {
                responsive: true, maintainAspectRatio: false, cutout: '65%',
                plugins: { legend: { position: 'bottom', labels: { color: '#94a3b8', font: { size: 11 }, padding: 12 } } },
            },
        });
    },

    renderVencimentos(data) {
        const el = document.getElementById('proximos-vencimentos');
        if (!data.length) { el.innerHTML = '<div class="empty-state"><p>✅ Nenhum vencimento próximo</p></div>'; return; }
        el.innerHTML = data.map(v => {
            const dot = v.dias_restantes < 0 ? 'red' : v.dias_restantes <= 3 ? 'yellow' : 'green';
            const dias = v.dias_restantes < 0 ? `${Math.abs(v.dias_restantes)}d atrás` : v.dias_restantes === 0 ? 'HOJE' : `em ${v.dias_restantes}d`;
            const fmt = v.valor ? v.valor.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }) : '-';
            return `<div class="alert-item">
                <div class="alert-dot ${dot}"></div>
                <div class="alert-info">
                    <div class="alert-title">${v.fornecedor}</div>
                    <div class="alert-sub">${v.empresa} • ${dias}</div>
                </div>
                <div style="text-align:right"><div class="alert-value">${fmt}</div><div class="alert-date">${new Date(v.data_vencimento + (v.data_vencimento.includes('T') ? '' : 'T12:00:00')).toLocaleDateString('pt-BR')}</div></div>
            </div>`;
        }).join('');
    },

    renderContratosResumo(kpis) {
        const el = document.getElementById('contratos-resumo');
        const pct = kpis.percentual_faturado;
        el.innerHTML = `
            <div style="text-align:center;padding:20px 0">
                <div style="font-size:2.5rem;font-weight:800;color:var(--accent)">${pct}%</div>
                <div style="font-size:0.85rem;color:var(--text-muted);margin:8px 0">Contratos faturados</div>
                <div class="progress-bar"><div class="progress-fill" style="width:${pct}%"></div></div>
                <div style="margin-top:12px;font-size:0.8rem;color:var(--text-secondary)">${kpis.contratos_faturados} de ${kpis.contratos_total} contratos</div>
            </div>
        `;
    },
};
