import { makePalette, makeRnd, pivoted } from "./paintUtils";
import { CELL_CX, TILT_PIVOT_Y, type PoseFrame, type View } from "./poses";
import type { ResolvedDNA } from "./dnaDefaults";
import type { PartCtx } from "./parts/partCtx";
import { paintBody, paintBelly } from "./parts/body";
import { paintHead } from "./parts/head";
import { paintArm, paintLeg } from "./parts/limbs";
import { paintTail } from "./parts/tail";
import { paintGillFrond } from "./parts/gills";
import { paintFace } from "./parts/face";
import { paintForehead } from "./parts/forehead";

/**
 * Orquestador de capas del puppet (cut-out de papel): coloca cada parte en
 * su pivote, aplica las rotaciones del PoseFrame y llama a su painter.
 * Z-order fijo: tail → legBack → armBack → body → belly → legFront →
 * armFront → head → gills → face → forehead.
 *
 * La animación vive en los transforms — los painters de parte son estáticos,
 * por lo que mañana cada uno se sustituye por su sprite PNG sin tocar nada
 * más (ver spriteContract.ts).
 */
export function paintPuppetFrame(
  ctx: CanvasRenderingContext2D,
  view: View,
  pose: PoseFrame,
  dna: ResolvedDNA,
  tint: number,
  seed: number,
): void {
  const p: PartCtx = {
    ctx,
    pal: makePalette(tint),
    rnd: makeRnd(seed),
    view,
    dna,
    pose,
  };
  ctx.save();
  ctx.lineWidth = 7;
  ctx.lineJoin = "round";
  ctx.lineCap = "round";

  // Transform raíz: ancla de la figura dentro de la celda. Para poses
  // inclinadas (nado/sueño) el pivote es el centro de masa del rig.
  ctx.translate(CELL_CX, pose.anchorY - pose.bob);
  if (pose.tilt !== 0) {
    ctx.rotate(pose.tilt);
    ctx.translate(0, -TILT_PIVOT_Y);
  }

  if (view === "side") paintSide(p);
  else paintFacing(p);

  ctx.restore();
}

/** Envuelve fn con la inclinación del torso (pivote en caderas). */
function torso(p: PartCtx, hipX: number, hipY: number, fn: () => void): void {
  pivoted(p.ctx, hipX, hipY, p.pose.lean, () => {
    p.ctx.translate(-hipX, -hipY);
    fn();
  });
}

/** Perfil (mira a la izquierda: cara en -x, cola en +x). */
function paintSide(p: PartCtx): void {
  const { ctx, pose, rnd } = p;
  const HIP_X = 8;
  const HIP_Y = -46;
  const HEAD = { x: -14, y: -178 };

  // cola (fuera del lean — conecta a la cadera), gruesa y curvada hacia arriba
  pivoted(ctx, 36, -92, -0.45 + pose.tailSwing, () => paintTail(p));
  // pierna trasera
  pivoted(ctx, 18, -48, pose.legBack, () => paintLeg(p));

  torso(p, HIP_X, HIP_Y, () => {
    pivoted(ctx, 24, -106, pose.armBack, () => paintArm(p));
    pivoted(ctx, 6, -90, 0, () => {
      paintBody(p);
      paintBelly(p);
    });
  });

  // pierna delantera (sobre el cuerpo, fuera del lean)
  pivoted(ctx, -2, -46, pose.legFront, () => paintLeg(p));

  torso(p, HIP_X, HIP_Y, () => {
    pivoted(ctx, -14, -110, pose.armFront, () => paintArm(p));
    pivoted(ctx, HEAD.x, HEAD.y, 0, () => paintHead(p, tintOf(p)));
    // branquias del lado visible: 3 frondas en la nuca, hacia atrás/arriba
    const frondas: Array<[number, number, number]> = [
      [HEAD.x + 30, HEAD.y - 42, -1.1],
      [HEAD.x + 44, HEAD.y - 20, -0.72],
      [HEAD.x + 50, HEAD.y + 4, -0.35],
    ];
    frondas.forEach(([fx, fy, rot], i) => {
      const len = 26 + rnd(i + 3) * 8;
      pivoted(ctx, fx, fy, rot + pose.gillSway * 0.08, () => paintGillFrond(p, len));
    });
    pivoted(ctx, HEAD.x, HEAD.y, 0, () => paintFace(p));
    pivoted(ctx, HEAD.x + 6, HEAD.y - 50, 0, () => paintForehead(p));
  });
}

/** Frente o espalda (simétrico; la espalda omite cara y muestra cola). */
function paintFacing(p: PartCtx): void {
  const { ctx, pose, rnd, view } = p;
  const HIP_X = 0;
  const HIP_Y = -46;
  const HEAD = { x: 0, y: -176 };

  if (view === "back") {
    // cola asomando, curvándose a un lado (como el billboard original)
    pivoted(ctx, 0, -84, 0.5 + rnd(9) * 0.25, () => paintTail(p));
  }

  pivoted(ctx, 26, -48, pose.legBack, () => paintLeg(p));

  torso(p, HIP_X, HIP_Y, () => {
    pivoted(ctx, 46, -106, pose.armBack + 0.25, () => paintArm(p));
    pivoted(ctx, 0, -88, 0, () => {
      paintBody(p);
      paintBelly(p);
    });
  });

  pivoted(ctx, -26, -48, pose.legFront, () => paintLeg(p));

  torso(p, HIP_X, HIP_Y, () => {
    pivoted(ctx, -46, -106, pose.armFront - 0.25, () => paintArm(p));
    pivoted(ctx, HEAD.x, HEAD.y, 0, () => paintHead(p, tintOf(p)));
    // branquias: 3 frondas por lado en abanico (espejo exacto con scale -1)
    for (const side of [-1, 1]) {
      for (let i = 0; i < 3; i++) {
        const len = 26 + rnd(i + (side + 1) * 3) * 8;
        const rot = -0.35 + i * 0.45 + pose.gillSway * 0.08;
        pivoted(ctx, HEAD.x + side * 48, HEAD.y - 28 + i * 22, side * rot, () => {
          if (side < 0) ctx.scale(-1, 1);
          paintGillFrond(p, len);
        });
      }
    }
    pivoted(ctx, HEAD.x, HEAD.y, 0, () => paintFace(p));
    pivoted(ctx, HEAD.x, HEAD.y - 52, 0, () => paintForehead(p));
  });
}

// El tint ya está aplicado en la paleta; head necesita el número crudo para
// oscurecer la nuca. Lo reconstruimos del CSS para no arrastrarlo por todos
// los painters.
function tintOf(p: PartCtx): number {
  return parseInt(p.pal.skin.slice(1), 16);
}
