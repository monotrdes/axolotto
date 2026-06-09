"""
test_blockchain_desync.py — Pruebas de desincronización entre BD y Blockchain.

Escenarios cubiertos:
  1. Fallo de Web3Service ANTES del commit en BD → saldo no se guarda (consistente).
  2. Fallo de Web3Service con excepción genérica → respuesta es HTTP 500.
  3. Timeout de Web3Service → excepción manejada, BD no commitea.
  4. Depósito de GAL (sin blockchain) siempre es consistente aunque la BD rollbackee.
  5. Mock de transferir_axogemas exitoso → BD sí se guarda, tx_hash devuelto.
  6. La llamada a Web3Service ocurre ANTES del commit (orden correcto en bank_service).
  7. Múltiples fallos consecutivos no dejan estado parcial acumulado.
  8. verify_usdc_payment: hash mock siempre devuelve True (modo dev).
  9. verify_usdc_payment: hash que falla en RPC → devuelve False sin romper el flujo.
 10. is_connected: True/False sin lanzar excepción.
"""
import sys
import os
import pytest
from unittest.mock import patch, MagicMock, call
from fastapi import HTTPException
from sqlmodel import select

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from app.services.bank_service import BankService
from app.services.web3_service import Web3Service
from app.models.economy import Wallet, TransactionLedger, CurrencyType

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from conftest import make_user, make_wallet


# ---------------------------------------------------------------------------
# 1. Fallo de blockchain ANTES del commit → BD no queda sucia
# ---------------------------------------------------------------------------

class TestBlockchainFailBeforeCommit:
    def test_axogema_deposit_rollsback_when_blockchain_fails(self, session, engine):
        """
        Si transferir_axogemas lanza excepción, admin_deposit debe re-lanzar
        HTTP 500 y NO guardar nada en la BD (saldo permanece en 0).
        """
        user = make_user(
            session,
            privy_did="did:privy:desync_axg_fail",
            wallet_address="0xDeAdBeEf000000000000000000000000DeAdBeEf",
        )

        with patch(
            "app.services.bank_service.Web3Service.transferir_axogemas",
            side_effect=Exception("Nonce conflict — red caída"),
        ):
            with pytest.raises(HTTPException) as exc_info:
                BankService.admin_deposit(
                    session,
                    user.privy_did,
                    50.0,
                    CurrencyType.AXOGEMA,
                    "test blockchain fail",
                )

        assert exc_info.value.status_code == 500
        assert "Blockchain" in exc_info.value.detail

        # El saldo NO debe haberse modificado
        wallet = session.exec(
            select(Wallet).where(Wallet.user_id == user.privy_did)
        ).first()
        if wallet:
            assert wallet.axogemas == 0.0, "El saldo no debe cambiar tras fallo blockchain."

        # No debe haber entradas en el Ledger
        ledger = session.exec(
            select(TransactionLedger).where(TransactionLedger.user_id == user.privy_did)
        ).all()
        assert len(ledger) == 0, "No debe quedar registro en el Ledger tras fallo blockchain."

    def test_blockchain_timeout_raises_500(self, session, engine):
        """Un timeout de Web3Service debe resultar en HTTP 500, no 200 parcial."""
        import socket
        user = make_user(
            session,
            privy_did="did:privy:desync_timeout",
            wallet_address="0xDeAdBeEf000000000000000000000001DeAdBeEf",
        )

        with patch(
            "app.services.bank_service.Web3Service.transferir_axogemas",
            side_effect=TimeoutError("RPC timeout after 30s"),
        ):
            with pytest.raises(HTTPException) as exc_info:
                BankService.admin_deposit(
                    session,
                    user.privy_did,
                    100.0,
                    CurrencyType.AXOGEMA,
                    "timeout test",
                )

        assert exc_info.value.status_code == 500

    def test_multiple_consecutive_failures_leave_no_partial_state(self, session, engine):
        """
        Tres depósitos AXOGEMA fallidos consecutivos no deben acumular saldo
        ni dejar registros en el Ledger.
        """
        user = make_user(
            session,
            privy_did="did:privy:desync_multi_fail",
            wallet_address="0xDeAdBeEf000000000000000000000002DeAdBeEf",
        )

        with patch(
            "app.services.bank_service.Web3Service.transferir_axogemas",
            side_effect=Exception("red caída"),
        ):
            for _ in range(3):
                with pytest.raises(HTTPException):
                    BankService.admin_deposit(
                        session,
                        user.privy_did,
                        10.0,
                        CurrencyType.AXOGEMA,
                        "multi fail",
                    )

        wallet = session.exec(
            select(Wallet).where(Wallet.user_id == user.privy_did)
        ).first()
        if wallet:
            assert wallet.axogemas == 0.0, "Tres fallos no deben acumular saldo."

        ledger = session.exec(
            select(TransactionLedger).where(TransactionLedger.user_id == user.privy_did)
        ).all()
        assert len(ledger) == 0, "Tres fallos no deben dejar entradas en Ledger."


