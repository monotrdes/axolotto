"use client";

import React, { useState, useEffect, useRef, useCallback } from 'react';

// ── Types ──────────────────────────────────────────────────────────────────────

export type Speaker = "webito" | "gritón" | "axo";

export interface WebitoDialogueProps {
  text: string;
  speaker?: Speaker;
  onDismiss?: () => void;
  autoHideMs?: number;
  mood?: "victory" | "defeat";
}

// ── Speaker config ─────────────────────────────────────────────────────────────

const SPEAKER_CONFIG: Record<Speaker, { label: string; color: string; glowColor: string }> = {
  "webito":  { label: "🥚 Webito",       color: "#00e5ff", glowColor: "rgba(0,229,255,0.35)" },
  "gritón":  { label: "📣 El Gritón",    color: "#fbbf24", glowColor: "rgba(251,191,36,0.35)" },
  "axo":     { label: "🦎 Tu Axolotito", color: "#34d399", glowColor: "rgba(52,211,153,0.35)" },
};

const TYPEWRITER_MS = 30;

// ── Component ──────────────────────────────────────────────────────────────────

export default function WebitoDialogue({
  text,
  speaker = "webito",
  onDismiss,
  autoHideMs,
  mood,
}: WebitoDialogueProps) {
  const [displayed, setDisplayed]       = useState("");
  const [finished, setFinished]         = useState(false);
  const [visible, setVisible]           = useState(true);
  const [blink, setBlink]               = useState(true);

  // Refs for stable access inside intervals/timeouts
  const textRef       = useRef(text);
  const timerRef      = useRef<ReturnType<typeof setTimeout> | null>(null);
  const autoHideRef   = useRef<ReturnType<typeof setTimeout> | null>(null);
  const charIdxRef    = useRef(0);
  const finishedRef   = useRef(false);

  const baseCfg = SPEAKER_CONFIG[speaker];
  const cfg = mood
    ? {
        ...baseCfg,
        color:      mood === "victory" ? "#34d399" : "#f87171",
        glowColor:  mood === "victory" ? "rgba(52,211,153,0.35)" : "rgba(248,113,113,0.35)",
      }
    : baseCfg;

  // Reset and restart typewriter whenever `text` changes
  useEffect(() => {
    textRef.current   = text;
    charIdxRef.current = 0;
    finishedRef.current = false;
    setDisplayed("");
    setFinished(false);
    setVisible(true);

    if (timerRef.current) clearTimeout(timerRef.current);

    const tick = () => {
      const idx = charIdxRef.current;
      if (idx >= textRef.current.length) {
        finishedRef.current = true;
        setFinished(true);
        return;
      }
      setDisplayed(textRef.current.slice(0, idx + 1));
      charIdxRef.current = idx + 1;
      timerRef.current = setTimeout(tick, TYPEWRITER_MS);
    };

    timerRef.current = setTimeout(tick, TYPEWRITER_MS);

    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [text]);

  // Auto-hide after all text is shown + autoHideMs delay
  useEffect(() => {
    if (!finished || !autoHideMs) return;
    autoHideRef.current = setTimeout(() => {
      setVisible(false);
      onDismiss?.();
    }, autoHideMs);
    return () => {
      if (autoHideRef.current) clearTimeout(autoHideRef.current);
    };
  }, [finished, autoHideMs, onDismiss]);

  // Blink cursor
  useEffect(() => {
    if (!finished) return;
    const interval = setInterval(() => setBlink(b => !b), 520);
    return () => clearInterval(interval);
  }, [finished]);

  // Tap/click handler: accelerate typewriter or advance
  const handleInteract = useCallback(() => {
    if (!finishedRef.current) {
      // Skip to end immediately
      if (timerRef.current) clearTimeout(timerRef.current);
      setDisplayed(textRef.current);
      charIdxRef.current = textRef.current.length;
      finishedRef.current = true;
      setFinished(true);
    } else {
      // Already done — dismiss
      setVisible(false);
      onDismiss?.();
    }
  }, [onDismiss]);

  if (!visible) return null;

  return (
    // Outer clickable area — full width, slides up from bottom
    <div
      role="dialog"
      aria-live="polite"
      aria-label={`Diálogo de ${cfg.label}`}
      onClick={handleInteract}
      className="relative w-full cursor-pointer select-none animate-dialogue-rise"
      style={{ animationFillMode: "both" }}
    >
      {/* Speech bubble body */}
      <div
        className="relative rounded-2xl p-4 sm:p-5"
        style={{
          background: "rgba(6,6,20,0.92)",
          border: `2px solid ${cfg.color}`,
          boxShadow: `0 0 24px ${cfg.glowColor}, inset 0 0 12px rgba(0,0,0,0.5)`,
        }}
      >
        {/* Triangle pointer — bottom center */}
        <div
          aria-hidden="true"
          className="absolute -bottom-[13px] left-1/2 -translate-x-1/2 w-0 h-0"
          style={{
            borderLeft: "12px solid transparent",
            borderRight: "12px solid transparent",
            borderTop: `12px solid ${cfg.color}`,
          }}
        />

        {/* Speaker label */}
        <p
          className="text-[10px] font-black uppercase tracking-widest mb-2"
          style={{ color: cfg.color }}
        >
          {cfg.label}
        </p>

        {/* Typewriter text */}
        <p className="text-white text-sm sm:text-base font-medium leading-relaxed min-h-[3em]">
          {displayed}
          {/* Caret while typing */}
          {!finished && (
            <span
              aria-hidden="true"
              className="inline-block w-0.5 h-4 ml-0.5 align-middle bg-current animate-pulse"
              style={{ color: cfg.color }}
            />
          )}
        </p>

        {/* "Tap to continue" indicator */}
        {finished && (
          <div
            aria-label="Toca para continuar"
            className="mt-3 flex items-center justify-end gap-1"
            style={{ opacity: blink ? 1 : 0, transition: "opacity 0.15s ease" }}
          >
            <span
              className="text-[10px] font-black uppercase tracking-widest"
              style={{ color: cfg.color }}
            >
              Toca para continuar
            </span>
            <span style={{ color: cfg.color }} aria-hidden="true">&#9660;</span>
          </div>
        )}
      </div>
    </div>
  );
}
