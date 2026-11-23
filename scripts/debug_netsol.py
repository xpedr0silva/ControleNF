import sqlite3

db_path = r"f:\USER\PEDRO\ControleNF\backend\data\notas_fiscais_2026.db"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
c = conn.cursor()

# Buscar lançamentos NETSOL para verificar datas
c.execute("""
SELECT l.id, l.contrato_id, l.mes, l.ano, l.status, l.data_vencimento,
       f.nome as forn_nome, e.sigla as emp_sigla
FROM lancamentos_mensais l
JOIN contratos_software c2 ON l.contrato_id = c2.id
JOIN fornecedores f ON c2.fornecedor_id = f.id
JOIN empresas_grupo e ON c2.empresa_grupo_id = e.id
WHERE f.nome LIKE '%NETSOL%' AND l.ano = 2026
ORDER BY l.mes
""")
for r in c.fetchall():
    print(dict(r))

# Verificar se calcular_vencimento restringe
print("\n--- Teste de data ---")
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
from services.vencimento import calcular_vencimento
from datetime import date

# Tentar vencimento 01/05 para lancamento de Abril
print(f"calcular_vencimento(2026, 4, 1) = {calcular_vencimento(2026, 4, 1)}")
print(f"calcular_vencimento(2026, 4, 30) = {calcular_vencimento(2026, 4, 30)}")
print(f"date(2026, 5, 1) = {date(2026, 5, 1)}")

conn.close()
