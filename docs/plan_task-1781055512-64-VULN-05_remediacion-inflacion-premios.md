# Plan de Remediación: VULN-05 — Inflación de premios no respaldada en multijugador

**Tarea:** task-1781055512-64-VULN-05  
**Severidad:** 🟠 Alta  
**Auditoría:** docs/AUDITORIA_SEGURIDAD_2026-06-09.md (líneas 153-166)

---

## Problema

En el flujo de liquidación de partidas multijugador (`multiplayer_service.py:300-353, 480-522`), el reparto de premios viola la invariante de conservación de fondos:

1. **Bolsa calculada:** `total_collected_gal = human_boards_count * room.entry_fee_gal`
2. **Reparto nominal:** 35% ganador + 55% segundo + 5% tesorería + 5% jackpot = 100%
3. **Problema:** Se suman DESPUÉS **dos bonuses fantasma**:
   - `luck_bonus = (stat_luck / 1000) * share` → **hasta +10%**
   - `vip_bonus` → **hasta +5%**
   
   Estos bonuses **no se debitan de la bolsa** ni de ningún vault; se acuñan directamente en `escrow_balance_gal`.

4. **Agravante:** VIPs pagan `effective_fee` (reducida), pero la bolsa se computa con `entry_fee_gal` (completa):
   - Bolsa financiada por: `room.entry_fee_gal` (X)
   - Bolsa gastada en: `effective_fee` (0.8X para VIP) + bonuses
   - Resultado: **sobre-financiamiento sistemático**

---

## Escenario de Explotación

```
1. Jugador con stat_luck=900 (9% bonus) y VIP Axolite entra a partida de 100 AXF.
   - Cuota real pagada: 80 AXF (20% descuento VIP)
   - Bolsa esperada: 100 AXF

2. Gana. Su share antes de bonuses: 35 AXF

3. Se aplican bonuses:
   - luck_bonus: 9% × 35 = 3.15 AXF (GENERADO, no pagado por nadie)
   - vip_bonus: 2% = 0.7 AXF (GENERADO, no pagado por nadie)
   - Total recibido: 35 + 3.15 + 0.7 = 38.85 AXF

4. Bolsa: Financiada con 100 AXF, gastada 38.85 en ganador + otros pagos = INFLACIÓN NETA

5. Repetir N veces → FRJ devaluado por creación de fondos sin respaldo.
```

---

## Plan de Remediación

### Fase 1: Arreglo conceptual

**Opción A (Recomendada): Reservar bolsa para bonuses**

Cambiar el cálculo de reparto a:
```
total_collected = human_boards_count * room.entry_fee_gal

# Fondos destinados a jugadores (antes de bonuses)
player_pool = total_collected * 0.95  # 95% (era 35+55+5 = 95%)
treasury_pool = total_collected * 0.05  # 5% (tesorería)

# Dentro de player_pool:
winner_base = player_pool * 0.35 / 0.95  ≈ 36.8%
runner_up_base = player_pool * 0.55 / 0.95  ≈ 57.9%
jackpot = player_pool * 0.05 / 0.95  ≈ 5.3%

# Los bonuses se aplican DENTRO del pool:
# NO se añaden sobre el total, sino que redistribuyen dentro de player_pool
winner_with_luck = winner_base + (luck_bonus como % de winner_base)
```

**Opción B (Alternativa): Vault explícito de bonuses**

Mantener bolsa intacta y alimentar bonuses desde un vault de tesorería separado:
```
# Bolsa para repartos: 100%
winner_share = 35 AXF
runner_up_share = 55 AXF
treasury = 5 AXF
jackpot = 5 AXF

# Bonuses vienen de un reward pool (tesorería o fondo VIP):
luck_bonus_funded = min(available_reward_pool, luck_bonus_amount)
vip_bonus_funded = min(available_reward_pool, vip_bonus_amount)

# Garantía: Σ pagos_finales + fondo_sobrante == total_collected + reward_pool_usado
```

### Fase 2: Implementación

**Archivo:** `backend/app/services/multiplayer_service.py`

#### 2.1 Refactor `settle_room()` (líneas 300-353)

```python
def settle_room(session: Session, room_id: int, user_ids: List[str]):
    """
    Liquida una partida respetando invariante: Σ pagos == Σ recolectado.
    """
    room = session.get(GameRoom, room_id, with_for_update=True)
    
    # Bolsa total recolectada (FUENTE DE VERDAD)
    boards = session.exec(select(GameBoard).where(...)).all()
    human_boards_count = sum(1 for b in boards if not b.is_ai)
    total_collected_gal = human_boards_count * room.entry_fee_gal
    
    # Reparto base (35/55/5/5 del total_collected, sin bonuses fantasma)
    if option == "A":  # In-pool bonuses
        winner_base = total_collected_gal * 0.368  # 35/95
        runner_up_base = total_collected_gal * 0.579  # 55/95
        jackpot_amount = total_collected_gal * 0.053  # 5/95
        treasury_amount = total_collected_gal * 0.05  # 5/100 (constante)
        
        # Bonuses dentro del pool disponible (max el 15% del base)
        winner_bonus = min(winner_base * 0.15, luck_bonus_amount)
        final_winner = winner_base + winner_bonus
        
    elif option == "B":  # Separate vault
        final_winner = winner_base + bonus_from_vault(...)
    
    # INVARIANTE: Validar antes de commit
    total_paid = final_winner + runner_up + jackpot_amount + treasury_amount
    assert total_paid <= total_collected_gal, f"Pagos {total_paid} > bolsa {total_collected_gal}"
    remainder = total_collected_gal - total_paid
    
    # Acreditar + loguear
    accrue_rewards(session, winner_user, final_winner, "luck_bonus" if bonus else "base_prize")
    # Log estructura: {"winner": user_id, "share": amount, "bonus": bonus_type, "room_id": ...}
    
    session.commit()
    return {"total_paid": total_paid, "remainder": remainder}
```

