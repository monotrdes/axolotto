# Ideas de Diseño — Junio 2026

> Documento de análisis y recomendaciones para 4 ideas de game design.
> Estado: **propuesta** — sin código implementado.

---

## 1. Imágenes en Metadata de NFTs

### 1.1 Tablas como imagen

**Problema:** Los NFTs `TablasLoteria` (ERC-721) no tienen imagen. El contrato guarda `layoutOf[tokenId]` como `uint256[16]` pero el metadata endpoint no genera visual.

**Propuesta:** Generar imagen composite 4×4 al vuelo, igual que los axolotitos generan SVG dinámico.

**Endpoint sugerido:**
```
GET /api/v1/metadata/tabla/{token_id}.svg
```

**Lógica:**
1. Leer `layoutOf[tokenId]` del contrato (16 card IDs)
2. Cargar las 16 imágenes `.webp` de cartas desde `/public/cartas_loteria/`
3. Componer grid 4×4 con bordes tipo tabla de lotería mexicana
4. Agregar número de token, raridad de la tabla, foil si aplica
5. Servir como `image/svg+xml` o generar PNG con Pillow

**Metadata JSON:**
```json
{
  "name": "Tabla #42",
  "image": "https://api.axolot.to/api/v1/metadata/tabla/42.svg",
  "attributes": [
    {"trait_type": "Cards", "value": [1, 15, 23, 8, ...]},
    {"trait_type": "Edition", "value": "1st Edition"},
    {"trait_type": "Foil", "value": "None"}
  ]
}
```

**Consideraciones técnicas:**
- Reusar patrón de `metadata.py:99-220` (`get_axolotilo_svg`) — ya genera SVG dinámico
- Las 54 cartas `.webp` son estáticas; hay que cargarlas en memoria o cache
- Para PNG: Pillow compone en ~50ms, cachear resultado
- Alternativa más ligera: SVG con `<image href="...">` embebiendo las cartas — más rápido, sin dependencia Pillow
- Si la tabla es Foil/1st Edition, overlay semitransparente encima del grid

### 1.2 Cartas con variantes (1st Edition, Foil)

**Problema:** Las 54 cartas son imágenes `.webp` estáticas. No hay distinción visual/metadata para ediciones especiales.

**Propuesta:** Agregar campos al metadata de `CartasLoteria` (ERC-1155):

```json
{
  "name": "El Axolotl",
  "image": "https://api.axolot.to/api/v1/metadata/carta/1.svg",
  "attributes": [
    {"trait_type": "Card Number", "value": 1},
    {"trait_type": "Edition", "value": "1st Edition"},
    {"trait_type": "Foil", "value": "Holo"},
    {"trait_type": "Rarity", "value": "Legendaria"}
  ]
}
```

**Variantes de imagen por query params:**
```
GET /api/v1/metadata/carta/1.svg?edition=first&foil=holo
GET /api/v1/metadata/carta/1.svg?edition=standard&foil=none
```

**Efectos visuales:**
| Variante | Efecto |
|----------|--------|
| 1st Edition | Borde dorado + sello "1st" en esquina |
| Foil Holo | Overlay arcoíris animado (CSS/SVG) |
| Foil Cosmos | Fondo estrellado + brillo |
| 1st Edition + Foil | Borde dorado + sello + overlay foil |

**Frontend:** Ya existe overlay holo en `LoteriaCard.tsx:241-242` para `is_shiny` y `Legendaria`. Extender para leer `edition` y `foil` del metadata.

**Implementación:**
- Contrato `CartasLoteria.sol`: agregar mapping `cardEdition[tokenId]` y `cardFoil[tokenId]` o codificar en token ID (ej. token ID 1001 = carta 1, 1st edition, foil)
- Backend: endpoint `GET /metadata/carta/{id}.svg` con query params
- Generar SVG con capas: imagen base + overlay edición + overlay foil

---

## 2. Renombrado de Tokens

### 2.1 Estado actual

Contratos duplicados on-chain:
| Contrato | Símbolo | Rol | Estado |
|----------|---------|-----|--------|
| `Axogema.sol` | AXG | Premium | **Activo** |
| `Axoficha.sol` | AXF | Premium (legacy) | Inactivo/duplicado |
| `GemaAlga.sol` | GAL | Game | **Activo** |
| `Frijolito.sol` | FRJ | Game (legacy) | Inactivo/duplicado |

DB backend:
- Columna real: `wallet.axofichas` → property alias `axogemas`
- Columna real: `wallet.frijolitos` → property alias `gemas_alga`

Frontend:
- Muestra GAL como "COR" (Corcholatas) — slang interno
- `CodeEntryPanel.tsx` aún referencia AXF y FRJ

