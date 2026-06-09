<#
.SYNOPSIS
    Despliega contratos Axolotto en Anvil local (Windows-native, forge via Docker).
.DESCRIPTION
    Usa la imagen ghcr.io/foundry-rs/foundry:latest para compilar y desplegar
    los contratos al contenedor Anvil corriendo en localhost:8545.
    Actualiza backend/.env y frontend/env.local con las direcciones desplegadas.

    Requiere: Docker Desktop corriendo, Anvil accesible en localhost:8545.
.EXAMPLE
    .\scripts\deploy_local.ps1
#>

$ErrorActionPreference = "Stop"

$ScriptDir = $PSScriptRoot
$Root = Split-Path $ScriptDir -Parent
$ContractsDir = Join-Path $Root "contracts"
$BackendEnv = Join-Path $Root "backend\.env"
$FrontendEnv = Join-Path $Root "frontend\env.local"
$DeployerKey = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
$DeployerAddr = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
$FoundryImage = "ghcr.io/foundry-rs/foundry:latest"
# host.docker.internal funciona en Docker Desktop for Windows.
# Si usas otro runtime, cambia a la IP del host o usa --network axolotto_net.
$RpcUrl = "http://host.docker.internal:8545"

function Update-OrAddEnv {
    param([string]$Key, [string]$Value, [string]$File)
    $lines = if (Test-Path $File) { Get-Content $File } else { @() }
    $found = $false
    $newLines = $lines | ForEach-Object {
        if ($_ -match "^${Key}=") {
            $found = $true
            "${Key}=${Value}"
        }
        else {
            $_
        }
    }
    if (-not $found) {
        $newLines += "${Key}=${Value}"
    }
    $newLines -join "`n" | Set-Content $File -Encoding UTF8 -NoNewline
}

# Extrae una direccion del output de forge (formato: DEPLOYED_NAME=0x...)
function Extract-Addr {
    param([string]$Name)
    $match = $global:DeployOutput | Select-String -Pattern "DEPLOYED_${Name}=(0x[a-fA-F0-9]+)" | Select-Object -First 1
    if ($match) {
        $match.Matches.Groups[1].Value
    }
    else {
        $null
    }
}

Write-Host "=============================================================="
Write-Host "  Axolotto - Deploy Local (Windows + Docker Forge)"
Write-Host "=============================================================="

# -- 1. Verificar que Anvil responde --------------------------------------

