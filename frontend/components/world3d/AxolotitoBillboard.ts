import * as THREE from "three";
import { gillAccent, skinToTint } from "./skinColors";

/**
 * Axolotito billboard 2D para el mundo-diorama 3D (P2 del checkpoint
 * world3d): plano siempre orientado a cámara (yaw lo fija el motor vía
 * `World3DScene.billboards`) con el títere de papel pintado en Canvas2D.
 *
 * Tiene vista frontal Y trasera (requisito: deben poder dar la espalda) —
 * `setFacing("back")` cambia la textura cuando camine alejándose de cámara.
 * El idle alterna dos poses de branquias y parpadea. Cuando exista el atlas
 * de arte real, `paintAxolotito` se sustituye sin tocar el resto.
 */

export interface BillboardDNA {
  /** skin_color del backend (pink, gray_light, gray_dark, gold, astral). */
  skinColor?: string;
  /** Variación procedural (branquias, chapas). */
  seed?: number;
}

const W = 220;
const H = 280;

function css(c: number): string {
  return `#${c.toString(16).padStart(6, "0")}`;
}

function mix(c: number, to: number, k: number): number {
  const r = ((c >> 16) & 0xff) * (1 - k) + ((to >> 16) & 0xff) * k;
  const g = ((c >> 8) & 0xff) * (1 - k) + ((to >> 8) & 0xff) * k;
  const b = (c & 0xff) * (1 - k) + (to & 0xff) * k;
  return (Math.round(r) << 16) | (Math.round(g) << 8) | Math.round(b);
}

const EDGE = "#fff7ec"; // filo de papel (convención del puppet Pixi)
const INK = "#2b2b3a";

function paintAxolotito(
  view: "front" | "back",
  pose: 0 | 1,
  blink: boolean,
  tint: number,
  seed: number,
): HTMLCanvasElement {
  const c = document.createElement("canvas");
  c.width = W;
  c.height = H;
  const ctx = c.getContext("2d")!;
  const skin = css(tint);
  const belly = css(mix(tint, 0xffffff, 0.3));
  const accent = css(gillAccent(tint));
  const rnd = (n: number) => {
    // pseudo-aleatorio determinista por seed (mismo axolotito = mismas chapas)
    const x = Math.sin(seed * 127.1 + n * 311.7) * 43758.5453;
    return x - Math.floor(x);
  };
  ctx.lineWidth = 7;
  ctx.lineJoin = "round";
  ctx.lineCap = "round";

  const blob = (
    cx: number,
    cy: number,
    rx: number,
    ry: number,
    fill: string,
    rot = 0,
    stroke: string | null = EDGE,
  ) => {
    ctx.beginPath();
    ctx.ellipse(cx, cy, rx, ry, rot, 0, Math.PI * 2);
    ctx.fillStyle = fill;
    ctx.fill();
    if (stroke) {
      ctx.strokeStyle = stroke;
      ctx.stroke();
    }
  };

  // cola (solo se ve de espaldas, curvándose a un lado)
  if (view === "back") {
    ctx.save();
    ctx.translate(110, 215);
    ctx.rotate(0.5 + rnd(9) * 0.25);
    blob(38, -8, 40, 16, skin, -0.35);
    blob(34, -8, 24, 7, accent, -0.35, null);
    ctx.restore();
  }

  // patas
  for (const px of [84, 136]) blob(px, 252, 14, 18, skin);
  // cuerpo + panza (la panza solo de frente)
  blob(110, 198, 48, 58, skin);
  if (view === "front") blob(110, 212, 29, 38, belly, 0, null);
  // bracitos
  const armDrop = pose ? 3 : 0;
  blob(64, 196 + armDrop, 12, 22, skin, 0.25);
  blob(156, 196 + armDrop, 12, 22, skin, -0.25);
  // cabeza
  blob(110, 118, 62, 58, skin);
  if (view === "back") blob(110, 112, 46, 42, css(mix(tint, 0x000000, 0.08)), 0, null);

  // branquias: 3 frondas por lado (el "alma" del axolote), pose las mece
  const sway = pose ? 5 : -3;
  for (const side of [-1, 1]) {
    for (let i = 0; i < 3; i++) {
      const baseA = (-0.55 + i * 0.5) * 0.9;
      ctx.save();
      ctx.translate(110 + side * 52, 100 + i * 22);
      ctx.rotate(side * (baseA * 0.35 + 0.9) + side * sway * 0.02);
      const len = 26 + rnd(i + (side + 1) * 3) * 8;
      blob(len * 0.55, sway * 0.4, len, 9.5, accent);
      blob(len * 0.55, sway * 0.4, len * 0.55, 4.5, css(mix(gillAccent(tint), 0xffffff, 0.35)), 0, null);
      ctx.restore();
    }
  }

  if (view === "front") {
    // ojos
    ctx.strokeStyle = INK;
    ctx.fillStyle = INK;
    if (blink) {
      ctx.lineWidth = 6;
      for (const ex of [84, 136]) {
        ctx.beginPath();
        ctx.arc(ex, 116, 9, 0.15 * Math.PI, 0.85 * Math.PI);
        ctx.stroke();
      }
      ctx.lineWidth = 7;
    } else {
      for (const ex of [84, 136]) {
        ctx.beginPath();
        ctx.arc(ex, 118, 7.5, 0, Math.PI * 2);
        ctx.fill();
      }
    }
    // sonrisa
    ctx.lineWidth = 5.5;
    ctx.strokeStyle = INK;
    ctx.beginPath();
    ctx.arc(110, 128, 16, 0.2 * Math.PI, 0.8 * Math.PI);
    ctx.stroke();
    ctx.lineWidth = 7;
    // chapas
    ctx.globalAlpha = 0.45;
    blob(72, 138, 9 + rnd(1) * 3, 6, accent, 0, null);
    blob(148, 138, 9 + rnd(2) * 3, 6, accent, 0, null);
    ctx.globalAlpha = 1;
  }

  return c;
}

