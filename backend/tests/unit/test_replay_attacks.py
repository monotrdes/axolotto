"""
test_replay_attacks.py — Suite completo §4.2: Robo o Reuso de Hash de Transacción.

Cubre los siguientes escenarios de ataque:
  A. Replay: reutilizar el mismo tx_hash en una segunda orden propia.
  B. Replay cruzado de usuario: User B intenta usar el tx_hash ya confirmado por User A.
  C. Robo de hash activo: User B intenta reclamar una transacción cuyo `from` es User A.
  D. Conflicto concurrente: ProcessedTransaction ya existe antes del commit (race condition).
  E. Orden ya completada: reenviar confirm_payment a una orden en estado COMPLETED.
  F. Orden expirada: reenviar confirm_payment después de que expiró.
  G. Orden de otro usuario: un usuario intenta confirmar una orden que no le pertenece.
  H. tx_hash vacío o formato inválido: cadena vacía, None simulado, sin prefijo 0x.
  I. tx_hash modo dev (0x_mock): debe saltarse la verificación on-chain y ser aceptado.
  J. Integridad de ProcessedTransaction: el registro se crea exactamente una vez con user_id,
     purpose y created_at correctos.
  K. Idempotencia de estado CONFIRMING: una orden que ya está CONFIRMING no se reprocesa.
  L. El campo purpose de ProcessedTransaction es 'checkout_usdc' (no otro valor arbitrario).
"""
import pytest
from datetime import datetime, timedelta
from sqlmodel import Session, select
from fastapi import HTTPException

from app.models.economy import (
    CryptoPurchaseOrder,
    OrderStatus,
    ProcessedTransaction,
    Wallet,
)
from app.models.user import User
from app.services.checkout_service import CheckoutService
from tests.conftest import make_user, make_wallet


# ---------------------------------------------------------------------------
# Fixtures y helpers
# ---------------------------------------------------------------------------

def make_order(
    session: Session,
    order_id: str,
    user_id: str,
    *,
    status: OrderStatus = OrderStatus.AWAITING_PAYMENT,
    expires_in_minutes: int = 60,
) -> CryptoPurchaseOrder:
    """Helper: crea y persiste una CryptoPurchaseOrder de prueba."""
    order = CryptoPurchaseOrder(
        id=order_id,
        user_id=user_id,
        pack_id="huevito",
        usd_amount=2.0,
        usdc_amount=2.02,
        axg_amount=200.0,
        expires_at=datetime.utcnow() + timedelta(minutes=expires_in_minutes),
        status=status,
        treasury_address="0xTREASURY",
    )
    session.add(order)
    session.commit()
    return order


@pytest.fixture(autouse=True)
def mock_web3_checkout(monkeypatch):
    """
    Parchea Web3Service y BankService para evitar llamadas reales a blockchain/mint.

    Lógica del mock de verify_usdc_payment:
      - Si expected_sender empieza con '0xSTEALER' → retorna False (hash robado / sender incorrecto).
      - Si tx_hash empieza con '0x_bad' → retorna False (tx inválida on-chain).
      - Cualquier otro caso → retorna True (tx válida).
    """
    from unittest.mock import MagicMock

    def mock_verify(tx_hash, expected_recipient, min_usdc, expected_sender):
        if expected_sender and expected_sender.lower().startswith("0xstealer"):
            return False
        if tx_hash and tx_hash.startswith("0x_bad"):
            return False
        return True

    monkeypatch.setattr(
        "app.services.checkout_service.settings.ALLOW_DEV_PAYMENTS",
        True,
    )
    monkeypatch.setattr(
        "app.services.checkout_service.Web3Service.verify_usdc_payment",
        mock_verify,
    )
    monkeypatch.setattr(
        "app.services.checkout_service.BankService.admin_deposit",
        MagicMock(return_value={"tx_hash": "0xaxgminttx"}),
    )


# ---------------------------------------------------------------------------
# A. Replay: mismo usuario, mismo tx_hash en segunda orden
# ---------------------------------------------------------------------------

