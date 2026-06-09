// ═══════════════════════════════════════════════════════
// HOOK — Unboxing State Machine (pack → opening → reveal → summary)
// ═══════════════════════════════════════════════════════
import { useState, useCallback } from 'react';
import type { UnboxingPhase, CardItem } from '@/types/store';

export interface UseUnboxingOptions {
  /** Called when the unboxing modal closes (e.g. to refresh inventory) */
  onClose?: (tabDestino?: string) => void;
}

export function useUnboxing({ onClose }: UseUnboxingOptions = {}) {
  const [modalAbierto, setModalAbierto] = useState(false);
  const [cartasObtenidas, setCartasObtenidas] = useState<string[]>([]);
  const [txHash, setTxHash] = useState('');
  const [cartasObtenidasObjects, setCartasObtenidasObjects] = useState<any[]>([]);

  // Unboxing phase state machine
  const [unboxingState, setUnboxingState] = useState<UnboxingPhase>('pack');
  const [currentRevealIndex, setCurrentRevealIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const [currentOpeningPack, setCurrentOpeningPack] = useState<any | null>(null);

  /**
   * Sorts cards by rarity (common → legendary), shiny cards last for suspense.
   */
  const sortCardsByRarity = useCallback((cards: any[]): any[] => {
    const rarityRank: Record<string, number> = {
      'Común': 1,
      'Poco Común': 2,
      'Rara': 3,
      'Épica': 4,
      'Legendaria': 5,
    };
    return [...cards].sort((a: any, b: any) => {
      const rA = rarityRank[a.dynamic_rarity] || 1;
      const rB = rarityRank[b.dynamic_rarity] || 1;
      if (rA === rB) {
        return (a.is_shiny ? 1 : 0) - (b.is_shiny ? 1 : 0);
      }
      return rA - rB;
    });
  }, []);

  /**
   * Initialize unboxing with sorted cards, the pack, and tx hash.
   */
  const startUnboxing = useCallback(
    (cards: any[], pack: any, tx: string) => {
      const sorted = sortCardsByRarity(cards);
      setCartasObtenidasObjects(sorted);
      setCartasObtenidas(sorted.map((c: any) => c.name));
      setTxHash(tx || '');
      setCurrentOpeningPack(pack);
      setUnboxingState('pack');
      setCurrentRevealIndex(0);
      setIsFlipped(false);
      setModalAbierto(true);
    },
    [sortCardsByRarity],
  );

  /**
   * Close unboxing modal and optionally navigate to a tab.
   */
  const cerrarModalUnboxing = useCallback(
    (tabDestino?: string) => {
      setModalAbierto(false);
      if (onClose) {
        onClose(tabDestino);
      }
    },
    [onClose],
  );

  /**
   * Reset all unboxing state back to defaults.
   */
  const resetUnboxing = useCallback(() => {
    setModalAbierto(false);
    setCartasObtenidas([]);
    setTxHash('');
    setCartasObtenidasObjects([]);
    setUnboxingState('pack');
    setCurrentRevealIndex(0);
    setIsFlipped(false);
    setCurrentOpeningPack(null);
  }, []);

  const advanceReveal = useCallback(() => {
    setCurrentRevealIndex((prev) => prev + 1);
  }, []);

  return {
    // State
    modalAbierto,
    cartasObtenidas,
    txHash,
    cartasObtenidasObjects,
    unboxingState,
    currentRevealIndex,
    isFlipped,
    currentOpeningPack,

    // Setters (for direct access when needed)
    setModalAbierto,
    setCartasObtenidas,
    setTxHash,
    setCartasObtenidasObjects,
    setUnboxingState,
    setCurrentRevealIndex,
    setIsFlipped,
    setCurrentOpeningPack,

    // Convenience actions
    startUnboxing,
    cerrarModalUnboxing,
    resetUnboxing,
    advanceReveal,
    sortCardsByRarity,
  };
}
