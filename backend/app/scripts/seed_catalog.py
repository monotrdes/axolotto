import sys
import os

# Ajustamos el path para que el script entienda dónde están los módulos de tu app
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(backend_dir)

# Load environment variables from both root and backend .env files
from dotenv import load_dotenv
load_dotenv(os.path.join(backend_dir, "..", ".env"))
load_dotenv(os.path.join(backend_dir, ".env"), override=True)

# Adjust DATABASE_URL if running on the host machine (not inside Docker)
if not os.path.exists("/.dockerenv") and "DATABASE_URL" in os.environ:
    db_url = os.environ["DATABASE_URL"]
    if "@db_axolotto:5432" in db_url:
        os.environ["DATABASE_URL"] = db_url.replace("@db_axolotto:5432", "@127.0.0.1:5433")

from sqlmodel import Session, select
from sqlalchemy import text
from app.database import engine
from app.models.items import ItemCatalog, ItemType, Rarity
from app.core.prices import WEBITO_PRICES, BOOSTER_PRICES, CONSUMABLE_PRICES, BOARD_PRICES

def run_seed():
    print("Iniciando la siembra del catálogo...")

    # Asegurar que el valor del enum exista en PostgreSQL antes de usarlo (no-op en SQLite)
    try:
        with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
            conn.execute(text("ALTER TYPE itemtype ADD VALUE IF NOT EXISTS 'CURRENCY_PACK'"))
    except Exception:
        pass  # SQLite or enum already exists

    with Session(engine) as session:
        # Aseguramos borrar boosters viejos obsoletos si existen
        all_current_boosters = session.exec(select(ItemCatalog).where(ItemCatalog.item_type == ItemType.BOOSTER)).all()
        allowed_booster_names = {"Booster Fiesta", "Booster Nido", "Booster Cosmos", "Booster Mezclado", "Booster Brillante (Foil)"}
        has_outdated_boosters = any(b.name not in allowed_booster_names for b in all_current_boosters)
        
        if has_outdated_boosters:
            print("Limpiando boosters obsoletos del catálogo...")
            for b in all_current_boosters:
                if b.name not in allowed_booster_names:
                    session.delete(b)
            session.commit()

        # Aseguramos borrar paquetes de algas viejos obsoletos si existen
        all_current_currency = session.exec(select(ItemCatalog).where(ItemCatalog.item_type == ItemType.CURRENCY_PACK)).all()
        allowed_currency_names = {"Paquete Frijolitos Común", "Paquete Frijolitos Abundante", "Paquete Frijolitos Imperial", "Súper Carga de Frijolitos"}
        has_outdated_currency = any(c.name not in allowed_currency_names for c in all_current_currency)
        
        if has_outdated_currency:
            print("Limpiando paquetes de algas obsoletos del catálogo...")
            for c in all_current_currency:
                if c.name not in allowed_currency_names:
                    session.delete(c)
            session.commit()

        items_to_seed = [
            # --- ECOSISTEMA DE WEBITOS ---
            ItemCatalog(
                name="Webito Génesis (Fase 1)",
                description="Los primeros ajolotes de Axolotto. Edición limitada con tag de Fundador.",
                item_type=ItemType.EGG,
                rarity=Rarity.EPIC,
                price_axg=WEBITO_PRICES[1],
                max_supply=200,
                max_per_user=3,
                is_active=True,
                item_metadata={"fase": 1, "tag": "Genesis"}
            ),
            ItemCatalog(
                name="Webito Expansión (Fase 2)",
                description="La familia crece. Segunda generación de ajolotes.",
                item_type=ItemType.EGG,
                rarity=Rarity.RARE,
                price_axg=WEBITO_PRICES[2],
                max_supply=1260,
                max_per_user=8,
                is_active=False,
                item_metadata={"fase": 2}
            ),
            ItemCatalog(
                name="Webito Retail (Fase 3)",
                description="Última oportunidad para conseguir tu ajolote en la tienda oficial.",
                item_type=ItemType.EGG,
                rarity=Rarity.COMMON,
                price_axg=WEBITO_PRICES[3],
                max_supply=2520,
                max_per_user=None,
                is_active=False,
                item_metadata={"fase": 3}
            ),
            ItemCatalog(
                name="Webito Astral (Limitado)",
                description="Un huevo celestial ultra-raro con un aspecto cósmico exclusivo.",
                item_type=ItemType.EGG,
                rarity=Rarity.LEGENDARY,
                price_axg=WEBITO_PRICES["astral"],
                max_supply=100,
                max_per_user=1,
                is_active=True,
                item_metadata={"fase": 1, "tag": "Astral", "is_astral": True}
            ),

            # --- ECOSISTEMA DE BOOSTERS TEMÁTICOS Y PREMIUM ---
            # --- FASE 1 (First Edition) ---
            ItemCatalog(
                name="Booster Fiesta",
                description="Contiene 7 cartas del folklore, comida y fiesta mexicana. (1ra Edición)",
                item_type=ItemType.BOOSTER,
                rarity=Rarity.EPIC,
                price_axg=BOOSTER_PRICES[1]["fiesta"]["axg"],
                price_gal=BOOSTER_PRICES[1]["fiesta"]["gal"],
                max_supply=200,
                max_per_user=5,
                is_active=True,
                item_metadata={"fase": 1, "cards_per_booster": 7, "pack_theme": "fiesta"}
            ),
            ItemCatalog(
                name="Booster Nido",
                description="Contiene 7 cartas de animales, plantas y elementos del nido. (1ra Edición)",
                item_type=ItemType.BOOSTER,
                rarity=Rarity.RARE,
                price_axg=BOOSTER_PRICES[1]["nido"]["axg"],
                price_gal=BOOSTER_PRICES[1]["nido"]["gal"],
                max_supply=200,
                max_per_user=5,
                is_active=True,
                item_metadata={"fase": 1, "cards_per_booster": 7, "pack_theme": "nido"}
            ),
            ItemCatalog(
                name="Booster Cosmos",
                description="Contiene 7 cartas místicas, del cosmos y herramientas tradicionales. (1ra Edición)",
                item_type=ItemType.BOOSTER,
                rarity=Rarity.RARE,
                price_axg=BOOSTER_PRICES[1]["cosmos"]["axg"],
                price_gal=BOOSTER_PRICES[1]["cosmos"]["gal"],
                max_supply=200,
                max_per_user=5,
                is_active=True,
                item_metadata={"fase": 1, "cards_per_booster": 7, "pack_theme": "cosmos"}
            ),
            ItemCatalog(
                name="Booster Mezclado",
                description="Contiene 7 cartas de cualquier tipo de la colección de 54. (1ra Edición)",
                item_type=ItemType.BOOSTER,
                rarity=Rarity.COMMON,
                price_axg=BOOSTER_PRICES[1]["pure"]["axg"],
                price_gal=BOOSTER_PRICES[1]["pure"]["gal"],
                max_supply=300,
                max_per_user=8,
                is_active=True,
                item_metadata={"fase": 1, "cards_per_booster": 7, "pack_theme": "pure"}
            ),

            # --- FASE 2 (Segunda Edición / Unlimited) ---
            ItemCatalog(
                name="Booster Fiesta",
                description="Contiene 7 cartas del folklore, comida y fiesta mexicana.",
                item_type=ItemType.BOOSTER,
                rarity=Rarity.EPIC,
                price_axg=BOOSTER_PRICES[2]["fiesta"]["axg"],
                price_gal=BOOSTER_PRICES[2]["fiesta"]["gal"],
                max_supply=2000,
                max_per_user=15,
                is_active=False,
                item_metadata={"fase": 2, "cards_per_booster": 7, "pack_theme": "fiesta"}
            ),
            ItemCatalog(
                name="Booster Nido",
                description="Contiene 7 cartas de animales, plantas y elementos del nido.",
                item_type=ItemType.BOOSTER,
                rarity=Rarity.RARE,
                price_axg=BOOSTER_PRICES[2]["nido"]["axg"],
                price_gal=BOOSTER_PRICES[2]["nido"]["gal"],
                max_supply=2000,
                max_per_user=15,
                is_active=False,
                item_metadata={"fase": 2, "cards_per_booster": 7, "pack_theme": "nido"}
            ),
            ItemCatalog(
                name="Booster Cosmos",
                description="Contiene 7 cartas místicas, del cosmos y herramientas tradicionales.",
                item_type=ItemType.BOOSTER,
                rarity=Rarity.RARE,
                price_axg=BOOSTER_PRICES[2]["cosmos"]["axg"],
                price_gal=BOOSTER_PRICES[2]["cosmos"]["gal"],
                max_supply=2000,
                max_per_user=15,
                is_active=False,
                item_metadata={"fase": 2, "cards_per_booster": 7, "pack_theme": "cosmos"}
            ),
            ItemCatalog(
                name="Booster Mezclado",
                description="Contiene 7 cartas de cualquier tipo de la colección de 54.",
                item_type=ItemType.BOOSTER,
                rarity=Rarity.COMMON,
                price_axg=BOOSTER_PRICES[2]["pure"]["axg"],
                price_gal=BOOSTER_PRICES[2]["pure"]["gal"],
                max_supply=2000,
                max_per_user=15,
                is_active=False,
                item_metadata={"fase": 2, "cards_per_booster": 7, "pack_theme": "pure"}
            ),

            # --- FASE 3 (Tercera Edición / Retail) ---
            ItemCatalog(
                name="Booster Fiesta",
                description="Contiene 7 cartas del folklore, comida y fiesta mexicana.",
                item_type=ItemType.BOOSTER,
                rarity=Rarity.EPIC,
                price_axg=BOOSTER_PRICES[3]["fiesta"]["axg"],
                price_gal=BOOSTER_PRICES[3]["fiesta"]["gal"],
                max_supply=5000,
                max_per_user=None,
                is_active=False,
                item_metadata={"fase": 3, "cards_per_booster": 7, "pack_theme": "fiesta"}
            ),
            ItemCatalog(
                name="Booster Nido",
                description="Contiene 7 cartas de animales, plantas y elementos del nido.",
                item_type=ItemType.BOOSTER,
                rarity=Rarity.RARE,
                price_axg=BOOSTER_PRICES[3]["nido"]["axg"],
                price_gal=BOOSTER_PRICES[3]["nido"]["gal"],
                max_supply=5000,
                max_per_user=None,
                is_active=False,
                item_metadata={"fase": 3, "cards_per_booster": 7, "pack_theme": "nido"}
            ),
            ItemCatalog(
                name="Booster Cosmos",
                description="Contiene 7 cartas místicas, del cosmos y herramientas tradicionales.",
                item_type=ItemType.BOOSTER,
                rarity=Rarity.RARE,
                price_axg=BOOSTER_PRICES[3]["cosmos"]["axg"],
                price_gal=BOOSTER_PRICES[3]["cosmos"]["gal"],
                max_supply=5000,
                max_per_user=None,
                is_active=False,
                item_metadata={"fase": 3, "cards_per_booster": 7, "pack_theme": "cosmos"}
            ),
            ItemCatalog(
                name="Booster Mezclado",
                description="Contiene 7 cartas de cualquier tipo de la colección de 54.",
                item_type=ItemType.BOOSTER,
                rarity=Rarity.COMMON,
                price_axg=BOOSTER_PRICES[3]["pure"]["axg"],
                price_gal=BOOSTER_PRICES[3]["pure"]["gal"],
                max_supply=5000,
                max_per_user=None,
                is_active=False,
                item_metadata={"fase": 3, "cards_per_booster": 7, "pack_theme": "pure"}
            ),

            # --- BOOSTER ESPECIAL BRILLANTE ---
            ItemCatalog(
                name="Booster Brillante (Foil)",
                description="Garantiza cartas holográficas Shiny con efectos animados on-chain.",
                item_type=ItemType.BOOSTER,
                rarity=Rarity.LEGENDARY,
                price_axg=BOOSTER_PRICES["foil"]["axg"],
                price_gal=BOOSTER_PRICES["foil"]["gal"],
                max_supply=999999,
                is_active=True,
                item_metadata={"fase": 1, "cards_per_booster": 7, "pack_theme": "foil"}
            ),

            # --- ECOSISTEMA DE PROTECCIÓN Y SERVICIOS (CONSUMIBLES) ---
            ItemCatalog(
                name="Pase Coral VIP (30 días)",
                description="VIP Club Casual: +20 FRJ/día, 5% descuento en tienda, cápsulas mensuales y marco Coral exclusivo.",
                item_type=ItemType.CONSUMABLE,
                rarity=Rarity.RARE,
                price_axg=CONSUMABLE_PRICES["vip_coral"],
                price_gal=0.0,
                max_supply=999999,
                is_active=True,
                item_metadata={"duration_days": 30, "is_vip": True, "vip_tier": "coral"}
            ),
            ItemCatalog(
                name="Pase Dorado VIP (30 días)",
                description="VIP Club Frecuente: +50 FRJ/día, 12% descuento, slot de tabla extra, comisión P2P 3%, cápsulas mensuales y corona animada.",
                item_type=ItemType.CONSUMABLE,
                rarity=Rarity.EPIC,
                price_axg=CONSUMABLE_PRICES["vip_dorado"],
                price_gal=0.0,
                max_supply=999999,
                is_active=True,
                item_metadata={"duration_days": 30, "is_vip": True, "vip_tier": "dorado"}
            ),
            ItemCatalog(
                name="Pase Axolite VIP (30 días)",
                description="VIP Club Hardcore: +130 FRJ/día, 20% descuento, 2 slots de tabla, slot axolotito extra, comisión P2P 2% y marco animado legendario.",
                item_type=ItemType.CONSUMABLE,
                rarity=Rarity.LEGENDARY,
                price_axg=CONSUMABLE_PRICES["vip_axolite"],
                price_gal=0.0,
                max_supply=999999,
                is_active=True,
                item_metadata={"duration_days": 30, "is_vip": True, "vip_tier": "axolite"}
            ),
            ItemCatalog(
                name="Cápsula Bronce",
                description="Una cápsula sorpresa tier bronce. Contiene un premio aleatorio.",
                item_type=ItemType.CONSUMABLE,
                rarity=Rarity.COMMON,
                price_axg=0.0,
                price_gal=1500.0,
                max_supply=999999,
                is_active=True,
                item_metadata={"slot": "consumable", "capsule_tier": "bronce"}
            ),
            ItemCatalog(
                name="Cápsula Plata",
                description="Una cápsula sorpresa tier plata. Mejores premios que la bronce.",
                item_type=ItemType.CONSUMABLE,
                rarity=Rarity.RARE,
                price_axg=0.0,
                price_gal=5000.0,
                max_supply=999999,
                is_active=True,
                item_metadata={"slot": "consumable", "capsule_tier": "plata"}
            ),
            ItemCatalog(
                name="Cápsula Oro",
                description="Una cápsula sorpresa tier oro. Los mejores premios y mayor chance de legendary.",
                item_type=ItemType.CONSUMABLE,
                rarity=Rarity.EPIC,
                price_axg=0.0,
                price_gal=20000.0,
                max_supply=999999,
                is_active=True,
                item_metadata={"slot": "consumable", "capsule_tier": "oro"}
            ),

            # --- TABLAS DE JUEGO (BOARD) ---
            ItemCatalog(
                name="Tabla Clásica de Axolotto",
                description="La tabla de lotería tradicional de 16 casillas para jugar y divertirte.",
                item_type=ItemType.BOARD,
                rarity=Rarity.COMMON,
                price_axg=BOARD_PRICES["clasica"]["axg"],
                price_gal=BOARD_PRICES["clasica"]["gal"],
                max_supply=999999,
                is_active=True,
                item_metadata={"bonus_luck": 0.0, "bonus_payout": 1.0}
            ),
            ItemCatalog(
                name="Tabla de la Suerte",
                description="Tabla especial con aura de trébol que otorga +10% de Suerte.",
                item_type=ItemType.BOARD,
                rarity=Rarity.RARE,
                price_axg=BOARD_PRICES["suerte"]["axg"],
                price_gal=BOARD_PRICES["suerte"]["gal"],
                max_supply=999999,
                is_active=True,
                item_metadata={"bonus_luck": 10.0, "bonus_payout": 1.0}
            ),
            ItemCatalog(
                name="Tabla Pro de Plasma",
                description="Una tabla cibernética avanzada de alta tecnología que aumenta un 20% las ganancias.",
                item_type=ItemType.BOARD,
                rarity=Rarity.EPIC,
                price_axg=BOARD_PRICES["plasma"]["axg"],
                price_gal=BOARD_PRICES["plasma"]["gal"],
                max_supply=999999,
                is_active=True,
                item_metadata={"bonus_luck": 0.0, "bonus_payout": 1.2}
            ),
            ItemCatalog(
                name="Tabla Cósmica Animada",
                description="Tablero con animaciones de fondo, efectos auditivos estelares y cosmético dorado.",
                item_type=ItemType.BOARD,
                rarity=Rarity.LEGENDARY,
                price_axg=BOARD_PRICES["cosmica"]["axg"],
                price_gal=BOARD_PRICES["cosmica"]["gal"],
                max_supply=999999,
                is_active=True,
                item_metadata={"bonus_luck": 0.0, "bonus_payout": 1.0, "is_cosmetic": True}
            ),
            ItemCatalog(
                name="Upgrade de Board Slots",
                description="Desbloquea permanentemente un espacio extra para tus tableros activos.",
                item_type=ItemType.CONSUMABLE,
                rarity=Rarity.RARE,
                price_axg=CONSUMABLE_PRICES["upgrade_board_slots"],
                price_gal=0.0,
                max_supply=999999,
                is_active=True,
                item_metadata={"is_upgrade": True}
            ),

            # --- PAQUETES DE DIVISAS (AXF a FRJ) ---
            ItemCatalog(
                name="Paquete Frijolitos Común",
                description="Contiene 100 Frijolitos para cambiar o comprar.",
                item_type=ItemType.CURRENCY_PACK,
                rarity=Rarity.COMMON,
                price_axg=10.0,
                is_active=False,
                item_metadata={"gal_amount": 100.0}
            ),
            ItemCatalog(
                name="Paquete Frijolitos Abundante",
                description="Contiene 550 Frijolitos. ¡Bono de +10% FRJ extra!",
                item_type=ItemType.CURRENCY_PACK,
                rarity=Rarity.RARE,
                price_axg=50.0,
                is_active=False,
                item_metadata={"gal_amount": 550.0}
            ),
            ItemCatalog(
                name="Paquete Frijolitos Imperial",
                description="Contiene 1,200 Frijolitos. ¡Bono de +20% FRJ extra!",
                item_type=ItemType.CURRENCY_PACK,
                rarity=Rarity.EPIC,
                price_axg=100.0,
                is_active=False,
                item_metadata={"gal_amount": 1200.0}
            ),
            ItemCatalog(
                name="Súper Carga de Frijolitos",
                description="Contiene 6,500 Frijolitos. ¡Bono de +30% FRJ extra!",
                item_type=ItemType.CURRENCY_PACK,
                rarity=Rarity.LEGENDARY,
                price_axg=500.0,
                is_active=False,
                item_metadata={"gal_amount": 6500.0}
            ),

            # --- ACCESORIOS (Para Gashapón) ---
            ItemCatalog(
                name="Gorrita de Pescador",
                description="Una gorrita clásica que protege los ojos del Axolotito. Otorga +5.0 de Concentración.",
                item_type=ItemType.ACCESSORY,
                rarity=Rarity.COMMON,
                is_active=True,
                is_sellable=True,
                item_metadata={"slot": "head", "bonus_focus": 5.0}
            ),
            ItemCatalog(
                name="Gafas de Sol Neón",
                description="Estilo puro de club de playa. Otorga +15.0 de Concentración y reduce -5.0 de Salinidad.",
                item_type=ItemType.ACCESSORY,
                rarity=Rarity.RARE,
                is_active=True,
                is_sellable=True,
                item_metadata={"slot": "eyes", "bonus_focus": 15.0, "bonus_salinity": -5.0}
            ),
            ItemCatalog(
                name="Capa de Alga Sagrada",
                description="Tejida a mano por ancianos del charco. Otorga +15.0 de Suerte y +5.0 de Sabiduría.",
                item_type=ItemType.ACCESSORY,
                rarity=Rarity.EPIC,
                is_active=True,
                is_sellable=True,
                item_metadata={"slot": "body", "bonus_luck": 15.0, "bonus_wisdom": 5.0}
            ),
            ItemCatalog(
                name="Corona de Rey Ajolote",
                description="Un artefacto ancestral dorado. Otorga +25.0 de Suerte y +10.0 de Carisma.",
                item_type=ItemType.ACCESSORY,
                rarity=Rarity.LEGENDARY,
                is_active=True,
                is_sellable=True,
                item_metadata={"slot": "head", "bonus_luck": 25.0, "bonus_charisma": 10.0}
            ),
            ItemCatalog(
                name="Flotador de Patito",
                description="Perfecto para nadadores amateur. Restaura estamina y aumenta la estamina máxima en +15.",
                item_type=ItemType.ACCESSORY,
                rarity=Rarity.COMMON,
                is_active=True,
                is_sellable=True,
                item_metadata={"slot": "body", "bonus_stamina": 15}
            ),
            ItemCatalog(
                name="Monóculo Intelectual",
                description="Para Axolotitos que disfrutan de la lectura y el marcado preciso de cartas. Otorga +15.0 de Sabiduría y +5.0 de Concentración.",
                item_type=ItemType.ACCESSORY,
                rarity=Rarity.RARE,
                is_active=True,
                is_sellable=True,
                item_metadata={"slot": "eyes", "bonus_wisdom": 15.0, "bonus_focus": 5.0}
            ),

            # --- NATURALEZAS (NATURE) ---
            ItemCatalog(
                name="Naturaleza: Glotón",
                description="Este Axolotito come sin parar. Su energía es legendaria pero su concentración sufre.",
                item_type=ItemType.CONSUMABLE,
                rarity=Rarity.COMMON,
                price_axg=0.0,
                price_gal=0.0,
                max_supply=999999,
                is_active=False,
                item_metadata={"nature": "gloton", "stamina_food_bonus_pct": 30, "focus_modifier": -10}
            ),
        ]

        # Hacer upsert dinámico matching por name y fase (si existe)
        for item in items_to_seed:
            existing = None
            item_fase = item.item_metadata.get("fase") if item.item_metadata else None
            candidates = session.exec(select(ItemCatalog).where(ItemCatalog.name == item.name)).all()
            for cand in candidates:
                cand_fase = cand.item_metadata.get("fase") if cand.item_metadata else None
                if cand_fase == item_fase:
                    existing = cand
                    break
            
            if existing:
                existing.description = item.description
                existing.item_type = item.item_type
                existing.rarity = item.rarity
                existing.price_axg = item.price_axg
                existing.price_gal = item.price_gal
                existing.is_active = item.is_active
                existing.is_sellable = item.is_sellable
                existing.max_supply = item.max_supply
                existing.max_per_user = item.max_per_user
                existing.item_metadata = item.item_metadata
                session.add(existing)
            else:
                session.add(item)
                
        session.commit()
        print(f"✅ ¡Catálogo actualizado con éxito (se sembraron/actualizaron {len(items_to_seed)} items)!")

if __name__ == "__main__":
    run_seed()