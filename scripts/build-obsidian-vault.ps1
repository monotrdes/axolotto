<#
.SYNOPSIS
    Build a clean Obsidian vault with only relevant project files:
    player wiki + dev docs + GDD + source code (no libraries).

.DESCRIPTION
    Copies selected files from the repo into obsidian/ folder to open
    as an Obsidian vault. Excludes node_modules, __pycache__, contract
    libraries (forge-std, openzeppelin), and task-specific plan files.

    Run after making changes to wiki/ or docs/ to update the vault.

.EXAMPLE
    .\scripts\build-obsidian-vault.ps1
#>

param(
    [string]$VaultPath = $null
)

$ErrorActionPreference = "Stop"
$repoRoot = $PSScriptRoot | Split-Path -Parent | Resolve-Path

if (-not $VaultPath) {
    $VaultPath = Join-Path $repoRoot "obsidian"
}
$vaultRoot = [System.IO.Path]::GetFullPath($VaultPath)

Write-Host "=============================================="
Write-Host "  Axolotto - Build Obsidian Vault"
Write-Host "=============================================="
Write-Host ('  Source: ' + $repoRoot)
Write-Host ('  Target: ' + $vaultRoot)
Write-Host ""

# --------------------------------------------------
# Helpers
# --------------------------------------------------
$global:copiedCount = 0
$global:skippedCount = 0

function Copy-File {
    param([string]$Src, [string]$RelDest)
    if (-not (Test-Path $Src -PathType Leaf)) { return }
    $dest = Join-Path $vaultRoot $RelDest
    $destDir = Split-Path $dest -Parent
    if (-not (Test-Path $destDir)) {
        New-Item -ItemType Directory -Force -Path $destDir | Out-Null
    }
    Copy-Item -Path $Src -Destination $dest -Force
    $global:copiedCount++
}

