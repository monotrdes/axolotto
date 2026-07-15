"""
Endpoint para el sistema de Backers de 2021.
Los inversores originales pueden reclamar sus Webitos Fundadores gratis.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database import get_session
from app.models.items import LegacyBacker, PlayerInventory, ItemCatalog, ItemType
from app.models.user import User
from app.services.web3_service import Web3Service
from app.core.auth import get_verified_user_id
from app.core.config import settings
from app.core.product_policy import require_feature

router = APIRouter()


@router.get("/status")
def get_legacy_status(
    user_id: str,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id)
):
    """
    Comprueba si el usuario autenticado tiene Webitos Fundadores pendientes de reclamar.
    Busca por email o wallet address en la tabla LegacyBacker.
    """
    if user_id != verified_user_id:
        raise HTTPException(status_code=403, detail="No autorizado.")

    user = session.exec(select(User).where(User.privy_did == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    # Buscar por email o wallet (lo que esté registrado)
    backer = None
    if user.email:
        backer = session.exec(
            select(LegacyBacker).where(LegacyBacker.email_or_wallet == user.email.lower())
        ).first()
    if not backer and user.wallet_address:
        backer = session.exec(
            select(LegacyBacker).where(LegacyBacker.email_or_wallet == user.wallet_address.lower())
        ).first()

    if not backer:
        return {"is_legacy_backer": False, "eggs_owed": 0, "eggs_claimed": 0, "eggs_pending": 0}

    eggs_pending = backer.eggs_owed - backer.eggs_claimed
    return {
        "is_legacy_backer": True,
        "eggs_owed": backer.eggs_owed,
        "eggs_claimed": backer.eggs_claimed,
        "eggs_pending": eggs_pending,
        "backer_id": backer.id,
    }


@router.post("/claim")
def claim_legacy_egg(
    user_id: str,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id)
):
    """
    Reclama un Webito Fundador (Fase 1) gratis para el backer de 2021.
    Mintea on-chain, añade al inventario y actualiza eggs_claimed.
    """
    require_feature(
        settings.ENABLE_LEGACY_ASSET_CLAIMS,
        "legacy_asset_claims",
    )
    if user_id != verified_user_id:
        raise HTTPException(status_code=403, detail="No autorizado.")

    user = session.exec(select(User).where(User.privy_did == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    # Buscar el registro de backer
    backer = None
    if user.email:
        backer = session.exec(
            select(LegacyBacker).where(LegacyBacker.email_or_wallet == user.email.lower())
        ).first()
    if not backer and user.wallet_address:
        backer = session.exec(
            select(LegacyBacker).where(LegacyBacker.email_or_wallet == user.wallet_address.lower())
        ).first()

    if not backer:
        raise HTTPException(status_code=404, detail="Este usuario no está en la lista de backers de 2021.")

    eggs_pending = backer.eggs_owed - backer.eggs_claimed
    if eggs_pending <= 0:
        raise HTTPException(status_code=400, detail="Ya reclamaste todos tus Webitos Fundadores. ¡Gracias por tu apoyo!")

    # Buscar ítem Webito Génesis (Fase 1) — ID 1
    egg_item = session.exec(
        select(ItemCatalog).where(ItemCatalog.item_type == ItemType.EGG)
    ).first()
    if not egg_item:
        raise HTTPException(status_code=500, detail="No se encontró el ítem de huevo en el catálogo.")

    if not user.wallet_address:
        raise HTTPException(
            status_code=400,
            detail="Necesitas una wallet verificada para reclamar este activo.",
        )

    # La cadena es autoritativa: un fallo aborta antes de tocar inventario.
    tx_hash = Web3Service.mint_webito_onchain(user.wallet_address)

    # Agregar al inventario
    inv = session.exec(
        select(PlayerInventory)
        .where(PlayerInventory.user_id == user_id)
        .where(PlayerInventory.item_id == egg_item.id)
    ).first()

    if inv:
        inv.quantity += 1
        session.add(inv)
    else:
        inv = PlayerInventory(user_id=user_id, item_id=egg_item.id, quantity=1)
        session.add(inv)

    # Actualizar contador del backer
    backer.eggs_claimed += 1
    session.add(backer)
    session.commit()

    print(f"🥚 Webito Fundador reclamado por backer histórico: {user_id} | TxHash: {tx_hash}")

    remaining = backer.eggs_owed - backer.eggs_claimed
    return {
        "mensaje": f"¡Webito Fundador reclamado con éxito! Quedan {remaining} por reclamar.",
        "tx_hash": tx_hash,
        "eggs_remaining": remaining,
        "item_id": egg_item.id,
    }
