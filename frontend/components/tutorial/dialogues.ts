/**
 * Hardcoded tutorial dialogue strings.
 * The backend DialogueEngine integration is planned for v2.
 * All text is written in Spanish to match the game's language.
 */

export type Nature = "lucky" | "salty" | "hyperactive" | "methodical" | "shy";
export type TutorialEvent =
  | "phase_start"
  | "phase_win"
  | "phase_lose"
  | "distracted"
  | "focus_boost";

// ── Phase 1: Salinidad ────────────────────────────────────────────────────────

const PHASE1_START: Record<Nature, string> = {
  lucky:
    "¡Holaaa! Soy Webito, tu huevo de lotería! Vamos a jugar nuestra primera partida. " +
    "Tengo mucha salinidad, eso significa que mi mala suerte puede afectar la partida... " +
    "¡pero no importa, la suerte siempre llega!",
  salty:
    "Soy Webito. Salinidad alta. Eso básicamente significa que este juego puede ir mal. " +
    "Ya lo sé. No hace falta que me lo recuerdes.",
  hyperactive:
    "¡¡HOLAAA!! ¡¡Soy Webito!! ¡¡Vamos a jugar ya ya ya!! " +
    "Eso de la salinidad no me preocupa para nada, ¡¡vamos con todo!!",
  methodical:
    "Iniciando partida tutorial — Fase 1. Mi salinidad calculada es elevada. " +
    "Esto incrementa la probabilidad de resultados adversos en aproximadamente un 12%. " +
    "Procederé con cautela.",
  shy:
    "Hola... soy Webito. Dicen que tengo mucha salinidad... " +
    "espero no arruinar la partida. Haré lo que pueda.",
};

const PHASE1_WIN: Record<Nature, string> = {
  lucky:
    "¡¡LO SABÍA!! La suerte siempre gana. ¡¡LOTERÍA!! Mira, incluso con salinidad alta podemos ganar. " +
    "¿Ves? Te dije que no había de qué preocuparse.",
  salty:
    "Ganamos. Bien. Supongo que la salinidad no fue tan catastrófica esta vez. " +
    "No te acostumbres.",
  hyperactive:
    "¡¡GANAMOOOS!! ¡¡YEAAAH!! ¡¡Eso es!! ¡¡Somos imparables!! ¡¡Siguiente ronda, vamos!!",
  methodical:
    "Victoria confirmada. La salinidad fue compensada por factores aleatorios favorables. " +
    "Archivando resultado para análisis posterior.",
  shy:
    "Oh... ¡ganamos! Qué alivio. No esperaba que saliera bien, la verdad.",
};

const PHASE1_LOSE: Record<Nature, string> = {
  lucky:
    "Ups... perdimos. Pero eso fue solo la salinidad metiendo las patas. " +
    "En la próxima mi aura de suerte lo compensará, ¡ya verás!",
  salty:
    "Perdimos. Como era de esperarse con tanta salinidad. " +
    "Bueno, al menos lo intenté.",
  hyperactive:
    "¡Noooo! ¡Perdimos! ¡Pero está bien, está bien! ¡La próxima ganamos con más energía todavía!",
  methodical:
    "Derrota. La salinidad elevada generó el resultado estadísticamente más probable. " +
    "Ajustando parámetros para la Fase 2.",
  shy:
    "Perdimos... lo sabía. La salinidad es mucha. Pero... ¿seguimos intentando?",
};

// ── Phase 2: Focus ────────────────────────────────────────────────────────────

const PHASE2_START: Record<Nature, string> = {
  lucky:
    "¡Segunda partida! Esta vez se trata de mi concentración. " +
    "Puede que me distraiga con las cartas más bonitas, ¡pero mi suerte lo compensará!",
  salty:
    "Segunda ronda. Focus. Yo sé perfectamente bien cuáles son mis cartas, " +
    "lo que pasa es que a veces simplemente no me da la gana marcarlas a tiempo.",
  hyperactive:
    "¡¡FASE DOS!! ¡¡Focus!! ¡¡Yo tengo un enfoque INCREÍBLE cuando quiero!! " +
    "¡¡Aunque a veces veo una carta chida y me quedo mirándola... pero solo por un segundo!!",
  methodical:
    "Fase 2 iniciada. El parámetro crítico ahora es el Focus. " +
    "Mi concentración determina directamente la tasa de marcado correcto. Procediendo.",
  shy:
    "Esta vez... es sobre concentración. A veces me distraigo un poco. " +
    "Intentaré estar atento, lo prometo.",
};

const PHASE2_DISTRACTED: Record<Nature, string> = {
  lucky:
    "¡Uy! Me distraje mirando esa carta tan bonita. " +
    "Tócala rápido para recuperar el tiempo perdido, ¡mi suerte todavía nos salva!",
  salty:
    "...ya sé. Me distraje. No me mires así. Toca la carta resaltada y seguimos.",
  hyperactive:
    "¡AYYY! ¡Me fui! ¡Estaba mirando aquella carta tan colorida! " +
    "¡Toca la que brilla, rápido rápido rápido!",
  methodical:
    "Anomalía detectada: distracción involuntaria. " +
    "Para corregir el error, selecciona la casilla iluminada inmediatamente.",
  shy:
    "Oh no... me distraje de nuevo. Lo siento mucho. " +
    "¿Puedes tocar la carta que brilla? Por favor.",
};

