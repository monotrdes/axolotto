from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import Optional, List
from datetime import datetime
import json
import logging

from app.database import get_session
from app.core.auth import get_verified_user_id, verify_no_active_game
from app.models.items import ItemCatalog, PlayerInventory, ItemType, InventoryMarketListing
from app.models.user import User
from app.models.economy import TransactionLedger, CurrencyType, TransactionType, ChainOutbox
from app.models.lobby_models import TreasuryVault
from app.services.bank_service import BankService
from app.services.rarity_service import get_card_dynamic_rarities
from app.core.config import VIP_CONFIG, frj_to_internal, frj_to_display

logger = logging.getLogger("market")
from pydantic import BaseModel

router = APIRouter()

class ListInventoryItemRequest(BaseModel):
    inventory_id: int
    quantity: int
    price_gal: float

@router.post("/inventory/list")
def list_inventory_item(
    request: ListInventoryItemRequest,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(verify_no_active_game),
):
    """Lista un sobre o carta de PlayerInventory para venta P2P en el mercado."""
    user = session.exec(select(User).where(User.privy_did == verified_user_id)).first()
    from app.core.auth import require_tutorial
    if user: require_tutorial(user)
    if request.quantity <= 0:
        raise HTTPException(status_code=400, detail="La cantidad debe ser mayor a 0.")
    if request.price_gal <= 0:
        raise HTTPException(status_code=400, detail="El precio de venta debe ser mayor a 0 FRJ.")

    # 1. Obtener la fila del inventario
    inv_item = session.exec(
        select(PlayerInventory)
        .where(PlayerInventory.id == request.inventory_id)
        .where(PlayerInventory.user_id == verified_user_id)
        .where(PlayerInventory.quantity >= request.quantity)
        .with_for_update()
    ).first()

    if not inv_item:
        raise HTTPException(status_code=400, detail="No posees este ítem en la cantidad solicitada.")

    # 2. Verificar que el item existe en catálogo y es vendible
    item = session.get(ItemCatalog, inv_item.item_id)
    if not item or not item.is_sellable:
        raise HTTPException(status_code=400, detail="Este ítem no se puede vender.")

    # 3. Descontar del inventario activo
    inv_item.quantity -= request.quantity
    if inv_item.quantity <= 0:
        session.delete(inv_item)
    else:
        session.add(inv_item)

    # 4. Crear publicación en mercado
    listing = InventoryMarketListing(
        seller_id=verified_user_id,
        item_id=inv_item.item_id,
        quantity=request.quantity,
        is_first_edition=inv_item.is_first_edition,
        is_shiny=inv_item.is_shiny,
        price_gal=request.price_gal,
        is_active=True
    )
    session.add(listing)
    session.commit()
    session.refresh(listing)

    return {"mensaje": f"Publicación creada con éxito. Listing ID: {listing.id}"}

@router.post("/inventory/{listing_id}/cancel")
def cancel_inventory_listing(
    listing_id: int,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(verify_no_active_game),
):
    """Cancela una publicación de inventario y regresa los ítems al inventario del vendedor."""
    user = session.exec(select(User).where(User.privy_did == verified_user_id)).first()
    from app.core.auth import require_tutorial
    if user: require_tutorial(user)
    listing = session.exec(
        select(InventoryMarketListing)
        .where(InventoryMarketListing.id == listing_id)
        .where(InventoryMarketListing.seller_id == verified_user_id)
        .where(InventoryMarketListing.is_active == True)
        .with_for_update()
    ).first()

    if not listing:
        raise HTTPException(status_code=404, detail="Publicación no encontrada o inactiva.")

    # 1. Regresar ítems al PlayerInventory del vendedor
    inv_item = session.exec(
        select(PlayerInventory)
        .where(PlayerInventory.user_id == verified_user_id)
        .where(PlayerInventory.item_id == listing.item_id)
        .where(PlayerInventory.is_first_edition == listing.is_first_edition)
        .where(PlayerInventory.is_shiny == listing.is_shiny)
        .with_for_update()
    ).first()

    if inv_item:
        inv_item.quantity += listing.quantity
        session.add(inv_item)
    else:
        inv_item = PlayerInventory(
            user_id=verified_user_id,
            item_id=listing.item_id,
            quantity=listing.quantity,
            is_first_edition=listing.is_first_edition,
            is_shiny=listing.is_shiny
        )
        session.add(inv_item)

    # 2. Desactivar y borrar el listing
    session.delete(listing)
    session.commit()

    return {"mensaje": "Publicación cancelada. Ítems devueltos al inventario."}

