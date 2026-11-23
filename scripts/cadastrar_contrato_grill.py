import sqlite3
import datetime
import os

year = datetime.datetime.now().year
db_path = f'backend/data/notas_fiscais_{year}.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get IDs
cursor.execute("SELECT id FROM empresas_grupo WHERE sigla = 'Torque Grill'")
emp_id = cursor.fetchone()[0]

cursor.execute("SELECT id FROM fornecedores WHERE nome = 'TOTVS - LARGE ENTERPRISE'")
forn_id = cursor.fetchone()[0]

codigo = "AAMW42/02"
fim = "2026-05-31"
desc = "TOTVS MENSALIDADE"

print(f"Cadastrando contrato {codigo} para Torque Grill (ID {emp_id})...")

# Check if exists
cursor.execute("SELECT id FROM contratos_software WHERE codigo_contrato = ? AND empresa_grupo_id = ?", (codigo, emp_id))
if cursor.fetchone():
    cursor.execute("UPDATE contratos_software SET data_fim = ?, descricao = ? WHERE codigo_contrato = ? AND empresa_grupo_id = ?", 
                   (fim, desc, codigo, emp_id))
    print(f"  [OK] Atualizado: {codigo}")
else:
    cursor.execute("""
        INSERT INTO contratos_software (fornecedor_id, empresa_grupo_id, codigo_contrato, descricao, data_fim, valor_mensal, dia_vencimento, condicao_pagamento, ativo)
        VALUES (?, ?, ?, ?, ?, 0.0, 15, 'MENSAL', 1)
    """, (forn_id, emp_id, codigo, desc, fim))
    print(f"  [OK] Criado: {codigo}")

conn.commit()
conn.close()
