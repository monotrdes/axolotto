from sqlmodel import Session, select
from fastapi import HTTPException

from app.models.user import User
from app.models.items import ItemCatalog, ItemType
from app.models.economy import CurrencyType
from app.services.bank_service import BankService
from app.services.shop_service import ShopService


def phase_vip(engine, config, **state) -> dict:
    """Activa VIP para los jugadores que lo tengan en su personalidad y verifica los beneficios."""
    session: Session = state["session"]
    progress = state["progress"]
    players: list = state["players"]
    stats: dict = state["stats"]
    errors: list = state["errors"]

    progress("  👑 Activando y verificando VIP Club...")

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

    if not vip_catalog:
        progress("  ⚠️  Sin items VIP en catálogo. Saltando fase.")
        return {}

    for p in players:
        user_id     = p["user_id"]
        personality = p["personality"]
        tier        = personality.get("vip_tier")
        if not tier or tier not in vip_catalog:
            continue

        item = vip_catalog[tier]
        user = session.exec(select(User).where(User.privy_did == user_id)).first()
        wallet = BankService.get_or_create_wallet(session, user_id)

        if not user.is_vip:
            # Asegurar saldo suficiente en AXG para la membresía
            if wallet.axofichas < item.price_axg:
                wallet.axofichas = item.price_axg + 100
                session.add(wallet)
                session.commit()

            try:
                res = ShopService.buy_item(
                    session=session,
                    user_id=user_id,
                    item_id=item.id,
                    payment_currency=CurrencyType.AXOGEMA,
                )
                session.refresh(user)
                stats["vip_activations"] = stats.get("vip_activations", 0) + 1
                welcome_frj = res.get("welcome_frj_bonus", 0) if isinstance(res, dict) else 0
                print(f"  👑 {user_id}: VIP {tier.upper()} activado"
                      + (f" (+{welcome_frj} FRJ bienvenida)" if welcome_frj else ""))
            except HTTPException as e:
                errors.append(f"vip_buy {user_id} {tier}: {e.detail}")
                continue
        else:
            print(f"  👑 {user_id}: VIP {tier.upper()} ya estaba activo desde el inicio (compras con descuento)")

        # ── Verificar beneficios VIP ──────────────────────────────────────────

        # 1. Descuento en tienda: comprar un CONSUMABLE y ver que tiene descuento
        consumable = session.exec(
            select(ItemCatalog).where(
                ItemCatalog.item_type == ItemType.CONSUMABLE,
                ItemCatalog.is_active == True,
                ItemCatalog.price_axg > 0,
            )
        ).first()
        if consumable:
            wallet_before = wallet.axofichas
            try:
                ShopService.buy_item(
                    session=session,
                    user_id=user_id,
                    item_id=consumable.id,
                    payment_currency=CurrencyType.AXOGEMA,
                )
                session.refresh(wallet)
                paid = wallet_before - wallet.axofichas
                expected_no_discount = consumable.price_axg
                if paid < expected_no_discount:
                    pct = round((1 - paid / expected_no_discount) * 100, 1)
                    print(f"  🏷️  {user_id}: descuento VIP verificado: {pct:.1f}% ({expected_no_discount} → {paid:.2f} AXG)")
                else:
                    print(f"  ℹ️  {user_id}: compra consumible sin descuento observable (precio: {paid:.2f})")
            except HTTPException as e:
                errors.append(f"vip_discount_check {user_id}: {e.detail}")

        # 2. Reclamar FRJ diario VIP
        try:
            from app.api.v1.endpoints.user import claim_vip_frj
            claim_res = claim_vip_frj(session=session, verified_user_id=user_id)
            session.refresh(wallet)
            print(f"  🌿 {user_id}: FRJ VIP reclamado → {claim_res.get('gal_claimed', 0):.0f} FRJ")
            stats["vip_gal_claimed"] = stats.get("vip_gal_claimed", 0) + 1
        except HTTPException as e:
            if e.status_code == 400:
                print(f"  ℹ️  {user_id}: FRJ VIP ya reclamado hoy ({e.detail})")
            else:
                errors.append(f"vip_claim {user_id}: {e.detail}")

        # 3. Verificar que is_vip = True en User
        session.refresh(user)
        assert user.is_vip, f"❌ {user_id}: is_vip debería ser True tras comprar {tier}"
        print(f"  ✅ {user_id}: is_vip={user.is_vip}, tier={user.vip_tier}, "
              f"días={user.vip_days_remaining if hasattr(user, 'vip_days_remaining') else 'N/A'}")

        # 4. Activar auto-renovación VIP para jugadores comprometidos
        if personality["name"] in ("whale", "aggressive"):
            try:
                from app.api.v1.endpoints.user import set_vip_auto_renew, AutoRenewRequest
                set_vip_auto_renew(
                    req=AutoRenewRequest(enabled=True),
                    session=session,
                    verified_user_id=user_id,
                )
                session.refresh(user)
                stats["vip_auto_renew"] = stats.get("vip_auto_renew", 0) + 1
                progress(f"  🔄 {user_id}: Auto-renovación VIP activada (streak: {user.vip_streak_months} mes(es))")
            except HTTPException as e:
                errors.append(f"vip_autorenew {user_id}: {e.detail}")

    progress(f"  ✅ VIP activado para {stats.get('vip_activations', 0)} jugadores, "
             f"{stats.get('vip_auto_renew', 0)} con auto-renovación.")
    return {}
