# Rediseño del Sistema de Stats del Axolotito: 8 → 4 Stats

> **Spec de diseño.** Estado: aprobado por el dueño del producto. Fecha: 2026-05-31.
> **Ver también:** `GDD.md` (§2 Axolotitos), `AXOLOTTO_BIBLE.md` (§3), `00_PLAN_GAMIFICACION.md` (Natures), `tutorial_onboarding_prompts.md` (tutorial).

---

## 1. Objetivo

Reducir los 8 stats actuales del Axolotito a **4 stats** con nombres en español mexicano casual que un jugador hyper-casual entienda a la primera, sin tutoriales. Cada stat debe tener **impacto real y visible en cada partida**. Eliminar los stats que hoy son puramente decorativos o tienen impacto insignificante.

### Problema actual

De los 8 stats existentes, solo 5 tienen mecánica real y 2 son puramente narrativos:

| Stat actual | Estado real |
|---|---|
| `stat_luck` | ✅ Activo (críticos, drops, bonus premio) |
| `stat_focus` | ✅ Activo (ventana de marcado, miss chance) |
| `stat_stamina` | ✅ Activo (energía máxima, pistas) |
| `stat_salinity` | ✅ Activo (drena energía post-partida) |
| `stat_agility` | ✅ Activo (velocidad del gritón, mitigation) |
| `stat_charisma` | ⚠️ Impacto mínimo (descuento tienda máx 10%) |
| `stat_wisdom` | ❌ Solo narrativa (diálogos, nombres, +staking insignificante) |
| `stat_strength` | ❌ Solo narrativa (diálogos, nombres, mitigation incubación) |

---

## 2. Los 4 Stats Finales (Opción "El Refrán Mexicano")

| Stat | Ícono | Origen | Rango | Default |
|---|---|---|---|---|
| **SUERTE** | ✨ | `stat_luck` | 0–100 | 10 |
| **OJO** | 👁️ | `stat_focus` (+ absorbe `stat_agility`) | 0–100 | 50 |
| **PILA** | 🔋 | `stat_stamina` | 50–200 | 100 |
| **SAL** | 🧂 | `stat_salinity` (⚠️ se quiere BAJA) | 0–100 | 5 |

**Retirados:** `stat_charisma`, `stat_wisdom`, `stat_strength`, `stat_agility` (este último fusionado en OJO).

### Justificación de nombres
- **SUERTE** — universal, directo.
- **OJO** — "¡mucho ojo!" = pon atención. Cubre precisión y concentración.
- **PILA** — "échale pila" = ponle energía. Cubre resistencia.
- **SAL** — "estar salado" = tener mala suerte. Es el anti-stat perfecto, culturalmente obvio sin explicación.

---

## 3. Mecánicas por Stat

### ✨ SUERTE (0–100)
- **Bot/Multi:** bonus sobre el premio al ganar (`luck/1000 × premio`).
- **Drops:** probabilidad de ítems raros al terminar partida.
- **Gashapón:** pequeño bonus a la rareza de rolls (absorbe lo que hacía Carisma como "beneficio de tienda").
- **Manual:** **sin crits** durante la partida (ver §5). Solo afecta drops post-partida.

### 👁️ OJO (0–100, absorbe Agility)
- **Bot/Multi:** miss chance 0–30% al marcar cartas cantadas (`max(0, min(0.3, (100-ojo)*0.003))`).
- **Al nacer:** `stat_agility` se setea igual a `stat_focus` para que ambos campos reflejen el mismo OJO. La lógica que leía `stat_agility` ahora lee el mismo valor.
- **Manual:** **sin efecto** durante la partida (ver §5).

