import sqlite3
import os

db_path = r"f:\USER\PEDRO\ControleNF\backend\data\notas_fiscais_2026.db"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
c = conn.cursor()

c.execute("""
SELECT ativo, count(*) as count 
FROM contratos_software 
WHERE fornecedor_id IN (SELECT id FROM fornecedores WHERE nome LIKE '%TOTVS%') 
GROUP BY ativo
""")

for r in c.fetchall():
    print(dict(r))

conn.close()
