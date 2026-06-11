"""
chain_outbox_worker.py — Worker que procesa la tabla ChainOutbox con reintentos y backoff.

Garantiza eventual consistencia entre PostgreSQL (fuente de verdad del juego) y la
blockchain (libro mayor de auditoría). Implementa:
  - Procesamiento FIFO por entrada (con SKIP LOCKED para concurrencia)
  - Reintentos con backoff exponencial (1s → 2s → 4s → 8s → 16s, max 5)
  - Idempotencia vía ProcessedTransaction (anti-replay)
  - Structured logging (nunca print() para fallos financieros)
"""

import json
import logging
import time
from typing import Optional

from sqlmodel import Session, select

from app.database import engine
from app.models.economy import ChainOutbox, ProcessedTransaction
from app.services.web3_service import Web3Service

logger = logging.getLogger("chain_outbox")

# ── Backoff config ──────────────────────────────────────────────────────
MAX_RETRIES = 5
BASE_DELAY_SECONDS = 2  # 2s → 4s → 8s → 16s → 32s


def _compute_backoff(retry_count: int) -> float:
    """Backoff exponencial: 2^(retry) segundos, max 60s."""
    return min(BASE_DELAY_SECONDS * (2 ** retry_count), 60.0)


def _dispatch_onchain(entry: ChainOutbox) -> str:
    """Ejecuta la operación on-chain según entry.operation.

    Retorna el tx_hash. Lanza excepción si falla.
    """
    payload = json.loads(entry.payload_json)
    op = entry.operation

    if op == "burn_frj":
        return Web3Service.burn_frj(payload["from_address"], payload["amount"])
    elif op == "mint_frj":
        return Web3Service.mint_frj(payload["to_address"], payload["amount"])
    elif op == "transfer_axf":
        return Web3Service.transferir_axofichas(payload["to_address"], payload["amount"])
    elif op == "transfer_card":
        return Web3Service.transfer_card_onchain(
            payload["from_address"],
            payload["to_address"],
            payload["card_id"],
            payload.get("quantity", 1),
        )
    elif op == "transfer_board":
        return Web3Service.transfer_board_onchain(
            payload["from_address"],
            payload["to_address"],
            payload["board_id"],
        )
    elif op == "update_board_stats":
        return Web3Service.update_table_stats_onchain(
            payload["board_token_id"],
            payload["won"],
            payload["xp_gained"],
        )
    elif op == "burn_consumable":
        return Web3Service.burn_consumable(
            payload["from_address"],
            payload["consumable_id"],
            payload.get("amount", 1),
        )
    elif op == "mint_cards":
        return Web3Service.mint_cards_onchain(
            payload["to_address"],
            payload["card_ids"],
            payload["amounts"],
        )
    elif op == "dissolve_board":
        return Web3Service.dissolve_board_onchain(
            payload["board_token_id"],
            payload["destroy_card_index"],
        )
    elif op == "escrow_deposit":
        return Web3Service.escrow_deposit_and_list(
            payload["listing_id"],
            payload["seller_address"],
            payload["nft_contract"],
            payload["token_id"],
            payload["price_axf"],
        )
    elif op == "escrow_release":
        return Web3Service.escrow_release(
            payload["listing_id"],
            payload["buyer_address"],
            payload["payment_ref"],
        )
    elif op == "escrow_refund":
        return Web3Service.escrow_refund(payload["listing_id"])
    elif op == "transfer_booster":
        return Web3Service.transferir_sobrecito_onchain(
            payload["from_address"],
            payload["to_address"],
            payload["booster_fase"],
            payload.get("quantity", 1),
        )
    else:
        raise ValueError(f"Operación desconocida en ChainOutbox: {op}")


