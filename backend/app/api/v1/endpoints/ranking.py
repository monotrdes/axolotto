from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime

from app.database import get_session
from app.models.user import User
from app.models.axolotito import Axolotito
from app.models.board import PlayerBoard

router = APIRouter()

@router.get("/axolotitos", response_model=List[dict])
def get_axolotito_ranking(
    sort_by: str = "level",
    limit: int = 20,
    session: Session = Depends(get_session)
):
    """Obtiene el ranking de los mejores Axolotitos ordenados por Nivel o Poder de combate."""
    if sort_by not in ("level", "power"):
        raise HTTPException(status_code=400, detail="Criterio de ordenamiento no válido para Axolotitos.")
    
    # Consulta de Axolotito cruzando con User
    statement = select(Axolotito, User).join(User, Axolotito.user_id == User.privy_did)
    
    if sort_by == "level":
        statement = statement.order_by(Axolotito.level.desc(), Axolotito.experience.desc())
    elif sort_by == "power":
        power_expr = (
            Axolotito.stat_luck +
            Axolotito.stat_focus +
            Axolotito.stat_stamina +
            (100 - Axolotito.stat_salinity)
        )
        statement = statement.order_by(power_expr.desc())
        
    statement = statement.limit(limit)
    results = session.exec(statement).all()
    
    ranking = []
    for axo, owner in results:
        power = (
            axo.stat_luck +
            axo.stat_focus +
            axo.stat_stamina +
            (100 - axo.stat_salinity)
        )
        
        ranking.append({
            "id": axo.id,
            "name": axo.name,
            "level": axo.level,
            "experience": axo.experience,
            "blockchain_token_id": axo.blockchain_token_id,
            "skin_color": axo.skin_color,
            "gill_type": axo.gill_type,
            "eye_type": axo.eye_type,
            "mouth_type": axo.mouth_type,
            "tail_type": axo.tail_type,
            "forehead_type": axo.forehead_type,
            "limb_type": axo.limb_type,
            "status": axo.status,
            "energy_current": axo.energy_current,
            "stat_stamina": axo.stat_stamina,
            "poder": round(power, 1),
            "power_rating": round(power, 1),
            "stats": {
                "suerte": axo.stat_luck,
                "ojo":    axo.stat_focus,
                "pila":   axo.stat_stamina,
                "sal":    axo.stat_salinity,
            },
            "owner_id": owner.privy_did,
            "owner_nickname": owner.nickname or (f"Jugador_{owner.privy_did[-8:]}" if len(owner.privy_did) > 8 else owner.privy_did) if owner.privy_did else "Jugador Anónimo",
            "owner_avatar_url": owner.avatar_url,
            "owner_vip_tier": owner.vip_tier if owner.is_vip else None,
        })

    return ranking

@router.get("/boards/forjadas", response_model=List[dict])
def get_forged_boards(session: Session = Depends(get_session)):
    """Tablas Forjadas: NPC boards that graduated to level 10 and await the gashapon pool."""
    boards = session.exec(
        select(PlayerBoard)
        .where(PlayerBoard.is_npc_pool == True)
        .where(PlayerBoard.npc_retired == True)
        .order_by(PlayerBoard.level.desc(), PlayerBoard.games_played.desc())
    ).all()
    return [
        {
            "id": b.id,
            "name": b.name,
            "level": b.level,
            "xp": b.xp,
            "games_played": b.games_played,
            "games_won": b.games_won,
            "win_rate": round(b.games_won / max(1, b.games_played) * 100, 1),
            "origin_story": b.origin_story,
            "npc_room": b.npc_room,
            "is_npc_pool": b.is_npc_pool,
            "npc_retired": b.npc_retired,
        }
        for b in boards
    ]


@router.get("/boards", response_model=List[dict])
def get_boards_ranking(
    sort_by: str = "wins",
    limit: int = 20,
    session: Session = Depends(get_session)
):
    """Obtiene el ranking de los mejores tableros de juego (Lotería)."""
    if sort_by not in ("wins", "level", "lucky", "salty", "streak"):
        raise HTTPException(status_code=400, detail="Criterio de ordenamiento no válido para Tablas.")
        
    statement = select(PlayerBoard, User).join(User, PlayerBoard.user_id == User.privy_did).where(PlayerBoard.is_dead == False)
    
    if sort_by == "wins":
        statement = statement.order_by(PlayerBoard.games_won.desc(), PlayerBoard.games_played.desc())
    elif sort_by == "level":
        statement = statement.order_by(PlayerBoard.level.desc(), PlayerBoard.xp.desc())
        
    if sort_by in ("wins", "level"):
        statement = statement.limit(limit)
        results = session.exec(statement).all()
    else:
        # Filtro de mínimo de 5 partidas jugadas para rankings competitivos basados en desempeño
        statement = statement.where(PlayerBoard.games_played >= 5)
        results = session.exec(statement).all()
        
    ranking_list = []
    from app.services.board_service import get_board_csr
    
    for board, owner in results:
        csr = get_board_csr(board)
        win_rate = (board.games_won / board.games_played * 100) if board.games_played > 0 else 0.0
        
        # Calcular racha de victorias de derecha a izquierda
        streak = 0
        if board.recent_games_results:
            for res in reversed(board.recent_games_results):
                if res:
                    streak += 1
                else:
                    break
                    
        ranking_list.append({
            "id": board.id,
            "name": board.name,
            "level": board.level,
            "xp": board.xp,
            "games_played": board.games_played,
            "games_won": board.games_won,
            "win_rate": round(win_rate, 1),
            "csr": round(csr, 1),
            "streak": streak,
            "is_listed_for_rent": board.is_listed_for_rent,
            "is_rented": board.is_rented,
            "rent_fee_gal": board.rent_fee_gal,
            "rent_share_owner_pct": board.rent_share_owner_pct,
            "is_npc_pool": board.is_npc_pool,
            "npc_retired": board.npc_retired,
            "origin_story": board.origin_story,
            "owner_id": owner.privy_did,
            "owner_nickname": "🤖 Sistema" if board.is_npc_pool else (owner.nickname or (f"Jugador_{owner.privy_did[-8:]}" if len(owner.privy_did) > 8 else owner.privy_did) if owner.privy_did else "Jugador Anónimo"),
            "owner_avatar_url": owner.avatar_url,
            "owner_vip_tier": owner.vip_tier if owner.is_vip else None,
        })
        
    # Ordenar y truncar en memoria si es necesario
    if sort_by == "lucky":
        ranking_list.sort(key=lambda x: (x["csr"], x["games_won"]), reverse=True)
        ranking_list = ranking_list[:limit]
    elif sort_by == "salty":
        ranking_list.sort(key=lambda x: (x["csr"], -x["games_played"]))
        ranking_list = ranking_list[:limit]
    elif sort_by == "streak":
        ranking_list.sort(key=lambda x: (x["streak"], x["games_won"]), reverse=True)
        ranking_list = ranking_list[:limit]
        
    return ranking_list
