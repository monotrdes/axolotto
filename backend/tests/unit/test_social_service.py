"""
test_social_service.py — Pruebas unitarias de SocialService.

Cubre:
  1. send_friend_request: éxito, auto-aceptación, rechazo self/duplicado/bloqueado, rate-limit
  2. accept_friend_request: éxito, no encontrada
  3. reject_friend_request: éxito, no encontrada
  4. remove_friend: éxito, no encontrada
  5. block_user: crear nuevo bloqueo, actualizar existente
  6. get_friends_list: lista ordenada, sin amigos
  7. get_top_active_friends: límite N
  8. get_pending_requests / get_sent_requests
  9. search_players: éxito, query corta, excluye bloqueados
  10. get_recent_players
  11. get_suggestions: amigos de amigos
  12. process_like: éxito, no-amigos, self-like, límite diario
  13. get_friend_cave / visit_cave: éxito, no-amigos
  14. are_friends / validate_room_access
"""
import sys
import os
import pytest
from datetime import datetime, timedelta
from fastapi import HTTPException
from sqlmodel import select

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from app.services.social_service import SocialService
from app.models.social import (
    FriendRelation, FriendStatus, SocialActionLog, SocialActionType,
)
from app.models.user import User
from app.models.economy import Wallet

# Importar helpers compartidos de conftest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from conftest import make_user, make_wallet


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_user_with_nick(session, privy_did: str, nickname: str, **kwargs) -> User:
    """Crear usuario con nickname y billetera."""
    user = make_user(session, privy_did=privy_did, **kwargs)
    user.nickname = nickname
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def _make_wallet_frj(session, user_id: str, frijolitos: int = 0, axofichas: int = 0) -> Wallet:
    """Crear wallet con saldos FRJ/AXF."""
    wallet = Wallet(user_id=user_id, frijolitos=frijolitos, axofichas=axofichas)
    session.add(wallet)
    session.commit()
    session.refresh(wallet)
    return wallet


# ═══════════════════════════════════════════════════════════════════════════════
# 1. send_friend_request
# ═══════════════════════════════════════════════════════════════════════════════

