import sys
import os
import pytest
from sqlmodel import select, Session

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from app.models.items import ItemCatalog, ItemType, PlayerInventory, Rarity
from app.api.v1.endpoints.admin import admin_card_distribution

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from conftest import make_user, make_item


def test_card_distribution_endpoint(session: Session):
    # 1. Crear cartas en el catálogo
    card1 = make_item(session, name="Carta 1", item_type=ItemType.CARD, rarity=Rarity.COMMON)
    card2 = make_item(session, name="Carta 2", item_type=ItemType.CARD, rarity=Rarity.RARE)
    card3 = make_item(session, name="Carta 3", item_type=ItemType.CARD, rarity=Rarity.EPIC)
    
    # Asignar metadata de número de lotería
    card1.item_metadata = {"numero_loteria": 1}
    card2.item_metadata = {"numero_loteria": 2}
    card3.item_metadata = {"numero_loteria": 3}
    session.add_all([card1, card2, card3])
    session.commit()

    # 2. Crear jugadores
    user_a = make_user(session, privy_did="did:privy:usera")
    user_b = make_user(session, privy_did="did:privy:userb")

    # 3. Dar inventario a los jugadores
    inv1 = PlayerInventory(user_id=user_a.privy_did, item_id=card1.id, quantity=3, is_shiny=False, is_first_edition=True)
    inv2 = PlayerInventory(user_id=user_b.privy_did, item_id=card1.id, quantity=1, is_shiny=True, is_first_edition=False)
    inv3 = PlayerInventory(user_id=user_a.privy_did, item_id=card2.id, quantity=5, is_shiny=True, is_first_edition=True)
    
    session.add_all([inv1, inv2, inv3])
    session.commit()

    # 4. Invocar el endpoint directamente pasando la sesión de prueba
    response = admin_card_distribution(None, session)

    # 5. Validar respuestas y métricas
    assert response["total_unique_cards"] >= 3
    assert response["total_copies_in_circulation"] >= 9  # 3 + 1 + 5
    assert response["total_shiny_in_circulation"] >= 6   # 1 (inv2) + 5 (inv3)
    assert response["total_first_edition_in_circulation"] >= 8  # 3 (inv1) + 5 (inv3)

    # Validar que los conteos de distribución de rareza estén presentes
    assert "catalog_rarity_distribution" in response
    assert "circulation_rarity_distribution" in response

    # Validar que retorne el listado detallado de cartas
    assert len(response["cards"]) >= 3
    c1_res = next((c for c in response["cards"] if c["id"] == card1.id), None)
    assert c1_res is not None
    assert c1_res["total_circulation"] == 4
    assert c1_res["shiny_circulation"] == 1
    assert c1_res["first_edition_circulation"] == 3
    assert c1_res["numero_loteria"] == 1
