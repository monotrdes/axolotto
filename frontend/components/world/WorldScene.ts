import type { AxolotitoData } from "./entities/AxolotitoSprite";
import type { DecorationItem } from "./zones/NidoZone";

export interface WorldScene {
  setAxolotitos(data: AxolotitoData[]): void;
  setCaveDecorations(caveIndex: number, decorations: DecorationItem[]): void;
  focusZone(zoneId: string): void;
}
