"""Business logic for user endpoints.

All database mutations, reads, and validations live here.
Endpoint handlers in user.py call these functions and return their results.
"""
from sqlmodel import Session, select
from fastapi import HTTPException
from datetime import datetime, timedelta
from typing import Any, Optional
import json

from app.models.user import User
from app.models.items import ItemCatalog, PlayerInventory, ItemType
from app.models.economy import Wallet, CurrencyType, TransactionType, TransactionLedger
from app.models.lobby_models import TreasuryVault
from app.models.axolotito import Axolotito
from app.models.board import PlayerBoard
from app.models.promo import PendingReward, PromoCode
from app.core.config import VIP_CONFIG, settings
from app.services.bank_service import BankService
from app.services.web3_service import Web3Service
from app.services.rarity_service import get_card_dynamic_rarities
from app.api.v1.endpoints.dev import DEV_AUTO_REWARD_AXF, DEV_AUTO_REWARD_FRJ


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _player_luck(axolotitos: list) -> float:
    """SUERTE del usuario = promedio de stat_luck de todos sus Axolotitos."""
    if not axolotitos:
        return 0.0
    return sum(a.stat_luck for a in axolotitos) / len(axolotitos)


def _lookup_or_404(model, id_value: Any, session: Session, detail: str = "Recurso no encontrado."):
    """Helper: get by PK or raise 404."""
    obj = session.get(model, id_value)
    if not obj:
        raise HTTPException(status_code=404, detail=detail)
    return obj


# ---------------------------------------------------------------------------
# Sync / Profile
# ---------------------------------------------------------------------------

def sync_user(
    session: Session,
    privy_did: str,
    email: Optional[str],
    wallet_address: Optional[str],
    verified_user_id: str,
) -> dict:
    """Create or update user, return full sync payload."""
    if privy_did != verified_user_id:
        raise HTTPException(
            status_code=403,
            detail="No autorizado para sincronizar este usuario.",
        )

    db_user = session.exec(
        select(User).where(User.privy_did == privy_did)
    ).first()

    if not db_user:
        # Registro nuevo
        if wallet_address is not None:
            wallet_owner = session.exec(
                select(User).where(User.wallet_address == wallet_address)
            ).first()
            if wallet_owner:
                raise HTTPException(
                    status_code=409,
                    detail="Esta dirección de wallet ya está asociada a otra cuenta.",
                )
        db_user = User(
            privy_did=privy_did,
            email=email,
            wallet_address=wallet_address,
        )
        session.add(db_user)
        mensaje = "¡Bienvenido! Usuario y Wallet registrados."
    else:
        # Actualización inteligente
        if email is not None:
            db_user.email = email

        if wallet_address is not None:
            if (
                db_user.wallet_address
                and db_user.wallet_address != wallet_address
            ):
                raise HTTPException(
                    status_code=403,
                    detail="Tu wallet ya está registrada y verificada. Contacta soporte para solicitar un cambio.",
                )
            if not db_user.wallet_address:
                wallet_owner = session.exec(
                    select(User).where(
                        User.wallet_address == wallet_address,
                        User.privy_did != privy_did,
                    )
                ).first()
                if wallet_owner:
                    raise HTTPException(
                        status_code=409,
                        detail="Esta dirección de wallet ya está asociada a otra cuenta.",
                    )
            db_user.wallet_address = wallet_address

        session.add(db_user)
        mensaje = "Datos de perfil actualizados."

    session.commit()
    session.refresh(db_user)

    wallet = BankService.get_or_create_wallet(session, db_user.privy_did)

    # ── Dev mode: auto corcholata reward ──────────────────────────────────
    is_new_user = mensaje.startswith("¡Bienvenido!")
    if settings.BLOCKCHAIN_MODE == "local" and is_new_user:
        existing_pending = session.exec(
            select(PendingReward).where(PendingReward.user_id == verified_user_id)
        ).first()
        if not existing_pending:
            dev_code = session.exec(
                select(PromoCode).where(PromoCode.code == "DEV_AUTO")
            ).first()
            if not dev_code:
                dev_code = PromoCode(
                    code="DEV_AUTO",
                    batch="dev",
                    reward_type="booster_pack",
                    reward_axofichas=DEV_AUTO_REWARD_AXF,
                    reward_frijolitos=DEV_AUTO_REWARD_FRJ,
                )
                session.add(dev_code)
                session.flush()
            pending = PendingReward(
                user_id=verified_user_id,
                promo_code_id=dev_code.id,
                reward_axf=DEV_AUTO_REWARD_AXF,
                reward_frj=DEV_AUTO_REWARD_FRJ,
                expires_at=datetime.utcnow() + timedelta(days=365),
            )
            session.add(pending)
            session.flush()

    days_remaining = None
    if db_user.is_vip and db_user.vip_expires_at:
        days_remaining = max(
            (db_user.vip_expires_at - datetime.utcnow()).days, 0
        )

    axolotitos = session.exec(
        select(Axolotito).where(Axolotito.user_id == verified_user_id)
    ).all()
    player_luck_value = _player_luck(axolotitos)

    pending_result = session.exec(
        select(PendingReward).where(
            PendingReward.user_id == verified_user_id,
            PendingReward.claimed == False,
        )
    ).first()
    has_pending = pending_result is not None

    return {
        "mensaje": mensaje,
        "wallet": {
            "axofichas": wallet.axofichas,
            "frijolitos": wallet.frijolitos,
            "axogemas": wallet.axofichas,
            "gemas_alga": wallet.frijolitos,
            "vip_tier": db_user.vip_tier if db_user.is_vip else None,
            "vip_expires_at": db_user.vip_expires_at.isoformat()
            if db_user.vip_expires_at
            else None,
            "vip_days_remaining": days_remaining,
            "vip_pending_gal": db_user.vip_pending_gal if db_user.is_vip else 0.0,
        },
        "player_luck": round(player_luck_value, 1),
        "is_new_user": mensaje.startswith("¡Bienvenido!"),
        "tutorial_completed": db_user.tutorial_completed,
        "cave_level": db_user.cave_level,
        "cave_name": db_user.cave_name,
        "has_pending_corcholata_reward": has_pending,
    }


