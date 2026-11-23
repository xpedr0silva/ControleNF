"""
Sistema de Controle de Notas Fiscais - Grupo Emalto
FastAPI Application
"""
import sys
import os
from pathlib import Path
from contextlib import asynccontextmanager

# Garantir que o diretório do backend esteja no path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from config import HOST, PORT, APP_TITLE, APP_VERSION, get_local_ip, FRONTEND_DIR
from database import create_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Eventos de startup e shutdown."""
    # Startup
    print(f"\n{'='*60}")
    print(f"  {APP_TITLE} v{APP_VERSION}")
    print(f"{'='*60}")
    create_tables()
    
    # Rodar seed de dados iniciais se banco estiver vazio
    from seed_data import seed_if_empty
    seed_if_empty()
    
    ip = get_local_ip()
    print(f"\n  Acesso Local:  http://localhost:{PORT}")
    print(f"  Acesso Rede:   http://{ip}:{PORT}")
    print(f"{'='*60}\n")
    
    yield
    
    # Shutdown
    print("\n[INFO] Sistema encerrado.")


app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    lifespan=lifespan,
)

# CORS para acesso em rede
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers
from routers.empresas import router as empresas_router
from routers.fornecedores import router as fornecedores_router
from routers.notas_fiscais import router as notas_router
from routers.cadastros import router as cadastros_router
from routers.contratos import router as contratos_router
from routers.dashboard import router as dashboard_router
from routers.exportacao import router as exportacao_router

app.include_router(empresas_router)
app.include_router(fornecedores_router)
app.include_router(notas_router)
app.include_router(contratos_router)
app.include_router(cadastros_router)
app.include_router(dashboard_router)
app.include_router(exportacao_router)

# Servir frontend estático
if FRONTEND_DIR.exists():
    for subdir in ["assets", "css", "js"]:
        path = FRONTEND_DIR / subdir
        if path.exists():
            app.mount(f"/{subdir}", StaticFiles(directory=str(path)), name=subdir)


@app.get("/")
def serve_frontend():
    """Servir o frontend SPA."""
    index = FRONTEND_DIR / "index.html"
    if index.exists():
        return FileResponse(str(index))
    return {"message": f"{APP_TITLE} API - Frontend não encontrado"}


@app.get("/api/health")
def health_check():
    return {"status": "ok", "version": APP_VERSION}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=HOST, port=PORT, reload=False)
