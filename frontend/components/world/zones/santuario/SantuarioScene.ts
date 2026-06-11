import { Container, Graphics, Text, Ticker } from "pixi.js";
import gsap from "gsap";
import type { WorldEngine } from "../../engine/WorldEngine";
import type { AxolotitoData } from "../../entities/AxolotitoSprite";
import type { AmigoData } from "../../mapBackendAxolotito";
import { AxolotitoPuppet, type PuppetState } from "../../puppet/AxolotitoPuppet";
import { DESIGN_SPACE, PAINTED_BOUNDS, lunarSurfaceTint } from "../zoneConfig";

/**
 * Diorama del Santuario (plan task-84 §2, rediseño cueva submarina):
 * chinampa vertical de 3 niveles. Arriba: SOLO crianza — nidos con huevo o
 * camita, hasta 8 slots desbloqueados por expansión de cueva (los bloqueados
 * se ven como roca sin excavar). Centro: la casa con la Mesa de amigos (la
 * decoración tipada llega en la fase de sala). Abajo: embarcadero social.
 * Fondo/arte = placeholder Graphics hasta el atlas.
 */

const { w: W, h: H } = DESIGN_SPACE.santuario;
// Overscan lateral pintado (visible en pantallas anchas, plan §3.4).
const { x0: PX, w: PW } = PAINTED_BOUNDS.santuario;

// Bandas verticales de los 3 niveles (espacio de diseño 1080×1920).
const NIVEL_NIDOS_ROW1_Y = 310;
const NIVEL_NIDOS_ROW2_Y = 540;
const NIVEL_SALA = { top: 760, bottom: 1230 };
const NIVEL_EMBARCADERO_Y = 1500;

const NEST_SLOTS_X = [180, 420, 660, 900];
// El backend define 8 niveles de cueva = 8 nidos máximo (spot i abre en nivel i+1).
const MAX_NEST_SLOTS = 8;
const WANDER_SPEED = 55; // px/s en espacio de diseño

/** Posición del slot de nido i (2 filas de 4). */
function nestSlotPos(i: number): { x: number; y: number } {
  return {
    x: NEST_SLOTS_X[i % 4],
    y: i < 4 ? NIVEL_NIDOS_ROW1_Y : NIVEL_NIDOS_ROW2_Y,
  };
}

/** Estado de la cueva que el diorama necesita (de GET /cave/status). */
export interface CaveStatusData {
  level: number;
  spots: number;
  hasTable: boolean;
  tableSeats: number;
}

/** Payload de GET /cave/decorations que consume el diorama. */
export interface DecorSlotInfo {
  slot_id: string;
  subcategory: string;
}
export interface DecorItemDetail {
  name?: string;
  emoji?: string;
  color?: string | null;
}
export interface DecoracionesData {
  decorations: Record<string, number | null>;
  slots: DecorSlotInfo[];
  items: Record<string, DecorItemDetail>;
}

// Anclas de los slots de decoración en la sala (espacio de diseño).
// MESA/MANTEL/SILLAS son badges junto a la mesa (la mesa grande sigue siendo
// el hotspot de hostear partidas); FONDO usa también el overscan lateral.
const SALA_ANCHORS: Record<string, ReadonlyArray<readonly [number, number]>> = {
  AMBIENTE: [[120, 810]],
  LUZ: [[W / 2, 800]],
  MESA: [[W / 2 - 200, 1075]],
  MANTEL: [[W / 2, 1060]],
  SILLAS: [[W / 2 + 200, 1075]],
  FONDO: [
    [110, 1130],
    [970, 1130],
    [80, 900],
    [1000, 900],
    [-240, 1010],
    [1320, 1010],
  ],
  ESPECIAL: [
    [300, 990],
    [780, 990],
    [180, 870],
    [900, 870],
    [W / 2, 900],
  ],
};

function parseHexColor(color: string | null | undefined, fallback: number): number {
  if (!color) return fallback;
  const n = parseInt(color.replace("#", ""), 16);
  return Number.isNaN(n) ? fallback : n;
}

interface PuppetEntry {
  puppet: AxolotitoPuppet;
  targetX: number;
  baseY: number;
  paused: number;
  particleTimer: number;
}

