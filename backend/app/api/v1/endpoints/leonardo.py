"""
leonardo.py — Webhook endpoint para recibir resultados de Leonardo.ai

Leonardo.ai llama a este endpoint con un POST cuando termina de generar
cada imagen. El handler descarga las imágenes y las guarda en disco.

Endpoint público (sin autenticación de usuario), protegido opcionalmente
con LEONARDO_WEBHOOK_SECRET.

POST /api/v1/leonardo/webhook
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

import httpx
from fastapi import APIRouter, Header, HTTPException, Request

logger = logging.getLogger(__name__)

router = APIRouter()

# ---------------------------------------------------------------------------
# Configuración desde entorno
# ---------------------------------------------------------------------------
LEONARDO_OUTPUT_DIR = os.environ.get("LEONARDO_OUTPUT_DIR", "./output/cards")
LEONARDO_WEBHOOK_SECRET = os.environ.get("LEONARDO_WEBHOOK_SECRET", "")


def get_jobs_mapping() -> Dict[str, str]:
    """Lee jobs_mapping.json y devuelve { generation_id: card_name }."""
    mapping_path = Path(LEONARDO_OUTPUT_DIR) / "jobs_mapping.json"
    if not mapping_path.exists():
        return {}
    try:
        with open(mapping_path) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        logger.warning(f"No se pudo leer jobs_mapping.json: {e}")
        return {}


async def download_image(url: str, dest_path: Path) -> bool:
    """Descarga una imagen desde la URL de Leonardo CDN y la guarda en dest_path."""
    try:
        async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            with open(dest_path, "wb") as f:
                f.write(resp.content)
        return True
    except Exception as e:
        logger.error(f"Error al descargar imagen de {url}: {e}")
        return False


# ---------------------------------------------------------------------------
# Webhook handler
# ---------------------------------------------------------------------------
@router.post("/webhook")
async def leonardo_webhook(
    request: Request,
    authorization: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    """
    Recibe el callback de Leonardo.ai cuando termina una generación.

    Payload esperado:
    {
      "type": "image_generation.complete",
      "data": {
        "generations_by_pk": {
          "id": "gen-xxx",
          "status": "COMPLETE",
          "generated_images": [
            { "id": "img-xxx", "url": "https://cdn.leonardo.ai/..." },
            ...
          ]
        }
      }
    }
    """
    # --- Verificar webhook secret (si está configurado) ---
    if LEONARDO_WEBHOOK_SECRET:
        expected = f"Bearer {LEONARDO_WEBHOOK_SECRET}"
        if authorization != expected:
            logger.warning("Webhook recibido con secret inválido.")
            raise HTTPException(status_code=401, detail="Unauthorized")

    # --- Parsear body ---
    try:
        body = await request.json()
    except Exception:
        logger.warning("Webhook con body inválido (no es JSON).")
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    # Log completo del payload para diagnosticar la estructura real de Leonardo
    logger.info(f"🎨 Webhook Leonardo.ai — payload completo: {json.dumps(body, indent=2)}")

    event_type = body.get("type", "")
    logger.info(f"🎨 Webhook Leonardo.ai recibido — tipo: {event_type!r}")

    # Solo procesar completions de generación de imágenes
    if event_type != "image_generation.complete":
        logger.info(f"   Tipo ignorado: {event_type!r}")
        return {"status": "ignored", "type": event_type}

    # --- Extraer datos de la generación ---
    # Intentar ambas estructuras conocidas de Leonardo
    data = body.get("data", {})
    generation_data = data.get("generations_by_pk") or data.get("generation") or data
    generation_id: str = generation_data.get("id", "")
    status: str = generation_data.get("status", "")
    generated_images: list = generation_data.get("generated_images", [])

    if not generation_id:
        logger.warning(f"Webhook sin generation_id. Keys en body: {list(body.keys())} | Keys en data: {list(data.keys()) if isinstance(data, dict) else 'N/A'}")
        return {"status": "skipped", "reason": "no generation_id", "body_keys": list(body.keys())}

    if status != "COMPLETE":
        logger.info(f"   Generación {generation_id[:8]}... con status '{status}' — ignorando.")
        return {"status": "ignored", "generation_id": generation_id, "status_value": status}

    if not generated_images:
        logger.warning(f"   Generación {generation_id[:8]}... completada pero sin imágenes.")
        return {"status": "skipped", "reason": "no images", "generation_id": generation_id}

    # --- Resolver card_name a partir del mapping ---
    mapping = get_jobs_mapping()
    card_name = mapping.get(generation_id)

    if not card_name:
        logger.warning(
            f"   generation_id {generation_id[:8]}... no encontrado en jobs_mapping.json. "
            "¿El script aún no lo registró?"
        )
        return {"status": "unknown", "generation_id": generation_id}

    logger.info(f"   📋 Carta identificada: {card_name}")

    # --- Descargar y guardar imágenes ---
    output_dir = Path(LEONARDO_OUTPUT_DIR)
    card_dir = output_dir / card_name

    saved_files = []
    for idx, img_data in enumerate(generated_images, start=1):
        img_url = img_data.get("url")
        if not img_url:
            logger.warning(f"   Imagen {idx} sin URL, saltando.")
            continue

        dest_path = card_dir / f"variante_{idx}.png"

        if dest_path.exists():
            logger.info(f"   ⏩ {dest_path.name} ya existe, saltando descarga.")
            saved_files.append(str(dest_path))
            continue

        logger.info(f"   ⬇️  Descargando variante {idx}: {img_url[:60]}...")
        success = await download_image(img_url, dest_path)

        if success:
            logger.info(f"   ✅ Guardada: {dest_path}")
            saved_files.append(str(dest_path))
        else:
            logger.error(f"   ❌ Falló la descarga de variante {idx} para {card_name}")

    logger.info(
        f"🎴 {card_name}: {len(saved_files)}/{len(generated_images)} imágenes procesadas."
    )

    return {
        "status": "ok",
        "card": card_name,
        "generation_id": generation_id,
        "images_saved": len(saved_files),
        "files": saved_files,
    }


# ---------------------------------------------------------------------------
# Endpoint de salud / info (útil para verificar que el módulo está activo)
# ---------------------------------------------------------------------------
@router.get("/status")
def leonardo_status() -> Dict[str, Any]:
    """Información del estado del módulo Leonardo.ai."""
    output_dir = Path(LEONARDO_OUTPUT_DIR)
    mapping_path = output_dir / "jobs_mapping.json"

    mapping = get_jobs_mapping()
    cards_with_images = 0

    if output_dir.exists():
        for card_dir in output_dir.iterdir():
            if card_dir.is_dir() and len(list(card_dir.glob("variante_*.png"))) >= 1:
                cards_with_images += 1

    return {
        "status": "active",
        "output_dir": str(output_dir.resolve()),
        "mapping_exists": mapping_path.exists(),
        "total_jobs_submitted": len(mapping),
        "cards_with_images_on_disk": cards_with_images,
        "webhook_secret_configured": bool(LEONARDO_WEBHOOK_SECRET),
    }
