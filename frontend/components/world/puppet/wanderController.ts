/**
 * Deambular horizontal de un títere bípedo: elegir destino, caminar hacia
 * él, pausar, repetir. Lo reusan SantuarioScene (modo sala) y TianguisScene
 * (NPCs paseando). El rig mira a la izquierda por defecto → flip a +x.
 */

interface WanderPuppet {
  x: number;
  scale: { x: number };
  state: string;
  setState(state: "idle" | "walking"): void;
}

export interface WanderOpts {
  minX: number;
  maxX: number;
  speed: number; // px/s en espacio de diseño
}

export class WanderController {
  private targetX: number;
  private paused: number;

  constructor(
    private puppet: WanderPuppet,
    private opts: WanderOpts,
  ) {
    this.targetX = puppet.x;
    this.paused = 1 + Math.random() * 3;
  }

  update(dt: number): void {
    const { puppet, opts } = this;
    if (this.paused > 0) {
      this.paused -= dt;
      if (this.paused <= 0) {
        this.targetX = opts.minX + Math.random() * (opts.maxX - opts.minX);
      }
      return;
    }
    const dx = this.targetX - puppet.x;
    if (Math.abs(dx) < 8) {
      this.paused = 2 + Math.random() * 4;
      if (puppet.state === "walking") puppet.setState("idle");
      return;
    }
    if (puppet.state === "idle") puppet.setState("walking");
    const dir = Math.sign(dx);
    puppet.x += dir * opts.speed * dt;
    puppet.scale.x = dir > 0 ? -1 : 1;
  }

  /** Quedarse quieto un momento y olvidar el destino (p.ej. al volver a la sala). */
  reset(pause = 0.5): void {
    this.paused = pause;
    this.targetX = this.puppet.x;
  }
}
