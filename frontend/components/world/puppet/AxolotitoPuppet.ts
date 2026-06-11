import { Container, Graphics } from "pixi.js";
import type { AxolotitoData } from "../entities/AxolotitoSprite";
import {
  drawBody,
  drawEyeClosed,
  drawEyeOpen,
  drawGill,
  drawHead,
  drawLimb,
  drawMouthSmile,
  drawShadow,
  drawTail,
  gillAccent,
  skinToTint,
} from "./paperParts";

/**
 * Títere cut-out de papel (plan task-84 §6): jerarquía rígida de piezas
 * animada proceduralmente con osciladores sobre los pivotes. Sin frames,
 * sin esqueleto externo. Las texturas placeholder vienen de paperParts;
 * el atlas real las reemplazará sin cambiar este rig.
 */

export type PuppetState = "idle" | "walking" | "sleeping" | "playing";

/** Parámetros de oscilación por estado (se interpolan en transiciones). */
interface MotionProfile {
  bobAmp: number; // px de bobbing vertical
  bobSpeed: number; // rad/s
  breathAmp: number; // delta de scaleY
  gillSpeed: number; // rad/s
  tailAmp: number; // rad
  tilt: number; // rotación base del cuerpo (rad)
}

const PROFILES: Record<PuppetState, MotionProfile> = {
  idle: { bobAmp: 6, bobSpeed: 2.4, breathAmp: 0.045, gillSpeed: 3.4, tailAmp: 0.12, tilt: 0 },
  walking: { bobAmp: 10, bobSpeed: 5.0, breathAmp: 0.05, gillSpeed: 5.5, tailAmp: 0.3, tilt: 0.06 },
  playing: { bobAmp: 12, bobSpeed: 6.0, breathAmp: 0.06, gillSpeed: 6.5, tailAmp: 0.35, tilt: 0 },
  sleeping: { bobAmp: 2, bobSpeed: 1.1, breathAmp: 0.07, gillSpeed: 1.2, tailAmp: 0.04, tilt: 0.5 },
};

const TRANSITION_SECS = 0.2; // cross-fade entre estados (plan §6.3)

export class AxolotitoPuppet extends Container {
  readonly axoId: string;
  state: PuppetState = "idle";

  private body: Container;
  private head: Container;
  private tail: Graphics;
  private gills: Graphics[] = [];
  private eyeOpenL: Graphics;
  private eyeOpenR: Graphics;
  private eyeClosedL: Graphics;
  private eyeClosedR: Graphics;
  private shadow: Graphics;

  private elapsed = Math.random() * 10; // desfase para que no se sincronicen
  private profile: MotionProfile = { ...PROFILES.idle };
  private targetProfile: MotionProfile = PROFILES.idle;
  private transition = 1; // 0..1
  private blinkTimer = 2 + Math.random() * 4;
  private blinking = 0;

  constructor(data: AxolotitoData) {
    super();
    this.axoId = data.id;
    const tint = skinToTint(data.skinColor);
    const accent = gillAccent(tint);

    this.shadow = drawShadow();
    this.shadow.position.set(0, 52);
    this.addChild(this.shadow);

    this.tail = drawTail(tint);
    this.tail.position.set(34, 4);
    this.addChild(this.tail);

    this.body = new Container();
    this.body.addChild(drawBody(tint));
    for (const [lx, ly] of [
      [-26, 22],
      [10, 26],
    ] as const) {
      const limb = drawLimb(tint);
      limb.position.set(lx, ly);
      this.body.addChild(limb);
    }
    this.addChild(this.body);

    this.head = new Container();
    this.head.position.set(-42, -16);
    this.head.addChild(drawHead(tint));
    // 3 branquias por lado, pivote en la base para ondular.
    for (const side of [-1, 1] as const) {
      for (let i = 0; i < 3; i++) {
        const gill = drawGill(accent);
        gill.position.set(side * 24, -16 + i * 12);
        gill.scale.x = side;
        gill.rotation = side * (-0.5 + i * 0.45);
        this.gills.push(gill);
        this.head.addChild(gill);
      }
    }
    this.eyeOpenL = drawEyeOpen();
    this.eyeOpenL.position.set(-13, -6);
    this.eyeOpenR = drawEyeOpen();
    this.eyeOpenR.position.set(13, -6);
    this.eyeClosedL = drawEyeClosed();
    this.eyeClosedL.position.set(-13, -6);
    this.eyeClosedR = drawEyeClosed();
    this.eyeClosedR.position.set(13, -6);
    const mouth = drawMouthSmile();
    mouth.position.set(0, 12);
    this.head.addChild(this.eyeOpenL, this.eyeOpenR, this.eyeClosedL, this.eyeClosedR, mouth);
    this.body.addChild(this.head);

    this.setEyesClosed(false);
    this.setState(data.state ?? "idle", true);
  }

