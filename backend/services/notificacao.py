"""
Serviço de notificações de NFs pendentes e vencidas.
"""
from datetime import date, timedelta
from sqlalchemy.orm import Session, joinedload
from models import LancamentoMensal, NotaFiscal, ContratoSoftware, Fornecedor, EmpresaGrupo


def obter_notificacoes(db: Session) -> dict:
    """
    Retorna resumo de notificações sobre NFs e lançamentos.
    
    Categories:
    - vencidas: já venceram e não foram faturadas
    - vencendo_hoje: vencem hoje
    - vencendo_semana: vencem nos próximos 7 dias
    """
    hoje = date.today()
    semana = hoje + timedelta(days=7)
    
    # Buscar lançamentos pendentes (apenas de contratos ativos)
    lancamentos = db.query(LancamentoMensal).join(
        ContratoSoftware
    ).join(
        Fornecedor, ContratoSoftware.fornecedor_id == Fornecedor.id
    ).join(
        EmpresaGrupo, ContratoSoftware.empresa_grupo_id == EmpresaGrupo.id
    ).filter(
        LancamentoMensal.status.in_(["PENDENTE"]),
        LancamentoMensal.data_vencimento <= semana,
        ContratoSoftware.ativo == True,
    ).options(
        joinedload(LancamentoMensal.contrato).joinedload(ContratoSoftware.fornecedor),
        joinedload(LancamentoMensal.contrato).joinedload(ContratoSoftware.empresa_grupo),
    ).all()
    
    items = []
    vencidas = 0
    vencendo_hoje = 0
    vencendo_semana = 0
    
    for lanc in lancamentos:
        delta = (lanc.data_vencimento - hoje).days
        
        if delta < 0:
            tipo = "vencida"
            vencidas += 1
        elif delta == 0:
            tipo = "vencendo_hoje"
            vencendo_hoje += 1
        else:
            tipo = "vencendo_semana"
            vencendo_semana += 1
        
        items.append({
            "tipo": tipo,
            "lancamento_id": lanc.id,
            "fornecedor": lanc.contrato.fornecedor.nome,
            "empresa": lanc.contrato.empresa_grupo.sigla,
            "codigo_contrato": lanc.contrato.codigo_contrato,
            "valor": lanc.valor,
            "data_vencimento": lanc.data_vencimento.isoformat(),
            "dias_restantes": delta,
            "mes": lanc.mes,
            "ano": lanc.ano,
        })
    
    # Ordenar: vencidas primeiro, depois por data
    items.sort(key=lambda x: (
        {"vencida": 0, "vencendo_hoje": 1, "vencendo_semana": 2}[x["tipo"]],
        x["data_vencimento"]
    ))
    
    # Buscar NFs avulsas / pre-notas pendentes (ignorando as vinculadas a contratos inativos)
    nfs_pendentes = db.query(NotaFiscal).outerjoin(
        ContratoSoftware, NotaFiscal.contrato_id == ContratoSoftware.id
    ).filter(
        NotaFiscal.status_pre_nota == "PENDENTE",
        NotaFiscal.data_vencimento != None,
        NotaFiscal.data_vencimento <= semana,
        (NotaFiscal.contrato_id == None) | (ContratoSoftware.ativo == True)
    ).all()
    
    for nf in nfs_pendentes:
        delta = (nf.data_vencimento - hoje).days
        if delta < 0:
            tipo = "vencida"
            vencidas += 1
        elif delta == 0:
            tipo = "vencendo_hoje"
            vencendo_hoje += 1
        else:
            tipo = "vencendo_semana"
            vencendo_semana += 1
        
        items.append({
            "tipo": tipo,
            "fornecedor": nf.empresa_fornecedor,
            "empresa": nf.empresa_grupo.sigla if nf.empresa_grupo else "N/A",
            "valor": nf.valor,
            "data_vencimento": nf.data_vencimento.isoformat(),
            "dias_restantes": delta,
            "numero_nota": nf.numero_nota,
        })
    
    return {
        "vencidas": vencidas,
        "vencendo_hoje": vencendo_hoje,
        "vencendo_semana": vencendo_semana,
        "total_alertas": vencidas + vencendo_hoje + vencendo_semana,
        "items": items,
    }


def formatar_notificacao_texto(resumo: dict) -> str:
    """Formata o resumo de notificações para exibição em toast/popup."""
    linhas = []
    
    if resumo["vencidas"] > 0:
        linhas.append(f"🔴 {resumo['vencidas']} NF(s) VENCIDA(S)")
    if resumo["vencendo_hoje"] > 0:
        linhas.append(f"⚠️ {resumo['vencendo_hoje']} NF(s) vencem HOJE")
    if resumo["vencendo_semana"] > 0:
        linhas.append(f"⏳ {resumo['vencendo_semana']} NF(s) vencem esta semana")
    
    if not linhas:
        return "✅ Nenhuma NF pendente ou vencida!"
    
    return "\n".join(linhas)
