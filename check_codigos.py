import sqlite3

for db_path in [r'\\EmaltoNT29\work\USER\PEDRO\ControleNF\backend\data\notas_fiscais_2025.db',
               r'\\EmaltoNT29\work\USER\PEDRO\ControleNF\backend\data\notas_fiscais_2026.db']:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Listar NFs com codigo_fornecedor
    c.execute("""
        SELECT nf.empresa_grupo_id, eg.sigla, nf.empresa_fornecedor, nf.codigo_fornecedor, nf.numero_nota, nf.mes_referencia, nf.ano_referencia
        FROM notas_fiscais nf
        JOIN empresas_grupo eg ON eg.id = nf.empresa_grupo_id
        WHERE nf.codigo_fornecedor IS NOT NULL AND nf.codigo_fornecedor != ''
        ORDER BY nf.ano_referencia, nf.mes_referencia
    """)
    nfs = c.fetchall()
    print(f"\n=== {db_path.split('\\\\')[-1]} ===")
    print(f"NFs com codigo_fornecedor: {len(nfs)}")
    for nf in nfs[:20]:
        print(f"  EmpID={nf[0]} ({nf[1]}) | {nf[2]} | cod={nf[3]} | NF={nf[4]} | {nf[5]}/{nf[6]}")

    # Listar contratos com codigo_fornecedor
    c.execute("SELECT id, empresa_grupo_id, codigo_contrato, codigo_fornecedor FROM contratos_software WHERE codigo_fornecedor IS NOT NULL AND codigo_fornecedor != ''")
    contratos = c.fetchall()
    print(f"Contratos com codigo_fornecedor: {len(contratos)}")
    for c_row in contratos[:20]:
        print(f"  ID={c_row[0]} | EmpID={c_row[1]} | contrato={c_row[2]} | fornecedor={c_row[3]}")

    conn.close()