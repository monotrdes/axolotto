"use client";

import React, { useEffect, useState, useRef } from "react";

// ── Types ─────────────────────────────────────────────────────────────────────

export interface SpeechBubbleProps {
  text: string;
  vipTier?: string | null;
  nature?: string | null;
  stickerId?: string | null;
  megaphone?: boolean;
  visible: boolean;
  /** Auto-hide duration in ms (default 3500, megaphone 6000) */
  durationMs?: number;
  onHide?: () => void;
}

// ── VIP tier styles ────────────────────────────────────────────────────────────

const VIP_BORDER: Record<string, string> = {
  coral: "border-cyan-500/40 shadow-[0_0_8px_rgba(6,182,212,0.2)]",
  dorado: "border-amber-400/50 shadow-[0_0_12px_rgba(251,191,36,0.25)] animate-shimmer",
  axolite: "border-transparent bg-gradient-to-r from-pink-400 via-purple-400 to-amber-400 bg-clip-padding !border-2 shadow-[0_0_16px_rgba(236,72,153,0.3)]",
};

const VIP_BADGE: Record<string, string> = {
  coral: "🪸",
  dorado: "✨",
  axolite: "🌟",
};

const NATURE_CLASS: Record<string, string> = {
  hyperactive: "font-bold",
  shy: "text-xs opacity-80",
  showoff: "italic",
  curious: "font-mono text-xs",
};

const NATURE_PARTICLE: Record<string, string> = {
  hyperactive: "⚡",
  shy: "💧",
  showoff: "✨",
  curious: "🔍",
};

// ── Component ──────────────────────────────────────────────────────────────────

export default function SpeechBubble({
  text,
  vipTier,
  nature,
  stickerId,
  megaphone = false,
  visible,
  durationMs,
  onHide,
}: SpeechBubbleProps) {
  const [phase, setPhase] = useState<"in" | "visible" | "out">("in");
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const defaultDuration = megaphone ? 6000 : 3500;
  const actualDuration = durationMs ?? defaultDuration;

  useEffect(() => {
    if (!visible) {
      setPhase("out");
      return () => {
        if (timerRef.current) clearTimeout(timerRef.current);
      };
    }

    // Reset phase when text changes
    setPhase("in");
    const inTimer = setTimeout(() => setPhase("visible"), 350);

    // Auto-hide
    const hideTimer = setTimeout(() => {
      setPhase("out");
      const outTimer = setTimeout(() => onHide?.(), 300);
      timerRef.current = outTimer;
    }, actualDuration + 350);

    return () => {
      clearTimeout(inTimer);
      clearTimeout(hideTimer);
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [text, visible, actualDuration, onHide]);

  if (!visible && phase === "out") return null;

  const borderClass = vipTier ? (VIP_BORDER[vipTier] ?? "") : "border-white/10";
  const badge = vipTier ? (VIP_BADGE[vipTier] ?? "") : "";
  const natureClass = nature ? (NATURE_CLASS[nature] ?? "") : "";
  const particle = nature ? (NATURE_PARTICLE[nature] ?? "") : "";

  const animClass =
    phase === "in"
      ? "animate-chat-bubble-in"
      : phase === "out"
        ? "animate-chat-bubble-out"
        : "animate-chat-bubble-float";

  return (
    <div
      className={`
        absolute -top-16 left-1/2 -translate-x-1/2 z-50
        max-w-[200px] px-3 py-1.5 rounded-2xl
        bg-slate-900/85 backdrop-blur-md border
        text-white text-xs leading-relaxed
        whitespace-normal break-words
        pointer-events-none select-none
        ${borderClass} ${animClass}
        ${megaphone ? "!text-sm !font-black !max-w-[240px] border-amber-500/80 shadow-[0_0_20px_rgba(245,158,11,0.4)]" : ""}
      `}
    >
      {/* VIP badge */}
      {badge && (
        <span className="absolute -top-2 -right-2 text-xs leading-none">
          {badge}
        </span>
      )}

      {/* Content */}
      {stickerId ? (
        <span className="text-3xl leading-none block text-center">{stickerId}</span>
      ) : (
        <span className={`line-clamp-3 ${natureClass}`}>
          {particle && <span className="mr-0.5">{particle}</span>}
          {text}
        </span>
      )}

      {/* Megaphone indicator */}
      {megaphone && (
        <span className="absolute -bottom-5 left-1/2 -translate-x-1/2 text-[9px] text-amber-400 font-black whitespace-nowrap">
          📢 Megáfono
        </span>
      )}
    </div>
  );
}
