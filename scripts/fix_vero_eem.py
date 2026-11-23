import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
from database import SessionLocal
from models import NotaFiscal, LancamentoMensal
from services.vinculacao import desvincular_nf_do_contrato, vincular_nf_ao_contrato
import datetime

db = SessionLocal()

# NF 289 (012.308.995, R$480) está no lancamento 721 (contrato 61)
# Deveria estar no lancamento 733 (contrato 62)
nota_289 = db.query(NotaFiscal).filter(NotaFiscal.id == 289).first()
print(f"NF 289 antes: lancamento_mensal_id={nota_289.lancamento_mensal_id}, contrato_id={nota_289.contrato_id}")

# Desvincular do contrato errado
desvincular_nf_do_contrato(db, nota_289)
nota_289.contrato_id = None  # Limpar para forcar redistribuicao
db.flush()

print(f"NF 289 depois de desvincular: lancamento_mensal_id={nota_289.lancamento_mensal_id}, contrato_id={nota_289.contrato_id}")

# Revincular - agora vai pegar o lancamento vazio (733)
result = vincular_nf_ao_contrato(db, nota_289)
print(f"NF 289 depois de revincular: lancamento_mensal_id={nota_289.lancamento_mensal_id}, contrato_id={nota_289.contrato_id}, sucesso={result}")

db.commit()
print("Correcao aplicada!")
