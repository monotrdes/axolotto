#!/usr/bin/env python3
"""
simulate_universe.py v3 — Simulador Integral del Universo Axolotto

⚠️  DEPRECADO — Usar el simulador modular en su lugar:
      python backend/app/scripts/simulation/runner.py

Este archivo se mantiene como referencia histórica y backup.
No recibe nuevas features. El simulador modular (simulation/runner.py)
es la versión canónica con todas las fases actualizadas (corcholatas,
tutorial con auto-hatch, etc.).

Usage:
    cd D:\Axolotto_2026\axolotto
    python backend/app/scripts/simulate_universe.py
    python backend/app/scripts/simulate_universe.py --players 4 --incubation 45 --games 5

Fases:
    0.  Reset TOTAL de BD (deploy-clean: todos los usuarios, incl. Pro)
        + migraciones mínimas
    1.  Creación de usuarios con personalidades aleatorias
    2.  Seed AXG + compra de paquetes GAL
    3a. Compra de boosters (normal + foil) — quedan SELLADOS en inventario
    3b. Apertura inmediata (whale: abre todo de una)
    4.  Compra de huevos + incubación real + interacciones periódicas
    4b. Apertura post-incubación (selective/random: foils + aleatorios)
    5.  Gashapon: estándar, cápsulas diarias, triple suerte
    6b. Apertura final boosters (hoarder: antes de armar tableros)
    6.  Gestión de tablas: tableros aleatorios + manual con cartas del inventario
    7.  VIP: activación de tiers coral/dorado/axolite + verificación de beneficios
    8.  Partidas individuales: solo + autojuego con presupuesto alto
    9.  Multijugador: inscribir → RECALL test → reinscribir → simular → liquidar
   10.  Tests de rutas negativas (acciones prohibidas que deben fallar)
   11.  Reporte final

Estrategias de apertura de boosters por personalidad:
    whale      → immediate  (abre todo al comprar)
    aggressive → selective  (foils ya, normales post-incubación)
    casual     → hoarder    (guarda todos, abre al final)
    collector  → random     (50 % de probabilidad por sobre)
    free2play  → hoarder    (guarda los pocos que tiene, abre al final)

Orden de compra en phase_fund_wallets (por personalidad con VIP):
    1. AXG (hard currency)
    2. GAL packs (COR — soft currency)
    3. VIP membership  ← después de tener GAL, para que boosters/huevos gocen descuento
"""

import sys
import os
import json
import argparse
import random
import secrets
import time
from datetime import datetime, timedelta

# ── Path setup ────────────────────────────────────────────────────────────────
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
project_root = os.path.dirname(backend_dir)
sys.path.append(backend_dir)

from dotenv import load_dotenv
load_dotenv(os.path.join(backend_dir, "..", ".env"))
load_dotenv(os.path.join(backend_dir, ".env"))

# ── Early arg parsing: --db-url must be set BEFORE app.database is imported ──
_pre = argparse.ArgumentParser(add_help=False)
_pre.add_argument("--db-url", default=None)
_pre_args, _ = _pre.parse_known_args()
if _pre_args.db_url:
    os.environ["DATABASE_URL"] = _pre_args.db_url
elif not os.path.exists("/.dockerenv"):
    # Remap Docker hostnames when running on the host machine
    if "DATABASE_URL" in os.environ:
        _dbu = os.environ["DATABASE_URL"]
        if "@db_axolotto:5432" in _dbu:
            os.environ["DATABASE_URL"] = _dbu.replace("@db_axolotto:5432", "@127.0.0.1:5433")
    for _key in ("WEB3_PROVIDER_URL", "ANVIL_RPC_URL", "RPC_URL"):
        if _key in os.environ and "anvil_axolotto" in os.environ[_key]:
            os.environ[_key] = os.environ[_key].replace("anvil_axolotto", "127.0.0.1")

from sqlmodel import Session, select, func
from sqlalchemy import delete, text as sa_text
from sqlmodel import SQLModel
from fastapi import HTTPException

from app.database import engine
from app.core.config import settings
from app.models.user import User
from app.models.economy import Wallet, CurrencyType, TransactionLedger, TransactionType, AxgPurchaseRecord
from app.models.items import ItemCatalog, ItemType, PlayerInventory, WebitoIncubation
from app.models.board import PlayerBoard
from app.models.axolotito import Axolotito
from app.models.lobby_models import GameRoom, RoomRegistration, JackpotVault, TreasuryVault, MultiplayerGameLog, JackpotWin
from app.services.bank_service import BankService
from app.services.shop_service import ShopService
from app.services.multiplayer_service import MultiplayerService, get_or_create_waiting_room
from app.api.v1.endpoints.board import (
    create_random_board, create_manual_board,
    CreateManualBoardRequest, delete_board,
)
from app.api.v1.endpoints.game import PlayRequest, FeedRequest
from app.services.game_service import GameService
from app.api.v1.endpoints.incubation import (
    get_user_incubations, hatch_webito,
)
from app.api.v1.endpoints.multiplayer import (
    register_axolotito, recall_axolotito,
    settle_axolotito_escrow, RegisterRequest,
)
from app.api.v1.endpoints.shop import (
    roll_gashapon, claim_daily_capsule, roll_capsule, roll_triple_suerte,
    open_booster, get_store_items,
    GashaponRollRequest, CapsuleRollRequest, OpenBoosterRequest,
    melt_card_endpoint as melt_card, forge_card_endpoint as forge_card, MeltCardRequest, ForgeCardRequest, TripleSuerteRequest,
)
from app.api.v1.endpoints.market import (
    list_inventory_item, buy_inventory_listing, get_inventory_listings,
    ListInventoryItemRequest,
)
from app.api.v1.endpoints.user import sync_user
from app.api.v1.endpoints.user import SyncUserRequest as SyncRequest

# ── RNG ───────────────────────────────────────────────────────────────────────
_rng = random.SystemRandom()


# ── Utilidades de consola ─────────────────────────────────────────────────────
def _make_bar(pct: float, width: int = 22) -> str:
    """Barra de progreso ASCII: [████████░░░░░░░░] 42%"""
    filled = int(width * min(pct, 100) / 100)
    return "█" * filled + "░" * (width - filled)

# ── Personalidades de jugador ─────────────────────────────────────────────────
PERSONALITY_POOL = [
    {
        # Máximo gastador: abre todo inmediatamente, VIP máximo, juega en champion
        "name": "whale",
        "boosters_normal": 35,
        "boosters_foil": 12,
        "eggs": 4,
        "boards_random": 4,
        "solo_games": 8,
        "auto_budget": 1000.0,
        "vip_tier": "axolite",
        "gashapon_rolls": 6,
        "play_style": "champion",
        "does_triple_suerte": True,
    },
    {
        # Coleccionista: acumula boosters/huevos/tableros, VIP por descuento, casi no juega
        "name": "collector",
        "boosters_normal": 28,
        "boosters_foil": 10,
        "eggs": 4,
        "boards_random": 5,
        "solo_games": 1,
        "auto_budget": 0.0,
        "vip_tier": "dorado",
        "gashapon_rolls": 5,
        "play_style": "rookie",
        "does_triple_suerte": False,
    },
    {
        # Jugador competitivo: muchas partidas, gasta en ítems, vende en P2P
        "name": "aggressive",
        "boosters_normal": 20,
        "boosters_foil": 5,
        "eggs": 2,
        "boards_random": 3,
        "solo_games": 10,
        "auto_budget": 700.0,
        "vip_tier": "dorado",
        "gashapon_rolls": 3,
        "play_style": "champion",
        "does_triple_suerte": True,
    },
    {
        # Jugador casual: gasto mínimo, pocas partidas, VIP básico
        "name": "casual",
        "boosters_normal": 6,
        "boosters_foil": 1,
        "eggs": 1,
        "boards_random": 2,
        "solo_games": 3,
        "auto_budget": 100.0,
        "vip_tier": "coral",
        "gashapon_rolls": 1,
        "play_style": "rookie",
        "does_triple_suerte": False,
    },
    {
        # Free-to-play: casi sin gasto real, juega mucho para ganar GAL, sin VIP
        "name": "free2play",
        "boosters_normal": 2,
        "boosters_foil": 0,
        "eggs": 0,
        "boards_random": 2,
        "solo_games": 15,
        "auto_budget": 400.0,
        "vip_tier": None,
        "gashapon_rolls": 2,
        "play_style": "rookie",
        "does_triple_suerte": False,
    },
]

PRO_USER_DID = "did:privy:cmnn1tv0o02au0ckzho9ugkb2"


# ═══════════════════════════════════════════════════════════════════════════════
# FASE 0: RESET + MIGRACIONES
# ═══════════════════════════════════════════════════════════════════════════════

def phase_reset(session: Session, progress) -> None:
    """
    Limpia TODOS los datos de juego — como si fuera un deploy fresh.
    Se borran datos de TODOS los usuarios (incluyendo Pro). Los registros
    de User se conservan pero se resetean sus campos de estado (VIP, slots, etc.).
    """
    progress("  ♻️  Reseteando estado completo (deploy-clean — todos los usuarios)...")

    # 1. Romper FK circular antes de borrar
    try:
        session.execute(sa_text("UPDATE axolotito SET assigned_board_id = NULL"))
        session.commit()
    except Exception:
        session.rollback()

    # 2. Borrar TODOS los datos de juego (sin filtro de usuario)
    #    Orden: tablas dependientes primero para evitar violaciones de FK
    for model in [
        JackpotWin, RoomRegistration, MultiplayerGameLog, GameRoom,
        WebitoIncubation, PlayerBoard, Axolotito,
        TransactionLedger, PlayerInventory, Wallet,
        JackpotVault, TreasuryVault, AxgPurchaseRecord,
    ]:
        try:
            session.exec(delete(model))
            session.commit()
        except Exception as e:
            session.rollback()
            progress(f"  ⚠️  No se pudo borrar {model.__name__}: {e}")

    # 3a. Eliminar usuarios simulados de runs anteriores (evita acumulación de
    #     fantasmas sin wallet que contaminan la vista de jugadores en admin).
    #     Hay que borrar las tablas con FK a user.privy_did primero.
    #     Los usuarios reales (Privy auth) conservan sus filas.
    SIM_PATTERN = "did:privy:sim_player_%"
    _sim_fk_tables = [
        ("whitelistentry",      "user_id"),
        ("pending_rewards",     "user_id"),
        ("axolotito",           "user_id"),
        ("playerboard",         "user_id"),
        ("playerinventory",     "user_id"),
        ("transactionledger",   "user_id"),
        ("wallet",              "user_id"),
        ("jackpotwin",          "user_id"),
        ("multiplayergamelog",  "user_id"),
        ("cryptopurchaseorder", "user_id"),
        ("processedtransaction","user_id"),
        ("axg_purchase_record", "user_id"),
        ("cryptopaymentattempt","user_id"),
        ("axf_purchase_record", "user_id"),
        ("manualmodeevent",     "created_by"),
        ("inventorymarketlisting","seller_id"),
        ("promocode",           "redeemed_by"),
    ]
    try:
        for table, col in _sim_fk_tables:
            session.execute(sa_text(
                f"DELETE FROM {table} WHERE {col} LIKE :pat"
            ), {"pat": SIM_PATTERN})
        result = session.execute(sa_text(
            "DELETE FROM \"user\" WHERE privy_did LIKE :pat"
        ), {"pat": SIM_PATTERN})
        session.commit()
        progress(f"  🧹 {result.rowcount} usuarios sim de runs anteriores eliminados.")
    except Exception as e:
        session.rollback()
        progress(f"  ⚠️  No se pudo limpiar usuarios sim anteriores: {e}")

    # 3b. Resetear campos de estado del User para TODOS los usuarios reales
    #     (VIP, slots, puntos, etc. — vuelven a valores de deploy)
    try:
        session.execute(sa_text("""
            UPDATE "user" SET
                vip_tier                 = NULL,
                vip_expires_at           = NULL,
                vip_streak_months        = 0,
                vip_streak_last_renewed  = NULL,
                vip_pending_gal          = 0.0,
                vip_pending_gal_expires_at = NULL,
                vip_last_daily_gal_at    = NULL,
                vip_tiers_activated      = '[]',
                vip_auto_renew           = FALSE,
                unlocked_board_slots     = 3,
                cave_level               = 1,
                cave_name                = NULL,
                puntos                   = 0,
                first_crypto_purchase_at = NULL,
                promo_code_attempts      = 0,
                tutorial_completed       = FALSE,
                last_play_date           = NULL,
                daily_play_streak        = 0,
                f2p_astral_fragments     = 0,
                f2p_daily_gal_earned     = 0.0,
                f2p_daily_gal_reset_at   = NULL,
                f2p_daily_frags_earned   = 0,
                last_f2p_daily_claim_at  = NULL,
                f2p_daily_claim_streak   = 0
        """))
        session.commit()
    except Exception as e:
        session.rollback()
        progress(f"  ⚠️  No se pudo resetear campos User: {e}")

    # 4. Reiniciar boosters de catálogo a Fase 1
    try:
        all_boosters = session.exec(
            select(ItemCatalog).where(ItemCatalog.item_type == ItemType.BOOSTER)
        ).all()
        for b in all_boosters:
            fase = (b.item_metadata or {}).get("fase", 1)
            b.is_active = (fase == 1)
            session.add(b)
        session.commit()
    except Exception:
        session.rollback()

    progress("  ✅ Reset completo — BD virgen (wallets, axolotitos, tableros, VIP, jackpot).")


