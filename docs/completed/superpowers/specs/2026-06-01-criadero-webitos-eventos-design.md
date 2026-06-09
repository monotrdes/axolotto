# Rediseño del Criadero, Webitos y Modo Manual con Eventos

> **Spec de diseño.** Estado: aprobado por el dueño del producto. Fecha: 2026-06-01.
> **Ver también:** `docs/superpowers/specs/2026-05-31-sistema-4-stats-axolotito-design.md`, `GDD.md` (§3 Criadero), `AXOLOTTO_BIBLE.md`.

---

## 1. Objetivo

Rediseñar tres sistemas interrelacionados:

1. **Imprinting** — reemplaza las acciones de cuidado con cooldown por un sistema de partidas que moldean el ADN del Webito.
2. **Ceremonia de nacimiento** — cada eclosión es un evento cinematográfico único e irrepetible.
3. **Eventos de modo manual** — el modo manual existe solo cuando hay un evento activo, configurable completamente desde admin.

Adicionalmente: ajustar SUERTE del jugador (promedio de sus Axolotitos) y penalización de la naturaleza Glotón.

---

## 2. Sistema de Imprinting (reemplaza cuidados con cooldown)

### 2.1 Concepto

Al comprar un Webito, nace con **ADN incompleto**: valores de stats en rango medio, sin terminar. El jugador lleva al Webito como compañero a N partidas de Lotería usando cualquier Axolotito que ya posea como **padrino**. Cada partida sube o baja stats según lo que ocurrió en ella. Después de N partidas, el ADN se **sella** y el Webito eclosa con la ceremonia.

El tutorial del primer Axolotito ya usa este sistema — sus 3 fases son las primeras 3 partidas de imprinting. No hay diferencia mecánica entre el primer Axolotito y los siguientes.

### 2.2 Partidas de imprinting por rareza

| Rareza | Partidas requeridas | Ceremonia |
|--------|--------------------|-----------:|
| ⚪ Común | 3 | ~12 segundos |
| 🔵 Raro | 5 | ~18 segundos |
| 🌟 Legendario | 7 | ~25 segundos |

### 2.3 ADN de inicio (al comprar el Webito)

Los stats de inicio son valores medios dentro del rango, con variación aleatoria de ±15:

| Stat | Rango del stat | Valor inicial aprox. |
|------|---------------|---------------------|
| ✨ SUERTE | 0–100 | ~35 ± 15 |
| 👁️ OJO | 0–100 | ~40 ± 15 |
| 🔋 PILA | 50–200 | ~90 ± 20 |
| 🧂 SAL | 0–100 | ~20 ± 10 |

La **naturaleza** (Suertudo, Metódico, etc.) se determina al comprar el Webito y es visible desde el inicio — le da identidad inmediata. Los valores de stats son los que fluctúan.

### 2.4 Mapeo evento → cambio de stat

Cada partida emite eventos que se evalúan al terminar. Los deltas se acumulan y se aplican al Webito al final de la partida. Los valores están clampeados a los rangos válidos de cada stat.

#### ✨ SUERTE
| Evento de partida | Delta |
|---|---|
| Ganó la partida | +8 a +15 (aleatorio en rango) |
| Perdió la partida | −8 a −12 |
| Ganó con jackpot o bonus | +20 |

#### 👁️ OJO
| Evento de partida | Delta |
|---|---|
| ≥ 80% de cartas cantadas marcadas correctamente | +10 a +18 |
| ≤ 50% de cartas marcadas | −8 a −14 |
| Padrino tuvo miss chance bajo (OJO alto) | +5 |

#### 🔋 PILA
| Evento de partida | Delta |
|---|---|
| Sesión larga (3+ partidas en la misma sesión) | +10 a +15 |
| Partida única y corta | −5 |
| Padrino terminó con >80% de su energía actual sobre su PILA máxima | +8 |

#### 🧂 SAL
| Evento de partida | Delta |
|---|---|
| Partida limpia (padrino con SAL < 20) | −6 a −10 |
| Padrino drenó mucha energía post-partida (SAL alta) | +8 a +12 |
| Muchas cartas perdidas (>40% miss) | +5 |

### 2.5 Progresión visual del ADN

