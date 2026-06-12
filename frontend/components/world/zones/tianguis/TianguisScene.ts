import { Container, Graphics, Text, Ticker } from "pixi.js";
import gsap from "gsap";
import type { WorldEngine } from "../../engine/WorldEngine";
import type { AxolotitoData } from "../../entities/AxolotitoSprite";
import { AxolotitoPuppet } from "../../puppet/AxolotitoPuppet";
import { RoboAxolotePuppet } from "../../puppet/RoboAxolotePuppet";
import { WanderController } from "../../puppet/wanderController";
import { SKIN_COLORS } from "../../puppet/paperParts";
import { partVariants } from "../../puppet/parts";
import { dustParticle } from "../../particles";
import { DESIGN_SPACE, PAINTED_BOUNDS, lunarSurfaceTint } from "../zoneConfig";
import { setupWaterDisplacement } from "../../engine/waterDisplacement";
import { TIER_PROFILE } from "../../engine/qualityTier";

/**
 * Diorama del Tianguis (plan task-84 §2, Fase 2): mercado flotante con 5
 * puestos interactivos. Cada tap emite un hotspot que page.tsx mapea al
 * panel HTML correspondiente. Arte placeholder Graphics hasta el atlas.
 */

const { w: W, h: H } = DESIGN_SPACE.tianguis;
const { x0: PX, w: PW } = PAINTED_BOUNDS.tianguis;

interface StallDef {
  kind: string;
  emoji: string;
  label: string;
  color: number;
  x: number;
  y: number;
}

// Hotspots → onStallClick(kind) en page.tsx ('fountain' abre el banco).
const STALLS: StallDef[] = [
  { kind: "booster", emoji: "🛍️", label: "Sobrecitos", color: 0xe4007c, x: 250, y: 820 },
  { kind: "adopcion", emoji: "🪺", label: "Adopción", color: 0x4ade80, x: 830, y: 820 },
  { kind: "fountain", emoji: "⛲", label: "Banco", color: 0x2dd4bf, x: 540, y: 1020 },
  { kind: "forja", emoji: "🔥", label: "Forja", color: 0xf59e0b, x: 250, y: 1280 },
  { kind: "p2p", emoji: "🛶", label: "Trajineras P2P", color: 0xc2410c, x: 830, y: 1280 },
];

function pick<T>(arr: T[]): T {
  return arr[Math.floor(Math.random() * arr.length)];
}

/** Paseante con piel y partes variantes al azar (escaparate de rarezas). */
function randomNpcData(i: number): AxolotitoData {
  return {
    id: `tianguis-npc-${i}`,
    name: `Paseante ${i}`,
    level: 1,
    energy: 100,
    stats: { suerte: 0, ojo: 0, pila: 0, sal: 0 },
    state: "idle",
    caveIndex: 0,
    isEgg: false,
    skinColor: pick(Object.keys(SKIN_COLORS)),
    gillType: pick(partVariants("gill")),
    eyeType: pick(partVariants("eye_open")),
    mouthType: pick(partVariants("mouth")),
    tailType: pick(partVariants("tail")),
    foreheadType: pick(partVariants("forehead")),
    limbType: pick(partVariants("limb")),
  };
}

// Banda del muelle donde pasean los NPCs (pies sobre la madera, y=1400+50).
const NPC_WALK_Y = { top: 1408, bottom: 1446 };
const NPC_WALK_SPEED = 50;

interface NpcEntry {
  puppet: AxolotitoPuppet | RoboAxolotePuppet;
  wander: WanderController;
  dustTimer: number;
}

export class TianguisScene extends Container {
  private engine: WorldEngine;
  private banners: Graphics[] = [];
  private displacement?: ReturnType<typeof setupWaterDisplacement>;
  private npcLayer = new Container();
  private npcs: NpcEntry[] = [];
  private particleLayer = new Container();
  private particles: Array<{ obj: Container; vx: number; vy: number; life: number; maxLife: number }> = [];
  private elapsed = 0;
  private tick = (ticker: Ticker) => this.update(ticker.deltaMS / 1000);

  constructor(engine: WorldEngine) {
    super();
    this.engine = engine;
    this.buildBackdrop();
    for (const def of STALLS) this.addChild(this.buildStall(def));
    this.npcLayer.sortableChildren = true;
    this.addChild(this.npcLayer, this.particleLayer);
    this.spawnNpcs();
    engine.app.ticker.add(this.tick);
  }

  override destroy(options?: Parameters<Container["destroy"]>[0]): void {
    this.engine.app.ticker.remove(this.tick);
    if (this.displacement) {
      this.displacement.destroy();
    }
    this.particles = [];
    this.npcs = [];
    super.destroy(options);
  }