  setState(state: PuppetState, immediate = false): void {
    if (state === this.state && !immediate) return;
    this.state = state;
    this.targetProfile = PROFILES[state];
    if (immediate) {
      this.profile = { ...PROFILES[state] };
      this.transition = 1;
    } else {
      this.transition = 0;
    }
    this.setEyesClosed(state === "sleeping");
  }

  /** Llamar cada frame con dt en segundos. */
  update(dt: number): void {
    this.elapsed += dt;

    // Cross-fade del perfil de movimiento.
    if (this.transition < 1) {
      this.transition = Math.min(1, this.transition + dt / TRANSITION_SECS);
      const t = this.transition;
      const from = this.profile;
      const to = this.targetProfile;
      this.profile = {
        bobAmp: from.bobAmp + (to.bobAmp - from.bobAmp) * t,
        bobSpeed: from.bobSpeed + (to.bobSpeed - from.bobSpeed) * t,
        breathAmp: from.breathAmp + (to.breathAmp - from.breathAmp) * t,
        gillSpeed: from.gillSpeed + (to.gillSpeed - from.gillSpeed) * t,
        tailAmp: from.tailAmp + (to.tailAmp - from.tailAmp) * t,
        tilt: from.tilt + (to.tilt - from.tilt) * t,
      };
    }

    const p = this.profile;
    const bob = Math.sin(this.elapsed * p.bobSpeed) * p.bobAmp;
    this.body.position.y = bob;
    this.tail.position.y = 4 + bob * 0.7;
    this.body.rotation = p.tilt + Math.sin(this.elapsed * p.bobSpeed * 0.5) * 0.03;

    // Respiración (squash & stretch de papel).
    const breath = 1 + Math.sin(this.elapsed * p.bobSpeed * 0.8) * p.breathAmp;
    this.body.scale.y = breath;
    this.body.scale.x = 2 - breath; // conservación de volumen estilo cartoon

    // Cola: vaivén con pivote en la base.
    this.tail.rotation = Math.sin(this.elapsed * p.bobSpeed * 1.2) * p.tailAmp;

    // Branquias: ondulación desfasada por pieza (el alma del axolote).
    this.gills.forEach((gill, i) => {
      const base = gill.scale.x < 0 ? -1 : 1;
      gill.rotation =
        base * (-0.5 + (i % 3) * 0.45) +
        Math.sin(this.elapsed * p.gillSpeed + i * 0.9) * 0.16 * base;
    });

    // Sombra reacciona a la altura del bob.
    const shadowScale = 1 - (bob / Math.max(1, p.bobAmp)) * 0.12;
    this.shadow.scale.set(shadowScale, 1);

    // Parpadeo (solo despierto).
    if (this.state !== "sleeping") {
      if (this.blinking > 0) {
        this.blinking -= dt;
        if (this.blinking <= 0) this.setEyesClosed(false);
      } else {
        this.blinkTimer -= dt;
        if (this.blinkTimer <= 0) {
          this.blinkTimer = 3 + Math.random() * 4;
          this.blinking = 0.12;
          this.setEyesClosed(true);
        }
      }
    }
  }

  private setEyesClosed(closed: boolean): void {
    this.eyeOpenL.visible = !closed;
    this.eyeOpenR.visible = !closed;
    this.eyeClosedL.visible = closed;
    this.eyeClosedR.visible = closed;
  }
}