### 2.2 Análisis del naming

**"Axoficha" (AXF) para premium currency:**
- ✅ "Ficha" evoca chip de casino/poker — calza con "dinero real"
- ✅ Axo- prefijo mantiene identidad de marca
- ✅ Fácil de pronunciar, recordar
- ❌ Conflicto menor con "Ficha de Gashapon"

**"Frijolito" (FRJ) para game currency:**
- ✅ Temático: los axolotes comen frijoles en el lore
- ✅ Divertido, memorable, contrasta con "ficha" serio
- ✅ Cultura mexicana: frijol es alimento básico
- ❌ "ito" puede sonar muy infantil para whales

**"Ficha de Gashapon" — el conflicto:**
- La "Ficha de Gashapon" es un ítem consumible (ERC-1155), no una currency ERC-20
- El conflicto es solo semántico: misma palabra "ficha" para dos conceptos distintos
- En contexto: una es currency premium, otra es ticket de máquina tragamonedas

### 2.3 Sugerencia

| Concepto | Nombre | Símbolo | Tipo |
|----------|--------|---------|------|
| Premium currency | **Axoficha** | AXF | ERC-20 |
| Game currency | **Frijolito** | FRJ | ERC-20 |
| Gashapon ticket | **Capsulón** | — | ERC-1155 ítem |
| Slang cariñoso | Corcholata | COR | Solo display |

**Cambios:**
- Renombrar "Ficha de Gashapon" → "Capsulón" o "Moneda Gashapon"
- "Capsulón" sugerido: evoca la cápsula física del gashapon, sin usar "ficha"
- Mantener "COR" como slang en frontend (los jugadores ya lo usan), pero labels oficiales dicen FRJ
- Unificar contratos: migrar `Axogema` → `Axoficha`, `GemaAlga` → `Frijolito`

### 2.4 Plan de migración (2 fases)

**Fase 1 — Backend + Frontend (sin tocar contratos):**
1. Actualizar labels en frontend: "AXG" → "AXF", "GAL" → "FRJ", mantener "COR" como slang
2. Renombrar en `economy.py`: hacer canónicos `axofichas`/`frijolitos`, eliminar aliases confusos
3. Actualizar `CodeEntryPanel.tsx` y cualquier UI que muestre los símbolos viejos
4. Renombrar item gashapon en `shop.py:170`: `"Ficha de Gashapon"` → `"Capsulón"`

**Fase 2 — Contratos (requiere redeploy + migración):**
1. Hacer `Axoficha.sol` el contrato canónico (ya deployado, solo necesita ser adoptado)
2. Hacer `Frijolito.sol` el contrato canónico
3. Migrar balances de `Axogema` → `Axoficha` y `GemaAlga` → `Frijolito`
4. Actualizar `GameController.sol` para usar nuevas direcciones
5. Deprecar contratos viejos (no hacer burn, mantener como legacy)

---

## 3. Patrones de Victoria Expandidos

### 3.1 Estado actual

Tablero 4×4 (16 celdas, índices 0-15):

```
 0  1  2  3
 4  5  6  7
 8  9 10 11
12 13 14 15
```

**Ya implementados en `multiplayer_service.py:23-66`:**

| Patrón | Celdas | Detectado |
|--------|--------|-----------|
| Línea horizontal (4 filas) | 4 c/u | ✅ `check_line()` |
| Línea vertical (4 cols) | 4 c/u | ✅ `check_line()` |
| Diagonal (2) | 4 c/u | ✅ `check_line()` |
| Cuadrito (9 cuadritos 2×2) | 4 c/u | ✅ `check_cuadrito()` |
| Tabla llena | 16 | ✅ Prize 2 |

**Definidos en modelo pero sin lógica (`manual_mode_event.py:29`):**
- `esquinas` — sin detector
- `cruz` — sin detector
- `l_invertida` — sin detector

### 3.2 Nuevos patrones propuestos

```python
# esquinas: 4 esquinas del tablero
WINNING_ESQUINAS = [{0, 3, 12, 15}]

# cruz: fila central + columna central (7 celdas)
WINNING_CRUZ = [{1, 4, 5, 6, 7, 9, 13}]  # índices 1,4,5,6,7,9,13
# realmente: centro H = {4,5,6,7}, centro V = {1,5,9,13}, intersección en 5
# cruz = {1, 4, 5, 6, 7, 9, 13}

# l_invertida: L en cualquier orientación (6 celdas)
# Ejemplo L normal: fila 3 entera + col 0 entera = {12,13,14,15, 0,4,8}
# L invertida H: fila 0 + col 3 = {0,1,2,3, 7,11,15}
# L invertida V: fila 3 + col 3 = {12,13,14,15, 3,7,11}
```

