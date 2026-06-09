"use client";

/* ─── BoardPreview — grid 4×4 de una tabla de lotería ────────────────────────
   Úsalo en cualquier contexto donde necesites mostrar el contenido de una tabla.

   Tamaños:
     'chip'   — tarjetas 18px (xxs), gap-1    → mini-preview en el botón de tabla
     'sheet'  — tarjetas 28px (xs),  gap-1.5  → board detail sheet / bottom sheet
     'editor' — tarjetas 44px (sm),  gap-2    → vista expandida / futuro editor

   Props:
     board     — objeto con card_ids[16], any array (puede tener menos de 16 → slots vacíos)
     allCards  — catálogo de cartas para lookup por id
     size      — preset de tamaño (default 'sheet')
─────────────────────────────────────────────────────────────────────────────── */

import LoteriaCard from '@/components/ui/LoteriaCard';
import type { CardSize } from '@/components/ui/LoteriaCard';
import { deriveBoardRarity, isBoardShiny, rarityFrameClass } from '@/lib/boardRarity';

export type BoardPreviewSize = 'chip' | 'sheet' | 'editor';

interface SizeConfig {
  cardSize: CardSize;
  gap: string;
  padding: string;
}

const SIZE_CONFIG: Record<BoardPreviewSize, SizeConfig> = {
  chip:   { cardSize: 'xxs', gap: 'gap-1',   padding: 'p-1.5' },
  sheet:  { cardSize: 'xs',  gap: 'gap-1.5', padding: 'p-2'   },
  editor: { cardSize: 'sm',  gap: 'gap-2',   padding: 'p-3'   },
};

export interface BoardPreviewProps {
  board: { card_ids: (number | string)[] };
  allCards: any[];
  size?: BoardPreviewSize;
  /** Clase extra para el contenedor grid (ej: className="w-full") */
  className?: string;
}

export default function BoardPreview({
  board,
  allCards,
  size = 'sheet',
  className = '',
}: BoardPreviewProps) {
  const { cardSize, gap, padding } = SIZE_CONFIG[size];

  const cardIds = (board.card_ids || []).map((id: any) => id != null ? Number(id) : null);
  const rarity   = deriveBoardRarity(cardIds, allCards);
  const shiny    = isBoardShiny(cardIds, allCards);
  const frameClass = rarityFrameClass(rarity);

  return (
    <div className={`relative grid grid-cols-4 ${gap} bg-slate-950/60 ${padding} border ${frameClass} ${className}`}>
      {shiny && <div className="board-shiny-overlay" />}
      {Array(16).fill(null).map((_, i) => {
        const rawId  = board.card_ids?.[i];
        const cardId = rawId != null ? Number(rawId) : null;
        const card   = cardId
          ? allCards.find((c: any) => Number(c.id) === cardId || Number(c.item_id) === cardId)
          : null;

        if (card) {
          return (
            <LoteriaCard
              key={i}
              card={card}
              size={cardSize}
              showQty={false}
              isFirstEdition={card.is_first_edition}
            />
          );
        }

        // Slot vacío
        const cardPx = typeof cardSize === 'number'
          ? cardSize
          : ({ xxs: 18, xs: 28, sm: 44, md: 60, lg: 80 } as Record<string, number>)[cardSize] ?? 28;

        return (
          <div
            key={i}
            className="border border-dashed border-slate-700/40 bg-slate-900/30"
            style={{ width: cardPx, height: Math.round(cardPx * 1.5) }}
          />
        );
      })}
    </div>
  );
}
