# Plan de Actualización del Simulador del Universo Axolotto (`simulate_universe.py`)

Este documento detalla el plan para integrar las mecánicas de gamificación, fusiones, naturalezas, el desarme seguro con solvente y el flujo optimizado de compra, apertura y venta P2P de boosters en el script de simulación integral `backend/app/scripts/simulate_universe.py`.

---

## 🎯 Objetivos de la Actualización

1. **Uso Dinámico de Fichas de Gashapón**:
   * Simular la obtención de "Ficha de Gashapón".
   * Consumir fichas en tiradas estándar y cápsulas (Cobre = 1, Plata = 2, Oro = 4, Triple Suerte = 6) de acuerdo con los inventarios de los jugadores.
2. **Cenote Místico / Card Melter**:
   * Simular la fundición de 5 copias duplicadas de cartas comunes/raras/épicas (`/melter/melt`) para obtener fragmentos y una carta superior.
   * Simular la forja de cartas específicas (`/melter/forge`) canjeando fragmentos acumulados y GAL.
3. **Naturalezas (Personalities)**:
   * Registrar e imprimir la personalidad (Nature) asignada a cada Axolotito al nacer (`methodical`, `lucky`, `hyperactive`, `shy`, `wise`, `glutton`).
   * Mostrar cómo influyen estas naturalezas en las interacciones cotidianas y batallas (p.ej., Glotón con comida, Hiperactivo al dormir, Sabio en staking).
4. **Desarme Seguro con Solvente de Pegamento**:
   * Añadir una sección de desarme donde un jugador utiliza el Solvente de Pegamento (costo de 120 GAL) para desarmar una tabla y recuperar sus 16 cartas al 100% intactas, en vez de perder una al azar.
5. **Simulación de Compra, Apertura y Venta P2P de Boosters**:
   * **Mayor volumen de sobres**: Incrementar sustancialmente el número de sobres comprados por los jugadores en sus configuraciones de personalidad (p.ej., Whales: 30 normales / 10 foil; Collectors: 15 normales / 3 foil; Aggressives: 20 normales / 5 foil; Casuals: 8 normales / 2 foil).
   * **Apertura de la mayoría**: Modificar las estrategias de apertura para que todos los jugadores abran la gran mayoría de sus sobres (p.ej., del 75% al 100%), dejando solo unos pocos (1 a 3 sobres) sellados en su inventario.
   * **Mercado Secundario P2P**: Agregar un proceso simulado donde los jugadores publican sus sobres sellados restantes en el mercado secundario (`/inventory/list`) y otros jugadores con GAL excedente los buscan (`/inventory/listings`) y compran (`/inventory/{listing_id}/buy`).

---

## 🛠️ Detalle de los Procesos a Agregar

### Fase 2b: Distribución de Fichas de Gashapón
* **Acción**: Otorgar fichas iniciales en el inventario para poder probar su uso.
* **Detalle**: 
  * Los "Whales" y "Collectors" recibirán 20 Fichas de Gashapón.
  * Los "Casuals" y "Aggressives" recibirán 10 Fichas de Gashapón.
  * Se buscará `"Ficha de Gashapón"` en el catálogo de ítems y se insertará en el inventario mediante un registro de `PlayerInventory`.

### Fase 3a & 3b (Boosters): Incremento de Volumen y Apertura Mayoritaria
* **Acción**: Aumentar la cantidad de sobres en el `PERSONALITY_POOL`:
  * `whale`: 30 normales, 10 foils. (Estrategia: abre el 100%).
  * `collector`: 15 normales, 3 foils. (Estrategia: abre el 85%, deja ~2-3 sellados).
  * `aggressive`: 20 normales, 5 foils. (Estrategia: abre el 80%, deja ~4-5 sellados).
  * `casual` (hoarder): 8 normales, 2 foils. (Estrategia: abre el 75%, deja ~2-3 sellados).
* **Detalle**:
  * Modificar `BOOSTER_OPEN_STRATEGY` o la lógica en `phase_open_boosters()` para que "hoarder" y otras estrategias no bloqueen el 100% de los boosters, sino que abran la gran mayoría, permitiendo tanto armar mejores tableros como conservar unos pocos para el comercio.

