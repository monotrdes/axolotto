"""
tutorial_service.py — Lógica de negocio para el tutorial del Axolotito.

Fases del tutorial (guardadas en WebitoIncubation.tutorial_phase):
  0 = sin tutorial activo
  1 = Fase 1: Partida auto de Salinidad
  2 = Fase 2: Partida auto de Focus + Agility (con momentos de intervención manual)
  3 = Fase 3: Partida auto de Luck + Stamina (Cheat Astral disponible)
  4 = Evaluación de karma
  5 = Tutorial completado

Karma:
  "lucky"  → bonus_luck > 60 O ganó la mayoría de mini-simulaciones  → +50 GAL
  "salty"  → default                                                   → +1 consumible "gotas_antiescarcha"
"""

import random
from datetime import datetime
from typing import Optional

from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.economy import (
    CurrencyType,
    TransactionLedger,
    TransactionType,
)
from app.models.items import ItemCatalog, PlayerInventory, WebitoIncubation
from app.models.board import PlayerBoard
from app.models.axolotito import Axolotito
from app.models.user import User
from app.services.bank_service import BankService
from app.services.dialogue_engine import DialogueContext, DialogueEngine

_rng = random.SystemRandom()
_engine = DialogueEngine()

# Número de rondas simuladas por fase de mini-simulación
PHASE_ROUNDS = 5

# Nombre del consumible que se otorga como bonus karma salty
GOTAS_ITEM_NAME = "gotas_antiescarcha"

# GAL que se otorgan como bonus karma lucky
LUCKY_GAL_BONUS = 50.0


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------

def _simulate_phase_wins(
    stat_a: float,
    stat_b: float,
    rounds: int = PHASE_ROUNDS,
) -> int:
    """
    Simula `rounds` mini-rondas de lotería usando dos stats como ventaja.
    Devuelve la cantidad de rondas ganadas.
    El umbral de victoria por ronda es > 50% de probabilidad combinada normalizada.
    """
    wins = 0
    for _ in range(rounds):
        # Cada stat contribuye a la probabilidad en [0, 1]
        prob = (stat_a / 200.0) + (stat_b / 200.0)  # máximo teórico = 1.0
        if _rng.random() < prob:
            wins += 1
    return wins


def _get_incubation_stat(incubation: WebitoIncubation, stat_name: str) -> float:
    """Lee un bonus de stat del huevo. Devuelve 0.0 si el campo no existe."""
    return float(getattr(incubation, f"bonus_{stat_name}", 0.0))


def _find_gotas_item(session: Session) -> Optional[ItemCatalog]:
    """Busca el ítem de gotas_antiescarcha en el catálogo."""
    return session.exec(
        select(ItemCatalog).where(ItemCatalog.name == GOTAS_ITEM_NAME)
    ).first()


# ---------------------------------------------------------------------------
# Servicio principal
# ---------------------------------------------------------------------------