def get_user_inventory(
    session: Session, user_id: str, verified_user_id: str
) -> list:
    """Return all items owned by the user with their details."""
    if user_id != verified_user_id:
        raise HTTPException(
            status_code=403,
            detail="No tienes acceso a los recursos de este usuario.",
        )

    statement = (
        select(ItemCatalog, PlayerInventory)
        .join(PlayerInventory, ItemCatalog.id == PlayerInventory.item_id)
        .where(PlayerInventory.user_id == user_id)
    )
    results = session.exec(statement).all()

    dynamic_rarities = get_card_dynamic_rarities(session)

    response_items = []
    for item, inv in results:
        item_data = item.model_dump()
        if item.item_type == ItemType.CARD:
            rarity_info = dynamic_rarities.get(
                item.id, {"dynamic_rarity": "Común", "circulation": 0}
            )
            item_data["dynamic_rarity"] = rarity_info["dynamic_rarity"]
            item_data["circulation"] = rarity_info["circulation"]
        item_data["inventory_id"] = inv.id
        item_data["quantity"] = inv.quantity
        item_data["is_first_edition"] = inv.is_first_edition
        item_data["is_shiny"] = inv.is_shiny
        response_items.append(item_data)

    return response_items


def get_user_axolotitos(
    session: Session, user_id: str, verified_user_id: str
) -> list:
    """Return owned + actively rented axolotitos for a user."""
    if user_id != verified_user_id:
        raise HTTPException(
            status_code=403,
            detail="No tienes acceso a los recursos de este usuario.",
        )

    owned = session.exec(
        select(Axolotito).where(Axolotito.user_id == user_id)
    ).all()

    now = datetime.utcnow()
    rented = session.exec(
        select(Axolotito)
        .where(Axolotito.renter_id == user_id)
        .where(Axolotito.is_rented == True)
        .where(Axolotito.rent_expires_at > now)
    ).all()

    return owned + rented


# ---------------------------------------------------------------------------
# Bot config
# ---------------------------------------------------------------------------