function tex(c: HTMLCanvasElement): THREE.CanvasTexture {
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = 2;
  return t;
}

export class AxolotitoBillboard extends THREE.Group {
  facing: "front" | "back" = "front";

  private mesh: THREE.Mesh;
  private mat: THREE.MeshStandardMaterial;
  private frontA: THREE.CanvasTexture;
  private frontB: THREE.CanvasTexture;
  private frontBlink: THREE.CanvasTexture;
  private back: THREE.CanvasTexture;
  private phase = Math.random() * 10;
  private blinkTimer = 2 + Math.random() * 4;
  private blinking = 0;

  constructor(dna: BillboardDNA = {}, height = 1.35) {
    super();
    const tint = skinToTint(dna.skinColor);
    const seed = dna.seed ?? Math.random() * 100;
    this.frontA = tex(paintAxolotito("front", 0, false, tint, seed));
    this.frontB = tex(paintAxolotito("front", 1, false, tint, seed));
    this.frontBlink = tex(paintAxolotito("front", 0, true, tint, seed));
    this.back = tex(paintAxolotito("back", 0, false, tint, seed));

    this.mat = new THREE.MeshStandardMaterial({
      map: this.frontA,
      roughness: 1,
      alphaTest: 0.5,
    });
    const w = height * (W / H);
    this.mesh = new THREE.Mesh(new THREE.PlaneGeometry(w, height), this.mat);
    this.mesh.position.y = height / 2;
    this.add(this.mesh);

    // sombra de contacto
    const shadow = new THREE.Mesh(
      new THREE.CircleGeometry(w * 0.34, 18),
      new THREE.MeshBasicMaterial({ color: 0x000000, transparent: true, opacity: 0.2 }),
    );
    shadow.rotation.x = -Math.PI / 2;
    shadow.position.y = 0.012;
    shadow.scale.y = 0.6; // elíptica (local Y = profundidad tras rotar)
    this.add(shadow);
  }

  setFacing(facing: "front" | "back"): void {
    this.facing = facing;
    if (facing === "back") this.mat.map = this.back;
  }

  /**
   * Orienta el sprite según el vector de marcha en el plano del suelo:
   * da la espalda al alejarse de cámara (dz < 0) y se espeja según dx.
   */
  setWalk(dx: number, dz: number): void {
    this.setFacing(dz < 0 ? "back" : "front");
    if (Math.abs(dx) > 0.01) this.mesh.scale.x = dx < 0 ? -1 : 1;
  }

  /** Idle: respiración, vaivén de branquias (swap de pose) y parpadeo. */
  update(t: number, dt: number): void {
    const breathe = 1 + Math.sin(t * 1.7 + this.phase) * 0.018;
    this.mesh.scale.y = breathe;
    this.mesh.rotation.z = Math.sin(t * 0.9 + this.phase) * 0.03;

    if (this.facing === "back") {
      if (this.mat.map !== this.back) this.mat.map = this.back;
      return;
    }
    if (this.blinking > 0) {
      this.blinking -= dt;
      this.mat.map = this.frontBlink;
      return;
    }
    this.blinkTimer -= dt;
    if (this.blinkTimer <= 0) {
      this.blinkTimer = 3 + Math.random() * 4;
      this.blinking = 0.13;
      this.mat.map = this.frontBlink;
      return;
    }
    this.mat.map = Math.sin(t * 2.6 + this.phase) > 0 ? this.frontA : this.frontB;
  }
}
