<#
.SYNOPSIS
    Taskboard CLI helper — interactúa con el tablero Kanban desde cualquier agente.
.DESCRIPTION
    Funciona para Claude, DeepClaude, y AGY. Todos usan la misma API REST en localhost:8181.
    Simplifica crear, mover, comentar y listar tareas sin tener que escribir curls largos.

.EXAMPLE
    ./bin/taskboard.ps1 create "Fix auth bug" "El login falla con tokens expirados" planning backend
    ./bin/taskboard.ps1 status task-123 review "Fix implementado, tests pasan"
    ./bin/taskboard.ps1 list doing
    ./bin/taskboard.ps1 get task-123
    ./bin/taskboard.ps1 comment task-123 "Investigando la causa raíz..."
#>

param(
    [ValidateSet("create","move","status","comment","attach","list","get","help")]
    [string]$Action = "help",

    [string]$Arg1,  # task-id for move/status/comment/get, title for create
    [string]$Arg2,  # column for move/status, description for create, comment text for comment
    [string]$Arg3,  # comment for status, column for create
    [string]$Arg4   # category for create
)

$BASE = "http://localhost:8181"

function Write-JsonResponse {
    param($response)
    try {
        $json = $response.Content | ConvertFrom-Json
        $json | ConvertTo-Json -Depth 5
    } catch {
        Write-Host "Error parsing response: $_"
        Write-Host $response.Content
    }
}

