"""
test_bank_service.py — Pruebas unitarias de BankService.

Cubre:
  1. Idempotencia de get_or_create_wallet (misma instancia en llamadas repetidas).
  2. Rechazo de depósitos con monto <= 0.
  3. Exactitud numérica en depósito de Gema-Alga (sin pérdida de decimales).
  4. Rollback de saldo cuando el remitente no tiene fondos suficientes en P2P.
  5. Transferencia P2P aplica la comisión de la casa (5%) correctamente.
  6. Se registran entradas en el Ledger para cada operación.
  7. Rechazo de autotransferencia (sender == receiver).
  8. Rechazo de transferencia de fragmentos (no transferibles por contrato).
"""
import sys
import os
import pytest
from unittest.mock import patch
from fastapi import HTTPException
from sqlmodel import select

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from app.services.bank_service import BankService, P2P_FEE_BPS, P2P_FEE_DENOMINATOR
P2P_FEE_PERCENTAGE = P2P_FEE_BPS / P2P_FEE_DENOMINATOR
from app.models.economy import (
    Wallet, TransactionLedger, CurrencyType, TransactionType
)

# Importar los helpers compartidos de conftest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from conftest import make_user, make_wallet


# ---------------------------------------------------------------------------
# 1. Idempotencia de get_or_create_wallet
# ---------------------------------------------------------------------------

class TestGetOrCreateWallet:
    def test_creates_wallet_when_missing(self, session, engine):
        """Primera llamada crea la wallet con saldos en cero."""
        user = make_user(session, privy_did="did:privy:wallet_new")
        wallet = BankService.get_or_create_wallet(session, user.privy_did)

        assert wallet is not None
        assert wallet.user_id == user.privy_did
        assert wallet.axogemas == 0.0
        assert wallet.gemas_alga == 0.0

    def test_idempotent_second_call_returns_same_wallet(self, session, engine):
        """Llamar dos veces no crea duplicados; devuelve el mismo registro."""
        user = make_user(session, privy_did="did:privy:wallet_idem")
        w1 = BankService.get_or_create_wallet(session, user.privy_did)
        w2 = BankService.get_or_create_wallet(session, user.privy_did)

        # Misma PK → misma fila
        assert w1.id == w2.id

        # Solo existe una wallet para ese usuario en la BD
        wallets = session.exec(
            select(Wallet).where(Wallet.user_id == user.privy_did)
        ).all()
        assert len(wallets) == 1

    def test_existing_wallet_preserves_balance(self, session, engine):
        """get_or_create_wallet no reinicia un saldo preexistente."""
        user = make_user(session, privy_did="did:privy:wallet_preserve")
        make_wallet(session, user_id=user.privy_did, gemas_alga=250.0)

        wallet = BankService.get_or_create_wallet(session, user.privy_did)
        assert wallet.gemas_alga == 250.0


# ---------------------------------------------------------------------------
# 2. admin_deposit — validaciones de entrada
# ---------------------------------------------------------------------------

class TestAdminDepositValidation:
    def test_rejects_zero_amount(self, session, engine):
        """Monto = 0 debe lanzar HTTPException 400."""
        user = make_user(session, privy_did="did:privy:dep_zero")
        with pytest.raises(HTTPException) as exc_info:
            BankService.admin_deposit(
                session, user.privy_did, 0, CurrencyType.GEMA_ALGA, "test"
            )
        assert exc_info.value.status_code == 400

    def test_rejects_negative_amount(self, session, engine):
        """Monto negativo debe lanzar HTTPException 400."""
        user = make_user(session, privy_did="did:privy:dep_neg")
        with pytest.raises(HTTPException) as exc_info:
            BankService.admin_deposit(
                session, user.privy_did, -50.0, CurrencyType.GEMA_ALGA, "test"
            )
        assert exc_info.value.status_code == 400

    def test_rejects_unknown_user(self, session, engine):
        """Usuario inexistente debe lanzar HTTPException 404."""
        with pytest.raises(HTTPException) as exc_info:
            BankService.admin_deposit(
                session, "did:privy:ghost", 100.0, CurrencyType.GEMA_ALGA, "test"
            )
        assert exc_info.value.status_code == 404


# ---------------------------------------------------------------------------
# 3. admin_deposit — exactitud numérica en Gema-Alga
# ---------------------------------------------------------------------------

