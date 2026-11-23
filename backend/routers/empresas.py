"""
Router para CRUD de Empresas do Grupo Emalto.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import EmpresaGrupo
from schemas import EmpresaGrupoCreate, EmpresaGrupoUpdate, EmpresaGrupoResponse

router = APIRouter(prefix="/api/empresas", tags=["Empresas do Grupo"])


@router.get("/", response_model=list[EmpresaGrupoResponse])
def listar_empresas(ativo: bool = None, db: Session = Depends(get_db)):
    query = db.query(EmpresaGrupo)
    if ativo is not None:
        query = query.filter(EmpresaGrupo.ativo == ativo)
    return query.order_by(EmpresaGrupo.sigla).all()


@router.get("/{empresa_id}", response_model=EmpresaGrupoResponse)
def obter_empresa(empresa_id: int, db: Session = Depends(get_db)):
    empresa = db.query(EmpresaGrupo).filter(EmpresaGrupo.id == empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    return empresa


@router.post("/", response_model=EmpresaGrupoResponse, status_code=201)
def criar_empresa(data: EmpresaGrupoCreate, db: Session = Depends(get_db)):
    existente = db.query(EmpresaGrupo).filter(EmpresaGrupo.sigla == data.sigla).first()
    if existente:
        raise HTTPException(status_code=400, detail=f"Empresa '{data.sigla}' já existe")
    empresa = EmpresaGrupo(**data.model_dump())
    db.add(empresa)
    db.commit()
    db.refresh(empresa)
    return empresa


@router.put("/{empresa_id}", response_model=EmpresaGrupoResponse)
def atualizar_empresa(empresa_id: int, data: EmpresaGrupoUpdate, db: Session = Depends(get_db)):
    empresa = db.query(EmpresaGrupo).filter(EmpresaGrupo.id == empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(empresa, field, value)
    db.commit()
    db.refresh(empresa)
    return empresa


@router.delete("/{empresa_id}")
def deletar_empresa(empresa_id: int, db: Session = Depends(get_db)):
    empresa = db.query(EmpresaGrupo).filter(EmpresaGrupo.id == empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    db.delete(empresa)
    db.commit()
    return {"detail": "Empresa removida com sucesso"}
