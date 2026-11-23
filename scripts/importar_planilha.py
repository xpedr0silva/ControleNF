"""
Importador de dados da planilha Excel existente.
Lê as 5 abas e popula o banco SQLite.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from datetime import datetime, date
import openpyxl
from database import SessionLocal, create_tables
from models import NotaFiscal, EmpresaGrupo


# Mapeamento de siglas usadas na planilha para nomes do banco
SIGLA_MAP = {
    'EMALTO INDÚSTRIA': 'EIM', 'EMALTO INDUSTRIA': 'EIM', 'EIM': 'EIM',
    'EMALTO ESTRUTURAS': 'EEM', 'EEM': 'EEM',
    'EMALTO ENERGIA': 'EEN', 'EEN': 'EEN',
    'FUNDAÇÃO EMALTO': 'Fundação', 'FUNDACAO EMALTO': 'Fundação',
    'TORQUE DIESEL': 'Torque Diesel',
    'TORQUE DIESEL - FILIAL': 'Torque Diesel Filial',
    'TORQUE GRILL': 'Torque Grill',
    'TORQUE PNEUS': 'Torque Pneus',
    'EMALTO AGRONEGÓCIOS': 'Agronegócios', 'AGRONEGÓCIOS': 'Agronegócios',
    'AGRONEGOCIOS': 'Agronegócios',
}

# Mapeamento de mês da aba
MES_MAP = {
    'DEZ': 12, 'JAN': 1, 'FEV': 2, 'MAR': 3, 'ABR': 4,
    'MAI': 5, 'JUN': 6, 'JUL': 7, 'AGO': 8, 'SET': 9, 'OUT': 10, 'NOV': 11,
}


def parse_sheet_name(name):
    """Extrai mês e ano do nome da aba (ex: 'DEZ-25' → (12, 2025))."""
    parts = name.upper().split('-')
    if len(parts) != 2:
        return None, None
    mes = MES_MAP.get(parts[0])
    ano = int('20' + parts[1]) if len(parts[1]) == 2 else int(parts[1])
    return mes, ano


def resolve_empresa(db, grupo_nome):
    """Resolve o nome da empresa para o ID no banco."""
    if not grupo_nome:
        return None
    nome_upper = grupo_nome.strip().upper()
    sigla = SIGLA_MAP.get(nome_upper, nome_upper)
    empresa = db.query(EmpresaGrupo).filter(EmpresaGrupo.sigla == sigla).first()
    return empresa.id if empresa else None


def parse_date(value):
    """Tenta converter diversos formatos de data."""
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        value = value.strip()
        if value.upper() in ('À VISTA', 'A VISTA', 'AVISTA'):
            return None
        for fmt in ('%d/%m/%Y', '%d/%m/%y', '%Y-%m-%d'):
            try:
                return datetime.strptime(value, fmt).date()
            except ValueError:
                continue
    return None


def importar_planilha(caminho_xlsx, dry_run=False):
    """Importa dados da planilha para o banco."""
    print(f"\n{'='*60}")
    print(f"  Importando: {caminho_xlsx}")
    print(f"  Modo: {'DRY RUN (sem gravar)' if dry_run else 'GRAVAÇÃO REAL'}")
    print(f"{'='*60}\n")

    wb = openpyxl.load_workbook(caminho_xlsx)
    db = SessionLocal()
    total_importadas = 0
    erros = []

    try:
        for sheet_name in wb.sheetnames:
            mes, ano = parse_sheet_name(sheet_name)
            if not mes or not ano:
                print(f"  [!] Aba ignorada: {sheet_name}")
                continue

            ws = wb[sheet_name]
            count = 0
            print(f"\n  Processando: {sheet_name} ({mes}/{ano})")

            for row in range(3, ws.max_row + 1):
                empresa = ws.cell(row, 1).value
                if not empresa:
                    continue

                numero_nota = ws.cell(row, 2).value
                numero_pedido = ws.cell(row, 3).value
                valor = ws.cell(row, 4).value
                grupo = ws.cell(row, 5).value
                vencimento = ws.cell(row, 6).value
                pre_nota = ws.cell(row, 7).value

                empresa_grupo_id = resolve_empresa(db, grupo)
                data_venc = parse_date(vencimento)
                status = 'OK' if pre_nota and str(pre_nota).strip().upper() == 'OK' else 'PENDENTE'

                # Determinar condição de pagamento
                condicao = None
                if isinstance(vencimento, str) and vencimento.strip().upper() in ('À VISTA', 'A VISTA'):
                    condicao = 'A_VISTA'

                nf = NotaFiscal(
                    empresa_fornecedor=str(empresa).strip(),
                    numero_nota=str(numero_nota).strip() if numero_nota else None,
                    numero_pedido=str(numero_pedido).strip() if numero_pedido else None,
                    valor=float(valor) if valor else 0.0,
                    empresa_grupo_id=empresa_grupo_id,
                    data_vencimento=data_venc,
                    status_pre_nota=status,
                    condicao_pagamento=condicao,
                    tipo='AVULSO',
                    mes_referencia=mes,
                    ano_referencia=ano,
                )

                if not dry_run:
                    db.add(nf)
                count += 1

            if not dry_run:
                db.commit()
            total_importadas += count
            print(f"     [OK] {count} notas processadas")

        print(f"\n{'='*60}")
        print(f"  TOTAL: {total_importadas} notas fiscais importadas")
        if erros:
            print(f"  ERROS: {len(erros)}")
            for e in erros[:10]:
                print(f"    - {e}")
        print(f"{'='*60}\n")

    except Exception as e:
        db.rollback()
        print(f"\n  ERRO: {e}")
        raise
    finally:
        db.close()

    return total_importadas


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Importar planilha de NFs')
    parser.add_argument('arquivo', nargs='?',
        default=r'C:\Users\pedro.martins\Documents\Automats\Planilha de controle\Controle Notas Fiscais.xlsx')
    parser.add_argument('--dry-run', action='store_true', help='Simular sem gravar')
    args = parser.parse_args()

    create_tables()
    importar_planilha(args.arquivo, dry_run=args.dry_run)
