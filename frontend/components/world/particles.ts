import { Container, Graphics, Text } from "pixi.js";

/**
 * Partículas ambientales compartidas por las escenas del mundo papel picado.
 * La escena las posiciona y gestiona vida/movimiento (ver spawnParticle).
 */

/** "z" flotante sobre un axolotito dormido. */
export function zzzParticle(): Container {
  const t = new Text({ text: "z", style: { fontSize: 30, fill: 0x9bd9e4, fontWeight: "900" } });
  t.anchor.set(0.5);
  t.rotation = -0.3 + Math.random() * 0.6;
  return t;
}

/** Burbuja de agua — estela del nado. */
export function bubbleParticle(): Container {
  return new Graphics()
    .circle(0, 0, 4 + Math.random() * 5)
    .stroke({ color: 0x9bd9e4, width: 2 });
}

/** Polvito levantado por los pasos de la caminata bípeda. */
export function dustParticle(): Container {
  return new Graphics()
    .circle(0, 0, 3 + Math.random() * 4)
    .fill({ color: 0xcdb8a0, alpha: 0.5 });
}