def phase_migrations(progress) -> None:
    """Asegura que las columnas opcionales existen en la BD."""
    progress("  🔧 Aplicando migraciones mínimas...")
    SQLModel.metadata.create_all(engine)

    with engine.connect() as conn:
        # Asegurar que los valores del enum transactiontype existen en la BD
        for enum_val in ("BURN", "VIP_GAL_EXPIRED", "CRAFTING"):
            try:
                conn.execute(sa_text(
                    f"ALTER TYPE transactiontype ADD VALUE IF NOT EXISTS '{enum_val}'"
                ))
                conn.commit()
            except Exception:
                conn.rollback()

        is_sqlite = "sqlite" in str(engine.url)

        def _get_cols(table: str) -> set:
            if is_sqlite:
                return {r[1] for r in conn.execute(sa_text(f"PRAGMA table_info({table})")).fetchall()}
            return {r[0] for r in conn.execute(
                sa_text(f"SELECT column_name FROM information_schema.columns WHERE table_name='{table}'")
            ).fetchall()}

        for table, col, ddl in [
            ("playerboard",   "is_dead",             "BOOLEAN DEFAULT FALSE"),
            ("playerboard",   "blockchain_token_id", "INTEGER NULL"),
            ("playerboard",   "card_first_editions", "JSON DEFAULT '[]'"),
            ("playerboard",   "is_listed_for_sale",  "BOOLEAN DEFAULT FALSE"),
            ("playerboard",   "sale_price_gal",      "DOUBLE PRECISION DEFAULT 0.0"),
            ("playerboard",   "is_frozen_by_vip",    "BOOLEAN DEFAULT FALSE"),
            ("playerboard",   "is_npc_pool",         "BOOLEAN DEFAULT FALSE"),
            ("playerboard",   "npc_room",             "VARCHAR(50)"),
            ("playerboard",   "npc_retired",         "BOOLEAN DEFAULT FALSE"),
            ("playerboard",   "origin_story",        "TEXT"),
            ("playerinventory","is_first_edition",   "BOOLEAN DEFAULT FALSE"),
            ("axolotito",     "sleep_expires_at",    "TIMESTAMP NULL"),
            ("axolotito",     "is_main",             "BOOLEAN DEFAULT FALSE"),
            ("axolotito",     "is_frozen_by_vip",    "BOOLEAN DEFAULT FALSE"),
            ("axolotito",     "escrow_balance_gal",  "DOUBLE PRECISION DEFAULT 0.0"),
            ("axolotito",     "wants_to_stop",       "BOOLEAN DEFAULT FALSE"),
            ("axolotito",     "loyalty_points",      "INTEGER DEFAULT 0"),
            ("axolotito",     "is_listed_for_sale",  "BOOLEAN DEFAULT FALSE"),
            ("axolotito",     "sale_price_gal",      "DOUBLE PRECISION DEFAULT 0.0"),
            ("axolotito",     "is_listed_for_rent",  "BOOLEAN DEFAULT FALSE"),
            ("axolotito",     "rent_fee_gal",        "DOUBLE PRECISION DEFAULT 0.0"),
            ("axolotito",     "rent_share_owner_pct","INTEGER DEFAULT 0"),
            ("axolotito",     "rent_expires_at",     "TIMESTAMP NULL"),
            ("axolotito",     "cpu_win_streak",      "INTEGER DEFAULT 0"),
            ("axolotito",     "cave_items",          "JSON DEFAULT '[]'"),
            ("axolotito",     "nature",              "VARCHAR(255) NULL"),
        ]:
            try:
                cols = _get_cols(table)
                if col not in cols:
                    conn.execute(sa_text(f"ALTER TABLE {table} ADD COLUMN {col} {ddl}"))
            except Exception:
                pass
        conn.commit()
    # Seed catalog (needed for SQLite local simulation runs)
    with Session(engine) as seed_sess:
        progress("  📦 Actualizando/sembrando cartas de la Lotería Axolotto...")
        try:
            from app.scripts.seed_cards import seed_cartas
            seed_cartas()
        except Exception as e:
            progress(f"  ⚠️  seed_cartas falló: {e}")

        other_count = seed_sess.exec(
            select(func.count(ItemCatalog.id)).where(ItemCatalog.item_type != ItemType.CARD)
        ).one()
        if other_count == 0:
            progress("  📦 Sembrando boosters, huevos, VIP, paquetes GAL...")
            try:
                from app.scripts.seed_catalog import run_seed
                run_seed()
            except Exception as e:
                progress(f"  ⚠️  seed_catalog falló: {e}")

    progress("  ✅ Migraciones aplicadas.")


# ═══════════════════════════════════════════════════════════════════════════════
# FASE 1: CREACIÓN DE USUARIOS
# ═══════════════════════════════════════════════════════════════════════════════

def phase_create_users(session: Session, n_players: int, stats: dict, progress) -> list[dict]:
    """Crea n_players usuarios con personalidades distintas. Devuelve lista de dicts {user_id, wallet_addr, personality}."""
    progress(f"  👥 Creando {n_players + 1} jugadores con personalidades...")
    players = []

    # Crear/verificar el usuario treasury para evitar FK violations en TransactionLedger
    treasury_user = session.exec(select(User).where(User.privy_did == "treasury")).first()
    if not treasury_user:
        treasury_user = User(
            privy_did="treasury",
            email="treasury@axolot.to",
            wallet_address="0x" + "0" * 40,
            unlocked_board_slots=0,
        )
        session.add(treasury_user)
        session.commit()

    # Usuario Pro (desarrollador) → personalidad 'whale'
    pro_user = session.exec(select(User).where(User.privy_did == PRO_USER_DID)).first()
    if not pro_user:
        pro_user = User(
            privy_did=PRO_USER_DID,
            email="user_pro@example.com",
            wallet_address=f"0x{'dead' + '0' * 36}",
            unlocked_board_slots=5,
        )
        session.add(pro_user)
        session.commit()
        session.refresh(pro_user)
    players.append({
        "user_id": PRO_USER_DID,
        "wallet_addr": pro_user.wallet_address,
        "personality": PERSONALITY_POOL[1],  # whale
    })
    print(f"  👑 Usuario Pro: {PRO_USER_DID}")

    # Jugadores simulados
    shuffled = PERSONALITY_POOL.copy()
    _rng.shuffle(shuffled)
    for i in range(1, n_players + 1):
        did = f"did:privy:sim_player_{i}"
        wallet_addr = f"0x{secrets.token_hex(20)}"
        personality = shuffled[(i - 1) % len(shuffled)]

        existing = session.exec(select(User).where(User.privy_did == did)).first()
        if not existing:
            user = User(
                privy_did=did,
                email=f"sim_player_{i}@example.com",
                wallet_address=wallet_addr,
                unlocked_board_slots=3,
            )
            session.add(user)
            session.commit()
            stats["users_created"] = stats.get("users_created", 0) + 1
        else:
            existing.wallet_address = wallet_addr
            session.add(existing)
            session.commit()

        players.append({
            "user_id": did,
            "wallet_addr": wallet_addr,
            "personality": personality,
        })
        print(f"  👤 {did} | estilo: {personality['name']}")

    session.commit()
    progress(f"  ✅ {len(players)} jugadores listos.")
    return players


# ═══════════════════════════════════════════════════════════════════════════════
# FASE 2: AXG SEED + COMPRA DE PAQUETES GAL
# ═══════════════════════════════════════════════════════════════════════════════

def phase_fund_wallets(session: Session, players: list[dict], stats: dict, errors: list, progress) -> None:
    """
    Simula la compra de paquetes de AXG con pesos (MXN) para cada jugador
    según lo que requiere comprar en base a su personalidad, almacena los registros
    en la BD (equivalente en pesos) y activa el VIP de inmediato si corresponde,
    para que todos los consumos posteriores gocen del descuento VIP.
    """
    progress("  💰 Simulando compra de paquetes de AXG (Pesos MXN) y fondeo de wallets...")

    # Buscar los items VIP en el catálogo
    vip_items = session.exec(
        select(ItemCatalog).where(
            ItemCatalog.is_active == True,
        )
    ).all()
    vip_catalog = {
        (item.item_metadata or {}).get("vip_tier"): item
        for item in vip_items
        if (item.item_metadata or {}).get("is_vip")
    }

    # Buscar los paquetes de GAL en el catálogo
    gal_packs = session.exec(
        select(ItemCatalog).where(
            ItemCatalog.item_type == ItemType.CURRENCY_PACK,
            ItemCatalog.is_active == True,
        )
    ).all()

    for p in players:
        user_id = p["user_id"]
        personality = p["personality"]
        wallet = BankService.get_or_create_wallet(session, user_id)
        user = session.exec(select(User).where(User.privy_did == user_id)).first()

        # 1. Calcular AXG requerido para comprar todo lo planificado
        eggs_count = personality.get("eggs", 0)
        # Buscar el huevo activo en el catálogo para conocer su precio exacto
        egg_item = session.exec(
            select(ItemCatalog).where(
                ItemCatalog.item_type == ItemType.EGG,
                ItemCatalog.is_active == True,
            )
        ).first()
        egg_price = egg_item.price_axg if egg_item else 1200.0
        eggs_cost = eggs_count * egg_price

        vip_tier = personality.get("vip_tier")
        vip_cost = 0.0
        vip_discount = 0.0
        if vip_tier and vip_tier in vip_catalog:
            vip_cost = vip_catalog[vip_tier].price_axg
            from app.core.config import VIP_CONFIG
            vip_discount = VIP_CONFIG.get(vip_tier, {}).get("discount", 0.0)

        boosters_normal = personality.get("boosters_normal", 0)
        boosters_foil = personality.get("boosters_foil", 0)

        # Precios base en catálogo (usando aproximados/máximos para asegurar saldo)
        normal_price_base = 350.0
        foil_price_base = 800.0

        # Si compra VIP, sus boosters tendrán descuento "desde siempre"
        effective_normal = round(normal_price_base * (1.0 - vip_discount), 2)
        effective_foil = round(foil_price_base * (1.0 - vip_discount), 2)

        boosters_cost = (boosters_normal * effective_normal) + (boosters_foil * effective_foil)

        # Buffer para gal_packs, gashapon, tablas, etc.
        gameplay_buffer = 4000.0

        total_needed_axg = eggs_cost + vip_cost + boosters_cost + gameplay_buffer

        # 2. Simular compra de paquetes de AXG
        # Paquetes: 200x$35, 550x$88, 1725x$263 y 7250x$875
        AXG_PACKS = [
            {"axg": 7250, "price_mxn": 875.0, "name": "7250x$875"},
            {"axg": 1725, "price_mxn": 263.0, "name": "1725x$263"},
            {"axg": 550,  "price_mxn": 88.0,  "name": "550x$88"},
            {"axg": 200,  "price_mxn": 35.0,  "name": "200x$35"},
        ]

        current_obtained = 0.0
        mxn_spent = 0.0
        purchased_packs_counts = {}

        while current_obtained < total_needed_axg:
            remaining = total_needed_axg - current_obtained
            chosen_pack = None
            for pack in AXG_PACKS:
                if pack["axg"] <= remaining:
                    chosen_pack = pack
                    break
            if not chosen_pack:
                chosen_pack = AXG_PACKS[-1] # el más pequeño si lo restante es menor a 200

            # Registrar compra en BD
            record = AxgPurchaseRecord(
                user_id=user_id,
                axf_amount=chosen_pack["axg"],
                mxn_amount=chosen_pack["price_mxn"],
                pack_name=chosen_pack["name"],
                created_at=datetime.utcnow()
            )
            session.add(record)
            
            current_obtained += chosen_pack["axg"]
            mxn_spent += chosen_pack["price_mxn"]
            purchased_packs_counts[chosen_pack["name"]] = purchased_packs_counts.get(chosen_pack["name"], 0) + 1

        session.commit()

        # Actualizar saldo del wallet
        wallet.axofichas = current_obtained
        wallet.frijolitos = 0.0

        # DEPRECADO: El dev corcholata basket ya no se entrega directo al wallet.
        # Ahora se usa el flujo real: PromoCode → PendingReward → claim post-tutorial.
        # Ver simulation/phase_01b_corcholata.py y phase_04_incubation.py
        # wallet.axofichas += settings.DEV_AUTO_REWARD_AXF
        # wallet.frijolitos += settings.DEV_AUTO_REWARD_FRJ

        session.add(wallet)
        session.commit()

        packs_summary = ", ".join([f"{k} ({v}x)" for k, v in purchased_packs_counts.items()])
        print(f"  💎 {user_id}: Simulación compra AXG: {packs_summary} | Total AXG: {current_obtained:.0f} | MXN: ${mxn_spent:.2f}")
        stats["axg_purchased_mxn"] = stats.get("axg_purchased_mxn", 0.0) + mxn_spent
        stats["axg_purchased_qty"] = stats.get("axg_purchased_qty", 0.0) + current_obtained

        # 3. Comprar paquetes GAL con AXG (primero COR, luego VIP para que el descuento aplique)
        if gal_packs:
            n_packs = _rng.randint(2, 5)
            for _ in range(n_packs):
                pack = _rng.choice(gal_packs)
                try:
                    ShopService.buy_item(
                        session=session,
                        user_id=user_id,
                        item_id=pack.id,
                        payment_currency=CurrencyType.AXOGEMA,
                    )
                    stats["gal_packs_bought"] = stats.get("gal_packs_bought", 0) + 1
                except HTTPException as e:
                    errors.append(f"gal_pack {user_id}: {e.detail}")
            session.refresh(wallet)
            print(f"  🌿 {user_id}: {wallet.frijolitos:.0f} GAL tras {n_packs} paquetes")
        else:
            # Sin paquetes en catálogo: seed directo para que el resto funcione
            wallet.frijolitos = 5000.0
            session.add(wallet)
            session.commit()
            print(f"  🌿 {user_id}: 5000 GAL (sin CURRENCY_PACK en catálogo)")

        # 4. Activar VIP ahora que ya tiene GAL — compras futuras (boosters, huevos) gozarán descuento
        if vip_tier and vip_tier in vip_catalog:
            vip_item = vip_catalog[vip_tier]
            try:
                res = ShopService.buy_item(
                    session=session,
                    user_id=user_id,
                    item_id=vip_item.id,
                    payment_currency=CurrencyType.AXOGEMA,
                )
                session.refresh(wallet)
                session.refresh(user)
                stats["vip_activations"] = stats.get("vip_activations", 0) + 1
                welcome_gal = res.get("welcome_gal_bonus", 0) if isinstance(res, dict) else 0
                print(f"  👑 {user_id}: VIP {vip_tier.upper()} activado tras fondear GAL (+{welcome_gal} GAL bienvenida) — próximas compras con descuento")
            except HTTPException as e:
                errors.append(f"vip_buy_early {user_id} {vip_tier}: {e.detail}")

    progress(f"  ✅ Wallets fondeadas.")


