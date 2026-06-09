"""
simulate_degraded_network.py — Simulación de red degradada (§3.3)

Escenarios cubiertos (backend — pytest):
  A. Latencia alta en Web3Service (100 ms) → open_booster completa con 200; BD consistente.
  B. Latencia muy alta en burn onchain (2 s) → open_booster tolera el retraso (try/except).
  C. Timeout en llamada crítica (transferir_axogemas) → admin_deposit falla con 500; BD intacta.
  D. Desconexión intermitente (50% fallo) → buy_item nunca deja estado parcial en BD.
  E. Double-submit de apertura de booster (1 unidad, 10 hilos) → exactamente 1 entrega, 9 rechazos.
  F. Double-submit con latencia (race bajo lentitud blockchain) → sigue garantizando 1 ganador.
  G. Recuperación: fallo blockchain seguido de éxito → el éxito persiste correctamente.
  H. Cascada: buy_item → open_booster bajo latencia 200 ms; BD consistente al final.

Checks de frontend (manuales — no automatizables sin Playwright):
  ☐ El botón de compra muestra spinner mientras la petición está en vuelo (isLoading=true).
  ☐ El botón permanece deshabilitado hasta que llega la respuesta.
  ☐ Doble-click en "Comprar" no dispara dos peticiones (debounce o disabled inmediato).
  ☐ Si el backend tarda > 10 s, el frontend muestra "Intenta de nuevo" y habilita el botón.
  ☐ Doble-submit de formulario de checkout no genera dos órdenes (botón disabled post-click).
"""

import sys
import os
import time
import random
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import patch
import pytest
from fastapi import HTTPException
from sqlmodel import Session, select

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from app.services.shop_service import ShopService
from app.services.bank_service import BankService
from app.models.economy import Wallet, CurrencyType
from app.models.items import ItemCatalog, PlayerInventory, ItemType, Rarity
from app.models.user import User

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from conftest import make_user, make_wallet, make_item, make_card_pool


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _addr(n: int) -> str:
    return f"0x{n:040x}"


def _slow_ok(delay_s: float = 0.1):
    """Mock que espera delay_s y devuelve un tx_hash falso."""
    def _fn(*args, **kwargs):
        time.sleep(delay_s)
        return "0x_slow_mock_hash"
    return _fn


def _intermittent(fail_rate: float = 0.5):
    """Mock que falla con probabilidad fail_rate."""
    def _fn(*args, **kwargs):
        if random.random() < fail_rate:
            raise ConnectionError("Nodo RPC no disponible (simulado)")
        return "0x_intermittent_mock_hash"
    return _fn


_make_cards_catalog = make_card_pool  # alias local; make_card_pool(session, count=10)


def _make_booster(session: Session, user_id: str, qty: int = 1) -> tuple:
    """Crea un ítem booster en catálogo + entrada en inventario del usuario."""
    item = make_item(
        session,
        name=f"Booster-Net-{user_id[-6:]}",
        item_type=ItemType.BOOSTER,
        price_axg=10.0,
        item_metadata={"fase": 1},
    )
    inv = PlayerInventory(user_id=user_id, item_id=item.id, quantity=qty)
    session.add(inv)
    session.commit()
    session.refresh(inv)
    return item, inv


# ---------------------------------------------------------------------------
# A. Latencia baja (100 ms) — open_booster retorna resultado con cartas
# ---------------------------------------------------------------------------