@router.post("/inventory/{listing_id}/buy")
def buy_inventory_listing(
    listing_id: int,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(verify_no_active_game),
):
    """Compra un sobre o carta listada en el mercado P2P usando Frijolitos (FRJ)."""
    listing = session.exec(
        select(InventoryMarketListing)
        .where(InventoryMarketListing.id == listing_id)
        .where(InventoryMarketListing.is_active == True)
        .with_for_update()
    ).first()

    if not listing:
        raise HTTPException(status_code=404, detail="Publicación no encontrada o ya fue vendida.")

    if listing.seller_id == verified_user_id:
        raise HTTPException(status_code=400, detail="No puedes comprar tu propia publicación.")

    # 1. Checar carteras
    buyer_wallet = BankService.get_or_create_wallet(session, verified_user_id, for_update=True)
    seller_wallet = BankService.get_or_create_wallet(session, listing.seller_id, for_update=True)
    price = listing.price_gal
    price_internal = frj_to_internal(price)

    if buyer_wallet.frijolitos < price_internal:
        raise HTTPException(status_code=400, detail=f"Saldo FRJ insuficiente (requieres {price} FRJ, tienes {frj_to_display(buyer_wallet.frijolitos):.1f} FRJ).")

    # 2. Comisión P2P (con soporte para descuento de VIP del comprador)
    buyer_user = session.exec(select(User).where(User.privy_did == verified_user_id)).first()
    from app.core.auth import require_tutorial
    if buyer_user: require_tutorial(buyer_user)
    commission_rate = 0.05
    if buyer_user and buyer_user.is_vip and buyer_user.vip_tier:
        commission_rate = VIP_CONFIG.get(buyer_user.vip_tier, {}).get("p2p_commission", 0.05)
    commission = int(round(price_internal * commission_rate))
    seller_share = price_internal - commission

    # 3. Transacción financiera interna
    buyer_wallet.frijolitos -= price_internal
    seller_wallet.frijolitos += seller_share

    vault = session.exec(select(TreasuryVault)).first()
    if not vault:
        vault = TreasuryVault(balance=0)
        session.add(vault)
    vault.balance += commission

    # 4. Crear ledger de transacciones
    item = session.get(ItemCatalog, listing.item_id)
    item_name = item.name if item else f"Item #{listing.item_id}"
    
    ledger_buyer = TransactionLedger(
        user_id=verified_user_id, amount=price_internal, currency=CurrencyType.FRIJOLITO,
        tx_type=TransactionType.MARKET_BUY, description=f"Compra P2P: {item_name} x{listing.quantity}"
    )
    ledger_seller = TransactionLedger(
        user_id=listing.seller_id, amount=seller_share, currency=CurrencyType.FRIJOLITO,
        tx_type=TransactionType.REWARD, description=f"Venta P2P: {item_name} x{listing.quantity} (comisión {commission_rate*100:.1f}%)"
    )
    ledger_commission = TransactionLedger(
        user_id="treasury", amount=commission, currency=CurrencyType.FRIJOLITO,
        tx_type=TransactionType.BURN, description=f"Comisión P2P {commission_rate*100:.1f}% {item_name} x{listing.quantity}"
    )

    # 5. Transferencia Web3 on-chain via outbox (si ambos tienen wallets vinculadas)
    seller_user = session.exec(select(User).where(User.privy_did == listing.seller_id)).first()
    if buyer_user and buyer_user.wallet_address and seller_user and seller_user.wallet_address:
        if item:
            if item.item_type == ItemType.BOOSTER:
                metadata = item.item_metadata or {}
                booster_fase = metadata.get("fase", 1)
                session.add(ChainOutbox(
                    user_id=listing.seller_id,
                    operation="transfer_booster",
                    payload_json=json.dumps({
                        "from_address": seller_user.wallet_address,
                        "to_address": buyer_user.wallet_address,
                        "booster_fase": booster_fase,
                        "quantity": listing.quantity,
                    }),
                    status="pending",
                ))
            elif item.item_type == ItemType.CARD:
                session.add(ChainOutbox(
                    user_id=listing.seller_id,
                    operation="transfer_card",
                    payload_json=json.dumps({
                        "from_address": seller_user.wallet_address,
                        "to_address": buyer_user.wallet_address,
                        "card_id": listing.item_id,
                        "quantity": listing.quantity,
                    }),
                    status="pending",
                ))

    # 6. Reasignar propiedad y agregar al PlayerInventory del comprador
    inv_item = session.exec(
        select(PlayerInventory)
        .where(PlayerInventory.user_id == verified_user_id)
        .where(PlayerInventory.item_id == listing.item_id)
        .where(PlayerInventory.is_first_edition == listing.is_first_edition)
        .where(PlayerInventory.is_shiny == listing.is_shiny)
        .with_for_update()
    ).first()

    if inv_item:
        inv_item.quantity += listing.quantity
        session.add(inv_item)
    else:
        inv_item = PlayerInventory(
            user_id=verified_user_id,
            item_id=listing.item_id,
            quantity=listing.quantity,
            is_first_edition=listing.is_first_edition,
            is_shiny=listing.is_shiny
        )
        session.add(inv_item)

    # 7. Completar y guardar cambios
    session.delete(listing)
    session.add(buyer_wallet)
    session.add(seller_wallet)
    session.add(vault)
    session.add(ledger_buyer)
    session.add(ledger_seller)
    session.add(ledger_commission)
    session.commit()
    # Procesar outbox best-effort inline; el worker reintenta si falla
    try:
        from app.services.chain_outbox_worker import process_outbox_sync
        process_outbox_sync(session, max_batch=5)
    except Exception:
        pass

    return {"mensaje": f"Compra de {item_name} x{listing.quantity} realizada con éxito."}

