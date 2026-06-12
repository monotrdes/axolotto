from sqlmodel import Session, select, func
from app.models.items import ItemCatalog, ItemType, PlayerInventory

def get_card_dynamic_rarities(session: Session) -> dict:
    """
    Calcula la rareza dinámica y la circulación global para todas las cartas
    de la Lotería de manera en tiempo real, resolviendo empates a favor del nivel
    de rareza más exclusivo.
    
    Retorna un diccionario: { card_id: { "dynamic_rarity": str, "circulation": int } }
    """
    # 1. Obtener todas las cartas del catálogo maestro
    cards = session.exec(
        select(ItemCatalog)
        .where(ItemCatalog.item_type == ItemType.CARD)
        .order_by(ItemCatalog.id)
    ).all()
    
    if not cards:
        return {}
        
    # 2. Obtener la cantidad total en circulación por item_id (en inventario de jugadores reales)
    circ_query = (
        select(PlayerInventory.item_id, func.sum(PlayerInventory.quantity))
        .where(PlayerInventory.user_id != "npc_axolotto_system")
        .group_by(PlayerInventory.item_id)
    )
    circ_results = session.exec(circ_query).all()
    circ_map = {item_id: int(total_qty) for item_id, total_qty in circ_results if total_qty is not None}
    
    # 2b. Obtener la cantidad de copias colocadas en tableros activos (tanto de jugadores como de bots)
    from app.models.board import PlayerBoard
    boards = session.exec(
        select(PlayerBoard)
        .where(PlayerBoard.is_dead == False)
    ).all()
    
    board_card_counts = {}
    for board in boards:
        if board.card_ids:
            for cid in board.card_ids:
                board_card_counts[cid] = board_card_counts.get(cid, 0) + 1
                
    # 3. Mapear cada carta a su cantidad en circulación actual (Inventario + Tableros)
    card_circulations = []
    for c in cards:
        qty_inventory = circ_map.get(c.id, 0)
        qty_boards = board_card_counts.get(c.id, 0)
        total_qty = qty_inventory + qty_boards
        card_circulations.append((c.id, total_qty))
        
    # 4. Ordenar las cartas por circulación de menor a mayor (más escasas primero)
    card_circulations.sort(key=lambda x: x[1])
    
    # 5. Definir percentiles de asignación inicial por índice
    total_cards = len(card_circulations)
    limit_legendary = max(1, int(total_cards * 0.05))                 # Escasísimo 5%
    limit_epic = limit_legendary + max(1, int(total_cards * 0.10))      # Siguiente 10%
    limit_rare = limit_epic + max(1, int(total_cards * 0.20))          # Siguiente 20%
    limit_uncommon = limit_rare + max(1, int(total_cards * 0.30))      # Siguiente 30%
    
    # Asignar rareza por posición inicial
    rarities = {}
    for idx, (cid, qty) in enumerate(card_circulations):
        if idx < limit_legendary:
            rarity = "Legendaria"
        elif idx < limit_epic:
            rarity = "Épica"
        elif idx < limit_rare:
            rarity = "Rara"
        elif idx < limit_uncommon:
            rarity = "Poco Común"
        else:
            rarity = "Común"
        rarities[cid] = {"rarity": rarity, "circulation": qty}

    # 6. Agrupar por circulación para resolver empates (Ties Resolution)
    # Si dos o más cartas tienen la misma circulación, comparten la rareza menos exclusiva
    # asignada a cualquiera de ellas en el ordenamiento inicial (resolución hacia abajo).
    circ_groups = {}
    for cid, qty in card_circulations:
        circ_groups.setdefault(qty, []).append(cid)
        
    rarity_order = ["Legendaria", "Épica", "Rara", "Poco Común", "Común"]
    
    for qty, group_cids in circ_groups.items():
        worst_rarity = "Legendaria"
        for cid in group_cids:
            current_r = rarities[cid]["rarity"]
            if rarity_order.index(current_r) > rarity_order.index(worst_rarity):
                worst_rarity = current_r
        # Asignar a todo el grupo de empate el nivel de rareza menos exclusivo
        for cid in group_cids:
            rarities[cid]["rarity"] = worst_rarity

    # Construir el mapa final
    final_map = {}
    for cid, data in rarities.items():
        final_map[cid] = {
            "dynamic_rarity": data["rarity"],
            "circulation": data["circulation"]
        }
    return final_map
