# 🃏 Axolotto: Token & Price Processing Bible

Este documento es la referencia definitiva para todas las divisas, paquetes, catálogos, conversiones y la política de protección financiera anti-arbitraje de **Axolotto**. Su objetivo es estandarizar los cálculos en todo el sistema (backend, frontend, simulaciones y administración) para asegurar la rentabilidad de la plataforma.

---

## 1. Monedas y Conversiones Base

### A. Tipo de Cambio Primario: MXN ↔ AXG (Axogema)
Las AXG son la divisa premium que se adquiere con dinero real. El tipo de cambio promedio se deriva de las ventas históricas reales, pero se establece la siguiente matriz de paquetes oficiales:

| Paquete | AXG Otorgadas | Precio Fíat (MXN) | Costo Unitario por AXG (MXN) | Descuento / Notas |
| :--- | :---: | :---: | :---: | :---: |
| **Paquete Pequeño** | 200 AXG | **$35.00 MXN** | $0.1750 MXN | Precio base casual |
| **Paquete Mediano** | 550 AXG | **$88.00 MXN** | $0.1600 MXN | ~8.5% descuento |
| **Paquete Grande** | 1,725 AXG | **$263.00 MXN** | $0.1524 MXN | ~13% descuento |
| **Paquete Ballena** | 7,250 AXG | **$875.00 MXN** | **$0.1207 MXN** | ~31% de descuento base |

> [!WARNING]
> **El precio de 1 AXG varía desde $0.1207 MXN (mayorista) hasta $0.1750 MXN (minorista).**
> Para cualquier cálculo de reserva de recompra, se utiliza el promedio dinámico del usuario, o el costo mínimo mayorista de **$0.1207 MXN** como límite de protección de liquidez.

---

### B. Tipo de Cambio Secundario: AXG ↔ GAL (Gemas de Alga)
La divisa blanda del juego (GAL) se obtiene jugando o convirtiendo AXG.

| Paquete Algas | Costo AXG | GAL Otorgadas | Equivalencia (GAL por AXG) | Costo de 1 GAL en Pesos (MXN)* |
| :--- | :---: | :---: | :---: | :---: |
| **Alga Común** | 10 AXG | 100 GAL | 10.0 GAL | $0.0121 MXN |
| **Alga Abundante** | 50 AXG | 550 GAL | 11.0 GAL | $0.0110 MXN |
| **Alga Imperial** | 100 AXG | 1,200 GAL | 12.0 GAL | $0.0101 MXN |
| **Súper Carga** | 500 AXG | 6,500 GAL | **13.0 GAL** | **$0.0093 MXN** |

*\*Basado en el costo mayorista de AXG ($0.1207 MXN).*

---

## 2. Catálogo Oficial de Precios

### A. Webitos (Eggs)
*Los huevos primarios se venden por fases con suministro limitado para incentivar el valor temprano:*

* **Fase 1 (Génesis — Fundador):** **400 AXG** (Suministro: 420 unidades)
* **Fase 2 (Expansión):** **800 AXG** (Suministro: 1,260 unidades)
* **Fase 3 (Retail / Mercado completo):** **1,200 AXG** (Suministro: 2,520 unidades)
* **Edición Astral Especial (Límite anual):** **3,000 AXG** (Suministro: 100 unidades por año)

---

### B. Ecosistema de Boosters
*Los sobres de cartas se encarecen en cada fase a medida que aumenta la base de jugadores:*

* **Fase 1 (Primera Edición):** Temáticos (Fiesta, Nido, Cosmos) = **100 AXG** | Mezclado = **60 AXG**
* **Fase 2 (Unlimited):** Temáticos = **150 AXG** | Mezclado = **100 AXG**
* **Fase 3 (Retail / Estándar):** Temáticos = **200 AXG** | Mezclado = **150 AXG**

---

### C. Slots de Tableros (Board Slots)
*El jugador puede guardar más tableros activos adquiriendo slots adicionales:*

* **Slots 1 al 3:** Gratis (desbloqueados de inicio).
* **Slot 4:** **500 GAL** (Reto: 0 partidas).
* **Slot 5:** **1,000 GAL** (Reto: 10 partidas).
* **Slot 6:** **2,000 GAL** (Reto: 25 partidas).
* **Slot 7:** **4,000 GAL** (Reto: 50 partidas / 5 victorias).
* **Slot 8:** **8,000 GAL** (Reto: 100 partidas / 15 victorias).
* **Slot 9+:** **15,000 GAL * multiplicador incremental**.