#### 2.2 Refactor `claim_all_staking()` / bonus accrual

En `game_logic.py` o un nuevo `bonus_service.py`, centralizar el cálculo de bonuses:

```python
class BonusCalculator:
    @staticmethod
    def calculate_luck_bonus(base_share: float, stat_luck: int, max_pct: float = 0.10) -> float:
        """Calcula luck_bonus como % del share, capped a max_pct"""
        bonus_pct = min((stat_luck / 1000), max_pct)
        return base_share * bonus_pct
    
    @staticmethod
    def calculate_vip_bonus(user_vip_tier: str, base_share: float, vault: VIPRewardVault) -> tuple:
        """Devuelve (bonus_amount, remaining_vault)"""
        tier_bonus_pct = VIP_TIERS[user_vip_tier]["bonus_multiplier"]
        bonus_amount = base_share * tier_bonus_pct
        
        # Validar que el vault tenga fondos
        if vault.available < bonus_amount:
            bonus_amount = vault.available
        
        return bonus_amount, vault.available - bonus_amount
```

#### 2.3 Validación y reconciliación

Añadir un task periodic que verifique invariantes:

```python
# En backend/app/services/audit_service.py (nuevo)

def validate_game_room_ledger(session: Session, room_id: int) -> bool:
    """
    Comprueba que entrada_total == pagos_salida + saldo_remanente
    """
    room = session.get(GameRoom, room_id)
    
    # Entrada: fees recolectadas
    boards = session.exec(select(GameBoard).where(GameBoard.room_id == room_id)).all()
    entry_total = sum(b.entry_fee_gal for b in boards)
    
    # Salida: premios acreditados
    escrows = session.exec(select(EscrowBalance).where(...)).all()
    payouts = sum(e.balance_gal for e in escrows if e.room_id == room_id)
    
    # Validación
    if entry_total < payouts:
        logger.error(f"INVARIANT VIOLATION room_id={room_id}: "
                     f"entry {entry_total} < payouts {payouts}")
        return False
    
    remainder = entry_total - payouts
    logger.info(f"room_id={room_id} ledger OK: entry={entry_total}, "
                f"payouts={payouts}, remainder={remainder}")
    return True
```

### Fase 3: Testing

**Archivo:** `backend/tests/test_multiplayer_invariants.py` (nuevo)

```python
import pytest
from app.services.multiplayer_service import settle_room, BonusCalculator

def test_settle_room_respects_total_collected():
    """VULN-05: Verificar invariante Σ pagos == Σ entrada"""
    room = create_test_room(entry_fee=100)
    boards = [create_test_board(room, is_ai=False) for _ in range(2)]  # 2 jugadores
    
    session.add_all(boards)
    session.commit()
    
    # Liquidar
    result = settle_room(session, room.id, [boards[0].user_id, boards[1].user_id])
    
    # Validar invariante
    entry_total = 2 * 100  # 2 jugadores × 100 AXF
    payouts = result["total_paid"]
    
    assert payouts <= entry_total, f"Pagos {payouts} exceden entrada {entry_total}"
    assert result["remainder"] >= 0, "Remainder negativo (BUG)"

def test_luck_bonus_capped():
    """VULN-05: Bonus de luck no exceede 10% del share"""
    calculator = BonusCalculator()
    
    # Luck extremo (999)
    bonus = calculator.calculate_luck_bonus(base_share=100, stat_luck=999, max_pct=0.10)
    assert bonus == 10.0, f"Bonus {bonus} debería ser capped a 10"
    
    # Luck normal (500)
    bonus = calculator.calculate_luck_bonus(base_share=100, stat_luck=500, max_pct=0.10)
    assert bonus == 5.0, f"Bonus {bonus} esperado 5.0"

def test_vip_bonus_respects_vault():
    """VULN-05: VIP bonus se retira del vault, no se crea de la nada"""
    vault = VIPRewardVault(available=50)
    calculator = BonusCalculator()
    
    bonus, remaining = calculator.calculate_vip_bonus("Axolite", base_share=100, vault=vault)
    
    # Ejemplo: Axolite = 2%
    assert bonus <= 2.0, "Bonus no debe exceder tier %"
    assert remaining == vault.available - bonus, "Vault debe reducirse"
    assert remaining >= 0, "Vault no puede ser negativo"
```

### Fase 4: Despliegue

1. **Antes de merge:** Ejecutar tests de invariantes y validar que no haya regresiones de rewards en juegos existentes.
2. **Migration:** Opcionalmente auditar las top 1000 partidas históricas y detectar sobre-pagos (si es crítico).
3. **Logging:** Activar logs estructurados de settled rooms (para reconciliación futura).
4. **Monitoreo:** Alertar si invariante se viola en producción (métricas de `total_collected` vs `total_paid`).

---

## Definición de Hecho (DoD)

- [ ] Refactorizar `settle_room()` para respetar invariante de bolsa
- [ ] Tests de invariantes pasen (entry == payouts + remainder)
- [ ] Bonus de luck y VIP capped a sus límites respectivos
- [ ] Logs estructurados de liquidación por partida (JSON con amounts)
- [ ] Validación periódica en audit_service (opción)
- [ ] Zero test regressions en existentes
- [ ] PR comentado + merged a `develop` + entrada en CHANGELOG.md

---

*Generado por la Auditoría de Seguridad Web3 2026-06-09. Remediación de media-alta prioridad.*
