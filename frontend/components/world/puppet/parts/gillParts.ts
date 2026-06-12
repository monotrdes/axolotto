import { Graphics } from "pixi.js";
import { PAPER_EDGE } from "../paperParts";
import type { PartBuilder } from "./types";

/**
 * Branquias por gill_type (axolotito.py): short, normal, feathery, crown,
 * phoenix. Pivote en la base (0,0), la rama crece hacia +x; el rig coloca
 * 3 por lado con scale.x = ±1 y rotaciones distintas.
 */

const normal: PartBuilder = ({ accent }) =>
  new Graphics()
    .ellipse(14, 0, 15, 6)
    .fill(accent)
    .stroke({ color: PAPER_EDGE, width: 3 });

const short: PartBuilder = ({ accent }) =>
  new Graphics()
    .ellipse(8, 0, 9, 5)
    .fill(accent)
    .stroke({ color: PAPER_EDGE, width: 3 });

const feathery: PartBuilder = ({ accent }) => {
  const g = new Graphics();
  // Rama central + 2 plumas desfasadas — silueta tupida.
  g.ellipse(15, 0, 16, 5).fill(accent).stroke({ color: PAPER_EDGE, width: 2.5 });
  g.ellipse(11, -4, 11, 4).fill(accent).stroke({ color: PAPER_EDGE, width: 2 });
  g.ellipse(11, 4, 11, 4).fill(accent).stroke({ color: PAPER_EDGE, width: 2 });
  return g;
};

const crown: PartBuilder = () =>
  // Abanico dorado en punta — porte de realeza.
  new Graphics()
    .poly([0, -3, 22, -8, 28, 0, 22, 8, 0, 3])
    .fill(0xf5c542)
    .stroke({ color: PAPER_EDGE, width: 3 });

const phoenix: PartBuilder = () => {
  const g = new Graphics();
  // Llama naranja con núcleo amarillo y punta afilada.
  g.poly([0, -4, 18, -7, 30, 0, 18, 7, 0, 4]).fill(0xff7a3c).stroke({ color: PAPER_EDGE, width: 3 });
  g.ellipse(12, 0, 8, 3).fill({ color: 0xffd166, alpha: 0.9 });
  return g;
};

export const GILL_BUILDERS: Record<string, PartBuilder> = {
  short,
  normal,
  feathery,
  crown,
  phoenix,
};