const PHASE2_FOCUS_BOAST: Record<Nature, string> = {
  lucky:
    "¡Mira qué concentrado! No me perdí ni una carta. " +
    "Eso más mi suerte legendaria es una combinación imbatible.",
  salty:
    "Bien, sí. No me distraje. No es para tanto, es lo mínimo.",
  hyperactive:
    "¡¡ENFOQUE NIVEL DIOS!! ¡¡Marqué TODO!! ¡¡Soy una máquina de precisión!! ¡¡Casi!!",
  methodical:
    "Focus óptimo alcanzado. Tasa de marcado: 100%. Exactamente como lo calculé.",
  shy:
    "Creo que... ¿estuve concentrado? Eso es raro. Pero me alegra.",
};

const PHASE2_WIN: Record<Nature, string> = {
  lucky:
    "¡¡Lo hicimos!! ¡¡Mi concentración y mi suerte juntas son invencibles!!",
  salty:
    "Ganamos otra vez. Bien. El Focus sirve, hay que admitirlo.",
  hyperactive:
    "¡¡VICTORIAAA!! ¡¡SIII!! ¡¡Somos los mejores!! ¡¡Vamos a la fase tres!!",
  methodical:
    "Victoria. El modelo predictivo era correcto: mayor Focus equivale a mayor tasa de éxito.",
  shy:
    "¡Ganamos! No lo esperaba, de verdad. Qué bueno.",
};

const PHASE2_LOSE: Record<Nature, string> = {
  lucky:
    "Ay... perdimos. Pero fue culpa de la salinidad de la fase anterior, no de mi concentración. " +
    "¡La siguiente nos la llevamos!",
  salty:
    "Perdimos. Sí. Puede haber sido el Focus, puede haber sido la salinidad. " +
    "No importa. Sigamos.",
  hyperactive:
    "¡Nooo! ¡Pero estuuuvo cerca! ¡¡La siguiente la ganamos con el doble de energía!!",
  methodical:
    "Derrota. Identificando factores determinantes para optimizar la Fase 3.",
  shy:
    "Perdimos... pero aprendí algo. Hay que concentrarse más la próxima vez.",
};

// ── Phase 3: Luck ─────────────────────────────────────────────────────────────

const PHASE3_START: Record<Nature, string> = {
  lucky:
    "¡¡Última fase!! Y se trata de SUERTE, que es mi especialidad absoluta. " +
    "¡Vamos a dar todo lo que tenemos en esta partida!",
  salty:
    "Tercera y última ronda. Suerte. " +
    "Lo intentaremos, sin garantías.",
  hyperactive:
    "¡¡FASE TRES!! ¡¡SUERTE!! ¡¡MI TEMA FAVORITO!! " +
    "¡¡VAMOS A DARLO TODO EN ESTA PARTIDA!! ¡¡YA QUIERO!!",
  methodical:
    "Fase 3. Variable principal: Luck. " +
    "Condiciones óptimas para rendimiento. Procediendo.",
  shy:
    "La última partida... y todo depende de la suerte que tengamos. " +
    "Nunca lo he hecho, pero tú me ayudas, ¿verdad?",
};


const PHASE3_WIN: Record<Nature, string> = {
  lucky:
    "¡¡¡CAMPEÓN!!! ¡¡La SUERTE estuvo de nuestro lado!! " +
    "¡¡Tres partidas, tres lecciones, y ahora eres un verdadero jugador de Axolotto!!",
  salty:
    "Ganamos. Tutorial completo. " +
    "Supongo que el juego no es tan malo. Seguiré jugando. Tal vez.",
  hyperactive:
    "¡¡¡LOTERÍA TOTAL!!! ¡¡¡SOMOS LOS REYES!!! ¡¡¡TRES DE TRES!!! " +
    "¡¡¡EL MUNDO ES NUESTRO!!!",
  methodical:
    "Tutorial completado. Tasa de éxito final: óptima. " +
    "Has aprendido las mecánicas fundamentales. Ahora podemos proceder al juego real.",
  shy:
    "¡Ganamos! El tutorial terminó y... sobreviví. Gracias por ayudarme.",
};

const PHASE3_LOSE: Record<Nature, string> = {
  lucky:
    "Ah... perdimos la última. Pero aprendiste todo lo importante. " +
    "La salinidad, el focus, la suerte. ¡Ya estás listo para las partidas reales!",
  salty:
    "Perdimos la última. Igual que la primera, casi. " +
    "Tutorial terminado. Ahora sabes lo básico.",
  hyperactive:
    "¡¡Ay nooo!! ¡¡Pero no importa!! ¡¡El tutorial está completo!! " +
    "¡¡Aprendimos todo!! ¡¡La próxima partida real la ganamos seguro!!",
  methodical:
    "Derrota en fase final. Sin embargo, los objetivos de aprendizaje fueron cumplidos. " +
    "Continúa al modo normal con los conocimientos adquiridos.",
  shy:
    "Perdimos... pero el tutorial terminó. Aprendí cosas. Gracias por jugar conmigo.",
};

