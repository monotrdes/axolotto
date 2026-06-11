"""
test_referral_service.py — Pruebas unitarias de ReferralService.

Cubre:
  1. get_or_create_referral_code: creación lazy, idempotencia, sanitización
  2. claim_referral: éxito, código inválido, auto-referido, ya referido, límite referidor, auto-friend
  3. process_milestone: todos los hitos (registered, tutorial_done, first_game, d7_retained,
     converted, vip_coral), doble concesión prevenida, delay anti-fraude
  4. get_referral_dashboard: código + stats + referidos
  5. Recompensas correctas: FRJ, AXF, items, VIP days
"""
import sys
import os
import pytest
from datetime import datetime, timedelta
from sqlmodel import Session, select, text

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from app.services.referral_service import ReferralService, REWARDS, MAX_LIFETIME_REFERRALS
from app.models.social import (
    ReferralCode, ReferralTracking, ReferralStatus,
    FriendRelation, FriendStatus,
)
from app.models.user import User
from app.models.economy import Wallet

# Importar helpers compartidos de conftest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from conftest import make_user


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_user_with_nick(session, privy_did: str, nickname: str, **kwargs) -> User:
    user = make_user(session, privy_did=privy_did, **kwargs)
    user.nickname = nickname
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def _make_wallet(session, user_id: str, frijolitos: int = 0, axofichas: int = 0) -> Wallet:
    wallet = Wallet(user_id=user_id, frijolitos=frijolitos, axofichas=axofichas)
    session.add(wallet)
    session.commit()
    session.refresh(wallet)
    return wallet


# ═══════════════════════════════════════════════════════════════════════════════
# 1. get_or_create_referral_code
# ═══════════════════════════════════════════════════════════════════════════════

class TestGetOrCreateReferralCode:
    def test_creates_code_from_nickname(self, session, engine):
        u1 = _make_user_with_nick(session, "did:privy:ref_code_a", "AxoMaster")

        rc = ReferralService.get_or_create_referral_code(session, u1.privy_did)

        assert rc is not None
        assert rc.user_id == u1.privy_did
        assert rc.code.startswith("AX-")
        assert "AXOMASTER" in rc.code

    def test_idempotent_returns_same_code(self, session, engine):
        u1 = _make_user_with_nick(session, "did:privy:ref_idem", "IdemUser")

        rc1 = ReferralService.get_or_create_referral_code(session, u1.privy_did)
        rc2 = ReferralService.get_or_create_referral_code(session, u1.privy_did)

        assert rc1.id == rc2.id
        assert rc1.code == rc2.code

    def test_handles_short_nickname(self, session, engine):
        """Nickname muy corto (<2 chars tras sanitizar) genera código random."""
        u1 = _make_user_with_nick(session, "did:privy:ref_short", "X")

        rc = ReferralService.get_or_create_referral_code(session, u1.privy_did)

        assert rc is not None
        assert rc.code.startswith("AX-")
        # No debería ser solo "AX-X" (mínimo 6 chars hex)
        assert len(rc.code) >= 6

    def test_handles_none_nickname(self, session, engine):
        u1 = make_user(session, privy_did="did:privy:ref_none")
        # No seteamos nickname — queda None

        rc = ReferralService.get_or_create_referral_code(session, u1.privy_did)

        assert rc is not None
        assert rc.code.startswith("AX-")

    def test_sanitizes_special_chars(self, session, engine):
        u1 = _make_user_with_nick(session, "did:privy:ref_special", "Áxø_Máster!99")

        rc = ReferralService.get_or_create_referral_code(session, u1.privy_did)

        # Sin caracteres especiales ni acentos
        assert "AX-" in rc.code
        # El nickname se limpia a solo alfanuméricos
        clean_part = rc.code.replace("AX-", "")
        assert all(c.isalnum() or c == "-" for c in clean_part)


# ═══════════════════════════════════════════════════════════════════════════════
# 2. claim_referral
# ═══════════════════════════════════════════════════════════════════════════════

