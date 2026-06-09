# Plan Maestro — Criadero: "Tu Cenote" (Una Cueva que Crece)

> **Contexto:** El diseño actual tiene 6 cuevas separadas con sistema dual-path de desbloqueo. El usuario quiere pivotar a UNA sola caverna que crece con el jugador — más íntimo, más personal, y que integre el hosting de partidas.

---

## 1. Diseño Conceptual

### 1.1 Fantasía Central

Eres guardián de **tu propio cenote**. Empiezas con un pequeño nicho en la roca. Conforme juegas, gastas y demuestras maestría, el cenote se expande — revela nuevas cámaras, más profundidad, más espacio para tus axolotitos. Eventualmente tienes una caverna tan grande que puedes **invitar gente a jugar en tu mesa**.

No es un lobby de slots. Es **tu hogar bajo el agua**.

### 1.2 Layout de la Caverna (vista 2.5D)

```
        ┌────────────────────────────────────────────┐
        │         ☀️ SUPERFICIE (luz cenital)          │
        │  ≈≈≈ rayos de luz ≈≈≈ burbujas ≈≈≈≈≈≈≈≈≈  │
        │                                             │
        │   🦎 axolotitos nadando libremente          │
        │                                             │
        │  ┌──────────────────────────────────┐      │
        │  │     ZONA DE VIDA (Nidos/Lechos)   │      │
        │  │  🥚/🦎  🥚/🦎  🥚/🦎  🥚/🦎     │      │
        │  │  spots fluidos: incubación        │      │
        │  │  o descanso según necesidad       │      │
        │  └──────────────────────────────────┘      │
        │                                             │
        │  ┌──────────────────────────────────┐      │
        │  │     🎴 MESA DE JUEGO              │      │
        │  │  (se desbloquea en nivel 3)       │      │
        │  │  [tablero] [cartas] [fichas]      │      │
        │  └──────────────────────────────────┘      │
        │                                             │
        │  ┌──────────────────────────────────┐      │
        │  │  🏆 EXHIBICIÓN + 👥 VISITANTES    │      │
        │  │  (entrada de la cueva — abajo)    │      │
        │  │  trofeos, axo estrella, visitas   │      │
        │  └──────────────────────────────────┘      │
        │                                             │
        └────────────────────────────────────────────┘
              ↑ entrada por abajo (invertido vs actual)
```

**Por qué la entrada abajo:**
- La luz viene de arriba → el agua se oscurece al bajar → la entrada está en lo más profundo
- Los visitantes "suben" desde la entrada a las zonas sociales
- Narrativa: tu cueva es un tesoro escondido en lo profundo del cenote

**Cambio respecto al Santuario actual:**
- Actual: caves en el fondo (back/front nidos en z-20 y z-40)
- Nuevo: las zonas están organizadas verticalmente. La entrada abajo, los nidos en medio, la superficie arriba.

---

## 2. Sistema de Expansión — 8 Niveles

### 2.1 Niveles

| Nivel | Nombre | Spots | Mesa | Decor Slots | Requisito Clave |
|-------|--------|-------|------|-------------|-----------------|
| 1 | El Nicho | 1 | — | 2 | Inicio (tutorial) |
| 2 | La Gruta | 2 | — | 4 | 10 juegos + 500 FRJ |
| 3 | La Caverna | 3 | 2 jug | 6 | 3 wins + 3-day streak |
| 4 | El Salón | 4 | 4 jug | 8 | 1 jackpot |
| 5 | El Santuario | 5 | 6 jug | 10 | Axo nivel 20 |
| 6 | El Abismo | 6 | 8 jug | 12 | VIP Cualquiera + 50 juegos |
| 7 | El Templo | 7 | 8 jug + custom | 14 | VIP Dorado/Axolite + 100 juegos |
| 8 | Palacio Astral | 8 | 8 jug + torneos | 16 | VIP Axolite + 200 juegos |

### 2.2 Cómo se Expande

Cada expansión no es instantánea — es un **mini-evento de excavación**:

