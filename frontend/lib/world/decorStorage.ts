import type { DecorationItem } from "@/components/world/zones/NidoZone";

/**
 * Persistencia de decoraciones de cueva en localStorage (plan task-84 §8 F1).
 * El endpoint backend es una sub-tarea aparte; cuando exista, este módulo se
 * convierte en caché local y la fuente de verdad pasa al servidor.
 */

const KEY_PREFIX = "axolotto_cave_decor_";

export type CaveDecorMap = Record<number, DecorationItem[]>;

export function loadCaveDecor(userId: string): CaveDecorMap {
  if (typeof window === "undefined" || !userId) return {};
  try {
    const raw = window.localStorage.getItem(KEY_PREFIX + userId);
    return raw ? (JSON.parse(raw) as CaveDecorMap) : {};
  } catch {
    return {};
  }
}

export function saveCaveDecor(
  userId: string,
  caveIndex: number,
  items: DecorationItem[],
): void {
  if (typeof window === "undefined" || !userId) return;
  try {
    const all = loadCaveDecor(userId);
    if (items.length > 0) all[caveIndex] = items;
    else delete all[caveIndex];
    window.localStorage.setItem(KEY_PREFIX + userId, JSON.stringify(all));
  } catch {
    // Modo privado / quota llena: la decoración vive solo en la sesión.
  }
}
