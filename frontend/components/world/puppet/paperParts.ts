import { Graphics } from "pixi.js";

/**
 * Partes del títere en estilo papel recortado, dibujadas con Graphics
 * (placeholder de Fase 1). Cuando exista el atlas `axolotito-parts`,
 * estas funciones se sustituyen por Sprites — la jerarquía del rig
 * (AxolotitoPuppet) no cambia. Convención: borde blanco = filo de papel.
 */

const PAPER_EDGE = 0xfff7ec;
const EDGE_W = 5;

/** Colores de piel del backend (axolotito.py: skin_color). */
export const SKIN_COLORS: Record<string, number> = {
  pink: 0xffa3c0,
  gray_light: 0xc9ccd6,
  gray_dark: 0x6b7080,
  gold: 0xf5c542,
  astral: 0x9b6df0,
};

export function skinToTint(skin?: string): number {
  return SKIN_COLORS[skin ?? "pink"] ?? SKIN_COLORS.pink;
}

export function drawBody(tint: number): Graphics {
  return new Graphics()
    .ellipse(0, 0, 52, 38)
    .fill(tint)
    .stroke({ color: PAPER_EDGE, width: EDGE_W });
}

export function drawHead(tint: number): Graphics {
  return new Graphics()
    .circle(0, 0, 36)
    .fill(tint)
    .stroke({ color: PAPER_EDGE, width: EDGE_W });
}

/** Una rama de branquia; el rig coloca 3 por lado con rotaciones distintas. */
export function drawGill(accent: number): Graphics {
  return new Graphics()
    .ellipse(16, 0, 18, 7)
    .fill(accent)
    .stroke({ color: PAPER_EDGE, width: 3 });
}

export function drawTail(tint: number): Graphics {
  return new Graphics()
    .poly([0, -16, 64, -4, 64, 4, 0, 16])
    .fill(tint)
    .stroke({ color: PAPER_EDGE, width: 4 });
}

export function drawLimb(tint: number): Graphics {
  return new Graphics()
    .roundRect(-6, 0, 12, 26, 6)
    .fill(tint)
    .stroke({ color: PAPER_EDGE, width: 3 });
}

export function drawEyeOpen(): Graphics {
  return new Graphics()
    .circle(0, 0, 7)
    .fill(0xffffff)
    .circle(1.5, 0.5, 3.5)
    .fill(0x2b2b3a);
}

export function drawEyeClosed(): Graphics {
  return new Graphics()
    .moveTo(-6, 0)
    .quadraticCurveTo(0, 5, 6, 0)
    .stroke({ color: 0x2b2b3a, width: 2.5 });
}

export function drawMouthSmile(): Graphics {
  return new Graphics()
    .moveTo(-9, 0)
    .quadraticCurveTo(0, 8, 9, 0)
    .stroke({ color: 0x2b2b3a, width: 2.5 });
}

export function drawShadow(): Graphics {
  return new Graphics().ellipse(0, 0, 44, 10).fill({ color: 0x000000, alpha: 0.22 });
}

/** Branquia más cálida que la piel para que resalte (el "alma" del axolote). */
export function gillAccent(tint: number): number {
  // Mezcla simple hacia bugambilia para todas las pieles.
  const r = ((tint >> 16) & 0xff) * 0.45 + 0xe4 * 0.55;
  const g = ((tint >> 8) & 0xff) * 0.45 + 0x00 * 0.55;
  const b = (tint & 0xff) * 0.45 + 0x7c * 0.55;
  return (Math.round(r) << 16) | (Math.round(g) << 8) | Math.round(b);
}
