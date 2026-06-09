"""
tutorial.py — Endpoints REST del sistema de tutorial del Axolotito.

Rutas:
  POST /api/v1/tutorial/start
  POST /api/v1/tutorial/next-step/{incubation_id}
  POST /api/v1/tutorial/complete/{incubation_id}
"""

import hashlib
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from app.core.auth import get_verified_user_id
from app.database import get_session
from app.models.items import ItemCatalog, ItemType, WebitoIncubation
from app.models.user import User
from app.services.dialogue_engine import DialogueEngine
from app.services.tutorial_service import TutorialService


def _stats_from_user_id(user_id: str) -> dict:
    """
    Genera stats iniciales únicos y reproducibles para el Webito del tutorial
    derivados del hash SHA-256 del user_id.

    Usa 16 bits por stat con un multiplicador mixto para máxima dispersión:
      bonus_luck:       10–100
      bonus_focus:      10–100
      bonus_stamina:    40–160  (rango amplio: afecta SAL y nature hyperactive)
      bonus_agility:    10–100
      bonus_salinity_adj: 10–40  (valor de salinidad; con base=0 ES la SAL final)
    """
    digest = hashlib.sha256(user_id.encode()).digest()  # 32 bytes

    def rng16(byte_a: int, byte_b: int, lo: float, hi: float) -> float:
        # Combina 2 bytes distintos para 16 bits de entropía
        val = (digest[byte_a] << 8) | digest[byte_b]  # 0–65535
        return round(lo + (val / 65535.0) * (hi - lo), 1)

    return {
        "bonus_luck":         rng16(0,  7,  10.0, 100.0),
        "bonus_focus":        rng16(1,  8,  10.0, 100.0),
        "bonus_stamina":      rng16(2,  9,  40.0, 160.0),
        "bonus_agility":      rng16(3, 10,  10.0, 100.0),
        "bonus_salinity_adj": rng16(4, 11,  10.0,  40.0),
    }

def _board_from_user_id(user_id: str, session: Session) -> list:
    """
    Genera 16 card IDs determinísticos desde user_id, replicando exactamente
    el algoritmo del frontend (ActBoardPreview.tsx):
      stringToSeed(userId)  → djb2 hash → seed
      seededBoard(seed)     → LCG Fisher-Yates shuffle de números 1–54 → primeros 16

    La función mapea los números de lotería (1–54) a los IDs reales del
    catálogo (ItemCatalog) usando item_metadata.numero_loteria.
    """
    # ── Paso 1: djb2 hash (idéntico a frontend stringToSeed) ──────────
    h = 5381
    for ch in user_id:
        h = ((h << 5) + h) + ord(ch)
        # Simular JS ToInt32: h = h & h
        h_u32 = h & 0xFFFFFFFF
        h = h_u32 - 0x100000000 if h_u32 >= 0x80000000 else h_u32
    seed = abs(h)

    # ── Paso 2: Cargar catálogo y mapear número_loteria → card_id ────
    all_cards = session.exec(
        select(ItemCatalog).where(ItemCatalog.item_type == ItemType.CARD)
    ).all()

    # Fallback: IDs secuenciales si no hay catálogo
    if not all_cards:
        return list(range(1, 17))

    num_to_cid: dict[int, int] = {}
    for c in all_cards:
        n = int((c.item_metadata or {}).get("numero_loteria", 0))
        if n and 1 <= n <= 54:
            num_to_cid[n] = c.id

    # ── Paso 3: LCG Fisher-Yates (idéntico a frontend seededBoard) ────
    nums = list(range(1, 55))  # números de lotería 1–54
    s = (seed if seed != 0 else 42) & 0xFFFFFFFF
    # Convertir a signed 32-bit para coincidir con JS (s se almacena como Number)
    s_signed = s - 0x100000000 if s >= 0x80000000 else s

    for i in range(len(nums) - 1, 0, -1):
        # JS: s = (s * 1664525 + 1013904223) & 0xffffffff
        s_unsigned = (s_signed * 1664525 + 1013904223) & 0xFFFFFFFF
        s_signed = s_unsigned - 0x100000000 if s_unsigned >= 0x80000000 else s_unsigned
        j = abs(s_signed) % (i + 1)
        nums[i], nums[j] = nums[j], nums[i]

    # Tomar primeros 16 y mapear a card IDs del catálogo
    selected = nums[:16]
    return [num_to_cid.get(n, n) for n in selected]


