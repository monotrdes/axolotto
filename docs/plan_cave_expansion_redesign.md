# Propuesta de Diseño: Rediseño de Expansión de Cueva (Cenote)

> **Contexto:** Actualmente, el sistema permite que un jugador pague Axofichas (AXF/AXG) para saltarse directamente los logros de expansión de la cueva de forma instantánea. Esta propuesta reestructura el flujo para que los logros sean obligatorios y las Axofichas funcionen exclusivamente como aceleradores de tiempo.
>
> **Actualización de Balanceo:** Se calibra el costo de aceleración usando el paquete mínimo de **200 AXF por $35 MXN** (1 AXF = $0.175 MXN) y se simula la generación de Frijolitos (FRJ) a 30 días para validar la progresión F2P y VIP.

---

## 1. Análisis del Flujo Actual vs. Propuesto

### El Problema del Bypass Directo
* **Desvalorización de Logros:** Si un jugador puede pagar 3 AXF para pasar al nivel 3, el logro asociado ("Gana 3 partidas + racha de 3 días") pierde su peso como trofeo. La progresión se vuelve una simple molestia económica.
* **Corte del Ciclo de Apego:** La expansión de la cueva otorga slots para más Axolotitos. Al saltarse la progresión, el jugador acumula personajes demasiado rápido sin aprender a cuidarlos o interactuar con ellos, reduciendo el engagement a largo plazo.
* **Hard Paywall en Niveles 6-8:** Bloquear de forma estricta los niveles 6, 7 y 8 detrás de suscripciones VIP (Coral, Dorado, Axolite) frustra a los jugadores gratuitos (F2P), limitando su capacidad para competir de forma pasiva (staking) o coleccionar más de 5 Axolotitos.

### El Nuevo Modelo de Progresión (Game Design Standard)
1. **Logro Obligatorio:** Todos los jugadores deben cumplir el reto/misión para habilitar la expansión de la cueva. No se puede comprar el derecho a expandir con dinero.
2. **Costo en Frijolitos (FRJ):** Iniciar la expansión consume una cantidad de Frijolitos (Soft Currency). Esto actúa como un sumidero (sink) de moneda esencial para controlar la inflación del ecosistema.
3. **Fase de Excavación (Tiempo):** La expansión toma horas reales (de 2h a 72h). Esto crea expectación y ritmo en la jugabilidad.
4. **Monetización vía Acelerador (Calibrado):** Las Axofichas (AXF) se utilizan **únicamente** para reducir o eliminar el temporizador de excavación. Se establece un ratio de **4 AXF por hora de excavación** (1 AXF cada 15 minutos).
5. **VIP como Ventaja, no como Paywall:** Los niveles 6-8 pueden ser alcanzados por jugadores F2P mediante grinding (requisitos de partidas y costos en FRJ muy altos), pero los jugadores VIP reciben:
   * **50% de descuento** en el costo de Frijolitos.
   * **50% de descuento** en el tiempo de excavación (velocidad duplicada).
   * Estatus de logro simplificado / alternativo (auto-completar el logro de su nivel de VIP correspondiente).

---

## 2. Calibración de Monetización (AXF a Pesos MXN)

Tomando en cuenta que el paquete más económico es de **200 AXF por $35 MXN** (1 AXF = $0.175 MXN), la aceleración del tiempo de excavación queda valorada de la siguiente forma con el ratio de **4 AXF / hora** ($0.70 MXN/hora):

* **2 Horas (Nivel 2):** 8 AXF (≈ $1.40 MXN)
* **6 Horas (Nivel 3):** 24 AXF (≈ $4.20 MXN)
* **12 Horas (Nivel 4):** 48 AXF (≈ $8.40 MXN)
* **24 Horas (Nivel 5):** 96 AXF (≈ $16.80 MXN)
* **36 Horas (Nivel 6):** 144 AXF (≈ $25.20 MXN)
* **48 Horas (Nivel 7):** 192 AXF (≈ $33.60 MXN)
* **72 Horas (Nivel 8):** 288 AXF (≈ $50.40 MXN)