def update_axolotito_bot_config(
    session: Session,
    axolotito_id: int,
    bot_enabled: bool,
    bot_budget_axf: float,
    bot_loss_limit_axf: float,
    bot_profit_limit_axf: float,
    assigned_board_id: Optional[int],
    verified_user_id: str,
    user_id_from_body: Optional[str] = None,
) -> dict:
    """Update auto-play bot configuration for an axolotito."""
    axolotito = _lookup_or_404(
        Axolotito, axolotito_id, session, detail="Axolotito no encontrado."
    )

    is_owner = axolotito.user_id == verified_user_id
    is_active_renter = (
        axolotito.renter_id == verified_user_id
        and axolotito.is_rented
        and axolotito.rent_expires_at
        and axolotito.rent_expires_at > datetime.utcnow()
    )
    if not (is_owner or is_active_renter) or (
        user_id_from_body is not None and user_id_from_body != verified_user_id
    ):
        raise HTTPException(
            status_code=403,
            detail="No tienes permiso sobre este Axolotito o usuario.",
        )

    if assigned_board_id is not None:
        player_board = session.get(PlayerBoard, assigned_board_id)
        if not player_board:
            raise HTTPException(
                status_code=400, detail="El tablero seleccionado no existe."
            )
        if player_board.is_dead:
            raise HTTPException(
                status_code=400,
                detail="El tablero seleccionado está desarmado (muerta).",
            )

        now_time = datetime.utcnow()
        is_board_owner = player_board.user_id == verified_user_id
        is_board_active_renter = (
            player_board.renter_id == verified_user_id
            and player_board.is_rented
            and player_board.rent_expires_at
            and player_board.rent_expires_at > now_time
        )
        if not (is_board_owner or is_board_active_renter):
            raise HTTPException(
                status_code=400,
                detail="No posees o no tienes rentado este tablero.",
            )

    if (
        bot_budget_axf < 0
        or bot_loss_limit_axf < 0
        or bot_profit_limit_axf < 0
    ):
        raise HTTPException(
            status_code=400,
            detail="El presupuesto y límites deben ser valores positivos.",
        )

    axolotito.bot_enabled = bot_enabled
    axolotito.bot_budget_axg = bot_budget_axf
    axolotito.bot_loss_limit_axg = bot_loss_limit_axf
    axolotito.bot_profit_limit_axg = bot_profit_limit_axf
    axolotito.assigned_board_id = assigned_board_id

    session.add(axolotito)
    session.commit()
    session.refresh(axolotito)

    return {
        "mensaje": "Configuración del bot guardada exitosamente.",
        "axolotito": axolotito,
    }


# ---------------------------------------------------------------------------
# Market — sale & rent listings
# ---------------------------------------------------------------------------

def get_sale_market_axolotitos(
    session: Session, skip: int = 0, limit: int = 20
) -> list:
    """Return axolotitos listed for sale (excludes VIP-frozen)."""
    axos = session.exec(
        select(Axolotito)
        .where(Axolotito.is_listed_for_sale == True)
        .where(Axolotito.status == "idle")
        .where(Axolotito.is_frozen_by_vip == False)
        .offset(skip)
        .limit(limit)
    ).all()

    resultado = []
    for axo in axos:
        owner = session.exec(
            select(User).where(User.privy_did == axo.user_id)
        ).first()
        owner_vip_tier = owner.vip_tier if (owner and owner.is_vip) else None
        axo_dict = axo.model_dump()
        axo_dict["owner_vip_tier"] = owner_vip_tier
        resultado.append(axo_dict)
    return resultado


def get_rent_market_axolotitos(
    session: Session, skip: int = 0, limit: int = 20
) -> list:
    """Return axolotitos listed for rent (excludes VIP-frozen)."""
    now = datetime.utcnow()
    axos = session.exec(
        select(Axolotito)
        .where(Axolotito.is_listed_for_rent == True)
        .where(Axolotito.is_frozen_by_vip == False)
        .where(
            (Axolotito.is_rented == False)
            | (Axolotito.rent_expires_at == None)
            | (Axolotito.rent_expires_at <= now)
        )
        .offset(skip)
        .limit(limit)
    ).all()

    resultado = []
    for axo in axos:
        owner = session.exec(
            select(User).where(User.privy_did == axo.user_id)
        ).first()
        owner_vip_tier = owner.vip_tier if (owner and owner.is_vip) else None
        axo_dict = axo.model_dump()
        axo_dict["owner_vip_tier"] = owner_vip_tier
        resultado.append(axo_dict)
    return resultado


