from datetime import datetime, timedelta
from sqlmodel import Session, select
from fastapi import HTTPException
from starlette.requests import Request

from app.models.axolotito import Axolotito
from app.models.user import User
from app.api.v1.endpoints.staking import stake_axolotito, unstake_axolotito
from app.services.bank_service import BankService

def phase_staking_start(engine, config, **state) -> dict:
    session: Session = state["session"]
    progress = state["progress"]
    players: list = state["players"]
    stats: dict = state["stats"]
    errors: list = state["errors"]

    progress("  👑 Iniciando Staking de Axolotitos (para jugadores con >= 2 Axolotitos)...")
    staked_count = 0

    mock_scope = {
        "type": "http",
        "method": "POST",
        "path": "/api/v1/staking/stake",
        "headers": []
    }
    mock_req = Request(mock_scope)

    for p in players:
        user_id = p["user_id"]
        personality = p["personality"]
        
        # Check owned axolotitos
        axos = session.exec(
            select(Axolotito)
            .where(Axolotito.user_id == user_id)
            .where(Axolotito.is_frozen_by_vip == False)
        ).all()
        
        # If player has at least 2 axolotitos, stake the extra ones (all except the first one)
        if len(axos) >= 2:
            for staked_axo in axos[1:]:
                # Make sure it's idle
                if staked_axo.status != "idle":
                    staked_axo.status = "idle"
                    session.add(staked_axo)
                    session.commit()
                    session.refresh(staked_axo)
                    
                try:
                    # Call stake endpoint
                    res = stake_axolotito(
                        request=mock_req,
                        axolotito_id=staked_axo.id,
                        status="studying",
                        session=session,
                        verified_user_id=user_id
                    )
                    staked_count += 1
                    print(f"  👑 {user_id}: Axolotito '{staked_axo.name}' puesto en staking (studying)")
                except HTTPException as e:
                    errors.append(f"stake_axolotito {user_id}: {e.detail}")
                except Exception as e:
                    errors.append(f"stake_axolotito_unexpected {user_id}: {e}")
                    session.rollback()

    stats["axolotitos_staked"] = staked_count
    progress(f"  ✅ Staking iniciado para {staked_count} Axolotito(s).")
    return {}

def phase_staking_end(engine, config, **state) -> dict:
    session: Session = state["session"]
    progress = state["progress"]
    players: list = state["players"]
    stats: dict = state["stats"]
    errors: list = state["errors"]

    progress("  👑 Finalizando Staking de Axolotitos y reclamando recompensas...")
    unstaked_count = 0
    total_rewards_frj = 0.0

    mock_scope = {
        "type": "http",
        "method": "POST",
        "path": "/api/v1/staking/unstake",
        "headers": []
    }
    mock_req = Request(mock_scope)

    for p in players:
        user_id = p["user_id"]
        
        # Find staked axolotitos
        staked_axos = session.exec(
            select(Axolotito)
            .where(Axolotito.user_id == user_id)
            .where(Axolotito.status.in_(["studying", "resting"]))
        ).all()
        
        for axo in staked_axos:
            # Simular paso de tiempo: restar 4 horas de last_staking_claim para generar yield
            # (ya que la simulación corre en milisegundos y de otra forma daría 0.0 FRJ)
            axo.last_staking_claim = datetime.utcnow() - timedelta(hours=4)
            session.add(axo)
            session.commit()
            session.refresh(axo)
            
            try:
                # Call unstake endpoint which claims reward and sets to idle
                res = unstake_axolotito(
                    request=mock_req,
                    axolotito_id=axo.id,
                    session=session,
                    verified_user_id=user_id
                )
                unstaked_count += 1
                claimed = res.get("claimed_frj", 0.0)
                total_rewards_frj += claimed
                print(f"  👑 {user_id}: Axolotito '{axo.name}' sacado de staking. Recompensa: {claimed:.2f} FRJ")
            except HTTPException as e:
                errors.append(f"unstake_axolotito {user_id}: {e.detail}")
            except Exception as e:
                errors.append(f"unstake_axolotito_unexpected {user_id}: {e}")
                session.rollback()

    stats["axolotitos_unstaked"] = unstaked_count
    stats["staking_rewards_frj"] = total_rewards_frj
    progress(f"  ✅ Staking finalizado para {unstaked_count} Axolotito(s). Recompensa total: {total_rewards_frj:.2f} FRJ")
    return {}