  /**
   * Axolotitos ambientales paseando por el muelle — escaparate vivo de las
   * partes variantes. Cantidad por tier de calidad; en alta se suma un
   * Robo-Axolote de cuerda entre la multitud.
   */
  private spawnNpcs(): void {
    if (this.engine.quality === "ligera") return;
    const count = this.engine.quality === "alta" ? 4 : 2;
    const minX = PX + 100;
    const maxX = PX + PW - 100;
    for (let i = 0; i < count; i++) {
      this.addNpc(new AxolotitoPuppet(randomNpcData(i), true), minX, maxX);
    }
    if (this.engine.quality === "alta") {
      this.addNpc(new RoboAxolotePuppet(randomNpcData(99)), minX, maxX);
    }
    this.spawnSittingNpcs();
  }

  private addNpc(puppet: AxolotitoPuppet | RoboAxolotePuppet, minX: number, maxX: number): void {
    const y = NPC_WALK_Y.top + Math.random() * (NPC_WALK_Y.bottom - NPC_WALK_Y.top);
    puppet.position.set(minX + Math.random() * (maxX - minX), y);
    puppet.zIndex = y;
    this.npcLayer.addChild(puppet);
    this.npcs.push({
      puppet,
      wander: new WanderController(puppet, { minX, maxX, speed: NPC_WALK_SPEED }),
      dustTimer: 1 + Math.random(),
    });
  }

  private spawnSittingNpcs(): void {
    // Spawn 2 sitting NPCs around a wooden table on the wooden dock
    const tableX = PX + PW - 260; // Place towards the right side of the dock
    const tableY = 1410;
    const PAPER_EDGE = 0xfff7ec;

    const group = new Container();
    group.position.set(tableX, tableY);
    group.zIndex = tableY;

    // Stool Left
    const stoolL = new Graphics()
      .ellipse(0, 0, 18, 8).fill(0x5c3a21)
      .rect(-10, 0, 4, 18).fill(0x422817)
      .rect(6, 0, 4, 18).fill(0x422817)
      .stroke({ color: PAPER_EDGE, width: 2 });
    stoolL.position.set(-45, 10);

    // Stool Right
    const stoolR = new Graphics()
      .ellipse(0, 0, 18, 8).fill(0x5c3a21)
      .rect(-10, 0, 4, 18).fill(0x422817)
      .rect(6, 0, 4, 18).fill(0x422817)
      .stroke({ color: PAPER_EDGE, width: 2 });
    stoolR.position.set(45, 10);

    // Table
    const tableGraphics = new Graphics()
      .ellipse(0, 0, 52, 20).fill(0x5c3a21)
      .rect(-38, 0, 6, 28).fill(0x422817)
      .rect(32, 0, 6, 28).fill(0x422817)
      .stroke({ color: PAPER_EDGE, width: 2.5 });
    tableGraphics.position.set(0, 12);

    group.addChild(stoolL, stoolR, tableGraphics);
    this.npcLayer.addChild(group);

    // Sitting NPC left
    const npcDataL = randomNpcData(10);
    npcDataL.state = "sitting";
    const puppetL = new AxolotitoPuppet(npcDataL, true);
    puppetL.position.set(tableX - 45, tableY + 5);
    puppetL.scale.x = -1; // Faces right (towards table)
    puppetL.zIndex = tableY + 5;
    this.npcLayer.addChild(puppetL);
    this.npcs.push({
      puppet: puppetL,
      wander: null as any,
      dustTimer: 999999,
    });

    // Sitting NPC right
    const npcDataR = randomNpcData(11);
    npcDataR.state = "sitting";
    const puppetR = new AxolotitoPuppet(npcDataR, true);
    puppetR.position.set(tableX + 45, tableY + 5);
    puppetR.scale.x = 1; // Faces left (towards table)
    puppetR.zIndex = tableY + 5;
    this.npcLayer.addChild(puppetR);
    this.npcs.push({
      puppet: puppetR,
      wander: null as any,
      dustTimer: 999999,
    });
  }

  private update(dt: number): void {
    if (this.destroyed) return;
    this.elapsed += dt;
    if (this.displacement) {
      this.displacement.update(dt);
    }
    // Banderines de papel picado ondulando con corrientes (plan §1).
    this.banners.forEach((banner, i) => {
      banner.rotation = Math.sin(this.elapsed * 1.6 + i * 0.8) * 0.06;
    });

    // NPCs paseando por el muelle con polvito en los pasos.
    for (const npc of this.npcs) {
      npc.puppet.update(dt);
      npc.wander?.update(dt);
      npc.dustTimer -= dt;
      if (npc.dustTimer <= 0) {
        if (npc.puppet.state === "walking") {
          const dust = dustParticle();
          dust.position.set(
            npc.puppet.x + 14 * (npc.puppet.scale.x || 1),
            npc.puppet.y - 4,
          );
          this.particleLayer.addChild(dust);
          this.particles.push({ obj: dust, vx: 0, vy: 18, life: 0, maxLife: 0.6 });
          npc.dustTimer = 0.5 + Math.random() * 0.5;
        } else {
          npc.dustTimer = 0.8 + Math.random();
        }
      }
    }

    // Partículas del melting
    for (let i = this.particles.length - 1; i >= 0; i--) {
      const p = this.particles[i];
      p.life += dt;
      p.obj.position.x += p.vx * dt;
      p.obj.position.y -= p.vy * dt;
      p.obj.alpha = Math.max(0, 1 - p.life / p.maxLife);
      if (p.life >= p.maxLife) {
        p.obj.destroy({ children: true });
        this.particles.splice(i, 1);
      }
    }
  }

