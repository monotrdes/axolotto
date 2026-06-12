import * as THREE from "three";
import { ANIMS, type AnimName } from "./animations";
import { CELL_H, CELL_W } from "./poses";
import { paintPuppetFrame } from "./axolotitoPainter";
import { resolveDNA, type BillboardDNA } from "./dnaDefaults";
import { skinToTint } from "../skinColors";

/**
 * Hornea TODOS los frames de animación de un puppet en un solo atlas canvas
 * → una sola CanvasTexture por puppet. Cambiar de frame en runtime es solo
 * mover texture.offset (cero re-uploads, cero swaps de material.map).
 *
 * El layout (orden de anims, celdas, gutter) es también el contrato del
 * spritesheet cuando llegue el arte real (docs/sprite_contract_axolotito.md).
 */

const GUTTER = 4;
const COLS = 6;

interface FrameUV {
  ox: number;
  oy: number;
}

export class PuppetAtlas {
  readonly texture: THREE.CanvasTexture;
  /** Aspecto de celda (ancho/alto) para dimensionar el plano. */
  readonly aspect = CELL_W / CELL_H;

  private uvs = new Map<string, FrameUV>();
  private repeatX: number;
  private repeatY: number;

  constructor(dna: BillboardDNA) {
    const resolved = resolveDNA(dna);
    const tint = skinToTint(dna.skinColor);
    const seed = dna.seed ?? Math.random() * 100;

    const names = Object.keys(ANIMS) as AnimName[];
    const total = names.reduce((n, a) => n + ANIMS[a].frames.length, 0);
    const rows = Math.ceil(total / COLS);
    const atlasW = COLS * (CELL_W + GUTTER) + GUTTER;
    const atlasH = rows * (CELL_H + GUTTER) + GUTTER;

    const canvas = document.createElement("canvas");
    canvas.width = atlasW;
    canvas.height = atlasH;
    const ctx = canvas.getContext("2d")!;

    let cell = 0;
    for (const name of names) {
      const anim = ANIMS[name];
      anim.frames.forEach((pose, idx) => {
        const col = cell % COLS;
        const row = Math.floor(cell / COLS);
        const px = GUTTER + col * (CELL_W + GUTTER);
        const py = GUTTER + row * (CELL_H + GUTTER);
        ctx.save();
        ctx.translate(px, py);
        ctx.beginPath();
        ctx.rect(0, 0, CELL_W, CELL_H);
        ctx.clip();
        paintPuppetFrame(ctx, anim.view, pose, resolved, tint, seed);
        ctx.restore();
        // UV: origen abajo-izquierda (three.js), canvas crece hacia abajo
        this.uvs.set(`${name}:${idx}`, {
          ox: px / atlasW,
          oy: 1 - (py + CELL_H) / atlasH,
        });
        cell++;
      });
    }

    this.repeatX = CELL_W / atlasW;
    this.repeatY = CELL_H / atlasH;

    this.texture = new THREE.CanvasTexture(canvas);
    this.texture.colorSpace = THREE.SRGBColorSpace;
    this.texture.anisotropy = 2;
    this.texture.repeat.set(this.repeatX, this.repeatY);
  }

  /** Apunta la textura al frame pedido (solo mueve offset UV). */
  setFrame(anim: AnimName, frame: number): void {
    const uv = this.uvs.get(`${anim}:${frame}`);
    if (!uv) return;
    this.texture.offset.set(uv.ox, uv.oy);
  }

  dispose(): void {
    this.texture.dispose();
  }
}
