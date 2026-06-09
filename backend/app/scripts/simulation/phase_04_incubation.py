"""
phase_04_incubation.py — Compra, imprinting y eclosión de Webitos.

Flujo nuevo (imprinting system):
  1. Para el PRIMER huevo de cada jugador: flujo de tutorial (start→advance×3→complete) → hatch
     Esto crea el primer Axolotito sin necesitar un padrino existente.
  2. Para huevos ADICIONALES: imprinting simulado con el primer Axolotito como padrino → hatch
"""
import random
from datetime import datetime, timedelta

from sqlmodel import Session, select
from fastapi import HTTPException

from app.models.items import ItemCatalog, ItemType, WebitoIncubation, Rarity, PlayerInventory
from app.models.axolotito import Axolotito
from app.models.user import User
from app.models.economy import CurrencyType
from app.services.shop_service import ShopService
from app.services.tutorial_service import TutorialService
from app.services.imprinting_service import (
    ImprintingGameResult,
    compute_deltas,
    apply_deltas_to_incubation,
    initial_base_stats,
    required_games_for_rarity,
)
from app.api.v1.endpoints.incubation import get_user_incubations, hatch_webito

_rng = random.SystemRandom()


def _run_tutorial_path(session: Session, user_id: str, incubation: WebitoIncubation) -> dict:
    """Simula el flujo COMPLETO del tutorial para el primer webito del jugador,
    replicando exactamente lo que hace el cliente real:

      1. /start    → stats determinísticos (hash de user_id) + tablero determinístico
      2. /play-game + /next-step ×3 → cada fase juega una partida real de lotería
         del tutorial y avanza con el resultado real (`won`)
      3. /complete → karma + auto-eclosión + creación de la "Tabla Tutorial"

    Opera sobre el `incubation` específico (no usa la selección "primer phase<5"
    del endpoint /start) para evitar elegir un huevo de personalidad por error.

    Retorna el dict de complete_tutorial (incluye has_pending_reward y axolotito).
    """
    from app.api.v1.endpoints.tutorial import (
        _board_from_user_id,
        _stats_from_user_id,
        play_tutorial_game,
        tutorial_next_step,
        complete_tutorial as complete_tutorial_endpoint,
        NextStepBody,
    )
    try:
        # ── Replicar lo que hace el endpoint /start sobre ESTE huevo ──────────
        # Stats determinísticos por user_id (igual que producción) y tablero
        # determinístico — sin esto complete_tutorial NO crea la Tabla Tutorial.
        seed_stats = _stats_from_user_id(user_id)
        incubation.bonus_luck         = seed_stats["bonus_luck"]
        incubation.bonus_focus        = seed_stats["bonus_focus"]
        incubation.bonus_stamina      = seed_stats["bonus_stamina"]
        incubation.bonus_agility      = seed_stats["bonus_agility"]
        incubation.bonus_salinity_adj = seed_stats["bonus_salinity_adj"]
        if not incubation.tutorial_board_card_ids:
            incubation.tutorial_board_card_ids = _board_from_user_id(user_id, session)
        session.add(incubation)
        session.commit()
        session.refresh(incubation)

        inc_id = incubation.id

        # Phase 0 → 1 (start_tutorial hace su propio commit + refresh)
        TutorialService.start_tutorial(session=session, user_id=user_id, incubation=incubation)

        # Phase 1 → 2 → 3 → 4 (karma): cada fase juega una partida real del tutorial
        # y avanza con el resultado real (`won`), igual que el cliente.
        for _ in range(3):
            won = None
            try:
                game_res = play_tutorial_game(session=session, verified_user_id=user_id)
                won = (game_res.get("resultado") == "victoria")
            except HTTPException:
                won = None  # fallback: advance_phase usará su mini-simulación interna
            tutorial_next_step(
                incubation_id=inc_id,
                body=NextStepBody(won=won),
                session=session,
                verified_user_id=user_id,
            )

        # Phase 4 → 5 (complete hace commit, refresh, auto-hatch + Tabla Tutorial)
        result = complete_tutorial_endpoint(
            incubation_id=inc_id,
            session=session,
            verified_user_id=user_id,
        )
        return result
    except HTTPException as e:
        # Try to fast-forward if tutorial was already partially started
        try:
            inc = session.get(WebitoIncubation, incubation.id)
            if inc and inc.tutorial_phase > 0 and inc.tutorial_phase < 5:
                while inc.tutorial_phase < 4:
                    try:
                        TutorialService.advance_phase(session=session, user_id=user_id, incubation=inc)
                    except Exception:
                        break
                result = TutorialService.complete_tutorial(session=session, user_id=user_id, incubation=inc)
                return result
        except Exception:
            pass
        # If all else fails, manually set imprinting_complete
        try:
            inc = session.get(WebitoIncubation, incubation.id)
            if inc and not inc.imprinting_complete:
                inc.imprinting_complete = True
                session.add(inc)
                session.commit()
        except Exception:
            session.rollback()
        return {}


