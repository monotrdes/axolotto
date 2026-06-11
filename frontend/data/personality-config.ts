/**
 * personality-config.ts — Axolotito Nature personality phrases and chat effects.
 *
 * Used by QuickReactionWheel and SpeechBubble to customize chat behavior
 * based on the Axolotito's nature (personality trait).
 *
 * Las 6 naturalezas reales (backend incubation.py, wiki §04):
 *   methodical | lucky | hyperactive | glutton | shy | wise
 *
 * Compatibilidad legacy: showoff → lucky, curious → wise (plan task-84 §5).
 */

// ── Types ─────────────────────────────────────────────────────────────────────

export type Nature =
  | "methodical"
  | "lucky"
  | "hyperactive"
  | "glutton"
  | "shy"
  | "wise";

/** Mapea valores legacy (plan v1) a las 6 naturalezas reales del backend. */
export function normalizeNature(raw: string | null | undefined): Nature {
  switch (raw) {
    case "methodical": return "methodical";
    case "lucky": return "lucky";
    case "hyperactive": return "hyperactive";
    case "glutton": return "glutton";
    case "shy": return "shy";
    case "wise": return "wise";
    // Legacy (plan v1 — showoff/curious no existen en el backend):
    case "showoff": return "lucky";
    case "curious": return "wise";
    // Fallback: si el backend llegara a mandar algo no reconocido.
    default: return "hyperactive";
  }
}

export interface PersonalityPhrases {
  greeting: string;
  nearWin: string;
  victory: string;
  defeat: string;
  taunt: string;
}

export interface NatureChatEffect {
  className: string;
  particleEmoji: string;
}

// ── Quick phrases by nature ───────────────────────────────────────────────────

export const PERSONALITY_PHRASES: Record<Nature, PersonalityPhrases> = {
  methodical: {
    greeting: "Analizando la sala…",
    nearWin: "Una carta. Probabilidad: 97.3%.",
    victory: "Exactamente como calculé.",
    defeat: "Revisaré los datos para la próxima.",
    taunt: "Tu estrategia es estadísticamente subóptima.",
  },
  lucky: {
    greeting: "¡Llegó la buena suerte!",
    nearWin: "¡El destino me sonríe!",
    victory: "¡ESO ES TODO! ¡FÁCIL!",
    defeat: "Estaba arreglado, ¡la suerte volverá!",
    taunt: "A ver, impresiónenme.",
  },
  hyperactive: {
    greeting: "¡HOLA A TODOS!",
    nearWin: "¡A UNA CARTA!! ¡AAAH!",
    victory: "¡GANEEEE! ¡TOMA!",
    defeat: "Grrr, ¡revancha ya!",
    taunt: "¡QUE ESPERAN?!",
  },
  glutton: {
    greeting: "Mmm, ¿alguien trajo garnachas?",
    nearWin: "Casi gano… necesito un snack.",
    victory: "¡BANQUETE! ¡Que traigan más!",
    defeat: "Perdí pero al menos cené rico.",
    taunt: "¿Y si apostamos comida?",
  },
  shy: {
    greeting: "hola…",
    nearWin: "estoy cerca… creo",
    victory: "gané… qué bien",
    defeat: "ni modo, felicidades",
    taunt: "suerte a todos…",
  },
  wise: {
    greeting: "El cenote me susurra secretos…",
    nearWin: "La intuición nunca falla.",
    victory: "El conocimiento es la verdadera victoria.",
    defeat: "Cada derrota es una lección.",
    taunt: "¿Cuál es su estrategia?",
  },
};

// ── Chat visual effects by nature ─────────────────────────────────────────────

export const NATURE_CHAT_EFFECTS: Record<Nature, NatureChatEffect> = {
  methodical: {
    className: "font-mono text-xs",
    particleEmoji: "📊",
  },
  lucky: {
    className: "italic",
    particleEmoji: "✨",
  },
  hyperactive: {
    className: "font-bold",
    particleEmoji: "⚡",
  },
  glutton: {
    className: "font-bold",
    particleEmoji: "🍩",
  },
  shy: {
    className: "text-xs opacity-80",
    particleEmoji: "💧",
  },
  wise: {
    className: "font-mono text-xs",
    particleEmoji: "🔍",
  },
};

