import { blob } from "../paintUtils";
import type { PartCtx } from "./partCtx";

/**
 * Cola gruesa cut-out: nace en (0,0) y se extiende hacia +x (el orquestador
 * la rota en su base; tailSwing anima la propulsión al nadar).
 * tailType: standard (lisa), wavy (dos lóbulos), betta (velo amplio),
 * plasma (brillante de acento).
 */
export function paintTail(p: PartCtx): void {
  const { ctx, pal } = p;
  switch (p.dna.tail) {
    case "wavy": {
      blob(ctx, 32, -4, 36, 17, pal.skin, -0.12);
      blob(ctx, 64, -16, 22, 12, pal.skin, -0.42);
      blob(ctx, 30, -5, 22, 8, pal.accent, -0.12, null);
      break;
    }
    case "betta": {
      blob(ctx, 42, -8, 48, 30, pal.skin, -0.18);
      // velo interior con rayos de acento
      blob(ctx, 44, -8, 36, 21, pal.accent, -0.18, null);
      ctx.strokeStyle = pal.accentLight;
      ctx.lineWidth = 4;
      for (const a of [-0.45, -0.18, 0.1]) {
        ctx.beginPath();
        ctx.moveTo(8, 0);
        ctx.lineTo(8 + Math.cos(a) * 70, Math.sin(a) * 70 - 8);
        ctx.stroke();
      }
      ctx.lineWidth = 7;
      break;
    }
    case "plasma": {
      blob(ctx, 38, -6, 44, 18, pal.accent, -0.15);
      blob(ctx, 34, -7, 28, 9, pal.accentLight, -0.15, null);
      break;
    }
    default: {
      // standard
      blob(ctx, 38, -6, 44, 18, pal.skin, -0.15);
      blob(ctx, 34, -6, 27, 8, pal.accent, -0.15, null);
    }
  }
}
