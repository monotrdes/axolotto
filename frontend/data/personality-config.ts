// ── Personality Reactions Configuration ──────────────────────────────────────
// Mapea cada naturaleza × trigger a su emoji, animación CSS, aura y descripción.
// Use: import { PERSONALITY_REACTIONS } from "@/data/personality-config";

// ── Types ────────────────────────────────────────────────────────────────────

export type NatureType = "hyperactive" | "shy" | "showoff" | "curious";

export type NatureTrigger =
  | "hit"
  | "miss"
  | "near_win"
  | "won"
  | "lost"
  | "idle"
  | "card_called"
  | "tension_critical";

export interface PersonalityReaction {
  /** Emoji principal que se muestra */
  emoji: string;
  /** Clase de animacion CSS (animate-*) */
  animClass: string;
  /** Clase CSS del aura de particulas */
  auraClass?: string;
  /** Texto corto que aparece junto al avatar */
  label: string;
  /** Descripcion (espanol) de lo que hace el axolotito */
  description: string;
}

// ── Full mapping: 4 natures × 8 triggers = 32 reactions ──────────────────────

export const PERSONALITY_REACTIONS: Record<
  NatureType,
  Record<NatureTrigger, PersonalityReaction>
> = {
  // ══════════════════════════════════════════════════════════════════════════
  // HYPERACTIVE — ⚡ energia electrica, rapido, explosivo
  // ══════════════════════════════════════════════════════════════════════════
  hyperactive: {
    idle: {
      emoji: "⚡",
      animClass: "animate-hyper-bounce",
      auraClass: "aura-spark",
      label: "",
      description: "Tembloroso y listo para la accion",
    },
    card_called: {
      emoji: "👀",
      animClass: "animate-hyper-tremble",
      auraClass: "aura-spark",
      label: "¡MI CARTAAA!",
      description: "Se estira hacia el frente como para atrapar la carta",
    },
    hit: {
      emoji: "🎯",
      animClass: "animate-hyper-bounce",
      auraClass: "aura-spark",
      label: "¡CAZADO!",
      description: "Brinca de emocion y da una voltereta",
    },
    miss: {
      emoji: "💥",
      animClass: "animate-hyper-tremble",
      auraClass: "aura-spark",
      label: "¡NOOO!",
      description: "Se sacude con frustracion electrica",
    },
    tension_critical: {
      emoji: "🌀",
      animClass: "animate-hyper-spiral",
      auraClass: "aura-spark",
      label: "¡TENSION!",
      description: "Gira como un torbellino de nervios",
    },
    won: {
      emoji: "🏆",
      animClass: "animate-hyper-flip",
      auraClass: "aura-spark",
      label: "¡SOY EL MEJOR!",
      description: "Hace una voltereta hacia atras y aterriza en pose de poder",
    },
    lost: {
      emoji: "😤",
      animClass: "animate-hyper-tantrum",
      auraClass: "aura-spark",
      label: "¡RABIETA!",
      description: "Se pone boca abajo y patalea furiosamente",
    },
    near_win: {
      emoji: "🎆",
      animClass: "animate-hyper-spiral",
      auraClass: "aura-spark",
      label: "¡CERCA!",
      description: "Da vueltas en circulo de la emocion",
    },
  },

  // ══════════════════════════════════════════════════════════════════════════
  // SHY / TIMID — 😊 gentil, lento, sutil, sonrojado
  // ══════════════════════════════════════════════════════════════════════════
  shy: {
    idle: {
      emoji: "😊",
      animClass: "animate-shy-blush",
      auraClass: "aura-droplet",
      label: "",
      description: "Sonrie timidamente mientras se mece",
    },
    card_called: {
      emoji: "👂",
      animClass: "animate-shy-peek",
      auraClass: "aura-droplet",
      label: "¿Mi carta?",
      description: "Se asoma curioso pero se esconde rapido",
    },
    hit: {
      emoji: "🌟",
      animClass: "animate-shy-blush",
      auraClass: "aura-droplet",
      label: "¡Bien!",
      description: "Sonrie y se sonroja suavemente",
    },
    miss: {
      emoji: "😅",
      animClass: "animate-shy-shrink",
      auraClass: "aura-droplet",
      label: "Oops...",
      description: "Se encoge un poco avergonzado",
    },
    tension_critical: {
      emoji: "💓",
      animClass: "animate-shy-bounce",
      auraClass: "aura-droplet",
      label: "Ayayay...",
      description: "Se mece nerviosamente de lado a lado",
    },
    won: {
      emoji: "🎀",
      animClass: "animate-shy-applaud",
      auraClass: "aura-droplet",
      label: "Gane...",
      description: "Aplaude lentamente con una sonrisa nerviosa",
    },
    lost: {
      emoji: "💧",
      animClass: "animate-shy-shrink",
      auraClass: "aura-droplet",
      label: "Otra vez sera...",
      description: "Suspira y se encoge con resignacion",
    },
    near_win: {
      emoji: "🫣",
      animClass: "animate-shy-peek",
      auraClass: "aura-droplet",
      label: "Ay no...",
      description: "Se tapa los ojos y asoma entre los dedos",
    },
  },

  // ══════════════════════════════════════════════════════════════════════════
  // SHOW-OFF / PROUD — ✨ orgulloso, dramático, llamativo
  // ══════════════════════════════════════════════════════════════════════════
  showoff: {
    idle: {
      emoji: "✨",
      animClass: "animate-showoff-pose",
      auraClass: "aura-sparkle",
      label: "",
      description: "Se pavonea con actitud de superioridad",
    },
    card_called: {
      emoji: "💅",
      animClass: "animate-showoff-pose",
      auraClass: "aura-sparkle",
      label: "Obvio...",
      description: "Se arregla las unas con indiferencia",
    },
    hit: {
      emoji: "😎",
      animClass: "animate-showoff-shades",
      auraClass: "aura-sparkle",
      label: "Facil.",
      description: "Se pone lentes oscuros con estilo",
    },
    miss: {
      emoji: "🤨",
      animClass: "animate-showoff-backturn",
      auraClass: "aura-sparkle",
      label: "Bah...",
      description: "Voltea la cara con desde",
    },
    tension_critical: {
      emoji: "🔥",
      animClass: "animate-showoff-pose",
      auraClass: "aura-sparkle",
      label: "Miren esto...",
      description: "Flexiona un musculo imaginario",
    },
    won: {
      emoji: "👑",
      animClass: "animate-showoff-bow",
      auraClass: "aura-sparkle",
      label: "¡SOY DIOS!",
      description: "Hace una reverencia dramatica para el publico",
    },
    lost: {
      emoji: "💢",
      animClass: "animate-showoff-backturn",
      auraClass: "aura-sparkle",
      label: "Me aburri...",
      description: "Voltea la espalda y se cruza de brazos",
    },
    near_win: {
      emoji: "⭐",
      animClass: "animate-showoff-pose",
      auraClass: "aura-sparkle",
      label: "Clase mundial",
      description: "Infla el pecho con orgullo",
    },
  },

  // ══════════════════════════════════════════════════════════════════════════
  // CURIOUS — 🔍 investigativo, analítico, observador
  // ══════════════════════════════════════════════════════════════════════════
  curious: {
    idle: {
      emoji: "🔍",
      animClass: "animate-curious-examine",
      auraClass: "aura-eye-float",
      label: "",
      description: "Examina el tablero con atencion",
    },
    card_called: {
      emoji: "🧐",
      animClass: "animate-curious-zoom",
      auraClass: "aura-eye-float",
      label: "Interesante...",
      description: "Saca una lupa y examina la carta",
    },
    hit: {
      emoji: "📌",
      animClass: "animate-curious-examine",
      auraClass: "aura-eye-float",
      label: "Anotado.",
      description: "Asiente con satisfaccion intelectual",
    },
    miss: {
      emoji: "📝",
      animClass: "animate-curious-notebook",
      auraClass: "aura-eye-float",
      label: "Tomare nota...",
      description: "Saca una libreta y escribe algo",
    },
    tension_critical: {
      emoji: "🤔",
      animClass: "animate-curious-zoom",
      auraClass: "aura-eye-float",
      label: "El patron...",
      description: "Se acerca al tablero estudiando el patron",
    },
    won: {
      emoji: "🧠",
      animClass: "animate-curious-examine",
      auraClass: "aura-eye-float",
      label: "Predecible.",
      description: "Ajusta sus lentes con aire de sabiduria",
    },
    lost: {
      emoji: "📚",
      animClass: "animate-curious-notebook",
      auraClass: "aura-eye-float",
      label: "Para la proxima...",
      description: "Toma notas sobre la estrategia del rival",
    },
    near_win: {
      emoji: "🔎",
      animClass: "animate-curious-zoom",
      auraClass: "aura-eye-float",
      label: "Casi...",
      description: "Saca una lupa gigante para buscar la carta faltante",
    },
  },
};

