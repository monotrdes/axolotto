import secrets

from sqlmodel import Session, select

from app.models.user import User
from app.models.economy import Wallet

from sim_types import PERSONALITY_POOL, PRO_USER_DID, _rng


def phase_create_users(engine, config, **state) -> dict:
    """Crea n_players usuarios con personalidades distintas. Devuelve dict con key 'players'."""
    session: Session = state["session"]
    progress = state["progress"]
    stats: dict = state["stats"]

    n_players = config.players

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
            cave_level=1,
        )
        session.add(pro_user)
        session.commit()
        session.refresh(pro_user)
    else:
        pro_user.cave_level = 1
        session.add(pro_user)
        session.commit()
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
                cave_level=1,
            )
            session.add(user)
            session.commit()
            stats["users_created"] = stats.get("users_created", 0) + 1
        else:
            existing.wallet_address = wallet_addr
            existing.cave_level = 1
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
    return {"players": players}
