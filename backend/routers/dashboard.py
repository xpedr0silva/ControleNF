"""
Router para Dashboard - KPIs e dados agregados.
"""
from datetime import date, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from database import get_db
from models import NotaFiscal, LancamentoMensal, ContratoSoftware, Fornecedor, EmpresaGrupo
from services.notificacao import obter_notificacoes
from services.vencimento import NOMES_MESES
from config import ANO_CORRENTE

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/kpis")
def obter_kpis(mes: int = None, ano: int = None, db: Session = Depends(get_db)):
    """KPIs principais do dashboard."""
    if not ano:
        ano = ANO_CORRENTE
    if not mes:
        mes = date.today().month

    # NFs do mês
    nfs_query = db.query(NotaFiscal).filter(
        NotaFiscal.ano_referencia == ano,
        NotaFiscal.mes_referencia == mes,
    )
    total_nfs = nfs_query.count()
    nfs_ok = nfs_query.filter(NotaFiscal.status_pre_nota == "OK").count()
    nfs_pendentes = nfs_query.filter(NotaFiscal.status_pre_nota == "PENDENTE").count()
    valor_total = db.query(func.coalesce(func.sum(NotaFiscal.valor), 0)).filter(
        NotaFiscal.ano_referencia == ano, NotaFiscal.mes_referencia == mes
    ).scalar()

    # NFs vencidas (qualquer mês)
    hoje = date.today()
    nfs_vencidas = db.query(NotaFiscal).filter(
        NotaFiscal.status_pre_nota == "PENDENTE",
        NotaFiscal.data_vencimento < hoje,
        NotaFiscal.ano_referencia == ano,
    ).count()

    # Lançamentos do mês
    lanc_total = db.query(LancamentoMensal).filter(
        LancamentoMensal.ano == ano, LancamentoMensal.mes == mes
    ).count()
    lanc_faturados = db.query(LancamentoMensal).filter(
        LancamentoMensal.ano == ano, LancamentoMensal.mes == mes,
        LancamentoMensal.status.in_(["FATURADO", "PAGO"])
    ).count()

    return {
        "total_nfs": total_nfs,
        "nfs_ok": nfs_ok,
        "nfs_pendentes": nfs_pendentes,
        "nfs_vencidas": nfs_vencidas,
        "valor_total": round(valor_total, 2),
        "contratos_faturados": lanc_faturados,
        "contratos_total": lanc_total,
        "percentual_faturado": round((lanc_faturados / lanc_total * 100) if lanc_total else 0, 1),
        "mes": mes,
        "ano": ano,
        "nome_mes": NOMES_MESES.get(mes, ""),
    }


@router.get("/gastos-por-fornecedor")
def gastos_por_fornecedor(ano: int = None, mes: int = None, db: Session = Depends(get_db)):
    if not ano:
        ano = ANO_CORRENTE
    query = db.query(
        NotaFiscal.empresa_fornecedor,
        func.sum(NotaFiscal.valor).label("valor_total"),
        func.count(NotaFiscal.id).label("quantidade"),
    ).filter(NotaFiscal.ano_referencia == ano)
    if mes:
        query = query.filter(NotaFiscal.mes_referencia == mes)
    results = query.group_by(NotaFiscal.empresa_fornecedor).order_by(func.sum(NotaFiscal.valor).desc()).all()
    return [{"fornecedor": r[0], "valor_total": round(r[1], 2), "quantidade": r[2]} for r in results]


@router.get("/gastos-por-empresa")
def gastos_por_empresa(ano: int = None, mes: int = None, db: Session = Depends(get_db)):
    if not ano:
        ano = ANO_CORRENTE
    query = db.query(
        EmpresaGrupo.sigla,
        func.sum(NotaFiscal.valor).label("valor_total"),
        func.count(NotaFiscal.id).label("quantidade"),
    ).join(EmpresaGrupo, NotaFiscal.empresa_grupo_id == EmpresaGrupo.id).filter(
        NotaFiscal.ano_referencia == ano
    )
    if mes:
        query = query.filter(NotaFiscal.mes_referencia == mes)
    results = query.group_by(EmpresaGrupo.sigla).order_by(func.sum(NotaFiscal.valor).desc()).all()
    return [{"empresa": r[0], "valor_total": round(r[1], 2), "quantidade": r[2]} for r in results]


@router.get("/gastos-mensais")
def gastos_mensais(ano: int = None, db: Session = Depends(get_db)):
    if not ano:
        ano = ANO_CORRENTE
    results = db.query(
        NotaFiscal.mes_referencia,
        func.sum(NotaFiscal.valor).label("valor_total"),
        func.count(NotaFiscal.id).label("quantidade"),
    ).filter(NotaFiscal.ano_referencia == ano).group_by(
        NotaFiscal.mes_referencia
    ).order_by(NotaFiscal.mes_referencia).all()
    return [{
        "mes": r[0], "nome_mes": NOMES_MESES.get(r[0], ""),
        "valor_total": round(r[1], 2), "quantidade": r[2]
    } for r in results]


@router.get("/proximos-vencimentos")
def proximos_vencimentos(limit: int = 10, db: Session = Depends(get_db)):
    hoje = date.today()
    lancamentos = db.query(LancamentoMensal).join(ContratoSoftware).join(
        Fornecedor, ContratoSoftware.fornecedor_id == Fornecedor.id
    ).join(
        EmpresaGrupo, ContratoSoftware.empresa_grupo_id == EmpresaGrupo.id
    ).filter(
        LancamentoMensal.status == "PENDENTE",
        LancamentoMensal.data_vencimento >= hoje - timedelta(days=30),
        ContratoSoftware.ativo == True,
    ).options(
        joinedload(LancamentoMensal.contrato).joinedload(ContratoSoftware.fornecedor),
        joinedload(LancamentoMensal.contrato).joinedload(ContratoSoftware.empresa_grupo),
    ).order_by(LancamentoMensal.data_vencimento).limit(limit).all()

    return [{
        "fornecedor": l.contrato.fornecedor.nome,
        "empresa": l.contrato.empresa_grupo.sigla,
        "data_vencimento": l.data_vencimento.isoformat(),
        "valor": l.valor,
        "status": l.status,
        "dias_restantes": (l.data_vencimento - hoje).days,
        "lancamento_id": l.id,
    } for l in lancamentos]


@router.get("/notificacoes")
def notificacoes(db: Session = Depends(get_db)):
    """Retorna resumo de notificações (vencidas, hoje, semana)."""
    return obter_notificacoes(db)
