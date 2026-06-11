import jwt
import logging
from typing import Optional
from fastapi import Depends, HTTPException, Security, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt import PyJWKClient
from app.core.config import settings

logger = logging.getLogger("auth")

security = HTTPBearer(auto_error=False)

# Cache for the JWK client to avoid recreating it on every request
_jwks_client: Optional[PyJWKClient] = None

def get_jwks_client() -> Optional[PyJWKClient]:
    global _jwks_client
    if _jwks_client is not None:
        return _jwks_client
    
    if settings.PRIVY_APP_ID:
        url = f"https://auth.privy.io/api/v1/apps/{settings.PRIVY_APP_ID}/jwks.json"
        _jwks_client = PyJWKClient(url)
        return _jwks_client
    return None

def get_verified_user_id(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security)
) -> str:
    """
    Extrae y verifica el token de Privy de la cabecera Authorization.
    Devuelve el privy_did (el claim 'sub' del JWT).
    """
    if not credentials:
        if settings.ALLOW_DEV_AUTH and settings.BLOCKCHAIN_MODE == "local":
            user_id = request.headers.get("X-Dev-User")
            if user_id:
                return user_id
        raise HTTPException(status_code=401, detail="Token de autorización ausente.")

    token = credentials.credentials

    # Sin PRIVY_APP_ID solo se acepta token si ALLOW_DEV_AUTH está activo en modo local.
    # En producción el startup validator garantiza que PRIVY_APP_ID esté configurado.
    if not settings.PRIVY_APP_ID:
        if settings.ALLOW_DEV_AUTH and settings.BLOCKCHAIN_MODE == "local":
            try:
                payload = jwt.decode(token, options={"verify_signature": False})
                user_id = payload.get("sub")
                if not user_id:
                    raise HTTPException(status_code=401, detail="El token decodificado no contiene el campo 'sub'.")
                return user_id
            except jwt.DecodeError as e:
                raise HTTPException(status_code=401, detail=f"Token inválido: {str(e)}")
        raise HTTPException(status_code=401, detail="Token de autorización inválido.")

    # Caso 2: PRIVY_APP_ID configurado (Modo Producción Seguro)
    try:
        jwks_client = get_jwks_client()
        if not jwks_client:
            raise HTTPException(status_code=500, detail="Error configurando el cliente JWKS de Privy.")

        # Obtener la llave pública correspondiente al 'kid' del token
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        
        # Verificar y decodificar el token con la firma de Privy
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["ES256"],
            audience=settings.PRIVY_APP_ID,
            issuer="privy.io"
        )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Sujeto (sub) ausente en el token de Privy.")
            
        return user_id

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="El token de Privy ha expirado.")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Token de Privy inválido: {str(e)}")
    except Exception as e:
        logger.error(f"Error durante la verificación de token: {str(e)}")
        raise HTTPException(status_code=401, detail=f"Error de autenticación: {str(e)}")


def require_admin(user_id: str = Depends(get_verified_user_id)) -> str:
    admin_dids = settings.admin_dids
    if not admin_dids:
        raise HTTPException(status_code=503, detail="Admin no configurado en este servidor.")
    if user_id not in admin_dids:
        raise HTTPException(status_code=403, detail="Acceso de administrador requerido.")
    return user_id


def verify_no_active_game(
    user_id: str = Depends(get_verified_user_id)
) -> str:
    """
    Verifica que el usuario no tenga una partida multijugador activa en curso.
    Si está en partida, lanza HTTP 409 Conflict.
    """
    from sqlmodel import Session, select
    from app.database import engine
    from app.models.lobby_models import RoomRegistration, GameRoom
    from app.models.axolotito import Axolotito

    with Session(engine) as session:
        active_game = session.exec(
            select(RoomRegistration)
            .join(GameRoom, RoomRegistration.room_id == GameRoom.id)
            .join(Axolotito, RoomRegistration.axolotito_id == Axolotito.id)
            .where(Axolotito.user_id == user_id)
            .where(GameRoom.status == "playing")
        ).first()

        if active_game:
            raise HTTPException(
                status_code=409,
                detail="IN_GAME_LOCK: Tienes una partida activa en curso. Completa el juego actual para interactuar con el resto del sistema."
            )
    return user_id


def require_tutorial(user) -> None:
    """
    Verifica que el usuario haya completado el tutorial.
    Bloquea CUALQUIER acción del juego hasta que el tutorial esté terminado.
    Excepciones: perfil, auth, dev, admin, y el propio tutorial.
    """
    if not getattr(user, "tutorial_completed", False):
        raise HTTPException(
            status_code=403,
            detail="TUTORIAL_REQUIRED: Debes completar el tutorial antes de explorar el mundo de Axolotto.",
        )

