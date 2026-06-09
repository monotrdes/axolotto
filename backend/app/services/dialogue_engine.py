"""
dialogue_engine.py — Motor de diálogos dinámico para el universo Axolotto.

El Webito tiene una personalidad (nature) que afecta el tono del diálogo,
no el contenido. Todas las líneas usan modismos mexicanos y referencias al
universo acuático/lotería del juego.

Personalidades:
  lucky / hyperactive  → exclamativo, mucho entusiasmo, signos de admiración
  salty / shy          → reservado, humor seco, auto-compasivo
  methodical           → analítico, menciona números y probabilidades
"""

from enum import Enum
import random
from typing import Optional


class DialogueContext(str, Enum):
    TUTORIAL_PHASE_1 = "tutorial_phase_1"            # Salinidad
    TUTORIAL_PHASE_2 = "tutorial_phase_2"            # Focus + Agility
    TUTORIAL_PHASE_3 = "tutorial_phase_3"            # Luck + Stamina
    TUTORIAL_FOCUS_MOMENT = "tutorial_focus_moment"  # Intervención manual (focus)
    TUTORIAL_AGILITY_MOMENT = "tutorial_agility_moment"  # Intervención manual (agility) — DEPRECATED (stat retirado; mantenido por tutorial_service.py)
    TUTORIAL_LUCK_MOMENT = "tutorial_luck_moment"    # Cheat Astral (luck)
    GAME_START = "game_start"
    GAME_WIN = "game_win"
    GAME_LOSE = "game_lose"
    GAME_CRIT = "game_crit"
    INTER_AXO_VS_BOT_1 = "inter_axo_vs_bot_1"
    INTER_AXO_VS_BOT_5 = "inter_axo_vs_bot_5"
    INTER_AXO_VS_HUMAN = "inter_axo_vs_human"
    GRITÓN_CARD_CALLED = "gritón_card_called"


_rng = random.SystemRandom()

# ---------------------------------------------------------------------------
# Banco de líneas por stat y banda de valor
# ---------------------------------------------------------------------------

# Estructura: {stat: {banda: [linea1, linea2, linea3]}}
# Bandas: "low" (0-25), "mid" (25-50), "high" (50-80), "peak" (80-100)

