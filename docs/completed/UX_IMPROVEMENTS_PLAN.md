# Plan: UX Improvements — Botones, Cartas, Notificaciones, Santuario

## 1. Hold-to-Confirm en botones de compra/gasto

### Problema
Compras y gastos costosos se disparan con un solo tap. No hay confirmación y es difícil deshacer.

### Solución: Componente `HoldButton`

Un botón que requiere mantener pulsado ~1 segundo para ejecutar. Mientras se mantiene:
- Se llena progresivamente (anillo circular o barra interior)
- Crece ligeramente con scale (feedback táctil visual)
- Al completar: vibración leve (haptics) + ejecuta la acción

**Implementación:**
- Nuevo componente `frontend/components/ui/HoldButton.tsx`
- Props: `onConfirm`, `duration` (ms, default 1000), `label`, `variant`, `className`
- CSS: `@keyframes fill` + `transform: scale(1 → 1.05)` durante el hold
- Usar `onPointerDown` / `onPointerUp` / `onPointerLeave` para cross-device

```typescript
// Uso básico
<HoldButton
  onConfirm={handlePurchase}
  duration={1000}
  label="Comprar — 50 GAL"
  variant="danger"
/>
```

**Dónde aplicar:**
- Comprar booster/sobre en Store
- Comprar Axolotito en Market P2P
- Comprar tablero en Market P2P
- Abrir cápsula (bola de cobre/plata/oro)
- Gashapon roll (premium)
- Desarmar tablero (dissolve)
- Vender/listar tablero o axolotito en market
- Entrada a sala Champion (50 GAL)

**Acciones que NO necesitan HoldButton** (reversibles o baratas):
- Confirmar nickname
- Marcar favorito
- Abrir inventario
- Sala Rookie (bajo costo)

---

## 2. Cartas más grandes

### Problema
Las cartas de lotería están demasiado pequeñas, especialmente en el tablero durante el juego. Difícil ver el emoji y nombre.

### Solución: Escala x2 configurable

- `LoteriaCard.tsx`: revisar tamaños base. Actualmente probablemente 40-60px. Target: 80-120px en game view.
- `BoardCardGrid.tsx`: ajustar grid columns para acomodar cartas más grandes
- `LoteriaBoard.tsx`: ajustar `cardSize` prop defaults
- CpuSimScreen: el board principal del jugador debería usar cards más grandes. Los mini-boards de bots pueden quedarse pequeños.
- Responsive: en móvil, las cartas en el tablero principal = ~70px, en escritorio = ~90px

**Ajustes:**
- `cardSize` default en `LoteriaBoard`: de ~`sm` a `md` o `lg`
- `CpuSimScreen` player board: `cardSize={80}` (actualmente ~40)
- Texto del nombre de la carta: aumentar de `text-[7px]` a `text-[10px]` o similar

---

## 3. Fix autosort axolotitos al alimentar

### Problema
En la pantalla de selección de axolotito (`AxoSelectScreen.tsx`), al dar de comer a un axolotito, la lista se re-ordena (probablemente por `energy` o algún stat que cambia). Esto causa un salto visual molesto.

### Análisis
La lista probablemente usa `useState([...axolotitos].sort(...))` o tiene un `useEffect` que re-aplica el sort cuando los datos cambian. Dar de comer actualiza la energía → re-sort.

### Fix
- Fijar el orden de la lista al **nivel del axolotito** (`axo.level`) al momento del render inicial
- No re-sortear en respuesta a cambios de energía/hambre
- El nivel no cambia por comida, es estable
- Si el usuario quiere re-ordenar: botón manual de sort

```typescript
// Sort estable al cargar, no reactivo a cambios de energía
const [sortedAxos, setSortedAxos] = useState(() => 
  [...axolotitos].sort((a, b) => b.level - a.level || b.xp - a.xp)
);
// Al alimentar: actualizar solo el axo afectado en el array, no re-sortear
```

---

## 4. Notificaciones con sonido en ganancias/pérdidas/compras

### Problema
Cuando el jugador gana GAL, pierde GAL, compra algo, o recibe un premio, no hay feedback auditivo ni visual rápido. La experiencia se siente silenciosa.

### Solución: Sistema de toast + sonido

**Componente `EconomyToast`** (o extender el sistema de toast existente):
- Aparece 2-3 segundos, luego fade out
- Posición: arriba centrado o esquina superior derecha
- Variantes:
  - `gain`: verde, ✅ icono, "+" sound
  - `loss`: rojo/naranja, 💸 icono, "whoosh" sound
  - `purchase`: azul, 🛒 icono, "ding" sound
  - `legendary`: dorado parpadeante, ⚔️ icono, "fanfare" sound

**Sonidos (Web Audio API):**
- No usar archivos de audio externos. Generar con `AudioContext` + oscilladores:
  - Ganancia: tono ascendente (do-mi-sol, 200ms cada nota)
  - Pérdida: tono descendente (sol-mi-do, 200ms cada nota)
  - Compra: "ding" corto (440Hz, 150ms)
  - Legendario: chord complejo (4 notas, 500ms)
- Respetar `prefers-reduced-motion` / silencio del sistema (mute si no hay interacción previa del usuario)

