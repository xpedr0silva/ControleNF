import sqlite3
import os

db_path = r"f:\USER\PEDRO\ControleNF\backend\data\notas_fiscais_2026.db"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
c = conn.cursor()

c.execute("""
SELECT c.id, c.fornecedor_id, f.nome as forn_nome, e.sigla as emp_sigla, c.codigo_contrato, c.descricao 
FROM contratos_software c 
JOIN fornecedores f ON c.fornecedor_id = f.id 
JOIN empresas_grupo e ON c.empresa_grupo_id = e.id 
WHERE c.ativo = 1 AND f.nome LIKE '%TOTVS%' 
ORDER BY forn_nome, emp_sigla
""")

for r in c.fetchall():
    print(dict(r))

conn.close()