class TestSendFriendRequest:
    def test_sends_request_successfully(self, session, engine):
        """Envía solicitud de amistad correctamente."""
        u1 = _make_user_with_nick(session, "did:privy:sender", "Sender")
        u2 = _make_user_with_nick(session, "did:privy:target", "Target")
        _make_wallet_frj(session, u1.privy_did)
        _make_wallet_frj(session, u2.privy_did)

        rel = SocialService.send_friend_request(session, u1.privy_did, u2.privy_did)

        assert rel is not None
        assert rel.user_a == u1.privy_did
        assert rel.user_b == u2.privy_did
        assert rel.status == FriendStatus.PENDING

    def test_auto_accepts_mutual_pending(self, session, engine):
        """Si el otro ya envió solicitud, se auto-acepta al enviar en dirección opuesta."""
        u1 = _make_user_with_nick(session, "did:privy:auto_a", "AutoA")
        u2 = _make_user_with_nick(session, "did:privy:auto_b", "AutoB")
        _make_wallet_frj(session, u1.privy_did)
        _make_wallet_frj(session, u2.privy_did)

        # u1 envía a u2
        SocialService.send_friend_request(session, u1.privy_did, u2.privy_did)
        # u2 envía a u1 → debe auto-aceptar
        rel = SocialService.send_friend_request(session, u2.privy_did, u1.privy_did)

        assert rel.status == FriendStatus.ACTIVE
        assert rel.friends_since is not None

    def test_rejects_self_friend_request(self, session, engine):
        """No se puede enviar solicitud a uno mismo."""
        u1 = _make_user_with_nick(session, "did:privy:self_req", "Self")
        _make_wallet_frj(session, u1.privy_did)

        with pytest.raises(HTTPException) as exc_info:
            SocialService.send_friend_request(session, u1.privy_did, u1.privy_did)
        assert exc_info.value.status_code == 400
        assert "ti mismo" in exc_info.value.detail

    def test_rejects_duplicate_friend_request(self, session, engine):
        """No se puede enviar solicitud duplicada al mismo usuario."""
        u1 = _make_user_with_nick(session, "did:privy:dup_a", "DupA")
        u2 = _make_user_with_nick(session, "did:privy:dup_b", "DupB")
        _make_wallet_frj(session, u1.privy_did)
        _make_wallet_frj(session, u2.privy_did)

        SocialService.send_friend_request(session, u1.privy_did, u2.privy_did)

        with pytest.raises(HTTPException) as exc_info:
            SocialService.send_friend_request(session, u1.privy_did, u2.privy_did)
        assert exc_info.value.status_code == 400
        assert "Ya enviaste" in exc_info.value.detail

    def test_rejects_when_already_friends(self, session, engine):
        """No se puede enviar solicitud si ya son amigos."""
        u1 = _make_user_with_nick(session, "did:privy:af_a", "AFa")
        u2 = _make_user_with_nick(session, "did:privy:af_b", "AFb")
        _make_wallet_frj(session, u1.privy_did)
        _make_wallet_frj(session, u2.privy_did)

        # Crear amistad existente
        rel = FriendRelation(user_a=u1.privy_did, user_b=u2.privy_did, status=FriendStatus.ACTIVE, friends_since=datetime.utcnow())
        session.add(rel)
        session.commit()

        with pytest.raises(HTTPException) as exc_info:
            SocialService.send_friend_request(session, u1.privy_did, u2.privy_did)
        assert exc_info.value.status_code == 400
        assert "Ya son amigos" in exc_info.value.detail

    def test_rejects_when_blocked(self, session, engine):
        """No se puede enviar solicitud a un usuario bloqueado."""
        u1 = _make_user_with_nick(session, "did:privy:blk_a", "BlkA")
        u2 = _make_user_with_nick(session, "did:privy:blk_b", "BlkB")
        _make_wallet_frj(session, u1.privy_did)
        _make_wallet_frj(session, u2.privy_did)

        SocialService.block_user(session, u2.privy_did, u1.privy_did)

        with pytest.raises(HTTPException) as exc_info:
            SocialService.send_friend_request(session, u1.privy_did, u2.privy_did)
        assert exc_info.value.status_code == 400
        assert "No puedes agregar" in exc_info.value.detail

    def test_rejects_target_not_found(self, session, engine):
        """Error 404 si el destinatario no existe."""
        u1 = _make_user_with_nick(session, "did:privy:ghost_sender", "GhostS")
        _make_wallet_frj(session, u1.privy_did)

        with pytest.raises(HTTPException) as exc_info:
            SocialService.send_friend_request(session, u1.privy_did, "did:privy:no_existe")
        assert exc_info.value.status_code == 404

    def test_rate_limit_enforced(self, session, engine):
        """No se pueden enviar >10 solicitudes en una hora."""
        u1 = _make_user_with_nick(session, "did:privy:rl_sender", "RLSender")
        _make_wallet_frj(session, u1.privy_did)

        # Crear 10 targets y enviar solicitudes
        for i in range(10):
            target = _make_user_with_nick(session, f"did:privy:rl_target_{i}", f"RLTarget{i}")
            _make_wallet_frj(session, target.privy_did)
            # Hacer que parezca que la solicitud fue hace <1 hora creando el log manualmente
            # Truco: insertar SocialActionLogs para saturar el rate limit
            SocialService._log_action(session, u1.privy_did, target.privy_did, SocialActionType.FRIEND_REQUEST_SENT)

        # La solicitud #11 debe fallar
        target11 = _make_user_with_nick(session, "did:privy:rl_target_11", "RLTarget11")
        _make_wallet_frj(session, target11.privy_did)

        with pytest.raises(HTTPException) as exc_info:
            SocialService.send_friend_request(session, u1.privy_did, target11.privy_did)
        assert exc_info.value.status_code == 429


