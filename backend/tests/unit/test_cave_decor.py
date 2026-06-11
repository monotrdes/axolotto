"""
test_cave_decor.py — Taxonomía de slots tipados y equipamiento de decoración.

Cubre (plan task-84, rediseño del Santuario):
  - _slot_layout: cuadra con decor_slots por nivel y respeta gating
    (LUZ desde nivel 2, MESA/SILLAS con mesa, MANTEL desde nivel 4)
  - /decorations/update: slot fuera del nivel, subcategoría incorrecta,
    MANTEL sin MESA, equip descuenta inventario, unequip lo devuelve
  - slots ausentes del body se tratan como removidos (item vuelve al inventario)
"""
import json

import pytest
from fastapi import HTTPException

from app.api.v1.endpoints.cave_decor import (
    SUBCATEGORY_ORDER,
    UpdateDecorationsRequest,
    _get_decor_slots,
    _slot_layout,
    update_cave_decorations,
)
from app.models.items import ItemType, PlayerInventory
from tests.conftest import make_item, make_user


# ── Helpers ────────────────────────────────────────────────────────────────

def _make_decor_item(session, name, subcat, **extra_meta):
    return make_item(
        session,
        name=name,
        item_type=ItemType.CAVE_ITEM,
        price_gal=300,
        item_metadata={"cave_subcategory": subcat, "emoji": "🏺", **extra_meta},
    )


def _give_item(session, user_id, item_id, qty=1):
    session.add(PlayerInventory(user_id=user_id, item_id=item_id, quantity=qty))
    session.commit()


def _inv_qty(session, user_id, item_id):
    from sqlmodel import select
    inv = session.exec(
        select(PlayerInventory)
        .where(PlayerInventory.user_id == user_id)
        .where(PlayerInventory.item_id == item_id)
    ).first()
    return inv.quantity if inv else 0


# ── _slot_layout ───────────────────────────────────────────────────────────

@pytest.mark.parametrize("level", range(1, 9))
def test_slot_layout_cuadra_con_decor_slots(level):
    layout = _slot_layout(level)
    assert len(layout) == _get_decor_slots(level)
    # slot_ids únicos y con subcategorías válidas
    ids = [s["slot_id"] for s in layout]
    assert len(set(ids)) == len(ids)
    assert all(s["subcategory"] in SUBCATEGORY_ORDER for s in layout)


def test_slot_layout_gating_por_nivel():
    def subcats(level):
        return {s["subcategory"] for s in _slot_layout(level)}

    # Nivel 1: solo ambiente + fondo
    assert subcats(1) == {"AMBIENTE", "FONDO"}
    # Nivel 2: aparece la luz, aún sin mesa
    assert "LUZ" in subcats(2) and "MESA" not in subcats(2)
    # Nivel 3: mesa y sillas (has_table), todavía sin mantel
    assert {"MESA", "SILLAS"} <= subcats(3) and "MANTEL" not in subcats(3)
    # Nivel 4+: mantel y primer especial
    assert {"MANTEL", "ESPECIAL"} <= subcats(4)
    # Nivel 8: layout completo (16 slots)
    assert len(_slot_layout(8)) == 16


# ── /decorations/update ────────────────────────────────────────────────────

def test_equip_valido_descuenta_inventario(session):
    user = make_user(session, privy_did="did:privy:decor1")
    item = _make_decor_item(session, "Loto de Papel", "FONDO", focus_bonus=0.01)
    _give_item(session, user.privy_did, item.id)

    resp = update_cave_decorations(
        body=UpdateDecorationsRequest(decorations={"FONDO_0": item.id}),
        session=session,
        verified_user_id=user.privy_did,
    )

    assert resp["decorations"] == {"FONDO_0": item.id}
    assert resp["used_slots"] == 1
    assert str(item.id) in resp["items"]
    assert resp["items"][str(item.id)]["subcategory"] == "FONDO"
    assert any(s["slot_id"] == "FONDO_0" for s in resp["slots"])
    assert _inv_qty(session, user.privy_did, item.id) == 0


def test_slot_fuera_del_nivel_rechazado(session):
    # Nivel 1 no tiene MESA_0 (mesa llega en nivel 3)
    user = make_user(session, privy_did="did:privy:decor2")
    mesa = _make_decor_item(session, "Mesa de Trajinera", "MESA")
    _give_item(session, user.privy_did, mesa.id)

    with pytest.raises(HTTPException) as exc:
        update_cave_decorations(
            body=UpdateDecorationsRequest(decorations={"MESA_0": mesa.id}),
            session=session,
            verified_user_id=user.privy_did,
        )
    assert exc.value.status_code == 400


def test_subcategoria_incorrecta_rechazada(session):
    user = make_user(session, privy_did="did:privy:decor3")
    fondo = _make_decor_item(session, "Helecho Marino", "FONDO")
    _give_item(session, user.privy_did, fondo.id)

    with pytest.raises(HTTPException) as exc:
        update_cave_decorations(
            body=UpdateDecorationsRequest(decorations={"AMBIENTE_0": fondo.id}),
            session=session,
            verified_user_id=user.privy_did,
        )
    assert exc.value.status_code == 400
    assert "AMBIENTE" in exc.value.detail


def test_mantel_sin_mesa_rechazado(session):
    user = make_user(session, privy_did="did:privy:decor4")
    user.cave_level = 4  # MANTEL_0 existe desde nivel 4
    session.add(user)
    session.commit()
    mantel = _make_decor_item(session, "Mantel Tenango", "MANTEL")
    _give_item(session, user.privy_did, mantel.id)

    with pytest.raises(HTTPException) as exc:
        update_cave_decorations(
            body=UpdateDecorationsRequest(decorations={"MANTEL_0": mantel.id}),
            session=session,
            verified_user_id=user.privy_did,
        )
    assert exc.value.status_code == 400
    assert "mesa" in exc.value.detail.lower()