### 🔋 PILA (50–200)
- **Energía máxima:** cuántas partidas puede jugar antes de dormir (igual que hoy).
- **NUEVO — Velocidad de recuperación:** PILA alta = duerme menos tiempo para recuperar 100%.
  - Fórmula: `sleep_mult = clamp(1.0 - ((pila - 50) / 300), 0.35, 1.0)`.
  - PILA 50 → 100% del tiempo base. PILA 100 → ~83%. PILA 200 → 50% (mínimo 35% con clamp).
- **Manual:** la energía sigue siendo el límite de sesión (cada partida consume energía).

### 🧂 SAL (0–100, se quiere BAJA)
- **Post-partida (todos los modos):** drena energía extra `round(sal × 0.2)` = hasta 20 pts (igual que hoy).
- **Solo/Bot — Deck bias:** las cartas del tablero del Axolotito tienden a desplazarse a la segunda mitad del mazo. Prob por carta en la primera mitad: `sal/200` (máx 50%). Ver §4.
- **Multijugador — Slip:** cuando se canta una carta del tablero, prob. `sal/300` (máx 33%) de que "se escape" y no se marque. Roll independiente del miss chance de OJO. Ver §4.
- **Multijugador — Entropía de sala:** el SAL promedio de todos los Axolotitos determina el caos de la partida (efecto emergente; ver §4).
- **Manual:** **sin deck bias** durante la partida. Solo drena energía post-partida (ver §5).

---

## 4. Mecánica de SAL en Detalle

### 4.1 Modo Solo / Bot — Deck Bias
El mazo de 54 cartas se baraja normalmente. Luego, para cada Axolotito con SAL > 0, cada carta de su tablero que caiga en la primera mitad del mazo tiene probabilidad `sal/200` de intercambiarse con una posición aleatoria de la segunda mitad. El jugador no ve el orden del mazo — solo percibe que "las cartas no le salen". Parece mala suerte, no un penalizador explícito.

Función nueva: `_apply_sal_bias(deck, board_card_ids, sal, rng)`, llamada justo después de `rng.shuffle(deck)`.

### 4.2 Multijugador — Por qué NO se usa deck bias
El mazo es compartido. Si dos jugadores comparten una carta y tienen SAL distinta, el orden del mazo no puede satisfacer a ambos. El deck bias por jugador es irresoluble en multi. Se usan dos mecánicas independientes:

**Slip individual** (`sal/300`, máx 33%): roll por jugador, independiente. Cuando el gritón canta una carta del tablero de un Axolotito salado, existe esa probabilidad de que no se marque ("se le escapó"). Se ejecuta justo después del check de miss chance de OJO en el loop de cartas (`multiplayer_service.py` ~línea 320). Ambos rolls pueden fallar — un Axolotito con SAL 80 + OJO 20 es muy débil.

**Entropía de sala** (efecto emergente): `room_entropy = avg(SAL de todos) / 100`. A mayor entropía, más slips totales en la sala, resultados más impredecibles, los underdogs tienen chance y los favoritos pueden caer. Se expone en el UI como un indicador de "tipo de sala" (Limpia / Mixta / Salada). Crea estrategia de selección de sala sin diseñarla explícitamente: jugadores limpios evitan salas saladas (su ventaja se diluye), jugadores salados prefieren entrar con otros salados.

---

## 5. División Manual vs Bot (decisión de diseño clave)

**En modo manual, el jugador ES el Axolotito.** Sus reflejos y conexión a internet son el verdadero stat. Aplicar modificadores de stat durante una partida manual sería injusto (castiga al jugador hábil con Axolotito débil; premia al malo con Axolotito fuerte). Por tanto:

| Stat | Bot / Multi | Manual (en partida) | Manual (post-partida / sesión) |
|---|---|---|---|
| ✨ SUERTE | bonus premio + drops | sin efecto | drops raros |
| 👁️ OJO | miss chance | sin efecto | — |
| 🔋 PILA | energía + recuperación | — | energía máx (límite de sesión) + recuperación |
| 🧂 SAL | deck bias / slip + drena | sin deck bias / slip | drena energía |

