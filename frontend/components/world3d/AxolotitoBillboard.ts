import * as THREE from "three";
import { PuppetAtlas } from "./puppet/frameAtlas";
import { ANIMS, IDLE_BLINK_FRAME, type AnimName } from "./puppet/animations";
import type { BillboardDNA } from "./puppet/dnaDefaults";
import type { View } from "./puppet/poses";

export type { BillboardDNA };

/**
 * Axolotito billboard 2D para el mundo-diorama 3D: plano siempre orientado
 * a cámara (yaw lo fija el motor vía `World3DScene.billboards`) con el
 * títere de papel horneado en un atlas de frames (puppet/frameAtlas.ts).
 *
 * Estados de locomoción: idle (respira, parpadea, mece branquias), walk
 * (ciclo de pasos en 2 patas — perfil con piernas alternando), swim (cuerpo
 * horizontal ondulando) y sleep (acostado, ojos cerrados). El bob de pasos
 * y la ondulación de nado viven AQUÍ (horneados en frames + flotación
 * interna): las escenas solo mueven position.x/z y llaman setWalk/setState.
 *
 * Las 7 dimensiones de ADN (skin/gill/eye/mouth/tail/forehead/limb) se
 * componen por capas en puppet/axolotitoPainter.ts; los painters se
 * sustituyen por sprites PNG por parte sin tocar esta clase (ver
 * puppet/spriteContract.ts).
 */

export type PuppetState = "idle" | "walk" | "swim" | "sleep";

export class AxolotitoBillboard extends THREE.Group {
  facing: "front" | "back" = "front";

  private mesh: THREE.Mesh;
  private mat: THREE.MeshStandardMaterial;
  private atlas: PuppetAtlas;
  private shadow: THREE.Mesh;
  private shadowMat: THREE.MeshBasicMaterial;
  private height: number;

  private state: PuppetState = "idle";
  /** Vista activa con histéresis (evita popping side↔front/back). */
  private view: View = "front";
  private flipX = 1;
  private animTime = 0;
  private phase = Math.random() * 10;
  private blinkTimer = 2 + Math.random() * 4;
  private blinking = 0;

  constructor(dna: BillboardDNA = {}, height = 1.35) {
    super();
    this.height = height;
    this.atlas = new PuppetAtlas(dna);
    this.atlas.setFrame("idleFront", 0);

    this.mat = new THREE.MeshStandardMaterial({
      map: this.atlas.texture,
      roughness: 1,
      alphaTest: 0.5,
    });
    const w = height * this.atlas.aspect;
    this.mesh = new THREE.Mesh(new THREE.PlaneGeometry(w, height), this.mat);
    this.mesh.position.y = height / 2;
    this.add(this.mesh);

    // sombra de contacto
    this.shadowMat = new THREE.MeshBasicMaterial({
      color: 0x000000,
      transparent: true,
      opacity: 0.2,
    });
    this.shadow = new THREE.Mesh(new THREE.CircleGeometry(w * 0.34, 18), this.shadowMat);
    this.shadow.rotation.x = -Math.PI / 2;
    this.shadow.position.y = 0.012;
    this.shadow.scale.y = 0.6; // elíptica (local Y = profundidad tras rotar)
    this.add(this.shadow);
  }

  /** Cambia el estado de locomoción (idempotente). */
  setState(state: PuppetState): void {
    if (state === this.state) return;
    this.state = state;
    this.animTime = 0;
    if (state === "swim" || state === "sleep") this.view = "side";
    else if (this.view === "side" && state === "idle") this.view = "front";
  }

  getState(): PuppetState {
    return this.state;
  }

  /** Compat: fuerza vista frontal o trasera (tenderos estáticos). */
  setFacing(facing: "front" | "back"): void {
    this.facing = facing;
    this.view = facing;
  }

