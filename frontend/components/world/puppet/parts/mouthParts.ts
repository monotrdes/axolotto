import { Graphics } from "pixi.js";
import { INK } from "../paperParts";
import type { PartBuilder } from "./types";

/**
 * Bocas por mouth_type (axolotito.py): flat, smile, fang, rockstar, divine.
 * Centro de la boca en (0,0).
 */

const flat: PartBuilder = () =>
  new Graphics().moveTo(-8, 0).lineTo(8, 0).stroke({ color: INK, width: 2.5 });

const smile: PartBuilder = () =>
  new Graphics()
    .moveTo(-9, 0)
    .quadraticCurveTo(0, 8, 9, 0)
    .stroke({ color: INK, width: 2.5 });

const fang: PartBuilder = () => {
  const g = new Graphics();
  g.moveTo(-9, 0).quadraticCurveTo(0, 8, 9, 0).stroke({ color: INK, width: 2.5 });
  // Colmillo asomando del lado izquierdo.
  g.poly([-5, 2, -1, 2, -3, 8]).fill(0xffffff).stroke({ color: INK, width: 1.2 });
  return g;
};

const rockstar: PartBuilder = () => {
  const g = new Graphics();
  // Boca abierta cantando, con lengua.
  g.ellipse(0, 3, 7, 6).fill(INK);
  g.ellipse(0, 6, 4, 2.5).fill(0xe4607c);
  return g;
};

const divine: PartBuilder = () => {
  const g = new Graphics();
  // Sonrisa serena breve + destello dorado.
  g.moveTo(-6, 0).quadraticCurveTo(0, 5, 6, 0).stroke({ color: INK, width: 2.5 });
  g.circle(10, -2, 1.6).fill(0xf5c542);
  return g;
};

export const MOUTH_BUILDERS: Record<string, PartBuilder> = {
  flat,
  smile,
  fang,
  rockstar,
  divine,
};