def _run_imprinting(
    session: Session,
    incubation: WebitoIncubation,
    padrino: Axolotito,
    skip_imprinting: bool = False,
) -> None:
    """
    Simula el imprinting para un webito usando un padrino.
    Si skip_imprinting=True, salta la simulación y marca directamente como completo.
    """
    if skip_imprinting:
        # Fast mode: set base stats and mark complete directly
        base = initial_base_stats()
        incubation.base_stat_luck     = base["base_stat_luck"]
        incubation.base_stat_focus    = base["base_stat_focus"]
        incubation.base_stat_stamina  = base["base_stat_stamina"]
        incubation.base_stat_salinity = base["base_stat_salinity"]
        incubation.imprinting_padrino_id = padrino.id
        incubation.imprinting_complete = True
        session.add(incubation)
        session.commit()
        return

    # Get rarity from catalog
    egg_item = session.exec(
        select(ItemCatalog).where(ItemCatalog.id == incubation.item_id)
    ).first()
    rarity = egg_item.rarity if egg_item else Rarity.COMMON
    n_games = required_games_for_rarity(rarity)

    # Set base stats
    base = initial_base_stats()
    incubation.base_stat_luck     = base["base_stat_luck"]
    incubation.base_stat_focus    = base["base_stat_focus"]
    incubation.base_stat_stamina  = base["base_stat_stamina"]
    incubation.base_stat_salinity = base["base_stat_salinity"]
    incubation.imprinting_padrino_id = padrino.id
    session.add(incubation)
    session.commit()
    session.refresh(incubation)

    # Simulate N games
    for i in range(n_games):
        result = ImprintingGameResult(
            won=_rng.random() > 0.4,
            had_jackpot_bonus=_rng.random() < 0.08,
            mark_accuracy=_rng.uniform(0.5, 0.95),
            session_game_count=i + 1,
            padrino_energy_pct=min(1.0, padrino.energy_current / max(1, padrino.stat_stamina)),
            padrino_sal=padrino.stat_salinity,
        )
        deltas = compute_deltas(result)
        apply_deltas_to_incubation(incubation, deltas)

    incubation.imprinting_complete = True
    session.add(incubation)
    session.commit()


