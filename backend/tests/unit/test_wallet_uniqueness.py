"""
test_wallet_uniqueness.py — Suite §4.6: Inflado de Jackpot vía wallet duplicada.

Escenarios cubiertos:
  A. Registro nuevo con wallet ya tomada → 409.
  B. Usuario existente que intenta cambiar su wallet verificada → 403.
  C. Usuario existente que configura wallet por primera vez → OK.
  D. Wallet ya tomada al intentar asignarla a un segundo usuario → 409.
  E. Idempotencia: enviar la misma wallet que ya está registrada no lanza error.
  F. Dos usuarios con wallet=None se registran sin conflicto.
"""
import pytest
from sqlmodel import Session, select
from fastapi import HTTPException

from starlette.requests import Request
from app.models.user import User
from app.api.v1.endpoints.user import sync_user, SyncUserRequest


# ---------------------------------------------------------------------------
# Helper — simula la lógica de sync_user sin el stack HTTP completo
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def disable_limiter():
    from app.core.limiter import limiter
    old_enabled = limiter.enabled
    limiter.enabled = False
    yield
    limiter.enabled = old_enabled

def _sync(session: Session, privy_did: str, wallet_address=None, email=None):
    """Llama a sync_user con un request construido; levanta HTTPException si hay error."""
    req = SyncUserRequest(privy_did=privy_did, email=email, wallet_address=wallet_address)

    # Construir un Request dummy para slowapi
    scope = {
        "type": "http",
        "method": "POST",
        "path": "/api/v1/user/sync",
        "headers": [],
    }
    request = Request(scope=scope)

    # Llamamos la función directamente pasando los parámetros como kwargs
    return sync_user(request=request, req=req, session=session, verified_user_id=privy_did)


# ---------------------------------------------------------------------------
# A. Registro nuevo con wallet ya tomada → 409
# ---------------------------------------------------------------------------

def test_nueva_cuenta_wallet_duplicada_rechazada(session):
    """El sistema rechaza registrar una nueva cuenta con una wallet ya en uso."""
    _sync(session, privy_did="user_original", wallet_address="0xAAA")

    with pytest.raises(HTTPException) as exc:
        _sync(session, privy_did="user_atacante", wallet_address="0xAAA")

    assert exc.value.status_code == 409
    assert "otra cuenta" in exc.value.detail


# ---------------------------------------------------------------------------
# B. Usuario existente cambia wallet verificada → 403
# ---------------------------------------------------------------------------

def test_cambio_de_wallet_bloqueado(session):
    """Un usuario con wallet ya verificada no puede cambiarla (re-KYC requerido)."""
    _sync(session, privy_did="user_kyc", wallet_address="0xBBB")

    with pytest.raises(HTTPException) as exc:
        _sync(session, privy_did="user_kyc", wallet_address="0xCCC")

    assert exc.value.status_code == 403
    assert "soporte" in exc.value.detail.lower() or "verificada" in exc.value.detail.lower()


# ---------------------------------------------------------------------------
# C. Primer registro de wallet (usuario sin wallet previa) → OK
# ---------------------------------------------------------------------------

def test_primera_asignacion_de_wallet_ok(session):
    """Un usuario que se registró sin wallet puede asignar una por primera vez."""
    _sync(session, privy_did="user_sin_wallet")
    result = _sync(session, privy_did="user_sin_wallet", wallet_address="0xDDD")

    user = session.exec(select(User).where(User.privy_did == "user_sin_wallet")).first()
    assert user.wallet_address == "0xDDD"
    assert "actualizado" in result["mensaje"].lower() or "bienvenido" in result["mensaje"].lower()


# ---------------------------------------------------------------------------
# D. Wallet tomada al asignarla a segundo usuario → 409
# ---------------------------------------------------------------------------

def test_asignacion_wallet_tomada_a_segundo_usuario(session):
    """Si usuario A ya tiene la wallet 0xEEE, usuario B (sin wallet) no puede reclamarla."""
    _sync(session, privy_did="user_a", wallet_address="0xEEE")
    _sync(session, privy_did="user_b")  # se registra sin wallet

    with pytest.raises(HTTPException) as exc:
        _sync(session, privy_did="user_b", wallet_address="0xEEE")

    assert exc.value.status_code == 409


# ---------------------------------------------------------------------------
# E. Idempotencia: re-enviar la misma wallet ya registrada → OK
# ---------------------------------------------------------------------------

def test_idempotencia_misma_wallet(session):
    """Enviar la misma wallet en sucesivas llamadas /sync es idempotente."""
    _sync(session, privy_did="user_idempotente", wallet_address="0xFFF")
    # Segunda llamada con la misma wallet no debe lanzar error
    result = _sync(session, privy_did="user_idempotente", wallet_address="0xFFF")
    assert result is not None


# ---------------------------------------------------------------------------
# F. Múltiples cuentas sin wallet no generan conflicto
# ---------------------------------------------------------------------------

def test_multiples_usuarios_sin_wallet_no_conflictan(session):
    """wallet_address=None no debe considerarse duplicada entre usuarios."""
    _sync(session, privy_did="user_nwallet_1")
    _sync(session, privy_did="user_nwallet_2")
    _sync(session, privy_did="user_nwallet_3")

    for did in ["user_nwallet_1", "user_nwallet_2", "user_nwallet_3"]:
        user = session.exec(select(User).where(User.privy_did == did)).first()
        assert user is not None
        assert user.wallet_address is None
