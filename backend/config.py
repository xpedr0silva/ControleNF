"""
Configurações centrais do Sistema de Controle de Notas Fiscais.
"""
import os
import socket
from pathlib import Path
from datetime import datetime

# === Diretórios ===
BASE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = BASE_DIR / "backend"
FRONTEND_DIR = BASE_DIR / "frontend"
DATA_DIR = BACKEND_DIR / "data"
BACKUPS_DIR = DATA_DIR / "backups"
EXPORTS_DIR = DATA_DIR / "exports"

# Criar diretórios se não existirem
DATA_DIR.mkdir(parents=True, exist_ok=True)
BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

# === Banco de Dados ===
ANO_CORRENTE = datetime.now().year
DB_FILENAME = f"notas_fiscais_{ANO_CORRENTE}.db"
DATABASE_URL = f"sqlite:///{DATA_DIR / DB_FILENAME}"

def get_database_url(ano: int = None) -> str:
    """Retorna a URL do banco de dados para um ano específico."""
    if ano is None:
        ano = ANO_CORRENTE
    db_file = DATA_DIR / f"notas_fiscais_{ano}.db"
    return f"sqlite:///{db_file}"

def get_backup_databases() -> list[dict]:
    """Lista os bancos de dados de backup disponíveis."""
    dbs = []
    for f in sorted(DATA_DIR.glob("notas_fiscais_*.db")):
        ano = f.stem.replace("notas_fiscais_", "")
        dbs.append({
            "ano": int(ano),
            "arquivo": str(f),
            "tamanho_mb": round(f.stat().st_size / (1024 * 1024), 2),
            "corrente": int(ano) == ANO_CORRENTE
        })
    # Verificar backups também
    for f in sorted(BACKUPS_DIR.glob("notas_fiscais_*.db")):
        ano = f.stem.replace("notas_fiscais_", "")
        dbs.append({
            "ano": int(ano),
            "arquivo": str(f),
            "tamanho_mb": round(f.stat().st_size / (1024 * 1024), 2),
            "corrente": False
        })
    return dbs

# === Servidor ===
HOST = "0.0.0.0"
PORT = 8050
APP_TITLE = "Controle de Notas Fiscais"
APP_VERSION = "1.0.0"

def get_local_ip() -> str:
    """Descobre o IP local para acesso em rede."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

# === Empresas do Grupo Emalto (dados fixos) ===
EMPRESAS_GRUPO = [
    {"sigla": "EIM", "nome_completo": "Emalto Indústria Mecânica"},
    {"sigla": "EEM", "nome_completo": "Emalto Estruturas Metálicas"},
    {"sigla": "EEN", "nome_completo": "Emalto Energia"},
    {"sigla": "Fundação", "nome_completo": "Fundação Emalto"},
    {"sigla": "Torque Diesel", "nome_completo": "Torque Diesel"},
    {"sigla": "Torque Diesel Filial", "nome_completo": "Torque Diesel - Filial"},
    {"sigla": "Torque Grill", "nome_completo": "Torque Grill"},
    {"sigla": "Torque Pneus", "nome_completo": "Torque Pneus"},
    {"sigla": "Agronegócios", "nome_completo": "Emalto Agronegócios"},
]

# === Fornecedores de Software Mensal (dados fixos) ===
FORNECEDORES_MENSAIS = [
    {"nome": "KTREE", "categoria": "SOFTWARE_MENSAL", "descricao": "Serviço de E-mail"},
    {"nome": "TOTVS - MICROSIGA", "categoria": "SOFTWARE_MENSAL", "descricao": "ERP Microsiga"},
    {"nome": "TOTVS - SOLUÇÕES", "categoria": "SOFTWARE_MENSAL", "descricao": "TOTVS Soluções"},
    {"nome": "TOTVS - LARGE ENTERPRISE", "categoria": "SOFTWARE_MENSAL", "descricao": "TOTVS Large Enterprise"},
    {"nome": "JUNSOFT", "categoria": "SOFTWARE_MENSAL", "descricao": "Sistema Junsoft"},
    {"nome": "SYSAID", "categoria": "SOFTWARE_MENSAL", "descricao": "Help Desk SysAid"},
    {"nome": "VERO", "categoria": "SOFTWARE_MENSAL", "descricao": "Internet Vero"},
    {"nome": "VIVO", "categoria": "SOFTWARE_MENSAL", "descricao": "Telefonia Vivo"},
    {"nome": "INTERPONTO", "categoria": "SOFTWARE_MENSAL", "descricao": "Controle de Ponto"},
    {"nome": "NETSOL", "categoria": "SOFTWARE_MENSAL", "descricao": "Soluções de Rede"},
    {"nome": "MAK SOLUTIONS", "categoria": "SOFTWARE_MENSAL", "descricao": "MAK Solutions"},
    {"nome": "STARLINK", "categoria": "SOFTWARE_MENSAL", "descricao": "Internet Starlink"},
    {"nome": "GOOGLE CLOUD", "categoria": "SOFTWARE_MENSAL", "descricao": "Google Cloud Platform"},
    {"nome": "WEBPOSTO", "categoria": "SOFTWARE_MENSAL", "descricao": "Sistema WebPosto"},
]

# Fornecedores avulsos (aparecem na planilha mas não são mensais)
FORNECEDORES_AVULSOS = [
    "LOJA ELÉTRICA", "REGISTRO.BR", "DIGITRON", "FULL SERVICE",
    "GENIUS", "GKM SYSTEM", "INGRAM", "IPAPRINT", "M3CORP",
    "MODESTO", "TELCOM", "USIMICRO", "WEBBEAGÁ", "ALIANÇA TECNOLOGIA",
]
