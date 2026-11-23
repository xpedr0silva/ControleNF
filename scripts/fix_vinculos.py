import sqlite3
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
from database import SessionLocal
from models import NotaFiscal
from services.vinculacao import vincular_nf_ao_contrato

db = SessionLocal()
notas = db.query(NotaFiscal).filter(NotaFiscal.lancamento_mensal_id == None, NotaFiscal.contrato_id != None).all()
print(f"Encontradas {len(notas)} NFs com contrato mas sem lancamento.")

count = 0
for nota in notas:
    if vincular_nf_ao_contrato(db, nota):
        count += 1
        print(f"Vinculada NF {nota.id} (Numero: {nota.numero_nota}) ao lancamento {nota.lancamento_mensal_id}")

db.commit()
print(f"Total vinculadas com sucesso: {count}")