interface Particle {
  obj: Container;
  vy: number;
  life: number;
  maxLife: number;
}

interface BoatEntry {
  boat: Container;
  baseY: number;
  phase: number;
}

type NestKind = "locked" | "egg" | "camita" | "empty";

export class SantuarioScene extends Container {
  private engine: WorldEngine;
  private puppetLayer = new Container();
  private nestLayer = new Container();
  private salaLayer = new Container();
  private ambientOverlay = new Graphics();
  private amigosLayer = new Container();
  private particleLayer = new Container();
  private puppets = new Map<string, PuppetEntry>();
  private caveStatus: CaveStatusData = { level: 1, spots: 1, hasTable: false, tableSeats: 0 };
  private lastAxolotitos: AxolotitoData[] = [];
  private decoraciones: DecoracionesData | null = null;
  private particles: Particle[] = [];
  private boats: BoatEntry[] = [];
  private prevNestKinds = new Map<number, NestKind>();
  private hatchTweens: gsap.core.Timeline[] = [];
  private actionBubbles: Container | null = null;
  private actionBubblesFor: string | null = null;
  private actionBubblesTimer: gsap.core.Tween | null = null;
  private elapsed = 0;
  private tick = (ticker: Ticker) => this.update(ticker.deltaMS / 1000);

  constructor(engine: WorldEngine) {
    super();
    this.engine = engine;
    this.buildBackdrop();
    this.addChild(
      this.ambientOverlay,
      this.salaLayer,
      this.nestLayer,
      this.amigosLayer,
      this.puppetLayer,
      this.particleLayer,
    );
    this.rebuildNests();
    this.rebuildSala();
    engine.app.ticker.add(this.tick);
  }

  override destroy(options?: Parameters<Container["destroy"]>[0]): void {
    this.engine.app.ticker.remove(this.tick);
    this.closeActionBubbles();
    this.killHatchTweens();
    this.puppets.clear();
    this.particles = [];
    this.boats = [];
    super.destroy(options);
  }

  /** Embarcadero social: amigos llegan en trajineritas (plan §2). */
  setAmigos(amigos: AmigoData[]): void {
    if (this.destroyed) return;
    this.closeActionBubbles();
    this.amigosLayer.removeChildren().forEach((c) => c.destroy({ children: true }));
    this.boats = [];

    // Canasta de mimbre: abre el pergamino completo de amigos (AmigosPage).
    const canasta = new Container();
    const cg = new Graphics()
      .ellipse(0, 0, 52, 36)
      .fill(0xa9743f)
      .stroke({ color: 0xfff7ec, width: 4 });
    canasta.addChild(cg);
    const cEmoji = new Text({ text: "🧺", style: { fontSize: 44 } });
    cEmoji.anchor.set(0.5);
    cEmoji.position.set(0, -8);
    canasta.addChild(cEmoji);
    const cTag = new Text({
      text: "Amigos",
      style: { fontSize: 20, fill: 0xfff7ec, fontWeight: "700" },
    });
    cTag.anchor.set(0.5);
    cTag.position.set(0, 52);
    canasta.addChild(cTag);
    canasta.position.set(W - 130, NIVEL_EMBARCADERO_Y + 40);
    this.hotspot(canasta, "canasta-amigos");
    this.amigosLayer.addChild(canasta);

    // Hasta 4 trajineritas visibles; el resto queda en la canasta.
    const visibles = amigos.slice(0, 4);
    visibles.forEach((amigo, i) => {
      const baseY = NIVEL_EMBARCADERO_Y + (i % 2) * 26;
      const boat = this.buildTrajinerita(amigo);
      boat.position.set(150 + i * 210, baseY);
      this.amigosLayer.addChild(boat);
      this.boats.push({ boat, baseY, phase: i * 1.3 });
    });
    if (amigos.length > 4) {
      const more = new Text({
        text: `+${amigos.length - 4} en la canasta`,
        style: { fontSize: 20, fill: 0xfff7ec, fontWeight: "700" },
      });
      more.anchor.set(0.5);
      more.position.set(W / 2, NIVEL_EMBARCADERO_Y + 110);
      this.amigosLayer.addChild(more);
    }
  }

