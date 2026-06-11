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
  /**
   * En pantallas anchas, máximo ancho visible para que el encuadre se sienta
   * como "enfoque de sección" (deja recorrido de paneo). Sin este valor la
   * cámara revela todo el overscan disponible.
   */
  focusMaxW?: number;
}

/** Espacio de diseño por macrozona. Base vertical 9:16; la Pirámide es ancha (3 pantallas). */
export const DESIGN_SPACE: Record<MacroZoneId, { w: number; h: number }> = {
  santuario: { w: 1080, h: 1920 },
  tianguis: { w: 1080, h: 1920 },
  // Pirámide: 3 secciones de 1080 separadas por 480 de agua abierta +
  // orillas de 480 para que las subzonas extremas puedan centrarse en web.
  piramide: { w: 5160, h: 1920 },
};

/**
 * Área PINTADA por la escena (incluye overscan lateral decorativo).
 * En móvil 9:16 la cámara encuadra el centro jugable; en desktop 16:9
 * muestra el alto completo y revela los laterales (plan §3.4) en lugar
 * de hacer zoom y recortar el alto.
 */
export const PAINTED_BOUNDS: Record<MacroZoneId, { x0: number; w: number }> = {
  santuario: { x0: -660, w: 2400 },
  tianguis: { x0: -660, w: 2400 },
  piramide: { x0: 0, w: 5160 },
};

/** Encuadre por defecto de cada macrozona (composición 9:16 centrada). */
export const MACRO_FRAMINGS: Record<MacroZoneId, Framing> = {
  santuario: { x: 0, y: 0, w: 1080, h: 1920 },
  tianguis: { x: 0, y: 0, w: 1080, h: 1920 },
  // Llegada a la Pirámide: encuadre central (Explanada al frente).
  piramide: { x: 2040, y: 0, w: 1080, h: 1920, focusMaxW: 1900 },
};

/**
 * Encuadres de subzonas de la Pirámide. Narrativa de cámara (plan §2):
 * rankings = asciende (centro-arriba), salas = se sumerge (derecha-abajo),
 * capsulas = desvío lateral (izquierda).
 */
export const PIRAMIDE_FRAMINGS: Record<PiramideSubZoneId, Framing> = {
  rankings: { x: 2040, y: 0, w: 1080, h: 1920, focusMaxW: 1900 },
  capsulas: { x: 480, y: 200, w: 1080, h: 1920, focusMaxW: 1900 },
  salas: { x: 3600, y: 400, w: 1080, h: 1920, focusMaxW: 1900 },
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