El jugador ve las "hebras de ADN" del Webito en su perfil durante el imprinting:
- La **naturaleza** es visible desde el inicio.
- Cada stat se muestra como barra con su valor actual.
- Después de cada partida, las barras animan hacia los nuevos valores.
- Stats aún sin "activar" (si la lógica lo requiere por rareza) se muestran con opacidad reducida.

### 2.6 Quién puede ser padrino

Cualquier Axolotito del jugador puede ser padrino. Un Axolotito puede ser padrino de un solo Webito a la vez. El jugador elige el padrino al iniciar el imprinting.

---

## 3. Ceremonia de Nacimiento (Modo Cinematográfico)

### 3.1 Secuencia de 7 pasos

| Paso | Descripción | Duración aprox. |
|------|-------------|-----------------|
| 1 | Pantalla oscura. El huevo pulsa 3 veces con luz interna. | ~2s |
| 2 | El huevo se rompe. El Axolotito aparece como silueta brillante. | ~1.5s |
| 3 | El nombre aparece letra por letra (typewriter). Un tono por letra. | ~2s |
| 4 | La naturaleza se revela con fanfare. Color único por naturaleza explota de fondo. | ~2s |
| 5 | Los 4 stats se revelan como cartas de Lotería: flip individual, pausa, sonido de carta. Orden: ✨ → 👁️ → 🔋 → 🧂. Si SAL es baja (< 15): chime especial. Si un stat es excepcionalmente alto: acorde positivo. | ~4s |
| 6 | Frase de origen generada: *"Aprendió jugando con [nombre del padrino]. Ganaron [N] de [M] partidas."* | ~2s |
| 7 | Botón *"Conocer a [nombre]"* — el jugador cierra la ceremonia cuando quiere. | manual |

### 3.2 Variación por rareza

| Rareza | Diferencias en ceremonia |
|--------|--------------------------|
| ⚪ Común | Secuencia estándar. ~12s. |
| 🔵 Raro | Partículas de agua al romperse el huevo. Stats con contador animado (cuenta rápido hasta el valor). ~18s. |
| 🌟 Legendario | Pantalla completa. El cenote aparece de fondo. Animación de pose única según naturaleza. Stats con rayos y confeti dorado. ~25s. |

### 3.3 Nombre generado

El nombre del Axolotito se genera automáticamente a partir de su naturaleza y stat dominante (stat más alto relativo a su rango), usando el sistema `axo_names.py` existente. El jugador puede renombrarlo después desde su perfil.

---

## 4. Progresión de Stats Post-Nacimiento

Las acciones de cuidado con cooldown (`acariciar`, `cantar`, `alimentar`) quedan **eliminadas**. Los stats de un Axolotito ya nacido mejoran por tres vías:

| Fuente | Tipo | Notas |
|--------|------|-------|
| Equipo (ropa, accesorios) | Permanente mientras equipado | Bonos en los campos `stat_*` según el item |
| Items especiales | Temporal (duración definida) | Ej. "Polvo de Suerte: +20 SUERTE por 2h" |
| Subir de nivel | Permanente | Ver §4.1 |

### 4.1 Sistema de niveles (concepto — spec propio)

Los Axolotitos ganan XP jugando partidas. Al subir de nivel reciben puntos de stat distribuidos según su naturaleza. Este sistema se especificará por separado. Para este spec, basta con confirmar que existe como tercera capa de progresión.

**Stack de stat final:**
```
STAT_FINAL = base (imprinting) + equipo + buff temporal + bonus de nivel
```

---

## 5. Modo Manual con Eventos

### 5.1 Filosofía

El modo manual **no tiene ventana horaria hardcodeada**. Existe solo cuando hay un evento activo creado desde el admin. Esto permite:
- Control total del admin sobre cuándo hay partidas manuales.
- Usar eventos cortos para testing de modo online real.
- Crear eventos multi-día para cubrir el loop de juego diario.
- Escalar a una ventana permanente simplemente creando un evento recurrente de larga duración.

### 5.2 Comportamiento del botón de modo manual para el jugador

| Estado | Lo que ve el jugador |
|--------|---------------------|
| Evento activo ahora | Nombre del evento, bonos activos, tiempo restante, botón *"Jugar modo manual"* habilitado |
| Sin evento activo, hay próximo | Botón deshabilitado. *"Modo cerrado"* + countdown al próximo evento + nombre del evento próximo |
| Sin eventos programados | Botón deshabilitado. *"Próximamente"* |

