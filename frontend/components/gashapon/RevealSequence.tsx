"use client";

import React, { useState } from 'react';
import type { Tier } from './tierConfig';
import type { GashaRarity } from './rarityConfig';
import CapsuleDropPhase from './CapsuleDropPhase';
import CapsuleOpenPhase from './CapsuleOpenPhase';
import PrizeRevealPhase from './PrizeRevealPhase';

// ── RollResult type ─────────────────────────────────────────────────────────────

interface RollResult {
  type?: string; name?: string; amount?: number;
  rarity?: string; description?: string;
  item_metadata?: Record<string, any>;
  guaranteed?: boolean;
  is_legendary?: boolean; legendary_type?: string;
}

// ── Props ───────────────────────────────────────────────────────────────────────

interface RevealSequenceProps {
  result: RollResult;
  tier: Tier;
  rarity: GashaRarity;
  onClose: () => void;
  closeLabel?: string;
}

type RevealPhase = 'drop' | 'open' | 'prize';

// ── Component ───────────────────────────────────────────────────────────────────

export default function RevealSequence({
  result,
  tier,
  rarity,
  onClose,
  closeLabel,
}: RevealSequenceProps) {
  const [phase, setPhase] = useState<RevealPhase>('drop');

  return (
    <div className="relative w-full max-w-sm mx-auto">
      {phase === 'drop' && (
        <CapsuleDropPhase
          tier={tier}
          rarity={rarity}
          onComplete={() => setPhase('open')}
        />
      )}
      {phase === 'open' && (
        <CapsuleOpenPhase
          rarity={rarity}
          onComplete={() => setPhase('prize')}
        />
      )}
      {phase === 'prize' && (
        <PrizeRevealPhase
          result={result}
          tier={tier}
          rarity={rarity}
          onClose={onClose}
          closeLabel={closeLabel}
        />
      )}
    </div>
  );
}