  /** Estado de la cueva (nivel/spots/mesa) desde GET /cave/status. */
  setCaveStatus(status: CaveStatusData): void {
    if (this.destroyed) return;
    this.caveStatus = status;
    this.rebuildNests();
    this.rebuildSala();
  }

  /** Decoraciones equipadas + layout de slots desde GET /cave/decorations. */
  setDecoraciones(data: DecoracionesData): void {
    if (this.destroyed) return;
    this.decoraciones = data;
    this.rebuildSala();
  }

  /** Sincroniza huevos y axolotitos desde los datos del backend. */
  setAxolotitos(data: AxolotitoData[]): void {
    if (this.destroyed) return;
    this.lastAxolotitos = data;
    this.rebuildNests();

    const axos = data.filter((a) => !a.isEgg && a.state !== "sleeping");

    // Nivel central: títeres vivos.
    const seen = new Set<string>();
    for (const axo of axos) {
      seen.add(axo.id);
      const existing = this.puppets.get(axo.id);
      const state = toPuppetState(axo);
      if (existing) {
        existing.puppet.setState(state);
        continue;
      }
      const puppet = new AxolotitoPuppet(axo);
      const baseY =
        NIVEL_SALA.top + 80 + Math.random() * (NIVEL_SALA.bottom - NIVEL_SALA.top - 160);
      puppet.position.set(120 + Math.random() * (W - 240), baseY);
      puppet.setState(state, true);
      this.puppetLayer.addChild(puppet);
      this.puppets.set(axo.id, {
        puppet,
        targetX: puppet.x,
        baseY,
        paused: 1 + Math.random() * 3,
        particleTimer: 1 + Math.random() * 2,
      });
    }
    // Retirar títeres de axolotitos que ya no están.
    for (const [id, entry] of this.puppets) {
      if (!seen.has(id)) {
        entry.puppet.destroy({ children: true });
        this.puppets.delete(id);
      }
    }
  }

  /**
   * Zona superior (solo crianza): un nido por slot — huevo si incuba, camita
   * si su axolotito nació, roca con candado si el slot aún no se desbloquea.
   * Tap: huevo/camita → gestión en el panel Santuario; bloqueado → expandir.
   */
  private rebuildNests(): void {
    this.killHatchTweens();
    this.nestLayer.removeChildren().forEach((c) => c.destroy({ children: true }));
    const eggs = this.lastAxolotitos.filter((a) => a.isEgg);
    const axos = this.lastAxolotitos.filter((a) => !a.isEgg);
    const spots = Math.max(1, Math.min(this.caveStatus.spots, MAX_NEST_SLOTS));
    const kinds = new Map<number, NestKind>();

    for (let slot = 0; slot < MAX_NEST_SLOTS; slot++) {
      const { x, y } = nestSlotPos(slot);
      if (slot >= spots) {
        // Slot bloqueado: roca sin excavar — el spot i se abre en nivel i+1.
        kinds.set(slot, "locked");
        const node = buildLockedNest(x, y, slot + 1);
        this.hotspot(node, "nido-bloqueado");
        this.nestLayer.addChild(node);
        continue;
      }
      const egg = eggs.find((e) => e.caveIndex === slot);
      const owner = axos.find((a) => a.caveIndex === slot);
      const kind: NestKind = egg ? "egg" : owner ? "camita" : "empty";
      kinds.set(slot, kind);
      const node = egg
        ? buildNestWithEgg(x, y, egg)
        : owner
          ? buildCamita(x, y, owner.name, owner.state === "sleeping")
          : buildEmptyNest(x, y);
      if (egg) this.hotspot(node, "nido-huevo", egg.id);
      else if (owner) this.hotspot(node, "nido-axo", owner.id);
      else this.hotspot(node, "nido-vacio");
      this.nestLayer.addChild(node);
      // Eclosión: este slot tenía huevo y ahora tiene camita (plan §2).
      if (kind === "camita" && this.prevNestKinds.get(slot) === "egg") {
        this.playHatchAnimation(node, x, y);
      }
    }
    this.prevNestKinds = kinds;
  }

