/**
 * Tipos de pose y constantes del rig del Axolotito (rediseño puppet 3D).
 *
 * Espacio de rig: origen (0,0) = punto de contacto de los pies con el piso,
 * +x derecha, -y arriba (convención canvas). El perfil ("side") mira a la
 * IZQUIERDA por defecto (cara en -x, cola en +x), igual que el rig Pixi
 * legacy; la escena lo espeja con scale.x del mesh.
 *
 * La animación vive en los transforms (cut-out de papel): los painters de
 * parte dibujan estáticos y el orquestador rota cada pieza en su pivote.
 */

export type View = "front" | "back" | "side";

/** Pose de un frame: rotaciones por parte + transform global. */
export interface PoseFrame {
  /** Rotación de piernas en la cadera (rad, + = hacia atrás en side). */
  legFront: number;
  legBack: number;
  /** Rotación de brazos en el hombro (rad). */
  armFront: number;
  armBack: number;
  /** Inclinación del torso con pivote en caderas (rad). */
  lean: number;
  /** Elevación del cuerpo en px (+ = arriba; bob de pasos). */
  bob: number;
  /** Rotación global de la figura (rad; -π/2 ≈ horizontal, nado/sueño). */
  tilt: number;
  /** Y del ancla de la figura dentro de la celda del atlas. */
  anchorY: number;
  /** Swing de la cola sumado a su rotación base (rad). */
  tailSwing: number;
  /** Vaivén de branquias, -1..1. */
  gillSway: number;
  eyes: "open" | "closed";
}

/** Celda del atlas (antes 220×280; +ancho para cola y zancada de perfil). */
export const CELL_W = 256;
export const CELL_H = 280;
/** X del ancla de la figura (centro de celda). */
export const CELL_CX = 128;
/** Y del piso para poses de pie. */
export const FOOT_Y = 270;

/** Pivote de la rotación global tilt (centro de masa, en coords de rig). */
export const TILT_PIVOT_Y = -110;

export function basePose(): PoseFrame {
  return {
    legFront: 0,
    legBack: 0,
    armFront: 0,
    armBack: 0,
    lean: 0,
    bob: 0,
    tilt: 0,
    anchorY: FOOT_Y,
    tailSwing: 0,
    gillSway: 0,
    eyes: "open",
  };
}
