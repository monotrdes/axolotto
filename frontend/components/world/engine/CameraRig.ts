import type { Container } from "pixi.js";
import gsap from "gsap";
import type { Framing } from "../zones/zoneConfig";

/**
 * Cámara 2.5D: posiciona/escala el contenedor de escena para que un encuadre
 * (región del espacio de diseño) cubra el viewport (cover-fit). Paneos con GSAP
 * para las subzonas de la Pirámide. (plan task-84 §3.2-3.4)
 */
export class CameraRig {
  private scene: Container | null = null;
  private framing: Framing | null = null;
  private viewW = 1;
  private viewH = 1;
  private tween: gsap.core.Tween | null = null;
  /** prefers-reduced-motion → paneos instantáneos. */
  reducedMotion = false;

  attach(scene: Container): void {
    this.kill();
    this.scene = scene;
    if (this.framing) this.apply(this.framing);
  }

  resize(viewW: number, viewH: number): void {
    this.viewW = Math.max(1, viewW);
    this.viewH = Math.max(1, viewH);
    if (this.framing) this.apply(this.framing);
  }

  /** Corte directo al encuadre (entrada a macrozona tras la cortina). */
  snapTo(framing: Framing): void {
    this.kill();
    this.framing = framing;
    this.apply(framing);
  }

  /** Paneo suave (subzonas de la Pirámide). Resuelve al terminar. */
  panTo(framing: Framing, durationSec = 0.7): Promise<void> {
    this.framing = framing;
    if (!this.scene) return Promise.resolve();
    if (this.reducedMotion) {
      this.apply(framing);
      return Promise.resolve();
    }
    const target = this.transformFor(framing);
    this.kill();
    return new Promise((resolve) => {
      this.tween = gsap.to(this.scene!, {
        x: target.x,
        y: target.y,
        duration: durationSec,
        ease: "power2.inOut",
        onUpdate: () => {
          // La escala solo cambia si el encuadre cambia de tamaño (raro en paneos).
          if (this.scene) this.scene.scale.set(target.scale);
        },
        onComplete: () => resolve(),
      });
    });
  }

  destroy(): void {
    this.kill();
    this.scene = null;
  }

  private kill(): void {
    this.tween?.kill();
    this.tween = null;
  }

  private transformFor(framing: Framing): { x: number; y: number; scale: number } {
    const scale = Math.max(this.viewW / framing.w, this.viewH / framing.h);
    const cx = framing.x + framing.w / 2;
    const cy = framing.y + framing.h / 2;
    return {
      scale,
      x: this.viewW / 2 - cx * scale,
      y: this.viewH / 2 - cy * scale,
    };
  }

  private apply(framing: Framing): void {
    if (!this.scene) return;
    const t = this.transformFor(framing);
    this.scene.scale.set(t.scale);
    this.scene.position.set(t.x, t.y);
  }
}