1. Jugador alcanza los requisitos → la siguiente zona muestra un ícono de pico/pala
2. Inicia "Excavación" → timer de X horas (Nivel 1→2: 2h, Nivel 7→8: 48h)
3. Puede acelerar con AXG (1 AXG = -2h)
4. Al completar: **animación de excavación de 5-8 segundos**:
   - Rocas se desmoronan del borde de la cueva
   - Nube de sedimento/polvo enturbia el agua
   - El agua se aclara gradualmente revelando la nueva zona
   - Chispas doradas y sonido de descubrimiento
   - La nueva zona hace "glow up" por primera vez
5. Tutorial integrado presenta la nueva zona

**Diseño de la animación de excavación en capas:**
```
Fase 1 (0-2s): Grietas aparecen en la roca, cámara tiembla sutilmente
Fase 2 (2-4s): Rocas caen, sedimento nubla el agua (overlay marrón 80% opacidad → 0%)
Fase 3 (4-6s): Nueva zona revelada con glow dorado intenso → se atenúa a normal
Fase 4 (6-8s): Partículas de celebración, badge de "Nivel X alcanzado"
```

**Dual path (logro / pago):** Niveles 2-5 tienen atajo de pago con AXG. Niveles 6-8 requieren VIP (no se pueden comprar directamente).

| Nivel | Costo Logro | Costo Pago (AXG) |
|-------|------------|-------------------|
| 2 | 10 juegos + 500 FRJ | 2 AXG |
| 3 | 3 wins + 3-day streak | 3 AXG |
| 4 | 1 jackpot | 5 AXG |
| 5 | Axo nivel 20 | 10 AXG |
| 6 | VIP + 50 juegos | — |
| 7 | VIP Dorado+ + 100 juegos | — |
| 8 | VIP Axolite + 200 juegos | — |

---

## 3. Zona de Vida — Spots Fluidos (Incubación + Descanso Unificados)

### 3.1 El Problema

Al inicio necesitas incubar huevos. Al final tienes 7-8 axolotitos y cero necesidad de incubar. ¿Qué pasa con esos espacios?

### 3.2 Solución: Spots Universales

Cada "spot" en la zona de vida es un **nicho adaptable** que puede estar en 3 modos:

| Modo | Contenido | Visual |
|------|-----------|--------|
| **Incubando** | Un huevo con calor/escarcha | Glow naranja pulsante, partículas |
| **Descansando** | Un axolotito equipado aquí | Glow suave cyan, axo animado |
| **Vacío** | Spot disponible | Brillo tenue, listo para usar |

**Regla de asignación:**
- Spots totales = nivel de cueva
- Spots en incubación = huevos que tienes (capped at spots totales)
- Spots en descanso = axolotitos que quieres exhibir (drag & drop)
- Si tienes 0 huevos, todos los spots pueden ser de descanso
- Si tienes más axolotitos que spots, los extras "guardan" en un estado de fondo (no visibles, pero accesibles desde selector)

### 3.3 Interacciones por Spot

**Tap en spot vacío:** Menú contextual: "Incubar huevo" (si tienes huevos en inventario) o "Traer axolotito" (selector de tus axolotitos)

**Tap en spot con huevo:** Abre EggSheet (ya implementado en Santuario.tsx:611-717)

**Tap en spot con axolotito:** Abre AxoSheet con opciones: Ver/Equipar/Alimentar/Mover/Dormir

**Drag & drop:** Arrastrar axolotitos entre spots para reorganizar

### 3.4 Visualización de Axolotitos — Selección Rápida

**Problema actual:** En Santuario.tsx los axolotitos nadan libremente (posiciones random). Son difíciles de seleccionar, tocar uno pequeño en mobile es frustrante.

**Solución — Doble modo de vista:**

**Modo Libre (default):** Axolotitos nadan como ahora. Animaciones de nado, tamaños variables por profundidad. Toque abre AxoSheet.

**Modo Gestión (toggle):** Axolotitos se alinean en sus spots/lechos. Vista tipo "selección de equipo". Cada uno en su espacio designado, con badge de estado (energía, sueño, expedición). Fácil seleccionar, equipar, alimentar.

El toggle se activa con un botón "Gestionar" / "Vista Libre" en la toolbar.

### 3.5 Alimentación y Cuidados en la Cueva

Actualmente feed/sleep están en PlayMode (AxoStatusBar). Deberían ser accesibles desde la cueva:

- **Tap largo** en un axolotito → menú radial: Alimentar, Dormir, Equipar, Mover, Destacar
- **Alimentar:** Mini modal con Alga Pellet (2 FRJ, +15 energía) y Camarón (10 FRJ, +60 energía)
- **Dormir:** El axo se acuesta en su spot, animación Zzz, timer visible

