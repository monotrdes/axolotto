import { blob } from "../paintUtils";
import type { PartCtx } from "./partCtx";

/** Cuerpo regordete; origen = centro del cuerpo. */
export function paintBody(p: PartCtx): void {
  if (p.view === "side") {
    blob(p.ctx, 0, 0, 52, 50, p.pal.skin);
  } else {
    blob(p.ctx, 0, 0, 50, 54, p.pal.skin);
  }
}

/** Panza clara (no se ve de espaldas). */
export function paintBelly(p: PartCtx): void {
  if (p.view === "back") return;
  if (p.view === "side") {
    blob(p.ctx, -14, 10, 26, 32, p.pal.belly, 0.1, null);
  } else {
    blob(p.ctx, 0, 10, 30, 38, p.pal.belly, 0, null);
  }
}
