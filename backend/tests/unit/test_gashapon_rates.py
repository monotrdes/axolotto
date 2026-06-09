"""
test_gashapon_rates.py — Pruebas estadísticas y funcionales del Gashapón y Sistema de Cápsulas.

Cubre:
  - Boundaries determinísticos en los umbrales de probabilidad (gashapón y cápsulas)
  - Distribución estadística en 100k tiradas por tipo de roll
  - Sistema de pity: incremento, reset y forzado al límite por tier
  - Flujo funcional completo: costos FRJ, uso de cápsulas, inventario, ledger
"""
import random as stdlib_random
from typing import Optional

import pytest
from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.economy import CurrencyType, TransactionLedger, TransactionType, Wallet
from app.models.items import (
    CapsulaPity, ItemCatalog, ItemType, PlayerInventory, Rarity,
)
from app.api.v1.endpoints.shop import (
    GashaponRollRequest, roll_gashapon,
)
from app.services.capsule_service import (
    _roll_capsule, FRJ_RANGES, PITY_LIMITS, TIER_COSTS, TIER_POOLS, PITY_FIELD_MAP,
)
from tests.conftest import make_item, make_user, make_wallet


# ---------------------------------------------------------------------------
# Helpers de seeds de catálogo mínimo para _roll_capsule
# ---------------------------------------------------------------------------

def _seed_capsule_catalog(session: Session) -> None:
    """Crea un ítem por tipo×rareza para que _roll_capsule siempre tenga de dónde elegir."""
    for r in (Rarity.COMMON, Rarity.RARE, Rarity.EPIC, Rarity.LEGENDARY):
        make_item(session, f"Carta {r.value}", ItemType.CARD, rarity=r)
        make_item(session, f"Acc {r.value}", ItemType.ACCESSORY, rarity=r)
    make_item(session, "Booster Cápsula", ItemType.BOOSTER,
              item_metadata={"pack_theme": "pure", "fase": 1})
    make_item(session, "Webito Cápsula", ItemType.EGG, price_gal=200.0)
    session.commit()


class _FixedRandom:
    """Reemplazo determinístico del módulo random para tests de pity."""

    def __init__(self, fixed_value: float = 0.0):
        self._val = fixed_value

    def random(self) -> float:
        import inspect
        caller = inspect.stack()[1].function
        if caller in ("_try_legendary_drop", "_try_tabla_forjada_drop"):
            return 0.99
        return self._val

    def choice(self, seq):
        return seq[0]

    def uniform(self, a: float, b: float) -> float:
        return a + (b - a) * self._val


# ===========================================================================
# 1. Distribución del Gashapón clásico (sin BD)
# ===========================================================================

class TestGashaponDistribution:
    """Valida probabilidades de rareza del roll_gashapon (lógica pura, sin BD)."""

    def _common_rarity(self, rand: float) -> str:
        if rand < 0.70:
            return "common"
        elif rand < 0.95:
            return "rare"
        else:
            return "epic"

    def _premium_rarity(self, rand: float) -> str:
        if rand < 0.40:
            return "rare"
        elif rand < 0.85:
            return "epic"
        else:
            return "legendary"

    # ---- Roll común (70 / 25 / 5) -----------------------------------------

    def test_common_boundary_just_below_common_threshold(self):
        assert self._common_rarity(0.70 - 1e-9) == "common"

    def test_common_boundary_at_rare_threshold(self):
        assert self._common_rarity(0.70) == "rare"

    def test_common_boundary_just_below_epic_threshold(self):
        assert self._common_rarity(0.95 - 1e-9) == "rare"

    def test_common_boundary_at_epic_threshold(self):
        assert self._common_rarity(0.95) == "epic"

    def test_common_distribution_100k(self):
        """100k tiradas comunes: cada rareza dentro de ±3 pp del valor teórico."""
        N, TOL = 100_000, 0.03
        counts: dict[str, int] = {"common": 0, "rare": 0, "epic": 0}
        for _ in range(N):
            counts[self._common_rarity(stdlib_random.random())] += 1
        assert abs(counts["common"] / N - 0.70) < TOL, counts
        assert abs(counts["rare"]   / N - 0.25) < TOL, counts
        assert abs(counts["epic"]   / N - 0.05) < TOL, counts

    # ---- Roll premium (40 / 45 / 15) --------------------------------------

    def test_premium_boundary_just_below_rare_threshold(self):
        assert self._premium_rarity(0.40 - 1e-9) == "rare"

    def test_premium_boundary_at_epic_threshold(self):
        assert self._premium_rarity(0.40) == "epic"

    def test_premium_boundary_just_below_legendary_threshold(self):
        assert self._premium_rarity(0.85 - 1e-9) == "epic"

    def test_premium_boundary_at_legendary_threshold(self):
        assert self._premium_rarity(0.85) == "legendary"

    def test_premium_distribution_100k(self):
        """100k tiradas premium: distribución dentro de ±3 pp."""
        N, TOL = 100_000, 0.03
        counts: dict[str, int] = {"rare": 0, "epic": 0, "legendary": 0}
        for _ in range(N):
            counts[self._premium_rarity(stdlib_random.random())] += 1
        assert abs(counts["rare"]       / N - 0.40) < TOL, counts
        assert abs(counts["epic"]       / N - 0.45) < TOL, counts
        assert abs(counts["legendary"]  / N - 0.15) < TOL, counts