// ═══════════════════════════════════════════════════════════════════════════════
// ACTO 1 — Presentación del Webito
// ═══════════════════════════════════════════════════════════════════════════════

/** Three sequential dialogue lines for Acto 1. Tap to advance between them. */
export const ACT1_INTRO_LINES: Record<Nature, [string, string, string]> = {
  hyperactive: [
    "¡¡¡HOLAAAAAA!!! ¡Llevo semanas en este cascarón y por FIN alguien llegó!",
    "Soy WEBITO. Un axolotito que todavía no nace. Y ya quiero jugar LOTERÍA con todo.",
    "¿Me ayudas a nacer? ¡Necesito energía y tú eres justo lo que faltaba! ¿Lo harémos?",
  ],
  lucky: [
    "Hola. Soy Webito. Llevaba tiempo esperando al jugador correcto.",
    "La suerte me dijo que eras tú. Siempre le hago caso a la suerte.",
    "Hay un juego afuera llamado Lotería. Yo lo necesito. ¿Le entramos juntos?",
  ],
  salty: [
    "Hola. Soy Webito. Llevo semanas encerrado en este cascarón.",
    "No es queja. Es contexto. El agua está salada y así es la vida.",
    "Afuera hay un juego de Lotería y yo quiero jugar. ¿Me ayudas o no?",
  ],
  methodical: [
    "Saludos. Soy Webito, un axolotito en proceso de incubación.",
    "Estadísticamente, ya era momento de que llegara mi jugador. Buenos datos.",
    "He analizado el juego de Lotería. La estrategia óptima requiere un compañero. Ese eres tú.",
  ],
  shy: [
    "Eh... hola. Soy Webito. Llevo mucho tiempo aquí adentro y...",
    "Bueno... me alegra que hayas llegado. Mucho.",
    "Hay un juego afuera llamado Lotería. Yo quiero jugar, pero... ¿me acompañas?",
  ],
};

// ═══════════════════════════════════════════════════════════════════════════════
// ACTO 2 — Ficha de ADN (stat reveal)
// ═══════════════════════════════════════════════════════════════════════════════

/** One-liner per stat per value band. */
export function getStatOneliner(stat: "SAL" | "OJO" | "PILA" | "SUERTE", value: number): string {
  if (stat === "SAL") {
    if (value < 35) return "Aguas tranquilas. El cenote no me pone nervioso.";
    if (value < 65) return "Sal media. El deck tiene sorpresas, pero las manejo.";
    return "Sal alta. El deck me va a poner a prueba. Me gusta el reto.";
  }
  if (stat === "OJO") {
    if (value < 35) return "Me distraigo... pero lo sé y estoy trabajando en ello.";
    if (value < 65) return "Ojo entrenado. Casi nunca se me escapa una carta.";
    return "Ojo clínico. Cuando el Gritón canta, yo ya marqué.";
  }
  if (stat === "PILA") {
    if (value < 50) return "Pila moderada. Cada partida es preciosa.";
    if (value < 80) return "Pila sólida. Sin problemas de energía.";
    return "¡PILA AL TOPE! Podría jugar toda la noche.";
  }
  // SUERTE
  if (value < 40) return "Suerte constructiva. Mejor que suerte tengo ESTRATEGIA.";
  if (value < 65) return "Suerte equilibrada. Lo correcto, bien jugado.";
  return "Suerte de campeón. Los drops raros me buscan a mí.";
}

/** Final comment after all 4 stats are revealed, per nature. */
export const ACT2_FINAL_COMMENT: Record<Nature, string> = {
  hyperactive: "¡¡ESA ES MI FICHA!! ¡¡Soy único en todo el cenote!! ¡¡Nadie tiene mi ADN!!",
  lucky:       "Ahí está. Mi ADN completo. Interesante combinación. Tengo buen presentimiento.",
  salty:       "Pos esos son mis stats. Lo que hay es lo que hay. Sin drama.",
  methodical:  "Análisis completado. Perfil genético registrado. Estoy listo para proceder.",
  shy:         "Esos... esos son mis stats. ¿Están bien? Espero que estén bien.",
};

// ═══════════════════════════════════════════════════════════════════════════════
// ACTO 3 — Tabla del Destino (board preview)
// ═══════════════════════════════════════════════════════════════════════════════

export const ACT3_BOARD_INTRO: Record<Nature, string> = {
  hyperactive: "¡¡Mira!! Para jugar Lotería necesitamos una Tabla. ¡Cada tabla es una cuadrícula con 16 cartas seleccionadas de un mazo total de 54! ¡Vamos a barajar el mazo para formar tu 'Acta de Nacimiento'!",
  lucky:       "Para entrar a jugar Lotería, necesitamos una Tabla. Una tabla se forma eligiendo 16 cartas al azar de la baraja completa de 54. ¡Vamos a barajar para ver qué nos da el destino para tu 'Acta de Nacimiento'!",
  salty:       "Antes de jugar, ocupamos una Tabla. Son 16 cartas sacadas de la baraja total de 54. A ver qué sale cuando barajemos este mazo para hacer tu 'Acta de Nacimiento'...",
  methodical:  "Todo juego de Lotería requiere una Tabla de 4x4. Cada tabla representa un subconjunto de 16 cartas extraídas secuencialmente de un mazo de 54. Iniciando barajado para estructurar tu 'Acta de Nacimiento'.",
  shy:         "Para poder jugar... necesitamos una Tabla. Es una cuadrícula con 16 cartas escogidas del mazo entero de 54. ¿Barajamos las cartas para ver cómo queda tu 'Acta de Nacimiento'?",
};

