from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
from app.database import get_session
from app.models.items import ItemCatalog, WebitoIncubation, PlayerInventory, ItemType
from app.models.user import User
from app.services.bank_service import BankService
from app.services.axo_names import generar_nombre_axolotito
from app.models.economy import Wallet, TransactionLedger, CurrencyType, TransactionType
import secrets
import random
_rng = random.SystemRandom()
import sqlalchemy as sa
from app.models.axolotito import Axolotito
from app.services.web3_service import Web3Service

from app.core.auth import get_verified_user_id, verify_no_active_game
from app.services.imprinting_service import (
    initial_base_stats,
    required_games_for_rarity,
    final_stats as imprinting_final_stats,
)

router = APIRouter()

# --- MODELOS PYDANTIC ---
class StartImprintingPayload(BaseModel):
    incubation_id: int
    padrino_axolotito_id: int


@router.get("/user/{user_id}")
def get_user_incubations(
    user_id: str, 
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id)
):
    if user_id != verified_user_id:
        raise HTTPException(status_code=403, detail="No tienes acceso a los recursos de este usuario.")

    user = session.exec(select(User).where(User.privy_did == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    # Calcular límite de incubaciones simultáneas del Cenote
    from app.api.v1.endpoints.cave_expansion import CAVE_PASSIVE_BONUSES
    bonus_slots = 0
    for lvl in range(1, user.cave_level + 1):
        bonus = CAVE_PASSIVE_BONUSES.get(lvl, {})
        bonus_slots += bonus.get("global_incubation_slot", 0)
    
    max_incubation_slots = user.cave_level + bonus_slots

    # 1. AUTO-SYNC: Meter huevos huérfanos a la incubadora (hasta el límite de slots)
    inventario = session.exec(
        select(PlayerInventory, ItemCatalog)
        .join(ItemCatalog, PlayerInventory.item_id == ItemCatalog.id)
        .where(PlayerInventory.user_id == user_id)
        .where(ItemCatalog.item_type == ItemType.EGG)
    ).all()

    # Contar incubaciones activas existentes
    active_incubations_count = session.exec(
        select(sa.func.count(WebitoIncubation.id)).where(WebitoIncubation.user_id == user_id)
    ).one_or_none() or 0

    sync_needed = False
    for inv, catalogo in inventario:
        existentes = session.exec(
            select(WebitoIncubation).where(WebitoIncubation.user_id == user_id).where(WebitoIncubation.item_id == catalogo.id)
        ).all()
        faltantes = inv.quantity - len(existentes)
        if faltantes > 0:
            for _ in range(faltantes):
                if active_incubations_count >= max_incubation_slots:
                    break
                nueva = WebitoIncubation(user_id=user_id, item_id=catalogo.id, fecha_eclosion_estimada=datetime.utcnow() + timedelta(seconds=5))
                session.add(nueva)
                active_incubations_count += 1
                sync_needed = True

    if sync_needed:
        session.commit()

    # 2. TRAER DATOS PARA EL FRONTEND
    statement = select(WebitoIncubation, ItemCatalog.name).join(
        ItemCatalog, WebitoIncubation.item_id == ItemCatalog.id
    ).where(WebitoIncubation.user_id == user_id)
    
    results = session.exec(statement).all()

    payload = []
    for incubation, item_name in results:
        now = datetime.utcnow()
        if incubation.fecha_eclosion_estimada > now:
            horas_restantes = int((incubation.fecha_eclosion_estimada - now).total_seconds() / 3600)
        else:
            horas_restantes = 0

        padrino_name = None
        padrino_nature = None
        if incubation.imprinting_padrino_id is not None:
            padrino = session.get(Axolotito, incubation.imprinting_padrino_id)
            if padrino:
                padrino_name = padrino.name
                padrino_nature = padrino.nature

        payload.append({
            "id": incubation.id,
            "item_id": incubation.item_id,
            "name": item_name,
            "horasRestantes": horas_restantes,
            "emoji": "🥚",
            # --- BONOS ACUMULADOS (imprinting) ---
            "bonus_focus": incubation.bonus_focus,
            "bonus_stamina": incubation.bonus_stamina,
            "bonus_luck": incubation.bonus_luck,
            "bonus_salinity_adj": incubation.bonus_salinity_adj,
            "genetic_purity": incubation.genetic_purity,
            "imprinting_padrino_id": incubation.imprinting_padrino_id,
            "imprinting_complete": incubation.imprinting_complete,
            "imprinting_games_played": incubation.imprinting_games_played,
            "tutorial_phase": incubation.tutorial_phase,
            "padrino_name": padrino_name,
            "padrino_nature": padrino_nature,
        })

    return payload



def generate_axolotito_dna(stats: dict) -> str:
    # Formatear cada stat con 3 dígitos rellenos de ceros
    salinity_part = f"{int(stats['salinity']):03d}"
    luck_part = f"{int(stats['luck']):03d}"
    focus_part = f"{int(stats['focus']):03d}"
    stamina_part = f"{int(stats['stamina']):03d}"
    charisma_part = f"{int(stats['charisma']):03d}"
    agility_part = f"{int(stats['agility']):03d}"
    wisdom_part = f"{int(stats['wisdom']):03d}"
    strength_part = f"{int(stats['strength']):03d}"
    
    # 8 dígitos aleatorios para el seed/variación genética (para breeding)
    sys_rand = secrets.SystemRandom()
    seed_part = f"{sys_rand.randint(0, 99999999):08d}"
    
    return f"{salinity_part}{luck_part}{focus_part}{stamina_part}{charisma_part}{agility_part}{wisdom_part}{strength_part}{seed_part}"


def map_stats_to_traits(stats: dict) -> dict:
    sal = stats["salinity"]
    luck = stats["luck"]
    focus = stats["focus"]
    stamina = stats["stamina"]
    charisma = stats["charisma"]
    agility = stats["agility"]
    wisdom = stats["wisdom"]
    strength = stats["strength"]
    
    # Salinidad -> skin_color
    if sal <= 10.0: skin_color = "pink"
    elif sal <= 30.0: skin_color = "gray_light_pink"
    elif sal <= 60.0: skin_color = "gray_light"
    elif sal <= 90.0: skin_color = "gray_dark"
    else: skin_color = "gray_dead_sea"
    
    # Concentración -> eye_type
    if focus < 20.0: eye_type = "derp"
    elif focus < 50.0: eye_type = "dreamer"
    elif focus < 80.0: eye_type = "cute"
    elif focus < 95.0: eye_type = "intellectual"
    else: eye_type = "zen"
    
    # Energía -> gill_type
    if stamina < 80: gill_type = "short"
    elif stamina < 120: gill_type = "normal"
    elif stamina < 160: gill_type = "feathery"
    elif stamina < 190: gill_type = "crown"
    else: gill_type = "phoenix"
    
    # Carisma -> mouth_type
    if charisma < 20.0: mouth_type = "flat"
    elif charisma < 60.0: mouth_type = "smile"
    elif charisma < 80.0: mouth_type = "fang"
    elif charisma < 95.0: mouth_type = "rockstar"
    else: mouth_type = "divine"
    
    # Agilidad -> tail_type
    if agility < 30.0: tail_type = "standard"
    elif agility < 60.0: tail_type = "wavy"
    elif agility < 85.0: tail_type = "betta"
    else: tail_type = "plasma"
    
    # Sabiduría -> forehead_type
    if wisdom < 40.0: forehead_type = "none"
    elif wisdom < 70.0: forehead_type = "stripes"
    elif wisdom < 90.0: forehead_type = "gem"
    else: forehead_type = "halo"
    
    # Fuerza -> limb_type
    if strength < 40.0: limb_type = "soft"
    elif strength < 75.0: limb_type = "claws"
    elif strength < 95.0: limb_type = "scales"
    else: limb_type = "coral"
    
    return {
        "skin_color": skin_color,
        "gill_type": gill_type,
        "eye_type": eye_type,
        "mouth_type": mouth_type,
        "tail_type": tail_type,
        "forehead_type": forehead_type,
        "limb_type": limb_type
    }


@router.post("/hatch/{incubation_id}")
def hatch_webito(
    incubation_id: int,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(verify_no_active_game)
):
    # 1. Buscar la incubación con lock pesimista para prevenir double-hatch
    incubation = session.exec(
        select(WebitoIncubation)
        .where(WebitoIncubation.id == incubation_id)
        .with_for_update()
    ).first()
    if not incubation or incubation.user_id != verified_user_id:
        raise HTTPException(status_code=404, detail="Incubación no encontrada.")

    # 1.5. Verificar si es un Webito Astral
    egg_item = session.get(ItemCatalog, incubation.item_id)
    is_astral = False
    if egg_item and egg_item.item_metadata:
        is_astral = egg_item.item_metadata.get("is_astral", False)

    # 2. Verificar que el usuario exista
    user = session.exec(select(User).where(User.privy_did == verified_user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    # 2.5 Verificar límite de axolotitos en el Cenote antes de eclosionar
    total_axolotitos = session.exec(
        select(sa.func.count(Axolotito.id))
        .where(Axolotito.user_id == verified_user_id)
    ).one_or_none() or 0
    
    axo_limit = user.cave_level + user.vip_bonus_axolotito_slots
    if total_axolotitos >= axo_limit:
        raise HTTPException(
            status_code=400,
            detail=f"Límite alcanzado. Ya tienes {total_axolotitos} Axolotito(s) eclosionados (límite: {axo_limit}). "
                   f"Por favor expande tu Cenote antes de eclosionar nuevos huevos."
        )

    # 3. Validar si está listo (la fecha estimada debe haberse cumplido)
    now = datetime.utcnow()
    if incubation.fecha_eclosion_estimada > now:
        raise HTTPException(
            status_code=400,
            detail="El huevo aún requiere tiempo para estar listo para eclosionar."
        )

    # 4. El imprinting debe estar completo
    if not incubation.imprinting_complete:
        raise HTTPException(
            status_code=400,
            detail="El imprinting no está completo. Juega más partidas con tu padrino.",
        )

    return _perform_hatch(incubation, user, session, is_astral)


def _perform_hatch(
    incubation: WebitoIncubation,
    user: User,
    session: Session,
    is_astral: bool = False,
) -> dict:
    """Núcleo de eclosión: calcula stats finales, traits, DNA y nombre, acuña el NFT,
    crea el registro Axolotito y limpia la incubación. Los callers validan las
    precondiciones (tiempo, imprinting). Reutilizado por el endpoint /hatch y por
    el cierre del tutorial (auto-eclosión)."""
    user_id = incubation.user_id
    sys_rand = secrets.SystemRandom()

    # --- IMPRINTING: stats finales ---
    computed = imprinting_final_stats(incubation)
    final_luck      = computed["stat_luck"]
    final_focus     = computed["stat_focus"]
    final_stamina   = computed["stat_stamina"]
    final_salinity  = computed["stat_salinity"]
    final_agility   = computed["stat_agility"]
    final_charisma  = 0.0
    final_wisdom    = 0.0
    final_strength  = 0.0
    purity          = 100.0
    mutation_type   = "imprinting"
    salinity_penalty = 0.0

    # 4.5. Seleccionar Personalidad (Nature)
    chosen_nature = sys_rand.choice(["methodical", "lucky", "hyperactive", "shy", "wise", "glutton"])

    # Agrupar estadísticas finales
    stats = {
        "salinity": final_salinity,
        "luck": final_luck,
        "focus": final_focus,
        "stamina": final_stamina,
        "charisma": final_charisma,
        "agility": final_agility,
        "wisdom": final_wisdom,
        "strength": final_strength
    }

    # 5. Mapear estadísticas a rasgos cosméticos
    traits = map_stats_to_traits(stats)

    if is_astral:
        # Webito Astral aesthetic overrides: 80% astral, 20% gold
        traits["skin_color"] = "astral" if sys_rand.random() < 0.80 else "gold"
        
        # Guarantee at least one premium visual mutation: halo (forehead) or divine (mouth)
        has_halo = sys_rand.random() < 0.50
        has_divine = sys_rand.random() < 0.50
        if not has_halo and not has_divine:
            if sys_rand.random() < 0.50:
                has_halo = True
            else:
                has_divine = True
                
        if has_halo:
            traits["forehead_type"] = "halo"
        if has_divine:
            traits["mouth_type"] = "divine"

    # 6. Mutación Mítica (Pureza >= 110%): 25% de probabilidad de otorgar un rasgo visual mítico/raro
    if purity >= 110.0 and sys_rand.random() < 0.25:
        mutation_type = "mítica"
        rare_traits = [
            ("gill_type", "phoenix"),
            ("tail_type", "plasma"),
            ("forehead_type", "halo"),
            ("mouth_type", "divine"),
            ("limb_type", "coral")
        ]
        chosen_trait, chosen_val = sys_rand.choice(rare_traits)
        traits[chosen_trait] = chosen_val

    # 7. Empacar ADN (basado en estadísticas finales)
    dna = generate_axolotito_dna(stats)
    
    # Generación de nombre — determinístico desde DNA + incubation_id
    # Mismo DNA + misma incubación = siempre el mismo nombre
    # DNA idéntico + incubación distinta = nombres distintos (colisión imposible en práctica)
    name = generar_nombre_axolotito(
        dna=dna,
        incubation_id=incubation.id,
        stats=stats,
    )

    # 8. Acuñar NFT en Blockchain
    target_wallet = user.wallet_address if user.wallet_address else "0x0000000000000000000000000000000000000000"
    
    # 9. Calcular next_token_id local como fallback
    # Para evitar colisiones con los IDs secuenciales de la blockchain (1, 2, 3...),
    # los fallbacks locales empiezan en 1,000,000,000.
    # Buscar el máximo global (incluye IDs on-chain bajos que puedan existir).
    fallback_max_row = session.exec(
        sa.select(sa.func.max(Axolotito.blockchain_token_id))
    ).first()
    max_existing = fallback_max_row[0] if fallback_max_row and fallback_max_row[0] is not None else 0
    next_token_id = max(max_existing, 1_000_000_000) + 1

    blockchain_token_id = next_token_id
    try:
        stats_tuple = (
            int(final_salinity),
            int(final_luck),
            int(final_focus),
            int(final_stamina),
            int(final_charisma),
            int(final_agility),
            int(final_wisdom),
            int(final_strength)
        )
        traits_tuple = (
            traits.get("skin_color", "pink"),
            traits.get("gill_type", "normal"),
            traits.get("eye_type", "cute"),
            traits.get("mouth_type", "smile"),
            traits.get("tail_type", "standard"),
            traits.get("forehead_type", "none"),
            traits.get("limb_type", "soft")
        )
        tx_hash = Web3Service.mint_axolotito_onchain(target_wallet, dna, stats_tuple, traits_tuple)

        # Intentar obtener el ID real de la blockchain
        real_token_id = Web3Service.get_token_id_from_tx(tx_hash)
        if real_token_id is not None:
            # Safety: verificar que el ID on-chain no colisione con un axolotito existente
            existing = session.exec(
                select(Axolotito).where(Axolotito.blockchain_token_id == real_token_id)
            ).first()
            if existing:
                print(f"⚠️ Token ID on-chain {real_token_id} ya existe en DB (axo #{existing.id}), usando fallback {next_token_id}")
            else:
                blockchain_token_id = real_token_id
    except Exception as e:
        print(f"⚠️ Error al acuñar NFT de Axolotito en Blockchain: {e}")
        tx_hash = f"0x_error_fallback_{secrets.token_hex(32)}"

    print(f"🧬 Bonos de cuidado aplicados con Pureza del {purity:.1f}% — Mutación: {mutation_type}")

    # Capturar valores antes de eliminar la incubación
    _imprinting_padrino_id = incubation.imprinting_padrino_id
    _imprinting_games_played = incubation.imprinting_games_played

    padrino = None
    if _imprinting_padrino_id is not None:
        padrino = session.exec(
            select(Axolotito)
            .where(Axolotito.id == _imprinting_padrino_id)
            .with_for_update()
        ).first()

    if padrino:
        padrino.mentorship_count = (padrino.mentorship_count or 0) + 1
        
        # Compare deltas to find the highest
        bonuses = {
            "luck": incubation.bonus_luck,
            "focus": incubation.bonus_focus,
            "stamina": incubation.bonus_stamina,
            "salinity": incubation.bonus_salinity_adj
        }
        highest_stat = max(bonuses, key=bonuses.get)
        
        if highest_stat == "luck":
            padrino.stat_luck += 2.0
        elif highest_stat == "focus":
            padrino.stat_focus += 2.0
        elif highest_stat == "stamina":
            padrino.stat_stamina += 2
        elif highest_stat == "salinity":
            padrino.stat_salinity += 2.0
            
        padrino.experience += 150
        while padrino.experience >= (padrino.level * 100):
            padrino.experience -= (padrino.level * 100)
            padrino.level += 1
            
        session.add(padrino)

    nuevo_axolote = Axolotito(
        user_id=user_id,
        name=name,
        skin_color=traits["skin_color"],
        gill_type=traits["gill_type"],
        eye_type=traits["eye_type"],
        mouth_type=traits["mouth_type"],
        tail_type=traits["tail_type"],
        forehead_type=traits["forehead_type"],
        limb_type=traits["limb_type"],
        stat_salinity=final_salinity,
        stat_luck=final_luck,
        stat_focus=final_focus,
        stat_stamina=final_stamina,
        stat_charisma=final_charisma,
        stat_agility=final_agility,
        stat_wisdom=final_wisdom,
        stat_strength=final_strength,
        energy_current=final_stamina,
        blockchain_token_id=blockchain_token_id,
        dna_sequence=dna,
        nature=chosen_nature,
        status="idle",
        tutored_by_id=padrino.id if padrino else None
    )
    session.add(nuevo_axolote)

    # 10. Consumir el huevo de la incubación e inventario
    session.delete(incubation)
    
    inv_egg = session.exec(
        select(PlayerInventory)
        .where(PlayerInventory.user_id == user_id)
        .where(PlayerInventory.item_id == incubation.item_id)
        .with_for_update()
    ).first()

    if inv_egg:
        inv_egg.quantity -= 1
        if inv_egg.quantity <= 0:
            session.delete(inv_egg)
        else:
            session.add(inv_egg)

    session.commit()
    session.refresh(nuevo_axolote)

    # Log para transparencia
    print(f"🐣 Nacimiento Exitoso: {nuevo_axolote.name} creado para {user_id}. DNA: {dna}. TxHash: {tx_hash}")

    return {
        "mensaje": "¡Huevo eclosionado con éxito!",
        "axolotito": {
            "id": nuevo_axolote.id,
            "name": nuevo_axolote.name,
            "blockchain_token_id": nuevo_axolote.blockchain_token_id,
            "dna": nuevo_axolote.dna_sequence,
            "tx_hash": tx_hash,
            "traits": traits,
            "stats": {
                "suerte":   nuevo_axolote.stat_luck,
                "ojo":      nuevo_axolote.stat_focus,
                "pila":     nuevo_axolote.stat_stamina,
                "sal":      nuevo_axolote.stat_salinity,
                # Campos legacy (para compatibilidad con ABI)
                "salinity": nuevo_axolote.stat_salinity,
                "luck":     nuevo_axolote.stat_luck,
                "focus":    nuevo_axolote.stat_focus,
                "stamina":  nuevo_axolote.stat_stamina,
                "agility":  nuevo_axolote.stat_agility,
                "charisma": 0.0,
                "wisdom":   0.0,
                "strength": 0.0,
            },
            "imprinting_summary": {
                "padrino_id":   _imprinting_padrino_id,
                "games_played": _imprinting_games_played,
            },
            "genetic_purity": purity,
            "mutation_type": mutation_type,
            "salinity_penalty": salinity_penalty
        }
    }

@router.post("/start-imprinting")
def start_imprinting(
    payload: StartImprintingPayload,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(verify_no_active_game),
):
    """Inicia el imprinting de un Webito. Asigna padrino y genera stats base."""
    incubation = session.exec(
        select(WebitoIncubation)
        .where(WebitoIncubation.id == payload.incubation_id)
        .with_for_update()
    ).first()
    if not incubation or incubation.user_id != verified_user_id:
        raise HTTPException(status_code=404, detail="Incubación no encontrada.")
    if incubation.imprinting_padrino_id is not None:
        raise HTTPException(status_code=400, detail="El imprinting ya fue iniciado.")

    padrino = session.exec(
        select(Axolotito)
        .where(Axolotito.id == payload.padrino_axolotito_id)
        .where(Axolotito.user_id == verified_user_id)
    ).first()
    if not padrino:
        raise HTTPException(status_code=404, detail="Padrino no encontrado.")

    if padrino.is_frozen_by_vip:
        raise HTTPException(status_code=400, detail=f"{padrino.name} está congelado y no puede ser padrino.")
    if padrino.status == "sleeping":
        raise HTTPException(status_code=400, detail=f"{padrino.name} está durmiendo. Espera a que despierte.")


    # Verificar que el padrino no ya es padrino de otro webito
    already_padrino = session.exec(
        select(WebitoIncubation)
        .where(WebitoIncubation.imprinting_padrino_id == padrino.id)
        .where(WebitoIncubation.user_id == verified_user_id)
        .where(WebitoIncubation.imprinting_complete == False)
        .with_for_update()
    ).first()
    if already_padrino and already_padrino.id != incubation.id:
        raise HTTPException(
            status_code=400,
            detail=f"{padrino.name} ya está siendo padrino de otro Webito.",
        )

    # Generar stats base y asignar padrino
    base = initial_base_stats(padrino)
    incubation.base_stat_luck     = base["base_stat_luck"]
    incubation.base_stat_focus    = base["base_stat_focus"]
    incubation.base_stat_stamina  = base["base_stat_stamina"]
    incubation.base_stat_salinity = base["base_stat_salinity"]
    incubation.imprinting_padrino_id = padrino.id

    # Obtener rareza del huevo para saber cuántas partidas necesita
    egg_item = session.exec(
        select(ItemCatalog).where(ItemCatalog.id == incubation.item_id)
    ).first()
    required = required_games_for_rarity(egg_item.rarity) if egg_item else 3

    session.add(incubation)
    session.commit()
    session.refresh(incubation)

    return {
        "mensaje": f"¡Imprinting iniciado! Lleva a {padrino.name} a {required} partidas.",
        "incubation_id": incubation.id,
        "padrino": {"id": padrino.id, "name": padrino.name},
        "required_games": required,
        "games_played": 0,
    }


@router.get("/imprinting-status/{incubation_id}")
def imprinting_status(
    incubation_id: int,
    session: Session = Depends(get_session),
    verified_user_id: str = Depends(get_verified_user_id),
):
    """Estado actual del imprinting de un Webito."""
    incubation = session.exec(
        select(WebitoIncubation).where(WebitoIncubation.id == incubation_id)
    ).first()
    if not incubation or incubation.user_id != verified_user_id:
        raise HTTPException(status_code=404, detail="Incubación no encontrada.")

    egg_item = session.exec(
        select(ItemCatalog).where(ItemCatalog.id == incubation.item_id)
    ).first()
    required = required_games_for_rarity(egg_item.rarity) if egg_item else 3

    padrino_name = None
    if incubation.imprinting_padrino_id:
        padrino = session.exec(
            select(Axolotito).where(Axolotito.id == incubation.imprinting_padrino_id)
        ).first()
        padrino_name = padrino.name if padrino else None

    return {
        "incubation_id": incubation.id,
        "imprinting_started": incubation.imprinting_padrino_id is not None,
        "imprinting_complete": incubation.imprinting_complete,
        "games_played": incubation.imprinting_games_played,
        "required_games": required,
        "padrino_name": padrino_name,
        "current_stats": {
            "suerte_delta": round(incubation.bonus_luck, 1),
            "ojo_delta":    round(incubation.bonus_focus, 1),
            "pila_delta":   round(incubation.bonus_stamina, 1),
            "sal_delta":    round(incubation.bonus_salinity_adj, 1),
        } if incubation.imprinting_padrino_id is not None else None,
    }