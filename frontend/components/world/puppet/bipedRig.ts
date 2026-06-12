import { Container } from "pixi.js";

/**
 * Esqueleto bípedo compartido (plan puppet bípedo §A/§E): lo construyen
 * AxolotitoPuppet (piezas de papel) y RoboAxolotePuppet (piezas de latón)
 * inyectando su BipedPartSet. Tres responsabilidades en tres nodos:
 *  - flip horizontal → scale.x del Container raíz (lo hace la escena)
 *  - inclinación nado/sueño → rotation de rigRoot
 *  - sombra → hermana de rigRoot, nunca rota ni se inclina
 * Origen (0,0) del puppet = punto de contacto de los pies con el piso.
 * El rig mira a la izquierda por defecto (cara en -x, cola en +x).
 */

export interface RigConfig {
  legLength: number;
  armLength: number;
  rigCenterY: number;
  hipY: number;
  shoulderY: number;
  tailY: number;
}

export const CLASSIC_CONFIG: RigConfig = {
  legLength: 36,
  armLength: 26,
  rigCenterY: -72,
  hipY: -36,
  shoulderY: -94,
  tailY: -48,
};

export const TIANGUIS_CONFIG: RigConfig = {
  legLength: 48,
  armLength: 36,
  rigCenterY: -84,
  hipY: -48,
  shoulderY: -106,
  tailY: -60,
};

// Compatibilidad hacia atrás (otros scripts o clases mecánicas)
export const LEG_LENGTH = CLASSIC_CONFIG.legLength;
export const ARM_LENGTH = CLASSIC_CONFIG.armLength;
export const RIG_CENTER_Y = CLASSIC_CONFIG.rigCenterY;

/** Fábrica de piezas que cada puppet inyecta (papel u hojalata). */
export interface BipedPartSet {
  body(): Container;
  head(): Container;
  gill(): Container;
  tail(): Container;
  limb(length: number): Container;
  eyeOpen(): Container;
  eyeClosed(): Container;
  mouth(): Container;
  shadow(): Container;
  forehead?(): Container | null;
}

/** Referencias a los nodos animables que devuelve buildBipedRig. */
export interface BipedRigRefs {
  shadow: Container;
  rigRoot: Container;
  torso: Container;
  head: Container;
  tail: Container;
  legFront: Container;
  legBack: Container;
  armFront: Container;
  armBack: Container;
  gills: Container[];
  eyeOpenL: Container;
  eyeOpenR: Container;
  eyeClosedL: Container;
  eyeClosedR: Container;
}

/**
 * Construye la jerarquía y la cuelga de `root`. Orden atrás→adelante:
 * armBack, legBack, tail, torso(+head), legFront, armFront.
 */
export function buildBipedRig(
  root: Container,
  parts: BipedPartSet,
  config: RigConfig = CLASSIC_CONFIG,
): BipedRigRefs {
  const shadow = parts.shadow();
  shadow.position.set(0, 2);
  root.addChild(shadow);

  const rigRoot = new Container();
  rigRoot.pivot.set(0, config.rigCenterY);
  rigRoot.position.set(0, config.rigCenterY);
  root.addChild(rigRoot);

  const armBack = parts.limb(config.armLength);
  armBack.position.set(16, config.shoulderY);
  const legBack = parts.limb(config.legLength);
  legBack.position.set(10, config.hipY);

  const tail = parts.tail();
  tail.position.set(16, config.tailY);

  // El torso pivota en las caderas: la respiración estira hacia arriba
  // y los pies no patinan.
  const torso = new Container();
  torso.position.set(0, config.hipY);
  torso.addChild((() => {
    const body = parts.body();
    body.position.set(0, config.rigCenterY - config.hipY); // centro del torso rel a caderas
    return body;
  })());

  const head = new Container();
  head.position.set(-6, -78); // abs ≈ (-6, -114): sobre el torso
  head.addChild(parts.head());

  const gills: Container[] = [];
  for (const side of [-1, 1] as const) {
    for (let i = 0; i < 3; i++) {
      const gill = parts.gill();
      gill.position.set(side * 20, -14 + i * 10);
      gill.scale.x = side;
      gill.rotation = side * (-0.5 + i * 0.45);
      gills.push(gill);
      head.addChild(gill);
    }
  }

  const eyeOpenL = parts.eyeOpen();
  eyeOpenL.position.set(-12, -4);
  const eyeOpenR = parts.eyeOpen();
  eyeOpenR.position.set(12, -4);
  const eyeClosedL = parts.eyeClosed();
  eyeClosedL.position.set(-12, -4);
  const eyeClosedR = parts.eyeClosed();
  eyeClosedR.position.set(12, -4);
  const mouth = parts.mouth();
  mouth.position.set(-6, 10);
  head.addChild(eyeOpenL, eyeOpenR, eyeClosedL, eyeClosedR, mouth);

  const forehead = parts.forehead?.();
  if (forehead) {
    forehead.position.set(0, -26);
    head.addChild(forehead);
  }
  torso.addChild(head);

  const legFront = parts.limb(config.legLength);
  legFront.position.set(-10, config.hipY);
  const armFront = parts.limb(config.armLength);
  armFront.position.set(-16, config.shoulderY);

  rigRoot.addChild(armBack, legBack, tail, torso, legFront, armFront);

  return {
    shadow, rigRoot, torso, head, tail,
    legFront, legBack, armFront, armBack,
    gills, eyeOpenL, eyeOpenR, eyeClosedL, eyeClosedR,
  };
}
