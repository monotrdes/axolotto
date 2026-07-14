<#
.SYNOPSIS
    Despliega Axolotto en el servidor de producción (192.168.100.15).
.DESCRIPTION
    Este script permite automatizar el despliegue al servidor de producción.
    Soporta dos flujos:
      1. Git-based Deploy (Recomendado): Realiza push local, hace pull en el servidor y compila/reinicia el frontend/backend.
      2. Hot-fix Deploy (Directo): Sube archivos específicos editados localmente usando SCP y luego reconstruye en el servidor.
.EXAMPLE
    .\scripts\deploy_production.ps1 -Mode Git
    .\scripts\deploy_production.ps1 -Mode HotFix -Files "frontend/app/page.tsx"
#>

param(
    [ValidateSet("Git", "HotFix")]
    [string]$Mode = "Git",

    [string[]]$Files = @("frontend/app/page.tsx")
)

$ErrorActionPreference = "Stop"

$Server = "192.168.100.15"
$User = "monotr"
$RemoteDir = "/home/monotr/axolotto"
$ProductionUrl = "https://www.axolot.to"

Write-Host "=============================================================="
Write-Host "  Axolotto - Despliegue a Producción ($Server)"
Write-Host "=============================================================="
Write-Host "URL de producción: $ProductionUrl"
Write-Host ""

# -- 1. Verificar conectividad SSH -----------------------------------------
Write-Host "[check] Verificando conexión SSH..."
try {
    $remoteHost = & ssh "${User}@${Server}" "hostname" 2>$null
    if ($LASTEXITCODE -ne 0 -or -not $remoteHost) {
        throw "No se pudo establecer conexión SSH con ${User}@${Server}"
    }
    Write-Host "   [OK] Conectado a: $remoteHost"
}
catch {
    Write-Host "   [FAIL] SSH falló. Asegúrate de tener tu llave SSH cargada y configurada." -ForegroundColor Red
    exit 1
}

# -- 2. Flujo Git -----------------------------------------------------------
if ($Mode -eq "Git") {
    Write-Host ""
    Write-Host "[git] Iniciando despliegue basado en Git..."
    
    # Obtener rama actual
    $branch = (git branch --show-current).Trim()
    Write-Host "   Rama local actual: $branch"

    # Verificar cambios locales sin commitear
    $status = (git status --short)
    if ($status) {
        Write-Host "   [WARN] Tienes cambios locales sin commitear:" -ForegroundColor Yellow
        $status | ForEach-Object { Write-Host "     $_" -ForegroundColor Gray }
        
        $choice = Read-Host "   ¿Deseas commitear y subir estos cambios automáticamente? (S/N)"
        if ($choice -eq "S" -or $choice -eq "s") {
            $msg = Read-Host "   Ingresa el mensaje del commit"
            if (-not $msg) { $msg = "deploy: auto-commit antes de deploy" }
            git add -A
            git commit -m $msg
            Write-Host "   [OK] Cambios commiteados localmente." -ForegroundColor Green
        } else {
            Write-Host "   [ABORT] Cancela el despliegue para limpiar o hacer commit manualmente." -ForegroundColor Red
            exit 1
        }
    }

    # Push a GitHub
    Write-Host "   Subiendo rama '$branch' a origin..."
    git push origin $branch
    if ($LASTEXITCODE -ne 0) {
        Write-Host "   [FAIL] Error al hacer git push" -ForegroundColor Red
        exit 1
    }
    Write-Host "   [OK] Push completado." -ForegroundColor Green

    # Pull y despliegue en servidor
    Write-Host "   Actualizando código en el servidor e iniciando compilación..."
    $sshCmd = "cd $RemoteDir && git fetch origin && git checkout $branch && git pull origin $branch && cd frontend && npm install && npm run build && pm2 delete axolotto-frontend 2>/dev/null; pm2 start npm --name axolotto-frontend -- start"
    
    Write-Host "   Ejecutando comandos remotos en el servidor..." -ForegroundColor Gray
    & ssh "${User}@${Server}" $sshCmd
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "   [FAIL] El despliegue o la compilación falló en el servidor." -ForegroundColor Red
        exit 1
    }
    
    Write-Host "   [OK] Despliegue completado con éxito en el servidor." -ForegroundColor Green
}

# -- 3. Flujo HotFix --------------------------------------------------------
elseif ($Mode -eq "HotFix") {
    Write-Host ""
    Write-Host "[hotfix] Iniciando copia directa de archivos vía SCP..."
    
    if ($Files.Count -eq 0) {
        Write-Host "   [FAIL] Debes especificar al menos un archivo en -Files." -ForegroundColor Red
        exit 1
    }

    foreach ($file in $Files) {
        if (-not (Test-Path $file)) {
            Write-Host "   [FAIL] El archivo local no existe: $file" -ForegroundColor Red
            exit 1
        }
        
        # Convertir ruta a formato Unix para el destino
        $remoteFile = "$RemoteDir/" + $file.Replace("\", "/")
        Write-Host "   Copiando $file -> $remoteFile"
        
        # Ejecutar SCP
        & scp $file "${User}@${Server}:${remoteFile}"
        if ($LASTEXITCODE -ne 0) {
            Write-Host "   [FAIL] Falló la transferencia de $file" -ForegroundColor Red
            exit 1
        }
    }
    
    Write-Host "   [OK] Archivos transferidos con éxito." -ForegroundColor Green

    # Recompilar y reiniciar frontend en el servidor
    Write-Host "   Recompilando frontend en el servidor..."
    $sshCmd = "cd $RemoteDir/frontend && npm run build && pm2 delete axolotto-frontend 2>/dev/null; pm2 start npm --name axolotto-frontend -- start"
    
    & ssh "${User}@${Server}" $sshCmd
    if ($LASTEXITCODE -ne 0) {
        Write-Host "   [FAIL] Falló la reconstrucción del frontend en el servidor." -ForegroundColor Red
        exit 1
    }
    
    Write-Host "   [OK] HotFix aplicado y frontend reiniciado con éxito." -ForegroundColor Green
}

Write-Host ""
Write-Host "=============================================================="
Write-Host "  [OK] Despliegue finalizado!"
Write-Host "  Visita: $ProductionUrl"
Write-Host "=============================================================="
