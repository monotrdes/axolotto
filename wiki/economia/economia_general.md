---
tags: [economia, balance]
description: "Modelo económico: house edge, jackpot, staking de boards, emisión FRJ, mecanismos anti-inflación"
last_modified: "2026-06-07"
source_files: ["backend/simulation_report.txt", "backend/app/core/config.py", "backend/app/services/multiplayer_service.py", "backend/app/services/board_service.py", "backend/app/models/lobby_models.py"]
---

# Economía General — Modelo y Balance

---

## Modelo de Reserva (Distribución del Pozo Multijugador)

Fuente: `multiplayer_service.py` — función de settlement de sala.

Cuando inicia una partida multijugador, el pozo total (`total_collected_gal`) se distribuye así:

| Destino | Porcentaje | Descripción |
|---------|-----------|-------------|
| Premio 1 (primer Lotería) | 35% | Dividido entre todos los ganadores del primer Lotería |
| Premio 2 (Tabla Llena) | 55% | Dividido entre los ganadores de tabla completa |
| Tesorería (TreasuryVault) | 5% | House commission acumulada en DB |
| Jackpot (JackpotVault) | 5% | Contribución al bote acumulado global |
| **Total** | **100%** | — |

> Cuando la sala tiene anfitrión (cave room con host), el 5% extra del anfitrión sale del Premio 1 (que baja a 30%), manteniendo el Premio 2 en 55% y las comisiones en 10%.

---

## House Edge por Sala (Resultados de Simulación)

Fuente: `backend/simulation_report.txt` — simulación real ejecutada con 12 jugadores en el backend.

> Nota: el reporte disponible corresponde a una corrida de prueba del simulador v3 con 12 usuarios (no 50 000 partidas). Los datos de win rate provienen de esa muestra.

### Partidas Individuales (147 jugadas)

| Métrica | Valor |
|---------|-------|
| Partidas totales | 147 |
| Victorias | 44 |
| Win rate jugadores | 29.9% |
| FRJ obtenidas por jugadores | 4 988.82 |
| Partidas autojuego (bot) | 27 |

### Salas Multijugador (13 partidas registradas)

| Sala | Partidas | Victorias | Win rate | Neto promedio ganador FRJ |
|------|----------|-----------|----------|--------------------------|
| Charco de Novatos (`rookie_pool`) | 8 | 3 | ~37.5% | +50.5 a +94.0 (muestra) |
| Fosa del Campeón (`champion_abyss`) | 5 | 1 victorias limpias | ~40% | +57.8 a +136.2 (muestra) |
| **Total multijugador** | 13 | 4 | 31% | — |

**Neto total de jugadores**: -111.5 FRJ (la casa/jackpot retiene el 10% del pozo).

> El house edge efectivo del 10% (5% Tesorería + 5% Jackpot) es el esperado por diseño. En la muestra pequeña el neto negativo refleja que más jugadores perdieron que ganaron, lo cual es estadísticamente normal con n=13.

---

## Jackpot

Fuente: `lobby_models.py` (modelo `JackpotVault`) + `multiplayer_service.py` (lógica de pago).

| Parámetro | Valor |
|-----------|-------|
| Semilla inicial | 1 000 FRJ (fondos de proyecto) |
| Semilla de reinicio estándar | 1 000 FRJ |
| Contribución por partida | 5% del pozo total de la sala |
| Pago al ganador | 90% del JackpotVault acumulado |
| Resto tras pagar | 10% del JackpotVault (mínimo 1 000 FRJ; si cae por debajo, la Tesorería aporta la diferencia) |

### Condición para Ganar el Jackpot

El jackpot solo es elegible si se cumplen **todas** estas condiciones en la sala:

1. El primer Lotería ocurre en el **turno 4, 5 o 6** (ventana estrecha de cartas)
2. La sala tiene **al menos 5 tablas humanas** (no bots)
3. La sala tiene **al menos 2 wallet_address únicas** (anti-sybil)

El ganador recibe el 90% del bote. Si hay múltiples ganadores simultáneos, el 90% se divide entre ellos.

### Bonus Jackpot VIP Axolite

Los jugadores con VIP Axolite reciben un +5% adicional sobre su share individual del jackpot (y también sobre Premio 1 y Premio 2). Se aplica en el momento del settlement.

---

## Staking de Boards (Emisión Pasiva de FRJ)

Fuente: `board_service.py` — funciones `get_board_hourly_rate` y `get_accrued_staking`.

Los boards emiten FRJ pasivamente según la rareza de sus cartas. La tasa base es la suma de los bonos de rareza de las 16 cartas del board, multiplicada por un factor de nivel.

### Bonos por Rareza de Carta (FRJ/hora por carta)

| Rareza | FRJ/hora |
|--------|---------|
| Common | 0.05 |
| Rare | 0.15 |
| Epic | 0.40 |
| Legendary | 1.00 |

> La rareza Uncommon no aparece en el mapa; usa el fallback de 0.05 FRJ/hora (igual que Common).

### Fórmula de Cálculo

```
hourly_rate = sum(rarity_bonus per card) * (1.0 + board.level / 10.0)
accrued_gal = hours_elapsed * hourly_rate   (máximo 24 horas acumuladas sin reclamar)
```

**Ejemplo** — Board nivel 1, 16 cartas Common:
- `hourly_rate = 16 × 0.05 × (1 + 1/10) = 0.88 FRJ/hora`
- `max_24h = 21.12 FRJ`

**Ejemplo** — Board nivel 5, 4 Legendary + 12 Common:
- `hourly_rate = (4×1.00 + 12×0.05) × (1 + 5/10) = 4.60 × 1.5 = 6.90 FRJ/hora`
- `max_24h = 165.6 FRJ`

### Play-to-Stake

El staking pasivo está condicionado a actividad reciente: si el jugador no jugó ninguna partida en las últimas **24 horas**, el acumulado devuelve 0. Esto incentiva la participación activa.

---

## Mecanismos Anti-Inflación

| Mecanismo | Descripción | Moneda quemada |
|-----------|-------------|----------------|
| **Card Melting** | Quemar cartas duplicadas a cambio de FRJ (burn mechanism) | Cartas NFT → FRJ emitidos |
| **Consumibles** | Gastar FRJ en alimento (30–150 FRJ), Solvente (120 FRJ), Gotas (200 FRJ) | FRJ |
| **Entry fees multijugador** | Cada partida recircula FRJ al ecosistema (premios + tesorería + jackpot) | FRJ circula, no se destruye |
| **Desbloqueo de slots** | Gastar FRJ para más ranuras de board (500 → 15 000 FRJ por slot) | FRJ |
| **Cápsulas Gashapon** | Gastar FRJ (1 500 – 22 500) por premios aleatorios | FRJ |
| **VIP diarios** | La emisión VIP es controlada y acotada por tier (40/100/200 FRJ/día máximo) | — (emisión, no quema) |

---

→ Ver [[vip_tiers]] para análisis de valor VIP · [[tablas_precios]] para fees exactos de salas y consumibles · [[../mecanicas/staking]] para tasas de emisión (pendiente de crear)
