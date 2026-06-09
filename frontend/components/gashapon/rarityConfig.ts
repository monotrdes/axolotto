// ── Rarity HSL palette and helpers ──────────────────────────────────────────────
// Shared by Gashapon reveal sequence and legendaries.

export type GashaRarity = 'common' | 'rare' | 'epic' | 'legendary' | 'astral';

export interface RarityStyle {
  h: number; s: number; l: number;
  label: string;
  emoji: string;
}

const RARITY_DEF: Record<GashaRarity, RarityStyle> = {
  common:    { h: 170, s: 75, l: 45, label: 'COMÚN',      emoji: '🟢' },
  rare:      { h: 195, s: 85, l: 50, label: 'RARO',       emoji: '🔷' },
  epic:      { h: 280, s: 80, l: 60, label: 'ÉPICO',      emoji: '✨' },
  legendary: { h: 45,  s: 100, l: 55, label: 'LEGENDARIO', emoji: '⭐' },
  astral:    { h: 295, s: 95, l: 65, label: 'ASTRAL',     emoji: '🌌' },
};

export const RARITY = RARITY_DEF;

/** Get the HSL color string for a rarity. */
export function rarityHsl(r: GashaRarity): string {
  const c = RARITY_DEF[r];
  return `hsl(${c.h}, ${c.s}%, ${c.l}%)`;
}

/** Get the glow/shadow color for a rarity (semi-transparent). */
export function rarityGlow(r: GashaRarity): string {
  const c = RARITY_DEF[r];
  return `hsla(${c.h}, ${c.s}%, ${c.l}%, 0.45)`;
}

/** Map a RollResult rarity string to GashaRarity. */
export function mapResultToRarity(rarityStr?: string): GashaRarity {
  switch (rarityStr?.toLowerCase()) {
    case 'legendary': return 'legendary';
    case 'epic':      return 'epic';
    case 'rare':      return 'rare';
    case 'astral':
    case 'mythic':    return 'astral';
    default:          return 'common';
  }
}
