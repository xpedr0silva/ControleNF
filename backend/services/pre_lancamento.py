"""
Servico de pre-lancamento de contratos mensais.
Gera lancamentos de Jan-Dez para cada contrato ativo.
Suporta multiplas NFs por lancamento mensal.
"""
from datetime import datetime, date
from sqlalchemy.orm import Session
from models import ContratoSoftware, LancamentoMensal
from services.vencimento import calcular_vencimento


def gerar_lancamentos_anuais(db: Session, ano: int) -> dict:
    """
    Gera lancamentos mensais (Jan-Dez) para todos os contratos ativos.

    Returns:
        Dict com {criados, existentes, erros, detalhes}
    """
    contratos = db.query(ContratoSoftware).filter(
        ContratoSoftware.ativo == True
    ).all()

    criados = 0
    existentes = 0
    erros = []

    for contrato in contratos:
        for mes in range(1, 13):
            # Verificar vigencia
            primeiro_dia_mes = date(ano, mes, 1)
            
            # Se o contrato ainda nao comecou ou ja terminou, pular ou remover se for PENDENTE
            fora_da_vigencia = False
            if contrato.data_inicio and primeiro_dia_mes < contrato.data_inicio.replace(day=1):
                fora_da_vigencia = True
            if contrato.data_fim and primeiro_dia_mes > contrato.data_fim.replace(day=1):
                fora_da_vigencia = True
            
            if fora_da_vigencia:
                # Se ja existe um lancamento PENDENTE fora da vigencia, removemos
                db.query(LancamentoMensal).filter(
                    LancamentoMensal.contrato_id == contrato.id,
                    LancamentoMensal.mes == mes,
                    LancamentoMensal.ano == ano,
                    LancamentoMensal.status == "PENDENTE"
                ).delete()
                continue

            existente = db.query(LancamentoMensal).filter(
                LancamentoMensal.contrato_id == contrato.id,
                LancamentoMensal.mes == mes,
                LancamentoMensal.ano == ano,
            ).first()

            if existente:
                existentes += 1
                continue

            try:
                data_venc = calcular_vencimento(ano, mes, contrato.dia_vencimento)

                lancamento = LancamentoMensal(
                    contrato_id=contrato.id,
                    mes=mes,
                    ano=ano,
                    data_vencimento=data_venc,
                    status="PENDENTE",
                    valor=contrato.valor_mensal,
                )
                db.add(lancamento)
                criados += 1
            except Exception as e:
                erros.append(f"Contrato {contrato.id}, Mes {mes}: {str(e)}")

    db.commit()

    return {
        "ano": ano,
        "contratos_processados": len(contratos),
        "lancamentos_criados": criados,
        "lancamentos_existentes": existentes,
        "erros": erros,
    }


def atualizar_status_lancamento(
    db: Session,
    lancamento_id: int,
    status: str,
    numero_nota: str = None,
    numero_pedido: str = None,
    valor: float = None,
) -> LancamentoMensal:
    """Atualiza o status de um lancamento mensal."""
    lancamento = db.query(LancamentoMensal).filter(
        LancamentoMensal.id == lancamento_id
    ).first()

    if not lancamento:
        return None

    lancamento.status = status
    lancamento.updated_at = datetime.now()

    if numero_nota is not None:
        lancamento.numero_nota = numero_nota
    if numero_pedido is not None:
        lancamento.numero_pedido = numero_pedido
    if valor is not None:
        lancamento.valor = valor

    db.commit()
    db.refresh(lancamento)
    return lancamento


def obter_matriz_contratos(db: Session, ano: int, mes: int = None) -> list[dict]:
    """
    Retorna a matriz de contratos para visualizacao.
    Formato: fornecedor -> meses -> status de cada contrato.
    Status derivado automaticamente:
    - LANCADO: >=1 NF vinculada ao lancamento
    - VENCIDO: data passou sem NF
    - PENDENTE: aguardando NF
    Suporta multiplas NFs por lancamento com contagem e valor consolidado.
    """
    from datetime import date as date_type
    from models import Fornecedor, EmpresaGrupo, NotaFiscal
    from sqlalchemy.orm import joinedload, selectinload

    query = db.query(LancamentoMensal).join(
        ContratoSoftware
    ).join(
        Fornecedor, ContratoSoftware.fornecedor_id == Fornecedor.id
    ).join(
        EmpresaGrupo, ContratoSoftware.empresa_grupo_id == EmpresaGrupo.id
    ).filter(
        LancamentoMensal.ano == ano,
        ContratoSoftware.ativo == True
    ).options(
        joinedload(LancamentoMensal.contrato).joinedload(ContratoSoftware.fornecedor),
        joinedload(LancamentoMensal.contrato).joinedload(ContratoSoftware.empresa_grupo),
        selectinload(LancamentoMensal.notas_fiscais),
    )

    if mes:
        query = query.filter(LancamentoMensal.mes == mes)

    lancamentos = query.all()
    hoje = date_type.today()

    matriz = {}
    for lanc in lancamentos:
        forn_nome = lanc.contrato.fornecedor.nome
        if forn_nome not in matriz:
            matriz[forn_nome] = {
                "fornecedor": forn_nome,
                "fornecedor_id": lanc.contrato.fornecedor.id,
                "meses": {}
            }

        if lanc.mes not in matriz[forn_nome]["meses"]:
            matriz[forn_nome]["meses"][lanc.mes] = []

        notas = lanc.notas_fiscais or []
        quantidade_nf = len(notas)
        nota_lancada = quantidade_nf > 0
        valor_total_nf = sum(n.valor or 0 for n in notas) if nota_lancada else 0

        if nota_lancada:
            status = "LANCADO"
        elif lanc.status in ["CANCELADO", "NAO_SE_APLICA"]:
            status = lanc.status
        elif lanc.data_vencimento and lanc.data_vencimento < hoje:
            status = "VENCIDO"
        else:
            status = "PENDENTE"

        if lanc.status != status:
            lanc.status = status

        notas_detalhe = []
        if nota_lancada:
            for n in notas:
                notas_detalhe.append({
                    "nota_id": n.id,
                    "numero_nota": n.numero_nota,
                    "numero_pedido": n.numero_pedido,
                    "valor": n.valor,
                    "status_pre_nota": n.status_pre_nota,
                    "enviado_email": n.enviado_email,
                    "protocolo_pre_nota": n.protocolo_pre_nota,
                })

        matriz[forn_nome]["meses"][lanc.mes].append({
            "lancamento_id": lanc.id,
            "contrato_id": lanc.contrato.id,
            "empresa": lanc.contrato.empresa_grupo.sigla,
            "codigo_contrato": lanc.contrato.codigo_contrato,
            "status": status,
            "nota_lancada": nota_lancada,
            "quantidade_nf": quantidade_nf,
            "valor_total_nf": valor_total_nf,
            "nota_id": notas[0].id if nota_lancada else None,
            "numero_nota": notas[0].numero_nota if nota_lancada else lanc.numero_nota,
            "valor": valor_total_nf if nota_lancada else lanc.valor,
            "data_vencimento": lanc.data_vencimento.isoformat() if lanc.data_vencimento else None,
            "notas": notas_detalhe,
        })

    db.commit()
    return list(matriz.values())
