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
from app.models.items import ItemCatalog, ItemType

def run_fix():
    print("Iniciando la corrección de metadatos en el catálogo...")
    with Session(engine) as session:
        items = session.exec(select(ItemCatalog)).all()
        for item in items:
            # Si ya tiene algo en item_metadata, podemos saltarlo o forzar
            meta = {}
            if "Gotas" in item.name:
                meta = {"duration_hours": 12, "target": "single"}
            elif "Lámpara" in item.name:
                meta = {"duration_hours": 24, "target": "single"}
            elif "Génesis" in item.name:
                meta = {"fase": 1, "tag": "Genesis"}
            elif "Expansión" in item.name:
                meta = {"fase": 2}
            elif "Retail" in item.name:
                meta = {"fase": 3}
            elif "Booster Fundador" in item.name:
                meta = {"fase": 1, "cards_per_booster": 7, "rng_type": "pure"}
            elif "Booster Dinámico" in item.name:
                meta = {"fase": 2, "cards_per_booster": 7, "guaranteed_rare": True}
            elif "Booster Estable" in item.name:
                meta = {"fase": 3, "cards_per_booster": 7, "guaranteed_rare": True}
            elif "Tabla Clásica" in item.name:
                meta = {"bonus_luck": 0.0, "bonus_payout": 1.0}
            elif "Tabla de la Suerte" in item.name:
                meta = {"bonus_luck": 10.0, "bonus_payout": 1.0}
            elif "Tabla Pro" in item.name:
                meta = {"bonus_luck": 0.0, "bonus_payout": 1.2}
            elif item.item_type == ItemType.CARD:
                # Intentamos buscar el número de lotería
                meta = {"first_edition": True}
            
            if meta:
                item.item_metadata = meta
                session.add(item)
                print(f"🔧 Actualizando {item.name} con metadatos: {meta}")

        session.commit()
        print("✅ Corrección de metadatos completada exitosamente.")

if __name__ == "__main__":
    run_fix()