export const ACT3_BOARD_REVEALED: Record<Nature, string> = {
  hyperactive: "¡¡QUEDÓ INCREÍBLE!! ¡¡Esas 16 cartas son mi Acta de Nacimiento!! ¡¡Nadie más tiene esta combinación!! ¡¡Empecemos la demo ya ya ya!!",
  lucky:       "Listo. Mi Acta de Nacimiento está revelada. Estas 16 cartas tienen muy buenas vibras. Iniciemos la ronda de prueba.",
  salty:       "Ahí está. Mi Acta de Nacimiento con sus 16 cartas. Espero que el Gritón sea benevolente hoy. Hagamos la prueba.",
  methodical:  "Secuencia de reparto finalizada. Se han posicionado las 16 cartas que componen mi Acta de Nacimiento. Ejecutando simulación demo.",
  shy:         "¡Qué bonita quedó! Esta es mi Acta de Nacimiento... mis 16 cartas. ¿Jugamos la ronda de prueba juntos?",
};


/** Webito reacts when a hit card is called (4 hits per demo, indexed 0-3). */
export const ACT3_HIT_REACTIONS: Record<Nature, [string, string, string, string]> = {
  hyperactive: [
    "¡¡ESA ES MÍA!! ¡¡MÁRCALA MÁRCALA MÁRCALA!!",
    "¡¡OTRA MÍA!! ¡¡VOY LLENANDO LA LÍNEA!! ¡¡DALE!!",
    "¡¡CASI CASI!! ¡¡UNA MÁS Y LOTERÍA!! ¡¡TOCA!!",
    "¡¡LA ÚLTIMA!! ¡¡TOCA ESA CARTA AHORA MISMO!!",
  ],
  lucky: [
    "¡Esa es mía! Sabía que iba a salir. Márcala.",
    "Otra. La suerte trabaja rápido. ¡Márcala!",
    "¡Ya casi! Una más y cerramos la línea. Dale.",
    "¡La última de la línea! Márcala y gritas LOTERÍA.",
  ],
  salty: [
    "Esa es mía. Márcala.",
    "Otra. Bien. Márcala también.",
    "Casi. Márcala. Falta una.",
    "La última. Márcala. Ya.",
  ],
  methodical: [
    "Carta identificada en mi tabla. Márcala para completar la secuencia.",
    "Segunda carta de la línea objetivo. Marcado requerido.",
    "75% de la línea completado. Marca esta para continuar.",
    "Carta final de la línea. Márcala y el algoritmo gana.",
  ],
  shy: [
    "Oh... esa es mía. ¿La marcas por favor?",
    "¡Otra! Me estoy llenando. ¿La marcas?",
    "¡Casi! Solo una más... ¿la marcas?",
    "¡La última de la línea! Márcala... ¡por favor!",
  ],
};

export const ACT3_VICTORY: Record<Nature, string> = {
  hyperactive: "¡¡¡LOTERÍA!!! ¡¡¡GANAMOS!!! ¡¡¡ERES UN NATO DE LA LOTERÍA!!! ¡¡¡INCREÍBLE!!!",
  lucky:       "¡LOTERÍA! Cuatro en línea. Así de fácil cuando tienes suerte. Eres un nato.",
  salty:       "¡Lotería! Cuatro en línea. Sí, lo hiciste bien. Eres un nato. No está mal.",
  methodical:  "¡LOTERÍA! Línea completa. Ejecución perfecta. Eres un jugador nato, estadísticamente confirmado.",
  shy:         "¡¡Lotería!! ¡Lo logramos! Eres... eres un nato de la Lotería. ¡En serio!",
};

export const ACT3_LINES_EXPLAIN: Record<Nature, string> = {
  hyperactive: "¡¡HAY 10 FORMAS DE GANAR!! ¡¡FILAS, COLUMNAS Y DIAGONALES!! ¡¡MÍRELAS TODAS!!",
  lucky:       "Hay 10 caminos hacia la victoria. Filas, columnas, diagonales. Te los muestro.",
  salty:       "Hay 10 líneas ganadoras posibles. No solo filas. También columnas y diagonales. Mira.",
  methodical:  "El tablero tiene 10 líneas ganadoras posibles. Las muestro en secuencia para que las memorices.",
  shy:         "Hay 10 formas de ganar, no solo las filas. ¿Las ves? Columnas y diagonales también cuentan.",
};

export const ACT3_FULL_BOARD: Record<Nature, string> = {
  hyperactive: "¡¡Y A VECES LA SALA PIDE LLENAR TODA LA TABLA!! ¡¡16 CARTAS SIN FALLAR UNA!! ¡¡ESO SE LLAMA TABLA LLENA!! ¡¡SIN MISERICORDIA!!",
  lucky:       "Y a veces la sala pide llenar TODA la tabla. 16 cartas. Eso requiere suerte... y concentración.",
  salty:       "Y a veces el modo de juego es tabla llena. Las 16 cartas. Sin atajos. El cenote no perdona.",
  methodical:  "Existe un modo adicional: tabla completa. Requiere marcar las 16 posiciones. Dificultad máxima.",
  shy:         "A veces... a veces la sala pide llenar TODA la tabla. Las 16 cartas. Es difícil, pero se puede.",
};