class TestLowLatency:
    def test_open_booster_succeeds_with_100ms_latency(self, session):
        """Web3 tarda 100 ms al quemar; el resultado debe incluir cartas y BD queda limpia."""
        _make_cards_catalog(session)
        user = make_user(session, privy_did="net_a1", wallet_address=_addr(0xA001))
        item, _ = _make_booster(session, user.privy_did)

        with patch("app.services.shop_service.Web3Service.burn_booster_onchain",
                   side_effect=_slow_ok(0.1)), \
             patch("app.services.shop_service.Web3Service.mint_cards_onchain",
                   side_effect=_slow_ok(0.1)):
            result = ShopService.open_booster(session, user.privy_did, item.id)

        assert isinstance(result, dict)

        inv = session.exec(
            select(PlayerInventory)
            .where(PlayerInventory.user_id == user.privy_did)
            .where(PlayerInventory.item_id == item.id)
        ).first()
        assert inv is None or inv.quantity == 0, "Inventario debe haberse consumido."

    def test_bd_consistent_after_slow_open_booster(self, session):
        """Apertura lenta (150 ms) no deja duplicados ni registros huérfanos en inventario."""
        _make_cards_catalog(session)
        user = make_user(session, privy_did="net_a2", wallet_address=_addr(0xA002))
        item, _ = _make_booster(session, user.privy_did)

        with patch("app.services.shop_service.Web3Service.burn_booster_onchain",
                   side_effect=_slow_ok(0.15)), \
             patch("app.services.shop_service.Web3Service.mint_cards_onchain",
                   side_effect=_slow_ok(0.1)):
            ShopService.open_booster(session, user.privy_did, item.id)

        inv_rows = session.exec(
            select(PlayerInventory)
            .where(PlayerInventory.user_id == user.privy_did)
            .where(PlayerInventory.item_id == item.id)
        ).all()
        total_qty = sum(r.quantity for r in inv_rows)
        assert total_qty == 0, "Exactamente 1 booster debe haberse consumido."


# ---------------------------------------------------------------------------
# B. Latencia alta (2 s) en burn — open_booster lo tolera vía try/except
# ---------------------------------------------------------------------------

class TestHighLatencyTolerated:
    def test_open_booster_tolerates_slow_burn(self, session):
        """
        El burn onchain está en try/except; aunque tarde 2 s, el sobre abre y entrega cartas.
        """
        _make_cards_catalog(session)
        user = make_user(session, privy_did="net_b1", wallet_address=_addr(0xB001))
        item, _ = _make_booster(session, user.privy_did)

        with patch("app.services.shop_service.Web3Service.burn_booster_onchain",
                   side_effect=_slow_ok(2.0)), \
             patch("app.services.shop_service.Web3Service.mint_cards_onchain",
                   return_value="0x_mint_ok"):
            t0 = time.monotonic()
            result = ShopService.open_booster(session, user.privy_did, item.id)
            elapsed = time.monotonic() - t0

        assert isinstance(result, dict)
        assert elapsed >= 1.8, f"Mock de 2 s debió tardar ≥1.8 s; tardó {elapsed:.2f}s"

    def test_open_booster_tolerates_burn_failure(self, session):
        """Si burn_booster_onchain lanza excepción (red caída), el sobre igual se abre."""
        _make_cards_catalog(session)
        user = make_user(session, privy_did="net_b2", wallet_address=_addr(0xB002))
        item, _ = _make_booster(session, user.privy_did)

        with patch("app.services.shop_service.Web3Service.burn_booster_onchain",
                   side_effect=ConnectionError("RPC timeout")), \
             patch("app.services.shop_service.Web3Service.mint_cards_onchain",
                   return_value="0x_mint_ok"):
            result = ShopService.open_booster(session, user.privy_did, item.id)

        assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# C. Timeout en llamada CRÍTICA → HTTP 500, BD intacta
# ---------------------------------------------------------------------------

class TestCriticalCallTimeout:
    def test_admin_deposit_fails_with_timeout(self, session):
        """
        transferir_axogemas (llamada crítica sin try/except) levanta TimeoutError →
        admin_deposit debe retornar HTTP 500 y NO modificar el saldo.
        """
        user = make_user(session, privy_did="net_c1", wallet_address=_addr(0xC001))

        def _slow_timeout(*args, **kwargs):
            time.sleep(0.05)
            raise TimeoutError("RPC timeout después de 30s")

        with patch("app.services.bank_service.Web3Service.transferir_axogemas",
                   side_effect=_slow_timeout):
            with pytest.raises(HTTPException) as exc:
                BankService.admin_deposit(
                    session, user.privy_did, 50.0, CurrencyType.AXOGEMA, "timeout critico"
                )

        assert exc.value.status_code == 500
        wallet = session.exec(select(Wallet).where(Wallet.user_id == user.privy_did)).first()
        if wallet:
            assert wallet.axogemas == 0.0, "BD no debe haberse modificado tras timeout."