# ═══════════════════════════════════════════════════════════════════════════════
# FASE 3: COMPRA DE BOOSTERS (sellados — se abren después)
# ═══════════════════════════════════════════════════════════════════════════════

# Estrategia de apertura por personalidad:
#   "immediate"  → abre todo en cuanto compra
#   "selective"  → abre solo foils ahora, guarda normales para después
#   "hoarder"    → guarda todos; los abre mucho después (o nunca)
#   "random"     → decide aleatoriamente cuáles abrir
BOOSTER_OPEN_STRATEGY: dict[str, str] = {
    "whale":      "immediate",   # Ballena: abre todo de una vez
    "aggressive": "selective",   # Agresivo: abre la mayoría en post-incubación, conserva un poco
    "casual":     "hoarder",     # Casual: abre la mayoría al final, conserva un poco
    "collector":  "random",      # Coleccionista: abre la mayoría, conserva un poco
    "free2play":  "hoarder",     # F2P: guarda los pocos que tiene, los abre al final
}


def phase_buy_boosters(session: Session, players: list[dict], stats: dict, errors: list, progress) -> None:
    """
    COMPRA boosters normales y foil para cada jugador de acuerdo a su pool de personalidad.
    Los sobres quedan SELLADOS en el inventario — no se abren aquí.
    Llama a phase_open_boosters() cuando quieras abrirlos.
    """
    progress("  📦 Comprando boosters (quedan sellados en inventario)...")

    all_boosters = session.exec(
        select(ItemCatalog).where(
            ItemCatalog.item_type == ItemType.BOOSTER,
            ItemCatalog.is_active == True,
        )
    ).all()

    if not all_boosters:
        progress("  ⚠️  Sin boosters activos en catálogo. Saltando fase.")
        return

    normal_boosters = [b for b in all_boosters if not (b.item_metadata or {}).get("is_foil")]
    foil_boosters   = [b for b in all_boosters if     (b.item_metadata or {}).get("is_foil")]

    for p in players:
        user_id     = p["user_id"]
        personality = p["personality"]

        # — Boosters normales —
        for _ in range(personality["boosters_normal"]):
            active_normal_boosters = session.exec(
                select(ItemCatalog).where(
                    ItemCatalog.item_type == ItemType.BOOSTER,
                    ItemCatalog.is_active == True,
                )
            ).all()
            normal_boosters_list = [b for b in active_normal_boosters if not (b.item_metadata or {}).get("is_foil")]
            booster_item = _rng.choice(normal_boosters_list) if normal_boosters_list else None
            if not booster_item:
                break
            try:
                ShopService.buy_item(
                    session=session,
                    user_id=user_id,
                    item_id=booster_item.id,
                    payment_currency=CurrencyType.AXOGEMA,
                )
                stats["boosters_bought"] = stats.get("boosters_bought", 0) + 1
                print(f"  📦 {user_id}: compró booster normal '{booster_item.name}' (sellado)")
            except HTTPException as e:
                errors.append(f"booster_buy {user_id}: {e.detail}")

        # — Booster Foil —
        for _ in range(personality["boosters_foil"]):
            active_foil_boosters = session.exec(
                select(ItemCatalog).where(
                    ItemCatalog.item_type == ItemType.BOOSTER,
                    ItemCatalog.is_active == True,
                )
            ).all()
            foil_boosters_list = [b for b in active_foil_boosters if (b.item_metadata or {}).get("is_foil")]
            if foil_boosters_list:
                foil_item = foil_boosters_list[0]
                try:
                    ShopService.buy_item(
                        session=session,
                        user_id=user_id,
                        item_id=foil_item.id,
                        payment_currency=CurrencyType.AXOGEMA,
                    )
                    stats["boosters_foil_bought"] = stats.get("boosters_foil_bought", 0) + 1
                    print(f"  ✨ {user_id}: compró Booster Foil '{foil_item.name}' (sellado)")
                except HTTPException as e:
                    errors.append(f"foil_buy {user_id}: {e.detail}")

        # Resumen final del inventario sellado actual
        sealed_rows = session.exec(
            select(PlayerInventory)
            .join(ItemCatalog, PlayerInventory.item_id == ItemCatalog.id)
            .where(
                PlayerInventory.user_id == user_id,
                ItemCatalog.item_type == ItemType.BOOSTER,
                PlayerInventory.quantity > 0,
            )
        ).all()
        n_sealed = sum(inv.quantity for inv in sealed_rows)
        strategy_label = BOOSTER_OPEN_STRATEGY.get(personality["name"], "all")
        if n_sealed:
            print(f"  💼 {user_id}: {n_sealed} sobre(s) de colección sellados iniciales "
                  f"[estrategia: {strategy_label}]")

    progress(f"  ✅ Sobres comprados: {stats.get('boosters_bought', 0)} normales + "
             f"{stats.get('boosters_foil_bought', 0)} foil | "
             f"cartas: {stats.get('cards_opened', 0)}")


def phase_open_boosters(
    session: Session,
    players: list[dict],
    stats: dict,
    errors: list,
    progress,
    *,
    label: str = "",
    filter_strategy: set[str] | None = None,
) -> None:
    """
    Abre boosters del inventario del jugador de acuerdo a su estrategia,
    abriendo la mayoría y dejando unos pocos (1-3) sellados.
    """
    tag = f" [{label}]" if label else ""
    progress(f"  🎴 Abriendo sobres sellados{tag}...")

    for p in players:
        user_id     = p["user_id"]
        personality = p["personality"]
        strategy    = BOOSTER_OPEN_STRATEGY.get(personality["name"], "all")

        if filter_strategy is not None and strategy not in filter_strategy:
            continue

        # Recuperar sobres sellados en inventario
        booster_invs = session.exec(
            select(PlayerInventory)
            .join(ItemCatalog, PlayerInventory.item_id == ItemCatalog.id)
            .where(
                PlayerInventory.user_id == user_id,
                ItemCatalog.item_type == ItemType.BOOSTER,
                PlayerInventory.quantity > 0,
            )
        ).all()

        if not booster_invs:
            print(f"  ℹ️  {user_id}{tag}: sin sobres sellados")
            continue

        to_open_list = []
        for inv in booster_invs:
            item = session.get(ItemCatalog, inv.item_id)
            is_foil = (item.item_metadata or {}).get("is_foil", False) if item else False
            qty = inv.quantity

            if strategy == "immediate":
                open_qty = qty
            elif strategy == "selective":
                if is_foil:
                    open_qty = qty
                else:
                    open_qty = int(qty * 0.80)
                    if open_qty == qty and qty > 1:
                        open_qty = qty - 1
            elif strategy == "random":
                open_qty = int(qty * 0.85)
                if open_qty == qty and qty > 1:
                    open_qty = qty - 1
            elif strategy == "hoarder":
                open_qty = int(qty * 0.75)
                if open_qty == qty and qty > 1:
                    open_qty = qty - 1
            else:
                open_qty = qty

            if qty > 0 and open_qty == 0:
                open_qty = max(1, int(qty * 0.5))

            if open_qty > 0:
                to_open_list.append((inv, open_qty))

        total_opened = 0
        for inv, open_qty in to_open_list:
            for _ in range(open_qty):
                try:
                    res = open_booster(
                        request=OpenBoosterRequest(item_id=inv.item_id),
                        session=session,
                        verified_user_id=user_id,
                    )
                    cards_gained = len(res.get("cards", []))
                    stats["cards_opened"] = stats.get("cards_opened", 0) + cards_gained
                    shiny = sum(1 for c in res.get("cards", []) if c.get("is_shiny"))
                    total_opened += 1
                except HTTPException as e:
                    errors.append(f"booster_open{tag} {user_id}: {e.detail}")
                    break

        current_sealed = session.exec(
            select(PlayerInventory)
            .join(ItemCatalog, PlayerInventory.item_id == ItemCatalog.id)
            .where(
                PlayerInventory.user_id == user_id,
                ItemCatalog.item_type == ItemType.BOOSTER,
                PlayerInventory.quantity > 0,
            )
        ).all()
        n_sealed = sum(inv.quantity for inv in current_sealed)

        if total_opened > 0:
            print(f"  🎴 {user_id}{tag}: {total_opened} sobre(s) abiertos | {n_sealed} sellado(s) conservado(s)")
        else:
            print(f"  ℹ️  {user_id}{tag}: ningún sobre abierto en este momento | {n_sealed} sellado(s) conservado(s)")

    progress(f"  ✅ Sobres abiertos{tag}. Cartas totales hasta ahora: {stats.get('cards_opened', 0)}")


# ═══════════════════════════════════════════════════════════════════════════════
# FASE 4: COMPRA DE WEBITOS + INCUBACIÓN REAL + INTERACCIONES
# ═══════════════════════════════════════════════════════════════════════════════

