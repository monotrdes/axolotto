/**
 * ADN visual del puppet: las 7 dimensiones del backend (axolotito.py) con
 * defaults. `BillboardDNA` vive aquí (AxolotitoBillboard lo re-exporta para
 * compat); todo opcional para que los tenderos del Tianguis sigan
 * funcionando con solo skinColor+seed.
 */

export interface BillboardDNA {
  /** skin_color del backend (pink, gray_light, gray_dark, gold, astral). */
  skinColor?: string;
  /** Variación procedural (branquias, chapas). */
  seed?: number;
  gillType?: string; // short | normal | feathery | crown | phoenix
  eyeType?: string; // derp | dreamer | cute | intellectual | zen
  mouthType?: string; // flat | smile | fang | rockstar | divine
  tailType?: string; // standard | wavy | betta | plasma
  foreheadType?: string; // none | stripes | gem | halo
  limbType?: string; // soft | claws | scales | coral
}

export interface ResolvedDNA {
  gill: string;
  eye: string;
  mouth: string;
  tail: string;
  forehead: string;
  limb: string;
}

const pick = (v: string | undefined, valid: string[], def: string): string =>
  v && valid.includes(v) ? v : def;

export function resolveDNA(dna: BillboardDNA): ResolvedDNA {
  return {
    gill: pick(dna.gillType, ["short", "normal", "feathery", "crown", "phoenix"], "normal"),
    eye: pick(dna.eyeType, ["derp", "dreamer", "cute", "intellectual", "zen"], "cute"),
    mouth: pick(dna.mouthType, ["flat", "smile", "fang", "rockstar", "divine"], "smile"),
    tail: pick(dna.tailType, ["standard", "wavy", "betta", "plasma"], "standard"),
    forehead: pick(dna.foreheadType, ["none", "stripes", "gem", "halo"], "none"),
    limb: pick(dna.limbType, ["soft", "claws", "scales", "coral"], "soft"),
  };
}
