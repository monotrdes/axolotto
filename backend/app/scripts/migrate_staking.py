"""
Script de migración: sincronizar inventario con tablas existentes.

Las tablas creadas ANTES del stake real no descontaron inventario.
Este script descuenta las cartas stakeadas de PlayerInventory para
que los conteos sean correctos.

Ejecutar UNA SOLA VEZ:
  cd backend && python -m app.scripts.migrate_staking
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from sqlmodel import Session, select
from app.database import engine
from app.models.board import PlayerBoard
from app.models.items import PlayerInventory


def run():
    with Session(engine) as session:
        boards = session.exec(
            select(PlayerBoard).where(PlayerBoard.is_dead == False)
        ).all()

        print(f"Tablas activas encontradas: {len(boards)}")
        deducted = 0
        skipped = 0

        for board in boards:
            card_first_editions = getattr(board, "card_first_editions", None) or [False] * len(board.card_ids)
            for idx, cid in enumerate(board.card_ids):
                is_fe = card_first_editions[idx] if idx < len(card_first_editions) else False
                inv = session.exec(
                    select(PlayerInventory)
                    .where(PlayerInventory.user_id == board.user_id)
                    .where(PlayerInventory.item_id == cid)
                    .where(PlayerInventory.is_first_edition == is_fe)
                ).first()
                if inv and inv.quantity > 0:
                    inv.quantity -= 1
                    if inv.quantity <= 0:
                        session.delete(inv)
                    else:
                        session.add(inv)
                    deducted += 1
                else:
                    print(f"  ⚠️  Tabla #{board.id} user={board.user_id}: carta {cid} FE={is_fe} no encontrada en inventario (qty=0 o inexistente)")
                    skipped += 1

        session.commit()
        print(f"\n✅ Migración completa: {deducted} copias descontadas, {skipped} omitidas (ya sin inventario).")


if __name__ == "__main__":
    run()
