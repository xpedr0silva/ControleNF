import sqlite3
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
from database import SessionLocal
from models import ContratoSoftware, LancamentoMensal, NotaFiscal
from services.vinculacao import vincular_nf_ao_contrato
import datetime

db = SessionLocal()
ano = 2026

# 1. Gerar LancamentoMensal para contratos que não têm
contratos = db.query(ContratoSoftware).all()
for c in contratos:
    for mes in range(1, 13):
        lancamento = db.query(LancamentoMensal).filter(
            LancamentoMensal.contrato_id == c.id,
            LancamentoMensal.mes == mes,
            LancamentoMensal.ano == ano
        ).first()
        
        if not lancamento:
            print(f"Criando LancamentoMensal para contrato {c.id}, mes {mes}, ano {ano}")
            dia = c.dia_vencimento or 15
            
            # Lidar com dias que não existem em alguns meses (ex: 31 de abril)
            try:
                data_vencimento = datetime.date(ano, mes, dia)
            except ValueError:
                # Dia muito grande para o mes, vai para o ultimo dia do mes
                if mes == 12:
                    data_vencimento = datetime.date(ano + 1, 1, 1) - datetime.timedelta(days=1)
                else:
                    data_vencimento = datetime.date(ano, mes + 1, 1) - datetime.timedelta(days=1)

            l = LancamentoMensal(
                contrato_id=c.id,
                mes=mes,
                ano=ano,
                status="PENDENTE",
                data_vencimento=data_vencimento
            )
            db.add(l)

db.commit()

# 2. Refazer os vínculos das notas que estão sem lancamento
notas = db.query(NotaFiscal).filter(NotaFiscal.lancamento_mensal_id == None, NotaFiscal.contrato_id != None).all()
count = 0
for nota in notas:
    if vincular_nf_ao_contrato(db, nota):
        count += 1
        print(f"Vinculada NF {nota.id} ao lancamento {nota.lancamento_mensal_id}")
    else:
        print(f"Ainda falhou para NF {nota.id}")

db.commit()

# 3. Processar automação de encerramento se houver contratos com mes_encerramento
for c in contratos:
    if c.mes_encerramento and c.ano_encerramento == ano:
        # Pega lancamentos do mes_encerramento em diante no ano_encerramento
        lancamentos = db.query(LancamentoMensal).filter(
            LancamentoMensal.contrato_id == c.id,
            LancamentoMensal.ano == ano,
            LancamentoMensal.mes >= c.mes_encerramento,
            LancamentoMensal.status.in_(("PENDENTE", "VENCIDO"))
        ).all()
        for l in lancamentos:
            l.status = "CANCELADO"
            l.updated_at = datetime.datetime.now()
db.commit()

print(f"Matriz reconstruída e {count} NFs vinculadas.")