# ---------------------------------------------------------------------------
# 2. Blockchain exitosa → BD se guarda correctamente
# ---------------------------------------------------------------------------

class TestBlockchainSuccessConsistency:
    def test_successful_axogema_deposit_saves_wallet_and_ledger(self, session, engine):
        """
        Con blockchain mockeada exitosa, el saldo se guarda en BD
        y el tx_hash aparece en la respuesta.
        """
        user = make_user(
            session,
            privy_did="did:privy:desync_axg_ok",
            wallet_address="0xDeAdBeEf000000000000000000000003DeAdBeEf",
        )
        fake_tx_hash = "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890ab"

        with patch(
            "app.services.bank_service.Web3Service.transferir_axogemas",
            return_value=fake_tx_hash,
        ):
            result = BankService.admin_deposit(
                session,
                user.privy_did,
                25.0,
                CurrencyType.AXOGEMA,
                "blockchain ok test",
            )

        assert result["tx_hash"] == fake_tx_hash
        assert "polygon_scan" in result

        session.expire_all()
        wallet = BankService.get_or_create_wallet(session, user.privy_did)
        assert wallet.axogemas == 25.0, "Saldo debe haberse guardado tras blockchain exitosa."

        ledger = session.exec(
            select(TransactionLedger).where(TransactionLedger.user_id == user.privy_did)
        ).all()
        assert len(ledger) == 1
        assert ledger[0].amount == 25.0

    def test_gal_deposit_always_consistent_no_blockchain(self, session, engine):
        """
        Un depósito de Gema-Alga no llama a Web3Service, por lo que
        siempre es consistente aunque la blockchain esté caída.
        """
        user = make_user(session, privy_did="did:privy:desync_gal_ok")

        with patch(
            "app.services.bank_service.Web3Service.transferir_axogemas",
            side_effect=Exception("blockchain caída"),  # nunca debe llamarse
        ):
            result = BankService.admin_deposit(
                session,
                user.privy_did,
                500.0,
                CurrencyType.GEMA_ALGA,
                "gal sin blockchain",
            )

        assert result["nuevo_saldo"] == 500.0

        session.expire_all()
        wallet = BankService.get_or_create_wallet(session, user.privy_did)
        assert wallet.gemas_alga == 500.0

    def test_blockchain_called_before_db_commit(self, session, engine):
        """
        Verificar que Web3Service se invoca ANTES del commit que persiste el saldo.

        El flujo en bank_service.admin_deposit es:
          1. get_or_create_wallet()  →  puede hacer un commit interno (crear wallet)
          2. Web3Service.transferir_axogemas()  →  blockchain
          3. session.commit()  →  persiste el saldo actualizado en BD

        El invariante crítico es que la blockchain (paso 2) ocurra
        ANTES del commit final que persiste el saldo (paso 3), no antes
        del commit auxiliar de creación de wallet (paso 1).
        """
        user = make_user(
            session,
            privy_did="did:privy:desync_order",
            wallet_address="0xDeAdBeEf000000000000000000000004DeAdBeEf",
        )
        call_log = []

        def mock_transferir(to_address, amount):
            call_log.append("blockchain_called")
            return "0x_mock_hash_order_test"

        original_commit = session.commit

        def mock_commit():
            call_log.append("db_committed")
            original_commit()

        # Activar el interceptor durante admin_deposit
        with patch(
            "app.services.bank_service.Web3Service.transferir_axogemas",
            side_effect=mock_transferir,
        ):
            with patch.object(session, "commit", side_effect=mock_commit):
                BankService.admin_deposit(
                    session,
                    user.privy_did,
                    10.0,
                    CurrencyType.AXOGEMA,
                    "order test",
                )

        # Invariante: blockchain debe haberse llamado Y el saldo debe haberse commiteado
        assert "blockchain_called" in call_log, "Web3Service debe haberse invocado."
        assert "db_committed" in call_log, "El commit debe ocurrir tras blockchain."

        # El commit FINAL (el que persiste el saldo) debe venir DESPUÉS de blockchain.
        # Puede haber commits previos (get_or_create_wallet), lo que importa es
        # que blockchain llegue antes del último commit.
        bc_idx = call_log.index("blockchain_called")
        last_commit_idx = len(call_log) - 1 - call_log[::-1].index("db_committed")
        assert bc_idx < last_commit_idx, (
            f"Web3Service (pos {bc_idx}) debe invocarse ANTES del commit final "
            f"de saldo (pos {last_commit_idx}). Log: {call_log}"
        )


# ---------------------------------------------------------------------------
# 3. verify_usdc_payment — modo dev y manejo de errores RPC
# ---------------------------------------------------------------------------