export const ACT3_OUTRO: Record<Nature, string> = {
  hyperactive: "¡¡ENTENDIDO!! ¡¡FILAS, COLUMNAS, DIAGONALES, TABLA LLENA!! ¡¡YA LO SÉ TODO!! ¡¡VAMOS!!",
  lucky:       "Entendido. Las reglas son simples. Cuando nazca, vamos a dominar esto.",
  salty:       "Entendido. Las reglas no son complicadas. A ver cómo resulta en partida real.",
  methodical:  "Reglas asimiladas. 10 líneas, modo tabla llena. Estoy listo para la fase siguiente.",
  shy:         "¡Entendido! Gracias por enseñarme. Cuando nazca... vamos a jugar bien.",
};

// ═══════════════════════════════════════════════════════════════════════════════
// ACTO 4 — El Pacto
// ═══════════════════════════════════════════════════════════════════════════════

export function getAct4PactoLines(nature: Nature, salValue: number): [string, string] {
  const line1: Record<Nature, string> = {
    hyperactive: "¡¡Para nacer necesito ENERGÍA de las partidas!! ¡¡Y cada vez que jugamos, mis stats se moldean en tiempo real!!",
    lucky:       "Para nacer necesito energía, y la energía viene de las partidas. Cada vez que jugamos, mis stats se afilan.",
    salty:       "Para nacer necesito energía. Las partidas la generan y mis stats se moldean. Así funciona.",
    methodical:  "El nacimiento requiere energía acumulada mediante partidas, que a su vez calibran mis stats en tiempo real.",
    shy:         "Para nacer... necesito energía. Y tú me la das jugando. Mis stats aprenden contigo.",
  };
  const opener: Record<Nature, string> = {
    hyperactive: "¡¡Vamos a moldear esos stats AHORA!! ¡¡Empezamos con SAL!!",
    lucky:       "Vamos a moldear esos stats. Empezamos con SAL.",
    salty:       "Vamos a moldear esos stats. Empezamos con SAL.",
    methodical:  "Iniciando secuencia de calibración. Primera variable: SAL.",
    shy:         "Vamos... vamos a moldear esos stats. Empezamos con SAL.",
  };
  return [line1[nature], `${opener[nature]} ${getActSalPreGame(nature, salValue)}`];
}

// ═══════════════════════════════════════════════════════════════════════════════
// ACTOS 5-7 — Pre/Post Game por Stat
// ═══════════════════════════════════════════════════════════════════════════════

/** Pre-game dialogue for Acto 5 (SAL). salValue = 100 - stamina. */
export function getActSalPreGame(nature: Nature, salValue: number): string {
  const level = salValue < 35 ? "low" : salValue < 65 ? "mid" : "high";
  const byLevel: Record<string, Record<Nature, string>> = {
    low: {
      hyperactive: "¡¡SAL BAJA!! ¡¡Aguas calmadas!! ¡¡El deck no me puede!! ¡¡Vamos a arrasar!!",
      lucky:       "SAL baja. El deck está de mi lado hoy. No tengo que forzar la suerte.",
      salty:       "SAL baja. Aguas tranquilas. Raro, pero bienvenido.",
      methodical:  "SAL en rango bajo. La probabilidad de cartas adversas es mínima. Condiciones favorables.",
      shy:         "Mi SAL está baja... eso es bueno, ¿verdad? El deck no debería ser tan difícil.",
    },
    mid: {
      hyperactive: "¡¡SAL MEDIA!! ¡¡No está mal!! ¡¡El deck tiene sus cosas pero yo tengo más energía!!",
      lucky:       "SAL media. Ni muy difícil ni muy fácil. Me gustan los desafíos medidos.",
      salty:       "SAL media. El deck va a tener sus sorpresas. Como siempre.",
      methodical:  "SAL dentro de parámetros normales. Variabilidad del deck: moderada. Proceedo.",
      shy:         "SAL media... esperemos que no sea muy difícil el deck.",
    },
    high: {
      hyperactive: "¡¡SAL ALTA!! ¡¡EL DECK ESTÁ ENDIABLADO!! ¡¡PERO YO AGUANTO TODO!! ¡¡VAMOS!!",
      lucky:       "SAL alta. El deck va duro. Pero a veces la partida más difícil es la más emocionante.",
      salty:       "SAL alta. El deck está complicado. Lo sabía. Pero yo aguanto.",
      methodical:  "SAL elevada. Alta probabilidad de cartas adversas. Ajustando estrategia para entorno hostil.",
      shy:         "SAL alta... el deck va a ser difícil. Pero... lo intentamos, ¿sí?",
    },
  };
  return byLevel[level][nature];
}