def test_mantel_con_mesa_permitido(session):
    user = make_user(session, privy_did="did:privy:decor5")
    user.cave_level = 4
    session.add(user)
    session.commit()
    mesa = _make_decor_item(session, "Mesa de Obsidiana", "MESA")
    mantel = _make_decor_item(session, "Mantel Tenango", "MANTEL")
    _give_item(session, user.privy_did, mesa.id)
    _give_item(session, user.privy_did, mantel.id)

    resp = update_cave_decorations(
        body=UpdateDecorationsRequest(
            decorations={"MESA_0": mesa.id, "MANTEL_0": mantel.id}
        ),
        session=session,
        verified_user_id=user.privy_did,
    )
    assert resp["used_slots"] == 2


def test_unequip_devuelve_al_inventario(session):
    user = make_user(session, privy_did="did:privy:decor6")
    item = _make_decor_item(session, "Vasija Pintada", "FONDO")
    _give_item(session, user.privy_did, item.id)

    update_cave_decorations(
        body=UpdateDecorationsRequest(decorations={"FONDO_0": item.id}),
        session=session,
        verified_user_id=user.privy_did,
    )
    assert _inv_qty(session, user.privy_did, item.id) == 0

    # Quitar con null explícito
    resp = update_cave_decorations(
        body=UpdateDecorationsRequest(decorations={"FONDO_0": None}),
        session=session,
        verified_user_id=user.privy_did,
    )
    assert resp["used_slots"] == 0
    assert _inv_qty(session, user.privy_did, item.id) == 1


def test_slot_ausente_del_body_se_remueve_y_devuelve(session):
    # El body es el estado deseado completo: omitir un slot equipado lo
    # remueve y el item NO se pierde (vuelve al inventario).
    user = make_user(session, privy_did="did:privy:decor7")
    fondo = _make_decor_item(session, "Helecho de Papel", "FONDO")
    ambiente = _make_decor_item(session, "Ambiente Atardecer", "AMBIENTE")
    _give_item(session, user.privy_did, fondo.id)
    _give_item(session, user.privy_did, ambiente.id)

    update_cave_decorations(
        body=UpdateDecorationsRequest(decorations={"FONDO_0": fondo.id}),
        session=session,
        verified_user_id=user.privy_did,
    )

    # Nuevo body solo menciona AMBIENTE_0 → FONDO_0 debe removerse
    resp = update_cave_decorations(
        body=UpdateDecorationsRequest(decorations={"AMBIENTE_0": ambiente.id}),
        session=session,
        verified_user_id=user.privy_did,
    )
    assert resp["decorations"] == {"AMBIENTE_0": ambiente.id}
    assert _inv_qty(session, user.privy_did, fondo.id) == 1


def test_compra_cave_item_con_frj_sin_wallet_web3(session):
    # Las decoraciones no son NFT: se compran con FRJ aunque el usuario no
    # tenga wallet Web3 vinculada, y terminan en PlayerInventory.
    from app.core.prices import CAVE_DECOR_PRICES
    from app.models.economy import CurrencyType
    from app.services.shop_service import ShopService
    from tests.conftest import make_wallet

    precio = CAVE_DECOR_PRICES["common"]
    user = make_user(session, privy_did="did:privy:decor9", wallet_address=None)
    make_wallet(session, user.privy_did, gemas_alga=precio * 2)
    item = make_item(
        session,
        name="Antorcha de Prueba",
        item_type=ItemType.CAVE_ITEM,
        price_gal=precio,
        item_metadata={"cave_subcategory": "LUZ", "emoji": "🕯️"},
    )

    ShopService.buy_item(
        session=session,
        user_id=user.privy_did,
        item_id=item.id,
        payment_currency=CurrencyType.GEMA_ALGA,
    )

    from app.models.economy import Wallet
    from sqlmodel import select
    wallet = session.exec(
        select(Wallet).where(Wallet.user_id == user.privy_did)
    ).first()
    assert wallet.frijolitos == precio  # descontó exactamente el precio
    assert _inv_qty(session, user.privy_did, item.id) == 1


def test_catalogo_seed_consistente():
    # Cada item del seed tiene subcategoría válida, precio FRJ > 0 y emoji.
    from app.scripts.seed_cave_decor import build_catalog

    catalog = build_catalog()
    assert len(catalog) >= 20
    subcats_presentes = set()
    for item in catalog:
        meta = item.item_metadata
        assert item.item_type == ItemType.CAVE_ITEM
        assert item.price_gal and item.price_gal > 0
        assert meta["cave_subcategory"] in SUBCATEGORY_ORDER
        assert meta.get("emoji")
        subcats_presentes.add(meta["cave_subcategory"])
    # Las 7 categorías tienen al menos un item comprable
    assert subcats_presentes == set(SUBCATEGORY_ORDER)


def test_prefijos_viejos_se_descartan_en_lectura(session):
    # Migración: decoraciones con la taxonomía vieja (FLOOR/WALL...) no rompen
    # el GET — se filtran del estado.
    from app.api.v1.endpoints.cave_decor import _build_decorations_response

    user = make_user(session, privy_did="did:privy:decor8")
    user.cave_decorations = json.dumps({"FLOOR_0": 999, "WALL_1": 998})
    session.add(user)
    session.commit()

    resp = _build_decorations_response(user, session)
    assert resp["decorations"] == {}
    assert resp["used_slots"] == 0
