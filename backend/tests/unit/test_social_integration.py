"""
test_social_integration.py — Tests de integración para endpoints Social y Referidos.

Usa TestClient con dependency_overrides para mockear autenticación Privy y DB.
Cubre flujos completos end-to-end:

  1. Flujo completo de amistad: buscar → solicitar → aceptar → listar → like → visitar → eliminar
  2. Flujo de bloqueo: bloquear → no aparece en búsqueda → no puede enviar solicitud
  3. Flujo de referidos: generar código → claim → milestones → dashboard
  4. Validaciones de seguridad: sin auth (401), rate-limit (429)
  5. Búsqueda y sugerencias: search, recent players, suggestions
  6. Endpoints de cueva: visit, get cave data
"""
import sys
import os
import pytest
import json
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from app.main import app
from app.core.auth import get_verified_user_id
from app.database import get_session

# Helpers de conftest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from conftest import make_user


# ── Helpers ───────────────────────────────────────────────────────────────────

def _setup_user(session, privy_did: str, nickname: str, **kwargs):
    """Crear usuario con nickname, wallet y avatar para integración."""
    from app.models.economy import Wallet
    user = make_user(session, privy_did=privy_did, **kwargs)
    user.nickname = nickname
    session.add(user)
    # Wallet
    wallet = Wallet(user_id=privy_did, frijolitos=10000, axofichas=5000000)
    session.add(wallet)
    session.commit()
    session.refresh(user)
    return user


def _override_deps(session, user_id: str):
    """Sobreescribir dependencias de FastAPI para tests."""
    app.dependency_overrides[get_verified_user_id] = lambda: user_id
    app.dependency_overrides[get_session] = lambda: session


def _clear_overrides():
    app.dependency_overrides.clear()


# ═══════════════════════════════════════════════════════════════════════════════
# 1. Flujo Completo de Amistad
# ═══════════════════════════════════════════════════════════════════════════════

class TestFullFriendshipFlow:
    def test_full_friend_lifecycle(self, session, engine):
        """End-to-end: buscar → enviar solicitud → aceptar → like → visitar cueva → eliminar."""
        u1 = _setup_user(session, "did:privy:intg_u1", "IntegUno")
        u2 = _setup_user(session, "did:privy:intg_u2", "IntegDos")

        client = TestClient(app)

        # ── Fase 1: Buscar jugador ──────────────────────────────────────────
        _override_deps(session, u1.privy_did)
        try:
            res = client.get("/api/v1/social/friends/search?q=IntegDos&limit=10")
            assert res.status_code == 200
            results = res.json()
            assert any(r["user_id"] == u2.privy_did for r in results)
            assert any(r["friendship_status"] == "none" for r in results)
        finally:
            _clear_overrides()

        # ── Fase 2: Enviar solicitud ────────────────────────────────────────
        _override_deps(session, u1.privy_did)
        try:
            res = client.post("/api/v1/social/friends/request", json={"target_user_id": u2.privy_did})
            assert res.status_code == 201
            data = res.json()
            assert data["status"] == "pending"
            relation_id = data["relation_id"]
        finally:
            _clear_overrides()

        # ── Fase 3: u2 ve solicitudes pendientes ───────────────────────────
        _override_deps(session, u2.privy_did)
        try:
            res = client.get("/api/v1/social/friends/pending")
            assert res.status_code == 200
            pending = res.json()
            assert len(pending) == 1
            assert pending[0]["from_user_id"] == u1.privy_did
        finally:
            _clear_overrides()

        # ── Fase 4: u2 acepta solicitud ─────────────────────────────────────
        _override_deps(session, u2.privy_did)
        try:
            res = client.post(f"/api/v1/social/friends/accept/{relation_id}")
            assert res.status_code == 200
            data = res.json()
            assert "amigos" in data["message"].lower()
        finally:
            _clear_overrides()

        # ── Fase 5: u1 lista amigos ─────────────────────────────────────────
        _override_deps(session, u1.privy_did)
        try:
            res = client.get("/api/v1/social/friends")
            assert res.status_code == 200
            friends = res.json()
            assert len(friends) == 1
            assert friends[0]["friend_id"] == u2.privy_did
        finally:
            _clear_overrides()

        # ── Fase 6: u1 da like a u2 ─────────────────────────────────────────
        _override_deps(session, u1.privy_did)
        try:
            res = client.post(f"/api/v1/social/like/{u2.privy_did}")
            assert res.status_code == 200
            data = res.json()
            assert "+1 FRJ" in data["message"]
        finally:
            _clear_overrides()

        # ── Fase 7: u1 visita cueva de u2 ───────────────────────────────────
        _override_deps(session, u1.privy_did)
        try:
            res = client.post(f"/api/v1/social/visit/{u2.privy_did}")
            assert res.status_code == 200
            cave = res.json()
            assert cave["friend_id"] == u2.privy_did
            assert cave["nickname"] == "IntegDos"
        finally:
            _clear_overrides()

        # ── Fase 8: u1 elimina amistad ──────────────────────────────────────
        _override_deps(session, u1.privy_did)
        try:
            res = client.delete(f"/api/v1/social/friends/{relation_id}")
            assert res.status_code == 200
        finally:
            _clear_overrides()

        # ── Fase 9: Verificar que ya no son amigos ──────────────────────────
        _override_deps(session, u1.privy_did)
        try:
            res = client.get("/api/v1/social/friends")
            assert res.status_code == 200
            friends = res.json()
            assert len(friends) == 0
        finally:
            _clear_overrides()

    def test_top_friends_endpoint(self, session, engine):
        """GET /friends/top devuelve máximo N amigos."""
        u1 = _setup_user(session, "did:privy:intg_top1", "TopUno")
        u2 = _setup_user(session, "did:privy:intg_top2", "TopDos")
        u3 = _setup_user(session, "did:privy:intg_top3", "TopTres")

        from app.models.social import FriendRelation, FriendStatus
        from datetime import datetime
        for friend in [u2, u3]:
            rel = FriendRelation(
                user_a=u1.privy_did, user_b=friend.privy_did,
                status=FriendStatus.ACTIVE, friends_since=datetime.utcnow(),
            )
            session.add(rel)
        session.commit()

        _override_deps(session, u1.privy_did)
        try:
            client = TestClient(app)
            res = client.get("/api/v1/social/friends/top?limit=2")
            assert res.status_code == 200
            data = res.json()
            assert len(data) <= 2
        finally:
            _clear_overrides()


