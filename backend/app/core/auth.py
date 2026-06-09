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
        # Si no hay token y PRIVY_APP_ID no está configurado, permitimos continuar únicamente en modo local de desarrollo
        if settings.BLOCKCHAIN_MODE == "local" and not settings.PRIVY_APP_ID:
            logger.warning("No se proporcionó token de autorización. Continuando en modo de desarrollo sin verificación.")
            # Intentar buscar user_id en la query o el body para desarrollo
            user_id = request.query_params.get("user_id") or request.query_params.get("privy_did")
            if user_id:
                return user_id
            raise HTTPException(
                status_code=401,
                detail="Cabecera de autorización ausente. En desarrollo, pasa 'user_id' como parámetro de consulta."
            )
        raise HTTPException(status_code=401, detail="Token de autorización ausente.")

    token = credentials.credentials

    # Caso 1: PRIVY_APP_ID no está configurado (Solo permitido en Modo desarrollo / Local)
    if not settings.PRIVY_APP_ID:
        if settings.BLOCKCHAIN_MODE != "local":
            raise HTTPException(
                status_code=500,
                detail="PRIVY_APP_ID no está configurado en un entorno no local."
            )
        try:
            # Decodificamos el token sin verificar la firma para facilitar pruebas locales
            payload = jwt.decode(token, options={"verify_signature": False})
            user_id = payload.get("sub")
            if not user_id:
                raise HTTPException(status_code=401, detail="El token decodificado no contiene el campo 'sub'.")
            return user_id
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Error decodificando token en modo desarrollo: {str(e)}")

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
