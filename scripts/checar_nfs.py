import sqlite3
import datetime
import os

year = datetime.datetime.now().year
db_path = f'backend/data/notas_fiscais_{year}.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

nfs = ['1023694', '4336012', '4336090', '4352265', '4352283', '4352310']
for nf in nfs:
    cursor.execute("SELECT numero_nota, empresa_fornecedor, valor FROM notas_fiscais WHERE numero_nota LIKE ?", (f'%{nf}%',))
    res = cursor.fetchall()
    print(f'NF {nf}: {res}')

conn.close()