class TestAdminDepositNumericAccuracy:
    def test_gema_alga_precision(self, session, engine):
        """El saldo se incrementa exactamente sin pérdida de decimales."""
        user = make_user(session, privy_did="did:privy:dep_precise")
        initial_deposit = 123.456
        second_deposit = 876.544

        BankService.admin_deposit(
            session, user.privy_did, initial_deposit, CurrencyType.GEMA_ALGA, "dep1"
        )
        BankService.admin_deposit(
            session, user.privy_did, second_deposit, CurrencyType.GEMA_ALGA, "dep2"
        )

        wallet = BankService.get_or_create_wallet(session, user.privy_did)
        total = initial_deposit + second_deposit
        assert abs(wallet.gemas_alga - total) < 1e-9, (
            f"Esperado {total}, obtenido {wallet.gemas_alga}"
        )

    def test_ledger_entry_created_on_deposit(self, session, engine):
        """Cada depósito genera exactamente una entrada en TransactionLedger."""
        user = make_user(session, privy_did="did:privy:dep_ledger")
        BankService.admin_deposit(
            session, user.privy_did, 50.0, CurrencyType.GEMA_ALGA, "ledger_test"
        )

        entries = session.exec(
            select(TransactionLedger).where(
                TransactionLedger.user_id == user.privy_did
            )
        ).all()
        assert len(entries) == 1
        assert entries[0].amount == 50.0
        assert entries[0].currency == CurrencyType.GEMA_ALGA

    def test_axogema_deposit_blocked_without_wallet_address(self, session, engine):
        """Depositar AXOGEMA a un usuario sin wallet_address Web3 debe fallar."""
        user = make_user(
            session,
            privy_did="did:privy:dep_axg_nowallet",
            wallet_address=None,    # Sin wallet vinculada
        )
        with pytest.raises(HTTPException) as exc_info:
            BankService.admin_deposit(
                session, user.privy_did, 10.0, CurrencyType.AXOGEMA, "axg_test"
            )
        assert exc_info.value.status_code == 400


# ---------------------------------------------------------------------------
# 4. transfer_p2p — validaciones de entrada
# ---------------------------------------------------------------------------

class TestTransferP2PValidation:
    def test_rejects_zero_amount(self, session, engine):
        """Monto = 0 en P2P debe lanzar 400."""
        u1 = make_user(session, privy_did="did:privy:p2p_z_sender")
        u2 = make_user(session, privy_did="did:privy:p2p_z_receiver")
        with pytest.raises(HTTPException) as exc_info:
            BankService.transfer_p2p(
                session, u1.privy_did, u2.privy_did, 0, CurrencyType.GEMA_ALGA
            )
        assert exc_info.value.status_code == 400

    def test_rejects_self_transfer(self, session, engine):
        """Enviarse gemas a uno mismo debe lanzar 400."""
        user = make_user(session, privy_did="did:privy:p2p_self")
        with pytest.raises(HTTPException) as exc_info:
            BankService.transfer_p2p(
                session, user.privy_did, user.privy_did, 100.0, CurrencyType.GEMA_ALGA
            )
        assert exc_info.value.status_code == 400

    def test_rejects_fragment_transfer(self, session, engine):
        """Los fragmentos no son transferibles entre jugadores."""
        u1 = make_user(session, privy_did="did:privy:p2p_frag1")
        u2 = make_user(session, privy_did="did:privy:p2p_frag2")
        make_wallet(session, user_id=u1.privy_did, gemas_alga=500.0)
        make_wallet(session, user_id=u2.privy_did)
        with pytest.raises(HTTPException):
            BankService.transfer_p2p(
                session, u1.privy_did, u2.privy_did, 10.0,
                CurrencyType.FRAGMENTO_COMUN
            )


# ---------------------------------------------------------------------------
# 5. transfer_p2p — rollback por fondos insuficientes
# ---------------------------------------------------------------------------

class TestTransferP2PInsufficientFunds:
    def test_rollback_on_insufficient_balance(self, session, engine):
        """Si el remitente no tiene fondos, ambas wallets quedan intactas."""
        u1 = make_user(session, privy_did="did:privy:p2p_broke_s")
        u2 = make_user(session, privy_did="did:privy:p2p_broke_r")
        make_wallet(session, user_id=u1.privy_did, gemas_alga=10.0)   # Saldo insuficiente
        make_wallet(session, user_id=u2.privy_did, gemas_alga=0.0)

        with pytest.raises(HTTPException) as exc_info:
            BankService.transfer_p2p(
                session, u1.privy_did, u2.privy_did, 100.0, CurrencyType.GEMA_ALGA
            )
        assert exc_info.value.status_code == 400

        # Refrescar wallets y verificar que los saldos NO cambiaron
        session.expire_all()
        w1 = BankService.get_or_create_wallet(session, u1.privy_did)
        w2 = BankService.get_or_create_wallet(session, u2.privy_did)
        assert w1.gemas_alga == 10.0, "El remitente no debe perder saldo."
        assert w2.gemas_alga == 0.0, "El receptor no debe ganar saldo."

    def test_no_ledger_entries_on_failed_transfer(self, session, engine):
        """Una transferencia fallida no debe dejar registros en el Ledger."""
        u1 = make_user(session, privy_did="did:privy:p2p_ledger_fail_s")
        u2 = make_user(session, privy_did="did:privy:p2p_ledger_fail_r")
        make_wallet(session, user_id=u1.privy_did, gemas_alga=5.0)
        make_wallet(session, user_id=u2.privy_did)

        with pytest.raises(HTTPException):
            BankService.transfer_p2p(
                session, u1.privy_did, u2.privy_did, 50.0, CurrencyType.GEMA_ALGA
            )

        entries = session.exec(
            select(TransactionLedger).where(
                TransactionLedger.user_id.in_([u1.privy_did, u2.privy_did])
            )
        ).all()
        assert len(entries) == 0, "No deben quedar entradas en el Ledger tras un fallo."


