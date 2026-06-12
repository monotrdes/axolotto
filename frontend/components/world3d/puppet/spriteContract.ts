/**
 * Contrato de arte para sustituir los painters procedurales por sprites
 * PNG por parte (cut-out). Documento humano: docs/sprite_contract_axolotito.md
 *
 * Modelo: cada parte del puppet es un PNG estático con un pivote declarado;
 * la animación (caminar, nadar, mecer branquias) la sigue haciendo el
 * orquestador rotando piezas — los sprites NO traen frames de cuerpo
 * completo. Una variante de ADN = solo el PNG de esa parte.
 *
 * Integración futura (no implementada aún): axolotitoPainter consulta un
 * `PartArtRegistry`; si la parte tiene sprite cargado hace
 * `ctx.drawImage(img, -pivot.x, -pivot.y, w, h)` dentro del mismo
 * `pivoted(...)` — mismo pivote, mismas rotaciones, cero cambios en
 * locomoción, atlas o escenas.
 */

import type { View } from "./poses";

/** Identificador de parte (coincide con los painters de parts/). */
export type PartId =
  | "body"
  | "belly"
  | "head"
  | "arm"
  | "leg"
  | "tail"
  | "gillFrond"
  | "eyes"
  | "mouth"
  | "forehead";

export interface PartArtSource {
  kind: "procedural" | "sprite";
  /** URL del PNG (transparente, @2x del canvas lógico 256×280). */
  url?: string;
  /** Pivote en px del PNG (punto que cae en el ancla del rig). */
  pivot?: { x: number; y: number };
  /**
   * Opcional: tira horizontal de N frames del mismo tamaño para partes con
   * animación dibujada (p.ej. branquias ondeando). Si falta, la pieza es
   * estática y se anima por transform.
   */
  frames?: number;
}

/** Clave de lookup: parte + vista + tipo de ADN ("soft", "crown", …). */
export type PartArtKey = `${PartId}:${View}:${string}`;

export type PartArtRegistry = Partial<Record<PartArtKey, PartArtSource>>;

/** Registro global (vacío = todo procedural). Se llenará al integrar arte. */
export const partArt: PartArtRegistry = {};
