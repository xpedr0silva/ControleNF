import os
import re
import sqlite3
from pypdf import PdfReader

DB_PATH = r"f:\USER\PEDRO\ControleNF\backend\data\notas_fiscais_2026.db"

def extract_proposal(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for i in range(min(len(reader.pages), 2)):
            text += reader.pages[i].extract_text()
        
        match = re.search(r":\s*Proposta\s*:\s*([\w\d\/\-]+)", text, re.IGNORECASE)
        if match: return match.group(1)
        match = re.search(r"Proposta\s*:\s*([\w\d\/\-]+)", text, re.IGNORECASE)
        if match: return match.group(1)
        return None
    except Exception:
        return None

def sync_path(path, empresa_id, fornecedor_id, conn):
    if not path or not os.path.exists(path):
        return

    print(f"\nSincronizando: {path}")
    cursor = conn.cursor()
    files = [f for f in os.listdir(path) if f.lower().endswith(".pdf")]
    
    for filename in files:
        full_path = os.path.join(path, filename)
        proposal = extract_proposal(full_path)
        
        if proposal:
            cursor.execute("SELECT id FROM contratos_software WHERE empresa_grupo_id = ? AND codigo_contrato = ?", (empresa_id, proposal))
            exists = cursor.fetchone()
            
            if not exists:
                print(f"  [NOVO] {proposal} (ref: {filename})")
                cursor.execute("""
                    INSERT INTO contratos_software (fornecedor_id, empresa_grupo_id, codigo_contrato, descricao, valor_mensal, dia_vencimento, ativo)
                    VALUES (?, ?, ?, ?, 0.0, 15, 1)
                """, (fornecedor_id, empresa_id, proposal, f"Extraído de: {filename}"))
                contrato_id = cursor.lastrowid
                
                # Gerar matriz de lancamentos
                import datetime
                ano = 2026
                for mes in range(1, 13):
                    try:
                        data_vencimento = datetime.date(ano, mes, 15)
                    except ValueError:
                        data_vencimento = datetime.date(ano, mes, 1)
                        
                    cursor.execute("""
                        INSERT INTO lancamentos_mensais (contrato_id, mes, ano, status, data_vencimento)
                        VALUES (?, ?, ?, ?, ?)
                    """, (contrato_id, mes, ano, 'PENDENTE', data_vencimento.isoformat()))

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # IDs TOTVS
    cursor.execute("SELECT id, nome FROM fornecedores WHERE nome LIKE '%TOTVS%'")
    f_list = cursor.fetchall()
    totvs_large_id = next((f[0] for f in f_list if "LARGE" in f[1].upper()), f_list[0][0])
    totvs_msiga_id = next((f[0] for f in f_list if "MICROSIGA" in f[1].upper()), f_list[0][0])

    base_totvs = r"F:\Emalto\Informatica\Conhecimentos\TOTVS"
    if not os.path.exists(base_totvs):
        print("Caminho base TOTVS nao encontrado.")
        return

    # Localizar pastas dinamicamente para evitar erro de encoding
    subfolders = os.listdir(base_totvs)
    
    diesel_path = next((os.path.join(base_totvs, d) for d in subfolders if "DIESEL" in d.upper()), None)
    grill_path = next((os.path.join(base_totvs, d) for d in subfolders if "GRILL" in d.upper()), None)
    eim_path = next((os.path.join(base_totvs, d) for d in subfolders if "EMALTO IND" in d.upper()), None)

    targets = [
        (diesel_path, 5, totvs_large_id),
        (grill_path, 7, totvs_msiga_id),
        (eim_path, 1, totvs_msiga_id)
    ]

    for p, emp_id, forn_id in targets:
        if p:
            sync_path(p, emp_id, forn_id, conn)
            for sub in ["2026", "2025", "Tickets Contratos"]:
                sync_path(os.path.join(p, sub), emp_id, forn_id, conn)

    conn.commit()
    conn.close()
    print("\nSincronizacao finalizada.")

if __name__ == "__main__":
    main()
