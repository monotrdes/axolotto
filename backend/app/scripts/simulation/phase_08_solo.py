from datetime import datetime, timedelta

from sqlmodel import Session, select
from fastapi import HTTPException

from app.models.axolotito import Axolotito
from app.models.board import PlayerBoard
from app.services.bank_service import BankService
from app.core.config import frj_to_internal
from app.api.v1.endpoints.game import PlayRequest, CaveEquipRequest, FeedRequest
from app.services.game_service import GameService
from app.services.cave_service import equip_cave_item
from app.models.items import ItemCatalog, ItemType, PlayerInventory

from sim_types import _rng


def phase_individual_play(engine, config, **state) -> dict:
    session: Session = state["session"]
    progress = state["progress"]
    players: list = state["players"]
    boards_by_user: dict = state["boards_by_user"]
    stats: dict = state["stats"]
    errors: list = state["errors"]

    progress("  🎮 Simulando partidas individuales y autojuego...")

    for p in players:
        user_id     = p["user_id"]
        personality = p["personality"]
        play_style  = personality.get("play_style", "rookie")

        # ── Bucle de Espectador F2P y Forja de Huevo ──
        if personality.get("name") == "free2play":
            print(f"  📺 {user_id} (free2play): Iniciando bucle de espectador para acumular fragmentos astrales...")
            from app.api.v1.endpoints.f2p import watch_reward
            from app.api.v1.endpoints.incubation import hatch_webito
            from app.models.items import WebitoIncubation
            from app.models.user import User
            
            watch_count = 0
            while watch_count < 110:
                won_mirror = _rng.random() > 0.5
                try:
                    res = watch_reward(won=won_mirror, session=session, verified_user_id=user_id)
                    watch_count += 1
                    total_frags = res.get("total_fragments", 0)
                    if total_frags >= 100:
                        print(f"    ✨ {user_id} alcanzó {total_frags} fragmentos astrales en {watch_count} reproducciones.")
                        break
                except Exception as e:
                    errors.append(f"watch_reward {user_id}: {e}")
                    break
            
            # Forja de huevo común cuando se acumulan 100 fragmentos
            user = session.exec(select(User).where(User.privy_did == user_id)).first()
            if user and user.f2p_astral_fragments >= 100:
                print(f"    🔨 {user_id} (free2play): Forjando huevo común con 100 fragmentos...")
                try:
                    user.f2p_astral_fragments -= 100
                    session.add(user)
                    session.commit()
                    
                    egg = session.exec(
                        select(ItemCatalog).where(
                            ItemCatalog.item_type == ItemType.EGG,
                            ItemCatalog.is_active == True,
                        )
                    ).first()
                    if egg:
                        incubation = WebitoIncubation(
                            user_id=user_id,
                            item_id=egg.id,
                            fecha_eclosion_estimada=datetime.utcnow() - timedelta(seconds=5),
                            imprinting_complete=True
                        )
                        session.add(incubation)
                        session.commit()
                        session.refresh(incubation)
                        
                        hatch_res = hatch_webito(
                            incubation_id=incubation.id,
                            session=session,
                            verified_user_id=user_id
                        )
                        stats["eggs_hatched"] = stats.get("eggs_hatched", 0) + 1
                        axo_id = hatch_res.get("axolotito", {}).get("id")
                        axo_name = hatch_res.get("axolotito", {}).get("name", "?")
                        axo_obj = session.get(Axolotito, axo_id) if axo_id else None
                        axo_nature = axo_obj.nature if axo_obj else "?"
                        
                        if "natures" not in stats:
                            stats["natures"] = {}
                        stats["natures"][axo_nature] = stats["natures"].get(axo_nature, 0) + 1
                        
                        print(f"    🐣 {user_id} (free2play): Eclosionó huevo forjado -> '{axo_name}' ({axo_nature})!")
                except Exception as e:
                    session.rollback()
                    errors.append(f"f2p_forge_egg {user_id}: {e}")

        axolotitos = session.exec(
            select(Axolotito).where(
                Axolotito.user_id == user_id,
                Axolotito.status.in_(["idle", "sleeping"]),
            )
        ).all()
        boards_ids = boards_by_user.get(user_id, [])
        boards = session.exec(
            select(PlayerBoard).where(
                PlayerBoard.id.in_(boards_ids),
                PlayerBoard.is_dead == False,
            )
        ).all() if boards_ids else []

        if not axolotitos or not boards:
            print(f"  ⚠️  {user_id}: sin axolotitos o tablas, saltando play.")
            continue

        for axo_idx, axo in enumerate(axolotitos):
            session.refresh(axo)

            # Despertar si duerme
            if axo.status == "sleeping":
                axo.sleep_expires_at = datetime.utcnow() - timedelta(seconds=5)
                session.add(axo)
                session.commit()
                try:
                    GameService.wake_axolotito(axo_id=axo.id, session=session, verified_user_id=user_id)
                    session.refresh(axo)
                except Exception:
                    session.rollback()

            # Asegurar energía mínima
            if axo.energy_current < 20:
                axo.energy_current = axo.stat_stamina or 100
                session.add(axo)
                session.commit()

            board = boards[axo_idx % len(boards)]
            axo.assigned_board_id = board.id
            session.add(axo)
            session.commit()

            n_games  = personality.get("solo_games", 4)
            print(f"  🦎 {axo.name} ({personality['name']}): {n_games} partidas...")

            # — Partidas manuales —
            for game_i in range(n_games):
                session.refresh(axo)
                if axo.energy_current < 10:
                    axo.energy_current = axo.stat_stamina or 100
                    session.add(axo)
                    session.commit()

                room = "champion" if play_style == "champion" else (
                    "champion" if _rng.random() < 0.35 else "rookie"
                )
                try:
                    req = PlayRequest(
                        axolotito_id=axo.id,
                        room_name=room,
                        bot_enabled=False,
                        bot_budget_gal=0,
                        bot_loss_limit_pct=30.0,
                        bot_profit_limit_pct=50.0,
                    )
                    result = GameService.play_match(
                        axolotito_id=req.axolotito_id,
                        room_name=req.room_name,
                        multiplier=req.multiplier,
                        bot_enabled=req.bot_enabled,
                        bot_budget_gal=req.bot_budget_gal,
                        bot_loss_limit_pct=req.bot_loss_limit_pct,
                        bot_profit_limit_pct=req.bot_profit_limit_pct,
                        session=session,
                        verified_user_id=user_id,
                    )
                    stats["games_played"] = stats.get("games_played", 0) + 1
                    if result.get("resultado") == "victoria":
                        stats["wins"] = stats.get("wins", 0) + 1
                        outcome = f"🏆 +{result.get('prize_gal', 0):.1f} FRJ"
                    else:
                        stats["losses"] = stats.get("losses", 0) + 1
                        outcome = f"💔 +{result.get('prize_gal', 0):.1f} FRJ"
                    stats["total_prize_gal"] = stats.get("total_prize_gal", 0.0) + result.get("prize_gal", 0.0)
                    print(f"    #{game_i+1} [{room}] {outcome} | {result.get('turns')} turnos")
                except HTTPException as e:
                    session.rollback()
                    errors.append(f"play {user_id} {axo.name}: {e.detail}")

            # — Autojuego con presupuesto alto (primer axolotito por usuario) —
            # collector tiene auto_budget=0 → no hace autojuego
            if axo_idx == 0 and personality.get("auto_budget", 300.0) > 0:
                budget = personality.get("auto_budget", 300.0)
                wallet = BankService.get_or_create_wallet(session, user_id)
                if wallet.frijolitos < frj_to_internal(budget):
                    wallet.frijolitos = frj_to_internal(budget + 200)
                    session.add(wallet)
                    session.commit()

                session.refresh(axo)
                if axo.energy_current < 10:
                    axo.energy_current = axo.stat_stamina or 100
                    session.add(axo)
                    session.commit()

                print(f"  🤖 {axo.name}: autojuego con {budget} FRJ de presupuesto...")
                auto_wins = 0
                for auto_i in range(3):
                    session.refresh(axo)
                    if axo.energy_current < 10:
                        axo.energy_current = axo.stat_stamina or 100
                        session.add(axo)
                        session.commit()
                    try:
                        req = PlayRequest(
                            axolotito_id=axo.id,
                            room_name="rookie",
                            bot_enabled=True,
                            bot_budget_gal=budget,
                            bot_loss_limit_pct=30.0,
                            bot_profit_limit_pct=50.0,
                        )
                        result = GameService.play_match(
                        axolotito_id=req.axolotito_id,
                        room_name=req.room_name,
                        multiplier=req.multiplier,
                        bot_enabled=req.bot_enabled,
                        bot_budget_gal=req.bot_budget_gal,
                        bot_loss_limit_pct=req.bot_loss_limit_pct,
                        bot_profit_limit_pct=req.bot_profit_limit_pct,
                        session=session,
                        verified_user_id=user_id,
                    )
                        stats["games_played"] = stats.get("games_played", 0) + 1
                        if result.get("resultado") == "victoria":
                            stats["wins"] = stats.get("wins", 0) + 1
                            auto_wins += 1
                        else:
                            stats["losses"] = stats.get("losses", 0) + 1
                    except HTTPException as e:
                        session.rollback()
                        errors.append(f"autoplay {user_id}: {e.detail}")
                print(f"  🤖 Autojuego: {auto_wins}/3 victorias")
                stats["autogames"] = stats.get("autogames", 0) + 3

        # ── Post-game care: alimentar, dormir, equipar ──────────────────
        for axo in axolotitos:
            session.refresh(axo)

            # Alimentar axolotitos con energía baja
            if axo.energy_current < axo.stat_stamina * 0.4:
                food = "shrimp" if _rng.random() < 0.3 else "pellet"
                try:
                    GameService.feed_axolotito(
                        axo_id=axo.id,
                        food_type=food,
                        session=session,
                        verified_user_id=user_id,
                    )
                    session.refresh(axo)
                    stats["feedings"] = stats.get("feedings", 0) + 1
                    print(f"  🍽️  {user_id}: {axo.name} alimentado con {food} (energía: {axo.energy_current:.0f})")
                except HTTPException as e:
                    errors.append(f"feed {user_id}/{axo.name}: {e.detail}")
                except Exception as e:
                    session.rollback()

            # Dormir axolotitos con energía crítica
            if axo.energy_current < 20 and axo.status == "idle":
                try:
                    GameService.sleep_axolotito(
                        axo_id=axo.id,
                        session=session,
                        verified_user_id=user_id,
                    )
                    stats["sleeps"] = stats.get("sleeps", 0) + 1
                    print(f"  😴 {user_id}: {axo.name} durmiendo...")
                except HTTPException as e:
                    errors.append(f"sleep {user_id}/{axo.name}: {e.detail}")

            # Equipar cave items del inventario
            cave_inv = session.exec(
                select(PlayerInventory).join(ItemCatalog).where(
                    PlayerInventory.user_id == user_id,
                    ItemCatalog.item_type == ItemType.CAVE_ITEM,
                    PlayerInventory.quantity > 0,
                )
            ).first()
            if cave_inv:
                cave = list(axo.cave_items or [])
                if cave_inv.item_id not in cave and len(cave) < 3:
                    try:
                        equip_cave_item(
                            axo_id=axo.id,
                            item_id=cave_inv.item_id,
                            session=session,
                            verified_user_id=user_id,
                        )
                        stats["cave_equips"] = stats.get("cave_equips", 0) + 1
                        print(f"  🔧 {user_id}: cave item equipado en {axo.name}")
                    except HTTPException as e:
                        errors.append(f"cave_equip {user_id}: {e.detail}")

            # Equipar accesorios (head/eyes/body)
            acc_inv = session.exec(
                select(PlayerInventory).join(ItemCatalog).where(
                    PlayerInventory.user_id == user_id,
                    ItemCatalog.item_type == ItemType.ACCESSORY,
                    PlayerInventory.quantity > 0,
                )
            ).all()
            for slot_name, attr in [("head", "equipped_head_item_id"), ("eyes", "equipped_eyes_item_id"), ("body", "equipped_body_item_id")]:
                already_equipped = getattr(axo, attr)
                if already_equipped:
                    continue
                for inv in acc_inv:
                    if inv.item_id == already_equipped:
                        continue
                    try:
                        from app.api.v1.endpoints.user import equip_accessory, EquipRequest
                        equip_accessory(
                            axolotito_id=axo.id,
                            req=EquipRequest(item_id=inv.item_id, slot=slot_name),
                            session=session,
                            verified_user_id=user_id,
                        )
                        stats["accessory_equips"] = stats.get("accessory_equips", 0) + 1
                        print(f"  💍 {user_id}: accesorio equipado en slot {slot_name} de {axo.name}")
                        break  # Un accesorio por slot
                    except HTTPException as e:
                        errors.append(f"acc_equip {user_id}/{slot_name}: {e.detail}")
                    except Exception:
                        session.rollback()

    progress(f"  ✅ Partidas: {stats.get('games_played',0)} jugadas, "
             f"{stats.get('wins',0)} victorias, "
             f"{stats.get('autogames',0)} en autojuego, "
             f"{stats.get('feedings',0)} alimentaciones, "
             f"{stats.get('sleeps',0)} ciclos sueño.")
    return {}