router = APIRouter()
_engine_dialogue = DialogueEngine()


def _get_active_incubation(
    incubation_id: int,
    user_id: str,
    session: Session,
) -> WebitoIncubation:
    """Busca la incubación y verifica que pertenezca al usuario autenticado."""
    incubation = session.get(WebitoIncubation, incubation_id)
    if not incubation:
        raise HTTPException(status_code=404, detail="Incubación no encontrada.")
    if incubation.user_id != user_id:
        raise HTTPException(status_code=403, detail="No tienes acceso a esta incubación.")
    return incubation


# ---------------------------------------------------------------------------
# POST /start
# ---------------------------------------------------------------------------

@router.post("/start")
def start_tutorial(
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
):
    """
    Inicia el tutorial. Busca o crea automáticamente la incubación tutorial del usuario.
    No requiere incubation_id — el backend lo gestiona.
    Devuelve: {id: int, phase: 1, dialogue: str, egg_intro_dialogue: str}
    """
    # Buscar incubación de tutorial en curso (phase 0–4)
    incubation = session.exec(
        select(WebitoIncubation)
        .where(WebitoIncubation.user_id == verified_user_id)
        .where(WebitoIncubation.tutorial_phase < 5)
        .order_by(WebitoIncubation.id)
    ).first()

    stats = _stats_from_user_id(verified_user_id)

    if not incubation:
        # Crear incubación tutorial con el primer EGG del catálogo como placeholder
        egg_item = session.exec(
            select(ItemCatalog).where(ItemCatalog.item_type == ItemType.EGG)
        ).first()
        if not egg_item:
            raise HTTPException(
                status_code=500,
                detail="Sin huevos en el catálogo. Contacta al administrador.",
            )
        incubation = WebitoIncubation(
            user_id=verified_user_id,
            item_id=egg_item.id,
            fecha_eclosion_estimada=datetime.utcnow() + timedelta(days=1),
            bonus_focus=stats["bonus_focus"],
            bonus_luck=stats["bonus_luck"],
            bonus_agility=stats["bonus_agility"],
            bonus_stamina=stats["bonus_stamina"],
            bonus_salinity_adj=stats["bonus_salinity_adj"],
        )
        session.add(incubation)
        session.commit()
        session.refresh(incubation)
    elif incubation.tutorial_phase == 0:
        # Incubación existe pero fue reseteada (phase=0): regenerar stats desde user_id
        incubation.bonus_focus        = stats["bonus_focus"]
        incubation.bonus_luck         = stats["bonus_luck"]
        incubation.bonus_agility      = stats["bonus_agility"]
        incubation.bonus_stamina      = stats["bonus_stamina"]
        incubation.bonus_salinity_adj = stats["bonus_salinity_adj"]
        # Limpiar cualquier base_stat_* heredado del refactor roto (evita doble conteo)
        incubation.base_stat_luck     = 0.0
        incubation.base_stat_focus    = 0.0
        incubation.base_stat_stamina  = 0.0
        incubation.base_stat_salinity = 0.0
        session.add(incubation)
        session.commit()
        session.refresh(incubation)

    # ── Garantizar que la tabla determinística del tutorial esté almacenada ──
    if not incubation.tutorial_board_card_ids:
        incubation.tutorial_board_card_ids = _board_from_user_id(
            verified_user_id, session
        )
        session.add(incubation)
        session.commit()
        session.refresh(incubation)

    # Si el tutorial ya estaba iniciado, devolver el estado actual sin reiniciar
    if incubation.tutorial_phase > 0:
        from app.services.dialogue_engine import DialogueEngine as _DE
        _nature = _DE().infer_personality_from_incubation(
            bonus_luck=incubation.bonus_luck,
            bonus_focus=incubation.bonus_focus,
            bonus_stamina=incubation.bonus_stamina,
        )
        return {
            "id": incubation.id,
            "phase": incubation.tutorial_phase,
            "egg_intro_dialogue": "Tu Webito ya está en el tutorial. ¡Continúa!",
            "dialogue": "El tutorial ya está en marcha.",
            "bonus_luck": incubation.bonus_luck,
            "bonus_focus": incubation.bonus_focus,
            "bonus_stamina": incubation.bonus_stamina,
            "bonus_salinity_adj": incubation.bonus_salinity_adj,
            "base_stat_luck": incubation.base_stat_luck,
            "base_stat_focus": incubation.base_stat_focus,
            "base_stat_stamina": incubation.base_stat_stamina,
            "base_stat_salinity": incubation.base_stat_salinity,
            "inferred_nature": _nature,
            "tutorial_act_index": incubation.tutorial_act_index,
        }

    result = TutorialService.start_tutorial(
        session=session,
        user_id=verified_user_id,
        incubation=incubation,
    )
    result["id"] = incubation.id
    result["tutorial_act_index"] = incubation.tutorial_act_index
    return result