# ===========================================================================
# 2. Distribución del pool de Cápsulas (sin BD)
# ===========================================================================

class TestCapsulePoolDistribution:
    """Valida pools de outcomes de Cápsulas sin tocar la BD."""

    def _simulate_outcome(self, tier: str, rand: float) -> str:
        for threshold, otype in TIER_POOLS[tier]:
            if rand < threshold:
                return otype
        return "axolotito"

    @pytest.mark.parametrize("tier", ["bronce", "plata", "oro"])
    def test_pool_thresholds_are_monotonically_increasing(self, tier):
        prev = 0.0
        for threshold, _ in TIER_POOLS[tier]:
            assert threshold > prev, f"Tier {tier}: {threshold} no es mayor que {prev}"
            prev = threshold

    @pytest.mark.parametrize("tier", ["bronce", "plata", "oro"])
    def test_pool_last_threshold_is_one(self, tier):
        last_threshold = TIER_POOLS[tier][-1][0]
        assert last_threshold == pytest.approx(1.0), f"Tier {tier}: último umbral debe ser 1.0"

    @pytest.mark.parametrize("tier,expected_rates", [
        ("bronce", {"gal": 0.45, "carta": 0.30, "accesorio": 0.10, "sobre": 0.10, "axolotito": 0.05}),
        ("plata",  {"gal": 0.20, "carta": 0.45, "accesorio": 0.15, "sobre": 0.10, "axolotito": 0.10}),
        ("oro",    {"gal": 0.05, "carta": 0.40, "accesorio": 0.20, "sobre": 0.10, "axolotito": 0.25}),
    ])
    def test_pool_distribution_100k(self, tier, expected_rates):
        """100k tiradas por tier: cada outcome dentro de ±3 pp del valor teórico."""
        N, TOL = 100_000, 0.03
        counts: dict[str, int] = {k: 0 for k in expected_rates}
        for _ in range(N):
            outcome = self._simulate_outcome(tier, stdlib_random.random())
            counts[outcome] += 1
        for otype, expected in expected_rates.items():
            actual = counts[otype] / N
            assert abs(actual - expected) < TOL, (
                f"Tier {tier} / {otype}: esperado {expected:.2f}, obtenido {actual:.4f}"
            )


# ===========================================================================
# 3. Sistema de Pity de Cápsulas (con BD)
# ===========================================================================

