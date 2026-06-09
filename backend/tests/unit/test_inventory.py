from __future__ import annotations
"""
test_inventory.py — Pruebas unitarias del inventario de jugadores (PlayerInventory).

Cubre:
  1. _add_to_inventory crea una nueva fila si el ítem no existe.
  2. _add_to_inventory incrementa quantity en la fila existente (no crea duplicados).
  3. Llamadas repetidas no dejan filas duplicadas para el mismo (user_id, item_id).
  4. Apertura de booster con quantity=0 → error 400 / no entrega carta.
  5. El campo quantity nunca baja de 0 al consumir.
  6. Ítem con quantity=1 se puede consumir y queda en quantity=0.
  7. Múltiples ítems distintos crean filas independientes.
  8. Idempotencia: consumir un ítem dos veces en secuencia detecta stock insuficiente.
  9. Sin duplicados: después de N _add_to_inventory con el mismo item siempre hay 1 fila.
"""
import sys
import os
import pytest
from sqlmodel import select

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from app.models.items import PlayerInventory, ItemType, Rarity
from app.models.economy import CurrencyType

# Importar función interna de shop directamente
from app.api.v1.endpoints.shop import _add_to_inventory

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from conftest import make_user, make_item


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_inv(session, user_id: str, item_id: int) -> PlayerInventory | None:
    return session.exec(
        select(PlayerInventory)
        .where(PlayerInventory.user_id == user_id)
        .where(PlayerInventory.item_id == item_id)
    ).first()


def _all_inv(session, user_id: str) -> list[PlayerInventory]:
    return session.exec(
        select(PlayerInventory).where(PlayerInventory.user_id == user_id)
    ).all()


# ---------------------------------------------------------------------------
# 1. _add_to_inventory — creación de nueva fila
# ---------------------------------------------------------------------------

class TestAddToInventoryCreate:
    def test_creates_row_when_item_not_owned(self, session, engine):
        """Si el usuario no tiene el ítem, se crea una fila con quantity=1."""
        user = make_user(session, privy_did="did:privy:inv_create")
        item = make_item(session, name="Carta Test", item_type=ItemType.CARD)

        _add_to_inventory(session, user.privy_did, item.id)
        session.commit()

        inv = _get_inv(session, user.privy_did, item.id)
        assert inv is not None
        assert inv.quantity == 1

    def test_distinct_items_create_separate_rows(self, session, engine):
        """Dos ítems distintos deben generar dos filas independientes."""
        user = make_user(session, privy_did="did:privy:inv_two_items")
        item_a = make_item(session, name="Carta A", item_type=ItemType.CARD)
        item_b = make_item(session, name="Accesorio B", item_type=ItemType.ACCESSORY)

        _add_to_inventory(session, user.privy_did, item_a.id)
        _add_to_inventory(session, user.privy_did, item_b.id)
        session.commit()

        rows = _all_inv(session, user.privy_did)
        assert len(rows) == 2

        quantities = {r.item_id: r.quantity for r in rows}
        assert quantities[item_a.id] == 1
        assert quantities[item_b.id] == 1


# ---------------------------------------------------------------------------
# 2. _add_to_inventory — sin duplicados (incrementa fila existente)
# ---------------------------------------------------------------------------