  /**
   * Orienta el sprite según el vector de marcha en el plano del suelo.
   * Perfil cuando domina el desplazamiento lateral; espalda solo casi
   * recto alejándose (dz < 0); frente casi recto acercándose. Histéresis
   * para no parpadear entre vistas en diagonales.
   */
  setWalk(dx: number, dz: number): void {
    const adx = Math.abs(dx);
    const adz = Math.abs(dz);
    if (adx < 1e-6 && adz < 1e-6) return;

    if (this.state === "swim" || this.state === "sleep") {
      this.view = "side";
    } else {
      const enterSide = adx > 0.45 * adz;
      const leaveSide = adx < 0.35 * adz;
      if (this.view === "side") {
        if (leaveSide) this.view = dz < 0 ? "back" : "front";
      } else if (enterSide) {
        this.view = "side";
      } else {
        this.view = dz < 0 ? "back" : "front";
      }
    }
    this.facing = this.view === "back" ? "back" : "front";

    if (adx > 0.01) {
      // el perfil está pintado mirando a -x; frente/espalda son simétricos
      this.flipX = this.view === "side" ? (dx < 0 ? 1 : -1) : dx < 0 ? -1 : 1;
    }
  }

  /** Avanza la animación del estado actual (frames del atlas + flotación). */
  update(t: number, dt: number): void {
    this.animTime += dt;
    this.mesh.scale.x = this.flipX;

    // respiración/vaivén solo de pie (en walk/swim el ciclo ya trae el bob)
    if (this.state === "idle" || this.state === "sleep") {
      const rate = this.state === "sleep" ? 0.9 : 1.7;
      this.mesh.scale.y = 1 + Math.sin(t * rate + this.phase) * 0.018;
      this.mesh.rotation.z = this.state === "idle" ? Math.sin(t * 0.9 + this.phase) * 0.03 : 0;
    } else {
      this.mesh.scale.y = 1;
      this.mesh.rotation.z = 0;
    }

    // flotación y sombra según estado
    let lift = 0;
    let shadowK = 1;
    if (this.state === "swim") {
      lift = Math.sin(t * 1.8 + this.phase) * 0.035;
      shadowK = 0.45;
    }
    this.mesh.position.y = this.height / 2 + lift;
    this.shadowMat.opacity = 0.2 * shadowK;
    this.shadow.scale.x = shadowK === 1 ? 1 : 0.75;

    const [anim, frame] = this.pickFrame(t, dt);
    this.atlas.setFrame(anim, frame);
  }

  private pickFrame(t: number, dt: number): [AnimName, number] {
    switch (this.state) {
      case "walk": {
        const anim: AnimName =
          this.view === "side" ? "walkSide" : this.view === "back" ? "walkBack" : "walkFront";
        const def = ANIMS[anim];
        return [anim, Math.floor(this.animTime * def.fps) % def.frames.length];
      }
      case "swim": {
        const def = ANIMS.swimSide;
        return ["swimSide", Math.floor(this.animTime * def.fps) % def.frames.length];
      }
      case "sleep": {
        const def = ANIMS.sleepSide;
        return ["sleepSide", Math.floor(this.animTime * def.fps) % def.frames.length];
      }
      default: {
        // idle: vaivén de branquias A/B + parpadeo (solo de frente)
        if (this.view === "back") {
          return ["idleBack", Math.sin(t * 2.6 + this.phase) > 0 ? 0 : 1];
        }
        if (this.blinking > 0) {
          this.blinking -= dt;
          return ["idleFront", IDLE_BLINK_FRAME];
        }
        this.blinkTimer -= dt;
        if (this.blinkTimer <= 0) {
          this.blinkTimer = 3 + Math.random() * 4;
          this.blinking = 0.13;
          return ["idleFront", IDLE_BLINK_FRAME];
        }
        return ["idleFront", Math.sin(t * 2.6 + this.phase) > 0 ? 0 : 1];
      }
    }
  }

  dispose(): void {
    this.atlas.dispose();
    this.mat.dispose();
    this.mesh.geometry.dispose();
    this.shadowMat.dispose();
    this.shadow.geometry.dispose();
  }
}
