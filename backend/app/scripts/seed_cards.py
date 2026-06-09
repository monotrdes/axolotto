import sys
import os

backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(backend_dir)

# Load environment variables from both root and backend .env files
from dotenv import load_dotenv
load_dotenv(os.path.join(backend_dir, "..", ".env"))
load_dotenv(os.path.join(backend_dir, ".env"))

# Adjust DATABASE_URL if running on the host machine (not inside Docker)
if not os.path.exists("/.dockerenv") and "DATABASE_URL" in os.environ:
    db_url = os.environ["DATABASE_URL"]
    if "@db_axolotto:5432" in db_url:
        os.environ["DATABASE_URL"] = db_url.replace("@db_axolotto:5432", "@127.0.0.1:5433")

from sqlmodel import Session, select
from app.database import engine
from app.models.items import ItemCatalog, ItemType, Rarity

def seed_cartas():
    nombres_cartas = [
        "El axolotl", "El diablito", "La Patrona", "El Godín", "La piñata", "La sirena", "El Trompo", 
        "La botella", "El molcajete", "El Chilaquil", "El aguacate", "El luchador", "El sombrero", 
        "La catrina", "El maíz", "La bandera", "El Acordeón", "La chancla", "El firulais", "El Michi", 
        "La mano", "Los Tenis", "La luna", "El colibrí", "La caguama", "El café", "El corazón", "La salsa", 
        "El Chamoy", "El camarón", "El papel picado", "El músico", "La araña", "El alebrije", "La estrella", 
        "La concha", "El mundo", "El taco", "El nopal", "El alacrán", "La rosa", "La calavera", "La campana", 
        "El cantarito", "El venado", "El sol", "El penacho", "La chalupa", "El vocho", "El pescado", 
        "La Cobija", "La maceta", "El Elote", "La Botarga"
    ]

    rarities_map = {
        "El axolotl": Rarity.LEGENDARY,
        "El alebrije": Rarity.LEGENDARY,
        "El sol": Rarity.LEGENDARY,
        
        "La catrina": Rarity.EPIC,
        "La bandera": Rarity.EPIC,
        "El colibrí": Rarity.EPIC,
        "La calavera": Rarity.EPIC,
        "El penacho": Rarity.EPIC,
        "El corazón": Rarity.EPIC,
        
        "El luchador": Rarity.RARE,
        "La luna": Rarity.RARE,
        "El músico": Rarity.RARE,
        "El mundo": Rarity.RARE,
        "El taco": Rarity.RARE,
        "El nopal": Rarity.RARE,
        "El alacrán": Rarity.RARE,
        "La rosa": Rarity.RARE,
        "El vocho": Rarity.RARE,
        "El pescado": Rarity.RARE,
        "La Cobija": Rarity.RARE,
        "El diablito": Rarity.RARE,
    }

    print("Iniciando la siembra/actualización de la Lotería Axolotto...")
    
    with Session(engine) as session:
        for i, nombre in enumerate(nombres_cartas):
            rarity = rarities_map.get(nombre, Rarity.COMMON)
            existing = session.exec(
                select(ItemCatalog)
                .where(ItemCatalog.item_type == ItemType.CARD)
                .where(ItemCatalog.name == nombre)
            ).first()

            if existing:
                existing.rarity = rarity
                existing.is_active = True
                existing.is_sellable = True
                existing.description = f"Carta oficial de la colección: {nombre}"
                existing.item_metadata = {"numero_loteria": i + 1, "first_edition": True}
                session.add(existing)
                print(f"🔧 Actualizando carta '{nombre}' -> rareza: {rarity.value}, numero_loteria: {i + 1}")
            else:
                carta = ItemCatalog(
                    name=nombre,
                    description=f"Carta oficial de la colección: {nombre}",
                    item_type=ItemType.CARD,
                    rarity=rarity,
                    price_axg=0,
                    is_active=True,
                    is_sellable=True,
                    item_metadata={"numero_loteria": i + 1, "first_edition": True}
                )
                session.add(carta)
                print(f"✨ Creando carta '{nombre}' -> rareza: {rarity.value}")
        
        session.commit()
        print("✅ ¡Catálogo de cartas de la Lotería Axolotto actualizado con éxito!")

if __name__ == "__main__":
    seed_cartas()