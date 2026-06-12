/**
 * Colores de piel y funciones de tinte compartidas por los billboards 3D
 * (AxolotitoBillboard) y escenas del mundo-diorama.
 * Extraído de paperParts.ts — sin dependencia de Pixi.
 */

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

/** Branquia más cálida que la piel para que resalte (el "alma" del axolote). */
export function gillAccent(tint: number): number {
  // Mezcla simple hacia bugambilia para todas las pieles.
  const r = ((tint >> 16) & 0xff) * 0.45 + 0xe4 * 0.55;
  const g = ((tint >> 8) & 0xff) * 0.45 + 0x00 * 0.55;
  const b = (tint & 0xff) * 0.45 + 0x7c * 0.55;
  return (Math.round(r) << 16) | (Math.round(g) << 8) | Math.round(b);
}
