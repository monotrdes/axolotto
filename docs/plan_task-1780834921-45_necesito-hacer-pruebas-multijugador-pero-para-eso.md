# Plan: Pruebas Multijugador y Simulación de Oponentes (Dev Mode)

> Generado por **antigravity** · tarea `task-1780834921-45` · 2026-06-07T12:26:00Z

---

## Descripción

El objetivo de esta tarea es proveer un mecanismo robusto y autónomo para probar las mecánicas y flujos del modo Multijugador en entornos locales de desarrollo (Local Dev). Actualmente, al no haber otros jugadores conectados en Local Dev, la sala se autocompleta con "bots virtuales" que no existen físicamente en la base de datos tras expirar un timeout. Esto dificulta la depuración de perfiles reales de jugadores, sus estadísticas, el historial de partidas, y el comportamiento de las salas.

Proponemos una solución de dos partes:
1. **Endpoint de desarrollo (`POST /api/v1/dev/fill-multiplayer-rooms`)**: Genera usuarios mock reales en la base de datos (con wallets, Axolotitos e inventarios de tablas), los financia con Frijolitos (FRJ) y los registra en la sala de espera seleccionada.
2. **Controlador del Scheduler en Dev Mode**: Modifica las reglas del programador de emparejamiento para que, en modo local, una sala que contenga *únicamente* jugadores mock no inicie la partida por timeout de forma autónoma. La sala esperará indefinidamente a que el desarrollador (usuario real) se registre, permitiendo un flujo de pruebas controlado.

---

## Análisis de Impacto

- **Backend / DB (`test.db`)**: 
  - Se crearán usuarios mock (`did:privy:dev_mock_1` a `did:privy:dev_mock_5`), sus carteras (`Wallet`), Axolotitos (`Axolotito`) y tablas de juego (`PlayerBoard`).
  - Se modificará levemente el bucle de matchmaking de `MultiplayerService` para condicionar el inicio de salas en desarrollo.
- **Frontend / UI**:
  - Se ampliará el badge flotante de herramientas de desarrollo (`TutorialResetButton.tsx`) convirtiéndolo en un panel multiuso `🛠️ DEV Panel`.
  - Se añadirá una sección de "Llenado de Salas de Espera" con selectores de sala y un botón interactivo para invocar oponentes.
- **Flujo de Juego / Game Design**:
  - **Matchmaking**: El juego sólo empezará cuando el usuario se sume al lobby pre-poblado por los mocks.
  - **Simulación**: Al iniciar la partida, los perfiles de los oponentes simularán las tiradas basadas en sus estadísticas reales grabadas en la DB en lugar de perfiles genéricos vacíos.

---

## Archivos a crear/modificar