  /**
   * Transformación nido→camita al eclosionar: un huevo efímero tiembla cada
   * vez más fuerte, revienta en cascaritas y la camita brota con rebote de
   * cartón. Con prefers-reduced-motion el swap queda instantáneo (como antes).
   */
  private playHatchAnimation(camita: Container, x: number, y: number): void {
    if (this.engine.camera.reducedMotion) return;

    // Huevo efímero encima de la camita (mismas formas que buildNestWithEgg, listo/dorado).
    const egg = new Container();
    egg.position.set(x, y);
    egg.addChild(
      new Graphics()
        .ellipse(0, 26, 56, 20)
        .fill(0x8b5e34)
        .stroke({ color: 0xfff7ec, width: 4 })
        .ellipse(0, 0, 32, 40)
        .fill(0xfff3c4)
        .stroke({ color: 0xf5c542, width: 4 }),
    );
    this.nestLayer.addChild(egg);
    camita.scale.set(0);

    const tl = gsap.timeline({
      onComplete: () => {
        if (!egg.destroyed) egg.destroy({ children: true });
      },
    });
    tl.to(egg, { rotation: 0.12, duration: 0.07, yoyo: true, repeat: 9, ease: "sine.inOut" });
    tl.add(() => this.spawnShellBurst(x, y));
    tl.to(egg.scale, { x: 1.35, y: 1.35, duration: 0.16, ease: "power2.out" });
    tl.to(egg, { alpha: 0, duration: 0.16 }, "<");
    tl.to(camita.scale, { x: 1, y: 1, duration: 0.45, ease: "back.out(2.2)" }, ">-0.04");
    this.hatchTweens.push(tl);
  }

  /** Cascaritas + destello al reventar el huevo (no en tier ligera). */
  private spawnShellBurst(x: number, y: number): void {
    if (this.destroyed || this.engine.quality === "ligera") return;
    for (let i = 0; i < 8; i++) {
      const bit = new Graphics()
        .poly([0, -8, 7, 5, -7, 5])
        .fill(i % 2 ? 0xfff3c4 : 0xf5c542)
        .stroke({ color: 0xfff7ec, width: 2 });
      bit.rotation = Math.random() * Math.PI * 2;
      this.spawnParticle(
        bit,
        x + (Math.random() - 0.5) * 80,
        y + (Math.random() - 0.5) * 36,
        30 + Math.random() * 55,
        0.9,
      );
    }
    const spark = new Text({ text: "✨", style: { fontSize: 36 } });
    spark.anchor.set(0.5);
    this.spawnParticle(spark, x, y - 20, 40, 1.1);
  }

  /** Mata timelines de eclosión vivos (rebuild o destroy a mitad de animación). */
  private killHatchTweens(): void {
    this.hatchTweens.forEach((t) => t.kill());
    this.hatchTweens = [];
  }