# ---------------------------------------------------------------------------
# POST /play-game  — partida simulada para el tutorial (sin axolotito real)
# ---------------------------------------------------------------------------

import random as _random

_TUTORIAL_WINNING_LINES = [
    {0, 1, 2, 3}, {4, 5, 6, 7}, {8, 9, 10, 11}, {12, 13, 14, 15},
    {0, 4, 8, 12}, {1, 5, 9, 13}, {2, 6, 10, 14}, {3, 7, 11, 15},
    {0, 5, 10, 15}, {3, 6, 9, 12},
]

_tutorial_rng = _random.SystemRandom()


@router.post("/play-game")
def play_tutorial_game(
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
):
    """
    Simula una partida de lotería para el tutorial.
    No requiere Axolotito ni Tabla reales. Sin efectos de economía.
    Devuelve el mismo formato que /game/play.
    """
    from app.models.items import ItemCatalog, ItemType

    all_cards = session.exec(
        select(ItemCatalog).where(ItemCatalog.item_type == ItemType.CARD)
    ).all()

    if all_cards:
        card_ids = [c.id for c in all_cards]
        card_map = {c.id: c.name for c in all_cards}
        num_map  = {c.id: int((c.item_metadata or {}).get("numero_loteria", 0)) for c in all_cards}
    else:
        # Fallback sin catálogo
        card_ids = list(range(1, 55))
        card_map = {i: f"Carta {i}" for i in card_ids}
        num_map  = {i: i for i in card_ids}

    # Tablero del jugador: persistido desde /start (determinístico por user_id).
    # El tablero del bot sigue siendo aleatorio (nunca se muestra en el preview).
    incubation = session.exec(
        select(WebitoIncubation)
        .where(WebitoIncubation.user_id == verified_user_id)
        .where(WebitoIncubation.tutorial_phase >= 1)
        .where(WebitoIncubation.tutorial_phase < 5)
        .order_by(WebitoIncubation.id)
    ).first()

    if not incubation or not incubation.tutorial_board_card_ids:
        raise HTTPException(
            status_code=400,
            detail="Tutorial no iniciado o sin tabla registrada. Llama a /start primero.",
        )

    player_board = incubation.tutorial_board_card_ids
    bot_board    = _tutorial_rng.sample(card_ids, min(16, len(card_ids)))

    PLAYER_FOCUS = 50.0
    BOT_FOCUS    = 50.0
    player_miss_chance = max(0.0, min(0.3, (100.0 - PLAYER_FOCUS) * 0.003))
    bot_miss_chance    = max(0.0, min(0.3, (100.0 - BOT_FOCUS)    * 0.003))

    def _check_line(marked: set) -> bool:
        return any(line.issubset(marked) for line in _TUTORIAL_WINNING_LINES)

    deck = card_ids.copy()
    _tutorial_rng.shuffle(deck)

    player_marked: set = set()
    bot_marked:    set = set()
    turns = 0
    is_win = False
    winning_line: Optional[list] = None
    drawn_history: list = []
    player_misses: list = []

    for card_id in deck:
        turns += 1
        card_name = card_map.get(card_id, f"Carta #{card_id}")
        drawn_history.append(card_name)

        if card_id in bot_board:
            bot_idx = bot_board.index(card_id)
            if _tutorial_rng.random() >= bot_miss_chance:
                bot_marked.add(bot_idx)

        if card_id in player_board:
            p_idx = player_board.index(card_id)
            if _tutorial_rng.random() < player_miss_chance:
                player_misses.append(card_name)
            else:
                player_marked.add(p_idx)

        player_won = _check_line(player_marked)
        bot_won    = _check_line(bot_marked)

        if player_won or bot_won:
            is_win = player_won
            if player_won:
                # Find the specific line the player completed
                for line in _TUTORIAL_WINNING_LINES:
                    if line.issubset(player_marked):
                        winning_line = sorted(list(line))
                        break
            else:
                # Bot won — find the specific line
                for line in _TUTORIAL_WINNING_LINES:
                    if line.issubset(bot_marked):
                        winning_line = sorted(list(line))
                        break
            break

    # Fallback: if deck exhausted without winner, pick bot's most-advanced line for display
    if winning_line is None and not is_win:
        best_line = max(
            _TUTORIAL_WINNING_LINES,
            key=lambda line: len(line & bot_marked),
            default=set()
        )
        winning_line = sorted(list(best_line)) if best_line else []

    bot_board_nums    = [[num_map.get(cid, 0) for cid in bot_board]]
    player_board_nums = [num_map.get(cid, 0) for cid in player_board]
    name_to_num       = {card_map[cid].lower(): num_map.get(cid, 0)
                         for cid in card_ids if card_map.get(cid)}

    return {
        "resultado":            "victoria" if is_win else "derrota",
        "room_title":           "Tutorial",
        "winner":               "Tú" if is_win else "Bot 1",
        "turns":                turns,
        "prize_gal":            0,
        "board_xp_gained":      0,
        "board_level_current":  1,
        "axo_xp_gained":        0,
        "axo_level_current":    1,
        "energy_remaining":     100,
        "drawn_cards_sample":   drawn_history[:turns],
        "player_missed_cards":  player_misses,
        "bot_count":            1,
        "bot_focus":            BOT_FOCUS,
        "player_miss_chance_pct": round(player_miss_chance * 100, 1),
        "lucky_save_occurred":  False,
        "lucky_save_turn":      None,
        "win_streak_after":     0,
        "streak_bonus_pct":     0,
        "streak_broken":        False,
        "bot_board_nums":       bot_board_nums,
        "bot_board_ids":        [None],
        "bot_marked_indices":   [list(bot_marked)],
        "winning_line":         winning_line or [],   # completed line indices (empty if none)
        "winner_bot_index":     0 if not is_win else None,  # always bot 0 in tutorial
        "player_board_nums":    player_board_nums,
        "name_to_num":          name_to_num,
        "imprinting":           None,
    }


