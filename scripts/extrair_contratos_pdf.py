import os
import re
from pypdf import PdfReader

def extract_proposal(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        # Check first 2 pages
        text = ""
        for i in range(min(len(reader.pages), 2)):
            text += reader.pages[i].extract_text()
        
        # Search for pattern :Proposta: 354970/01 or similar
        # Pattern handles spaces and variations
        match = re.search(r":\s*Proposta\s*:\s*([\w\d\/\-]+)", text, re.IGNORECASE)
        if match:
            return match.group(1)
        
        # Fallback search if ":Proposta:" is not exact
        match = re.search(r"Proposta\s*:\s*([\w\d\/\-]+)", text, re.IGNORECASE)
        if match:
            return match.group(1)
            
        return None
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    base_path = r"F:\Emalto\Informatica\Conhecimentos\TOTVS\Torque Grill\2026"
    results = []
    
    if not os.path.exists(base_path):
        print(f"Path not found: {base_path}")
        return

    print(f"Analisando arquivos em: {base_path}\n")
    
    files = [f for f in os.listdir(base_path) if f.lower().endswith(".pdf")]
    
    for filename in files:
        full_path = os.path.join(base_path, filename)
        proposal = extract_proposal(full_path)
        if proposal:
            results.append((filename, proposal))
            print(f"[OK] {filename} -> {proposal}")
        else:
            # print(f"[..] {filename} -> Nao encontrado")
            pass

    # Also check Tickets Contratos
    tickets_path = os.path.join(base_path, "Tickets Contratos")
    if os.path.exists(tickets_path):
        print(f"\nAnalisando Tickets em: {tickets_path}\n")
        ticket_files = [f for f in os.listdir(tickets_path) if f.lower().endswith(".pdf")]
        for filename in ticket_files:
            full_path = os.path.join(tickets_path, filename)
            proposal = extract_proposal(full_path)
            if proposal:
                results.append((f"Ticket/{filename}", proposal))
                print(f"[OK] {filename} -> {proposal}")

    print(f"\nResumo: {len(results)} propostas encontradas.")

if __name__ == "__main__":
    main()
