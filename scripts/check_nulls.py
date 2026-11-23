import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
from database import SessionLocal
from models import ContratoSoftware, Fornecedor

db = SessionLocal()
totvs = db.query(Fornecedor).filter(Fornecedor.nome.like('%TOTVS%')).all()
for f in totvs:
    print(f"Fornecedor: {f.nome} (ID: {f.id})")
    contratos = db.query(ContratoSoftware).filter(ContratoSoftware.fornecedor_id == f.id).all()
    for c in contratos:
        print(f"  Contrato ID: {c.id}, valor: {c.valor_mensal}, dia: {c.dia_vencimento}, cond: {c.condicao_pagamento}")