// ── Default phrases for the QuickReactionWheel (3-phrase slots) ───────────────

export function getQuickPhrases(nature: Nature | null | undefined): string[] {
  const n = normalizeNature(nature);
  const phrases = PERSONALITY_PHRASES[n] ?? PERSONALITY_PHRASES.hyperactive;
  return [phrases.greeting, phrases.taunt, phrases.nearWin];
}

// ── Victory/defeat phrase for result screen ───────────────────────────────────

export function getResultPhrase(
  nature: Nature | null | undefined,
  won: boolean
): string {
  const n = normalizeNature(nature);
  const phrases = PERSONALITY_PHRASES[n] ?? PERSONALITY_PHRASES.hyperactive;
  return won ? phrases.victory : phrases.defeat;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Personality Reactions API (used by PersonalityReactions.tsx)
// ═══════════════════════════════════════════════════════════════════════════════

export type NatureType = Nature;

export type NatureTrigger =
  | "join"
  | "near_win"
  | "victory"
  | "defeat"
  | "idle"
  | "card_called"
  | "tension_high"
  | "afk";

export interface AuraParticle {
  emoji: string;
  x: number;
  y: number;
  animClass: string;
  color: string;
}

interface ReactionConfig {
  emoji: string;
  animClass: string;
  description: string;
}

type ReactionMap = Record<NatureTrigger, ReactionConfig>;

/**
 * Reacciones de las 6 naturalezas reales del backend (plan task-84 §5).
 * Matches backend/app/api/v1/endpoints/incubation.py NATURALEZAS.
 */
export const PERSONALITY_REACTIONS: Record<NatureType, ReactionMap> = {
  methodical: {
    join:        { emoji: "🧐", animClass: "animate-nest-idle", description: "Evaluando la sala" },
    near_win:    { emoji: "📊", animClass: "animate-pulse", description: "Probabilidad: 97.3%" },
    victory:     { emoji: "🏆", animClass: "animate-axo-bob", description: "Reverencia precisa" },
    defeat:      { emoji: "📝", animClass: "animate-nest-idle", description: "Tomando notas" },
    idle:        { emoji: "🤔", animClass: "animate-nest-idle", description: "Calculando" },
    card_called: { emoji: "👀", animClass: "animate-bounce", description: "Carta registrada" },
    tension_high:{ emoji: "📊", animClass: "animate-pulse", description: "Recalculando" },
    afk:         { emoji: "💤", animClass: "animate-nest-idle", description: "En pausa analítica" },
  },
  lucky: {
    join:        { emoji: "🍀", animClass: "animate-axo-wander", description: "¡Llegó la suerte!" },
    near_win:    { emoji: "🌟", animClass: "animate-axo-bob", description: "El destino llama" },
    victory:     { emoji: "🎉", animClass: "animate-axo-wander", description: "Baile de la suerte" },
    defeat:      { emoji: "😅", animClass: "animate-shake", description: "La suerte volverá" },
    idle:        { emoji: "✨", animClass: "animate-axo-wander", description: "Brillando" },
    card_called: { emoji: "🧐", animClass: "animate-axo-bob", description: "¿Será mi carta?" },
    tension_high:{ emoji: "✨", animClass: "animate-pulse", description: "Destino cercano" },
    afk:         { emoji: "💤", animClass: "animate-axo-wander", description: "Soñando con premios" },
  },
  hyperactive: {
    join:        { emoji: "⚡", animClass: "animate-axo-bob", description: "Entrando con energía" },
    near_win:    { emoji: "🔥", animClass: "animate-pulse", description: "Temblando de emoción" },
    victory:     { emoji: "🎉", animClass: "animate-axo-bob", description: "Saltos caóticos" },
    defeat:      { emoji: "💢", animClass: "animate-shake", description: "Berrinche" },
    idle:        { emoji: "⚡", animClass: "animate-axo-bob", description: "Inquieto" },
    card_called: { emoji: "👀", animClass: "animate-bounce", description: "¡Carta cantada!" },
    tension_high:{ emoji: "⚡", animClass: "animate-pulse", description: "Tensión eléctrica" },
    afk:         { emoji: "💤", animClass: "animate-pulse", description: "Se quedó dormido" },
  },
  glutton: {
    join:        { emoji: "🍩", animClass: "animate-axo-bob", description: "Con garnachas en mano" },
    near_win:    { emoji: "🍿", animClass: "animate-pulse", description: "Comiendo por nervios" },
    victory:     { emoji: "🎂", animClass: "animate-axo-bob", description: "¡Banquete!" },
    defeat:      { emoji: "🍕", animClass: "animate-nest-idle", description: "Comiendo por estrés" },
    idle:        { emoji: "🍬", animClass: "animate-axo-bob", description: "Mordisqueando" },
    card_called: { emoji: "👀", animClass: "animate-bounce", description: "Pausa el snack" },
    tension_high:{ emoji: "🍩", animClass: "animate-pulse", description: "Antojo nervioso" },
    afk:         { emoji: "💤", animClass: "animate-nest-idle", description: "Siesta de comida" },
  },
  shy: {
    join:        { emoji: "💧", animClass: "animate-nest-idle", description: "Entrando tímidamente" },
    near_win:    { emoji: "😳", animClass: "animate-pulse", description: "Nervioso" },
    victory:     { emoji: "🥺", animClass: "animate-nest-idle", description: "Celebración tímida" },
    defeat:      { emoji: "😔", animClass: "animate-nest-idle", description: "Escondido tras su tabla" },
    idle:        { emoji: "💧", animClass: "animate-nest-idle", description: "Tranquilo" },
    card_called: { emoji: "👁️", animClass: "animate-pulse", description: "Marca escondido" },
    tension_high:{ emoji: "💧", animClass: "animate-pulse", description: "Encogido" },
    afk:         { emoji: "💤", animClass: "animate-nest-idle", description: "Escondido" },
  },
  wise: {
    join:        { emoji: "🦉", animClass: "animate-nest-idle", description: "Observando en silencio" },
    near_win:    { emoji: "🧘", animClass: "animate-nest-idle", description: "Sereno" },
    victory:     { emoji: "💡", animClass: "animate-axo-bob", description: "Levita con aureola" },
    defeat:      { emoji: "📿", animClass: "animate-nest-idle", description: "Aceptación serena" },
    idle:        { emoji: "🔍", animClass: "animate-axo-bob", description: "Meditando" },
    card_called: { emoji: "👁️", animClass: "animate-bounce", description: "Percepción aguda" },
    tension_high:{ emoji: "🧘", animClass: "animate-pulse", description: "Paz bajo presión" },
    afk:         { emoji: "💤", animClass: "animate-nest-idle", description: "Sueños de sabiduría" },
  },
};

export function generateAuraParticles(nature: NatureType): AuraParticle[] {
  const particleMap: Record<NatureType, { emoji: string; color: string; count: number }> = {
    methodical:   { emoji: "📊", color: "#60A5FA", count: 5 },
    lucky:        { emoji: "✨", color: "#FBBF24", count: 5 },
    hyperactive:  { emoji: "⚡", color: "#FFD700", count: 6 },
    glutton:      { emoji: "🍩", color: "#F59E0B", count: 4 },
    shy:          { emoji: "💧", color: "#60A5FA", count: 4 },
    wise:         { emoji: "🔍", color: "#00CED1", count: 5 },
  };

  const config = particleMap[nature] ?? particleMap.hyperactive;
  const particles: AuraParticle[] = [];

  for (let i = 0; i < config.count; i++) {
    particles.push({
      emoji: config.emoji,
      x: Math.round(20 + Math.random() * 60),
      y: Math.round(20 + Math.random() * 60),
      animClass: i % 2 === 0 ? "animate-axo-bob" : "animate-nest-idle",
      color: config.color,
    });
  }

  return particles;
}