Write-Host ""
Write-Host "[chain] Verificando Anvil en localhost:8545..."
try {
    $body = '{"jsonrpc":"2.0","method":"eth_chainId","params":[],"id":1}'
    $null = Invoke-WebRequest -Uri "http://localhost:8545" -Method POST -Body $body `
        -ContentType "application/json" -TimeoutSec 5 -UseBasicParsing
    Write-Host "   [OK] Anvil responde"
}
catch {
    Write-Host "   [FAIL] Anvil no responde en localhost:8545" -ForegroundColor Red
    Write-Host ""
    Write-Host "   Asegurate de que Docker Desktop esta corriendo y ejecuta:"
    Write-Host "     docker compose up -d db_axolotto anvil_axolotto"
    exit 1
}

# -- 2. Compilar contratos -------------------------------------------------

Write-Host ""
Write-Host "[clean] Limpiando artifacts stale..."
docker run --rm `
    -v "${ContractsDir}:/app" `
    -w /app `
    $FoundryImage `
    "forge clean"
Write-Host "   [OK] Clean completado"

Write-Host ""
Write-Host "[build] Compilando contratos (forge via Docker)..."
docker run --rm `
    -v "${ContractsDir}:/app" `
    -w /app `
    $FoundryImage `
    "forge build"
if ($LASTEXITCODE -ne 0) {
    Write-Host "   [FAIL] Build fallo" -ForegroundColor Red
    exit 1
}
Write-Host "   [OK] Compilacion exitosa"

# -- 3. Desplegar contratos -------------------------------------------------

Write-Host ""
Write-Host "[deploy] Desplegando contratos en Anvil..."
$forgeCmd = "forge script script/Deploy.s.sol --rpc-url $RpcUrl --broadcast --private-key $DeployerKey"
$rawLines = & docker run --rm `
    -v "${ContractsDir}:/app" `
    -w /app `
    -e DEPLOYER_PRIVATE_KEY=$DeployerKey `
    -e METADATA_BASE_URL="http://localhost:8001/api/v1/metadata/" `
    $FoundryImage `
    $forgeCmd 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "   [FAIL] Deploy fallo" -ForegroundColor Red
    exit 1
}

$global:DeployOutput = $rawLines -join "`n"
Write-Host $global:DeployOutput

# -- 4. Extraer direcciones -------------------------------------------------

$GAL        = Extract-Addr "GAL"
$AXG        = Extract-Addr "AXG"
$WEBITOS    = Extract-Addr "WEBITOS"
$AXOLOTITOS = Extract-Addr "AXOLOTITOS"
$CARTAS     = Extract-Addr "CARTAS"
$BOOSTERS   = Extract-Addr "BOOSTERS"
$TABLAS     = Extract-Addr "TABLAS"
$CONSUMABLES = Extract-Addr "CONSUMABLES"
$CONTROLLER = Extract-Addr "GAME_CONTROLLER"

Write-Host ""
Write-Host "[addrs] Contratos desplegados:"
Write-Host "   GAL (ERC-20):          $GAL"
Write-Host "   AXG (ERC-20):          $AXG"
Write-Host "   Webitos (ERC-721):     $WEBITOS"
Write-Host "   Axolotitos (ERC-721):  $AXOLOTITOS"
Write-Host "   Cartas (ERC-1155):     $CARTAS"
Write-Host "   Boosters (ERC-1155):   $BOOSTERS"
Write-Host "   Tablas (ERC-721):      $TABLAS"
Write-Host "   Consumables (ERC-1155):$CONSUMABLES"
Write-Host "   GameController:        $CONTROLLER"

# -- 5. Actualizar backend/.env --------------------------------------------

Write-Host ""
Write-Host "[config] Actualizando $BackendEnv con direcciones de contratos locales..."

Update-OrAddEnv "BLOCKCHAIN_MODE"          "local"                       $BackendEnv
Update-OrAddEnv "ANVIL_RPC_URL"            "http://anvil_axolotto:8545"  $BackendEnv
Update-OrAddEnv "TREASURY_PRIVATE_KEY"     $DeployerKey                  $BackendEnv
Update-OrAddEnv "AXOGEMA_ADDRESS"          $AXG                          $BackendEnv
Update-OrAddEnv "GEMA_ALGA_ADDRESS"        $GAL                          $BackendEnv
Update-OrAddEnv "WEBITOS_ADDRESS"          $WEBITOS                      $BackendEnv
Update-OrAddEnv "AXOLOTITOS_ADDRESS"       $AXOLOTITOS                   $BackendEnv
Update-OrAddEnv "CARDS_ADDRESS"            $CARTAS                       $BackendEnv
Update-OrAddEnv "BOOSTERS_ADDRESS"         $BOOSTERS                     $BackendEnv
Update-OrAddEnv "TABLAS_ADDRESS"           $TABLAS                       $BackendEnv
Update-OrAddEnv "CONSUMABLES_ADDRESS"      $CONSUMABLES                  $BackendEnv
Update-OrAddEnv "GAME_CONTROLLER_ADDRESS"  $CONTROLLER                   $BackendEnv
Update-OrAddEnv "PLASMA_RPC_URL"           "http://anvil_axolotto:8545"  $BackendEnv

Write-Host "   [OK] Backend .env actualizado"

# -- 6. Actualizar frontend/env.local con las nuevas direcciones -----------

Write-Host ""
Write-Host "[config] Sincronizando direcciones de contratos a frontend/env.local..."

Update-OrAddEnv "NEXT_PUBLIC_GEMA_ALGA_ADDRESS"        $GAL                          $FrontendEnv
Update-OrAddEnv "NEXT_PUBLIC_AXOGEMA_ADDRESS"          $AXG                          $FrontendEnv
Update-OrAddEnv "NEXT_PUBLIC_WEBITOS_ADDRESS"          $WEBITOS                      $FrontendEnv
Update-OrAddEnv "NEXT_PUBLIC_GAME_CONTROLLER_ADDRESS"  $CONTROLLER                   $FrontendEnv
# RPC y Chain ID se mantienen sin cambios (Anvil local = 127.0.0.1:8545, chain 31337)

Write-Host "   [OK] Frontend env.local actualizado con nuevas direcciones"

Write-Host ""
Write-Host "=============================================================="
Write-Host "  [OK] Deploy completo!"
Write-Host "=============================================================="
