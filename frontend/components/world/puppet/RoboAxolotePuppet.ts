import { Container, Graphics } from "pixi.js";
import type { AxolotitoData } from "../entities/AxolotitoSprite";
import {
  drawRoboBody,
  drawRoboHead,
  drawRoboGill,
  drawRoboTail,
  drawRoboLimb,
  drawRoboEye,
  drawRoboEyeClosed,
  drawRoboMouth,
  drawRoboShadow,
  drawWindUpKey,
  createGear,
} from "./roboParts";

/**
 * Robo-Axolote: títere mecánico para NPCs/CPUs en la mesa de competencia.
 * (plan task-84 §6.5)
 *
 * Mismo rig que AxolotitoPuppet pero con texturas de latón/remaches y
 * animación de tic-tac mecánico en vez de oscilación sinusoidal orgánica.
 * La llave de cuerda en la espalda gira constantemente — comunica "soy bot"
 * sin necesidad de texto.
 */

export type RoboPuppetState = "idle" | "playing";

interface MotionProfile {
  bobAmp: number;
  tickSpeed: number; // Hz del tic-tac
  breathAmp: number;
  gillSpeed: number;
  tailAmp: number;
  tilt: number;
}

const PROFILES: Record<RoboPuppetState, MotionProfile> = {
  idle: { bobAmp: 3, tickSpeed: 1.6, breathAmp: 0.02, gillSpeed: 2.8, tailAmp: 0.08, tilt: 0 },
  playing: { bobAmp: 6, tickSpeed: 3.0, breathAmp: 0.03, gillSpeed: 4.5, tailAmp: 0.2, tilt: 0 },
};

const TRANSITION_SECS = 0.25;

export class RoboAxolotePuppet extends Container {
  readonly axoId: string;
  state: RoboPuppetState = "idle";

  private windUpKey: Container;
  private body: Container;
  private tail: Container;
  private gills: Container[] = [];
  private eyeOpenL: Container;
  private eyeOpenR: Container;
  private eyeClosedL: Container;
  private eyeClosedR: Container;
  private shadow: Container;
  private chestGear: Container | null = null;

  private elapsed = Math.random() * 8;
  private tickPhase = 0; // 0..1 fase discreta del tic-tac
  private profile: MotionProfile = { ...PROFILES.idle };
  private targetProfile: MotionProfile = PROFILES.idle;
  private transition = 1;

  constructor(data: AxolotitoData) {
    super();
    this.axoId = data.id;

    this.shadow = drawRoboShadow();
    this.shadow.position.set(0, 52);
    this.addChild(this.shadow);

    // Llave de cuerda (espalda) — gira constantemente.
    this.windUpKey = drawWindUpKey();
    this.windUpKey.position.set(-20, -14);
    this.addChild(this.windUpKey);

    this.tail = drawRoboTail();
    this.tail.position.set(34, 4);
    this.addChild(this.tail);

    this.body = new Container();
    this.body.addChild(drawRoboBody());

    this.chestGear = createGear(10);
    this.chestGear.position.set(0, 2);
    this.body.addChild(this.chestGear);

    for (const [lx, ly] of [[-26, 22], [10, 26]] as const) {
      const limb = drawRoboLimb();
      limb.position.set(lx, ly);
      this.body.addChild(limb);
    }
    this.addChild(this.body);

    const head = new Container();
    head.position.set(-42, -16);
    head.addChild(drawRoboHead());
    for (const side of [-1, 1] as const) {
      for (let i = 0; i < 3; i++) {
        const gill = drawRoboGill();
        gill.position.set(side * 24, -16 + i * 12);
        gill.scale.x = side;
        gill.rotation = side * (-0.5 + i * 0.45);
        this.gills.push(gill);
        head.addChild(gill);
      }
    }
    this.eyeOpenL = drawRoboEye();
    this.eyeOpenL.position.set(-10, -4);
    this.eyeOpenR = drawRoboEye();
    this.eyeOpenR.position.set(10, -4);
    this.eyeClosedL = drawRoboEyeClosed();
    this.eyeClosedL.position.set(-10, -4);
    this.eyeClosedR = drawRoboEyeClosed();
    this.eyeClosedR.position.set(10, -4);
    const mouth = drawRoboMouth();
    mouth.position.set(0, 12);
    head.addChild(this.eyeOpenL, this.eyeOpenR, this.eyeClosedL, this.eyeClosedR, mouth);
    this.body.addChild(head);

    this.setEyesClosed(false);
    this.setState(data.state === "sleeping" ? "idle" : "idle", true);
  }

