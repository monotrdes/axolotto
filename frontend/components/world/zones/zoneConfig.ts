import type { TabId } from "@/types/play";

/** Macrozonas del mundo papel picado (plan task-84 §2). */
export type MacroZoneId = "santuario" | "tianguis" | "piramide";

/** Subzonas de la Pirámide — misma escena, paneo de cámara sin cortina. */
export type PiramideSubZoneId = "rankings" | "salas" | "capsulas";

export interface ZoneTarget {
  macro: MacroZoneId;
  sub?: PiramideSubZoneId;
}

/** Encuadre: región del espacio de diseño que la cámara cubre (cover-fit). */
export interface Framing {
  x: number;
  y: number;
  w: number;
  h: number;
}

/** Espacio de diseño por macrozona. Base vertical 9:16; la Pirámide es ancha (3 pantallas). */
export const DESIGN_SPACE: Record<MacroZoneId, { w: number; h: number }> = {
  santuario: { w: 1080, h: 1920 },
  tianguis: { w: 1080, h: 1920 },
  piramide: { w: 3240, h: 1920 },
};

/** Encuadre por defecto de cada macrozona (composición 9:16 centrada). */
export const MACRO_FRAMINGS: Record<MacroZoneId, Framing> = {
  santuario: { x: 0, y: 0, w: 1080, h: 1920 },
  tianguis: { x: 0, y: 0, w: 1080, h: 1920 },
  // Llegada a la Pirámide: encuadre central (Explanada al frente).
  piramide: { x: 1080, y: 0, w: 1080, h: 1920 },
};

/**
 * Encuadres de subzonas de la Pirámide. Narrativa de cámara (plan §2):
 * rankings = asciende (centro-arriba), salas = se sumerge (derecha-abajo),
 * capsulas = desvío lateral (izquierda).
 */
export const PIRAMIDE_FRAMINGS: Record<PiramideSubZoneId, Framing> = {
  rankings: { x: 1080, y: 0, w: 1080, h: 1920 },
  capsulas: { x: 0, y: 200, w: 1080, h: 1920 },
  salas: { x: 2160, y: 400, w: 1080, h: 1920 },
};

/** Tab HTML que corresponde a cada destino del mundo. */
export function targetToTab(target: ZoneTarget): TabId {
  if (target.macro === "santuario") return "santuario";
  if (target.macro === "tianguis") return "tienda";
  switch (target.sub) {
    case "rankings":
      return "rankings";
    case "capsulas":
      return "gashapon";
    default:
      return "jugar";
  }
}

/**
 * Resuelve cualquier id de zona/tab (incluye los legacy de ZONE_TABS:
 * 'nido', 'sala', 'capsulas'...) a un destino del mundo nuevo.
 */
export function resolveZoneTarget(zoneId: string): ZoneTarget {
  switch (zoneId) {
    case "nido":
    case "santuario":
    case "criadero":
    case "axolotitos":
      return { macro: "santuario" };
    case "tianguis":
    case "tienda":
      return { macro: "tianguis" };
    case "piramide":
    case "rankings":
      return { macro: "piramide", sub: "rankings" };
    case "capsulas":
    case "gashapon":
      return { macro: "piramide", sub: "capsulas" };
    case "sala":
    case "salas":
    case "jugar":
    default:
      return { macro: "piramide", sub: "salas" };
  }
}

/** Encuadre final para un destino. */
export function framingFor(target: ZoneTarget): Framing {
  if (target.macro === "piramide" && target.sub) {
    return PIRAMIDE_FRAMINGS[target.sub];
  }
  return MACRO_FRAMINGS[target.macro];
}
