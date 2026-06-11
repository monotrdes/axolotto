import type { Container } from "pixi.js";
import type { WorldEngine } from "../engine/WorldEngine";
import {
  framingFor,
  resolveZoneTarget,
  PAINTED_BOUNDS,
  DESIGN_SPACE,
  type MacroZoneId,
  type ZoneTarget,
} from "./zoneConfig";
import { buildPlaceholderScene } from "./placeholderScenes";

export type SceneBuilder = (engine: WorldEngine) => Container | Promise<Container>;

/** Cortina de papel: la implementa React (PaperCurtain); aquí solo el contrato. */
export interface CurtainController {
  cover(): Promise<void>;
  reveal(): Promise<void>;
}

/**
 * Monta/desmonta macrozonas (escenas desconectadas, plan §3.2):
 * - Entre macrozonas: cortina → destroy escena saliente → build entrante → snap cámara → revelar.
 * - Dentro de la Pirámide: paneo de cámara, sin cortina ni cargas.
 */
export class ZoneManager {
  private current: { target: ZoneTarget; scene: Container } | null = null;
  private transitioning = false;

  /** Fases 1-4 reemplazan builders por dioramas reales sin tocar el manager. */
  private builders: Record<MacroZoneId, SceneBuilder> = {
    santuario: (e) => buildPlaceholderScene("santuario", e),
    tianguis: (e) => buildPlaceholderScene("tianguis", e),
    piramide: (e) => buildPlaceholderScene("piramide", e),
  };

  constructor(private engine: WorldEngine) {}

  registerBuilder(zone: MacroZoneId, builder: SceneBuilder): void {
    this.builders[zone] = builder;
  }

  get activeTarget(): ZoneTarget | null {
    return this.current?.target ?? null;
  }

  /** Entrada inicial sin cortina (primer mount). */
  async enter(zoneId: string): Promise<void> {
    const target = resolveZoneTarget(zoneId);
    await this.mount(target);
  }

  async navigate(zoneId: string, curtain: CurtainController | null): Promise<void> {
    if (this.transitioning) return;
    const target = resolveZoneTarget(zoneId);
    const from = this.current?.target;

    if (!from) {
      await this.enter(zoneId);
      return;
    }

    // Misma macrozona → paneo (subzonas de la Pirámide).
    if (from.macro === target.macro) {
      if (from.sub === target.sub) return;
      this.transitioning = true;
      try {
        this.current!.target = target;
        await this.engine.camera.panTo(framingFor(target));
        this.engine.bridge.emit("zoneSettled", { macro: target.macro, sub: target.sub });
      } finally {
        this.transitioning = false;
      }
      return;
    }

    // Macrozona distinta → cortina de papel.
    this.transitioning = true;
    try {
      await curtain?.cover();
      this.unmount();
      await this.mount(target);
      await curtain?.reveal();
    } finally {
      this.transitioning = false;
    }
  }

  destroy(): void {
    this.unmount();
  }

  private async mount(target: ZoneTarget): Promise<void> {
    const scene = await this.builders[target.macro](this.engine);
    this.engine.stage.addChild(scene);
    this.engine.camera.attach(scene, {
      ...PAINTED_BOUNDS[target.macro],
      y0: 0,
      h: DESIGN_SPACE[target.macro].h,
    });
    this.engine.camera.snapTo(framingFor(target));
    this.current = { target, scene };
    this.engine.bridge.emit("zoneSettled", { macro: target.macro, sub: target.sub });
  }

  private unmount(): void {
    if (!this.current) return;
    // TODO(Fase 2): Assets.unload del atlas de la macrozona saliente (plan §7).
    this.current.scene.destroy({ children: true, texture: true });
    this.current = null;
  }
}