---

## 4. Sistema de Hosting — "La Mesa"

### 4.1 Vista General

A partir del nivel 3, la cueva tiene una mesa de juego **renderizada en el canvas 2.5D** como parte de la escena del cenote. Se ve físicamente en el fondo, con tablero, cartas, fichas y sillas para los jugadores. Al tocar la mesa, se abre el flujo de hosting/lobby. El dueño puede **hostear partidas con reglas custom**.

**Render de la mesa en la escena:**
- La mesa ocupa la zona central-baja de la cueva (entre zona de vida y exhibición)
- Muestra el nombre de la sala actual (si está hosteando) o "Mesa disponible"
- Sillas/espacios alrededor: 2-8 según nivel, las ocupadas muestran mini avatares de axolotitos
- Efecto de glow cuando hay partida en curso (naranja = esperando jugadores, verde = en juego)
- Al tocar: sheet se despliega con opciones (Hostear / Unirse / Ver sala actual)

### 4.2 Reglas Configurables (Tier Medio)

| Regla | Opciones |
|-------|----------|
| **Tipo de juego** | Lotería Clásica (4x4), Lotería Rápida (2 cartas) |
| **Buy-in** | 10-1000 FRJ (host define min y max) |
| **Jugadores** | 2-8 (según nivel de mesa) |
| **Visibilidad** | Pública (cualquiera) / Amigos / Solo invitados |
| **Velocidad** | Normal / Rápido / Turbo |
| **Patrón de victoria** | Línea, 2x2 cuadrito, 4 esquinas, Full board |
| **Contraseña** | Texto opcional para salas privadas |
| **Nombre de sala** | Texto libre, aparece en lobby |

**No se incluye:** Cartas especiales on/off (complejidad excesiva para MVP).

### 4.3 Creación de Sala (Flujo)

1. Dueño toca la mesa → "Hostear Partida"
2. Modal de configuración con las reglas de arriba
3. Vista previa del buy-in total y comisión de la casa
4. "Abrir Sala" → se crea un `GameRoom` con `host_id = user_id`, las reglas custom se guardan en `room_config JSON`
5. La sala aparece en un nuevo tab del lobby: "Salas de Jugadores" (junto a "Rookie" y "Champion")
6. Otros jugadores pueden buscar, filtrar y unirse

### 4.4 Incentivos del Host

| Beneficio | Detalle |
|-----------|---------|
| 5% del buy-in total | Va directo al host en GAL |
| 1% del jackpot | Si la sala genera jackpot |
| Reputación | +1 por partida hosteada, +5 por sala llena |
| Badge de Anfitrión | Visible en perfil y rankings |
| Mejor visibilidad | Salas de hosts con alta reputación aparecen primero |

### 4.5 Economía del Hosting

- Crear sala es gratis
- La comisión del 5% viene del pozo, no de los jugadores (transparente)
- La casa (treasury) sigue llevando su 5% (host + casa = 10% del pozo)
- Si el host también juega en su propia sala, paga buy-in normal

---

## 5. Zona de Exhibición y Visitantes

### 5.1 Exhibición (Entrada de la Cueva)

Ubicada en la parte inferior (entrada). Visible para visitantes:

- **Axolotito Estrella:** Un axo designado como "destacado" — se muestra grande, con stats y traits
- **Trofeos:** Logros display (primer jackpot, 100 juegos, VIP activo)
- **Tabla de récords:** Mejor racha, mayor jackpot, axo más fuerte

### 5.2 Visitantes

- Cualquier jugador puede visitar la cueva de otro (modo solo lectura)
- Ven la exhibición, los axolotitos, las decoraciones
- Pueden dejar "aplausos" (likes) — máximo 1 por visita
- Si el host está hosteando, pueden unirse a la mesa desde ahí
- **No pueden** interactuar con huevos, alimentar, ni equipar

### 5.3 Privacidad

- Setting global: "Cueva pública" / "Solo amigos" / "Privada"
- La cueva privada igual puede hostear salas públicas (la mesa es independiente)
- Visitantes no ven el nombre real del dueño si tiene alias configurado

---

## 6. Personalización de la Caverna

### 6.1 Decor Slots por Nivel