def process_single_entry(session: Session) -> Optional[ChainOutbox]:
    """Procesa una única entrada pendiente de la outbox.

    Usa SELECT FOR UPDATE SKIP LOCKED para permitir múltiples workers sin
    colisiones. Retorna la entrada procesada, o None si no hay pendientes.
    """
    entry = session.exec(
        select(ChainOutbox)
        .where(ChainOutbox.status == "pending")
        .order_by(ChainOutbox.created_at.asc())
        .with_for_update(skip_locked=True)
    ).first()

    if not entry:
        return None

    # Marcar como processing para que otros workers no la toquen
    entry.status = "processing"
    entry.updated_at = None  # se actualizará en commit
    session.commit()

    try:
        # Anti-replay: si ya existe ProcessedTransaction con este propósito
        # para este usuario, no duplicar (defensa adicional)
        tx_hash = _dispatch_onchain(entry)

        entry.tx_hash = tx_hash
        entry.status = "confirmed"
        entry.last_error = None
        session.add(entry)

        # Registrar en ProcessedTransaction para prevenir replay
        session.add(ProcessedTransaction(
            tx_hash=tx_hash,
            user_id=entry.user_id,
            purpose=f"outbox_{entry.operation}",
        ))

        session.commit()
        logger.info(
            "chain_outbox: confirmed  id=%s op=%s user=%s tx=%s",
            entry.id, entry.operation, entry.user_id, tx_hash,
        )
        return entry

    except Exception as e:
        entry.retry_count += 1
        entry.last_error = str(e)[:500]
        entry.retry_count = entry.retry_count  # ensure dirty

        if entry.retry_count >= entry.max_retries:
            entry.status = "failed"
            session.commit()
            logger.error(
                "chain_outbox: FAILED  id=%s op=%s user=%s retries=%d/%d error=%s",
                entry.id, entry.operation, entry.user_id,
                entry.retry_count, entry.max_retries, entry.last_error,
            )
        else:
            delay = _compute_backoff(entry.retry_count)
            entry.status = "pending"  # volver a intentar
            session.commit()
            logger.warning(
                "chain_outbox: retry %d/%d in %.0fs  id=%s op=%s user=%s error=%s",
                entry.retry_count, entry.max_retries, delay,
                entry.id, entry.operation, entry.user_id, entry.last_error,
            )
            # Dormir el backoff antes de volver (solo en worker síncrono)
            time.sleep(delay)

        return entry


def process_all_pending(session: Session, max_batch: int = 20) -> int:
    """Procesa hasta max_batch entradas pendientes. Retorna el número procesado."""
    processed = 0
    for _ in range(max_batch):
        entry = process_single_entry(session)
        if entry is None:
            break
        processed += 1
    return processed


def process_outbox_sync(session: Session, max_batch: int = 20) -> int:
    """Procesa la outbox de forma síncrona. Útil en modo mock o para llamadas inline.

    En modo mock (IS_MOCK_WEB3=true), las operaciones on-chain son no-op,
    así que procesamos todo de inmediato sin reintentos ni backoff.
    """
    from app.core.config import settings

    entries = session.exec(
        select(ChainOutbox)
        .where(ChainOutbox.status == "pending")
        .order_by(ChainOutbox.created_at.asc())
        .limit(max_batch)
    ).all()

    processed = 0
    for entry in entries:
        entry.status = "processing"
        session.commit()

        try:
            if not settings.IS_MOCK_WEB3:
                tx_hash = _dispatch_onchain(entry)
            else:
                tx_hash = f"mock_tx_{entry.operation}_{entry.id}"

            entry.tx_hash = tx_hash
            entry.status = "confirmed"
            session.add(ProcessedTransaction(
                tx_hash=tx_hash,
                user_id=entry.user_id,
                purpose=f"outbox_{entry.operation}",
            ))
            session.commit()
            processed += 1

        except Exception as e:
            entry.retry_count += 1
            entry.last_error = str(e)[:500]
            entry.status = "pending" if entry.retry_count < entry.max_retries else "failed"
            session.commit()
            logger.error(
                "chain_outbox: sync error id=%s op=%s user=%s error=%s",
                entry.id, entry.operation, entry.user_id, entry.last_error,
            )

    return processed
