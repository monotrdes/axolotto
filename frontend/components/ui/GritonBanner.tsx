"use client";

import React, { useEffect, useState } from "react";
import Image from "next/image";
import { LOTERIA_EMOJI, CARD_IMAGE } from "./LoteriaCard";

// ── Types ─────────────────────────────────────────────────────────────────────

export interface GritonCard {
  cardId?: number;
  cardNumber?: number;
  /** If cardNumber is not provided, look up from allCards using cardId */
  turn: number;
  windowMs?: number;
  name?: string;
}

interface GritonBannerProps {
  /** Current card being called (null = no active card) */
  card: GritonCard | null;
  /** Total cards in deck (for progress display) */
  totalCards?: number;
  /** All cards catalog for resolving names/numbers */
  allCards?: any[];
  /** Show timer bar (manual mode) */
  showTimer?: boolean;
}

// ── Component ─────────────────────────────────────────────────────────────────

export default function GritonBanner({
  card,
  totalCards,
  allCards = [],
  showTimer = false,
}: GritonBannerProps) {
  const [elapsedPct, setElapsedPct] = useState(0); // 0..100

  // Resolve card info
  const resolvedNumber =
    card?.cardNumber ??
    (card?.cardId
      ? allCards.find((c: any) => Number(c.id) === Number(card.cardId))
          ?.item_metadata?.numero_loteria
      : undefined);

  const cardName =
    card?.name ??
    (card?.cardId
      ? allCards.find((c: any) => Number(c.id) === Number(card.cardId))?.name
      : undefined);

  const cardImg = resolvedNumber ? CARD_IMAGE[resolvedNumber] : null;
  const cardEmoji = resolvedNumber ? LOTERIA_EMOJI[resolvedNumber] : "🃏";
  const windowMs = card?.windowMs ?? 2000;

  // Timer animation
  useEffect(() => {
    if (!card || !showTimer) {
      setElapsedPct(0);
      return;
    }

    const start = Date.now();
    const total = windowMs;

    const interval = setInterval(() => {
      const pct = Math.min(100, ((Date.now() - start) / total) * 100);
      setElapsedPct(pct);
      if (pct >= 100) clearInterval(interval);
    }, 50);

    return () => clearInterval(interval);
  }, [card, showTimer, windowMs]);

  // Reset on new card
  useEffect(() => {
    setElapsedPct(0);
  }, [card?.cardId, card?.turn]);

  if (!card) {
    return (
      <div className="h-20 flex items-center justify-center">
        <p className="text-xs text-slate-600 font-black uppercase tracking-widest">
          Esperando al Gritón...
        </p>
      </div>
    );
  }

  const isUrgent = showTimer && elapsedPct > 70;
  const remainingPct = 100 - elapsedPct;

  return (
    <div className="relative overflow-hidden rounded-2xl border border-white/10 bg-slate-950/70">
      {/* Timer bar (manual mode) */}
      {showTimer && (
        <div
          className="absolute top-0 left-0 h-1 transition-colors duration-300"
          style={{
            width: `${remainingPct}%`,
            backgroundColor: isUrgent
              ? "rgb(239,68,68)" // red-500
              : elapsedPct > 40
                ? "rgb(251,191,36)" // amber-400
                : "rgb(52,211,153)", // emerald-400
          }}
        />
      )}

      <div className="flex items-center gap-3 p-3 pt-4">
        {/* Card image/emoji */}
        <div
          className={`relative shrink-0 rounded-lg overflow-hidden border ${
            isUrgent
              ? "border-red-500/50 shadow-[0_0_12px_rgba(239,68,68,0.4)]"
              : "border-indigo-500/30 shadow-[0_0_12px_rgba(99,102,241,0.25)]"
          }`}
          style={{ width: 64, height: 96 }}
        >
          {cardImg ? (
            <Image
              src={cardImg}
              alt={cardName ?? `Carta #${resolvedNumber}`}
              className="absolute inset-0 w-full h-full object-cover animate-card-call"
              draggable={false}
              fill
              sizes="64px"
            />
          ) : (
            <div
              className="absolute inset-0 flex items-center justify-center text-3xl"
              style={{
                background: `radial-gradient(110% 75% at 50% 0%, hsl(${(resolvedNumber ?? 0) * 47 % 360},75%,55%) 0%, hsl(${(resolvedNumber ?? 0) * 47 % 360},70%,30%) 55%, hsl(${(resolvedNumber ?? 0) * 47 % 360},80%,12%) 100%)`,
              }}
            >
              {cardEmoji}
            </div>
          )}
        </div>

        {/* Info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-black text-indigo-400 uppercase tracking-widest bg-indigo-950/50 px-2 py-0.5 rounded-full">
              Turno {card.turn}
            </span>
            {totalCards && (
              <span className="text-[9px] text-slate-500">
                {card.turn}/{totalCards}
              </span>
            )}
          </div>
          <h3 className="text-base font-black text-white mt-1 truncate">
            {cardName ?? `#${resolvedNumber ?? "?"}`}
          </h3>
          {resolvedNumber && (
            <p className="text-[11px] text-slate-400 font-bold mt-0.5">
              Nº {resolvedNumber}
            </p>
          )}
        </div>

        {/* Progress number */}
        <div className="text-right shrink-0">
          <span
            className={`text-2xl font-black ${
              isUrgent ? "text-red-400 animate-pulse" : "text-slate-300"
            }`}
          >
            #{resolvedNumber ?? "?"}
          </span>
          {showTimer && (
            <p className="text-[9px] text-slate-500 font-bold">
              {Math.max(0, Math.round((windowMs * remainingPct) / 100 / 100) / 10)}s
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
