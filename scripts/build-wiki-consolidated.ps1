<#
.SYNOPSIS
    Consolida todos los archivos .md del wiki en un solo archivo gigante
    para subir a Odysseus (u otras plataformas de AI memory).

.DESCRIPTION
    Concatena todos los .md de wiki/ (excluyendo .obsidian/ y el vault
    abandonado axolotto-wiki/) en wiki-consolidado.md con separadores
    claros entre secciones. Total: ~31 archivos, ~200KB.

.PARAMETER OutputPath
    Ruta del archivo de salida. Por defecto: wiki-consolidado.md en la raiz.

.EXAMPLE
    .\scripts\build-wiki-consolidated.ps1
    .\scripts\build-wiki-consolidated.ps1 -OutputPath "C:\Users\imzet\Desktop\axolotto-wiki.md"
#>

param(
    [string]$OutputPath = (Join-Path $PSScriptRoot ".." "wiki-consolidado.md")
)

$wikiRoot = Join-Path $PSScriptRoot ".." "wiki"
$outputPath = [System.IO.Path]::GetFullPath($OutputPath)

# Directorios a excluir
$excludeDirs = @(".obsidian", "axolotto-wiki")

# Orden de procesamiento
$dirOrder = @(
    @{ Dir = "";              Label = "Raiz" },
    @{ Dir = "ai";            Label = "AI" },
    @{ Dir = "arquitectura";  Label = "Arquitectura" },
    @{ Dir = "api";           Label = "API" },
    @{ Dir = "economia";      Label = "Economia" },
    @{ Dir = "mecanicas";     Label = "Mecanicas" },
    @{ Dir = "jugadores";     Label = "Jugadores" }
)

# Orden de archivos dentro de ciertos dirs
$fileOrder = @{
    "" = @("00-INDEX.md", "CHANGELOG.md")
}

# ─── Recolectar archivos ───
$entries = @()
foreach ($dirDef in $dirOrder) {
    $dir = $dirDef.Dir
    $searchPath = if ($dir -eq "") { $wikiRoot } else { Join-Path $wikiRoot $dir }
    if (-not (Test-Path $searchPath)) { continue }

    $mdFiles = @(Get-ChildItem -Path $searchPath -Filter "*.md" -File)
    if ($mdFiles.Count -eq 0) { continue }

    # Respetar orden preferido si existe
    $preferred = $fileOrder[$dir]
    $ordered = @()
    $remaining = @($mdFiles)

    if ($preferred) {
        foreach ($prefName in $preferred) {
            $match = $mdFiles | Where-Object { $_.Name -eq $prefName }
            if ($match) {
                $ordered += $match
                $remaining = @($remaining | Where-Object { $_.Name -ne $prefName })
            }
        }
    }
    $ordered += ($remaining | Sort-Object Name)

    foreach ($f in $ordered) {
        $entries += @{ Dir = $dir; Label = $dirDef.Label; File = $f }
    }
}

# ─── Generar output ───
$now = Get-Date -Format "yyyy-MM-dd HH:mm"
$totalFiles = $entries.Count
$sb = New-Object System.Text.StringBuilder

[void]$sb.AppendLine("# Axolotto — Wiki Completa")
[void]$sb.AppendLine("")
[void]$sb.AppendLine("> **Generado:** $now")
[void]$sb.AppendLine("> **Archivos:** $totalFiles archivos markdown del wiki")
[void]$sb.AppendLine("> **Proposito:** Contexto completo para Odysseus / AI memory platforms")
[void]$sb.AppendLine("> **Script:** \`scripts/build-wiki-consolidated.ps1\` — re-ejecutar para regenerar")
[void]$sb.AppendLine("")
[void]$sb.AppendLine("---")
[void]$sb.AppendLine("")

$currentDir = $null
foreach ($entry in $entries) {
    $dir = $entry.Dir
    $label = $entry.Label
    $file = $entry.File

    # Separador de directorio
    if ($dir -ne $currentDir) {
        [void]$sb.AppendLine("")
        [void]$sb.AppendLine("---")
        [void]$sb.AppendLine("")
        [void]$sb.AppendLine("## $label")
        [void]$sb.AppendLine("")
        $currentDir = $dir
    }

    # Titulo del archivo
    $fileLabel = $file.BaseName
    [void]$sb.AppendLine("### $fileLabel")
    [void]$sb.AppendLine("> \`$dir/$($file.Name)\`")
    [void]$sb.AppendLine("")

    # Contenido
    $content = Get-Content -Path $file.FullName -Raw -Encoding UTF8
    if ($content) {
        [void]$sb.AppendLine($content.TrimEnd())
    } else {
        [void]$sb.AppendLine("*(archivo vacio)*")
    }
    [void]$sb.AppendLine("")
}

# ─── Escribir archivo ───
$output = $sb.ToString()
[System.IO.File]::WriteAllText($outputPath, $output, [System.Text.UTF8Encoding]::new($false))
$outputSize = (Get-Item $outputPath).Length

Write-Host "Wiki consolidado generado:" -ForegroundColor Green
Write-Host "  $outputPath" -ForegroundColor Cyan
Write-Host "  Tamano: $($outputSize.ToString('N0')) bytes | Archivos: $totalFiles" -ForegroundColor White
