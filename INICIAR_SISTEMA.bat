@echo off
chcp 65001 >nul
title Controle de Notas Fiscais - Grupo Emalto

echo.
echo  ====================================================
echo   Controle de Notas Fiscais - Grupo Emalto
echo  ====================================================
echo.

:: Navegar para a pasta backend usando pushd para suportar caminhos UNC e caminhos de rede mapeados
pushd "%~dp0backend"

:: Verificar se o venv existe
if not exist "venv\Scripts\activate.bat" (
    echo  [SETUP] Criando ambiente virtual...
    py -3.10 -m venv venv 2>nul
    if errorlevel 1 (
        python -m venv venv
    )
    call venv\Scripts\activate.bat
    echo  [SETUP] Instalando dependencias...
    python -m pip install --upgrade pip
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

echo  [INFO] Iniciando servidor...
echo.
python main.py

:: Restaurar o diretório de trabalho anterior e desmapear o drive temporário do pushd se necessário
popd

pause
