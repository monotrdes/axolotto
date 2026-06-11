from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel
from app.database import engine
from app.core.limiter import limiter
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from app.api.v1.endpoints import bank, user, shop, incubation, metadata, legacy, board, game, ranking, multiplayer, checkout, market, market_escrow, payments, leonardo, admin, whitelist, codes, f2p, tutorial, cave_expansion, admin_events, events, dev, rewards, staking, social, referrals
from app.api.v1.ws import game_ws
from app.core.config import settings

app = FastAPI(title="Axolotto API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.on_event("startup")
async def on_startup():
    # Crea de forma segura cualquier tabla faltante (ej. legacybacker) sin alterar las existentes
    SQLModel.metadata.create_all(engine)
    
    # Migrar enum itemtype: agregar valores nuevos en modo autocommit
    from sqlalchemy import text
    with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
        conn.execute(text("ALTER TYPE itemtype ADD VALUE IF NOT EXISTS 'CURRENCY_PACK'"))
        conn.execute(text("ALTER TYPE itemtype ADD VALUE IF NOT EXISTS 'cave_item'"))

    # Agregar columnas de Hatchery 2.0 de manera dinámica si no existen en webitoincubation
    with engine.connect() as conn:
        result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'webitoincubation';"))
        existing_cols = {row[0] for row in result.fetchall()}
        
        cols_to_add = [
            ("last_petting", "TIMESTAMP"),
            ("last_singing", "TIMESTAMP"),
            ("last_feeding", "TIMESTAMP"),
            ("bonus_strength", "DOUBLE PRECISION DEFAULT 0.0"),
            ("bonus_agility", "DOUBLE PRECISION DEFAULT 0.0"),
            ("bonus_wisdom", "DOUBLE PRECISION DEFAULT 0.0"),
            ("bonus_focus", "DOUBLE PRECISION DEFAULT 0.0"),
            ("bonus_stamina", "DOUBLE PRECISION DEFAULT 0.0"),
            ("bonus_luck", "DOUBLE PRECISION DEFAULT 0.0"),
            ("genetic_purity", "DOUBLE PRECISION DEFAULT 100.0"),
        ]
        
        for col_name, col_type in cols_to_add:
            if col_name not in existing_cols:
                conn.execute(text(f"ALTER TABLE webitoincubation ADD COLUMN {col_name} {col_type};"))

        # Re-fetch column list (may have changed after cols_to_add loop above)
        result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'webitoincubation';"))
        existing_cols = {row[0] for row in result.fetchall()}

        # --- Imprinting 1.0 ---
        imprinting_cols = [
            ("imprinting_games_played", "INTEGER DEFAULT 0"),
            ("imprinting_padrino_id",   "INTEGER"),
            ("base_stat_luck",          "DOUBLE PRECISION DEFAULT 0.0"),
            ("base_stat_focus",         "DOUBLE PRECISION DEFAULT 0.0"),
            ("base_stat_stamina",       "DOUBLE PRECISION DEFAULT 0.0"),
            ("base_stat_salinity",      "DOUBLE PRECISION DEFAULT 0.0"),
            ("bonus_salinity_adj",      "DOUBLE PRECISION DEFAULT 0.0"),
            ("imprinting_complete",     "BOOLEAN DEFAULT FALSE"),
        ]
        for col_name, col_type in imprinting_cols:
            if col_name not in existing_cols:
                conn.execute(text(
                    f"ALTER TABLE webitoincubation ADD COLUMN {col_name} {col_type};"
                ))
        conn.commit()

        # Add FK constraint for imprinting_padrino_id if not already present
        fk_check = conn.execute(text("""
            SELECT conname FROM pg_constraint
            WHERE conrelid = 'webitoincubation'::regclass
              AND conname = 'webitoincubation_imprinting_padrino_id_fkey'
        """)).first()
        if not fk_check:
            try:
                conn.execute(text("""
                    ALTER TABLE webitoincubation
                    ADD CONSTRAINT webitoincubation_imprinting_padrino_id_fkey
                    FOREIGN KEY (imprinting_padrino_id)
                    REFERENCES axolotito(id)
                    ON DELETE SET NULL
                """))
                conn.commit()
            except Exception as e:
                print(f"⚠️ Could not add FK for imprinting_padrino_id: {e}")
                conn.rollback()

        # --- MIGRACIÓN DE CONSTRAINTS PARA HATCHERY 3.0 ---
        # 1. Dropear el foreign key viejo que apunta a itemcatalog si existe
        result_fk = conn.execute(text("""
            SELECT conname 
            FROM pg_constraint 
            WHERE conrelid = 'axolotito'::regclass 
              AND confrelid = 'itemcatalog'::regclass;
        """))
        for row in result_fk.fetchall():
            conn.execute(text(f"ALTER TABLE axolotito DROP CONSTRAINT {row[0]};"))
            
        # 2. Limpiar assigned_board_id que no existan en playerboard
        #    (Son IDs del catálogo antiguo que ya no son válidos)
        conn.execute(text("""
            UPDATE axolotito
            SET assigned_board_id = NULL
            WHERE assigned_board_id IS NOT NULL
              AND assigned_board_id NOT IN (SELECT id FROM playerboard);
        """))

        # 3. Agregar el nuevo foreign key apuntando a playerboard (si no existe ya)
        result_fk_new = conn.execute(text("""
            SELECT conname 
            FROM pg_constraint 
            WHERE conrelid = 'axolotito'::regclass 
              AND confrelid = 'playerboard'::regclass;
        """))
        if not result_fk_new.fetchall():
            conn.execute(text("""
                ALTER TABLE axolotito 
                ADD CONSTRAINT axolotito_assigned_board_id_playerboard_fkey 
                FOREIGN KEY (assigned_board_id) 
                REFERENCES playerboard(id) 
                ON DELETE SET NULL;
            """))
            
        # --- MIGRACIÓN DE USER SLOTS ---
        result_user = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'user';"))
        existing_user_cols = {row[0] for row in result_user.fetchall()}
        if "unlocked_board_slots" not in existing_user_cols:
            conn.execute(text("ALTER TABLE \"user\" ADD COLUMN unlocked_board_slots INTEGER DEFAULT 3;"))
            
        # --- MIGRACIÓN DE TABLA PLAYERBOARD (IS_DEAD / BLOCKCHAIN_TOKEN_ID / SALE) ---
        result_board = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'playerboard';"))
        existing_board_cols = {row[0] for row in result_board.fetchall()}
        if "is_dead" not in existing_board_cols:
            conn.execute(text("ALTER TABLE playerboard ADD COLUMN is_dead BOOLEAN DEFAULT FALSE;"))
        if "blockchain_token_id" not in existing_board_cols:
            conn.execute(text("ALTER TABLE playerboard ADD COLUMN blockchain_token_id INTEGER NULL UNIQUE;"))
        if "card_first_editions" not in existing_board_cols:
            conn.execute(text("ALTER TABLE playerboard ADD COLUMN card_first_editions JSON DEFAULT '[]';"))
        if "is_listed_for_sale" not in existing_board_cols:
            conn.execute(text("ALTER TABLE playerboard ADD COLUMN is_listed_for_sale BOOLEAN DEFAULT FALSE;"))
        if "sale_price_gal" not in existing_board_cols:
            conn.execute(text("ALTER TABLE playerboard ADD COLUMN sale_price_gal DOUBLE PRECISION DEFAULT 0.0;"))

        # --- MIGRACIÓN DE TABLA PLAYERINVENTORY (IS_FIRST_EDITION) ---
        result_inv = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'playerinventory';"))
        existing_inv_cols = {row[0] for row in result_inv.fetchall()}
        if "is_first_edition" not in existing_inv_cols:
            conn.execute(text("ALTER TABLE playerinventory ADD COLUMN is_first_edition BOOLEAN DEFAULT FALSE;"))
        if "is_shiny" not in existing_inv_cols:
            conn.execute(text("ALTER TABLE playerinventory ADD COLUMN is_shiny BOOLEAN DEFAULT FALSE;"))
            
        # --- MIGRACIÓN DE TABLA ITEMCATALOG (max_per_user anti-ballena) ---
        result_catalog = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'itemcatalog';"))
        existing_catalog_cols = {row[0] for row in result_catalog.fetchall()}
        if "max_per_user" not in existing_catalog_cols:
            conn.execute(text("ALTER TABLE itemcatalog ADD COLUMN max_per_user INTEGER NULL;"))

        # --- MIGRACIÓN DE TABLA TRANSACTIONLEDGER (item_id) ---
        result_ledger = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'transactionledger';"))
        existing_ledger_cols = {row[0] for row in result_ledger.fetchall()}
        if "item_id" not in existing_ledger_cols:
            conn.execute(text("ALTER TABLE transactionledger ADD COLUMN item_id INTEGER NULL;"))
            try:
                items = conn.execute(text("SELECT id, name FROM itemcatalog;")).fetchall()
                for item_id, name in items:
                    conn.execute(
                        text("UPDATE transactionledger SET item_id = :item_id WHERE item_id IS NULL AND description LIKE :pattern;"),
                        {"item_id": item_id, "pattern": f"%{name}%"}
                    )
            except Exception as e:
                print(f"⚠️ Error during dynamic backfill: {e}")

        # --- MIGRACIÓN DE TABLA AXOLOTITO (SLEEP_EXPIRES_AT / ESCROW / LOYALTY / MARKET / ACCESSORIES) ---
        result_axo = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'axolotito';"))
        existing_axo_cols = {row[0] for row in result_axo.fetchall()}
        if "sleep_expires_at" not in existing_axo_cols:
            conn.execute(text("ALTER TABLE axolotito ADD COLUMN sleep_expires_at TIMESTAMP NULL;"))
        if "last_staking_claim" not in existing_axo_cols:
            conn.execute(text("ALTER TABLE axolotito ADD COLUMN last_staking_claim TIMESTAMP NULL;"))
        if "accrued_unclaimed" not in existing_axo_cols:
            conn.execute(text("ALTER TABLE axolotito ADD COLUMN accrued_unclaimed DOUBLE PRECISION DEFAULT 0.0;"))
        if "escrow_balance_gal" not in existing_axo_cols:
            conn.execute(text("ALTER TABLE axolotito ADD COLUMN escrow_balance_gal DOUBLE PRECISION DEFAULT 0.0;"))
        if "loyalty_points" not in existing_axo_cols:
            conn.execute(text("ALTER TABLE axolotito ADD COLUMN loyalty_points INTEGER DEFAULT 0;"))
        if "wants_to_stop" not in existing_axo_cols:
            conn.execute(text("ALTER TABLE axolotito ADD COLUMN wants_to_stop BOOLEAN DEFAULT FALSE;"))
            
        # Market fields
        if "is_listed_for_sale" not in existing_axo_cols:
            conn.execute(text("ALTER TABLE axolotito ADD COLUMN is_listed_for_sale BOOLEAN DEFAULT FALSE;"))
        if "sale_price_gal" not in existing_axo_cols:
            conn.execute(text("ALTER TABLE axolotito ADD COLUMN sale_price_gal DOUBLE PRECISION DEFAULT 0.0;"))
        if "is_listed_for_rent" not in existing_axo_cols:
            conn.execute(text("ALTER TABLE axolotito ADD COLUMN is_listed_for_rent BOOLEAN DEFAULT FALSE;"))
        if "rent_fee_gal" not in existing_axo_cols:
            conn.execute(text("ALTER TABLE axolotito ADD COLUMN rent_fee_gal DOUBLE PRECISION DEFAULT 0.0;"))
        if "rent_share_owner_pct" not in existing_axo_cols:
            conn.execute(text("ALTER TABLE axolotito ADD COLUMN rent_share_owner_pct INTEGER DEFAULT 0;"))
        if "is_rented" not in existing_axo_cols:
            conn.execute(text("ALTER TABLE axolotito ADD COLUMN is_rented BOOLEAN DEFAULT FALSE;"))
        if "renter_id" not in existing_axo_cols:
            conn.execute(text("ALTER TABLE axolotito ADD COLUMN renter_id VARCHAR(255) NULL;"))
        if "rent_expires_at" not in existing_axo_cols:
            conn.execute(text("ALTER TABLE axolotito ADD COLUMN rent_expires_at TIMESTAMP NULL;"))
            
        # Accessories fields
        if "equipped_head_item_id" not in existing_axo_cols:
            conn.execute(text("ALTER TABLE axolotito ADD COLUMN equipped_head_item_id INTEGER NULL;"))
        if "equipped_eyes_item_id" not in existing_axo_cols:
            conn.execute(text("ALTER TABLE axolotito ADD COLUMN equipped_eyes_item_id INTEGER NULL;"))
        if "equipped_body_item_id" not in existing_axo_cols:
            conn.execute(text("ALTER TABLE axolotito ADD COLUMN equipped_body_item_id INTEGER NULL;"))
        if "is_main" not in existing_axo_cols:
            conn.execute(text("ALTER TABLE axolotito ADD COLUMN is_main BOOLEAN DEFAULT FALSE;"))

        # Cave equipment system
        if "cave_items" not in existing_axo_cols:
            conn.execute(text("ALTER TABLE axolotito ADD COLUMN cave_items JSON DEFAULT '[]';"))
            
        if "nature" not in existing_axo_cols:
            conn.execute(text("ALTER TABLE axolotito ADD COLUMN nature VARCHAR(255) NULL;"))

        if "mentorship_count" not in existing_axo_cols:
            conn.execute(text("ALTER TABLE axolotito ADD COLUMN mentorship_count INTEGER DEFAULT 0;"))
        if "tutored_by_id" not in existing_axo_cols:
            conn.execute(text("ALTER TABLE axolotito ADD COLUMN tutored_by_id INTEGER NULL;"))

        # --- MIGRACIÓN TUTORIAL / F2P / WEBITO SLOTS ---
        result_user3 = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'user';"))
        existing_user3 = {row[0] for row in result_user3.fetchall()}
        tutorial_user_cols = [
            ("tutorial_completed",    "BOOLEAN NOT NULL DEFAULT FALSE"),
            ("webito_slots_unlocked", "INTEGER NOT NULL DEFAULT 1"),
            ("last_play_date",        "TIMESTAMP NULL"),
            ("daily_play_streak",     "INTEGER NOT NULL DEFAULT 0"),
            ("f2p_astral_fragments",  "INTEGER NOT NULL DEFAULT 0"),
            ("f2p_daily_gal_earned",  "DOUBLE PRECISION NOT NULL DEFAULT 0.0"),
            ("f2p_daily_gal_reset_at","TIMESTAMP NULL"),
        ]
        for col_name, col_type in tutorial_user_cols:
            if col_name not in existing_user3:
                conn.execute(text(f'ALTER TABLE "user" ADD COLUMN {col_name} {col_type};'))

        # --- MIGRACIÓN CENOTE EXPANSIÓN (cave_level reemplaza webito_slots_unlocked) ---
        cave_user_cols = [
            ("cave_level",                      "INTEGER NOT NULL DEFAULT 1"),
            ("cave_name",                       "VARCHAR(255) NULL"),
            ("cave_decorations",                "JSON DEFAULT '{}'"),
            ("cave_expansion_started_at",        "TIMESTAMP NULL"),
            ("cave_expansion_target_level",      "INTEGER NULL"),
        ]
        for col_name, col_type in cave_user_cols:
            if col_name not in existing_user3:
                conn.execute(text(f'ALTER TABLE "user" ADD COLUMN {col_name} {col_type};'))

        # Migrar dato existente: webito_slots_unlocked → cave_level
        # Solo si cave_level sigue en 1 (default) y webito_slots_unlocked > 1
        conn.execute(text("""
            UPDATE "user"
            SET cave_level = webito_slots_unlocked
            WHERE cave_level = 1 AND webito_slots_unlocked > 1
        """))

        # --- MIGRACIÓN GAMEROOM (hosting) ---
        result_gr = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'gameroom';"))
        existing_gr = {row[0] for row in result_gr.fetchall()}
        gameroom_cols = [
            ("host_id",                 "VARCHAR(255) NULL"),
            ("room_config",             "JSON NULL"),
            ("visibility",              "VARCHAR(20) DEFAULT 'public'"),
            ("password_hash",           "VARCHAR(255) NULL"),
            ("host_reputation_earned",  "INTEGER DEFAULT 0"),
            ("countdown_started_at",    "TIMESTAMP NULL"),
            ("last_host_activity_at",   "TIMESTAMP NULL"),
        ]
        for col_name, col_type in gameroom_cols:
            if col_name not in existing_gr:
                conn.execute(text(f'ALTER TABLE gameroom ADD COLUMN {col_name} {col_type};'))

        result_incub = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'webitoincubation';"))
        existing_incub = {row[0] for row in result_incub.fetchall()}
        if "tutorial_phase" not in existing_incub:
            conn.execute(text("ALTER TABLE webitoincubation ADD COLUMN tutorial_phase INTEGER NOT NULL DEFAULT 0;"))
        if "tutorial_act_index" not in existing_incub:
            conn.execute(text("ALTER TABLE webitoincubation ADD COLUMN tutorial_act_index INTEGER NOT NULL DEFAULT 0;"))
        if "tutorial_karma" not in existing_incub:
            conn.execute(text("ALTER TABLE webitoincubation ADD COLUMN tutorial_karma VARCHAR(20) NULL;"))

        # Extend transactiontype enum with new tutorial values
        for val in ["tutorial_bonus", "webito_unlock"]:
            conn.execute(text(f"ALTER TYPE transactiontype ADD VALUE IF NOT EXISTS '{val}'"))

        conn.commit()

    # --- IMPORTAR Y CREAR TABLAS DE LOBBY / JACKPOT ---
    from app.models.lobby_models import TreasuryVault, JackpotVault, JackpotWin, GameRoom, RoomRegistration, MultiplayerGameLog
    # Importar modelos de checkout para que se registren en metadata antes del create_all
    from app.models.economy import CryptoPurchaseOrder, AxfPurchaseRecord  # noqa: F401
    from app.models.items import InventoryMarketListing  # noqa: F401
    from app.models.market_escrow import EscrowListing, FiatPaymentIntent, EarnedBalanceLock  # noqa: F401
    from app.models.promo import PromoCode, PendingReward  # noqa: F401
    from app.models.manual_mode_event import ManualModeEvent  # noqa: F401 — registra tabla
    from app.models.social import FriendRelation, SocialActionLog, ReferralCode, ReferralTracking  # noqa: F401 — registra tablas
    SQLModel.metadata.create_all(engine)

    # --- MIGRACIONES DINÁMICAS: CHECKOUT / USER ---
    with engine.connect() as conn:
        result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'user';"))
        existing_user_cols = {row[0] for row in result.fetchall()}
        if "first_crypto_purchase_at" not in existing_user_cols:
            conn.execute(text("ALTER TABLE \"user\" ADD COLUMN first_crypto_purchase_at TIMESTAMP NULL;"))
        conn.commit()

    # --- MIGRACIÓN DINÁMICA: PLAY_MODE EN ROOMREGISTRATION ---
    with engine.connect() as conn:
        result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'roomregistration';"))
        existing_reg_cols = {row[0] for row in result.fetchall()}
        if "play_mode" not in existing_reg_cols:
            conn.execute(text("ALTER TABLE roomregistration ADD COLUMN play_mode VARCHAR NOT NULL DEFAULT 'auto';"))
        if "ready" not in existing_reg_cols:
            conn.execute(text("ALTER TABLE roomregistration ADD COLUMN ready BOOLEAN NOT NULL DEFAULT FALSE;"))
        if "ready_at" not in existing_reg_cols:
            conn.execute(text("ALTER TABLE roomregistration ADD COLUMN ready_at TIMESTAMP NULL;"))
        conn.commit()

    # --- SEED DE JACKPOT Y TESORERÍA ---
    from sqlmodel import Session, select
    from app.models.user import User
    with Session(engine) as session:
        # Check Treasury User
        treasury_user = session.exec(select(User).where(User.privy_did == "treasury")).first()
        if not treasury_user:
            session.add(User(
                privy_did="treasury",
                email="treasury@axolot.to",
                wallet_address="0x" + "0" * 40,
                unlocked_board_slots=0
            ))
        # Check Treasury
        treasury = session.exec(select(TreasuryVault)).first()
        if not treasury:
            session.add(TreasuryVault(balance=0.0))
        # Check Jackpot
        jackpot = session.exec(select(JackpotVault)).first()
        if not jackpot:
            session.add(JackpotVault(current_amount=1000.0, seed_amount=1000.0))
        session.commit()

    # --- MIGRACIONES VIP ---
    with engine.connect() as conn:
        # Nuevos valores del enum transactiontype
        for val in ["burn", "vip_gal_expired", "f2p_reward", "tutorial_bonus", "webito_unlock", "staking_reward"]:
            conn.execute(text(f"ALTER TYPE transactiontype ADD VALUE IF NOT EXISTS '{val}'"))

        result_user2 = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'user';"))
        existing_user2 = {row[0] for row in result_user2.fetchall()}

        vip_cols = [
            ("vip_tier", "VARCHAR(20) NULL"),
            ("vip_expires_at", "TIMESTAMP NULL"),
            ("vip_streak_months", "INTEGER DEFAULT 0"),
            ("vip_streak_last_renewed", "TIMESTAMP NULL"),
            ("vip_pending_gal", "DOUBLE PRECISION DEFAULT 0.0"),
            ("vip_pending_gal_expires_at", "TIMESTAMP NULL"),
            ("vip_last_daily_gal_at", "TIMESTAMP NULL"),
            ("vip_tiers_activated", "TEXT DEFAULT '[]'"),
            ("vip_auto_renew", "BOOLEAN DEFAULT FALSE"),
        ]
        for col_name, col_type in vip_cols:
            if col_name not in existing_user2:
                conn.execute(text(f'ALTER TABLE "user" ADD COLUMN {col_name} {col_type};'))

        # is_frozen_by_vip en playerboard
        result_board2 = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'playerboard';"))
        existing_board2 = {row[0] for row in result_board2.fetchall()}
        if "is_frozen_by_vip" not in existing_board2:
            conn.execute(text("ALTER TABLE playerboard ADD COLUMN is_frozen_by_vip BOOLEAN DEFAULT FALSE;"))

        # NPC Bot Pool columns
        result_board3 = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'playerboard';"))
        existing_board3 = {row[0] for row in result_board3.fetchall()}
        if "is_npc_pool" not in existing_board3:
            conn.execute(text("ALTER TABLE playerboard ADD COLUMN is_npc_pool BOOLEAN NOT NULL DEFAULT FALSE;"))
        if "npc_room" not in existing_board3:
            conn.execute(text("ALTER TABLE playerboard ADD COLUMN npc_room VARCHAR(50) NULL;"))
        if "npc_retired" not in existing_board3:
            conn.execute(text("ALTER TABLE playerboard ADD COLUMN npc_retired BOOLEAN NOT NULL DEFAULT FALSE;"))
        if "origin_story" not in existing_board3:
            conn.execute(text("ALTER TABLE playerboard ADD COLUMN origin_story TEXT NULL;"))

        # is_frozen_by_vip en axolotito
        result_axo2 = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'axolotito';"))
        existing_axo2 = {row[0] for row in result_axo2.fetchall()}
        if "is_frozen_by_vip" not in existing_axo2:
            conn.execute(text("ALTER TABLE axolotito ADD COLUMN is_frozen_by_vip BOOLEAN DEFAULT FALSE;"))

        # cpu_win_streak — Win Streak mechanic
        if "cpu_win_streak" not in existing_axo2:
            conn.execute(text("ALTER TABLE axolotito ADD COLUMN cpu_win_streak INTEGER NOT NULL DEFAULT 0;"))

        # --- MIGRACIÓN F2P: campos de fragmentos astrales y tope diario ---
        result_user_f2p = conn.execute(text('SELECT column_name FROM information_schema.columns WHERE table_name = \'user\';'))
        existing_user_f2p = {row[0] for row in result_user_f2p.fetchall()}
        f2p_cols = [
            ("f2p_astral_fragments", "INTEGER NOT NULL DEFAULT 0"),
            ("f2p_daily_gal_earned", "DOUBLE PRECISION NOT NULL DEFAULT 0.0"),
            ("f2p_daily_gal_reset_at", "TIMESTAMP NULL"),
            ("last_f2p_daily_claim_at", "TIMESTAMP NULL"),
            ("f2p_daily_claim_streak", "INTEGER DEFAULT 0"),
        ]
        for col_name, col_type in f2p_cols:
            if col_name not in existing_user_f2p:
                conn.execute(text(f'ALTER TABLE "user" ADD COLUMN {col_name} {col_type};'))

        # --- MIGRACIÓN DE CHECK CONSTRAINTS EN WALLET ---
        if "postgresql" in str(engine.url):
            try:
                # Comprobar si existe la restricción axofichas_non_negative
                result_chk = conn.execute(text("""
                    SELECT conname 
                    FROM pg_constraint 
                    WHERE conrelid = 'wallet'::regclass AND conname = 'axofichas_non_negative';
                """))
                if not result_chk.fetchall():
                    conn.execute(text("ALTER TABLE wallet ADD CONSTRAINT axofichas_non_negative CHECK (axofichas >= 0);"))
                
                # Comprobar si existe la restricción frijolitos_non_negative
                result_chk2 = conn.execute(text("""
                    SELECT conname 
                    FROM pg_constraint 
                    WHERE conrelid = 'wallet'::regclass AND conname = 'frijolitos_non_negative';
                """))
                if not result_chk2.fetchall():
                    conn.execute(text("ALTER TABLE wallet ADD CONSTRAINT frijolitos_non_negative CHECK (frijolitos >= 0);"))
            except Exception as e:
                print(f"⚠️ Error al crear restricciones de wallet de forma dinámica: {e}")

        conn.commit()

    # --- REPARAR numero_loteria FALTANTE EN CARTAS ---
    # Asegura que todas las cartas tipo CARD tengan numero_loteria en su item_metadata.
    # Necesario si fueron creadas antes de que se añadiera este campo al seed.
    with engine.connect() as conn:
        nombres_y_numero = [
            ("El axolotl", 1), ("El diablito", 2), ("La Patrona", 3), ("El Godín", 4),
            ("La piñata", 5), ("La sirena", 6), ("El Trompo", 7), ("La botella", 8),
            ("El molcajete", 9), ("El Chilaquil", 10), ("El aguacate", 11), ("El luchador", 12),
            ("El sombrero", 13), ("La catrina", 14), ("El maíz", 15), ("La bandera", 16),
            ("El Acordeón", 17), ("La chancla", 18), ("El firulais", 19), ("El Michi", 20),
            ("La mano", 21), ("Los Tenis", 22), ("La luna", 23), ("El colibrí", 24),
            ("La caguama", 25), ("El café", 26), ("El corazón", 27), ("La salsa", 28),
            ("El Chamoy", 29), ("El camarón", 30), ("El papel picado", 31), ("El músico", 32),
            ("La araña", 33), ("El alebrije", 34), ("La estrella", 35), ("La concha", 36),
            ("El mundo", 37), ("El taco", 38), ("El nopal", 39), ("El alacrán", 40),
            ("La rosa", 41), ("La calavera", 42), ("La campana", 43), ("El cantarito", 44),
            ("El venado", 45), ("El sol", 46), ("El penacho", 47), ("La chalupa", 48),
            ("El vocho", 49), ("El pescado", 50), ("La Cobija", 51), ("La maceta", 52),
            ("El Elote", 53), ("La Botarga", 54),
        ]
        for nombre, numero in nombres_y_numero:
            conn.execute(text(
                """UPDATE itemcatalog
                   SET item_metadata = COALESCE(item_metadata, '{}')::jsonb
                       || jsonb_build_object('numero_loteria', :num, 'first_edition', true)
                   WHERE LOWER(name) = LOWER(:name)
                     AND item_type = 'CARD'
                     AND (item_metadata IS NULL OR item_metadata->>'numero_loteria' IS NULL)"""
            ), {"num": numero, "name": nombre})
        conn.commit()

    # --- INICIAR SCHEDULER MULTIJUGADOR ---
    import asyncio
    from app.services.multiplayer_service import MultiplayerService
    asyncio.create_task(MultiplayerService.start_scheduler_loop())

    # --- INICIAR SCHEDULER VIP ---
    from app.services.vip_scheduler import vip_scheduler_loop
    asyncio.create_task(vip_scheduler_loop())

# CORS super importante para que tu frontend Next.js no sea bloqueado
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://axolot.to", "https://www.axolot.to", "https://juega.axolot.to", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint for monitoring and restart polling."""
    return {"status": "ok", "service": "axolotto-backend"}

app.include_router(bank.router, prefix="/api/v1/bank", tags=["Economy"])
app.include_router(user.router, prefix="/api/v1/auth", tags=["Auth & Users"])
app.include_router(shop.router, prefix="/api/v1/shop", tags=["Store"])
app.include_router(incubation.router, prefix="/api/v1/incubation", tags=["Incubadora"])
app.include_router(metadata.router, prefix="/api/v1/metadata", tags=["Metadata"])
app.include_router(legacy.router, prefix="/api/v1/legacy", tags=["Legacy Backers 2021"])
app.include_router(board.router, prefix="/api/v1/board", tags=["Tablas de Juego (Lotería)"])
app.include_router(game.router, prefix="/api/v1/game", tags=["Partidas de Lotería"])
app.include_router(ranking.router, prefix="/api/v1/ranking", tags=["Rankings y Salón de la Gloria"])
app.include_router(multiplayer.router, prefix="/api/v1/multiplayer", tags=["Lotería Multijugador"])
app.include_router(game_ws.router, prefix="/api/v1/ws", tags=["WebSocket — Juego Manual"])
app.include_router(checkout.router, prefix="/api/v1/bank/checkout", tags=["Checkout Cripto"])
app.include_router(market.router, prefix="/api/v1/market", tags=["Marketplace P2P Inventario"])
app.include_router(market_escrow.router, prefix="/api/v1/market/escrow", tags=["Tianguis P2P Escrow"])
app.include_router(payments.router, prefix="/api/v1/payments", tags=["Pagos Fiat (Webhooks)"])
app.include_router(leonardo.router, prefix="/api/v1/leonardo", tags=["Leonardo.ai Cards"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])
app.include_router(whitelist.router, prefix="/api/v1/whitelist", tags=["Whitelist Fase 1"])
app.include_router(codes.router, prefix="/api/v1/codes", tags=["Promo Codes"])
app.include_router(f2p.router, prefix="/api/v1/f2p", tags=["F2P — Huevo Durmiente"])
app.include_router(tutorial.router, prefix="/api/v1/tutorial", tags=["Tutorial del Axolotito"])
app.include_router(cave_expansion.router, prefix="/api/v1/cave", tags=["Cenote — Expansión"])
app.include_router(admin_events.router, prefix="/api/v1/admin/events", tags=["admin-events"])
if settings.BLOCKCHAIN_MODE == "local":
    app.include_router(dev.router, prefix="/api/v1/dev", tags=["Dev Tools"])
app.include_router(events.router, prefix="/api/v1/events", tags=["events"])
app.include_router(rewards.router, prefix="/api/v1/rewards", tags=["Rewards"])
app.include_router(staking.router, prefix="/api/v1/staking", tags=["Staking"])
app.include_router(social.router, prefix="/api/v1/social", tags=["Social — Amigos"])
app.include_router(referrals.router, prefix="/api/v1/referrals", tags=["Social — Referidos"])