def list_axolotito_for_sale(
    session: Session,
    axolotito_id: int,
    sale_price_gal: float,
    verified_user_id: str,
) -> dict:
    """List an axolotito for sale on the marketplace."""
    axo = _lookup_or_404(
        Axolotito, axolotito_id, session, detail="Axolotito no encontrado."
    )
    if axo.user_id != verified_user_id:
        raise HTTPException(
            status_code=403, detail="No eres dueño de este Axolotito."
        )
    if axo.is_tutorial:
        raise HTTPException(
            status_code=400,
            detail="El Axolotito del tutorial no se puede vender.",
        )
    if axo.is_frozen_by_vip:
        raise HTTPException(
            status_code=423,
            detail="Este Axolotito está congelado. Renueva tu VIP para desbloquearlo.",
        )
    if axo.status != "idle":
        raise HTTPException(
            status_code=400,
            detail="El Axolotito debe estar 'idle' para venderse.",
        )
    if axo.is_rented:
        raise HTTPException(
            status_code=400,
            detail="No puedes vender un Axolotito que está rentado.",
        )
    if axo.is_listed_for_rent:
        raise HTTPException(
            status_code=400,
            detail="Retíralo del mercado de rentas antes de venderlo.",
        )
    if sale_price_gal <= 0:
        raise HTTPException(
            status_code=400,
            detail="El precio de venta debe ser mayor a 0 GAL.",
        )

    axo.is_listed_for_sale = True
    axo.sale_price_gal = sale_price_gal
    session.add(axo)
    session.commit()
    return {
        "mensaje": f"Axolotito '{axo.name}' en venta por {axo.sale_price_gal} GAL."
    }


def cancel_axolotito_sale(
    session: Session, axolotito_id: int, verified_user_id: str
) -> dict:
    """Remove an axolotito from sale listings."""
    axo = _lookup_or_404(
        Axolotito, axolotito_id, session, detail="Axolotito no encontrado."
    )
    if axo.user_id != verified_user_id:
        raise HTTPException(
            status_code=403, detail="No eres dueño de este Axolotito."
        )
    if not axo.is_listed_for_sale:
        raise HTTPException(
            status_code=400, detail="El Axolotito no está en venta."
        )

    axo.is_listed_for_sale = False
    session.add(axo)
    session.commit()
    return {"mensaje": "Publicación de venta cancelada."}


def list_axolotito_for_rent(
    session: Session,
    axolotito_id: int,
    rent_fee_gal: float,
    rent_share_owner_pct: int,
    verified_user_id: str,
) -> dict:
    """List an axolotito for rent on the marketplace."""
    axo = _lookup_or_404(
        Axolotito, axolotito_id, session, detail="Axolotito no encontrado."
    )
    if axo.user_id != verified_user_id:
        raise HTTPException(
            status_code=403, detail="No eres dueño de este Axolotito."
        )
    if axo.is_tutorial:
        raise HTTPException(
            status_code=400,
            detail="El Axolotito del tutorial no se puede rentar.",
        )
    if axo.is_frozen_by_vip:
        raise HTTPException(
            status_code=423,
            detail="Este Axolotito está congelado. Renueva tu VIP para desbloquearlo.",
        )
    if axo.status != "idle":
        raise HTTPException(
            status_code=400,
            detail="El Axolotito debe estar 'idle' para rentarse.",
        )
    if axo.is_rented:
        raise HTTPException(
            status_code=400,
            detail="El Axolotito ya tiene una renta activa.",
        )
    if axo.is_listed_for_sale:
        raise HTTPException(
            status_code=400,
            detail="Retíralo del mercado de ventas antes de rentarlo.",
        )
    if rent_fee_gal <= 0:
        raise HTTPException(
            status_code=400,
            detail="El costo de renta debe ser mayor a 0 GAL.",
        )
    if not (0 <= rent_share_owner_pct <= 100):
        raise HTTPException(
            status_code=400,
            detail="El split debe ser entre 0 y 100.",
        )

    axo.is_listed_for_rent = True
    axo.rent_fee_gal = rent_fee_gal
    axo.rent_share_owner_pct = rent_share_owner_pct
    session.add(axo)
    session.commit()
    return {
        "mensaje": f"Axolotito '{axo.name}' listado en renta."
    }


def cancel_axolotito_rent(
    session: Session, axolotito_id: int, verified_user_id: str
) -> dict:
    """Remove an axolotito from rent listings."""
    axo = _lookup_or_404(
        Axolotito, axolotito_id, session, detail="Axolotito no encontrado."
    )
    if axo.user_id != verified_user_id:
        raise HTTPException(
            status_code=403, detail="No eres dueño de este Axolotito."
        )
    if axo.is_rented:
        raise HTTPException(
            status_code=400,
            detail="No puedes cancelar la publicación con una renta activa.",
        )

    axo.is_listed_for_rent = False
    session.add(axo)
    session.commit()
    return {"mensaje": "Publicación de renta cancelada."}


