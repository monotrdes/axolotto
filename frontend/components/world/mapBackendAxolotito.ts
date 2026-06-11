import type { AxolotitoData } from "./entities/AxolotitoSprite";

/**
 * Mapea el row crudo del backend (GET /auth/axolotitos/{userId} — modelo
 * Axolotito de axolotito.py) al shape que consume el mundo papel picado.
 */

export interface BackendAxolotito {
  id?: number | string;
  name?: string;
  level?: number;
  energy_current?: number;
  status?: string;
  skin_color?: string;
  stat_luck?: number;
  stat_focus?: number;
  stat_stamina?: number;
  stat_salinity?: number;
}

function toPuppetVisualState(status: string | undefined, energy: number): AxolotitoData["state"] {
  if (status === "sleeping" || energy <= 0) return "sleeping";
  if (status?.startsWith("playing")) return "playing";
  return "idle";
}

export function mapBackendAxolotito(axo: BackendAxolotito, idx: number): AxolotitoData {
  const energy = Math.round(axo.energy_current ?? 100);
  return {
    id: String(axo.id ?? `axo-${idx}`),
    name: axo.name ?? `Axolotito ${idx + 1}`,
    level: axo.level ?? 1,
    energy,
    stats: {
      suerte: axo.stat_luck ?? 50,
      ojo: axo.stat_focus ?? 50,
      pila: axo.stat_stamina ?? 50,
      sal: axo.stat_salinity ?? 50,
    },
    state: toPuppetVisualState(axo.status, energy),
    caveIndex: idx,
    isEgg: false,
    skinColor: axo.skin_color,
  };
}
