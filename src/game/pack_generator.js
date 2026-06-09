// src/game/pack_generator.js
// Pack generator module handling card pack creation with duplicate prevention and shiny rules.

/**
 * Generates a pack of cards based on the booster type.
 * @param {string} boosterType - "normal", "first_edition", "foil", "special_shiny"
 * @param {Object} options - optional parameters (e.g., supply manager)
 * @returns {Array<Object>} array of card objects
 */
export function generatePack(boosterType, options = {}) {
  // Placeholder card pool (IDs 1-200). In real implementation, import from data source.
  const allCards = Array.from({ length: 200 }, (_, i) => ({ id: i + 1 }));
  const pack = [];
  const usedIds = new Set();

  // Helper to get a random card not already used.
  function getRandomCard() {
    let card;
    do {
      const idx = Math.floor(Math.random() * allCards.length);
      card = allCards[idx];
    } while (usedIds.has(card.id));
    usedIds.add(card.id);
    return { ...card };
  }

  // Base pack size (e.g., 10 cards). Adjust as needed.
  const PACK_SIZE = 10;

  // Insert logic per booster type.
  switch (boosterType) {
    case "normal":
      // Normal booster: at most one shiny.
      let shinyAdded = false;
      while (pack.length < PACK_SIZE) {
        const card = getRandomCard();
        if (!shinyAdded && Math.random() < 0.05) { // 5% chance shiny
          card.isShiny = true;
          shinyAdded = true;
        }
        pack.push(card);
      }
      break;

    case "first_edition":
      // Higher shiny probability, still no duplicates.
      while (pack.length < PACK_SIZE) {
        const card = getRandomCard();
        if (Math.random() < 0.15) { // elevated chance
          card.isShiny = true;
          card.isFirstEdition = true;
          // Mark combined flag
          card.isShinyFirstEdition = true;
        }
        pack.push(card);
      }
      break;

    case "foil":
      // Foil booster: ensure at least one foil card.
      let foilAdded = false;
      while (pack.length < PACK_SIZE) {
        const card = getRandomCard();
        if (!foilAdded && Math.random() < 0.1) { // 10% chance foil
          card.isFoil = true;
          foilAdded = true;
        }
        pack.push(card);
      }
      break;

    case "special_shiny":
      // Special shiny booster: exactly 5 unique shiny cards from pool of 54.
      // Assume shinyPool is provided via options.
      const shinyPool = options.shinyPool || Array.from({ length: 54 }, (_, i) => ({ id: 1000 + i }));
      if (shinyPool.length < 5) {
        throw new Error("Insufficient shiny pool for special booster");
      }
      // Randomly pick 5 unique shiny cards.
      const shuffled = shinyPool.sort(() => Math.random() - 0.5);
      for (let i = 0; i < 5; i++) {
        const card = { ...shuffled[i] };
        card.isShiny = true;
        card.isShinyFirstEdition = true; // treat as shiny + first edition per spec
        pack.push(card);
        usedIds.add(card.id);
      }
      // Fill remaining slots with normal non‑shiny cards, respecting duplicate rule.
      while (pack.length < PACK_SIZE) {
        const card = getRandomCard();
        pack.push(card);
      }
      break;

    default:
      throw new Error(`Unknown booster type: ${boosterType}`);
  }

  return pack;
}
