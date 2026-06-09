"""
pila_service.py — Mecanica del stat PILA (stamina).

PILA determina la energia maxima y la velocidad de recuperacion al dormir.
Mas PILA = duerme menos tiempo antes de estar listo de nuevo.
"""


def recovery_multiplier(pila: float) -> float:
    """
    Multiplicador del tiempo de sueno segun PILA (rango 50-200).
    sleep_mult = clamp(1.0 - ((pila - 50) / 300), 0.35, 1.0)

    PILA 50  -> 1.0  (tiempo completo)
    PILA 100 -> ~0.83
    PILA 200 -> 0.5
    """
    raw = 1.0 - ((pila - 50.0) / 300.0)
    return max(0.35, min(1.0, raw))
