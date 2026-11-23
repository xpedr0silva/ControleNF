import sqlite3
import os

db_path = r"f:\USER\PEDRO\ControleNF\backend\data\notas_fiscais_2026.db"

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("--- NOTAS FISCAIS TOTVS ---")
cursor.execute("SELECT id, empresa_fornecedor, numero_nota, empresa_grupo_id, lancamento_mensal_id, contrato_id, tipo FROM notas_fiscais WHERE empresa_fornecedor LIKE '%TOTVS%'")
for row in cursor.fetchall():
    print(dict(row))

print("\n--- CONTRATOS TOTVS ---")
cursor.execute("SELECT c.id, c.fornecedor_id, f.nome as fornecedor_nome, c.empresa_grupo_id, c.codigo_contrato, c.ativo FROM contratos_software c JOIN fornecedores f ON c.fornecedor_id = f.id WHERE f.nome LIKE '%TOTVS%'")
for row in cursor.fetchall():
    print(dict(row))

print("\n--- LANCAMENTOS MENSAIS TOTVS ---")
cursor.execute("SELECT l.id, l.contrato_id, l.mes, l.ano, l.status, l.numero_nota FROM lancamentos_mensais l JOIN contratos_software c ON l.contrato_id = c.id JOIN fornecedores f ON c.fornecedor_id = f.id WHERE f.nome LIKE '%TOTVS%'")
for row in cursor.fetchall():
    print(dict(row))

conn.close()
