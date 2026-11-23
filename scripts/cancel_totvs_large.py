import sqlite3
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
from database import SessionLocal
from models import ContratoSoftware, LancamentoMensal, Fornecedor
import datetime

db = SessionLocal()
ano = 2026

# Encontrar contratos da TOTVS - LARGE ENTERPRISE
contratos = db.query(ContratoSoftware).join(Fornecedor).filter(
    Fornecedor.nome.ilike("%TOTVS - LARGE ENTERPRISE%")
).all()

print(f"Encontrados {len(contratos)} contratos para TOTVS - LARGE ENTERPRISE")

for c in contratos:
    print(f"Atualizando contrato {c.id} ({c.codigo_contrato}) - Encerramento em Junho/2026")
    c.mes_encerramento = 6
    c.ano_encerramento = 2026
    
    # Atualizar lançamentos de Junho (6) até Dezembro (12)
    lancamentos = db.query(LancamentoMensal).filter(
        LancamentoMensal.contrato_id == c.id,
        LancamentoMensal.ano == ano,
        LancamentoMensal.mes >= 6
    ).all()
    
    for l in lancamentos:
        print(f"  -> Lançamento Mes {l.mes} alterado para CANCELADO")
        l.status = "CANCELADO"
        l.updated_at = datetime.datetime.now()

db.commit()
print("Sucesso!")
