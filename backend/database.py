"""
Configuração do banco de dados SQLite com SQLAlchemy.
Suporta múltiplos bancos (rotação anual).
"""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from contextlib import contextmanager
from config import DATABASE_URL, get_database_url

# Engine principal (ano corrente)
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

# Habilitar WAL mode e foreign keys para melhor performance e integridade
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA busy_timeout=5000")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """Dependency para injetar sessão do banco no FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_for_year(ano: int):
    """Cria engine e session para um ano específico (consulta de backups)."""
    url = get_database_url(ano)
    eng = create_engine(url, connect_args={"check_same_thread": False})

    @event.listens_for(eng, "connect")
    def set_pragma(dbapi_conn, conn_rec):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Session = sessionmaker(autocommit=False, autoflush=False, bind=eng)
    return Session


def create_tables():
    """Cria todas as tabelas no banco do ano corrente."""
    from models import (
        EmpresaGrupo, Fornecedor, ContratoSoftware,
        LancamentoMensal, NotaFiscal, Configuracao, FornecedorEmpresaIdentificador
    )
    Base.metadata.create_all(bind=engine)
    print(f"[DB] Tabelas criadas com sucesso em {DATABASE_URL}")


def create_tables_for_year(ano: int):
    """Cria todas as tabelas em um banco de ano específico."""
    url = get_database_url(ano)
    eng = create_engine(url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=eng)
    print(f"[DB] Tabelas criadas para o ano {ano}")
    return eng
