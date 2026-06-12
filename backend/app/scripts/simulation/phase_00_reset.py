from sqlmodel import Session, select, func
from sqlalchemy import delete, text as sa_text
from sqlmodel import SQLModel

from app.models.economy import TransactionLedger, AxgPurchaseRecord
from app.models.items import ItemCatalog, ItemType, PlayerInventory, WebitoIncubation
from app.models.board import PlayerBoard
from app.models.axolotito import Axolotito
from app.models.lobby_models import GameRoom, RoomRegistration, JackpotVault, TreasuryVault, MultiplayerGameLog, JackpotWin
from app.models.economy import Wallet
from app.models.promo import PromoCode, PendingReward
from app.models.social import FriendRelation, SocialActionLog, ReferralCode, ReferralTracking
from app.models.user import User
from app.core.config import settings
from sim_types import PRO_USER_DID, ADMIN_REFERRAL_CODE


def phase_reset(engine, config, **state) -> dict:
    """
    Limpia TODOS los datos de juego — como si fuera un deploy fresh.
    Se borran datos de TODOS los usuarios (incluyendo admin/Pro). Los registros
    de User se conservan pero se resetean sus campos de estado (VIP, slots, etc.).
    """
    session: Session = state["session"]
    progress = state["progress"]

    progress("  ♻️  Reseteando estado completo (deploy-clean — todos los usuarios)...")

    is_postgres = "postgresql" in str(engine.url)

    if is_postgres:
        # TRUNCATE CASCADE maneja todas las FKs automáticamente, sin importar orden
        game_tables = [
            "jackpotwin", "roomregistration", "multiplayergamelog", "gameroom",
            "webitoincubation", "axolotito", "playerboard",
            "transactionledger", "playerinventory", "wallet",
            "jackpotvault", "treasuryvault",
            "axf_purchase_record",
            "pending_rewards", "promocode",
            "inventorymarketlisting", "processedtransaction",
            "capsuladailyfree", "capsulapity",
            "cryptopaymentattempt", "cryptopurchaseorder",
            "chainoutbox", "playerboardslot", "activegamestate",
            "manualmodeevent",
            # Social tables — se limpian en cada simulación
            "friend_relations", "social_action_logs",
            "referral_codes", "referral_tracking",
        ]
        try:
            # Verificar qué tablas existen realmente (evita que una tabla missing rompa todo el TRUNCATE)
            existing_tables = [
                r[0] for r in session.execute(
                    sa_text("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname = 'public'")
                ).fetchall()
            ]
            tables_to_truncate = [t for t in game_tables if t in existing_tables]
            missing = [t for t in game_tables if t not in existing_tables]
            if missing:
                progress(f"  ⚠️  Tablas no encontradas (skip): {', '.join(missing)}")
            if tables_to_truncate:
                tables_sql = ", ".join(f'"{t}"' for t in tables_to_truncate)
                session.execute(sa_text(f"TRUNCATE TABLE {tables_sql} RESTART IDENTITY CASCADE"))
                session.commit()
                progress(f"  🗑️  TRUNCATE CASCADE: {len(tables_to_truncate)}/{len(game_tables)} tablas vaciadas.")
            else:
                progress("  ⚠️  Ninguna tabla para truncar.")
        except Exception as e:
            session.rollback()
            progress(f"  ⚠️  TRUNCATE falló: {e}")
    else:
        # SQLite: DELETE en orden correcto (no soporta TRUNCATE CASCADE)
        try:
            session.execute(sa_text("UPDATE axolotito SET assigned_board_id = NULL"))
            session.commit()
        except Exception:
            session.rollback()

        for model in [
            JackpotWin, RoomRegistration, MultiplayerGameLog, GameRoom,
            WebitoIncubation, PlayerBoard, Axolotito,
            TransactionLedger, PlayerInventory, Wallet,
            JackpotVault, TreasuryVault, AxgPurchaseRecord,
            PendingReward,
            FriendRelation, SocialActionLog, ReferralCode, ReferralTracking,
        ]:
            try:
                session.execute(delete(model))
                session.commit()
            except Exception as e:
                session.rollback()
                progress(f"  ⚠️  No se pudo borrar {model.__name__}: {e}")

    # 3. Resetear campos de estado del User para TODOS los usuarios
    #    (VIP, slots, puntos, etc. — vuelven a valores de deploy)
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
                cave_level              = 1,
                cave_name               = NULL,
                cave_decorations         = '{}',
                cave_expansion_target_level = NULL,
                cave_expansion_started_at   = NULL,
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
                f2p_daily_claim_streak   = 0,
                lunar_streak_day         = 0,
                lunar_week               = 1,
                lunar_last_claim_at      = NULL,
                lunar_cycles_completed   = 0,
                webito_slots_unlocked    = 1
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

    # 4b. Resetear estadísticas de cartas cantadas (times_called) a 0
    try:
        from sqlalchemy import update
        session.execute(
            update(ItemCatalog).values(times_called=0)
        )
        session.commit()
    except Exception as e:
        session.rollback()
        progress(f"  ⚠️  No se pudo resetear times_called: {e}")

    # 5. Re-crear el código de referido hardcodeado del admin
    #    (debe sobrevivir resets — es el link público que se comparte externamente)
    _ensure_admin_referral_code(session, progress)

    progress("  ✅ Reset completo — BD virgen (wallets, axolotitos, tableros, VIP, jackpot, social).")

    # Limpiar PromoCodes de simulación previos (se recrean en phase_01b)
    _ensure_sim_promocode(session)
    return {}


