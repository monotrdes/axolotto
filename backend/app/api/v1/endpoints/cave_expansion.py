from __future__ import annotations
"""
cave_expansion.py — Endpoints de expansión del Cenote (sistema de cueva única que crece).

Rutas:
  GET  /api/v1/cave/status
  POST /api/v1/cave/expand
  POST /api/v1/cave/expand/accelerate
  GET  /api/v1/cave/public/{user_id}
  POST /api/v1/cave/visit/{user_id}

Reemplaza webito_slots.py. El jugador tiene UNA cueva que se expande en 8 niveles.
Cada nivel agrega spots, decor slots, y eventualmente mesa de juego.
"""

import math
import traceback
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, func, select

from app.core.auth import get_verified_user_id
from app.database import get_session
from app.core.config import frj_to_internal, frj_to_display, axf_to_internal, axf_to_display
from app.models.axolotito import Axolotito
from app.models.economy import (
    CurrencyType,
    TransactionLedger,
    TransactionType,
    Wallet,
)
from app.models.items import ItemCatalog, ItemType, Rarity
from app.models.user import User
from app.services.bank_service import BankService

router = APIRouter()

MAX_CAVE_LEVEL = 8

# ── Definición de Niveles del Cenote ─────────────────────────────────────────
CAVE_LEVEL_DEFINITIONS: dict[int, dict] = {
    2: {
        "name": "La Gruta",
        "lore": "Las algas luminosas revelan una nueva cámara en la roca. Tu cenote respira.",
        "spots": 2,
        "decor_slots": 4,
        "has_table": False,
        "reward_egg": "fase1",
        "excavation_hours": 2.0,
        "cost_frj": 500,
        "path_logro": {
            "label": "Juega 10 partidas + Axolotito principal nivel 3",
            "description": "Demuestra que eres un habitante del cenote.",
            "check": lambda user, wallet, stats: (
                stats.get("total_games", 0) >= 10
                and stats.get("main_axo_level", 0) >= 3
            ),
            "error": "Necesitas 10 partidas jugadas y tu Axolotito principal debe alcanzar nivel 3.",
        },
    },
    3: {
        "name": "La Caverna",
        "lore": "El espíritu de la Lotería ilumina un nuevo salón. Hay espacio para una mesa.",
        "spots": 3,
        "decor_slots": 6,
        "has_table": True,
        "table_seats": 2,
        "reward_egg": "fase1_plus",
        "excavation_hours": 6.0,
        "cost_frj": 1500,
        "path_logro": {
            "label": "Gana 3 partidas + racha de 3 días",
            "description": "La suerte favorece a los constantes.",
            "check": lambda user, wallet, stats: (
                stats.get("total_wins", 0) >= 3
                and stats.get("current_streak", 0) >= 3
            ),
            "error": "Necesitas 3 victorias y una racha de 3 días consecutivos jugando.",
        },
    },
    4: {
        "name": "El Salón",
        "lore": "El cuarzo del cenote resuena con energía. Tu cueva ahora es un salón.",
        "spots": 4,
        "decor_slots": 8,
        "has_table": True,
        "table_seats": 4,
        "reward_egg": "fase2",
        "excavation_hours": 12.0,
        "cost_frj": 4000,
        "path_logro": {
            "label": "Gana 1 Jackpot",
            "description": "Solo los campeones expanden su salón.",
            "check": lambda user, wallet, stats: (
                stats.get("jackpots_won", 0) >= 1
            ),
            "error": "Necesitas haber ganado al menos 1 Jackpot para expandir a El Salón.",
        },
    },
    5: {
        "name": "El Santuario",
        "lore": "Las profundidades del cenote exigen poder. Pocos llegan hasta aquí.",
        "spots": 5,
        "decor_slots": 10,
        "has_table": True,
        "table_seats": 6,
        "reward_egg": "fase2_nature",
        "excavation_hours": 24.0,
        "cost_frj": 8000,
        "path_logro": {
            "label": "Axolotito principal nivel 15",
            "description": "Tu compañero debe demostrar su poder.",
            "check": lambda user, wallet, stats: (
                stats.get("main_axo_level", 0) >= 15
            ),
            "error": "Tu Axolotito principal debe alcanzar nivel 15 para expandir a El Santuario.",
        },
    },
    6: {
        "name": "El Abismo",
        "lore": "La oscuridad revela secretos. Solo los más dedicados o los miembros del club pueden descender más.",
        "spots": 6,
        "decor_slots": 12,
        "has_table": True,
        "table_seats": 8,
        "reward_egg": "fase2_nature",
        "excavation_hours": 36.0,
        "cost_frj": 15000,
        "path_logro": {
            "label": "50 partidas totales + 100 feeds, o VIP Coral+",
            "description": "La dedicación total o la membresía abren el abismo.",
            "check": lambda user, wallet, stats: (
                (stats.get("total_games", 0) >= 50 and stats.get("feeds_given", 0) >= 100)
                or user.vip_tier in ("coral", "dorado", "axolite")
            ),
            "error": (
                "Necesitas 50 partidas jugadas y 100 alimentaciones a tus Axolotitos, "
                "o ser miembro VIP Coral, Dorado o Axolite."
            ),
        },
    },
    7: {
        "name": "El Templo",
        "lore": "Un templo ancestral emerge de la roca. La música del agua llena el espacio.",
        "spots": 7,
        "decor_slots": 14,
        "has_table": True,
        "table_seats": 8,
        "reward_egg": "astral",
        "excavation_hours": 48.0,
        "cost_frj": 30000,
        "path_logro": {
            "label": "100 partidas totales + 15 victorias, o VIP Dorado+",
            "description": "Solo los más dedicados o los VIP de alto nivel acceden al Templo.",
            "check": lambda user, wallet, stats: (
                (stats.get("total_games", 0) >= 100 and stats.get("total_wins", 0) >= 15)
                or user.vip_tier in ("dorado", "axolite")
            ),
            "error": (
                "Necesitas 100 partidas jugadas y 15 victorias, "
                "o ser miembro VIP Dorado o Axolite para acceder al Templo."
            ),
        },
    },
    8: {
        "name": "Palacio Astral",
        "lore": (
            "El cenote se conecta con el cosmos. Tu cueva es ahora un palacio "
            "entre dimensiones. Las estrellas nadan a tu alrededor."
        ),
        "spots": 8,
        "decor_slots": 16,
        "has_table": True,
        "table_seats": 8,
        "reward_egg": "astral",
        "excavation_hours": 72.0,
        "cost_frj": 60000,
        "path_logro": {
            "label": "200 partidas totales + Axolotito Épico/Legendario, o VIP Axolite",
            "description": "La dedicación suprema o la membresía élite abren el palacio.",
            "check": lambda user, wallet, stats: (
                (stats.get("total_games", 0) >= 200 and stats.get("has_epic_legendary_axo", False))
                or user.vip_tier == "axolite"
            ),
            "error": (
                "Necesitas 200 partidas jugadas y un Axolotito Épico o Legendario (piel gold/astral), "
                "o ser miembro VIP Axolite para acceder al Palacio Astral."
            ),
        },
    },
}

