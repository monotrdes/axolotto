<#
.SYNOPSIS
    Taskboard CLI helper - interactua con el tablero Kanban desde cualquier agente.
.DESCRIPTION
    Funciona para Claude, DeepClaude, y AGY. Todos usan la misma API REST en localhost:8181.
    Simplifica crear, mover, comentar y listar tareas sin tener que escribir curls largos.

.EXAMPLE
    ./bin/taskboard.ps1 create "Fix auth bug" "El login falla con tokens expirados" planning backend
    ./bin/taskboard.ps1 status task-123 review "Fix implementado, tests pasan"
    ./bin/taskboard.ps1 list doing
    ./bin/taskboard.ps1 get task-123
    ./bin/taskboard.ps1 batch review done
#>

param(
    [string]$Action = "help",

    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Rest
)

$BASE = "http://localhost:8181"

# -- helpers ----------------------------------------------------------

function _api-post($path, $body) {
    try {
        $response = Invoke-RestMethod -Uri "$BASE$path" -Method Post -Body ($body | ConvertTo-Json) -ContentType "application/json"
        return @{ ok = $true; data = $response }
    } catch {
        $err = if ($_.ErrorDetails.Message) { $_.ErrorDetails.Message } else { "$_" }
        try { $errJson = $err | ConvertFrom-Json; $err = $errJson.message } catch {}
        return @{ ok = $false; error = $err }
    }
}

function _api-get($path) {
    try {
        $response = Invoke-RestMethod -Uri "$BASE$path" -Method Get
        return @{ ok = $true; data = $response }
    } catch {
        return @{ ok = $false; error = "$_" }
    }
}

# -- dispatch ---------------------------------------------------------

