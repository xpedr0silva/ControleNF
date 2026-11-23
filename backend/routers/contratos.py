"""
Router para Contratos de Software e Lancamentos Mensais.
A matriz e read-only: o status e atualizado automaticamente via NFs.
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from database import get_db
from models import ContratoSoftware, LancamentoMensal, Fornecedor, EmpresaGrupo, NotaFiscal
from schemas import (
    ContratoSoftwareCreate, ContratoSoftwareUpdate, ContratoSoftwareResponse,
    LancamentoMensalResponse, NotaFiscalResponse,
)
from services.pre_lancamento import gerar_lancamentos_anuais, obter_matriz_contratos
from config import ANO_CORRENTE

router = APIRouter(prefix="/api/contratos", tags=["Contratos"])


@router.get("/", response_model=list[ContratoSoftwareResponse])
def listar_contratos(fornecedor_id: int = None, empresa_grupo_id: int = None, ativo: bool = None, db: Session = Depends(get_db)):
    query = db.query(ContratoSoftware).options(joinedload(ContratoSoftware.fornecedor), joinedload(ContratoSoftware.empresa_grupo))
    if fornecedor_id:
        query = query.filter(ContratoSoftware.fornecedor_id == fornecedor_id)
    if empresa_grupo_id:
        query = query.filter(ContratoSoftware.empresa_grupo_id == empresa_grupo_id)
    if ativo is not None:
        query = query.filter(ContratoSoftware.ativo == ativo)
    return query.all()


@router.get("/{contrato_id}", response_model=ContratoSoftwareResponse)
def obter_contrato(contrato_id: int, db: Session = Depends(get_db)):
    contrato = db.query(ContratoSoftware).options(joinedload(ContratoSoftware.fornecedor), joinedload(ContratoSoftware.empresa_grupo)).filter(ContratoSoftware.id == contrato_id).first()
    if not contrato:
        raise HTTPException(status_code=404, detail="Contrato nao encontrado")
    return contrato


@router.post("/", response_model=ContratoSoftwareResponse, status_code=201)
def criar_contrato(data: ContratoSoftwareCreate, db: Session = Depends(get_db)):
    contrato = ContratoSoftware(**data.model_dump())
    db.add(contrato)
    db.commit()
    db.refresh(contrato)
    return contrato


@router.put("/{contrato_id}", response_model=ContratoSoftwareResponse)
def atualizar_contrato(contrato_id: int, data: ContratoSoftwareUpdate, db: Session = Depends(get_db)):
    contrato = db.query(ContratoSoftware).filter(ContratoSoftware.id == contrato_id).first()
    if not contrato:
        raise HTTPException(status_code=404, detail="Contrato nao encontrado")
    
    valor_antigo = contrato.valor_mensal
    
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(contrato, field, value)
    contrato.updated_at = datetime.now()
    
    # Se o valor mensal foi alterado, atualizar tambem os lancamentos mensais pendentes/vencidos sem NF vinculada
    if data.valor_mensal is not None and data.valor_mensal != valor_antigo:
        lancamentos = db.query(LancamentoMensal).filter(
            LancamentoMensal.contrato_id == contrato_id,
            LancamentoMensal.status.in_(["PENDENTE", "VENCIDO"])
        ).all()
        for lanc in lancamentos:
            if not lanc.numero_nota:
                lanc.valor = data.valor_mensal
                lanc.updated_at = datetime.now()
                
    db.commit()
    db.refresh(contrato)
    return contrato


@router.delete("/{contrato_id}")
def deletar_contrato(contrato_id: int, db: Session = Depends(get_db)):
    contrato = db.query(ContratoSoftware).filter(ContratoSoftware.id == contrato_id).first()
    if not contrato:
        raise HTTPException(status_code=404, detail="Contrato nao encontrado")
        
    # Em vez de excluir do banco (o que quebra o historico de notas passadas),
    # fazemos um Soft Delete (inativamos o contrato).
    contrato.ativo = False
    contrato.updated_at = datetime.now()
    db.commit()
    return {"detail": "Contrato inativado com sucesso"}


@router.post("/gerar-lancamentos/{ano}")
def gerar_lancamentos(ano: int, db: Session = Depends(get_db)):
    """Gera lancamentos mensais (Jan-Dez) para todos os contratos ativos."""
    return gerar_lancamentos_anuais(db, ano)


@router.get("/lancamentos/", response_model=list[LancamentoMensalResponse])
def listar_lancamentos(ano: int = None, mes: int = None, status: str = None, contrato_id: int = None, db: Session = Depends(get_db)):
    if not ano:
        ano = ANO_CORRENTE
    query = db.query(LancamentoMensal).options(
        joinedload(LancamentoMensal.contrato).joinedload(ContratoSoftware.fornecedor),
        joinedload(LancamentoMensal.contrato).joinedload(ContratoSoftware.empresa_grupo),
    ).filter(LancamentoMensal.ano == ano)
    if mes:
        query = query.filter(LancamentoMensal.mes == mes)
    if status:
        query = query.filter(LancamentoMensal.status == status)
    if contrato_id:
        query = query.filter(LancamentoMensal.contrato_id == contrato_id)
    return query.order_by(LancamentoMensal.mes, LancamentoMensal.contrato_id).all()


@router.get("/matriz/{ano}")
def obter_matriz(ano: int, mes: int = None, db: Session = Depends(get_db)):
    """Retorna a matriz de contratos (fornecedor x mes). Status auto-derivado das NFs."""
    return obter_matriz_contratos(db, ano, mes)


@router.get("/lancamentos/{lancamento_id}/notas", response_model=list[NotaFiscalResponse])
def listar_notas_do_lancamento(lancamento_id: int, db: Session = Depends(get_db)):
    """Lista todas as NFs vinculadas a um lancamento mensal."""
    lancamento = db.query(LancamentoMensal).filter(LancamentoMensal.id == lancamento_id).first()
    if not lancamento:
        raise HTTPException(status_code=404, detail="Lancamento nao encontrado")
    notas = db.query(NotaFiscal).filter(NotaFiscal.lancamento_mensal_id == lancamento_id).all()
    return notas


@router.get("/fornecedor/{fornecedor_id}", response_model=list[ContratoSoftwareResponse])
def listar_contratos_por_fornecedor(fornecedor_id: int, db: Session = Depends(get_db)):
    """Lista contratos de um fornecedor especifico (usado para TOTVS)."""
    contratos = db.query(ContratoSoftware).options(
        joinedload(ContratoSoftware.fornecedor),
        joinedload(ContratoSoftware.empresa_grupo),
    ).filter(
        ContratoSoftware.fornecedor_id == fornecedor_id,
        ContratoSoftware.ativo == True,
    ).all()
    return contratos


@router.patch("/lancamentos/{lancamento_id}/status")
def atualizar_status_lancamento(lancamento_id: int, status: str, db: Session = Depends(get_db)):
    """Atualiza o status de um lancamento mensal (ex: CANCELADO, NAO_SE_APLICA, PENDENTE)."""
    lancamento = db.query(LancamentoMensal).filter(LancamentoMensal.id == lancamento_id).first()
    if not lancamento:
        raise HTTPException(status_code=404, detail="Lancamento nao encontrado")

    status_validos = ["PENDENTE", "FATURADO", "PAGO", "VENCIDO", "LANCADO", "CANCELADO", "NAO_SE_APLICA"]
    if status not in status_validos:
        raise HTTPException(status_code=400, detail=f"Status invalido. Use: {', '.join(status_validos)}")

    lancamento.status = status
    lancamento.updated_at = datetime.now()
    db.commit()
    return {"detail": f"Status atualizado para {status}"}


@router.patch("/lancamentos/{lancamento_id}/vencimento")
def atualizar_vencimento_lancamento(
    lancamento_id: int,
    data_vencimento: str,
    replicar_meses: bool = False,
    replicar_empresas: bool = False,
    db: Session = Depends(get_db)
):
    """
    Atualiza a data de vencimento de um lancamento mensal.
    
    Se replicar_meses=True, calcula o offset (diferenca em meses) entre a data
    escolhida e o mes do lancamento, e aplica o mesmo offset nos demais meses.
    Exemplo: ABR com vencimento em 20/MAI (offset +1 mes, dia 20):
      MAI -> 20/JUN, JUN -> 20/JUL, DEZ -> 20/JAN/proximo_ano, etc.
    
    Se replicar_empresas=True, aplica a mesma logica para todos os contratos
    ativos do mesmo fornecedor.
    """
    from datetime import date as date_type
    import calendar

    lancamento = db.query(LancamentoMensal).filter(LancamentoMensal.id == lancamento_id).first()
    if not lancamento:
        raise HTTPException(status_code=404, detail="Lancamento nao encontrado")

    try:
        nova_data = date_type.fromisoformat(data_vencimento)
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Data invalida. Use o formato AAAA-MM-DD.")

    # 1. Salvar a data exata escolhida no lancamento original
    lancamento.data_vencimento = nova_data
    lancamento.updated_at = datetime.now()

    if replicar_meses or replicar_empresas:
        contrato_origem = lancamento.contrato
        ano_ref = lancamento.ano
        mes_ref = lancamento.mes
        novo_dia = nova_data.day

        # Calcular o offset em meses entre a data escolhida e o mes de referencia do lancamento
        # Ex: lancamento.mes=4 (ABR), nova_data.month=5 (MAI), nova_data.year=2026 -> offset_meses = 1
        offset_meses = (nova_data.year * 12 + nova_data.month) - (ano_ref * 12 + mes_ref)

        def aplicar_offset(mes_lancamento: int) -> date_type:
            """Calcula a data de vencimento para um mes dado, aplicando o mesmo offset."""
            # Mes e ano alvo do vencimento
            total_meses = ano_ref * 12 + mes_lancamento + offset_meses
            ano_venc = (total_meses - 1) // 12
            mes_venc = (total_meses - 1) % 12 + 1
            # Ajustar dia para o limite do mes (ex: dia 31 em fevereiro -> dia 28/29)
            ultimo_dia = calendar.monthrange(ano_venc, mes_venc)[1]
            dia_ajustado = min(novo_dia, ultimo_dia)
            return date_type(ano_venc, mes_venc, dia_ajustado)

        # Encontrar quais contratos devem ser atualizados
        contratos_a_atualizar = [contrato_origem]
        if replicar_empresas:
            outros_contratos = db.query(ContratoSoftware).filter(
                ContratoSoftware.fornecedor_id == contrato_origem.fornecedor_id,
                ContratoSoftware.ativo == True,
                ContratoSoftware.id != contrato_origem.id
            ).all()
            contratos_a_atualizar.extend(outros_contratos)

        for contrato in contratos_a_atualizar:
            # Atualizar o dia de vencimento base do contrato
            contrato.dia_vencimento = novo_dia
            contrato.updated_at = datetime.now()

            if replicar_meses:
                # Atualizar todos os meses do ano, preservando o offset
                lancamentos = db.query(LancamentoMensal).filter(
                    LancamentoMensal.contrato_id == contrato.id,
                    LancamentoMensal.ano == ano_ref
                ).all()
                for l in lancamentos:
                    if l.id == lancamento.id:
                        # Ja foi salvo acima com a data exata escolhida pelo usuario
                        continue
                    l.data_vencimento = aplicar_offset(l.mes)
                    l.updated_at = datetime.now()
            else:
                # Replicar apenas o mes correspondente nas outras empresas
                lancamentos = db.query(LancamentoMensal).filter(
                    LancamentoMensal.contrato_id == contrato.id,
                    LancamentoMensal.ano == ano_ref,
                    LancamentoMensal.mes == mes_ref
                ).all()
                for l in lancamentos:
                    if l.id == lancamento.id:
                        continue
                    l.data_vencimento = aplicar_offset(l.mes)
                    l.updated_at = datetime.now()

    db.commit()
    return {"detail": f"Vencimento atualizado para {nova_data.strftime('%d/%m/%Y')}"}


@router.get("/lancamentos/{lancamento_id}/notas-candidatas")
def buscar_notas_candidatas(lancamento_id: int, db: Session = Depends(get_db)):
    """
    Busca NFs que podem ser vinculadas/movidas para este lancamento.
    Retorna:
      1. NFs nao vinculadas (lancamento_mensal_id == None)
      2. NFs vinculadas a OUTROS lancamentos irmaos (mesmo fornecedor+empresa+mes/ano)
         para permitir redistribuicao entre contratos.
    """
    lancamento = db.query(LancamentoMensal).options(
        joinedload(LancamentoMensal.contrato).joinedload(ContratoSoftware.fornecedor),
        joinedload(LancamentoMensal.contrato).joinedload(ContratoSoftware.empresa_grupo),
    ).filter(LancamentoMensal.id == lancamento_id).first()

    if not lancamento:
        raise HTTPException(status_code=404, detail="Lancamento nao encontrado")

    contrato = lancamento.contrato
    fornecedor = contrato.fornecedor
    empresa = contrato.empresa_grupo

    # 1. NFs nao vinculadas que batem com fornecedor + empresa + mes/ano
    notas_livres = db.query(NotaFiscal).options(
        joinedload(NotaFiscal.empresa_grupo)
    ).filter(
        NotaFiscal.empresa_fornecedor.ilike(f"%{fornecedor.nome}%"),
        NotaFiscal.empresa_grupo_id == empresa.id,
        NotaFiscal.mes_referencia == lancamento.mes,
        NotaFiscal.ano_referencia == lancamento.ano,
        NotaFiscal.lancamento_mensal_id == None,
    ).all()

    # 2. NFs vinculadas a OUTROS lancamentos irmaos (mesmo fornecedor+empresa+mes)
    #    para permitir mover/redistribuir
    contratos_mesmo_grupo = db.query(ContratoSoftware).filter(
        ContratoSoftware.fornecedor_id == fornecedor.id,
        ContratoSoftware.empresa_grupo_id == empresa.id,
        ContratoSoftware.ativo == True,
    ).all()
    contrato_ids = [c.id for c in contratos_mesmo_grupo]

    lancamentos_irmaos = db.query(LancamentoMensal).filter(
        LancamentoMensal.contrato_id.in_(contrato_ids),
        LancamentoMensal.mes == lancamento.mes,
        LancamentoMensal.ano == lancamento.ano,
        LancamentoMensal.id != lancamento.id,  # Excluir o proprio
    ).all()
    lancamento_ids_irmaos = [l.id for l in lancamentos_irmaos]

    notas_em_irmaos = []
    if lancamento_ids_irmaos:
        notas_em_irmaos = db.query(NotaFiscal).options(
            joinedload(NotaFiscal.empresa_grupo)
        ).filter(
            NotaFiscal.lancamento_mensal_id.in_(lancamento_ids_irmaos),
        ).all()

    # Converter para dict
    resultado = []

    for n in notas_livres:
        resultado.append({
            "id": n.id,
            "numero_nota": n.numero_nota,
            "numero_pedido": n.numero_pedido,
            "valor": n.valor,
            "empresa_fornecedor": n.empresa_fornecedor,
            "empresa_sigla": empresa.sigla if empresa else None,
            "data_vencimento": str(n.data_vencimento) if n.data_vencimento else None,
            "status_pre_nota": n.status_pre_nota,
            "lancamento_atual_id": None,
            "origem": "livre",
        })

    for n in notas_em_irmaos:
        resultado.append({
            "id": n.id,
            "numero_nota": n.numero_nota,
            "numero_pedido": n.numero_pedido,
            "valor": n.valor,
            "empresa_fornecedor": n.empresa_fornecedor,
            "empresa_sigla": empresa.sigla if empresa else None,
            "data_vencimento": str(n.data_vencimento) if n.data_vencimento else None,
            "status_pre_nota": n.status_pre_nota,
            "lancamento_atual_id": n.lancamento_mensal_id,
            "origem": "outro_lancamento",
        })

    return resultado


def _recalcular_lancamento(db: Session, lancamento: LancamentoMensal):
    """Recalcula numero_nota, numero_pedido, valor e status de um lancamento
    com base nas NFs atualmente vinculadas a ele."""
    notas_restantes = db.query(NotaFiscal).filter(
        NotaFiscal.lancamento_mensal_id == lancamento.id
    ).all()

    if not notas_restantes:
        lancamento.status = "PENDENTE"
        lancamento.numero_nota = None
        lancamento.numero_pedido = None
        # Manter valor original do contrato
    elif len(notas_restantes) == 1:
        n = notas_restantes[0]
        lancamento.status = "LANCADO"
        lancamento.numero_nota = n.numero_nota
        lancamento.numero_pedido = n.numero_pedido
        lancamento.valor = n.valor or lancamento.valor
    else:
        lancamento.status = "LANCADO"
        lancamento.numero_nota = ", ".join(filter(None, [n.numero_nota for n in notas_restantes]))
        lancamento.numero_pedido = ", ".join(filter(None, [n.numero_pedido for n in notas_restantes]))
        lancamento.valor = sum(n.valor or 0 for n in notas_restantes)

    lancamento.updated_at = datetime.now()


@router.post("/lancamentos/{lancamento_id}/vincular-nota")
def vincular_nota_manual(lancamento_id: int, nota_id: int, db: Session = Depends(get_db)):
    """
    Vincula manualmente uma NF a um lancamento mensal.
    Se a NF ja estiver vinculada a outro lancamento, MOVE ela
    (desvincula do antigo e recalcula ambos).
    """
    lancamento_destino = db.query(LancamentoMensal).filter(
        LancamentoMensal.id == lancamento_id
    ).first()
    if not lancamento_destino:
        raise HTTPException(status_code=404, detail="Lancamento nao encontrado")

    if lancamento_destino.status in ("CANCELADO", "NAO_SE_APLICA"):
        raise HTTPException(status_code=400, detail="Lancamento cancelado ou N/A. Nao e possivel vincular.")

    nota = db.query(NotaFiscal).filter(NotaFiscal.id == nota_id).first()
    if not nota:
        raise HTTPException(status_code=404, detail="Nota fiscal nao encontrada")

    # Se ja esta vinculada ao MESMO lancamento, nao faz nada
    if nota.lancamento_mensal_id == lancamento_id:
        raise HTTPException(status_code=400, detail="Esta nota ja esta vinculada a este lancamento.")

    # Se esta vinculada a OUTRO lancamento, desvincular primeiro
    lancamento_origem = None
    if nota.lancamento_mensal_id:
        lancamento_origem = db.query(LancamentoMensal).filter(
            LancamentoMensal.id == nota.lancamento_mensal_id
        ).first()
        # Desvincular da origem
        nota.lancamento_mensal_id = None

    # Vincular ao destino
    nota.lancamento_mensal_id = lancamento_destino.id
    nota.contrato_id = lancamento_destino.contrato_id
    nota.tipo = "MENSAL"
    nota.updated_at = datetime.now()

    # Recalcular lancamento de ORIGEM (se existia)
    if lancamento_origem:
        _recalcular_lancamento(db, lancamento_origem)

    # Recalcular lancamento de DESTINO
    _recalcular_lancamento(db, lancamento_destino)

    db.commit()

    msg = f"Nota {nota.numero_nota or nota.id} vinculada com sucesso."
    if lancamento_origem:
        msg = f"Nota {nota.numero_nota or nota.id} movida com sucesso para este lancamento."
    return {"detail": msg}