class TestVerifyUsdcPayment:
    def test_mock_hash_always_returns_true(self):
        """En modo dev, hashes con prefijo '0x_mock' siempre son válidos."""
        result = Web3Service.verify_usdc_payment(
            tx_hash="0x_mock_dev_hash",
            expected_recipient="0x0000000000000000000000000000000000000001",
            min_usdc=10.0,
        )
        assert result is True

    def test_empty_hash_returns_true_in_dev(self):
        """Hash vacío es tratado como modo dev."""
        result = Web3Service.verify_usdc_payment(
            tx_hash="",
            expected_recipient="0x0000000000000000000000000000000000000001",
            min_usdc=5.0,
        )
        assert result is True

    def test_rpc_failure_returns_false_without_raising(self):
        """
        Si la RPC lanza excepción al verificar, verify_usdc_payment
        debe devolver False sin propagar la excepción.

        Se parchea USDC_ADDRESS para que el código no tome el atajo de dev
        ("USDC_ADDRESS no configurado → True") y llegue al bloque que
        invoca _get_w3 donde ocurre el fallo de RPC.
        """
        with patch(
            "app.services.web3_service.Web3Service._get_w3",
            side_effect=Exception("RPC no disponible"),
        ), patch(
            "app.services.web3_service.settings.USDC_ADDRESS",
            "0x0000000000000000000000000000000000000002",
        ):
            result = Web3Service.verify_usdc_payment(
                tx_hash="0xREAL_HASH_THAT_DOESNT_EXIST_12345678901234567890",
                expected_recipient="0x0000000000000000000000000000000000000001",
                min_usdc=10.0,
            )
        assert result is False, "RPC caída debe devolver False, no lanzar excepción."

    def test_receipt_status_failed_returns_false(self):
        """
        Si el recibo tiene status=0 (revertida on-chain), debe devolver False.
        Se parchea USDC_ADDRESS para bypassar el atajo de modo dev.
        """
        mock_w3 = MagicMock()
        mock_w3.eth.get_transaction_receipt.return_value = {
            "status": 0,
            "logs": [],
        }

        with patch(
            "app.services.web3_service.Web3Service._get_w3",
            return_value=mock_w3,
        ), patch(
            "app.services.web3_service.settings.USDC_ADDRESS",
            "0x0000000000000000000000000000000000000002",
        ):
            result = Web3Service.verify_usdc_payment(
                tx_hash="0xREAL_REVERTED_TX_HASH_123456789012345678901234567",
                expected_recipient="0x0000000000000000000000000000000000000001",
                min_usdc=10.0,
            )
        assert result is False, "Transacción revertida debe devolver False."

    def test_receipt_none_returns_false(self):
        """
        Si el recibo es None (tx pendiente/inexistente), debe devolver False.
        Se parchea USDC_ADDRESS para bypassar el atajo de modo dev.
        """
        mock_w3 = MagicMock()
        mock_w3.eth.get_transaction_receipt.return_value = None

        with patch(
            "app.services.web3_service.Web3Service._get_w3",
            return_value=mock_w3,
        ), patch(
            "app.services.web3_service.settings.USDC_ADDRESS",
            "0x0000000000000000000000000000000000000002",
        ):
            result = Web3Service.verify_usdc_payment(
                tx_hash="0xREAL_PENDING_TX_HASH_1234567890123456789012345678",
                expected_recipient="0x0000000000000000000000000000000000000001",
                min_usdc=10.0,
            )
        assert result is False


# ---------------------------------------------------------------------------
# 4. is_connected — manejo seguro de fallos RPC
# ---------------------------------------------------------------------------

class TestIsConnected:
    def test_returns_true_when_connected(self):
        """is_connected devuelve True cuando Web3 puede conectarse."""
        mock_w3 = MagicMock()
        mock_w3.is_connected.return_value = True

        with patch(
            "app.services.web3_service.Web3Service._get_w3",
            return_value=mock_w3,
        ):
            assert Web3Service.is_connected() is True

    def test_returns_false_when_rpc_unreachable(self):
        """is_connected devuelve False sin lanzar excepción cuando la RPC falla."""
        with patch(
            "app.services.web3_service.Web3Service._get_w3",
            side_effect=Exception("Connection refused"),
        ):
            result = Web3Service.is_connected()
        assert result is False, "RPC caída debe devolver False, no propagar excepción."

    def test_returns_false_when_w3_not_connected(self):
        """is_connected devuelve False si Web3.is_connected() devuelve False."""
        mock_w3 = MagicMock()
        mock_w3.is_connected.return_value = False

        with patch(
            "app.services.web3_service.Web3Service._get_w3",
            return_value=mock_w3,
        ):
            assert Web3Service.is_connected() is False