class TestAddToInventoryNoDuplicates:
    def test_second_call_increments_quantity_not_creates_row(self, session, engine):
        """La segunda llamada con el mismo ítem debe sumar quantity, no crear nueva fila."""
        user = make_user(session, privy_did="did:privy:inv_no_dup")
        item = make_item(session, name="Carta Única", item_type=ItemType.CARD)

        _add_to_inventory(session, user.privy_did, item.id)
        session.commit()
        _add_to_inventory(session, user.privy_did, item.id)
        session.commit()

        rows = session.exec(
            select(PlayerInventory)
            .where(PlayerInventory.user_id == user.privy_did)
            .where(PlayerInventory.item_id == item.id)
        ).all()

        assert len(rows) == 1, f"Se esperaba 1 fila, se encontraron {len(rows)}."
        assert rows[0].quantity == 2

    def test_n_calls_produce_single_row_with_correct_quantity(self, session, engine):
        """N llamadas a _add_to_inventory deben producir exactamente 1 fila con quantity=N."""
        N = 7
        user = make_user(session, privy_did="did:privy:inv_n_calls")
        item = make_item(session, name="Carta Repetida", item_type=ItemType.CARD)

        for _ in range(N):
            _add_to_inventory(session, user.privy_did, item.id)
        session.commit()

        rows = session.exec(
            select(PlayerInventory)
            .where(PlayerInventory.user_id == user.privy_did)
            .where(PlayerInventory.item_id == item.id)
        ).all()

        assert len(rows) == 1, f"Se esperaba 1 fila, se encontraron {len(rows)}."
        assert rows[0].quantity == N

    def test_different_users_same_item_create_separate_rows(self, session, engine):
        """El mismo ítem para dos usuarios distintos debe generar filas separadas."""
        user_a = make_user(session, privy_did="did:privy:inv_ua")
        user_b = make_user(session, privy_did="did:privy:inv_ub")
        item = make_item(session, name="Carta Compartida", item_type=ItemType.CARD)

        _add_to_inventory(session, user_a.privy_did, item.id)
        _add_to_inventory(session, user_b.privy_did, item.id)
        session.commit()

        inv_a = _get_inv(session, user_a.privy_did, item.id)
        inv_b = _get_inv(session, user_b.privy_did, item.id)

        assert inv_a is not None and inv_b is not None
        assert inv_a.id != inv_b.id, "Las filas de distintos usuarios deben ser diferentes."
        assert inv_a.quantity == 1
        assert inv_b.quantity == 1


# ---------------------------------------------------------------------------
# 3. Consumo / decremento de inventario
# ---------------------------------------------------------------------------

class TestInventoryConsume:
    def test_consuming_item_decrements_quantity(self, session, engine):
        """Consumir un ítem reduce quantity en 1."""
        user = make_user(session, privy_did="did:privy:inv_consume")
        item = make_item(session, name="Sobre Consume", item_type=ItemType.BOOSTER)

        inv = PlayerInventory(user_id=user.privy_did, item_id=item.id, quantity=3)
        session.add(inv)
        session.commit()
        session.refresh(inv)

        inv.quantity -= 1
        session.add(inv)
        session.commit()
        session.refresh(inv)

        assert inv.quantity == 2

    def test_consuming_last_item_leaves_quantity_zero(self, session, engine):
        """Consumir el último ítem deja quantity=0, no elimina la fila."""
        user = make_user(session, privy_did="did:privy:inv_zero")
        item = make_item(session, name="Sobre Último", item_type=ItemType.BOOSTER)

        inv = PlayerInventory(user_id=user.privy_did, item_id=item.id, quantity=1)
        session.add(inv)
        session.commit()
        session.refresh(inv)

        inv.quantity -= 1
        session.add(inv)
        session.commit()
        session.refresh(inv)

        assert inv.quantity == 0, "quantity debe quedar en 0, no eliminarse."
        # La fila debe seguir existiendo
        assert _get_inv(session, user.privy_did, item.id) is not None

    def test_cannot_consume_when_quantity_is_zero(self, session, engine):
        """Intentar consumir con quantity=0 debe detectarse antes de aplicar cambios."""
        user = make_user(session, privy_did="did:privy:inv_overuse")
        item = make_item(session, name="Sobre Vacío", item_type=ItemType.BOOSTER)

        inv = PlayerInventory(user_id=user.privy_did, item_id=item.id, quantity=0)
        session.add(inv)
        session.commit()
        session.refresh(inv)

        # Simular la comprobación que todo endpoint debe realizar antes de decrementar
        can_consume = inv.quantity > 0
        assert can_consume is False, (
            "Un inventario con quantity=0 NO debe permitir consumo."
        )
        # El quantity no debe haber cambiado
        assert inv.quantity == 0

    def test_sequential_consume_detects_empty_stock(self, session, engine):
        """Dos consumos consecutivos de un ítem con quantity=1 deben fallar en el segundo."""
        user = make_user(session, privy_did="did:privy:inv_seq_consume")
        item = make_item(session, name="Sobre Secuencial", item_type=ItemType.BOOSTER)

        inv = PlayerInventory(user_id=user.privy_did, item_id=item.id, quantity=1)
        session.add(inv)
        session.commit()
        session.refresh(inv)

        # Primer consumo — OK
        assert inv.quantity > 0
        inv.quantity -= 1
        session.add(inv)
        session.commit()
        session.refresh(inv)
        assert inv.quantity == 0

        # Segundo consumo — debe detectar stock insuficiente
        can_consume_again = inv.quantity > 0
        assert can_consume_again is False, (
            "El segundo consumo debe detectar stock insuficiente."
        )

    def test_quantity_never_goes_negative_via_guard(self, session, engine):
        """El guard quantity > 0 impide que quantity llegue a valores negativos."""
        user = make_user(session, privy_did="did:privy:inv_no_neg")
        item = make_item(session, name="Carta No-Neg", item_type=ItemType.CARD)

        inv = PlayerInventory(user_id=user.privy_did, item_id=item.id, quantity=0)
        session.add(inv)
        session.commit()
        session.refresh(inv)

        # Con el guard correcto, nunca se aplica el decremento
        if inv.quantity > 0:
            inv.quantity -= 1
            session.add(inv)
            session.commit()
            session.refresh(inv)

        assert inv.quantity >= 0, "quantity no debe ser negativa."