*Nota: Esta estructura monetaria incentiva la aceleración en rangos medios y altos, ofreciendo una excelente relación de monetización por tiempo sin devaluar los logros.*

---

## 3. Simulación de la Economía de Frijolitos (Balance de Producción)

Para validar si los costos en Frijolitos propuestos son correctos, modelamos el comportamiento de 4 perfiles de jugador durante 30 días, incorporando la **recompensa diaria de check-in** (faucet F2P de 50 a 110 FRJ/día) y el **staking pasivo de Axolotitos** (Play-to-Stake activo):

### Resultados del Simulador a 30 Días:

* **Perfil 1: F2P Casual** (1 juego al día, 2 Axolotitos comunes en staking, reclama check-in diario)
  * **Balance Inicial:** 50 FRJ (Tutorial)
  * **Día 10:** 419 FRJ (Cueva Lvl 2)
  * **Día 30:** 1,165.5 FRJ (Cueva Lvl 3)
  * *Conclusión:* El jugador casual avanza de forma constante. Logra la Cueva 2 en la primera semana y la Cueva 3 al final del mes. Nunca cae en insolvencia gracias al check-in diario.

* **Perfil 2: F2P Active** (10 juegos al día, 1 Axolotito común subiendo de nivel, reclama check-in diario, expande cueva)
  * **Balance Inicial:** 50 FRJ
  * **Día 10:** 458 FRJ (Cueva Lvl 1)
  * **Día 20:** 1,117 FRJ (Cueva Lvl 2)
  * **Día 30:** 1,294.3 FRJ (Cueva Lvl 3)
  * *Conclusión:* El grinding de 10 juegos diarios consume mucha energía y Frijolitos al inicio, pero a medida que el Axolotito sube de nivel (Lvl 13 en Día 30) y su Focus sube de 40 a 70, su win rate sube y empieza a acumular Frijolitos rápidamente.

* **Perfil 3: VIP Dorado** (10 juegos al día, 1 Axolotito raro, +100 FRJ/day VIP, 50% de descuento)
  * **Balance Inicial:** 500 FRJ (Bono Dorado)
  * **Día 10:** 1,046 FRJ (Cueva Lvl 3)
  * **Día 30:** 4,413.5 FRJ (Cueva Lvl 4)
  * *Conclusión:* Gracias al descuento del 50% y los bonos VIP, el jugador Dorado progresa fluidamente. Llega a Cueva 4 en el día 20 y tiene balance de sobra para preparar su cueva de nivel 5 (esperando a que su Axolotito alcance el nivel requerido).

* **Perfil 4: Spender** (Compra 200 AXF y los convierte a 1500 FRJ el primer día, juega activo)
  * **Balance Inicial:** 1,550 FRJ
  * **Día 10:** 1,484 FRJ (Cueva Lvl 2)
  * **Día 30:** 2,869.9 FRJ (Cueva Lvl 3)
  * *Conclusión:* La compra inicial elimina por completo el "cash squeeze" de la primera semana, permitiéndole expandirse al Nivel 2 de inmediato y jugar sin preocuparse por la solvencia.

---

## 4. Matriz de Requerimientos y Costos Ajustados

