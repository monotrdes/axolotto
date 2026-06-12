import * as THREE from "three";
import { detectQualityTier, TIER_PROFILE, type QualityTier } from "../world/engine/qualityTier";

/**
 * Motor three.js del mundo-diorama 3D de papel (decisión 2026-06-12).
 * Convive con el motor Pixi: GameCanvas monta este motor solo en las zonas
 * ya migradas (hoy: Tianguis) y oculta el canvas Pixi mientras tanto.
 *
 * Cámara ortográfica dimétrica (~34° de elevación — frontal suficiente para
 * ver a los tenderos bajo los toldos), parallax sutil con el puntero y
 * enfoque animado por puesto (focusStall/resetFocus).
 */

export interface SceneAnimation {
  (t: number, dt: number): void;
}

export interface StallFocus {
  x: number;
  z: number;
  /** Factor de zoom sobre el viewH base (0.6 = 40% más cerca). */
  zoom: number;
}

export interface World3DScene {
  group: THREE.Object3D;
  /** Objetos tocables; el primer ancestro con userData.stallId define el id. */
  hotspots: THREE.Object3D[];
  animations: SceneAnimation[];
  /** Encuadres de enfoque por puesto (focusStall). */
  stallFocus: Record<string, StallFocus>;
  /** Animación de fundido (equivalente 3D de playMeltAnimation del Tianguis Pixi). */
  playMelt?(): void;
  dispose(): void;
}

const BASE_TARGET = new THREE.Vector3(0, 0.8, -0.4);

export class ThreeWorldEngine {
  renderer!: THREE.WebGLRenderer;
  scene = new THREE.Scene();
  camera = new THREE.OrthographicCamera();
  quality: QualityTier = "media";
  reducedMotion = false;
  onHotspot: ((stallId: string) => void) | null = null;

  private host!: HTMLElement;
  private current: World3DScene | null = null;
  private clock = new THREE.Clock();
  private raf = 0;
  private running = false;
  private pausedByUi = false;
  private lastFrame = 0;
  private fpsCap = 60;

  // Cámara: target/zoom animados por lerp en el loop.
  private azBase = 0;
  private elBase = THREE.MathUtils.degToRad(34);
  private az = this.azBase;
  private el = this.elBase;
  private pointer = { x: 0, y: 0 };
  private camTarget = BASE_TARGET.clone();
  private camTargetGoal = BASE_TARGET.clone();
  private zoom = 1;
  private zoomGoal = 1;

  private resizeObserver: ResizeObserver | null = null;
  private raycaster = new THREE.Raycaster();
  private downPos: { x: number; y: number } | null = null;

  private onVisibility = () => {
    if (document.hidden) this.stop();
    else if (!this.pausedByUi) this.start();
  };
  private onPointerMove = (e: PointerEvent) => {
    this.pointer.x = (e.clientX / window.innerWidth - 0.5) * 2;
    this.pointer.y = (e.clientY / window.innerHeight - 0.5) * 2;
  };
  private onPointerDown = (e: PointerEvent) => {
    this.downPos = { x: e.clientX, y: e.clientY };
  };
  private onPointerUp = (e: PointerEvent) => {
    if (!this.downPos || !this.current) return;
    const moved = Math.hypot(e.clientX - this.downPos.x, e.clientY - this.downPos.y);
    this.downPos = null;
    if (moved > 12) return; // fue un arrastre, no un tap
    const rect = this.renderer.domElement.getBoundingClientRect();
    const ndc = new THREE.Vector2(
      ((e.clientX - rect.left) / rect.width) * 2 - 1,
      -((e.clientY - rect.top) / rect.height) * 2 + 1,
    );
    this.raycaster.setFromCamera(ndc, this.camera);
    const hits = this.raycaster.intersectObjects(this.current.hotspots, true);
    for (const hit of hits) {
      let obj: THREE.Object3D | null = hit.object;
      while (obj) {
        const id = obj.userData?.stallId as string | undefined;
        if (id) {
          this.onHotspot?.(id);
          return;
        }
        obj = obj.parent;
      }
    }
  };

  static create(host: HTMLElement): ThreeWorldEngine {
    const engine = new ThreeWorldEngine();
    engine.init(host);
    return engine;
  }