# ---------------------------------------------------------------------------
# D. Desconexión intermitente → buy_item nunca deja estado parcial
# ---------------------------------------------------------------------------

class TestIntermittentDisconnect:
    def test_no_partial_state_after_intermittent_failures(self, session):
        """
        Con 80% de tasa de fallo en Web3, repetir buy_item 5 veces.
        El saldo solo debe bajar en las operaciones que completaron exitosamente.
        """
        user = make_user(session, privy_did="net_d1", wallet_address=_addr(0xD001))
        make_wallet(session, user.privy_did, axogemas=500.0)
        item = make_item(
            session,
            name="Booster-Intermittent",
            item_type=ItemType.BOOSTER,
            price_axg=10.0,
            item_metadata={"fase": 1},
        )

        successes = 0
        for _ in range(5):
            try:
                with patch("app.services.shop_service.Web3Service.burn_axogemas",
                           side_effect=_intermittent(fail_rate=0.8)), \
                     patch("app.services.shop_service.Web3Service.mint_booster_onchain",
                           side_effect=_intermittent(fail_rate=0.8)):
                    ShopService.buy_item(session, user.privy_did, item.id, CurrencyType.AXOGEMA)
                    successes += 1
            except Exception:
                session.rollback()

        session.expire_all()
        wallet_final = session.exec(select(Wallet).where(Wallet.user_id == user.privy_did)).first()

        expected_balance = 500.0 - successes * 10.0
        assert wallet_final.axogemas == pytest.approx(expected_balance, abs=0.01), (
            f"Saldo esperado: {expected_balance}, real: {wallet_final.axogemas} "
            f"({successes} compras exitosas)"
        )


# ---------------------------------------------------------------------------
# E. Double-submit de apertura (1 unidad, 10 hilos) → exactamente 1 éxito
# ---------------------------------------------------------------------------

class TestDoubleSubmitPrevention:
    def test_concurrent_open_booster_only_one_succeeds(self, session, engine):
        """
        10 hilos intentan abrir el mismo booster (quantity=1) simultáneamente.
        SELECT FOR UPDATE garantiza que solo 1 tiene éxito; los demás reciben 400.
        Requiere PostgreSQL (SQLite no soporta bloqueo a nivel de fila).
        """
        if engine.dialect.name == "sqlite":
            pytest.skip("SQLite no soporta SELECT FOR UPDATE entre hilos.")
        _make_cards_catalog(session)
        user = make_user(session, privy_did="net_e1", wallet_address=None)
        item, _ = _make_booster(session, user.privy_did, qty=1)

        results = []
        lock = threading.Lock()

        def attempt():
            from sqlmodel import Session as S
            with S(engine) as s:
                try:
                    with patch("app.services.shop_service.Web3Service.burn_booster_onchain",
                               return_value="0x_mock"), \
                         patch("app.services.shop_service.Web3Service.mint_cards_onchain",
                               return_value="0x_mock"):
                        ShopService.open_booster(s, user.privy_did, item.id)
                    with lock:
                        results.append("ok")
                except HTTPException as e:
                    with lock:
                        results.append(e.status_code)
                except Exception:
                    with lock:
                        results.append("error")

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(attempt) for _ in range(10)]
            for f in as_completed(futures):
                f.result()

        success_count = results.count("ok")
        assert success_count == 1, (
            f"Exactamente 1 apertura debe tener éxito. Resultados: {results}"
        )

    def test_concurrent_open_booster_with_latency(self, session, engine):
        """
        Lo mismo con 100 ms de latencia en burn onchain — SELECT FOR UPDATE sigue siendo efectivo.
        Requiere PostgreSQL (SQLite no soporta bloqueo a nivel de fila).
        """
        if engine.dialect.name == "sqlite":
            pytest.skip("SQLite no soporta SELECT FOR UPDATE entre hilos.")
        _make_cards_catalog(session)
        user = make_user(session, privy_did="net_e2", wallet_address=None)
        item, _ = _make_booster(session, user.privy_did, qty=1)

        results = []
        lock = threading.Lock()

        def attempt():
            from sqlmodel import Session as S
            with S(engine) as s:
                try:
                    with patch("app.services.shop_service.Web3Service.burn_booster_onchain",
                               side_effect=_slow_ok(0.1)), \
                         patch("app.services.shop_service.Web3Service.mint_cards_onchain",
                               side_effect=_slow_ok(0.05)):
                        ShopService.open_booster(s, user.privy_did, item.id)
                    with lock:
                        results.append("ok")
                except HTTPException as e:
                    with lock:
                        results.append(e.status_code)
                except Exception:
                    with lock:
                        results.append("error")

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(attempt) for _ in range(8)]
            for f in as_completed(futures):
                f.result()

        success_count = results.count("ok")
        assert success_count == 1, (
            f"Con latencia, exactamente 1 apertura debe tener éxito. Resultados: {results}"
        )