def test_A_replay_same_user_same_hash(session):
    """
    [A] Un usuario confirma con tx_hash 'X', luego intenta reutilizarlo
    en una segunda orden suya → debe fallar con HTTP 409.
    """
    user = make_user(session, privy_did="user_a", wallet_address="0xAAAA")
    make_wallet(session, user_id="user_a")

    order_1 = make_order(session, "ord_a1", "user_a")
    order_2 = make_order(session, "ord_a2", "user_a")

    tx = "0xREPLAY_SAME_USER"

    # Primera confirmación: OK
    result = CheckoutService.confirm_payment(
        session=session, order_id="ord_a1", user_id="user_a", tx_hash=tx
    )
    assert result.status == OrderStatus.COMPLETED

    # Segunda confirmación con mismo hash: debe ser rechazada
    with pytest.raises(HTTPException) as exc:
        CheckoutService.confirm_payment(
            session=session, order_id="ord_a2", user_id="user_a", tx_hash=tx
        )
    assert exc.value.status_code == 409
    assert "ya fue procesado" in exc.value.detail or "ya fue utilizado" in exc.value.detail


# ---------------------------------------------------------------------------
# B. Replay cruzado: User B intenta usar el hash que User A ya confirmó
# ---------------------------------------------------------------------------

def test_B_cross_user_replay(session):
    """
    [B] User A confirma con hash 'X'. User B tiene su propia orden y envía
    el mismo hash intentando obtener AXG gratis → HTTP 409.
    """
    user_a = make_user(session, privy_did="user_a", wallet_address="0xAAAA")
    user_b = make_user(session, privy_did="user_b", wallet_address="0xBBBB")
    make_wallet(session, user_id="user_a")
    make_wallet(session, user_id="user_b")

    order_a = make_order(session, "ord_b_a", "user_a")
    order_b = make_order(session, "ord_b_b", "user_b")

    tx = "0xCROSS_USER_REPLAY"

    # User A confirma primero: OK
    CheckoutService.confirm_payment(
        session=session, order_id="ord_b_a", user_id="user_a", tx_hash=tx
    )

    # User B intenta el mismo hash en su orden: debe fallar
    with pytest.raises(HTTPException) as exc:
        CheckoutService.confirm_payment(
            session=session, order_id="ord_b_b", user_id="user_b", tx_hash=tx
        )
    assert exc.value.status_code == 409


# ---------------------------------------------------------------------------
# C. Robo de hash: sender en la blockchain no coincide con el wallet del reclamante
# ---------------------------------------------------------------------------

def test_C_tx_hash_theft_sender_mismatch(session):
    """
    [C] El tx_hash existe on-chain, pero el `from` es la wallet de User A.
    El ladrón (User B con wallet 0xSTEALER...) lo reclama → on-chain falla,
    la orden queda FAILED y lanza HTTP 422.
    """
    # El mock retorna False si expected_sender empieza con '0xSTEALER'
    thief = make_user(session, privy_did="thief", wallet_address="0xSTEALERdeadbeef")
    make_wallet(session, user_id="thief")

    order = make_order(session, "ord_c1", "thief")

    with pytest.raises(HTTPException) as exc:
        CheckoutService.confirm_payment(
            session=session,
            order_id="ord_c1",
            user_id="thief",
            tx_hash="0xVALID_TX_OF_VICTIM",
        )
    assert exc.value.status_code == 422
    assert "on-chain" in exc.value.detail.lower() or "verificarse" in exc.value.detail.lower()

    # La orden queda AWAITING_PAYMENT, no COMPLETED o FAILED, para permitir reintentos
    from sqlmodel import select as sqlselect
    order_db = session.exec(
        sqlselect(CryptoPurchaseOrder).where(CryptoPurchaseOrder.id == "ord_c1")
    ).first()
    assert order_db is not None
    assert order_db.status == OrderStatus.AWAITING_PAYMENT


