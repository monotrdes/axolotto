import json
import random
_rng = random.SystemRandom()
from collections import Counter
from datetime import datetime, timedelta
from sqlmodel import Session, select, func
from fastapi import HTTPException
from app.core.config import settings, VIP_CONFIG, axf_to_display, frj_to_display, axf_to_internal, frj_to_internal
from app.core.product_policy import require_feature
from app.core.account_policy import require_account_capability
from app.models.items import ItemCatalog, PlayerInventory, ItemType
from app.models.economy import Wallet, CurrencyType, TransactionType, TransactionLedger
from app.services.bank_service import BankService
from app.services.web3_service import Web3Service
from app.models.user import User
from app.models.axolotito import Axolotito
import logging
logger = logging.getLogger("shop_service")

# --- CATEGORÍAS TEMÁTICAS DE CARTAS PARA SOBRES ---
FIESTA_CARDS = {
    "El axolotl", "El diablito", "La Patrona", "El Godín", "La piñata", "La sirena",
    "La botella", "El Chilaquil", "El luchador", "La catrina", "La chancla", "La caguama",
    "El músico", "El taco", "La chalupa", "La Botarga", "El cantarito", "El Acordeón"
}

NIDO_CARDS = {
    "El Trompo", "El molcajete", "El aguacate", "El sombrero", "El maíz", "La bandera",
    "El firulais", "El Michi", "El colibrí", "El café", "El camarón", "La araña",
    "La concha", "El nopal", "El alacrán", "La rosa", "La maceta", "El Elote"
}

COSMOS_CARDS = {
    "La mano", "Los Tenis", "La luna", "El corazón", "La salsa", "El Chamoy",
    "El papel picado", "El alebrije", "La estrella", "El mundo", "La calavera", "La campana",
    "El venado", "El sol", "El penacho", "El vocho", "El pescado", "La Cobija"
}


