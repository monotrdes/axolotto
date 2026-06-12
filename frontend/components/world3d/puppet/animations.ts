import { basePose, type PoseFrame, type View } from "./poses";

/**
 * Ciclos de animación del puppet: cada ciclo es una lista de PoseFrames
 * muestreados que `frameAtlas` hornea como celdas del atlas en build-time
 * (no hay repintado en runtime). La matemática viene del bipedAnimator
 * legacy (7d62e4b): piernas alternadas sin(φ)/sin(φ+π), brazos
 * contralaterales y bob -|cos(φ)| (dos apoyos por ciclo).
 */

export type AnimName =
  | "idleFront"
  | "idleBack"
  | "walkSide"
  | "walkFront"
  | "walkBack"
  | "swimSide"
  | "sleepSide";

export interface AnimDef {
  view: View;
  /** Frames por segundo al reproducir el ciclo. */
  fps: number;
  frames: PoseFrame[];
}

const TAU = Math.PI * 2;

function idleFrames(): PoseFrame[] {
  // A (branquias a un lado), B (al otro, bracitos caídos), blink (= A + ojos
  // cerrados, frame 2 — AxolotitoBillboard lo superpone con su timer).
  const a = basePose();
  a.gillSway = -0.7;
  const b = basePose();
  b.gillSway = 0.7;
  b.armFront = 0.08;
  b.armBack = -0.08;
  b.bob = -1.5;
  const blink: PoseFrame = { ...a, eyes: "closed" };
  return [a, b, blink];
}

function walkSideFrames(n = 6): PoseFrame[] {
  const frames: PoseFrame[] = [];
  for (let i = 0; i < n; i++) {
    const phi = (i / n) * TAU;
    const f = basePose();
    f.legFront = Math.sin(phi) * 0.55;
    f.legBack = Math.sin(phi + Math.PI) * 0.55;
    f.armFront = Math.sin(phi + Math.PI) * 0.35 - 0.08;
    f.armBack = Math.sin(phi) * 0.35 - 0.08;
    f.bob = Math.abs(Math.cos(phi)) * 5;
    f.lean = 0.14; // ~8° inclinado al frente (referencia papercraft)
    f.tailSwing = Math.sin(phi + 0.8) * 0.12;
    f.gillSway = Math.sin(phi) * 0.8;
    frames.push(f);
  }
  return frames;
}

/** Caminata vista de frente/espalda: piernas poco legibles → 2 frames. */
function walkFacingFrames(): PoseFrame[] {
  const frames: PoseFrame[] = [];
  for (const s of [1, -1]) {
    const f = basePose();
    f.legFront = s * 0.16;
    f.legBack = -s * 0.16;
    f.armFront = -s * 0.2;
    f.armBack = s * 0.2;
    f.bob = 3;
    f.gillSway = s * 0.7;
    frames.push(f);
  }
  return frames;
}

function swimFrames(n = 4): PoseFrame[] {
  const frames: PoseFrame[] = [];
  for (let i = 0; i < n; i++) {
    const phi = (i / n) * TAU;
    const f = basePose();
    f.tilt = -Math.PI / 2 + 0.12; // horizontal, hocico apenas arriba
    f.anchorY = 150; // figura centrada en la celda
    // patitas plegadas hacia atrás, remando suave y alternado
    f.legFront = 0.55 + Math.sin(phi) * 0.18;
    f.legBack = 0.55 + Math.sin(phi + Math.PI) * 0.18;
    f.armFront = 0.5 + Math.sin(phi + 1.2) * 0.15;
    f.armBack = 0.5 + Math.sin(phi + 1.2 + Math.PI) * 0.15;
    f.tailSwing = Math.sin(phi) * 0.35; // propulsión
    f.lean = Math.sin(phi + 0.5) * 0.05; // ondulación sutil del cuerpo
    f.gillSway = Math.sin(phi + 2) * 1;
    frames.push(f);
  }
  return frames;
}

function sleepFrames(): PoseFrame[] {
  const frames: PoseFrame[] = [];
  for (const s of [1, -1]) {
    const f = basePose();
    f.tilt = -Math.PI / 2;
    f.anchorY = 212; // acostado cerca del piso de la celda
    f.eyes = "closed";
    f.legFront = 0.5;
    f.legBack = 0.62;
    f.armFront = 0.55;
    f.armBack = 0.65;
    f.tailSwing = s * 0.05;
    f.gillSway = s * 0.35;
    frames.push(f);
  }
  return frames;
}

function backFrames(frames: PoseFrame[]): PoseFrame[] {
  return frames;
}

export const ANIMS: Record<AnimName, AnimDef> = {
  idleFront: { view: "front", fps: 0, frames: idleFrames() },
  idleBack: { view: "back", fps: 0, frames: backFrames(idleFrames().slice(0, 2)) },
  walkSide: { view: "side", fps: 10, frames: walkSideFrames() },
  walkFront: { view: "front", fps: 5, frames: walkFacingFrames() },
  walkBack: { view: "back", fps: 5, frames: walkFacingFrames() },
  swimSide: { view: "side", fps: 7, frames: swimFrames() },
  sleepSide: { view: "side", fps: 1.2, frames: sleepFrames() },
};

/** Índice del frame de parpadeo dentro de idleFront. */
export const IDLE_BLINK_FRAME = 2;