_STAT_LINES: dict[str, dict[str, list[str]]] = {
    "salinity": {
        "low": [
            "Las aguas del Cenote te son amigables, casi ni salinidad tienes.",
            "Tu cascarón huele a agua dulce del manantial, eso es muy buena senal.",
            "Poca sal en tus branquias: eres un Axolotito del montón, pero del montón bueno.",
        ],
        "mid": [
            "Un poco de sal en tu ADN... el Cenote te ha probado y te ha encontrado regular.",
            "Tus branquias detectan salinidad moderada. Ni tan pez ni tan ajolote.",
            "La Sirena de la Lotería te mira con ojo crítico: tienes sal, pero tampoco exageres.",
        ],
        "high": [
            "Oof, tienes bastante sal. El Cenote te va a poner a sudar... o a sudar algas.",
            "Tus branquias están más saladas que el Catrín después de perder en lotería.",
            "Con esa salinidad, el Gritón va a gritar tu nombre con sospecha.",
        ],
        "peak": [
            "¡Agua del Mar Muerto! Tu salinidad está por las nubes, Axolotito.",
            "Tus branquias prácticamente lloran sal. El Cenote te rechaza... por ahora.",
            "Salinidad máxima detectada. El Catrín se ríe, pero tú puedes revertirlo.",
        ],
    },
    "luck": {
        "low": [
            "La suerte no es tu fuerte, campeón. Pero el esfuerzo compensa, dicen por ahí.",
            "El Sol de la Lotería no te alumbra mucho... aún. Sigue jugando.",
            "Tus gemas de alga brillan poco, pero hasta el ajolote más seco encuentra su charco.",
        ],
        "mid": [
            "Suerte regular, como encontrar una GAL en la bolsa del pantalón.",
            "La Rosa de la Lotería te sonríe a medias. No está mal para empezar.",
            "Tienes suerte suficiente para no ahogarte, pero no para flotar solo.",
        ],
        "high": [
            "Las branquias se te erizan de buena vibra. La suerte viene en olas.",
            "El Cenote te derrama brillos de GAL. Buena suerte, Axolotito.",
            "¡El Sol te toca directo! Tus drops van a llover como temporada de lluvias.",
        ],
        "peak": [
            "¡Suerte legendaria! El Catrín te hace una reverencia en señal de respeto.",
            "¡La Sirena canta para ti! Drops, gemas y cartas de primera edición te esperan.",
            "Máxima fortuna detectada. Hasta el Gritón grita tu nombre con admiración.",
        ],
    },
    "focus": {
        "low": [
            "Tu concentración... existe, creo. En algún lugar del cascarón.",
            "El Gritón grita, tú volteas a ver las algas. Concentración: poquísima.",
            "Las cartas de Lotería pasan frente a ti y tú estás pensando en el Cenote.",
        ],
        "mid": [
            "Concentración moderada. No pierdes el hilo, pero tampoco lo tensas mucho.",
            "Tus ojos siguen las cartas del Gritón con relativa atención. Vas bien.",
            "Focus de estudiante que puso el despertador: despierto, pero apenas.",
        ],
        "high": [
            "Tu concentración es digna de un campeón de Lotería. El Gritón te teme.",
            "Las branquias vibran cuando hay cartas en juego. Tu focus es envidioso.",
            "Detectas los patrones del Cenote como pocos. Concentración de élite.",
        ],
        "peak": [
            "¡Concentración absoluta! Ni el Catrín puede distraerte con sus chistes.",
            "El Gritón grita y tú ya marcaste la carta antes de que termine la frase.",
            "Focus máximo: tu mente es el Cenote mismo, profundo y sin distracciones.",
        ],
    },
    "stamina": {
        "low": [
            "Energía escasa. Tus branquias apenas se mueven, Axolotito.",
            "El Cenote te cansa rápido. Descansa, come algas, vuelve.",
            "Tus GAL se gastan antes de que empiece la partida. Cuídate.",
        ],
        "mid": [
            "Energía decente. Aguantas unas cuantas rondas de Lotería sin despeinarte.",
            "Tus branquias bombean bien a media jornada. No es mal comienzo.",
            "Stamina regular: como un taco de canasta, te sostiene pero no vuelas.",
        ],
        "high": [
            "¡Buena energía! Tus branquias trabajan horas extra sin quejarse.",
            "El Cenote te carga con poder. Aguantas más partidas que el promedio.",
            "Tus GAL se regeneran rápido. Eres una máquina de Lotería, Axolotito.",
        ],
        "peak": [
            "¡Stamina de leyenda! El Catrín ya firmó tu contrato de deportista élite.",
            "Tus branquias no se cansan nunca. ¿Duermes? ¿Comes? ¿O puras partidas?",
            "Energía máxima: podrías jugar Lotería por el Cenote entero y seguir de pie.",
        ],
    },
}

# ---------------------------------------------------------------------------
# Líneas de contexto de tutorial
# ---------------------------------------------------------------------------

_TUTORIAL_LINES: dict[str, dict[str, list[str]]] = {
    "tutorial_phase_1": {
        "neutral": [
            "Tu cascarón empieza a vibrar... el Cenote está midiendo tu salinidad.",
            "Fase 1: El agua del Cenote prueba tu sal. ¿Cuánta aguantas?",
            "Las algas murmuran: tu Axolotito está aprendiendo a leer el agua.",
        ]
    },
    "tutorial_phase_2": {
        "neutral": [
            "Fase 2: La concentración y la agilidad se forjan en las cartas del Gritón.",
            "El Gritón ya calienta la voz. ¿Están listos tus ojos para las cartas?",
            "Tu cascarón brilla con focus. Las algas te guían hacia El Catrín.",
        ]
    },
    "tutorial_phase_3": {
        "neutral": [
            "Fase 3: La suerte del Cenote y tu energía se ponen a prueba.",
            "El Cenote gira sus remolinos de GAL. ¿Tienes la stamina para aguantar?",
            "La Sirena susurra secretos de suerte. Escucha bien, Axolotito.",
        ]
    },
    "tutorial_focus_moment": {
        "neutral": [
            "¡Momento de concentración! La carta de La Rosa aparece. ¡Márcala ahora!",
            "El Gritón grita El Sol, ¿lo ves? ¡Tu focus entra en acción!",
            "¡Intervención manual! Dirige tus branquias hacia la carta correcta.",
        ]
    },
    "tutorial_agility_moment": {
        "neutral": [
            "¡Rápido! El Gritón ya está a punto de gritar. ¡Mueve esas aletas!",
            "Momento de agilidad: marca la carta antes de que el agua se enfríe.",
            "¡La corriente cambia! Tu agilidad decide si marcas o pierdes la carta.",
        ]
    },
    "tutorial_luck_moment": {
        "neutral": [
            "¡Fragmento Astral activado! La suerte del Cenote interviene a tu favor.",
            "El Cenote revela un secreto: usa el Fragmento Astral y gira la suerte.",
            "¡Cheat Astral disponible! El universo acuático te da una mano de GAL.",
        ]
    },
}