### Fase 4 (Eclosión): Registro de Naturalezas
* **Acción**: Al invocar `hatch_webito(...)` en la eclosión, el Axolotito obtiene una personalidad de forma aleatoria en el backend.
* **Detalle**:
  * Imprimir la naturaleza del Axolotito recién nacido junto a sus estadísticas de pureza.
  * Registrar estadísticas en el reporte final sobre qué naturalezas predominan en el universo.

### Fase 5 (Gashapon): Consumo Dinámico de Fichas
* **Acción**: Modificar las llamadas a gashapon para priorizar el uso de tickets/fichas.
* **Detalle**:
  * Si el jugador tiene suficientes fichas, llamar a `roll_gashapon(...)` con `use_ticket=True` (gasta 1 ficha).
  * Si el jugador tiene suficientes fichas, llamar a `roll_capsule(...)` con `use_ticket=True` (Cobre: 1, Plata: 2, Oro: 4).
  * Si un jugador con estilo "does_triple_suerte" tiene 6 o más fichas, llamar a `roll_triple_suerte(...)` con `use_ticket=True` (gasta 6 fichas).
  * Si no tiene fichas suficientes, usar el flujo por defecto cobrando GAL.

### Fase 6c: Cenote Místico (Melt & Forge)
* **Nueva Subfase**: Procesar fundición y forja.
* **Detalle**:
  * **Fundición (Melt)**: Buscar grupos de 5 o más cartas idénticas no-foil en el inventario de los jugadores. Si el jugador tiene suficiente GAL (100 para común, 250 para rara, 1500 para épica), invocar `melt_card(...)` consecutivamente para obtener fragmentos y una carta superior aleatoria.
  * **Forja (Forge)**: Si el jugador ha acumulado suficientes fragmentos de una rareza (`frag_comun >= 50`, `frag_raro >= 100`, `frag_epico >= 250`, `frag_legendario >= 500`) y tiene suficiente GAL, elegir una carta que no tenga en su tablero ni inventario y llamar a `forge_card(...)` para forjarla.

### Fase 6d: Desarme Seguro de Tablas
* **Nueva Subfase**: Simular reestructuración estratégica de tableros.
* **Detalle**:
  * Elegir al menos 1 tablero activo de un jugador casual/agresivo que tenga más de 2 tableros creados.
  * Asegurarse de que el jugador tenga 120 GAL.
  * Invocar la ruta de desarme `delete_board(board_id=..., session=session, verified_user_id=...)`.
  * Imprimir en consola la confirmación: cobro de 120 GAL y recuperación exitosa de las 16 cartas en su inventario.

### Fase 6e: Mercado Secundario P2P (Venta y Compra de Sobres Sellados)
* **Nueva Subfase**: Simular el mercado secundario.
* **Detalle**:
  * **Listar**: Jugadores que tengan sobres sellados en su inventario los publicarán en el mercado secundario llamando a `list_inventory_item(...)` a un precio competitivo (p.ej., 180 GAL por normal, 450 GAL por foil).
  * **Comprar**: Jugadores con GAL excedente (especialmente Whales y Collectors) buscarán publicaciones activas con `get_inventory_listings(...)` y comprarán sobres sellados de otros jugadores llamando a `buy_inventory_listing(...)`.

---

## 📈 Plan de Verificación de Simulación

Para validar los cambios, se ejecutará el script con diferentes configuraciones de terminal:

```bash
# Simulación rápida con 4 jugadores
python backend/app/scripts/simulate_universe.py --players 4 --incubation 10 --games 3
```

Se comprobará en la salida de consola y en el archivo `simulation_report.txt` que:
* Se registran las fundiciones realizadas y las cartas superiores obtenidas.
* Se muestran las cartas forjadas exitosamente.
* Se listan las naturalezas obtenidas en la eclosión.
* Se reporta el uso de fichas de Gashapón y su reducción de inventario.
* Se detalla el desarme de tableros usando el Solvente de Pegamento.
* Se reportan las publicaciones creadas en el mercado P2P y las compras exitosas entre jugadores.