### 5.3 Modelo de datos: `ManualModeEvent`

```python
class ManualModeEvent(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str                          # "Noche de Lotería #1 🌙"
    start_date: date                   # 2026-06-06
    end_date: date                     # 2026-06-08
    daily_open_time: time | None       # 15:00 — None = todo el día
    daily_close_time: time | None      # 23:00
    # Economía
    tabla_cost_gal: float = 10.0       # costo por tabla por partida
    max_tablas_per_player: int = 3     # cuántas tablas puede tomar el jugador
    prize_pool_pct: float = 0.80       # % del pozo al ganador
    platform_fee_pct: float = 0.10    # fee de plataforma (burn/tesorería)
    jackpot_contribution_pct: float = 0.10
    bonus_gal_on_win: float = 0.0      # GAL extra al ganar
    drop_multiplier: float = 1.0       # multiplicador de drops de items
    xp_bonus_pct: float = 0.0         # % extra de XP para niveles
    # Mecánicas
    griton_delay_ms: int = 2000        # delay entre cartas (800–3000)
    griton_repeats: bool = True        # el gritón repite la carta 1 vez
    win_condition: str = "tabla_llena" # línea_h|línea_v|esquinas|tabla_llena|cruz|l_invertida
    max_game_duration_s: int | None = None
    tie_behavior: str = "split"        # split|replay
    allowed_modes: str = "both"        # manual|bot|both
    # Jugadores
    max_players_per_room: int = 10
    min_players_to_start: int = 2
    room_wait_timeout_s: int = 90
    vip_only: bool = False
    min_axo_level: int | None = None
    first_time_only: bool = False
    # Comunicación
    broadcast_message: str | None = None
    broadcast_sent: bool = False
    broadcast_sent_at: datetime | None = None
    auto_reminder: bool = True         # notificación 1h antes de cada apertura diaria
    notify_room_start: bool = True
    post_event_summary: bool = True
    # Meta
    is_active: bool = True
    created_by: str                    # user_id del admin
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### 5.4 Lógica de estado de evento activo

**Nota de timezone:** `daily_open_time` / `daily_close_time` se guardan en hora local configurada en el evento (por defecto `America/Mexico_City`). El campo `timezone: str = "America/Mexico_City"` debe añadirse al modelo. La función debe convertir UTC → timezone del evento antes de comparar.

```python
def get_active_event(db: Session) -> ManualModeEvent | None:
    """Devuelve el evento activo en este momento, si existe."""
    now = datetime.utcnow()
    today = now.date()
    current_time = now.time()  # TODO: convertir a timezone del evento

    return db.exec(
        select(ManualModeEvent)
        .where(ManualModeEvent.is_active == True)
        .where(ManualModeEvent.start_date <= today)
        .where(ManualModeEvent.end_date >= today)
        .where(
            or_(
                ManualModeEvent.daily_open_time == None,
                and_(
                    ManualModeEvent.daily_open_time <= current_time,
                    ManualModeEvent.daily_close_time >= current_time,
                )
            )
        )
    ).first()
```

### 5.5 Notificaciones (broadcast)

- **Convocatoria manual**: Admin pulsa *"Enviar convocatoria"* en cualquier momento. Envía notificación push + in-app a todos los jugadores con el `broadcast_message`.
- **Reminder automático**: Si `auto_reminder=True`, el sistema envía una notificación 1h antes de cada apertura diaria del evento.
- **Sala lista**: Cuando se alcanza `min_players_to_start` en una sala, notificación in-app a los jugadores en espera.
- **Resumen post-evento**: Al terminar el último día del evento, notificación con ganadores, total distribuido y próximo evento.

### 5.6 Endpoints admin requeridos

```
POST   /api/v1/admin/events              — crear evento
GET    /api/v1/admin/events              — listar eventos (activos, próximos, pasados)
PATCH  /api/v1/admin/events/{id}         — editar evento
DELETE /api/v1/admin/events/{id}         — cancelar/desactivar evento
POST   /api/v1/admin/events/{id}/broadcast — enviar convocatoria manualmente
GET    /api/v1/admin/events/{id}/stats   — jugadores, partidas, GAL distribuido
```

### 5.7 Endpoint público (para el UI del jugador)

```
GET /api/v1/events/manual-mode
→ { active_event: {...} | null, next_event: {...} | null }
```

---

## 6. SUERTE del Jugador (User-Level)

La SUERTE afecta drops y beneficios a nivel de cuenta del jugador (ej. Gashapón, drops raros). Se calcula como el **promedio de SUERTE de todos sus Axolotitos**.

```python
def player_luck(axolotitos: list[Axolotito]) -> float:
    if not axolotitos:
        return 0.0
    return sum(a.stat_luck for a in axolotitos) / len(axolotitos)