**Consecuencia técnica:** `manual_game_service.py` (calcula ventana, delay del gritón, hints, crits desde stats) **deja de ser necesario para cálculos de stat**. El modo manual corre con un set fijo de constantes estándar para todos. El servicio se simplifica o se elimina junto con sus llamadas.

---

## 6. Naturalezas (Natures) — Ajuste de Modificadores

Las 6 naturalezas se reajustan para usar solo los 4 stats nuevos:

| Naturaleza | Modificador (nuevo) | Cambio respecto al actual |
|---|---|---|
| 🍀 Suertudo | +10 SUERTE, -5 PILA | era -5 Agility → ahora -5 PILA |
| 🧠 Metódico | +10 OJO, -5 PILA | sin cambio conceptual (focus→ojo) |
| 🍖 Glotón | +30% energía por comida, sin penalización | era -5 Wisdom → penalización eliminada |
| 😶 Tímido | -10 SAL al nacer, -5 SUERTE | era -5 Charisma → ahora -5 SUERTE |
| ⚡ Hiperactivo | +25% vel. sueño, -5 OJO | sin cambio (focus→ojo) |
| 📖 Sabio | +15 PILA, -5 SAL | rediseño completo (era +Wisdom/-Charisma) |

---

## 7. Loop de Cuidados del Criadero

1 acción de cuidado = 1 stat claro:

| Acción | Cooldown | Stat que sube |
|---|---|---|
| 🤲 Acariciar | 4h | 👁️ OJO |
| 🎵 Cantarle | 8h | ✨ SUERTE |
| 🍤 Alimentar | 12h | 🔋 PILA |
| 🌊 Karma tutorial | al nacer | 🧂 SAL (alta o baja) |

**Mapeo de campos `bonus_*` existentes (sin migración de DB):**
- `bonus_focus` + `bonus_agility` → ambos suman a OJO al nacer.
- `bonus_wisdom` → se redirige a SUERTE (sabiduría → fortuna).
- `bonus_luck` → SUERTE.
- `bonus_stamina` → PILA.
- `bonus_strength` → se ignora (queda en 0).

**Reducir SAL:** solo con consumibles (Gotas Anti-sal), la naturaleza Tímido, y equipo tipo "eyes" con `bonus_sal` negativo.

---

## 8. Fórmula de Poder (Ranking)

```
Poder = SUERTE + OJO + PILA + (100 − SAL)
```
SAL se invierte: menos sal = más poder. Máximo teórico: `100 + 100 + 200 + 100 = 500`.

---

## 9. Estrategia de Base de Datos (sin migración riesgosa)

- Las columnas `stat_wisdom`, `stat_strength`, `stat_charisma`, `stat_agility` **se mantienen** en PostgreSQL.
- Para Axolotitos nuevos: `stat_agility = stat_focus` (mismo OJO); `stat_wisdom`, `stat_strength`, `stat_charisma` se congelan en 0.
- La ABI de la chain **no cambia** (sigue minteando los 8 campos del struct; los 4 retirados van en 0 / espejo).
- Cero `ALTER TABLE`, cero riesgo de pérdida de datos en producción.
- El UI y las API responses solo exponen los 4 stats con nombres nuevos.

---

## 10. Integración con el Tutorial (ya avanzado)

El tutorial existente (`TutorialFlow.tsx`, `TutorialCpuGame.tsx`, `tutorial_service.py`) ya enseña en 3 fases + karma + eclosión. Está **muy alineado** con los 4 stats:

| Fase tutorial actual | Stat enseñado | Acción de migración |
|---|---|---|
| Fase 1: Salinidad | 🧂 SAL | renombrar label "Salinidad" → "Sal" (opcional, ya es correcto) |
| Fase 2: Concentración (Focus+Agility) | 👁️ OJO | renombrar "Concentración" → "Ojo"; fusionar agility en ojo |
| Fase 3: Suerte (Luck+Stamina) | ✨ SUERTE + 🔋 PILA | renombrar para reflejar SUERTE/PILA |
| Karma reveal (lucky/salty) | define SAL inicial | sin cambio — ya funciona |