# ---------------------------------------------------------------------------
# Líneas de evento de juego
# ---------------------------------------------------------------------------

_GAME_EVENT_LINES: dict[str, list[str]] = {
    "win": [
        "¡Lotería! El Cenote celebra contigo. Las GAL llueven sobre tu tablero.",
        "¡Ganaste! El Gritón grita tu nombre con orgullo.",
        "¡Victoria! La Sirena canta y el Catrín te felicita a regañadientes.",
        "¡Eres el campeón del Cenote! Tus branquias brillan de orgullo.",
    ],
    "lose": [
        "Perdiste... pero el Cenote guarda tus lecciones para la próxima.",
        "El Catrín gana esta vez. Pero tú vuelves más fuerte, Axolotito.",
        "Ni modo, se fue la partida. Las algas ya preparan tu revancha.",
        "Derrota temporal. El Gritón te grita: ¡la próxima es la tuya!",
    ],
    "crit": [
        "¡Golpe crítico! El Cenote vibra con tu poder.",
        "¡Las branquias explotan de energía! Crítico total.",
        "¡El Catrín ni lo vio venir! Crítico demoledor.",
        "¡La Sirena ríe con ganas! Ese golpe crítico sacudió el Cenote.",
    ],
}

# ---------------------------------------------------------------------------
# Líneas de karma
# ---------------------------------------------------------------------------

_KARMA_LINES: dict[str, list[str]] = {
    "lucky": [
        "¡Tu karma es SUERTUDO! El Cenote te besa en las branquias.",
        "¡Karma de suerte revelado! La Sirena ya tejió tu destino dorado.",
        "¡Eres un Axolotito de la buena vibra! Las GAL te persiguen como sombra.",
    ],
    "salty": [
        "Tu karma es SALADO... pero la sal da sabor a la vida, no lo olvides.",
        "El Cenote te dio karma salty. El Catrín ya sabe que eres de los que no se rinden.",
        "Karma salado detectado. No es mala suerte, es carácter. Adelante, Axolotito.",
    ],
}

# ---------------------------------------------------------------------------
# Líneas inter-Axo (combate/competencia)
# ---------------------------------------------------------------------------

_INTER_AXO_LINES: dict[str, list[str]] = {
    "bot_1": [
        "Tu primer oponente digital te mira desde el otro lado del Cenote.",
        "Un bot novato entra al juego. El Gritón lanza la primera carta.",
        "Primera batalla en el Cenote. El bot abre sus tablillas y tú abres tus branquias.",
    ],
    "bot_5": [
        "El quinto bot consecutivo... ¡este Cenote se va a quedar sin competencia!",
        "Cinco bots caídos o por caer. El Gritón ya está ronco de gritar tus victorias.",
        "Racha de cinco contra bots. Las algas te corean. El Catrín toma nota.",
    ],
    "human": [
        "¡Jugador humano detectado! El Cenote se pone serio.",
        "Enfrente tuyo hay un humano de carne y branquias. ¡Que empiece la lotería!",
        "Oponente humano en la tablilla. El Gritón sube el volumen. ¡Todo o nada!",
    ],
}

# ---------------------------------------------------------------------------
# Líneas del Gritón según agilidad
# ---------------------------------------------------------------------------

_GRITÓN_LINES: dict[str, list[str]] = {
    "slow": [
        "El Gritón gruñe: '¡Reacciona más rápido, Axolotito!'",
        "'¡Esa carta ya pasó!' — grita el Gritón mientras tú buscas la ficha.",
        "El Gritón suspira hondo: 'La siguiente vida, espero que con más agilidad.'",
    ],
    "medium": [
        "El Gritón asiente: 'No está mal. Pero puedes ser más rápido.'",
        "'¡Ahí mero!' — El Gritón celebra a medias tu velocidad.",
        "El Gritón te lanza una mirada: 'Bien... pero El Catrín hubiera sido más rápido.'",
    ],
    "fast": [
        "'¡Ese sí es un Axolotito!' — El Gritón bate palmas.",
        "El Gritón grita tu carta con orgullo: '¡Lo marcó antes que yo la dijera!'",
        "'¡Reflejos de plasma puro!' — El Gritón ya le cuenta a todos del Cenote.",
    ],
}

# ---------------------------------------------------------------------------
# Modificadores de tono por personalidad
# ---------------------------------------------------------------------------

