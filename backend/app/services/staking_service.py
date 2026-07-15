"""staking_service.py — Axolotito Staking con Caps y Play-to-Stake.

Los Axolotitos generan FRJ (Frijolitos) pasivamente mientras su dueño
siga jugando al menos 1 partida cada 24h (Play-to-Stake).
"""

from datetime import datetime, timedelta
from typing import Dict, List

from fastapi import HTTPException
from sqlmodel import Session, select

from app.core.config import settings
from app.core.product_policy import require_feature
from app.models.axolotito import Axolotito
from app.models.economy import (
    CurrencyType,
    TransactionLedger,
    TransactionType,
)
from app.models.user import User
from app.services.bank_service import BankService

# ---------------------------------------------------------------------------
# Skin rarity mapping: skin_color → rarity label
# ---------------------------------------------------------------------------
SKIN_RARITY_MAP: Dict[str, str] = {
    # Comun
    "pink":        "comun",
    "gray":        "comun",
    "gray_light":  "comun",
    "gray_dark":   "comun",
    # Rara
    "cyan":        "rara",
    "purple":      "rara",
    # Epica
    "neon":        "epica",
    "coral":       "epica",
    # Legendaria
    "gold":        "legendaria",
    # Astral
    "astral":      "astral",
}

# Skin multiplier by rarity label (FRJ/hour)
SKIN_MULTIPLIER: Dict[str, float] = {
    "comun":       0.05,
    "rara":        0.15,
    "epica":       0.40,
    "legendaria":  1.00,
    "astral":      2.50,
}

# ---------------------------------------------------------------------------
# Parts bonus: each body-part trait value maps to a rarity, then to a bonus.
# If a trait value is not mapped it defaults to comun (0.01).
# ---------------------------------------------------------------------------
_TRAIT_RARITY: Dict[str, Dict[str, str]] = {
    "gill_type": {
        "short":    "comun",
        "normal":   "comun",
        "feathery": "rara",
        "crown":    "epica",
        "phoenix":  "legendaria",
    },
    "eye_type": {
        "cute":     "comun",
        "derp":     "comun",
        "dreamer":  "rara",
        "cool":     "epica",
        "zen":      "legendaria",
    },
    "mouth_type": {
        "flat":     "comun",
        "smile":    "comun",
        "fang":     "rara",
        "rockstar": "epica",
        "divine":   "legendaria",
    },
    "tail_type": {
        "standard": "comun",
        "wavy":     "comun",
        "betta":    "rara",
        "plasma":   "epica",
    },
    "forehead_type": {
        "none":     "comun",
        "stripes":  "comun",
        "gem":      "rara",
        "halo":     "epica",
    },
    "limb_type": {
        "soft":     "comun",
        "claws":    "comun",
        "scales":   "rara",
        "coral":    "epica",
    },
}

PARTS_BONUS_BY_RARITY: Dict[str, float] = {
    "comun":       0.01,
    "rara":        0.03,
    "epica":       0.08,
    "legendaria":  0.20,
}

# Max accumulation window in hours
MAX_ACCUMULATION_HOURS: int = 12

# Hours without a game before staking freezes
PLAY_TO_STAKE_HOURS: int = 24


