import { Container, Graphics, Text } from "pixi.js";
import { DESIGN_SPACE, PAINTED_BOUNDS, type MacroZoneId } from "./zoneConfig";
import type { WorldEngine } from "../engine/WorldEngine";

/**
 * Escenas placeholder de Fase 0: capas planas con la paleta "atardecer en el
 * cenote" para probar cámara, paneos y transiciones. Los dioramas reales
 * llegan en Fases 1-4 y reemplazan estos builders en el registry del
 * ZoneManager sin tocar nada más.
 */

const PALETTE = {
  aguaProfunda: 0x0a2540,
  aguaMedia: 0x134e6f,
  aguaSuperficie: 0x1b7a8c,
  bugambilia: 0xe4007c,
  cempasuchil: 0xf59e0b,
  turquesa: 0x2dd4bf,
  velaCalida: 0xffd68c,
};

const ZONE_ACCENT: Record<MacroZoneId, number> = {
  santuario: PALETTE.bugambilia,
  tianguis: PALETTE.cempasuchil,
  piramide: PALETTE.turquesa,
};

const ZONE_LABEL: Record<MacroZoneId, string> = {
  santuario: "🪺 El Santuario",
  tianguis: "🏪 El Tianguis",
  piramide: "🗿 La Pirámide",
};

export function buildPlaceholderScene(zone: MacroZoneId, _engine: WorldEngine): Container {
  const { w, h } = DESIGN_SPACE[zone];
  // El fondo se pinta con overscan lateral (pantallas anchas, plan §3.4).
  const { x0: px, w: pw } = PAINTED_BOUNDS[zone];
  const scene = new Container();

  // Capa fondo: agua profunda con degradado simulado en 3 bandas.
  const bg = new Graphics();
  bg.rect(px, 0, pw, h * 0.35).fill(PALETTE.aguaSuperficie);
  bg.rect(px, h * 0.35, pw, h * 0.35).fill(PALETTE.aguaMedia);
  bg.rect(px, h * 0.7, pw, h * 0.3).fill(PALETTE.aguaProfunda);
  scene.addChild(bg);

  // Capa media: "colinas" de papel recortado (siluetas superpuestas).
  const hills = new Graphics();
  const accent = ZONE_ACCENT[zone];
  for (let i = 0; i < Math.ceil(pw / 540); i++) {
    hills
      .circle(px + 270 + i * 540, h * 0.78, 320)
      .fill({ color: accent, alpha: 0.25 });
  }
  scene.addChild(hills);

  // Capa primer plano: "faroles" cálidos.
  const lanterns = new Graphics();
  for (let i = 0; i < Math.ceil(pw / 360); i++) {
    lanterns
      .circle(px + 180 + i * 360, h * 0.45 + (i % 2) * 120, 28)
      .fill({ color: PALETTE.velaCalida, alpha: 0.9 });
  }
  scene.addChild(lanterns);

  // Etiqueta de zona (solo placeholder; los dioramas reales no llevan texto).
  const label = new Text({
    text: ZONE_LABEL[zone],
    style: { fontSize: 64, fill: 0xffffff, fontWeight: "900" },
  });
  label.anchor.set(0.5);
  label.position.set(w / 2, h * 0.5);
  scene.addChild(label);

  // Marcadores de subzonas de la Pirámide para verificar paneos.
  if (zone === "piramide") {
    const subLabels: Array<[string, number]> = [
      ["🎰 Cámara de la Suerte", 540],
      ["🏆 Explanada", 1620],
      ["🎲 Cenote de las Salas", 2700],
    ];
    for (const [text, x] of subLabels) {
      const sub = new Text({
        text,
        style: { fontSize: 44, fill: 0xffd68c, fontWeight: "700" },
      });
      sub.anchor.set(0.5);
      sub.position.set(x, h * 0.62);
      scene.addChild(sub);
    }
  }

  return scene;
}