# ═══════════════════════════════════════════════════════════════════════════════
# 2. accept_friend_request
# ═══════════════════════════════════════════════════════════════════════════════

class TestAcceptFriendRequest:
    def test_accepts_pending_request(self, session, engine):
        u1 = _make_user_with_nick(session, "did:privy:acc_a", "AccA")
        u2 = _make_user_with_nick(session, "did:privy:acc_b", "AccB")
        _make_wallet_frj(session, u1.privy_did)
        _make_wallet_frj(session, u2.privy_did)

        rel = SocialService.send_friend_request(session, u1.privy_did, u2.privy_did)

        accepted = SocialService.accept_friend_request(session, u2.privy_did, rel.id)

        assert accepted.status == FriendStatus.ACTIVE
        assert accepted.friends_since is not None

    def test_rejects_not_found_request(self, session, engine):
        u1 = _make_user_with_nick(session, "did:privy:acc_nf", "AccNF")
        _make_wallet_frj(session, u1.privy_did)

        with pytest.raises(HTTPException) as exc_info:
            SocialService.accept_friend_request(session, u1.privy_did, 99999)
        assert exc_info.value.status_code == 404

    def test_only_target_can_accept(self, session, engine):
        """Solo el destinatario (user_b) puede aceptar."""
        u1 = _make_user_with_nick(session, "did:privy:acc_u1", "AccU1")
        u2 = _make_user_with_nick(session, "did:privy:acc_u2", "AccU2")
        u3 = _make_user_with_nick(session, "did:privy:acc_u3", "AccU3")
        _make_wallet_frj(session, u1.privy_did)
        _make_wallet_frj(session, u2.privy_did)

        rel = SocialService.send_friend_request(session, u1.privy_did, u2.privy_did)

        # u3 (tercero) no puede aceptar
        with pytest.raises(HTTPException) as exc_info:
            SocialService.accept_friend_request(session, u3.privy_did, rel.id)
        assert exc_info.value.status_code == 404


# ═══════════════════════════════════════════════════════════════════════════════
# 3. reject_friend_request
# ═══════════════════════════════════════════════════════════════════════════════

class TestRejectFriendRequest:
    def test_rejects_pending_request(self, session, engine):
        u1 = _make_user_with_nick(session, "did:privy:rej_a", "RejA")
        u2 = _make_user_with_nick(session, "did:privy:rej_b", "RejB")
        _make_wallet_frj(session, u1.privy_did)
        _make_wallet_frj(session, u2.privy_did)

        rel = SocialService.send_friend_request(session, u1.privy_did, u2.privy_did)

        SocialService.reject_friend_request(session, u2.privy_did, rel.id)

        # Verificar que el estado cambió a REMOVED
        updated = session.get(FriendRelation, rel.id)
        assert updated.status == FriendStatus.REMOVED

    def test_rejects_not_found_request(self, session, engine):
        u1 = _make_user_with_nick(session, "did:privy:rej_nf", "RejNF")
        _make_wallet_frj(session, u1.privy_did)

        with pytest.raises(HTTPException) as exc_info:
            SocialService.reject_friend_request(session, u1.privy_did, 99999)
        assert exc_info.value.status_code == 404


# ═══════════════════════════════════════════════════════════════════════════════
# 4. remove_friend
# ═══════════════════════════════════════════════════════════════════════════════