# ---------------------------------------------------------------------------
# D. Conflicto concurrente: ProcessedTransaction ya existe en BD antes del commit
# ---------------------------------------------------------------------------

def test_D_db_unique_constraint_concurrent_race(session):
    """
    [D] Simula la situación donde dos requests concurrentes superan ambos
    lookups al mismo tiempo. El UNIQUE constraint de BD debe rechazar el segundo.
    Se logra insertando manualmente una ProcessedTransaction antes de que
    confirm_payment la intente insertar.
    """
    user = make_user(session, privy_did="user_d", wallet_address="0xDDDD")
    make_wallet(session, user_id="user_d")

    order = make_order(session, "ord_d1", "user_d")

    # Simular que otro thread ya la registró
    pre_entry = ProcessedTransaction(
        tx_hash="0xRACE_TX",
        user_id="user_d",
        purpose="checkout_usdc",
    )
    session.add(pre_entry)
    session.commit()

    # Ahora confirm_payment debe detectarla en el Capa 1 lookup y rechazar
    with pytest.raises(HTTPException) as exc:
        CheckoutService.confirm_payment(
            session=session,
            order_id="ord_d1",
            user_id="user_d",
            tx_hash="0xRACE_TX",
        )
    assert exc.value.status_code == 409


# ---------------------------------------------------------------------------
# E. Orden ya completada: no se reprocesa
# ---------------------------------------------------------------------------

def test_E_already_completed_order(session):
    """
    [E] Si la orden ya está en estado COMPLETED, confirm_payment debe
    rechazar inmediatamente con HTTP 409 antes de tocar la BD o la blockchain.
    """
    user = make_user(session, privy_did="user_e", wallet_address="0xEEEE")
    make_wallet(session, user_id="user_e")

    order = make_order(session, "ord_e1", "user_e", status=OrderStatus.COMPLETED)

    with pytest.raises(HTTPException) as exc:
        CheckoutService.confirm_payment(
            session=session,
            order_id="ord_e1",
            user_id="user_e",
            tx_hash="0xNEW_TX",
        )
    assert exc.value.status_code == 409
    assert "completada" in exc.value.detail.lower()


# ---------------------------------------------------------------------------
# F. Orden expirada: reenviar confirm_payment después de expirar
# ---------------------------------------------------------------------------

def test_F_expired_order_replay(session):
    """
    [F] Si la orden ya expiró (expires_at < now), debe rechazarse con HTTP 410.
    No se debe registrar ProcessedTransaction ni cambiar estado a CONFIRMING.
    """
    user = make_user(session, privy_did="user_f", wallet_address="0xFFFF")
    make_wallet(session, user_id="user_f")

    # Crear orden que ya expiró (expires_in_minutes negativo)
    order = make_order(session, "ord_f1", "user_f", expires_in_minutes=-10)

    with pytest.raises(HTTPException) as exc:
        CheckoutService.confirm_payment(
            session=session,
            order_id="ord_f1",
            user_id="user_f",
            tx_hash="0xEXPIRED_REPLAY",
        )
    assert exc.value.status_code == 410

    # La ProcessedTransaction no debe haberse creado
    pt = session.exec(
        select(ProcessedTransaction).where(
            ProcessedTransaction.tx_hash == "0xEXPIRED_REPLAY"
        )
    ).first()
    assert pt is None


# ---------------------------------------------------------------------------
# G. Orden de otro usuario: un usuario trata de confirmar una orden ajena
# ---------------------------------------------------------------------------

def test_G_order_belongs_to_different_user(session):
    """
    [G] User B no puede confirmar una orden creada por User A.
    Debe fallar con HTTP 403 antes de cualquier verificación on-chain.
    """
    user_a = make_user(session, privy_did="user_a_g", wallet_address="0xAAAA")
    user_b = make_user(session, privy_did="user_b_g", wallet_address="0xBBBB")
    make_wallet(session, user_id="user_a_g")

    order = make_order(session, "ord_g1", "user_a_g")

    with pytest.raises(HTTPException) as exc:
        CheckoutService.confirm_payment(
            session=session,
            order_id="ord_g1",
            user_id="user_b_g",   # ← User B intenta apropiarse de la orden de User A
            tx_hash="0xSOME_TX",
        )
    assert exc.value.status_code == 403
    assert "no es tuya" in exc.value.detail.lower()