switch ($Action) {

    # -- CREATE --

    "create" {
        $title = $Rest[0]
        $desc  = $Rest[1]
        $col   = if ($Rest[2]) { $Rest[2] } else { "planning" }
        $cat   = if ($Rest[3]) { $Rest[3] } else { "backend" }

        if (-not $title) {
            Write-Host "Uso: taskboard.ps1 create TITULO DESCRIPCION [columna] [categoria]"
            exit 1
        }

        $body = @{ prompt = "$title`n`n$desc"; column = $col; category = $cat }
        $r = _api-post "/api/tasks/create" $body
        if ($r.ok) {
            Write-Host "OK $($r.data.id) -> $col | $($r.data.title)" -ForegroundColor Green
        } else {
            Write-Host "ERROR: $($r.error)" -ForegroundColor Red
        }
    }

    # -- MOVE --

    "move" {
        $taskId = $Rest[0]; $col = $Rest[1]
        $force = ($Rest -contains "--force")
        $forceMerge = ($Rest -contains "--force-merge")

        if (-not $taskId -or -not $col) {
            Write-Host "Uso: taskboard.ps1 move TASK-ID COLUMNA [--force] [--force-merge]"
            exit 1
        }

        $body = @{ id = $taskId; status = $col; force = $force; force_merge = $forceMerge }
        $r = _api-post "/api/tasks/move" $body
        if ($r.ok) {
            Write-Host "OK $taskId -> $col" -ForegroundColor Green
            if ($r.data.notice) { Write-Host "   $($r.data.notice)" }
        } else {
            Write-Host "ERROR: $($r.error)" -ForegroundColor Red
        }
    }

    # -- STATUS (move + comment + optional agent) --

    "status" {
        $taskId = $Rest[0]; $col = $Rest[1]; $comment = $Rest[2]; $agent = $Rest[3]

        if (-not $taskId -or -not $col) {
            Write-Host "Uso: taskboard.ps1 status TASK-ID COLUMNA [comentario] [agente]"
            exit 1
        }

        $body = @{ id = $taskId; status = $col; comment = $comment }
        if ($agent) { $body["assigned_to"] = $agent }
        $r = _api-post "/api/tasks/status" $body
        if ($r.ok) {
            Write-Host "OK $taskId -> $col" -ForegroundColor Green
            if ($r.data.notice) { Write-Host "   $($r.data.notice)" }
        } else {
            Write-Host "ERROR: $($r.error)" -ForegroundColor Red
        }
    }

    # -- COMMENT --

    "comment" {
        $taskId = $Rest[0]; $text = $Rest[1]

        if (-not $taskId -or -not $text) {
            Write-Host "Uso: taskboard.ps1 comment TASK-ID COMENTARIO"
            exit 1
        }

        $r = _api-post "/api/tasks/comment" @{ id = $taskId; text = $text }
        if ($r.ok) {
            Write-Host "OK comentario en $taskId" -ForegroundColor Green
        } else {
            Write-Host "ERROR: $($r.error)" -ForegroundColor Red
        }
    }

    # -- ATTACH (vincular/desvincular doc) --

    "attach" {
        $taskId = $Rest[0]; $docPath = $Rest[1]

        if (-not $taskId) {
            Write-Host "Uso: taskboard.ps1 attach TASK-ID RUTA-DOC|''"
            exit 1
        }

        $r = _api-post "/api/tasks/edit" @{ id = $taskId; plan_doc_path = $docPath }
        if ($r.ok) {
            if ($docPath) {
                Write-Host "OK $taskId -> doc: $docPath" -ForegroundColor Green
            } else {
                Write-Host "OK $taskId -> doc desvinculado" -ForegroundColor Green
            }
        } else {
            Write-Host "ERROR: $($r.error)" -ForegroundColor Red
        }
    }

    # -- LIST --

    "list" {
        $col = $Rest[0]
        $r = _api-get "/api/tasks"
        if (-not $r.ok) { Write-Host "ERROR: $($r.error)" -ForegroundColor Red; exit 1 }

        $tasks = $r.data.tasks
        if ($col) { $tasks = $tasks | Where-Object { $_.status -eq $col } }

        if (-not $tasks -or $tasks.Count -eq 0) {
            Write-Host "(sin tareas)" -ForegroundColor Gray
            exit 0
        }

        $icons = @{
            wishes    = [System.Char]::ConvertFromUtf32(0x1F4AD)
            concepts  = [System.Char]::ConvertFromUtf32(0x1F4CC)
            planning  = [System.Char]::ConvertFromUtf32(0x1F4CB)
            doing     = [System.Char]::ConvertFromUtf32(0x26A1)
            review    = [System.Char]::ConvertFromUtf32(0x1F50D)
            done      = [System.Char]::ConvertFromUtf32(0x2705)
        }
        $counts = @{}
        $tasks | ForEach-Object {
            $i = $icons[$_.status]
            if ($_.assigned_to -ne 'unassigned') {
                Write-Host "  $i $($_.id) [$($_.status)] $($_.title) @$($_.assigned_to)"
            } else {
                Write-Host "  $i $($_.id) [$($_.status)] $($_.title)"
            }
            $counts[$_.status] += 1
        }
        $summary = ($counts.Keys | ForEach-Object { "$_=$($counts[$_])" }) -join " "
        Write-Host "  -- $($tasks.Count) tareas | $summary" -ForegroundColor Gray
    }

    # -- GET --

    "get" {
        $taskId = $Rest[0]
        if (-not $taskId) { Write-Host "Uso: taskboard.ps1 get TASK-ID"; exit 1 }

        $r = _api-get "/api/tasks"
        if (-not $r.ok) { Write-Host "ERROR: $($r.error)" -ForegroundColor Red; exit 1 }

        $task = $r.data.tasks | Where-Object { $_.id -eq $taskId }
        if (-not $task) { Write-Host "ERROR: Tarea no encontrada: $taskId" -ForegroundColor Red; exit 1 }

        Write-Host "=== $($task.id): $($task.title) ===" -ForegroundColor Cyan
        Write-Host "Estado: $($task.status) | Prioridad: $($task.priority) | Categoria: $($task.category)"
        Write-Host "Asignado: $($task.assigned_to) | Scope: $($task.scope)"
        if ($task.git_branch) { Write-Host "Rama: $($task.git_branch)" }
        Write-Host ""
        Write-Host $task.description

        if ($task.comments -and $task.comments.Count -gt 0) {
            Write-Host ""; Write-Host "Comentarios ($($task.comments.Count)):" -ForegroundColor Yellow
            $task.comments | ForEach-Object { Write-Host "  [$($_.author)] $($_.text)" -ForegroundColor Gray }
        }
        if ($task.planning_data.plan_doc_path) {
            Write-Host ""; Write-Host "Doc: $($task.planning_data.plan_doc_path)" -ForegroundColor Cyan
        }
        if ($task.planning_data.requirements) {
            Write-Host ""; Write-Host "Requisitos:" -ForegroundColor Yellow
            $task.planning_data.requirements | ForEach-Object {
                $check = if ($_.completed) { "[x]" } else { "[ ]" }
                Write-Host "  $check $($_.text)"
            }
        }
    }

    # -- BATCH (mover multiples tareas de una columna a otra) --

    "batch" {
        $fromCol = $Rest[0]; $toCol = $Rest[1]
        $force = ($Rest -contains "--force")
        $forceMerge = ($Rest -contains "--force-merge")

        if (-not $fromCol -or -not $toCol) {
            Write-Host "Uso: taskboard.ps1 batch COL-ORIGEN COL-DESTINO [--force] [--force-merge]"
            Write-Host "Ej:  taskboard.ps1 batch review done"
            Write-Host "Ej:  taskboard.ps1 batch doing review --force"
            exit 1
        }

        $r = _api-get "/api/tasks"
        if (-not $r.ok) { Write-Host "ERROR: $($r.error)" -ForegroundColor Red; exit 1 }

        $ids = ($r.data.tasks | Where-Object { $_.status -eq $fromCol } | ForEach-Object { $_.id })
        if (-not $ids -or $ids.Count -eq 0) {
            Write-Host "OK 0 tareas: no hay nada en '$fromCol'" -ForegroundColor Green
            exit 0
        }

        $body = @{ ids = @($ids); status = $toCol; force = $force; force_merge = $forceMerge }
        $r2 = _api-post "/api/tasks/move-batch" $body
        if ($r2.ok) {
            $ok = 0; $fail = 0
            $r2.data.results | ForEach-Object {
                if ($_.success) { $ok++ } else { $fail++; Write-Host "   FAIL $($_.id): $($_.reason)" -ForegroundColor Red }
            }
            $msg = "OK $ok tareas movidas: $fromCol -> $toCol"
            if ($fail -gt 0) { $msg += " | $fail fallaron" }
            Write-Host $msg -ForegroundColor Green
        } else {
            Write-Host "ERROR: $($r2.error)" -ForegroundColor Red
        }
    }

    # -- DELETE --

    "delete" {
        $taskId = $Rest[0]
        $force = ($Rest -contains "--force")

        if (-not $taskId) { Write-Host "Uso: taskboard.ps1 delete TASK-ID [--force]"; exit 1 }

        if (-not $force) {
            Write-Host "Usa --force para confirmar eliminacion de $taskId" -ForegroundColor Yellow
            exit 1
        }

        $r = _api-post "/api/tasks/delete" @{ id = $taskId }
        if ($r.ok) {
            Write-Host "OK $taskId eliminada" -ForegroundColor Green
        } else {
            Write-Host "ERROR: $($r.error)" -ForegroundColor Red
        }
    }

    # -- ASSIGN --

    "assign" {
        $taskId = $Rest[0]; $agent = $Rest[1]
        $known = @("claude","deepclaude","agy")

        if (-not $taskId -or $agent -notin $known) {
            Write-Host "Uso: taskboard.ps1 assign TASK-ID claude|deepclaude|agy"
            exit 1
        }

        $r = _api-post "/api/tasks/assign" @{ id = $taskId; agent = $agent }
        if ($r.ok) {
            Write-Host "OK $taskId -> @$agent" -ForegroundColor Green
        } else {
            Write-Host "ERROR: $($r.error)" -ForegroundColor Red
        }
    }

    # -- DONE (marcar ejecucion manual terminada -> review) --

    "done" {
        $taskId = $Rest[0]
        if (-not $taskId) { Write-Host "Uso: taskboard.ps1 done TASK-ID"; exit 1 }

        $r = _api-post "/api/tasks/exec-done" @{ id = $taskId }
        if ($r.ok) {
            Write-Host "OK $taskId -> review (ejecucion marcada terminada)" -ForegroundColor Green
        } else {
            Write-Host "ERROR: $($r.error)" -ForegroundColor Red
        }
    }

    # -- PLAN --

    "plan" {
        $taskId = $Rest[0]; $action = $Rest[1]

        if (-not $taskId -or $action -notin @("generate","approve","cancel")) {
            Write-Host "Uso: taskboard.ps1 plan TASK-ID generate|approve|cancel"
            exit 1
        }

        switch ($action) {
            "generate" {
                $feedback = if ($Rest[2]) { $Rest[2] } else { "" }
                $body = @{ id = $taskId; feedback = $feedback }
                $r = _api-post "/api/tasks/plan/generate" $body
            }
            "approve" {
                $r = _api-post "/api/tasks/plan/approve" @{ id = $taskId; approved = $true }
            }
            "cancel" {
                $r = _api-post "/api/tasks/plan/cancel" @{ id = $taskId }
            }
        }

        if ($r.ok) {
            Write-Host "OK $taskId plan $action" -ForegroundColor Green
            if ($r.data.message) { Write-Host "   $($r.data.message)" }
        } else {
            Write-Host "ERROR: $($r.error)" -ForegroundColor Red
        }
    }

    # -- GIT-MERGE --

    "git-merge" {
        $taskId = $Rest[0]
        $force = ($Rest -contains "--force")

        if (-not $taskId) {
            Write-Host "Uso: taskboard.ps1 git-merge TASK-ID [--force]"
            exit 1
        }

        $body = @{ task_id = $taskId; force = $force }
        $r = _api-post "/api/git/merge" $body
        if ($r.ok) {
            Write-Host "OK merge: $($r.data.message)" -ForegroundColor Green
            if ($r.data.cleanup_notes) { Write-Host "   cleanup: $($r.data.cleanup_notes -join ', ')" }
        } else {
            Write-Host "ERROR: $($r.data.error)" -ForegroundColor Red
            if ($r.data.conflict) { Write-Host "   Conflicto detectado - resuelve manualmente" -ForegroundColor Yellow }
        }
    }

    # -- GIT-CLEANUP --

    "git-cleanup" {
        $r = _api-post "/api/git/cleanup" @{}
        if ($r.ok) {
            Write-Host "OK $($r.data.removed_count) worktrees eliminados" -ForegroundColor Green
            if ($r.data.removed) {
                $r.data.removed | ForEach-Object {
                    Write-Host "   - $($_.task_id) [$($_.reason)]"
                }
            }
            if ($r.data.errors) {
                $r.data.errors | ForEach-Object { Write-Host "   ERROR: $_" -ForegroundColor Red }
            }
        } else {
            Write-Host "ERROR: $($r.error)" -ForegroundColor Red
        }
    }

    # -- DIFF --

    "diff" {
        $taskId = $Rest[0]
        if (-not $taskId) { Write-Host "Uso: taskboard.ps1 diff TASK-ID"; exit 1 }

        $r = _api-get "/api/tasks/diff?task_id=$taskId"
        if ($r.ok) {
            if ($r.data.diff) {
                Write-Host $r.data.diff
            } else {
                Write-Host "(sin cambios)" -ForegroundColor Gray
            }
        } else {
            Write-Host "ERROR: $($r.error)" -ForegroundColor Red
        }
    }

    # -- AGENTS --

    "agents" {
        $r = _api-get "/api/agents"
        if ($r.ok) {
            $r.data.agents | ForEach-Object {
                $s = if ($_.active) { "[ON]" } else { "[--]" }
                Write-Host "  $s $($_.name): $($_.status)"
            }
        } else {
            Write-Host "ERROR: $($r.error)" -ForegroundColor Red
        }
    }

    # -- HELP (default) --

    default {
        Write-Host @"
Taskboard CLI - operador Kanban para agentes AI

  Tareas:
    taskboard.ps1 create TITULO DESCR [col] [cat]    Nueva tarea
    taskboard.ps1 status ID COL [coment] [agente]     Mover + comentar (preferir)
    taskboard.ps1 move ID COL [--force]              Solo mover
    taskboard.ps1 get ID                             Detalle completo
    taskboard.ps1 list [columna]                     Listar tareas
    taskboard.ps1 comment ID TEXTO                   Solo comentar
    taskboard.ps1 delete ID --force                  Eliminar tarea
    taskboard.ps1 attach ID DOC|''                   Vincular doc (docs/*.md)

  Batch:
    taskboard.ps1 batch DE A [--force]               Mover TODAS las tareas de una columna a otra

  Agentes:
    taskboard.ps1 assign ID claude|deepclaude|agy    Cambiar asignacion
    taskboard.ps1 done ID                            Marcar ejecucion terminada -> review
    taskboard.ps1 agents                             Estado de agentes AI

  Planificacion AI:
    taskboard.ps1 plan ID generate [feedback]        Generar/refinar plan
    taskboard.ps1 plan ID approve                    Aprobar plan
    taskboard.ps1 plan ID cancel                     Cancelar planificacion

  Git:
    taskboard.ps1 git-merge ID [--force]             Mergear rama de tarea
    taskboard.ps1 git-cleanup                        Limpiar worktrees huerfanos
    taskboard.ps1 diff ID                            Ver diff de changes

Columnas:  wishes concepts planning doing review done
Categorias: frontend backend bug docs security finance game infra devops blockchain
"@
    }
}