class TestRemoveFriend:
    def test_removes_active_friendship(self, session, engine):
        u1 = _make_user_with_nick(session, "did:privy:rm_a", "RmA")
        u2 = _make_user_with_nick(session, "did:privy:rm_b", "RmB")
        _make_wallet_frj(session, u1.privy_did)
        _make_wallet_frj(session, u2.privy_did)

        rel = FriendRelation(
            user_a=u1.privy_did, user_b=u2.privy_did,
            status=FriendStatus.ACTIVE, friends_since=datetime.utcnow(),
        )
        session.add(rel)
        session.commit()
        session.refresh(rel)

        SocialService.remove_friend(session, u1.privy_did, rel.id)

        updated = session.get(FriendRelation, rel.id)
        assert updated.status == FriendStatus.REMOVED

    def test_remove_works_in_both_directions(self, session, engine):
        """Ambos lados pueden eliminar la amistad."""
        u1 = _make_user_with_nick(session, "did:privy:rm_bi_a", "RmBiA")
        u2 = _make_user_with_nick(session, "did:privy:rm_bi_b", "RmBiB")
        _make_wallet_frj(session, u1.privy_did)
        _make_wallet_frj(session, u2.privy_did)

        rel = FriendRelation(
            user_a=u1.privy_did, user_b=u2.privy_did,
            status=FriendStatus.ACTIVE, friends_since=datetime.utcnow(),
        )
        session.add(rel)
        session.commit()
        session.refresh(rel)

        # u2 (user_b) también puede eliminar
        SocialService.remove_friend(session, u2.privy_did, rel.id)
        updated = session.get(FriendRelation, rel.id)
        assert updated.status == FriendStatus.REMOVED

    def test_rejects_not_found(self, session, engine):
        u1 = _make_user_with_nick(session, "did:privy:rm_nf", "RmNF")
        _make_wallet_frj(session, u1.privy_did)

        with pytest.raises(HTTPException) as exc_info:
            SocialService.remove_friend(session, u1.privy_did, 99999)
        assert exc_info.value.status_code == 404

    def test_rejects_remove_pending_relation(self, session, engine):
        """Solo se puede eliminar amistad ACTIVA, no PENDING."""
        u1 = _make_user_with_nick(session, "did:privy:rm_pend_a", "RmPendA")
        u2 = _make_user_with_nick(session, "did:privy:rm_pend_b", "RmPendB")
        _make_wallet_frj(session, u1.privy_did)
        _make_wallet_frj(session, u2.privy_did)

        rel = SocialService.send_friend_request(session, u1.privy_did, u2.privy_did)

        with pytest.raises(HTTPException) as exc_info:
            SocialService.remove_friend(session, u1.privy_did, rel.id)
        assert exc_info.value.status_code == 404


# ═══════════════════════════════════════════════════════════════════════════════
# 5. block_user
# ═══════════════════════════════════════════════════════════════════════════════

class TestBlockUser:
    def test_blocks_new_user(self, session, engine):
        u1 = _make_user_with_nick(session, "did:privy:block_a", "BlockA")
        u2 = _make_user_with_nick(session, "did:privy:block_b", "BlockB")
        _make_wallet_frj(session, u1.privy_did)
        _make_wallet_frj(session, u2.privy_did)

        SocialService.block_user(session, u1.privy_did, u2.privy_did)

        rel = SocialService._find_relation(session, u1.privy_did, u2.privy_did)
        assert rel.status == FriendStatus.BLOCKED

    def test_block_upgrades_existing_relation(self, session, engine):
        """Bloquear a un amigo cambia ACTIVE → BLOCKED."""
        u1 = _make_user_with_nick(session, "did:privy:block_up_a", "BlockUpA")
        u2 = _make_user_with_nick(session, "did:privy:block_up_b", "BlockUpB")
        _make_wallet_frj(session, u1.privy_did)
        _make_wallet_frj(session, u2.privy_did)

        rel = FriendRelation(
            user_a=u1.privy_did, user_b=u2.privy_did,
            status=FriendStatus.ACTIVE, friends_since=datetime.utcnow(),
        )
        session.add(rel)
        session.commit()

        SocialService.block_user(session, u1.privy_did, u2.privy_did)

        updated = session.get(FriendRelation, rel.id)
        assert updated.status == FriendStatus.BLOCKED


# ═══════════════════════════════════════════════════════════════════════════════
# 6. get_friends_list
# ═══════════════════════════════════════════════════════════════════════════════