  /**
   * Sala central (la casa): mesa de juego con skin/mantel/sillas según lo
   * equipado, tinte de AMBIENTE sobre el agua, y chips de slot tipados —
   * vacío = "+" punteado discreto, ocupado = el item; tap → panel de
   * decoración filtrado a esa categoría (hotspot "decor:<slot_id>").
   */
  private rebuildSala(): void {
    this.salaLayer.removeChildren().forEach((c) => c.destroy({ children: true }));
    this.ambientOverlay.clear();

    const decor = this.decoraciones;
    const itemAt = (slotId: string): DecorItemDetail | null => {
      const itemId = decor?.decorations?.[slotId];
      if (itemId === null || itemId === undefined) return null;
      return decor?.items?.[String(itemId)] ?? null;
    };

    // Tinte de AMBIENTE sobre toda el agua (suave, no sustituye al fondo).
    const ambiente = itemAt("AMBIENTE_0");
    if (ambiente?.color) {
      this.ambientOverlay
        .rect(PX, 0, PW, H)
        .fill({ color: parseHexColor(ambiente.color, 0x1b7a8c), alpha: 0.22 });
    }

    // ── Mesa de juego (centro de la sala) ──
    const mesaItem = itemAt("MESA_0");
    const mantelItem = itemAt("MANTEL_0");
    const sillasItem = itemAt("SILLAS_0");
    const mesa = new Container();
    const cx = W / 2;
    const cy = NIVEL_SALA.bottom - 10;
    const mesaColor = parseHexColor(mesaItem?.color, 0xa9743f);
    const mesaG = new Graphics()
      .ellipse(0, 0, 130, 52)
      .fill(mesaColor)
      .stroke({ color: 0xfff7ec, width: 5 });
    mesa.addChild(mesaG);
    if (mantelItem) {
      const mantel = new Graphics()
        .ellipse(0, -4, 100, 36)
        .fill(parseHexColor(mantelItem.color, 0xe4007c))
        .stroke({ color: 0xfff7ec, width: 3 });
      mesa.addChild(mantel);
    }
    // Sillas/troncos alrededor según los asientos reales de la cueva.
    if (this.caveStatus.hasTable && this.caveStatus.tableSeats > 0) {
      const sillaColor = parseHexColor(sillasItem?.color, 0x8b5e34);
      const n = Math.min(this.caveStatus.tableSeats, 8);
      for (let i = 0; i < n; i++) {
        const ang = (i / n) * Math.PI * 2 - Math.PI / 2;
        const silla = new Graphics()
          .roundRect(-18, -11, 36, 22, 7)
          .fill(sillaColor)
          .stroke({ color: 0xfff7ec, width: 3 });
        silla.position.set(Math.cos(ang) * 175, Math.sin(ang) * 75);
        mesa.addChild(silla);
      }
    }
    mesa.position.set(cx, cy);
    this.hotspot(mesa, "mesa-amigos");
    this.salaLayer.addChild(mesa);

    // ── Chips de slot ──
    if (!decor) return; // sin datos aún: solo la mesa
    const idxBySubcat = new Map<string, number>();
    for (const slot of decor.slots) {
      const anchors = SALA_ANCHORS[slot.subcategory];
      const idx = idxBySubcat.get(slot.subcategory) ?? 0;
      idxBySubcat.set(slot.subcategory, idx + 1);
      const anchor = anchors?.[idx];
      if (!anchor) continue;

      const equipped = itemAt(slot.slot_id);
      const chip = new Container();
      if (equipped) {
        const icon = new Text({ text: equipped.emoji || "🏺", style: { fontSize: 42 } });
        icon.anchor.set(0.5);
        chip.addChild(icon);
      } else {
        const ring = new Graphics()
          .circle(0, 0, 26)
          .stroke({ color: 0xfff7ec, width: 3, alpha: 0.35 });
        const plus = new Text({
          text: "+",
          style: { fontSize: 30, fill: 0xfff7ec, fontWeight: "700" },
        });
        plus.anchor.set(0.5);
        plus.alpha = 0.4;
        chip.addChild(ring, plus);
      }
      chip.position.set(anchor[0], anchor[1]);
      this.hotspot(chip, "decor", slot.slot_id);
      this.salaLayer.addChild(chip);
    }
  }

  private update(dt: number): void {
    if (this.destroyed) return;
    this.elapsed += dt;

    // Trajineritas meciéndose en el agua.
    for (const b of this.boats) {
      b.boat.position.y = b.baseY + Math.sin(this.elapsed * 1.4 + b.phase) * 7;
      b.boat.rotation = Math.sin(this.elapsed * 1.1 + b.phase) * 0.04;
    }

    // Partículas ambientales (Zzz / burbujas) — no en tier ligera.
    const conParticulas = this.engine.quality !== "ligera";
    for (let i = this.particles.length - 1; i >= 0; i--) {
      const p = this.particles[i];
      p.life += dt;
      p.obj.position.y -= p.vy * dt;
      p.obj.alpha = Math.max(0, 1 - p.life / p.maxLife);
      if (p.life >= p.maxLife) {
        p.obj.destroy({ children: true });
        this.particles.splice(i, 1);
      }
    }

    for (const entry of this.puppets.values()) {
      const { puppet } = entry;
      puppet.update(dt);

      if (conParticulas) {
        entry.particleTimer -= dt;
        if (entry.particleTimer <= 0) {
          if (puppet.state === "sleeping") {
            this.spawnParticle(zzzParticle(), puppet.x + 30, puppet.y - 60, 28, 2.2);
            entry.particleTimer = 1.8 + Math.random();
          } else if (puppet.state === "walking") {
            this.spawnParticle(bubbleParticle(), puppet.x - 40 * Math.sign(puppet.scale.x || 1), puppet.y - 10, 55, 1.2);
            entry.particleTimer = 0.5 + Math.random() * 0.5;
          } else {
            entry.particleTimer = 1 + Math.random();
          }
        }
      }

      if (puppet.state === "sleeping") continue;

      // Deambular: elegir destino, nadar hacia él, pausar, repetir.
      if (entry.paused > 0) {
        entry.paused -= dt;
        if (entry.paused <= 0) {
          entry.targetX = 120 + Math.random() * (W - 240);
        }
        continue;
      }
      const dx = entry.targetX - puppet.x;
      if (Math.abs(dx) < 8) {
        entry.paused = 2 + Math.random() * 4;
        if (puppet.state === "walking") puppet.setState("idle");
        continue;
      }
      if (puppet.state === "idle") puppet.setState("walking");
      const dir = Math.sign(dx);
      puppet.x += dir * WANDER_SPEED * dt;
      // El rig mira a la izquierda por defecto (cabeza en -x).
      puppet.scale.x = dir > 0 ? -1 : 1;
    }
  }

