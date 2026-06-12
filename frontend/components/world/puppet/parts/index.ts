import type { Container } from "pixi.js";
import { getTextureOrFallback } from "../paperParts";
import type { PartBuilder, PartCtx } from "./types";
import { GILL_BUILDERS } from "./gillParts";
import { EYE_OPEN_BUILDERS, EYE_CLOSED_BUILDERS } from "./eyeParts";
import { MOUTH_BUILDERS } from "./mouthParts";
import { TAIL_BUILDERS } from "./tailParts";
import { LIMB_BUILDERS } from "./limbParts";
import { FOREHEAD_BUILDERS } from "./foreheadParts";

/**
 * Registry de partes variantes por rareza (plan puppet bípedo §D).
 * Cada parte se resuelve atlas-primero (clave `${kind}_${variant}`) y cae
 * al builder Graphics. Variante desconocida → default, así el backend puede
 * agregar tipos nuevos sin romper el frontend.
 */

export type PartKind =
  | "gill"
  | "eye_open"
  | "eye_closed"
  | "mouth"
  | "tail"
  | "limb"
  | "forehead";

export type { PartCtx } from "./types";

const REGISTRY: Record<PartKind, Record<string, PartBuilder>> = {
  gill: GILL_BUILDERS,
  eye_open: EYE_OPEN_BUILDERS,
  eye_closed: EYE_CLOSED_BUILDERS,
  mouth: MOUTH_BUILDERS,
  tail: TAIL_BUILDERS,
  limb: LIMB_BUILDERS,
  forehead: FOREHEAD_BUILDERS,
};

const DEFAULTS: Record<PartKind, string> = {
  gill: "normal",
  eye_open: "cute",
  eye_closed: "cute",
  mouth: "smile",
  tail: "standard",
  limb: "soft",
  forehead: "none",
};

/** Anclas de sprite por parte (coinciden con el pivote del builder Graphics). */
const ANCHORS: Record<PartKind, readonly [number, number]> = {
  gill: [0, 0.5],
  eye_open: [0.5, 0.5],
  eye_closed: [0.5, 0.5],
  mouth: [0.5, 0.5],
  tail: [0, 0.5],
  limb: [0.5, 0],
  forehead: [0.5, 0.5],
};

export function buildPart(
  kind: PartKind,
  variant: string | undefined,
  ctx: PartCtx,
): Container | null {
  const builders = REGISTRY[kind];
  const v = variant && builders[variant] ? variant : DEFAULTS[kind];
  const [ax, ay] = ANCHORS[kind];
  const fromAtlas = getTextureOrFallback(`${kind}_${v}`, ax, ay, ctx.tint);
  return fromAtlas ?? builders[v](ctx);
}

/** Variantes disponibles de una parte (para previews / NPCs aleatorios). */
export function partVariants(kind: PartKind): string[] {
  return Object.keys(REGISTRY[kind]);
}
