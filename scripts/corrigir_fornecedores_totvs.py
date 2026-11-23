import sqlite3
import datetime
import os
import re
from pypdf import PdfReader

def get_prestador(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        text = reader.pages[0].extract_text()
        if "LARGE ENTERPRISE" in text.upper():
            return "TOTVS - LARGE ENTERPRISE"
        if "TOTVS S.A" in text.upper() or "TOTVS SA" in text.upper():
            return "TOTVS - MICROSIGA"
        return "TOTVS - LARGE ENTERPRISE" # Default
    except:
        return "TOTVS - LARGE ENTERPRISE"

def main():
    year = datetime.datetime.now().year
    db_path = f'backend/data/notas_fiscais_{year}.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Mapeamento de nomes para IDs
    cursor.execute("SELECT id, nome FROM fornecedores WHERE nome LIKE 'TOTVS%'")
    forn_map = {row[1]: row[0] for row in cursor.fetchall()}
    
    paths = [
        (r"F:\Emalto\Informatica\Conhecimentos\TOTVS\Torque Diesel\2026", 5), # Diesel
        (r"F:\Emalto\Informatica\Conhecimentos\TOTVS\Torque Grill\2026", 7)   # Grill
    ]

    for base_path, emp_id in paths:
        if not os.path.exists(base_path): continue
        files = [f for f in os.listdir(base_path) if f.lower().endswith(".pdf")]
        for filename in files:
            full_path = os.path.join(base_path, filename)
            
            # Extrair Proposta
            reader = PdfReader(full_path)
            text = reader.pages[0].extract_text()
            match = re.search(r"Proposta\s*:\s*([\w\d\/\-]+)", text, re.IGNORECASE)
            if match:
                prop = match.group(1)
                prestador = get_prestador(full_path)
                forn_id = forn_map.get(prestador)
                
                if forn_id:
                    # Atualizar o contrato no banco
                    cursor.execute("UPDATE contratos_software SET fornecedor_id = ? WHERE codigo_contrato = ? AND empresa_grupo_id = ?", 
                                   (forn_id, prop, emp_id))
                    if cursor.rowcount > 0:
                        print(f"[FIX] Contrato {prop} -> {prestador}")
    
    conn.commit()
    conn.close()
    print("\nCorrecao concluida.")

if __name__ == "__main__":
    main()