  private buildBackdrop(): void {
    const bg = new Graphics();
    // Agua en 3 bandas (atardecer en el cenote).
    // La banda superficial se tiñe según la fase lunar (plan task-84 §4).
    const lunar = this.engine.lunarPhase || 1;
    const surfaceColor = lunarSurfaceTint(lunar);
    bg.rect(PX, 0, PW, H * 0.3).fill(surfaceColor);
    bg.rect(PX, H * 0.3, PW, H * 0.4).fill(0x134e6f);
    bg.rect(PX, H * 0.7, PW, H * 0.3).fill(0x0a2540);
    // Plataformas de chinampa (2 filas de nidos + sala + embarcadero).
    for (const y of [
      NIVEL_NIDOS_ROW1_Y + 90,
      NIVEL_NIDOS_ROW2_Y + 90,
      NIVEL_SALA.bottom + 70,
      NIVEL_EMBARCADERO_Y + 90,
    ]) {
      bg.roundRect(PX + 40, y, PW - 80, 46, 22).fill(0x8b5e34).stroke({ color: 0xfff7ec, width: 4 });
    }
    // Vegetación decorativa en los laterales (solo visible en pantallas anchas).
    for (const side of [PX + 150, PX + PW - 150]) {
      for (let i = 0; i < 3; i++) {
        bg.ellipse(side + (i - 1) * 90, H * 0.72 - i * 60, 46, 90)
          .fill({ color: 0x4ade80, alpha: 0.5 });
      }
    }
    this.addChild(bg);

    const label = new Text({
      text: "🪺 El Santuario",
      style: { fontSize: 52, fill: 0xfff7ec, fontWeight: "900" },
    });
    label.anchor.set(0.5);
    label.position.set(W / 2, 160);
    this.addChild(label);
  }

  /** Trajinerita de amigo: barquita de madera con toldo y punto de presencia. */
  private buildTrajinerita(amigo: AmigoData): Container {
    const boat = new Container();
    const g = new Graphics();
    // Casco.
    g.poly([-90, 0, 90, 0, 64, 36, -64, 36]).fill(0x8b5e34).stroke({ color: 0xfff7ec, width: 4 });
    // Toldo de colores.
    g.roundRect(-70, -54, 140, 26, 10).fill(0xe4007c).stroke({ color: 0xfff7ec, width: 3 });
    g.rect(-62, -28, 8, 28).fill(0xfff7ec);
    g.rect(54, -28, 8, 28).fill(0xfff7ec);
    boat.addChild(g);

    // Punto de presencia (online/offline).
    const dot = new Graphics().circle(78, -44, 8).fill(amigo.isOnline ? 0x4ade80 : 0x6b7080);
    boat.addChild(dot);

    const tag = new Text({
      text: amigo.nickname,
      style: { fontSize: 22, fill: 0xfff7ec, fontWeight: "700" },
    });
    tag.anchor.set(0.5);
    tag.position.set(0, -76);
    boat.addChild(tag);

    // Tap → burbujas de acción ❤️/👁/🎲 sobre la trajinerita (no abre panel).
    boat.eventMode = "static";
    boat.cursor = "pointer";
    boat.on("pointertap", () => {
      gsap.fromTo(
        boat.scale,
        { x: 1, y: 1 },
        { x: 1.08, y: 1.08, duration: 0.12, yoyo: true, repeat: 1, ease: "power2.out" },
      );
      this.toggleActionBubbles(boat, amigo);
    });
    return boat;
  }