_NATURE_PREFIXES: dict[str, list[str]] = {
    "lucky":       ["¡Órale!", "¡A todo dar!", "¡De pelos!"],
    "hyperactive": ["¡Ya ya ya!", "¡Híjole!", "¡Ándale!"],
    "salty":       ["Pos...", "Ni modo.", "Qué le vamos a hacer."],
    "shy":         ["Bueno, es que...", "No sé, pero...", "Pues creo que..."],
    "methodical":  ["Estadísticamente hablando,", "Los datos dicen que", "Calculando:"],
}

_NATURE_SUFFIXES: dict[str, list[str]] = {
    "lucky":       ["¡¡¡", "¡Viva el Cenote!", "¡El destino es nuestro!"],
    "hyperactive": ["¡¡", "¡No paro!", "¡Vamos vamos vamos!"],
    "salty":       ["...sí.", "Ni modo, así es la vida.", "Pero aquí seguimos."],
    "shy":         ["...supongo.", "si no te molesta.", "espero."],
    "methodical":  ["con un margen del 12%.", "según el patrón del Cenote.", "probabilidad calculada."],
}


def _pick(lst: list[str]) -> str:
    return _rng.choice(lst)


def _apply_nature(line: str, nature: Optional[str]) -> str:
    """Añade un prefijo/sufijo según la personalidad del Axolotito."""
    if not nature or nature not in _NATURE_PREFIXES:
        return line
    prefix = _pick(_NATURE_PREFIXES[nature])
    suffix = _pick(_NATURE_SUFFIXES[nature])
    return f"{prefix} {line} {suffix}"


def _band(value: float) -> str:
    if value <= 25:
        return "low"
    if value <= 50:
        return "mid"
    if value <= 80:
        return "high"
    return "peak"


class DialogueEngine:
    """Motor de diálogos del universo Axolotto."""

    def get_line(
        self,
        stat: str,
        value: float,
        context: DialogueContext,
        nature: Optional[str] = None,
    ) -> str:
        """Retorna una línea de diálogo según stat, rango de valor, contexto y personalidad."""
        # Primero intentar línea específica del contexto de tutorial
        ctx_key = context.value
        if ctx_key in _TUTORIAL_LINES:
            base = _pick(_TUTORIAL_LINES[ctx_key]["neutral"])
            return _apply_nature(base, nature)

        # Línea basada en el stat + banda de valor
        stat_bank = _STAT_LINES.get(stat)
        if stat_bank:
            band = _band(value)
            base = _pick(stat_bank[band])
            return _apply_nature(base, nature)

        return _apply_nature("El Cenote guarda sus secretos por ahora.", nature)

    def get_karma_line(self, karma: str) -> str:
        """Línea especial al revelar el karma al nacer."""
        lines = _KARMA_LINES.get(karma, _KARMA_LINES["salty"])
        return _pick(lines)

    def get_game_event_line(
        self,
        event: str,
        axo_luck: float = 50.0,
        axo_salinity: float = 30.0,
        nature: Optional[str] = None,
    ) -> str:
        """event: 'win' | 'lose' | 'crit'"""
        lines = _GAME_EVENT_LINES.get(event, _GAME_EVENT_LINES["lose"])
        base = _pick(lines)
        return _apply_nature(base, nature)

    def get_inter_axo_line(
        self,
        opponent_type: str,
        nature: Optional[str] = None,
    ) -> str:
        """opponent_type: 'bot_1' | 'bot_5' | 'human'"""
        lines = _INTER_AXO_LINES.get(opponent_type, _INTER_AXO_LINES["bot_1"])
        base = _pick(lines)
        return _apply_nature(base, nature)

    def get_gritón_line(
        self,
        axo_agility: float,
        card_name: str = "",
    ) -> str:
        """El Gritón reacciona diferente según la agilidad del Axo."""
        if axo_agility < 30:
            band = "slow"
        elif axo_agility < 70:
            band = "medium"
        else:
            band = "fast"
        line = _pick(_GRITÓN_LINES[band])
        if card_name:
            line = line.replace("La carta", f"La carta '{card_name}'")
        return line

    def infer_personality_from_incubation(
        self,
        bonus_luck: float,
        bonus_focus: float,
        bonus_stamina: float,
    ) -> str:
        """
        Infiere la personalidad probable del huevo antes del nacimiento,
        basándose en los bonos acumulados de cuidado.
        """
        if bonus_luck > 60:
            return "lucky"
        if bonus_focus > 60:
            return "methodical"
        if bonus_stamina > 60:
            return "hyperactive"
        return "salty"
