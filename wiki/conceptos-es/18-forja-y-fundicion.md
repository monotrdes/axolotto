# 18 — Forja y Fundición (Forge & Melter)

> **English Summary**: The crafting system has two halves: the **Card Melter** ("El Cenote Místico") destroys 5 identical non-shiny, non-first-edition duplicates to reward fragments + FRJ + 1 random card of a higher tier; the **Forge** spends fragments + FRJ to craft a *specific* card from the 54-card catalog with no randomness. Fragments (común/raro/épico/legendario) are wallet-tracked and non-tradable. Commons are best melted, valuable singles are best sold on the P2P market, and the Forge is your tool when you need one exact card to finish a collection or optimize a board.

---

## Quick Reference

| Concept | Key Rule |
|---------|----------|
| **Fundición (Melter)** | Burn 5 identical copies → fragments + FRJ + 1 random higher-rarity card |
| **Forja (Forge)** | Spend fragments + FRJ → craft 1 **specific** card of your choice |
| **Cannot melt** | Shiny/foil, first edition, or legendary cards |
| **Fragment storage** | Wallet-tracked, non-tradable, non-transferable |
| **Best melt** | Common duplicates (5+ copies) |
| **Best sell** | Foils, first editions, high-market-value rares/legendaries (see [[19-mercado-p2p]]) |
| **Best forge** | When 1–2 cards away from completing a collection or building a board strategy |

---

## 1. La Fundición de Cartas — "El Cenote Místico"

La Fundición es un caldero místico donde sacrificas cartas duplicadas para obtener recursos de crafteo y una carta de rareza superior. Es el sistema principal para convertir cartas excedentes en valor real.

### Reglas de fundición

- Debes quemar **5 copias idénticas** de la misma carta.
- Las 5 copias deben ser **no brillantes (non-shiny)** y **no primera edición (non-first-edition)**.
- **No se pueden fundir** cartas legendarias, cartas foil/shiny, ni cartas de primera edición.
- Recibes: **fragmentos + FRJ + 1 carta aleatoria de una rareza superior**.

### Costos y recompensas

| Input (5 cartas) | Costo FRJ | Fragmentos ganados | Output (1 carta) |
|------------------|-----------|---------------------|------------------|
| 5 Comunes | 100 FRJ | +10 frag_común | 1 Rara aleatoria |
| 5 Raras | 250 FRJ | +10 frag_raro | 1 Épica aleatoria |
| 5 Épicas | 1,500 FRJ | +10 frag_épico | 1 Legendaria aleatoria |
| 5 Legendarias | No permitido | — | — |

> La salida es **aleatoria** dentro de la rareza superior. No puedes elegir qué carta recibes al fundir.

---

## 2. Tipos de Fragmentos

Los fragmentos son la moneda de crafteo. Se almacenan en tu wallet y **no son transferibles ni comerciables** en el [[19-mercado-p2p|Mercado P2P]].

| Fragmento | Color | Se obtiene al fundir | Se usa para forjar |
|-----------|-------|----------------------|---------------------|
| `frag_común` | Verde | 5 Comunes | Cartas Comunes |
| `frag_raro` | Azul | 5 Raras | Cartas Raras |
| `frag_épico` | Púrpura | 5 Épicas | Cartas Épicas |
| `frag_legendario` | Dorado | — (ver Forja) | Cartas Legendarias |

> Los fragmentos legendarios **no se obtienen fundiendo** (porque no se pueden fundir legendarias). Se obtienen por otras vías (eventos, recompensas especiales, [[13-tienda-y-tianguis|Tienda]]).

---

## 3. La Forja — Crafteo de cartas específicas

A diferencia de la Fundición, la Forja te permite crear una **carta exacta** del catálogo de 54 cartas (ver [[09-cartas]]). **Sin aleatoriedad**: tú eliges cuál quieres.

### Costos de forja

| Rareza objetivo | Fragmentos requeridos | Costo FRJ |
|-----------------|-----------------------|-----------|
| Común | 50 frag_común | 100 FRJ |
| Rara | 100 frag_raro | 500 FRJ |
| Épica | 250 frag_épico | 1,000 FRJ |
| Legendaria | 500 frag_legendario | 3,000 FRJ |

> Forjar una Legendaria (500 frags + 3,000 FRJ) es un objetivo de largo plazo. Requiere acumular fragmentos legendarios consistentemente.

---

## 4. Estrategia — ¿Fundir o Vender?

La decisión de fundir una carta o venderla en el [[19-mercado-p2p|Mercado P2P]] depende de su rareza, edición y valor de mercado:

| Situación | Acción recomendada | Razón |
|-----------|--------------------|-------|
| 5+ duplicados de una Común | **Fundir** | Las comunes rara vez tienen alto valor P2P; los fragmentos son más útiles |
| Carta foil/shiny o primera edición | **Vender en P2P** | No se puede fundir de todos modos; valor de colección alto |
| Rara con buen precio de mercado | **Vender en P2P** | Revisa precios primero; puede valer más que los fragmentos |
| Épica duplicada | **Pensar con cuidado** | Evalúa si el precio P2P justifica no fundir |
| Legendaria duplicada | **Vender en P2P** | No se puede fundir; siempre tiene valor de mercado |
| A 1–2 cartas de completar colección | **Forjar** | Usa los fragmentos acumulados para cerrar la colección |
| Necesitas carta específica para estrategia de tablero | **Forjar** | La Forja te da control total sobre cuál recibes |

### Regla general

- **Comunes → Fundir.** Conviertes "basura" en recursos de crafteo.
- **Raras con valor → Vender.** Consulta el [[19-mercado-p2p|Mercado P2P]] antes.
- **Épicas → Analizar caso por caso.**
- **Legendarias → Vender.** No hay otra opción; su valor P2P suele ser alto.
- **Para completar colecciones → Forjar.** Es la única forma garantizada de obtener la carta exacta que te falta.

---

## 5. Gestión de Fragmentos

- Los fragmentos se acumulan **pasivamente** al fundir cartas. No requieren acción adicional.
- Consulta tu saldo en la **interfaz del Cenote Místico (Fundición)**.
- **No acumules fragmentos indefinidamente.** Úsalos para forjar cartas que realmente necesitas, ya sea para completar una colección o para armar estrategias de tablero específicas.
- Prioriza forjar cartas que tengan sinergia con tu [[09-cartas|colección actual]] y tu estilo de juego.

---

## 6. Flujo completo recomendado

1. **Abre sobres** en la [[13-tienda-y-tianguis|Tienda]] para obtener cartas.
2. **Identifica duplicados**: separa commons repetidas, foil/primera-edición, y cartas con valor P2P.
3. **Vende** las cartas con alto valor en el [[19-mercado-p2p|Mercado P2P]].
4. **Funde** las comunes sobrantes para generar fragmentos y una carta de rareza superior.
5. **Forja** cartas específicas cuando te falten pocas para completar una colección o necesites una carta clave para tu tablero.
6. **Repite.** El ciclo abrir-fundir-forjar-vender mantiene tu colección en crecimiento constante.

---

**Wikilinks**: [[09-cartas]] · [[13-tienda-y-tianguis]] · [[19-mercado-p2p]] · [[00-INDEX]]
