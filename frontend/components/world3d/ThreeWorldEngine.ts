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
  /**
   * Billboards 2D (axolotitos): el motor les fija el yaw de cámara cada
   * frame. Deben colgar del root de la escena (sin padres rotados).
   */
  billboards?: THREE.Object3D[];
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

  private ambientLight!: THREE.AmbientLight;
  private sunLight!: THREE.DirectionalLight;
  private bubbles?: THREE.Points;
  private bubbleData: Array<{ seed: number; speed: number }> = [];

  // Micro-interacciones: hover (solo desktop) y rebote de cartón al tocar.
  private hoverFine = false;
  private hoverNdc: THREE.Vector2 | null = null;
  private hoverRoot: THREE.Object3D | null = null;
  private frame = 0;
  private fx = new Map<THREE.Object3D, { base: number; k: number; bounceStart: number }>();

  private onVisibility = () => {
    if (document.hidden) this.stop();
    else if (!this.pausedByUi) this.start();
  };
  private onPointerMove = (e: PointerEvent) => {
    this.pointer.x = (e.clientX / window.innerWidth - 0.5) * 2;
    this.pointer.y = (e.clientY / window.innerHeight - 0.5) * 2;
    if (this.hoverFine) {
      const rect = this.renderer.domElement.getBoundingClientRect();
      this.hoverNdc ??= new THREE.Vector2();
      this.hoverNdc.set(
        ((e.clientX - rect.left) / rect.width) * 2 - 1,
        -((e.clientY - rect.top) / rect.height) * 2 + 1,
      );
    }
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
    const root = this.stallRootAt(ndc);
    if (root) {
      this.bounce(root);
      this.onHotspot?.(root.userData.stallId as string);
    }
  };

  /** Primer ancestro con userData.stallId bajo el puntero, o null. */
  private stallRootAt(ndc: THREE.Vector2): THREE.Object3D | null {
    if (!this.current) return null;
    this.raycaster.setFromCamera(ndc, this.camera);
    const hits = this.raycaster.intersectObjects(this.current.hotspots, true);
    for (const hit of hits) {
      let obj: THREE.Object3D | null = hit.object;
      while (obj) {
        if (obj.userData?.stallId) return obj;
        obj = obj.parent;
      }
    }
    return null;
  }

  private fxFor(obj: THREE.Object3D): { base: number; k: number; bounceStart: number } {
    let st = this.fx.get(obj);
    if (!st) {
      st = { base: obj.scale.x, k: 1, bounceStart: -1 };
      this.fx.set(obj, st);
    }
    return st;
  }

  /** Rebote de cartón al tocar un puesto. */
  private bounce(obj: THREE.Object3D): void {
    if (this.reducedMotion) return;
    this.fxFor(obj).bounceStart = this.clock.elapsedTime;
  }

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
    this.hoverFine =
      window.matchMedia?.("(hover: hover) and (pointer: fine)").matches ?? false;

    this.renderer = new THREE.WebGLRenderer({ antialias: true });
    this.renderer.setPixelRatio(
      Math.min(window.devicePixelRatio || 1, this.quality === "ligera" ? 1.5 : 2),
    );
    // Sombras suaves solo en tiers con presupuesto (el alma del look maqueta).
    this.renderer.shadowMap.enabled = this.quality !== "ligera";
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    host.appendChild(this.renderer.domElement);

    // Neblina Xochimilco pre-hispánica cristalina (linear Fog).
    // Deja el primer plano totalmente claro y nítido (0% niebla), y desvanece suavemente el fondo.
    this.scene.fog = new THREE.Fog(0x0f5a54, 30, 60);

    // Gradiente de laguna de Xochimilco ancestral (aguas cristalinas y luminosas).
    const bg = document.createElement("canvas");
    bg.width = 4;
    bg.height = 256;
    const bgCtx = bg.getContext("2d")!;
    const grad = bgCtx.createLinearGradient(0, 256, 0, 0);
    grad.addColorStop(0, "#0c3c3a");   // Profundidades cristalinas color esmeralda-azul
    grad.addColorStop(0.4, "#0f5a54"); // Turquesa medio
    grad.addColorStop(0.75, "#1fa394"); // Esmeralda transparente
    grad.addColorStop(1, "#5ce1c9");    // Luz brillante filtrando por el agua
    bgCtx.fillStyle = grad;
    bgCtx.fillRect(0, 0, 4, 256);
    const bgTex = new THREE.CanvasTexture(bg);
    bgTex.colorSpace = THREE.SRGBColorSpace;
    this.scene.background = bgTex;

    // Luces con tonalidad acuática brillante y mágica (bioluminiscencia turquesa).
    this.ambientLight = new THREE.AmbientLight(0x40dfcc, 1.2);
    this.scene.add(this.ambientLight);

    this.sunLight = new THREE.DirectionalLight(0xfff2d4, 1.9); // Sol cálido brillante cruzando el agua
    this.sunLight.position.set(4, 16, 9);
    this.sunLight.castShadow = this.quality !== "ligera";
    this.sunLight.shadow.mapSize.set(2048, 2048);
    Object.assign(this.sunLight.shadow.camera, { left: -13, right: 13, top: 14, bottom: -14, far: 60 });
    this.sunLight.shadow.bias = -0.0004;
    this.scene.add(this.sunLight);

    // Burbujas flotantes (Points) siempre habilitadas (variando conteo para optimizar).
    const bubbleCount = this.quality === "alta" ? 80 : (this.quality === "media" ? 40 : 18);
    const geo = new THREE.BufferGeometry();
    const positions = new Float32Array(bubbleCount * 3);
    this.bubbleData = [];
    for (let i = 0; i < bubbleCount; i++) {
      positions[i * 3] = (Math.random() - 0.5) * 16;
      positions[i * 3 + 1] = Math.random() * 8;
      positions[i * 3 + 2] = (Math.random() - 0.5) * 16 - 1;
      this.bubbleData.push({
        seed: Math.random() * 100,
        speed: 0.35 + Math.random() * 0.4,
      });
    }
    geo.setAttribute("position", new THREE.BufferAttribute(positions, 3));

    // Creación del canvas para la textura de burbuja transparente con borde y specular
    const bCanvas = document.createElement("canvas");
    bCanvas.width = 32;
    bCanvas.height = 32;
    const bCtx = bCanvas.getContext("2d")!;
    bCtx.clearRect(0, 0, 32, 32);
    bCtx.strokeStyle = "rgba(255, 255, 255, 0.75)";
    bCtx.lineWidth = 2.5;
    bCtx.beginPath();
    bCtx.arc(16, 16, 12, 0, Math.PI * 2);
    bCtx.stroke();
    bCtx.fillStyle = "rgba(255, 255, 255, 0.85)";
    bCtx.beginPath();
    bCtx.arc(11, 11, 3.5, 0, Math.PI * 2);
    bCtx.fill();

    const bTex = new THREE.CanvasTexture(bCanvas);
    const mat = new THREE.PointsMaterial({
      size: 0.26,
      map: bTex,
      transparent: true,
      opacity: 0.75,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
      fog: false, // Desactivar niebla para que resplandezcan siempre
    });

    this.bubbles = new THREE.Points(geo, mat);
    this.scene.add(this.bubbles);

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
    this.fx.clear();
    this.hoverRoot = null;
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
    if (this.bubbles) {
      this.scene.remove(this.bubbles);
      this.bubbles.geometry.dispose();
      (this.bubbles.material as THREE.PointsMaterial).dispose();
      this.bubbles = undefined;
    }
    this.renderer.dispose();
    this.renderer.domElement.remove();
  }

  private snapCamera(): void {
    this.camTarget.copy(this.camTargetGoal);
    this.zoom = this.zoomGoal;
  }

  private viewH(): number {
    const w = this.host.clientWidth;
    const h = Math.max(1, this.host.clientHeight);
    const a = w / h;
    const baseH = a < 0.9 ? 12.8 : 11.2;
    // Si la pantalla es muy estrecha (retrato móvil extremo), aumentamos vh
    // para que el ancho de la cámara (vh * a) sea al menos 6.0 unidades lógicas,
    // garantizando que todos los puestos queden visibles horizontalmente sin alejar demasiado la cámara.
    const minW = 6.0;
    if (a < 0.9 && baseH * a < minW) {
      return (minW / a) * this.zoom;
    }
    return baseH * this.zoom;
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
    this.frame++;

    if (this.current && !this.reducedMotion) {
      for (const anim of this.current.animations) anim(t, dt);
    }

    // Actualización de burbujas flotantes (efecto bajo el agua)
    if (this.bubbles && this.bubbleData.length > 0 && !this.reducedMotion) {
      const posAttr = this.bubbles.geometry.getAttribute("position") as THREE.BufferAttribute;
      const array = posAttr.array as Float32Array;
      for (let i = 0; i < this.bubbleData.length; i++) {
        const data = this.bubbleData[i];
        let y = array[i * 3 + 1];
        let x = array[i * 3];
        y += dt * data.speed;
        const wobble = Math.sin(t * 1.8 + data.seed) * 0.007;
        x += wobble;
        if (y > 7.5) {
          y = -1.0;
          x = (Math.random() - 0.5) * 15;
        }
        array[i * 3] = x;
        array[i * 3 + 1] = y;
      }
      posAttr.needsUpdate = true;
    }

    // Refracción de luz (efecto bajo el agua en calidad media/alta)
    if (this.quality !== "ligera" && this.ambientLight) {
      this.ambientLight.intensity = 1.2 + Math.sin(t * 1.3) * 0.08;
      if (this.sunLight) {
        this.sunLight.position.x = 4 + Math.sin(t * 0.8) * 0.3;
        this.sunLight.position.z = 9 + Math.cos(t * 0.8) * 0.3;
      }
    }

    // Billboards siempre de cara a la cámara (yaw plano, cámara ortográfica).
    if (this.current?.billboards) {
      for (const b of this.current.billboards) b.rotation.y = this.az;
    }

    // Hover (desktop): raycast cada 3 frames; resalta el puesto bajo el cursor.
    if (this.hoverFine && this.hoverNdc && this.frame % 3 === 0) {
      const root = this.stallRootAt(this.hoverNdc);
      if (root !== this.hoverRoot) {
        if (this.hoverRoot) this.fxFor(this.hoverRoot); // asegura el lerp de salida
        this.hoverRoot = root;
        if (root) this.fxFor(root);
        this.renderer.domElement.style.cursor = root ? "pointer" : "";
      }
    }

    // Efectos de escala (hover + rebote) — después de las animaciones de la
    // escena para ganar a cualquier reset de escala propio (p.ej. el melt).
    for (const [obj, st] of this.fx) {
      const targetK = obj === this.hoverRoot ? 1.05 : 1;
      st.k = this.reducedMotion ? targetK : st.k + (targetK - st.k) * 0.16;
      let env = 1;
      if (st.bounceStart >= 0) {
        const bt = t - st.bounceStart;
        if (bt < 0.7) env = 1 + Math.sin(bt * 18) * 0.09 * Math.exp(-bt * 5);
        else st.bounceStart = -1;
      }
      obj.scale.setScalar(st.base * st.k * env);
      if (obj !== this.hoverRoot && st.bounceStart < 0 && Math.abs(st.k - 1) < 0.002) {
        obj.scale.setScalar(st.base);
        this.fx.delete(obj);
      }
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