class TestClaimReferral:
    def test_claims_code_successfully(self, session, engine):
        referrer = _make_user_with_nick(session, "did:privy:claim_ref", "ClaimRef")
        referred = _make_user_with_nick(session, "did:privy:claim_new", "ClaimNew")
        _make_wallet(session, referrer.privy_did, frijolitos=1000)
        _make_wallet(session, referred.privy_did, frijolitos=1000)

        code = ReferralService.get_or_create_referral_code(session, referrer.privy_did)

        result = ReferralService.claim_referral(session, code.code, referred.privy_did)

        assert result["status"] == "ok"
        assert "50 FRJ" in result["referrer_reward"]

        # Verificar que ambos recibieron 50 FRJ (en backend mínima = 50 * 10000 = 500000)
        ref_wallet = session.exec(select(Wallet).where(Wallet.user_id == referrer.privy_did)).first()
        new_wallet = session.exec(select(Wallet).where(Wallet.user_id == referred.privy_did)).first()
        assert ref_wallet.frijolitos > 1000
        assert new_wallet.frijolitos > 1000

        # Verificar tracking creado
        tracking = session.exec(
            select(ReferralTracking).where(ReferralTracking.referred_id == referred.privy_did)
        ).first()
        assert tracking is not None
        assert tracking.status == ReferralStatus.REGISTERED

    def test_rejects_invalid_code(self, session, engine):
        u1 = _make_user_with_nick(session, "did:privy:bad_code", "BadCode")
        _make_wallet(session, u1.privy_did)

        result = ReferralService.claim_referral(session, "AX-CODIGO_INEXISTENTE", u1.privy_did)

        assert result["status"] == "invalid_code"

    def test_rejects_self_referral(self, session, engine):
        u1 = _make_user_with_nick(session, "did:privy:self_ref", "SelfRef")
        _make_wallet(session, u1.privy_did)

        code = ReferralService.get_or_create_referral_code(session, u1.privy_did)

        result = ReferralService.claim_referral(session, code.code, u1.privy_did)

        assert result["status"] == "self_referral"

    def test_rejects_already_referred(self, session, engine):
        referrer = _make_user_with_nick(session, "did:privy:dup_ref", "DupRef")
        referred = _make_user_with_nick(session, "did:privy:dup_new", "DupNew")
        _make_wallet(session, referrer.privy_did, frijolitos=1000)
        _make_wallet(session, referred.privy_did, frijolitos=1000)

        code = ReferralService.get_or_create_referral_code(session, referrer.privy_did)

        # Primer claim: éxito
        result1 = ReferralService.claim_referral(session, code.code, referred.privy_did)
        assert result1["status"] == "ok"

        # Segundo claim con otro código: rechazado
        referrer2 = _make_user_with_nick(session, "did:privy:dup_ref2", "DupRef2")
        _make_wallet(session, referrer2.privy_did, frijolitos=1000)
        code2 = ReferralService.get_or_create_referral_code(session, referrer2.privy_did)

        result2 = ReferralService.claim_referral(session, code2.code, referred.privy_did)
        assert result2["status"] == "already_referred"

    def test_auto_creates_friendship(self, session, engine):
        referrer = _make_user_with_nick(session, "did:privy:auto_fr_ref", "AutoFrRef")
        referred = _make_user_with_nick(session, "did:privy:auto_fr_new", "AutoFrNew")
        _make_wallet(session, referrer.privy_did, frijolitos=1000)
        _make_wallet(session, referred.privy_did, frijolitos=1000)

        code = ReferralService.get_or_create_referral_code(session, referrer.privy_did)

        ReferralService.claim_referral(session, code.code, referred.privy_did)

        # Verificar amistad creada
        from app.services.social_service import SocialService
        assert SocialService.are_friends(session, referrer.privy_did, referred.privy_did) is True

    def test_code_stats_updated(self, session, engine):
        referrer = _make_user_with_nick(session, "did:privy:stats_ref", "StatsRef")
        referred = _make_user_with_nick(session, "did:privy:stats_new", "StatsNew")
        _make_wallet(session, referrer.privy_did, frijolitos=1000)
        _make_wallet(session, referred.privy_did, frijolitos=1000)

        code = ReferralService.get_or_create_referral_code(session, referrer.privy_did)

        ReferralService.claim_referral(session, code.code, referred.privy_did)

        # Refrescar código
        updated_code = session.exec(
            select(ReferralCode).where(ReferralCode.user_id == referrer.privy_did)
        ).first()
        assert updated_code.total_uses == 1
        assert updated_code.active_referrals == 1
        assert updated_code.rewards_earned_frj > 0


# ═══════════════════════════════════════════════════════════════════════════════
# 3. process_milestone
# ═══════════════════════════════════════════════════════════════════════════════