- [backend/app/api/v1/endpoints/dev.py](file:///D:/Axolotto_2026/axolotto/backend/app/api/v1/endpoints/dev.py) — Añadir endpoint `POST /fill-multiplayer-rooms`.
- [backend/app/services/multiplayer_service.py](file:///D:/Axolotto_2026/axolotto/backend/app/services/multiplayer_service.py) — Ajustar `process_waiting_rooms` para omitir auto-start en salas con solo mocks en Local Dev.
- [frontend/components/dev/TutorialResetButton.tsx](file:///D:/Axolotto_2026/axolotto/frontend/components/dev/TutorialResetButton.tsx) — Expandir el componente a `DevToolsBadge` y añadir los controles de multijugador.

---

## Checklist de criterios de aceptación

- [ ] El endpoint `POST /api/v1/dev/fill-multiplayer-rooms` crea correctamente de 1 a 5 usuarios mock con sus Axolotitos y tablas si no existen.
- [ ] El endpoint inscribe a los Axolotitos mock en la sala seleccionada (`rookie_pool` o `champion_abyss`) deduciendo su buy-in de su balance y colocándolo en `escrow_balance_gal`.
- [ ] En desarrollo local (`BLOCKCHAIN_MODE=local`), las salas con 100% jugadores mock permanecen en estado `waiting` independientemente del tiempo transcurrido.
- [ ] Cuando el desarrollador se registra en una sala previamente poblada con mocks, la sala cumple con el cupo mínimo (>= 4 tablas) e inicia la partida en la siguiente ejecución del scheduler (10 segundos).
- [ ] El badge flotante del frontend muestra una sección dedicada a Multijugador que permite elegir la sala y rellenarla con un solo click.

---

## Propuestas / Mejoras (Game Design & UX)

### 1. Graceful Bot Fallback en Producción (Opinión de Game Design)
El comportamiento actual de rellenar con bots virtuales si la sala no se completa en X segundos es **correcto y necesario** en producción. En juegos Web3 de lotería casual:
- Si el usuario se queda atrapado en el lobby esperando más de 60 segundos, abandonará la plataforma y posiblemente no regrese (UX frustrante).
- Sin embargo, los bots virtuales deben comportarse de forma realista. El jackpot está protegido por la regla anti-sybil (`human_wallets >= 2` y `human_boards_count >= 5`), por lo que no hay riesgo económico para el tesoro del juego.
- **Recomendación**: Mantener los bots para producción pero asegurar que visualmente no frustren al jugador (por ejemplo, dándoles nombres amigables de Axolotitos que simulen ser reales y ocultando el hecho explícito de que son bots para mantener el ambiente competitivo).

### 2. Control de Inicio para Pruebas
Para evitar que las salas expiren antes de que el desarrollador pueda hacer clic en el frontend, definiremos que las salas que solo tengan usuarios con prefijo `did:privy:dev_mock_` tengan un tiempo de espera infinito. Tan pronto como entra una billetera no mock (la del dev real), el contador de tiempo de espera regular se activa o la sala inicia directamente si ya se alcanza el cupo total.

---

## Notas de Diseño

### Estructura de Creación del Mock Player (Backend)
```python
@router.post("/fill-multiplayer-rooms")
def fill_multiplayer_rooms(
    room_type: str = "rookie_pool",
    count: int = 3,
    session: Session = Depends(get_session)
):
    # 1. Asegurar BLOCKCHAIN_MODE == local
    # 2. Iterar 1..count para crear/actualizar did:privy:dev_mock_{i}
    # 3. Darles saldo de FRJ (10000)
    # 4. Crear su Axolotito (Mockito {i}) y su PlayerBoard (grilla de 16 cartas random) si no existen
    # 5. Registrar en la sala usando get_or_create_waiting_room
```

### Integración en el Matchmaking Loop (`MultiplayerService`)
```python
# En process_waiting_rooms:
has_real_player = False
for reg in regs:
    axo = session.get(Axolotito, reg.axolotito_id)
    if axo and not axo.user_id.startswith("did:privy:dev_mock_"):
        has_real_player = True
        break

if settings.BLOCKCHAIN_MODE == "local" and not has_real_player:
    # Sala solo tiene mocks, no iniciar
    should_start = False
```

---

## Guía de Verificación

1. **Paso 1**: Levantar el backend en local (`BLOCKCHAIN_MODE=local`).
2. **Paso 2**: Entrar a la interfaz de desarrollo y presionar el botón `🛠️ DEV`.
3. **Paso 3**: En la sección de multijugador, elegir `Charco de Novatos (Rookie)` y presionar `Llenar Sala`.
4. **Paso 4**: Verificar en la base de datos o en la consola que se hayan creado los usuarios mock y que estén en espera en la sala (`GET /api/v1/multiplayer/lobby` debe listarlos).
5. **Paso 5**: Verificar que pasados los 60 segundos la sala sigue en `waiting` (la consola no muestra logs de simulación iniciada).
6. **Paso 6**: Registrar al axolotito del jugador real en la misma sala desde la interfaz de juego.
7. **Paso 7**: Confirmar que la partida inicia automáticamente a los pocos segundos con los oponentes simulando sus turnos en base a sus estadísticas reales.
