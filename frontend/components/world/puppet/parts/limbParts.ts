import { Graphics } from "pixi.js";
import { PAPER_EDGE } from "../paperParts";
import type { PartBuilder } from "./types";

/**
 * Extremidades por limb_type (axolotito.py): soft, claws, scales, coral.
 * Pivote arriba (hombro/cadera) en (0,0); la pieza cuelga hacia +y.
 * ctx.length distingue brazo (corto) de pierna (largo).
 */

const DEFAULT_LENGTH = 34;

const soft: PartBuilder = ({ tint, length = DEFAULT_LENGTH }) =>
  new Graphics()
    .roundRect(-6, 0, 12, length, 6)
    .fill(tint)
    .stroke({ color: PAPER_EDGE, width: 3 });

const claws: PartBuilder = ({ tint, length = DEFAULT_LENGTH }) => {
  const g = new Graphics();
  g.roundRect(-6, 0, 12, length - 4, 6).fill(tint).stroke({ color: PAPER_EDGE, width: 3 });
  // 3 garritas en la punta.
  for (const cx of [-4, 0, 4]) {
    g.poly([cx - 2, length - 5, cx + 2, length - 5, cx, length + 3]).fill(0xfff7ec);
  }
  return g;
};

const scales: PartBuilder = ({ tint, length = DEFAULT_LENGTH }) => {
  const g = new Graphics();
  g.roundRect(-6, 0, 12, length, 6).fill(tint).stroke({ color: PAPER_EDGE, width: 3 });
  // Chevrones de escamas.
  for (let y = 8; y < length - 4; y += 9) {
    g.moveTo(-4, y).quadraticCurveTo(0, y + 4, 4, y).stroke({ color: PAPER_EDGE, width: 2 });
  }
  return g;
};

const coral: PartBuilder = ({ tint, accent, length = DEFAULT_LENGTH }) => {
  const g = new Graphics();
  g.roundRect(-6, 0, 12, length, 6).fill(tint).stroke({ color: PAPER_EDGE, width: 3 });
  // Brotes de coral a los lados.
  g.circle(-7, length * 0.4, 3.5).fill(accent).stroke({ color: PAPER_EDGE, width: 1.5 });
  g.circle(7, length * 0.65, 3).fill(accent).stroke({ color: PAPER_EDGE, width: 1.5 });
  return g;
};

export const LIMB_BUILDERS: Record<string, PartBuilder> = {
  soft,
  claws,
  scales,
  coral,
};
