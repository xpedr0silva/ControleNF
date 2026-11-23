"""
Modelos SQLAlchemy para o Sistema de Controle de Notas Fiscais.
"""
from datetime import datetime, date
from sqlalchemy import (
    Column, Integer, String, Float, Date, DateTime,
    Boolean, ForeignKey, Text, Index
)
from sqlalchemy.orm import relationship
from database import Base


class EmpresaGrupo(Base):
    """Empresas do Grupo Emalto (EIM, EEM, EEN, Torque, etc.)."""
    __tablename__ = "empresas_grupo"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sigla = Column(String(50), unique=True, nullable=False)
    nome_completo = Column(String(200), nullable=False)
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)

    # Relacionamentos
    contratos = relationship("ContratoSoftware", back_populates="empresa_grupo")
    notas_fiscais = relationship("NotaFiscal", back_populates="empresa_grupo")

    def __repr__(self):
        return f"<EmpresaGrupo {self.sigla}>"


class Fornecedor(Base):
    """Fornecedores de software e serviços."""
    __tablename__ = "fornecedores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100), unique=True, nullable=False)
    categoria = Column(String(20), nullable=False, default="AVULSO")  # SOFTWARE_MENSAL | AVULSO
    descricao = Column(String(200))
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)

    # Relacionamentos
    contratos = relationship("ContratoSoftware", back_populates="fornecedor")

    def __repr__(self):
        return f"<Fornecedor {self.nome}>"


class FornecedorEmpresaIdentificador(Base):
    """Mapeamento de codigo identificador (planilha) para cada Fornecedor + Empresa."""
    __tablename__ = "fornecedor_empresa_identificador"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fornecedor_id = Column(Integer, ForeignKey("fornecedores.id"), nullable=False)
    empresa_grupo_id = Column(Integer, ForeignKey("empresas_grupo.id"), nullable=False)
    codigo_identificador = Column(String(50))  # Ex: "11366-01", "KTREE", etc.

    fornecedor = relationship("Fornecedor")
    empresa_grupo = relationship("EmpresaGrupo")

    __table_args__ = (
        Index("ix_identificador_fornecedor_empresa", "fornecedor_id", "empresa_grupo_id", unique=True),
    )

    def __repr__(self):
        return f"<Identificador {self.fornecedor_id}->{self.empresa_grupo_id}: {self.codigo_identificador}>"


class ContratoSoftware(Base):
    """Contratos fixos de software mensal (referência fixa)."""
    __tablename__ = "contratos_software"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fornecedor_id = Column(Integer, ForeignKey("fornecedores.id"), nullable=False)
    empresa_grupo_id = Column(Integer, ForeignKey("empresas_grupo.id"), nullable=False)
    codigo_contrato = Column(String(50))  # Ex: "(11366-01)"
    descricao = Column(String(200))
    valor_mensal = Column(Float, default=0.0)
    dia_vencimento = Column(Integer, default=15)  # Dia fixo do mês
    condicao_pagamento = Column(String(50), default="MENSAL")  # MENSAL | 1/30/60/90 | A_VISTA
    data_inicio = Column(Date) # Data de inicio da vigencia
    data_fim = Column(Date)    # Data de encerramento da vigencia
    ativo = Column(Boolean, default=True)
    codigo_fornecedor = Column(String(50))  # Código do fornecedor na planilha (ex: 02320-01, EEN, etc.)
    mes_encerramento = Column(Integer)  # Mes de encerramento programado (1-12), None se nao encerra
    ano_encerramento = Column(Integer)  # Ano de encerramento programado, None se nao encerra
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relacionamentos
    fornecedor = relationship("Fornecedor", back_populates="contratos")
    empresa_grupo = relationship("EmpresaGrupo", back_populates="contratos")
    lancamentos = relationship("LancamentoMensal", back_populates="contrato")

    __table_args__ = (
        Index("ix_contrato_fornecedor_empresa", "fornecedor_id", "empresa_grupo_id"),
    )

    def __repr__(self):
        return f"<Contrato {self.fornecedor_id} -> {self.empresa_grupo_id}>"


