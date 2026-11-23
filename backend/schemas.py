"""
Pydantic V2 schemas para validação de request/response.
"""
from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional


# === Empresa Grupo ===
class EmpresaGrupoBase(BaseModel):
    sigla: str = Field(..., max_length=50)
    nome_completo: str = Field(..., max_length=200)
    ativo: bool = True

class EmpresaGrupoCreate(EmpresaGrupoBase):
    pass

class EmpresaGrupoUpdate(BaseModel):
    sigla: Optional[str] = None
    nome_completo: Optional[str] = None
    ativo: Optional[bool] = None

class EmpresaGrupoResponse(EmpresaGrupoBase):
    id: int
    created_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


# === Fornecedor ===
class FornecedorBase(BaseModel):
    nome: str = Field(..., max_length=100)
    categoria: str = Field(default="AVULSO", max_length=20)
    descricao: Optional[str] = None
    ativo: bool = True

class FornecedorCreate(FornecedorBase):
    pass

class FornecedorUpdate(BaseModel):
    nome: Optional[str] = None
    categoria: Optional[str] = None
    descricao: Optional[str] = None
    ativo: Optional[bool] = None

class FornecedorResponse(FornecedorBase):
    id: int
    created_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


# === Identificador de Fornecedor/Empresa (Cód. Planilha) ===
class FornecedorEmpresaIdentificadorBase(BaseModel):
    fornecedor_id: int
    empresa_grupo_id: int
    codigo_identificador: Optional[str] = None

class FornecedorEmpresaIdentificadorCreate(FornecedorEmpresaIdentificadorBase):
    pass

class FornecedorEmpresaIdentificadorUpdate(BaseModel):
    codigo_identificador: Optional[str] = None

class FornecedorEmpresaIdentificadorResponse(FornecedorEmpresaIdentificadorBase):
    id: int
    fornecedor: Optional[FornecedorResponse] = None
    empresa_grupo: Optional[EmpresaGrupoResponse] = None
    model_config = {"from_attributes": True}


# === Contrato Software ===
class ContratoSoftwareBase(BaseModel):
    fornecedor_id: int
    empresa_grupo_id: int
    codigo_contrato: Optional[str] = None
    codigo_fornecedor: Optional[str] = None
    descricao: Optional[str] = None
    valor_mensal: Optional[float] = 0.0
    dia_vencimento: Optional[int] = 15
    condicao_pagamento: Optional[str] = "MENSAL"
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None
    ativo: bool = True
    mes_encerramento: Optional[int] = None
    ano_encerramento: Optional[int] = None

class ContratoSoftwareCreate(ContratoSoftwareBase):
    pass

class ContratoSoftwareUpdate(BaseModel):
    fornecedor_id: Optional[int] = None
    empresa_grupo_id: Optional[int] = None
    codigo_contrato: Optional[str] = None
    codigo_fornecedor: Optional[str] = None
    descricao: Optional[str] = None
    valor_mensal: Optional[float] = None
    dia_vencimento: Optional[int] = None
    condicao_pagamento: Optional[str] = None
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None
    ativo: Optional[bool] = None
    mes_encerramento: Optional[int] = None
    ano_encerramento: Optional[int] = None

class ContratoSoftwareResponse(ContratoSoftwareBase):
    id: int
    fornecedor: Optional[FornecedorResponse] = None
    empresa_grupo: Optional[EmpresaGrupoResponse] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


# === Lançamento Mensal ===
class LancamentoMensalBase(BaseModel):
    contrato_id: int
    mes: int = Field(..., ge=1, le=12)
    ano: int
    data_vencimento: date
    status: str = "PENDENTE"
    numero_nota: Optional[str] = None
    numero_pedido: Optional[str] = None
    valor: float = 0.0
    observacao: Optional[str] = None

class LancamentoMensalCreate(LancamentoMensalBase):
    pass

class LancamentoMensalUpdate(BaseModel):
    status: Optional[str] = None
    numero_nota: Optional[str] = None
    numero_pedido: Optional[str] = None
    valor: Optional[float] = None
    observacao: Optional[str] = None
    data_vencimento: Optional[date] = None

class LancamentoMensalResponse(LancamentoMensalBase):
    id: int
    contrato: Optional[ContratoSoftwareResponse] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