export const ACT5_POST_GAME: Record<Nature, string> = {
  hyperactive: "¡¡PRIMERA PARTIDA COMPLETADA!! ¡¡Siento la energía!! ¡¡Mi SAL ya está calibrada!!",
  lucky:       "Primera partida. SAL entendida. El cenote registró mi resistencia.",
  salty:       "Primera partida terminada. El cenote tomó nota de mi SAL. Seguimos.",
  methodical:  "Fase SAL completada. Datos de salinidad registrados. Pasando a la siguiente variable.",
  shy:         "¡La primera partida ya pasó! Mi SAL... quedó registrada. Vamos bien.",
};

/** Pre-game for Acto 6 (OJO). focusValue = bonus_focus. */
export function getActOjoPreGame(nature: Nature, focusValue: number): string {
  if (focusValue >= 60) {
    const high: Record<Nature, string> = {
      hyperactive: "¡¡OJO AL MÁXIMO!! ¡¡Cuando el Gritón cante yo ya la tengo marcada!! ¡¡VELOCIDAD!!",
      lucky:       "OJO afilado. Las cartas no se me escapan. Esta partida es nuestra.",
      salty:       "OJO bien puesto. Pocas distracciones. No está mal para ser yo.",
      methodical:  "OJO en parámetros óptimos. Tasa de marcado proyectada: superior al promedio.",
      shy:         "Mi OJO está... bien alto. Creo que puedo no perder ninguna carta hoy.",
    };
    return high[nature];
  }
  const low: Record<Nature, string> = {
    hyperactive: "¡OJO MEDIANO! ¡Me puedo distraer un poco! ¡Pero tú me avisas si me voy, sí?!",
    lucky:       "Mi OJO está en proceso. Me puedo distraer. Pero la suerte cubre los huecos.",
    salty:       "Mi OJO no está en su mejor día. Me puedo distraer. Ya lo sabes.",
    methodical:  "OJO subóptimo detectado. Riesgo de distracción presente. Mantente alerta.",
    shy:         "Mi OJO está... mediano. Me puedo distraer un poco. Lo siento de antemano.",
  };
  return low[nature];
}

export const ACT6_POST_GAME: Record<Nature, string> = {
  hyperactive: "¡¡OJO CALIBRADO!! ¡¡Siento cómo mi concentración creció!! ¡¡Más energía!!",
  lucky:       "OJO entrenado. Siento que mis reflejos mejoraron con esa partida.",
  salty:       "OJO calibrado. Segunda partida terminada. Voy tomando forma.",
  methodical:  "Variable OJO calibrada. Progreso del tutorial: 66.6%. Continuando.",
  shy:         "Segunda partida terminada. Mi OJO aprendió algo. Ya casi llego.",
};

/** Pre-game for Acto 7 (SUERTE+PILA). */
export function getActSuertePilaPreGame(nature: Nature, luck: number, stamina: number): string {
  const highLuck = luck >= 60;
  const highPila = stamina >= 70;
  if (highLuck && highPila) {
    const combo: Record<Nature, string> = {
      hyperactive: "¡¡SUERTE ALTA Y PILA FULL!! ¡¡ESTO ES DEVASTADOR PARA EL CENOTE!! ¡¡VAMOS!!",
      lucky:       "Suerte alta, pila llena. La combinación perfecta. Esta partida tiene mi nombre.",
      salty:       "Suerte y pila altas. Pos qué bien. A ver si se nota.",
      methodical:  "SUERTE elevada + PILA máxima. Condiciones óptimas para rendimiento superior.",
      shy:         "Tengo buena suerte y mucha pila. Ojalá... ojalá eso sea suficiente.",
    };
    return combo[nature];
  }
  const base: Record<Nature, string> = {
    hyperactive: "¡¡LA PARTIDA FINAL!! ¡¡SUERTE y PILA se fusionan!! ¡¡SOY IMPARABLE!!",
    lucky:       "La última prueba. Suerte y resistencia juntas. Mi momento favorito.",
    salty:       "Tercera y última partida. Suerte y pila. Lo que sea que salga, sale.",
    methodical:  "Partida final del tutorial. Variables: SUERTE y PILA. Análisis en curso.",
    shy:         "La última partida. Suerte y pila combinadas. Un poco nervioso, pero vamos.",
  };
  return base[nature];
}

export const ACT7_POST_GAME: Record<Nature, string> = {
  hyperactive: "¡¡TRES PARTIDAS!! ¡¡ENERGÍA COMPLETA!! ¡¡SIENTO ALGO MOVERSE EN EL CASCARÓN!!",
  lucky:       "Tres partidas. El cenote tomó nota. Siento algo diferente... dentro de mí.",
  salty:       "Tres partidas terminadas. El cenote decidió. Ahora... siento algo.",
  methodical:  "Protocolo de tutorial: completado. Energía acumulada: máxima. Iniciando secuencia de nacimiento.",
  shy:         "Tres partidas... lo logramos. Siento algo moverse adentro. Es hora.",
};

// ═══════════════════════════════════════════════════════════════════════════════
// ACTO 8 — Karma Reveal
// ═══════════════════════════════════════════════════════════════════════════════

