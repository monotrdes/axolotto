from sqlmodel import Session, select
from fastapi import HTTPException

from app.models.items import ItemCatalog, ItemType, PlayerInventory
from app.services.bank_service import BankService
from app.services.forge_service import melt_card, forge_card
from app.core.config import frj_to_internal
from app.api.v1.endpoints.shop import MeltCardRequest, ForgeCardRequest

from sim_types import _rng


def phase_card_melter(engine, config, **state) -> dict:
    session: Session = state["session"]
    progress = state["progress"]
    players: list = state["players"]
    stats: dict = state["stats"]
    errors: list = state["errors"]

    progress("  🧪 Iniciando Cenote Místico (Card Melter: Melt & Forge)...")
    from app.models.items import Rarity

    for p in players:
        user_id = p["user_id"]
        personality = p["personality"]

        if personality["name"] not in ("whale", "collector", "aggressive"):
            continue

        melted_any = True
        while melted_any:
            melted_any = False
            inv_cards = session.exec(
                select(PlayerInventory)
                .join(ItemCatalog, PlayerInventory.item_id == ItemCatalog.id)
                .where(
                    PlayerInventory.user_id == user_id,
                    ItemCatalog.item_type == ItemType.CARD,
                    PlayerInventory.quantity >= 5,
                    PlayerInventory.is_shiny == False
                )
            ).all()

            for inv in inv_cards:
                card = session.get(ItemCatalog, inv.item_id)
                if not card or card.rarity not in (Rarity.COMMON, Rarity.RARE, Rarity.EPIC):
                    continue

                cost_map = {Rarity.COMMON: 100.0, Rarity.RARE: 250.0, Rarity.EPIC: 1500.0}
                cost = cost_map.get(card.rarity, 99999.0)

                wallet = BankService.get_or_create_wallet(session, user_id)
                if wallet.frijolitos >= frj_to_internal(cost):
                    try:
                        res = melt_card(
                            session=session,
                            user_id=user_id,
                            card_id=inv.item_id,
                            is_first_edition=inv.is_first_edition,
                        )
                        stats["cards_melted"] = stats.get("cards_melted", 0) + 5
                        stats["melter_fusions"] = stats.get("melter_fusions", 0) + 1
                        new_card_name = res.get("new_card", {}).get("name", "?")
                        new_card_rarity = res.get("new_card", {}).get("rarity", "?")
                        print(f"  🧪 {user_id}: fundió 5 copias de '{card.name}' ({card.rarity.value}) -> obtuvo '{new_card_name}' ({new_card_rarity})")
                        melted_any = True
                        break
                    except HTTPException as e:
                        errors.append(f"melt {user_id}: {e.detail}")

        wallet = BankService.get_or_create_wallet(session, user_id)
        forge_options = [
            ("Legendaria", Rarity.LEGENDARY, "frag_legendario", 500, 3000.0),
            ("Épica", Rarity.EPIC, "frag_epico", 250, 1000.0),
            ("Rara", Rarity.RARE, "frag_raro", 100, 500.0),
            ("Común", Rarity.COMMON, "frag_comun", 50, 100.0)
        ]

        for rarity_label, rarity_enum, frag_field, frag_cost, gal_cost in forge_options:
            frags_qty = getattr(wallet, frag_field, 0)
            if frags_qty >= frag_cost and wallet.frijolitos >= frj_to_internal(gal_cost):
                owned_card_ids = session.exec(
                    select(PlayerInventory.item_id)
                    .join(ItemCatalog, PlayerInventory.item_id == ItemCatalog.id)
                    .where(PlayerInventory.user_id == user_id, ItemCatalog.item_type == ItemType.CARD)
                ).all()

                forgeable_cards = session.exec(
                    select(ItemCatalog)
                    .where(
                        ItemCatalog.item_type == ItemType.CARD,
                        ItemCatalog.rarity == rarity_enum,
                        ItemCatalog.is_active == True,
                        ~ItemCatalog.id.in_(owned_card_ids) if owned_card_ids else True
                    )
                ).all()

                if not forgeable_cards:
                    forgeable_cards = session.exec(
                        select(ItemCatalog)
                        .where(ItemCatalog.item_type == ItemType.CARD, ItemCatalog.rarity == rarity_enum, ItemCatalog.is_active == True)
                    ).all()

                if forgeable_cards:
                    target_card = _rng.choice(forgeable_cards)
                    try:
                        res = forge_card(
                            session=session,
                            user_id=user_id,
                            target_card_id=target_card.id,
                        )
                        stats["cards_forged"] = stats.get("cards_forged", 0) + 1
                        print(f"  🔨 {user_id}: forjó '{target_card.name}' ({rarity_label}) usando {frag_cost} fragmentos y {gal_cost} FRJ")
                        wallet = BankService.get_or_create_wallet(session, user_id)
                    except HTTPException as e:
                        errors.append(f"forge {user_id}: {e.detail}")

    return {}