# ---------------------------------------------------------------------------
# POST /next-step/{incubation_id}
# ---------------------------------------------------------------------------

class NextStepBody(BaseModel):
    won: Optional[bool] = None


@router.post("/next-step/{incubation_id}")
def tutorial_next_step(
    incubation_id: int,
    body: NextStepBody = Body(default=NextStepBody()),
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
):
    """
    Avanza una fase del tutorial.
    Fase 1→2→3→4 (karma)→5 (completado).
    `won` (opcional): resultado real de la partida jugada — se usa para actualizar bonus_stamina en fase 1.
    Devuelve: {phase, dialogue, bonus_stamina?, karma?, ...}
    """
    incubation = _get_active_incubation(incubation_id, verified_user_id, session)
    return TutorialService.advance_phase(
        session=session,
        user_id=verified_user_id,
        incubation=incubation,
        won=body.won,
    )


# ---------------------------------------------------------------------------
# POST /complete/{incubation_id}
# ---------------------------------------------------------------------------

@router.post("/complete/{incubation_id}")
def complete_tutorial(
    incubation_id: int,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
):
    """
    Aplica el bonus de karma, marca tutorial_completed=True en el User.
    Devuelve: {completed, karma, bonus, dialogue, next_step: "hatch"}
    """
    incubation = _get_active_incubation(incubation_id, verified_user_id, session)
    return TutorialService.complete_tutorial(
        session=session,
        user_id=verified_user_id,
        incubation=incubation,
    )


class SaveActBody(BaseModel):
    act_index: int


@router.post("/save-act/{incubation_id}")
def save_tutorial_act(
    incubation_id: int,
    body: SaveActBody,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
):
    """
    Guarda el acto actual en el que se encuentra el usuario en el tutorial.
    """
    incubation = _get_active_incubation(incubation_id, verified_user_id, session)
    incubation.tutorial_act_index = body.act_index
    session.add(incubation)
    session.commit()
    return {
        "ok": True,
        "tutorial_act_index": incubation.tutorial_act_index,
    }
