import type { Container } from "pixi.js";

/** Contexto de dibujo que recibe cada builder de parte. */
export interface PartCtx {
  /** Tinte de piel (skin_color → skinToTint). */
  tint: number;
  /** Color de acento de branquias (gillAccent). */
  accent: number;
  /** Largo en px — solo para extremidades (brazo vs pierna). */
  length?: number;
}

/** Builder de una variante; null = la parte no se dibuja (p.ej. forehead none). */
export type PartBuilder = (ctx: PartCtx) => Container | null;
