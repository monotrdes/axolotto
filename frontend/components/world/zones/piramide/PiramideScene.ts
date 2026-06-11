import { Container, Graphics, Text, Ticker } from "pixi.js";
import gsap from "gsap";
import type { WorldEngine } from "../../engine/WorldEngine";
import type { AxolotitoData } from "../../entities/AxolotitoSprite";
import { AxolotitoPuppet } from "../../puppet/AxolotitoPuppet";
import { DESIGN_SPACE, lunarSurfaceTint } from "../zoneConfig";

/**
 * Diorama de la Pirámide (plan task-84 §2, macrozona 3): escena ancha con
 * 3 subzonas unidas por paneo de cámara:
 *   x 0-1080     Cámara de la Suerte (gashapones)
 *   x 1080-2160  Explanada de Rankings (pirámide + podio top-3)
 *   x 2160-3240  Cenote de las Salas (pozas Novatos/Campeón)
 */

const { w: W, h: H } = DESIGN_SPACE.piramide;

const PAPER_EDGE = 0xfff7ec;

// Centros de las 3 subzonas (layout 480 orilla | 1080 | 480 gap | 1080 | ...).
const CX_CAPSULAS = 1020;
const CX_EXPLANADA = 2580;
const CX_SALAS = 4140;

export class PiramideScene extends Container {
  private engine: WorldEngine;
  private podioLayer = new Container();
  private podioPuppets: AxolotitoPuppet[] = [];
  private tick = (ticker: Ticker) => this.update(ticker.deltaMS / 1000);

  constructor(engine: WorldEngine) {
    super();
    this.engine = engine;
    this.buildBackdrop();
    this.buildCamaraSuerte();
    this.buildExplanada();
    this.buildCenoteSalas();
    this.addChild(this.podioLayer);
    engine.app.ticker.add(this.tick);
  }

  override destroy(options?: Parameters<Container["destroy"]>[0]): void {
    this.engine.app.ticker.remove(this.tick);
    this.podioPuppets = [];
    super.destroy(options);
  }

  /** Top-3 del ranking (GET /ranking/axolotitos) parado en el podio. */
  setPodio(data: AxolotitoData[]): void {
    if (this.destroyed) return;
    this.podioLayer.removeChildren().forEach((c) => c.destroy({ children: true }));
    this.podioPuppets = [];

    // Posiciones: 🥇 centro (más alto), 🥈 izquierda, 🥉 derecha.
    const spots: Array<{ x: number; y: number; medal: string }> = [
      { x: CX_EXPLANADA, y: 1020, medal: "🥇" },
      { x: CX_EXPLANADA - 190, y: 1090, medal: "🥈" },
      { x: CX_EXPLANADA + 190, y: 1120, medal: "🥉" },
    ];
    data.slice(0, 3).forEach((axo, i) => {
      const spot = spots[i];
      const puppet = new AxolotitoPuppet(axo);
      puppet.setState("idle", true);
      puppet.position.set(spot.x, spot.y);
      this.podioLayer.addChild(puppet);
      this.podioPuppets.push(puppet);

      const tag = new Text({
        text: `${spot.medal} ${axo.name} · Nv ${axo.level}`,
        style: { fontSize: 24, fill: PAPER_EDGE, fontWeight: "800" },
      });
      tag.anchor.set(0.5);
      tag.position.set(spot.x, spot.y + 90);
      this.podioLayer.addChild(tag);
    });
  }

  private update(dt: number): void {
    if (this.destroyed) return;
    for (const puppet of this.podioPuppets) puppet.update(dt);
  }

  private buildBackdrop(): void {
    const bg = new Graphics();
    const lunar = this.engine.lunarPhase || 1;
    bg.rect(0, 0, W, H * 0.3).fill(lunarSurfaceTint(lunar));
    bg.rect(0, H * 0.3, W, H * 0.4).fill(0x134e6f);
    bg.rect(0, H * 0.7, W, H * 0.3).fill(0x0a2540);
    // Suelo de piedra continuo.
    bg.roundRect(40, 1560, W - 80, 50, 24).fill(0x6b7080).stroke({ color: PAPER_EDGE, width: 4 });

    // Decoración en orillas y tramos de agua abierta entre subzonas:
    // columnas de piedra antiguas con algas (el viaje del paneo no va vacío).
    for (const gx of [240, 1800, 3360, 4920]) {
      bg.roundRect(gx - 36, 1180, 72, 380, 10).fill(0x4d5260).stroke({ color: PAPER_EDGE, width: 3 });
      bg.roundRect(gx - 56, 1140, 112, 50, 8).fill(0x6b7080).stroke({ color: PAPER_EDGE, width: 3 });
      for (let i = 0; i < 3; i++) {
        bg.ellipse(gx - 70 + i * 70, 1540 - (i % 2) * 50, 30, 70).fill({ color: 0x4ade80, alpha: 0.45 });
      }
    }
    this.addChild(bg);
  }

