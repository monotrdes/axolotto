from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException
from sqlmodel import Session, select

from app.core.config import settings
from app.core.product_policy import require_feature
from app.models.promo import PendingReward, PromoCode
from app.models.items import ItemCatalog, WhitelistEntry
from app.models.user import User


def redeem_promo_code(session: Session, user_id: str, code: str, email: Optional[str] = None) -> dict:
    require_feature(
        settings.ENABLE_PROMOTIONAL_TOKEN_REWARDS,
        "promotional_token_rewards",
    )
    normalized = code.strip().upper()

    user = session.exec(select(User).where(User.privy_did == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    if user.promo_code_attempts >= 3:
        raise HTTPException(
            status_code=429,
            detail="Has superado el límite de 3 intentos fallidos para validar códigos."
        )

    if user.tutorial_completed:
        raise HTTPException(
            status_code=403,
            detail="Este código de corcholata solo es válido para cuentas nuevas."
        )

    if not user.email:
        raise HTTPException(
            status_code=400,
            detail="Tu cuenta de Privy no tiene un correo electrónico verificado. Vincula un correo a tu cuenta antes de canjear."
        )

    # One promo code per person of the same batch or overall (existing constraint)
    already_redeemed = session.exec(
        select(PromoCode).where(PromoCode.redeemed_by == user_id)
    ).first()
    if already_redeemed:
        raise HTTPException(
            status_code=409,
            detail="Ya canjeaste un código promocional. ¡Solo se permite uno por persona!",
        )

    # Lock the code row to prevent concurrent redemption races
    promo = session.exec(
        select(PromoCode).where(PromoCode.code == normalized).with_for_update()
    ).first()
    if not promo:
        user.promo_code_attempts += 1
        session.add(user)
        session.commit()
        intentos_restantes = max(0, 3 - user.promo_code_attempts)
        raise HTTPException(
            status_code=404,
            detail=f"Código no válido. Intentos restantes: {intentos_restantes}."
        )

    if promo.redeemed_by is not None:
        user.promo_code_attempts += 1
        session.add(user)
        session.commit()
        intentos_restantes = max(0, 3 - user.promo_code_attempts)
        raise HTTPException(
            status_code=409,
            detail=f"Este código ya fue canjeado por otra persona. Intentos restantes: {intentos_restantes}."
        )

    rewarded_item_name = None
    rewarded_item_id = None

    # Resolve item name for preview (don't deliver yet)
    if promo.reward_item_id is not None:
        item = session.get(ItemCatalog, promo.reward_item_id)
        if item and item.is_active:
            rewarded_item_name = item.name
            rewarded_item_id = item.id

    # ✅ NUEVO: Guardar premio en PendingReward (se entrega al final del tutorial)
    # en vez de entregar las monedas inmediatamente.
    pending = PendingReward(
        user_id=user_id,
        promo_code_id=promo.id,
        reward_axf=promo.reward_axofichas,
        reward_frj=promo.reward_frijolitos,
        reward_item_id=rewarded_item_id,
        expires_at=datetime.utcnow() + timedelta(days=7),
    )
    session.add(pending)

    # Stamp code as redeemed
    promo.redeemed_by = user_id
    promo.redeemed_at = datetime.utcnow()
    session.add(promo)

    # Whitelist upsert — respects unique constraint on user_id
    existing_wl = session.exec(
        select(WhitelistEntry).where(WhitelistEntry.user_id == user_id)
    ).first()
    already_whitelisted = existing_wl is not None
    if not existing_wl:
        entry = WhitelistEntry(
            user_id=user_id,
            email=user.email,
            source="souvenir",
            phase_access=1,
        )
        session.add(entry)

    session.commit()

    # Build preview
    rewards_preview = []
    if promo.reward_frijolitos > 0:
        rewards_preview.append(f"{promo.reward_frijolitos:.0f} Frijolitos")
    if promo.reward_axofichas > 0:
        rewards_preview.append(f"{promo.reward_axofichas:.0f} Axofichas")
    if rewarded_item_name:
        rewards_preview.append(rewarded_item_name)

    return {
        "status": "pending_tutorial",
        "mensaje": "Código verificado! Tu premio se revelará al terminar el tutorial.",
        "message": "Código verificado! Tu premio se revelará al terminar el tutorial.",
        "reward_preview": {
            "axofichas": promo.reward_axofichas,
            "frijolitos": promo.reward_frijolitos,
            "item": rewarded_item_name or "Ítem exclusivo de lanzamiento",
        },
        "frijolitos_rewarded": promo.reward_frijolitos,
        "axofichas_rewarded": promo.reward_axofichas,
        "item_id": rewarded_item_id,
        "item_name": rewarded_item_name,
        "already_whitelisted": already_whitelisted,
    }
