/**
 * Estados y perfiles de movimiento del títere bípedo (plan puppet bípedo §B).
 * Los axolotitos caminan erguidos en espacios concurridos y nadan (swimming)
 * solo en la cueva para ir a su camita.
 */

export type PuppetState = "idle" | "walking" | "swimming" | "sleeping" | "playing" | "sitting";

export interface MotionProfile {
  /** Ciclos/s del paso (caminata) o pataleo (nado). */
  stepRate: number;
  /** Amplitud de rotación de piernas (rad). */
  legSwing: number;
  /** Amplitud de rotación de brazos, en contrafase (rad). */
  armSwing: number;
  /** Bob vertical en px; en caminata son 2 apoyos por ciclo. */
  bobAmp: number;
  /** Squash de respiración del torso (delta de scaleY). */
  breathAmp: number;
  breathRate: number;
  /** Velocidad de ondulación de branquias (rad/s). */
  gillSpeed: number;
  /** Vaivén de cola: amplitud (rad) y velocidad (rad/s). */
  tailAmp: number;
  tailRate: number;
  /** Balanceo de peso de lado a lado en idle (rad). */
  sway: number;
  /** Inclinación del torso al caminar (rad). */
  lean: number;
  /** Rotación de rigRoot: 0 de pie, -π/2 nadando, ~-1.25 dormido acurrucado. */
  tilt: number;
  /** Px que flota rigRoot sobre el piso (nado / camita). */
  lift: number;
  /** Multiplicador de alpha de la sombra (flotando proyecta menos). */
  shadowAlpha: number;
  /** Rotación base o offset para las piernas (rad). */
  legOffset?: number;
  /** Rotación base o offset para los brazos (rad). */
  armOffset?: number;
}

export const PROFILES: Record<PuppetState, MotionProfile> = {
  idle: {
    stepRate: 0, legSwing: 0, armSwing: 0, bobAmp: 0,
    breathAmp: 0.05, breathRate: 2.0, gillSpeed: 3.4,
    tailAmp: 0.1, tailRate: 1.6, sway: 0.045, lean: 0,
    tilt: 0, lift: 0, shadowAlpha: 1,
    legOffset: 0, armOffset: 0,
  },
  walking: {
    stepRate: 1.7, legSwing: 0.55, armSwing: 0.35, bobAmp: 4,
    breathAmp: 0.04, breathRate: 3.0, gillSpeed: 5.0,
    tailAmp: 0.18, tailRate: 3.4, sway: 0, lean: 0.08,
    tilt: 0, lift: 0, shadowAlpha: 1,
    legOffset: 0, armOffset: 0,
  },
  swimming: {
    stepRate: 3.6, legSwing: 0.3, armSwing: 0.15, bobAmp: 6,
    breathAmp: 0.04, breathRate: 2.4, gillSpeed: 6.0,
    tailAmp: 0.55, tailRate: 5.0, sway: 0, lean: 0,
    tilt: -Math.PI / 2, lift: 56, shadowAlpha: 0.25, // lift increased slightly for longer limbs
    legOffset: 0, armOffset: 0,
  },
  sleeping: {
    stepRate: 0, legSwing: 0, armSwing: 0, bobAmp: 0,
    breathAmp: 0.08, breathRate: 1.0, gillSpeed: 1.2,
    tailAmp: 0.04, tailRate: 0.8, sway: 0, lean: 0,
    tilt: -1.25, lift: 10, shadowAlpha: 0.4,
    legOffset: 0, armOffset: 0,
  },
  playing: {
    stepRate: 2.4, legSwing: 0.25, armSwing: 0.85, bobAmp: 13,
    breathAmp: 0.06, breathRate: 4.0, gillSpeed: 6.5,
    tailAmp: 0.35, tailRate: 4.5, sway: 0, lean: 0,
    tilt: 0, lift: 0, shadowAlpha: 1,
    legOffset: 0, armOffset: 0,
  },
  sitting: {
    stepRate: 0, legSwing: 0, armSwing: 0, bobAmp: 0,
    breathAmp: 0.05, breathRate: 2.0, gillSpeed: 3.4,
    tailAmp: 0.1, tailRate: 1.5, sway: 0.03, lean: 0.05,
    tilt: 0, lift: -20, shadowAlpha: 0.85,
    legOffset: -Math.PI / 3.2, // legs angle forward and down
    armOffset: -Math.PI / 3.0, // arms angle forward towards table/lap
  },
};

/** Duración del cross-fade: más larga cuando el cuerpo gira mucho (de pie ↔ nadando). */
export function TRANSITION_SECS_FOR(from: MotionProfile, to: MotionProfile): number {
  return Math.abs((to.tilt ?? 0) - (from.tilt ?? 0)) > 0.5 ? 0.5 : 0.25;
}

/** Ease cúbico para que el tilt grande (de pie ↔ nadando) no se vea brusco. */
export function easeInOutCubic(t: number): number {
  return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
}

/** Interpolación campo a campo entre dos perfiles (t ∈ [0,1], ya easeado). */
export function lerpProfile(from: MotionProfile, to: MotionProfile, t: number): MotionProfile {
  const out = {} as Record<keyof MotionProfile, number>;
  for (const key of Object.keys(from) as (keyof MotionProfile)[]) {
    const vFrom = from[key] ?? 0;
    const vTo = to[key] ?? 0;
    out[key] = vFrom + (vTo - vFrom) * t;
  }
  return out as MotionProfile;
}