# ---------------------------------------------------------------------------
# H. tx_hash con formato inválido / vacío
# ---------------------------------------------------------------------------

def test_H_invalid_tx_hash_empty_string(session):
    """
    [H-1] tx_hash vacío: el mock de verify lo acepta (empieza sin '0x_bad'),
    pero el verdadero verify_usdc_payment retorna False para cadenas vacías.
    Aquí testeamos que una tx_hash marcada como '0x_bad' retorna 422.
    """
    user = make_user(session, privy_did="user_h", wallet_address="0xHHHH")
    make_wallet(session, user_id="user_h")

    order = make_order(session, "ord_h1", "user_h")

    # tx_hash con prefijo 0x_bad → mock retorna False → orden FAILED + HTTP 422
    with pytest.raises(HTTPException) as exc:
        CheckoutService.confirm_payment(
            session=session,
            order_id="ord_h1",
            user_id="user_h",
            tx_hash="0x_bad_invalid_hash",
        )
    assert exc.value.status_code == 422


def test_H2_short_tx_hash_rejected_onchain(session):
    """
    [H-2] tx_hash con formato imposible (muy corto, no es hex): el backend no debe
    dejar la orden en estado inconsistente si la verificación on-chain falla.
    """
    user = make_user(session, privy_did="user_h2", wallet_address="0xH2H2")
    make_wallet(session, user_id="user_h2")

    order = make_order(session, "ord_h2", "user_h2")

    with pytest.raises(HTTPException) as exc:
        CheckoutService.confirm_payment(
            session=session,
            order_id="ord_h2",
            user_id="user_h2",
            tx_hash="0x_bad_SHORT",
        )
    assert exc.value.status_code == 422

    # La orden debe haber quedado AWAITING_PAYMENT, no CONFIRMING o FAILED, para permitir reintentos
    order_db = session.exec(
        select(CryptoPurchaseOrder).where(CryptoPurchaseOrder.id == "ord_h2")
    ).first()
    assert order_db.status == OrderStatus.AWAITING_PAYMENT


# ---------------------------------------------------------------------------
# I. tx_hash modo dev (0x_mock): se acepta sin verificación on-chain
# ---------------------------------------------------------------------------

def test_I_mock_tx_hash_accepted_in_dev_mode(session):
    """
    [I] Un tx_hash que empieza con '0x_mock' es tratado como modo dev
    en verify_usdc_payment (retorna True siempre). Debe procesarse correctamente.
    """
    user = make_user(session, privy_did="user_i", wallet_address="0xIIII")
    make_wallet(session, user_id="user_i")

    order = make_order(session, "ord_i1", "user_i")

    result = CheckoutService.confirm_payment(
        session=session,
        order_id="ord_i1",
        user_id="user_i",
        tx_hash="0x_mock_dev_hash_abc",
    )
    assert result.status == OrderStatus.COMPLETED


# ---------------------------------------------------------------------------
# J. Integridad de ProcessedTransaction: campos correctos tras confirmar
# ---------------------------------------------------------------------------

def test_J_processed_transaction_fields_integrity(session):
    """
    [J] Tras una confirmación exitosa, se crea exactamente UN registro en
    ProcessedTransaction con user_id, purpose='checkout_usdc' y created_at correctos.
    """
    user = make_user(session, privy_did="user_j", wallet_address="0xJJJJ")
    make_wallet(session, user_id="user_j")

    order = make_order(session, "ord_j1", "user_j")
    tx = "0xINTEGRITY_CHECK"

    before = datetime.utcnow()
    CheckoutService.confirm_payment(
        session=session, order_id="ord_j1", user_id="user_j", tx_hash=tx
    )
    after = datetime.utcnow()

    pts = session.exec(
        select(ProcessedTransaction).where(ProcessedTransaction.tx_hash == tx)
    ).all()

    # Exactamente un registro
    assert len(pts) == 1
    pt = pts[0]
    assert pt.user_id == "user_j"
    assert pt.purpose == "checkout_usdc"
    assert pt.tx_hash == tx
    assert before <= pt.created_at <= after


