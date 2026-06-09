"""
f2p_service.py — Lógica de micro-recompensas y huevo durmiente para jugadores F2P.

El jugador F2P recibe un huevo durmiente desde el primer día.
Acumula Fragmentos Astrales viendo partidas; el huevo reacciona visualmente
en 5 etapas según cuántos fragmentos tiene acumulados.

Recompensas por ver partidas:
  - Ganó la tabla espejo: 3 FRJ + 2 fragmentos
  - No ganó: 0.1 FRJ + 1 fragmento

Hay un tope diario de FRJ para no sustituir la economía de pago.
"""

import random as _random

_rng = _random.SystemRandom()


# Textos de burbuja de sueño por etapa (vacío en etapa 0)
_DREAM_BUBBLES: dict[int, list[str]] = {
    0: [],
    1: ["...lotería...", "...mis cartas..."],
    2: ["...el gritón...", "...voy..."],
    3: ["...ya casi...", "...el Cenote me llama..."],
    4: ["...puedo sentirte...", "...ya casi nazco..."],
    5: ["¡Despierto pronto!", "¡El Cenote me está llamando!"],
}


class F2PService:
    """Servicio de economía F2P: huevo durmiente y micro-recompensas."""

    DAILY_CAP_FRJ: float = 10.0
    DAILY_CAP_FRAGS: int = 10
    FRAGMENTS_TO_HATCH: int = 100

    # Umbrales de fragmentos para cada etapa del huevo
    _STAGE_THRESHOLDS: list[int] = [0, 20, 40, 60, 80, 100]

    # Recompensas base
    _WIN_FRJ: float = 3.0
    _WIN_FRAGS: int = 2
    _LOSS_FRJ: float = 0.1
    _LOSS_FRAGS: int = 1

    def egg_reaction_stage(self, fragments: int) -> int:
        """
        Retorna la etapa de reacción del huevo (0–5).

          0: 0–19 frags    — quieto
          1: 20–39 frags   — primer temblor
          2: 40–59 frags   — burbujas
          3: 60–79 frags   — brilla
          4: 80–99 frags   — brilla intenso
          5: 100+ frags    — listo para eclosionar
        """
        if fragments >= 100:
            return 5
        if fragments >= 80:
            return 4
        if fragments >= 60:
            return 3
        if fragments >= 40:
            return 2
        if fragments >= 20:
            return 1
        return 0

    def get_dream_bubble(self, fragments: int) -> str:
        """
        Retorna una frase de burbuja de sueño según la etapa actual del huevo.
        Devuelve cadena vacía en etapa 0.
        """
        stage = self.egg_reaction_stage(fragments)
        options = _DREAM_BUBBLES.get(stage, [])
        if not options:
            return ""
        return _rng.choice(options)

    def under_daily_cap(self, earned_today: float) -> bool:
        """True si el jugador todavía no ha alcanzado el tope diario de FRJ."""
        return earned_today < self.DAILY_CAP_FRJ

    def watch_game_reward(self, won: bool) -> dict:
        """
        Calcula las recompensas por ver una partida.

        Args:
            won: True si el jugador ganó la tabla espejo observada.

        Returns:
            {"frj": float, "fragments": int}
        """
        if won:
            return {"frj": self._WIN_FRJ, "fragments": self._WIN_FRAGS}
        return {"frj": self._LOSS_FRJ, "fragments": self._LOSS_FRAGS}