// ── Aura particle config ─────────────────────────────────────────────────────
// Define las particulas que flotan alrededor del avatar segun la naturaleza.

export interface AuraParticle {
  emoji: string;
  animClass: string;
  /** Posicion vertical relativa (%) */
  y: number;
  /** Posicion horizontal relativa (%) */
  x: number;
  /** Color CSS para la particula */
  color: string;
}

/** Genera 5 particulas de aura con posiciones semi-aleatorias para una naturaleza. */
export function generateAuraParticles(nature: NatureType): AuraParticle[] {
  const base: Pick<AuraParticle, "emoji" | "animClass" | "color"> =
    AURA_PARTICLE_BASE[nature];

  // 4-6 particulas con posiciones fijas estilo reloj
  const positions = [
    { y: 5, x: 5 },
    { y: 10, x: 80 },
    { y: 75, x: 5 },
    { y: 80, x: 80 },
    { y: 50, x: -5 },
    { y: 45, x: 95 },
  ];

  return positions.map((pos) => ({
    ...base,
    ...pos,
  }));
}

const AURA_PARTICLE_BASE: Record<
  NatureType,
  Pick<AuraParticle, "emoji" | "animClass" | "color">
> = {
  hyperactive: { emoji: "⚡", animClass: "animate-aura-spark", color: "#FFD700" },
  shy: { emoji: "💧", animClass: "animate-aura-droplet", color: "#87CEEB" },
  showoff: { emoji: "✨", animClass: "animate-aura-sparkle", color: "#FFD700" },
  curious: { emoji: "👁️", animClass: "animate-aura-eye-float", color: "#00CED1" },
};

// ── Helper: mapea AxoReaction → NatureTrigger ───────────────────────────────

/** Mapa de compatibilidad entre AxoReaction (legacy) y NatureTrigger. */
export const AXO_REACTION_TO_TRIGGER: Record<string, NatureTrigger> = {
  idle: "idle",
  card_called: "card_called",
  cell_marked: "hit",
  cell_missed: "miss",
  tension_critical: "tension_critical",
  won: "won",
  lost: "lost",
};