---

### D. Consumibles y Cuidado de Axolotitos
* **Lámpara Infrarroja Pro:** **200 AXG** (Utility del criadero).
* **Gotas Anti-Escarcha:** **200 GAL** (Evita la congelación de webitos).
* **Solvente de Pegamento:** **120 GAL** (Permite desarmar tableros recuperando el 100% de las 16 cartas).
* **Algae Pellet (Alimento Común):** **30 GAL** (Restaura 15 de energía).
* **Brine Shrimp (Alimento Premium):** **150 GAL** (Restaura 60 de energía).

---

### E. Esferas de Gashapón
* **Esfera de Cobre (Bronce):** **1,500 GAL** (o 1 Ficha de Gashapón).
* **Esfera de Plata:** **5,000 GAL** (o 2 Fichas de Gashapón).
* **Esfera de Oro:** **20,000 GAL** (o 4 Fichas de Gashapón).
* **Esfera Triple (Descuento):** **22,500 GAL** (o 6 Fichas de Gashapón).

---

### F. Salas Multijugador (Lotería Match Fees — Nivel 1x)
* **Charco de Novatos (Rookie):** Entrada = **100 GAL** | Victoria = **160 GAL** | Consolación = **20 GAL**
* **Fosa del Campeón (Champion):** Entrada = **500 GAL** | Victoria = **2,900 GAL** | Consolación = **50 GAL**
* **Multiplicadores de Apuesta admitidos:** `1x`, `2x`, `5x`, `10x` (se multiplica proporcionalmente la cuota, premio y XP).

---

## 3. Política Anti-Arbitraje de Liquidez (Defensa contra el "Loco Rico")

### El Riesgo
Si un jugador con alto capital ("Whale") compra el paquete de 7,250 AXG por $875.00 MXN, está adquiriendo gemas a **$0.1207 MXN c/u**. 
Si existiera una tasa de retiro fija nominal en pesos basada en el valor casual de $2.00 MXN brutos (por ejemplo, devolver el 70% = $1.40 MXN por AXG), el jugador podría:
1. Comprar 1,000,000 AXG pagando **$120,689 MXN**.
2. Solicitar un Cash-Out (retiro) al día siguiente.
3. Retirar a la tasa fija de $1.40 MXN obteniendo **$1,400,000 MXN**.
4. **Resultado:** Quiebra de tu reserva de liquidez y robo de tus fondos mediante arbitraje de tasas.

---

### El Sistema de Protección de Axolotto

Para evitar este y otros vectores de insolvencia, aplicamos la **Fórmula de Recompra Dinámica Acreditada (DevEx)**:

1. **Retiro Basado en Costo de Adquisición Real:**
   El sistema no recompra gemas a una tasa nominal teórica fija. La tasa de recompra de un usuario se calcula como un porcentaje de su **costo real promedio de adquisición histórico** (`avg_price_per_axg`) registrado en su historial de compras fíat/cripto:

   $$\text{Tasa de Retiro del Usuario (MXN por AXG)} = \text{Costo Promedio de Adquisición} \times \text{Porcentaje de Retiro (70\% o 50\%)} $$

   * **Ejemplo del Loco Rico (Whale):** Compró AXG a promedio de **$0.1207 MXN**.
     - Su tasa de retiro al 70% es: $\$0.1207 \times 0.70 = \mathbf{\$0.0845\text{ MXN por AXG}}$.
     - Si solicita retirar sus 7,250 AXG, recibe **$612.50 MXN** (asumiendo una pérdida del 30% por spread, lo cual es sano para ti y previene el arbitraje).
   * **Ejemplo del Jugador Casual:** Compró el paquete chico a promedio de **$0.1750 MXN**.
     - Su tasa de retiro al 70% es: $\$0.1750 \times 0.70 = \mathbf{\$0.1225\text{ MXN por AXG}}$.
     - Si retira 200 AXG, recibe **$24.50 MXN** (asumiendo su spread correspondiente).

2. **Spread de Conversión In-Game (Residual del Creador):**
   El spread del 30% o 50% de retención en el retiro se queda de forma permanente en la **Reserva Líquida** como excedente del sistema, financiando los jackpots y el crecimiento del juego.