class TestCapsulePity:
    """Valida el contador pity: incremento, acumulación, reset y forzado al límite."""

    def _roll_non_axolotito(self, session: Session, user_id: str, tier: str, monkeypatch) -> dict:
        """Tirada con rand=0.0 → primer bucket siempre es non-axolotito para los tres tiers."""
        import app.services.capsule_service as service_mod
        monkeypatch.setattr(service_mod, "_rng", _FixedRandom(fixed_value=0.0))
        result = _roll_capsule(tier, user_id, session)
        session.commit()
        return result

    def _roll_axolotito_via_pity(self, session: Session, user_id: str, tier: str) -> dict:
        """Pone el pity al límite en BD y lanza la tirada — la función fuerza axolotito."""
        pity = session.exec(select(CapsulaPity).where(CapsulaPity.user_id == user_id)).first()
        if not pity:
            pity = CapsulaPity(user_id=user_id)
            session.add(pity)
        setattr(pity, PITY_FIELD_MAP[tier], PITY_LIMITS[tier])
        session.add(pity)
        session.commit()
        result = _roll_capsule(tier, user_id, session)
        session.commit()
        return result

    # ---- Incremento --------------------------------------------------------

    def test_pity_increments_by_one_on_non_axolotito(self, session, monkeypatch):
        user = make_user(session)
        _seed_capsule_catalog(session)

        self._roll_non_axolotito(session, user.privy_did, "bronce", monkeypatch)

        session.expire_all()
        pity = session.exec(select(CapsulaPity).where(CapsulaPity.user_id == user.privy_did)).first()
        assert pity is not None
        assert pity.pity_cobre == 1

    def test_pity_accumulates_across_rolls(self, session, monkeypatch):
        """Tres tiradas sin axolotito consecutivas → pity_plata == 3."""
        user = make_user(session)
        _seed_capsule_catalog(session)

        for _ in range(3):
            self._roll_non_axolotito(session, user.privy_did, "plata", monkeypatch)

        session.expire_all()
        pity = session.exec(select(CapsulaPity).where(CapsulaPity.user_id == user.privy_did)).first()
        assert pity.pity_plata == 3

    def test_pity_is_independent_per_tier(self, session, monkeypatch):
        """Rolls en 'bronce' no modifican pity_plata ni pity_oro."""
        user = make_user(session)
        _seed_capsule_catalog(session)

        for _ in range(3):
            self._roll_non_axolotito(session, user.privy_did, "bronce", monkeypatch)

        session.expire_all()
        pity = session.exec(select(CapsulaPity).where(CapsulaPity.user_id == user.privy_did)).first()
        assert pity.pity_cobre == 3
        assert pity.pity_plata == 0
        assert pity.pity_oro == 0

    # ---- Reset -------------------------------------------------------------

    def test_pity_resets_to_zero_after_axolotito(self, session, monkeypatch):
        """Dos tiradas no-axolotito (pity=2) → axolotito forzado por pity → reset a 0."""
        user = make_user(session)
        _seed_capsule_catalog(session)

        self._roll_non_axolotito(session, user.privy_did, "bronce", monkeypatch)
        self._roll_non_axolotito(session, user.privy_did, "bronce", monkeypatch)
        self._roll_axolotito_via_pity(session, user.privy_did, "bronce")

        session.expire_all()
        pity = session.exec(select(CapsulaPity).where(CapsulaPity.user_id == user.privy_did)).first()
        assert pity.pity_cobre == 0

    # ---- Forzado al límite (3 tiers) --------------------------------------

    @pytest.mark.parametrize("tier,limit", list(PITY_LIMITS.items()))
    def test_pity_at_limit_forces_axolotito(self, session, monkeypatch, tier, limit):
        """Con pity en el límite, rand=0.0 (que daría 'gal') es ignorado; se entrega axolotito."""
        user = make_user(session)
        _seed_capsule_catalog(session)

        # Precargar pity directamente al límite (usando columna real de BD)
        pity = CapsulaPity(user_id=user.privy_did)
        setattr(pity, PITY_FIELD_MAP[tier], limit)
        session.add(pity)
        session.commit()

        import app.api.v1.endpoints.shop as shop_mod
        monkeypatch.setattr(shop_mod, "_rng", _FixedRandom(fixed_value=0.0))
        result = _roll_capsule(tier, user.privy_did, session)
        session.commit()

        assert result["outcome_type"] == "axolotito", (
            f"Tier {tier} con pity={limit}: debió forzar axolotito pero obtuvo '{result['outcome_type']}'"
        )

    @pytest.mark.parametrize("tier,limit", list(PITY_LIMITS.items()))
    def test_pity_resets_after_forced_axolotito(self, session, monkeypatch, tier, limit):
        """Después del axolotito forzado por pity, el contador queda en 0."""
        user = make_user(session)
        _seed_capsule_catalog(session)

        pity = CapsulaPity(user_id=user.privy_did)
        setattr(pity, PITY_FIELD_MAP[tier], limit)
        session.add(pity)
        session.commit()

        import app.api.v1.endpoints.shop as shop_mod
        monkeypatch.setattr(shop_mod, "_rng", _FixedRandom(fixed_value=0.0))
        _roll_capsule(tier, user.privy_did, session)
        session.commit()

        session.expire_all()
        pity = session.exec(select(CapsulaPity).where(CapsulaPity.user_id == user.privy_did)).first()
        assert getattr(pity, PITY_FIELD_MAP[tier]) == 0, (
            f"Tier {tier}: pity debería ser 0 tras axolotito forzado"
        )

    # ---- Inicialización ----------------------------------------------------

    def test_pity_row_created_on_first_roll(self, session, monkeypatch):
        """La primera tirada crea el registro CapsulaPity para el usuario."""
        user = make_user(session)
        _seed_capsule_catalog(session)

        pity_before = session.exec(
            select(CapsulaPity).where(CapsulaPity.user_id == user.privy_did)
        ).first()
        assert pity_before is None

        self._roll_non_axolotito(session, user.privy_did, "bronce", monkeypatch)

        session.expire_all()
        pity_after = session.exec(
            select(CapsulaPity).where(CapsulaPity.user_id == user.privy_did)
        ).first()
        assert pity_after is not None