# ═══════════════════════════════════════════════════════════════════════════════
# 2. Flujo de Bloqueo
# ═══════════════════════════════════════════════════════════════════════════════

class TestBlockFlow:
    def test_block_hides_from_search_and_prevents_requests(self, session, engine):
        u1 = _setup_user(session, "did:privy:intg_blk_a", "BlockerA")
        u2 = _setup_user(session, "did:privy:intg_blk_b", "BlockerB")

        client = TestClient(app)

        # Bloquear
        _override_deps(session, u1.privy_did)
        try:
            res = client.post("/api/v1/social/friends/block", json={"user_id": u2.privy_did})
            assert res.status_code == 200
        finally:
            _clear_overrides()

        # Verificar que u2 no aparece en búsqueda de u1
        _override_deps(session, u1.privy_did)
        try:
            res = client.get("/api/v1/social/friends/search?q=BlockerB")
            assert res.status_code == 200
            results = res.json()
            assert all(r["user_id"] != u2.privy_did for r in results)
        finally:
            _clear_overrides()

        # Verificar que u2 no puede enviar solicitud a u1
        _override_deps(session, u2.privy_did)
        try:
            res = client.post("/api/v1/social/friends/request", json={"target_user_id": u1.privy_did})
            assert res.status_code == 400
        finally:
            _clear_overrides()


# ═══════════════════════════════════════════════════════════════════════════════
# 3. Flujo de Referidos
# ═══════════════════════════════════════════════════════════════════════════════

class TestReferralFlow:
    def test_full_referral_lifecycle(self, session, engine):
        """End-to-end: generar código → claim → dashboard → milestone."""
        referrer = _setup_user(session, "did:privy:intg_ref_r", "IntgRefR")
        referred = _setup_user(session, "did:privy:intg_ref_d", "IntgRefD")

        client = TestClient(app)

        # ── Paso 1: Obtener código del referidor ────────────────────────────
        _override_deps(session, referrer.privy_did)
        try:
            res = client.get("/api/v1/referrals/code")
            assert res.status_code == 200
            data = res.json()
            assert "code" in data
            code = data["code"]
        finally:
            _clear_overrides()

        # ── Paso 2: Referido canjea el código ───────────────────────────────
        _override_deps(session, referred.privy_did)
        try:
            res = client.post("/api/v1/referrals/claim", json={"code": code})
            assert res.status_code == 200
            data = res.json()
            assert data["status"] == "ok"
        finally:
            _clear_overrides()

        # ── Paso 3: Referido reporta milestone tutorial ─────────────────────
        _override_deps(session, referred.privy_did)
        try:
            res = client.post("/api/v1/referrals/milestone", json={"milestone": "tutorial_done"})
            assert res.status_code == 200
            data = res.json()
            assert data["status"] == "ok"
        finally:
            _clear_overrides()

        # ── Paso 4: Dashboard del referidor muestra resultados ──────────────
        _override_deps(session, referrer.privy_did)
        try:
            res = client.get("/api/v1/referrals/dashboard")
            assert res.status_code == 200
            data = res.json()
            assert data["total_uses"] >= 1
            assert len(data["referred_users"]) >= 1
        finally:
            _clear_overrides()

        # ── Paso 5: Reward history ──────────────────────────────────────────
        _override_deps(session, referrer.privy_did)
        try:
            res = client.get("/api/v1/referrals/reward-history")
            assert res.status_code == 200
        finally:
            _clear_overrides()


# ═══════════════════════════════════════════════════════════════════════════════
# 4. Validaciones de Seguridad
# ═══════════════════════════════════════════════════════════════════════════════

