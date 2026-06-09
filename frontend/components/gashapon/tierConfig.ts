// ── Tier configuration for Gashapon machines ────────────────────────────────────
// Extracted from Gashapon.tsx to share between machine cards and reveal sequence.

export type Tier = 'bronce' | 'plata' | 'oro';

export interface TierConfig {
  label: string;
  emoji: string;
  cost: number;
  color: string;
  glow: string;
  border: string;
  pityLimit: number;
  desc: string;
  probs: { label: string; pct: string; color: string }[];
}

export const TIER_CONFIG: Record<Tier, TierConfig> = {
  bronce: {
    label: 'Bronce', emoji: '🟠', cost: 150,
    color: '#D97706', glow: 'rgba(217,119,6,0.4)', border: 'rgba(217,119,6,0.5)',
    pityLimit: 10,
    desc: 'Cartas, accesorios y sobres. Sin webitos.',
    probs: [
      { label: '🫘 Frijolitos FRJ',  pct: '45%', color: 'text-amber-400'  },
      { label: '🃏 Carta',      pct: '35%', color: 'text-blue-400'   },
      { label: '👒 Accesorio',  pct: '12%', color: 'text-purple-400' },
      { label: '📦 Sobre Raro', pct: '5%',  color: 'text-cyan-400'   },
      { label: '✨ Carta Rara',  pct: '3%',  color: 'text-pink-400'   },
    ],
  },
  plata: {
    label: 'Plata', emoji: '⚪', cost: 500,
    color: '#94A3B8', glow: 'rgba(148,163,184,0.35)', border: 'rgba(148,163,184,0.5)',
    pityLimit: 5,
    desc: 'Balance entre riesgo y recompensa.',
    probs: [
      { label: '🫘 Frijolitos FRJ',   pct: '20%', color: 'text-amber-400'  },
      { label: '🃏 Carta Rara',  pct: '48%', color: 'text-blue-400'   },
      { label: '👒 Acc. Raro',   pct: '17%', color: 'text-purple-400' },
      { label: '📦 Sobre Raro',  pct: '8%',  color: 'text-cyan-400'   },
      { label: '✨ Carta Épica',  pct: '7%',  color: 'text-pink-400'   },
    ],
  },
  oro: {
    label: 'Oro', emoji: '🟡', cost: 2000,
    color: '#EAB308', glow: 'rgba(234,179,8,0.4)', border: 'rgba(234,179,8,0.55)',
    pityLimit: 3,
    desc: 'Máximo potencial. Alta chance de Cartas Épicas y Legendarias.',
    probs: [
      { label: '🫘 Frijolitos FRJ',   pct: '5%',  color: 'text-amber-400'  },
      { label: '🃏 Carta Épica', pct: '50%', color: 'text-blue-400'   },
      { label: '👒 Acc. Épico',  pct: '20%', color: 'text-purple-400' },
      { label: '📦 Sobre Épico', pct: '10%', color: 'text-cyan-400'   },
      { label: '✨ Carta Legendaria', pct: '15%', color: 'text-pink-400'   },
    ],
  },
};

export const TRIPLE_COST = 2250;
