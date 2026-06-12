"use client";

import React, { useEffect, useState, useRef, useCallback } from "react";
import { LOTERIA_EMOJI } from "../ui/LoteriaCard";

// ── Types ─────────────────────────────────────────────────────────────────────

interface GritonCardData {
  cardId?: number;
  cardNumber?: number;
  name?: string;
  turn: number;
}

interface GritonCharacterProps {
  /** Current card being called (null = idle / no active call) */
  currentCard: GritonCardData | null;
  /** Is this an urgent card (someone near win)? */
  isUrgent: boolean;
  /** Name of the player who is about to win */
  urgencyName?: string;
  /** Card catalog for resolving card numbers/names from cardId */
  allCards?: any[];
  /** Show dramatic pause ( "...") before revealing urgent card */
  showDramaticPause?: boolean;
  /** Tension level of the room */
  tensionLevel?: 'low' | 'medium' | 'high' | 'critical';
}

// ── Component ─────────────────────────────────────────────────────────────────

export default function GritonCharacter({
  currentCard,
  isUrgent,
  urgencyName,
  allCards = [],
  showDramaticPause = false,
  tensionLevel = "low",
}: GritonCharacterProps) {
  const [displayCard, setDisplayCard] = useState<GritonCardData | null>(null);
  const [isPausing, setIsPausing] = useState(false);
  const [isCalling, setIsCalling] = useState(false);
  const [idleEmoji, setIdleEmoji] = useState("🦎");
  const prevTurnRef = useRef<number | null>(null);
  const throatClearTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Resolve card info (same pattern as GritonBanner.tsx)
  const resolvedNumber =
    displayCard?.cardNumber ??
    (displayCard?.cardId
      ? allCards.find(
          (c: any) => Number(c.id) === Number(displayCard.cardId)
        )?.item_metadata?.numero_loteria
      : undefined);

  const cardName =
    displayCard?.name ??
    (displayCard?.cardId
      ? allCards.find(
          (c: any) => Number(c.id) === Number(displayCard.cardId)
        )?.name
      : undefined);

  const cardEmoji =
    resolvedNumber !== undefined ? LOTERIA_EMOJI[resolvedNumber] : "🃏";

  // ── Handle new card with optional dramatic pause ──────────────────────────

  useEffect(() => {
    if (!currentCard) return;
    if (currentCard.turn === prevTurnRef.current) return;
    prevTurnRef.current = currentCard.turn;

    setIsCalling(true);

    if (isUrgent && showDramaticPause) {
      // Dramatic pause: show "..." for 1s before revealing
      setIsPausing(true);
      setDisplayCard(null);
      const tPause = setTimeout(() => {
        setIsPausing(false);
        setDisplayCard(currentCard);
        // Keep the "calling" flag active through the pop animation
        const tAnim = setTimeout(() => setIsCalling(false), 500);
        return () => clearTimeout(tAnim);
      }, 1000);
      return () => clearTimeout(tPause);
    }

    // Normal card: reveal immediately
    setDisplayCard(currentCard);
    const tReset = setTimeout(() => setIsCalling(false), 400);
    return () => clearTimeout(tReset);
  }, [currentCard, isUrgent, showDramaticPause]);

  // ── Idle animations (throat clear, glasses adjust) ───────────────────────

  const scheduleThroatClear = useCallback(() => {
    const delay = 4000 + Math.random() * 5000; // 4-9s between idle actions
    throatClearTimer.current = setTimeout(() => {
      setIdleEmoji("😤"); // clears throat
      setTimeout(() => setIdleEmoji("🦎"), 800);
      scheduleThroatClear();
    }, delay);
  }, []);

  useEffect(() => {
    scheduleThroatClear();
    return () => {
      if (throatClearTimer.current) clearTimeout(throatClearTimer.current);
    };
  }, [scheduleThroatClear]);

  // ── Reset idle emoji based on tension level or urgency ───────────────────

  useEffect(() => {
    if (isUrgent) {
      setIdleEmoji("😳");
    } else {
      const emojiMap: Record<string, string> = {
        low: "🦎",
        medium: "🤨",
        high: "😳",
        critical: "😱",
      };
      setIdleEmoji(emojiMap[tensionLevel] || "🦎");
    }
  }, [isUrgent, tensionLevel]);

  // ── Render ───────────────────────────────────────────────────────────────

  const hasCallContent = displayCard || isPausing;
  const leanAnimClass =
    isCalling || isUrgent ? "animate-griton-lean" : "animate-griton-idle";

  return (
    <div
      className="relative h-[120px] overflow-visible pointer-events-none select-none"
      aria-label={`Gritón${currentCard ? ` — calling card turn ${currentCard.turn}` : ""}`}
    >
      {/* ── Speech bubble ───────────────────────────────────────────────────────
           Appears above the Griton with a pop animation.
           Extends above the 120px container (overflow-visible). */}
      <div
        className={`absolute z-10`}
        style={{
          bottom: "62px",
          left: "50%",
          transform: "translateX(-50%)",
          visibility: hasCallContent ? "visible" : "hidden",
        }}
      >
        <div
          className={`px-3 py-1.5 rounded-xl text-center whitespace-nowrap ${
            isUrgent
              ? "bg-gradient-to-r from-amber-900/90 to-yellow-900/90 border-2 border-amber-400/60 shadow-[0_0_16px_rgba(251,191,36,0.4)]"
              : "bg-slate-800/90 border border-white/20"
          }`}
          style={{
            animation: hasCallContent
              ? "bubble-pop-in 0.32s cubic-bezier(0.34,1.56,0.64,1) both"
              : "none",
          }}
        >
          {isPausing ? (
            /* Dramatic pause: ellipsis */
            <span className="text-lg text-amber-300 font-black tracking-[0.2em]">
              . . .
            </span>
          ) : displayCard ? (
            <>
              <span className="text-2xl leading-none">{cardEmoji}</span>
              <p
                className={`text-xs font-bold mt-0.5 leading-tight ${
                  isUrgent ? "text-amber-200" : "text-slate-200"
                }`}
              >
                {cardName ?? `#${resolvedNumber ?? "?"}`}
              </p>
              {isUrgent && urgencyName && (
                <p className="text-[7px] text-amber-400/70 font-bold mt-0.5 leading-tight">
                  {urgencyName} — a una carta
                </p>
              )}
            </>
          ) : null}
        </div>
      </div>

      {/* ── Podium de cartón (papel picado, plan task-84 §5) ──────────────── */}
      <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-20">
        <div
          className="w-full h-4 rounded-t-lg border-t-2"
          style={{
            background: "linear-gradient(180deg, #C49A6C 0%, #8B5E34 100%)",
            borderColor: "rgba(255,247,236,0.3)",
            boxShadow: "0 -2px 6px rgba(139,94,52,0.3), inset 0 1px 0 rgba(255,247,236,0.08)",
          }}
        />
      </div>

      {/* ── Griton body ───────────────────────────────────────────────────────
           Idle sway normally; leans forward when calling */}
      <div
        className={`absolute bottom-4 left-1/2 -translate-x-1/2 flex flex-col items-center ${leanAnimClass}`}
        style={{
          animationDuration: isUrgent
            ? "0.35s"
            : isCalling
              ? "0.5s"
              : tensionLevel === "critical"
                ? "1s"
                : tensionLevel === "high"
                  ? "1.8s"
                  : tensionLevel === "medium"
                    ? "2.8s"
                    : "4s",
          animationIterationCount: isCalling ? 2 : undefined,
        }}
      >
        {/* Crown (always visible) */}
        <span className="text-base leading-none mb-0.5 drop-shadow-[0_0_6px_rgba(251,191,36,0.4)]">
          👑
        </span>

        {/* Face */}
        <span
          className={`text-3xl leading-none transition-transform duration-300 ${
            isUrgent ? "scale-110" : ""
          }`}
          style={{
            filter: isUrgent
              ? "drop-shadow(0 0 6px rgba(251,191,36,0.5))"
              : undefined,
          }}
        >
          {idleEmoji}
        </span>

        {/* Gill frill decoration (subtle sway) */}
        <div className="flex justify-center gap-0.5 -mt-1">
          {[0, 1, 2].map((i) => (
            <span
              key={i}
              className="text-[8px] opacity-50"
              style={{
                display: "inline-block",
                animation: `algae-sway ${2 + i * 0.4}s ease-in-out infinite`,
                animationDelay: `${i * 0.2}s`,
              }}
            >
              🌿
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