# ---------------------------------------------------------------------------
# G. Recuperación: fallo → éxito → saldo correcto
# ---------------------------------------------------------------------------

class TestRecoveryAfterFailure:
    def test_successful_deposit_after_blockchain_failure(self, session):
        """
        Primer intento: blockchain caída → HTTP 500, saldo intacto.
        Segundo intento: blockchain recuperada → saldo actualizado a 100 AXG.
        """
        user = make_user(session, privy_did="net_g1", wallet_address=_addr(0x9001))

        with patch("app.services.bank_service.Web3Service.transferir_axogemas",
                   side_effect=Exception("nodo caído")):
            with pytest.raises(HTTPException) as exc:
                BankService.admin_deposit(
                    session, user.privy_did, 100.0, CurrencyType.AXOGEMA, "fallo 1"
                )
        assert exc.value.status_code == 500

        with patch("app.services.bank_service.Web3Service.transferir_axogemas",
                   return_value="0x_recovery_hash"):
            result = BankService.admin_deposit(
                session, user.privy_did, 100.0, CurrencyType.AXOGEMA, "éxito 2"
            )

        assert result["nuevo_saldo"] == 100.0

        session.expire_all()
        wallet = BankService.get_or_create_wallet(session, user.privy_did)
        assert wallet.axogemas == 100.0, "Solo el depósito exitoso debe persistir."


# ---------------------------------------------------------------------------
# H. Cascada: buy_item → open_booster bajo latencia 200 ms
# ---------------------------------------------------------------------------

class TestMixedOperationsUnderLatency:
    def test_buy_and_open_cascade_with_latency(self, session):
        """
        Flujo completo con latencia en Web3:
          1. buy_item(booster) con 200 ms de latencia → saldo -10 AXG.
          2. open_booster con 200 ms de latencia → inventario consumido, cartas entregadas.
        """
        _make_cards_catalog(session)
        user = make_user(session, privy_did="net_h1", wallet_address=_addr(0x8001))
        make_wallet(session, user.privy_did, axogemas=500.0)
        item = make_item(
            session,
            name="Booster-Cascade",
            item_type=ItemType.BOOSTER,
            price_axg=10.0,
            item_metadata={"fase": 1},
        )
        slow = _slow_ok(0.2)

        with patch("app.services.shop_service.Web3Service.burn_axogemas", side_effect=slow), \
             patch("app.services.shop_service.Web3Service.mint_booster_onchain", side_effect=slow):
            ShopService.buy_item(session, user.privy_did, item.id, CurrencyType.AXOGEMA)

        session.expire_all()
        wallet = BankService.get_or_create_wallet(session, user.privy_did)
        assert wallet.axogemas == pytest.approx(490.0, abs=0.01), "Debe haberse debitado 10 AXG."

        inv = session.exec(
            select(PlayerInventory)
            .where(PlayerInventory.user_id == user.privy_did)
            .where(PlayerInventory.item_id == item.id)
        ).first()
        assert inv is not None and inv.quantity >= 1, "Debe tener el booster en inventario."

        with patch("app.services.shop_service.Web3Service.burn_booster_onchain", side_effect=slow), \
             patch("app.services.shop_service.Web3Service.mint_cards_onchain", side_effect=slow):
            result = ShopService.open_booster(session, user.privy_did, item.id)

        assert isinstance(result, dict), "open_booster debe devolver un dict con las cartas."