def _ensure_admin_referral_code(session: Session, progress) -> None:
    """Re-crea el código de referido hardcodeado del admin después del reset.

    El admin (PRO_USER_DID) siempre debe tener el mismo código de referido
    para que su link público no cambie entre simulaciones/resets.
    """
    from datetime import datetime
    try:
        # Verificar si el admin ya existe en la BD
        admin_exists = session.exec(
            select(User).where(User.privy_did == PRO_USER_DID)
        ).first()
        if not admin_exists:
            progress("  ⚠️  Admin no encontrado en BD — el código se creará en phase_01_users.")
            return

        # Insertar el código hardcodeado del admin
        existing = session.exec(
            select(ReferralCode).where(ReferralCode.user_id == PRO_USER_DID)
        ).first()
        if existing:
            # Ya existe (posible si no se truncó), actualizar al código hardcodeado
            existing.code = ADMIN_REFERRAL_CODE
            existing.updated_at = datetime.utcnow()
            session.add(existing)
        else:
            rc = ReferralCode(
                user_id=PRO_USER_DID,
                code=ADMIN_REFERRAL_CODE,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            session.add(rc)
        session.commit()
        progress(f"  🔗 Código de referido del admin asegurado: {ADMIN_REFERRAL_CODE}")
    except Exception as e:
        session.rollback()
        progress(f"  ⚠️  No se pudo crear código de referido del admin: {e}")


def _ensure_sim_promocode(session: Session) -> str:
    """No-op: TRUNCATE CASCADE en phase_reset ya limpia promocode y pending_rewards."""
    return "cleaned"


def phase_migrations(engine, config, **state) -> dict:
    """Asegura que las columnas opcionales existen en la BD."""
    progress = state["progress"]

    progress("  🔧 Aplicando migraciones mínimas...")
    SQLModel.metadata.create_all(engine)

    # ── Enums de PostgreSQL ──────────────────────────────────────────────
    is_postgres = "postgresql" in str(engine.url)
    if is_postgres:
        try:
            import psycopg2
            db_url = str(engine.url)
            conn_raw = psycopg2.connect(db_url)
            conn_raw.autocommit = True
            cursor = conn_raw.cursor()
            for enum_val in ("BURN", "VIP_GAL_EXPIRED", "CRAFTING", "TUTORIAL_BONUS", "F2P_REWARD", "WEBITO_UNLOCK"):
                try:
                    cursor.execute(f"ALTER TYPE transactiontype ADD VALUE IF NOT EXISTS '{enum_val}'")
                except Exception:
                    pass
            cursor.close()
            conn_raw.close()
            print("  ✅ Migracion de enums en PostgreSQL ejecutada con exito")
        except Exception as e:
            print(f"  ⚠️  Error al migrar enums via psycopg2: {e}")

    # ── Columnas opcionales (PostgreSQL + SQLite) ───────────────────────
    is_sqlite = "sqlite" in str(engine.url)

    with engine.connect() as conn:
        def _get_cols(table: str) -> set:
            if is_sqlite:
                return {r[1] for r in conn.execute(sa_text(f"PRAGMA table_info({table})")).fetchall()}
            return {r[0] for r in conn.execute(
                sa_text(f"SELECT column_name FROM information_schema.columns WHERE table_name='{table}'")
            ).fetchall()}

        # ── Rename wallet columns (schema drift: axogemas→axofichas, gemas_alga→frijolitos) ─
        wallet_cols = _get_cols("wallet")
        if "axogemas" in wallet_cols and "axofichas" not in wallet_cols:
            try:
                conn.execute(sa_text("ALTER TABLE wallet RENAME COLUMN axogemas TO axofichas"))
                print("  ✅ wallet.axofichas → axofichas")
            except Exception as e:
                print(f"  ⚠️  No se pudo renombrar axogemas: {e}")
        if "gemas_alga" in wallet_cols and "frijolitos" not in wallet_cols:
            try:
                conn.execute(sa_text("ALTER TABLE wallet RENAME COLUMN gemas_alga TO frijolitos"))
                print("  ✅ wallet.frijolitos → frijolitos")
            except Exception as e:
                print(f"  ⚠️  No se pudo renombrar gemas_alga: {e}")

        # ── Agregar columnas faltantes ───────────────────────────────────
        migrations = [
            # user
            ("user",              "promo_code_attempts",          "INTEGER DEFAULT 0"),
            ("user",              "tutorial_completed",           "BOOLEAN DEFAULT FALSE"),
            ("user",              "cave_level",                   "INTEGER DEFAULT 1"),
            ("user",              "cave_name",                    "VARCHAR(255) NULL"),
            ("user",              "cave_expansion_started_at",    "TIMESTAMP NULL"),
            ("user",              "cave_expansion_target_level",  "INTEGER NULL"),
            ("user",              "cave_decorations",             "JSON DEFAULT '{}'"),
            ("user",              "last_play_date",               "TIMESTAMP NULL"),
            ("user",              "daily_play_streak",            "INTEGER DEFAULT 0"),
            ("user",              "f2p_astral_fragments",         "INTEGER DEFAULT 0"),
            ("user",              "f2p_daily_gal_earned",         "DOUBLE PRECISION DEFAULT 0.0"),
            ("user",              "f2p_daily_gal_reset_at",       "TIMESTAMP NULL"),
            # transactionledger
            ("transactionledger", "item_id",                      "INTEGER NULL"),
            # multiplayergamelog
            ("multiplayergamelog","prize_breakdown_json",         "TEXT NULL"),
            ("multiplayergamelog","won_premio_1",                 "BOOLEAN DEFAULT FALSE"),
            ("multiplayergamelog","won_premio_2",                 "BOOLEAN DEFAULT FALSE"),
            ("multiplayergamelog","won_jackpot",                  "BOOLEAN DEFAULT FALSE"),
            ("multiplayergamelog","entry_fee_paid",               "DOUBLE PRECISION DEFAULT 0.0"),
            ("multiplayergamelog","gross_prize_gal",              "DOUBLE PRECISION DEFAULT 0.0"),
            ("multiplayergamelog","notified",                     "BOOLEAN DEFAULT FALSE"),
            # webitoincubation
            ("webitoincubation",  "base_stat_luck",               "FLOAT DEFAULT 50.0"),
            ("webitoincubation",  "base_stat_focus",              "FLOAT DEFAULT 50.0"),
            ("webitoincubation",  "base_stat_stamina",            "FLOAT DEFAULT 100.0"),
            ("webitoincubation",  "base_stat_salinity",           "FLOAT DEFAULT 50.0"),
            ("webitoincubation",  "bonus_salinity_adj",           "FLOAT DEFAULT 0.0"),
            ("webitoincubation",  "imprinting_complete",          "BOOLEAN DEFAULT FALSE"),
            ("webitoincubation",  "imprinting_padrino_id",        "INTEGER NULL"),
            ("webitoincubation",  "imprinting_games_played",      "INTEGER DEFAULT 0"),
            ("webitoincubation",  "tutorial_board_card_ids",      "JSON DEFAULT NULL"),
            # playerboard
            ("playerboard",       "is_dead",                      "BOOLEAN DEFAULT FALSE"),
            ("playerboard",       "blockchain_token_id",          "INTEGER NULL"),
            ("playerboard",       "card_first_editions",          "JSON DEFAULT '[]'"),
            ("playerboard",       "is_listed_for_sale",           "BOOLEAN DEFAULT FALSE"),
            ("playerboard",       "sale_price_gal",               "DOUBLE PRECISION DEFAULT 0.0"),
            ("playerboard",       "is_frozen_by_vip",             "BOOLEAN DEFAULT FALSE"),
            ("playerboard",       "is_npc_pool",                  "BOOLEAN DEFAULT FALSE"),
            ("playerboard",       "npc_room",                     "VARCHAR(50)"),
            ("playerboard",       "npc_retired",                  "BOOLEAN DEFAULT FALSE"),
            ("playerboard",       "origin_story",                 "TEXT"),
            ("playerboard",       "is_tutorial",                  "BOOLEAN DEFAULT FALSE"),
            ("playerboard",       "slot_index",                   "INTEGER NULL"),
            ("playerboard",       "slot_generation",              "INTEGER DEFAULT 1"),
            # playerinventory
            ("playerinventory",   "is_first_edition",             "BOOLEAN DEFAULT FALSE"),
            ("playerinventory",   "is_shiny",                     "BOOLEAN DEFAULT FALSE"),
            # axolotito
            ("axolotito",         "sleep_expires_at",             "TIMESTAMP NULL"),
            ("axolotito",         "is_main",                      "BOOLEAN DEFAULT FALSE"),
            ("axolotito",         "is_frozen_by_vip",             "BOOLEAN DEFAULT FALSE"),
            ("axolotito",         "escrow_balance_gal",           "DOUBLE PRECISION DEFAULT 0.0"),
            ("axolotito",         "wants_to_stop",                "BOOLEAN DEFAULT FALSE"),
            ("axolotito",         "loyalty_points",               "INTEGER DEFAULT 0"),
            ("axolotito",         "is_listed_for_sale",           "BOOLEAN DEFAULT FALSE"),
            ("axolotito",         "sale_price_gal",               "DOUBLE PRECISION DEFAULT 0.0"),
            ("axolotito",         "is_listed_for_rent",           "BOOLEAN DEFAULT FALSE"),
            ("axolotito",         "rent_fee_gal",                 "DOUBLE PRECISION DEFAULT 0.0"),
            ("axolotito",         "rent_share_owner_pct",         "INTEGER DEFAULT 0"),
            ("axolotito",         "rent_expires_at",              "TIMESTAMP NULL"),
            ("axolotito",         "cpu_win_streak",               "INTEGER DEFAULT 0"),
            ("axolotito",         "cave_items",                   "JSON DEFAULT '[]'"),
            ("axolotito",         "nature",                       "VARCHAR(255) NULL"),
            ("axolotito",         "is_tutorial",                  "BOOLEAN DEFAULT FALSE"),
            ("axolotito",         "is_rented",                    "BOOLEAN DEFAULT FALSE"),
            ("axolotito",         "renter_id",                    "VARCHAR(255) NULL"),
        ]
        for table, col, ddl in migrations:
            try:
                cols = _get_cols(table)
                if col not in cols:
                    conn.execute(sa_text(f"ALTER TABLE {table} ADD COLUMN {col} {ddl}"))
                    print(f"  ✅ Migración: {table}.{col}")
            except Exception as e:
                print(f"  ⚠️  No se pudo agregar {table}.{col}: {e}")
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
            progress("  📦 Sembrando boosters, huevos, VIP, paquetes FRJ...")
            try:
                from app.scripts.seed_catalog import run_seed
                run_seed()
            except Exception as e:
                progress(f"  ⚠️  seed_catalog falló: {e}")

    progress("  ✅ Migraciones aplicadas.")
    return {}
