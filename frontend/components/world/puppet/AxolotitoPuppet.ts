import { Container } from "pixi.js";
import type { AxolotitoData } from "../entities/AxolotitoSprite";
import { drawBody, drawHead, drawShadow, gillAccent, skinToTint } from "./paperParts";
import { buildPart, type PartCtx } from "./parts";
import { buildBipedRig, type BipedPartSet, type BipedRigRefs } from "./bipedRig";
import { applyBipedPose } from "./bipedAnimator";
import {
  PROFILES,
  TRANSITION_SECS_FOR,
  easeInOutCubic,
  lerpProfile,
  type MotionProfile,
  type PuppetState,
} from "./motionProfiles";

export type { PuppetState } from "./motionProfiles";

/**
 * Títere bípedo de papel recortado: 2 brazos + 2 piernas, erguido.
 * Camina en espacios concurridos (sala, tianguis) y nada (swimming,
 * cuerpo horizontal) solo en la cueva para ir a su camita.
 *
 * Jerarquía en bipedRig.ts; animación procedural en bipedAnimator.ts;
 * partes variantes por rareza (gill/eye/mouth/tail/forehead/limb _type
 * del backend) en ./parts. Sin frames, sin esqueleto externo: el atlas
 * real reemplazará los Graphics sin cambiar el rig.
 */
export class AxolotitoPuppet extends Container {
  readonly axoId: string;
  state: PuppetState = "idle";

  private rig: BipedRigRefs;

  private elapsed = Math.random() * 10; // desfase para que no se sincronicen
  private startProfile: MotionProfile = { ...PROFILES.idle };
  private targetProfile: MotionProfile = PROFILES.idle;
  private profile: MotionProfile = { ...PROFILES.idle };
  private transition = 1; // 0..1
  private transitionSecs = 0.25;
  private blinkTimer = 2 + Math.random() * 4;
  private blinking = 0;

  constructor(data: AxolotitoData) {
    super();
    this.axoId = data.id;
    const tint = skinToTint(data.skinColor);
    const ctx: PartCtx = { tint, accent: gillAccent(tint) };

    const parts: BipedPartSet = {
      body: () => drawBody(tint, data.bodyType),
      head: () => drawHead(tint, data.headType),
      shadow: () => drawShadow(),
      gill: () => buildPart("gill", data.gillType, ctx) ?? new Container(),
      tail: () => buildPart("tail", data.tailType, ctx) ?? new Container(),
      limb: (length) => buildPart("limb", data.limbType, { ...ctx, length }) ?? new Container(),
      eyeOpen: () => buildPart("eye_open", data.eyeType, ctx) ?? new Container(),
      eyeClosed: () => buildPart("eye_closed", data.eyeType, ctx) ?? new Container(),
      mouth: () => buildPart("mouth", data.mouthType, ctx) ?? new Container(),
      forehead: () => buildPart("forehead", data.foreheadType, ctx),
    };
    this.rig = buildBipedRig(this, parts);

    this.setEyesClosed(false);
    this.setState(data.state ?? "idle", true);
  }

  setState(state: PuppetState, immediate = false): void {
    if (state === this.state && !immediate) return;
    const prev = this.state;
    this.state = state;
    this.targetProfile = PROFILES[state];
    if (immediate) {
      this.profile = { ...PROFILES[state] };
      this.startProfile = { ...PROFILES[state] };
      this.transition = 1;
    } else {
      this.startProfile = { ...this.profile };
      this.transition = 0;
      this.transitionSecs = TRANSITION_SECS_FOR(PROFILES[prev], PROFILES[state]);
    }
    this.setEyesClosed(state === "sleeping");
  }

  /** Llamar cada frame con dt en segundos. */
  update(dt: number): void {
    this.elapsed += dt;

    // Cross-fade del perfil (ease cúbico: el tilt de nado es un giro grande).
    if (this.transition < 1) {
      this.transition = Math.min(1, this.transition + dt / this.transitionSecs);
      this.profile = lerpProfile(
        this.startProfile,
        this.targetProfile,
        easeInOutCubic(this.transition),
      );
    }

    applyBipedPose(this.rig, this.profile, this.elapsed);

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
    this.rig.eyeOpenL.visible = !closed;
    this.rig.eyeOpenR.visible = !closed;
    this.rig.eyeClosedL.visible = closed;
    this.rig.eyeClosedR.visible = closed;
  }
}
