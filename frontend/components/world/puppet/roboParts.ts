import { Assets, Container, Sprite, Graphics, Texture } from "pixi.js";

/**
 * Partes del Robo-Axolote (CPU/NPC) en estilo latón y cartón con remaches,
 * llave de cuerda y engranajes visibles. (plan task-84 §6.5)
 *
 * Mismo rig que AxolotitoPuppet — PaperParts para orgánicos,
 * RoboParts para NPCs.
 */

const PAPER_EDGE = 0xfff7ec;
const EDGE_W = 4;

/** Latón base (cuerpo metálico). */
const BRASS = 0xd4a853;
/** Latón oscuro (detalles/remaches). */
const BRASS_DARK = 0xb8943a;
/** Cobre para engranajes. */
const COPPER = 0xc2410c;

// Cache for generated metal textures
let brassTexture: Texture | null = null;
let copperTexture: Texture | null = null;

function getBrassTexture(): Texture {
  if (brassTexture) return brassTexture;
  
  if (typeof document === 'undefined') {
    // SSR safety
    return Texture.WHITE;
  }

  const canvas = document.createElement("canvas");
  canvas.width = 128;
  canvas.height = 128;
  const ctx = canvas.getContext("2d");
  if (ctx) {
    // Brushed brass gradient
    const grad = ctx.createLinearGradient(0, 0, 128, 128);
    grad.addColorStop(0, "#fde047");   // yellow-300
    grad.addColorStop(0.3, "#ca8a04"); // yellow-600
    grad.addColorStop(0.5, "#fef08a"); // yellow-200
    grad.addColorStop(0.8, "#854d0e"); // yellow-800
    grad.addColorStop(1, "#ca8a04");   // yellow-600
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, 128, 128);
    
    // Add brushed metal noise
    ctx.fillStyle = "rgba(255, 255, 255, 0.12)";
    for (let i = 0; i < 300; i++) {
      const w = Math.random() * 40 + 10;
      const h = 1;
      const x = Math.random() * 128;
      const y = Math.random() * 128;
      ctx.fillRect(x, y, w, h);
    }
    ctx.fillStyle = "rgba(0, 0, 0, 0.1)";
    for (let i = 0; i < 300; i++) {
      const w = Math.random() * 30 + 5;
      const h = 1;
      const x = Math.random() * 128;
      const y = Math.random() * 128;
      ctx.fillRect(x, y, w, h);
    }
  }
  brassTexture = Texture.from(canvas);
  return brassTexture;
}

function getCopperTexture(): Texture {
  if (copperTexture) return copperTexture;

  if (typeof document === 'undefined') {
    // SSR safety
    return Texture.WHITE;
  }

  const canvas = document.createElement("canvas");
  canvas.width = 128;
  canvas.height = 128;
  const ctx = canvas.getContext("2d");
  if (ctx) {
    // Copper gradient
    const grad = ctx.createLinearGradient(0, 0, 0, 128);
    grad.addColorStop(0, "#ea580c");   // orange-600
    grad.addColorStop(0.35, "#fdba74"); // orange-300
    grad.addColorStop(0.6, "#9a3412"); // orange-800
    grad.addColorStop(1, "#431407");   // orange-950
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, 128, 128);
    
    // Brushed noise
    ctx.fillStyle = "rgba(255, 255, 255, 0.08)";
    for (let i = 0; i < 200; i++) {
      const w = Math.random() * 35 + 10;
      const h = 1;
      const x = Math.random() * 128;
      const y = Math.random() * 128;
      ctx.fillRect(x, y, w, h);
    }
  }
  copperTexture = Texture.from(canvas);
  return copperTexture;
}

/** Helper para retornar un Sprite de la caché si existe, aplicando ancla. */
function getTextureOrFallback(key: string, anchorX: number, anchorY: number): Container | null {
  if (Assets.cache.has(key)) {
    const sprite = Sprite.from(key);
    sprite.anchor.set(anchorX, anchorY);
    return sprite;
  }
  return null;
}

export function drawRoboBody(): Container {
  const sprite = getTextureOrFallback("robo_body", 0.5, 0.5);
  if (sprite) return sprite;
  const g = new Graphics();
  // Torso bípedo de latón con textura metálica real y remaches.
  g.ellipse(0, 0, 30, 42).fill({ texture: getBrassTexture() }).stroke({ color: PAPER_EDGE, width: EDGE_W });
  // Remaches (2 columnas de 3).
  for (const x of [-14, 14]) {
    for (const y of [-22, 0, 22]) {
      g.circle(x, y, 3.5).fill({ texture: getCopperTexture() }).stroke({ color: PAPER_EDGE, width: 1.5 });
    }
  }
  return g;
}

export function drawRoboHead(): Container {
  const sprite = getTextureOrFallback("robo_head", 0.5, 0.5);
  if (sprite) return sprite;
  const g = new Graphics();
  // Cabeza de latón con textura real.
  g.circle(0, 0, 30).fill({ texture: getBrassTexture() }).stroke({ color: PAPER_EDGE, width: EDGE_W });
  // Visor (banda oscura horizontal).
  g.ellipse(0, -2, 23, 9).fill(0x1e293b).stroke({ color: BRASS_DARK, width: 2.5 });
  // Antena.
  g.moveTo(15, -23).lineTo(19, -38).stroke({ color: BRASS_DARK, width: 3 });
  g.circle(19, -42, 5).fill({ texture: getCopperTexture() }).stroke({ color: PAPER_EDGE, width: 2 });
  return g;
}