| Nivel | Decor Slots | Desbloquea |
|-------|------------|------------|
| 1 | 2 | Decoraciones básicas |
| 2 | 4 | — |
| 3 | 6 | Fondo de cueva skin |
| 4 | 8 | Iluminación (color picker) |
| 5 | 10 | Suelo (textura) |
| 6 | 12 | Efectos de partículas |
| 7 | 14 | Música ambiente |
| 8 | 16 | Todo lo anterior + exclusivos VIP |

### 6.2 Tipos de Decoraciones

| Categoría | Ejemplos | Fuente |
|-----------|----------|--------|
| **Naturales** | Algas, corales, rocas, cristales | Tienda (FRJ), logros |
| **Místicas** | Velas, incienso, runas, espejos | Tienda (GAL), eventos |
| **Trofeos** | Copa de Jackpot, Medalla de Racha | Logros |
| **Premium** | Detrás de cada VIP tier | Tienda (AXG), VIP rewards |
| **Evento** | Altar Día de Muertos, Piñata | Eventos temporales |

### 6.3 Decoraciones con Efecto

Algunas decoraciones otorgan micro-bonos. Cap: máximo 5 decoraciones con efecto activas simultáneamente.

| Decoración | Efecto | Rareza |
|------------|--------|--------|
| Algas Sagradas | +3% calor pasivo en incubación | Común |
| Cristal de la Suerte | +2% rareza en huevos nuevos | Poco común |
| Reloj de Arena | -5% tiempo incubación | Poco común |
| Incensario Místico | +5% sabiduría en huevos | Raro |
| Trofeo del Lotero | +1% prob jackpot en mesa hosted | Raro |
| Espejo Astral | 1% rasgo Astral (nivel 7+) | Legendario |
| Altar de la Suerte | +2% todas las stats al eclosionar | Épico |

### 6.4 VIP y Decoraciones Premium

| VIP Tier | Decor Slots Extra | Premium Exclusivas |
|----------|-------------------|---------------------|
| Ninguno | +0 | 0 |
| Coral | +2 (total por nivel) | Fondos "Algas", "Arrecife" |
| Dorado | +4 | + Fondos "Cristal", "Aurora", música custom |
| Axolite | +6 | + Fondos "Astral", "Abismo", todas las músicas, efectos de partículas |

---

## 7. Beneficios Pasivos por Expansión

Cada nivel desbloqueado otorga bonus permanente:

| Nivel | Bonus Permanente |
|-------|-----------------|
| 1 | — |
| 2 | +2% GAL ganado en partidas |
| 3 | +1 carta extra en mano inicial (6 en vez de 5) |
| 4 | +5% probabilidad de booster en juego |
| 5 | +1 slot de incubación global |
| 6 | -5% de comisión P2P en mercado |
| 7 | 1 booster foil gratis por mes |
| 8 | +10% AXG ganado en todo el ecosistema |

---

## 8. Cambios Técnicos Necesarios

### 8.1 Lo que se ELIMINA (Fase 1 — limpieza inmediata)

- `Criadero.tsx` (1067 líneas) — legacy dead code, eliminar archivo + imports en play/page.tsx
- `CenoteCavesPanel.tsx` — ya no hay 6 cuevas separadas, se reemplaza por CaveExpansionPanel
- `webito_slots.py` completo — el sistema de slots individuales desaparece
- `webito_slots_unlocked` en modelo User — reemplazado por `cave_level`
- `SLOT_DEFINITIONS` — reemplazado por `CAVE_LEVEL_DEFINITIONS`
- Referencias a "criadero" en play/page.tsx tabs — renombrar a "Cenote" o similar
- TabId legacy 'criadero' y 'axolotitos' — consolidar en 'santuario' o 'cenote'

### 8.2 Lo que se MODIFICA

- `Santuario.tsx:275-606` — NidoScene se rediseña: entrada abajo, zonas verticales
- `Santuario.tsx:142-270` — NidoCave → SpotFluido (3 modos: incubando/descansando/vacío)
- `Santuario.tsx:498-552` — Axolotitos swimming → doble modo (libre/gestión)
- `Santuario.tsx:611-717` — EggSheet se mantiene, se adapta a spots fluidos
- `Santuario.tsx:722-897` — AxoSheet agrega opciones: alimentar, dormir, destacar
- `User model` — `webito_slots_unlocked` → `cave_level` (int, default 1, max 8)
- `game.py:813-950` — Cave endpoints se adaptan (cave_level en vez de slots)
- `shop_service.py:154` — axo_limit ahora usa cave_level, no VIP bonus directo
- `multiplayer.py` — agregar creación de sala hosted, reglas custom, lobby filter

