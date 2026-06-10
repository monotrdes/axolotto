# Plan: Santuario — Layout Móvil Vertical + Nuevas Categorías de Adornos

**Task:** task-1781080168-76  
**Estado:** planning  
**Fecha:** 2026-06-10

---

## Contexto

El Santuario actual tiene un layout libre/scrolleable que no encaja en la experiencia móvil nativa. El objetivo es convertirlo a una pantalla fija 9:16 sin scroll, dividida en tres zonas funcionales (ref: `docs/santuario_ux_plan.md`). Además, las categorías de decoración (FLOOR/WALL/WATER/SPECIAL) no corresponden al diseño del cenote — se reemplazan por 4 categorías semánticas.

---

## Layout Objetivo (9:16, sin scroll)

```
+------------------------------------------+
|  HUD: $AXF | $FRJ | 🎫 Ticket | ⚡ Boost  |  ~8%
+------------------------------------------+
|  ZONA SUPERIOR (CRIANZA Y ESTADOS)        |  ~22%
|  [ 1 ][ 2 ][ 3 ][ 4 ]                   |
|  [ 5 ][ 6 ][ 7 ][   ]                   |
+------------------------------------------+
|  ZONA CENTRAL (EL DIORAMA DEL CENOTE)    |  ~45%
|  🪴           [HOST]           🪴         |
|       🦎   [Mesa Lotería]  🦎             |
|  🪴     🦎               🦎    🪴         |
+------------------------------------------+
|  ZONA INFERIOR (UI SOCIAL Y NAVEGACIÓN)  |  ~25%
|  [Amigo 1]  ❤️ Like  + Invitar  👁 Visitar |
|  [Amigo 2]  ❤️ Like  + Invitar  👁 Visitar |
|  [Amigo 3]  ❤️ Like  + Invitar  👁 Visitar |
|  [Amigo 4]  ❤️ Like  + Invitar  👁 Visitar |
|  🦎 Santuario | 🎲 Jugar | 🛒 Mercado | 👥 Amigos | 👤 Perfil |
+------------------------------------------+
```

---

## Tareas de Implementación

### 1. SANTUARIO-LAYOUT — Refactorizar Santuario.tsx

**Archivo:** `frontend/components/Santuario.tsx`

- Reemplazar contenedor raíz por `flex flex-col h-screen w-full max-w-[430px] mx-auto bg-slate-900 overflow-hidden`
- Eliminar cualquier `overflow-y-auto`, `min-h`, o scroll
- Dividir en 4 secciones con alturas fijas: HUD (8%), ZonaSuperior (22%), ZonaCentral (flex-1), ZonaInferior (25%)
- Extraer cada sección a su propio componente en `frontend/components/santuario/`

### 2. SANTUARIO-HUD — Componente de Recursos

**Archivo nuevo:** `frontend/components/santuario/SantuarioHUD.tsx`

- Barra compacta horizontal
- Balance AXF (moneda dorada) + Balance FRJ (cristal azul) + Ticket count + Boost indicator
- Consumir los mismos estados/props que ya usa `Santuario.tsx` para balances

### 3. SANTUARIO-NIDOS — Zona Superior (7 Slots)

**Archivo nuevo:** `frontend/components/santuario/ZonaSuperior.tsx`

- Grid `grid-cols-4` con 7 slots (fila 1: slots 1-4, fila 2: slots 5-7 + placeholder vacío)
- Reutilizar `SpotFluido.tsx` para render de cada slot
- Slot con huevo: emoji huevo + timer overlay (ej: "3h 15m")
- Slot vacío: `+` con estilo tenue
- Borde del panel: `border border-yellow-400/30 rounded-xl`
- Label de zona en header

### 4. SANTUARIO-DIORAMA — Zona Central

**Archivo:** `frontend/components/santuario/NidoScene.tsx` (adaptar)  
**Archivo nuevo:** `frontend/components/santuario/ZonaCentral.tsx`

- Pasar `className` o `style` a `NidoScene` para que ocupe la zona central en lugar de `100vh`
- 4 slots de adornos fijos en posiciones absolutas: `left-4 top-1/3`, `left-4 bottom-1/4`, `right-4 top-1/3`, `right-4 bottom-1/4`
- Badge HOST sobre axolotito principal
- Layer de iluminación (capa CSS semitransparente con gradiente radial) sobre el fondo
- Label de zona en header

### 5. SANTUARIO-SOCIAL — Zona Inferior

**Archivo nuevo:** `frontend/components/santuario/ZonaInferior.tsx`

