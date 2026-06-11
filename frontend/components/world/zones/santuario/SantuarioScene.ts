import { Container, Graphics, Text, Ticker } from "pixi.js";
import gsap from "gsap";
import type { WorldEngine } from "../../engine/WorldEngine";
import type { AxolotitoData } from "../../entities/AxolotitoSprite";
import type { AmigoData } from "../../mapBackendAxolotito";
import type { DecorationItem } from "../NidoZone";
import { AxolotitoPuppet, type PuppetState } from "../../puppet/AxolotitoPuppet";
import { DESIGN_SPACE, PAINTED_BOUNDS } from "../zoneConfig";

/**
 * Diorama del Santuario (plan task-84 §2, Fase 1): chinampa vertical de
 * 3 niveles. Arriba: nidos (huevo → camita al eclosionar). Centro: sala de
 * estar con la Mesa de amigos. Abajo: embarcadero social (trajineras en
 * checkpoint posterior). Fondo/arte = placeholder Graphics hasta el atlas.
 */

const { w: W, h: H } = DESIGN_SPACE.santuario;
// Overscan lateral pintado (visible en pantallas anchas, plan §3.4).
const { x0: PX, w: PW } = PAINTED_BOUNDS.santuario;

// Bandas verticales de los 3 niveles (espacio de diseño 1080×1920).
const NIVEL_NIDOS_Y = 430;
const NIVEL_SALA = { top: 760, bottom: 1230 };
const NIVEL_EMBARCADERO_Y = 1500;

const NEST_SLOTS_X = [180, 420, 660, 900];
const WANDER_SPEED = 55; // px/s en espacio de diseño

// Posiciones de decoración alrededor del nido (máx 6 por cueva), esquivando
// el anillo de incubación y la etiqueta con el nombre.
const DECOR_OFFSETS: ReadonlyArray<readonly [number, number]> = [
  [-86, 34],
  [86, 34],
  [-86, -36],
  [86, -36],
  [-48, -82],
  [48, -82],
];

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

export class SantuarioScene extends Container {
  private engine: WorldEngine;
  private puppetLayer = new Container();
  private nestLayer = new Container();
  private decorLayer = new Container();
  private amigosLayer = new Container();
  private particleLayer = new Container();
  private puppets = new Map<string, PuppetEntry>();
  private decorations = new Map<number, DecorationItem[]>();
  private particles: Particle[] = [];
  private boats: BoatEntry[] = [];
  private actionBubbles: Container | null = null;
  private actionBubblesFor: string | null = null;
  private actionBubblesTimer: gsap.core.Tween | null = null;
  private elapsed = 0;
  private tick = (ticker: Ticker) => this.update(ticker.deltaMS / 1000);

  constructor(engine: WorldEngine) {
    super();
    this.engine = engine;
    this.buildBackdrop();
    this.addChild(this.nestLayer, this.decorLayer, this.amigosLayer, this.puppetLayer, this.particleLayer);
    engine.app.ticker.add(this.tick);
  }

  override destroy(options?: Parameters<Container["destroy"]>[0]): void {
    this.engine.app.ticker.remove(this.tick);
    this.closeActionBubbles();
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

  /** Sincroniza huevos y axolotitos desde los datos del backend. */
  setAxolotitos(data: AxolotitoData[]): void {
    if (this.destroyed) return;

    this.nestLayer.removeChildren().forEach((c) => c.destroy({ children: true }));
    const eggs = data.filter((a) => a.isEgg);
    const axos = data.filter((a) => !a.isEgg);

    // Nivel superior: un nido por slot — huevo si incuba, camita si su axolotito nació.
    // Tap en la cueva → panel de decoración (CuevaDecorPanel vía onCaveClick).
    NEST_SLOTS_X.forEach((x, slot) => {
      const egg = eggs.find((e) => e.caveIndex === slot) ?? eggs[slot];
      const owner = axos.find((a) => a.caveIndex === slot);
      const node = egg
        ? buildNestWithEgg(x, NIVEL_NIDOS_Y, egg)
        : buildCamita(x, NIVEL_NIDOS_Y, owner?.name);
      this.hotspot(node, "cueva", String(slot));
      this.nestLayer.addChild(node);
    });

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

  /** Decoraciones de la cueva (persistidas en localStorage hasta el endpoint backend). */
  setCaveDecorations(caveIndex: number, items: DecorationItem[]): void {
    if (this.destroyed) return;
    if (items.length > 0) this.decorations.set(caveIndex, items);
    else this.decorations.delete(caveIndex);
    this.redrawDecorations();
  }

  private redrawDecorations(): void {
    this.decorLayer.removeChildren().forEach((c) => c.destroy({ children: true }));
    for (const [slot, items] of this.decorations) {
      const x = NEST_SLOTS_X[slot];
      if (x === undefined) continue;
      items.slice(0, DECOR_OFFSETS.length).forEach((item, i) => {
        const [dx, dy] = DECOR_OFFSETS[i];
        const t = new Text({ text: item.emoji, style: { fontSize: 34 } });
        t.anchor.set(0.5);
        t.position.set(x + dx, NIVEL_NIDOS_Y + dy);
        t.rotation = -0.12 + (i % 3) * 0.12; // ligero desorden, como papel pegado a mano
        this.decorLayer.addChild(t);
      });
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
    // Agua en 3 bandas (atardecer en el cenote) — pintada con overscan lateral.
    bg.rect(PX, 0, PW, H * 0.3).fill(0x1b7a8c);
    bg.rect(PX, H * 0.3, PW, H * 0.4).fill(0x134e6f);
    bg.rect(PX, H * 0.7, PW, H * 0.3).fill(0x0a2540);
    // Plataformas de chinampa de los 3 niveles (se extienden al overscan).
    for (const y of [NIVEL_NIDOS_Y + 90, NIVEL_SALA.bottom + 70, NIVEL_EMBARCADERO_Y + 90]) {
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

    // Mesa de amigos al centro de la sala (hotspot funcional — plan §2).
    const mesa = new Graphics()
      .ellipse(0, 0, 130, 52)
      .fill(0xa9743f)
      .stroke({ color: 0xfff7ec, width: 5 });
    mesa.position.set(W / 2, NIVEL_SALA.bottom - 10);
    mesa.eventMode = "static";
    mesa.cursor = "pointer";
    mesa.on("pointertap", () => {
      this.engine.bridge.emit("hotspot", { kind: "mesa-amigos" });
    });
    this.addChild(mesa);

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

/** Camita del axolotito nacido en este nido (plan §2: nido→camita). */
function buildCamita(x: number, y: number, name?: string): Container {
  const c = new Container();
  c.position.set(x, y);
  const bed = new Graphics()
    .roundRect(-58, 0, 116, 36, 14)
    .fill(0xe4007c)
    .stroke({ color: 0xfff7ec, width: 4 })
    .roundRect(-58, -14, 34, 26, 8)
    .fill(0xfff7ec);
  c.addChild(bed);
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
