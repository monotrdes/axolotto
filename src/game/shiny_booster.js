// src/game/shiny_booster.js
// Handles creation of special shiny boosters with monthly cap and unique shiny cards.

import { getMonthlyUsage, incrementMonthlyUsage } from '../data/supply_manager.js';

/**
 * Generates a special shiny booster pack.
 * @param {Object} options - Must include shinyPool (array of shiny card objects).
 * @returns {Array<Object>} pack of cards (5 shiny + others)
 */
export function generateSpecialShinyBooster(options = {}) {
  const LIMIT = 100; // monthly limit
  const used = getMonthlyUsage('specialShiny');
  if (used >= LIMIT) {
    throw new Error('Monthly special shiny booster limit reached');
  }

  const pack = [];
  const usedIds = new Set();

  const shinyPool = options.shinyPool || Array.from({ length: 54 }, (_, i) => ({ id: 2000 + i }));
  if (shinyPool.length < 5) {
    throw new Error('Insufficient shiny pool for special booster');
  }
  // Pick 5 unique shiny cards.
  const shuffled = shinyPool.sort(() => Math.random() - 0.5);
  for (let i = 0; i < 5; i++) {
    const card = { ...shuffled[i] };
    card.isShiny = true;
    card.isShinyFirstEdition = true; // mark as shiny + 1st edition
    pack.push(card);
    usedIds.add(card.id);
  }

  // Fill remaining slots (assume total pack size 10).
  const PACK_SIZE = 10;
  // Simple dummy pool for non‑shiny cards.
  const normalPool = Array.from({ length: 200 }, (_, i) => ({ id: i + 1 }));
  while (pack.length < PACK_SIZE) {
    let card;
    do {
      const idx = Math.floor(Math.random() * normalPool.length);
      card = normalPool[idx];
    } while (usedIds.has(card.id));
    usedIds.add(card.id);
    pack.push({ ...card });
  }

  // Record usage.
  incrementMonthlyUsage('specialShiny');
  return pack;
}
