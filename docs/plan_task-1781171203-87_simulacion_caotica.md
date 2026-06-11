# Plan de Diseño: Simulador de Tráfico Caótico, Concurrente y de Seguridad (Chaos & Security Simulator)

Este documento detalla la arquitectura, el diseño y el plan de implementación para la actualización del sistema de simulación de Axolotto. El objetivo es evolucionar el actual flujo lineal y secuencial hacia un entorno de ejecución concurrente y caótico que simule tráfico real, ataques maliciosos concurrentes, y genere reportes detallados para la remediación de vulnerabilidades y optimización de rendimiento.

---

## 1. Objetivos del Nuevo Simulador

1. **Concurrencia Real (Multi-threading / Async):** Cada jugador simulado y cada actor malicioso correrá en su propia línea independiente (hilo o corrutina asíncrona) de forma concurrente, con intervalos de espera (*think-times*) aleatorios y dinámicos.
2. **Caos e Intercalado de Acciones:** Eliminar la estructura lineal por fases. Los jugadores podrán comprar, abrir, incubar, alimentar y registrarse en partidas de forma paralela y desordenada.
3. **Inyección de Tráfico Malicioso (Chaos Monkey):** Hilos dedicados a realizar pruebas de penetración automáticas y ataques constantes:
   - *Replays* de transacciones on-chain/USDC.
   - Intentos de bypass de autenticación (ID Spoofing).
   - Inyección de parámetros inválidos (valores negativos, desborde de tipos, caracteres de control).
   - Condiciones de carrera para *double-spend* y *double-booking*.
   - Probar los rate limits de los endpoints de la API.
4. **Reporte Crítico Estructurado:** Generar un reporte final detallado de incidencias ordenado por severidad (`CRITICAL`, `WARNING`, `INFO`) con recomendaciones directas para facilitar la toma de decisiones.

---

## 2. Arquitectura de Simulación Caótica

A continuación se muestra cómo interactúan los diferentes componentes concurrentes con la Base de Datos a través de sesiones aisladas de SQLModel.

```mermaid
graph TD
    subgraph Simulador Caótico (chaos_runner.py)
        A[Orquestador Principal] -->|Instancia| B[Pool de Hilos / Event Loop]
        
        subgraph Clientes Legítimos (Bots)
            B --> Thread_Player1[Bot 1: Whale]
            B --> Thread_Player2[Bot 2: Collector]
            B --> Thread_Player3[Bot 3: Free2Play]
        end
        
        subgraph Agentes de Caos (Atacantes)
            B --> Chaos_Monkey[Chaos Monkey: Race Conditions]
            B --> Hack_Agent1[Attacker: Privilege Escalation]
            B --> Hack_Agent2[Attacker: Replay & Reentrancy]
        end
    end
    
    subgraph Backend FastAPI / Base de Datos
        Thread_Player1 -->|Session A| DB[(PostgreSQL 16)]
        Thread_Player2 -->|Session B| DB
        Thread_Player3 -->|Session C| DB
        Chaos_Monkey -->|Session D - Rapid concurrent writes| DB
        Hack_Agent1 -->|Session E - Malformed Payloads| DB
        Hack_Agent2 -->|Session F - Reused Tx Hash| DB
    end
```

---

## 3. Comportamiento de los Hilos / Corrutinas

### 3.1. Hilos de Clientes Legítimos (Bots)
Cada bot de jugador se iniciará en un hilo dedicado y ejecutará una máquina de estados basada en su personalidad:
* **Whale:** Bucle rápido. Compra de forma intensiva, activa el VIP más alto, juega muchas partidas, decora su cueva con ítems premium. *Think-time: 0.1s - 0.8s*.
* **Collector:** Bucle medio. Compra boosters, los mantiene sellados, forja/desarma cartas, busca completar la colección. *Think-time: 0.5s - 1.5s*.
* **Free2Play:** Bucle lento pero persistente. Ve anuncios para conseguir fragmentos astrales, forja huevos comunes, juega partidas de bajo costo con el dinero generado. *Think-time: 1.0s - 3.0s*.

**Algoritmo del Bot Legítimo:**
```python
def player_loop(player_data, engine):
    while simulation_active:
        # 1. Abrir sesión de base de datos aislada
        with Session(engine) as session:
            # 2. Elegir acción basada en pesos de personalidad y estado actual del jugador
            action = choose_weighted_action(player_data)
            try:
                execute_endpoint_action(action, session, player_data)
            except Exception as e:
                # Logear errores esperados de negocio vs fallos inesperados
                record_incident(action, e)
        # 3. Esperar un tiempo aleatorio antes de la siguiente acción (think-time)
        time.sleep(random.uniform(player_data["min_wait"], player_data["max_wait"]))
```

---

## 4. El Escuadrón del Caos (Inyección de Ataques)

Para simular un entorno hostil real, se implementarán bots maliciosos concurrentes que atacarán los endpoints del backend en paralelo con las transacciones de los usuarios legítimos.

