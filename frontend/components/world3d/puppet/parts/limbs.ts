import { blob } from "../paintUtils";
import type { PartCtx } from "./partCtx";

/**
 * Extremidades cut-out: cuelgan de (0,0) (hombro o cadera) hacia +y.
 * El limbType del ADN decora la punta: soft (lisa), claws (deditos de
 * tinta), scales (arquitos), coral (bultitos de acento).
 */

function decorate(p: PartCtx, w: number, len: number): void {
  const { ctx, pal } = p;
  switch (p.dna.limb) {
    case "claws": {
      ctx.strokeStyle = pal.ink;
      ctx.lineWidth = 3.5;
      for (const dx of [-w * 0.45, 0, w * 0.45]) {
        ctx.beginPath();
        ctx.moveTo(dx, len + 2);
        ctx.lineTo(dx * 1.3, len + 9);
        ctx.stroke();
      }
      ctx.lineWidth = 7;
      break;
    }
    case "scales": {
      ctx.strokeStyle = pal.accent;
      ctx.lineWidth = 3;
      for (const dy of [len * 0.4, len * 0.65]) {
        ctx.beginPath();
        ctx.arc(0, dy, w * 0.55, 0.2 * Math.PI, 0.8 * Math.PI);
        ctx.stroke();
      }
      ctx.lineWidth = 7;
      break;
    }
    case "coral": {
      for (const [dx, dy, r] of [
        [-w * 0.4, len - 2, 4.5],
        [w * 0.35, len + 1, 4],
        [0, len + 4, 5],
      ]) {
        blob(ctx, dx, dy, r, r, p.pal.accent, 0, null);
      }
      break;
    }
  }
}

/** Bracito. */
export function paintArm(p: PartCtx): void {
  const len = 36;
  blob(p.ctx, 0, len * 0.55, 11, len * 0.6, p.pal.skin);
  // manita
  blob(p.ctx, 0, len + 1, 9.5, 7, p.pal.skin);
  decorate(p, 11, len);
}

/** Pierna corta con pie visible. */
export function paintLeg(p: PartCtx): void {
  const len = 40;
  blob(p.ctx, 0, len * 0.5, 15, len * 0.58, p.pal.skin);
  // pie: de perfil apunta al frente (-x), de frente mira a cámara
  if (p.view === "side") {
    blob(p.ctx, -7, len + 1, 14, 8, p.pal.skin);
  } else {
    blob(p.ctx, 0, len + 1, 15, 8.5, p.pal.skin);
  }
  decorate(p, 13, len);
}
