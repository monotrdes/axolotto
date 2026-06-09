from sqlmodel import Session, select
from fastapi import HTTPException
from app.models.economy import Wallet, TransactionLedger, CurrencyType, TransactionType
from app.models.user import User
from app.services.web3_service import Web3Service

# Constante: La comisión de la casa para transferencias P2P (Ej: 5%)
P2P_FEE_PERCENTAGE = 0.05


def assert_multijugador_currency(wallet: Wallet, amount_frj: float) -> None:
    """
    Guard de compliance legal: el juego multijugador SOLO acepta Frijolitos (FRJ).

    Verifica que la wallet tenga saldo suficiente en frijolitos para cubrir el monto.
    NUNCA toca axofichas (AXF) para operaciones de multijugador.

    Raises:
        HTTPException 402 si saldo insuficiente en FRJ.
        HTTPException 403 si se intenta usar AXF (no permitido en multijugador).
    """
    if wallet.frijolitos < amount_frj:
        raise HTTPException(
            status_code=402,
            detail=f"Saldo insuficiente de Frijolitos (FRJ). "
                   f"Tienes {wallet.frijolitos:.2f} FRJ y necesitas {amount_frj:.2f} FRJ. "
                   f"El multijugador solo acepta FRJ, no Axofichas (AXF)."
        )


class BankService:
    
    @staticmethod
    def get_or_create_wallet(session: Session, user_id: str, for_update: bool = False) -> Wallet:
        """Busca la wallet del usuario, si no existe, le crea una en ceros."""
        q = select(Wallet).where(Wallet.user_id == user_id)
        if for_update:
            q = q.with_for_update()
        wallet = session.exec(q).first()
        if not wallet:
            wallet = Wallet(user_id=user_id)
            session.add(wallet)
            session.commit()
            session.refresh(wallet)
        return wallet

    @staticmethod
    def admin_deposit(session: Session, user_id: str, amount: float, currency: CurrencyType, description: str):
        """Deposita dinero y, si son Axofichas, dispara la transacción en la Blockchain."""
        if amount <= 0:
            raise HTTPException(status_code=400, detail="El monto debe ser mayor a cero.")

        # 1. Buscamos al usuario para ver si tiene una wallet_address registrada
        user = session.exec(select(User).where(User.privy_did == user_id)).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado en la base de datos.")

        wallet = BankService.get_or_create_wallet(session, user_id)
        tx_hash = None

        # 2. MAGIA WEB3: Si es Axoficha, mandamos los tokens por la red Plasma
        if currency == CurrencyType.AXOGEMA:
            if not user.wallet_address:
                raise HTTPException(status_code=400, detail="El usuario no tiene una wallet Web3 vinculada.")

            try:
                # Disparamos la transacción en la blockchain
                tx_hash = Web3Service.transferir_axofichas(to_address=user.wallet_address, amount=amount)
                # Guardamos el hash en la descripción para tener auditoría cruzada
                description = f"{description} | Tx: {tx_hash}"
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error en la Blockchain: {str(e)}")

            wallet.axofichas += amount

        elif currency == CurrencyType.GEMA_ALGA:
            wallet.frijolitos += amount
        else:
            setattr(wallet, currency.value, getattr(wallet, currency.value) + int(amount))

        # 3. Guardamos el registro inmutable en PostgreSQL
        ledger_entry = TransactionLedger(
            user_id=user_id,
            amount=amount,
            currency=currency,
            tx_type=TransactionType.DEPOSIT if currency in [CurrencyType.AXOGEMA, CurrencyType.GEMA_ALGA] else TransactionType.REWARD,
            description=description
        )

        session.add(wallet)
        session.add(ledger_entry)
        session.commit()

        # 4. Preparamos la respuesta VIP
        respuesta = {
            "mensaje": f"Depósito exitoso de {amount} {currency.value}",
            "nuevo_saldo": getattr(wallet, "axofichas" if currency == CurrencyType.AXOGEMA else ("frijolitos" if currency == CurrencyType.GEMA_ALGA else f"{currency.value}s"))
        }

        # Si hubo transacción blockchain, devolvemos el link del explorador
        if tx_hash:
            respuesta["tx_hash"] = tx_hash
            respuesta["polygon_scan"] = f"https://amoy.polygonscan.com/tx/{tx_hash}"

        return respuesta

    @staticmethod
    def transfer_p2p(session: Session, sender_id: str, receiver_id: str, amount: float, currency: CurrencyType):
        """Transferencia entre amigos cobrando la comisión de la casa."""
        if amount <= 0:
            raise HTTPException(status_code=400, detail="El monto a enviar debe ser mayor a cero.")
        if sender_id == receiver_id:
            raise HTTPException(status_code=400, detail="No puedes enviarte gemas a ti mismo.")

        # Obtener wallets con bloqueo pesimista para prevenir double-spend concurrente
        sender_wallet = BankService.get_or_create_wallet(session, sender_id, for_update=True)
        receiver_wallet = BankService.get_or_create_wallet(session, receiver_id, for_update=True)

        # Mapeo explícito: CurrencyType → nombre real del campo en Wallet
        _CURRENCY_FIELD = {
            CurrencyType.AXOGEMA:   "axofichas",
            CurrencyType.GEMA_ALGA: "frijolitos",
        }

        # Validar que la moneda sea transferible ANTES de acceder al saldo
        if currency not in _CURRENCY_FIELD:
            raise HTTPException(status_code=400, detail="Los fragmentos no se pueden transferir.")

        # 1. Verificar fondos del remitente
        field_name = _CURRENCY_FIELD[currency]
        current_balance = getattr(sender_wallet, field_name)
        if current_balance < amount:
            raise HTTPException(status_code=400, detail="Fondos insuficientes.")

        # 2. Calcular la tajada del Rey (Comisión)
        fee = amount * P2P_FEE_PERCENTAGE
        amount_after_fee = amount - fee

        try:
            # 3. Restar al que envía
            if currency == CurrencyType.AXOGEMA:
                sender_wallet.axofichas -= amount
                receiver_wallet.axofichas += amount_after_fee
            elif currency == CurrencyType.GEMA_ALGA:
                sender_wallet.frijolitos -= amount
                receiver_wallet.frijolitos += amount_after_fee
            else:
                raise HTTPException(status_code=400, detail="Los fragmentos no se pueden transferir.")

            # 4. Registrar salida del remitente
            sender_ledger = TransactionLedger(
                user_id=sender_id,
                amount=amount,
                currency=currency,
                tx_type=TransactionType.P2P_SEND,
                related_user_id=receiver_id,
                description=f"Envío a {receiver_id}"
            )

            # 5. Registrar entrada del receptor (ya con la comisión aplicada)
            receiver_ledger = TransactionLedger(
                user_id=receiver_id,
                amount=amount_after_fee,
                currency=currency,
                tx_type=TransactionType.P2P_RECEIVE,
                related_user_id=sender_id,
                fee_applied=fee, # <--- ¡Aquí queda auditada la ganancia de la casa!
                description=f"Recibido de {sender_id}"
            )

            # Enviar todo a la base de datos (Atómico: o pasa todo, o no pasa nada)
            session.add(sender_wallet)
            session.add(receiver_wallet)
            session.add(sender_ledger)
            session.add(receiver_ledger)
            session.commit()

            return {
                "mensaje": "Transferencia exitosa",
                "enviado": amount,
                "comision": fee,
                "recibido_por_amigo": amount_after_fee
            }

        except Exception as e:
            session.rollback() # ¡EL SALVAVIDAS! Si algo falla, deshace los cambios.
            raise HTTPException(status_code=500, detail=f"Error en el banco: {str(e)}")