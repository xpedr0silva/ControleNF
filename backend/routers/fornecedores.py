"""
Router para CRUD de Fornecedores.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Fornecedor
from schemas import FornecedorCreate, FornecedorUpdate, FornecedorResponse

router = APIRouter(prefix="/api/fornecedores", tags=["Fornecedores"])


@router.get("/", response_model=list[FornecedorResponse])
def listar_fornecedores(
    categoria: str = None,
    ativo: bool = None,
    db: Session = Depends(get_db)
):
    query = db.query(Fornecedor)
    if categoria:
        query = query.filter(Fornecedor.categoria == categoria)
    if ativo is not None:
        query = query.filter(Fornecedor.ativo == ativo)
    return query.order_by(Fornecedor.nome).all()


@router.get("/{fornecedor_id}", response_model=FornecedorResponse)
def obter_fornecedor(fornecedor_id: int, db: Session = Depends(get_db)):
    fornecedor = db.query(Fornecedor).filter(Fornecedor.id == fornecedor_id).first()
    if not fornecedor:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado")
    return fornecedor


@router.post("/", response_model=FornecedorResponse, status_code=201)
def criar_fornecedor(data: FornecedorCreate, db: Session = Depends(get_db)):
    existente = db.query(Fornecedor).filter(Fornecedor.nome == data.nome).first()
    if existente:
        raise HTTPException(status_code=400, detail=f"Fornecedor '{data.nome}' já existe")
    fornecedor = Fornecedor(**data.model_dump())
    db.add(fornecedor)
    db.commit()
    db.refresh(fornecedor)
    return fornecedor


@router.put("/{fornecedor_id}", response_model=FornecedorResponse)
def atualizar_fornecedor(fornecedor_id: int, data: FornecedorUpdate, db: Session = Depends(get_db)):
    fornecedor = db.query(Fornecedor).filter(Fornecedor.id == fornecedor_id).first()
    if not fornecedor:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(fornecedor, field, value)
    db.commit()
    db.refresh(fornecedor)
    return fornecedor


@router.delete("/{fornecedor_id}")
def deletar_fornecedor(fornecedor_id: int, db: Session = Depends(get_db)):
    fornecedor = db.query(Fornecedor).filter(Fornecedor.id == fornecedor_id).first()
    if not fornecedor:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado")
    db.delete(fornecedor)
    db.commit()
    return {"detail": "Fornecedor removido com sucesso"}
