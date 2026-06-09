const RARITY_ORDER = ['Común', 'Poco Común', 'Rara', 'Épica', 'Legendaria'] as const;
export type BoardRarity = (typeof RARITY_ORDER)[number];

function findCard(cid: number, allCards: any[]): any | undefined {
  return allCards.find((c: any) => Number(c.id) === Number(cid) || Number(c.item_id) === Number(cid));
}

export function deriveBoardRarity(cardIds: (number | null | undefined)[], allCards: any[]): BoardRarity {
  let maxIdx = 0;
  for (const cid of cardIds) {
    if (!cid) continue;
    const card = findCard(cid, allCards);
    if (!card) continue;
    const idx = RARITY_ORDER.indexOf(card.dynamic_rarity as BoardRarity);
    if (idx > maxIdx) maxIdx = idx;
  }
  return RARITY_ORDER[maxIdx];
}

export function isBoardShiny(cardIds: (number | null | undefined)[], allCards: any[]): boolean {
  return cardIds.some((cid) => {
    if (!cid) return false;
    return findCard(cid, allCards)?.is_shiny === true;
  });
}

export function rarityFrameClass(rarity: BoardRarity): string {
  const map: Record<BoardRarity, string> = {
    'Común':      'board-frame-comun',
    'Poco Común': 'board-frame-poco-comun',
    'Rara':       'board-frame-rara',
    'Épica':      'board-frame-epica',
    'Legendaria': 'board-frame-legendaria',
  };
  return map[rarity] ?? 'board-frame-comun';
}