# === Nota Fiscal ===
class NotaFiscalBase(BaseModel):
    empresa_fornecedor: str = Field(..., max_length=100)
    numero_nota: Optional[str] = None
    numero_pedido: Optional[str] = None
    valor: float = 0.0
    empresa_grupo_id: Optional[int] = None
    data_vencimento: Optional[date] = None
    status_pre_nota: str = "PENDENTE"
    enviado_email: bool = False
    protocolo_pre_nota: Optional[str] = None
    condicao_pagamento: Optional[str] = None
    tipo: str = "AVULSO"
    lancamento_mensal_id: Optional[int] = None
    contrato_id: Optional[int] = None
    codigo_fornecedor: Optional[str] = None
    mes_referencia: Optional[int] = None
    ano_referencia: Optional[int] = None
    observacao: Optional[str] = None

class NotaFiscalCreate(NotaFiscalBase):
    pass

class NotaFiscalUpdate(BaseModel):
    empresa_fornecedor: Optional[str] = None
    numero_nota: Optional[str] = None
    numero_pedido: Optional[str] = None
    valor: Optional[float] = None
    empresa_grupo_id: Optional[int] = None
    data_vencimento: Optional[date] = None
    status_pre_nota: Optional[str] = None
    enviado_email: Optional[bool] = None
    protocolo_pre_nota: Optional[str] = None
    condicao_pagamento: Optional[str] = None
    tipo: Optional[str] = None
    lancamento_mensal_id: Optional[int] = None
    contrato_id: Optional[int] = None
    codigo_fornecedor: Optional[str] = None
    mes_referencia: Optional[int] = None
    ano_referencia: Optional[int] = None
    observacao: Optional[str] = None

class NotaFiscalResponse(NotaFiscalBase):
    id: int
    empresa_grupo: Optional[EmpresaGrupoResponse] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


# === Dashboard ===
class DashboardKPIs(BaseModel):
    total_nfs: int = 0
    nfs_pendentes: int = 0
    nfs_vencidas: int = 0
    nfs_ok: int = 0
    valor_total: float = 0.0
    valor_pendente: float = 0.0
    contratos_faturados: int = 0
    contratos_total: int = 0
    percentual_faturado: float = 0.0

class ProximoVencimento(BaseModel):
    fornecedor: str
    empresa: str
    data_vencimento: date
    valor: float
    status: str
    dias_restantes: int

class GastoPorFornecedor(BaseModel):
    fornecedor: str
    valor_total: float
    quantidade: int

class GastoPorEmpresa(BaseModel):
    empresa: str
    valor_total: float
    quantidade: int

class GastoMensal(BaseModel):
    mes: int
    nome_mes: str
    valor_total: float
    quantidade: int


# === Notificações ===
class NotificacaoItem(BaseModel):
    tipo: str  # "vencida" | "vencendo_hoje" | "vencendo_semana"
    fornecedor: str
    empresa: str
    valor: float
    data_vencimento: date
    dias_restantes: int

class NotificacaoResumo(BaseModel):
    vencidas: int = 0
    vencendo_hoje: int = 0
    vencendo_semana: int = 0
    items: list[NotificacaoItem] = []


# === Matriz de Contratos ===
class NotaVinculadaResumo(BaseModel):
    nota_id: int
    numero_nota: Optional[str] = None
    numero_pedido: Optional[str] = None
    valor: Optional[float] = None
    status_pre_nota: Optional[str] = None
    enviado_email: Optional[bool] = None
    protocolo_pre_nota: Optional[str] = None

class MatrizContratoCell(BaseModel):
    contrato_id: int
    lancamento_id: int
    fornecedor: str
    empresa: str
    codigo_contrato: Optional[str] = None
    mes: int
    status: str
    nota_lancada: bool = False
    quantidade_nf: int = 0
    valor_total_nf: float = 0.0
    nota_id: Optional[int] = None
    numero_nota: Optional[str] = None
    valor: float = 0.0
    data_vencimento: Optional[date] = None
    notas: list[NotaVinculadaResumo] = []

class MatrizContratoRow(BaseModel):
    fornecedor: str
    fornecedor_id: int
    meses: dict[int, list[MatrizContratoCell]] = {}
