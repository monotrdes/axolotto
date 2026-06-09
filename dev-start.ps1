# dev-start.ps1 — Arranque unificado del ecosistema Axolotto + Agy
# Uso:
#   .\dev-start.ps1                  # Arranque completo (agy + ollama + taskboard)
#   .\dev-start.ps1 -NoAgy           # Sin agy gateway (usa ai_router.py standalone)
#   .\dev-start.ps1 -NoOllama        # Sin modelos locales
#   .\dev-start.ps1 -TaskboardOnly   # Solo el taskboard

param(
    [switch]$NoAgy,
    [switch]$NoOllama,
    [switch]$TaskboardOnly
)

$ErrorActionPreference = 'Continue'
$repoRoot = $PSScriptRoot
Set-Location $repoRoot

# Track child processes for cleanup on Ctrl+C
$agyProcess = $null
$startedOllama = $false

# Cleanup function — kills child processes on exit
function Cleanup-ChildProcesses {
    if ($agyProcess -and !$agyProcess.HasExited) {
        Write-Host "`n[cleanup] Cerrando Agy Gateway (PID $($agyProcess.Id))..." -ForegroundColor Yellow
        $agyProcess.Kill()
        $agyProcess.WaitForExit(3000)
        Write-Host '[cleanup] Agy Gateway detenido.' -ForegroundColor Gray
    }
    # Also kill any orphaned agy processes from previous runs
    $orphans = Get-Process agy -ErrorAction SilentlyContinue | Where-Object { $_.Id -ne $agyProcess.Id }
    foreach ($o in $orphans) {
        Write-Host "[cleanup] Cerrando agy huérfano (PID $($o.Id))..." -ForegroundColor DarkYellow
        $o.Kill()
    }
}

Write-Host ''
Write-Host 'Axolotto Dev Environment' -ForegroundColor Cyan
Write-Host '================================' -ForegroundColor DarkCyan
Write-Host ''

if ($TaskboardOnly) {
    Write-Host '[1/1] Iniciando solo Taskboard...' -ForegroundColor Blue
    $ts = Join-Path $repoRoot 'tools/taskboard/server.py'
    if (-not (Test-Path $ts)) {
        Write-Host 'ERROR: No se encontro server.py' -ForegroundColor Red
        exit 1
    }
    python $ts
    exit 0
}

# Paso 1: Ollama
if (-not $NoOllama) {
    $ollamaOk = $false
    try {
        $null = Invoke-RestMethod -Uri 'http://localhost:11434/api/tags' -TimeoutSec 2 -ErrorAction Stop
        $ollamaOk = $true
        Write-Host '[1/3] Ollama ya corriendo en :11434' -ForegroundColor Green
    } catch {}

    if (-not $ollamaOk) {
        # Try to find ollama executable
        $ollamaPath = $null
        $commonPaths = @(
            "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe",
            "$env:ProgramFiles\Ollama\ollama.exe",
            "${env:ProgramFiles(x86)}\Ollama\ollama.exe",
            (Get-Command ollama -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source)
        )
        foreach ($p in $commonPaths) {
            if ($p -and (Test-Path $p)) {
                $ollamaPath = $p
                break
            }
        }

        if ($ollamaPath) {
            Write-Host '[1/3] Iniciando Ollama...' -ForegroundColor Yellow
            $ollamaProc = Start-Process $ollamaPath -ArgumentList 'serve' -WindowStyle Hidden -PassThru
            $startedOllama = $true
            Start-Sleep 3
            # Verify it actually started
            try {
                $null = Invoke-RestMethod -Uri 'http://localhost:11434/api/tags' -TimeoutSec 2 -ErrorAction Stop
                Write-Host '       Ollama iniciado en :11434' -ForegroundColor Gray
            } catch {
                Write-Host '       Ollama tarda en responder. Puede necesitar mas tiempo.' -ForegroundColor DarkYellow
            }
        } else {
            Write-Host '[1/3] Ollama no encontrado. Instalalo desde https://ollama.com' -ForegroundColor DarkYellow
            Write-Host '       El taskboard funcionara sin QA local.' -ForegroundColor Gray
        }
    }
} else {
    Write-Host '[1/3] Ollama omitido (-NoOllama)' -ForegroundColor DarkYellow
}

# Paso 2: Agy Gateway — track process for cleanup, VERIFY port is open
if (-not $NoAgy) {
    $cfg = Join-Path $repoRoot 'workspace.json'
    if (Test-Path $cfg) {
        Write-Host '[2/3] Iniciando Agy Gateway...' -ForegroundColor Magenta
        $agyProcess = Start-Process agy -ArgumentList "run --watch --config $cfg" -WindowStyle Hidden -PassThru
        # Wait and check if port actually opened
        $portOpen = $false
        for ($i = 0; $i -lt 6; $i++) {
            Start-Sleep 2
            $portCheck = netstat -ano 2>$null | Select-String ':8642.*LISTENING'
            if ($portCheck) {
                $portOpen = $true
                break
            }
            # Also check if process died
            if ($agyProcess.HasExited) {
                break
            }
        }

        if ($portOpen) {
            Write-Host "       Gateway en ws://localhost:8642 (PID $($agyProcess.Id))" -ForegroundColor Gray
        } elseif ($agyProcess -and !$agyProcess.HasExited) {
            Write-Host '       Agy esta corriendo pero NO abrio el puerto :8642.' -ForegroundColor DarkYellow
            Write-Host '       Probable falta de tokens/cuota de Gemini. El taskboard usara Plan B.' -ForegroundColor DarkYellow
            # Kill the useless agy process to free RAM
            $agyProcess.Kill()
            $agyProcess = $null
        } else {
            Write-Host '       Agy no pudo iniciar. El taskboard usara Plan B (Claude Sonnet).' -ForegroundColor DarkYellow
            $agyProcess = $null
        }
    } else {
        Write-Host '[2/3] workspace.json NO encontrado' -ForegroundColor Red
    }
} else {
    Write-Host '[2/3] Agy omitido (-NoAgy) — modo standalone' -ForegroundColor DarkYellow
}

# Paso 3: Taskboard ( bloqueante hasta Ctrl+C )
Write-Host '[3/3] Iniciando Taskboard...' -ForegroundColor Blue
$ts = Join-Path $repoRoot 'tools/taskboard/server.py'
if (-not (Test-Path $ts)) {
    Write-Host 'ERROR: server.py no encontrado' -ForegroundColor Red
    Cleanup-ChildProcesses
    exit 1
}

Write-Host ''
Write-Host 'Entorno listo:' -ForegroundColor Green
Write-Host '   Taskboard:  http://localhost:8181' -ForegroundColor Gray
if ($agyProcess) {
    Write-Host '   Agy Gateway: ws://localhost:8642' -ForegroundColor Gray
} elseif (-not $NoAgy) {
    Write-Host '   Agy Gateway: NO DISPONIBLE (Plan B activo)' -ForegroundColor DarkYellow
}
if (-not $NoOllama) {
    Write-Host '   Ollama:      http://localhost:11434' -ForegroundColor Gray
}
Write-Host '   Ctrl+C para detener todo' -ForegroundColor DarkGray
Write-Host ''

# Run taskboard — this blocks until Ctrl+C
try {
    python $ts
} catch [System.Management.Automation.BreakException] {
    # Ctrl+C pressed
} catch {
    Write-Host "ERROR: $_" -ForegroundColor Red
} finally {
    # Always clean up child processes
    Cleanup-ChildProcesses
}

Write-Host 'Entorno detenido.' -ForegroundColor Gray