switch ($Action) {
    "create" {
        $title = $Arg1
        $desc = $Arg2
        $column = if ($Arg3) { $Arg3 } else { "planning" }
        $category = if ($Arg4) { $Arg4 } else { "backend" }

        if (-not $title) {
            Write-Host "Uso: taskboard.ps1 create <título> <descripción> [columna] [categoría]"
            exit 1
        }

        $body = @{
            prompt = "$title`n`n$desc"
            column = $column
            category = $category
        } | ConvertTo-Json

        Write-Host "Creando tarea: $title" -ForegroundColor Cyan
        try {
            $response = Invoke-RestMethod -Uri "$BASE/api/tasks/create" -Method Post -Body $body -ContentType "application/json"
            Write-Host "✅ Tarea creada: $($response.id)" -ForegroundColor Green
            Write-Host "   Título: $($response.title)"
            Write-Host "   Estado: $($response.status)"
            Write-Host "   Categoría: $($response.category)"
        } catch {
            Write-Host "❌ Error: $_" -ForegroundColor Red
        }
    }

    "move" {
        $taskId = $Arg1
        $column = $Arg2

        if (-not $taskId -or -not $column) {
            Write-Host "Uso: taskboard.ps1 move <task-id> <columna>"
            Write-Host "Columnas: wishes, concepts, planning, doing, review, done"
            exit 1
        }

        $body = @{ id = $taskId; status = $column } | ConvertTo-Json

        Write-Host "Moviendo $taskId → $column" -ForegroundColor Cyan
        try {
            $response = Invoke-RestMethod -Uri "$BASE/api/tasks/move" -Method Post -Body $body -ContentType "application/json"
            Write-Host "✅ Movido a $column" -ForegroundColor Green
            if ($response.notice) { Write-Host "   $($response.notice)" }
        } catch {
            $errorMsg = $_.ErrorDetails.Message
            if (-not $errorMsg) { $errorMsg = $_ }
            Write-Host "❌ Error: $errorMsg" -ForegroundColor Red
        }
    }

    "status" {
        # Move + comment in one call. Arg4 = optional agent (claude|deepclaude|agy)
        $taskId = $Arg1
        $column = $Arg2
        $comment = $Arg3
        $agent = $Arg4

        if (-not $taskId -or -not $column) {
            Write-Host "Uso: taskboard.ps1 status <task-id> <columna> [comentario] [agente]"
            Write-Host "Columnas: wishes, concepts, planning, doing, review, done"
            Write-Host "Agentes: claude, deepclaude, agy"
            exit 1
        }

        $bodyHash = @{ id = $taskId; status = $column; comment = $comment }
        if ($agent) { $bodyHash["assigned_to"] = $agent }
        $body = $bodyHash | ConvertTo-Json

        Write-Host "Actualizando $taskId → $column" -ForegroundColor Cyan
        try {
            $response = Invoke-RestMethod -Uri "$BASE/api/tasks/status" -Method Post -Body $body -ContentType "application/json"
            Write-Host "✅ Actualizado a $column" -ForegroundColor Green
            if ($response.notice) { Write-Host "   $($response.notice)" }
            if ($agent) { Write-Host "   Tarea movida a $column" -ForegroundColor Gray }
        } catch {
            Write-Host "❌ Error: $_" -ForegroundColor Red
        }
    }

    "comment" {
        $taskId = $Arg1
        $text = $Arg2

        if (-not $taskId -or -not $text) {
            Write-Host "Uso: taskboard.ps1 comment <task-id> <comentario>"
            exit 1
        }

        $body = @{ id = $taskId; text = $text } | ConvertTo-Json

        Write-Host "Agregando comentario a $taskId" -ForegroundColor Cyan
        try {
            $response = Invoke-RestMethod -Uri "$BASE/api/tasks/comment" -Method Post -Body $body -ContentType "application/json"
            Write-Host "✅ Comentario agregado" -ForegroundColor Green
        } catch {
            Write-Host "❌ Error: $_" -ForegroundColor Red
        }
    }

    "attach" {
        # Vincula un doc Markdown (relativo al repo, dentro de docs/) a una tarea.
        # La tarjeta mostrará el badge 📄 Plan que abre el visor de docs.
        # Pasar "" como ruta para desvincular el doc.
        $taskId = $Arg1
        $docPath = $Arg2

        if (-not $taskId) {
            Write-Host "Uso: taskboard.ps1 attach <task-id> <ruta-doc|''>"
            Write-Host "Ej:  taskboard.ps1 attach task-123 docs/plan_mi_feature.md"
            exit 1
        }

        $body = @{ id = $taskId; plan_doc_path = $docPath } | ConvertTo-Json

        Write-Host "Adjuntando doc a $taskId" -ForegroundColor Cyan
        try {
            $response = Invoke-RestMethod -Uri "$BASE/api/tasks/edit" -Method Post -Body $body -ContentType "application/json"
            if ($docPath) {
                Write-Host "✅ Doc vinculado: $docPath" -ForegroundColor Green
            } else {
                Write-Host "✅ Doc desvinculado" -ForegroundColor Green
            }
        } catch {
            $errorMsg = $_.ErrorDetails.Message
            if (-not $errorMsg) { $errorMsg = $_ }
            Write-Host "❌ Error: $errorMsg" -ForegroundColor Red
        }
    }

    "list" {
        $column = $Arg1
        Write-Host "Tareas del tablero:" -ForegroundColor Cyan
        try {
            $response = Invoke-RestMethod -Uri "$BASE/api/tasks" -Method Get
            $tasks = $response.tasks
            if ($column) {
                $tasks = $tasks | Where-Object { $_.status -eq $column }
            }
            if (-not $tasks -or $tasks.Count -eq 0) {
                Write-Host "   (sin tareas)" -ForegroundColor Gray
                exit 0
            }
            $tasks | ForEach-Object {
                $icon = @{
                    wishes = [System.Char]::ConvertFromUtf32(0x1F4AD)
                    concepts = [System.Char]::ConvertFromUtf32(0x1F4CC)
                    planning = [System.Char]::ConvertFromUtf32(0x1F4CB)
                    doing = [System.Char]::ConvertFromUtf32(0x26A1)
                    review = [System.Char]::ConvertFromUtf32(0x1F50D)
                    done = [System.Char]::ConvertFromUtf32(0x2705)
                }
                $i = $icon[$_.status]
                $agent = if ($_.assigned_to -ne 'unassigned') { " @$($_.assigned_to)" } else { "" }
                Write-Host "  $i $($_.id) [$($_.status)] $($_.title)$agent" -ForegroundColor White
            }
        } catch {
            Write-Host "❌ Error: $_" -ForegroundColor Red
        }
    }

    "get" {
        $taskId = $Arg1
        if (-not $taskId) {
            Write-Host "Uso: taskboard.ps1 get <task-id>"
            exit 1
        }
        try {
            $response = Invoke-RestMethod -Uri "$BASE/api/tasks" -Method Get
            $task = $response.tasks | Where-Object { $_.id -eq $taskId }
            if ($task) {
                Write-Host "=== $($task.id): $($task.title) ===" -ForegroundColor Cyan
                Write-Host "Estado: $($task.status) | Prioridad: $($task.priority) | Categoría: $($task.category)"
                Write-Host "Asignado: $($task.assigned_to) | Scope: $($task.scope)"
                Write-Host ""
                Write-Host "Descripción:" -ForegroundColor Yellow
                Write-Host $task.description
                if ($task.comments) {
                    Write-Host ""
                    Write-Host "Comentarios ($($task.comments.Count)):" -ForegroundColor Yellow
                    $task.comments | ForEach-Object {
                        Write-Host "  [$($_.author)] $($_.text)" -ForegroundColor Gray
                    }
                }
                if ($task.planning_data -and $task.planning_data.plan_doc_path) {
                    Write-Host ""
                    Write-Host "Documento adjunto:" -ForegroundColor Yellow
                    Write-Host "  📄 $($task.planning_data.plan_doc_path)" -ForegroundColor Cyan
                }
                if ($task.planning_data -and $task.planning_data.requirements) {
                    Write-Host ""
                    Write-Host "Requisitos:" -ForegroundColor Yellow
                    $task.planning_data.requirements | ForEach-Object {
                        $check = if ($_.completed) { "✅" } else { "⬜" }
                        Write-Host "  $check $($_.text)"
                    }
                }
            } else {
                Write-Host "Tarea no encontrada: $taskId" -ForegroundColor Red
            }
        } catch {
            Write-Host "❌ Error: $_" -ForegroundColor Red
        }
    }

    "help" {
        Write-Host @"
Taskboard CLI Helper — para Claude, DeepClaude, y AGY

USO:
  taskboard.ps1 create <título> <descripción> [columna] [categoría]
  taskboard.ps1 move <task-id> <columna>
  taskboard.ps1 status <task-id> <columna> [comentario]
  taskboard.ps1 comment <task-id> <comentario>
  taskboard.ps1 attach <task-id> <ruta-doc>     (ej: docs/plan_x.md — '' desvincula)
  taskboard.ps1 list [columna]
  taskboard.ps1 get <task-id>

COLUMNAS: wishes, concepts, planning, doing, review, done
CATEGORÍAS: frontend, backend, bug, docs, security, finance, game, infra, devops, blockchain
AGENTES: claude, deepclaude, agy
"@
    }
}
