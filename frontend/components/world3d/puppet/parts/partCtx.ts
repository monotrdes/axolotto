import type { Palette, Rnd } from "../paintUtils";
import type { PoseFrame, View } from "../poses";
import type { ResolvedDNA } from "../dnaDefaults";

/**
 * Contexto que recibe cada painter de parte. Convención cut-out: el ctx ya
 * está trasladado/rotado al pivote de la parte — los painters dibujan
 * relativo a (0,0). Cuando lleguen los sprites, cada painter se sustituye
 * por un drawImage anclado en ese mismo pivote (ver spriteContract.ts).
 */
export interface PartCtx {
  ctx: CanvasRenderingContext2D;
  pal: Palette;
  rnd: Rnd;
  view: View;
  dna: ResolvedDNA;
  pose: PoseFrame;
}
