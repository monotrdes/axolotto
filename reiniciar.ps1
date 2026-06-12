<#
.SYNOPSIS
    Reinicia el ecosistema Axolotto (100% Windows-native, sin WSL).
.DESCRIPTION
    Docker Desktop, PM2 y Foundry (vía Docker) corren nativo en Windows.
    Taskboard NO se reinicia con "axo".

.PARAMETER Target
    "axo" = backend + frontend + DB + Anvil + contratos (default)
    "task" = solo taskboard
    "all" = todo incluyendo taskboard
    "frontend" = solo frontend (build + PM2 restart)
.EXAMPLE
    .\reiniciar.ps1 axo
    .\reiniciar.ps1 all
#>

param(
    [ValidateSet("axo", "task", "all", "frontend")]
    [string]$Target = "axo"
)

$ErrorActionPreference = "Continue"

function Write-Step {
    param([string]$Message)
    Write-Host $Message -ForegroundColor Cyan
}

# ── Restart Taskboard ────────────────────────────────────────────────

function Restart-Taskboard {
    Write-Step "Taskboard..."
    $existing = Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -like "*taskboard*" }
    if ($existing) { $existing | Stop-Process -Force }
    $portPid = (Get-NetTCPConnection -LocalPort 8181 -ErrorAction SilentlyContinue).OwningProcess
    foreach ($p in $portPid) { Stop-Process -Id $p -Force -ErrorAction SilentlyContinue }
    Start-Sleep 1
    $scriptPath = Join-Path $PSScriptRoot "tools\taskboard\server.py"
    Start-Process python -ArgumentList $scriptPath -WindowStyle Normal
    Write-Host "  Taskboard -> http://localhost:8181" -ForegroundColor Green
}

# ── Deploy contratos ─────────────────────────────────────────────────

function Invoke-Deploy {
    Write-Step "Contratos (forge via Docker)..."
    $deployScript = Join-Path $PSScriptRoot "scripts\deploy_local.ps1"
    & powershell -ExecutionPolicy Bypass -File $deployScript
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  WARNING: Deploy fallo (codigo $LASTEXITCODE)" -ForegroundColor Red
    }
}

# ── Restart Axolotto Stack ───────────────────────────────────────────

function Restart-Axo {
    # Verificar que Docker Desktop está corriendo
    $dockerOk = docker info 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ERROR: Docker Desktop no esta corriendo." -ForegroundColor Red
        Write-Host "  Inicia Docker Desktop y vuelve a intentar." -ForegroundColor Yellow
        return
    }

    Write-Step "Deteniendo contenedores..."
    docker compose down 2>$null
    docker rm -f axolotto_backend axolotto_db axolotto_anvil 2>$null
    Write-Host "  Listo"

    Write-Step "Liberando puerto 8545..."
    $p8545 = (Get-NetTCPConnection -LocalPort 8545 -ErrorAction SilentlyContinue).OwningProcess
    foreach ($p in $p8545) { Stop-Process -Id $p -Force -ErrorAction SilentlyContinue }
    Write-Host "  Listo"

    Write-Step "DB + Anvil..."
    docker compose up -d db_axolotto anvil_axolotto
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ERROR: No se pudo levantar DB + Anvil" -ForegroundColor Red
        return
    }

    Write-Step "Esperando Anvil (4s)..."
    Start-Sleep 4

    Invoke-Deploy

    Write-Step "Backend..."
    docker compose up -d --build backend_axolotto
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  WARNING: No se pudo compilar/reconstruir el backend (sin conexion / proxy Docker?). Intentando iniciar con la imagen local..." -ForegroundColor Yellow
        docker compose up -d backend_axolotto
        if ($LASTEXITCODE -ne 0) {
            Write-Host "  ERROR: No se pudo levantar el backend" -ForegroundColor Red
            return
        }
    }

    Write-Step "Frontend..."
    Push-Location (Join-Path $PSScriptRoot "frontend")
    try {
        Write-Host "  Instalando dependencias..."
        npm install 2>&1 | Select-Object -Last 5
        Write-Host "  Build..."
        $buildResult = npx next build 2>&1
        $buildResult | Select-Object -Last 15
        if ($LASTEXITCODE -ne 0) {
            Write-Host "  ERROR: Build fallo (codigo $LASTEXITCODE)" -ForegroundColor Red
            Write-Host "  Ultimas 30 lineas del build:"
            $buildResult | Select-Object -Last 30
            return
        }
        pm2 delete axolotto-frontend 2>$null
        pm2 start ecosystem.config.js
        Start-Sleep 2
        $pm2Status = pm2 list 2>&1 | Select-String "axolotto-frontend"
        if ($pm2Status) {
            Write-Host "  PM2 status: $pm2Status" -ForegroundColor Gray
        }
    }
    finally {
        Pop-Location
    }

    Write-Host ""
    Write-Host "Backend  -> http://localhost:8001" -ForegroundColor Green
    Write-Host "Frontend -> http://localhost:3000" -ForegroundColor Green
    Write-Host "Anvil    -> http://localhost:8545" -ForegroundColor Green
}

# ── Docker health check helper ────────────────────────────────────────

function Test-DockerReady {
    $null = docker info 2>$null
    return ($LASTEXITCODE -eq 0)
}

# ── Restart Frontend Only ─────────────────────────────────────────────

function Restart-Frontend {
    Write-Step "Frontend..."
    Push-Location (Join-Path $PSScriptRoot "frontend")
    try {
        Write-Host "  Instalando dependencias..."
        npm install 2>&1 | Select-Object -Last 5
        Write-Host "  Build..."
        $buildResult = npx next build 2>&1
        $buildResult | Select-Object -Last 15
        if ($LASTEXITCODE -ne 0) {
            Write-Host "  ERROR: Build fallo (codigo $LASTEXITCODE)" -ForegroundColor Red
            Write-Host "  Ultimas 30 lineas del build:"
            $buildResult | Select-Object -Last 30
            return
        }
        pm2 delete axolotto-frontend 2>$null
        pm2 start ecosystem.config.js
        Start-Sleep 2
        $pm2Status = pm2 list 2>&1 | Select-String "axolotto-frontend"
        if ($pm2Status) {
            Write-Host "  PM2 status: $pm2Status" -ForegroundColor Gray
        }
    }
    finally {
        Pop-Location
    }
    Write-Host "Frontend -> http://localhost:3000" -ForegroundColor Green
}

# ── Main ──────────────────────────────────────────────────────────────

switch ($Target) {
    "task"     { Restart-Taskboard }
    "frontend" { Restart-Frontend }
    "axo"      { Restart-Axo }
    "all"      {
        Restart-Axo
        Write-Host ""
        Restart-Taskboard
    }
}
