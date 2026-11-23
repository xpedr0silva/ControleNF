import sqlite3

DB_PATH = r"f:\USER\PEDRO\ControleNF\backend\data\notas_fiscais_2026.db"

def update_identificadores():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Mapeamento KTREE (Fornecedor ID pode variar, buscamos pelo nome)
    cursor.execute("SELECT id FROM fornecedores WHERE nome = 'KTREE'")
    ktree_row = cursor.fetchone()
    
    if ktree_row:
        ktree_id = ktree_row[0]
        # EIM (1), EEM (2), EEN (3), Fundacao (4)
        updates = [
            (1, "11366-01"),
            (2, "004092-01"),
            (3, "11366-01"),
            (4, "00460-01")
        ]
        
        for emp_id, code in updates:
            # Verifica se existe contrato para essa combinacao
            cursor.execute("SELECT id FROM contratos_software WHERE fornecedor_id = ? AND empresa_grupo_id = ?", (ktree_id, emp_id))
            exists = cursor.fetchone()
            
            if exists:
                cursor.execute("UPDATE contratos_software SET codigo_contrato = ? WHERE id = ?", (code, exists[0]))
                print(f"KTREE -> Empresa {emp_id}: Atualizado para {code}")
            else:
                # Cria se nao existir (para garantir que apareça na matriz)
                cursor.execute("""
                    INSERT INTO contratos_software (fornecedor_id, empresa_grupo_id, codigo_contrato, descricao, valor_mensal, dia_vencimento, ativo)
                    VALUES (?, ?, ?, ?, 0.0, 15, 1)
                """, (ktree_id, emp_id, code, "Identificador Planilha"))
                print(f"KTREE -> Empresa {emp_id}: Criado com código {code}")

    # Adicionar outros se houver...
    # Exemplo: VERO, VIVO, INTERPONTO se voce tiver os codigos
    
    conn.commit()
    conn.close()
    print("Atualizacao de identificadores concluida.")

if __name__ == "__main__":
    update_identificadores()
