import sqlite3
import datetime
import os

year = datetime.datetime.now().year
db_path = f'backend/data/notas_fiscais_{year}.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get IDs
cursor.execute("SELECT id FROM empresas_grupo WHERE sigla = 'Torque Diesel'")
emp_id = cursor.fetchone()[0]

cursor.execute("SELECT id FROM fornecedores WHERE nome = 'TOTVS - LARGE ENTERPRISE'")
forn_id = cursor.fetchone()[0]

contratos = [
    {"codigo": "354414/01", "fim": "2026-05-31", "desc": "TOTVS SMS LGT"},
    {"codigo": "AAKUW5/10", "fim": "2026-05-31", "desc": "TOTVS CONCILIADOR"},
    {"codigo": "AAJR37",    "fim": "2026-10-31", "desc": "TOTVS TRANSMITE"},
    {"codigo": "AAMVUZ/02", "fim": "2026-10-31", "desc": "TOTVS APP BACKOFC"},
    {"codigo": "AANRDS/01", "fim": "2026-10-31", "desc": "TOTVS INTELIGENCIA TRIBUTARIA"},
    {"codigo": "AAHHWW/04", "fim": None,         "desc": "TOTVS MENSALIDADE"},
    {"codigo": "354970/01", "fim": None,         "desc": "TOTVS FULL"},
]

print(f"Cadastrando {len(contratos)} contratos para Torque Diesel...")

for c in contratos:
    # Check if exists
    cursor.execute("SELECT id FROM contratos_software WHERE codigo_contrato = ? AND empresa_grupo_id = ?", (c["codigo"], emp_id))
    if cursor.fetchone():
        print(f"  [AVISO] Contrato {c['codigo']} ja existe. Atualizando...")
        cursor.execute("UPDATE contratos_software SET data_fim = ?, descricao = ? WHERE codigo_contrato = ? AND empresa_grupo_id = ?", 
                       (c["fim"], c["desc"], c["codigo"], emp_id))
    else:
        cursor.execute("""
            INSERT INTO contratos_software (fornecedor_id, empresa_grupo_id, codigo_contrato, descricao, data_fim, valor_mensal, dia_vencimento, condicao_pagamento, ativo)
            VALUES (?, ?, ?, ?, ?, 0.0, 15, 'MENSAL', 1)
        """, (forn_id, emp_id, c["codigo"], c["desc"], c["fim"]))
        print(f"  [OK] Criado: {c['codigo']}")

conn.commit()
conn.close()

print("\nProcesso concluido. Nao esqueca de rodar 'Gerar Lancamentos' no sistema para atualizar a matriz.")