### 8.3 Lo NUEVO

- `cave_level` en User model (reemplaza webito_slots_unlocked)
- `cave_expansion` endpoint: GET status, POST start, POST accelerate
- `cave_decorations` en User model: JSON con decoraciones por cueva
- `GameRoom.host_id`, `GameRoom.room_config`, `GameRoom.visibility`, `GameRoom.password_hash`
- `POST /multiplayer/create-room` (host crea sala custom)
- `GET /multiplayer/player-rooms` (salas hosted por jugadores)
- `POST /cave/visit/{user_id}` (registrar visita, dejar aplauso)
- `GET /cave/public/{user_id}` (datos públicos de cueva ajena)
- `POST /cave/axolotitos/{id}/move-spot` (mover axo entre spots)
- `POST /cave/axolotitos/{id}/toggle-display` (libre ↔ spot)
- `CaveExpansionPanel.tsx` (reemplaza CenoteCavesPanel)
- `HostingSetupModal.tsx` (configuración de sala)
- `PlayerRoomsLobby.tsx` (listado de salas hosted)

---

## 9. Plan de Implementación

### Fase 1: Refactor del Modelo de Datos (Semana 1)
- [x] 1.1 Agregar `cave_level` a User (default 1), migración Alembic
- [x] 1.2 Migrar datos: `webito_slots_unlocked` → `cave_level` para usuarios existentes
- [x] 1.3 Definir `CAVE_LEVEL_DEFINITIONS` (8 niveles, requisitos, recompensas)
- [x] 1.4 Agregar `cave_decorations` JSON a User
- [x] 1.5 Extender `GameRoom` con `host_id`, `room_config`, `visibility`, `password_hash`
- [x] 1.6 Crear endpoints de expansión: GET/POST cave/expand *(Nota: Falta completar auto-resolución del timer en el backend y conectar botones en frontend)*

### Fase 2: Spots Fluidos y Zona de Vida (Semana 2-3)
- [x] 2.1 Rediseñar NidoScene: entrada abajo, organización vertical *(Implementado en canvas 2.5D)*
- [x] 2.2 SpotsFluidos: componente que soporta 3 modos (incubando/descansando/vacío) *(Componente SpotFluido)*
- [x] 2.3 Lógica de asignación de spots (cuántos incubando vs descansando)
- [x] 2.4 Modo Gestión: axolotitos alineados en spots, fácil selección *(Toggle 'Gestionar' integrado)*
- [ ] 2.5 Menú radial en axolotito (alimentar, dormir, equipar, mover, destacar) *(Parcial: implementado a través de AxoSheet bottom sheet)*
- [ ] 2.6 Drag & drop entre spots
- [ ] 2.7 Animación de excavación al expandir nivel

### Fase 3: Hosting de Partidas (Semana 4-5)
- [x] 3.1 Endpoint `POST /multiplayer/create-room` con reglas custom
- [x] 3.2 Endpoint `GET /multiplayer/player-rooms` con filtros
- [ ] 3.3 Modificar lobby para mostrar "Salas de Jugadores" como tercer tab
- [x] 3.4 `HostingSetupModal.tsx` con todas las reglas configurables
- [x] 3.5 Integrar reglas custom en `simulate_multiplayer_match()`
- [x] 3.6 Sistema de comisión de host (5% del pozo)
- [x] 3.7 Contraseña y sala privada
- [x] 3.8 Reputación de anfitrión

### Fase 4: Exhibición, Visitas y Social (Semana 6)
- [ ] 4.1 Zona de exhibición en la entrada (axo estrella, trofeos, récords)
- [x] 4.2 Endpoint de cueva pública (GET /cave/public/{user_id})
- [ ] 4.3 UI de visita: modo read-only del cenote ajeno
- [ ] 4.4 Sistema de aplausos (likes) *(Backend listo, falta UI)*
- [ ] 4.5 Settings de privacidad (pública/amigos/privada) *(Backend listo, falta UI)*
- [ ] 4.6 Designar axolotito estrella

