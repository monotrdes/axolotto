from __future__ import annotations
import pytest
from pydantic import ValidationError
from sqlmodel import Session
from sqlalchemy.exc import IntegrityError
from fastapi.testclient import TestClient

from app.main import app
from app.models.economy import Wallet
from app.api.v1.endpoints.checkout import ConfirmPaymentRequest

def test_wallet_negative_balances_rejected(session: Session):
    # Intentar guardar una cartera con saldo negativo de gemas_alga
    w1 = Wallet(user_id="did:privy:user_hardening_1", gemas_alga=-5.0, axogemas=10.0)
    session.add(w1)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()

    # Intentar guardar una cartera con saldo negativo de axogemas
    w2 = Wallet(user_id="did:privy:user_hardening_2", gemas_alga=10.0, axogemas=-1.0)
    session.add(w2)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()

def test_tx_hash_pydantic_validation():
    # Hash válido de 64 caracteres hex
    valid_hash = "0x" + "a" * 64
    req = ConfirmPaymentRequest(tx_hash=valid_hash)
    assert req.tx_hash == valid_hash

    # Hash mock válido
    mock_hash = "0x_mock_12345"
    req_mock = ConfirmPaymentRequest(tx_hash=mock_hash)
    assert req_mock.tx_hash == mock_hash

    # Hashes inválidos (longitud incorrecta, no hex, etc.)
    invalid_hashes = [
        "0x" + "a" * 63,
        "0x" + "a" * 65,
        "0x" + "g" * 64,
        "invalid_format",
        "",
    ]
    for h in invalid_hashes:
        with pytest.raises(ValidationError):
            ConfirmPaymentRequest(tx_hash=h)

def test_rate_limiting_checkout_confirm(session):
    from app.core.auth import get_verified_user_id
    from app.database import get_session
    
    app.dependency_overrides[get_verified_user_id] = lambda: "did:privy:user_hardening_3"
    app.dependency_overrides[get_session] = lambda: session
    
    try:
        client = TestClient(app)
        responses = []
        # Hacer suficientes peticiones para exceder el límite de 5/minuto
        for _ in range(10):
            res = client.post(
                "/api/v1/bank/checkout/crypto/some-order-id/confirm",
                json={"tx_hash": "0x" + "b" * 64}
            )
            responses.append(res.status_code)
        
        # 429 indica que el rate limit de SlowAPI fue excedido y respondió adecuadamente
        assert 429 in responses
    finally:
        app.dependency_overrides.clear()

def test_rate_limiting_checkout_create(session):
    from app.core.auth import get_verified_user_id
    from app.database import get_session
    
    app.dependency_overrides[get_verified_user_id] = lambda: "did:privy:user_hardening_4"
    app.dependency_overrides[get_session] = lambda: session
    
    try:
        client = TestClient(app)
        responses = []
        # Hacer suficientes peticiones para exceder el límite de 10/minuto
        for _ in range(15):
            res = client.post(
                "/api/v1/bank/checkout/crypto",
                json={"pack_id": "pack_100"}
            )
            responses.append(res.status_code)
        
        assert 429 in responses
    finally:
        app.dependency_overrides.clear()

def test_rate_limiting_bank_transfer(session):
    from app.core.auth import get_verified_user_id
    from app.database import get_session
    
    app.dependency_overrides[get_verified_user_id] = lambda: "did:privy:user_hardening_5"
    app.dependency_overrides[get_session] = lambda: session
    
    try:
        client = TestClient(app)
        responses = []
        # Hacer suficientes peticiones para exceder el límite de 5/minuto
        for _ in range(10):
            res = client.post(
                "/api/v1/bank/transfer",
                json={
                    "sender_id": "did:privy:user_hardening_5",
                    "receiver_id": "did:privy:other_user",
                    "amount": 10.0,
                    "currency": "frijolito"
                }
            )
            responses.append(res.status_code)
        
        assert 429 in responses
    finally:
        app.dependency_overrides.clear()

def test_rate_limiting_rewards_claim(session):
    from app.core.auth import get_verified_user_id
    from app.database import get_session
    
    app.dependency_overrides[get_verified_user_id] = lambda: "did:privy:user_hardening_6"
    app.dependency_overrides[get_session] = lambda: session
    
    try:
        client = TestClient(app)
        responses = []
        # Hacer suficientes peticiones para exceder el límite de 5/minuto
        for _ in range(10):
            res = client.post(
                "/api/v1/rewards/claim"
            )
            responses.append(res.status_code)
        
        assert 429 in responses
    finally:
        app.dependency_overrides.clear()

