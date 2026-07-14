#!/usr/bin/env python3
"""
seed_npc_boards.py — Populates the DB with persistent NPC bot boards.

Creates:
  - 1 NPC system user (privy_did="npc_axolotto_system")
  - 20 Rookie NPC boards
  - 20 Champion NPC boards

Idempotent: skips creation if boards already exist for the NPC user.

Usage:
    cd D:\Axolotto_2026\axolotto
    python backend/app/scripts/seed_npc_boards.py
"""

import os
import sys
import random

# ── Path setup ────────────────────────────────────────────────────────────────
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(backend_dir)

from dotenv import load_dotenv
load_dotenv(os.path.join(backend_dir, "..", ".env"))
load_dotenv(os.path.join(backend_dir, ".env"))

# Remap Docker hostnames when running on the host machine
if not os.path.exists("/.dockerenv"):
    if "DATABASE_URL" in os.environ:
        db_url = os.environ["DATABASE_URL"]
        if "@db_axolotto:5432" in db_url:
            os.environ["DATABASE_URL"] = db_url.replace("@db_axolotto:5432", "@127.0.0.1:5433")

from sqlalchemy import text, inspect
from sqlmodel import Session, select, func
from app.database import engine
from app.models.user import User
from app.models.board import PlayerBoard
from app.models.items import ItemCatalog, ItemType
from app.core.config import settings
from app.services.web3_service import Web3Service

NPC_PRIVY_DID = "npc_axolotto_system"
ROOKIE_COUNT = 20
CHAMPION_COUNT = 20

_rng = random.SystemRandom()


def _ensure_columns() -> None:
    """Add NPC board columns if they don't exist yet (standalone migration)."""
    inspector = inspect(engine)
    cols = {col["name"] for col in inspector.get_columns("playerboard")}
    migrations = [
        ("is_npc_pool",  "ALTER TABLE playerboard ADD COLUMN is_npc_pool BOOLEAN NOT NULL DEFAULT FALSE"),
        ("npc_room",     "ALTER TABLE playerboard ADD COLUMN npc_room VARCHAR(50) NULL"),
        ("npc_retired",  "ALTER TABLE playerboard ADD COLUMN npc_retired BOOLEAN NOT NULL DEFAULT FALSE"),
        ("origin_story", "ALTER TABLE playerboard ADD COLUMN origin_story TEXT NULL"),
    ]
    with engine.connect() as conn:
        for col, sql in migrations:
            if col not in cols:
                conn.execute(text(sql))
                print(f"  Added column: {col}")
        conn.commit()


def main() -> None:
    _ensure_columns()
    with Session(engine) as session:
        # 1. Get or create NPC user
        npc_user = session.exec(
            select(User).where(User.privy_did == NPC_PRIVY_DID)
        ).first()
        if not npc_user:
            npc_user = User(
                privy_did=NPC_PRIVY_DID,
                nickname="NPC System",
                wallet_address=settings.NPC_WALLET_ADDRESS,
            )
            session.add(npc_user)
            session.commit()
            session.refresh(npc_user)
            print(f"Created NPC user: privy_did={NPC_PRIVY_DID}, wallet={settings.NPC_WALLET_ADDRESS}")
        else:
            # Backfill wallet if it was created before this field was set
            if not npc_user.wallet_address:
                npc_user.wallet_address = settings.NPC_WALLET_ADDRESS
                session.add(npc_user)
                session.commit()
                print(f"Updated NPC user wallet: {settings.NPC_WALLET_ADDRESS}")
            else:
                print(f"NPC user already exists: privy_did={NPC_PRIVY_DID}")

        # 2. Check if boards already exist (idempotent)
        existing_count = session.exec(
            select(func.count(PlayerBoard.id))
            .where(PlayerBoard.user_id == NPC_PRIVY_DID)
            .where(PlayerBoard.is_npc_pool == True)
        ).one()

        if existing_count > 0:
            print(f"NPC boards already exist ({existing_count} total). Skipping seed.")
            return

        # 3. Fetch all card IDs from ItemCatalog
        all_cards = session.exec(
            select(ItemCatalog).where(ItemCatalog.item_type == ItemType.CARD)
        ).all()
        if len(all_cards) < 16:
            print(f"ERROR: Only {len(all_cards)} cards found in catalog. Need at least 16.")
            sys.exit(1)

        all_card_ids = [c.id for c in all_cards]
        print(f"Found {len(all_card_ids)} cards in catalog.")

        # 4. Create NPC boards
        created_rookie = 0
        created_champion = 0

        for i in range(1, ROOKIE_COUNT + 1):
            board = PlayerBoard(
                user_id=NPC_PRIVY_DID,
                name=f"Bot Rookie #{i}",
                card_ids=_rng.sample(all_card_ids, 16),
                card_first_editions=[False] * 16,
                is_npc_pool=True,
                npc_room="rookie",
                npc_retired=False,
            )
            session.add(board)
            created_rookie += 1

        for i in range(1, CHAMPION_COUNT + 1):
            board = PlayerBoard(
                user_id=NPC_PRIVY_DID,
                name=f"Bot Champion #{i}",
                card_ids=_rng.sample(all_card_ids, 16),
                card_first_editions=[False] * 16,
                is_npc_pool=True,
                npc_room="champion",
                npc_retired=False,
            )
            session.add(board)
            created_champion += 1

        session.commit()
        # Refresh to get auto-assigned IDs from the DB
        all_new_boards = session.exec(
            select(PlayerBoard)
            .where(PlayerBoard.user_id == NPC_PRIVY_DID)
            .where(PlayerBoard.is_npc_pool == True)
            .where(PlayerBoard.blockchain_token_id == None)
        ).all()

        print(f"Seeded {created_rookie} Rookie NPC boards and {created_champion} Champion NPC boards.")

        # Mint each board on-chain (safe: skips gracefully if Anvil is not running)
        minted_count = 0
        for board in all_new_boards:
            try:
                token_id = Web3Service.create_npc_board(board.card_ids)
                board.blockchain_token_id = token_id
                session.add(board)
                minted_count += 1
                print(f"  Minted on-chain: board_id={board.id}, token_id={token_id}")
            except Exception as e:
                print(f"  Could not mint NPC board on-chain (board_id={board.id}): {e}")

        if minted_count > 0:
            session.commit()
            print(f"Saved {minted_count} blockchain_token_id(s) to DB.")

        print("Done.")


if __name__ == "__main__":
    main()