### Fase 5: Personalización Completa (Semana 7)
- [ ] 5.1 Grid de decoraciones en la cueva (usar CuevaDecorPanel existente como base)
- [ ] 5.2 Catálogo de decoraciones (20+ objetos)
- [ ] 5.3 Backend CRUD para decoraciones
- [ ] 5.4 Decoraciones con efecto (micro-bonos, cap 5)
- [ ] 5.5 Skins de fondo, iluminación, suelo, música
- [ ] 5.6 Integración con VIP para decoraciones premium

### Fase 6: VIP y Endgame (Semana 8)
- [ ] 6.1 Niveles 6-8 requieren VIP (según tier)
- [ ] 6.2 Decoraciones premium por VIP tier
- [ ] 6.3 Beneficios VIP expandidos (decor slots extra, fondos exclusivos)
- [ ] 6.4 Badge de VIP en entrada de cueva
- [ ] 6.5 Torneos (nivel 8)

### Post-MVP: Crianza (Breeding) — Fuera del scope actual
- El breeding (cruzar dos axolotitos para producir huevo con rasgos combinados) se diseña como update post-lanzamiento
- No se incluye en este plan. Se documentará en un plan separado cuando el core esté estable.

---

## 10. Checkpoint de Validación

### Checkpoint 1: ¿La cueva se siente como un hogar?
- [ ] Jugador nombra su cueva
- [ ] Decoraciones son visibles y personales
- [ ] Layout cambia visiblemente con cada expansión
- [ ] Los axolotitos se ven vivos (animaciones, interacciones)

### Checkpoint 2: ¿La progresión es clara?
- [ ] Requisitos de cada nivel visibles y trackeables
- [ ] Primera expansión (nivel 1→2) en ≤3 sesiones
- [ ] Animación de expansión satisfactoria
- [ ] El camino F2P es viable para niveles 1-5

### Checkpoint 3: ¿Hostear es fácil y divertido?
- [x] Crear sala toma <30 segundos
- [x] Reglas custom son claras
- [ ] Las salas hosted son visibles en el lobby *(Falta agregar tab en UI de lobby)*
- [x] El host recibe su comisión correctamente

### Checkpoint 4: ¿VIP agrega valor real?
- [ ] Niveles 7-8 son aspiracionales pero alcanzables
- [ ] Decoraciones premium son deseables
- [ ] Beneficios VIP son visibles para no-VIP (generan deseo)

### Checkpoint 5: ¿Rendimiento 2.5D?
- [ ] 60fps en mobile con 8 axolotitos + decoraciones
- [ ] Transiciones fluidas entre niveles
- [ ] Carga inicial <3 segundos

---

## 11. Decisiones Tomadas

| Decisión | Elección | Justificación |
|----------|----------|---------------|
| Layout de cueva | Una caverna abierta (no túneles) | Aprovecha el Santuario 2.5D actual, menos complejidad |
| Entrada | Por abajo (invertir layout actual) | Narrativa de profundidad, luz de arriba |
| Expansión | Lineal fija (1→2→3...→8) | Balance predecible, tutorial claro |
| Incubación + descanso | Spots fluidos universales | Mismo espacio sirve early y late game, sin zonas muertas |
| Reglas de hosting | Tier medio (buy-in, players, visibilidad, speed, patrones, password, nombre) | Suficiente profundidad sin sobrecomplejizar |
| Cartas especiales en hosting | NO incluir en MVP | Complejidad excesiva para lanzamiento inicial |
| Mesa de juego | Render en canvas 2.5D (no UI overlay) | Inmersión, la mesa es parte del hogar |
| Animación de expansión | Excavación animada (5-8s) | Satisfactoria, física, memorable |
| Breeding | Post-MVP (fuera del plan) | Mantener scope contenido, validar core primero |
| Criadero.tsx legacy | Eliminar en Fase 1 | Sin deuda técnica, el nuevo sistema reemplaza todo |
| CenoteCavesPanel | Eliminar en Fase 1 | Reemplazado por CaveExpansionPanel |
| VIP niveles 7-8 | Exclusivo Dorado (7) y Axolite (7-8) | Valor real al VIP sin bloquear progresión base |
| Decoraciones premium | Los 3 tiers VIP desbloquean categorías | Coral también gana, no solo tiers altos |

