import sqlite3
import datetime
import os

year = datetime.datetime.now().year
db_path = f'backend/data/notas_fiscais_{year}.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get Torque Diesel ID
cursor.execute("SELECT id FROM empresas_grupo WHERE sigla = 'Torque Diesel'")
row = cursor.fetchone()
if not row:
    print("Torque Diesel not found")
    exit()
emp_id = row[0]

# Get all TOTVS suppliers
cursor.execute("SELECT id, nome FROM fornecedores WHERE nome LIKE 'TOTVS%' ")
forns = cursor.fetchall()
forn_ids = [f[0] for f in forns]

# Get current contracts for Torque Diesel and TOTVS
cursor.execute(f"SELECT id, fornecedor_id, codigo_contrato, descricao FROM contratos_software WHERE empresa_grupo_id = {emp_id} AND fornecedor_id IN ({','.join(map(str, forn_ids))})")
contratos = cursor.fetchall()

print('Empresa ID:', emp_id)
print('Fornecedores TOTVS:', forns)
print('Contratos Atuais (ID, FornID, Codigo, Desc):', contratos)

conn.close()