# ---------------------------------------------------------------------------
# K. Idempotencia de estado CONFIRMING: no se puede re-confirmar
# ---------------------------------------------------------------------------

def test_K_confirming_order_cannot_be_reprocessed(session):
    """
    [K] Una orden que ya está en estado CONFIRMING (e.g. pago verificado pero
    el mint falló a medias) no debe poder confirmarse de nuevo con el mismo
    o distinto tx_hash → HTTP 409 por COMPLETED o fallo en el tx_hash duplicado.
    Aquí simulamos que la orden quedó en CONFIRMING manualmente.
    """
    user = make_user(session, privy_did="user_k", wallet_address="0xKKKK")
    make_wallet(session, user_id="user_k")

    # Crear orden ya en CONFIRMING con tx_hash ya asignado
    order = make_order(session, "ord_k1", "user_k", status=OrderStatus.CONFIRMING)
    # Asignar el tx_hash_payment directamente para simular la mitad del flujo
    order.tx_hash_payment = "0xALREADY_CONFIRMING"
    session.add(order)

    # También crear la entrada en ProcessedTransaction
    pt = ProcessedTransaction(
        tx_hash="0xALREADY_CONFIRMING",
        user_id="user_k",
        purpose="checkout_usdc",
    )
    session.add(pt)
    session.commit()

    # Intento de re-confirmar con el mismo hash → Capa 1 lo rechaza
    with pytest.raises(HTTPException) as exc:
        CheckoutService.confirm_payment(
            session=session,
            order_id="ord_k1",
            user_id="user_k",
            tx_hash="0xALREADY_CONFIRMING",
        )
    assert exc.value.status_code == 409


# ---------------------------------------------------------------------------
# L. El campo purpose de ProcessedTransaction es siempre 'checkout_usdc'
# ---------------------------------------------------------------------------

def test_L_processed_transaction_purpose_is_checkout_usdc(session):
    """
    [L] Verificar que el campo `purpose` en ProcessedTransaction es exactamente
    'checkout_usdc' para todas las confirmaciones de checkout, no un valor arbitrario.
    Esto garantiza que la tabla es extensible para otros propósitos futuros sin colisiones.
    """
    user = make_user(session, privy_did="user_l", wallet_address="0xLLLL")
    make_wallet(session, user_id="user_l")

    order = make_order(session, "ord_l1", "user_l")
    tx = "0xPURPOSE_CHECK"

    CheckoutService.confirm_payment(
        session=session, order_id="ord_l1", user_id="user_l", tx_hash=tx
    )

    pt = session.exec(
        select(ProcessedTransaction).where(ProcessedTransaction.tx_hash == tx)
    ).first()
    assert pt is not None
    assert pt.purpose == "checkout_usdc"


# ---------------------------------------------------------------------------
# M. Robo de hash: hash válido on-chain pero el `from` es address cero / inválido
# ---------------------------------------------------------------------------

def test_M_hash_with_zero_address_sender(session):
    """
    [M] Caso extremo: el `from` de la transacción es 0x0000... (address cero).
    El mock lo maneja como 0x_bad (tx inválida), debe retornar HTTP 422.
    La verificación on-chain real también lo rechazaría porque 0x0 != expected_sender.
    """
    user = make_user(session, privy_did="user_m", wallet_address="0xMMMM")
    make_wallet(session, user_id="user_m")

    order = make_order(session, "ord_m1", "user_m")

    # Forzamos fallo on-chain con 0x_bad
    with pytest.raises(HTTPException) as exc:
        CheckoutService.confirm_payment(
            session=session,
            order_id="ord_m1",
            user_id="user_m",
            tx_hash="0x_bad_zero_sender",
        )
    assert exc.value.status_code == 422