Props del componente (`bonusFocus`, `bonusAgility`, etc.) se consolidan a los 4 nuevos. El karma sigue determinando SAL alta/baja al nacer.

---

## 11. Inventario de Archivos Afectados

### Backend
- `models/axolotito.py` — comentarios/labels (columnas DB sin cambio).
- `models/items.py` — comentarios de `bonus_*` en `WebitoIncubation`.
- `services/manual_game_service.py` — simplificar/eliminar (ya no calcula desde stats).
- `services/shop_service.py` — eliminar `charisma_discount` (líneas ~193–194).
- `services/dialogue_engine.py` — quitar bancos "wisdom"/"strength"; renombrar "focus"→"ojo", "salinity"→"sal".
- `services/axo_names.py` — quitar "strength"/"wisdom"/"charisma"/"agility"; agregar "ojo"/"pila".
- `services/tutorial_service.py` — consolidar a 4 stats; mapear bonus a SUERTE/OJO/PILA.
- `services/multiplayer_service.py` — añadir slip de SAL + entropía de sala; renombrar keys JSON.
- `api/endpoints/incubation.py` — eclosión: `agility=focus`, `bonus_wisdom→suerte`, quitar `strength_mitigation`; respuesta 4 stats.
- `api/endpoints/game.py` — quitar `stat_wisdom` del miss_chance; añadir `_apply_sal_bias`; agility derivado de OJO.
- `api/endpoints/multiplayer.py` — renombrar keys JSON; slip de SAL.
- `api/endpoints/board.py` — eliminar `wisdom_bonus` del staking.
- `api/endpoints/ranking.py` — nueva fórmula de poder; limpiar JSON a 4 stats.
- `api/endpoints/metadata.py` — exponer solo 4 stats en metadata NFT.
- `api/endpoints/admin.py` — mostrar 4 stats (mantener 8 ocultos para admin).
- `scripts/seed_catalog.py` — `item_metadata`: `bonus_wisdom→bonus_suerte`, `bonus_charisma→bonus_suerte`, `bonus_agility→bonus_ojo`.
- `tests/` — renombrar `stat_focus`/`stat_agility` en fixtures; nuevos tests de slip/deck bias/recuperación.

### Frontend
- `components/AxoStatusBar.tsx`, `Santuario.tsx`, `Criadero.tsx`, `Inventory.tsx`, `Inventory_.tsx`, `MarketP2P.tsx`, `screens/AxoSelectScreen.tsx`, `screens/BoardSelectScreen.tsx`, `screens/CpuSimScreen.tsx` — mostrar 4 stats con nuevos nombres/iconos.
- `components/tutorial/TutorialFlow.tsx`, `TutorialCpuGame.tsx`, `dialogues.ts` — consolidar props a 4 stats; renombrar labels de fase.

---

## 12. Pilares de Gamificación

1. **Comprensión inmediata** — 1 ícono + 1 palabra por stat. SAL es la única barra roja (el jugador la quiere baja sin leer nada).
2. **Loop de cuidado claro** — 3 acciones, 3 stats, sin ambigüedad.
3. **Builds por naturaleza** — cada naturaleza especializa un stat; coleccionismo estratégico sin números.
4. **Sin stat inútil** — cada stat pesa en cada partida; el casual siente la diferencia sin entender la fórmula.

---

## 13. Fuera de Alcance (YAGNI)

- No se migran ni borran columnas de DB.
- No se cambia la ABI de los contratos.
- No se rediseña el sistema de equipo/accesorios más allá de remapear `bonus_*` en `seed_catalog.py`.
- No se añaden stats nuevos más allá de las dos mecánicas nuevas (recuperación PILA, slip/entropía SAL).
