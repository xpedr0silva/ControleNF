import sqlite3

for db_path in [
    r'\\EmaltoNT29\work\USER\PEDRO\ControleNF\backend\data\notas_fiscais_2025.db',
    r'\\EmaltoNT29\work\USER\PEDRO\ControleNF\backend\data\notas_fiscais_2026.db'
]:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    print(f"\n===== {db_path.split('\\')[-1]} =====")

    # Todos contratos
    c.execute("""
        SELECT cs.id, eg.sigla, f.nome, cs.codigo_contrato, cs.codigo_fornecedor
        FROM contratos_software cs
        JOIN empresas_grupo eg ON eg.id = cs.empresa_grupo_id
        JOIN fornecedores f ON f.id = cs.fornecedor_id
        ORDER BY eg.sigla, f.nome
    """)
    print("\nCONTRATOS:")
    for r in c.fetchall():
        print(f"  ID={r[0]} | {r[1]} | {r[2]} | contrato={r[3]} | fornecedor={r[4]}")

    # NFs distintas
    c.execute("""
        SELECT DISTINCT nf.empresa_grupo_id, eg.sigla, nf.empresa_fornecedor, nf.codigo_fornecedor
        FROM notas_fiscais nf
        JOIN empresas_grupo eg ON eg.id = nf.empresa_grupo_id
        WHERE nf.codigo_fornecedor IS NOT NULL AND nf.codigo_fornecedor != ''
        ORDER BY eg.sigla, nf.empresa_fornecedor
    """)
    print("\nNFs com codigo_fornecedor:")
    for r in c.fetchall():
        print(f"  EmpID={r[0]} ({r[1]}) | fornecedor={r[2]} | codigo={r[3]}")

    conn.close()