# ---------------------------------------------------------------------------
# VIP
# ---------------------------------------------------------------------------

def get_vip_status(
    session: Session, verified_user_id: str
) -> dict:
    """Return full VIP status for the authenticated user."""
    user = session.exec(
        select(User).where(User.privy_did == verified_user_id)
    ).first()
    if not user:
        raise HTTPException(
            status_code=404, detail="Usuario no encontrado."
        )

    days_remaining = 0
    if user.is_vip and user.vip_expires_at:
        days_remaining = max(
            (user.vip_expires_at - datetime.utcnow()).days, 0
        )

    config = VIP_CONFIG.get(user.vip_tier or "", {})
    tiers_activated = json.loads(user.vip_tiers_activated or "[]")

    streak_rewards = []
    if user.vip_streak_months >= 3:
        streak_rewards.append("constante")
    if user.vip_streak_months >= 6:
        streak_rewards.append("veterano")
    if user.vip_streak_months >= 12:
        streak_rewards.append("original")
    if user.vip_streak_months >= 24:
        streak_rewards.append("leyenda")

    return {
        "is_vip": user.is_vip,
        "vip_tier": user.vip_tier if user.is_vip else None,
        "vip_expires_at": user.vip_expires_at.isoformat()
        if user.vip_expires_at
        else None,
        "days_remaining": days_remaining,
        "vip_streak_months": user.vip_streak_months,
        "vip_streak_last_renewed": user.vip_streak_last_renewed.isoformat()
        if user.vip_streak_last_renewed
        else None,
        "vip_tiers_activated": tiers_activated,
        "vip_pending_gal": user.vip_pending_gal,
        "vip_pending_gal_expires_at": user.vip_pending_gal_expires_at.isoformat()
        if user.vip_pending_gal_expires_at
        else None,
        "streak_rewards_earned": streak_rewards,
        "vip_auto_renew": user.vip_auto_renew,
        "benefits": {
            "gal_daily": config.get("gal_daily", 0),
            "discount_pct": int(config.get("discount", 0) * 100),
            "capsulas_mensuales": config.get("capsulas_mensuales", {}),
            "table_bonus_slots": config.get("table_bonus_slots", 0),
            "axolotito_bonus_slots": config.get("axolotito_bonus_slots", 0),
            "p2p_commission_pct": config.get("p2p_commission", 0.05) * 100,
            "jackpot_bonus_pct": config.get("jackpot_bonus", 0) * 100,
        }
        if user.is_vip
        else {},
    }


def claim_vip_gal(
    session: Session, verified_user_id: str
) -> dict:
    """Claim accumulated VIP GAL into the user's wallet."""
    user = session.exec(
        select(User).where(User.privy_did == verified_user_id)
    ).first()
    if not user:
        raise HTTPException(
            status_code=404, detail="Usuario no encontrado."
        )
    if not user.is_vip:
        raise HTTPException(
            status_code=403,
            detail="No tienes una suscripción VIP activa.",
        )
    if user.vip_pending_gal <= 0:
        raise HTTPException(
            status_code=400,
            detail="No tienes GAL VIP pendiente de reclamar. Vuelve mañana.",
        )

    amount = user.vip_pending_gal
    wallet = BankService.get_or_create_wallet(session, verified_user_id)
    wallet.frijolitos += amount

    ledger = TransactionLedger(
        user_id=verified_user_id,
        amount=amount,
        currency=CurrencyType.GEMA_ALGA,
        tx_type=TransactionType.REWARD,
        description=f"Bono VIP reclamado ({user.vip_tier})",
    )

    user.vip_pending_gal = 0.0
    user.vip_pending_gal_expires_at = None

    session.add(user)
    session.add(wallet)
    session.add(ledger)
    session.commit()

    return {
        "gal_claimed": amount,
        "mensaje": f"¡Reclamaste {amount:.0f} GAL de tu bono VIP {user.vip_tier.capitalize()}!",
        "wallet_gal_total": wallet.frijolitos,
    }


