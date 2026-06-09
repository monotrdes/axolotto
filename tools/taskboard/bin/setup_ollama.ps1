# setup_ollama.ps1 — Verificar e instalar modelos Ollama para Axolotto
# Uso: .\tools\taskboard\bin\setup_ollama.ps1

param(
    [switch]$Pull,     # Descargar modelos si no existen
    [switch]$ListOnly  # Solo listar modelos disponibles
)

$OLLAMA_HOST = "http://localhost:11434"
$REQUIRED_MODELS = @(
    "qwen2.5-coder:7b"
)

Write-Host "`n🖥️ Ollama Setup — Axolotto Agent Ecosystem" -ForegroundColor Cyan
Write-Host "============================================`n" -ForegroundColor DarkCyan

# 1. Check if Ollama is running
Write-Host "[1/3] Verificando servicio Ollama..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$OLLAMA_HOST/api/tags" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "       ✅ Ollama corriendo en $OLLAMA_HOST" -ForegroundColor Green
} catch {
    Write-Host "       ❌ Ollama no está corriendo. Inicia 'ollama serve' primero." -ForegroundColor Red
    Write-Host "       Descarga: https://ollama.com/download" -ForegroundColor Gray
    exit 1
}

# 2. List installed models
Write-Host "`n[2/3] Modelos instalados:" -ForegroundColor Yellow
$installedModels = @()
if ($response.models) {
    foreach ($m in $response.models) {
        $name = $m.name
        $size = [math]::Round($m.size / 1GB, 2)
        Write-Host "       📦 $name ($size GB)" -ForegroundColor Gray
        $installedModels += $name
    }
}

if ($installedModels.Count -eq 0) {
    Write-Host "       (ninguno)" -ForegroundColor DarkGray
}

if ($ListOnly) {
    Write-Host "`n✅ Listo." -ForegroundColor Green
    exit 0
}

# 3. Check required models
Write-Host "`n[3/3] Verificando modelos requeridos para Axolotto:" -ForegroundColor Yellow
$missing = @()
foreach ($required in $REQUIRED_MODELS) {
    $baseName = $required -replace ":\d+.*$", ""
    $found = $installedModels | Where-Object { $_ -like "$baseName*" }
    if ($found) {
        Write-Host "       ✅ $required — instalado" -ForegroundColor Green
    } else {
        Write-Host "       ❌ $required — NO instalado" -ForegroundColor Red
        $missing += $required
    }
}

if ($missing.Count -gt 0) {
    Write-Host "`n⚠️  Faltan $($missing.Count) modelo(s)." -ForegroundColor Yellow

    if ($Pull) {
        Write-Host "`n📥 Descargando modelos..." -ForegroundColor Magenta
        foreach ($model in $missing) {
            Write-Host "       Descargando $model..." -ForegroundColor Gray
            try {
                ollama pull $model
                Write-Host "       ✅ $model descargado." -ForegroundColor Green
            } catch {
                Write-Host "       ❌ Error descargando $model : $_" -ForegroundColor Red
            }
        }
    } else {
        Write-Host "`n   Ejecuta con -Pull para descargarlos automáticamente:" -ForegroundColor Gray
        Write-Host "   .\tools\taskboard\bin\setup_ollama.ps1 -Pull" -ForegroundColor White
    }
} else {
    Write-Host "`n✅ Todos los modelos requeridos están instalados." -ForegroundColor Green
}

Write-Host "`n📋 Modelos y uso en Axolotto:" -ForegroundColor Cyan
Write-Host "   qwen2.5-coder:7b  → QA local, linters, commits, sanity-checks (GPU RTX 3070)" -ForegroundColor Gray
Write-Host "   Costo: $0 (local)" -ForegroundColor Gray
Write-Host ""
