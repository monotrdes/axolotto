import { Container } from "pixi.js";
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
import { buildBipedRig, type BipedRigRefs } from "./bipedRig";
import { applyBipedPose } from "./bipedAnimator";
import {
  PROFILES,
  lerpProfile,
  easeInOutCubic,
  type MotionProfile,
} from "./motionProfiles";

/**
 * Robo-Axolote: títere mecánico bípedo para NPCs/CPUs.
 *
 * Mismo rig que AxolotitoPuppet (bipedRig + bipedAnimator) pero con piezas
 * de latón/remaches y el `elapsed` cuantizado en ticks — el mismo animador
 * produce tic-tac mecánico en vez de oscilación orgánica. La llave de
 * cuerda en la espalda gira constantemente — comunica "soy bot" sin texto.
 */

export type RoboPuppetState = "idle" | "walking" | "playing";

const TICK_HZ = 7; // pasos discretos del tic-tac

// Perfiles del bípedo orgánico con energía contenida (rigidez de hojalata).
const ROBO_PROFILES: Record<RoboPuppetState, MotionProfile> = {
  idle: { ...PROFILES.idle, breathAmp: 0.02, sway: 0.03, tailAmp: 0.08 },
  walking: { ...PROFILES.walking, legSwing: 0.45, armSwing: 0.3, bobAmp: 3 },
  playing: { ...PROFILES.playing, bobAmp: 8, armSwing: 0.6, breathAmp: 0.03 },
};

const TRANSITION_SECS = 0.25;

export class RoboAxolotePuppet extends Container {
  readonly axoId: string;
  state: RoboPuppetState = "idle";

  private rig: BipedRigRefs;
  private windUpKey: Container;
  private chestGear: Container;

  private elapsed = Math.random() * 8;
  private startProfile: MotionProfile = { ...ROBO_PROFILES.idle };
  private targetProfile: MotionProfile = ROBO_PROFILES.idle;
  private profile: MotionProfile = { ...ROBO_PROFILES.idle };
  private transition = 1;

  constructor(data: AxolotitoData) {
    super();
    this.axoId = data.id;

    this.rig = buildBipedRig(this, {
      body: drawRoboBody,
      head: drawRoboHead,
      gill: drawRoboGill,
      tail: drawRoboTail,
      limb: (length) => drawRoboLimb(length),
      eyeOpen: drawRoboEye,
      eyeClosed: drawRoboEyeClosed,
      mouth: drawRoboMouth,
      shadow: drawRoboShadow,
    });

    // Llave de cuerda en la espalda (+x = atrás) — hija del torso para
    // acompañar la respiración.
    this.windUpKey = drawWindUpKey();
    this.windUpKey.position.set(28, -40);
    this.windUpKey.rotation = Math.PI / 2; // asoma hacia atrás
    this.rig.torso.addChildAt(this.windUpKey, 0);

    this.chestGear = createGear(9);
    this.chestGear.position.set(-8, -30);
    this.rig.torso.addChild(this.chestGear);

    this.setEyesClosed(false);
    this.setState(data.state === "playing" ? "playing" : "idle", true);
  }

  setState(state: RoboPuppetState, immediate = false): void {
    if (state === this.state && !immediate) return;
    this.state = state;
    this.targetProfile = ROBO_PROFILES[state];
    if (immediate) {
      this.profile = { ...ROBO_PROFILES[state] };
      this.startProfile = { ...ROBO_PROFILES[state] };
      this.transition = 1;
    } else {
      this.startProfile = { ...this.profile };
      this.transition = 0;
    }
  }

  update(dt: number): void {
    this.elapsed += dt;

    if (this.transition < 1) {
      this.transition = Math.min(1, this.transition + dt / TRANSITION_SECS);
      this.profile = lerpProfile(
        this.startProfile,
        this.targetProfile,
        easeInOutCubic(this.transition),
      );
    }

    // Tic-tac: el animador compartido recibe el tiempo cuantizado en pasos.
    const ticked = Math.floor(this.elapsed * TICK_HZ) / TICK_HZ;
    applyBipedPose(this.rig, this.profile, ticked);

    // Mecanismos continuos (no cuantizados, para que se sientan de cuerda).
    this.windUpKey.rotation += dt * 2.8;
    this.chestGear.rotation += dt * 3.5;
    for (const gill of this.rig.gills) {
      const gear = gill.children.find((c) => c.label === "rotating_gear");
      if (gear) {
        gear.rotation += dt * 4 * (gill.scale.x < 0 ? -1 : 1);
      }
    }

    // Parpadeo mecánico (flash del visor, lento y regular).
    const blinkCycle = this.elapsed % 4;
    this.setEyesClosed(blinkCycle > 3.7);
  }

  private setEyesClosed(closed: boolean): void {
    this.rig.eyeOpenL.visible = !closed;
    this.rig.eyeOpenR.visible = !closed;
    this.rig.eyeClosedL.visible = closed;
    this.rig.eyeClosedR.visible = closed;
  }
}