**Tabla completa de patrones:**

| # | Patrón | Celdas | Dificultad | Premio sugerido |
|---|--------|--------|------------|-----------------|
| 1 | Línea (H o V) | 4 | Fácil | 10% del pozo |
| 2 | Diagonal | 4 | Fácil | 10% del pozo |
| 3 | Cuadrito (2×2) | 4 | Medio | 15% del pozo |
| 4 | Esquinas | 4 | Medio | 15% del pozo |
| 5 | L invertida | 6-7 | Difícil | 25% del pozo |
| 6 | Cruz | 7 | Difícil | 25% del pozo |
| 7 | Tabla llena | 16 | Muy difícil | 55% del pozo (jackpot) |

### 3.3 Sistema de reglas por partida

**Modelo propuesto:**

```python
# lobby_models.py — agregar a GameRoom
class GameRoom(Base):
    ...
    win_rules: List[str] = Field(default=["linea", "cuadrito", "tabla_llena"])
    # valores posibles:
    #   "linea", "diagonal", "cuadrito", "esquinas",
    #   "cruz", "l_invertida", "tabla_llena"
    # valor especial: "random" → elige 3-4 al iniciar
```

**Room types sugeridos:**

| Tipo | Reglas | Entry Fee | Pool |
|------|--------|-----------|------|
| Clásica | línea, tabla_llena | 100 FRJ | 160 FRJ |
| Cuadrito | cuadrito, línea, tabla_llena | 200 FRJ | 350 FRJ |
| Random | random 3-4 patrones | 150 FRJ | 250 FRJ |
| Full House | todos los patrones | 500 FRJ | 800 FRJ |
| Custom | definido por host | variable | variable |

**Frontend:** Mostrar reglas activas como íconos en la room card del lobby (`SalaSelectScreen.tsx`, `MultiplayerLobby.tsx`).

**Implementación inmediata:**
- `multiplayer_service.py`: agregar `check_esquinas()`, `check_cruz()`, `check_l_invertida()`
- `game.py`: mismos detectores para solo/CPU mode
- Tests: extender `test_multiplayer_service.py` con tests para nuevos patrones

---

## 4. Player-Hosted Games: Cuevita Host

> 💡 **"La cuevita del axolotito que va a jugar es la casa host"**

### 4.1 Concepto

Cada Axolotito tiene su **cuevita** (cave/burrow) en el cenote. El dueño puede:
- Decorarla con muebles y objetos comprados en la tienda
- Hostear partidas de lotería dentro de su cuevita
- Configurar reglas, entry fee, y premios
- Otros jugadores visitan la cuevita para jugar

**Loop de engagement:**
```
Jugar → Ganar FRJ → Comprar muebles → Decorar cuevita → 
→ Atraer más jugadores → Más partidas → Más FRJ → ...
```

### 4.2 Sistema de decoración

**Estado actual:** `axolotito.cave_items` (JSON, max 3 ítems), `CuevaDecorPanel.tsx` (placeholder).

**Propuesta de expansión:**

Categorías de ítems decorativos (`ItemType.CAVE_ITEM`):

| Categoría | Ejemplos | Slots | Precio (FRJ) |
|-----------|----------|-------|-------------|
| Mesas | Mesa rústica, Mesa de poker, Mesa dorada | 1-3 | 200-5000 |
| Sillas | Banquito, Silla acolchada, Trono | 2-8 | 100-3000 |
| Iluminación | Velita, Lámpara de lava, Candelabro | 1-4 | 150-2000 |
| Pared | Póster lotería, Ventana al cenote, Tapiz | 1-6 | 100-1500 |
| Suelo | Tapete, Alfombra mágica, Piso de mosaico | 1-2 | 300-4000 |
| Especial | Bocina, Fogata, Fuente de axolote | 1-2 | 1000-10000 (AXF) |

**Grid de decoración:**
- Tamaño: 8×6 tiles (48 slots)
- Ítems ocupan N×M tiles según tipo
- Sistema drag & drop en frontend (ya esbozado en `CuevaDecorPanel.tsx`)
- Guardar layout como JSON: `cave_layout: [{item_id, grid_x, grid_y, rotation}]`

**Ítems premium (AXF):**
- Efectos visuales especiales (partículas, animaciones)
- Música ambiente para visitantes
- Temas completos: "Cueva de Cristal", "Fiesta Mexicana", "Abismo Cósmico"

### 4.3 Hosting de partidas

