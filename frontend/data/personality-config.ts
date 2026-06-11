/**
 * personality-config.ts — Axolotito Nature personality phrases and chat effects.
 *
 * Used by QuickReactionWheel and SpeechBubble to customize chat behavior
 * based on the Axolotito's nature (personality trait).
 */

// ── Types ─────────────────────────────────────────────────────────────────────

export type Nature = "hyperactive" | "shy" | "showoff" | "curious";

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
  hyperactive: {
    greeting: "HOLA A TODOS!",
    nearWin: "A UNA CARTA!! AAAH!",
    victory: "GANEEEE! TOMA!",
    defeat: "Grrr, revancha ya!",
    taunt: "QUE ESPERAN?!",
  },
  shy: {
    greeting: "hola...",
    nearWin: "estoy cerca... creo",
    victory: "gane... que bien",
    defeat: "ni modo, felicidades",
    taunt: "suerte a todos...",
  },
  showoff: {
    greeting: "Llego el rey/pro!",
    nearWin: "Ya pueden irse a casa",
    victory: "ESO ES TODO! FACIL!",
    defeat: "Estaba arreglado.",
    taunt: "A ver, impresionenme.",
  },
  curious: {
    greeting: "Listos para perder?",
    nearWin: "Que carta falta? Ah!",
    victory: "Interesante resultado!",
    defeat: "Interesante jugada...",
    taunt: "Cual es su estrategia?",
  },
};

// ── Chat visual effects by nature ─────────────────────────────────────────────

export const NATURE_CHAT_EFFECTS: Record<Nature, NatureChatEffect> = {
  hyperactive: {
    className: "font-bold",
    particleEmoji: "⚡",
  },
  shy: {
    className: "text-xs opacity-80",
    particleEmoji: "💧",
  },
  showoff: {
    className: "italic",
    particleEmoji: "✨",
  },
  curious: {
    className: "font-mono text-xs",
    particleEmoji: "🔍",
  },
};

// ── Default phrases for the QuickReactionWheel (3-phrase slots) ───────────────

export function getQuickPhrases(nature: Nature | null | undefined): string[] {
  const n = nature ?? "curious";
  const phrases = PERSONALITY_PHRASES[n] ?? PERSONALITY_PHRASES.curious;
  return [phrases.greeting, phrases.taunt, phrases.nearWin];
}

// ── Victory/defeat phrase for result screen ───────────────────────────────────

export function getResultPhrase(
  nature: Nature | null | undefined,
  won: boolean
): string {
  const n = nature ?? "curious";
  const phrases = PERSONALITY_PHRASES[n] ?? PERSONALITY_PHRASES.curious;
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

export const PERSONALITY_REACTIONS: Record<NatureType, ReactionMap> = {
  hyperactive: {
    join:        { emoji: "⚡", animClass: "animate-axo-bob", description: "Entrando con energia" },
    near_win:    { emoji: "🔥", animClass: "animate-pulse", description: "Temblando de emocion" },
    victory:     { emoji: "🎉", animClass: "animate-axo-bob", description: "Celebrando freneticamente" },
    defeat:      { emoji: "💢", animClass: "animate-shake", description: "Frustrado" },
    idle:        { emoji: "⚡", animClass: "animate-axo-bob", description: "Inquieto" },
    card_called: { emoji: "👀", animClass: "animate-bounce", description: "Carta cantada!" },
    tension_high:{ emoji: "⚡", animClass: "animate-pulse", description: "Tension electrica" },
    afk:         { emoji: "💤", animClass: "animate-pulse", description: "Se quedo dormido" },
  },
  shy: {
    join:        { emoji: "💧", animClass: "animate-nest-idle", description: "Entrando timidamente" },
    near_win:    { emoji: "😳", animClass: "animate-pulse", description: "Nervioso" },
    victory:     { emoji: "🥺", animClass: "animate-nest-idle", description: "Feliz pero timido" },
    defeat:      { emoji: "😔", animClass: "animate-nest-idle", description: "Decepcionado" },
    idle:        { emoji: "💧", animClass: "animate-nest-idle", description: "Tranquilo" },
    card_called: { emoji: "👁️", animClass: "animate-pulse", description: "Atento" },
    tension_high:{ emoji: "💧", animClass: "animate-pulse", description: "Tenso" },
    afk:         { emoji: "💤", animClass: "animate-nest-idle", description: "Escondido" },
  },
  showoff: {
    join:        { emoji: "👑", animClass: "animate-axo-wander", description: "Llego la realeza" },
    near_win:    { emoji: "😎", animClass: "animate-axo-bob", description: "Confiado" },
    victory:     { emoji: "🏆", animClass: "animate-axo-wander", description: "Triunfante" },
    defeat:      { emoji: "🤨", animClass: "animate-shake", description: "Incredulo" },
    idle:        { emoji: "✨", animClass: "animate-axo-wander", description: "Presumiendo" },
    card_called: { emoji: "🧐", animClass: "animate-axo-bob", description: "Analizando" },
    tension_high:{ emoji: "✨", animClass: "animate-pulse", description: "Brillando bajo presion" },
    afk:         { emoji: "💤", animClass: "animate-axo-wander", description: "Descansando con estilo" },
  },
  curious: {
    join:        { emoji: "🔍", animClass: "animate-axo-bob", description: "Explorando" },
    near_win:    { emoji: "🤔", animClass: "animate-pulse", description: "Intrigado" },
    victory:     { emoji: "💡", animClass: "animate-axo-bob", description: "Descubrimiento!" },
    defeat:      { emoji: "📝", animClass: "animate-nest-idle", description: "Tomando notas" },
    idle:        { emoji: "🔍", animClass: "animate-axo-bob", description: "Curioseando" },
    card_called: { emoji: "👀", animClass: "animate-bounce", description: "Observando" },
    tension_high:{ emoji: "🔍", animClass: "animate-pulse", description: "Escudrinando" },
    afk:         { emoji: "💤", animClass: "animate-nest-idle", description: "Investigando en sueños" },
  },
};

export function generateAuraParticles(nature: NatureType): AuraParticle[] {
  const particleMap: Record<NatureType, { emoji: string; color: string; count: number }> = {
    hyperactive: { emoji: "⚡", color: "#FFD700", count: 6 },
    shy:         { emoji: "💧", color: "#60A5FA", count: 4 },
    showoff:     { emoji: "✨", color: "#FBBF24", count: 5 },
    curious:     { emoji: "🔍", color: "#00CED1", count: 5 },
  };

  const config = particleMap[nature] ?? particleMap.curious;
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