# ── Bonos pasivos por nivel ─────────────────────────────────────────────────
CAVE_PASSIVE_BONUSES: dict[int, dict] = {
    1: {},
    2: {"gal_multiplier": 1.02},           # +2% FRJ
    3: {"extra_starting_card": True},       # +1 carta en mano inicial
    4: {"booster_chance_bonus": 0.05},      # +5% prob booster
    5: {"global_incubation_slot": 1},       # +1 slot incubación global
    6: {"p2p_fee_reduction": 0.05},         # -5% comisión P2P
    7: {"monthly_foil_booster": 1},         # 1 booster foil/mes
    8: {"axg_multiplier": 1.10},            # +10% AXF en ecosistema
}


# ── Helpers ──────────────────────────────────────────────────────────────────

def _get_user_stats(session: Session, user_id: str) -> dict:
    """Recolecta estadísticas del jugador para verificar logros."""
    from app.models.board import PlayerBoard

    boards = session.exec(
        select(PlayerBoard).where(
            PlayerBoard.user_id == user_id,
            PlayerBoard.is_dead == False,
        )
    ).all()

    total_games = sum(b.games_played or 0 for b in boards)
    total_wins = sum(b.games_won or 0 for b in boards)

    main_axo = session.exec(
        select(Axolotito)
        .where(Axolotito.user_id == user_id)
        .order_by(Axolotito.created_at)
    ).first()
    main_axo_level = main_axo.level if main_axo else 1

    jackpots_won = session.exec(
        select(TransactionLedger)
        .where(TransactionLedger.user_id == user_id)
        .where(TransactionLedger.tx_type == TransactionType.REWARD)
        .where(TransactionLedger.description.ilike("%jackpot%"))
    ).all()
    jackpot_count = len(jackpots_won)

    user = session.exec(select(User).where(User.privy_did == user_id)).first()
    current_streak = user.daily_play_streak if user else 0

    # Feeds: contamos registros de TransactionLedger con descripción "Alimentar"
    # feed_axolotito() en game_service usa tx_type=MARKET_BUY + description="Alimentar a..."
    feed_records = session.exec(
        select(TransactionLedger)
        .where(TransactionLedger.user_id == user_id)
        .where(TransactionLedger.description.ilike("%alimentar%"))
    ).all()
    feeds_given = len(feed_records)

    # Axolotito épico/legendario: proxy via skin_color ("gold" = épico, "astral" = legendario)
    # El modelo Axolotito no tiene campo rarity, se infiere del skin_color premium
    epic_legendary_axo = session.exec(
        select(Axolotito)
        .where(Axolotito.user_id == user_id)
        .where(Axolotito.skin_color.in_(["gold", "astral"]))
    ).first()
    has_epic_legendary_axo = epic_legendary_axo is not None

    # Partidas multijugador: no existe campo en DB actualmente; retorna 0
    total_games_multiplayer = 0

    return {
        "total_games": total_games,
        "total_wins": total_wins,
        "main_axo_level": main_axo_level,
        "jackpots_won": jackpot_count,
        "current_streak": current_streak,
        "feeds_given": feeds_given,
        "has_epic_legendary_axo": has_epic_legendary_axo,
        "total_games_multiplayer": total_games_multiplayer,
    }