class TestProcessMilestone:
    def _setup_referral(self, session, ref_nick="RefMilestone", new_nick="NewMilestone"):
        """Helper: crea referidor, referido, wallets y claim inicial."""
        referrer = _make_user_with_nick(session, f"did:privy:{ref_nick.lower()}", ref_nick)
        referred = _make_user_with_nick(session, f"did:privy:{new_nick.lower()}", new_nick)
        _make_wallet(session, referrer.privy_did, frijolitos=0, axofichas=0)
        _make_wallet(session, referred.privy_did, frijolitos=0, axofichas=0)

        code = ReferralService.get_or_create_referral_code(session, referrer.privy_did)
        ReferralService.claim_referral(session, code.code, referred.privy_did)

        return referrer, referred

    def test_tutorial_done_milestone(self, session, engine):
        referrer, referred = self._setup_referral(session, "RefTut", "NewTut")

        result = ReferralService.process_milestone(session, referred.privy_did, "tutorial_done")

        assert result["status"] == "ok"

        # Verificar AXF (20 * 1_000_000 = 20_000_000 backend mínima)
        ref_wallet = session.exec(select(Wallet).where(Wallet.user_id == referrer.privy_did)).first()
        new_wallet = session.exec(select(Wallet).where(Wallet.user_id == referred.privy_did)).first()
        assert ref_wallet.axofichas == 20_000_000
        assert new_wallet.axofichas == 20_000_000

        # Verificar status actualizado
        tracking = session.exec(
            select(ReferralTracking).where(ReferralTracking.referred_id == referred.privy_did)
        ).first()
        assert tracking.status == ReferralStatus.TUTORIAL_DONE

    def test_first_game_milestone(self, session, engine):
        referrer, referred = self._setup_referral(session, "RefGame", "NewGame")

        # Record FRJ after registration reward (50 FRJ = 500000)
        ref_wallet_before = session.exec(select(Wallet).where(Wallet.user_id == referrer.privy_did)).first()
        frj_before = ref_wallet_before.frijolitos  # 500000 from registration

        result = ReferralService.process_milestone(session, referred.privy_did, "first_game")

        assert result["status"] == "ok"
        # Solo el referidor recibe FRJ adicional (30 * 10000 = 300000)
        session.refresh(ref_wallet_before)
        assert ref_wallet_before.frijolitos == frj_before + 300000

    def test_prevents_double_grant(self, session, engine):
        referrer, referred = self._setup_referral(session, "RefDouble", "NewDouble")

        r1 = ReferralService.process_milestone(session, referred.privy_did, "tutorial_done")
        assert r1["status"] == "ok"

        r2 = ReferralService.process_milestone(session, referred.privy_did, "tutorial_done")
        assert r2["status"] == "already_granted"

    def test_rejects_unknown_milestone(self, session, engine):
        referrer, referred = self._setup_referral(session, "RefUnknown", "NewUnknown")

        result = ReferralService.process_milestone(session, referred.privy_did, "milestone_falso")

        assert result["status"] == "unknown_milestone"

    def test_not_referred_user_has_no_milestones(self, session, engine):
        u1 = _make_user_with_nick(session, "did:privy:no_ref", "NoRef")
        _make_wallet(session, u1.privy_did)

        result = ReferralService.process_milestone(session, u1.privy_did, "tutorial_done")

        assert result["status"] == "not_referred"

    def test_d7_retained_enforces_delay(self, session, engine):
        """d7_retained requiere 24h de delay anti-fraude."""
        referrer, referred = self._setup_referral(session, "RefD7", "NewD7")

        # Recién registrado — debe fallar por delay
        result = ReferralService.process_milestone(session, referred.privy_did, "d7_retained")
        assert result["status"] == "pending_delay"

        # Simular que pasaron 25 horas
        tracking = session.exec(
            select(ReferralTracking).where(ReferralTracking.referred_id == referred.privy_did)
        ).first()
        tracking.referred_at = datetime.utcnow() - timedelta(hours=25)
        session.add(tracking)
        session.commit()

        result2 = ReferralService.process_milestone(session, referred.privy_did, "d7_retained")
        assert result2["status"] == "ok"

    def test_vip_coral_milestone(self, session, engine):
        """VIP Coral extiende días VIP a ambos si tienen VIP tier."""
        referrer, referred = self._setup_referral(session, "RefVIP", "NewVIP")
        # Dar VIP tier a ambos
        referrer.vip_tier = "coral"
        referrer.vip_expires_at = datetime.utcnow() + timedelta(days=7)
        referred.vip_tier = "coral"
        referred.vip_expires_at = datetime.utcnow() + timedelta(days=7)
        session.add(referrer)
        session.add(referred)
        session.commit()

        # Simular delay superado
        tracking = session.exec(
            select(ReferralTracking).where(ReferralTracking.referred_id == referred.privy_did)
        ).first()
        tracking.referred_at = datetime.utcnow() - timedelta(hours=25)
        session.add(tracking)
        session.commit()

        result = ReferralService.process_milestone(session, referred.privy_did, "vip_coral")
        assert result["status"] == "ok"

        # Verificar extensión VIP (3 días extra)
        session.refresh(referrer)
        session.refresh(referred)
        # vip_expires_at debe ser ~10 días desde ahora (7 original + 3 extra)
        expected_min = datetime.utcnow() + timedelta(days=9)
        assert referrer.vip_expires_at > expected_min
        assert referred.vip_expires_at > expected_min


# ═══════════════════════════════════════════════════════════════════════════════
# 4. get_referral_dashboard
# ═══════════════════════════════════════════════════════════════════════════════

