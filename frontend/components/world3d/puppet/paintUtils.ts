/**
 * Utilidades de pintado compartidas por los painters de parte del puppet.
 * Mantienen la convención de papel picado: blobs con filo claro (EDGE)
 * y tinta morada (INK), igual que el billboard original.
 */

import { gillAccent } from "../skinColors";

export const EDGE = "#fff7ec"; // filo de papel
export const INK = "#2b2b3a";

export interface Palette {
  skin: string;
  belly: string;
  accent: string;
  accentLight: string;
  ink: string;
  edge: string;
}

export function css(c: number): string {
  return `#${c.toString(16).padStart(6, "0")}`;
}

export function mix(c: number, to: number, k: number): number {
  const r = ((c >> 16) & 0xff) * (1 - k) + ((to >> 16) & 0xff) * k;
  const g = ((c >> 8) & 0xff) * (1 - k) + ((to >> 8) & 0xff) * k;
  const b = (c & 0xff) * (1 - k) + (to & 0xff) * k;
  return (Math.round(r) << 16) | (Math.round(g) << 8) | Math.round(b);
}

export function makePalette(tint: number): Palette {
  return {
    skin: css(tint),
    belly: css(mix(tint, 0xffffff, 0.3)),
    accent: css(gillAccent(tint)),
    accentLight: css(mix(gillAccent(tint), 0xffffff, 0.35)),
    ink: INK,
    edge: EDGE,
  };
}

export type Rnd = (n: number) => number;

/** Pseudo-aleatorio determinista por seed (mismo axolotito = mismas chapas). */
export function makeRnd(seed: number): Rnd {
  return (n: number) => {
    const x = Math.sin(seed * 127.1 + n * 311.7) * 43758.5453;
    return x - Math.floor(x);
  };
}

/** Elipse con relleno y filo de papel (la primitiva de todo el puppet). */
export function blob(
  ctx: CanvasRenderingContext2D,
  cx: number,
  cy: number,
  rx: number,
  ry: number,
  fill: string,
  rot = 0,
  stroke: string | null = EDGE,
): void {
  ctx.beginPath();
  ctx.ellipse(cx, cy, rx, ry, rot, 0, Math.PI * 2);
  ctx.fillStyle = fill;
  ctx.fill();
  if (stroke) {
    ctx.strokeStyle = stroke;
    ctx.stroke();
  }
}

/** Ejecuta `fn` con el ctx trasladado/rotado en un pivote (pieza cut-out). */
export function pivoted(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  rot: number,
  fn: () => void,
): void {
  ctx.save();
  ctx.translate(x, y);
  ctx.rotate(rot);
  fn();
  ctx.restore();
}
