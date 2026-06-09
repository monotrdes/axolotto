"""
manual_game_service.py — Parámetros de entorno para el modo manual de Axolotto.

En modo manual el jugador controla el tablero directamente.
Los stats del Axolotito no mueven un bot — modulan el *entorno* de juego:

  Focus   → ventana de tiempo que la carta resaltada permanece activa
  Agility → delay entre cartas cantadas por el gritón (menor = más difícil)
  Stamina → número de pistas visuales disponibles en la partida
  Luck    → probabilidad de crítico si el jugador marca en el primer 30% de la ventana
  Salinity → afecta el RNG del pool de cartas (igual que en auto; sin cambios aquí)
"""

from dataclasses import dataclass, asdict


@dataclass
class ManualEnvParams:
    """Parámetros de entorno calculados a partir de los stats de un Axolotito."""
    highlight_window_ms: int   # Tiempo (ms) que la carta resaltada permanece activa
    griton_delay_ms: int       # Tiempo (ms) entre cada carta cantada por el gritón
    visual_hints: int          # Número de pistas visuales disponibles en la partida
    crit_window_ms: int        # 30 % de highlight_window_ms — marcar aquí activa prob. crítico


class ManualGameService:
    """Cálculo de parámetros de entorno manual a partir de stats del Axolotito."""

    # --- Rangos de stat ---
    FOCUS_MIN: float = 0.0
    FOCUS_MAX: float = 100.0
    WINDOW_MIN_MS: int = 1000   # focus=0  → ventana estrecha (difícil)
    WINDOW_MAX_MS: int = 4000   # focus=100 → ventana amplia (fácil)

    AGILITY_MIN: float = 0.0
    AGILITY_MAX: float = 100.0
    DELAY_MIN_MS: int = 800     # agility=0  → delay corto (rápido = difícil)
    DELAY_MAX_MS: int = 2500    # agility=100 → delay largo (lento = fácil)

    STAMINA_MIN: int = 50
    STAMINA_MAX: int = 200
    HINTS_MIN: int = 1          # stamina=50
    HINTS_MAX: int = 8          # stamina=200

    LUCK_MIN: float = 0.0
    LUCK_MAX: float = 100.0
    CRIT_PROB_MIN: float = 0.03  # luck=0   → 3 % de crítico
    CRIT_PROB_MAX: float = 0.50  # luck=100 → 50 % de crítico

    CRIT_WINDOW_RATIO: float = 0.30  # primero 30 % de la ventana activa el crítico

    # ------------------------------------------------------------------
    # Helpers internos
    # ------------------------------------------------------------------

    @staticmethod
    def _lerp(value: float, src_min: float, src_max: float, dst_min: float, dst_max: float) -> float:
        """Interpolación lineal de value en [src_min, src_max] → [dst_min, dst_max]."""
        if src_max == src_min:
            return dst_min
        t = (value - src_min) / (src_max - src_min)
        t = max(0.0, min(1.0, t))  # clamp
        return dst_min + t * (dst_max - dst_min)

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    @classmethod
    def fixed_params(cls) -> "ManualEnvParams":
        """
        Parámetros fijos para modo manual: el jugador ES el Axolotito.
        En modo manual NO se aplican modificadores de stat (spec §5).
        """
        return ManualEnvParams(
            highlight_window_ms=2000,
            griton_delay_ms=2000,
            visual_hints=3,
            crit_window_ms=600,
        )

    def get_env_params(self, focus: float, agility: float, stamina: int) -> ManualEnvParams:
        """
        Calcula los parámetros de entorno manual dados los stats del Axolotito.

        Args:
            focus:   stat_focus  (0–100)
            agility: stat_agility (0–100)
            stamina: stat_stamina (50–200)

        Returns:
            ManualEnvParams con los valores calculados.
        """
        highlight_window_ms = int(round(self._lerp(
            focus,
            self.FOCUS_MIN, self.FOCUS_MAX,
            self.WINDOW_MIN_MS, self.WINDOW_MAX_MS,
        )))

        griton_delay_ms = int(round(self._lerp(
            agility,
            self.AGILITY_MIN, self.AGILITY_MAX,
            self.DELAY_MIN_MS, self.DELAY_MAX_MS,
        )))

        visual_hints = int(round(self._lerp(
            stamina,
            self.STAMINA_MIN, self.STAMINA_MAX,
            self.HINTS_MIN, self.HINTS_MAX,
        )))

        crit_window_ms = int(round(highlight_window_ms * self.CRIT_WINDOW_RATIO))

        return ManualEnvParams(
            highlight_window_ms=highlight_window_ms,
            griton_delay_ms=griton_delay_ms,
            visual_hints=visual_hints,
            crit_window_ms=crit_window_ms,
        )

    def crit_probability(self, luck: float, marked_in_window: bool) -> float:
        """
        Retorna la probabilidad de crítico para este turno.

        Args:
            luck:             stat_luck (0–100)
            marked_in_window: True si el jugador marcó dentro del primer 30 % de la ventana

        Returns:
            0.0 si el jugador no marcó en la ventana crítica; de lo contrario,
            un float en [CRIT_PROB_MIN, CRIT_PROB_MAX] según el luck.
        """
        if not marked_in_window:
            return 0.0

        return self._lerp(
            luck,
            self.LUCK_MIN, self.LUCK_MAX,
            self.CRIT_PROB_MIN, self.CRIT_PROB_MAX,
        )

    def to_dict(self, params: ManualEnvParams) -> dict:
        """Serializa ManualEnvParams a un dict plano."""
        return asdict(params)
