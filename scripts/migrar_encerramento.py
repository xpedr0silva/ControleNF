"""
Migra o banco de dados para adicionar colunas mes_encerramento e ano_encerramento
na tabela contratos_software.
"""
import sqlite3
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
from config import DATA_DIR

databases = [
    os.path.join(DATA_DIR, "notas_fiscais_2025.db"),
    os.path.join(DATA_DIR, "notas_fiscais_2026.db"),
]

for db_path in databases:
    if not os.path.exists(db_path):
        print(f"[SKIP] {db_path} nao existe")
        continue

    print(f"[MIGRANDO] {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Verificar se as colunas ja existem
    cursor.execute("PRAGMA table_info(contratos_software)")
    colunas = [col[1] for col in cursor.fetchall()]

    if "mes_encerramento" not in colunas:
        cursor.execute("ALTER TABLE contratos_software ADD COLUMN mes_encerramento INTEGER")
        print("  + mes_encerramento adicionada")
    else:
        print("  = mes_encerramento ja existe")

    if "ano_encerramento" not in colunas:
        cursor.execute("ALTER TABLE contratos_software ADD COLUMN ano_encerramento INTEGER")
        print("  + ano_encerramento adicionada")
    else:
        print("  = ano_encerramento ja existe")

    conn.commit()
    conn.close()
    print(f"[OK] {db_path}")

print("\nMigracao concluida!")