  setState(state: RoboPuppetState, immediate = false): void {
    if (state === this.state && !immediate) return;
    this.state = state;
    this.targetProfile = PROFILES[state];
    if (immediate) {
      this.profile = { ...PROFILES[state] };
      this.transition = 1;
    } else {
      this.transition = 0;
    }
  }

  update(dt: number): void {
    this.elapsed += dt;

    // Cross-fade del perfil.
    if (this.transition < 1) {
      this.transition = Math.min(1, this.transition + dt / TRANSITION_SECS);
      const t = this.transition;
      const from = this.profile;
      const to = this.targetProfile;
      this.profile = {
        bobAmp: from.bobAmp + (to.bobAmp - from.bobAmp) * t,
        tickSpeed: from.tickSpeed + (to.tickSpeed - from.tickSpeed) * t,
        breathAmp: from.breathAmp + (to.breathAmp - from.breathAmp) * t,
        gillSpeed: from.gillSpeed + (to.gillSpeed - from.gillSpeed) * t,
        tailAmp: from.tailAmp + (to.tailAmp - from.tailAmp) * t,
        tilt: from.tilt + (to.tilt - from.tilt) * t,
      };
    }

    const p = this.profile;

    // ── Tic-tac mecánico (NO sinusoidal — pasos discretos) ────────
    this.tickPhase += dt * p.tickSpeed;
    const tick = this.tickPhase % 1;
    // Dos clicks por ciclo: uno en 0..0.5 y otro en 0.5..1.
    const click = tick < 0.2 ? tick * 5 : tick >= 0.5 && tick < 0.7 ? (tick - 0.5) * 5 : 1;
    const bob = (Math.round(this.tickPhase) % 2 === 0 ? click : -click) * p.bobAmp * 0.7;

    this.body.position.y = bob;
    this.tail.position.y = 4 + bob * 0.5;
    this.body.rotation = p.tilt;

    // Respiración (más rígida que el orgánico).
    const breath = 1 + Math.sin(this.elapsed * p.tickSpeed * 0.5) * p.breathAmp;
    this.body.scale.y = breath;
    this.body.scale.x = 2 - breath;

    // Cola: movimiento mecánico en pasos.
    const tailStep = Math.round(this.elapsed * p.tickSpeed) % 4;
    this.tail.rotation = (tailStep - 1.5) * 0.12 * (p.tailAmp / 0.08);

    // Branquias: tic-tac desfasado.
    this.gills.forEach((gill, i) => {
      const base = gill.scale.x < 0 ? -1 : 1;
      gill.rotation =
        base * (-0.5 + (i % 3) * 0.45) +
        (Math.round(this.elapsed * p.gillSpeed + i * 0.7) % 3 - 1) * 0.1 * base;
    });

    // Llave de cuerda: rotación constante.
    this.windUpKey.rotation += dt * 2.8;

    // Rotate gears
    if (this.chestGear) {
      this.chestGear.rotation += dt * 3.5;
    }
    this.gills.forEach((gill) => {
      const gear = gill.children.find(c => c.label === "rotating_gear");
      if (gear) {
        const direction = gill.scale.x < 0 ? -1 : 1;
        gear.rotation += dt * 4 * direction;
      }
    });

    // Sombra.
    const shadowScale = 1 - (Math.abs(bob) / Math.max(1, p.bobAmp)) * 0.1;
    this.shadow.scale.set(shadowScale, 1);

    // Parpadeo mecánico (flash del visor, más lento y regular que el orgánico).
    const blinkCycle = this.elapsed % 4;
    this.setEyesClosed(blinkCycle > 3.7);
  }

  private setEyesClosed(closed: boolean): void {
    this.eyeOpenL.visible = !closed;
    this.eyeOpenR.visible = !closed;
    this.eyeClosedL.visible = closed;
    this.eyeClosedR.visible = closed;
  }
}
