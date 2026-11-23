"""
Servico de vinculacao automatica NF <-> Contrato Mensal.
Ao lancar uma NF, detecta o contrato correspondente e atualiza o lancamento.
Suporta multiplas NFs vinculadas ao mesmo lancamento mensal.
"""
from datetime import datetime
from sqlalchemy.orm import Session
from models import NotaFiscal, LancamentoMensal, ContratoSoftware, Fornecedor


def vincular_nf_ao_contrato(db: Session, nota: NotaFiscal) -> bool:
    """
    Tenta vincular uma NF a um lancamento mensal existente.
    Match: fornecedor (por nome) + empresa_grupo_id + mes/ano.
    Quando ha multiplos contratos para o mesmo fornecedor+empresa,
    distribui as NFs nos lancamentos ainda vazios (PENDENTE/VENCIDO)
    antes de empilhar no mesmo lancamento.
    Retorna True se vinculou, False se nao encontrou contrato.
    """
    if not nota.empresa_grupo_id or not nota.mes_referencia or not nota.ano_referencia:
        return False

    lancamento = None

    if nota.contrato_id:
        # Contrato explicitamente selecionado pelo usuario
        lancamento = db.query(LancamentoMensal).filter(
            LancamentoMensal.contrato_id == nota.contrato_id,
            LancamentoMensal.mes == nota.mes_referencia,
            LancamentoMensal.ano == nota.ano_referencia,
        ).first()
    else:
        # Buscar fornecedor pelo nome
        fornecedor = db.query(Fornecedor).filter(
            Fornecedor.nome == nota.empresa_fornecedor
        ).first()

        if not fornecedor:
            fornecedor = db.query(Fornecedor).filter(
                Fornecedor.nome.ilike(f"%{nota.empresa_fornecedor}%")
            ).first()

        if not fornecedor:
            return False

        # Buscar TODOS os contratos ativos para este fornecedor+empresa
        contratos = db.query(ContratoSoftware).filter(
            ContratoSoftware.fornecedor_id == fornecedor.id,
            ContratoSoftware.empresa_grupo_id == nota.empresa_grupo_id,
            ContratoSoftware.ativo == True,
        ).all()

        if not contratos:
            return False

        # Buscar todos os lancamentos do mes para esses contratos
        contrato_ids = [c.id for c in contratos]
        lancamentos = db.query(LancamentoMensal).filter(
            LancamentoMensal.contrato_id.in_(contrato_ids),
            LancamentoMensal.mes == nota.mes_referencia,
            LancamentoMensal.ano == nota.ano_referencia,
        ).all()

        if not lancamentos:
            return False

        # Priorizar lancamentos vazios (PENDENTE ou VENCIDO) sobre os ja preenchidos
        lancamentos_vazios = [l for l in lancamentos if l.status in ("PENDENTE", "VENCIDO")]
        lancamentos_disponiveis = [l for l in lancamentos if l.status not in ("CANCELADO", "NAO_SE_APLICA")]

        if lancamentos_vazios:
            lancamento = lancamentos_vazios[0]
        elif lancamentos_disponiveis:
            lancamento = lancamentos_disponiveis[0]

        # Guardar o contrato_id na nota para referencia futura
        if lancamento:
            nota.contrato_id = lancamento.contrato_id

    if not lancamento:
        return False

    if lancamento.status in ("CANCELADO", "NAO_SE_APLICA"):
        return False

    nota.lancamento_mensal_id = lancamento.id
    nota.tipo = "MENSAL"
    lancamento.status = "LANCADO"

    qtd_nfs = len(lancamento.notas_fiscais) if lancamento.notas_fiscais else 0
    if nota not in (lancamento.notas_fiscais or []):
        qtd_nfs += 1

    if qtd_nfs <= 1:
        lancamento.numero_nota = nota.numero_nota
        lancamento.numero_pedido = nota.numero_pedido
        lancamento.valor = nota.valor or lancamento.valor
    else:
        notas_do_lancamento = [n for n in (lancamento.notas_fiscais or []) if n.id != nota.id]
        notas_do_lancamento.append(nota)
        lancamento.numero_nota = ", ".join(filter(None, [n.numero_nota for n in notas_do_lancamento]))
        lancamento.numero_pedido = ", ".join(filter(None, [n.numero_pedido for n in notas_do_lancamento]))
        lancamento.valor = sum(n.valor or 0 for n in notas_do_lancamento)

    lancamento.updated_at = datetime.now()

    db.flush()
    return True


def desvincular_nf_do_contrato(db: Session, nota: NotaFiscal):
    """
    Remove vinculacao de uma NF com o lancamento mensal.
    Se existem outras NFs vinculadas, mantem status LANCADO e recalcula.
    Se nenhuma NF restante, reverte para PENDENTE.
    """
    if not nota.lancamento_mensal_id:
        return

    lancamento = db.query(LancamentoMensal).filter(
        LancamentoMensal.id == nota.lancamento_mensal_id
    ).first()

    if lancamento:
        notas_restantes = [n for n in (lancamento.notas_fiscais or []) if n.id != nota.id]

        if notas_restantes:
            lancamento.status = "LANCADO"
            if len(notas_restantes) == 1:
                n = notas_restantes[0]
                lancamento.numero_nota = n.numero_nota
                lancamento.numero_pedido = n.numero_pedido
                lancamento.valor = n.valor or lancamento.valor
            else:
                lancamento.numero_nota = ", ".join(filter(None, [n.numero_nota for n in notas_restantes]))
                lancamento.numero_pedido = ", ".join(filter(None, [n.numero_pedido for n in notas_restantes]))
                lancamento.valor = sum(n.valor or 0 for n in notas_restantes)
        else:
            lancamento.status = "PENDENTE"
            lancamento.numero_nota = None
            lancamento.numero_pedido = None

        lancamento.updated_at = datetime.now()

    nota.lancamento_mensal_id = None