def set_vip_auto_renew(
    session: Session, enabled: bool, verified_user_id: str
) -> dict:
    """Enable or disable VIP auto-renewal."""
    user = session.exec(
        select(User).where(User.privy_did == verified_user_id)
    ).first()
    if not user:
        raise HTTPException(
            status_code=404, detail="Usuario no encontrado."
        )
    if not user.is_vip:
        raise HTTPException(
            status_code=403,
            detail="Necesitas una suscripción VIP activa para configurar la auto-renovación.",
        )
    user.vip_auto_renew = enabled
    session.add(user)
    session.commit()
    return {
        "vip_auto_renew": user.vip_auto_renew,
        "mensaje": "Auto-renovación activada."
        if enabled
        else "Auto-renovación desactivada.",
    }


# ---------------------------------------------------------------------------
# Rent / Buy Axolotito
# ---------------------------------------------------------------------------

def rent_axolotito(
    session: Session, axolotito_id: int, verified_user_id: str
) -> dict:
    """Rent an axolotito from the marketplace (24h)."""
    axo = session.exec(
        select(Axolotito)
        .where(Axolotito.id == axolotito_id)
        .with_for_update()
    ).first()
    if not axo:
        raise HTTPException(
            status_code=404, detail="Axolotito no encontrado."
        )
    if axo.is_frozen_by_vip:
        raise HTTPException(
            status_code=423,
            detail="Este Axolotito está congelado. Renueva tu VIP para desbloquearlo.",
        )
    if axo.user_id == verified_user_id:
        raise HTTPException(
            status_code=400,
            detail="No puedes rentar tu propio Axolotito.",
        )
    if not axo.is_listed_for_rent:
        raise HTTPException(
            status_code=400,
            detail="Este Axolotito no está en renta.",
        )

    now = datetime.utcnow()
    if axo.is_rented and axo.rent_expires_at and axo.rent_expires_at <= now:
        axo.is_rented = False
        axo.renter_id = None

    if axo.is_rented:
        raise HTTPException(
            status_code=400,
            detail="Renta activa por otro inquilino.",
        )

    renter_wallet = BankService.get_or_create_wallet(
        session, verified_user_id, for_update=True
    )
    owner_wallet = BankService.get_or_create_wallet(
        session, axo.user_id, for_update=True
    )

    fee = axo.rent_fee_gal
    renter_user = session.exec(
        select(User).where(User.privy_did == verified_user_id)
    ).first()
    commission_rate = 0.05
    if renter_user and renter_user.is_vip and renter_user.vip_tier:
        commission_rate = VIP_CONFIG.get(renter_user.vip_tier, {}).get(
            "p2p_commission", 0.05
        )
    commission = round(fee * commission_rate, 2)
    owner_share = fee - commission

    if renter_wallet.frijolitos < fee:
        raise HTTPException(
            status_code=400,
            detail=f"Saldo GAL insuficiente (requieres {fee} GAL).",
        )

    renter_wallet.frijolitos -= fee
    owner_wallet.frijolitos += owner_share

    vault = session.exec(select(TreasuryVault)).first()
    if not vault:
        vault = TreasuryVault()
        session.add(vault)
    vault.balance += commission

    ledger_renter = TransactionLedger(
        user_id=verified_user_id,
        amount=fee,
        currency=CurrencyType.GEMA_ALGA,
        tx_type=TransactionType.MARKET_BUY,
        description=f"Renta de Axolotito #{axo.id}",
    )
    ledger_owner = TransactionLedger(
        user_id=axo.user_id,
        amount=owner_share,
        currency=CurrencyType.GEMA_ALGA,
        tx_type=TransactionType.REWARD,
        description=f"Ingreso por renta de Axolotito #{axo.id} (comisión {commission_rate*100:.1f}%)",
    )
    ledger_treasury = TransactionLedger(
        user_id="treasury",
        amount=commission,
        currency=CurrencyType.GEMA_ALGA,
        tx_type=TransactionType.BURN,
        description=f"Comisión P2P {commission_rate*100:.1f}% renta Axolotito #{axo.id}",
    )

    axo.is_rented = True
    axo.renter_id = verified_user_id
    axo.rent_expires_at = now + timedelta(days=1)
    axo.status = "idle"

    session.add(renter_wallet)
    session.add(owner_wallet)
    session.add(ledger_renter)
    session.add(ledger_owner)
    session.add(ledger_treasury)
    session.add(axo)
    session.commit()

    return {
        "mensaje": f"¡Rentas a '{axo.name}' con éxito por 24 horas!",
        "rent_expires_at": axo.rent_expires_at,
    }


