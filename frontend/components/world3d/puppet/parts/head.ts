import { blob, css, mix } from "../paintUtils";
import type { PartCtx } from "./partCtx";

/** Cabeza grande (~48% de la altura); origen = centro de la cabeza. */
export function paintHead(p: PartCtx, tint: number): void {
  if (p.view === "side") {
    blob(p.ctx, 0, 0, 58, 54, p.pal.skin);
    // hocico sutil de perfil
    blob(p.ctx, -46, 12, 18, 13, p.pal.skin, 0.15, null);
  } else {
    blob(p.ctx, 0, 0, 64, 58, p.pal.skin);
    if (p.view === "back") {
      // nuca apenas más oscura para leer la espalda
      blob(p.ctx, 0, -6, 46, 42, css(mix(tint, 0x000000, 0.08)), 0, null);
    }
  }
}