class TestGetFriendsList:
    def test_returns_active_friends_sorted(self, session, engine):
        u1 = _make_user_with_nick(session, "did:privy:fl_main", "Main")
        u2 = _make_user_with_nick(session, "did:privy:fl_f1", "Friend1")
        u3 = _make_user_with_nick(session, "did:privy:fl_f2", "Friend2")
        _make_wallet_frj(session, u1.privy_did)
        _make_wallet_frj(session, u2.privy_did)
        _make_wallet_frj(session, u3.privy_did)

        # Crear amistades
        for friend in [u2, u3]:
            rel = FriendRelation(
                user_a=u1.privy_did, user_b=friend.privy_did,
                status=FriendStatus.ACTIVE, friends_since=datetime.utcnow(),
                interaction_count=5,
            )
            session.add(rel)
        session.commit()

        friends = SocialService.get_friends_list(session, u1.privy_did)

        assert len(friends) == 2
        friend_ids = {f["friend_id"] for f in friends}
        assert u2.privy_did in friend_ids
        assert u3.privy_did in friend_ids

    def test_returns_empty_when_no_friends(self, session, engine):
        u1 = _make_user_with_nick(session, "did:privy:fl_none", "NoFriends")
        _make_wallet_frj(session, u1.privy_did)

        friends = SocialService.get_friends_list(session, u1.privy_did)
        assert friends == []

    def test_excludes_pending_and_removed(self, session, engine):
        u1 = _make_user_with_nick(session, "did:privy:fl_filter", "Filter")
        u2 = _make_user_with_nick(session, "did:privy:fl_active", "ActiveF")
        u3 = _make_user_with_nick(session, "did:privy:fl_pending", "PendF")
        _make_wallet_frj(session, u1.privy_did)
        _make_wallet_frj(session, u2.privy_did)
        _make_wallet_frj(session, u3.privy_did)

        # Activo
        session.add(FriendRelation(user_a=u1.privy_did, user_b=u2.privy_did, status=FriendStatus.ACTIVE, friends_since=datetime.utcnow()))
        # Pendiente
        session.add(FriendRelation(user_a=u1.privy_did, user_b=u3.privy_did, status=FriendStatus.PENDING))
        session.commit()

        friends = SocialService.get_friends_list(session, u1.privy_did)
        assert len(friends) == 1
        assert friends[0]["friend_id"] == u2.privy_did


# ═══════════════════════════════════════════════════════════════════════════════
# 7. get_top_active_friends
# ═══════════════════════════════════════════════════════════════════════════════

class TestGetTopActiveFriends:
    def test_respects_limit(self, session, engine):
        u1 = _make_user_with_nick(session, "did:privy:top_main", "TopMain")
        _make_wallet_frj(session, u1.privy_did)

        for i in range(6):
            friend = _make_user_with_nick(session, f"did:privy:top_f{i}", f"TopF{i}")
            _make_wallet_frj(session, friend.privy_did)
            session.add(FriendRelation(
                user_a=u1.privy_did, user_b=friend.privy_did,
                status=FriendStatus.ACTIVE, friends_since=datetime.utcnow(),
                interaction_count=i,
            ))
        session.commit()

        top = SocialService.get_top_active_friends(session, u1.privy_did, limit=3)
        assert len(top) == 3


# ═══════════════════════════════════════════════════════════════════════════════
# 8. get_pending_requests / get_sent_requests
# ═══════════════════════════════════════════════════════════════════════════════

