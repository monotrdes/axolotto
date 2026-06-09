---
tags: [ai-context, reglas]
description: "Reglas inviolables de desarrollo con explicación del WHY"
last_modified: "2026-06-07"
source_files: ["CLAUDE.md", "memory/feedback_critical_rules.md"]
---

# Reglas Críticas de Desarrollo

| # | Regla | WHY (consecuencia de violarla) | Dónde aplica |
|---|-------|-------------------------------|-------------|
| 1 | Nunca push a main/master — feature branches → dev → master | Master es lo que ven los usuarios en producción. Un push directo puede romper el juego en vivo. | Git workflow |
| 2 | Conventional Commits: `feat(scope): desc`, `fix(scope): desc`, `docs:`, `refactor:` | Sin convención el historial es ilegible y el taskboard no puede parsear cambios automáticamente. | Todo commit |
| 3 | `SELECT FOR UPDATE` antes de mutar Wallet/Inventory | Race condition probada en producción: dos requests concurrentes pueden leer el mismo balance y ambas acreditar, causando doble cobro o doble crédito con dinero real. | `backend/app/services/bank_service.py`, todos los servicios que tocan balance |
| 4 | `ProcessedTransaction` (UNIQUE) — INSERT antes de acreditar | Un tx on-chain puede ser procesado dos veces si el request hace retry. Sin el INSERT previo, el jugador recibe AXF/FRJ dos veces por la misma transacción blockchain. | `backend/app/services/web3_service.py`, endpoint checkout |
| 5 | `random.SystemRandom()` exclusivamente — jamás `random.random()` | Requisito de fairness criptográfica para sorteos de lotería. `random.random()` es predecible y puede ser explotado para predecir resultados. Grep `random.random\|random.choice` antes de cualquier commit de game logic. | Toda aleatoriedad en backend |
| 6 | Direcciones de contrato siempre desde env vars (`NEXT_PUBLIC_*`) o `settings.py` | Los contratos se redeploy en testnet constantemente. Las direcciones hardcodeadas se rompen silenciosamente — el juego parece funcionar pero las transacciones fallan en chain. | `contracts/`, `frontend/hooks/`, `backend/app/services/web3_service.py` |
| 7 | Verificar `authenticated` (Privy) antes de cualquier mutación de wallet | Sin esta verificación cualquier request no-autenticado puede mutar el estado del juego. | Todos los endpoints con `Depends(get_current_user)` y componentes frontend con `usePrivy()` |
| 8 | Taskboard solo en `tools/taskboard/` — nunca tocar backend/frontend/contracts desde tareas de taskboard | Aislamiento: el taskboard es una herramienta interna. Si una tarea del taskboard describe cambios en el juego, esos cambios son para el scope del juego — no para el propio taskboard. | `tools/taskboard/` |
| 9 | Agentes trabajan en worktrees aislados bajo `../.axolotto_worktrees/` | Evita contaminar la rama principal durante desarrollo paralelo. Worktrees huérfanos (sin rama activa) deben limpiarse periódicamente. | Git worktrees, agentes AI |
| 10 | No iniciar servidores desde tareas de agente | Los agentes deben verificar con unit tests o análisis estático, no levantando el stack completo. Iniciar servidores desde agentes puede causar conflictos de puerto y estado impredecible. | Todos los agentes |

## Regla 11: Taskboard obligatorio para toda tarea

**Regla**: Toda tarea, idea o plan que se inicie DEBE registrarse en el taskboard como tarjeta. Sin tarjeta no existe la tarea.

| Acción | Qué hacer |
|--------|-----------|
| Al iniciar trabajo | Crear tarjeta → mover a `doing` con agente asignado |
| Al terminar | Mover a `review` con descripción de qué se hizo |
| Al recibir aprobación | Mover a `done` — NUNCA sin aprobación explícita del usuario |
| Al publicar plan en `docs/` | Vincular el doc a la tarjeta para activar badge 📄 |

```powershell
# Crear con todos los badges activados:
.\tools\taskboard\bin\taskboard.ps1 create "Título" "Descripción" planning <categoría>
.\tools\taskboard\bin\taskboard.ps1 status <id> doing "Comenzando" <claude|deepclaude|agy>
```

→ Ver guía completa en [[agent_routing]] sección "Workflow Obligatorio del Taskboard"

| 12 | Changelog obligatorio | Cada merge a `develop` debe registrar entrada en `wiki/CHANGELOG.md`. El taskboard lo automatiza; si falla, revisar manualmente. Sin changelog el historial de cambios del wiki queda incompleto. | Taskboard → DONE, todo merge a dev |

## Regla extra: Ledger obligatorio
Cada cambio de balance (AXF o FRJ) **debe** escribir una fila en `TransactionLedger`. Sin esto la auditoría y el debug de economía son imposibles. Aplica en todos los servicios de `backend/app/services/`.

## Cómo aplicar las reglas en la práctica

**Antes de cualquier commit de game logic:**
```bash
# Verificar que no hay random.random() o random.choice()
grep -r "random\.random\|random\.choice" backend/app/
```

**Patrón correcto para mutación de wallet:**
```python
# En service layer:
wallet = session.exec(
    select(Wallet).where(Wallet.user_id == user_id).with_for_update()
).one()
# ... lógica de negocio ...
session.add(TransactionLedger(...))
session.commit()
```

**Patrón correcto para replay protection:**
```python
# INSERT ANTES de acreditar:
try:
    session.add(ProcessedTransaction(tx_hash=tx_hash))
    session.flush()  # lanza IntegrityError si ya existe
except IntegrityError:
    return  # ya procesado, ignorar silenciosamente
# ... acreditar AXF/FRJ aquí ...
```

→ Ver [[gotchas]] para casos edge donde estas reglas tienen matices
→ Ver [[agent_routing]] para qué agente especializado aplica cada regla
