/**
 * Contratos Mensais Module - Matriz read-only, status auto-derivado das NFs
 * Suporta multiplas NFs por lancamento mensal
 */
const Contratos = {
  MESES: ['JAN','FEV','MAR','ABR','MAI','JUN','JUL','AGO','SET','OUT','NOV','DEZ'],

  async render() {
    const container = document.getElementById('page-contratos');
    container.innerHTML = `
      <div class="table-toolbar">
        <div style="display:flex;align-items:center;gap:12px">
          <h3 style="font-size:1rem;font-weight:600">Matriz de Contratos ${App.anoSelecionado}</h3>
          <span style="font-size:0.78rem;color:var(--text-muted)">
            O status atualiza automaticamente ao lan\u00e7ar NFs
          </span>
        </div>
        <div class="table-filters">
          <button class="btn btn-secondary" id="btn-gerar-lancamentos">\u26a1 Gerar Lan\u00e7amentos</button>
          <button class="btn btn-primary" id="btn-novo-contrato">\u2795 Novo Contrato</button>
        </div>
      </div>
      <div style="display:flex;gap:16px;margin-bottom:16px;flex-wrap:wrap">
        <div style="display:flex;align-items:center;gap:6px;font-size:0.78rem;color:var(--text-muted)">
          <span style="width:14px;height:14px;border-radius:4px;background:var(--success-soft);display:inline-block"></span> Nota Lan\u00e7ada
        </div>
        <div style="display:flex;align-items:center;gap:6px;font-size:0.78rem;color:var(--text-muted)">
          <span style="width:14px;height:14px;border-radius:4px;background:var(--warning-soft);display:inline-block"></span> Pendente
        </div>
        <div style="display:flex;align-items:center;gap:6px;font-size:0.78rem;color:var(--text-muted)">
          <span style="width:14px;height:14px;border-radius:4px;background:var(--danger-soft);display:inline-block"></span> Vencido (sem NF)
        </div>
        <div style="display:flex;align-items:center;gap:6px;font-size:0.78rem;color:var(--text-muted)">
          <span style="width:14px;height:14px;border-radius:4px;background:rgba(139,92,246,0.2);display:inline-flex;align-items:center;justify-content:center;font-size:0.6rem">\ud83d\udfe3</span> Cancelado
        </div>
        <div style="display:flex;align-items:center;gap:6px;font-size:0.78rem;color:var(--text-muted)">
          <span style="width:14px;height:14px;border-radius:4px;background:rgba(107,114,128,0.2);display:inline-flex;align-items:center;justify-content:center;font-size:0.6rem">\u26aa</span> N\u00e3o se Aplica
        </div>
      </div>
      <div class="data-table-wrapper matrix-wrapper" id="matriz-container">
        <div class="empty-state"><p>Carregando...</p></div>
      </div>
    `;
    document.getElementById('btn-gerar-lancamentos').addEventListener('click', () => this.gerarLancamentos());
    document.getElementById('btn-novo-contrato').addEventListener('click', () => this.openContratoModal());
    await this.loadData();
  },

  async loadData() {
    try {
      const matriz = await API.getMatriz(App.anoSelecionado);
      this.renderMatriz(matriz);
    } catch (e) { console.error(e); }
  },

  renderMatriz(data) {
    const container = document.getElementById('matriz-container');
    if (!data.length) {
      container.innerHTML = '<div class="empty-state"><div class="empty-icon">\ud83d\udcc5</div><h3>Nenhum lan\u00e7amento</h3><p>Clique em "Gerar Lan\u00e7amentos" para criar os lan\u00e7amentos do ano</p></div>';
      return;
    }
    let html = '<table class="matrix-table"><thead><tr><th>Fornecedor</th>';
    this.MESES.forEach(mesNomeCabecalho => html += `<th>${mesNomeCabecalho}</th>`);
    html += '</tr></thead><tbody>';

    data.forEach(row => {
      html += `<tr><td>${row.fornecedor}</td>`;
      for (let mesNum = 1; mesNum <= 12; mesNum++) {
        const cells = row.meses[mesNum] || [];
        html += '<td>';
        
        if (cells.length === 0) {
          html += '<span style="color:var(--text-muted)">\u2014</span>';
        } else {
          // Agrupar por empresa (caso haja contratos de empresas diferentes no mesmo fornecedor)
          const porEmpresa = {};
          cells.forEach(c => {
            const empKey = (c.empresa || 'S/E').trim().toUpperCase();
            if (!porEmpresa[empKey]) porEmpresa[empKey] = [];
            porEmpresa[empKey].push(c);
          });

          html += '<div class="matrix-cell">';
          Object.keys(porEmpresa).forEach(empKey => {
            const grupo = porEmpresa[empKey];
            const emp = grupo[0].empresa; // Nome original para exibir
            const total = grupo.length;
            const lancados = grupo.filter(c => c.nota_lancada).length;
            const todosCancelados = grupo.every(c => c.status === 'CANCELADO');
            const todosNaoAplica = grupo.every(c => c.status === 'NAO_SE_APLICA');
            const todosLancados = grupo.every(c => c.nota_lancada);
            const temVencido = grupo.some(c => c.status === 'VENCIDO');
            
            let statusConsolidado = 'PENDENTE';
            let icon = '\u23f3'; // Ampulheta
            let cssClass = 'pendente';

            if (todosLancados) {
              statusConsolidado = 'LANCADO';
              icon = '\u2705'; // Check verde
              cssClass = 'faturado';
            } else if (todosCancelados) {
              statusConsolidado = 'CANCELADO';
              icon = '\ud83d\udfe3'; // Circulo Roxo (Linguagem visual solicitada)
              cssClass = 'cancelado';
            } else if (todosNaoAplica) {
              statusConsolidado = 'NAO_SE_APLICA';
              icon = '\u26aa'; // Circulo Branco/Cinza
              cssClass = 'nao-se-aplica';
            } else if (temVencido) {
              statusConsolidado = 'VENCIDO';
              icon = '\ud83d\udd34'; // Bola vermelha
              cssClass = 'vencido';
            } else if (lancados > 0) {
              // Mix de estados ou parcial
              statusConsolidado = 'PARCIAL';
              icon = '\u23f3'; 
              cssClass = 'pendente'; 
            }

            const title = `Empresa: ${emp}\nContratos: ${lancados}/${total} lan\u00e7ados\nClique para ver detalhes`;
            const badgeLabel = total > 1 ? `<span style="font-size:0.6rem;margin-left:2px">${lancados}/${total}</span>` : '';

            html += `<div class="matrix-status ${cssClass}" title="${title}" onclick='Contratos.showGroupDetail(${JSON.stringify(grupo).replace(/'/g, "&#39;")}, "${row.fornecedor}", ${mesNum})'>
              ${icon}${badgeLabel}<span class="matrix-empresa">${emp}</span>
            </div>`;
          });
          html += '</div>';
        }
        html += '</td>';
      }
      html += '</tr>';
    });
    html += '</tbody></table>';
    container.innerHTML = html;
  },

  showGroupDetail(grupo, fornecedor, mes) {
    const cell = grupo[0]; // Referencia para a empresa
    const mesNome = this.MESES[mes - 1];
    const fmt = v => v ? v.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }) : 'R$ 0,00';
    
    let listHtml = `
      <div style="max-height:400px; overflow-y:auto; margin-top:15px">
        <table class="data-table" style="font-size:0.85rem">
          <thead>
            <tr>
              <th>Status</th>
              <th>A\u00e7\u00f5es</th>
            </tr>
          </thead>
          <tbody>
    `;

    grupo.forEach(c => {
      const st = c.status.toLowerCase();
      let badgeClass = 'badge-pendente';
      let label = 'Pendente';
      if (c.nota_lancada) { badgeClass = 'badge-ok'; label = 'Lan\u00e7ado'; }
      else if (st === 'vencido') { badgeClass = 'badge-vencido'; label = 'Vencido'; }
      else if (st === 'cancelado') { badgeClass = 'badge-cancelado'; label = 'Cancelado'; }
      else if (st === 'nao_se_aplica') { badgeClass = 'badge-nao-se-aplica'; label = 'N/A'; }

      listHtml += `
        <tr>
          <td><span class="badge ${badgeClass}">${label}</span></td>
          <td>
            <button class="btn btn-secondary btn-sm" onclick='Contratos.showDetail(${JSON.stringify(c).replace(/'/g, "&#39;")}, "${fornecedor}", "${mesNome}", ${mes})' title="Gerenciar">
              <i class="fas fa-cog"></i>
            </button>
          </td>
        </tr>
      `;
    });

    listHtml += '</tbody></table></div>';

    App.openModal(`${fornecedor} \u2014 ${mesNome}`, `
      <div style="display:flex; justify-content:space-between; margin-bottom:15px; background:var(--glass); padding:12px; border-radius:8px">
        <div><small>Empresa:</small><br><strong>${cell.empresa}</strong></div>
        <div><small>M\u00eas/Ano:</small><br><strong>${mesNome}/${App.anoSelecionado}</strong></div>
        <div style="text-align:right"><small>Total Contratos:</small><br><strong>${grupo.length}</strong></div>
      </div>
      ${listHtml}
    `, [{ text: 'Fechar', class: 'btn btn-secondary', action: () => App.closeModal() }]);
  },

  showDetail(cell, fornecedor, mesNome, mes) {
    const fmt = v => v ? v.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }) : 'R$ 0,00';
    const fmtDate = d => d ? new Date(d + (d.includes('T') ? '' : 'T12:00:00')).toLocaleDateString('pt-BR') : '-';
    const qtd = cell.quantidade_nf || 0;
    
    let statusHtml = '';
    if (cell.nota_lancada) {
      const qtdLabel = qtd > 1 ? `${qtd} Notas Fiscais Lan\u00e7adas` : 'Nota Lan\u00e7ada';
      statusHtml = `<div class="badge badge-ok" style="font-size:0.85rem;padding:6px 14px">\u2705 ${qtdLabel}</div>`;
    } else if (cell.status === 'VENCIDO') {
      statusHtml = `<div class="badge badge-vencido" style="font-size:0.85rem;padding:6px 14px">\ud83d\udd34 Vencido - Sem NF</div>`;
    } else if (cell.status === 'CANCELADO') {
      statusHtml = `<div class="badge badge-cancelado" style="font-size:0.85rem;padding:6px 14px">\u274c Cancelado</div>`;
    } else if (cell.status === 'NAO_SE_APLICA') {
      statusHtml = `<div class="badge badge-nao-se-aplica" style="font-size:0.85rem;padding:6px 14px">\u2014 N\u00e3o se Aplica</div>`;
    } else {
      statusHtml = `<div class="badge badge-pendente" style="font-size:0.85rem;padding:6px 14px">\u23f3 Aguardando NF</div>`;
    }

    let detalhes = `
      <div style="text-align:center;margin-bottom:20px">${statusHtml}</div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;font-size:0.85rem">
        <div><span style="color:var(--text-muted)">Fornecedor:</span><br><strong>${fornecedor}</strong></div>
        <div><span style="color:var(--text-muted)">Empresa:</span><br><strong>${cell.empresa}</strong></div>
        <div><span style="color:var(--text-muted)">M\u00eas:</span><br><strong>${mesNome} ${App.anoSelecionado}</strong></div>
        <div><span style="color:var(--text-muted)">Vencimento:</span><br><strong>${fmtDate(cell.data_vencimento)}</strong></div>
        <div><span style="color:var(--text-muted)">Valor ${qtd > 1 ? 'Total' : ''}:</span><br><strong>${fmt(cell.valor)}</strong></div>
      </div>
    `;

    if (cell.nota_lancada && cell.notas && cell.notas.length > 0) {
      detalhes += `
        <div style="margin-top:16px;padding:12px;background:var(--success-soft);border-radius:var(--radius-md)">
          <div style="font-size:0.78rem;color:var(--success);font-weight:600;margin-bottom:8px">
            ${cell.notas.length > 1 ? cell.notas.length + ' Notas Fiscais Vinculadas' : 'Nota Fiscal Vinculada'}
          </div>
          ${cell.notas.length > 1 ? `
            <table style="width:100%;font-size:0.82rem;border-collapse:collapse">
              <thead>
                <tr style="border-bottom:1px solid var(--border)">
                  <th style="text-align:left;padding:4px 8px;color:var(--text-muted)">N\u00ba NF</th>
                  <th style="text-align:left;padding:4px 8px;color:var(--text-muted)">Pedido</th>
                  <th style="text-align:right;padding:4px 8px;color:var(--text-muted)">Valor</th>
                  <th style="text-align:center;padding:4px 8px;color:var(--text-muted)">Pr\u00e9-Nota</th>
                </tr>
              </thead>
              <tbody>
                ${cell.notas.map(n => `
                  <tr style="border-bottom:1px solid var(--border)">
                    <td style="padding:4px 8px;font-weight:600">${n.numero_nota || '-'}</td>
                    <td style="padding:4px 8px">${n.numero_pedido || '-'}</td>
                    <td style="padding:4px 8px;text-align:right;font-weight:600">${fmt(n.valor)}</td>
                    <td style="padding:4px 8px;text-align:center">
                      <span class="badge ${n.status_pre_nota === 'OK' ? 'badge-ok' : 'badge-pendente'}" style="font-size:0.7rem">
                        ${n.status_pre_nota === 'OK' ? '\u2705 OK' : '\u23f3 Pend.'}
                      </span>
                    </td>
                  </tr>
                `).join('')}
              </tbody>
              <tfoot>
                <tr style="font-weight:700">
                  <td style="padding:6px 8px" colspan="2">Total</td>
                  <td style="padding:6px 8px;text-align:right">${fmt(cell.valor)}</td>
                  <td></td>
                </tr>
              </tfoot>
            </table>
          ` : `
            <div style="font-size:0.85rem">
              N\u00ba NF: <strong>${cell.notas[0].numero_nota || '-'}</strong>
              ${cell.notas[0].numero_pedido ? ` | Pedido: <strong>${cell.notas[0].numero_pedido}</strong>` : ''}
              | Valor: <strong>${fmt(cell.notas[0].valor)}</strong>
            </div>
          `}
        </div>
      `;
    } else if (!cell.nota_lancada) {
      detalhes += `
        <div style="margin-top:16px;padding:12px;background:var(--accent-soft);border-radius:var(--radius-md)">
          <div style="font-size:0.78rem;color:var(--accent);font-weight:600;margin-bottom:4px">Como vincular?</div>
          <div style="font-size:0.82rem;color:var(--text-secondary)">Lance uma NF em "Notas Fiscais" com o fornecedor <strong>${fornecedor}</strong> e empresa <strong>${cell.empresa}</strong> para o m\u00eas de <strong>${mesNome}</strong>. O sistema vincula automaticamente!</div>
        </div>
      `;
    }

    const statusParaAlterar = ['PENDENTE', 'CANCELADO', 'NAO_SE_APLICA'];
    const labelsStatus = {
      PENDENTE: 'Pendente',
      CANCELADO: 'Cancelado',
      NAO_SE_APLICA: 'N\u00e3o se Aplica'
    };
    const colorsStatus = {
      PENDENTE: 'badge-pendente',
      VENCIDO: 'badge-vencido',
      LANCADO: 'badge-ok',
      CANCELADO: 'badge-cancelado',
      NAO_SE_APLICA: 'badge-nao-se-aplica'
    };
    const labelAtual = cell.status === 'LANCADO' ? 'Lan\u00e7ado' : 
                       cell.status === 'VENCIDO' ? 'Vencido' : 
                       labelsStatus[cell.status] || cell.status;
    const currentStatus = cell.status;
    const podeAlterar = !cell.nota_lancada;

    App.openModal(`${fornecedor} \u2014 ${mesNome}`, detalhes, [
      { text: 'Fechar', class: 'btn btn-secondary', action: () => App.closeModal() },
      ...(podeAlterar ? [{
        text: '\u2699\ufe0f Alterar Status',
        class: 'btn btn-secondary',
        action: () => {
          App.closeModal();
          const opts = statusParaAlterar.map(s => {
            const sel = s === currentStatus ? 'selected' : '';
            return `<option value="${s}" ${sel}>${labelsStatus[s]}</option>`;
          }).join('');
          App.openModal('Alterar Status', `
            <div class="form-group" style="margin-bottom:20px">
              <label class="form-label" style="display:block;margin-bottom:8px">Status atual:</label>
              <div class="badge ${colorsStatus[currentStatus]}" style="font-size:0.9rem;padding:8px 16px;width:100%;justify-content:center">
                ${labelAtual}
              </div>
            </div>
            <div class="form-group">
              <label class="form-label" style="display:block;margin-bottom:8px">Novo status desejado:</label>
              <select class="form-select" id="status-select" style="font-size:0.95rem;padding:12px;width:100%">
                ${opts}
              </select>
              <p style="font-size:0.75rem;color:var(--text-muted);margin-top:8px">
                Nota: Se voc\u00ea lan\u00e7ar uma NF para este m\u00eas, o status mudar\u00e1 para "Lan\u00e7ado" automaticamente.
              </p>
            </div>
          ` , [
            { text: 'Cancelar', class: 'btn btn-secondary', action: () => Contratos.showDetail(cell, fornecedor, mesNome, mes) },
            {
              text: 'Confirmar Altera\u00e7\u00e3o',
              class: 'btn btn-primary',
              action: () => {
                const novo = document.getElementById('status-select').value;
                if (!cell.lancamento_id) {
                  App.toast('Erro: ID do lan\u00e7amento n\u00e3o encontrado.', 'error');
                  return;
                }
                API.atualizarStatusLancamento(cell.lancamento_id, novo).then(() => {
                  App.toast(`Status alterado para ${labelsStatus[novo]}`, 'success');
                  App.closeModal();
                  Contratos.loadData();
                }).catch(e => App.toast('Erro ao atualizar: ' + e.message, 'error'));
              }
            }
          ]);
        }
      }] : []),
      {
        text: '\ud83d\udcc5 Alterar Vencimento',
        class: 'btn btn-secondary',
        action: () => {
          App.closeModal();
          // Converter data ISO para input date (YYYY-MM-DD)
          const dataAtual = cell.data_vencimento || '';
          App.openModal('Alterar Data de Vencimento', `
            <div class="form-group" style="margin-bottom:20px">
              <label class="form-label" style="display:block;margin-bottom:8px">Vencimento atual:</label>
              <div class="badge badge-pendente" style="font-size:0.9rem;padding:8px 16px;width:100%;justify-content:center">
                ${fmtDate(cell.data_vencimento)}
              </div>
            </div>
            <div class="form-group">
              <label class="form-label" style="display:block;margin-bottom:8px">Nova data de vencimento:</label>
              <input class="form-input" type="date" id="vencimento-input" value="${dataAtual}" style="font-size:0.95rem;padding:12px;width:100%">
            </div>
            <div class="form-group" style="margin-top:15px;padding:12px;background:var(--glass);border-radius:var(--radius-md)">
              <div style="font-size:0.75rem;color:var(--text-muted);margin-bottom:10px;font-weight:600">📋 Opções de replicação</div>
              <label style="display:flex;align-items:flex-start;gap:8px;cursor:pointer;font-size:0.84rem;color:var(--text-primary);margin-bottom:8px">
                <input type="checkbox" id="chk-replicar-meses" checked style="width:16px;height:16px;margin-top:2px;flex-shrink:0">
                <span>Replicar para os outros meses mantendo o mesmo padrão<br>
                <small style="color:var(--text-muted)">Ex: ABR→20/MAI, MAI→20/JUN, JUN→20/JUL...</small></span>
              </label>
              <label style="display:flex;align-items:flex-start;gap:8px;cursor:pointer;font-size:0.84rem;color:var(--text-primary)">
                <input type="checkbox" id="chk-replicar-empresas" style="width:16px;height:16px;margin-top:2px;flex-shrink:0">
                <span>Replicar para outras empresas deste mesmo fornecedor</span>
              </label>
            </div>
          `, [
            { text: 'Cancelar', class: 'btn btn-secondary', action: () => Contratos.showDetail(cell, fornecedor, mesNome, mes) },
            {
              text: 'Confirmar',
              class: 'btn btn-primary',
              action: () => {
                const novaData = document.getElementById('vencimento-input').value;
                const repMeses = document.getElementById('chk-replicar-meses').checked;
                const repEmpresas = document.getElementById('chk-replicar-empresas').checked;
                if (!novaData) {
                  App.toast('Selecione uma data v\u00e1lida.', 'error');
                  return;
                }
                if (!cell.lancamento_id) {
                  App.toast('Erro: ID do lan\u00e7amento n\u00e3o encontrado.', 'error');
                  return;
                }
                API.atualizarVencimentoLancamento(cell.lancamento_id, novaData, repMeses, repEmpresas).then(() => {
                  App.toast('Data de vencimento atualizada!', 'success');
                  App.closeModal();
                  Contratos.loadData();
                }).catch(e => App.toast('Erro ao atualizar: ' + e.message, 'error'));
              }
            }
          ]);
        }
      },
      ...(!cell.nota_lancada ? [
        { text: '\ud83d\udd17 Vincular Nota', class: 'btn btn-secondary', action: () => { App.closeModal(); Contratos.vincularNotaModal(cell, fornecedor, mesNome, mes); }},
        { text: 'Lan\u00e7ar NF Agora', class: 'btn btn-primary', action: () => { App.closeModal(); App.navigateTo('notas'); setTimeout(() => Notas.openModalPreFill(fornecedor, cell.empresa, mes), 300); }}
      ] : []),
    ]);
  },

  async gerarLancamentos() {
    if (!confirm(`Gerar lan\u00e7amentos mensais para ${App.anoSelecionado}?`)) return;
    try {
      const r = await API.gerarLancamentos(App.anoSelecionado);
      App.toast(`${r.lancamentos_criados} lan\u00e7amentos criados!`, 'success');
      this.loadData();
    } catch (e) { App.toast(`Erro: ${e.message}`, 'error'); }
  },

  async openContratoModal() {
    const [empresas, fornecedores] = await Promise.all([API.getEmpresas(), API.getFornecedores()]);
    const empOpts = empresas.map(e => `<option value="${e.id}">${e.sigla}</option>`).join('');
    const fornOpts = fornecedores.map(f => `<option value="${f.id}">${f.nome}</option>`).join('');
    App.openModal('Novo Contrato', `
      <div class="form-row">
        <div class="form-group"><label class="form-label">Fornecedor *</label><select class="form-select" id="ct-forn"><option value="">Selecione...</option>${fornOpts}</select></div>
        <div class="form-group"><label class="form-label">Empresa *</label><select class="form-select" id="ct-emp"><option value="">Selecione...</option>${empOpts}</select></div>
      </div>
      <div class="form-row">
        <div class="form-group" style="width:100%"><label class="form-label">Dia Vencimento</label><input class="form-input" type="number" id="ct-dia" value="15" min="1" max="31"></div>
      </div>
      <div class="form-row">
        <div class="form-group"><label class="form-label">Valor Mensal (R$)</label><input class="form-input" type="number" step="0.01" id="ct-valor" value="0"></div>
        <div class="form-group"><label class="form-label">Condi\u00e7\u00e3o</label><select class="form-select" id="ct-cond"><option value="MENSAL">Mensal</option><option value="A_VISTA">\u00c0 Vista</option><option value="1/30/60/90">1/30/60/90</option></select></div>
      </div>
      <div class="form-row">
        <div class="form-group"><label class="form-label">Vig\u00eancia In\u00edcio (Opcional)</label><input class="form-input" type="date" id="ct-inicio"></div>
        <div class="form-group"><label class="form-label">Vig\u00eancia Fim (Opcional)</label><input class="form-input" type="date" id="ct-fim"></div>
      </div>
      <div class="form-group"><label class="form-label">Descri\u00e7\u00e3o do Contrato</label><input class="form-input" id="ct-desc" placeholder="Ex: Licen\u00e7a ERP, Suporte, etc."></div>
    `, [
      { text: 'Cancelar', class: 'btn btn-secondary', action: () => App.closeModal() },
      { text: 'Criar', class: 'btn btn-primary', action: () => this.salvarContrato() },
    ]);
  },

  async salvarContrato() {
    const data = {
      fornecedor_id: parseInt(document.getElementById('ct-forn').value),
      empresa_grupo_id: parseInt(document.getElementById('ct-emp').value),
      dia_vencimento: parseInt(document.getElementById('ct-dia').value) || 15,
      valor_mensal: parseFloat(document.getElementById('ct-valor').value) || 0,
      condicao_pagamento: document.getElementById('ct-cond').value,
      data_inicio: document.getElementById('ct-inicio').value || null,
      data_fim: document.getElementById('ct-fim').value || null,
      descricao: document.getElementById('ct-desc').value || null,
    };
    if (!data.fornecedor_id || !data.empresa_grupo_id) { App.toast('Selecione fornecedor e empresa', 'error'); return; }
    try {
      await API.criarContrato(data);
      App.closeModal();
      App.toast('Contrato criado!', 'success');
      this.loadData();
    } catch (e) { App.toast(`Erro: ${e.message}`, 'error'); }
  },

  async vincularNotaModal(cell, fornecedor, mesNome, mes) {
    const fmt = v => v ? v.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }) : 'R$ 0,00';
    const fmtDate = d => d ? new Date(d + (d.includes('T') ? '' : 'T12:00:00')).toLocaleDateString('pt-BR') : '-';

    if (!cell.lancamento_id) {
      App.toast('Erro: ID do lan\u00e7amento n\u00e3o encontrado.', 'error');
      return;
    }

    App.openModal('Vincular Nota Fiscal', `
      <div style="text-align:center;padding:30px">
        <div class="spinner" style="margin:0 auto 12px"></div>
        <p style="color:var(--text-muted);font-size:0.85rem">Buscando notas n\u00e3o vinculadas...</p>
      </div>
    `, [
      { text: 'Voltar', class: 'btn btn-secondary', action: () => { App.closeModal(); Contratos.showDetail(cell, fornecedor, mesNome, mes); }}
    ]);

    try {
      const notas = await API.getNotasCandidatas(cell.lancamento_id);

      if (!notas || notas.length === 0) {
        App.openModal('Vincular Nota Fiscal', `
          <div style="text-align:center;padding:20px">
            <div style="font-size:2.5rem;margin-bottom:12px">\ud83d\udcad</div>
            <h4 style="margin-bottom:8px;color:var(--text-primary)">Nenhuma nota encontrada</h4>
            <p style="font-size:0.85rem;color:var(--text-muted);max-width:360px;margin:0 auto">
              N\u00e3o h\u00e1 notas fiscais n\u00e3o vinculadas para <strong>${fornecedor}</strong> / <strong>${cell.empresa}</strong> em <strong>${mesNome} ${App.anoSelecionado}</strong>.
            </p>
            <div style="margin-top:16px;padding:12px;background:var(--accent-soft);border-radius:var(--radius-md);text-align:left">
              <div style="font-size:0.78rem;color:var(--accent);font-weight:600;margin-bottom:4px">\ud83d\udca1 Dica</div>
              <div style="font-size:0.82rem;color:var(--text-secondary)">
                Verifique se a nota j\u00e1 foi lan\u00e7ada em "Notas Fiscais" com o fornecedor <strong>${fornecedor}</strong>,
                empresa <strong>${cell.empresa}</strong> e m\u00eas <strong>${mesNome}</strong>.
                Caso n\u00e3o tenha sido lan\u00e7ada ainda, use o bot\u00e3o "Lan\u00e7ar NF Agora".
              </div>
            </div>
          </div>
        `, [
          { text: 'Voltar', class: 'btn btn-secondary', action: () => { App.closeModal(); Contratos.showDetail(cell, fornecedor, mesNome, mes); }},
          { text: 'Lan\u00e7ar NF Agora', class: 'btn btn-primary', action: () => { App.closeModal(); App.navigateTo('notas'); setTimeout(() => Notas.openModalPreFill(fornecedor, cell.empresa, mes), 300); }}
        ]);
        return;
      }

      let notasLivres = notas.filter(n => n.origem === 'livre');
      let notasMoviveis = notas.filter(n => n.origem === 'outro_lancamento');

      let tableHtml = `
        <div style="margin-bottom:16px">
          <p style="font-size:0.85rem;color:var(--text-muted);margin-bottom:4px">
            Encontramos <strong>${notas.length}</strong> nota(s) dispon\u00edvel(is) para <strong>${fornecedor}</strong> / <strong>${cell.empresa}</strong> em <strong>${mesNome} ${App.anoSelecionado}</strong>.
          </p>
        </div>
      `;

      if (notasLivres.length > 0) {
        tableHtml += `
          <div style="font-size:0.78rem;color:var(--success);font-weight:600;margin-bottom:8px">\u2705 Notas n\u00e3o vinculadas (livres)</div>
          <div style="max-height:200px;overflow-y:auto;margin-bottom:16px">
            <table class="data-table" style="font-size:0.82rem">
              <thead>
                <tr>
                  <th>N\u00ba NF</th>
                  <th>Pedido</th>
                  <th>Valor</th>
                  <th>Vencimento</th>
                  <th>A\u00e7\u00e3o</th>
                </tr>
              </thead>
              <tbody>
        `;
        notasLivres.forEach(n => {
          tableHtml += `
            <tr>
              <td style="font-weight:600">${n.numero_nota || '-'}</td>
              <td>${n.numero_pedido || '-'}</td>
              <td style="font-weight:600">${fmt(n.valor)}</td>
              <td>${n.data_vencimento ? fmtDate(n.data_vencimento) : '-'}</td>
              <td>
                <button class="btn btn-primary btn-sm" onclick="Contratos.executarVinculacao(${cell.lancamento_id}, ${n.id})" title="Vincular esta nota">
                  \ud83d\udd17 Vincular
                </button>
              </td>
            </tr>
          `;
        });
        tableHtml += '</tbody></table></div>';
      }

      if (notasMoviveis.length > 0) {
        tableHtml += `
          <div style="font-size:0.78rem;color:var(--accent);font-weight:600;margin-bottom:4px">\ud83d\udd04 Notas em outro contrato (mover para c\u00e1)</div>
          <p style="font-size:0.75rem;color:var(--text-muted);margin-bottom:8px">
            Essas notas est\u00e3o vinculadas a outro lan\u00e7amento do mesmo fornecedor/empresa/m\u00eas. 
            Ao mover, ela ser\u00e1 desvinculada do contrato atual e vinculada a este.
          </p>
          <div style="max-height:250px;overflow-y:auto">
            <table class="data-table" style="font-size:0.82rem">
              <thead>
                <tr>
                  <th>N\u00ba NF</th>
                  <th>Pedido</th>
                  <th>Valor</th>
                  <th>Vencimento</th>
                  <th>A\u00e7\u00e3o</th>
                </tr>
              </thead>
              <tbody>
        `;
        notasMoviveis.forEach(n => {
          tableHtml += `
            <tr style="background:rgba(245,158,11,0.05)">
              <td style="font-weight:600">${n.numero_nota || '-'}</td>
              <td>${n.numero_pedido || '-'}</td>
              <td style="font-weight:600">${fmt(n.valor)}</td>
              <td>${n.data_vencimento ? fmtDate(n.data_vencimento) : '-'}</td>
              <td>
                <button class="btn btn-secondary btn-sm" style="border-color:var(--accent);color:var(--accent)" onclick="Contratos.executarVinculacao(${cell.lancamento_id}, ${n.id})" title="Mover esta nota para este contrato">
                  \ud83d\udd04 Mover
                </button>
              </td>
            </tr>
          `;
        });
        tableHtml += '</tbody></table></div>';
      }

      App.openModal(`\ud83d\udd17 Vincular Nota \u2014 ${fornecedor}`, tableHtml, [
        { text: 'Voltar', class: 'btn btn-secondary', action: () => { App.closeModal(); Contratos.showDetail(cell, fornecedor, mesNome, mes); }}
      ]);

    } catch (e) {
      App.toast('Erro ao buscar notas: ' + e.message, 'error');
      App.closeModal();
      Contratos.showDetail(cell, fornecedor, mesNome, mes);
    }
  },

  async executarVinculacao(lancamentoId, notaId) {
    try {
      const result = await API.vincularNotaManual(lancamentoId, notaId);
      App.toast(`\u2705 ${result.detail || 'Nota vinculada com sucesso!'}`, 'success');
      App.closeModal();
      await Contratos.loadData();
    } catch (e) {
      App.toast('Erro ao vincular: ' + e.message, 'error');
    }
  },
};
