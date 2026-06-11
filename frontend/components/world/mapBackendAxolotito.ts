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

/** Row del payload de GET /incubation/user/{userId} (incubation.py). */
export interface BackendIncubation {
  id?: number;
  name?: string;
  horasRestantes?: number;
  imprinting_complete?: boolean;
}

export function mapIncubationToEgg(inc: BackendIncubation, idx: number): AxolotitoData {
  const horas = inc.horasRestantes ?? 0;
  const listo = horas <= 0;
  return {
    id: `egg-${inc.id ?? idx}`,
    name: listo ? `${inc.name ?? "Webito"} ¡listo!` : `${inc.name ?? "Webito"} · ${horas}h`,
    level: 0,
    energy: 0,
    stats: { suerte: 0, ojo: 0, pila: 0, sal: 0 },
    state: "idle",
    caveIndex: idx,
    isEgg: true,
    // Sin total de horas en el payload: 100 = listo, 50 = incubando (visual).
    eggProgress: listo ? 100 : 50,
  };
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
