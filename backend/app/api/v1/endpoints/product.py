"""Public, non-sensitive product policy used by all clients."""

from fastapi import APIRouter

from app.core.product_policy import public_product_policy


router = APIRouter()


@router.get("/policy")
def get_product_policy() -> dict:
    return public_product_policy()

