import { Graphics } from "pixi.js";
import { INK } from "../paperParts";
import type { PartBuilder } from "./types";

/**
 * Ojos por eye_type (axolotito.py): cute, derp, dreamer, cool, zen.
 * Cada variante define versión abierta y cerrada; el puppet alterna
 * visibilidad para el parpadeo. Centro del ojo en (0,0).
 */

const cuteOpen: PartBuilder = () =>
  new Graphics()
    .circle(0, 0, 7)
    .fill(0xffffff)
    .circle(1.5, 0.5, 3.5)
    .fill(INK);

const cuteClosed: PartBuilder = () =>
  new Graphics()
    .moveTo(-6, 0)
    .quadraticCurveTo(0, 5, 6, 0)
    .stroke({ color: INK, width: 2.5 });

const derpOpen: PartBuilder = () =>
  // Pupila desalineada y de otro tamaño — mirada boba.
  new Graphics()
    .circle(0, 0, 7)
    .fill(0xffffff)
    .circle(-2.5, -2, 4.5)
    .fill(INK);

const dreamerOpen: PartBuilder = () => {
  const g = new Graphics();
  g.circle(0, 0, 8).fill(0xffffff).circle(0.5, 0.5, 5).fill(INK);
  // Brillo estelar grande — mirada soñadora.
  g.circle(-1.5, -1.5, 1.8).fill(0xffffff);
  g.circle(2.5, 2, 0.9).fill(0xffffff);
  return g;
};

const coolOpen: PartBuilder = () =>
  // Lente oscuro — siempre con gafas, abierto o cerrado.
  new Graphics()
    .roundRect(-8, -5, 16, 10, 4)
    .fill(0x23232e)
    .stroke({ color: 0xf5c542, width: 2 });

const zenOpen: PartBuilder = () =>
  // Párpado a media asta, en paz.
  new Graphics()
    .moveTo(-7, -2)
    .quadraticCurveTo(0, 4, 7, -2)
    .stroke({ color: INK, width: 3 });

export const EYE_OPEN_BUILDERS: Record<string, PartBuilder> = {
  cute: cuteOpen,
  derp: derpOpen,
  dreamer: dreamerOpen,
  cool: coolOpen,
  zen: zenOpen,
};

export const EYE_CLOSED_BUILDERS: Record<string, PartBuilder> = {
  cute: cuteClosed,
  derp: cuteClosed,
  dreamer: cuteClosed,
  cool: coolOpen, // las gafas no parpadean
  zen: zenOpen, // zen ya está casi cerrado
};