class TestReferralDashboard:
    def test_returns_code_and_stats(self, session, engine):
        u1 = _make_user_with_nick(session, "did:privy:dash_ref", "DashRef")
        _make_wallet(session, u1.privy_did)

        dashboard = ReferralService.get_referral_dashboard(session, u1.privy_did)

        assert "code" in dashboard
        assert dashboard["code"].startswith("AX-")
        assert dashboard["total_uses"] == 0
        assert dashboard["active_referrals"] == 0
        assert dashboard["rewards_earned_frj"] == 0
        assert "referred_users" in dashboard
        assert dashboard["max_lifetime"] == MAX_LIFETIME_REFERRALS

    def test_includes_referred_users(self, session, engine):
        referrer = _make_user_with_nick(session, "did:privy:dash_with_refs", "DashWithRefs")
        referred1 = _make_user_with_nick(session, "did:privy:dash_new1", "DashNew1")
        referred2 = _make_user_with_nick(session, "did:privy:dash_new2", "DashNew2")
        _make_wallet(session, referrer.privy_did, frijolitos=10000)
        _make_wallet(session, referred1.privy_did, frijolitos=1000)
        _make_wallet(session, referred2.privy_did, frijolitos=1000)

        code = ReferralService.get_or_create_referral_code(session, referrer.privy_did)
        ReferralService.claim_referral(session, code.code, referred1.privy_did)
        ReferralService.claim_referral(session, code.code, referred2.privy_did)

        dashboard = ReferralService.get_referral_dashboard(session, referrer.privy_did)

        assert dashboard["total_uses"] == 2
        assert len(dashboard["referred_users"]) == 2
        nicknames = [u["nickname"] for u in dashboard["referred_users"]]
        assert "DashNew1" in nicknames
        assert "DashNew2" in nicknames


# ═══════════════════════════════════════════════════════════════════════════════
# 5. Edge Cases
# ═══════════════════════════════════════════════════════════════════════════════

class TestEdgeCases:
    def test_referrer_lifetime_limit(self, session, engine):
        """Verificar que MAX_LIFETIME_REFERRALS se respeta en claim_referral."""
        referrer = _make_user_with_nick(session, "did:privy:limit_ref", "LimitRef")
        _make_wallet(session, referrer.privy_did, frijolitos=100000)

        code = ReferralService.get_or_create_referral_code(session, referrer.privy_did)

        # Crear MAX_LIFETIME_REFERRALS tracking entries (simulando referidos previos)
        for i in range(MAX_LIFETIME_REFERRALS):
            tracking = ReferralTracking(
                referrer_id=referrer.privy_did,
                referred_id=f"did:privy:limit_new_{i}",
                code_used=code.code,
                status=ReferralStatus.REGISTERED,
            )
            session.add(tracking)
        session.commit()

        # Intento #101 debe fallar
        new_user = _make_user_with_nick(session, "did:privy:limit_over", "LimitOver")
        _make_wallet(session, new_user.privy_did, frijolitos=1000)

        result = ReferralService.claim_referral(session, code.code, new_user.privy_did)
        assert result["status"] == "referrer_limit"

    def test_code_with_spaces_and_lowercase(self, session, engine):
        """El claim normaliza el código (strip + upper)."""
        referrer = _make_user_with_nick(session, "did:privy:case_ref", "CaseRef")
        referred = _make_user_with_nick(session, "did:privy:case_new", "CaseNew")
        _make_wallet(session, referrer.privy_did, frijolitos=1000)
        _make_wallet(session, referred.privy_did, frijolitos=1000)

        code = ReferralService.get_or_create_referral_code(session, referrer.privy_did)

        # Enviar código con espacios y minúsculas
        messy_code = f"  {code.code.lower()}  "
        result = ReferralService.claim_referral(session, messy_code, referred.privy_did)

        assert result["status"] == "ok"

    def test_friend_request_auto_accepts_reverse(self, session, engine):
        """Verificar que send_friend_request auto-acepta cuando hay solicitud pendiente inversa."""
        u1 = _make_user_with_nick(session, "did:privy:auto_a2", "AutoA2")
        u2 = _make_user_with_nick(session, "did:privy:auto_b2", "AutoB2")
        _make_wallet(session, u1.privy_did)
        _make_wallet(session, u2.privy_did)

        from app.services.social_service import SocialService

        # u1 envía solicitud a u2
        SocialService.send_friend_request(session, u1.privy_did, u2.privy_did)

        # u2 envía solicitud a u1 → auto-acepta porque u1 ya envió
        rel = SocialService.send_friend_request(session, u2.privy_did, u1.privy_did)

        assert rel.status == FriendStatus.ACTIVE
        assert SocialService.are_friends(session, u1.privy_did, u2.privy_did) is True
