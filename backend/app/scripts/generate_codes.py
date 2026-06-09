"""
Generate promo codes for Axolotto corcholatas.

Usage:
    python app/scripts/generate_codes.py \
        --batch feria-2026-01 \
        --count 200 \
        --booster-id 3 \
        --output codes.csv
"""
import sys
import os
import argparse
import csv
import secrets
from datetime import datetime

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
from app.models.items import ItemCatalog
from app.models.promo import PromoCode

# No visually ambiguous chars: excludes 0/O, 1/I, 5/S
ALPHABET = "ABCDEFGHJKLMNPQRTUVWXYZ23467889"


def generate_code() -> str:
    return "AXL-" + "".join(secrets.choice(ALPHABET) for _ in range(4))


def main():
    parser = argparse.ArgumentParser(description="Generate Axolotto promo codes")
    parser.add_argument("--batch", required=True, help="Batch label, e.g. feria-2026-01")
    parser.add_argument("--count", type=int, required=True, help="Number of codes to generate")
    parser.add_argument("--booster-id", type=int, required=True, help="ItemCatalog ID for the booster reward")
    parser.add_argument("--output", default="codes.csv", help="Output CSV file path")
    args = parser.parse_args()

    with Session(engine) as session:
        item = session.get(ItemCatalog, args.booster_id)
        if not item:
            print(f"Error: ItemCatalog id={args.booster_id} not found.")
            sys.exit(1)
        if not item.is_active:
            print(f"Warning: Item '{item.name}' is inactive. Continuing anyway.")

        # Collect existing codes to avoid collisions
        existing = {row.code for row in session.exec(select(PromoCode)).all()}

        codes = []
        attempts = 0
        while len(codes) < args.count:
            attempts += 1
            if attempts > args.count * 20:
                print("Error: Too many collision attempts. Alphabet exhausted?")
                sys.exit(1)
            candidate = generate_code()
            if candidate not in existing and candidate not in {c.code for c in codes}:
                promo = PromoCode(
                    code=candidate,
                    batch=args.batch,
                    reward_type="booster_pack",
                    reward_item_id=args.booster_id,
                    created_at=datetime.utcnow(),
                )
                codes.append(promo)

        for promo in codes:
            session.add(promo)
        session.commit()

    with open(args.output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["code", "batch", "reward_item_id", "item_name", "created_at"])
        writer.writeheader()
        for promo in codes:
            writer.writerow({
                "code": promo.code,
                "batch": promo.batch,
                "reward_item_id": promo.reward_item_id,
                "item_name": item.name,
                "created_at": promo.created_at.isoformat(),
            })

    print(f"Generated {len(codes)} codes for batch '{args.batch}' → {args.output}")
    print(f"Reward: {item.name} (id={item.id})")


if __name__ == "__main__":
    main()