class LancamentoMensal(Base):
    """Lançamentos mensais pré-gerados para cada contrato (Jan-Dez)."""
    __tablename__ = "lancamentos_mensais"

    id = Column(Integer, primary_key=True, autoincrement=True)
    contrato_id = Column(Integer, ForeignKey("contratos_software.id"), nullable=False)
    mes = Column(Integer, nullable=False)  # 1-12
    ano = Column(Integer, nullable=False)
    data_vencimento = Column(Date, nullable=False)  # Ajustada para dia útil
    status = Column(String(20), default="PENDENTE")  # PENDENTE | FATURADO | PAGO | VENCIDO | LANCADO | CANCELADO | NAO_SE_APLICA
    numero_nota = Column(String(50))  # Preenchido quando faturado
    numero_pedido = Column(String(50))
    valor = Column(Float, default=0.0)
    observacao = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relacionamentos
    contrato = relationship("ContratoSoftware", back_populates="lancamentos")
    notas_fiscais = relationship("NotaFiscal", back_populates="lancamento_mensal")

    __table_args__ = (
        Index("ix_lancamento_mes_ano", "mes", "ano"),
        Index("ix_lancamento_status", "status"),
        Index("ix_lancamento_contrato_mes_ano", "contrato_id", "mes", "ano", unique=True),
    )

    def __repr__(self):
        return f"<Lancamento {self.contrato_id} {self.mes}/{self.ano}>"


class NotaFiscal(Base):
    """Notas fiscais registradas (tanto de contratos mensais quanto avulsas)."""
    __tablename__ = "notas_fiscais"

    id = Column(Integer, primary_key=True, autoincrement=True)
    empresa_fornecedor = Column(String(100), nullable=False)  # Nome do fornecedor
    numero_nota = Column(String(50))
    numero_pedido = Column(String(50))
    valor = Column(Float, default=0.0)
    empresa_grupo_id = Column(Integer, ForeignKey("empresas_grupo.id"))
    codigo_fornecedor = Column(String(50))
    data_vencimento = Column(Date)
    status_pre_nota = Column(String(20), default="PENDENTE")  # OK | PENDENTE
    enviado_email = Column(Boolean, default=False)  # Se foi enviada por email
    protocolo_pre_nota = Column(String(50))  # Numero do protocolo da pre-nota
    condicao_pagamento = Column(String(50))
    tipo = Column(String(20), default="AVULSO")  # MENSAL | AVULSO
    lancamento_mensal_id = Column(Integer, ForeignKey("lancamentos_mensais.id"), nullable=True)
    contrato_id = Column(Integer, ForeignKey("contratos_software.id"), nullable=True)
    mes_referencia = Column(Integer)  # 1-12
    ano_referencia = Column(Integer)
    observacao = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relacionamentos
    empresa_grupo = relationship("EmpresaGrupo", back_populates="notas_fiscais")
    lancamento_mensal = relationship("LancamentoMensal", back_populates="notas_fiscais")

    __table_args__ = (
        Index("ix_nf_mes_ano", "mes_referencia", "ano_referencia"),
        Index("ix_nf_fornecedor", "empresa_fornecedor"),
        Index("ix_nf_status", "status_pre_nota"),
        Index("ix_nf_vencimento", "data_vencimento"),
    )

    def __repr__(self):
        return f"<NF {self.numero_nota} - {self.empresa_fornecedor}>"


class Configuracao(Base):
    """Configurações gerais do sistema."""
    __tablename__ = "configuracoes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chave = Column(String(100), unique=True, nullable=False)
    valor = Column(Text)
    descricao = Column(String(200))
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f"<Config {self.chave}={self.valor}>"