def _get_next_level_info(current_level: int, user=None, wallet=None, stats=None) -> dict | None:
    """Devuelve la info del siguiente nivel, o None si ya está al máximo.

    Cuando se pasan user, wallet y stats, el resultado incluye cost_frj_effective,
    excavation_hours_effective y achievement_met con descuentos VIP aplicados.
    """
    next_level = current_level + 1
    if next_level > MAX_CAVE_LEVEL:
        return None

    level_def = CAVE_LEVEL_DEFINITIONS[next_level]

    is_vip = user.is_vip if user is not None else False
    cost_frj = level_def.get("cost_frj", 0)
    cost_frj_effective = int(cost_frj * 0.5) if is_vip else cost_frj
    excavation_hours = level_def["excavation_hours"]
    excavation_hours_effective = excavation_hours * 0.5 if is_vip else excavation_hours

    # Evaluar logro solo cuando se dispone de todos los parámetros
    achievement_met = False
    if user is not None and wallet is not None and stats is not None:
        check_fn = (level_def.get("path_logro") or {}).get("check")
        if check_fn:
            try:
                achievement_met = bool(check_fn(user, wallet, stats))
            except Exception:
                achievement_met = False

    info: dict = {
        "level": next_level,
        "name": level_def["name"],
        "lore": level_def["lore"],
        "spots": level_def["spots"],
        "decor_slots": level_def["decor_slots"],
        "has_table": level_def["has_table"],
        "table_seats": level_def.get("table_seats", 0),
        "reward_egg": level_def["reward_egg"],
        "excavation_hours": excavation_hours,
        "cost_frj": cost_frj,
        "cost_frj_effective": cost_frj_effective,
        "excavation_hours_effective": excavation_hours_effective,
        "achievement_met": achievement_met,
        "paths": [],
    }

    if level_def.get("path_logro"):
        info["paths"].append({
            "type": "logro",
            "label": level_def["path_logro"]["label"],
            "description": level_def["path_logro"]["description"],
        })

    return info


