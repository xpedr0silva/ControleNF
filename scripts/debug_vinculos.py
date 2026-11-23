import sqlite3
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
from database import SessionLocal
from models import NotaFiscal, LancamentoMensal, ContratoSoftware

db = SessionLocal()
notas = db.query(NotaFiscal).filter(NotaFiscal.lancamento_mensal_id == None, NotaFiscal.contrato_id != None).all()

for nota in notas:
    print(f"NF {nota.id} (Numero: {nota.numero_nota}): mes={nota.mes_referencia}, ano={nota.ano_referencia}, contrato={nota.contrato_id}")
    contrato = db.query(ContratoSoftware).filter(ContratoSoftware.id == nota.contrato_id).first()
    if not contrato:
        print("  -> Contrato nao encontrado!")
        continue
    
    lancamento = db.query(LancamentoMensal).filter(
        LancamentoMensal.contrato_id == contrato.id,
        LancamentoMensal.mes == nota.mes_referencia,
        LancamentoMensal.ano == nota.ano_referencia,
    ).first()

    if not lancamento:
        print(f"  -> LancamentoMensal nao encontrado para contrato={contrato.id}, mes={nota.mes_referencia}, ano={nota.ano_referencia}!")
        continue

    print(f"  -> LancamentoMensal {lancamento.id} encontrado! Status={lancamento.status}")
    if lancamento.status in ("CANCELADO", "NAO_SE_APLICA"):
        print("  -> LancamentoMensal cancelado ou nao se aplica!")
        continue

    print("  -> TUDO OK, DEVERIA TER SIDO VINCULADO!")