def buy_axolotito(
    session: Session, axolotito_id: int, verified_user_id: str
) -> dict:
    """Buy an axolotito from the marketplace."""
    axo = session.exec(
        select(Axolotito)
        .where(Axolotito.id == axolotito_id)
        .with_for_update()
    ).first()
    if not axo:
        raise HTTPException(
            status_code=404, detail="Axolotito no encontrado."
        )
    if axo.is_frozen_by_vip:
        raise HTTPException(
            status_code=423,
            detail="Este Axolotito está congelado. Renueva tu VIP para desbloquearlo.",
        )
    if axo.user_id == verified_user_id:
        raise HTTPException(
            status_code=400,
            detail="No puedes comprar tu propio Axolotito.",
        )
    if not axo.is_listed_for_sale:
        raise HTTPException(
            status_code=400,
            detail="Este Axolotito no está en venta.",
        )
    if axo.is_rented:
        raise HTTPException(
            status_code=400,
            detail="El Axolotito está rentado actualmente.",
        )

    buyer_wallet = BankService.get_or_create_wallet(
        session, verified_user_id, for_update=True
    )
    seller_wallet = BankService.get_or_create_wallet(
        session, axo.user_id, for_update=True
    )
    price = axo.sale_price_gal

    if buyer_wallet.frijolitos < price:
        raise HTTPException(
            status_code=400,
            detail=f"Saldo GAL insuficiente (requieres {price} GAL).",
        )

    buyer_user = session.exec(
        select(User).where(User.privy_did == verified_user_id)
    ).first()
    commission_rate = 0.05
    if buyer_user and buyer_user.is_vip and buyer_user.vip_tier:
        commission_rate = VIP_CONFIG.get(buyer_user.vip_tier, {}).get(
            "p2p_commission", 0.05
        )
    commission = round(price * commission_rate, 2)
    seller_share = price - commission

    buyer_wallet.frijolitos -= price
    seller_wallet.frijolitos += seller_share

    vault = session.exec(select(TreasuryVault)).first()
    if not vault:
        vault = TreasuryVault(balance=0.0)
        session.add(vault)
    vault.balance += commission

    ledger_buyer = TransactionLedger(
        user_id=verified_user_id,
        amount=price,
        currency=CurrencyType.GEMA_ALGA,
        tx_type=TransactionType.MARKET_BUY,
        description=f"Compra de Axolotito #{axo.id}",
    )
    ledger_seller = TransactionLedger(
        user_id=axo.user_id,
        amount=seller_share,
        currency=CurrencyType.GEMA_ALGA,
        tx_type=TransactionType.REWARD,
        description=f"Venta de Axolotito #{axo.id} (comisión {commission_rate*100:.1f}%)",
    )
    ledger_commission = TransactionLedger(
        user_id="treasury",
        amount=commission,
        currency=CurrencyType.GEMA_ALGA,
        tx_type=TransactionType.BURN,
        description=f"Comisión P2P {commission_rate*100:.1f}% Axolotito #{axo.id}",
    )

    # Transferencia on-chain del NFT
    tx_hash = ""
    if axo.blockchain_token_id:
        seller_user = session.exec(
            select(User).where(User.privy_did == axo.user_id)
        ).first()
        if (
            buyer_user
            and buyer_user.wallet_address
            and seller_user
            and seller_user.wallet_address
        ):
            try:
                tx_hash = Web3Service.transfer_axolotito_onchain(
                    seller_user.wallet_address,
                    buyer_user.wallet_address,
                    axo.blockchain_token_id,
                )
            except Exception as e:
                print(f"⚠️ Error al transferir Axolotito on-chain: {e}")

    old_owner_id = axo.user_id
    axo.user_id = verified_user_id
    axo.is_listed_for_sale = False
    axo.sale_price_gal = 0.0

    session.add(buyer_wallet)
    session.add(seller_wallet)
    session.add(vault)
    session.add(ledger_buyer)
    session.add(ledger_seller)
    session.add(ledger_commission)
    session.add(axo)
    session.commit()

    return {
        "mensaje": f"¡Compraste a '{axo.name}' con éxito!",
        "new_owner": axo.user_id,
        "old_owner": old_owner_id,
        "tx_blockchain": tx_hash,
    }


# ---------------------------------------------------------------------------
# Equip / Unequip accessories
# ---------------------------------------------------------------------------