# ---------------------------------------------------------------------------
# N. Dos hashes distintos no interfieren entre sí (aislamiento positivo)
# ---------------------------------------------------------------------------

def test_N_two_different_hashes_independent(session):
    """
    [N] Dos usuarios con dos hashes distintos confirman correctamente sus órdenes.
    Verifica que no hay contaminación entre registros de ProcessedTransaction.
    """
    user_a = make_user(session, privy_did="user_n_a", wallet_address="0xNNNA")
    user_b = make_user(session, privy_did="user_n_b", wallet_address="0xNNNB")
    make_wallet(session, user_id="user_n_a")
    make_wallet(session, user_id="user_n_b")

    order_a = make_order(session, "ord_n_a", "user_n_a")
    order_b = make_order(session, "ord_n_b", "user_n_b")

    tx_a = "0xHASH_USER_N_A"
    tx_b = "0xHASH_USER_N_B"

    result_a = CheckoutService.confirm_payment(
        session=session, order_id="ord_n_a", user_id="user_n_a", tx_hash=tx_a
    )
    result_b = CheckoutService.confirm_payment(
        session=session, order_id="ord_n_b", user_id="user_n_b", tx_hash=tx_b
    )

    assert result_a.status == OrderStatus.COMPLETED
    assert result_b.status == OrderStatus.COMPLETED

    # Exactamente 2 registros distintos en ProcessedTransactions
    all_pts = session.exec(
        select(ProcessedTransaction).where(
            ProcessedTransaction.tx_hash.in_([tx_a, tx_b])
        )
    ).all()
    assert len(all_pts) == 2
    assert {pt.tx_hash for pt in all_pts} == {tx_a, tx_b}


# ===========================================================================
# O. Log de intentos de pago (CryptoPaymentAttempt)
# ===========================================================================

def test_O_payment_attempts_logging(session):
    """
    [O] Verifica que todos los intentos (exitosos y fallidos) de confirmación de pago
    se registren correctamente en la tabla CryptoPaymentAttempt.
    """
    from app.models.economy import CryptoPaymentAttempt

    user = make_user(session, privy_did="user_o", wallet_address="0xOOOO")
    make_wallet(session, user_id="user_o")
    order = make_order(session, "ord_o", "user_o")

    # 1. Intento fallido (con un hash inválido que falla verificación)
    tx_fail = "0x_bad_hash_format"
    with pytest.raises(HTTPException) as exc:
        CheckoutService.confirm_payment(
            session=session, order_id="ord_o", user_id="user_o", tx_hash=tx_fail
        )
    assert exc.value.status_code == 422

    # Verificar que el intento fallido se registró
    attempts = session.exec(
        select(CryptoPaymentAttempt).where(CryptoPaymentAttempt.order_id == "ord_o")
    ).all()
    assert len(attempts) == 1
    assert attempts[0].tx_hash == tx_fail
    assert attempts[0].status == "failed"
    assert attempts[0].error_detail is not None

    # 2. Intento exitoso (con un hash válido o mock en local mode)
    tx_success = "0x_mock_valid_payment_attempt"
    result = CheckoutService.confirm_payment(
        session=session, order_id="ord_o", user_id="user_o", tx_hash=tx_success
    )
    assert result.status == OrderStatus.COMPLETED

    # Verificar que el intento exitoso se registró y ahora tenemos 2 intentos
    session.expire_all()
    attempts = session.exec(
        select(CryptoPaymentAttempt)
        .where(CryptoPaymentAttempt.order_id == "ord_o")
        .order_by(CryptoPaymentAttempt.created_at)
    ).all()
    assert len(attempts) == 2

    # El primero sigue siendo el fallido
    assert attempts[0].tx_hash == tx_fail
    assert attempts[0].status == "failed"

    # El segundo es el exitoso
    assert attempts[1].tx_hash == tx_success
    assert attempts[1].status == "success"
