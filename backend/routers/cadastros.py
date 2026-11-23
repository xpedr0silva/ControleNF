from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from database import get_db
from models import FornecedorEmpresaIdentificador, Fornecedor, EmpresaGrupo, ContratoSoftware, LancamentoMensal
from schemas import (
    FornecedorEmpresaIdentificadorCreate,
    FornecedorEmpresaIdentificadorUpdate,
    FornecedorEmpresaIdentificadorResponse,
)

router = APIRouter(prefix="/api/cadastros", tags=["Cadastros Base"])

@router.get("/identificadores", response_model=list[FornecedorEmpresaIdentificadorResponse])
def listar_identificadores(fornecedor_id: int = None, empresa_grupo_id: int = None, db: Session = Depends(get_db)):
    """Lista todos os identificadores, com filtros opcionais."""
    query = db.query(FornecedorEmpresaIdentificador).options(
        joinedload(FornecedorEmpresaIdentificador.fornecedor),
        joinedload(FornecedorEmpresaIdentificador.empresa_grupo)
    )
    if fornecedor_id:
        query = query.filter(FornecedorEmpresaIdentificador.fornecedor_id == fornecedor_id)
    if empresa_grupo_id:
        query = query.filter(FornecedorEmpresaIdentificador.empresa_grupo_id == empresa_grupo_id)
    return query.all()

@router.post("/identificadores", response_model=FornecedorEmpresaIdentificadorResponse, status_code=201)
def criar_identificador(data: FornecedorEmpresaIdentificadorCreate, db: Session = Depends(get_db)):
    """Cria ou atualiza um identificador para a combinacao fornecedor/empresa."""
    existente = db.query(FornecedorEmpresaIdentificador).filter(
        FornecedorEmpresaIdentificador.fornecedor_id == data.fornecedor_id,
        FornecedorEmpresaIdentificador.empresa_grupo_id == data.empresa_grupo_id
    ).first()

    if existente:
        existente.codigo_identificador = data.codigo_identificador
        db.commit()
        db.refresh(existente)
        return existente

    novo_id = FornecedorEmpresaIdentificador(**data.model_dump())
    db.add(novo_id)
    db.commit()
    db.refresh(novo_id)
    return novo_id

@router.get("/identificadores/busca")
def buscar_identificador(fornecedor_id: int, empresa_grupo_id: int, db: Session = Depends(get_db)):
    """Busca o codigo de identificador de uma empresa especifica."""
    ident = db.query(FornecedorEmpresaIdentificador).filter(
        FornecedorEmpresaIdentificador.fornecedor_id == fornecedor_id,
        FornecedorEmpresaIdentificador.empresa_grupo_id == empresa_grupo_id
    ).first()
    if not ident:
        return {"codigo_identificador": None}
    return {"codigo_identificador": ident.codigo_identificador}


@router.get("/diretorio")
def listar_diretorio(db: Session = Depends(get_db)):
    """Retorna lista unificada de todos os codigos (identificadores comuns + contratos TOTVS)
    para exibicao na aba Diretorio de Codigos."""
    resultado = []

    # 1. Identificadores comuns (fornecedores nao-TOTVS)
    identificadores = db.query(FornecedorEmpresaIdentificador).options(
        joinedload(FornecedorEmpresaIdentificador.fornecedor),
        joinedload(FornecedorEmpresaIdentificador.empresa_grupo)
    ).all()

    for ident in identificadores:
        if not ident.fornecedor or not ident.empresa_grupo:
            continue
        resultado.append({
            "tipo": "COMUM",
            "fornecedor": ident.fornecedor.nome,
            "fornecedor_id": ident.fornecedor_id,
            "empresa": ident.empresa_grupo.sigla,
            "empresa_id": ident.empresa_grupo_id,
            "codigo_fornecedor": ident.codigo_identificador or None,
            "codigo_contrato": None,
            "descricao": None,
            "ativo": True,
            "mes_encerramento": None,
            "ano_encerramento": None,
        })

    # 2. Contratos TOTVS (fornecedores cujo nome contem TOTVS)
    contratos = db.query(ContratoSoftware).options(
        joinedload(ContratoSoftware.fornecedor),
        joinedload(ContratoSoftware.empresa_grupo)
    ).filter(
        ContratoSoftware.fornecedor.has(Fornecedor.nome.ilike("%TOTVS%"))
    ).all()

    for c in contratos:
        if not c.fornecedor or not c.empresa_grupo:
            continue
        resultado.append({
            "tipo": "TOTVS",
            "fornecedor": c.fornecedor.nome,
            "fornecedor_id": c.fornecedor_id,
            "empresa": c.empresa_grupo.sigla,
            "empresa_id": c.empresa_grupo_id,
            "codigo_fornecedor": c.codigo_fornecedor or None,
            "codigo_contrato": c.codigo_contrato or None,
            "descricao": c.descricao or None,
            "ativo": c.ativo,
            "mes_encerramento": c.mes_encerramento,
            "ano_encerramento": c.ano_encerramento,
        })

    # Ordenar: ativos primeiro, depois por fornecedor, empresa
    resultado.sort(key=lambda x: (not x["ativo"], x["fornecedor"], x["empresa"]))
    return resultado


@router.patch("/contratos/{contrato_id}/encerramento")
def definir_encerramento(contrato_id: int, mes: int = None, ano: int = None, db: Session = Depends(get_db)):
    """Define o mes/ano de encerramento de um contrato e propaga CANCELADO para lancamentos mensais."""
    contrato = db.query(ContratoSoftware).filter(ContratoSoftware.id == contrato_id).first()
    if not contrato:
        raise HTTPException(status_code=404, detail="Contrato nao encontrado")

    contrato.mes_encerramento = mes
    contrato.ano_encerramento = ano
    contrato.updated_at = datetime.now()

    # Propagar cancelamento nos lancamentos mensais
    if mes and ano:
        lancamentos = db.query(LancamentoMensal).filter(
            LancamentoMensal.contrato_id == contrato_id,
            LancamentoMensal.ano == ano,
        ).all()

        for lanc in lancamentos:
            if lanc.mes >= mes:
                # So cancela se nao houver NF ja vinculada (LANCADO)
                if lanc.status not in ("LANCADO",):
                    lanc.status = "CANCELADO"
                    lanc.updated_at = datetime.now()
            else:
                # Se antes do encerramento e estava cancelado por engano, reverter para PENDENTE
                if lanc.status == "CANCELADO":
                    lanc.status = "PENDENTE"
                    lanc.updated_at = datetime.now()

    db.commit()
    return {"detail": f"Encerramento definido: {mes}/{ano}" if mes else "Encerramento removido"}