  private init(host: HTMLElement): void {
    this.host = host;
    this.quality = detectQualityTier();
    this.fpsCap = TIER_PROFILE[this.quality].fpsCap;
    this.reducedMotion =
      window.matchMedia?.("(prefers-reduced-motion: reduce)").matches ?? false;

    this.renderer = new THREE.WebGLRenderer({ antialias: true });
    this.renderer.setPixelRatio(
      Math.min(window.devicePixelRatio || 1, this.quality === "ligera" ? 1.5 : 2),
    );
    // Sombras suaves solo en tiers con presupuesto (el alma del look maqueta).
    this.renderer.shadowMap.enabled = this.quality !== "ligera";
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    host.appendChild(this.renderer.domElement);

    this.scene.background = new THREE.Color(0x342b52);
    this.scene.add(new THREE.AmbientLight(0xd0c4f0, 0.95));
    const sun = new THREE.DirectionalLight(0xffe9c8, 1.5);
    sun.position.set(4, 16, 9);
    sun.castShadow = this.quality !== "ligera";
    sun.shadow.mapSize.set(2048, 2048);
    Object.assign(sun.shadow.camera, { left: -13, right: 13, top: 14, bottom: -14, far: 60 });
    sun.shadow.bias = -0.0004;
    this.scene.add(sun);

    this.resize();
    this.resizeObserver = new ResizeObserver(() => this.resize());
    this.resizeObserver.observe(host);

    document.addEventListener("visibilitychange", this.onVisibility);
    window.addEventListener("pointermove", this.onPointerMove);
    this.renderer.domElement.addEventListener("pointerdown", this.onPointerDown);
    this.renderer.domElement.addEventListener("pointerup", this.onPointerUp);

    this.start();
  }

  setScene(scene: World3DScene): void {
    this.clearScene();
    this.current = scene;
    this.scene.add(scene.group);
    this.resetFocus(true);
  }

  clearScene(): void {
    if (!this.current) return;
    this.scene.remove(this.current.group);
    this.current.dispose();
    this.current = null;
  }

  focusStall(stallId: string): void {
    const focus = this.current?.stallFocus[stallId];
    if (!focus) return;
    this.camTargetGoal.set(focus.x, BASE_TARGET.y, focus.z);
    this.zoomGoal = focus.zoom;
    if (this.reducedMotion) this.snapCamera();
  }

  resetFocus(immediate = false): void {
    this.camTargetGoal.copy(BASE_TARGET);
    this.zoomGoal = 1;
    if (immediate || this.reducedMotion) this.snapCamera();
  }

  setUiPaused(paused: boolean): void {
    this.pausedByUi = paused;
    if (paused) this.stop();
    else if (!document.hidden) this.start();
  }

  destroy(): void {
    this.stop();
    document.removeEventListener("visibilitychange", this.onVisibility);
    window.removeEventListener("pointermove", this.onPointerMove);
    this.renderer.domElement.removeEventListener("pointerdown", this.onPointerDown);
    this.renderer.domElement.removeEventListener("pointerup", this.onPointerUp);
    this.resizeObserver?.disconnect();
    this.resizeObserver = null;
    this.clearScene();
    this.renderer.dispose();
    this.renderer.domElement.remove();
  }

  private snapCamera(): void {
    this.camTarget.copy(this.camTargetGoal);
    this.zoom = this.zoomGoal;
  }

  private viewH(): number {
    const a = this.host.clientWidth / Math.max(1, this.host.clientHeight);
    return (a < 0.9 ? 12.8 : 11.2) * this.zoom;
  }

  private resize(): void {
    const w = this.host.clientWidth;
    const h = Math.max(1, this.host.clientHeight);
    const a = w / h;
    const vh = this.viewH();
    this.camera.left = (-vh * a) / 2;
    this.camera.right = (vh * a) / 2;
    this.camera.top = vh / 2 + 0.8;
    this.camera.bottom = -vh / 2 + 0.8;
    this.camera.near = 1;
    this.camera.far = 120;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(w, h);
  }

  private placeCamera(): void {
    const r = 42;
    this.camera.position.set(
      this.camTarget.x + r * Math.cos(this.el) * Math.sin(this.az),
      this.camTarget.y + r * Math.sin(this.el),
      this.camTarget.z + r * Math.cos(this.el) * Math.cos(this.az),
    );
    this.camera.lookAt(this.camTarget);
  }

  private start(): void {
    if (this.running) return;
    this.running = true;
    this.clock.getDelta(); // descarta el dt acumulado en pausa
    const loop = (now: number) => {
      if (!this.running) return;
      this.raf = requestAnimationFrame(loop);
      if (now - this.lastFrame < 1000 / this.fpsCap - 2) return;
      this.lastFrame = now;
      this.tick();
    };
    this.raf = requestAnimationFrame(loop);
  }

  private stop(): void {
    this.running = false;
    cancelAnimationFrame(this.raf);
  }

  private tick(): void {
    const dt = this.clock.getDelta();
    const t = this.clock.elapsedTime;

    if (this.current && !this.reducedMotion) {
      for (const anim of this.current.animations) anim(t, dt);
    }

    // Parallax sutil + lerp de enfoque.
    const parallax = this.reducedMotion ? 0 : 1;
    const targetAz = this.azBase + this.pointer.x * 0.09 * parallax;
    const targetEl = this.elBase - this.pointer.y * 0.05 * parallax;
    this.az += (targetAz - this.az) * 0.06;
    this.el += (targetEl - this.el) * 0.06;
    const prevZoom = this.zoom;
    this.camTarget.lerp(this.camTargetGoal, 0.08);
    this.zoom += (this.zoomGoal - this.zoom) * 0.08;
    if (Math.abs(this.zoom - prevZoom) > 1e-4) this.resize();
    this.placeCamera();

    this.renderer.render(this.scene, this.camera);
  }
}