def _grant_egg_reward(session: Session, user_id: str, reward_type: str | None) -> dict | None:
    """Otorga un huevo de recompensa al expandir la cueva."""
    if not reward_type:
        return None

    egg = None

    if reward_type == "astral":
        egg = session.exec(
            select(ItemCatalog)
            .where(ItemCatalog.item_type == ItemType.EGG)
            .where(ItemCatalog.is_active == True)
            .where(ItemCatalog.name.ilike("%astral%"))
        ).first()
        if not egg:
            eggs = session.exec(
                select(ItemCatalog)
                .where(ItemCatalog.item_type == ItemType.EGG)
                .where(ItemCatalog.is_active == True)
            ).all()
            for e in eggs:
                if (e.item_metadata or {}).get("is_astral"):
                    egg = e
                    break

    elif reward_type in ("fase2", "fase2_nature"):
        # Filtrado Python-side: .contains() en columna JSON genera LIKE (inválido en PostgreSQL).
        eggs = session.exec(
            select(ItemCatalog)
            .where(ItemCatalog.item_type == ItemType.EGG)
            .where(ItemCatalog.is_active == True)
        ).all()
        for e in eggs:
            if (e.item_metadata or {}).get("fase", 1) >= 2:
                egg = e
                break

    elif reward_type == "fase1_plus":
        # Filtrado Python-side: .contains() en columna JSON genera LIKE (inválido en PostgreSQL).
        candidates = session.exec(
            select(ItemCatalog)
            .where(ItemCatalog.item_type == ItemType.EGG)
            .where(ItemCatalog.is_active == True)
            .where(ItemCatalog.rarity.in_([Rarity.RARE, Rarity.EPIC, Rarity.LEGENDARY]))
        ).all()
        for e in candidates:
            if (e.item_metadata or {}).get("fase", 1) >= 1:
                egg = e
                break

    if not egg:
        egg = session.exec(
            select(ItemCatalog)
            .where(ItemCatalog.item_type == ItemType.EGG)
            .where(ItemCatalog.is_active == True)
            .order_by(ItemCatalog.id)
        ).first()

    if not egg:
        return None

    from app.services.drop_service import _add_to_inventory
    _add_to_inventory(session, user_id, egg.id)

    if reward_type == "astral":
        session.add(TransactionLedger(
            user_id=user_id,
            amount=0,
            currency=CurrencyType.GEMA_ALGA,
            tx_type=TransactionType.WEBITO_UNLOCK,
            description=f"Nivel {8} — Webito Astral de recompensa: {egg.name}",
            item_id=egg.id,
        ))

    return {
        "id": egg.id,
        "name": egg.name,
        "reward_type": reward_type,
    }


# ── GET /status ──────────────────────────────────────────────────────────────

