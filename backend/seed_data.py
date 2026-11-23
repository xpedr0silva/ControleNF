"""
Seed de dados iniciais: empresas do grupo, fornecedores e contratos.
Executado apenas se o banco estiver vazio.
"""
from datetime import date
from database import SessionLocal
from models import EmpresaGrupo, Fornecedor, ContratoSoftware, Configuracao, LancamentoMensal, NotaFiscal
from config import EMPRESAS_GRUPO, FORNECEDORES_MENSAIS, FORNECEDORES_AVULSOS, ANO_CORRENTE
from services.pre_lancamento import gerar_lancamentos_anuais


# Mapeamento de contratos extraídos da planilha (fornecedor → empresa:código)
CONTRATOS_MAP = {
    "KTREE": [
        ("EIM", "11366-01"), ("EEM", "004092-01"), ("EEN", "11366-01"),
        ("Fundação", "00460-01"), ("Torque Diesel", None),
    ],
    "TOTVS - MICROSIGA": [
        ("EIM", "02320-01"), ("Torque Diesel", "001381-01"),
    ],
    "TOTVS - SOLUÇÕES": [
        ("EIM", "12075-10"),
    ],
    "TOTVS - LARGE ENTERPRISE": [
        ("Torque Diesel", "003977-02"), ("Torque Grill", "000478-01"),
    ],
    "JUNSOFT": [
        ("Torque Pneus", None),
    ],
    "SYSAID": [
        ("EIM", "12054-01"),
    ],
    "VERO": [
        ("EEN", None), ("EIM", None), ("Torque Diesel", None), ("Torque Grill", None),
    ],
    "VIVO": [
        ("Torque Diesel", None), ("EIM", "05600-09"), ("EEM", "001960-09"),
    ],
    "INTERPONTO": [
        ("EIM", "05450-01"), ("EEM", "000242-01"), ("EEN", "05450-01"),
        ("Torque Diesel", "002253-01"), ("Torque Grill", "000047-01"),
    ],
    "NETSOL": [
        ("EIM", "10990-01"), ("EEM", "003894-01"), ("EEN", "10990-01"),
        ("Torque Diesel", "003457-01"),
    ],
    "MAK SOLUTIONS": [
        ("Torque Diesel", None),
    ],
    "STARLINK": [
        ("EIM", "11565-01"),
    ],
    "GOOGLE CLOUD": [
        ("EIM", "11585-01"),
    ],
    "WEBPOSTO": [
        ("Torque Diesel", None), ("Torque Grill", None),
    ],
}


def seed_if_empty():
    """Popula o banco com dados iniciais se estiver vazio."""
    db = SessionLocal()
    try:
        # Verificar se já tem dados
        if db.query(EmpresaGrupo).count() > 0:
            print("[SEED] Banco ja contem dados, pulando seed.")
            return

        print("[SEED] Populando banco com dados iniciais...")

        # 1. Empresas do Grupo
        empresas_map = {}
        for e in EMPRESAS_GRUPO:
            empresa = EmpresaGrupo(sigla=e["sigla"], nome_completo=e["nome_completo"])
            db.add(empresa)
            db.flush()
            empresas_map[e["sigla"]] = empresa.id
        print(f"  [OK] {len(EMPRESAS_GRUPO)} empresas do grupo criadas")

        # 2. Fornecedores Mensais
        fornecedores_map = {}
        for f in FORNECEDORES_MENSAIS:
            forn = Fornecedor(nome=f["nome"], categoria=f["categoria"], descricao=f["descricao"])
            db.add(forn)
            db.flush()
            fornecedores_map[f["nome"]] = forn.id
        print(f"  [OK] {len(FORNECEDORES_MENSAIS)} fornecedores mensais criados")

        # 3. Fornecedores Avulsos
        for nome in FORNECEDORES_AVULSOS:
            forn = Fornecedor(nome=nome, categoria="AVULSO")
            db.add(forn)
        print(f"  [OK] {len(FORNECEDORES_AVULSOS)} fornecedores avulsos criados")

        # 4. Contratos de Software
        contratos_criados = 0
        for forn_nome, contratos in CONTRATOS_MAP.items():
            forn_id = fornecedores_map.get(forn_nome)
            if not forn_id:
                continue
            for empresa_sigla, codigo in contratos:
                empresa_id = empresas_map.get(empresa_sigla)
                if not empresa_id:
                    continue
                contrato = ContratoSoftware(
                    fornecedor_id=forn_id,
                    empresa_grupo_id=empresa_id,
                    codigo_contrato=codigo,
                    dia_vencimento=15,
                    condicao_pagamento="MENSAL",
                )
                db.add(contrato)
                contratos_criados += 1
        print(f"  [OK] {contratos_criados} contratos de software criados")

        # 5. Configurações
        configs = [
            ("ano_corrente", str(ANO_CORRENTE), "Ano de referência atual"),
            ("notificacao_hora", "07:00", "Horário de notificação diária"),
            ("dias_alerta_vencimento", "7", "Dias de antecedência para alertas"),
        ]
        for chave, valor, desc in configs:
            db.add(Configuracao(chave=chave, valor=valor, descricao=desc))

        db.commit()

        # 6. Gerar lançamentos mensais para o ano corrente
        print(f"  [...] Gerando lancamentos mensais para {ANO_CORRENTE}...")
        resultado = gerar_lancamentos_anuais(db, ANO_CORRENTE)
        print(f"  [OK] {resultado['lancamentos_criados']} lancamentos mensais criados")

        # 7. Criar dados fictícios de demonstração para apresentação acadêmica
        print(f"  [...] Gerando dados e notas fiscais de demonstracao...")
        seed_demo_data(db, ANO_CORRENTE)

        print("[SEED] Seed concluido com sucesso!")

    except Exception as e:
        db.rollback()
        print(f"[SEED] ERRO no seed: {e}")
        raise
    finally:
        db.close()