@router.get("/inventory/listings")
def get_inventory_listings(
    item_type: Optional[ItemType] = None,
    sort: Optional[str] = "price_asc",
    skip: int = 0,
    limit: int = 20,
    session: Session = Depends(get_session),
):
    """Devuelve todas las publicaciones activas del mercado de inventario."""
    statement = (
        select(InventoryMarketListing, ItemCatalog)
        .join(ItemCatalog, InventoryMarketListing.item_id == ItemCatalog.id)
        .where(InventoryMarketListing.is_active == True)
    )

    if item_type:
        statement = statement.where(ItemCatalog.item_type == item_type)

    if sort == "price_asc":
        statement = statement.order_by(InventoryMarketListing.price_gal.asc())
    else:
        statement = statement.order_by(InventoryMarketListing.price_gal.desc())

    results = session.exec(statement.offset(skip).limit(limit)).all()

    # Raridades dinámicas para cartas
    dynamic_rarities = get_card_dynamic_rarities(session)

    response_listings = []
    for listing, item in results:
        listing_data = listing.model_dump()
        item_data = item.model_dump()
        
        if item.item_type == ItemType.CARD:
            rarity_info = dynamic_rarities.get(item.id, {"dynamic_rarity": "Común", "circulation": 0})
            item_data["dynamic_rarity"] = rarity_info["dynamic_rarity"]
            item_data["circulation"] = rarity_info["circulation"]
            
        listing_data["item"] = item_data
        response_listings.append(listing_data)

    return response_listings
