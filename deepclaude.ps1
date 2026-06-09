<#
.SYNOPSIS
    Ejecuta Claude CLI redirigiendo las llamadas a la API de DeepSeek (DeepClaude).
.DESCRIPTION
    Carga las variables de entorno del archivo .env del proyecto, configura las variables
    de Anthropic para apuntar a DeepSeek y ejecuta la CLI de Claude. Restaura el entorno al finalizar.
#>

# 1. Buscar el archivo .env subiendo por la estructura de directorios
$currentDir = Get-Item .
$envPath = $null
while ($currentDir -ne $null) {
    $candidate = Join-Path $currentDir.FullName ".env"
    if (Test-Path $candidate) {
        $envPath = $candidate
        break
    }
    $currentDir = $currentDir.Parent
}

# Si no se encuentra, usar el de la raíz por defecto
if (-not $envPath) {
    $defaultPath = "D:\Axolotto_2026\axolotto\.env"
    if (Test-Path $defaultPath) {
        $envPath = $defaultPath
    }
}

if (-not $envPath) {
    Write-Error "No se pudo encontrar el archivo .env del proyecto."
    exit 1
}

# 2. Cargar variables del .env
$envVars = @{}
Get-Content $envPath | Foreach-Object {
    $line = $_.Trim()
    if ($line -and -not $line.StartsWith("#")) {
        $parts = $line -split '=', 2
        if ($parts.Length -eq 2) {
            $key = $parts[0].Trim()
            $value = $parts[1].Trim()
            # Quitar comillas si existen
            $value = $value -replace "^['`"]|['`"]$"
            $envVars[$key] = $value
        }
    }
}

# 3. Extraer valores necesarios o asignar defaults
$dsApiKey = $envVars["DEEPSEEK_API_KEY"]
$dsBaseUrl = $envVars["DEEPSEEK_BASE_URL"]
if (-not $dsBaseUrl) { $dsBaseUrl = "https://api.deepseek.com/anthropic" }
$dsModel = $envVars["DEEPSEEK_MODEL"]
if (-not $dsModel) { $dsModel = "deepseek-v4-pro[1m]" }
$dsEffort = $envVars["DEEPSEEK_EFFORT"]
if (-not $dsEffort) { $dsEffort = "max" }

if (-not $dsApiKey) {
    Write-Error "La variable DEEPSEEK_API_KEY no está definida en el archivo .env ($envPath)."
    exit 1
}

# 4. Guardar variables de entorno actuales para restaurarlas después
$oldBaseUrl = $env:ANTHROPIC_BASE_URL
$oldApiKey = $env:ANTHROPIC_API_KEY
$oldModel = $env:ANTHROPIC_MODEL
$oldEffort = $env:DEEPSEEK_EFFORT
$oldUserProfile = $env:USERPROFILE
$oldHome = $env:HOME

# Crear un directorio de configuración global aislado para evitar conflictos con claude.ai
$dsHome = Join-Path $oldUserProfile ".claude_deepseek_home"
if (-not (Test-Path $dsHome)) {
    New-Item -ItemType Directory -Path $dsHome -Force | Out-Null
}

# 5. Configurar el entorno temporal para DeepSeek
$env:ANTHROPIC_BASE_URL = $dsBaseUrl
$env:ANTHROPIC_API_KEY = $dsApiKey
$env:ANTHROPIC_MODEL = $dsModel
$env:DEEPSEEK_EFFORT = $dsEffort
$env:USERPROFILE = $dsHome
$env:HOME = $dsHome

Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "  Iniciando Claude CLI con motor DeepSeek" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "URL: $env:ANTHROPIC_BASE_URL" -ForegroundColor Gray
Write-Host "Modelo: $env:ANTHROPIC_MODEL" -ForegroundColor Gray
Write-Host "Effort: $env:DEEPSEEK_EFFORT" -ForegroundColor Gray
Write-Host ""

try {
    # Buscar el ejecutable de claude
    $claudeCmd = Get-Command claude -ErrorAction SilentlyContinue
    if (-not $claudeCmd) {
        Write-Error "No se encontró el comando 'claude' en el PATH. Asegúrate de tener instalado Claude CLI."
        exit 1
    }

    # Ejecutar claude pasándole todos los argumentos
    & $claudeCmd.Source @args
}
catch {
    Write-Error "Ocurrió un error al ejecutar Claude CLI: $_"
}
finally {
    # 6. Restaurar el entorno original
    $env:ANTHROPIC_BASE_URL = $oldBaseUrl
    $env:ANTHROPIC_API_KEY = $oldApiKey
    $env:ANTHROPIC_MODEL = $oldModel
    $env:DEEPSEEK_EFFORT = $oldEffort
    $env:USERPROFILE = $oldUserProfile
    $env:HOME = $oldHome
    Write-Host ""
    Write-Host "Entorno original de Claude restaurado." -ForegroundColor Gray
}
