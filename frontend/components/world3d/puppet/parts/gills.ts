import { blob } from "../paintUtils";
import type { PartCtx } from "./partCtx";

/**
 * Una fronda de branquia (el "alma" del axolote): nace en (0,0) y se
 * extiende hacia +x; el orquestador instancia 3 por lado y las rota.
 * gillType: short, normal, feathery (con barbas), crown (abanico corto),
 * phoenix (largas hacia arriba).
 */
export function paintGillFrond(p: PartCtx, len: number): void {
  const { ctx, pal } = p;
  switch (p.dna.gill) {
    case "short": {
      const l = len * 0.62;
      blob(ctx, l * 0.55, 0, l, 10, pal.accent);
      blob(ctx, l * 0.55, 0, l * 0.5, 4.5, pal.accentLight, 0, null);
      break;
    }
    case "feathery": {
      blob(ctx, len * 0.55, 0, len, 8.5, pal.accent);
      for (const k of [0.35, 0.6, 0.85]) {
        blob(ctx, len * k + 2, -7, 7, 3.5, pal.accent, -0.7, null);
        blob(ctx, len * k + 2, 7, 7, 3.5, pal.accent, 0.7, null);
      }
      blob(ctx, len * 0.5, 0, len * 0.5, 3.5, pal.accentLight, 0, null);
      break;
    }
    case "crown": {
      const l = len * 0.72;
      blob(ctx, l * 0.55, 0, l, 13, pal.accent);
      blob(ctx, l * 0.6, 0, l * 0.5, 6.5, pal.accentLight, 0, null);
      break;
    }
    case "phoenix": {
      const l = len * 1.35;
      blob(ctx, l * 0.52, -3, l, 7.5, pal.accent, -0.08);
      blob(ctx, l * 0.6, -4, l * 0.55, 3.5, pal.accentLight, -0.08, null);
      break;
    }
    default: {
      // normal (look original)
      blob(ctx, len * 0.55, 0, len, 9.5, pal.accent);
      blob(ctx, len * 0.55, 0, len * 0.55, 4.5, pal.accentLight, 0, null);
    }
  }
}