  /**
   * Burbujas de acción del embarcadero (plan §2 Macrozona 1): ❤️ like,
   * 👁 visitar la cueva, 🎲 invitar a la mesa. Cuelgan de la trajinerita
   * (se mecen con ella) y se cierran al elegir acción, al volver a tocar
   * la barquita o solas tras unos segundos.
   */
  private toggleActionBubbles(boat: Container, amigo: AmigoData): void {
    const abrir = this.actionBubblesFor !== amigo.id;
    this.closeActionBubbles();
    if (!abrir) return;

    const acciones = [
      { emoji: "❤️", kind: "amigo-like", x: -80, y: -132 },
      { emoji: "👁", kind: "amigo-visita", x: 0, y: -156 },
      { emoji: "🎲", kind: "amigo-invita", x: 80, y: -132 },
    ];
    const group = new Container();
    acciones.forEach((accion, i) => {
      const bubble = new Container();
      bubble.addChild(
        new Graphics().circle(0, 0, 34).fill(0xfff7ec).stroke({ color: 0xe4007c, width: 4 }),
      );
      const icon = new Text({ text: accion.emoji, style: { fontSize: 30 } });
      icon.anchor.set(0.5);
      bubble.addChild(icon);
      bubble.position.set(accion.x, accion.y);
      bubble.eventMode = "static";
      bubble.cursor = "pointer";
      bubble.on("pointertap", (e) => {
        e.stopPropagation(); // que no rebote al tap de la trajinerita
        this.engine.bridge.emit("hotspot", { kind: accion.kind, id: amigo.id });
        this.closeActionBubbles();
      });
      group.addChild(bubble);
      gsap.from(bubble.scale, {
        x: 0,
        y: 0,
        duration: 0.25,
        delay: i * 0.06,
        ease: "back.out(2.2)",
      });
    });
    boat.addChild(group);
    this.actionBubbles = group;
    this.actionBubblesFor = amigo.id;
    this.actionBubblesTimer = gsap.delayedCall(5, () => this.closeActionBubbles());
  }

  private closeActionBubbles(): void {
    this.actionBubblesTimer?.kill();
    this.actionBubblesTimer = null;
    if (this.actionBubbles && !this.actionBubbles.destroyed) {
      this.actionBubbles.children.forEach((b) => gsap.killTweensOf(b.scale));
      this.actionBubbles.destroy({ children: true });
    }
    this.actionBubbles = null;
    this.actionBubblesFor = null;
  }

  private hotspot(target: Container, kind: string, id?: string): void {
    target.eventMode = "static";
    target.cursor = "pointer";
    target.on("pointertap", () => {
      gsap.fromTo(
        target.scale,
        { x: 1, y: 1 },
        { x: 1.08, y: 1.08, duration: 0.12, yoyo: true, repeat: 1, ease: "power2.out" },
      );
      this.engine.bridge.emit("hotspot", { kind, id });
    });
  }

  private spawnParticle(obj: Container, x: number, y: number, vy: number, maxLife: number): void {
    obj.position.set(x, y);
    this.particleLayer.addChild(obj);
    this.particles.push({ obj, vy, life: 0, maxLife });
  }
}

function zzzParticle(): Container {
  const t = new Text({ text: "z", style: { fontSize: 30, fill: 0x9bd9e4, fontWeight: "900" } });
  t.anchor.set(0.5);
  t.rotation = -0.3 + Math.random() * 0.6;
  return t;
}

function bubbleParticle(): Container {
  const g = new Graphics()
    .circle(0, 0, 4 + Math.random() * 5)
    .stroke({ color: 0x9bd9e4, width: 2 });
  return g;
}

function toPuppetState(axo: AxolotitoData): PuppetState {
  if (axo.state === "sleeping" || axo.energy === 0) return "sleeping";
  if (axo.state === "playing") return "playing";
  return "idle";
}

