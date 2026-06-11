import { Container, Graphics, Text, Ticker } from "pixi.js";
import gsap from "gsap";
import type { WorldEngine } from "../../engine/WorldEngine";
import { DESIGN_SPACE, PAINTED_BOUNDS } from "../zoneConfig";

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

export class TianguisScene extends Container {
  private engine: WorldEngine;
  private banners: Graphics[] = [];
  private elapsed = 0;
  private tick = (ticker: Ticker) => this.update(ticker.deltaMS / 1000);

  constructor(engine: WorldEngine) {
    super();
    this.engine = engine;
    this.buildBackdrop();
    for (const def of STALLS) this.addChild(this.buildStall(def));
    engine.app.ticker.add(this.tick);
  }

  override destroy(options?: Parameters<Container["destroy"]>[0]): void {
    this.engine.app.ticker.remove(this.tick);
    super.destroy(options);
  }

  private update(dt: number): void {
    if (this.destroyed) return;
    this.elapsed += dt;
    // Banderines de papel picado ondulando con corrientes (plan §1).
    this.banners.forEach((banner, i) => {
      banner.rotation = Math.sin(this.elapsed * 1.6 + i * 0.8) * 0.06;
    });
  }

  private buildBackdrop(): void {
    const bg = new Graphics();
    bg.rect(PX, 0, PW, H * 0.3).fill(0x1b7a8c);
    bg.rect(PX, H * 0.3, PW, H * 0.4).fill(0x134e6f);
    bg.rect(PX, H * 0.7, PW, H * 0.3).fill(0x0a2540);
    // Muelle de madera que recorre el mercado.
    bg.roundRect(PX + 40, 1400, PW - 80, 50, 24).fill(0x8b5e34).stroke({ color: 0xfff7ec, width: 4 });
    this.addChild(bg);

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
}
