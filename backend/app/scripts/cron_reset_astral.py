import sys
import os

# Adjust path to find the application modules
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(backend_dir)

# Load environment variables
from dotenv import load_dotenv
load_dotenv(os.path.join(backend_dir, "..", ".env"))
load_dotenv(os.path.join(backend_dir, ".env"))

# Adjust DATABASE_URL if running on the host machine
if not os.path.exists("/.dockerenv") and "DATABASE_URL" in os.environ:
    db_url = os.environ["DATABASE_URL"]
    if "@db_axolotto:5432" in db_url:
        os.environ["DATABASE_URL"] = db_url.replace("@db_axolotto:5432", "@127.0.0.1:5433")

from sqlmodel import Session, select
from app.database import engine
from app.models.items import ItemCatalog

def run_reset():
    print("Iniciando reactivación anual del Webito Astral (Limitado)...")
    
    with Session(engine) as session:
        statement = select(ItemCatalog).where(ItemCatalog.name == "Webito Astral (Limitado)")
        item = session.exec(statement).first()
        
        if item:
            if not item.is_active:
                item.is_active = True
                session.add(item)
                session.commit()
                print("✅ Webito Astral (Limitado) ha sido reactivado en el catálogo.")
            else:
                print("ℹ️ El Webito Astral (Limitado) ya se encuentra activo en el catálogo.")
        else:
            print("⚠️ No se encontró el Webito Astral (Limitado) en el catálogo.")

if __name__ == "__main__":
    run_reset()