```

**Consecuencia de diseño**: el jugador quiere tener Axolotitos suertudos porque mejoran su propia suerte personal, no solo la de cada bot individual. Incentiva coleccionar y mantener Axolotitos con SUERTE alta.

---

## 7. Ajuste Naturaleza Glotón

La naturaleza Glotón era la única sin penalización de stat. Se ajusta para tener una, como todas las demás:

| Antes | Después |
|-------|---------|
| +30% energía por comida | +30% energía por alimentar, **−10 OJO** |

Justificación: el Glotón está tan enfocado en comer que pierde concentración. Mantiene su identidad de "Axolotito de resistencia" pero con trade-off claro.

Tabla completa de naturalezas actualizada (del spec de 4 stats, incluyendo este ajuste):

| Naturaleza | Modificador |
|---|---|
| 🍀 Suertudo | +10 SUERTE, −5 PILA |
| 🧠 Metódico | +10 OJO, −5 PILA |
| 🍖 Glotón | +30% energía por alimentar, **−10 OJO** |
| 😶 Tímido | −10 SAL al nacer, −5 SUERTE |
| ⚡ Hiperactivo | +25% vel. sueño, −5 OJO |
| 📖 Sabio | +15 PILA, −5 SAL |

---

## 8. Inventario de Archivos Afectados

### Backend — Nuevo

- `models/manual_mode_event.py` — modelo `ManualModeEvent`
- `services/imprinting_service.py` — lógica de delta de stats por evento de partida, `apply_game_to_webito()`
- `services/event_notification_service.py` — broadcasts, reminders, resumen post-evento
- `api/v1/endpoints/admin_events.py` — CRUD de eventos, broadcast manual, stats
- `tests/unit/test_imprinting_service.py` — tests del mapeo evento→stat

### Backend — Modificado

- `models/axolotito.py` — campo `imprinting_games_played`, `imprinting_complete`
- `models/items.py` — `WebitoIncubation`: quitar campos de cooldown care (`last_petting`, etc.)
- `api/v1/endpoints/incubation.py` — flujo de imprinting en lugar de acciones con cooldown; eclosión automática al completar N partidas
- `api/v1/endpoints/game.py` — al terminar partida, si hay Webito en imprinting, llamar `imprinting_service.apply_game_to_webito()`
- `api/v1/endpoints/multiplayer.py` — ídem para partidas multijugador
- `api/v1/endpoints/user.py` — exponer `player_luck()` en el perfil del usuario
- `services/axo_names.py` — natureza + stat dominante influye en el nombre generado
- `scripts/seed_catalog.py` — ajustar nature `gluttony`: agregar `ojo_modifier: -10`

### Frontend — Nuevo

- `components/BirthCeremony.tsx` — secuencia cinematográfica de 7 pasos con variantes por rareza
- `components/ImprintingProgress.tsx` — UI del ADN en progreso durante imprinting
- `pages/admin/events.tsx` — CRUD de eventos con formulario completo

### Frontend — Modificado

- `components/Criadero.tsx` — reemplazar acciones de cuidado por UI de imprinting (seleccionar padrino, ver progreso de partidas)
- `components/tutorial/TutorialFlow.tsx` — alinear con imprinting (las 3 fases son las 3 partidas)
- `components/ManualModeButton.tsx` (nuevo o modificar botón existente) — estado evento activo/cerrado con countdown

---

## 9. Fuera de Alcance (YAGNI)

- Sistema de niveles de Axolotito (confirmado que existe, spec separado).
- Items temporales de boost de stats (diseño de catálogo de items — spec separado).
- Sistema de equipo/accesorios completo (ya existe parcialmente, se extiende en spec separado).
- Múltiples Webitos en imprinting simultáneamente (por ahora: uno a la vez por jugador).
- Imprinting en partidas de torneos o eventos especiales (se trata igual que bot/multi para el delta de stats).
