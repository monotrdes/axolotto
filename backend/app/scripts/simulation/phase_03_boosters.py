from sqlmodel import Session, select
from fastapi import HTTPException

from app.models.economy import CurrencyType
from app.models.items import ItemCatalog, ItemType, PlayerInventory
from app.models.user import User
from app.services.shop_service import ShopService
from app.api.v1.endpoints.shop import open_booster, OpenBoosterRequest
from app.core.config import VIP_CONFIG

from sim_types import BOOSTER_OPEN_STRATEGY, _rng


def _calc_vip_savings(session: Session, user_id: str, item: ItemCatalog) -> float:
    """Devuelve cuánto AXF se ahorró un jugador VIP en esta compra (0 si no es VIP)."""
    if item.item_type == ItemType.EGG or not item.price_axg:
        return 0.0
    user = session.exec(select(User).where(User.privy_did == user_id)).first()
    if not user or not user.is_vip or not user.vip_tier:
        return 0.0
    discount = VIP_CONFIG.get(user.vip_tier, {}).get("discount", 0.0)
    return round(item.price_axg * discount, 2)


def phase_buy_boosters(engine, config, **state) -> dict:
    """
    COMPRA boosters normales y foil para cada jugador de acuerdo a su pool de personalidad.
    Los sobres quedan SELLADOS en el inventario — no se abren aquí.
    Llama a phase_open_boosters() cuando quieras abrirlos.
    """
    session: Session = state["session"]
    progress = state["progress"]
    players: list = state["players"]
    stats: dict = state["stats"]
    errors: list = state["errors"]

    progress("  📦 Comprando boosters (quedan sellados en inventario)...")

    all_boosters = session.exec(
        select(ItemCatalog).where(
            ItemCatalog.item_type == ItemType.BOOSTER,
            ItemCatalog.is_active == True,
        )
    ).all()

    if not all_boosters:
        progress("  ⚠️  Sin boosters activos en catálogo. Saltando fase.")
        return {}

    normal_boosters = [b for b in all_boosters if not (b.item_metadata or {}).get("is_foil")]
    foil_boosters   = [b for b in all_boosters if     (b.item_metadata or {}).get("is_foil")]

    for p in players:
        user_id     = p["user_id"]
        personality = p["personality"]

        # — Boosters normales —
        for _ in range(personality["boosters_normal"]):
            active_normal_boosters = session.exec(
                select(ItemCatalog).where(
                    ItemCatalog.item_type == ItemType.BOOSTER,
                    ItemCatalog.is_active == True,
                )
            ).all()
            normal_boosters_list = [b for b in active_normal_boosters if not (b.item_metadata or {}).get("is_foil")]
            booster_item = _rng.choice(normal_boosters_list) if normal_boosters_list else None
            if not booster_item:
                break
            try:
                savings = _calc_vip_savings(session, user_id, booster_item)
                ShopService.buy_item(
                    session=session,
                    user_id=user_id,
                    item_id=booster_item.id,
                    payment_currency=CurrencyType.AXOGEMA,
                )
                stats["boosters_bought"] = stats.get("boosters_bought", 0) + 1
                stats["vip_savings_axg"] = stats.get("vip_savings_axg", 0.0) + savings
                print(f"  📦 {user_id}: compró booster normal '{booster_item.name}' (sellado)")
            except HTTPException as e:
                errors.append(f"booster_buy {user_id}: {e.detail}")

        # — Booster Foil —
        for _ in range(personality["boosters_foil"]):
            active_foil_boosters = session.exec(
                select(ItemCatalog).where(
                    ItemCatalog.item_type == ItemType.BOOSTER,
                    ItemCatalog.is_active == True,
                )
            ).all()
            foil_boosters_list = [b for b in active_foil_boosters if (b.item_metadata or {}).get("is_foil")]
            if foil_boosters_list:
                foil_item = foil_boosters_list[0]
                try:
                    savings = _calc_vip_savings(session, user_id, foil_item)
                    ShopService.buy_item(
                        session=session,
                        user_id=user_id,
                        item_id=foil_item.id,
                        payment_currency=CurrencyType.AXOGEMA,
                    )
                    stats["boosters_foil_bought"] = stats.get("boosters_foil_bought", 0) + 1
                    stats["vip_savings_axg"] = stats.get("vip_savings_axg", 0.0) + savings
                    print(f"  ✨ {user_id}: compró Booster Foil '{foil_item.name}' (sellado)")
                except HTTPException as e:
                    errors.append(f"foil_buy {user_id}: {e.detail}")

        # Resumen final del inventario sellado actual
        sealed_rows = session.exec(
            select(PlayerInventory)
            .join(ItemCatalog, PlayerInventory.item_id == ItemCatalog.id)
            .where(
                PlayerInventory.user_id == user_id,
                ItemCatalog.item_type == ItemType.BOOSTER,
                PlayerInventory.quantity > 0,
            )
        ).all()
        n_sealed = sum(inv.quantity for inv in sealed_rows)
        strategy_label = BOOSTER_OPEN_STRATEGY.get(personality["name"], "all")
        if n_sealed:
            print(f"  💼 {user_id}: {n_sealed} sobre(s) de colección sellados iniciales "
                  f"[estrategia: {strategy_label}]")

    progress(f"  ✅ Sobres comprados: {stats.get('boosters_bought', 0)} normales + "
             f"{stats.get('boosters_foil_bought', 0)} foil | "
             f"cartas: {stats.get('cards_opened', 0)}")
    return {}


