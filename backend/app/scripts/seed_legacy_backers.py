"""
Script para sembrar la tabla de Backers de 2021.
Ejecutar dentro del contenedor: python app/scripts/seed_legacy_backers.py

Agrega aquí los emails y/o wallets de los inversores originales del proyecto.
El campo 'eggs_owed' es el número de Webitos prometidos a cada backer.
"""
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
from app.models.items import LegacyBacker

# ============================================================
# LISTA DE BACKERS 2021 — Edita esta lista con los datos reales
# Usa email_or_wallet en minúsculas
# ============================================================
LEGACY_BACKERS = [
    # --- CUENTA DE PRUEBAS / DESARROLLO ---
    {"email_or_wallet": "monotr.des@gmail.com",   "eggs_owed": 3, "notes": "Dev account (pruebas)"},

    # --- BACKERS REALES 2021 ---
    # Agrega tus backers aquí con su email o wallet address:
    # {"email_or_wallet": "ejemplo@email.com",    "eggs_owed": 1, "notes": "Backer original"},
    # {"email_or_wallet": "0xABCDEF...",           "eggs_owed": 2, "notes": "Backer wallet"},
]

def run_seed():
    print("🥚 Iniciando siembra de Backers 2021...")
    inserted = 0
    updated = 0

    with Session(engine) as session:
        for data in LEGACY_BACKERS:
            key = data["email_or_wallet"].lower()
            existing = session.exec(
                select(LegacyBacker).where(LegacyBacker.email_or_wallet == key)
            ).first()

            if existing:
                # Actualizar si cambió la cantidad prometida
                if existing.eggs_owed != data["eggs_owed"]:
                    existing.eggs_owed = data["eggs_owed"]
                    session.add(existing)
                    updated += 1
                    print(f"  🔄 Actualizado: {key} → {data['eggs_owed']} webitos")
                else:
                    print(f"  ⏭️  Sin cambios: {key}")
            else:
                backer = LegacyBacker(
                    email_or_wallet=key,
                    eggs_owed=data["eggs_owed"],
                    eggs_claimed=0,
                    notes=data.get("notes", "")
                )
                session.add(backer)
                inserted += 1
                print(f"  ✅ Insertado: {key} → {data['eggs_owed']} webitos")

        session.commit()

    print(f"\n🎉 Listo. {inserted} insertados, {updated} actualizados.")

if __name__ == "__main__":
    run_seed()