- Lista fija de hasta 4 amigos: avatar circular + nombre + 3 botones (Like ❤️, Invitar +, Visitar 👁)
- Nav bar: 5 iconos con label (Santuario activo = highlighted)
- Altura total fija, sin scroll

### 6. SANTUARIO-DECOR — Nuevas Categorías de Adornos

**Archivos:**
- `frontend/types/santuario.ts` — cambiar `DecorSubcategory`
- `frontend/components/santuario/CaveDecorationPanel.tsx` — actualizar tabs + mock inventory
- `frontend/constants/santuario.ts` — actualizar constantes de categorías

**Cambio de tipo:**
```typescript
// Antes
type DecorSubcategory = 'FLOOR' | 'WALL' | 'WATER' | 'SPECIAL'

// Después
type DecorSubcategory = 'MANTEL' | 'ADORNOS_FIJOS' | 'ILUMINACION' | 'ENTORNO'
```

**Nuevos ítems mock:**

| Categoría | Ítems | Emoji | Rareza |
|-----------|-------|-------|--------|
| MANTEL | Papel Picado Catrina | 🏮 | rare |
| MANTEL | Mantel Bordado Tenango | 🧶 | epic |
| MANTEL | Cenote Minimalista | 💧 | common |
| ADORNOS_FIJOS | Maceta Loto de Papel | 🪷 | common |
| ADORNOS_FIJOS | Jarrón de Obsidiana Calada | 🏺 | rare |
| ADORNOS_FIJOS | Mini-Altar de Velas | 🕯️ | epic |
| ADORNOS_FIJOS | Incensario Copal | 🌿 | common |
| ILUMINACION | Guirnalda Fuego Fatuo | ✨ | rare |
| ILUMINACION | Lámparas de Jade | 💚 | epic |
| ILUMINACION | Antorchas Chinampa | 🔥 | common |
| ENTORNO | Cueva de Coral de Papel | 🪸 | rare |
| ENTORNO | Templo Maya en Ruinas | 🏛️ | legendary |
| ENTORNO | Fondo Día de Muertos | 💀 | epic |

---

## Archivos Críticos

| Archivo | Tipo de Cambio |
|---------|---------------|
| `frontend/components/Santuario.tsx` | Refactor mayor — layout raíz |
| `frontend/components/santuario/NidoScene.tsx` | Adaptar prop className/style |
| `frontend/components/santuario/CaveDecorationPanel.tsx` | Nuevas categorías + mock items |
| `frontend/types/santuario.ts` | Actualizar `DecorSubcategory` |
| `frontend/constants/santuario.ts` | Actualizar constantes |
| `frontend/components/santuario/SantuarioHUD.tsx` | Nuevo componente |
| `frontend/components/santuario/ZonaSuperior.tsx` | Nuevo componente |
| `frontend/components/santuario/ZonaCentral.tsx` | Nuevo componente |
| `frontend/components/santuario/ZonaInferior.tsx` | Nuevo componente |

---

## Estrategia CSS

```tsx
// Santuario.tsx — estructura raíz
<div className="flex flex-col h-screen w-full max-w-[430px] mx-auto bg-slate-900 overflow-hidden">
  <SantuarioHUD axf={axfBalance} frj={frjBalance} tickets={ticketCount} />
  <ZonaSuperior incubaciones={incubaciones} onSelectSlot={handleSelectSlot} />
  <ZonaCentral axolotitos={axolotitos} decoraciones={placedDecos} className="flex-1" />
  <ZonaInferior amigos={amigosActivos} activePage="santuario" onNavigate={handleNav} />
</div>
```

---

## Verificación

```bash
# Iniciar frontend
cd frontend && npm run dev

# Visual en navegador DevTools (modo móvil 390×844 / iPhone 14 Pro):
# ✓ Sin scroll vertical ni horizontal
# ✓ HUD con balances visibles en la cima
# ✓ 7 slots de nido en zona superior
# ✓ Diorama cenote con mesa central + axolotitos
# ✓ 4 slots de adornos fijos (2 izq + 2 der)
# ✓ Lista amigos + nav bar en zona inferior
# ✓ Panel adornos muestra 4 nuevas categorías (MANTEL/ADORNOS_FIJOS/ILUMINACION/ENTORNO)
# ✓ TypeScript sin errores: npx tsc --noEmit
```

---

## Referencia Visual

Ver imagen de referencia en conversación (2026-06-10) y `docs/santuario_ux_plan.md`.