def phase_open_boosters(
    engine,
    config,
    *,
    strategy: str = "",
    **state,
) -> dict:
    """
    Abre boosters del inventario del jugador de acuerdo a su estrategia,
    abriendo la mayoría y dejando unos pocos (1-3) sellados.

    strategy values:
        "immediate"  → filter_strategy={"immediate"},            label="inmediato"
        "selective"  → filter_strategy={"selective", "random"},  label="post-incubacion"
        "final"      → filter_strategy={"hoarder"},              label="final"
    """
    session: Session = state["session"]
    progress = state["progress"]
    players: list = state["players"]
    stats: dict = state["stats"]
    errors: list = state["errors"]

    # Map from strategy name to (filter_strategy set, label)
    _strategy_map = {
        "immediate": ({"immediate"}, "inmediato"),
        "selective":  ({"selective", "random"}, "post-incubacion"),
        "final":      ({"hoarder"}, "final"),
    }
    filter_strategy, label = _strategy_map.get(strategy, (None, strategy))

    tag = f" [{label}]" if label else ""
    progress(f"  🎴 Abriendo sobres sellados{tag}...")

    for p in players:
        user_id     = p["user_id"]
        personality = p["personality"]
        strat       = BOOSTER_OPEN_STRATEGY.get(personality["name"], "all")

        if filter_strategy is not None and strat not in filter_strategy:
            continue

        # Recuperar sobres sellados en inventario
        booster_invs = session.exec(
            select(PlayerInventory)
            .join(ItemCatalog, PlayerInventory.item_id == ItemCatalog.id)
            .where(
                PlayerInventory.user_id == user_id,
                ItemCatalog.item_type == ItemType.BOOSTER,
                PlayerInventory.quantity > 0,
            )
        ).all()

        if not booster_invs:
            print(f"  ℹ️  {user_id}{tag}: sin sobres sellados")
            continue

        to_open_list = []
        for inv in booster_invs:
            item = session.get(ItemCatalog, inv.item_id)
            is_foil = (item.item_metadata or {}).get("is_foil", False) if item else False
            qty = inv.quantity

            if strat == "immediate":
                open_qty = qty
            elif strat == "selective":
                if is_foil:
                    open_qty = qty
                else:
                    open_qty = int(qty * 0.80)
                    if open_qty == qty and qty > 1:
                        open_qty = qty - 1
            elif strat == "random":
                open_qty = int(qty * 0.85)
                if open_qty == qty and qty > 1:
                    open_qty = qty - 1
            elif strat == "hoarder":
                open_qty = int(qty * 0.75)
                if open_qty == qty and qty > 1:
                    open_qty = qty - 1
            else:
                open_qty = qty

            if qty > 0 and open_qty == 0:
                open_qty = max(1, int(qty * 0.5))

            if open_qty > 0:
                to_open_list.append((inv, open_qty))

        total_opened = 0
        for inv, open_qty in to_open_list:
            for _ in range(open_qty):
                try:
                    res = open_booster(
                        request=OpenBoosterRequest(item_id=inv.item_id),
                        session=session,
                        verified_user_id=user_id,
                    )
                    cards_gained = len(res.get("cards", []))
                    stats["cards_opened"] = stats.get("cards_opened", 0) + cards_gained
                    shiny = sum(1 for c in res.get("cards", []) if c.get("is_shiny"))
                    total_opened += 1
                except HTTPException as e:
                    errors.append(f"booster_open{tag} {user_id}: {e.detail}")
                    break

        current_sealed = session.exec(
            select(PlayerInventory)
            .join(ItemCatalog, PlayerInventory.item_id == ItemCatalog.id)
            .where(
                PlayerInventory.user_id == user_id,
                ItemCatalog.item_type == ItemType.BOOSTER,
                PlayerInventory.quantity > 0,
            )
        ).all()
        n_sealed = sum(inv.quantity for inv in current_sealed)

        if total_opened > 0:
            print(f"  🎴 {user_id}{tag}: {total_opened} sobre(s) abiertos | {n_sealed} sellado(s) conservado(s)")
        else:
            print(f"  ℹ️  {user_id}{tag}: ningún sobre abierto en este momento | {n_sealed} sellado(s) conservado(s)")

    progress(f"  ✅ Sobres abiertos{tag}. Cartas totales hasta ahora: {stats.get('cards_opened', 0)}")
    return {}