# ---------------------------------------------------------------------------
# 6. transfer_p2p — comisión y exactitud
# ---------------------------------------------------------------------------

class TestTransferP2PFee:
    def test_correct_fee_applied_gema_alga(self, session, engine):
        """La comisión de la casa (5%) se descuenta correctamente del receptor."""
        u1 = make_user(session, privy_did="did:privy:p2p_fee_s")
        u2 = make_user(session, privy_did="did:privy:p2p_fee_r")
        make_wallet(session, user_id=u1.privy_did, gemas_alga=200.0)
        make_wallet(session, user_id=u2.privy_did, gemas_alga=0.0)

        amount = 100.0
        result = BankService.transfer_p2p(
            session, u1.privy_did, u2.privy_did, amount, CurrencyType.GEMA_ALGA
        )

        expected_fee = amount * P2P_FEE_PERCENTAGE      # 5.0
        expected_received = amount - expected_fee        # 95.0

        assert abs(result["comision"] - expected_fee) < 1e-9
        assert abs(result["recibido_por_amigo"] - expected_received) < 1e-9

        session.expire_all()
        w1 = BankService.get_or_create_wallet(session, u1.privy_did)
        w2 = BankService.get_or_create_wallet(session, u2.privy_did)

        # El remitente pierde el monto total (sin importar la comisión)
        assert abs(w1.gemas_alga - (200.0 - amount)) < 1e-9
        # El receptor recibe el monto menos la comisión
        assert abs(w2.gemas_alga - expected_received) < 1e-9

    def test_ledger_entries_created_on_successful_transfer(self, session, engine):
        """Una transferencia exitosa genera exactamente 2 entradas en el Ledger."""
        u1 = make_user(session, privy_did="did:privy:p2p_ledger_ok_s")
        u2 = make_user(session, privy_did="did:privy:p2p_ledger_ok_r")
        make_wallet(session, user_id=u1.privy_did, gemas_alga=500.0)
        make_wallet(session, user_id=u2.privy_did, gemas_alga=0.0)

        BankService.transfer_p2p(
            session, u1.privy_did, u2.privy_did, 50.0, CurrencyType.GEMA_ALGA
        )

        sender_entries = session.exec(
            select(TransactionLedger).where(
                TransactionLedger.user_id == u1.privy_did,
                TransactionLedger.tx_type == TransactionType.P2P_SEND,
            )
        ).all()
        receiver_entries = session.exec(
            select(TransactionLedger).where(
                TransactionLedger.user_id == u2.privy_did,
                TransactionLedger.tx_type == TransactionType.P2P_RECEIVE,
            )
        ).all()

        assert len(sender_entries) == 1, "Debe haber exactamente 1 entrada de salida."
        assert len(receiver_entries) == 1, "Debe haber exactamente 1 entrada de entrada."
        assert receiver_entries[0].fee_applied == 50.0 * P2P_FEE_PERCENTAGE

    def test_sender_cannot_overdraft_with_exact_boundary(self, session, engine):
        """El remitente con saldo exactamente igual al monto sí puede enviar."""
        u1 = make_user(session, privy_did="did:privy:p2p_exact_s")
        u2 = make_user(session, privy_did="did:privy:p2p_exact_r")
        make_wallet(session, user_id=u1.privy_did, gemas_alga=100.0)
        make_wallet(session, user_id=u2.privy_did, gemas_alga=0.0)

        # Saldo = monto exacto → debe pasar
        result = BankService.transfer_p2p(
            session, u1.privy_did, u2.privy_did, 100.0, CurrencyType.GEMA_ALGA
        )
        assert result["enviado"] == 100.0

        session.expire_all()
        w1 = BankService.get_or_create_wallet(session, u1.privy_did)
        assert w1.gemas_alga == 0.0, "El remitente debe quedar en cero."