@router.get("/status")
def get_cave_status(
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
):
    """Devuelve el estado actual del Cenote del usuario autenticado."""
    user = session.exec(
        select(User).where(User.privy_did == verified_user_id).with_for_update()
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    # ── AUTO-RESOLVER EXPANSIÓN COMPLETADA POR TIEMPO ──
    # with_for_update() previene que dos requests concurrentes otorguen el huevo dos veces
    if user.cave_expansion_target_level and user.cave_expansion_started_at:
        level_def = CAVE_LEVEL_DEFINITIONS.get(user.cave_expansion_target_level, {})
        total_hours = level_def.get("excavation_hours", 24)
        elapsed = datetime.utcnow() - user.cave_expansion_started_at
        if elapsed >= timedelta(hours=total_hours):
            target_level = user.cave_expansion_target_level
            user.cave_level = target_level
            user.webito_slots_unlocked = target_level
            user.cave_expansion_target_level = None
            user.cave_expansion_started_at = None
            session.add(user)
            session.commit()
            session.refresh(user)

    current_level = user.cave_level
    stats = _get_user_stats(session, verified_user_id)

    # Wallet leída antes de _get_next_level_info para poder pasar como parámetro
    wallet = session.exec(select(Wallet).where(Wallet.user_id == verified_user_id)).first()

    next_level = _get_next_level_info(current_level, user=user, wallet=wallet, stats=stats)

    # Calcular bonos pasivos acumulados
    passive_bonuses = {}
    for lvl in range(1, current_level + 1):
        bonus = CAVE_PASSIVE_BONUSES.get(lvl, {})
        for key, value in bonus.items():
            if key in ("gal_multiplier", "axg_multiplier"):
                passive_bonuses[key] = passive_bonuses.get(key, 1.0) * value
            elif key in ("booster_chance_bonus", "p2p_fee_reduction"):
                passive_bonuses[key] = passive_bonuses.get(key, 0.0) + value
            elif key == "extra_starting_card":
                passive_bonuses[key] = True
            elif key in ("global_incubation_slot", "monthly_foil_booster"):
                passive_bonuses[key] = passive_bonuses.get(key, 0) + value

    # Estado de excavación
    expansion = None
    if user.cave_expansion_target_level and user.cave_expansion_started_at:
        level_def = CAVE_LEVEL_DEFINITIONS.get(user.cave_expansion_target_level, {})
        total_hours = level_def.get("excavation_hours", 24)
        elapsed = datetime.utcnow() - user.cave_expansion_started_at
        remaining = timedelta(hours=total_hours) - elapsed
        expansion = {
            "target_level": user.cave_expansion_target_level,
            "target_name": level_def.get("name", f"Nivel {user.cave_expansion_target_level}"),
            "started_at": user.cave_expansion_started_at.isoformat(),
            "total_hours": total_hours,
            "remaining_seconds": max(0, int(remaining.total_seconds())),
            "can_accelerate": remaining.total_seconds() > 0,
        }

    # Construir historial de niveles
    all_levels = []
    for lvl in range(1, MAX_CAVE_LEVEL + 1):
        if lvl == 1:
            all_levels.append({
                "level": 1,
                "name": "El Nicho",
                "unlocked": True,
                "lore": "Tu primer espacio en el Cenote. El tutorial te lo obsequió.",
                "spots": 1,
                "decor_slots": 2,
                "has_table": False,
            })
        else:
            level_def = CAVE_LEVEL_DEFINITIONS.get(lvl, {})
            all_levels.append({
                "level": lvl,
                "name": level_def.get("name", f"Nivel {lvl}"),
                "unlocked": lvl <= current_level,
                "lore": level_def.get("lore", ""),
                "spots": level_def.get("spots", 0),
                "decor_slots": level_def.get("decor_slots", 0),
                "has_table": level_def.get("has_table", False),
                "table_seats": level_def.get("table_seats", 0),
            })

    current_def = CAVE_LEVEL_DEFINITIONS.get(current_level, {})
    current_info = {
        "level": current_level,
        "name": current_def.get("name", "El Nicho") if current_level > 1 else "El Nicho",
        "spots": current_def.get("spots", 1) if current_level > 1 else 1,
        "decor_slots": current_def.get("decor_slots", 2) if current_level > 1 else 2,
        "has_table": current_def.get("has_table", False) if current_level > 1 else False,
        "table_seats": current_def.get("table_seats", 0) if current_level > 1 else 0,
    }

    wallet_data = {
        "frijolitos": frj_to_display(wallet.frijolitos) if wallet else 0.0,
        "axofichas": axf_to_display(wallet.axofichas) if wallet else 0.0,
    }

    total_axolotitos = session.exec(
        select(func.count(Axolotito.id))
        .where(Axolotito.user_id == verified_user_id)
    ).one_or_none() or 0

    return {
        "current": current_info,
        "max_level": MAX_CAVE_LEVEL,
        "cave_name": user.cave_name,
        "cave_decorations": user.cave_decorations,
        "stats": stats,
        "wallet": wallet_data,
        "next_level": next_level,
        "expansion": expansion,
        "passive_bonuses": passive_bonuses,
        "all_levels": all_levels,
        "axolotito_count": total_axolotitos,
    }


# ── POST /expand ─────────────────────────────────────────────────────────────

@router.post("/expand")
def start_expansion(
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
):
    """
    Inicia la expansión al siguiente nivel del Cenote.

    Requiere cumplir el logro obligatorio del nivel y pagar el costo en FRJ (Frijolitos).
    Los miembros VIP reciben 50% de descuento en FRJ y 50% de reducción en el tiempo
    de excavación. No existe un camino de pago directo con AXF para saltarse el logro.

    La expansión tiene un timer de excavación (2h a 72h según nivel).
    Se puede acelerar con AXF vía POST /expand/accelerate.
    """
    user = session.exec(select(User).where(User.privy_did == verified_user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    current_level = user.cave_level
    target_level = current_level + 1

    if target_level > MAX_CAVE_LEVEL:
        raise HTTPException(
            status_code=400,
            detail=f"Ya tienes el nivel máximo ({MAX_CAVE_LEVEL}) del Cenote.",
        )

    # Verificar que no hay expansión en curso
    if user.cave_expansion_target_level and user.cave_expansion_started_at:
        level_def = CAVE_LEVEL_DEFINITIONS.get(user.cave_expansion_target_level, {})
        total_hours = level_def.get("excavation_hours", 24)
        elapsed = datetime.utcnow() - user.cave_expansion_started_at
        if elapsed < timedelta(hours=total_hours):
            raise HTTPException(
                status_code=409,
                detail=(
                    f"Ya hay una excavación en curso para el nivel {user.cave_expansion_target_level}. "
                    f"Espera a que termine o acelera con AXF."
                ),
            )

    level_def = CAVE_LEVEL_DEFINITIONS[target_level]

    if not level_def.get("path_logro"):
        raise HTTPException(
            status_code=400,
            detail=f"El nivel {target_level} ('{level_def['name']}') no tiene logro definido.",
        )

    # Verificar logro
    stats = _get_user_stats(session, verified_user_id)
    wallet = BankService.get_or_create_wallet(session, verified_user_id, for_update=True)
    check_fn = level_def["path_logro"]["check"]
    if not check_fn(user, wallet, stats):
        raise HTTPException(
            status_code=403,
            detail=level_def["path_logro"]["error"],
        )

    # Calcular costo FRJ con descuento VIP del 50%
    is_vip = user.is_vip
    cost_frj = level_def["cost_frj"]
    cost_frj_effective = int(cost_frj * 0.5) if is_vip else cost_frj

    # Verificar saldo FRJ suficiente (wallet ya bloqueado con FOR UPDATE via BankService)
    cost_frj_effective_internal = frj_to_internal(cost_frj_effective)
    if wallet.frijolitos < cost_frj_effective_internal:
        raise HTTPException(
            status_code=403,
            detail=(
                f"Frijolitos insuficientes. Iniciar excavación de '{level_def['name']}' "
                f"cuesta {cost_frj_effective} FRJ"
                + (" (descuento VIP 50% aplicado)" if is_vip else "")
                + f". Tienes {frj_to_display(wallet.frijolitos):.1f} FRJ."
            ),
        )

    # Descontar FRJ
    wallet.frijolitos -= cost_frj_effective_internal
    session.add(wallet)

    # Calcular tiempo de excavación con descuento VIP del 50%
    excavation_hours = level_def["excavation_hours"]
    excavation_hours_effective = excavation_hours * 0.5 if is_vip else excavation_hours

    # Truco de timestamp: mover started_at hacia atrás para que el timer VIP
    # sea efectivamente la mitad. El check de auto-complete en GET /status usa
    # total_hours (base), así que si started_at = now - (hours - effective_hours),
    # el jugador VIP espera solo excavation_hours_effective horas reales.
    time_offset = timedelta(hours=excavation_hours - excavation_hours_effective)
    started_at = datetime.utcnow() - time_offset

    user.cave_expansion_target_level = target_level
    user.cave_expansion_started_at = started_at
    session.add(user)

    session.add(TransactionLedger(
        user_id=verified_user_id,
        amount=cost_frj_effective_internal,
        currency=CurrencyType.FRIJOLITO,
        tx_type=TransactionType.WEBITO_UNLOCK,
        description=(
            f"Excavación iniciada — Cenote Nivel {target_level} '{level_def['name']}' "
            f"— {cost_frj_effective} FRJ"
            + (" (VIP 50% desc.)" if is_vip else "")
        ),
    ))

    session.commit()
    session.refresh(user)

    return {
        "expanded": False,
        "excavation_started": True,
        "current_level": current_level,
        "target_level": target_level,
        "target_name": level_def["name"],
        "excavation_hours": excavation_hours,
        "excavation_hours_effective": excavation_hours_effective,
        "remaining_seconds": int(excavation_hours_effective * 3600),
        "frj_spent": cost_frj_effective,
        "vip_discount_applied": is_vip,
        "message": (
            f"¡Excavación iniciada! '{level_def['name']}' estará lista en "
            f"{excavation_hours_effective:.1f} horas. "
            f"Se descontaron {cost_frj_effective} FRJ. "
            f"Puedes acelerar con AXF."
        ),
    }


# ── POST /expand/accelerate ──────────────────────────────────────────────────

@router.post("/expand/accelerate")
def accelerate_expansion(
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
):
    """
    Acelera la excavación en curso usando AXF.
    Ratio: 4 AXF por hora restante (1 AXF cada 15 minutos), redondeado arriba.
    Si el timer llega a 0, la expansión se completa instantáneamente.
    """
    user = session.exec(select(User).where(User.privy_did == verified_user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    if not user.cave_expansion_target_level or not user.cave_expansion_started_at:
        raise HTTPException(status_code=400, detail="No hay excavación en curso.")

    target_level = user.cave_expansion_target_level
    level_def = CAVE_LEVEL_DEFINITIONS.get(target_level)
    if not level_def:
        raise HTTPException(status_code=500, detail="Definición de nivel no encontrada.")

    total_hours = level_def["excavation_hours"]
    elapsed = datetime.utcnow() - user.cave_expansion_started_at
    remaining = timedelta(hours=total_hours) - elapsed
    remaining_hours = max(0, remaining.total_seconds() / 3600)

    try:
        if remaining_hours <= 0:
            # Ya debería haberse completado, forzar finalización
            user.cave_level = target_level
            user.webito_slots_unlocked = target_level
            user.cave_expansion_target_level = None
            user.cave_expansion_started_at = None
            session.add(user)
            session.commit()
            session.refresh(user)

            next_level = _get_next_level_info(target_level)
            return {
                "completed": True,
                "current_level": target_level,
                "level_name": level_def["name"],
                "next_level": next_level,
                "message": f"¡{level_def['name']} completada! El Cenote se expande.",
            }

        # Calcular costo de aceleración: 4 AXF por hora, redondeado arriba
        axf_needed = max(1, math.ceil(remaining_hours * 4))

        axf_needed_internal = axf_to_internal(axf_needed)

        wallet = BankService.get_or_create_wallet(session, verified_user_id, for_update=True)
        if wallet.axofichas < axf_needed_internal:
            raise HTTPException(
                status_code=403,
                detail=(
                    f"Saldo insuficiente. Acelerar la excavación cuesta {axf_needed} AXF "
                    f"({remaining_hours:.1f}h restantes × 4 AXF/h). Tienes {axf_to_display(wallet.axofichas):.1f} AXF."
                ),
            )

        wallet.axofichas -= axf_needed_internal
        session.add(wallet)

        session.add(TransactionLedger(
            user_id=verified_user_id,
            amount=axf_needed_internal,
            currency=CurrencyType.AXOFICHA,
            tx_type=TransactionType.WEBITO_UNLOCK,
            description=f"Aceleración excavación Nivel {target_level} '{level_def['name']}' — {axf_needed} AXF",
        ))

        # Completar expansión (sin huevo de recompensa — se compra en tienda)
        user.cave_level = target_level
        user.webito_slots_unlocked = target_level
        user.cave_expansion_target_level = None
        user.cave_expansion_started_at = None
        session.add(user)
        session.commit()
        session.refresh(user)

        next_level = _get_next_level_info(target_level)
        return {
            "completed": True,
            "accelerated": True,
            "axf_spent": axf_needed,
            "current_level": target_level,
            "level_name": level_def["name"],
            "next_level": next_level,
            "message": (
                f"¡{level_def['name']} desbloqueada con {axf_needed} AXF! "
                f"El Cenote se expande."
            ),
        }
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        tb = traceback.format_exc()
        print(f"🔥 accelerate_expansion ERROR: {e}\n{tb}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno al acelerar: {str(e)}",
        )


# ── GET /public/{user_id} ────────────────────────────────────────────────────

@router.get("/public/{user_id}")
def get_public_cave(
    user_id: str,
    session: Session = Depends(get_session),
):
    """
    Devuelve datos públicos de la cueva de otro jugador (modo visita).
    """
    user = session.exec(select(User).where(User.privy_did == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    # Verificar privacidad
    # Por ahora, si no es pública, mostrar datos mínimos
    nickname = user.nickname or f"Jugador#{str(user.id)[:6]}"

    current_def = CAVE_LEVEL_DEFINITIONS.get(user.cave_level, {})
    current_info = {
        "level": user.cave_level,
        "name": current_def.get("name", "El Nicho") if user.cave_level > 1 else "El Nicho",
        "spots": current_def.get("spots", 1) if user.cave_level > 1 else 1,
        "has_table": current_def.get("has_table", False) if user.cave_level > 1 else False,
    }

    return {
        "user_id": user_id,
        "nickname": nickname,
        "avatar_url": user.avatar_url,
        "vip_tier": user.vip_tier if user.is_vip else None,
        "cave": current_info,
        "cave_name": user.cave_name,
        "cave_decorations": user.cave_decorations,
    }


# ── POST /visit/{user_id} ────────────────────────────────────────────────────

@router.post("/visit/{user_id}")
def visit_cave(
    user_id: str,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
):
    """
    Registra una visita a la cueva de otro jugador y deja un aplauso.
    Máximo 1 aplauso por visita.
    """
    if verified_user_id == user_id:
        raise HTTPException(status_code=400, detail="No puedes visitar tu propia cueva.")

    visited_user = session.exec(select(User).where(User.privy_did == user_id)).first()
    if not visited_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    # TODO: Registrar visita en tabla de analytics/eventos
    # Por ahora, devolver confirmación simple

    return {
        "visited": True,
        "cave_owner": visited_user.nickname or f"Jugador#{str(visited_user.id)[:6]}",
        "message": "¡Has visitado este Cenote! Dejaste un aplauso.",
    }
