"""Tests for VULN-07 (payment bypass) and VULN-09 (staking slot enforcement)."""
from __future__ import annotations

import pytest
from unittest.mock import patch
from sqlmodel import Session

from tests.conftest import make_user, make_wallet
from app.models.axolotito import Axolotito
from app.services.staking_service import StakingService
from app.services.web3_service import Web3Service


# ---------------------------------------------------------------------------
# VULN-07 — verify_usdc_payment must NOT bypass with ALLOW_DEV_PAYMENTS=False
# ---------------------------------------------------------------------------

class TestVuln07PaymentBypass:
    def test_empty_hash_rejected_when_dev_payments_off(self):
        with patch("app.services.web3_service.settings") as mock_cfg:
            mock_cfg.ALLOW_DEV_PAYMENTS = False
            mock_cfg.USDC_ADDRESS = ""
            result = Web3Service.verify_usdc_payment("", "0xRECIPIENT", 10.0)
        assert result is False

    def test_mock_hash_rejected_when_dev_payments_off(self):
        with patch("app.services.web3_service.settings") as mock_cfg:
            mock_cfg.ALLOW_DEV_PAYMENTS = False
            mock_cfg.USDC_ADDRESS = ""
            result = Web3Service.verify_usdc_payment("0x_mock_whatever", "0xRECIPIENT", 10.0)
        assert result is False

    def test_empty_hash_allowed_when_dev_payments_on(self):
        with patch("app.services.web3_service.settings") as mock_cfg:
            mock_cfg.ALLOW_DEV_PAYMENTS = True
            mock_cfg.PRODUCT_MODE = "legacy_simulation"
            mock_cfg.BLOCKCHAIN_MODE = "local"
            result = Web3Service.verify_usdc_payment("", "0xRECIPIENT", 10.0)
        assert result is True

    def test_mock_hash_allowed_when_dev_payments_on(self):
        with patch("app.services.web3_service.settings") as mock_cfg:
            mock_cfg.ALLOW_DEV_PAYMENTS = True
            mock_cfg.PRODUCT_MODE = "legacy_simulation"
            mock_cfg.BLOCKCHAIN_MODE = "local"
            result = Web3Service.verify_usdc_payment("0x_mock_whatever", "0xRECIPIENT", 10.0)
        assert result is True

    def test_mock_hash_rejected_outside_legacy_even_if_flag_is_on(self):
        with patch("app.services.web3_service.settings") as mock_cfg:
            mock_cfg.ALLOW_DEV_PAYMENTS = True
            mock_cfg.PRODUCT_MODE = "non_gambling"
            mock_cfg.BLOCKCHAIN_MODE = "local"
            result = Web3Service.verify_usdc_payment(
                "0x_mock_whatever", "0xRECIPIENT", 10.0
            )
        assert result is False

    def test_invalid_format_always_rejected(self):
        """Malformed hashes are rejected regardless of ALLOW_DEV_PAYMENTS."""
        with patch("app.services.web3_service.settings") as mock_cfg:
            mock_cfg.ALLOW_DEV_PAYMENTS = True
            mock_cfg.USDC_ADDRESS = "0xUSDA"
            result = Web3Service.verify_usdc_payment("not-a-hash", "0xRECIPIENT", 10.0)
        assert result is False

    def test_no_usdc_address_blocked_without_dev_flag(self):
        with patch("app.services.web3_service.settings") as mock_cfg:
            mock_cfg.ALLOW_DEV_PAYMENTS = False
            mock_cfg.USDC_ADDRESS = ""
            # Valid format hash but USDC_ADDRESS missing → rejected
            valid_hash = "0x" + "a" * 64
            result = Web3Service.verify_usdc_payment(valid_hash, "0xRECIPIENT", 10.0)
        assert result is False


# ---------------------------------------------------------------------------
# VULN-09 — claim_all_staking must respect staking slot limit
# ---------------------------------------------------------------------------

def _make_axolotito(session: Session, user_id: str, name: str) -> Axolotito:
    axo = Axolotito(user_id=user_id, name=name)
    session.add(axo)
    session.commit()
    session.refresh(axo)
    return axo


class TestVuln09StakingSlots:
    def test_slot_limit_enforced_with_explicit_cave_level(self, session):
        """User with cave_level=0 has 1 slot → only 1 of 4 axolotitos claimed."""
        user = make_user(session, privy_did="did:privy:vuln09_a")
        user.cave_level = 0
        session.add(user)
        session.commit()
        session.refresh(user)
        make_wallet(session, user.privy_did)

        for i in range(4):
            axo = _make_axolotito(session, user.privy_did, f"Axo-{i}")
            axo.accrued_unclaimed = 100
            session.add(axo)
        session.commit()
        session.refresh(user)

        result = StakingService.claim_all_staking(session, user)

        slots = StakingService.get_staking_slots(user)
        assert slots == 1
        assert len(result["axolotitos"]) == 1, (
            f"Expected 1 axolotito (slots={slots}), got {len(result['axolotitos'])}"
        )

    def test_slot_limit_enforced_cave_level_2(self, session):
        """User with cave_level=2 has 3 slots → all 3 axolotitos claimed."""
        user = make_user(session, privy_did="did:privy:vuln09_b")
        user.cave_level = 2
        session.add(user)
        session.commit()
        make_wallet(session, user.privy_did)

        for i in range(5):  # 5 axolotitos but only 3 slots
            axo = _make_axolotito(session, user.privy_did, f"Axo-{i}")
            axo.accrued_unclaimed = 50
            session.add(axo)
        session.commit()
        session.refresh(user)

        result = StakingService.claim_all_staking(session, user)

        slots = StakingService.get_staking_slots(user)
        assert slots == 3
        assert len(result["axolotitos"]) == 3, (
            f"Expected 3 axolotitos (slots={slots}), got {len(result['axolotitos'])}"
        )

    def test_fewer_axolotitos_than_slots(self, session):
        """User with more slots than axolotitos → all axolotitos claimed."""
        user = make_user(session, privy_did="did:privy:vuln09_c")
        user.cave_level = 5
        session.add(user)
        session.commit()
        make_wallet(session, user.privy_did)

        axo = _make_axolotito(session, user.privy_did, "Solo")
        axo.accrued_unclaimed = 200
        session.add(axo)
        session.commit()
        session.refresh(user)

        result = StakingService.claim_all_staking(session, user)
        assert len(result["axolotitos"]) == 1
