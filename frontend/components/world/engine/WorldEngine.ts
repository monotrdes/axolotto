import { Application, Container } from "pixi.js";
import { CameraRig } from "./CameraRig";
import { detectQualityTier, TIER_PROFILE, type QualityTier } from "./qualityTier";
import { WorldBridge } from "../WorldBridge";

/**
 * Núcleo Pixi del mundo papel picado: ciclo de vida de la Application,
 * pausa por visibilidad, cap de DPR/FPS por tier. (plan task-84 §3.1, §7)
 */
export class WorldEngine {
  app!: Application;
  /** Contenedor raíz donde ZoneManager monta la escena activa. */
  stage!: Container;
  camera = new CameraRig();
  bridge = new WorldBridge();
  quality: QualityTier = "media";
  /** Fase lunar actual (1-6) — tiñe la luz superficial de las 3 macrozonas (plan task-84 §2 Subzona 3b, §4 Fase 4). */
  lunarPhase = 1;

  private host!: HTMLElement;
  private resizeObserver: ResizeObserver | null = null;
  private onVisibility = () => {
    if (document.hidden) this.app.ticker.stop();
    else if (!this.pausedByUi) this.app.ticker.start();
  };
  private pausedByUi = false;

  static async create(host: HTMLElement): Promise<WorldEngine> {
    const engine = new WorldEngine();
    await engine.init(host);
    return engine;
  }

  private async init(host: HTMLElement): Promise<void> {
    this.host = host;
    this.quality = detectQualityTier();
    const profile = TIER_PROFILE[this.quality];

    this.app = new Application();
    await this.app.init({
      resizeTo: host,
      backgroundAlpha: 0,
      antialias: false,
      resolution: Math.min(window.devicePixelRatio || 1, 2),
      autoDensity: true,
    });
    this.app.ticker.maxFPS = profile.fpsCap;

    this.stage = new Container();
    this.app.stage.addChild(this.stage);

    host.appendChild(this.app.canvas);

    this.camera.reducedMotion =
      window.matchMedia?.("(prefers-reduced-motion: reduce)").matches ?? false;
    this.camera.resize(host.clientWidth, host.clientHeight);

    this.resizeObserver = new ResizeObserver(() => {
      this.camera.resize(host.clientWidth, host.clientHeight);
    });
    this.resizeObserver.observe(host);

    document.addEventListener("visibilitychange", this.onVisibility);
  }

  /** Pausa manual (ej: un modal HTML fullscreen cubre el canvas). */
  setUiPaused(paused: boolean): void {
    this.pausedByUi = paused;
    if (paused) this.app.ticker.stop();
    else if (!document.hidden) this.app.ticker.start();
  }

  destroy(): void {
    document.removeEventListener("visibilitychange", this.onVisibility);
    this.resizeObserver?.disconnect();
    this.resizeObserver = null;
    this.camera.destroy();
    this.bridge.clear();
    // true: destruye también texturas/geometrías de la GPU (plan §7, unload agresivo)
    this.app.destroy(true, { children: true, texture: true });
  }
}