class StakingService:
    """Handles passive FRJ generation for staked Axolotitos."""

    # ------------------------------------------------------------------
    # Slot calculation
    # ------------------------------------------------------------------
    @staticmethod
    def get_staking_slots(user: User) -> int:
        """Returns total staking slots = cave_level + 1."""
        return user.cave_level + 1

    # ------------------------------------------------------------------
    # Hourly rate calculation
    # ------------------------------------------------------------------
    @staticmethod
    def get_skin_rarity(skin_color: str) -> str:
        """Map a skin color string to a rarity label. Defaults to 'comun'."""
        return SKIN_RARITY_MAP.get(skin_color.lower(), "comun")

    @staticmethod
    def get_part_rarity(trait_name: str, trait_value: str) -> str:
        """Map a single trait value to a rarity label. Defaults to 'comun'."""
        mapping = _TRAIT_RARITY.get(trait_name, {})
        return mapping.get(trait_value.lower(), "comun")

    @staticmethod
    def calculate_axolotito_hourly_rate(axolotito: Axolotito) -> float:
        """FRJ/hour = SkinMultiplier x (1 + 0.1 x Level) + SUM( PartsBonus )."""
        # 1. Skin multiplier
        skin_rarity = StakingService.get_skin_rarity(axolotito.skin_color)
        skin_mult = SKIN_MULTIPLIER.get(skin_rarity, 0.05)

        # 2. Level multiplier
        level_mult = 1 + 0.1 * axolotito.level

        # 3. Parts bonus — sum over all 6 trait fields
        trait_fields = [
            ("gill_type",     axolotito.gill_type),
            ("eye_type",      axolotito.eye_type),
            ("mouth_type",    axolotito.mouth_type),
            ("tail_type",     axolotito.tail_type),
            ("forehead_type", axolotito.forehead_type),
            ("limb_type",     axolotito.limb_type),
        ]
        parts_total = 0.0
        for tname, tval in trait_fields:
            part_rarity = StakingService.get_part_rarity(tname, tval)
            parts_total += PARTS_BONUS_BY_RARITY.get(part_rarity, 0.01)

        hourly_rate = skin_mult * level_mult + parts_total
        return round(hourly_rate, 6)

    # ------------------------------------------------------------------
    # Play-to-Stake check
    # ------------------------------------------------------------------
    @staticmethod
    def is_staking_active(user: User) -> bool:
        """Returns True if user has played at least 1 game in the last 24h."""
        if user.last_play_date is None:
            return False
        cutoff = datetime.utcnow() - timedelta(hours=PLAY_TO_STAKE_HOURS)
        return user.last_play_date >= cutoff

    # ------------------------------------------------------------------
    # Accrual calculation
    # ------------------------------------------------------------------
    @staticmethod
    def calculate_accrued_frj(
        axolotito: Axolotito,
        user: User,
    ) -> float:
        """Calculate new FRJ to add to accrued_unclaimed.

        Returns the *new* FRJ amount (not the running total). Returns 0 if
        play-to-stake is inactive.
        """
        # Play-to-Stake guard
        if not StakingService.is_staking_active(user):
            return 0.0

        hourly_rate = StakingService.calculate_axolotito_hourly_rate(axolotito)

        # Hours elapsed since last claim (or since creation if never claimed)
        now = datetime.utcnow()
        if axolotito.last_staking_claim is None:
            hours_elapsed = MAX_ACCUMULATION_HOURS  # first claim: full window
        else:
            delta = now - axolotito.last_staking_claim
            hours_elapsed = delta.total_seconds() / 3600.0

        # Cap at MAX_ACCUMULATION_HOURS
        effective_hours = min(hours_elapsed, MAX_ACCUMULATION_HOURS)
        new_accrued = hourly_rate * effective_hours

        # Cap total (already unclaimed + new) at 12 x hourly_rate
        max_total = MAX_ACCUMULATION_HOURS * hourly_rate
        total_after = axolotito.accrued_unclaimed + new_accrued
        if total_after > max_total:
            new_accrued = max_total - axolotito.accrued_unclaimed

        # Avoid tiny rounding errors going negative
        return round(max(0.0, new_accrued), 6)

    # ------------------------------------------------------------------
    # Claim single axolotito
    # ------------------------------------------------------------------
    @staticmethod
    def claim_staking_reward(
        session: Session,
        axolotito_id: int,
        user: User,
    ) -> Dict:
        """Claim the staking reward for a single axolotito.

        Steps:
          1. Verify ownership.
          2. Calculate accrued FRJ.
          3. SELECT FOR UPDATE on wallet, add FRJ.
          4. Write TransactionLedger row.
          5. Reset last_staking_claim / accrued_unclaimed.
        """
        require_feature(
            settings.ENABLE_PASSIVE_TOKEN_REWARDS,
            "passive_token_rewards",
        )
        from app.core.auth import require_tutorial
        require_tutorial(user)
        axolotito = session.exec(
            select(Axolotito).where(Axolotito.id == axolotito_id)
        ).first()

        if not axolotito:
            raise HTTPException(
                status_code=404,
                detail=f"Axolotito {axolotito_id} no encontrado.",
            )
        if axolotito.user_id != user.privy_did:
            raise HTTPException(
                status_code=403,
                detail="Este Axolotito no te pertenece.",
            )

        # Calculate new FRJ since last claim
        new_frj = StakingService.calculate_accrued_frj(axolotito, user)
        # Total to claim = previously unclaimed + new accumulation
        total_claimable = axolotito.accrued_unclaimed + new_frj

        if total_claimable <= 0:
            # Nothing to claim; still reset timer so accumulation starts fresh
            axolotito.last_staking_claim = datetime.utcnow()
            axolotito.accrued_unclaimed = 0.0
            session.add(axolotito)
            session.commit()
            return {
                "axolotito_id": axolotito_id,
                "claimed_frj": 0.0,
                "hourly_rate": StakingService.calculate_axolotito_hourly_rate(axolotito),
                "message": "No hay FRJ acumulado. El temporizador se ha reiniciado.",
            }

        # If resting (Limpiar Cenote), apply variable luck-based multiplier
        multiplier = 1.0
        if axolotito.status == "resting":
            import random
            luck = axolotito.stat_luck if axolotito.stat_luck is not None else 10.0
            luck_bonus = (luck / 100.0) * 0.8
            min_mult = 0.4 + luck_bonus
            max_mult = 1.8 + luck_bonus
            multiplier = random.SystemRandom().uniform(min_mult, max_mult)
            total_claimable = total_claimable * multiplier

        # Lock wallet with SELECT FOR UPDATE
        wallet = BankService.get_or_create_wallet(
            session, user.privy_did, for_update=True,
        )
        wallet.frijolitos = (wallet.frijolitos or 0.0) + total_claimable
        wallet.last_updated = datetime.utcnow()

        # Ledger entry
        desc_suffix = f" (Multiplicador de Limpieza: {round(multiplier, 2)}x)" if multiplier != 1.0 else ""
        ledger = TransactionLedger(
            user_id=user.privy_did,
            amount=total_claimable,
            currency=CurrencyType.FRIJOLITO,
            tx_type=TransactionType.STAKING_REWARD,
            description=f"Recompensa de staking — Axolotito #{axolotito_id} ({axolotito.name}){desc_suffix}",
        )

        # Reset axolotito accumulator
        hourly_rate = StakingService.calculate_axolotito_hourly_rate(axolotito)
        axolotito.last_staking_claim = datetime.utcnow()
        axolotito.accrued_unclaimed = 0.0

        session.add(wallet)
        session.add(ledger)
        session.add(axolotito)
        session.commit()

        return {
            "axolotito_id": axolotito_id,
            "claimed_frj": round(total_claimable, 6),
            "hourly_rate": round(hourly_rate, 6),
            "multiplier": round(multiplier, 4),
        }

    # ------------------------------------------------------------------
    # Claim all
    # ------------------------------------------------------------------
    @staticmethod
    def claim_all_staking(
        session: Session,
        user: User,
    ) -> Dict:
        """Claim staking rewards for Axolotitos within the user's active staking slots."""
        require_feature(
            settings.ENABLE_PASSIVE_TOKEN_REWARDS,
            "passive_token_rewards",
        )
        from app.core.auth import require_tutorial
        require_tutorial(user)
        slots = StakingService.get_staking_slots(user)
        # Order by id for a stable, deterministic slot assignment.
        axolotitos = session.exec(
            select(Axolotito)
            .where(Axolotito.user_id == user.privy_did)
            .order_by(Axolotito.id)
            .limit(slots)
        ).all()

        total_claimed = 0.0
        per_axolotito = []

        for axo in axolotitos:
            try:
                result = StakingService.claim_staking_reward(
                    session, axo.id, user,
                )
                per_axolotito.append(result)
                total_claimed += result["claimed_frj"]
            except HTTPException:
                # Skip axolotitos that errored (shouldn't happen but be safe)
                continue

        return {
            "amount_claimed": round(total_claimed, 6),
            "total_claimed_frj": round(total_claimed, 6),
            "axolotitos": per_axolotito,
        }

    @staticmethod
    def unstake_without_reward(
        session: Session,
        axolotito_id: int,
        user: User,
    ) -> Dict:
        """Release a staking position while forfeiting disabled token yield."""
        axolotito = session.exec(
            select(Axolotito)
            .where(Axolotito.id == axolotito_id)
            .with_for_update()
        ).first()
        if not axolotito:
            raise HTTPException(status_code=404, detail="Axolotito no encontrado.")
        if axolotito.user_id != user.privy_did:
            raise HTTPException(status_code=403, detail="Este Axolotito no te pertenece.")
        if axolotito.status not in {"studying", "resting"}:
            raise HTTPException(status_code=400, detail="Este Axolotito no está en staking.")

        axolotito.status = "idle"
        axolotito.accrued_unclaimed = 0
        axolotito.last_staking_claim = None
        session.add(axolotito)
        session.commit()
        session.refresh(axolotito)

        return {
            "message": (
                f"Axolotito #{axolotito_id} liberado de staking sin "
                "recompensa porque la emisión pasiva está deshabilitada."
            ),
            "claimed_frj": 0.0,
            "rewards_enabled": False,
            "axolotito": {
                "id": axolotito.id,
                "name": axolotito.name,
                "status": axolotito.status,
            },
        }

    # ------------------------------------------------------------------
    # Status query
    # ------------------------------------------------------------------
    @staticmethod
    def get_staking_status(
        user: User,
        axolotitos: List[Axolotito],
    ) -> Dict:
        """Return full staking status: slots, per-axo rates, caps, play-to-stake."""
        from app.core.auth import require_tutorial
        require_tutorial(user)
        slots = StakingService.get_staking_slots(user)
        rewards_enabled = settings.ENABLE_PASSIVE_TOKEN_REWARDS
        staking_active = rewards_enabled and StakingService.is_staking_active(user)

        axo_statuses = []
        for axo in axolotitos:
            hourly_rate = (
                StakingService.calculate_axolotito_hourly_rate(axo)
                if rewards_enabled
                else 0.0
            )
            max_cap = round(MAX_ACCUMULATION_HOURS * hourly_rate, 6)

            # Calculate current accrued
            current_accrued = axo.accrued_unclaimed if rewards_enabled else 0.0
            if staking_active and axo.last_staking_claim is not None:
                # Fresh accrual since last claim (read-only, don't persist)
                now = datetime.utcnow()
                delta = now - axo.last_staking_claim
                hours_elapsed = min(
                    delta.total_seconds() / 3600.0,
                    MAX_ACCUMULATION_HOURS,
                )
                fresh = hourly_rate * hours_elapsed
                current_accrued = min(
                    axo.accrued_unclaimed + fresh,
                    max_cap,
                )

            # Calculate lock remaining seconds
            lock_minutes = 2 if settings.BLOCKCHAIN_MODE == "local" else 60
            lock_remaining = 0
            if rewards_enabled and axo.last_staking_claim:
                elapsed = (datetime.utcnow() - axo.last_staking_claim).total_seconds()
                if elapsed < (lock_minutes * 60):
                    lock_remaining = int((lock_minutes * 60) - elapsed)

            axo_statuses.append({
                "id": axo.id,
                "name": axo.name,
                "level": axo.level,
                "skin_color": axo.skin_color,
                "hourly_rate": round(hourly_rate, 6),
                "accrued_unclaimed": round(current_accrued, 6),
                "max_cap_frj": max_cap,
                "cap_reached": current_accrued >= max_cap - 0.0001,
                "play_to_stake_active": staking_active,
                "last_claim_at": (
                    axo.last_staking_claim.isoformat()
                    if axo.last_staking_claim
                    else None
                ),
                "lock_remaining_seconds": lock_remaining,
            })

        total_accrued = sum(a["accrued_unclaimed"] for a in axo_statuses)

        return {
            "user_id": user.privy_did,
            "rewards_enabled": rewards_enabled,
            "staking_active": staking_active,
            "slots_total": slots,
            "slots_used": len([a for a in axolotitos if a.status in ["studying", "resting"]]),
            "total_accrued": round(total_accrued, 6),
            "play_to_stake_window_hours": PLAY_TO_STAKE_HOURS,
            "max_accumulation_hours": MAX_ACCUMULATION_HOURS,
            "axolotitos": axo_statuses,
        }
