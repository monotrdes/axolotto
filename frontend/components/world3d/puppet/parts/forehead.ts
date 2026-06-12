import { blob } from "../paintUtils";
import type { PartCtx } from "./partCtx";

const GOLD = "#f5c542";

/**
 * Adorno de frente en coords locales (origen = parte alta de la cabeza).
 * foreheadType: none | stripes | gem | halo.
 */
export function paintForehead(p: PartCtx): void {
  const { ctx, pal } = p;
  switch (p.dna.forehead) {
    case "stripes": {
      ctx.strokeStyle = pal.accent;
      ctx.lineWidth = 4.5;
      for (const dx of [-16, 0, 16]) {
        ctx.beginPath();
        ctx.moveTo(dx, 2);
        ctx.quadraticCurveTo(dx * 1.15, 12, dx * 1.25, 22);
        ctx.stroke();
      }
      ctx.lineWidth = 7;
      break;
    }
    case "gem": {
      ctx.beginPath();
      ctx.moveTo(0, 0);
      ctx.lineTo(9, 11);
      ctx.lineTo(0, 22);
      ctx.lineTo(-9, 11);
      ctx.closePath();
      ctx.fillStyle = pal.accent;
      ctx.fill();
      ctx.strokeStyle = pal.edge;
      ctx.stroke();
      break;
    }
    case "halo": {
      ctx.save();
      ctx.lineWidth = 6;
      ctx.strokeStyle = GOLD;
      ctx.beginPath();
      ctx.ellipse(0, -16, 30, 9, 0, 0, Math.PI * 2);
      ctx.stroke();
      ctx.restore();
      // brillito
      blob(ctx, 24, -20, 3.5, 3.5, "#fff7ec", 0, null);
      break;
    }
    default:
      break; // none
  }
}
