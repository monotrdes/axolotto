"use client";
import type { VipTierConfig } from '@/types/play';

export const VIP_TIER_CONFIG: Record<string, VipTierConfig> = {
  coral:   { emoji: "🪸", label: "CORAL",   color: "#2DD4BF", glow: "rgba(45,212,191,0.5)"  },
  dorado:  { emoji: "✨", label: "DORADO",  color: "#FBBF24", glow: "rgba(251,191,36,0.5)"  },
  axolite: { emoji: "🌟", label: "AXOLITE", color: "#C084FC", glow: "rgba(192,132,252,0.5)" },
};
