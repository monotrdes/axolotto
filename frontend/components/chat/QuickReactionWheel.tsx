"use client";

import React, { useState, useRef, useEffect, useCallback } from "react";
import { getQuickPhrases, normalizeNature, type Nature } from "@/data/personality-config";

// ── Types ─────────────────────────────────────────────────────────────────────

interface QuickReactionWheelProps {
  send: (msg: any) => void;
  nature?: Nature | null;
  vipTier?: string | null;
  /** Disabled during active gameplay for manual players */
  disabled?: boolean;
}

const QUICK_EMOJIS = ["👍", "🔥", "😱"];

// ── Component ──────────────────────────────────────────────────────────────────

export default function QuickReactionWheel({
  send,
  nature,
  vipTier,
  disabled = false,
}: QuickReactionWheelProps) {
  const [open, setOpen] = useState(false);
  const wheelRef = useRef<HTMLDivElement>(null);

  const phrases = getQuickPhrases(nature);

  // Close on outside tap
  const handleClickOutside = useCallback((e: MouseEvent) => {
    if (wheelRef.current && !wheelRef.current.contains(e.target as Node)) {
      setOpen(false);
    }
  }, []);

  useEffect(() => {
    if (open) {
      document.addEventListener("mousedown", handleClickOutside);
      return () => document.removeEventListener("mousedown", handleClickOutside);
    }
  }, [open, handleClickOutside]);

  const handleSend = (text: string, isReaction: boolean) => {
    send({
      action: "chat_message",
      data: {
        text,
        is_reaction: isReaction,
        sticker_id: null,
        megaphone: false,
      },
    });
    setOpen(false);
  };

  // Radial positions for 6 slots
  const slots = [
    ...QUICK_EMOJIS.map((e) => ({ type: "emoji" as const, value: e })),
    ...phrases.slice(0, 3).map((p) => ({ type: "phrase" as const, value: p })),
  ];

  const radius = 64;

  return (
    <div ref={wheelRef} className="relative inline-block">
      {/* Trigger button */}
      <button
        onClick={() => !disabled && setOpen(!open)}
        disabled={disabled}
        className={`
          w-10 h-10 rounded-full flex items-center justify-center
          text-lg transition-all duration-200
          ${disabled
            ? "bg-slate-800/60 border border-slate-700/40 text-slate-600 cursor-not-allowed"
            : "bg-indigo-950/60 border border-indigo-500/30 hover:border-indigo-500/60 text-white hover:scale-110 active:scale-95 shadow-[0_0_12px_rgba(99,102,241,0.2)]"
          }
        `}
        title={disabled ? "Chat desactivado durante el juego" : "Reacciones rápidas"}
      >
        🦎
      </button>

      {/* Radial wheel */}
      {open && !disabled && (
        <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2">
          {/* Backdrop */}
          <div className="absolute inset-0 w-40 h-40 -top-4 -left-4 rounded-full bg-slate-950/40 backdrop-blur-sm border border-white/5" />

          <div className="relative w-32 h-32">
            {slots.map((slot, i) => {
              const angle = (i / slots.length) * Math.PI * 2 - Math.PI / 2;
              const x = radius * Math.cos(angle);
              const y = radius * Math.sin(angle);

              return (
                <button
                  key={`slot-${i}`}
                  onClick={() => handleSend(slot.value, slot.type === "emoji")}
                  className={`
                    absolute w-10 h-10 rounded-full
                    flex items-center justify-center
                    text-sm font-black transition-all duration-150
                    hover:scale-125 active:scale-90
                    ${slot.type === "emoji"
                      ? "bg-slate-800/80 border border-slate-600/50 text-xl hover:bg-indigo-900/60 hover:border-indigo-500/50"
                      : "bg-indigo-950/60 border border-indigo-500/30 text-[9px] text-indigo-200 hover:bg-indigo-900/80 hover:border-indigo-400/60"
                    }
                  `}
                  style={{
                    left: `calc(50% + ${x}px)`,
                    top: `calc(50% + ${y}px)`,
                    transform: "translate(-50%, -50%)",
                  }}
                >
                  {slot.value}
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
