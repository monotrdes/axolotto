"use client";

import React, { useState } from "react";
import { SmilePlus } from "lucide-react";

// ── Types ─────────────────────────────────────────────────────────────────────

interface StickerShopProps {
  onSelectSticker: (stickerId: string) => void;
  ownedStickers?: string[];
  vipTier?: string | null;
}

// ── Sticker tiers ─────────────────────────────────────────────────────────────

const FREE_STICKERS = ["👋", "🎉", "❤️", "😂", "🔥", "💀"];
const CORAL_STICKERS = ["🪸", "🐠", "🎭"];
const DORADO_STICKERS = ["✨", "👑", "💎", "🌟"];
const AXOLITE_STICKERS = ["🌈", "🦄", "🏆", "💫"];

function getAllowedStickers(vipTier?: string | null): string[] {
  const stickers = [...FREE_STICKERS];
  if (vipTier === "coral" || vipTier === "dorado" || vipTier === "axolite") {
    stickers.push(...CORAL_STICKERS);
  }
  if (vipTier === "dorado" || vipTier === "axolite") {
    stickers.push(...DORADO_STICKERS);
  }
  if (vipTier === "axolite") {
    stickers.push(...AXOLITE_STICKERS);
  }
  return stickers;
}

function getRequiredTier(sticker: string): string | null {
  if (CORAL_STICKERS.includes(sticker)) return "coral";
  if (DORADO_STICKERS.includes(sticker)) return "dorado";
  if (AXOLITE_STICKERS.includes(sticker)) return "axolite";
  return null;
}

// ── Component ──────────────────────────────────────────────────────────────────

export default function StickerShop({
  onSelectSticker,
  ownedStickers = [],
  vipTier,
}: StickerShopProps) {
  const [open, setOpen] = useState(false);

  const allowed = getAllowedStickers(vipTier);
  // Show all stickers but mark locked ones
  const allStickers = [
    ...FREE_STICKERS,
    ...CORAL_STICKERS,
    ...DORADO_STICKERS,
    ...AXOLITE_STICKERS,
  ];

  return (
    <div className="relative inline-block">
      {/* Trigger */}
      <button
        onClick={() => setOpen(!open)}
        className="w-8 h-8 rounded-lg bg-slate-800/60 border border-white/5 text-slate-400
                   hover:text-white hover:border-indigo-500/30 transition-colors
                   flex items-center justify-center"
        title="Stickers"
      >
        <SmilePlus size={14} />
      </button>

      {/* Picker */}
      {open && (
        <div className="absolute bottom-full right-0 mb-2 p-2 rounded-xl
                        bg-slate-950/90 backdrop-blur-md border border-white/10
                        shadow-[0_8px_32px_rgba(0,0,0,0.5)]">
          <div className="grid grid-cols-4 gap-1">
            {allStickers.map((sticker) => {
              const isAllowed = allowed.includes(sticker);
              const requiredTier = getRequiredTier(sticker);

              return (
                <button
                  key={sticker}
                  onClick={() => {
                    if (isAllowed) {
                      onSelectSticker(sticker);
                      setOpen(false);
                    }
                  }}
                  disabled={!isAllowed}
                  className={`
                    w-10 h-10 rounded-lg flex items-center justify-center text-xl
                    transition-all duration-150
                    ${isAllowed
                      ? "hover:bg-indigo-900/40 hover:scale-110 active:scale-90 cursor-pointer"
                      : "opacity-30 cursor-not-allowed grayscale"
                    }
                  `}
                  title={
                    isAllowed
                      ? `Sticker: ${sticker}`
                      : `Desbloquea con VIP ${requiredTier}`
                  }
                >
                  {sticker}
                </button>
              );
            })}
          </div>
          {(!vipTier || vipTier === "none") && (
            <p className="text-[8px] text-slate-500 text-center mt-2">
              Hazte VIP para desbloquear más stickers
            </p>
          )}
        </div>
      )}
    </div>
  );
}