def equip_accessory(
    session: Session,
    axolotito_id: int,
    item_id: int,
    slot: str,
    verified_user_id: str,
) -> dict:
    """Equip an accessory to an axolotito."""
    axo = _lookup_or_404(
        Axolotito, axolotito_id, session, detail="Axolotito no encontrado."
    )
    if axo.user_id != verified_user_id:
        raise HTTPException(
            status_code=403, detail="No eres dueño de este Axolotito."
        )
    if slot not in ["head", "eyes", "body"]:
        raise HTTPException(
            status_code=400,
            detail="Slot inválido. Usa 'head', 'eyes' o 'body'.",
        )

    item = session.get(ItemCatalog, item_id)
    if not item or item.item_type != ItemType.ACCESSORY:
        raise HTTPException(
            status_code=400,
            detail="El ítem seleccionado no es un accesorio válido.",
        )

    inv_item = session.exec(
        select(PlayerInventory)
        .where(PlayerInventory.user_id == verified_user_id)
        .where(PlayerInventory.item_id == item_id)
        .with_for_update()
    ).first()

    if not inv_item or inv_item.quantity < 1:
        raise HTTPException(
            status_code=400,
            detail="No posees este accesorio en tu inventario.",
        )

    # Desequipar slot existente
    old_item_id = getattr(axo, f"equipped_{slot}_item_id")
    if old_item_id:
        old_inv = session.exec(
            select(PlayerInventory)
            .where(PlayerInventory.user_id == verified_user_id)
            .where(PlayerInventory.item_id == old_item_id)
        ).first()
        if old_inv:
            old_inv.quantity += 1
        else:
            old_inv = PlayerInventory(
                user_id=verified_user_id, item_id=old_item_id, quantity=1
            )
        session.add(old_inv)

    inv_item.quantity -= 1
    if inv_item.quantity <= 0:
        session.delete(inv_item)
    else:
        session.add(inv_item)

    setattr(axo, f"equipped_{slot}_item_id", item_id)
    session.add(axo)
    session.commit()

    return {
        "mensaje": f"Equipaste '{item.name}' en la ranura de {slot}.",
        "equipped_id": item_id,
    }


def unequip_accessory(
    session: Session,
    axolotito_id: int,
    slot: str,
    verified_user_id: str,
) -> dict:
    """Unequip an accessory from an axolotito."""
    axo = _lookup_or_404(
        Axolotito, axolotito_id, session, detail="Axolotito no encontrado."
    )
    if axo.user_id != verified_user_id:
        raise HTTPException(
            status_code=403, detail="No eres dueño de este Axolotito."
        )
    if slot not in ["head", "eyes", "body"]:
        raise HTTPException(
            status_code=400,
            detail="Slot inválido. Usa 'head', 'eyes' o 'body'.",
        )

    item_id = getattr(axo, f"equipped_{slot}_item_id")
    if not item_id:
        return {"mensaje": f"No hay nada equipado en {slot}."}

    inv_item = session.exec(
        select(PlayerInventory)
        .where(PlayerInventory.user_id == verified_user_id)
        .where(PlayerInventory.item_id == item_id)
    ).first()

    if inv_item:
        inv_item.quantity += 1
    else:
        inv_item = PlayerInventory(
            user_id=verified_user_id, item_id=item_id, quantity=1
        )

    session.add(inv_item)
    setattr(axo, f"equipped_{slot}_item_id", None)
    session.add(axo)
    session.commit()

    return {"mensaje": f"Ranura de {slot} desequipada con éxito."}


# ---------------------------------------------------------------------------
# Set main axolotito
# ---------------------------------------------------------------------------

def set_main_axolotito(
    session: Session, axolotito_id: int, verified_user_id: str
) -> dict:
    """Designate an axolotito as the user's main."""
    axolotito = _lookup_or_404(
        Axolotito, axolotito_id, session, detail="Axolotito no encontrado."
    )
    if axolotito.user_id != verified_user_id:
        raise HTTPException(
            status_code=403, detail="No tienes permiso sobre este Axolotito."
        )

    other_axos = session.exec(
        select(Axolotito)
        .where(Axolotito.user_id == verified_user_id)
        .where(Axolotito.id != axolotito_id)
    ).all()
    for axo in other_axos:
        axo.is_main = False
        session.add(axo)

    axolotito.is_main = True
    session.add(axolotito)
    session.commit()
    session.refresh(axolotito)

    return {
        "mensaje": f"Axolotito '{axolotito.name}' designado como principal con éxito.",
        "is_main": True,
    }