---

## 12. Riesgos

| Riesgo | Mitigación |
|--------|------------|
| Muchos axolotitos en pantalla = lag | LOD: axos lejanos se renderizan como siluetas simples |
| Hosting puede fragmentar el pool de jugadores | Las salas oficiales (rookie/champion) siguen existiendo |
| Balance de bonos pasivos | Bonos pequeños (1-5%), no acumulativos sin límite |
| Complejidad de UI con 8 niveles | Progressive disclosure: solo muestras features del nivel actual |
| Migración de datos existentes | webito_slots_unlocked → cave_level es 1:1 mapeable |

---

## 13. Auditoría de Estado y Mejoras Identificadas (Junio 2026)

### 13.1 Estado de Avance Actual
- **Base de Datos y Modelos:** Completado. Se añadieron `cave_level`, `cave_decorations`, etc., y se extendió `GameRoom`.
- **Endpoints Backend:**
  - **Expansión (`cave_expansion.py`):** GET status, POST expand, POST accelerate, GET public y POST visit implementados.
  - **Multiplayer (`multiplayer.py`):** Creación y listado de salas hosted listos.
- **Frontend (`Santuario.tsx`):**
  - Vista 2.5D con capas verticales y entrada en la parte inferior completada.
  - Componente `SpotFluido` interactivo con 3 modos (huevo/axo/vacío) e interfaz en modo Gestión completada.
  - Mesa de juego que invoca `HostingSetupModal.tsx` completada.

### 13.2 Mejoras y Correcciones Críticas Identificadas
1. **Auto-resolución del Timer de Excavación (Backend):**
   * *Problema:* Si el usuario inicia una excavación vía logro y transcurren las horas requeridas, no hay proceso que cambie automáticamente su `cave_level` ni le asigne el huevo de recompensa.
   * *Solución:* En `GET /cave/status`, comprobar si el timer ha expirado. De ser así, realizar la transición al nuevo nivel, persistir en DB, emitir la recompensa y limpiar el estado de excavación activa antes de responder.
2. **Interactividad del Panel de Expansión (Frontend):**
   * *Problema:* El modal de expansión en `Santuario.tsx` muestra los requisitos pero carece de botones y manejadores `onClick` para iniciar la excavación (`POST /cave/expand`) o acelerar (`POST /cave/expand/accelerate`).
   * *Solución:* Convertir los elementos de requisitos en botones ejecutables cuando se cumplan las condiciones, y agregar un botón de acelerar en la sección de progreso.
3. **Tab de "Salas de Jugadores" en Lobby (Frontend):**
   * *Problema:* Las salas hosteadas están en base de datos pero no se muestran en el lobby (`MultiplayerLobby.tsx`), que solo contiene "Novatos" y "Campeón".
   * *Solución:* Introducir un tercer tab ("Salas de Jugadores") que consulte `GET /multiplayer/player-rooms` y permita ingresar contraseña para salas privadas.
4. **Escalamiento del Límite de Axolotitos:**
   * *Problema:* El límite de axolotitos en `shop_service.py` y `vip_scheduler.py` está fijado en un número estático (`7 + VIP`).
   * *Solución:* Ajustar para que el límite sea `cave_level + 6` (nivel 1 = 7, nivel 8 = 14) de modo que expandir el Cenote aumente la capacidad.

### 13.3 Hoja de Ruta Paso a Paso

* **Parte A: Correcciones del Core de Expansión**
  * Auto-resolución de timer en `GET /status` (backend).
  * Añadir botones e interacciones a requisitos de expansión en `Santuario.tsx` (frontend).
  * Ajustar límites de axolotitos dinámicos en `shop_service.py` y `vip_scheduler.py`.
* **Parte B: Lobby Multijugador y Salas de Jugadores**
  * Implementar el tercer tab en `MultiplayerLobby.tsx`.
  * Integrar flujo de unión de salas y contraseña.
* **Parte C: Animación de Excavación y Personalización**
  * Añadir animación visual de excavación en 2.5D (temblor, rocas, agua turbia).
  * Habilitar grid e inventario de decoraciones en la cueva.
* **Parte D: Social y Visitas**
  * Habilitar vista read-only del Cenote de otro jugador.
  * Habilitar sistema de aplausos e indicación de Axolotito Estrella.