export const ACT8_SUSPENSE: Record<Nature, string> = {
  hyperactive: "¡¡El cenote está analizando todo lo que hicimos!! ¡¡Siento las vibraciones!! ¡¡QUÉ EMOCIÓN!!",
  lucky:       "El cenote está evaluando... las cartas jugadas, los momentos clave. Siento que sé el resultado.",
  salty:       "El cenote está decidiendo. Supongo que lo sabremos pronto.",
  methodical:  "El algoritmo del cenote procesa las 3 partidas. El resultado es determinista. Esperando output.",
  shy:         "El cenote está evaluando... tengo un poco de nervios. ¿Y si el resultado es raro?",
};

export const ACT8_KARMA_REACTION: Record<"lucky" | "salty", Record<Nature, string>> = {
  lucky: {
    hyperactive: "¡¡¡SUERTUDO Y CON PILA!!! ¡¡¡ESTO ES DEVASTADOR PARA EL CENOTE!!! ¡¡¡NADIE NOS PARA!!!",
    lucky:       "Suerte. Claro. Lo sabía. La suerte siempre vuelve a los que la cultivan.",
    salty:       "Suerte... no la esperaba. Pos qué bien. Acepto.",
    methodical:  "Karma: LUCKY. Confirma la hipótesis inicial. La suerte es estadísticamente reproducible.",
    shy:         "¿Karma de suerte? Para mí... ¡qué alegría tan inesperada!",
  },
  salty: {
    hyperactive: "¡¡SALADO!! ¡¡PERO LOS SALADOS SOMOS LOS MÁS FUERTES!! ¡¡EL AGUA DURA FORJA CAMPEONES!!",
    lucky:       "Salado. Curioso. La suerte tomó otro camino. Igual voy a ganar.",
    salty:       "Salado. Como era de esperarse. El cenote me conoce bien.",
    methodical:  "Karma: SALTY. El resultado estadístico más probable dado el perfil de datos. Sin sorpresas.",
    shy:         "Salado... está bien. Los salados también jugamos bien. ¿Verdad?",
  },
};

// ═══════════════════════════════════════════════════════════════════════════════
// ACTO 9 — Nacimiento
// ═══════════════════════════════════════════════════════════════════════════════

export const ACT9_BIRTH_CRY: Record<Nature, string> = {
  hyperactive: "¡¡¡LIBRE!!! ¡¡El cenote me llama!! ¡¡Las cartas me llaman!! ¡¡TODO ME LLAMA!! ¡¡AAAAAH!!",
  lucky:       "Ah. El mundo. Huele a suerte fresca. ¡Vamos a jugar en serio!",
  salty:       "...ah. El mundo. Pos qué le vamos a hacer. A jugar.",
  methodical:  "Nacimiento completado. Stats confirmados. Probabilidades calculadas. Empecemos.",
  shy:         "H-hola... mundo. Soy yo. Es un placer conocerte. ¿J-jugamos?",
};

export const ACT9_STATS_LOCKED: Record<Nature, string> = {
  hyperactive: "¡¡MIS STATS QUEDARON GRABADOS EN EL CENOTE!! ¡¡SOY OFICIAL!! ¡¡SOY REAL!!",
  lucky:       "Mis stats están fijos. El cenote me reconoce. Soy un axolotito de verdad.",
  salty:       "Stats grabados. Soy oficial ahora. Sin vuelta atrás.",
  methodical:  "Registro genético completado. Identidad en blockchain del cenote confirmada.",
  shy:         "Mis stats quedaron grabados... ya soy real. Un axolotito de verdad.",
};

// ═══════════════════════════════════════════════════════════════════════════════
// ACTO 10 — World Intro
// ═══════════════════════════════════════════════════════════════════════════════

export const ACT10_INTRO: Record<Nature, string> = {
  hyperactive: "¡¡BIENVENIDO AL CENOTE!! ¡¡HAY TANTO QUE VER!! ¡¡TE LO VOY A ENSEÑAR TODO AHORA!!",
  lucky:       "Bienvenido al cenote. Este es mi mundo ahora. Y el tuyo también.",
  salty:       "El cenote. Grande, profundo, lleno de cosas. Te lo explico rápido.",
  methodical:  "Procediendo con la orientación del ecosistema. Hay 5 secciones clave que debes conocer.",
  shy:         "El cenote es... grande. Pero te lo enseño. Juntos no da tanto miedo.",
};

export const ACT10_CTA: Record<"lucky" | "salty", string> = {
  lucky:  "¡A las salas! La suerte nos espera. ✨",
  salty:  "Vale. A trabajar. El cenote no se conquista solo. 🧂",
};

// ── Public API ─────────────────────────────────────────────────────────────────

export function getTutorialDialogue(
  phase: 1 | 2 | 3,
  nature: Nature,
  event: TutorialEvent,
  statValue?: number
): string {
  if (phase === 1) {
    if (event === "phase_start") return PHASE1_START[nature];
    if (event === "phase_win")   return PHASE1_WIN[nature];
    if (event === "phase_lose")  return PHASE1_LOSE[nature];
  }

  if (phase === 2) {
    if (event === "phase_start")  return PHASE2_START[nature];
    if (event === "distracted")   return PHASE2_DISTRACTED[nature];
    if (event === "focus_boost")  return PHASE2_FOCUS_BOAST[nature];
    if (event === "phase_win")    return PHASE2_WIN[nature];
    if (event === "phase_lose")   return PHASE2_LOSE[nature];
  }

  if (phase === 3) {
    if (event === "phase_start")  return PHASE3_START[nature];
    if (event === "phase_win")    return PHASE3_WIN[nature];
    if (event === "phase_lose")   return PHASE3_LOSE[nature];
  }

  return "...";
}

