import { Graphics } from "pixi.js";

/**
 * Partes del Robo-Axolote (CPU/NPC) en estilo latón y cartón con remaches,
 * llave de cuerda y engranajes visibles. (plan task-84 §6.5)
 *
 * Mismo rig que AxolotitoPuppet — PaperParts para orgánicos,
 * RoboParts para NPCs. Placeholder Graphics hasta el atlas real.
 */

const PAPER_EDGE = 0xfff7ec;
const EDGE_W = 4;

/** Latón base (cuerpo metálico). */
const BRASS = 0xd4a853;
/** Latón oscuro (detalles/remaches). */
const BRASS_DARK = 0xb8943a;
/** Cobre para engranajes. */
const COPPER = 0xc2410c;

export function drawRoboBody(): Graphics {
  const g = new Graphics();
  // Cuerpo de latón con remaches.
  g.ellipse(0, 0, 52, 38).fill(BRASS).stroke({ color: PAPER_EDGE, width: EDGE_W });
  // Remaches (3 en cada lado).
  for (const x of [-28, 0, 28]) {
    for (const y of [-8, 8]) {
      g.circle(x, y, 3).fill(BRASS_DARK).stroke({ color: PAPER_EDGE, width: 1.5 });
    }
  }
  // Engranaje visible en el pecho.
  drawGearAt(g, 0, 2, 10);
  return g;
}

export function drawRoboHead(): Graphics {
  const g = new Graphics();
  // Cabeza de latón con visor.
  g.circle(0, 0, 36).fill(BRASS).stroke({ color: PAPER_EDGE, width: EDGE_W });
  // Visor (banda oscura horizontal — parecen goggles de soldador).
  g.ellipse(0, -2, 28, 10).fill(0x2b2b3a).stroke({ color: BRASS_DARK, width: 2.5 });
  // Antena.
  g.moveTo(18, -28).lineTo(22, -44).stroke({ color: BRASS_DARK, width: 3 });
  g.circle(22, -48, 5).fill(0xf5c542).stroke({ color: PAPER_EDGE, width: 2 });
  return g;
}

export function drawRoboGill(): Graphics {
  return new Graphics()
    .ellipse(16, 0, 18, 7)
    .fill(COPPER)
    .stroke({ color: PAPER_EDGE, width: 3 });
}

export function drawRoboTail(): Graphics {
  const g = new Graphics();
  g.poly([0, -16, 64, -4, 64, 4, 0, 16])
    .fill(BRASS)
    .stroke({ color: PAPER_EDGE, width: 4 });
  // Segmentos de cola (articulaciones).
  g.lineTo(24, -10).lineTo(24, 10).stroke({ color: BRASS_DARK, width: 2 });
  g.lineTo(44, -5).lineTo(44, 5).stroke({ color: BRASS_DARK, width: 2 });
  return g;
}

export function drawRoboLimb(): Graphics {
  const g = new Graphics();
  // Brazo/pata de latón articulado.
  g.roundRect(-6, 0, 12, 26, 6)
    .fill(BRASS)
    .stroke({ color: PAPER_EDGE, width: 3 });
  // Remache en la articulación superior.
  g.circle(0, 6, 3).fill(BRASS_DARK).stroke({ color: PAPER_EDGE, width: 1.5 });
  // Garra en la punta.
  g.moveTo(-4, 26).lineTo(0, 32).lineTo(4, 26).fill(COPPER);
  return g;
}

export function drawRoboEye(): Graphics {
  return new Graphics()
    .circle(0, 0, 6)
    .fill(0xf5c542)
    .circle(0, 0, 3)
    .fill(0xffffff)
    .stroke({ color: 0x2b2b3a, width: 1 });
}

export function drawRoboEyeClosed(): Graphics {
  return new Graphics()
    .rect(-6, -1, 12, 2)
    .fill(BRASS_DARK)
    .stroke({ color: PAPER_EDGE, width: 1.5 });
}

export function drawRoboMouth(): Graphics {
  // Parrilla de altavoz (no tiene boca, tiene speaker).
  const g = new Graphics();
  g.rect(-10, -3, 20, 10).fill(0x2b2b3a).stroke({ color: BRASS, width: 2 });
  for (let y = -1; y <= 4; y += 4) {
    g.moveTo(-8, y).lineTo(8, y).stroke({ color: BRASS, width: 1.5 });
  }
  return g;
}

export function drawRoboShadow(): Graphics {
  return new Graphics().ellipse(0, 0, 44, 10).fill({ color: 0x000000, alpha: 0.22 });
}

/** Llave de cuerda (espalda) — gira constantemente. */
export function drawWindUpKey(): Graphics {
  const g = new Graphics();
  // Eje.
  g.rect(-3, -10, 6, 12).fill(BRASS_DARK).stroke({ color: PAPER_EDGE, width: 2 });
  // Asas de la llave (mariposa).
  g.ellipse(10, -10, 14, 7).fill(BRASS).stroke({ color: PAPER_EDGE, width: 2.5 });
  g.ellipse(-10, -10, 14, 7).fill(BRASS).stroke({ color: PAPER_EDGE, width: 2.5 });
  g.circle(0, -10, 4).fill(BRASS_DARK);
  return g;
}

/** Engranaje decorativo en posición (px relativas al padre). */
function drawGearAt(g: Graphics, cx: number, cy: number, r: number): void {
  const teeth = 8;
  const innerR = r * 0.55;
  const toothH = r * 0.35;
  for (let i = 0; i < teeth; i++) {
    const angle = (i / teeth) * Math.PI * 2;
    const x1 = cx + Math.cos(angle) * (r - toothH);
    const y1 = cy + Math.sin(angle) * (r - toothH);
    const x2 = cx + Math.cos(angle) * r;
    const y2 = cy + Math.sin(angle) * r;
    g.moveTo(x1, y1).lineTo(x2, y2).stroke({ color: COPPER, width: 2.5 });
  }
  g.circle(cx, cy, innerR).stroke({ color: COPPER, width: 2 });
  g.circle(cx, cy, 2.5).fill(BRASS_DARK);
}