def _interact_eggs(session: Session, user_id: str, incubation_time_s: int) -> None:
    """
    Espera a que los huevos estén listos para eclosionar.
    El sistema de calor/congelado/cuidado fue retirado: los huevos eclosionan
    únicamente por tiempo (imprinting), así que solo esperamos el período.
    """
    wait_s = max(1, incubation_time_s)
    print(f"    ⏳ Esperando {wait_s}s mientras incuban los huevos...")
    time.sleep(wait_s)


def phase_incubation(
    session: Session,
    players: list[dict],
    incubation_secs: int,
    stats: dict,
    errors: list,
    progress,
    live_progress=None,
) -> None:
    """
    Compra huevos, establece timer de incubación de ~incubation_secs segundos,
    interactúa durante la espera mostrando barra de progreso en vivo, y eclosiona.

    live_progress: callback(msg) que sobreescribe la línea actual con \\r.
                   Si es None se usa progress() normal.
    """
    def _live(msg: str) -> None:
        if live_progress:
            live_progress(msg)
        else:
            progress(msg)

    progress(f"  🥚 Iniciando incubación con timer real de ~{incubation_secs}s...")

    initial_egg = session.exec(
        select(ItemCatalog).where(
            ItemCatalog.item_type == ItemType.EGG,
            ItemCatalog.is_active == True,
        )
    ).first()
    if not initial_egg:
        progress("  ⚠️  Sin webitos activos en catálogo. Saltando fase.")
        return

    # ── Comprar huevos y registrar incubaciones ───────────────────────────────
    total_eggs = 0
    for p in players:
        user_id     = p["user_id"]
        personality = p["personality"]
        n_eggs      = personality["eggs"]

        for _ in range(n_eggs):
            egg_item = session.exec(
                select(ItemCatalog).where(
                    ItemCatalog.item_type == ItemType.EGG,
                    ItemCatalog.is_active == True,
                )
            ).first()
            if not egg_item:
                break
            try:
                ShopService.buy_item(
                    session=session,
                    user_id=user_id,
                    item_id=egg_item.id,
                    payment_currency=CurrencyType.AXOGEMA,
                )
                stats["eggs_bought"] = stats.get("eggs_bought", 0) + 1
            except HTTPException as e:
                errors.append(f"egg_buy {user_id}: {e.detail}")

        # Crear registros WebitoIncubation a partir del inventario
        try:
            get_user_incubations(user_id=user_id, session=session, verified_user_id=user_id)
        except Exception:
            session.rollback()

        # Ajustar timer de eclosión (±20% jitter)
        jitter = _rng.uniform(-0.20, 0.20)
        target_secs = max(20, int(incubation_secs * (1 + jitter)))
        user_incs = session.exec(
            select(WebitoIncubation).where(WebitoIncubation.user_id == user_id)
        ).all()
        for inc in user_incs:
            inc.fecha_eclosion_estimada = datetime.utcnow() + timedelta(seconds=target_secs)
            session.add(inc)
        session.commit()
        total_eggs += len(user_incs)
        print(f"  🥚 {user_id}: {len(user_incs)} huevo(s) → timer {target_secs}s")

    # ── Loop de interacción con barra de progreso ─────────────────────────────
    start_time     = datetime.utcnow()
    global_deadline = start_time + timedelta(seconds=incubation_secs + 30)
    wait_s         = min(10, max(3, incubation_secs // 8))

    total_clicks = 0
    total_pets   = 0
    total_songs  = 0

    def _render_bar() -> None:
        """Dibuja la barra de progreso en la misma línea (\\r)."""
        elapsed  = (datetime.utcnow() - start_time).total_seconds()
        pct      = min(100.0, elapsed / incubation_secs * 100)
        resta_s  = max(0, incubation_secs - elapsed)
        bar      = _make_bar(pct)
        # Huevos listos = los cuya fecha_eclosion ya pasó
        all_incs = []
        for p in players:
            all_incs += session.exec(
                select(WebitoIncubation).where(WebitoIncubation.user_id == p["user_id"])
            ).all()
        n_ready = sum(1 for i in all_incs if i.fecha_eclosion_estimada <= datetime.utcnow())
        _live(
            f"  ⏳ [{bar}] {pct:5.1f}% │ {resta_s:4.0f}s rest │"
            f" 🥚 {n_ready}/{total_eggs} listos │"
            f" 👆 {total_clicks:5} │ 🫶 {total_pets:3} │ 🎵 {total_songs:3}"
        )

    progress(f"  ⏳ Interactuando con {total_eggs} huevo(s) durante ~{incubation_secs}s…")

    while datetime.utcnow() < global_deadline:
        all_ready = True

        # El calor/cuidado fue retirado: los huevos eclosionan solo por tiempo.
        # Solo verificamos si todos ya cumplieron su fecha de eclosión.
        for p in players:
            user_id = p["user_id"]
            incs = session.exec(
                select(WebitoIncubation).where(WebitoIncubation.user_id == user_id)
            ).all()
            if any(i.fecha_eclosion_estimada > datetime.utcnow() for i in incs):
                all_ready = False

        if all_ready:
            _render_bar()          # barra al 100 % antes de romper
            progress("\n  🎉 ¡Todos los huevos listos para eclosionar!")
            break

        # ── Countdown segundo a segundo con barra live ────────────────────────
        for remaining in range(wait_s, 0, -1):
            _render_bar()
            time.sleep(1)

    # Línea nueva tras las actualizaciones en vivo
    if live_progress:
        progress("")   # fuerza salto de línea en terminal

    # ── Eclosionar ────────────────────────────────────────────────────────────
    progress("  🐣 Eclosionando huevos listos...")
    for p in players:
        user_id = p["user_id"]
        incs = session.exec(
            select(WebitoIncubation).where(WebitoIncubation.user_id == user_id)
        ).all()
        for inc in incs:
            if inc.fecha_eclosion_estimada > datetime.utcnow():
                inc.fecha_eclosion_estimada = datetime.utcnow() - timedelta(seconds=5)
                session.add(inc)
                session.commit()
            try:
                res = hatch_webito(
                    incubation_id=inc.id,
                    session=session,
                    verified_user_id=user_id,
                )
                stats["eggs_hatched"] = stats.get("eggs_hatched", 0) + 1
                axo_name = res.get("axolotito", {}).get("name", "?")
                axo_id = res.get("axolotito", {}).get("id")
                axo_obj = session.get(Axolotito, axo_id)
                axo_nature = axo_obj.nature if axo_obj else "?"
                print(f"  🐣 {user_id}: eclosionó '{axo_name}' con naturaleza '{axo_nature}'")
            except Exception as e:
                session.rollback()
                errors.append(f"hatch {user_id}: {e}")

    progress(f"  ✅ {stats.get('eggs_hatched', 0)} Axolotito(s) eclosionados "
             f"│ 👆 {total_clicks} clicks │ 🫶 {total_pets} caricias │ 🎵 {total_songs} canciones")


# ═══════════════════════════════════════════════════════════════════════════════
# FASE 5: GASHAPON
# ═══════════════════════════════════════════════════════════════════════════════

def phase_gashapon(session: Session, players: list[dict], stats: dict, errors: list, progress) -> None:
    progress("  🎰 Jugando gashapon y cápsulas...")

    for p in players:
        user_id     = p["user_id"]
        personality = p["personality"]

        # — Gashapon estándar —
        for roll_i in range(personality.get("gashapon_rolls", 1)):
            try:
                res = roll_gashapon(
                    request=GashaponRollRequest(user_id=user_id),
                    session=session,
                    verified_user_id=user_id,
                )
                prize = res.get("item_name") or res.get("prize") or res.get("resultado", "?")
                print(f"  🎰 {user_id} roll #{roll_i+1}: {prize}")
                stats["gashapon_rolls"] = stats.get("gashapon_rolls", 0) + 1
            except HTTPException as e:
                errors.append(f"gashapon {user_id}: {e.detail}")

        # — Cápsula diaria —
        try:
            res = claim_daily_capsule(session=session, verified_user_id=user_id)
            prize = res.get("item_name") or res.get("resultado", "?")
            print(f"  💊 {user_id}: cápsula diaria → {prize}")
            stats["capsule_claims"] = stats.get("capsule_claims", 0) + 1
        except HTTPException as e:
            if e.status_code in (400, 409):
                print(f"  ℹ️  {user_id}: cápsula diaria ya reclamada hoy ({e.detail})")
            else:
                errors.append(f"capsule {user_id}: {e.detail}")

        # — Cápsulas de Tier extra —
        tier = "bronce"
        try:
            res = roll_capsule(
                request=CapsuleRollRequest(tier=tier),
                session=session,
                verified_user_id=user_id,
            )
            print(f"  💊 {user_id}: cápsula {tier} → {res.get('item_name', '?')}")
        except HTTPException as e:
            errors.append(f"capsule_roll {user_id}: {e.detail}")

        # — Triple Suerte —
        if personality.get("does_triple_suerte"):
            try:
                res = roll_triple_suerte(
                    request=TripleSuerteRequest(),
                    session=session,
                    verified_user_id=user_id
                )
                prizes = [r.get("item_name", "?") for r in res.get("results", [])]
                print(f"  🌟 {user_id}: Triple Suerte → {prizes}")
                stats["triple_suerte"] = stats.get("triple_suerte", 0) + 1
            except HTTPException as e:
                errors.append(f"triple_suerte {user_id}: {e.detail}")

    progress(f"  ✅ Gashapon: {stats.get('gashapon_rolls', 0)} rolls, "
             f"{stats.get('capsule_claims', 0)} cápsulas.")


# ═══════════════════════════════════════════════════════════════════════════════
# FASE 6: TABLAS
# ═══════════════════════════════════════════════════════════════════════════════

def phase_boards(session: Session, players: list[dict], stats: dict, errors: list, progress) -> dict[str, list[int]]:
    """Compra slots si hacen falta; crea tableros aleatorios y 1 manual. Retorna {user_id: [board_ids]}."""
    progress("  📋 Creando tableros (aleatorios + manual)...")
    boards_by_user: dict[str, list[int]] = {}

    for p in players:
        user_id     = p["user_id"]
        personality = p["personality"]
        user        = session.exec(select(User).where(User.privy_did == user_id)).first()
        if not user:
            continue

        n_random = personality.get("boards_random", 2)
        ids: list[int] = []

        # Verificar si necesita más slots
        current_boards = session.exec(
            select(func.count(PlayerBoard.id))
            .where(PlayerBoard.user_id == user_id, PlayerBoard.is_dead == False)
        ).one()
        needed = n_random + 1  # +1 para el manual
        if (user.unlocked_board_slots or 3) < needed:
            user.unlocked_board_slots = needed + 1
            session.add(user)
            session.commit()
            print(f"  🔓 {user_id}: slots ampliados a {user.unlocked_board_slots}")

        # Tableros aleatorios
        for b_i in range(n_random):
            try:
                res = create_random_board(
                    payload=CreateManualBoardRequest(
                        name=f"Tabla {personality['name'].title()} #{b_i+1}",
                        card_ids=[],
                    ),
                    session=session,
                    verified_user_id=user_id,
                )
                bid = res.get("board_id")
                if bid:
                    ids.append(bid)
                    stats["boards_created"] = stats.get("boards_created", 0) + 1
                    print(f"  📋 {user_id}: tabla aleatoria #{bid} ({len(res.get('card_ids',[]))} cartas)")
            except HTTPException as e:
                errors.append(f"board_random {user_id}: {e.detail}")

        # Tablero manual (con las cartas del inventario)
        inv_cards = session.exec(
            select(PlayerInventory)
            .join(ItemCatalog, PlayerInventory.item_id == ItemCatalog.id)
            .where(
                PlayerInventory.user_id == user_id,
                ItemCatalog.item_type == ItemType.CARD,
                PlayerInventory.quantity > 0,
            )
        ).all()

        if len(inv_cards) >= 16:
            selected = _rng.sample(inv_cards, 16)
            card_ids = [inv.item_id for inv in selected]
            try:
                res = create_manual_board(
                    payload=CreateManualBoardRequest(
                        name=f"Tabla Manual {personality['name'].title()}",
                        card_ids=card_ids,
                    ),
                    session=session,
                    verified_user_id=user_id,
                )
                bid = res.get("board_id")
                if bid:
                    ids.append(bid)
                    stats["boards_created"] = stats.get("boards_created", 0) + 1
                    stats["manual_boards"]   = stats.get("manual_boards", 0) + 1
                    print(f"  🖊️  {user_id}: tabla MANUAL #{bid}")
            except HTTPException as e:
                errors.append(f"board_manual {user_id}: {e.detail}")
        else:
            print(f"  ℹ️  {user_id}: pocas cartas ({len(inv_cards)}) para tabla manual")

        boards_by_user[user_id] = ids

    progress(f"  ✅ {stats.get('boards_created', 0)} tableros creados "
             f"({stats.get('manual_boards', 0)} manuales).")
    return boards_by_user


# ═══════════════════════════════════════════════════════════════════════════════
# FASE 2b: SEED TICKETS
# ═══════════════════════════════════════════════════════════════════════════════

def phase_seed_tickets(session: Session, players: list[dict], stats: dict, errors: list, progress) -> None:
    progress("  📦 Sembrando Cápsulas iniciales para los jugadores...")

    all_consumables = session.exec(
        select(ItemCatalog).where(ItemCatalog.item_type == ItemType.CONSUMABLE)
    ).all()
    capsula_items = {}
    for tier in ("bronce", "plata", "oro"):
        capsula_items[tier] = next(
            (c for c in all_consumables if (c.item_metadata or {}).get("capsule_tier") == tier),
            None
        )

    for p in players:
        user_id = p["user_id"]
        personality = p["personality"]
        tiers_qty = {"bronce": 3, "plata": 2, "oro": 1}
        if personality.get("name") in ("whale", "collector"):
            tiers_qty = {"bronce": 5, "plata": 3, "oro": 2}

        for tier, qty in tiers_qty.items():
            item = capsula_items.get(tier)
            if not item:
                continue
            inv_item = session.exec(
                select(PlayerInventory)
                .where(PlayerInventory.user_id == user_id)
                .where(PlayerInventory.item_id == item.id)
            ).first()
            if inv_item:
                inv_item.quantity += qty
            else:
                inv_item = PlayerInventory(
                    user_id=user_id,
                    item_id=item.id,
                    quantity=qty,
                    is_first_edition=False,
                    is_shiny=False
                )
            session.add(inv_item)
            print(f"  📦 {user_id}: +{qty} Cápsula {tier.capitalize()} en inventario")
    session.commit()


# ═══════════════════════════════════════════════════════════════════════════════
# FASE 6c: CARD MELTER (FUNDICIÓN & FORJA)
# ═══════════════════════════════════════════════════════════════════════════════

def phase_card_melter(session: Session, players: list[dict], stats: dict, errors: list, progress) -> None:
    progress("  🧪 Iniciando Cenote Místico (Card Melter: Melt & Forge)...")
    from app.models.items import Rarity

    for p in players:
        user_id = p["user_id"]
        personality = p["personality"]

        if personality["name"] not in ("whale", "collector", "aggressive"):
            continue

        melted_any = True
        while melted_any:
            melted_any = False
            inv_cards = session.exec(
                select(PlayerInventory)
                .join(ItemCatalog, PlayerInventory.item_id == ItemCatalog.id)
                .where(
                    PlayerInventory.user_id == user_id,
                    ItemCatalog.item_type == ItemType.CARD,
                    PlayerInventory.quantity >= 5,
                    PlayerInventory.is_shiny == False
                )
            ).all()

            for inv in inv_cards:
                card = session.get(ItemCatalog, inv.item_id)
                if not card or card.rarity not in (Rarity.COMMON, Rarity.RARE, Rarity.EPIC):
                    continue

                cost_map = {Rarity.COMMON: 100.0, Rarity.RARE: 250.0, Rarity.EPIC: 1500.0}
                cost = cost_map.get(card.rarity, 99999.0)

                wallet = BankService.get_or_create_wallet(session, user_id)
                if wallet.frijolitos >= cost:
                    try:
                        res = melt_card(
                            request=MeltCardRequest(card_id=inv.item_id, is_first_edition=inv.is_first_edition),
                            session=session,
                            verified_user_id=user_id
                        )
                        stats["cards_melted"] = stats.get("cards_melted", 0) + 5
                        stats["melter_fusions"] = stats.get("melter_fusions", 0) + 1
                        new_card_name = res.get("new_card", {}).get("name", "?")
                        new_card_rarity = res.get("new_card", {}).get("rarity", "?")
                        print(f"  🧪 {user_id}: fundió 5 copias de '{card.name}' ({card.rarity.value}) -> obtuvo '{new_card_name}' ({new_card_rarity})")
                        melted_any = True
                        break
                    except HTTPException as e:
                        errors.append(f"melt {user_id}: {e.detail}")

        wallet = BankService.get_or_create_wallet(session, user_id)
        forge_options = [
            ("Legendaria", Rarity.LEGENDARY, "frag_legendario", 500, 3000.0),
            ("Épica", Rarity.EPIC, "frag_epico", 250, 1000.0),
            ("Rara", Rarity.RARE, "frag_raro", 100, 500.0),
            ("Común", Rarity.COMMON, "frag_comun", 50, 100.0)
        ]

        for rarity_label, rarity_enum, frag_field, frag_cost, gal_cost in forge_options:
            frags_qty = getattr(wallet, frag_field, 0)
            if frags_qty >= frag_cost and wallet.frijolitos >= gal_cost:
                owned_card_ids = session.exec(
                    select(PlayerInventory.item_id)
                    .join(ItemCatalog, PlayerInventory.item_id == ItemCatalog.id)
                    .where(PlayerInventory.user_id == user_id, ItemCatalog.item_type == ItemType.CARD)
                ).all()

                forgeable_cards = session.exec(
                    select(ItemCatalog)
                    .where(
                        ItemCatalog.item_type == ItemType.CARD,
                        ItemCatalog.rarity == rarity_enum,
                        ItemCatalog.is_active == True,
                        ~ItemCatalog.id.in_(owned_card_ids) if owned_card_ids else True
                    )
                ).all()

                if not forgeable_cards:
                    forgeable_cards = session.exec(
                        select(ItemCatalog)
                        .where(ItemCatalog.item_type == ItemType.CARD, ItemCatalog.rarity == rarity_enum, ItemCatalog.is_active == True)
                    ).all()

                if forgeable_cards:
                    target_card = _rng.choice(forgeable_cards)
                    try:
                        res = forge_card(
                            request=ForgeCardRequest(target_card_id=target_card.id),
                            session=session,
                            verified_user_id=user_id
                        )
                        stats["cards_forged"] = stats.get("cards_forged", 0) + 1
                        print(f"  🔨 {user_id}: forjó '{target_card.name}' ({rarity_label}) usando {frag_cost} fragmentos y {gal_cost} GAL")
                        wallet = BankService.get_or_create_wallet(session, user_id)
                    except HTTPException as e:
                        errors.append(f"forge {user_id}: {e.detail}")


# ═══════════════════════════════════════════════════════════════════════════════
# FASE 6d: BOARD DECONSTRUCTION (DESARME SEGURO)
# ═══════════════════════════════════════════════════════════════════════════════

def phase_board_deconstruction(session: Session, players: list[dict], boards_by_user: dict[str, list[int]], stats: dict, errors: list, progress) -> None:
    progress("  🧴 Simulando desarme seguro con Solvente de Pegamento...")

    for p in players:
        user_id = p["user_id"]
        if p["personality"]["name"] not in ("casual", "aggressive"):
            continue

        user_boards = boards_by_user.get(user_id, [])
        if len(user_boards) < 2:
            continue

        board_id = user_boards.pop()
        wallet = BankService.get_or_create_wallet(session, user_id)
        if wallet.frijolitos < 120.0:
            wallet.frijolitos += 150.0
            session.add(wallet)
            session.commit()

        try:
            res = delete_board(board_id=board_id, session=session, verified_user_id=user_id)
            stats["boards_deconstructed"] = stats.get("boards_deconstructed", 0) + 1
            print(f"  🧴 {user_id}: desarmó la tabla #{board_id} usando Solvente de Pegamento (120 GAL). 16 cartas devueltas.")
        except HTTPException as e:
            errors.append(f"deconstruct {user_id} board #{board_id}: {e.detail}")


# ═══════════════════════════════════════════════════════════════════════════════
# FASE 6e: MERCADO SECUNDARIO P2P (BOOSTERS)
# ═══════════════════════════════════════════════════════════════════════════════

def phase_p2p_market(session: Session, players: list[dict], stats: dict, errors: list, progress) -> None:
    progress("  🤝 Simulando Mercado Secundario P2P (Listado y Venta)...")

    for p in players:
        user_id = p["user_id"]
        personality = p["personality"]

        if personality["name"] == "whale":
            continue

        sealed_boosters = session.exec(
            select(PlayerInventory)
            .join(ItemCatalog, PlayerInventory.item_id == ItemCatalog.id)
            .where(
                PlayerInventory.user_id == user_id,
                ItemCatalog.item_type == ItemType.BOOSTER,
                PlayerInventory.quantity > 0
            )
        ).all()

        for inv in sealed_boosters:
            item = session.get(ItemCatalog, inv.item_id)
            is_foil = (item.item_metadata or {}).get("is_foil", False) if item else False
            price = 500.0 if is_foil else 200.0

            try:
                res = list_inventory_item(
                    request=ListInventoryItemRequest(inventory_id=inv.id, quantity=1, price_gal=price),
                    session=session,
                    verified_user_id=user_id
                )
                stats["p2p_listings"] = stats.get("p2p_listings", 0) + 1
                print(f"  🤝 {user_id}: listó sobre '{item.name if item else 'Booster'}' en P2P a {price} GAL")
            except HTTPException as e:
                errors.append(f"p2p_list {user_id}: {e.detail}")

    for p in players:
        user_id = p["user_id"]
        personality = p["personality"]

        if personality["name"] not in ("whale", "collector"):
            continue

        listings = get_inventory_listings(item_type=ItemType.BOOSTER, session=session)
        if not listings:
            break

        bought_count = 0
        for listing in listings:
            if bought_count >= 2:
                break

            listing_id = listing["id"]
            seller_id = listing["seller_id"]
            price = listing["price_gal"]

            if seller_id == user_id:
                continue

            wallet = BankService.get_or_create_wallet(session, user_id)
            if wallet.frijolitos < price:
                wallet.frijolitos += price + 100.0
                session.add(wallet)
                session.commit()

            try:
                res = buy_inventory_listing(listing_id=listing_id, session=session, verified_user_id=user_id)
                stats["p2p_purchases"] = stats.get("p2p_purchases", 0) + 1
                print(f"  🤝 {user_id}: compró sobre en P2P por {price} GAL del vendedor {seller_id}")
                bought_count += 1
            except HTTPException as e:
                errors.append(f"p2p_buy {user_id}: {e.detail}")


# ═══════════════════════════════════════════════════════════════════════════════
# FASE 7: VIP
# ═══════════════════════════════════════════════════════════════════════════════

def phase_vip(session: Session, players: list[dict], stats: dict, errors: list, progress) -> None:
    """Activa VIP para los jugadores que lo tengan en su personalidad y verifica los beneficios."""
    progress("  👑 Activando y verificando VIP Club...")

    vip_items = session.exec(
        select(ItemCatalog).where(
            ItemCatalog.is_active == True,
        )
    ).all()
    vip_catalog = {
        (item.item_metadata or {}).get("vip_tier"): item
        for item in vip_items
        if (item.item_metadata or {}).get("is_vip")
    }

    if not vip_catalog:
        progress("  ⚠️  Sin items VIP en catálogo. Saltando fase.")
        return

    for p in players:
        user_id     = p["user_id"]
        personality = p["personality"]
        tier        = personality.get("vip_tier")
        if not tier or tier not in vip_catalog:
            continue

        item = vip_catalog[tier]
        user = session.exec(select(User).where(User.privy_did == user_id)).first()
        wallet = BankService.get_or_create_wallet(session, user_id)

        if not user.is_vip:
            # Asegurar saldo suficiente en AXG para la membresía
            if wallet.axofichas < item.price_axg:
                wallet.axofichas = item.price_axg + 100
                session.add(wallet)
                session.commit()

            try:
                res = ShopService.buy_item(
                    session=session,
                    user_id=user_id,
                    item_id=item.id,
                    payment_currency=CurrencyType.AXOGEMA,
                )
                session.refresh(user)
                stats["vip_activations"] = stats.get("vip_activations", 0) + 1
                welcome_gal = res.get("welcome_gal_bonus", 0) if isinstance(res, dict) else 0
                print(f"  👑 {user_id}: VIP {tier.upper()} activado"
                      + (f" (+{welcome_gal} GAL bienvenida)" if welcome_gal else ""))
            except HTTPException as e:
                errors.append(f"vip_buy {user_id} {tier}: {e.detail}")
                continue
        else:
            print(f"  👑 {user_id}: VIP {tier.upper()} ya estaba activo desde el inicio (compras con descuento)")

        # ── Verificar beneficios VIP ──────────────────────────────────────────

        # 1. Descuento en tienda: comprar un CONSUMABLE y ver que tiene descuento
        consumable = session.exec(
            select(ItemCatalog).where(
                ItemCatalog.item_type == ItemType.CONSUMABLE,
                ItemCatalog.is_active == True,
                ItemCatalog.price_axg > 0,
            )
        ).first()
        if consumable:
            wallet_before = wallet.axofichas
            try:
                ShopService.buy_item(
                    session=session,
                    user_id=user_id,
                    item_id=consumable.id,
                    payment_currency=CurrencyType.AXOGEMA,
                )
                session.refresh(wallet)
                paid = wallet_before - wallet.axofichas
                expected_no_discount = consumable.price_axg
                if paid < expected_no_discount:
                    pct = round((1 - paid / expected_no_discount) * 100, 1)
                    print(f"  🏷️  {user_id}: descuento VIP verificado: {pct:.1f}% ({expected_no_discount} → {paid:.2f} AXG)")
                else:
                    print(f"  ℹ️  {user_id}: compra consumible sin descuento observable (precio: {paid:.2f})")
            except HTTPException as e:
                errors.append(f"vip_discount_check {user_id}: {e.detail}")

        # 2. Reclamar GAL diario VIP
        try:
            from app.api.v1.endpoints.user import claim_daily_vip_gal
            claim_res = claim_daily_vip_gal(session=session, verified_user_id=user_id)
            session.refresh(wallet)
            print(f"  🌿 {user_id}: GAL VIP reclamado → {claim_res.get('claimed_gal', 0):.0f} GAL")
            stats["vip_gal_claimed"] = stats.get("vip_gal_claimed", 0) + 1
        except HTTPException as e:
            if e.status_code == 400:
                print(f"  ℹ️  {user_id}: GAL VIP ya reclamado hoy ({e.detail})")
            else:
                errors.append(f"vip_claim {user_id}: {e.detail}")
        except ImportError:
            pass

        # 3. Verificar que is_vip = True en User
        session.refresh(user)
        assert user.is_vip, f"❌ {user_id}: is_vip debería ser True tras comprar {tier}"
        print(f"  ✅ {user_id}: is_vip={user.is_vip}, tier={user.vip_tier}, "
              f"días={user.vip_days_remaining if hasattr(user, 'vip_days_remaining') else 'N/A'}")

    progress(f"  ✅ VIP activado para {stats.get('vip_activations', 0)} jugadores.")


# ═══════════════════════════════════════════════════════════════════════════════
# FASE 8: PARTIDAS INDIVIDUALES + AUTOJUEGO
# ═══════════════════════════════════════════════════════════════════════════════

def phase_individual_play(
    session: Session,
    players: list[dict],
    boards_by_user: dict[str, list[int]],
    stats: dict,
    errors: list,
    progress,
) -> None:
    progress("  🎮 Simulando partidas individuales y autojuego...")

    for p in players:
        user_id     = p["user_id"]
        personality = p["personality"]
        play_style  = personality.get("play_style", "rookie")

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
                        outcome = f"🏆 +{result.get('prize_gal', 0):.1f} GAL"
                    else:
                        stats["losses"] = stats.get("losses", 0) + 1
                        outcome = f"💔 +{result.get('prize_gal', 0):.1f} GAL"
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
                if wallet.frijolitos < budget:
                    wallet.frijolitos = budget + 200
                    session.add(wallet)
                    session.commit()

                session.refresh(axo)
                if axo.energy_current < 10:
                    axo.energy_current = axo.stat_stamina or 100
                    session.add(axo)
                    session.commit()

                print(f"  🤖 {axo.name}: autojuego con {budget} GAL de presupuesto...")
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

    progress(f"  ✅ Partidas: {stats.get('games_played',0)} jugadas, "
             f"{stats.get('wins',0)} victorias, "
             f"{stats.get('autogames',0)} en autojuego.")


# ═══════════════════════════════════════════════════════════════════════════════
# FASE 9: MULTIJUGADOR + RECALL TEST
# ═══════════════════════════════════════════════════════════════════════════════

def _trigger_waiting_rooms(session: Session, stats: dict, errors: list, round_num: int) -> None:
    """Fuerza el inicio de todas las salas en espera con al menos 1 inscripción."""
    session.expire_all()
    waiting_rooms = session.exec(
        select(GameRoom).where(GameRoom.status == "waiting")
    ).all()
    for room in waiting_rooms:
        regs = session.exec(
            select(RoomRegistration).where(RoomRegistration.room_id == room.id)
        ).all()
        if not regs:
            continue
        room.status = "playing"
        session.add(room)
        session.commit()
        n_boards = sum(1 for r in regs)
        print(f"  🎮 Ronda {round_num} — '{room.name}' ({n_boards} axo(s)) ▶️ iniciando...")
        try:
            MultiplayerService.simulate_multiplayer_match(room.id)
            session.expire_all()
            stats["multi_rooms_simulated"] = stats.get("multi_rooms_simulated", 0) + 1
        except Exception as e:
            session.rollback()
            errors.append(f"multi_simulate room {room.id} ronda {round_num}: {e}")


def _read_new_logs(
    session: Session,
    registered: dict,
    all_logs: list,
) -> None:
    """Lee MultiplayerGameLog no notificados y los imprime + acumula en all_logs."""
    for axo_id, info in registered.items():
        user_id = info["user_id"]
        new_logs = session.exec(
            select(MultiplayerGameLog)
            .where(MultiplayerGameLog.user_id == user_id)
            .where(MultiplayerGameLog.notified == False)  # noqa: E712
            .order_by(MultiplayerGameLog.created_at.asc())
        ).all()
        for log in new_logs:
            icon = "🏆" if log.outcome == "Victoria" else "💔"
            print(f"    {icon} {log.axo_name:<22} │ {log.room_name:<26} │ "
                  f"Neto: {log.net_gal:+7.1f} GAL │ XP: +{log.xp_gained}")
            all_logs.append({
                "user_id": user_id,
                "axo_name": log.axo_name,
                "room_name": log.room_name,
                "outcome": log.outcome,
                "net_gal": log.net_gal,
                "xp_gained": log.xp_gained,
            })
            log.notified = True
            session.add(log)
        session.commit()


def phase_multiplayer(
    session: Session,
    players: list[dict],
    boards_by_user: dict[str, list[int]],
    stats: dict,
    errors: list,
    progress,
    wait_secs: int = 35,
) -> None:
    progress("  ⚔️  Simulando multijugador (con test de recall y espera real)...")

    # ── Construir lista de jugadores elegibles ─────────────────────────────────
    eligible: list[tuple] = []  # (player_dict, axo, [boards])
    for p in players:
        user_id = p["user_id"]
        axos = session.exec(
            select(Axolotito).where(
                Axolotito.user_id == user_id,
                Axolotito.status == "idle",
            )
        ).all()
        bids = boards_by_user.get(user_id, [])
        boards = session.exec(
            select(PlayerBoard).where(
                PlayerBoard.id.in_(bids),
                PlayerBoard.is_dead == False,
            )
        ).all() if bids else []
        if axos and boards:
            eligible.append((p, axos[0], boards))

    if len(eligible) < 2:
        progress("  ⚠️  Pocos elegibles para multijugador (necesita al menos 2). Saltando.")
        return

    # ── TEST DE RECALL ────────────────────────────────────────────────────────
    recall_p, recall_axo, recall_boards = eligible[0]
    recall_user = recall_p["user_id"]

    wallet_r = BankService.get_or_create_wallet(session, recall_user)
    wallet_r.frijolitos = max(wallet_r.frijolitos, 500.0)
    session.add(wallet_r)
    recall_axo.energy_current = max(recall_axo.energy_current, 20)
    session.add(recall_axo)
    session.commit()

    recall_board_ids = [b.id for b in recall_boards[:2]]
    try:
        register_axolotito(
            req=RegisterRequest(
                axolotito_id=recall_axo.id,
                room_type="rookie",
                boards=recall_board_ids,
                budget_gal=200.0,
                loss_limit_pct=30.0,
                profit_limit_pct=50.0,
            ),
            session=session,
            verified_user_id=recall_user,
        )
        session.refresh(recall_axo)
        print(f"  📝 RECALL TEST: '{recall_axo.name}' inscrito (status={recall_axo.status})")

        recall_res = recall_axolotito(
            axolotito_id=recall_axo.id,
            session=session,
            verified_user_id=recall_user,
        )
        session.refresh(recall_axo)
        if recall_res.get("immediate"):
            print(f"  ✅ RECALL: '{recall_axo.name}' retirado en espera → status={recall_axo.status}")
            stats["recall_tests_passed"] = stats.get("recall_tests_passed", 0) + 1
            settle_axolotito_escrow(
                axolotito_id=recall_axo.id,
                session=session,
                verified_user_id=recall_user,
            )
            session.refresh(recall_axo)
            print(f"  💰 RECALL: fondos recuperados, status={recall_axo.status}")
        else:
            print(f"  ⚠️  RECALL no inmediato: {recall_res.get('mensaje')}")
    except HTTPException as e:
        errors.append(f"recall_test: {e.detail}")

    # ── REGISTRAR TODOS LOS JUGADORES ────────────────────────────────────────
    # registered: axo_id -> {user_id, budget, board_ids, room_type}
    registered: dict[int, dict] = {}

    for p, axo, boards in eligible:
        user_id = p["user_id"]
        personality = p["personality"]

        # Elegir sala según personalidad
        room_type = "champion" if personality.get("play_style") == "champion" else "rookie"
        fee = 50.0 if room_type == "champion" else 10.0

        # 1-3 tablas aleatorias
        n_boards = _rng.randint(1, min(3, len(boards)))
        chosen_boards = _rng.sample(boards, n_boards)
        chosen_ids = [b.id for b in chosen_boards]

        # Presupuesto para 4-8 rondas
        rounds_target = _rng.randint(4, 8)
        budget = round(fee * n_boards * rounds_target, 2)

        wallet = BankService.get_or_create_wallet(session, user_id)
        if wallet.frijolitos < budget:
            wallet.frijolitos = budget + 200.0
            session.add(wallet)

        # Forzar idle + energía suficiente
        session.refresh(axo)
        if axo.status != "idle":
            axo.status = "idle"
            session.add(axo)
        if axo.energy_current < 10:
            axo.energy_current = axo.stat_stamina or 100
            session.add(axo)
        session.commit()

        loss_pct = _rng.choice([20.0, 30.0, 40.0])
        profit_pct = _rng.choice([40.0, 60.0, 80.0, 100.0])

        try:
            register_axolotito(
                req=RegisterRequest(
                    axolotito_id=axo.id,
                    room_type=room_type,
                    boards=chosen_ids,
                    budget_gal=budget,
                    loss_limit_pct=loss_pct,
                    profit_limit_pct=profit_pct,
                ),
                session=session,
                verified_user_id=user_id,
            )
            session.refresh(axo)
            room_reg = session.exec(
                select(RoomRegistration).where(RoomRegistration.axolotito_id == axo.id)
            ).first()
            if room_reg:
                registered[axo.id] = {
                    "user_id": user_id,
                    "budget": budget,
                    "board_ids": chosen_ids,
                    "room_type": room_type,
                    "room_id": room_reg.room_id,
                }
                print(f"  📋 '{axo.name}' [{personality['name']}] → sala {room_type} "
                      f"| {n_boards} tabla(s) | presupuesto {budget:.0f} GAL "
                      f"| SL={loss_pct:.0f}% TP={profit_pct:.0f}%")
        except HTTPException as e:
            errors.append(f"multi_register {user_id}: {e.detail}")

    if not registered:
        progress("  ⚠️  Ningún axolotito pudo registrarse. Saltando.")
        return

    # Acumular todos los resultados de todas las rondas
    all_match_logs: list[dict] = []

    # ── CICLO DE RONDAS ──────────────────────────────────────────────────────
    MAX_ROUNDS = 3
    for round_num in range(1, MAX_ROUNDS + 1):

        # Espera real simulando el lobby timer (30 s del scheduler)
        progress(f"  ⏳ Ronda {round_num}: esperando {wait_secs}s "
                 f"(como el scheduler en producción)...")
        for tick in range(wait_secs, 0, -1):
            time.sleep(1)
            if tick % 10 == 0 or tick <= 3:
                progress(f"    🕐 {tick}s...")

        # Disparar simulación de todas las salas en espera
        _trigger_waiting_rooms(session, stats, errors, round_num)

        # Leer y mostrar resultados de esta ronda
        print(f"\n  📊 Resultados ronda {round_num}:")
        _read_new_logs(session, registered, all_match_logs)

        # Liquidar los que terminaron (waiting_settlement)
        for axo_id, info in registered.items():
            axo = session.get(Axolotito, axo_id)
            if axo and axo.status == "waiting_settlement":
                try:
                    res = settle_axolotito_escrow(
                        axolotito_id=axo_id,
                        session=session,
                        verified_user_id=info["user_id"],
                    )
                    stats["multi_axos_settled"] = stats.get("multi_axos_settled", 0) + 1
                    print(f"  💵 '{axo.name}' liquidado → "
                          f"{res['refunded_gal']:.1f} GAL devueltos "
                          f"(neto: {res['net_performance']:+.1f} GAL)")
                except HTTPException as e:
                    errors.append(f"multi_settle {info['user_id']}: {e.detail}")

        # Revisar si queda alguien aún en juego (auto-re-inscrito)
        still_playing = [
            axo_id for axo_id in registered
            if (lambda a: a and a.status == "playing")(session.get(Axolotito, axo_id))
        ]
        if not still_playing:
            print(f"  🎉 Todos los axolotitos terminaron tras ronda {round_num}.")
            break
        if round_num < MAX_ROUNDS:
            print(f"  🔄 {len(still_playing)} axo(s) re-inscrito(s) automáticamente → ronda {round_num + 1}")

    # Recall + settle cualquier axo que siga en juego tras MAX_ROUNDS
    for axo_id, info in registered.items():
        axo = session.get(Axolotito, axo_id)
        if axo and axo.status == "playing":
            try:
                recall_axolotito(axolotito_id=axo_id, session=session, verified_user_id=info["user_id"])
                session.refresh(axo)
            except HTTPException:
                pass
            if axo.status == "waiting_settlement":
                try:
                    res = settle_axolotito_escrow(
                        axolotito_id=axo_id, session=session, verified_user_id=info["user_id"]
                    )
                    stats["multi_axos_settled"] = stats.get("multi_axos_settled", 0) + 1
                    print(f"  💵 '{axo.name}' (forzado) → {res['refunded_gal']:.1f} GAL")
                except HTTPException as e:
                    errors.append(f"multi_settle_forced {info['user_id']}: {e.detail}")

    # ── ESTADO DEL JACKPOT ───────────────────────────────────────────────────
    jackpot = session.exec(select(JackpotVault)).first()
    if jackpot:
        print(f"\n  💰 Jackpot actual: {jackpot.current_amount:.2f} GAL")
        recent_wins = session.exec(
            select(JackpotWin).order_by(JackpotWin.won_at.desc()).limit(5)
        ).all()
        if recent_wins:
            stats["multi_jackpot_won"] = stats.get("multi_jackpot_won", 0) + len(recent_wins)
            for jw in recent_wins:
                jp_axo = session.get(Axolotito, jw.axo_id)
                print(f"  🎰 JACKPOT: {jp_axo.name if jp_axo else '?'} "
                      f"ganó {jw.amount_won:.0f} GAL en turno #{jw.cards_drawn_count}")

    stats["multi_match_logs"] = all_match_logs

    victories = sum(1 for l in all_match_logs if l["outcome"] == "Victoria")
    total_net  = sum(l["net_gal"] for l in all_match_logs)

    progress(
        f"  ✅ Multi: {stats.get('multi_rooms_simulated', 0)} salas │ "
        f"{len(all_match_logs)} partidas │ "
        f"{victories} victorias │ "
        f"Neto total: {total_net:+.1f} GAL │ "
        f"{stats.get('recall_tests_passed', 0)} recall(s) pasaron │ "
        f"{stats.get('multi_axos_settled', 0)} liquidados."
    )


# ═══════════════════════════════════════════════════════════════════════════════
# FASE 10: TESTS DE RUTAS NEGATIVAS
# ═══════════════════════════════════════════════════════════════════════════════

def phase_error_tests(
    session: Session,
    players: list[dict],
    boards_by_user: dict[str, list[int]],
    stats: dict,
    errors_log: list,
    progress,
) -> None:
    """
    Intenta realizar acciones prohibidas para verificar que el backend las rechaza correctamente.
    Cada test DEBE lanzar HTTPException con el código esperado; si no lo hace, se reporta como FALLO.
    """
    progress("  🚫 Ejecutando tests de rutas negativas...")

    user_a = players[0]["user_id"]
    user_b = players[1]["user_id"] if len(players) > 1 else players[0]["user_id"]

    axos_a = session.exec(
        select(Axolotito).where(Axolotito.user_id == user_a)
    ).all()
    axos_b = session.exec(
        select(Axolotito).where(Axolotito.user_id == user_b)
    ).all()

    passed = 0
    failed = 0

    def expect_error(label: str, expected_code: int, fn):
        nonlocal passed, failed
        try:
            fn()
            # Si llegamos aquí, no hubo error — FALLO
            print(f"  ❌ ERROR TEST '{label}': esperaba {expected_code}, pero NO lanzó excepción")
            errors_log.append(f"error_test_missing_{label}")
            failed += 1
        except HTTPException as e:
            if e.status_code == expected_code:
                print(f"  ✅ [{expected_code}] {label}: '{e.detail[:60]}'")
                passed += 1
            else:
                print(f"  ⚠️  ERROR TEST '{label}': esperaba {expected_code}, obtuvo {e.status_code}")
                errors_log.append(f"error_test_wrong_code_{label}_{e.status_code}")
                failed += 1
        except Exception as e:
            # Error inesperado (no HTTP) — contar como fallo de test pero no de servidor
            print(f"  ⚠️  ERROR TEST '{label}': excepción no-HTTP: {type(e).__name__}: {str(e)[:60]}")
            failed += 1
        finally:
            try:
                session.rollback()
            except Exception:
                pass

    # Test 1: Comprar item con saldo insuficiente → 402/400
    item = session.exec(
        select(ItemCatalog).where(ItemCatalog.is_active == True, ItemCatalog.price_axg > 0)
    ).first()
    if item:
        wallet = BankService.get_or_create_wallet(session, user_a)
        old_axg = wallet.axofichas
        wallet.axofichas = 0.01
        session.add(wallet)
        session.commit()
        expect_error(
            "compra_sin_saldo",
            402,
            lambda: ShopService.buy_item(session, user_a, item.id, CurrencyType.AXOGEMA),
        )
        wallet.axofichas = old_axg
        session.add(wallet)
        session.commit()

    # Test 2: Interactuar con axolotito de otro usuario → 403
    if axos_a and axos_b:
        axo_b = axos_b[0]
        expect_error(
            "axo_ajeno_feed",
            403,
            lambda: GameService.feed_axolotito(
                axo_id=axo_b.id,
                food_type="shrimp",
                session=session,
                verified_user_id=user_a,
            ),
        )

    # Test 3: Jugar sin energía → 400
    if axos_a:
        axo = axos_a[0]
        session.refresh(axo)
        old_energy = axo.energy_current
        old_status = axo.status
        axo.energy_current = 0
        axo.status = "idle"
        boards_ids = boards_by_user.get(user_a, [])
        if boards_ids:
            axo.assigned_board_id = boards_ids[0]
        session.add(axo)
        session.commit()
        expect_error(
            "jugar_sin_energia",
            400,
            lambda: GameService.play_match(
                axolotito_id=axo.id,
                room_name="rookie",
                multiplier=1,
                bot_enabled=False,
                bot_budget_gal=0,
                bot_loss_limit_pct=30.0,
                bot_profit_limit_pct=50.0,
                session=session,
                verified_user_id=user_a,
            ),
        )
        axo.energy_current = old_energy
        axo.status = old_status
        session.add(axo)
        session.commit()

    # Test 4: Inscribir axolotito ya inscrito → 400
    if axos_a and boards_by_user.get(user_a):
        axo = axos_a[0]
        session.refresh(axo)
        if axo.status == "idle":
            bids = boards_by_user[user_a][:1]
            wallet = BankService.get_or_create_wallet(session, user_a)
            wallet.frijolitos = max(wallet.frijolitos, 500)
            session.add(wallet)
            session.commit()
            try:
                register_axolotito(
                    req=RegisterRequest(
                        axolotito_id=axo.id,
                        room_type="rookie",
                        boards=bids,
                        budget_gal=100.0,
                        loss_limit_pct=30.0,
                        profit_limit_pct=50.0,
                    ),
                    session=session,
                    verified_user_id=user_a,
                )
            except HTTPException:
                pass

            session.refresh(axo)
            if axo.status == "playing":
                expect_error(
                    "inscripcion_doble",
                    400,
                    lambda: register_axolotito(
                        req=RegisterRequest(
                            axolotito_id=axo.id,
                            room_type="rookie",
                            boards=bids,
                            budget_gal=100.0,
                            loss_limit_pct=30.0,
                            profit_limit_pct=50.0,
                        ),
                        session=session,
                        verified_user_id=user_a,
                    ),
                )
                # Limpiar
                axo.status = "idle"
                axo.escrow_balance_gal = 0.0
                session.add(axo)
                try:
                    session.exec(
                        delete(RoomRegistration).where(RoomRegistration.axolotito_id == axo.id)
                    )
                    session.commit()
                except Exception:
                    session.rollback()

    # Test 5: Eclosionar huevo inexistente → 404
    expect_error(
        "hatch_inexistente",
        404,
        lambda: hatch_webito(
            incubation_id=999999,
            session=session,
            verified_user_id=user_a,
        ),
    )

    # Test 6: Cambiar wallet por una ya registrada → 409
    if len(players) >= 2:
        wallet_b = players[1]["wallet_addr"]
        expect_error(
            "wallet_duplicada",
            409,
            lambda: sync_user(
                req=SyncRequest(
                    privy_did=user_a,
                    wallet_address=wallet_b,
                    email=None,
                ),
                session=session,
                verified_user_id=user_a,
            ),
        )

    # Test 7: Recall de axolotito que no está en sala → 400
    if axos_a:
        axo = axos_a[0]
        session.refresh(axo)
        if axo.status == "idle":
            expect_error(
                "recall_sin_sala",
                400,
                lambda: recall_axolotito(
                    axolotito_id=axo.id,
                    session=session,
                    verified_user_id=user_a,
                ),
            )

    stats["error_tests_passed"] = passed
    stats["error_tests_failed"] = failed
    progress(f"  ✅ Tests de errores: {passed} pasaron, {failed} fallaron.")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Simulador v3 — Universo Axolotto")
    parser.add_argument("--players",      type=int,   default=4,  help="Jugadores simulados (exc. Pro)")
    parser.add_argument("--incubation",   type=int,   default=45, help="Segundos de incubación real")
    parser.add_argument("--games",        type=int,   default=5,  help="Partidas manuales por axolotito")
    parser.add_argument("--multi-wait",   type=int,   default=35, help="Segundos de espera de lobby por ronda multijugador")
    parser.add_argument("--skip-reset",   action="store_true",    help="No resetear BD al inicio")
    parser.add_argument("--max-boosters", type=int,   default=None, help="Boosters por jugador (sobreescribe personalidad)")
    parser.add_argument("--max-boards",   type=int,   default=None, help="Tableros por jugador (sobreescribe personalidad)")
    parser.add_argument("--max-webitos",  type=int,   default=None, help="Webitos por jugador (sobreescribe personalidad)")
    parser.add_argument("--db-url",       type=str,   default=None, help="Database URL directa (ej: postgresql://user:pass@127.0.0.1:5433/db)")
    parser.add_argument("--include-user", type=str,   default=None, help="privy_did de un usuario real para incluirlo como bot extra (su data se resetea)")
    args = parser.parse_args()

    print("\n" + "=" * 70)
    print("🚀  SIMULADOR DE UNIVERSO AXOLOTTO v3")
    print("=" * 70)
    print(f"👥 Jugadores: {args.players}  |  ⏱️  Incubación: {args.incubation}s  "
          f"|  🎮 Partidas: {args.games}  |  ⚔️  Multi-wait: {args.multi_wait}s")
    print("=" * 70)

    sim_start = datetime.utcnow()

    import warnings, logging
    warnings.filterwarnings("ignore")
    logging.getLogger("sqlalchemy.engine").setLevel(logging.ERROR)
    engine.echo = False

    log_file = open("simulation.log", "w", encoding="utf-8")
    original_stdout = sys.stdout
    sys.stdout = log_file

    def progress(msg: str) -> None:
        """Escribe una línea normal al terminal (va al stdout real, no al log)."""
        original_stdout.write(msg + "\n")
        original_stdout.flush()

    def live_progress(msg: str) -> None:
        """Sobreescribe la línea actual en terminal con \\r (para contadores en vivo)."""
        # Padding a 90 chars para borrar residuos de líneas anteriores más largas
        original_stdout.write(f"\r{msg:<90}")
        original_stdout.flush()

    # ── Mock Web3Service for sim: skip real blockchain calls ─────────────────
    # Sim wallets are fake addresses without ETH. Patch all on-chain calls to
    # return mock hashes so phases don't fail on gas/funds errors.
    from app.services import web3_service as _w3mod
    _MOCK_TX = "0x_sim_mock_tx"
    _w3mod.Web3Service.mint_webito_onchain    = staticmethod(lambda wallet:        _MOCK_TX)
    _w3mod.Web3Service.mint_sobrecito_onchain   = staticmethod(lambda *a, **kw:      _MOCK_TX)
    _w3mod.Web3Service.burn_axofichas          = staticmethod(lambda *a, **kw:      _MOCK_TX)
    _w3mod.Web3Service.burn_frj               = staticmethod(lambda *a, **kw:      _MOCK_TX)
    _w3mod.Web3Service.mint_frj               = staticmethod(lambda *a, **kw:      _MOCK_TX)
    _w3mod.Web3Service.mint_cards_onchain     = staticmethod(lambda *a, **kw:      _MOCK_TX)
    _w3mod.Web3Service.create_board_onchain   = staticmethod(lambda *a, **kw:      _MOCK_TX)
    _w3mod.Web3Service.dissolve_board_onchain = staticmethod(lambda *a, **kw:      _MOCK_TX)
    _w3mod.Web3Service.dissolve_board_safe_onchain = staticmethod(lambda *a, **kw:      _MOCK_TX)
    _w3mod.Web3Service.transfer_board_onchain = staticmethod(lambda *a, **kw:      _MOCK_TX)
    _w3mod.Web3Service.create_npc_board       = staticmethod(lambda *a, **kw:      _rng.randint(1000, 9999))

    stats: dict = {}
    errors: list = []

    session = Session(engine)
    try:
        phase_migrations(progress)
        progress("⏳ [1/10] Reset...")
        if not args.skip_reset:
            phase_reset(session, progress)

        progress("⏳ [2/10] Usuarios...")
        players = phase_create_users(session, args.players, stats, progress)

        # Apply --max-* overrides to each player's personality
        if args.max_boosters is not None or args.max_boards is not None or args.max_webitos is not None:
            for p in players:
                pers = p["personality"]
                if args.max_boosters is not None:
                    # Override: set exactly N boosters (ignore personality default)
                    pers["boosters_normal"] = args.max_boosters
                    pers["boosters_foil"]   = 0
                if args.max_boards is not None:
                    pers["boards_random"] = args.max_boards
                if args.max_webitos is not None:
                    pers["eggs"] = args.max_webitos

        # ── Add real user as extra bot player ─────────────────────────────────
        if args.include_user:
            real_user = session.exec(
                select(User).where(User.privy_did == args.include_user)
            ).first()
            if real_user:
                # Assign personality (cycle through pool)
                real_personality = _rng.choice(PERSONALITY_POOL).copy()
                if args.max_boosters is not None:
                    real_personality["boosters_normal"] = args.max_boosters
                    real_personality["boosters_foil"]   = 0
                if args.max_boards is not None:
                    real_personality["boards_random"] = args.max_boards
                if args.max_webitos is not None:
                    real_personality["eggs"] = args.max_webitos
                players.append({
                    "user_id":      real_user.privy_did,
                    "wallet_addr":  real_user.wallet_address or f"0x{'cafe' + '0' * 36}",
                    "personality":  real_personality,
                })
                progress(f"  👤 Usuario real incluido como bot: {args.include_user}")
            else:
                progress(f"  ⚠️  Usuario {args.include_user} no encontrado en DB. Saltando.")

        progress("⏳ [3/10] Fondos + paquetes GAL...")
        phase_fund_wallets(session, players, stats, errors, progress)

        progress("⏳ [3b/10] Cápsulas iniciales — sembrando saldo inicial...")
        phase_seed_tickets(session, players, stats, errors, progress)

        progress("⏳ [4/10] Boosters — compra (sellados)...")
        phase_buy_boosters(session, players, stats, errors, progress)

        # Apertura INMEDIATA: solo los jugadores con estrategia "immediate"
        progress("⏳ [4b/10] Boosters — apertura inmediata (whale)...")
        phase_open_boosters(session, players, stats, errors, progress,
                            label="inmediato", filter_strategy={"immediate"})

        progress(f"⏳ [5/10] Incubación real ({args.incubation}s) — barra en vivo...")
        phase_incubation(session, players, args.incubation, stats, errors, progress,
                         live_progress=live_progress)

        # Apertura POST-INCUBACIÓN: selective (foils ya comprados) + random
        progress("⏳ [5b/10] Boosters — apertura post-incubación (selective + random)...")
        phase_open_boosters(session, players, stats, errors, progress,
                            label="post-incubacion", filter_strategy={"selective", "random"})

        progress("⏳ [6/10] Gashapon + cápsulas...")
        phase_gashapon(session, players, stats, errors, progress)

        # Apertura FINAL antes de crear tableros: hoarders abren sus sobres
        # (necesitan cartas para armar tableros manuales)
        progress("⏳ [6b/10] Boosters — apertura final (hoarder + restantes)...")
        phase_open_boosters(session, players, stats, errors, progress,
                            label="final", filter_strategy={"hoarder"})

        progress("⏳ [7/10] Tableros...")
        boards_by_user = phase_boards(session, players, stats, errors, progress)

        progress("⏳ [7b/10] Cenote Místico (Card Melter: Melt & Forge)...")
        phase_card_melter(session, players, stats, errors, progress)

        progress("⏳ [7c/10] Desarme Seguro (Solvente de Pegamento)...")
        phase_board_deconstruction(session, players, boards_by_user, stats, errors, progress)

        progress("⏳ [7d/10] Mercado Secundario P2P...")
        phase_p2p_market(session, players, stats, errors, progress)

        progress("⏳ [8/10] VIP Club...")
        phase_vip(session, players, stats, errors, progress)

        progress(f"⏳ [9/10] Partidas individuales ({args.games} × jugador)...")
        for p in players:
            p["personality"] = {**p["personality"], "solo_games": args.games}
        phase_individual_play(session, players, boards_by_user, stats, errors, progress)

        progress("⏳ [9b/10] Multijugador + Recall...")
        phase_multiplayer(session, players, boards_by_user, stats, errors, progress,
                          wait_secs=args.multi_wait)

        progress("⏳ [10/10] Tests de errores...")
        phase_error_tests(session, players, boards_by_user, stats, errors, progress)

    finally:
        session.close()
        sys.stdout = original_stdout
        log_file.close()

    # ── Reporte ──────────────────────────────────────────────────────────────
    sim_end = datetime.utcnow()
    elapsed_s = round((sim_end - sim_start).total_seconds())
    elapsed_h = elapsed_s // 3600
    elapsed_m = (elapsed_s % 3600) // 60
    elapsed_ss = elapsed_s % 60
    elapsed_fmt = (f"{elapsed_h}h {elapsed_m}m {elapsed_ss}s" if elapsed_h
                   else f"{elapsed_m}m {elapsed_ss}s" if elapsed_m
                   else f"{elapsed_ss}s")
    finished_str = sim_end.strftime("%Y-%m-%d %H:%M:%S UTC")

    gp = stats.get("games_played", 0)
    win_rate = (stats.get("wins", 0) / gp * 100) if gp > 0 else 0.0

    report = f"""
{'='*70}
📊  REPORTE FINAL — SIMULADOR AXOLOTTO v3
🕐  Terminó: {finished_str}  |  ⏱️  Duración: {elapsed_fmt}  ({elapsed_s}s)
{'='*70}
👥  Usuarios creados:          {stats.get('users_created', 0)}
💸  AXG comprados (Sim.):      {stats.get('axg_purchased_qty', 0.0):.0f} AXG (Pesos: ${stats.get('axg_purchased_mxn', 0.0):.2f} MXN)
💎  Paquetes GAL comprados:    {stats.get('gal_packs_bought', 0)}
🃏  Boosters normales:         {stats.get('boosters_bought', 0)}
✨  Boosters foil:             {stats.get('boosters_foil_bought', 0)}
🎯  Boosters extra (abiertos): {stats.get('boosters_extra_bought', 0)}
🎴  Cartas abiertas total:     {stats.get('cards_opened', 0)}
🥚  Webitos adoptados:         {stats.get('eggs_bought', 0)}
🐣  Axolotitos eclosionados:   {stats.get('eggs_hatched', 0)}
{'-'*70}
🎰  Gashapon rolls:            {stats.get('gashapon_rolls', 0)}
💊  Cápsulas reclamadas:       {stats.get('capsule_claims', 0)}
🌟  Triple Suerte:             {stats.get('triple_suerte', 0)}
📋  Tableros creados:          {stats.get('boards_created', 0)}  ({stats.get('manual_boards', 0)} manuales)
{'-'*70}
👑  VIP activados:             {stats.get('vip_activations', 0)}
🌿  GAL VIP reclamados:        {stats.get('vip_gal_claimed', 0)}
{'-'*70}
🎮  Partidas individuales:     {gp}
  🏆 Victorias:               {stats.get('wins', 0)}  ({win_rate:.1f}%)
  💔 Derrotas:                {stats.get('losses', 0)}
  🤖 Autojuego:               {stats.get('autogames', 0)} partidas
  💰 GAL obtenidas:           {stats.get('total_prize_gal', 0.0):.2f}
{'-'*70}
⚔️  Salas multijugador:        {stats.get('multi_rooms_simulated', 0)}
  📞 Recall pasó:             {stats.get('recall_tests_passed', 0)}
  💵 Axos liquidados:         {stats.get('multi_axos_settled', 0)}
  💰 Jackpots ganados:        {stats.get('multi_jackpot_won', 0)}
{'-'*70}"""

    # Detalle de resultados multijugador por partida
    match_logs = stats.get("multi_match_logs", [])
    if match_logs:
        multi_victories = sum(1 for l in match_logs if l["outcome"] == "Victoria")
        multi_net = sum(l["net_gal"] for l in match_logs)
        report += f"""
  📊 Partidas jugadas:         {len(match_logs)}
  🏆 Victorias:               {multi_victories}  ({multi_victories/len(match_logs)*100:.0f}%)
  💸 GAL neto total:          {multi_net:+.1f}
  Detalle:
"""
        for log in match_logs:
            icon = "🏆" if log["outcome"] == "Victoria" else "💔"
            axo_name = log["axo_name"][:20]
            room_name = log["room_name"][:24]
            report += (f"    {icon} {axo_name:<20} │ {room_name:<24} │ "
                       f"Neto: {log['net_gal']:+7.1f} GAL │ XP: +{log['xp_gained']}\n")

    report += f"""
{'-'*70}
🚫  Tests de errores:
  ✅ Pasaron:                 {stats.get('error_tests_passed', 0)}
  ❌ Fallaron:                {stats.get('error_tests_failed', 0)}
{'='*70}
"""

    if errors:
        report += f"\n⚠️  ERRORES ({len(errors)}):\n"
        from collections import Counter
        for err, cnt in Counter(errors).most_common():
            report += f"  x{cnt}  {err}\n"
    else:
        report += "✅  Sin errores durante la simulación.\n"

    report += "=" * 70 + "\n"

    progress(report)

    try:
        with open("simulation_report.txt", "w", encoding="utf-8") as f:
            f.write(report)
        print("💾 Reporte guardado en simulation_report.txt")
    except Exception as e:
        print(f"⚠️  No se pudo guardar el reporte: {e}")

    print("🎉 ¡Simulación v2 completada!")


if __name__ == "__main__":
    main()