/** Nido con huevo incubando: anillo de progreso (dorado cuando está listo). */
function buildNestWithEgg(x: number, y: number, egg: AxolotitoData): Container {
  const c = new Container();
  c.position.set(x, y);
  const listo = (egg.eggProgress ?? 0) >= 100;
  const nest = new Graphics().ellipse(0, 26, 56, 20).fill(0x8b5e34).stroke({ color: 0xfff7ec, width: 4 });
  const shell = new Graphics()
    .ellipse(0, 0, 32, 40)
    .fill(listo ? 0xfff3c4 : 0xfde7f0)
    .stroke({ color: listo ? 0xf5c542 : 0xfff7ec, width: 4 });
  c.addChild(nest, shell);
  const progress = Math.max(0, Math.min(100, egg.eggProgress ?? 0));
  if (progress > 0) {
    const ring = new Graphics()
      .arc(0, 0, 50, -Math.PI / 2, -Math.PI / 2 + (Math.PI * 2 * progress) / 100)
      .stroke({ color: listo ? 0xf5c542 : 0xf59e0b, width: 6 });
    c.addChild(ring);
  }
  const tag = new Text({
    text: egg.name,
    style: { fontSize: 20, fill: listo ? 0xf5c542 : 0xfff7ec, fontWeight: "700" },
  });
  tag.anchor.set(0.5);
  tag.position.set(0, 78);
  c.addChild(tag);
  return c;
}

/** Slot desbloqueado sin habitante: nido de paja vacío. */
function buildEmptyNest(x: number, y: number): Container {
  const c = new Container();
  c.position.set(x, y);
  const nest = new Graphics()
    .ellipse(0, 26, 56, 20)
    .fill(0x8b5e34)
    .stroke({ color: 0xfff7ec, width: 4 })
    .ellipse(0, 22, 38, 12)
    .fill(0x6b4423);
  c.addChild(nest);
  const tag = new Text({
    text: "Nido libre",
    style: { fontSize: 18, fill: 0xcdb8a0, fontWeight: "700" },
  });
  tag.anchor.set(0.5);
  tag.position.set(0, 70);
  c.addChild(tag);
  return c;
}

/** Slot bloqueado: roca sin excavar con candado — invita a expandir la cueva. */
function buildLockedNest(x: number, y: number, levelNeeded: number): Container {
  const c = new Container();
  c.position.set(x, y);
  const rock = new Graphics()
    .ellipse(0, 8, 60, 46)
    .fill(0x3d4451)
    .stroke({ color: 0x596273, width: 4 })
    .ellipse(-18, -8, 16, 10)
    .fill(0x4a5260)
    .ellipse(20, 16, 12, 8)
    .fill(0x4a5260);
  c.addChild(rock);
  const lock = new Text({ text: "🔒", style: { fontSize: 30 } });
  lock.anchor.set(0.5);
  lock.position.set(0, 2);
  c.addChild(lock);
  const tag = new Text({
    text: `Nv. ${levelNeeded}`,
    style: { fontSize: 18, fill: 0x8a93a6, fontWeight: "700" },
  });
  tag.anchor.set(0.5);
  tag.position.set(0, 70);
  c.addChild(tag);
  return c;
}

/** Camita del axolotito nacido en este nido (plan §2: nido→camita). */
function buildCamita(x: number, y: number, name?: string, isSleeping?: boolean): Container {
  const c = new Container();
  c.position.set(x, y);
  const bed = new Graphics()
    .roundRect(-58, 0, 116, 36, 14)
    .fill(0xe4007c)
    .stroke({ color: 0xfff7ec, width: 4 })
    .roundRect(-58, -14, 34, 26, 8)
    .fill(0xfff7ec);
  c.addChild(bed);
  if (isSleeping) {
    const zzz = new Text({
      text: "💤 🦎",
      style: { fontSize: 24, fill: 0xfff7ec },
    });
    zzz.anchor.set(0.5);
    zzz.position.set(0, -18);
    c.addChild(zzz);
  }
  if (name) {
    const tag = new Text({
      text: name,
      style: { fontSize: 20, fill: 0xfff7ec, fontWeight: "700" },
    });
    tag.anchor.set(0.5);
    tag.position.set(0, 56);
    c.addChild(tag);
  }
  return c;
}