  // ── Subzona central: Explanada de Rankings ────────────────────────────
  private buildExplanada(): void {
    const cx = CX_EXPLANADA;
    const piramide = new Graphics();
    // Cuerpo escalonado (4 niveles de piedra).
    const niveles: Array<[number, number, number]> = [
      [460, 1380, 200],
      [360, 1200, 180],
      [260, 1040, 160],
      [150, 900, 140],
    ];
    for (const [halfW, y, hh] of niveles) {
      piramide
        .poly([cx - halfW, y, cx + halfW, y, cx + halfW * 0.78, y - hh, cx - halfW * 0.78, y - hh])
        .fill(0x6b7080)
        .stroke({ color: PAPER_EDGE, width: 4 });
    }
    // Escalinata central.
    piramide.rect(cx - 60, 760, 120, 620).fill(0x8b8f9c).stroke({ color: PAPER_EDGE, width: 3 });
    this.addChild(piramide);
    this.makeHotspot(piramide, "podio");

    // Podio de 3 pedestales frente a la escalinata.
    const podio = new Graphics();
    podio.roundRect(cx - 60, 1080, 120, 90, 8).fill(0xf5c542).stroke({ color: PAPER_EDGE, width: 4 });
    podio.roundRect(cx - 245, 1130, 110, 60, 8).fill(0xc9ccd6).stroke({ color: PAPER_EDGE, width: 4 });
    podio.roundRect(cx + 135, 1150, 110, 50, 8).fill(0xc2410c).stroke({ color: PAPER_EDGE, width: 4 });
    this.addChild(podio);
    this.makeHotspot(podio, "podio");

    this.addTitle(cx, 300, "🏆 Explanada de la Gloria");
  }

  // ── Subzona izquierda: Cámara de la Suerte ────────────────────────────
  private buildCamaraSuerte(): void {
    const machines: Array<{ x: number; color: number; label: string }> = [
      { x: CX_CAPSULAS - 280, color: 0xc2410c, label: "Bronce" },
      { x: CX_CAPSULAS, color: 0xc9ccd6, label: "Plata" },
      { x: CX_CAPSULAS + 280, color: 0xf5c542, label: "Oro" },
    ];
    for (const m of machines) {
      const machine = new Container();
      machine.position.set(m.x, 1180);
      const g = new Graphics();
      // Cuerpo de la máquina + domo de cápsulas.
      g.roundRect(-80, -60, 160, 240, 18).fill(m.color).stroke({ color: PAPER_EDGE, width: 4 });
      g.circle(0, -110, 84).fill({ color: 0x9bd9e4, alpha: 0.85 }).stroke({ color: PAPER_EDGE, width: 4 });
      // Capsulitas dentro del domo.
      for (let i = 0; i < 5; i++) {
        g.circle(-40 + (i % 3) * 40, -130 + Math.floor(i / 3) * 38, 16).fill(
          [0xe4007c, 0x2dd4bf, 0xf59e0b, 0x4ade80, 0x9b6df0][i],
        );
      }
      // Ranura de salida.
      g.roundRect(-30, 120, 60, 34, 8).fill(0x2b2b3a);
      machine.addChild(g);

      const tag = new Text({
        text: m.label,
        style: { fontSize: 26, fill: PAPER_EDGE, fontWeight: "800" },
      });
      tag.anchor.set(0.5);
      tag.position.set(0, 212);
      machine.addChild(tag);

      this.addChild(machine);
      this.makeHotspot(machine, "gashapon");
    }
    this.addTitle(CX_CAPSULAS, 380, "🎰 Cámara de la Suerte");
  }

  // ── Subzona derecha: Cenote de las Salas ──────────────────────────────
  private buildCenoteSalas(): void {
    // Charco de Novatos: poza somera, cálida, arriba.
    const novatos = new Container();
    const ng = new Graphics()
      .ellipse(0, 0, 280, 100)
      .fill(0x2dd4bf)
      .stroke({ color: PAPER_EDGE, width: 5 });
    novatos.addChild(ng);
    const nTag = new Text({
      text: "🐣 Charco de Novatos",
      style: { fontSize: 28, fill: 0x06303a, fontWeight: "800" },
    });
    nTag.anchor.set(0.5);
    novatos.addChild(nTag);
    novatos.position.set(CX_SALAS, 960);
    this.addChild(novatos);
    this.makeHotspot(novatos, "salas");

    // Fosa del Campeón: poza abisal, profunda, abajo.
    const campeon = new Container();
    const cg = new Graphics()
      .ellipse(0, 0, 300, 110)
      .fill(0x081c33)
      .stroke({ color: 0xf5c542, width: 5 });
    campeon.addChild(cg);
    const cTag = new Text({
      text: "👑 Fosa del Campeón",
      style: { fontSize: 28, fill: 0xf5c542, fontWeight: "800" },
    });
    cTag.anchor.set(0.5);
    campeon.addChild(cTag);
    campeon.position.set(CX_SALAS, 1380);
    this.addChild(campeon);
    this.makeHotspot(campeon, "salas");

    this.addTitle(CX_SALAS, 560, "🎲 Cenote de las Salas");
  }

  // ── Helpers ───────────────────────────────────────────────────────────
  private makeHotspot(target: Container | Graphics, kind: string): void {
    target.eventMode = "static";
    target.cursor = "pointer";
    target.on("pointertap", () => {
      gsap.fromTo(
        target.scale,
        { x: 1, y: 1 },
        { x: 1.05, y: 1.05, duration: 0.12, yoyo: true, repeat: 1, ease: "power2.out" },
      );
      this.engine.bridge.emit("hotspot", { kind });
    });
  }

  private addTitle(x: number, y: number, text: string): void {
    const title = new Text({
      text,
      style: { fontSize: 44, fill: PAPER_EDGE, fontWeight: "900" },
    });
    title.anchor.set(0.5);
    title.position.set(x, y);
    this.addChild(title);
  }
}
