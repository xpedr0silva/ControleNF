import sqlite3

db_path = r"f:\USER\PEDRO\ControleNF\backend\data\notas_fiscais_2026.db"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
c = conn.cursor()

print("=== CONTRATOS VERO ===")
c.execute("""
SELECT c.id, c.fornecedor_id, f.nome as forn_nome, e.sigla as emp_sigla, 
       c.codigo_contrato, c.descricao, c.empresa_grupo_id
FROM contratos_software c 
JOIN fornecedores f ON c.fornecedor_id = f.id 
JOIN empresas_grupo e ON c.empresa_grupo_id = e.id 
WHERE f.nome LIKE '%VERO%' AND c.ativo = 1
ORDER BY emp_sigla
""")
for r in c.fetchall():
    print(dict(r))

print("\n=== NOTAS FISCAIS VERO EEM JAN/2026 ===")
c.execute("""
SELECT id, empresa_fornecedor, numero_nota, numero_pedido, valor, 
       empresa_grupo_id, lancamento_mensal_id, contrato_id, tipo,
       mes_referencia, ano_referencia
FROM notas_fiscais 
WHERE empresa_fornecedor LIKE '%VERO%' AND mes_referencia = 1 AND ano_referencia = 2026
""")
for r in c.fetchall():
    print(dict(r))

print("\n=== LANCAMENTOS MENSAIS VERO EEM JAN/2026 ===")
c.execute("""
SELECT l.id, l.contrato_id, l.mes, l.ano, l.status, l.numero_nota, l.valor,
       c.codigo_contrato, c.descricao, e.sigla
FROM lancamentos_mensais l
JOIN contratos_software c ON l.contrato_id = c.id
JOIN fornecedores f ON c.fornecedor_id = f.id
JOIN empresas_grupo e ON c.empresa_grupo_id = e.id
WHERE f.nome LIKE '%VERO%' AND l.mes = 1 AND l.ano = 2026
""")
for r in c.fetchall():
    print(dict(r))

conn.close()
