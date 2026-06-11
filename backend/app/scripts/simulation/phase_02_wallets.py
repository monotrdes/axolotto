from datetime import datetime

from sqlmodel import Session, select
from fastapi import HTTPException

from app.models.user import User
from app.models.economy import Wallet, CurrencyType, AxgPurchaseRecord
from app.models.items import ItemCatalog, ItemType
from app.services.bank_service import BankService
from app.services.shop_service import ShopService
from app.core.config import VIP_CONFIG, frj_to_internal, FRJ_DECIMALS_BACKEND, axf_to_internal

from sim_types import _rng


def phase_fund_wallets(engine, config, **state) -> dict:
    """
    Simula la compra de paquetes de AXG con pesos (MXN) para cada jugador
    según lo que requiere comprar en base a su personalidad, almacena los registros
    en la BD (equivalente en pesos) y activa el VIP de inmediato si corresponde,
    para que todos los consumos posteriores gocen del descuento VIP.
    """
    session: Session = state["session"]
    progress = state["progress"]
    players: list = state["players"]
    stats: dict = state["stats"]
    errors: list = state["errors"]

    progress("  💰 Simulando compra de paquetes de AXG (Pesos MXN) y fondeo de wallets...")

    # Buscar los items VIP en el catálogo
    vip_items = session.exec(
        select(ItemCatalog).where(
            ItemCatalog.is_active == True,
        )
    ).all()
    vip_catalog = {
        (item.item_metadata or {}).get("vip_tier"): item
        for item in vip_items
        if (item.item_metadata or {}).get("is_vip")
    }

    # Buscar los paquetes de FRJ (Frijolitos) en el catálogo
    frj_packs = session.exec(
        select(ItemCatalog).where(
            ItemCatalog.item_type == ItemType.CURRENCY_PACK,
            ItemCatalog.is_active == True,
        )
    ).all()

    for p in players:
        user_id = p["user_id"]
        personality = p["personality"]
        wallet = BankService.get_or_create_wallet(session, user_id)
        user = session.exec(select(User).where(User.privy_did == user_id)).first()

        # 1. Calcular AXG requerido para comprar todo lo planificado
        eggs_count = personality.get("eggs", 0)
        # Buscar el huevo activo en el catálogo para conocer su precio exacto
        egg_item = session.exec(
            select(ItemCatalog).where(
                ItemCatalog.item_type == ItemType.EGG,
                ItemCatalog.is_active == True,
            )
        ).first()
        egg_price = egg_item.price_axg if egg_item else 1200.0
        eggs_cost = eggs_count * egg_price

        vip_tier = personality.get("vip_tier")
        vip_cost = 0.0
        vip_discount = 0.0
        if vip_tier and vip_tier in vip_catalog:
            vip_cost = vip_catalog[vip_tier].price_axg
            vip_discount = VIP_CONFIG.get(vip_tier, {}).get("discount", 0.0)

        boosters_normal = personality.get("boosters_normal", 0)
        boosters_foil = personality.get("boosters_foil", 0)

        # Precios base en catálogo (usando aproximados/máximos para asegurar saldo)
        normal_price_base = 350.0
        foil_price_base = 800.0

        # Si compra VIP, sus boosters tendrán descuento "desde siempre"
        effective_normal = round(normal_price_base * (1.0 - vip_discount), 2)
        effective_foil = round(foil_price_base * (1.0 - vip_discount), 2)

        boosters_cost = (boosters_normal * effective_normal) + (boosters_foil * effective_foil)

        # Buffer para gal_packs, gashapon, tablas, etc.
        gameplay_buffer = 4000.0

        total_needed_axg = eggs_cost + vip_cost + boosters_cost + gameplay_buffer

        # 2. Simular compra de paquetes de AXG
        # Paquetes: 200x$35, 550x$88, 1725x$263 y 7250x$875
        AXG_PACKS = [
            {"axg": 7250, "price_mxn": 875.0, "name": "7250x$875"},
            {"axg": 1725, "price_mxn": 263.0, "name": "1725x$263"},
            {"axg": 550,  "price_mxn": 88.0,  "name": "550x$88"},
            {"axg": 200,  "price_mxn": 35.0,  "name": "200x$35"},
        ]

        current_obtained = 0.0
        mxn_spent = 0.0
        purchased_packs_counts = {}

        while current_obtained < total_needed_axg:
            remaining = total_needed_axg - current_obtained
            chosen_pack = None
            for pack in AXG_PACKS:
                if pack["axg"] <= remaining:
                    chosen_pack = pack
                    break
            if not chosen_pack:
                chosen_pack = AXG_PACKS[-1]  # el más pequeño si lo restante es menor a 200

            # Registrar compra en BD
            record = AxgPurchaseRecord(
                user_id=user_id,
                axg_amount=chosen_pack["axg"],
                mxn_amount=chosen_pack["price_mxn"],
                pack_name=chosen_pack["name"],
                created_at=datetime.utcnow()
            )
            session.add(record)

            current_obtained += chosen_pack["axg"]
            mxn_spent += chosen_pack["price_mxn"]
            purchased_packs_counts[chosen_pack["name"]] = purchased_packs_counts.get(chosen_pack["name"], 0) + 1

        session.commit()

        # Actualizar saldo del wallet — usar valores custom si se especificaron
        if config.initial_axf > 0:
            wallet.axofichas = axf_to_internal(config.initial_axf)
        else:
            wallet.axofichas = axf_to_internal(current_obtained)
        wallet.frijolitos = 0
        session.add(wallet)
        session.commit()

        packs_summary = ", ".join([f"{k} ({v}x)" for k, v in purchased_packs_counts.items()])
        final_axf = config.initial_axf if config.initial_axf > 0 else current_obtained
        print(f"  💎 {user_id}: Simulación compra AXG: {packs_summary} | Total AXG: {final_axf:.0f} | MXN: ${mxn_spent:.2f}")
        stats["axg_purchased_mxn"] = stats.get("axg_purchased_mxn", 0.0) + mxn_spent
        stats["axg_purchased_qty"] = stats.get("axg_purchased_qty", 0.0) + current_obtained

        # 3. Fondear FRJ directamente (ShopService.buy_item bloquea CURRENCY_PACK por
        #    compliance regulatorio — status_code 403). En lugar de comprar paquetes,
        #    acreditamos FRJ directamente en unidad mínima (VULN-06).
        n_packs = _rng.randint(3, 6)
        if frj_packs:
            # Usar price_gal de los paquetes como referencia de cuánto FRJ otorga cada uno
            pack_amounts = [
                p.price_gal if p.price_gal else 2000 * (10 ** FRJ_DECIMALS_BACKEND)
                for p in frj_packs
            ]
            avg_pack = sum(pack_amounts) // len(pack_amounts)
            total_frj = n_packs * avg_pack
        else:
            total_frj = frj_to_internal(10000)  # 10,000 FRJ fallback

        wallet.frijolitos += total_frj
        session.add(wallet)
        session.commit()
        stats["frj_packs_bought"] = stats.get("frj_packs_bought", 0) + n_packs
        print(f"  🌿 {user_id}: {wallet.frijolitos / (10**FRJ_DECIMALS_BACKEND):.0f} FRJ "
              f"({n_packs} paquetes, +{total_frj / (10**FRJ_DECIMALS_BACKEND):.0f} FRJ)")

        # 3b. Si se especificó FRJ inicial custom, sobrescribir el saldo
        #      El valor se interpreta en FRJ legibles (ej. 5000 = 5000 FRJ),
        #      se convierte a unidad mínima antes de guardar (VULN-06).
        if config.initial_frj > 0:
            wallet.frijolitos = frj_to_internal(config.initial_frj)
            session.add(wallet)
            session.commit()
            print(f"  🌿 {user_id}: {wallet.frijolitos / (10**FRJ_DECIMALS_BACKEND):.0f} FRJ (custom inicial, {config.initial_frj} FRJ)")

        # 4. Activar VIP ahora que ya tiene GAL — compras futuras (boosters, huevos) gozarán descuento
        if vip_tier and vip_tier in vip_catalog:
            vip_item = vip_catalog[vip_tier]
            try:
                res = ShopService.buy_item(
                    session=session,
                    user_id=user_id,
                    item_id=vip_item.id,
                    payment_currency=CurrencyType.AXOGEMA,
                )
                session.refresh(wallet)
                session.refresh(user)
                stats["vip_activations"] = stats.get("vip_activations", 0) + 1
                welcome_frj = res.get("welcome_gal_bonus", 0) if isinstance(res, dict) else 0
                print(f"  👑 {user_id}: VIP {vip_tier.upper()} activado tras fondear FRJ (+{welcome_frj} FRJ bienvenida) — próximas compras con descuento")
            except HTTPException as e:
                errors.append(f"vip_buy_early {user_id} {vip_tier}: {e.detail}")

    progress(f"  ✅ Wallets fondeadas.")
    return {}