**Flujo:**
1. Dueño entra a su cuevita → botón "Hostear Partida"
2. Configura:
   - **Reglas de victoria:** checkboxes de patrones (línea, cuadrito, esquinas, etc.)
   - **Entry fee:** slider 50-1000 FRJ
   - **Max jugadores:** 4, 8, 12, 16, o 30
   - **Premio base:** aportación del host al pozo (opcional, atrae jugadores)
   - **Visibilidad:** pública o solo amigos/invitados
3. La sala aparece en el lobby con:
   - Nombre del host + avatar del axolotito
   - Preview de la cuevita (thumbnail)
   - Reglas activas como íconos
   - Entry fee y pozo actual
   - Jugadores registrados / capacidad

**Economía del host:**
- Host gana % de comisión por cada partida (ej. 5% del pozo)
- Host no paga entry fee en su propia sala (o paga con descuento)
- Cuevitas más decoradas = mejor visibilidad en lobby = más jugadores

### 4.4 Lobby de rooms player-hosted

Extender `SalaSelectScreen.tsx` con tabs/filtros:

```
[ Salas Oficiales ] [ Cuevitas Host ] [ Mis Salas ]
```

**Filtros:**
- Entry fee: bajo / medio / alto
- Reglas: clásica / cuadrito / random / full house
- Decoración: ⭐ a ⭐⭐⭐⭐⭐ (basado en ítems equipados)
- Reputación del host (ver 4.5)

**Room card** muestra:
- Thumbnail de la cuevita (generado como SVG del layout)
- Avatar del axolotito host
- Estrellas de decoración
- Entry fee + pozo
- Jugadores: 5/12

### 4.5 Reputación de host (opcional, fase 3)

Sistema simple de 1-5 estrellas:
- Jugadores califican al host después de cada partida
- Criterios: ¿reglas justas? ¿buena decoración? ¿lag?
- Promedio móvil de últimas 20 partidas
- Hosts con < 2 estrellas pierden visibilidad en lobby

### 4.6 Fases de implementación

**Fase 1 — Decoración expandida (2-3 semanas)**
- Extender `cave_items` a grid-based layout (JSON)
- Crear catálogo inicial de 15-20 ítems en `ItemCatalog`
- Actualizar `CuevaDecorPanel.tsx` con grid interactivo funcional
- Store: sección "Muebles y Decoración"

**Fase 2 — Hosting básico (3-4 semanas)**
- Modelo `HostedRoom`: extiende `GameRoom` con `host_axolotito_id`, `cave_layout_snapshot`
- Backend: crear/cerrar sala host, configurar reglas
- Frontend: formulario de creación de sala en cuevita
- Lobby: tab "Cuevitas Host" con rooms player-hosted
- Integrar con el scheduler de `multiplayer_service.py`

**Fase 3 — Descubrimiento y reputación (2-3 semanas)**
- Thumbnails dinámicos de cuevitas
- Sistema de calificación post-partida
- Filtros avanzados en lobby
- Eventos especiales: "Mejor Cueva del Mes"

---

## 5. Priorización

| Idea | Impacto | Esfuerzo | Prioridad |
|------|---------|----------|-----------|
| Patrones de victoria | Alto — más variedad de juego | Bajo (3-4 días) | 🥇 **YA** |
| Imágenes en NFTs | Medio — valor coleccionable | Medio (1-2 sem) | 🥈 |
| Renombrado tokens | Medio — identidad de marca | Medio (1-2 sem) | 🥉 |
| Cuevita Host | Muy Alto — UGC + retención | Muy Alto (2-3 meses) | 🏆 **Big Feature** |

**Recomendación:** Implementar patrones de victoria ya (es código mostly existente). Renombrado + imágenes en paralelo. Cuevita Host como feature flagship del Q3 2026.

---

## 6. Referencias

- `backend/app/services/multiplayer_service.py:23-66` — WINNING_LINES, WINNING_CUADRITOS, check_line, check_cuadrito
- `backend/app/api/v1/endpoints/metadata.py:99-220` — Patrón de SVG dinámico (axolotito)
- `backend/app/models/manual_mode_event.py:29` — win_condition con valores pre-definidos
- `backend/app/models/axolotito.py:64` — cave_items (JSON, max 3)
- `frontend/components/world/hud/CuevaDecorPanel.tsx` — UI placeholder de decoración
- `frontend/components/ui/LoteriaCard.tsx:27-80` — CARD_IMAGE mapping + holo overlay
- `docs/completed/nido_design.md` — Diseño del cenote 2.5D
- `docs/completed/GDD.md` — Game Design Document
- `docs/completed/AXOLOTTO_BIBLE.md` — Biblia completa del juego
