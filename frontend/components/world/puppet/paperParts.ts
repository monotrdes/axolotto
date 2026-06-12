import { Assets, Container, Sprite, Graphics } from "pixi.js";

/**
 * Piezas base del títere bípedo en estilo papel recortado, dibujadas con
 * Graphics (placeholder de Fase 1). Cuando exista el atlas `axolotito-parts`,
 * estas funciones se sustituyen por Sprites — la jerarquía del rig
 * (bipedRig) no cambia. Convención: borde blanco = filo de papel.
 *
 * Las partes variantes por rareza (branquias, ojos, boca, cola, extremidades,
 * frente) viven en `./parts/` y se resuelven vía buildPart().
 */

export const PAPER_EDGE = 0xfff7ec;
export const EDGE_W = 5;
export const INK = 0x2b2b3a;

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

/** Helper para retornar un Sprite de la caché si existe, aplicando ancla y tinte. */
export function getTextureOrFallback(
  key: string,
  anchorX: number,
  anchorY: number,
  tint?: number,
): Container | null {
  if (Assets.cache.has(key)) {
    const sprite = Sprite.from(key);
    sprite.anchor.set(anchorX, anchorY);
    if (tint !== undefined) {
      sprite.tint = tint;
    }
    return sprite;
  }
  return null;
}

/** Torso bípedo: elipse vertical centrada en el pecho. */
export function drawBody(tint: number): Container {
  const sprite = getTextureOrFallback("body", 0.5, 0.5, tint);
  if (sprite) return sprite;
  return new Graphics()
    .ellipse(0, 0, 30, 42)
    .fill(tint)
    .stroke({ color: PAPER_EDGE, width: EDGE_W });
}

export function drawHead(tint: number): Container {
  const sprite = getTextureOrFallback("head", 0.5, 0.5, tint);
  if (sprite) return sprite;
  return new Graphics()
    .circle(0, 0, 30)
    .fill(tint)
    .stroke({ color: PAPER_EDGE, width: EDGE_W });
}

export function drawShadow(): Container {
  const sprite = getTextureOrFallback("shadow", 0.5, 0.5);
  if (sprite) return sprite;
  return new Graphics().ellipse(0, 0, 36, 9).fill({ color: 0x000000, alpha: 0.22 });
}

/** Branquia más cálida que la piel para que resalte (el "alma" del axolote). */
export function gillAccent(tint: number): number {
  // Mezcla simple hacia bugambilia para todas las pieles.
  const r = ((tint >> 16) & 0xff) * 0.45 + 0xe4 * 0.55;
  const g = ((tint >> 8) & 0xff) * 0.45 + 0x00 * 0.55;
  const b = (tint & 0xff) * 0.45 + 0x7c * 0.55;
  return (Math.round(r) << 16) | (Math.round(g) << 8) | Math.round(b);
}
