"""Tipos Pydantic validados para montos monetarios (VULN-06).

Usage en schemas de endpoints:
    from app.core.economy_types import AxfAmount, FrjAmount

    class DepositRequest(BaseModel):
        amount: AxfAmount          # acepta float humano o int interno, siempre da int
        currency: CurrencyType

    class WalletResponse(BaseModel):
        axofichas: AxfAmount
        frijolitos: FrjAmount

Los tipos convierten automáticamente:
  - Entrada:  float (humano-legible) → int (unidad mínima)
  - Salida:   int → float (para display en JSON)
"""

from typing import Any
from pydantic import BeforeValidator, PlainSerializer
from typing_extensions import Annotated
from app.core.config import AXF_DECIMALS_BACKEND, FRJ_DECIMALS_BACKEND

_AXF = 10 ** AXF_DECIMALS_BACKEND
_FRJ = 10 ** FRJ_DECIMALS_BACKEND


# ── Validators (input: float|int → int interno) ────────────────────────

def _validate_axf(v: Any) -> int:
    """Convierte AXF humano-legible (float) o unidad mínima (int) a int interno."""
    if isinstance(v, int):
        if v < 0:
            raise ValueError("AXF amount cannot be negative")
        return v
    if isinstance(v, float):
        if v < 0:
            raise ValueError("AXF amount cannot be negative")
        return int(round(v * _AXF))
    raise TypeError(f"Expected float or int for AXF amount, got {type(v).__name__}")


def _validate_frj(v: Any) -> int:
    """Convierte FRJ humano-legible (float) o unidad mínima (int) a int interno."""
    if isinstance(v, int):
        if v < 0:
            raise ValueError("FRJ amount cannot be negative")
        return v
    if isinstance(v, float):
        if v < 0:
            raise ValueError("FRJ amount cannot be negative")
        return int(round(v * _FRJ))
    raise TypeError(f"Expected float or int for FRJ amount, got {type(v).__name__}")


# ── Serializers (output: int interno → float display) ──────────────────

def _serialize_axf(v: int) -> float:
    """Convierte AXF unidad mínima → float para JSON response."""
    if not isinstance(v, int):
        return float(v)
    return v / _AXF


def _serialize_frj(v: int) -> float:
    """Convierte FRJ unidad mínima → float para JSON response."""
    if not isinstance(v, int):
        return float(v)
    return v / _FRJ


# ── Tipos Annotated ────────────────────────────────────────────────────

AxfAmount = Annotated[
    int,
    BeforeValidator(_validate_axf),
    PlainSerializer(_serialize_axf, return_type=float),
]

FrjAmount = Annotated[
    int,
    BeforeValidator(_validate_frj),
    PlainSerializer(_serialize_frj, return_type=float),
]
