"""
Router para CRUD de Notas Fiscais.
Ao criar/atualizar/deletar, vincula automaticamente ao contrato mensal.
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from database import get_db
from models import NotaFiscal, EmpresaGrupo, LancamentoMensal
from schemas import NotaFiscalCreate, NotaFiscalUpdate, NotaFiscalResponse
from services.vinculacao import vincular_nf_ao_contrato, desvincular_nf_do_contrato

router = APIRouter(prefix="/api/notas-fiscais", tags=["Notas Fiscais"])


@router.get("/", response_model=list[NotaFiscalResponse])
def listar_notas_fiscais(
    mes: int = None,
    ano: int = None,
    fornecedor: str = None,
    empresa_grupo_id: int = None,
    status: str = None,
    tipo: str = None,
    busca: str = None,
    limit: int = Query(default=100, le=500),
    offset: int = 0,
    db: Session = Depends(get_db),
):
    query = db.query(NotaFiscal).options(
        joinedload(NotaFiscal.empresa_grupo)
    )
    
    if mes:
        query = query.filter(NotaFiscal.mes_referencia == mes)
    if ano:
        query = query.filter(NotaFiscal.ano_referencia == ano)
    if fornecedor:
        query = query.filter(NotaFiscal.empresa_fornecedor.ilike(f"%{fornecedor}%"))
    if empresa_grupo_id:
        query = query.filter(NotaFiscal.empresa_grupo_id == empresa_grupo_id)
    if status:
        query = query.filter(NotaFiscal.status_pre_nota == status)
    if tipo:
        query = query.filter(NotaFiscal.tipo == tipo)
    if busca:
        query = query.filter(
            (NotaFiscal.empresa_fornecedor.ilike(f"%{busca}%")) |
            (NotaFiscal.numero_nota.ilike(f"%{busca}%")) |
            (NotaFiscal.numero_pedido.ilike(f"%{busca}%"))
        )
    
    return query.order_by(
        NotaFiscal.ano_referencia.desc(),
        NotaFiscal.mes_referencia.desc(),
        NotaFiscal.data_vencimento.desc(),
    ).offset(offset).limit(limit).all()


@router.get("/count")
def contar_notas_fiscais(
    mes: int = None,
    ano: int = None,
    status: str = None,
    db: Session = Depends(get_db),
):
    query = db.query(NotaFiscal)
    if mes:
        query = query.filter(NotaFiscal.mes_referencia == mes)
    if ano:
        query = query.filter(NotaFiscal.ano_referencia == ano)
    if status:
        query = query.filter(NotaFiscal.status_pre_nota == status)
    return {"count": query.count()}


@router.get("/{nota_id}", response_model=NotaFiscalResponse)
def obter_nota_fiscal(nota_id: int, db: Session = Depends(get_db)):
    nota = db.query(NotaFiscal).options(
        joinedload(NotaFiscal.empresa_grupo)
    ).filter(NotaFiscal.id == nota_id).first()
    if not nota:
        raise HTTPException(status_code=404, detail="Nota fiscal nao encontrada")
    return nota


@router.post("/", response_model=NotaFiscalResponse, status_code=201)
def criar_nota_fiscal(data: NotaFiscalCreate, db: Session = Depends(get_db)):
    # Validar empresa do grupo se informada
    if data.empresa_grupo_id:
        empresa = db.query(EmpresaGrupo).filter(
            EmpresaGrupo.id == data.empresa_grupo_id
        ).first()
        if not empresa:
            raise HTTPException(status_code=400, detail="Empresa do grupo nao encontrada")
    
    # Auto-preencher mes/ano de referencia se nao informado
    nota_data = data.model_dump()
    if not nota_data.get("mes_referencia") and nota_data.get("data_vencimento"):
        nota_data["mes_referencia"] = nota_data["data_vencimento"].month
    if not nota_data.get("ano_referencia") and nota_data.get("data_vencimento"):
        nota_data["ano_referencia"] = nota_data["data_vencimento"].year
    if not nota_data.get("ano_referencia"):
        nota_data["ano_referencia"] = datetime.now().year
    if not nota_data.get("mes_referencia"):
        nota_data["mes_referencia"] = datetime.now().month

    if nota_data.get("empresa_grupo_id") and nota_data.get("mes_referencia") and nota_data.get("ano_referencia"):
        from models import Fornecedor, ContratoSoftware, FornecedorEmpresaIdentificador
        fornecedor = db.query(Fornecedor).filter(
            Fornecedor.nome.ilike(f"%{data.empresa_fornecedor}%")
        ).first()
        if fornecedor:
            # 1. Snapshot do Identificador (Planilha)
            ident = db.query(FornecedorEmpresaIdentificador).filter(
                FornecedorEmpresaIdentificador.fornecedor_id == fornecedor.id,
                FornecedorEmpresaIdentificador.empresa_grupo_id == nota_data["empresa_grupo_id"]
            ).first()
            if ident and ident.codigo_identificador and not nota_data.get("codigo_fornecedor"):
                nota_data["codigo_fornecedor"] = ident.codigo_identificador
                
            # 2. Vinculo ao Contrato (para a Matriz Mensal)
            contrato = None
            if nota_data.get("contrato_id"):
                contrato = db.query(ContratoSoftware).filter(
                    ContratoSoftware.id == nota_data["contrato_id"]
                ).first()
            else:
                contratos_ativos = db.query(ContratoSoftware).filter(
                    ContratoSoftware.fornecedor_id == fornecedor.id,
                    ContratoSoftware.empresa_grupo_id == nota_data["empresa_grupo_id"],
                    ContratoSoftware.ativo == True,
                ).all()
                if contratos_ativos:
                    if len(contratos_ativos) == 1:
                        contrato = contratos_ativos[0]
                    else:
                        # Multiplos contratos: escolher o que tem lancamento vazio
                        contrato_ids = [c.id for c in contratos_ativos]
                        lancamento_vazio = db.query(LancamentoMensal).filter(
                            LancamentoMensal.contrato_id.in_(contrato_ids),
                            LancamentoMensal.mes == nota_data["mes_referencia"],
                            LancamentoMensal.ano == nota_data["ano_referencia"],
                            LancamentoMensal.status.in_(["PENDENTE", "VENCIDO"]),
                        ).first()
                        if lancamento_vazio:
                            contrato = db.query(ContratoSoftware).filter(ContratoSoftware.id == lancamento_vazio.contrato_id).first()
                        else:
                            contrato = contratos_ativos[0]
                    if contrato:
                        nota_data["contrato_id"] = contrato.id
                    
            if contrato and contrato.codigo_fornecedor and not nota_data.get("codigo_fornecedor"):
                nota_data["codigo_fornecedor"] = contrato.codigo_fornecedor
            
            # 3. Validar se o lancamento da matriz nao esta bloqueado
            if nota_data.get("contrato_id"):
                lancamento = db.query(LancamentoMensal).filter(
                    LancamentoMensal.contrato_id == nota_data["contrato_id"],
                    LancamentoMensal.mes == nota_data["mes_referencia"],
                    LancamentoMensal.ano == nota_data["ano_referencia"],
                ).first()
                if lancamento and lancamento.status in ("CANCELADO", "NAO_SE_APLICA"):
                    raise HTTPException(
                        status_code=400,
                        detail=f"Lan\u00e7amento CANCELADO ou N\u00e3o se Aplica para este fornecedor neste m\u00eas. N\u00e3o \u00e9 poss\u00edvel lan\u00e7ar NF."
                    )
    
    nota = NotaFiscal(**nota_data)
    db.add(nota)
    db.flush()  # Gerar ID antes de vincular
    
    # Auto-vincular ao contrato mensal se existir match
    vincular_nf_ao_contrato(db, nota)
    
    db.commit()
    db.refresh(nota)
    return nota


@router.put("/{nota_id}", response_model=NotaFiscalResponse)
def atualizar_nota_fiscal(nota_id: int, data: NotaFiscalUpdate, db: Session = Depends(get_db)):
    nota = db.query(NotaFiscal).filter(NotaFiscal.id == nota_id).first()
    if not nota:
        raise HTTPException(status_code=404, detail="Nota fiscal nao encontrada")
    
    # Desvincular contrato antigo antes de atualizar
    desvincular_nf_do_contrato(db, nota)
    
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(nota, field, value)
    nota.updated_at = datetime.now()
    
    # Re-vincular ao contrato (pode ter mudado fornecedor/empresa/mes)
    if nota.empresa_grupo_id and nota.mes_referencia and nota.ano_referencia:
        from models import Fornecedor, ContratoSoftware, FornecedorEmpresaIdentificador
        fornecedor = db.query(Fornecedor).filter(
            Fornecedor.nome.ilike(f"%{nota.empresa_fornecedor}%")
        ).first()
        if fornecedor:
            # 1. Snapshot Identificador Planilha (so se nao tiver ainda)
            ident = db.query(FornecedorEmpresaIdentificador).filter(
                FornecedorEmpresaIdentificador.fornecedor_id == fornecedor.id,
                FornecedorEmpresaIdentificador.empresa_grupo_id == nota.empresa_grupo_id
            ).first()
            if ident and ident.codigo_identificador and not nota.codigo_fornecedor:
                nota.codigo_fornecedor = ident.codigo_identificador

            # 2. Vinculo ao Contrato Mensal
            contrato = None
            if nota.contrato_id:
                contrato = db.query(ContratoSoftware).filter(
                    ContratoSoftware.id == nota.contrato_id
                ).first()
            else:
                contratos_ativos = db.query(ContratoSoftware).filter(
                    ContratoSoftware.fornecedor_id == fornecedor.id,
                    ContratoSoftware.empresa_grupo_id == nota.empresa_grupo_id,
                    ContratoSoftware.ativo == True,
                ).all()
                if contratos_ativos:
                    if len(contratos_ativos) == 1:
                        contrato = contratos_ativos[0]
                    else:
                        contrato_ids = [c.id for c in contratos_ativos]
                        lancamento_vazio = db.query(LancamentoMensal).filter(
                            LancamentoMensal.contrato_id.in_(contrato_ids),
                            LancamentoMensal.mes == nota.mes_referencia,
                            LancamentoMensal.ano == nota.ano_referencia,
                            LancamentoMensal.status.in_(["PENDENTE", "VENCIDO"]),
                        ).first()
                        if lancamento_vazio:
                            contrato = db.query(ContratoSoftware).filter(ContratoSoftware.id == lancamento_vazio.contrato_id).first()
                        else:
                            contrato = contratos_ativos[0]
                    if contrato:
                        nota.contrato_id = contrato.id
                    
            if contrato and contrato.codigo_fornecedor and not nota.codigo_fornecedor:
                nota.codigo_fornecedor = contrato.codigo_fornecedor

            if nota.contrato_id:
                lancamento = db.query(LancamentoMensal).filter(
                    LancamentoMensal.contrato_id == nota.contrato_id,
                    LancamentoMensal.mes == nota.mes_referencia,
                    LancamentoMensal.ano == nota.ano_referencia,
                ).first()
                if lancamento and lancamento.status in ("CANCELADO", "NAO_SE_APLICA"):
                    raise HTTPException(
                        status_code=400,
                        detail=f"Lan\u00e7amento CANCELADO ou N\u00e3o se Aplica para este m\u00eas. N\u00e3o \u00e9 poss\u00edvel vincular."
                    )
    vincular_nf_ao_contrato(db, nota)
    
    db.commit()
    db.refresh(nota)
    return nota


@router.patch("/{nota_id}/status")
def atualizar_status_prenota(nota_id: int, status: str, db: Session = Depends(get_db)):
    """Atualizar rapidamente o status da pre-nota (OK/PENDENTE)."""
    nota = db.query(NotaFiscal).filter(NotaFiscal.id == nota_id).first()
    if not nota:
        raise HTTPException(status_code=404, detail="Nota fiscal nao encontrada")
    
    if status not in ("OK", "PENDENTE"):
        raise HTTPException(status_code=400, detail="Status deve ser 'OK' ou 'PENDENTE'")
    
    nota.status_pre_nota = status
    nota.updated_at = datetime.now()
    db.commit()
    return {"detail": f"Status atualizado para '{status}'"}


@router.patch("/{nota_id}/email")
def toggle_enviado_email(nota_id: int, db: Session = Depends(get_db)):
    """Toggle rapido do flag 'enviado por email'."""
    nota = db.query(NotaFiscal).filter(NotaFiscal.id == nota_id).first()
    if not nota:
        raise HTTPException(status_code=404, detail="Nota fiscal nao encontrada")
    
    nota.enviado_email = not nota.enviado_email
    nota.updated_at = datetime.now()
    db.commit()
    return {"detail": f"Email: {'Sim' if nota.enviado_email else 'Nao'}", "enviado_email": nota.enviado_email}


@router.patch("/{nota_id}/protocolo")
def atualizar_protocolo(nota_id: int, protocolo: str, db: Session = Depends(get_db)):
    """Atualizar numero do protocolo da pre-nota."""
    nota = db.query(NotaFiscal).filter(NotaFiscal.id == nota_id).first()
    if not nota:
        raise HTTPException(status_code=404, detail="Nota fiscal nao encontrada")
    
    nota.protocolo_pre_nota = protocolo
    nota.updated_at = datetime.now()
    db.commit()
    return {"detail": f"Protocolo atualizado: {protocolo}"}


@router.delete("/{nota_id}")
def deletar_nota_fiscal(nota_id: int, db: Session = Depends(get_db)):
    nota = db.query(NotaFiscal).filter(NotaFiscal.id == nota_id).first()
    if not nota:
        raise HTTPException(status_code=404, detail="Nota fiscal nao encontrada")
    
    # Desvincular contrato antes de deletar
    desvincular_nf_do_contrato(db, nota)
    
    db.delete(nota)
    db.commit()
    return {"detail": "Nota fiscal removida com sucesso"}
