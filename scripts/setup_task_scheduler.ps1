# =============================================
# Configuração do Task Scheduler para Notificações
# Execute como Administrador
# =============================================

$ScriptPath = Join-Path $PSScriptRoot "notificacao_diaria.py"

# Tentar usar o python do venv se ele existir
$VenvPython = Join-Path $PSScriptRoot "..\backend\venv\Scripts\python.exe"
if (Test-Path $VenvPython) {
    $PythonPath = (Get-Item $VenvPython).FullName
} else {
    $PythonPath = (Get-Command python -ErrorAction SilentlyContinue).Source
}

if (-not $PythonPath) {
    Write-Host "ERRO: Python nao encontrado no PATH nem no venv" -ForegroundColor Red
    exit 1
}

Write-Host "Configurando Task Scheduler..." -ForegroundColor Cyan
Write-Host "  Python: $PythonPath" -ForegroundColor Gray
Write-Host "  Script: $ScriptPath" -ForegroundColor Gray

# Remover tarefa existente se houver
Unregister-ScheduledTask -TaskName "ControleNF_Notificacao" -Confirm:$false -ErrorAction SilentlyContinue

# Ação: executar o script Python
$Action = New-ScheduledTaskAction -Execute $PythonPath -Argument $ScriptPath

# Trigger 1: Diariamente às 07:00
$TriggerDaily = New-ScheduledTaskTrigger -Daily -At "07:00"

# Trigger 2: No logon do usuário
$TriggerLogon = New-ScheduledTaskTrigger -AtLogon

# Configurações
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# Registrar
Register-ScheduledTask `
    -TaskName "ControleNF_Notificacao" `
    -Action $Action `
    -Trigger $TriggerDaily, $TriggerLogon `
    -Settings $Settings `
    -Description "Notificacao diaria de NFs pendentes - ControleNF" `
    -RunLevel Limited

Write-Host ""
Write-Host "Task criada com sucesso!" -ForegroundColor Green
Write-Host "  Nome: ControleNF_Notificacao" -ForegroundColor Gray
Write-Host "  Horario: 07:00 diariamente + ao fazer logon" -ForegroundColor Gray
Write-Host ""