export function createGear(r: number): Container {
  const g = new Graphics();
  const teeth = 8;
  const innerR = r * 0.55;
  const toothH = r * 0.35;
  for (let i = 0; i < teeth; i++) {
    const angle = (i / teeth) * Math.PI * 2;
    const x1 = Math.cos(angle) * (r - toothH);
    const y1 = Math.sin(angle) * (r - toothH);
    const x2 = Math.cos(angle) * r;
    const y2 = Math.sin(angle) * r;
    g.moveTo(x1, y1).lineTo(x2, y2).stroke({ color: COPPER, width: 2.5 });
  }
  g.circle(0, 0, innerR).fill({ texture: getCopperTexture() }).stroke({ color: COPPER, width: 2 });
  g.circle(0, 0, 2.5).fill(BRASS_DARK);
  return g;
}

export function drawRoboGill(): Container {
  const sprite = getTextureOrFallback("robo_gill", 0, 0.5);
  if (sprite) return sprite;
  
  const container = new Container();
  // Brazo metálico
  const arm = new Graphics()
    .rect(0, -3, 14, 6)
    .fill({ texture: getCopperTexture() })
    .stroke({ color: PAPER_EDGE, width: 2 });
  container.addChild(arm);
  
  // Engranaje rotativo
  const gear = createGear(12);
  gear.position.set(16, 0);
  gear.label = "rotating_gear";
  container.addChild(gear);
  
  return container;
}

export function drawRoboTail(): Container {
  const sprite = getTextureOrFallback("robo_tail", 0, 0.5);
  if (sprite) return sprite;
  const g = new Graphics();
  g.poly([0, -12, 44, -4, 44, 4, 0, 12])
    .fill({ texture: getBrassTexture() })
    .stroke({ color: PAPER_EDGE, width: 4 });
  // Segmentos de cola (articulaciones).
  g.lineTo(16, -9).lineTo(16, 9).stroke({ color: BRASS_DARK, width: 2 });
  g.lineTo(30, -6).lineTo(30, 6).stroke({ color: BRASS_DARK, width: 2 });
  return g;
}

export function drawRoboLimb(length = 26): Container {
  const sprite = getTextureOrFallback("robo_limb", 0.5, 0);
  if (sprite) return sprite;
  const g = new Graphics();
  g.roundRect(-6, 0, 12, length, 6)
    .fill({ texture: getBrassTexture() })
    .stroke({ color: PAPER_EDGE, width: 3 });
  // Remache en la articulación superior.
  g.circle(0, 6, 3.5).fill({ texture: getCopperTexture() }).stroke({ color: PAPER_EDGE, width: 1.5 });
  // Garra en la punta.
  g.moveTo(-4, length).lineTo(0, length + 6).lineTo(4, length).fill({ texture: getCopperTexture() });
  return g;
}

export function drawRoboEye(): Container {
  const sprite = getTextureOrFallback("robo_eye", 0.5, 0.5);
  if (sprite) return sprite;
  return new Graphics()
    .circle(0, 0, 6)
    .fill(0xf5c542)
    .circle(0, 0, 3)
    .fill(0xffffff)
    .stroke({ color: 0x2b2b3a, width: 1 });
}

export function drawRoboEyeClosed(): Container {
  const sprite = getTextureOrFallback("robo_eye_closed", 0.5, 0.5);
  if (sprite) return sprite;
  return new Graphics()
    .rect(-6, -1, 12, 2)
    .fill(BRASS_DARK)
    .stroke({ color: PAPER_EDGE, width: 1.5 });
}

export function drawRoboMouth(): Container {
  const sprite = getTextureOrFallback("robo_mouth", 0.5, 0.5);
  if (sprite) return sprite;
  const g = new Graphics();
  g.rect(-10, -3, 20, 10).fill(0x1e293b).stroke({ color: BRASS, width: 2 });
  for (let y = -1; y <= 4; y += 4) {
    g.moveTo(-8, y).lineTo(8, y).stroke({ color: BRASS, width: 1.5 });
  }
  return g;
}

export function drawRoboShadow(): Container {
  const sprite = getTextureOrFallback("robo_shadow", 0.5, 0.5);
  if (sprite) return sprite;
  return new Graphics().ellipse(0, 0, 36, 9).fill({ color: 0x000000, alpha: 0.22 });
}

export function drawWindUpKey(): Container {
  const sprite = getTextureOrFallback("robo_key", 0.5, 0.5);
  if (sprite) return sprite;
  const g = new Graphics();
  // Eje.
  g.rect(-3, -10, 6, 12).fill({ texture: getCopperTexture() }).stroke({ color: PAPER_EDGE, width: 2 });
  // Asas de la llave (mariposa).
  g.ellipse(10, -10, 14, 7).fill({ texture: getBrassTexture() }).stroke({ color: PAPER_EDGE, width: 2.5 });
  g.ellipse(-10, -10, 14, 7).fill({ texture: getBrassTexture() }).stroke({ color: PAPER_EDGE, width: 2.5 });
  g.circle(0, -10, 4).fill({ texture: getCopperTexture() });
  return g;
}

