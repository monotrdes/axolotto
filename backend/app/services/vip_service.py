"""
VIP Service — lectura de tiers, estadisticas globales y preview de upgrade.

Funciones moved from shop.py endpoints so that endpoint handlers stay thin.
"""
from datetime import datetime
from sqlmodel import Session, select, func
from fastapi import HTTPException
from app.core.config import VIP_CONFIG
from app.models.user import User
from app.services.shop_service import ShopService


def get_vip_tiers() -> list[dict]:
    """
    Devuelve los tiers VIP ordenados coral -> dorado -> axolite.
    Público — no requiere autenticación.
    """
    return ShopService.get_vip_tiers()


def get_vip_stats(session: Session) -> dict:
    """
    Devuelve el numero de usuarios con membresia VIP activa (vip_expires_at > now()).
    Público — no requiere autenticación.
    """
    now = datetime.utcnow()
    active_count = session.exec(
        select(func.count(User.id)).where(User.vip_expires_at > now)
    ).one()
    return {"active_vip_count": active_count}


def get_vip_upgrade_preview(session: Session, user: User, target_tier: str) -> dict:
    """Calcula el precio de upgrade VIP con credito proporcional, sin cobrar nada."""
    return ShopService.get_vip_upgrade_preview(session, user, target_tier)