class ShopService:

    @staticmethod
    def buy_item(session: Session, user_id: str, item_id: int, payment_currency: CurrencyType):
        require_feature(settings.ENABLE_FIXED_ITEM_SHOP, "fixed_item_shop")
        # 1. Buscar al usuario
        user = session.exec(select(User).where(User.privy_did == user_id)).first()
        if not user:
            raise HTTPException(status_code=400, detail="Usuario no encontrado.")

        if payment_currency in (CurrencyType.AXOGEMA, CurrencyType.AXOFICHA):
            require_account_capability(user, "can_purchase")

        # 1b. Verificar tutorial completado
        from app.core.auth import require_tutorial
        require_tutorial(user)

        # 2. Verificar que el item existe y bloquearlo con SELECT FOR UPDATE
        item = session.exec(
            select(ItemCatalog).where(ItemCatalog.id == item_id).with_for_update()
        ).first()
        if not item or not item.is_active:
            raise HTTPException(status_code=404, detail="El item no está disponible en la tienda.")

        if item.item_type == ItemType.CURRENCY_PACK:
            raise HTTPException(
                status_code=403,
                detail="La compra de Frijolitos con Axofichas está deshabilitada por motivos regulatorios."
            )

        # 3a. Desvío especial: compra de Pase VIP (no requiere wallet Web3)
        _meta = item.item_metadata or {}
        if _meta.get("is_vip") and _meta.get("vip_tier"):
            require_feature(settings.ENABLE_VIP_SALES, "vip_sales")
            wallet = BankService.get_or_create_wallet(session, user_id, for_update=True)
            return ShopService._handle_vip_purchase(session, user, wallet, item)

        if item.item_type in (ItemType.BOOSTER, ItemType.EGG):
            require_feature(
                settings.ENABLE_PURCHASED_RANDOM_REWARDS,
                "purchased_random_rewards",
            )

        # Para el resto de items sí se requiere wallet Web3 (NFTs).
        # Las decoraciones de cueva no son NFT: viven solo en PlayerInventory.
        if not user.wallet_address and item.item_type != ItemType.CAVE_ITEM:
            raise HTTPException(status_code=400, detail="Necesitas vincular una wallet Web3 para comprar NFTs.")

        # 3. Verificar Stock Global (Max Supply)
        metadata = item.item_metadata or {}
        if metadata.get("is_astral"):
            from datetime import datetime
            now = datetime.utcnow()
            start_of_year = datetime(now.year, 1, 1)
            annual_sold = session.exec(
                select(func.count(TransactionLedger.id))
                .where(TransactionLedger.item_id == item.id)
                .where(TransactionLedger.created_at >= start_of_year)
            ).one_or_none() or 0
            
            if annual_sold >= 100:
                item.is_active = False
                session.add(item)
                session.commit()
                raise HTTPException(status_code=400, detail="¡Sold Out! Se ha agotado el cupo anual de 100 Webitos Astrales.")
            total_sold = annual_sold
        elif (item.item_type == ItemType.BOOSTER) or item.item_type == ItemType.EGG:
            total_sold = session.exec(
                select(func.count(TransactionLedger.id))
                .where(TransactionLedger.item_id == item.id)
            ).one_or_none() or 0
        else:
            total_sold = session.exec(
                select(func.sum(PlayerInventory.quantity)).where(PlayerInventory.item_id == item_id)
            ).one_or_none() or 0

        if not metadata.get("is_astral") and item.max_supply and total_sold >= item.max_supply:
            item.is_active = False 
            session.add(item)
            session.commit()

            # --- TRANSICIÓN AUTOMÁTICA DE FASE ---
            metadata = item.item_metadata or {}
            current_fase = metadata.get("fase")
            if current_fase in [1, 2] and not metadata.get("is_astral"):
                next_fase = current_fase + 1
                all_candidates = session.exec(
                    select(ItemCatalog).where(ItemCatalog.item_type == item.item_type)
                ).all()
                for cand in all_candidates:
                    cand_metadata = cand.item_metadata or {}
                    if cand_metadata.get("fase") == next_fase:
                        cand.is_active = True
                        session.add(cand)
                        session.commit()
                        print(f"🔄 [TIENDA] Transición automática: '{item.name}' agotado. Activada Fase {next_fase}: '{cand.name}'.")
                        break

            raise HTTPException(status_code=400, detail="¡Sold Out! Este item se ha agotado globalmente.")

        # 4a. Verificar Límite por Usuario por Ítem (max_per_user, anti-ballena)
        if item.max_per_user:
            user_owned_count = session.exec(
                select(func.sum(PlayerInventory.quantity))
                .where(PlayerInventory.user_id == user_id)
                .where(PlayerInventory.item_id == item_id)
            ).first() or 0
            if user_owned_count >= item.max_per_user:
                raise HTTPException(
                    status_code=400,
                    detail=f"Límite de {item.max_per_user} unidades por wallet alcanzado para este ítem."
                )

        # 4. Verificar Límite por Usuario (Anti-Whale)
        if item.item_type == ItemType.BOOSTER:
            user_purchased = session.exec(
                select(func.count(TransactionLedger.id))
                .where(TransactionLedger.user_id == user_id)
                .where(TransactionLedger.tx_type == TransactionType.BOOSTER_PURCHASE)
            ).one_or_none() or 0
            
            if user_purchased >= 100:
                raise HTTPException(status_code=400, detail="Límite de preventa alcanzado (100 sobres).")
        else:
            if item.item_type == ItemType.EGG:
                # Contar huevos (webitos) actualmente en el inventario
                total_eggs = session.exec(
                    select(func.sum(PlayerInventory.quantity))
                    .join(ItemCatalog, PlayerInventory.item_id == ItemCatalog.id)
                    .where(PlayerInventory.user_id == user_id)
                    .where(ItemCatalog.item_type == ItemType.EGG)
                ).one_or_none() or 0

                # Contar axolotitos ya eclosionados (también ocupan un nido/dormitorio)
                total_axolotitos = session.exec(
                    select(func.count(Axolotito.id))
                    .where(Axolotito.user_id == user_id)
                ).one_or_none() or 0

                # Calcular nidos totales del Cenote: cave_level + 6 base (7 slots en Nv1, 14 en Nv8)
                from app.api.v1.endpoints.cave_expansion import CAVE_PASSIVE_BONUSES
                bonus_slots = 0
                for lvl in range(1, user.cave_level + 1):
                    bonus = CAVE_PASSIVE_BONUSES.get(lvl, {})
                    bonus_slots += bonus.get("global_incubation_slot", 0)
                max_incubation_slots = user.cave_level + bonus_slots

                # Cada nido puede tener UN ocupante: huevo en incubación O axolotito en dormitorio
                occupied_nests = total_eggs + total_axolotitos
                if occupied_nests >= max_incubation_slots:
                    raise HTTPException(
                        status_code=400,
                        detail=f"No tienes nidos disponibles. Tienes {total_axolotitos} axolotito(s) y {total_eggs} huevo(s) ocupando los {max_incubation_slots} nido(s) de tu Cenote. Expande el Cenote para obtener más espacio."
                    )

                # Verificar límite total (VIP puede tener bonus separado)
                user_owned = total_eggs + total_axolotitos
                axo_limit = user.cave_level + user.vip_bonus_axolotito_slots
                if user_owned >= axo_limit:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Límite alcanzado. Ya tienes {user_owned} webitos/axolotitos (límite: {axo_limit}). Expande tu Cenote para tener más espacio."
                    )
            else:
                user_owned = session.exec(
                    select(func.sum(PlayerInventory.quantity))
                    .where(PlayerInventory.user_id == user_id)
                    .where(PlayerInventory.item_id == item_id)
                ).one_or_none() or 0

        # 5. Validar Saldo y Cobrar
        if item.item_type == ItemType.CURRENCY_PACK:
            raise HTTPException(
                status_code=403,
                detail="La compra de Frijolitos con Axofichas está deshabilitada por motivos regulatorios."
            )

        wallet = BankService.get_or_create_wallet(session, user_id)
        price = item.price_axg if payment_currency in (CurrencyType.AXOGEMA, CurrencyType.AXOFICHA) else item.price_gal

        if not price:
            raise HTTPException(status_code=400, detail="Este item no se puede comprar con esa moneda.")

        # Descuento VIP (solo en AXF, excluye Webitos) — VULN-06: aritmética entera
        if payment_currency in (CurrencyType.AXOGEMA, CurrencyType.AXOFICHA) and user.is_vip and user.vip_tier and item.item_type not in [ItemType.EGG]:
            discount_bps = VIP_CONFIG.get(user.vip_tier, {}).get("discount_bps", 0)
            if discount_bps:
                price = price * (10000 - discount_bps) // 10000

        current_balance = wallet.axofichas if payment_currency in (CurrencyType.AXOGEMA, CurrencyType.AXOFICHA) else wallet.frijolitos
        
        if current_balance < price:
            raise HTTPException(status_code=400, detail=f"Saldo insuficiente de {payment_currency.value}.")

        # 6. Ejecutar Cobro y Entrega
        try:
            # Re-lock de wallet bajo transacción para prevenir double-spend concurrente.
            # Es necesario hacerlo aquí porque el flujo anterior puede tener commits
            # intermedios (transiciones de fase) que liberarían un lock anterior.
            wallet = session.exec(
                select(Wallet).where(Wallet.user_id == user_id).with_for_update()
            ).first()
            current_balance = wallet.axofichas if payment_currency in (CurrencyType.AXOGEMA, CurrencyType.AXOFICHA) else wallet.frijolitos
            if current_balance < price:
                raise HTTPException(status_code=402, detail=f"Saldo insuficiente de {payment_currency.value}.")

            # Descontar dinero
            if payment_currency in (CurrencyType.AXOGEMA, CurrencyType.AXOFICHA):
                wallet.axofichas -= price
                if user.wallet_address and settings.AXOGEMA_ADDRESS:
                    try:
                        Web3Service.burn_axofichas(user.wallet_address, price)
                    except Exception as e:
                        logger.error("Error al quemar AXF on-chain: %s", e)
            else:
                wallet.frijolitos -= price
                if user.wallet_address and settings.GEMA_ALGA_ADDRESS:
                    try:
                        Web3Service.burn_frj(user.wallet_address, price)
                    except Exception as e:
                        logger.error("Error al quemar FRJ on-chain: %s", e)

            # --- CURRENCY PACK: intercambio AXF → FRJ ---
            if item.item_type == ItemType.CURRENCY_PACK:
                frj_reward = int((item.item_metadata or {}).get("gal_amount", 0))
                wallet.frijolitos += frj_reward

                if user.wallet_address and settings.GEMA_ALGA_ADDRESS:
                    try:
                        Web3Service.mint_frj(user.wallet_address, frj_reward)
                    except Exception as e:
                        logger.error("Error al acuñar FRJ on-chain: %s", e)

                ledger = TransactionLedger(
                    user_id=user_id, amount=price, currency=payment_currency,
                    tx_type=TransactionType.MARKET_BUY,
                    description=f"Intercambio de AXF por {frj_reward} Frijolitos",
                    item_id=item.id
                )
                session.add(wallet)
                session.add(ledger)
                session.commit()

                return {
                    "mensaje": f"¡Intercambio completado! Recibiste {int(frj_reward)} FRJ en tu cuenta.",
                    "item_id": item.id,
                    "tipo": "currency_exchange"
                }

            es_fase_1 = (item.item_type == ItemType.BOOSTER)
            
            if es_fase_1:
                # --- ENTREGA DE BOOSTER SELLADO ---
                metadata = item.item_metadata or {}
                pack_theme = metadata.get("pack_theme", "pure")

                # 1. Enforce monthly limit of 100 on Booster Brillante (Foil)
                if pack_theme == "foil":
                    from datetime import datetime
                    now = datetime.utcnow()
                    start_of_month = datetime(now.year, now.month, 1)
                    monthly_sold = session.exec(
                        select(func.count(TransactionLedger.id))
                        .where(TransactionLedger.item_id == item.id)
                        .where(TransactionLedger.created_at >= start_of_month)
                    ).one_or_none() or 0
                    if monthly_sold >= 100:
                        raise HTTPException(
                            status_code=400, 
                            detail="¡Límite mensual alcanzado! Solo se pueden vender 100 Boosters Brillantes al mes globalmente."
                        )

                inv_item = session.exec(
                    select(PlayerInventory)
                    .where(PlayerInventory.user_id == user_id)
                    .where(PlayerInventory.item_id == item.id)
                ).first()

                if inv_item:
                    inv_item.quantity += 1
                else:
                    inv_item = PlayerInventory(
                        user_id=user_id,
                        item_id=item.id,
                        quantity=1,
                        is_first_edition=metadata.get("fase", 1) == 1,
                        is_shiny=False
                    )
                session.add(inv_item)

                # Acuñar el sobrecito on-chain (fase = sobrecito_id en ERC-1155)
                booster_fase = metadata.get("fase", 1)
                tx_hash = "0x_mock_sobrecito_tx"
                if user.wallet_address:
                    try:
                        tx_hash = Web3Service.mint_sobrecito_onchain(user.wallet_address, sobrecito_id=booster_fase, amount=1)
                    except Exception as e:
                        logger.error("Error al acuñar Sobrecito on-chain: %s", e)

                ledger = TransactionLedger(
                    user_id=user_id, amount=price, currency=payment_currency,
                    tx_type=TransactionType.BOOSTER_PURCHASE,
                    description=f"Compra de sobre sellado de {item.name}",
                    item_id=item.id
                )
                session.add(wallet)
                session.add(ledger)

                # --- TRANSICIÓN PROACTIVA SI SE ALCANZA EL LÍMITE ---
                if item.max_supply and (total_sold + 1) >= item.max_supply:
                    item.is_active = False
                    session.add(item)
                    
                    current_fase = metadata.get("fase")
                    if current_fase in [1, 2] and not metadata.get("is_astral"):
                        next_fase = current_fase + 1
                        all_candidates = session.exec(
                            select(ItemCatalog).where(ItemCatalog.item_type == item.item_type)
                        ).all()
                        for cand in all_candidates:
                            cand_metadata = cand.item_metadata or {}
                            if cand_metadata.get("fase") == next_fase:
                                cand.is_active = True
                                session.add(cand)
                                print(f"🔄 [TIENDA] Transición automática proactiva: '{item.name}' agotado. Activada Fase {next_fase}: '{cand.name}'.")
                                break

                session.commit()

                return {
                    "mensaje": f"¡Compraste un sobre sellado de {item.name}! Se ha guardado en tu mochila.",
                    "item_id": item.id,
                    "tipo": "sealed_booster",
                    "tx_hash": tx_hash
                }

            else:
                # --- COMPRA DE UPGRADE (BOARD SLOTS) ---
                if (item.item_metadata or {}).get("is_upgrade"):
                    user.unlocked_board_slots = (user.unlocked_board_slots or 3) + 1
                    session.add(user)
                    
                    ledger = TransactionLedger(
                        user_id=user_id, amount=price, currency=payment_currency,
                        tx_type=TransactionType.MARKET_BUY,
                        description=f"Compra de Upgrade: {item.name}. Total slots: {user.unlocked_board_slots}",
                        item_id=item.id
                    )
                    session.add(wallet)
                    session.add(ledger)
                    session.commit()
                    
                    return {
                        "mensaje": f"¡Compra completada! Tu espacio de tablas ha aumentado a {user.unlocked_board_slots}.",
                        "item_id": item.id,
                        "tipo": "upgrade_board_slots"
                    }

                # --- COMPRA NORMAL (WEBITOS) ---
                tx_hash = ""
                if item.item_type == ItemType.EGG:
                    tx_hash = Web3Service.mint_webito_onchain(user.wallet_address)

                inv_item = session.exec(
                    select(PlayerInventory)
                    .where(PlayerInventory.user_id == user_id)
                    .where(PlayerInventory.item_id == item_id)
                ).first()

                if inv_item:
                    inv_item.quantity += 1
                else:
                    inv_item = PlayerInventory(user_id=user_id, item_id=item_id, quantity=1)
                
                ledger = TransactionLedger(
                    user_id=user_id, amount=price, currency=payment_currency, 
                    tx_type=TransactionType.MARKET_BUY, description=f"Compra de {item.name}",
                    item_id=item.id
                )

                session.add(wallet)
                session.add(inv_item)
                session.add(ledger)
                
                # --- TRANSICIÓN PROACTIVA SI SE ALCANZA EL LÍMITE ---
                if item.max_supply and (total_sold + 1) >= item.max_supply:
                    item.is_active = False
                    session.add(item)
                    
                    metadata = item.item_metadata or {}
                    current_fase = metadata.get("fase")
                    if current_fase in [1, 2] and not metadata.get("is_astral"):
                        next_fase = current_fase + 1
                        all_candidates = session.exec(
                            select(ItemCatalog).where(ItemCatalog.item_type == item.item_type)
                        ).all()
                        for cand in all_candidates:
                            cand_metadata = cand.item_metadata or {}
                            if cand_metadata.get("fase") == next_fase:
                                cand.is_active = True
                                session.add(cand)
                                print(f"🔄 [TIENDA] Transición automática proactiva: '{item.name}' agotado. Activada Fase {next_fase}: '{cand.name}'.")
                                break
                
                session.commit()
                
                return {
                    "mensaje": f"Has comprado {item.name} con éxito.",
                    "item_id": item.id,
                    "tx_blockchain": tx_hash,
                    "tipo": "normal"
                }

        except HTTPException:
            session.rollback()
            raise
        except Exception as e:
            session.rollback()
            raise HTTPException(status_code=500, detail=f"Error en la compra: {str(e)}")

    # -------------------------------------------------------------------------
    # VIP PURCHASE
    # -------------------------------------------------------------------------

    @staticmethod
    def _handle_vip_purchase(session: Session, user: User, wallet: Wallet, item: ItemCatalog):
        tier = (item.item_metadata or {}).get("vip_tier")
        config = VIP_CONFIG.get(tier)
        if not config:
            raise HTTPException(status_code=400, detail="Tier VIP inválido.")

        base_price = int(config["price_axg"])

        # Crédito proporcional si ya tiene VIP activo y está subiendo de nivel
        credit_axg = 0
        if user.is_vip and user.vip_tier and user.vip_tier != tier:
            current_config = VIP_CONFIG.get(user.vip_tier, {})
            days_left = max((user.vip_expires_at - datetime.utcnow()).days, 0)
            daily_rate = current_config.get("price_axg", 0) // 30  # VULN-06: división entera
            credit_axg = min(daily_rate * days_left, base_price - 1)

        final_price = base_price - credit_axg

        if wallet.axofichas < final_price:
            raise HTTPException(
                status_code=400,
                detail=f"Saldo insuficiente. Necesitas {axf_to_display(final_price):.1f} AXF"
                       + (f" (con crédito de {axf_to_display(credit_axg):.1f} AXF por días restantes)" if credit_axg else "") + "."
            )

        wallet.axofichas -= final_price

        # Actualizar vip_expires_at (apilar días si es el mismo tier, reiniciar si cambia)
        base_date = max(user.vip_expires_at, datetime.utcnow()) if user.is_vip and user.vip_tier == tier else datetime.utcnow()
        user.vip_tier = tier
        user.vip_expires_at = base_date + timedelta(days=30)

        # Racha — solo incrementa si es una renovación de mes nuevo, no un upgrade del mismo período
        from datetime import timezone
        mx_tz = timezone(timedelta(hours=-6))
        now_mx = datetime.now(timezone.utc).astimezone(mx_tz)
        now = datetime.utcnow()
        if user.vip_streak_last_renewed:
            last_renewed_mx = user.vip_streak_last_renewed.replace(tzinfo=timezone.utc).astimezone(mx_tz)
            days_since = (now_mx - last_renewed_mx).days
            if days_since < 27:
                pass  # mismo período de facturación (upgrade): no tocar streak ni last_renewed
            elif days_since <= 63:
                user.vip_streak_months += 1  # renovación a tiempo
                user.vip_streak_last_renewed = now
            else:
                user.vip_streak_months = 1  # se fue y volvió: reiniciar
                user.vip_streak_last_renewed = now
        else:
            user.vip_streak_months = 1  # primera activación
            user.vip_streak_last_renewed = now

        # Cápsulas mensuales VIP
        capsulas_mensuales = config.get("capsulas_mensuales", {})
        if capsulas_mensuales:
            all_consumables = session.exec(
                select(ItemCatalog).where(ItemCatalog.item_type == ItemType.CONSUMABLE)
            ).all()
            for capsule_tier, qty in capsulas_mensuales.items():
                capsule_item = next(
                    (c for c in all_consumables if (c.item_metadata or {}).get("capsule_tier") == capsule_tier),
                    None
                )
                if capsule_item:
                    inv = session.exec(
                        select(PlayerInventory)
                        .where(PlayerInventory.user_id == user.privy_did)
                        .where(PlayerInventory.item_id == capsule_item.id)
                    ).first()
                    if inv:
                        inv.quantity += qty
                    else:
                        inv = PlayerInventory(user_id=user.privy_did, item_id=capsule_item.id, quantity=qty)
                    session.add(inv)

        # Bono de bienvenida (solo primera activación de este tier)
        tiers_activated = json.loads(user.vip_tiers_activated or "[]")
        is_first_activation = tier not in tiers_activated
        welcome_frj = 0
        if is_first_activation:
            welcome_frj = int(config.get("welcome_gal", 0))
            if welcome_frj > 0:
                wallet.frijolitos += welcome_frj

            # Entregar sobrecitos de bienvenida
            welcome_boosters = config.get("welcome_boosters", [])
            for b_type in welcome_boosters:
                sobrecito_name = "Sobrecito Brillante (Foil)" if b_type == "foil" else "Sobrecito Mezclado"
                target_booster = session.exec(
                    select(ItemCatalog)
                    .where(ItemCatalog.name == sobrecito_name)
                    .where(ItemCatalog.item_type == ItemType.BOOSTER)
                ).first()
                if target_booster:
                    inv_booster = session.exec(
                        select(PlayerInventory)
                        .where(PlayerInventory.user_id == user.privy_did)
                        .where(PlayerInventory.item_id == target_booster.id)
                    ).first()
                    if inv_booster:
                        inv_booster.quantity += 1
                    else:
                        inv_booster = PlayerInventory(
                            user_id=user.privy_did,
                            item_id=target_booster.id,
                            quantity=1
                        )
                    session.add(inv_booster)
            
            tiers_activated.append(tier)
            user.vip_tiers_activated = json.dumps(tiers_activated)

        # Ledger
        desc = f"Activación Pase VIP {tier.capitalize()} (30 días)"
        if credit_axg > 0:
            desc += f" — crédito upgrade: {axf_to_display(credit_axg):.1f} AXF"
        ledger = TransactionLedger(
            user_id=user.privy_did, amount=final_price, currency=CurrencyType.AXOFICHA,
            tx_type=TransactionType.MARKET_BUY, description=desc,
            item_id=item.id
        )

        session.add(user)
        session.add(wallet)
        session.add(ledger)
        session.commit()

        response = {
            "mensaje": f"¡Bienvenido al VIP {tier.capitalize()}! Tu suscripción vence el {user.vip_expires_at.strftime('%d/%m/%Y')}.",
            "vip_tier": tier,
            "vip_expires_at": user.vip_expires_at.isoformat(),
            "credit_applied_axg": axf_to_display(credit_axg),
            "tipo": "vip_activation",
        }
        if is_first_activation and welcome_frj > 0:
            response["welcome_frj_bonus"] = frj_to_display(welcome_frj)
        return response

    @staticmethod
    def get_vip_tiers() -> list[dict]:
        """
        Devuelve los tiers VIP ordenados coral → dorado → axolite con las claves
        del contrato público. Traduce las claves legacy del VIP_CONFIG interno:
          price_axg  → price_axf
          gal_daily  → frj_daily
          welcome_gal → welcome_frj
        y calcula frj_monthly = frj_daily * 30.
        """
        ORDER = ["coral", "dorado", "axolite"]
        result = []
        for tier_id in ORDER:
            cfg = VIP_CONFIG.get(tier_id)
            if cfg is None:
                continue
            frj_daily = frj_to_display(cfg["gal_daily"])
            result.append({
                "id": tier_id,
                "price_axf": axf_to_display(cfg["price_axg"]),
                "frj_daily": frj_daily,
                "frj_monthly": frj_daily * 30.0,
                "discount": cfg["discount"],
                "capsulas_mensuales": cfg["capsulas_mensuales"],
                "p2p_commission": cfg["p2p_commission"],
                "table_bonus_slots": cfg["table_bonus_slots"],
                "axolotito_bonus_slots": cfg["axolotito_bonus_slots"],
                "jackpot_bonus": cfg["jackpot_bonus"],
                "multiplayer_discount": cfg["multiplayer_discount"],
                "welcome_frj": frj_to_display(cfg["welcome_gal"]),
                "welcome_boosters": cfg["welcome_boosters"],
                "popular": cfg.get("popular", False),
            })
        return result

    @staticmethod
    def get_vip_upgrade_preview(session: Session, user: User, target_tier: str) -> dict:
        """Calcula el precio de upgrade a un tier VIP sin cobrar nada."""
        config = VIP_CONFIG.get(target_tier)
        if not config:
            raise HTTPException(status_code=400, detail="Tier VIP inválido.")

        base_price = int(config["price_axg"])
        credit_axg = 0
        days_left = 0

        if user.is_vip and user.vip_tier and user.vip_tier != target_tier:
            current_config = VIP_CONFIG.get(user.vip_tier, {})
            days_left = max((user.vip_expires_at - datetime.utcnow()).days, 0)
            daily_rate = current_config.get("price_axg", 0) // 30  # VULN-06: división entera
            credit_axg = min(daily_rate * days_left, base_price - 1)

        new_expires = datetime.utcnow() + timedelta(days=30)

        return {
            "current_tier": user.vip_tier,
            "current_expires_at": user.vip_expires_at.isoformat() if user.vip_expires_at else None,
            "days_remaining": days_left,
            "credit_axg": axf_to_display(credit_axg),
            "target_tier": target_tier,
            "base_price_axg": axf_to_display(base_price),
            "final_price_axg": axf_to_display(base_price - credit_axg),
            "new_expires_at": new_expires.isoformat(),
        }

    @staticmethod
    def open_booster(session: Session, user_id: str, item_id: int):
        require_feature(
            settings.ENABLE_PURCHASED_RANDOM_REWARDS,
            "purchased_random_rewards",
        )
        # 1. Buscar al usuario
        user = session.exec(select(User).where(User.privy_did == user_id)).first()
        if not user:
            raise HTTPException(status_code=400, detail="Usuario no encontrado.")

        # 1b. Verificar tutorial completado
        from app.core.auth import require_tutorial
        require_tutorial(user)

        # 2. Lock inventory row using SELECT FOR UPDATE to prevent race conditions
        inv_item = session.exec(
            select(PlayerInventory)
            .where(PlayerInventory.user_id == user_id)
            .where(PlayerInventory.item_id == item_id)
            .where(PlayerInventory.quantity > 0)
            .with_for_update()
        ).first()

        if not inv_item:
            raise HTTPException(status_code=400, detail="No tienes este booster en tu inventario.")

        # 3. Verificar que el item existe en catálogo y es un booster
        item = session.get(ItemCatalog, item_id)
        if not item or item.item_type != ItemType.BOOSTER:
            raise HTTPException(status_code=400, detail="El ítem especificado no es un booster válido.")

        # 4. Consumir el booster del inventario
        inv_item.quantity -= 1
        if inv_item.quantity <= 0:
            session.delete(inv_item)
        else:
            session.add(inv_item)

        # 5. Quemar el sobrecito on-chain (usando la fase como tokenId)
        metadata = item.item_metadata or {}
        booster_fase = metadata.get("fase", 1)
        tx_burn_hash = "0x_mock_burn_tx"
        if user.wallet_address:
            try:
                tx_burn_hash = Web3Service.burn_sobrecito_onchain(user.wallet_address, sobrecito_id=booster_fase, amount=1)
            except Exception as e:
                logger.error("Error al quemar Sobrecito on-chain: %s", e)

        # 6. Generar las 7 cartas únicas
        pack_theme = metadata.get("pack_theme", "pure")
        cartas_entregadas_nombres = []
        ids_to_mint_onchain = []
        todas_las_cartas = session.exec(select(ItemCatalog).where(ItemCatalog.item_type == ItemType.CARD)).all()
        
        # Filtrar cartas según temática del sobre
        if pack_theme == "fiesta":
            todas_las_cartas = [c for c in todas_las_cartas if c.name in FIESTA_CARDS]
        elif pack_theme == "nido":
            todas_las_cartas = [c for c in todas_las_cartas if c.name in NIDO_CARDS]
        elif pack_theme == "cosmos":
            todas_las_cartas = [c for c in todas_las_cartas if c.name in COSMOS_CARDS]
        
        # Fallback a todas si queda vacío
        if not todas_las_cartas or len(todas_las_cartas) < 7:
            todas_las_cartas = session.exec(select(ItemCatalog).where(ItemCatalog.item_type == ItemType.CARD)).all()

        is_fe = (booster_fase == 1)

        # Seleccionar 7 cartas únicas (Duplicate Prevention)
        cartas_ganadas = _rng.sample(todas_las_cartas, 7)
        cartas_shiny_flags = []

        # Determinar shiny flags
        if pack_theme == "foil":
            cartas_shiny_flags = [True, True, True, True, True, False, False]
        elif is_fe:
            cartas_shiny_flags = [_rng.random() < 0.15 for _ in range(7)]
        else:
            has_shiny = _rng.random() < 0.20
            cartas_shiny_flags = [False] * 7
            if has_shiny:
                shiny_idx = _rng.randint(0, 6)
                cartas_shiny_flags[shiny_idx] = True

        # Guardar en inventario
        for idx, carta_ganada in enumerate(cartas_ganadas):
            is_shiny = cartas_shiny_flags[idx]

            inv_card = session.exec(
                select(PlayerInventory)
                .where(PlayerInventory.user_id == user_id)
                .where(PlayerInventory.item_id == carta_ganada.id)
                .where(PlayerInventory.is_first_edition == is_fe)
                .where(PlayerInventory.is_shiny == is_shiny)
            ).first()

            if inv_card:
                inv_card.quantity += 1
            else:
                inv_card = PlayerInventory(
                    user_id=user_id,
                    item_id=carta_ganada.id,
                    quantity=1,
                    is_first_edition=is_fe,
                    is_shiny=is_shiny
                )
            session.add(inv_card)
            cartas_entregadas_nombres.append(carta_ganada.name)
            ids_to_mint_onchain.append(carta_ganada.id)

        # Get dynamic rarities
        from app.services.rarity_service import get_card_dynamic_rarities
        dynamic_rarities = get_card_dynamic_rarities(session)

        cards_payload = []
        for idx, c in enumerate(cartas_ganadas):
            is_shiny = cartas_shiny_flags[idx]
            dyn_rar = dynamic_rarities.get(c.id, {}).get("dynamic_rarity", "Común")
            cards_payload.append({
                "id": c.id,
                "name": c.name,
                "rarity": c.rarity,
                "dynamic_rarity": dyn_rar,
                "is_shiny": is_shiny,
                "is_first_edition": is_fe,
                "item_metadata": c.item_metadata
            })

        # Acuñar las cartas on-chain
        conteo = Counter(ids_to_mint_onchain)
        tx_mint_hash = "0x_mock_mint_tx"
        if user.wallet_address:
            try:
                tx_mint_hash = Web3Service.mint_cards_onchain(user.wallet_address, list(conteo.keys()), list(conteo.values()))
            except Exception as e:
                logger.error("Error al acuñar cartas on-chain: %s", e)

        # Ledger de la apertura
        ledger = TransactionLedger(
            user_id=user_id,
            amount=0,
            currency=CurrencyType.GEMA_ALGA, # Dummy currency type since it's an unboxing
            tx_type=TransactionType.BURN,
            description=f"Apertura diferida de Booster: {item.name}",
            item_id=item.id
        )
        session.add(ledger)
        session.commit()

        return {
            "mensaje": f"¡Sobre abierto! Conseguiste: {', '.join(cartas_entregadas_nombres)}",
            "tx_burn_blockchain": tx_burn_hash,
            "tx_mint_blockchain": tx_mint_hash,
            "tipo": "deferred_open",
            "shiny_flags": cartas_shiny_flags,
            "cards": cards_payload
        }