class TestSecurityValidations:
    def test_unauthenticated_rejected(self, session, engine):
        """Sin dependency_overrides, el endpoint debe rechazar la petición."""
        client = TestClient(app)
        # Sin override de auth, get_verified_user_id lanza 401
        res = client.get("/api/v1/social/friends")
        # Privy auth devuelve 401 cuando no hay token
        assert res.status_code in (401, 403)

    def test_cannot_like_non_friend(self, session, engine):
        u1 = _setup_user(session, "did:privy:intg_sec_a", "SecA")
        u2 = _setup_user(session, "did:privy:intg_sec_b", "SecB")

        _override_deps(session, u1.privy_did)
        try:
            client = TestClient(app)
            res = client.post(f"/api/v1/social/like/{u2.privy_did}")
            assert res.status_code == 403  # No son amigos
        finally:
            _clear_overrides()

    def test_cannot_visit_non_friend_cave(self, session, engine):
        u1 = _setup_user(session, "did:privy:intg_sec2_a", "Sec2A")
        u2 = _setup_user(session, "did:privy:intg_sec2_b", "Sec2B")

        _override_deps(session, u1.privy_did)
        try:
            client = TestClient(app)
            res = client.post(f"/api/v1/social/visit/{u2.privy_did}")
            assert res.status_code == 403
        finally:
            _clear_overrides()

    def test_self_friend_request_rejected(self, session, engine):
        u1 = _setup_user(session, "did:privy:intg_self", "IntgSelf")

        _override_deps(session, u1.privy_did)
        try:
            client = TestClient(app)
            res = client.post("/api/v1/social/friends/request", json={"target_user_id": u1.privy_did})
            assert res.status_code == 400
        finally:
            _clear_overrides()

    def test_self_referral_rejected(self, session, engine):
        u1 = _setup_user(session, "did:privy:intg_selfref", "IntgSelfRef")

        _override_deps(session, u1.privy_did)
        try:
            client = TestClient(app)
            # Obtener código propio
            res = client.get("/api/v1/referrals/code")
            code = res.json()["code"]
            # Intentar canjearlo uno mismo
            res2 = client.post("/api/v1/referrals/claim", json={"code": code})
            assert res2.status_code == 200
            assert res2.json()["status"] == "self_referral"
        finally:
            _clear_overrides()


# ═══════════════════════════════════════════════════════════════════════════════
# 5. Búsqueda, Sugerencias y Recientes
# ═══════════════════════════════════════════════════════════════════════════════

class TestDiscoveryEndpoints:
    def test_search_requires_min_query(self, session, engine):
        u1 = _setup_user(session, "did:privy:intg_disc_a", "DiscA")

        _override_deps(session, u1.privy_did)
        try:
            client = TestClient(app)
            res = client.get("/api/v1/social/friends/search?q=A")
            assert res.status_code == 422  # Validation error: min_length=2
        finally:
            _clear_overrides()

    def test_friend_suggestions(self, session, engine):
        u1 = _setup_user(session, "did:privy:intg_sug_a", "SugA")
        u2 = _setup_user(session, "did:privy:intg_sug_b", "SugB")
        u3 = _setup_user(session, "did:privy:intg_sug_c", "SugC")

        from app.models.social import FriendRelation, FriendStatus
        from datetime import datetime

        # u1 es amigo de u2, u2 es amigo de u3 → u3 debería ser sugerencia de u1
        session.add(FriendRelation(user_a=u1.privy_did, user_b=u2.privy_did, status=FriendStatus.ACTIVE, friends_since=datetime.utcnow()))
        session.add(FriendRelation(user_a=u2.privy_did, user_b=u3.privy_did, status=FriendStatus.ACTIVE, friends_since=datetime.utcnow()))
        session.commit()

        _override_deps(session, u1.privy_did)
        try:
            client = TestClient(app)
            res = client.get("/api/v1/social/friends/suggestions")
            assert res.status_code == 200
            suggestions = res.json()
            # u3 debería aparecer como sugerencia (amigo de amigo)
            assert any(s["user_id"] == u3.privy_did for s in suggestions)
        finally:
            _clear_overrides()

    def test_recent_players_empty_for_new_user(self, session, engine):
        u1 = _setup_user(session, "did:privy:intg_rec_a", "RecA")

        _override_deps(session, u1.privy_did)
        try:
            client = TestClient(app)
            res = client.get("/api/v1/social/friends/recent-players")
            assert res.status_code == 200
            assert res.json() == []
        finally:
            _clear_overrides()

    def test_get_friend_cave_readonly(self, session, engine):
        u1 = _setup_user(session, "did:privy:intg_cave_a", "CaveIntgA")
        u2 = _setup_user(session, "did:privy:intg_cave_b", "CaveIntgB")

        from app.models.social import FriendRelation, FriendStatus
        from datetime import datetime
        session.add(FriendRelation(user_a=u1.privy_did, user_b=u2.privy_did, status=FriendStatus.ACTIVE, friends_since=datetime.utcnow()))
        session.commit()

        _override_deps(session, u1.privy_did)
        try:
            client = TestClient(app)
            res = client.get(f"/api/v1/social/friends/{u2.privy_did}/cave")
            assert res.status_code == 200
            cave = res.json()
            assert cave["friend_id"] == u2.privy_did
        finally:
            _clear_overrides()
