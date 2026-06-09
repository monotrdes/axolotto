"""
checkout_service.py — Compras de AXF con cripto.

Flujo:
  1. create_order()    → genera orden AWAITING_PAYMENT con dirección treasury
  2. confirm_payment() → verifica tx on-chain y mintea AXF vía bank_service
  3. expire_stale_orders() → limpia órdenes vencidas (cron o on-demand)
"""
from datetime import datetime, timedelta
from typing import Optional
import hashlib
import uuid
import logging
import re

from fastapi import HTTPException
from sqlmodel import Session, select

logger = logging.getLogger("checkout")

from app.models.economy import CryptoPurchaseOrder, OrderStatus, CurrencyType, ProcessedTransaction, CryptoPaymentAttempt
from app.models.user import User
from app.services.bank_service import BankService
from app.services.web3_service import Web3Service
from app.core.config import settings

# ── Catálogo de packs ─────────────────────────────────────────────────────────

AXF_PACKS: dict[str, dict] = {
    "huevito":   {"usd": 2.0,  "axf_base": 200,   "bonus_pct": 0.00, "emoji": "🐣", "label": "Huevito"},
    "axolotito": {"usd": 5.0,  "axf_base": 500,   "bonus_pct": 0.10, "emoji": "🦎", "label": "Axolotito"},
    "cenote":    {"usd": 15.0, "axf_base": 1_500, "bonus_pct": 0.15, "emoji": "🌿", "label": "Cenote"},
    "jackpot":   {"usd": 50.0, "axf_base": 5_000, "bonus_pct": 0.20, "emoji": "🏆", "label": "Jackpot"},
}

FIRST_PURCHASE_BONUS = 0.10   # +10% AXF en la primera compra
FLASH_SALE_BONUS     = 0.25   # +25% AXF en el pack del día
ORDER_TTL_MINUTES    = 30
MAX_ACTIVE_ORDERS    = 3      # máximo de órdenes simultáneas por usuario


def get_flash_sale_pack() -> str:
    """Pack con oferta flash del día (determinístico por fecha, cambia a medianoche)."""
    day_str = datetime.utcnow().strftime("%Y-%m-%d")
    idx = int(hashlib.md5(day_str.encode()).hexdigest(), 16) % len(AXF_PACKS)
    return list(AXF_PACKS.keys())[idx]