def seed_demo_data(db, ano: int):
    """
    Popula dados fictícios de demonstração para apresentação acadêmica.
    Garante que gráficos, KPIs e matriz anual fiquem ilustrados sem exibir nenhum dado real.
    """
    try:
        # Valores mensais genéricos para os contratos
        contratos = db.query(ContratoSoftware).all()
        demo_valores = [150.0, 220.0, 350.0, 180.0, 420.0, 290.0, 500.0, 120.0]
        for idx, c in enumerate(contratos):
            c.valor_mensal = demo_valores[idx % len(demo_valores)]
        db.flush()

        # Amostra de faturas fictícias de demonstração
        demo_nfs = [
            (1, "KTREE", "EIM", "000.010.101", "10101", 350.0, "OK", "FATURADO"),
            (1, "KTREE", "EEM", "000.010.102", "10102", 180.0, "OK", "FATURADO"),
            (1, "TOTVS - MICROSIGA", "EIM", "000.010.103", "10103", 500.0, "OK", "FATURADO"),
            (1, "VERO", "EEN", "000.010.104", "10104", 220.0, "OK", "FATURADO"),
            (2, "KTREE", "EIM", "000.010.201", "10201", 350.0, "OK", "FATURADO"),
            (2, "KTREE", "EEM", "000.010.202", "10202", 180.0, "OK", "FATURADO"),
            (2, "SYSAID", "EIM", "000.010.203", "10203", 420.0, "PENDENTE", "LANCADO"),
            (3, "KTREE", "EIM", "000.010.301", "10301", 350.0, "OK", "FATURADO"),
            (3, "GOOGLE CLOUD", "EIM", "000.010.302", "10302", 150.0, "OK", "FATURADO"),
            (3, "STARLINK", "EIM", "000.010.303", "10303", 290.0, "PENDENTE", "LANCADO"),
            (4, "INTERPONTO", "EIM", "000.010.401", "10401", 120.0, "OK", "FATURADO"),
        ]

        for mes, forn_nome, emp_sigla, nf_num, ped_num, val, status_pre, status_lanc in demo_nfs:
            forn = db.query(Fornecedor).filter(Fornecedor.nome == forn_nome).first()
            emp = db.query(EmpresaGrupo).filter(EmpresaGrupo.sigla == emp_sigla).first()
            if not forn or not emp:
                continue

            contrato = db.query(ContratoSoftware).filter(
                ContratoSoftware.fornecedor_id == forn.id,
                ContratoSoftware.empresa_grupo_id == emp.id
            ).first()

            lanc = None
            if contrato:
                lanc = db.query(LancamentoMensal).filter(
                    LancamentoMensal.contrato_id == contrato.id,
                    LancamentoMensal.mes == mes,
                    LancamentoMensal.ano == ano
                ).first()
                if lanc:
                    lanc.status = status_lanc
                    lanc.numero_nota = nf_num
                    lanc.numero_pedido = ped_num
                    lanc.valor = val

            nf = NotaFiscal(
                empresa_fornecedor=forn_nome,
                numero_nota=nf_num,
                numero_pedido=ped_num,
                valor=val,
                empresa_grupo_id=emp.id,
                codigo_fornecedor=contrato.codigo_contrato if (contrato and contrato.codigo_contrato) else "DEMO-01",
                data_vencimento=date(ano, mes, 15),
                status_pre_nota=status_pre,
                tipo="MENSAL",
                lancamento_mensal_id=lanc.id if lanc else None,
                contrato_id=contrato.id if contrato else None,
                mes_referencia=mes,
                ano_referencia=ano,
                observacao="Nota fiscal de demonstração gerada para fins acadêmicos."
            )
            db.add(nf)

        db.commit()
        print("  [OK] Dados e notas fiscais de demonstracao criados com sucesso!")
    except Exception as err:
        print(f"  [AVISO] Nao foi possivel carregar dados de demo: {err}")


if __name__ == "__main__":
    seed_if_empty()
