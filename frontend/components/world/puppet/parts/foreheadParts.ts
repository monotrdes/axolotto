import { Graphics } from "pixi.js";
import { INK } from "../paperParts";
import type { PartBuilder } from "./types";

/**
 * Accesorios de frente por forehead_type (axolotito.py): none, stripes,
 * gem, halo. Anclados al slot foreheadAnchor de la cabeza (0,0 = frente).
 */

const none: PartBuilder = () => null;

const stripes: PartBuilder = ({ accent }) => {
  const g = new Graphics();
  for (const dx of [-9, 0, 9]) {
    g.moveTo(dx, -4).quadraticCurveTo(dx + 2, 2, dx, 7).stroke({ color: accent, width: 3 });
  }
  return g;
};

const gem: PartBuilder = () =>
  new Graphics()
    .poly([0, -6, 5, 0, 0, 6, -5, 0])
    .fill(0x6de0f0)
    .stroke({ color: INK, width: 1.5 });

const halo: PartBuilder = () =>
  // Anillo dorado flotando sobre la cabeza.
  new Graphics()
    .ellipse(0, -16, 14, 4.5)
    .stroke({ color: 0xf5c542, width: 3.5 });

export const FOREHEAD_BUILDERS: Record<string, PartBuilder> = {
  none,
  stripes,
  gem,
  halo,
};