function Copy-Dir {
    param(
        [string]$SrcDir,
        [string]$RelDest,
        [string[]]$ExcludeDirs = @(),
        [string[]]$Extensions = @()
    )
    if (-not (Test-Path $SrcDir -PathType Container)) { return }

    $destDir = Join-Path $vaultRoot $RelDest
    if (-not (Test-Path $destDir)) {
        New-Item -ItemType Directory -Force -Path $destDir | Out-Null
    }

    $files = Get-ChildItem -Path $SrcDir -Recurse -File

    foreach ($f in $files) {
        # Skip excluded directories
        $skip = $false
        foreach ($ex in $ExcludeDirs) {
            if ($f.DirectoryName -match [regex]::Escape($ex)) {
                $global:skippedCount++
                $skip = $true
                break
            }
        }
        if ($skip) { continue }

        # Filter by extension
        if ($Extensions.Count -gt 0) {
            if ($f.Extension -notin $Extensions) {
                $global:skippedCount++
                continue
            }
        }

        $rel = $f.FullName.Substring($SrcDir.Length).TrimStart('\', '/')
        $dest = Join-Path $destDir $rel
        $destParentDir = Split-Path $dest -Parent
        if (-not (Test-Path $destParentDir)) {
            New-Item -ItemType Directory -Force -Path $destParentDir | Out-Null
        }
        Copy-Item -Path $f.FullName -Destination $dest -Force
        $global:copiedCount++
    }
}

# --------------------------------------------------
# 1. Clean previous vault
# --------------------------------------------------
Write-Host "[1/7] Cleaning previous vault..."
if (Test-Path $vaultRoot) {
    Get-ChildItem -Path $vaultRoot -Exclude ".obsidian" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
} else {
    New-Item -ItemType Directory -Force -Path $vaultRoot | Out-Null
}

# --------------------------------------------------
# 2. Wiki (all markdown files)
# --------------------------------------------------
Write-Host "[2/7] Copying wiki/ (player guides + architecture + API)..."
$wikiSrc = Join-Path $repoRoot "wiki"
Copy-Dir -SrcDir $wikiSrc -RelDest "wiki" -ExcludeDirs @(".obsidian", "axolotto-wiki") -Extensions @(".md")

# --------------------------------------------------
# 3. Docs (GDD, bible, active plans)
# --------------------------------------------------
Write-Host "[3/7] Copying docs/ (GDD + design bible + active plans)..."

$keyDocs = @(
    @{Src="docs\completed\GDD.md";                  Dest="docs\GDD.md"},
    @{Src="docs\completed\AXOLOTTO_BIBLE.md";       Dest="docs\AXOLOTTO_BIBLE.md"},
    @{Src="docs\completed\vip_club_design.md";      Dest="docs\vip_club_design.md"},
    @{Src="docs\completed\SECURITY.md";             Dest="docs\SECURITY.md"},
    @{Src="docs\completed\SECURITY_AUDIT_2026_06_04.md"; Dest="docs\SECURITY_AUDIT_2026_06_04.md"},
    @{Src="docs\completed\MATRIZ_TRANSACCIONES_Y_REPARTOS.md"; Dest="docs\MATRIZ_TRANSACCIONES_Y_REPARTOS.md"},
    @{Src="docs\docs_review_and_status.md";         Dest="docs\docs_review_and_status.md"},
    @{Src="docs\000_PLAN_GLOBAL_PENDIENTES.md";     Dest="docs\000_PLAN_GLOBAL_PENDIENTES.md"},
    @{Src="docs\MASTER_PLAN_CRIADERO.md";           Dest="docs\MASTER_PLAN_CRIADERO.md"}
)
foreach ($doc in $keyDocs) {
    Copy-File -Src (Join-Path $repoRoot $doc.Src) -RelDest $doc.Dest
}

# Active plans from docs/ root
$docsRoot = Join-Path $repoRoot "docs"
$plans = Get-ChildItem -Path $docsRoot -Filter "plan_*.md" -File -ErrorAction SilentlyContinue
foreach ($plan in $plans) {
    if ($plan.Name -notmatch "^plan_task-") {
        Copy-File -Src $plan.FullName -RelDest ('docs\planes\' + $plan.Name)
    }
}

# --------------------------------------------------
# 4. Backend source: backend/app/
# --------------------------------------------------
Write-Host "[4/7] Copying backend/app/ (Python source)..."
$backendSrc = Join-Path $repoRoot "backend\app"
Copy-Dir -SrcDir $backendSrc -RelDest "backend\app" -ExcludeDirs @("__pycache__", ".pytest_cache")

# --------------------------------------------------
# 5. Frontend source: key directories
# --------------------------------------------------
Write-Host "[5/7] Copying frontend/ (TypeScript + React source)..."
$frontendRoot = Join-Path $repoRoot "frontend"
$feDirs = @("app", "components", "hooks", "lib", "types", "public", "styles", "config")
foreach ($dir in $feDirs) {
    $src = Join-Path $frontendRoot $dir
    if (Test-Path $src) {
        Copy-Dir -SrcDir $src -RelDest ('frontend\' + $dir) -ExcludeDirs @("node_modules", ".next")
    }
}
# Frontend config files
$feConfigs = @("package.json", "tsconfig.json", "tailwind.config.ts", "next.config.ts", "postcss.config.mjs")
foreach ($f in $feConfigs) {
    Copy-File -Src (Join-Path $frontendRoot $f) -RelDest ('frontend\' + $f)
}

# --------------------------------------------------
# 6. Contracts source: only src/
# --------------------------------------------------
Write-Host "[6/7] Copying contracts/src/ (Solidity contracts)..."
$contractsSrc = Join-Path $repoRoot "contracts\src"
Copy-Dir -SrcDir $contractsSrc -RelDest "contracts\src"

# Contract config files
$cConfigs = @("foundry.toml", "README.md")
foreach ($f in $cConfigs) {
    Copy-File -Src (Join-Path $repoRoot ('contracts\' + $f)) -RelDest ('contracts\' + $f)
}

# --------------------------------------------------
# 7. Root .md files + generate 00-HOME.md
# --------------------------------------------------
Write-Host "[7/7] Copying root files + generating 00-HOME.md..."

Copy-File -Src (Join-Path $repoRoot "CLAUDE.md") -RelDest "CLAUDE.md"
Copy-File -Src (Join-Path $repoRoot "HANDOFF_ANTIGRAVITY.md") -RelDest "HANDOFF_ANTIGRAVITY.md"

# Generate 00-HOME.md
$now = Get-Date -Format "yyyy-MM-dd HH:mm"
$sb = New-Object System.Text.StringBuilder

[void]$sb.AppendLine('---')
[void]$sb.AppendLine('tags: [home, index, moc]')
[void]$sb.AppendLine('created: "' + $now + '"')
[void]$sb.AppendLine('generated_by: "scripts/build-obsidian-vault.ps1"')
[void]$sb.AppendLine('---')
[void]$sb.AppendLine('')
[void]$sb.AppendLine('# Axolotto - Vault de Desarrollo')
[void]$sb.AppendLine('')
[void]$sb.AppendLine('> **Mapa de Conocimiento:** Wiki de Jugador + Documentacion Tecnica + Codigo Fuente')
[void]$sb.AppendLine('> Generado: ' + $now + ' | Regenerar: `.\scripts\build-obsidian-vault.ps1`')
[void]$sb.AppendLine('')
[void]$sb.AppendLine('---')
[void]$sb.AppendLine('')
[void]$sb.AppendLine('## Rutas de Navegacion')
[void]$sb.AppendLine('')
[void]$sb.AppendLine('### Soy Jugador - Quiero entender el juego')
[void]$sb.AppendLine('Empieza aqui: [[wiki/conceptos/00-INDEX]]')
[void]$sb.AppendLine('- [[wiki/conceptos/01-bienvenido-a-xochimilco]]')
[void]$sb.AppendLine('- [[wiki/conceptos/02-axolotitos]]')
[void]$sb.AppendLine('- [[wiki/conceptos/06-como-jugar-loteria]]')
[void]$sb.AppendLine('- [[wiki/conceptos/12-economia-dual]]')
[void]$sb.AppendLine('- [[wiki/conceptos/25-f2p-guia-gratis]]')
[void]$sb.AppendLine('')
[void]$sb.AppendLine('### Soy Developer - Quiero entender la arquitectura')
[void]$sb.AppendLine('Empieza aqui: [[CLAUDE]]')
[void]$sb.AppendLine('- [[wiki/arquitectura/backend]]')
[void]$sb.AppendLine('- [[wiki/arquitectura/frontend]]')
[void]$sb.AppendLine('- [[wiki/arquitectura/contratos]]')
[void]$sb.AppendLine('- [[wiki/arquitectura/base_de_datos]]')
[void]$sb.AppendLine('- [[wiki/api/resumen_endpoints]]')
[void]$sb.AppendLine('')
[void]$sb.AppendLine('### Soy Game Designer - Quiero el GDD')
[void]$sb.AppendLine('- [[docs/GDD]] - Game Design Document completo')
[void]$sb.AppendLine('- [[docs/AXOLOTTO_BIBLE]] - Biblia de diseno del juego')
[void]$sb.AppendLine('- [[docs/vip_club_design]] - Diseno del sistema VIP')
[void]$sb.AppendLine('- [[wiki/mecanicas/patrones_ganadores]]')
[void]$sb.AppendLine('- [[wiki/economia/economia_general]]')
[void]$sb.AppendLine('')
[void]$sb.AppendLine('### Soy AI Agent - Necesito contexto rapido')
[void]$sb.AppendLine('- [[wiki/ai/QUICK_START]] - Onboarding en <400 tokens')
[void]$sb.AppendLine('- [[wiki/ai/critical_rules]] - Reglas que NUNCA romper')
[void]$sb.AppendLine('- [[wiki/ai/gotchas]] - Bugs y trampas conocidas')
[void]$sb.AppendLine('- [[wiki/ai/agent_routing]] - Que agente usar')
[void]$sb.AppendLine('- [[wiki/00-INDEX]] - Indice completo del wiki')
[void]$sb.AppendLine('')
[void]$sb.AppendLine('---')
[void]$sb.AppendLine('')
[void]$sb.AppendLine('## Estructura del Vault')
[void]$sb.AppendLine('')
[void]$sb.AppendLine('| Carpeta | Contenido | Tipo |')
[void]$sb.AppendLine('|----------|-----------|------|')
[void]$sb.AppendLine('| `wiki/` | Wiki completa: conceptos, mecanicas, economia, API, arquitectura | `.md` |')
[void]$sb.AppendLine('| `docs/` | GDD, biblia, planes activos, diseno VIP | `.md` |')
[void]$sb.AppendLine('| `backend/app/` | FastAPI: endpoints, servicios, modelos, schemas | `.py` |')
[void]$sb.AppendLine('| `frontend/` | Next.js: pages, componentes, hooks, lib | `.tsx .ts` |')
[void]$sb.AppendLine('| `contracts/src/` | Solidity: 14 contratos del juego | `.sol` |')
[void]$sb.AppendLine('| `CLAUDE.md` | Instrucciones para AI agents + stack reference | `.md` |')
[void]$sb.AppendLine('')
[void]$sb.AppendLine('---')
[void]$sb.AppendLine('')
[void]$sb.AppendLine('## Archivos Clave por Sistema')
[void]$sb.AppendLine('')
[void]$sb.AppendLine('### Economia y Monedas')
[void]$sb.AppendLine('- [[wiki/economia/monedas]] - AXF vs FRJ')
[void]$sb.AppendLine('- [[wiki/economia/tablas_precios]] - Precios de TODO')
[void]$sb.AppendLine('- [[wiki/economia/vip_tiers]] - Tiers VIP')
[void]$sb.AppendLine('- `backend/app/api/v1/endpoints/bank.py`')
[void]$sb.AppendLine('- `backend/app/services/bank_service.py`')
[void]$sb.AppendLine('- `contracts/src/Axoficha.sol`')
[void]$sb.AppendLine('- `contracts/src/Frijolito.sol`')
[void]$sb.AppendLine('')
[void]$sb.AppendLine('### Juego (Loteria)')
[void]$sb.AppendLine('- [[wiki/conceptos/06-como-jugar-loteria]]')
[void]$sb.AppendLine('- [[wiki/mecanicas/patrones_ganadores]]')
[void]$sb.AppendLine('- `backend/app/api/v1/endpoints/game.py`')
[void]$sb.AppendLine('- `backend/app/services/game_logic.py`')
[void]$sb.AppendLine('- `frontend/components/PlayMode.tsx`')
[void]$sb.AppendLine('- `frontend/components/ui/LoteriaBoard.tsx`')
[void]$sb.AppendLine('')
[void]$sb.AppendLine('### Axolotitos y Crianza')
[void]$sb.AppendLine('- [[wiki/conceptos/02-axolotitos]]')
[void]$sb.AppendLine('- [[wiki/conceptos/11-webitos-y-crianza]]')
[void]$sb.AppendLine('- [[wiki/mecanicas/estadisticas_axolotito]]')
[void]$sb.AppendLine('- [[wiki/mecanicas/incubacion_imprinting]]')
[void]$sb.AppendLine('- `backend/app/api/v1/endpoints/incubation.py`')
[void]$sb.AppendLine('- `contracts/src/Axolotitos.sol`')
[void]$sb.AppendLine('- `contracts/src/Webitos.sol`')
[void]$sb.AppendLine('')
[void]$sb.AppendLine('### Multijugador')
[void]$sb.AppendLine('- [[wiki/conceptos/23-salas-y-multijugador]]')
[void]$sb.AppendLine('- [[wiki/jugadores/multijugador]]')
[void]$sb.AppendLine('- `backend/app/api/v1/endpoints/multiplayer.py`')
[void]$sb.AppendLine('- `frontend/components/MultiplayerLobby.tsx`')
[void]$sb.AppendLine('')
[void]$sb.AppendLine('### Tienda y Mercado')
[void]$sb.AppendLine('- [[wiki/conceptos/13-tienda-y-tianguis]]')
[void]$sb.AppendLine('- [[wiki/conceptos/19-mercado-p2p]]')
[void]$sb.AppendLine('- [[wiki/mecanicas/gashapon]]')
[void]$sb.AppendLine('- `backend/app/api/v1/endpoints/shop.py`')
[void]$sb.AppendLine('- `backend/app/api/v1/endpoints/market.py`')
[void]$sb.AppendLine('- `frontend/components/Store.tsx`')
[void]$sb.AppendLine('- `frontend/components/MarketP2P.tsx`')
[void]$sb.AppendLine('')
[void]$sb.AppendLine('### Cueva y Decoracion')
[void]$sb.AppendLine('- [[wiki/conceptos/16-el-cenote-cueva]]')
[void]$sb.AppendLine('- [[wiki/conceptos/17-decoracion-de-cueva]]')
[void]$sb.AppendLine('- [[wiki/mecanicas/expansion_cueva]]')
[void]$sb.AppendLine('- [[wiki/mecanicas/staking]]')
[void]$sb.AppendLine('')
[void]$sb.AppendLine('### VIP y Recompensas')
[void]$sb.AppendLine('- [[wiki/conceptos/15-vip-club]]')
[void]$sb.AppendLine('- [[wiki/conceptos/21-ciclo-lunar-y-recompensas]]')
[void]$sb.AppendLine('- `backend/app/services/vip_scheduler.py`')
[void]$sb.AppendLine('- [[docs/vip_club_design]]')
[void]$sb.AppendLine('')
[void]$sb.AppendLine('---')
[void]$sb.AppendLine('')
[void]$sb.AppendLine('## Tags Globales')
[void]$sb.AppendLine('')
[void]$sb.AppendLine('| Tag | Tema |')
[void]$sb.AppendLine('|-----|------|')
[void]$sb.AppendLine('| `#mecanica` | Mecanicas de juego |')
[void]$sb.AppendLine('| `#economia` | Economia, monedas, precios |')
[void]$sb.AppendLine('| `#jugador` | Guias para jugadores |')
[void]$sb.AppendLine('| `#dev` | Documentacion tecnica |')
[void]$sb.AppendLine('| `#api` | Endpoints y servicios |')
[void]$sb.AppendLine('| `#ai` | Instrucciones para AI agents |')
[void]$sb.AppendLine('| `#plan` | Planes y roadmap |')
[void]$sb.AppendLine('| `#index` | Indices y MOCs |')

$homeContent = $sb.ToString()
$homePath = Join-Path $vaultRoot "00-HOME.md"
[System.IO.File]::WriteAllText($homePath, $homeContent, [System.Text.UTF8Encoding]::new($false))

# --------------------------------------------------
# .obsidian config
# --------------------------------------------------
$obsConfigDir = Join-Path $vaultRoot ".obsidian"
if (-not (Test-Path $obsConfigDir)) {
    New-Item -ItemType Directory -Force -Path $obsConfigDir | Out-Null
}

$appJsonPath = Join-Path $obsConfigDir "app.json"
if (-not (Test-Path $appJsonPath)) {
    $appConfig = @{
        newFileLocation = "folder"
        newFileFolderPath = "wiki"
        attachmentFolderPath = "assets"
        showUnsupportedFiles = $true
        alwaysUpdateLinks = $true
        defaultViewMode = "source"
        livePreview = $true
        showLineNumber = $false
        readableLineLength = $false
        promptDelete = $false
    }
    $appConfig | ConvertTo-Json -Depth 3 | Set-Content -Path $appJsonPath -Encoding UTF8
}

$graphJsonPath = Join-Path $obsConfigDir "graph.json"
if (-not (Test-Path $graphJsonPath)) {
    $graphConfig = @{
        search = ""
        showTags = $true
        showAttachments = $false
        hideUnresolved = $false
        showOrphans = $true
        collapseColorGroups = $true
        colorGroups = @()
        collapseDisplay = $true
        showArrow = $true
        textFadeMultiplier = -3.0
        nodeSizeMultiplier = 1.0
        lineSizeMultiplier = 2.5
        collapseForces = $true
        centerStrength = 0.5
        repelStrength = 13.0
        linkStrength = 1.0
        linkDistance = 370
        scale = 0.3
        close = $true
    }
    $graphConfig | ConvertTo-Json -Depth 3 | Set-Content -Path $graphJsonPath -Encoding UTF8
}

# --------------------------------------------------
# Summary
# --------------------------------------------------
$allFiles = @(Get-ChildItem -Path $vaultRoot -Recurse -File -ErrorAction SilentlyContinue)
$totalFiles = $allFiles.Count
$mdFiles = ($allFiles | Where-Object { $_.Extension -eq ".md" }).Count
$pyFiles = ($allFiles | Where-Object { $_.Extension -eq ".py" }).Count
$tsxFiles = ($allFiles | Where-Object { $_.Extension -eq ".tsx" }).Count
$tsFiles = ($allFiles | Where-Object { $_.Extension -eq ".ts" }).Count
$solFiles = ($allFiles | Where-Object { $_.Extension -eq ".sol" }).Count
$totalSize = ($allFiles | Measure-Object Length -Sum).Sum
$sizeMB = [math]::Round($totalSize / 1MB, 2)

Write-Host ""
Write-Host "==============================================" -ForegroundColor Green
Write-Host "  Vault Obsidian Generated Successfully" -ForegroundColor Green
Write-Host "==============================================" -ForegroundColor Green
Write-Host ('  Path      : ' + $vaultRoot) -ForegroundColor Cyan
Write-Host ('  Total     : ' + $totalFiles + ' files') -ForegroundColor White
Write-Host ('    .md     : ' + $mdFiles + ' (graph nodes)') -ForegroundColor White
Write-Host ('    .py     : ' + $pyFiles + ' (backend)') -ForegroundColor Gray
Write-Host ('    .tsx    : ' + $tsxFiles + ' (frontend components)') -ForegroundColor Gray
Write-Host ('    .ts     : ' + $tsFiles + ' (frontend logic)') -ForegroundColor Gray
Write-Host ('    .sol    : ' + $solFiles + ' (contracts)') -ForegroundColor Gray
Write-Host ('  Size      : ' + $sizeMB + ' MB') -ForegroundColor White
Write-Host ('  Skipped   : ' + $global:skippedCount + ' (libs, cache, etc)') -ForegroundColor DarkGray
Write-Host ""
Write-Host "  To use:" -ForegroundColor Yellow
Write-Host "    Obsidian -> Open folder as vault ->" -ForegroundColor Yellow
Write-Host ('    Select: ' + $vaultRoot) -ForegroundColor Cyan
Write-Host ""