| Nivel | Nombre | Hito / Logro Requerido | Costo FRJ (F2P) | Costo FRJ (VIP) | Tiempo Base (F2P) | Tiempo Base (VIP) | Aceleración (AXF) | Beneficios Otorgados |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **1** | **El Nicho** | *Desbloqueado por defecto* | Gratis | Gratis | Instantáneo | Instantáneo | - | 1 slot Axolotito, 2 decoraciones. |
| **2** | **La Gruta** | Jugar 10 partidas totales + alcanzar nivel 3 | 500 FRJ | 250 FRJ | 2 horas | 1 hora | 8 AXF | 2 slots Axolotitos, 4 decoraciones, Huevo Fase 1. |
| **3** | **La Caverna** | Ganar 3 partidas + racha de 3 días activos | 1,500 FRJ | 750 FRJ | 6 horas | 3 horas | 24 AXF | 3 slots Axolotitos, 6 decoraciones, Mesa de Juego (2 sillas), Huevo Fase 1 Plus. |
| **4** | **El Salón** | Ganar 1 Jackpot **o** jugar 25 rondas multijugador | 4,000 FRJ | 2,000 FRJ | 12 horas | 6 horas | 48 AXF | 4 slots Axolotitos, 8 decoraciones, Mesa de Juego (4 sillas), Huevo Fase 2. |
| **5** | **El Santuario** | Axolotito principal alcance nivel 15 | 8,000 FRJ | 4,000 FRJ | 24 horas | 12 horas | 96 AXF | 5 slots Axolotitos, 10 decoraciones, Mesa de Juego (6 sillas), Huevo Fase 2 Nature. |
| **6** | **El Abismo** | Jugar 50 partidas totales + alimentar 100 veces<br>*(Auto-completado si VIP Coral+)* | 15,000 FRJ | 7,500 FRJ | 36 horas | 18 horas | 144 AXF | 6 slots Axolotitos, 12 decoraciones, Mesa de Juego (8 sillas), Huevo Fase 2 Nature. |
| **7** | **El Templo** | Jugar 100 partidas totales + ganar 15 partidas<br>*(Auto-completado si VIP Dorado+)* | 30,000 FRJ | 15,000 FRJ | 48 horas | 24 horas | 192 AXF | 7 slots Axolotitos, 14 decoraciones, Mesa de Juego (8 sillas), Huevo Astral. |
| **8** | **Palacio Astral** | Jugar 200 partidas totales + eclosionar un Axolotito Épico/Legendario<br>*(Auto-completado si VIP Axolite)* | 60,000 FRJ | 30,000 FRJ | 72 horas | 36 horas | 288 AXF | 8 slots Axolotitos, 16 decoraciones, Mesa de Juego (8 sillas), Huevo Astral + Skin Astral Cenote. |

---

## 5. Tareas de Implementación Técnica

### 5.1 Backend (FastAPI - `cave_expansion.py`)
- **Modificar la definición `CAVE_LEVEL_DEFINITIONS`:**
  * Remover `"path_pago"` de todos los niveles (elimina la compra directa).
  * Agregar costo de Frijolitos (`cost_frj`) a cada definición.
  * Actualizar `"path_logro"` para los niveles 6, 7 y 8 permitiendo el doble camino (grinding largo o VIP bypass).
- **Actualizar el endpoint `POST /expand`:**
  * Validar únicamente el camino de logro (eliminar el parámetro `path="pago"`).
  * Comprobar si el usuario es VIP para aplicar la reducción del 50% en costo de Frijolitos (`cost_frj`) y 50% de reducción en el tiempo de excavación (`excavation_hours`).
  * Descontar los Frijolitos de la billetera del usuario y registrar la transacción en el ledger como tipo `WEBITO_UNLOCK`.
  * Establecer la fecha de inicio (`cave_expansion_started_at`) y el nivel objetivo.
- **Modificar el endpoint `GET /status`:**
  * Devolver el costo en FRJ correspondiente al nivel del jugador (aplicando su descuento VIP actual).
  * Retornar si el logro actual está completado o no para que el frontend deshabilite el botón.
- **Ajustar el endpoint `POST /expand/accelerate`:**
  * Mantener la aceleración con Axofichas (AXF), cobrando 4 AXF por hora restante (1 AXF cada 15 minutos, redondeado arriba).

### 5.2 Frontend (React - `CaveExpansionPanel.tsx` o equivalente)
- **Actualizar la interfaz del panel de expansión:**
  * Mostrar el logro actual de forma clara (ej. barra de progreso de partidas o nivel necesario).
  * Mostrar el costo en Frijolitos (con un indicador si tiene descuento por VIP).
  * Reemplazar el botón "Comprar con AXF" por "Comenzar Excavación" (deshabilitado si no se cumple el logro o faltan frijolitos).
  * Mostrar de forma destacada el botón "Acelerar con [X] AXF" mientras haya una excavación activa.

---

## 6. Siguientes Pasos
Una vez aprobado este plan económico por el usuario, procederemos con las modificaciones de backend en [cave_expansion.py](file:///D:/Axolotto_2026/axolotto/backend/app/api/v1/endpoints/cave_expansion.py).
