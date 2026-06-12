import { Graphics } from "pixi.js";
import { PAPER_EDGE } from "../paperParts";
import type { PartBuilder } from "./types";

/**
 * Colas por tail_type (axolotito.py): standard, wavy, betta, plasma.
 * Pivote en la base (0,0); la cola crece hacia +x (atrás del bípedo,
 * que mira a -x). El animador la rota desde la base.
 */

const standard: PartBuilder = ({ tint }) =>
  new Graphics()
    .poly([0, -12, 44, -4, 44, 4, 0, 12])
    .fill(tint)
    .stroke({ color: PAPER_EDGE, width: 4 });

const wavy: PartBuilder = ({ tint }) =>
  // Silueta serpenteante con curvas suaves.
  new Graphics()
    .moveTo(0, -11)
    .quadraticCurveTo(18, -18, 32, -8)
    .quadraticCurveTo(46, 2, 50, -2)
    .quadraticCurveTo(44, 10, 28, 9)
    .quadraticCurveTo(12, 8, 0, 11)
    .closePath()
    .fill(tint)
    .stroke({ color: PAPER_EDGE, width: 4 });

const betta: PartBuilder = ({ tint, accent }) => {
  const g = new Graphics();
  // Abanico amplio semitranslúcido tipo pez betta.
  g.moveTo(0, -10)
    .quadraticCurveTo(34, -30, 52, -16)
    .quadraticCurveTo(58, 0, 52, 16)
    .quadraticCurveTo(34, 30, 0, 10)
    .closePath()
    .fill({ color: accent, alpha: 0.8 })
    .stroke({ color: PAPER_EDGE, width: 3.5 });
  g.poly([0, -10, 26, -4, 26, 4, 0, 10]).fill(tint);
  return g;
};

const plasma: PartBuilder = ({ tint }) => {
  const g = new Graphics();
  // Aura brillante alrededor del núcleo — cola energética.
  g.ellipse(26, 0, 30, 14).fill({ color: 0x9b6df0, alpha: 0.35 });
  g.poly([0, -10, 40, -3, 48, 0, 40, 3, 0, 10])
    .fill(tint)
    .stroke({ color: 0xc9a6ff, width: 3 });
  g.ellipse(22, 0, 12, 4).fill({ color: 0xffffff, alpha: 0.5 });
  return g;
};

export const TAIL_BUILDERS: Record<string, PartBuilder> = {
  standard,
  wavy,
  betta,
  plasma,
};
