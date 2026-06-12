/**
 * Detección de tier de calidad gráfica (plan task-84 §7).
 * 'alta' = 6 capas + shader agua | 'media' = 4 capas sin shader | 'ligera' = 2 capas, 30fps.
 */

export type QualityTier = "alta" | "media" | "ligera";
export type QualitySetting = QualityTier | "auto";

const STORAGE_KEY = "axolotto_world_quality";

export function getQualitySetting(): QualitySetting {
  if (typeof window === "undefined") return "auto";
  const stored = window.localStorage.getItem(STORAGE_KEY);
  if (stored === "alta" || stored === "media" || stored === "ligera") return stored;
  return "auto";
}

export function setQualitySetting(setting: QualitySetting): void {
  window.localStorage.setItem(STORAGE_KEY, setting);
}

/** Heurística de hardware. Se puede degradar después midiendo frame-time real. */
export function detectQualityTier(): QualityTier {
  if (typeof window === "undefined") return "media";

  const override = getQualitySetting();
  if (override !== "auto") return override;

  if (window.matchMedia?.("(prefers-reduced-motion: reduce)").matches) {
    return "ligera";
  }

  const nav = navigator as Navigator & { deviceMemory?: number };
  const memory = nav.deviceMemory ?? 4; // GB; Safari no lo expone → asumir medio
  const cores = navigator.hardwareConcurrency ?? 4;

  if (memory >= 6 && cores >= 6) return "alta";
  if (memory >= 3 && cores >= 4) return "media";
  return "ligera";
}

export const TIER_PROFILE: Record<
  QualityTier,
  { maxParallaxLayers: number; particles: boolean; waterShader: boolean; fpsCap: number }
> = {
  alta: { maxParallaxLayers: 6, particles: true, waterShader: true, fpsCap: 60 },
  media: { maxParallaxLayers: 4, particles: true, waterShader: false, fpsCap: 60 },
  ligera: { maxParallaxLayers: 2, particles: false, waterShader: false, fpsCap: 30 },
};