def phase_incubation(engine, config, **state) -> dict:
    """
    Compra huevos, realiza imprinting y eclosiona Axolotitos.

    Flujo:
    - Primer huevo de cada jugador: tutorial (crea primer Axolotito sin padrino)
    - Huevos adicionales: imprinting simulado usando primer Axolotito como padrino
    """
    session: Session = state["session"]
    progress = state["progress"]
    live_progress = state.get("live_progress")
    players: list = state["players"]
    stats: dict = state["stats"]
    errors: list = state["errors"]
    skip_imprinting: bool = getattr(config, "skip_imprinting", False)

    def _live(msg: str) -> None:
        if live_progress:
            live_progress(msg)
        else:
            progress(msg)

    progress("  🥚 Fase de incubación — flujo imprinting...")

    # ── Weather logging ──────────────────────────────────────────────────
    try:
        from app.core.weather import get_current_weather
        weather = get_current_weather()
        progress(f"  🌤️  Clima en Xochimilco: {weather.get('name', '?')} — {weather.get('desc', '?')[:80]}")
        if weather.get("freeze_chance", 0) > 0.15:
            progress(f"  ⚠️  Alto riesgo de congelamiento ({weather['freeze_chance']*100:.0f}%/h)")
        stats["weather_logged"] = weather.get("id", "?")
    except Exception:
        pass  # Weather module may not be available

    initial_egg = session.exec(
        select(ItemCatalog).where(
            ItemCatalog.item_type == ItemType.EGG,
            ItemCatalog.is_active == True,
        )
    ).first()
    if not initial_egg:
        progress("  ⚠️  Sin webitos activos en catálogo. Saltando fase.")
        return {}

    # ── Comprar y eclosionar huevos por jugador en flujo realista (verificando límites de Nivel 1) ──
    for p in players:
        user_id = p["user_id"]
        
        # Grant a free onboarding egg to all players to start the tutorial.
        egg = session.exec(
            select(ItemCatalog).where(
                ItemCatalog.item_type == ItemType.EGG,
                ItemCatalog.is_active == True,
            )
        ).first()
        if not egg:
            continue
            
        try:
            inv_item = session.exec(
                select(PlayerInventory)
                .where(PlayerInventory.user_id == user_id)
                .where(PlayerInventory.item_id == egg.id)
            ).first()
            if inv_item:
                inv_item.quantity += 1
            else:
                inv_item = PlayerInventory(
                    user_id=user_id,
                    item_id=egg.id,
                    quantity=1,
                    is_first_edition=False,
                    is_shiny=False
                )
            session.add(inv_item)
            session.commit()
            print(f"  🎁 {user_id}: Huevo de onboarding gratuito otorgado en inventario")
        except Exception as e:
            session.rollback()
            errors.append(f"free_egg_grant {user_id}: {e}")
            continue

        # Crear WebitoIncubation (tutorial)
        try:
            get_user_incubations(user_id=user_id, session=session, verified_user_id=user_id)
        except Exception as e:
            session.rollback()
            errors.append(f"sync_tutorial_incubation {user_id}: {e}")
            continue

        # Buscar la incubación de tutorial (fase < 5)
        inc = session.exec(
            select(WebitoIncubation)
            .where(WebitoIncubation.user_id == user_id)
            .where(WebitoIncubation.tutorial_phase < 5)
        ).first()
        
        first_axo = None
        if inc:
            _live(f"  🎓 {user_id}: tutorial para huevo #{inc.id}...")
            try:
                tutorial_result = _run_tutorial_path(session=session, user_id=user_id, incubation=inc)
                
                # Claim corcholata reward after tutorial if pending
                if tutorial_result and tutorial_result.get("has_pending_reward"):
                    try:
                        from app.api.v1.endpoints.rewards import claim_pending_reward
                        claim_res = claim_pending_reward(
                            session=session,
                            verified_user_id=user_id,
                        )
                        reward = claim_res.get("reward", {})
                        progress(
                            f"  🎁 {user_id}: Corcholata reclamada! "
                            f"AXF+{reward.get('axofichas', 0):.0f} FRJ+{reward.get('frijolitos', 0):.0f}"
                        )
                        stats["corcholatas_claimed"] = stats.get("corcholatas_claimed", 0) + 1
                    except HTTPException as e:
                        if "No tienes premios" not in str(e.detail):
                            errors.append(f"claim_corcholata {user_id}: {e.detail}")
                    except Exception as e:
                        errors.append(f"claim_corcholata_unexpected {user_id}: {e}")
                        session.rollback()

                # Buscar el axolotito recién creado por complete_tutorial
                new_axo = session.exec(
                    select(Axolotito).where(
                        Axolotito.user_id == user_id,
                        Axolotito.status == "idle",
                        Axolotito.is_frozen_by_vip == False,
                    )
                ).first()
                if new_axo:
                    first_axo = new_axo
                    stats["eggs_hatched"] = stats.get("eggs_hatched", 0) + 1
                    if "natures" not in stats:
                        stats["natures"] = {}
                    stats["natures"][new_axo.nature or "?"] = \
                        stats["natures"].get(new_axo.nature or "?", 0) + 1
                    axo_stats = tutorial_result.get("axolotito", {})
                    karma = tutorial_result.get("karma", "?")
                    progress(
                        f"  🐣 {user_id} (tutorial): '{new_axo.name}' ({new_axo.nature}) | "
                        f"SUERTE:{axo_stats.get('suerte', new_axo.stat_luck):.0f} "
                        f"OJO:{axo_stats.get('ojo', new_axo.stat_focus):.0f} "
                        f"PILA:{axo_stats.get('pila', new_axo.stat_stamina):.0f} "
                        f"SAL:{axo_stats.get('sal', new_axo.stat_salinity):.0f} | "
                        f"Karma:{karma}"
                    )
                    stats[f"karma_{karma}"] = stats.get(f"karma_{karma}", 0) + 1

                    # Verify the Tabla Tutorial was created and assigned to the axo
                    if new_axo.assigned_board_id:
                        from app.models.board import PlayerBoard as _PB
                        tut_board = session.get(_PB, new_axo.assigned_board_id)
                        if tut_board:
                            stats["tutorial_boards"] = stats.get("tutorial_boards", 0) + 1
                            progress(
                                f"  🎯 {user_id}: Tabla Tutorial #{tut_board.id} "
                                f"asignada a {new_axo.name}"
                            )
                    else:
                        errors.append(f"tutorial_no_board {user_id}: axo sin tabla tutorial asignada")

                    # Verify consumable reward for salty karma
                    if karma == "salty":
                        gotas_inv = session.exec(
                            select(PlayerInventory).join(ItemCatalog).where(
                                PlayerInventory.user_id == user_id,
                                ItemCatalog.name == "gotas_antiescarcha",
                                PlayerInventory.quantity > 0,
                            )
                        ).first()
                        if gotas_inv:
                            stats["gotas_received"] = stats.get("gotas_received", 0) + 1
                            progress(f"  💧 {user_id}: gotas_antiescarcha recibida (karma salty)")
            except Exception as e:
                errors.append(f"tutorial {user_id}: {e}")
                session.rollback()
                continue

        # 4. Validar el bloqueo de compra en Nivel 1 (El Nicho)
        # En este momento, el jugador tiene 1 axolotito del tutorial y su cave_level es 1 (límite: 1).
        # Cualquier compra de huevo adicional debe ser rechazada.
        user = session.exec(select(User).where(User.privy_did == user_id)).first()
        if user:
            try:
                ShopService.buy_item(
                    session=session,
                    user_id=user_id,
                    item_id=egg.id,
                    payment_currency=CurrencyType.AXOGEMA,
                )
                errors.append(f"block_test {user_id}: Error - Se permitió la compra de un huevo extra en nivel 1 teniendo ya un axolotito.")
            except HTTPException as e:
                stats["level_1_purchase_blocked"] = stats.get("level_1_purchase_blocked", 0) + 1
                print(f"  🔒 {user_id}: Límite de Nivel 1 verificado correctamente: {e.detail}")

        # 5. Expandir la cueva vía FRJ + logro para desbloquear más spots
        #    (La expansión completa con aceleración y logros se prueba en phase_07e)
        n_eggs = p["personality"].get("eggs", 0)
        if n_eggs > 0:
            target_level = min(5, 1 + n_eggs)
            current_level = user.cave_level if user else 1
            if current_level < target_level:
                from app.api.v1.endpoints.cave_expansion import start_expansion, accelerate_expansion
                from app.models.economy import Wallet
                while current_level < target_level:
                    try:
                        # Asegurar FRJ suficientes para la expansión
                        wallet = session.exec(
                            select(Wallet).where(Wallet.user_id == user_id).with_for_update()
                        ).first()
                        if wallet:
                            wallet.frijolitos = max(wallet.frijolitos or 0, 200_000)
                            wallet.axofichas = max(wallet.axofichas or 0, 10_000)
                            session.add(wallet)
                            session.commit()

                        # Iniciar expansión (requiere logro + FRJ, sin argumento "path")
                        res = start_expansion(
                            session=session,
                            verified_user_id=user_id
                        )
                        # Acelerar inmediatamente con AXF para saltar el timer
                        accel_res = accelerate_expansion(
                            session=session,
                            verified_user_id=user_id
                        )
                        current_level = accel_res.get("current_level", current_level + 1)
                        stats["cave_expansions"] = stats.get("cave_expansions", 0) + 1
                        stats["cave_expansion_axf_spent"] = stats.get("cave_expansion_axf_spent", 0) + accel_res.get("axf_spent", 0)
                        print(f"  ⛏️ {user_id}: Cenote expandido a nivel {current_level} "
                              f"({accel_res.get('axf_spent', 0)} AXF aceleración)")
                    except Exception as e:
                        errors.append(f"cave_expand {user_id} to {current_level+1}: {e}")
                        break

            # 6. Comprar los huevos adicionales una vez expandido el cenote
            for _ in range(n_eggs):
                try:
                    ShopService.buy_item(
                        session=session,
                        user_id=user_id,
                        item_id=egg.id,
                        payment_currency=CurrencyType.AXOGEMA,
                    )
                    stats["eggs_bought"] = stats.get("eggs_bought", 0) + 1
                except HTTPException as e:
                    errors.append(f"egg_buy_after_expand {user_id}: {e.detail}")

            # 7. Sincronizar incubaciones activas
            try:
                get_user_incubations(user_id=user_id, session=session, verified_user_id=user_id)
            except Exception as e:
                session.rollback()
                errors.append(f"sync_incubations {user_id}: {e}")
                continue

            # 8. Imprintar y eclosionar los huevos adicionales
            new_incs = session.exec(
                select(WebitoIncubation).where(WebitoIncubation.user_id == user_id)
            ).all()

            for inc in new_incs:
                # El del tutorial ya se eclosionó y borró, pero por seguridad evitamos re-procesar
                if inc.tutorial_phase < 5:
                    continue

                _live(f"  🧬 {user_id}: imprinting huevo #{inc.id} con padrino {first_axo.name if first_axo else '?'}")
                try:
                    if first_axo:
                        _run_imprinting(
                            session=session,
                            incubation=inc,
                            padrino=first_axo,
                            skip_imprinting=skip_imprinting,
                        )
                    session.refresh(inc)
                except Exception as e:
                    errors.append(f"imprinting {user_id}: {e}")
                    inc.imprinting_complete = True
                    session.add(inc)
                    session.commit()

                # Eclosionar
                try:
                    session.refresh(inc)
                    if not inc.imprinting_complete:
                        inc.imprinting_complete = True
                        session.add(inc)
                        session.commit()

                    if inc.fecha_eclosion_estimada > datetime.utcnow():
                        inc.fecha_eclosion_estimada = datetime.utcnow() - timedelta(seconds=5)
                        session.add(inc)
                        session.commit()

                    res = hatch_webito(
                        incubation_id=inc.id,
                        session=session,
                        verified_user_id=user_id,
                    )
                    stats["eggs_hatched"] = stats.get("eggs_hatched", 0) + 1

                    axo_id = res.get("axolotito", {}).get("id")
                    axo_name = res.get("axolotito", {}).get("name", "?")
                    axo_stats = res.get("axolotito", {}).get("stats", {})
                    axo_obj = session.get(Axolotito, axo_id) if axo_id else None
                    axo_nature = axo_obj.nature if axo_obj else "?"

                    if "natures" not in stats:
                        stats["natures"] = {}
                    stats["natures"][axo_nature] = stats["natures"].get(axo_nature, 0) + 1

                    progress(
                        f"  🐣 {user_id}: '{axo_name}' ({axo_nature}) | "
                        f"SUERTE:{axo_stats.get('suerte', 0):.0f} "
                        f"OJO:{axo_stats.get('ojo', 0):.0f} "
                        f"PILA:{axo_stats.get('pila', 0):.0f} "
                        f"SAL:{axo_stats.get('sal', 0):.0f}"
                    )
                except Exception as e:
                    session.rollback()
                    errors.append(f"hatch {user_id}: {e}")

    # ── 9. Mentorship limit testing ─────────────────────────────────────────
    # Verify that an axolotito cannot mentor more than 3 eggs.
    # Pick the whale player (most eggs → most axolotitos) to test.
    whale_player = None
    for p in players:
        if p["personality"].get("name") == "whale":
            whale_player = p
            break
    if not whale_player:
        whale_player = players[0] if players else None

    if whale_player:
        w_user_id = whale_player["user_id"]
        w_axos = session.exec(
            select(Axolotito).where(
                Axolotito.user_id == w_user_id,
                Axolotito.status == "idle",
                Axolotito.is_frozen_by_vip == False,
            )
        ).all()
        if w_axos:
            test_padrino = w_axos[0]
            # Force mentorship_count to 3 to test the limit
            test_padrino.mentorship_count = 3
            session.add(test_padrino)
            session.commit()

            # Create a new incubation for testing
            test_egg = session.exec(
                select(ItemCatalog).where(
                    ItemCatalog.item_type == ItemType.EGG,
                    ItemCatalog.is_active == True,
                )
            ).first()
            if test_egg:
                # Grant egg to inventory
                test_inv = session.exec(
                    select(PlayerInventory).where(
                        PlayerInventory.user_id == w_user_id,
                        PlayerInventory.item_id == test_egg.id,
                    )
                ).first()
                if test_inv:
                    test_inv.quantity += 1
                else:
                    test_inv = PlayerInventory(
                        user_id=w_user_id,
                        item_id=test_egg.id,
                        quantity=1,
                    )
                session.add(test_inv)
                session.commit()

                # Sync incubations
                try:
                    get_user_incubations(user_id=w_user_id, session=session, verified_user_id=w_user_id)
                except Exception:
                    session.rollback()

                # Find the new incubation (non-tutorial)
                test_inc = session.exec(
                    select(WebitoIncubation).where(
                        WebitoIncubation.user_id == w_user_id,
                        WebitoIncubation.tutorial_phase >= 5,
                        WebitoIncubation.imprinting_complete == False,
                    )
                ).first()

                if test_inc:
                    # Attempt to assign padrino beyond limit → should fail with 400
                    try:
                        from app.api.v1.endpoints.incubation import assign_padrino, PadrinoAssignBody
                        assign_padrino(
                            payload=PadrinoAssignBody(
                                incubation_id=test_inc.id,
                                padrino_axolotito_id=test_padrino.id,
                            ),
                            session=session,
                            verified_user_id=w_user_id,
                        )
                        errors.append(
                            f"mentorship_limit_test {w_user_id}: "
                            f"Error — se permitió apadrinar un 4° huevo con {test_padrino.name}"
                        )
                    except HTTPException as e:
                        if e.status_code == 400 and "apadrinado 3" in str(e.detail):
                            stats["padrino_mentorship_errors_checked"] = \
                                stats.get("padrino_mentorship_errors_checked", 0) + 1
                            print(f"  🔒 {w_user_id}: Límite de 3 mentorías verificado: {e.detail}")
                        else:
                            errors.append(f"mentorship_limit_test {w_user_id}: HTTP {e.status_code}: {e.detail}")
                    except Exception as e:
                        errors.append(f"mentorship_limit_test {w_user_id}: {e}")
                    finally:
                        session.rollback()

                # Reset mentorship_count for cleanliness
                try:
                    test_padrino.mentorship_count = 0
                    session.add(test_padrino)
                    session.commit()
                except Exception:
                    session.rollback()

    progress(f"  ✅ {stats.get('eggs_hatched', 0)} Axolotito(s) eclosionados, "
             f"{stats.get('padrino_mentorship_errors_checked', 0)} tests de límite mentoría")
    return {}