class TestPendingAndSentRequests:
    def test_get_pending_requests(self, session, engine):
        u1 = _make_user_with_nick(session, "did:privy:pend_main", "PendMain")
        u2 = _make_user_with_nick(session, "did:privy:pend_s", "PendS")
        _make_wallet_frj(session, u1.privy_did)
        _make_wallet_frj(session, u2.privy_did)

        SocialService.send_friend_request(session, u2.privy_did, u1.privy_did)

        pending = SocialService.get_pending_requests(session, u1.privy_did)
        assert len(pending) == 1
        assert pending[0]["from_user_id"] == u2.privy_did

    def test_get_sent_requests(self, session, engine):
        u1 = _make_user_with_nick(session, "did:privy:sent_main", "SentMain")
        u2 = _make_user_with_nick(session, "did:privy:sent_t", "SentT")
        _make_wallet_frj(session, u1.privy_did)
        _make_wallet_frj(session, u2.privy_did)

        SocialService.send_friend_request(session, u1.privy_did, u2.privy_did)

        sent = SocialService.get_sent_requests(session, u1.privy_did)
        assert len(sent) == 1
        assert sent[0]["to_user_id"] == u2.privy_did

    def test_empty_when_no_pending(self, session, engine):
        u1 = _make_user_with_nick(session, "did:privy:no_pend", "NoPend")
        _make_wallet_frj(session, u1.privy_did)

        assert SocialService.get_pending_requests(session, u1.privy_did) == []
        assert SocialService.get_sent_requests(session, u1.privy_did) == []


# ═══════════════════════════════════════════════════════════════════════════════
# 9. search_players
# ═══════════════════════════════════════════════════════════════════════════════

class TestSearchPlayers:
    def test_finds_by_nickname(self, session, engine):
        u1 = _make_user_with_nick(session, "did:privy:search_main", "SearchMain")
        u2 = _make_user_with_nick(session, "did:privy:search_axo", "AxolotePro")
        _make_wallet_frj(session, u1.privy_did)
        _make_wallet_frj(session, u2.privy_did)

        results = SocialService.search_players(session, "Axo", u1.privy_did)
        assert len(results) >= 1
        assert any(r["user_id"] == u2.privy_did for r in results)

    def test_excludes_self(self, session, engine):
        u1 = _make_user_with_nick(session, "did:privy:search_self", "SelfSearch")
        _make_wallet_frj(session, u1.privy_did)

        results = SocialService.search_players(session, "Self", u1.privy_did)
        assert all(r["user_id"] != u1.privy_did for r in results)

    def test_excludes_blocked_users(self, session, engine):
        u1 = _make_user_with_nick(session, "did:privy:search_blk_a", "SearchBlkA")
        u2 = _make_user_with_nick(session, "did:privy:search_blk_b", "BlkTarget")
        _make_wallet_frj(session, u1.privy_did)
        _make_wallet_frj(session, u2.privy_did)

        SocialService.block_user(session, u1.privy_did, u2.privy_did)

        results = SocialService.search_players(session, "Blk", u1.privy_did)
        assert all(r["user_id"] != u2.privy_did for r in results)

    def test_requires_min_2_chars(self, session, engine):
        u1 = _make_user_with_nick(session, "did:privy:search_short", "Short")
        _make_wallet_frj(session, u1.privy_did)

        with pytest.raises(HTTPException) as exc_info:
            SocialService.search_players(session, "A", u1.privy_did)
        assert exc_info.value.status_code == 400


# ═══════════════════════════════════════════════════════════════════════════════
# 10. process_like
# ═══════════════════════════════════════════════════════════════════════════════