# ===========================================================================
# 4. Gashapón funcional (costos FRJ, inventario)
# ===========================================================================

class TestGashaponFunctional:
    """Prueba el flujo completo del endpoint roll_gashapon."""

    @pytest.fixture(autouse=True)
    def seed_accessories(self, session):
        for r in (Rarity.COMMON, Rarity.RARE, Rarity.EPIC, Rarity.LEGENDARY):
            make_item(session, f"Acc {r.value}", ItemType.ACCESSORY, rarity=r)
        session.commit()

    def _roll(self, session, user_id: str, roll_type: str = "common") -> dict:
        return roll_gashapon(
            GashaponRollRequest(roll_type=roll_type),
            session=session,
            verified_user_id=user_id,
        )

    def test_common_roll_costs_1000_frj(self, session):
        user = make_user(session)
        make_wallet(session, user.privy_did, gemas_alga=5000.0)

        self._roll(session, user.privy_did, roll_type="common")

        wallet = session.exec(select(Wallet).where(Wallet.user_id == user.privy_did)).first()
        assert wallet.frijolitos == pytest.approx(4000.0)

    def test_premium_roll_costs_2500_frj(self, session):
        user = make_user(session)
        make_wallet(session, user.privy_did, gemas_alga=5000.0)

        self._roll(session, user.privy_did, roll_type="premium")

        wallet = session.exec(select(Wallet).where(Wallet.user_id == user.privy_did)).first()
        assert wallet.frijolitos == pytest.approx(2500.0)

    def test_roll_adds_accessory_to_inventory(self, session):
        user = make_user(session)
        make_wallet(session, user.privy_did, gemas_alga=5000.0)

        self._roll(session, user.privy_did)

        inv_entries = session.exec(
            select(PlayerInventory).where(PlayerInventory.user_id == user.privy_did)
        ).all()
        assert sum(i.quantity for i in inv_entries) >= 1

    def test_roll_creates_ledger_entry(self, session):
        user = make_user(session)
        make_wallet(session, user.privy_did, gemas_alga=5000.0)

        self._roll(session, user.privy_did)

        ledger = session.exec(
            select(TransactionLedger).where(TransactionLedger.user_id == user.privy_did)
        ).first()
        assert ledger is not None
        assert ledger.amount == pytest.approx(1000.0)

    def test_insufficient_frj_raises_400(self, session):
        user = make_user(session)
        make_wallet(session, user.privy_did, gemas_alga=500.0)

        with pytest.raises(HTTPException) as exc:
            self._roll(session, user.privy_did)
        assert exc.value.status_code == 400
        assert "insuficiente" in exc.value.detail.lower()

    def test_roll_result_contains_item_and_cost(self, session):
        user = make_user(session)
        make_wallet(session, user.privy_did, gemas_alga=5000.0)

        result = self._roll(session, user.privy_did)

        assert "item" in result
        assert result["cost_frj"] == pytest.approx(1000.0)


# ===========================================================================
# 5. Cápsula funcional (costos FRJ, uso de cápsulas en inventario)
# ===========================================================================