| Tipo de Ataque | Objetivo | Comportamiento del Bot Atacante | Resultado Esperado |
| :--- | :--- | :--- | :--- |
| **Replay Attack** | `checkout.confirm_payment` | Envía repetidamente el mismo `tx_hash` de una compra de USDC exitosa, tanto en ráfagas rápidas como en intervalos espaciados. | **HTTP 409 Conflict** (Bloqueado por `ProcessedTransaction` o barreras del modelo). |
| **ID Spoofing & Escalación** | Endpoints de Cuidado, Juego y Tienda | Peticiones que modifican o interactúan con Axolotitos, Inventarios o Tablas especificando el `verified_user_id` de otro jugador. Intentos de invocar endpoints `/dev/*`. | **HTTP 403 Forbidden / 401 Unauthorized** (Bypass detectado). |
| **Race Conditions (Double Spend)** | `/shop/buy`, `/shop/gashapon/roll` | Envía 10 solicitudes de compra simultáneas con un saldo exacto para 1 sola compra. | **Exactamente 1 éxito**, 9 fallos con **HTTP 400/402** (Control pesimista `SELECT FOR UPDATE` activo). |
| **Double Booking (Lobby)** | `/multiplayer/register` | Intenta registrar el mismo Axolotito en múltiples salas multijugador concurrentes en paralelo. | **Exactamente 1 registro exitoso**, los otros fallan con **HTTP 400**. |
| **Inyección de Límites** | Formularios y Endpoints | Envío de cantidades negativas en compras, montos gigantescos (desborde numérico), strings Unicode nulos (`\x00`) o payloads incompletos. | **HTTP 400/422 ValidationError** (Rechazados por esquemas Pydantic / validadores de modelos). |
| **Bypass de Cooldowns** | Recompensas Diarias, Sueño | Intenta reclamar recompensas diarias múltiples veces en un rango de segundos, o despertar Axolotitos manipulando campos de tiempo. | **HTTP 400 Bad Request** (Validado usando `utcnow()` del servidor). |

---

## 5. Reporte Crítico de Auditoría de Seguridad

Al finalizar la simulación, se recopilarán todos los eventos, logs e incidencias de la simulación caótica. Se clasificará la salida en base a severidades claras:

### 5.1. Niveles de Severidad
1. **CRITICAL 🔴 (Acción Inmediata Requerida):**
   * Un ataque de replay fue exitoso (el backend acreditó fondos dos veces con el mismo hash).
   * Un usuario pudo modificar el estado de un recurso ajeno (modificar cueva ajena, alimentar Axolotito ajeno, etc.).
   * Se produjo una desincronización de saldos de base de datos (pérdida de consistencia decimal).
   * Ocurrió un error `500 Internal Server Error` debido a condiciones de carrera o bloqueos mutuos (*deadlocks*) no recuperados en PostgreSQL.
2. **WARNING 🟡 (Revisar y Optimizar):**
   * Timeouts en consultas debido a bloqueo de tablas muy duraderos.
   * Transacciones abortadas por PostgreSQL debido a concurrencia que requieren lógica de reintento (*Retry Mechanism*).
   * Intentos de penetración que arrojaron códigos no estandarizados (ej. HTTP 500 en lugar de HTTP 400/422).
3. **INFO 🟢 (Comportamiento Correcto):**
   * Ataques y payloads maliciosos bloqueados exitosamente por el backend (HTTP 400, 402, 403, 409, 422).
   * Flujos de juego normales de los bots completados sin incidentes.

---

## 6. Plan de Implementación de la Tarea

### Paso 1: Creación del Módulo Chaos Runner
* Crear `backend/app/scripts/simulation/chaos_runner.py`.
* Implementar el motor de orquestación asíncrona o basado en `concurrent.futures.ThreadPoolExecutor` para manejar el paralelismo.
* Inicializar sesiones de base de datos individuales por cada hilo/bot.

### Paso 2: Implementación de Máquinas de Estado para los Bots
* Migrar las fases actuales (`phase_03_boosters.py`, `phase_08_solo.py`, `phase_09_multi.py`) a funciones modulares de acción de un solo paso que un bot pueda invocar de forma aleatoria basada en su personalidad.

### Paso 3: Codificación de Hilos de Caos (Chaos Monkey)
* Desarrollar los bots atacantes especializados en replays, escalación, dobles gastos y desbordes numéricos.
* Intercalar las llamadas de ataque en paralelo con la actividad normal de los bots.

### Paso 4: Colector y Formateador del Reporte Crítico
* Implementar un despachador central de excepciones y respuestas HTTP que intercepte y clasifique cada código devuelto por el backend.
* Diseñar la plantilla de salida del reporte en Markdown (`chaos_simulation_report.md`) que muestre estadísticas de throughput, porcentaje de mitigación de ataques y la lista de eventos críticos.

---

## 7. Criterios de Aceptación
* El simulador caótico puede correr concurrentemente con un mínimo de 5 hilos de jugadores y 3 hilos de ataque en paralelo.
* El sistema PostgreSQL no debe corromper datos bajo la carga concurrente.
* Todos los ataques maliciosos conocidos deben ser atajados y reflejarse en la sección `INFO` o `WARNING` del reporte (nada debe pasar a `CRITICAL` a menos que exista una vulnerabilidad real).
* El reporte de salida debe detallar exactamente qué endpoints sufrieron bloqueos de base de datos o latencias extremas.
