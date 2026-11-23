"""
Rotação anual de banco de dados.
Cria novo DB para o ano novo e move o antigo para backup.
"""
import sys
import os
import shutil
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from datetime import datetime
from config import DATA_DIR, BACKUPS_DIR
from database import create_tables_for_year, SessionLocal
from models import EmpresaGrupo, Fornecedor, ContratoSoftware
from services.pre_lancamento import gerar_lancamentos_anuais


def rotacionar_ano(ano_anterior=None, ano_novo=None):
    """Cria banco do ano novo e faz backup do anterior."""
    if not ano_anterior:
        ano_anterior = datetime.now().year - 1
    if not ano_novo:
        ano_novo = datetime.now().year

    db_anterior = DATA_DIR / f"notas_fiscais_{ano_anterior}.db"
    db_novo = DATA_DIR / f"notas_fiscais_{ano_novo}.db"

    print(f"\n{'='*60}")
    print(f"  Rotação Anual: {ano_anterior} → {ano_novo}")
    print(f"{'='*60}\n")

    # 1. Backup do banco anterior
    if db_anterior.exists():
        backup_dest = BACKUPS_DIR / f"notas_fiscais_{ano_anterior}.db"
        if not backup_dest.exists():
            shutil.copy2(str(db_anterior), str(backup_dest))
            print(f"  ✅ Backup criado: {backup_dest}")
        else:
            print(f"  ⚠️ Backup já existe: {backup_dest}")

    # 2. Criar banco novo
    if db_novo.exists():
        print(f"  ⚠️ Banco {ano_novo} já existe!")
        return

    print(f"  ⏳ Criando banco para {ano_novo}...")
    create_tables_for_year(ano_novo)

    # 3. Copiar dados fixos do banco anterior
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    if db_anterior.exists():
        eng_old = create_engine(f"sqlite:///{db_anterior}")
        OldSession = sessionmaker(bind=eng_old)
        old_db = OldSession()

        eng_new = create_engine(f"sqlite:///{db_novo}")
        NewSession = sessionmaker(bind=eng_new)
        new_db = NewSession()

        # Copiar empresas
        for emp in old_db.query(EmpresaGrupo).all():
            new_db.add(EmpresaGrupo(sigla=emp.sigla, nome_completo=emp.nome_completo, ativo=emp.ativo))

        # Copiar fornecedores
        for forn in old_db.query(Fornecedor).all():
            new_db.add(Fornecedor(nome=forn.nome, categoria=forn.categoria, descricao=forn.descricao, ativo=forn.ativo))

        new_db.commit()

        # Copiar contratos (precisa mapear IDs)
        emp_map = {e.sigla: e.id for e in new_db.query(EmpresaGrupo).all()}
        forn_map = {f.nome: f.id for f in new_db.query(Fornecedor).all()}

        for ct in old_db.query(ContratoSoftware).filter(ContratoSoftware.ativo == True).all():
            old_emp = old_db.query(EmpresaGrupo).filter(EmpresaGrupo.id == ct.empresa_grupo_id).first()
            old_forn = old_db.query(Fornecedor).filter(Fornecedor.id == ct.fornecedor_id).first()
            if old_emp and old_forn:
                new_emp_id = emp_map.get(old_emp.sigla)
                new_forn_id = forn_map.get(old_forn.nome)
                if new_emp_id and new_forn_id:
                    new_db.add(ContratoSoftware(
                        fornecedor_id=new_forn_id, empresa_grupo_id=new_emp_id,
                        codigo_contrato=ct.codigo_contrato, descricao=ct.descricao,
                        valor_mensal=ct.valor_mensal, dia_vencimento=ct.dia_vencimento,
                        condicao_pagamento=ct.condicao_pagamento, ativo=True
                    ))
        new_db.commit()
        print(f"  ✅ Dados fixos copiados")

        # 4. Gerar lançamentos mensais
        print(f"  ⏳ Gerando lançamentos para {ano_novo}...")
        resultado = gerar_lancamentos_anuais(new_db, ano_novo)
        print(f"  ✅ {resultado['lancamentos_criados']} lançamentos criados")

        old_db.close()
        new_db.close()
    else:
        print(f"  ⚠️ Banco anterior não encontrado, criando banco limpo.")

    print(f"\n  ✅ Rotação concluída!")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--anterior', type=int)
    parser.add_argument('--novo', type=int)
    args = parser.parse_args()
    rotacionar_ano(args.anterior, args.novo)