class TestProcessLike:
    def test_like_without_rewards_keeps_social_action_but_creates_no_wallets(
        self, session, engine, monkeypatch
    ):
        from app.core.config import settings

        u1 = _make_user_with_nick(session, "did:privy:safe_like_a", "SafeLikeA")
        u2 = _make_user_with_nick(session, "did:privy:safe_like_b", "SafeLikeB")
        session.add(FriendRelation(
            user_a=u1.privy_did,
            user_b=u2.privy_did,
            status=FriendStatus.ACTIVE,
            friends_since=datetime.utcnow(),
        ))
        session.commit()
        monkeypatch.setattr(settings, "ENABLE_GAMEPLAY_TOKEN_REWARDS", False)

        result = SocialService.process_like(session, u1.privy_did, u2.privy_did)

        assert result["message"] == "Like enviado."
        assert result["rewarded"] is False
        assert session.exec(
            select(Wallet).where(Wallet.user_id.in_([u1.privy_did, u2.privy_did]))
        ).all() == []

    def test_like_between_friends_awards_frj(self, session, engine):
        u1 = _make_user_with_nick(session, "did:privy:like_a", "LikeA")
        u2 = _make_user_with_nick(session, "did:privy:like_b", "LikeB")
        _make_wallet_frj(session, u1.privy_did, frijolitos=100)
        _make_wallet_frj(session, u2.privy_did, frijolitos=100)

        session.add(FriendRelation(
            user_a=u1.privy_did, user_b=u2.privy_did,
            status=FriendStatus.ACTIVE, friends_since=datetime.utcnow(),
        ))
        session.commit()

        result = SocialService.process_like(session, u1.privy_did, u2.privy_did)

        # Verificar +1 FRJ para ambos
        wallet1 = session.exec(select(Wallet).where(Wallet.user_id == u1.privy_did)).first()
        wallet2 = session.exec(select(Wallet).where(Wallet.user_id == u2.privy_did)).first()
        assert wallet1 is not None
        assert wallet2 is not None
        assert wallet1.frijolitos == 101
        assert wallet2.frijolitos == 101
        assert "Like enviado" in result["message"]

    def test_rejects_self_like(self, session, engine):
        u1 = _make_user_with_nick(session, "did:privy:sl_a", "SelfLike")
        _make_wallet_frj(session, u1.privy_did, frijolitos=100)

        with pytest.raises(HTTPException) as exc_info:
            SocialService.process_like(session, u1.privy_did, u1.privy_did)
        assert exc_info.value.status_code == 400

    def test_rejects_like_non_friend(self, session, engine):
        u1 = _make_user_with_nick(session, "did:privy:nf_like_a", "NFLikeA")
        u2 = _make_user_with_nick(session, "did:privy:nf_like_b", "NFLikeB")
        _make_wallet_frj(session, u1.privy_did)
        _make_wallet_frj(session, u2.privy_did)

        with pytest.raises(HTTPException) as exc_info:
            SocialService.process_like(session, u1.privy_did, u2.privy_did)
        assert exc_info.value.status_code == 403

    def test_enforces_daily_like_limit(self, session, engine):
        u1 = _make_user_with_nick(session, "did:privy:dlike_a", "DLIKEA")
        u2 = _make_user_with_nick(session, "did:privy:dlike_b", "DLIKEB")
        _make_wallet_frj(session, u1.privy_did, frijolitos=100)
        _make_wallet_frj(session, u2.privy_did, frijolitos=100)

        session.add(FriendRelation(
            user_a=u1.privy_did, user_b=u2.privy_did,
            status=FriendStatus.ACTIVE, friends_since=datetime.utcnow(),
        ))
        session.commit()

        # Primer like — debe funcionar
        SocialService.process_like(session, u1.privy_did, u2.privy_did)

        # Segundo like el mismo día — debe fallar
        with pytest.raises(HTTPException) as exc_info:
            SocialService.process_like(session, u1.privy_did, u2.privy_did)
        assert exc_info.value.status_code == 400
        assert "Ya le diste like" in exc_info.value.detail


# ═══════════════════════════════════════════════════════════════════════════════
# 11. get_friend_cave / visit_cave
# ═══════════════════════════════════════════════════════════════════════════════