class CheckoutService:

    @staticmethod
    def get_packs_info(usd_mxn: float = 17.5) -> list[dict]:
        """Lista de packs con precios, bonuses y oferta flash."""
        flash_pack = get_flash_sale_pack()
        packs = []
        for pack_id, cfg in AXF_PACKS.items():
            bonus_pct = cfg["bonus_pct"]
            bonuses = []
            is_flash = pack_id == flash_pack
            if is_flash:
                bonus_pct += FLASH_SALE_BONUS
                bonuses.append("flash_sale")
            axf_total = round(cfg["axf_base"] * (1 + bonus_pct))
            badge = None
            if pack_id == "axolotito":
                badge = "POPULAR"
            elif pack_id == "cenote":
                badge = "VALOR"
            elif pack_id == "jackpot":
                badge = "MEJOR DEAL"
            packs.append({
                "id":        pack_id,
                "label":     cfg["label"],
                "emoji":     cfg["emoji"],
                "usd":       cfg["usd"],
                "mxn":       round(cfg["usd"] * usd_mxn, 2),
                "axf_base":  cfg["axf_base"],
                "axf_total": axf_total,
                "bonus_pct": round(bonus_pct * 100),
                "badge":     badge,
                "is_flash":  is_flash,
                "bonuses":   bonuses,
            })
        return packs

    @staticmethod
    def create_order(
        session: Session,
        user_id: str,
        pack_id: str,
    ) -> CryptoPurchaseOrder:
        """Crea una orden de compra. Devuelve la orden con la dirección de pago."""
        if pack_id not in AXF_PACKS:
            raise HTTPException(status_code=400, detail=f"Pack '{pack_id}' no existe.")

        user = session.exec(select(User).where(User.privy_did == user_id)).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado.")
        if not user.wallet_address:
            raise HTTPException(
                status_code=400,
                detail="Tu cuenta no tiene una wallet Web3 vinculada. Inicia sesión con Privy."
            )

        # Rate limit: máximo MAX_ACTIVE_ORDERS órdenes activas simultáneas
        active = session.exec(
            select(CryptoPurchaseOrder).where(
                CryptoPurchaseOrder.user_id == user_id,
                CryptoPurchaseOrder.status == OrderStatus.AWAITING_PAYMENT,
                CryptoPurchaseOrder.expires_at > datetime.utcnow(),
            )
        ).all()
        if len(active) >= MAX_ACTIVE_ORDERS:
            raise HTTPException(
                status_code=429,
                detail=f"Tienes {len(active)} órdenes activas. Espera a que expiren o cancélalas."
            )

        cfg = AXF_PACKS[pack_id]
        flash_pack = get_flash_sale_pack()

        # Calcular bonus
        bonus_pct = cfg["bonus_pct"]
        bonus_applied_list = []
        is_first = user.first_crypto_purchase_at is None
        if is_first:
            bonus_pct += FIRST_PURCHASE_BONUS
            bonus_applied_list.append("first_purchase")
        if pack_id == flash_pack:
            bonus_pct += FLASH_SALE_BONUS
            bonus_applied_list.append("flash_sale")

        axf_amount = round(cfg["axf_base"] * (1 + bonus_pct), 2)
        usdc_amount = round(cfg["usd"] * 1.01, 4)  # 1% buffer para slippage

        try:
            treasury_address = Web3Service.get_treasury_address()
        except Exception:
            treasury_address = "0x0000000000000000000000000000000000000000"

        order = CryptoPurchaseOrder(
            user_id=user_id,
            pack_id=pack_id,
            usd_amount=cfg["usd"],
            usdc_amount=usdc_amount,
            axf_amount=axf_amount,
            treasury_address=treasury_address,
            bonus_applied=",".join(bonus_applied_list) if bonus_applied_list else None,
            bonus_pct=round(bonus_pct * 100, 1),
            expires_at=datetime.utcnow() + timedelta(minutes=ORDER_TTL_MINUTES),
        )
        session.add(order)
        session.commit()
        session.refresh(order)
        return order

    @staticmethod
    def confirm_payment(
        session: Session,
        order_id: str,
        user_id: str,
        tx_hash: str,
    ) -> CryptoPurchaseOrder:
        """
        El frontend informa el tx_hash tras enviar USDC.
        """
        # Validar formato tx_hash (solo si no estamos en modo local de blockchain)
        if settings.BLOCKCHAIN_MODE != "local":
            if not tx_hash or not re.fullmatch(r"0x[0-9a-fA-F]{64}", tx_hash):
                raise HTTPException(
                    status_code=400,
                    detail="Formato de hash de transacción inválido."
                )

        order = session.exec(
            select(CryptoPurchaseOrder).where(CryptoPurchaseOrder.id == order_id)
        ).first()
        if not order:
            raise HTTPException(status_code=404, detail="Orden no encontrada.")
        if order.user_id != user_id:
            raise HTTPException(status_code=403, detail="Esta orden no es tuya.")
        if order.status == OrderStatus.COMPLETED:
            raise HTTPException(status_code=409, detail="Esta orden ya fue completada.")
        if order.status == OrderStatus.FAILED:
            raise HTTPException(status_code=409, detail="Esta orden falló. Crea una nueva.")
        if order.status == OrderStatus.EXPIRED or order.expires_at < datetime.utcnow():
            order.status = OrderStatus.EXPIRED
            session.add(order)
            session.commit()
            raise HTTPException(status_code=410, detail="La orden expiró. Crea una nueva.")

        # Capa 1: lookup rápido en ProcessedTransactions (evita verificación on-chain costosa en replays obvios)
        if session.exec(
            select(ProcessedTransaction).where(ProcessedTransaction.tx_hash == tx_hash)
        ).first():
            raise HTTPException(
                status_code=409,
                detail="Este hash de transacción ya fue procesado previamente."
            )

        # Capa 2: check en CryptoPurchaseOrder (cubre el caso donde la orden ya fue confirmada
        # pero ProcessedTransaction aún no se escribió, e.g. crash entre commits)
        if session.exec(
            select(CryptoPurchaseOrder).where(CryptoPurchaseOrder.tx_hash_payment == tx_hash)
        ).first():
            raise HTTPException(
                status_code=409,
                detail="Este hash de transacción ya fue utilizado en otra orden."
            )

        # Registrar tx_hash en ProcessedTransactions atómicamente con el estado CONFIRMING.
        # El UNIQUE constraint de BD rechaza requests concurrentes que pasen ambos checks anteriores.
        processed_entry = ProcessedTransaction(
            tx_hash=tx_hash,
            user_id=user_id,
            purpose="checkout_usdc",
        )
        order.status = OrderStatus.CONFIRMING
        order.tx_hash_payment = tx_hash
        session.add(processed_entry)
        session.add(order)
        try:
            session.commit()
        except Exception:
            session.rollback()
            raise HTTPException(
                status_code=409,
                detail="Hash de transacción ya procesado (conflicto concurrente detectado)."
            )

        # Verificar pago on-chain (incluyendo remitente para prevenir tx-hash theft)
        user = session.exec(select(User).where(User.privy_did == user_id)).first()
        is_valid = Web3Service.verify_usdc_payment(
            tx_hash=tx_hash,
            expected_recipient=order.treasury_address,
            min_usdc=order.usdc_amount,
            expected_sender=user.wallet_address if user else None,
        )
        if not is_valid:
            # Eliminar la entrada ProcessedTransaction y resetear la orden a AWAITING_PAYMENT para permitir reintentar
            session.delete(processed_entry)
            order.status = OrderStatus.AWAITING_PAYMENT
            order.tx_hash_payment = None
            session.add(order)

            # Loggear el intento fallido
            attempt = CryptoPaymentAttempt(
                order_id=order.id,
                tx_hash=tx_hash,
                user_id=user_id,
                status="failed",
                error_detail="El pago no pudo verificarse on-chain.",
            )
            session.add(attempt)
            session.commit()
            logger.warning(
                f"Verificación de pago USDC falló para tx_hash {tx_hash} en la orden {order.id} del usuario {user_id}. "
                "La entrada ProcessedTransaction ha sido removida y la orden regresó a AWAITING_PAYMENT."
            )
            raise HTTPException(
                status_code=422,
                detail="El pago no pudo verificarse on-chain. Revisa el monto y la dirección. Puedes volver a intentarlo."
            )

        # Mintear AXG
        try:
            result = BankService.admin_deposit(
                session=session,
                user_id=user_id,
                amount=order.axf_amount,
                currency=CurrencyType.AXOGEMA,
                description=f"Compra pack {order.pack_id} | USDC tx: {tx_hash}",
            )
            order.tx_hash_mint = result.get("tx_hash")
        except HTTPException as e:
            # Loggear el intento fallido por error en minteo
            attempt = CryptoPaymentAttempt(
                order_id=order.id,
                tx_hash=tx_hash,
                user_id=user_id,
                status="failed",
                error_detail=f"Error al mintear AXG: {e.detail}",
            )
            session.add(attempt)
            order.status = OrderStatus.FAILED
            session.add(order)
            session.commit()
            raise HTTPException(status_code=500, detail=f"Error al mintear AXG: {e.detail}")

        # Marcar primera compra
        user = session.exec(select(User).where(User.privy_did == user_id)).first()
        if user and user.first_crypto_purchase_at is None:
            user.first_crypto_purchase_at = datetime.utcnow()
            session.add(user)

        order.status = OrderStatus.COMPLETED
        order.completed_at = datetime.utcnow()
        session.add(order)

        # Loggear el intento exitoso
        attempt = CryptoPaymentAttempt(
            order_id=order.id,
            tx_hash=tx_hash,
            user_id=user_id,
            status="success",
        )
        session.add(attempt)
        session.commit()
        session.refresh(order)
        return order

    @staticmethod
    def get_order(session: Session, order_id: str, user_id: str) -> CryptoPurchaseOrder:
        order = session.exec(
            select(CryptoPurchaseOrder).where(CryptoPurchaseOrder.id == order_id)
        ).first()
        if not order:
            raise HTTPException(status_code=404, detail="Orden no encontrada.")
        if order.user_id != user_id:
            raise HTTPException(status_code=403, detail="Esta orden no es tuya.")
        # Expirar on-the-fly si aplica
        if order.status == OrderStatus.AWAITING_PAYMENT and order.expires_at < datetime.utcnow():
            order.status = OrderStatus.EXPIRED
            session.add(order)
            session.commit()
        return order

    @staticmethod
    def expire_stale_orders(session: Session) -> int:
        """Marca EXPIRED las órdenes vencidas. Llamar periódicamente."""
        stale = session.exec(
            select(CryptoPurchaseOrder).where(
                CryptoPurchaseOrder.status == OrderStatus.AWAITING_PAYMENT,
                CryptoPurchaseOrder.expires_at < datetime.utcnow(),
            )
        ).all()
        for order in stale:
            order.status = OrderStatus.EXPIRED
            session.add(order)
        session.commit()
        return len(stale)