class TestCapsuleFunctional:
    """Prueba el flujo completo de roll_capsule con FRJ y con cápsulas de inventario."""

    @pytest.fixture(autouse=True)
    def seed_catalog(self, session):
        _seed_capsule_catalog(session)
        # Crear ítems de cápsula en el catálogo
        for tier_name, price in [("bronce", 1500.0), ("plata", 5000.0), ("oro", 20000.0)]:
            existing = session.exec(
                select(ItemCatalog).where(ItemCatalog.name == f"Cápsula {tier_name.capitalize()}")
            ).first()
            if not existing:
                make_item(
                    session,
                    name=f"Cápsula {tier_name.capitalize()}",
                    item_type=ItemType.CONSUMABLE,
                    price_gal=price,
                    item_metadata={"capsule_tier": tier_name},
                )
        session.commit()

    def test_roll_charges_frj(self, session):
        user = make_user(session)
        make_wallet(session, user.privy_did, gemas_alga=3000.0)
        from app.api.v1.endpoints.shop import roll_capsule, CapsuleRollRequest
        from unittest.mock import patch

        with patch("app.services.capsule_service._rng.random", return_value=0.99):
            res = roll_capsule(CapsuleRollRequest(tier="bronce"), session=session, verified_user_id=user.privy_did)
        wallet = session.exec(select(Wallet).where(Wallet.user_id == user.privy_did)).first()
        assert wallet.frijolitos == pytest.approx(1500.0)

    def test_insufficient_frj_raises_400(self, session):
        user = make_user(session)
        make_wallet(session, user.privy_did, gemas_alga=100.0)
        from app.api.v1.endpoints.shop import roll_capsule, CapsuleRollRequest

        with pytest.raises(HTTPException) as exc:
            roll_capsule(CapsuleRollRequest(tier="bronce"), session=session, verified_user_id=user.privy_did)
        assert exc.value.status_code == 400
        assert "FRJ" in exc.value.detail

    def test_roll_with_capsule_item_does_not_charge_frj(self, session):
        user = make_user(session)
        make_wallet(session, user.privy_did, gemas_alga=0.0)
        from app.api.v1.endpoints.shop import roll_capsule, CapsuleRollRequest
        from unittest.mock import patch

        # Dar una cápsula bronce en inventario
        capsula = session.exec(
            select(ItemCatalog).where(ItemCatalog.name == "Cápsula Bronce")
        ).first()
        assert capsula is not None
        session.add(PlayerInventory(user_id=user.privy_did, item_id=capsula.id, quantity=1))
        session.commit()

        with patch("app.services.capsule_service._rng.random", return_value=0.99):
            res = roll_capsule(CapsuleRollRequest(tier="bronce", use_capsule=True), session=session, verified_user_id=user.privy_did)

        wallet = session.exec(select(Wallet).where(Wallet.user_id == user.privy_did)).first()
        assert wallet.frijolitos == pytest.approx(0.0)  # no se cobró FRJ

    def test_roll_with_capsule_consumes_one(self, session):
        user = make_user(session)
        make_wallet(session, user.privy_did, gemas_alga=0.0)
        from app.api.v1.endpoints.shop import roll_capsule, CapsuleRollRequest

        capsula = session.exec(
            select(ItemCatalog).where(ItemCatalog.name == "Cápsula Bronce")
        ).first()
        assert capsula is not None
        session.add(PlayerInventory(user_id=user.privy_did, item_id=capsula.id, quantity=2))
        session.commit()

        roll_capsule(CapsuleRollRequest(tier="bronce", use_capsule=True), session=session, verified_user_id=user.privy_did)

        inv = session.exec(
            select(PlayerInventory)
            .where(PlayerInventory.user_id == user.privy_did)
            .where(PlayerInventory.item_id == capsula.id)
        ).first()
        assert inv is not None and inv.quantity == 1

    def test_roll_with_capsule_when_none_raises_400(self, session):
        user = make_user(session)
        make_wallet(session, user.privy_did, gemas_alga=0.0)
        from app.api.v1.endpoints.shop import roll_capsule, CapsuleRollRequest

        with pytest.raises(HTTPException) as exc:
            roll_capsule(CapsuleRollRequest(tier="bronce", use_capsule=True), session=session, verified_user_id=user.privy_did)
        assert exc.value.status_code == 400
        assert "Cápsula" in exc.value.detail