// ── Refresh greetings (Acto 1) ──────────────────────────────────────────────────

const ACT1_REFRESH_1: Record<Nature, string> = {
  hyperactive: "¡¡ALERTA DE REINICIO!! ¡Bloop! ¿Qué pasó? ¿Se trabó el cenote? ¡No importa, ya estoy listo otra vez! ¡Hola de nuevo! 🌊",
  lucky:       "Vaya, un reinicio. La suerte quiso que nos saludáramos otra vez. Hola de nuevo. 🍀",
  salty:       "Ah, un refresh. Típico. Se cayó la conexión o te arrepentiste de mi cara. Hola otra vez, supongo. 🧂",
  methodical:  "Detectada reconexión en el protocolo. Iniciando diálogo de contingencia. Saludos nuevamente. 📊",
  shy:         "¿Hola...? Creo que se cortó el agua por un segundo. Qué bueno que volviste... 🥚",
};

const ACT1_REFRESH_2: Record<Nature, string> = {
  hyperactive: "¡¡OTRA VEZ!! ¡Jaja! ¿Es un juego de velocidad? ¿Quién da más clicks? ¡Hola hola hola! 🌀",
  lucky:       "Dos refrescos seguidos. Los astros están alineados para que no nos vayamos todavía. ¡Hola de nuevo! ✨",
  salty:       "¿Otra vez? A ver, si no te caigo bien, hay un botón de reset por ahí... pero aquí sigo. Hola. 🙄",
  methodical:  "Reintento número 2. La probabilidad de error en el cliente aumenta. Procediendo con el saludo estándar. ⚙️",
  shy:         "¿Hola de nuevo...? ¿Todo bien afuera? Me asusté un poquito con el pestañeo... 🥺",
};

const ACT1_REFRESH_3: Record<Nature, string> = {
  hyperactive: "¡¡TRES!! ¡¡Estamos atrapados en un bucle de tiempo!! ¡Ayudaaa! ¡No, mentira, está divertido! ¡Holaaa! ⏱️",
  lucky:       "Tres veces... la tercera es la vencida, dicen. Pero si sigues refrescando, igual y nos da buena suerte. ¡Hola! 🎰",
  salty:       "Tres saludos. Esto ya es acoso. ¿Podemos avanzar a la Lotería o vas a seguir picándole al F5? 💢",
  methodical:  "Reintento número 3. Sugiero verificar estabilidad de red local. Saludo protocolario ejecutado. 💻",
  shy:         "H-hola... ¿es la tercera vez, verdad? Tal vez... tal vez no quieres que salga del cascarón... 🥚💦",
};

const ACT1_REFRESH_4: Record<Nature, string> = {
  hyperactive: "¡¡CUATRO REINICIOS!! ¡¡Mi cascarón va a empezar a brillar si seguimos así!! ¡Hola por cuarta vez! 🌟",
  lucky:       "Cuatro veces. Definitivamente el destino quiere que nos hagamos mejores amigos antes de empezar. ¡Hola! 🤝",
  salty:       "Cuatro. Ya no es gracioso. Mi paciencia es tan limitada como el agua dulce del cenote. Avanza, por favor. 😤",
  methodical:  "Reintento número 4. Límite de saludos dinámicos alcanzado. Recomendación: presionar botón 'Continuar'. 📌",
  shy:         "Hola... ya son cuatro veces. Si estás nervioso como yo, está bien. Podemos esperar aquí... 🌸",
};

const ACT1_WAKE_UP: Record<Nature, string> = {
  hyperactive: "¡¡¡AAAAHHH!!! ¡¡Me dormí!! ¡¡Pensé que habías ido por unos taquitos!! ¡Vamos a jugar ya ya ya! 🌮💨",
  lucky:       "Ah... me quedé dormido. Soñé que ganábamos la lotería y nos llenábamos de Axofichas. ¿Ahora sí empezamos? 🍀",
  salty:       "*Bostezo*... Al fin despiertas. O me despiertas. Como sea, avancemos antes de que me vuelva a dormir. 🥱",
  methodical:  "Fase de reposo involuntario terminada. El tiempo de inactividad superó el umbral. Continuemos con el tutorial. 📈",
  shy:         "Oh... lo siento, me dio un poquito de sueño con tanta espera. Qué bueno que sigues aquí. ¿Continuamos? 👉👈",
};

export function getAct1RefreshLines(nature: Nature, count: number): string[] {
  if (count === 1) return [ACT1_REFRESH_1[nature]];
  if (count === 2) return [ACT1_REFRESH_2[nature]];
  if (count === 3) return [ACT1_REFRESH_3[nature]];
  if (count === 4) return [ACT1_REFRESH_4[nature]];
  return [
    "*Zzz... Zzz... (Tu Webito se quedó dormido de tanto esperar)* 💤",
    ACT1_WAKE_UP[nature]
  ];
}