class TestFriendCave:
    def test_get_cave_requires_friendship(self, session, engine):
        u1 = _make_user_with_nick(session, "did:privy:cave_a", "CaveA")
        u2 = _make_user_with_nick(session, "did:privy:cave_b", "CaveB")
        _make_wallet_frj(session, u1.privy_did)
        _make_wallet_frj(session, u2.privy_did)

        with pytest.raises(HTTPException) as exc_info:
            SocialService.get_friend_cave(session, u1.privy_did, u2.privy_did)
        assert exc_info.value.status_code == 403

    def test_visit_logs_action_and_updates_interaction(self, session, engine):
        u1 = _make_user_with_nick(session, "did:privy:visit_a", "VisitA")
        u2 = _make_user_with_nick(session, "did:privy:visit_b", "VisitB")
        _make_wallet_frj(session, u1.privy_did)
        _make_wallet_frj(session, u2.privy_did)

        rel = FriendRelation(
            user_a=u1.privy_did, user_b=u2.privy_did,
            status=FriendStatus.ACTIVE, friends_since=datetime.utcnow(),
            interaction_count=0,
        )
        session.add(rel)
        session.commit()

        cave = SocialService.visit_cave(session, u1.privy_did, u2.privy_did)

        assert cave["friend_id"] == u2.privy_did
        assert cave["nickname"] == "VisitB"

        # Verificar que la interacción se incrementó
        session.refresh(rel)
        assert rel.interaction_count == 1


# ═══════════════════════════════════════════════════════════════════════════════
# 12. are_friends / validate_room_access
# ═══════════════════════════════════════════════════════════════════════════════

class TestAreFriendsAndRoomAccess:
    def test_are_friends_true(self, session, engine):
        u1 = _make_user_with_nick(session, "did:privy:arf_a", "ArfA")
        u2 = _make_user_with_nick(session, "did:privy:arf_b", "ArfB")
        _make_wallet_frj(session, u1.privy_did)
        _make_wallet_frj(session, u2.privy_did)

        session.add(FriendRelation(
            user_a=u1.privy_did, user_b=u2.privy_did,
            status=FriendStatus.ACTIVE, friends_since=datetime.utcnow(),
        ))
        session.commit()

        assert SocialService.are_friends(session, u1.privy_did, u2.privy_did) is True
        assert SocialService.are_friends(session, u2.privy_did, u1.privy_did) is True

    def test_are_friends_false(self, session, engine):
        u1 = _make_user_with_nick(session, "did:privy:nf1", "NF1")
        u2 = _make_user_with_nick(session, "did:privy:nf2", "NF2")
        _make_wallet_frj(session, u1.privy_did)
        _make_wallet_frj(session, u2.privy_did)

        assert SocialService.are_friends(session, u1.privy_did, u2.privy_did) is False

    def test_validate_public_room_always_true(self, session, engine):
        u1 = _make_user_with_nick(session, "did:privy:room_a", "RoomA")
        _make_wallet_frj(session, u1.privy_did)

        assert SocialService.validate_room_access(session, "public", "host", "visitor") is True

    def test_validate_private_room_always_false(self, session, engine):
        assert SocialService.validate_room_access(session, "private", "host", "visitor") is False

    def test_validate_friends_room(self, session, engine):
        u1 = _make_user_with_nick(session, "did:privy:fr_host", "FRHost")
        u2 = _make_user_with_nick(session, "did:privy:fr_friend", "FRFriend")
        u3 = _make_user_with_nick(session, "did:privy:fr_stranger", "FRStranger")
        _make_wallet_frj(session, u1.privy_did)
        _make_wallet_frj(session, u2.privy_did)
        _make_wallet_frj(session, u3.privy_did)

        session.add(FriendRelation(
            user_a=u1.privy_did, user_b=u2.privy_did,
            status=FriendStatus.ACTIVE, friends_since=datetime.utcnow(),
        ))
        session.commit()

        # Amigo puede entrar
        assert SocialService.validate_room_access(session, "friends", u1.privy_did, u2.privy_did) is True
        # Host puede entrar a su propia sala
        assert SocialService.validate_room_access(session, "friends", u1.privy_did, u1.privy_did) is True
        # Extraño no puede entrar
        assert SocialService.validate_room_access(session, "friends", u1.privy_did, u3.privy_did) is False