  private buildBackdrop(): void {
    const bg = new Graphics();
    const lunar = this.engine.lunarPhase || 1;
    bg.rect(PX, 0, PW, H * 0.3).fill(lunarSurfaceTint(lunar));
    bg.rect(PX, H * 0.3, PW, H * 0.4).fill(0x134e6f);
    bg.rect(PX, H * 0.7, PW, H * 0.3).fill(0x0a2540);
    // Muelle de madera que recorre el mercado.
    bg.roundRect(PX + 40, 1400, PW - 80, 50, 24).fill(0x8b5e34).stroke({ color: 0xfff7ec, width: 4 });
    this.addChild(bg);

    const profile = TIER_PROFILE[this.engine.quality];
    if (profile.waterShader) {
      this.displacement = setupWaterDisplacement(512, 512);
      this.addChild(this.displacement.sprite);
      bg.filters = [this.displacement.filter];
    }

    // Guirnalda de banderines de papel picado cruzando la escena.
    const guirnalda = new Container();
    const colores = [0xe4007c, 0xf59e0b, 0x2dd4bf, 0xc2410c, 0x4ade80];
    const span = PW - 120;
    const count = Math.floor(span / 90);
    for (let i = 0; i <= count; i++) {
      const x = PX + 60 + i * 90;
      const y = 560 + Math.sin((i / count) * Math.PI) * 60;
      const flag = new Graphics()
        .poly([0, 0, 56, 0, 28, 44])
        .fill(colores[i % colores.length]);
      flag.position.set(x, y);
      flag.pivot.set(28, 0);
      guirnalda.addChild(flag);
      this.banners.push(flag);
    }
    this.addChild(guirnalda);

    const label = new Text({
      text: "🏪 El Tianguis",
      style: { fontSize: 52, fill: 0xfff7ec, fontWeight: "900" },
    });
    label.anchor.set(0.5);
    label.position.set(W / 2, 160);
    this.addChild(label);
  }

  private buildStall(def: StallDef): Container {
    const stall = new Container();
    stall.position.set(def.x, def.y);

    const g = new Graphics();
    // Base del puesto (cartón) + techo de mantel.
    g.roundRect(-110, -20, 220, 110, 14).fill(0x8b5e34).stroke({ color: 0xfff7ec, width: 4 });
    g.poly([-130, -20, 130, -20, 96, -86, -96, -86]).fill(def.color).stroke({ color: 0xfff7ec, width: 4 });
    stall.addChild(g);

    const emoji = new Text({ text: def.emoji, style: { fontSize: 56 } });
    emoji.anchor.set(0.5);
    emoji.position.set(0, 34);
    stall.addChild(emoji);

    const tag = new Text({
      text: def.label,
      style: { fontSize: 26, fill: 0xfff7ec, fontWeight: "800" },
    });
    tag.anchor.set(0.5);
    tag.position.set(0, 122);
    stall.addChild(tag);

    // Interacción: rebote elástico de cartón + hotspot (plan §1).
    stall.eventMode = "static";
    stall.cursor = "pointer";
    stall.on("pointertap", () => {
      gsap.fromTo(
        stall.scale,
        { x: 1, y: 1 },
        { x: 1.08, y: 1.08, duration: 0.12, yoyo: true, repeat: 1, ease: "power2.out" },
      );
      this.engine.bridge.emit("hotspot", { kind: def.kind });
    });
    return stall;
  }

  playMeltAnimation(): void {
    const cx = 250; // x del caldero de la forja
    const cy = 1280; // y del caldero de la forja
    
    const count = this.engine.quality === "ligera" ? 0 : this.engine.quality === "media" ? 10 : 20;
    for (let i = 0; i < count; i++) {
      const pText = new Text({
        text: i % 3 === 0 ? "✨" : i % 3 === 1 ? "🔥" : "🌸",
        style: { fontSize: 18 + Math.random() * 16 }
      });
      pText.anchor.set(0.5);
      pText.position.set(cx + (Math.random() - 0.5) * 60, cy - 20);
      this.particleLayer.addChild(pText);
      this.particles.push({
        obj: pText,
        vx: (Math.random() - 0.5) * 85,
        vy: 95 + Math.random() * 135,
        life: 0,
        maxLife: 1.1 + Math.random() * 0.8
      });
    }
  }
}