**Trigger points:**
- Ganar partida CPU → toast "gain" con cantidad GAL
- Perder partida CPU → toast "loss"
- Comprar booster/cápsula → toast "purchase"
- Abrir sobre y recibir carta rara → toast "legendary" si Épico+
- Recibir Tabla Forjada en gashapon → toast "legendary" especial
- Ganar racha bonus → toast "gain" con "+X% bonus"

**Hook reutilizable:** `useEconomyToast()` → `{ showGain(amount, currency), showLoss(amount, currency), showPurchase(label), showLegendary(label) }`

---

## 5. Santuario/Nido: Cuevas como habitaciones de Axolotitos

### Problema
Actualmente el Santuario tiene cuevas donde solo viven Webitos. El límite es 7 axolotitos+webitos. Las cuevas parecen subutilizadas — solo sirven de "contenedor" visual.

### Nueva Visión: Cada Axolotito tiene SU cueva

Cuando un Webito nace (incuba y hace eclosión), la cueva en la que estaba pasa a ser la **habitación permanente** de ese Axolotito.

**Características de la cueva-habitación:**
- Muestra al Axolotito descansando/durmiendo ahí
- Nombre de la cueva = nombre del Axolotito
- **Slot de equipamiento**: cada cueva tiene 1-3 slots para objetos decorativos/funcionales obtenibles del gashapon
- Los objetos equipados dan pequeños bonos de stats o son puramente cosméticos

**Items de equipo para cuevas** (nuevos tipos en ItemCatalog):
- 🛏️ **Cama de algas** — +5% recovery de energía al dormir
- 🌊 **Cascada miniatura** — +3 stat_wisdom pasivo
- 🪨 **Roca sagrada** — activa Lucky Save extra (1 por partida)
- 🐟 **Acuario auxiliar** — reduce costo de alimentación 10%
- 🎋 **Bambú de la suerte** — +2% GAL en victorias
- 🌿 **Jardín de musgo** — cosmético, animación especial en la cueva

**Obtención:** exclusivamente desde Gashapon (cápsula oro y plata), rareza EPIC y LEGENDARY.

**UI en Santuario:**
- Click en cueva → modal "Habitación de [Axo Name]"
- Muestra axolotito con sus stats, energía, racha
- Sección "Equipamiento" con los slots disponibles (1 slot a nivel 1, +1 slot por cada 5 niveles del axolotito)
- Drag & drop o click para equipar/desequipar items del inventario
- Items no equipados van al inventario normal

**Backend:**
- Nuevo modelo `AxoCaveEquipment` o campo `cave_items: List[int]` en Axolotito (JSON, item IDs equipados)
- Nuevos tipos en ItemType enum: `CAVE_ITEM`
- Endpoint `POST /axolotitos/{axo_id}/cave/equip` y `unequip`
- Calcular bonos de stats en `play_match()` considerando cave items equipados

**Relación con Webitos:**
- Mientras el huevo está incubando, la cueva es del Webito
- Al nacer → cueva pasa al Axolotito recién nacido
- Si el Axolotito se vende en el market, ¿la cueva queda vacía? → opción de incluir/excluir el item equipado en la venta

---

## Ideas adicionales y mejoras

### Sobre HoldButton
- Timer visual con countdown "3... 2... 1..." para acciones muy destructivas (dissolve tablero)
- Mensaje de contexto dentro del botón mientras se mantiene: "Suelta para cancelar / Mantén para confirmar"
- Color que cambia progresivamente: gris → rojo durante el hold

### Sobre Notificaciones
- Stack de toasts: si hay múltiples ganancias rápidas (streak bonus + win prize), apilarlas
- Historial de notificaciones: icono campana con badge que muestra últimas 10 transacciones
- "Quiet hours": configuración para silenciar sonidos en ciertos horarios

### Sobre Santuario
- **Exploración de cuevas**: animación al entrar a la cueva (zoom in + transition)
- **Cueva compartida (futuro)**: 2 axolotitos pueden compartir cueva si son de la misma especie — bonus de sinergia
- **Niveles de cueva**: la cueva mejora visualmente conforme el axolotito sube de nivel (más decoraciones automáticas)
- **Visitantes**: si tienes tablero rentado a otro jugador, su Axolotito "visita" tu santuario

---

## Fases de implementación

| Fase | Feature | Archivos | Prioridad |
|------|---------|----------|-----------|
| 1a | `HoldButton` componente | `ui/HoldButton.tsx` | Alta |
| 1b | Aplicar HoldButton en compras clave | Store, Market, Shop, CpuSim | Alta |
| 2 | Cartas más grandes | LoteriaCard, BoardCardGrid, LoteriaBoard, CpuSimScreen | Alta |
| 3 | Fix autosort axolotitos | AxoSelectScreen.tsx | Media |
| 4a | `useEconomyToast` hook + EconomyToast | hooks/, ui/ | Media |
| 4b | Sonidos Web Audio API | audioUtils.ts | Media |
| 4c | Integrar toasts en play result, purchases | CpuSimScreen, Store, Shop | Media |
| 5a | Backend cave_items model + endpoints | axolotito.py model, endpoints | Baja |
| 5b | Nuevos ItemType CAVE_ITEM en catálogo | items.py, seed_catalog.py | Baja |
| 5c | UI Santuario con habitaciones | Santuario/Criadero component | Baja |
| 5d | Bonos de cave items en play_match | game.py | Baja |