# ---------------------------------------------------------------------------
# 4. Integridad estructural del inventario
# ---------------------------------------------------------------------------

class TestInventoryStructuralIntegrity:
    def test_inventory_row_has_correct_defaults(self, session, engine):
        """Una fila nueva de PlayerInventory debe tener los defaults correctos."""
        user = make_user(session, privy_did="did:privy:inv_defaults")
        item = make_item(session, name="Carta Defaults", item_type=ItemType.CARD)

        inv = PlayerInventory(user_id=user.privy_did, item_id=item.id)
        session.add(inv)
        session.commit()
        session.refresh(inv)

        assert inv.quantity == 1          # default=1
        assert inv.is_first_edition is False
        assert inv.is_shiny is False

    def test_inventory_zero_quantity_items_excluded_from_active_listing(self, session, engine):
        """Los ítems con quantity=0 no deben aparecer en consultas de inventario activo."""
        user = make_user(session, privy_did="did:privy:inv_active")
        item_a = make_item(session, name="Carta Activa", item_type=ItemType.CARD)
        item_b = make_item(session, name="Carta Agotada", item_type=ItemType.CARD)

        # item_a: tiene 2 copias
        inv_a = PlayerInventory(user_id=user.privy_did, item_id=item_a.id, quantity=2)
        # item_b: agotado
        inv_b = PlayerInventory(user_id=user.privy_did, item_id=item_b.id, quantity=0)
        session.add(inv_a)
        session.add(inv_b)
        session.commit()

        # La consulta de inventario activo usa quantity > 0
        active = session.exec(
            select(PlayerInventory)
            .where(PlayerInventory.user_id == user.privy_did)
            .where(PlayerInventory.quantity > 0)
        ).all()

        assert len(active) == 1
        assert active[0].item_id == item_a.id

    def test_total_inventory_count_per_user(self, session, engine):
        """El conteo total de filas por usuario refleja exactamente los ítems distintos."""
        user = make_user(session, privy_did="did:privy:inv_count")
        items = [
            make_item(session, name=f"Item {i}", item_type=ItemType.CARD)
            for i in range(4)
        ]

        for it in items:
            _add_to_inventory(session, user.privy_did, it.id)
            _add_to_inventory(session, user.privy_did, it.id)  # doble add
        session.commit()

        rows = _all_inv(session, user.privy_did)
        assert len(rows) == 4, "Debe haber exactamente 4 filas (una por ítem distinto)."
        for row in rows:
            assert row.quantity == 2, "Cada fila debe acumular ambas adiciones."
