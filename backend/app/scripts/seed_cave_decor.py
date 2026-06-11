"""
seed_cave_decor.py — Catálogo de decoraciones de cueva (CAVE_ITEM).

Siembra ~23 decoraciones comprables con FRJ (sink de frijolitos, plan
task-84), repartidas en la taxonomía de slots del Santuario:
AMBIENTE / LUZ / MESA / MANTEL / SILLAS / FONDO / ESPECIAL.

Idempotente por nombre (mismo patrón que seed_catalog.py): si el item ya
existe se actualiza precio/metadata; si no, se crea.

Uso:  python app/scripts/seed_cave_decor.py
"""
import sys
import os

backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(backend_dir)

from dotenv import load_dotenv
load_dotenv(os.path.join(backend_dir, "..", ".env"))
load_dotenv(os.path.join(backend_dir, ".env"), override=True)

if not os.path.exists("/.dockerenv") and "DATABASE_URL" in os.environ:
    db_url = os.environ["DATABASE_URL"]
    if "@db_axolotto:5432" in db_url:
        os.environ["DATABASE_URL"] = db_url.replace("@db_axolotto:5432", "@127.0.0.1:5433")

from sqlmodel import Session, select
from app.database import engine
from app.models.items import ItemCatalog, ItemType, Rarity
from app.core.prices import CAVE_DECOR_PRICES

_P = CAVE_DECOR_PRICES  # precios internos (FRJ × 10**4) por rareza


def _decor(name, description, rarity, subcat, emoji, color=None, max_per_user=None, **bonos):
    """Construye un ItemCatalog de decoración con metadata estándar."""
    meta = {"cave_subcategory": subcat, "emoji": emoji}
    if color:
        meta["color"] = color
    meta.update(bonos)  # focus_bonus / staking_bonus / incubation_boost
    return ItemCatalog(
        name=name,
        description=description,
        item_type=ItemType.CAVE_ITEM,
        rarity=rarity,
        price_gal=_P[rarity.value if hasattr(rarity, "value") else rarity],
        max_per_user=max_per_user,
        is_active=True,
        item_metadata=meta,
    )


def build_catalog() -> list[ItemCatalog]:
    C, R, E, L = Rarity.COMMON, Rarity.RARE, Rarity.EPIC, Rarity.LEGENDARY
    return [
        # ── AMBIENTE (color/tinte de la cueva) ──
        _decor("Ambiente Atardecer del Cenote", "El agua se tiñe del atardecer clásico de Xochimilco.",
               C, "AMBIENTE", "🌅", color="#1b7a8c", focus_bonus=0.01),
        _decor("Ambiente Bugambilia Nocturna", "Penumbra rosa mexicano para cuevas con estilo.",
               R, "AMBIENTE", "🌸", color="#7a1b5e", focus_bonus=0.02),
        _decor("Ambiente Templo Maya", "Luz dorada ancestral que emana de la piedra.",
               L, "AMBIENTE", "🏛️", color="#8a6d1f", max_per_user=1,
               focus_bonus=0.04, staking_bonus=0.04),

        # ── LUZ (iluminación) ──
        _decor("Antorcha de Chinampa", "Llama cálida de toda la vida.",
               C, "LUZ", "🕯️", focus_bonus=0.01),
        _decor("Farol de Papel Picado", "Recortes que bailan sombras en las paredes.",
               R, "LUZ", "🏮", focus_bonus=0.02),
        _decor("Luciérnagas del Cenote", "Un enjambre dócil que ilumina sin quemar.",
               E, "LUZ", "✨", focus_bonus=0.04),

        # ── MESA (skin de la mesa de juego) ──
        _decor("Mesa de Trajinera", "Madera curada por los canales.",
               C, "MESA", "🪵", color="#8b5e34"),
        _decor("Mesa de Talavera", "Azulejos pintados a mano, cada uno distinto.",
               E, "MESA", "🔷", color="#2563eb", staking_bonus=0.04),
        _decor("Mesa de Obsidiana", "Vidrio volcánico pulido. Las cartas resbalan solas.",
               L, "MESA", "⬛", color="#1f2937", max_per_user=1, staking_bonus=0.08),

        # ── MANTEL (requiere mesa equipada) ──
        _decor("Mantel de Fiesta", "Rosa mexicano con flecos de papel.",
               C, "MANTEL", "🎀", color="#e4007c"),
        _decor("Mantel Tenango", "Bordado hidalguense con animalitos del cenote.",
               R, "MANTEL", "🦜", color="#f59e0b", focus_bonus=0.02),
        _decor("Mantel Otomí Real", "Hilo de oro sobre algodón de chinampa.",
               E, "MANTEL", "🧵", color="#10b981", focus_bonus=0.02, staking_bonus=0.02),

        # ── SILLAS (asientos de la mesa) ──
        _decor("Sillas de Mimbre", "Tejidas a mano, crujen sabroso.",
               C, "SILLAS", "🪑", color="#a9743f"),
        _decor("Sillas Equipales", "Cuero y madera de rosa morada, como en Tlaquepaque.",
               R, "SILLAS", "🛋️", color="#7c3aed", focus_bonus=0.02),

        # ── FONDO (decoración de fondo, crece con el nivel) ──
        _decor("Helecho de Papel", "Verde que ondula con la corriente.",
               C, "FONDO", "🪴", incubation_boost=0.01),
        _decor("Lotos del Cenote", "Flotan donde el agua está más tranquila.",
               C, "FONDO", "🪷", incubation_boost=0.01),
        _decor("Hongos Bioluminiscentes", "Abrigan a los huevos con su calorcito azul.",
               R, "FONDO", "🍄", incubation_boost=0.02),
        _decor("Vasijas Pintadas", "Barro bruñido con grecas antiguas.",
               R, "FONDO", "🏺", staking_bonus=0.02),
        _decor("Mural de Papel Picado", "La historia de tu cueva recortada en papel de china.",
               E, "FONDO", "🖼️", focus_bonus=0.02, incubation_boost=0.02),

        # ── ESPECIAL (items únicos: rocola, reliquias...) ──
        _decor("Caja de Música de Cuerda", "Toca un arrullo acuático para los webitos.",
               C, "ESPECIAL", "🎵", incubation_boost=0.01),
        _decor("Cofre del Náufrago", "Nadie sabe qué guarda, pero atrae frijolitos.",
               R, "ESPECIAL", "🧰", staking_bonus=0.02),
        _decor("Rocola del Cenote", "Jarana, son y cumbia a un frijolito la canción.",
               E, "ESPECIAL", "📻", staking_bonus=0.04),
        _decor("Piedra del Sol", "Una réplica en miniatura que marca las horas de suerte.",
               L, "ESPECIAL", "🌞", max_per_user=1, focus_bonus=0.04, staking_bonus=0.04),
    ]


def run_seed():
    print("Sembrando catálogo de decoraciones de cueva...")
    created, updated = 0, 0
    with Session(engine) as session:
        for item in build_catalog():
            existing = session.exec(
                select(ItemCatalog).where(ItemCatalog.name == item.name)
            ).first()
            if existing:
                existing.description = item.description
                existing.item_type = item.item_type
                existing.rarity = item.rarity
                existing.price_gal = item.price_gal
                existing.max_per_user = item.max_per_user
                existing.is_active = True
                existing.item_metadata = item.item_metadata
                session.add(existing)
                updated += 1
            else:
                session.add(item)
                created += 1
        session.commit()
    print(f"✅ Decoraciones: {created} creadas, {updated} actualizadas.")


if __name__ == "__main__":
    run_seed()