class TutorialService:
    """Controla el flujo del tutorial por fases y aplica recompensas de karma."""

    @staticmethod
    def start_tutorial(
        session: Session,
        user_id: str,
        incubation: WebitoIncubation,
    ) -> dict:
        """
        Inicia el tutorial (fase 0 → 1).
        Solo puede llamarse una vez por huevo (phase == 0).
        """
        if incubation.tutorial_phase != 0:
            raise HTTPException(
                status_code=400,
                detail=f"El tutorial ya fue iniciado (fase {incubation.tutorial_phase}).",
            )

        incubation.tutorial_phase = 1
        incubation.tutorial_act_index = 0
        session.add(incubation)
        session.commit()
        session.refresh(incubation)

        inferred_nature = _engine.infer_personality_from_incubation(
            bonus_luck=incubation.bonus_luck,
            bonus_focus=incubation.bonus_focus,
            bonus_stamina=incubation.bonus_stamina,
        )

        dialogue = _engine.get_line(
            stat="salinity",
            value=30.0,  # salinidad inicial neutra para la intro
            context=DialogueContext.TUTORIAL_PHASE_1,
            nature=inferred_nature,
        )
        egg_intro_dialogue = (
            "El cascarón de tu Webito empieza a vibrar... "
            "el Cenote lo está reconociendo. ¡El tutorial ha comenzado!"
        )

        return {
            "phase": 1,
            "fresh_start": True,
            "dialogue": dialogue,
            "egg_intro_dialogue": egg_intro_dialogue,
            "bonus_luck": incubation.bonus_luck,
            "bonus_focus": incubation.bonus_focus,
            "bonus_stamina": incubation.bonus_stamina,
            "bonus_salinity_adj": incubation.bonus_salinity_adj,
            "base_stat_luck": incubation.base_stat_luck,
            "base_stat_focus": incubation.base_stat_focus,
            "base_stat_stamina": incubation.base_stat_stamina,
            "base_stat_salinity": incubation.base_stat_salinity,
            "inferred_nature": inferred_nature,
            "tutorial_act_index": 0,
        }

    @staticmethod
    def advance_phase(
        session: Session,
        user_id: str,
        incubation: WebitoIncubation,
        won: Optional[bool] = None,
    ) -> dict:
        """
        Avanza una fase del tutorial.
        Fase 1→2, 2→3, 3→4 (karma), 4→5 (completado + bonus).
        """
        current = incubation.tutorial_phase

        if current == 0:
            raise HTTPException(
                status_code=400,
                detail="El tutorial no ha iniciado. Llama a /start primero.",
            )
        if current >= 5:
            raise HTTPException(
                status_code=400,
                detail="El tutorial ya fue completado.",
            )

        inferred_nature = _engine.infer_personality_from_incubation(
            bonus_luck=incubation.bonus_luck,
            bonus_focus=incubation.bonus_focus,
            bonus_stamina=incubation.bonus_stamina,
        )

        result: dict = {}

        # ------------------------------------------------------------------ #
        # FASE 1 → 2: Mini-simulación de Salinidad
        # ------------------------------------------------------------------ #
        if current == 1:
            salinity_proxy = _get_incubation_stat(incubation, "stamina")  # stamina ~ resistencia a sal
            wins = _simulate_phase_wins(salinity_proxy, salinity_proxy)

            # Actualizar bonus_salinity_adj (SAL) según el resultado. NO se toca stamina:
            # PILA debe quedar fija durante todo el tutorial.
            # Magnitud debe coincidir con la predicción del frontend (ActGame ResultStatDisplay SAL_DELTA).
            result_won = won if won is not None else (wins > PHASE_ROUNDS / 2)
            sal_delta = -10.0 if result_won else 10.0  # ganar baja SAL (bueno), perder la sube
            new_sal = max(0.0, min(100.0, incubation.bonus_salinity_adj + sal_delta))
            incubation.bonus_salinity_adj = new_sal

            incubation.tutorial_phase = 2
            incubation.tutorial_act_index = 5  # Acto 6 OJO
            session.add(incubation)
            session.commit()

            dialogue = _engine.get_line(
                stat="salinity",
                value=new_sal,
                context=DialogueContext.TUTORIAL_PHASE_2,
                nature=inferred_nature,
            )
            result = {
                "phase": 2,
                "dialogue": dialogue,
                "mini_wins": wins,
                "mini_total": PHASE_ROUNDS,
                "bonus_salinity_adj": new_sal,
            }

        # ------------------------------------------------------------------ #
        # FASE 2 → 3: Mini-simulación de Focus + Agility
        # ------------------------------------------------------------------ #
        elif current == 2:
            focus = _get_incubation_stat(incubation, "focus")
            agility = _get_incubation_stat(incubation, "agility")
            wins = _simulate_phase_wins(focus, agility)

            # Actualizar bonus_focus según resultado real de la partida (o mini-sim como fallback)
            result_won = won if won is not None else (wins > PHASE_ROUNDS / 2)
            focus_delta = 10.0 if result_won else -10.0
            new_focus = max(10.0, min(100.0, incubation.bonus_focus + focus_delta))
            incubation.bonus_focus = new_focus

            # Momento de intervención manual — se informa al cliente
            focus_moment_dialogue = _engine.get_line(
                stat="focus",
                value=new_focus,
                context=DialogueContext.TUTORIAL_FOCUS_MOMENT,
                nature=inferred_nature,
            )
            agility_moment_dialogue = _engine.get_line(
                stat="agility",
                value=agility,
                context=DialogueContext.TUTORIAL_AGILITY_MOMENT,
                nature=inferred_nature,
            )

            incubation.tutorial_phase = 3
            incubation.tutorial_act_index = 6  # Acto 7 SUERTE_PILA
            session.add(incubation)
            session.commit()

            dialogue = _engine.get_line(
                stat="focus",
                value=new_focus,
                context=DialogueContext.TUTORIAL_PHASE_3,
                nature=inferred_nature,
            )
            result = {
                "phase": 3,
                "dialogue": dialogue,
                "focus_moment_dialogue": focus_moment_dialogue,
                "agility_moment_dialogue": agility_moment_dialogue,
                "mini_wins": wins,
                "bonus_focus": new_focus,
                "mini_total": PHASE_ROUNDS,
            }

        # ------------------------------------------------------------------ #
        # FASE 3 → 4: Mini-simulación de Luck + Stamina (Cheat Astral)
        # ------------------------------------------------------------------ #
        elif current == 3:
            luck = _get_incubation_stat(incubation, "luck")
            stamina = _get_incubation_stat(incubation, "stamina")
            wins = _simulate_phase_wins(luck, stamina)

            # Actualizar bonus_luck según resultado real de la partida (o mini-sim como fallback)
            result_won = won if won is not None else (wins > PHASE_ROUNDS / 2)
            luck_delta = 10.0 if result_won else -10.0
            new_luck = max(10.0, min(100.0, incubation.bonus_luck + luck_delta))
            incubation.bonus_luck = new_luck

            luck_moment_dialogue = _engine.get_line(
                stat="luck",
                value=new_luck,
                context=DialogueContext.TUTORIAL_LUCK_MOMENT,
                nature=inferred_nature,
            )

            # Evaluar karma preliminar para empezar a construirlo
            karma = TutorialService._evaluate_karma(
                incubation=incubation,
                phase_wins=wins,
            )
            incubation.tutorial_karma = karma
            incubation.tutorial_phase = 4
            incubation.tutorial_act_index = 7  # Acto 8 KARMA
            session.add(incubation)
            session.commit()

            karma_dialogue = _engine.get_karma_line(karma)
            result = {
                "phase": 4,
                "dialogue": _engine.get_line(
                    stat="luck",
                    value=new_luck,
                    context=DialogueContext.TUTORIAL_PHASE_1,
                    nature=inferred_nature,
                ),
                "luck_moment_dialogue": luck_moment_dialogue,
                "karma": karma,
                "karma_dialogue": karma_dialogue,
                "mini_wins": wins,
                "mini_total": PHASE_ROUNDS,
                "bonus_luck": new_luck,
            }

        # ------------------------------------------------------------------ #
        # FASE 4 → 5: Confirmación de karma y aplicación de bonus
        # ------------------------------------------------------------------ #
        elif current == 4:
            karma = incubation.tutorial_karma or "salty"
            karma_bonus = TutorialService._apply_karma_bonus(
                session=session,
                user_id=user_id,
                incubation=incubation,
                karma=karma,
            )
            incubation.tutorial_phase = 5
            incubation.tutorial_act_index = 11  # Completado
            session.add(incubation)
            session.commit()

            result = {
                "phase": 5,
                "dialogue": _engine.get_karma_line(karma),
                "karma": karma,
                "karma_bonus": karma_bonus,
                "next_step": "hatch",
            }

        return result

    @staticmethod
    def complete_tutorial(
        session: Session,
        user_id: str,
        incubation: WebitoIncubation,
    ) -> dict:
        """
        Aplica el bonus de karma, marca tutorial_completed=True en el User,
        y mueve la incubación a phase=5 si no estaba ya.
        """
        print(f"🐣 complete_tutorial llamado: incubation_id={incubation.id}, user_id={user_id}", flush=True)

        if incubation.tutorial_phase < 4:
            print(f"❌ Tutorial incompleto: paso {incubation.tutorial_phase}/4+", flush=True)
            raise HTTPException(
                status_code=400,
                detail=f"Debes completar todas las fases antes. Fase actual: {incubation.tutorial_phase}.",
            )

        print(f"📊 webito: current_step={incubation.tutorial_phase}, completed={incubation.tutorial_phase >= 5}", flush=True)

        karma = incubation.tutorial_karma or "salty"

        # Solo aplica el bonus si estamos llegando desde phase 4 (no repetir en phase 5)
        karma_bonus: Optional[dict] = None
        if incubation.tutorial_phase == 4:
            karma_bonus = TutorialService._apply_karma_bonus(
                session=session,
                user_id=user_id,
                incubation=incubation,
                karma=karma,
            )
            incubation.tutorial_phase = 5
            incubation.tutorial_act_index = 11  # Completado
            session.add(incubation)

        # Marcar tutorial completado en el usuario
        user = session.exec(select(User).where(User.privy_did == user_id)).first()
        if user and not user.tutorial_completed:
            user.tutorial_completed = True
            session.add(user)

        session.commit()

        # Marcar el webito como listo para eclosionar (equivalente al imprinting completado)
        incubation.imprinting_complete = True
        # Asegurar que la fecha de eclosión ya se cumplió para poder eclosionar de inmediato
        incubation.fecha_eclosion_estimada = datetime.utcnow()
        session.add(incubation)
        session.commit()

        # Auto-eclosión: el axolotito nace al instante al terminar el tutorial.
        # Import diferido para evitar import circular (incubation importa servicios).
        from app.api.v1.endpoints.incubation import _perform_hatch

        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado.")

        # Capturar tutorial_board_card_ids antes del hatch: _perform_hatch
        # hace session.delete(incubation) + commit() → el objeto queda inválido.
        tutorial_board_card_ids = incubation.tutorial_board_card_ids

        print(f"🐣 Llamando _perform_hatch para webito={incubation.id}", flush=True)
        axolotito_result = _perform_hatch(incubation, user, session)
        axo = axolotito_result.get("axolotito", {})
        print(f"✅ Hatch exitoso: {axo.get('name')} (id={axo.get('id')})", flush=True)

        # ── Crear PlayerBoard con la tabla del tutorial y asignarlo al axolotito ──
        if axo.get("id"):
            axolotito = session.get(Axolotito, axo["id"])
            if axolotito:
                axolotito.is_tutorial = True
                axolotito.is_main = True
                
                if tutorial_board_card_ids:
                    tutorial_board = PlayerBoard(
                        user_id=user_id,
                        name="Tabla Tutorial",
                        card_ids=tutorial_board_card_ids,
                        card_first_editions=[False] * 16,
                        is_tutorial=True,
                    )
                    session.add(tutorial_board)
                    session.flush()  # obtener ID autogenerado
                    
                    axolotito.assigned_board_id = tutorial_board.id
                    print(f"🎯 Tabla Tutorial #{tutorial_board.id} asignada a {axolotito.name}", flush=True)
                
                session.add(axolotito)
                session.commit()

        # Check for pending corcholata reward
        from app.models.promo import PendingReward
        pending_result = session.exec(
            select(PendingReward).where(
                PendingReward.user_id == user_id,
                PendingReward.claimed == False,
            )
        ).first()
        has_pending = pending_result is not None

        dialogue = _engine.get_karma_line(karma)
        return {
            "completed": True,
            "karma": karma,
            "bonus": karma_bonus,
            "dialogue": dialogue,
            "next_step": "hatch",
            "axolotito_name": axo.get("name"),
            "axolotito_id": axo.get("id"),
            "axolotito": axo,
            "has_pending_reward": has_pending,
        }

    # ------------------------------------------------------------------ #
    # Métodos internos
    # ------------------------------------------------------------------ #

    @staticmethod
    def _evaluate_karma(
        incubation: WebitoIncubation,
        phase_wins: int,
    ) -> str:
        """
        Determina el karma del Axolotito.
        lucky: bonus_luck > 60 O ganó la mayoría de mini-rondas de la última fase.
        salty: default.
        """
        luck_bonus = _get_incubation_stat(incubation, "luck")
        majority_wins = phase_wins > (PHASE_ROUNDS / 2)

        if luck_bonus > 60 or majority_wins:
            return "lucky"
        return "salty"

    @staticmethod
    def _apply_karma_bonus(
        session: Session,
        user_id: str,
        incubation: WebitoIncubation,
        karma: str,
    ) -> dict:
        """
        Aplica el bonus de karma al usuario.
        lucky  → +50 GAL
        salty  → +1 gotas_antiescarcha en inventario
        En ambos casos escribe en TransactionLedger.
        """
        if karma == "lucky":
            wallet = BankService.get_or_create_wallet(session, user_id, for_update=True)
            wallet.frijolitos += LUCKY_GAL_BONUS
            ledger = TransactionLedger(
                user_id=user_id,
                amount=LUCKY_GAL_BONUS,
                currency=CurrencyType.FRIJOLITO,
                tx_type=TransactionType.TUTORIAL_BONUS,
                description=f"Bonus karma lucky — tutorial huevo #{incubation.id}",
            )
            session.add(wallet)
            session.add(ledger)
            session.commit()
            return {"type": "frj", "amount": LUCKY_GAL_BONUS, "currency": "FRJ"}

        else:  # salty
            gotas = _find_gotas_item(session)
            if gotas:
                inv = session.exec(
                    select(PlayerInventory)
                    .where(PlayerInventory.user_id == user_id)
                    .where(PlayerInventory.item_id == gotas.id)
                    .with_for_update()
                ).first()

                if inv:
                    inv.quantity += 1
                    session.add(inv)
                else:
                    inv = PlayerInventory(
                        user_id=user_id,
                        item_id=gotas.id,
                        quantity=1,
                    )
                    session.add(inv)

                ledger = TransactionLedger(
                    user_id=user_id,
                    amount=1,
                    currency=CurrencyType.FRIJOLITO,
                    tx_type=TransactionType.TUTORIAL_BONUS,
                    description=f"Bonus karma salty: gotas_antiescarcha — tutorial huevo #{incubation.id}",
                )
                session.add(ledger)
                session.commit()
                return {"type": "item", "item": GOTAS_ITEM_NAME, "quantity": 1}

            # Si no existe el ítem en catálogo, dar FRJ como fallback
            wallet = BankService.get_or_create_wallet(session, user_id, for_update=True)
            wallet.frijolitos += 10.0
            ledger = TransactionLedger(
                user_id=user_id,
                amount=10.0,
                currency=CurrencyType.FRIJOLITO,
                tx_type=TransactionType.TUTORIAL_BONUS,
                description=f"Bonus karma salty (fallback FRJ) — tutorial huevo #{incubation.id}",
            )
            session.add(wallet)
            session.add(ledger)
            session.commit()
            return {"type": "frj", "amount": 10.0, "currency": "FRJ", "note": "gotas no disponibles en catalogo"}
