"use client";

import React, { useState, useRef, useEffect, useCallback } from "react";

export interface HoldButtonProps {
  onConfirm: () => void;
  label: React.ReactNode;
  duration?: number;       // ms, default 1000
  disabled?: boolean;
  className?: string;
  variant?: "primary" | "danger" | "teal" | "amber";
  sublabel?: string;
  style?: React.CSSProperties;   // custom container styles (background, border, etc.)
  ringColor?: string;            // SVG ring fill color (default: variant ring color)
}

// Variant color palettes (hex + rgba for ring)
const VARIANT_CONFIG: Record<
  NonNullable<HoldButtonProps["variant"]>,
  { bg: string; ring: string; ringRgba: string; text: string }
> = {
  primary: {
    bg: "linear-gradient(135deg, #E4007C, #B30062)",
    ring: "#E4007C",
    ringRgba: "rgba(228,0,124,0.8)",
    text: "#ffffff",
  },
  danger: {
    bg: "linear-gradient(135deg, #EF4444, #B91C1C)",
    ring: "#EF4444",
    ringRgba: "rgba(239,68,68,0.8)",
    text: "#ffffff",
  },
  teal: {
    bg: "linear-gradient(135deg, #2DD4BF, #0F766E)",
    ring: "#2DD4BF",
    ringRgba: "rgba(45,212,191,0.8)",
    text: "#000000",
  },
  amber: {
    bg: "linear-gradient(135deg, #F59E0B, #B45309)",
    ring: "#F59E0B",
    ringRgba: "rgba(245,158,11,0.8)",
    text: "#000000",
  },
};

export default function HoldButton({
  onConfirm,
  label,
  duration = 1000,
  disabled = false,
  className = "",
  variant = "primary",
  sublabel,
  style,
  ringColor,
}: HoldButtonProps) {
  const [progress, setProgress] = useState(0);   // 0–100
  const [holding, setHolding]   = useState(false);

  const intervalRef  = useRef<ReturnType<typeof setInterval> | null>(null);
  const confirmedRef = useRef(false);

  const colors = VARIANT_CONFIG[variant];
  const resolvedRingColor = ringColor ?? colors.ring;

  const clearTimer = useCallback(() => {
    if (intervalRef.current !== null) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  // Cleanup on unmount — prevent stale timer firing onConfirm
  useEffect(() => {
    return () => clearTimer();
  }, [clearTimer]);

  const startHold = useCallback(() => {
    if (disabled) return;
    confirmedRef.current = false;
    setHolding(true);
    setProgress(0);

    const startTime = Date.now();

    intervalRef.current = setInterval(() => {
      const elapsed = Date.now() - startTime;
      const pct = Math.min(100, (elapsed / duration) * 100);
      setProgress(pct);

      if (pct >= 100 && !confirmedRef.current) {
        confirmedRef.current = true;
        clearTimer();
        setHolding(false);
        setProgress(0);
        onConfirm();
      }
    }, 16);
  }, [disabled, duration, onConfirm, clearTimer]);

  const cancelHold = useCallback(() => {
    clearTimer();
    setHolding(false);
    setProgress(0);
  }, [clearTimer]);

  return (
    <div className={`relative inline-flex flex-col items-center select-none ${className}`}>
      <div className="relative w-full">
        {/* The button itself */}
        <button
          type="button"
          aria-label={typeof label === "string" ? label : undefined}
          disabled={disabled}
          onPointerDown={startHold}
          onPointerUp={cancelHold}
          onPointerLeave={cancelHold}
          onPointerCancel={cancelHold}
          className={[
            "relative z-10 overflow-hidden px-5 py-2.5 rounded-xl font-black text-xs uppercase tracking-wider",
            "transition-all duration-150 cursor-pointer select-none touch-none",
            "active:scale-[1.02]",
            holding ? "scale-[1.05]" : "",
            disabled ? "opacity-40 cursor-not-allowed" : "",
          ].join(" ")}
          style={{
            background: disabled ? "rgba(100,100,120,0.4)" : colors.bg,
            color: disabled ? "#9CA3AF" : colors.text,
            boxShadow: holding
              ? `0 0 20px ${colors.ringRgba}, 0 4px 12px rgba(0,0,0,0.4)`
              : "0 2px 8px rgba(0,0,0,0.3)",
            ...style,
            // Preserve scale transform from holding state — merge with any transform in style
            transform: holding ? `scale(1.05)${style?.transform ? ` ${style.transform}` : ""}` : (style?.transform ?? undefined),
          }}
        >
          {/* Horizontal progress fill — full height, grows left→right */}
          {holding && (
            <span
              className="absolute inset-y-0 left-0 z-0 pointer-events-none"
              aria-hidden="true"
              style={{
                width: `${progress}%`,
                background: "rgba(255,255,255,0.28)",
                borderRight: `2px solid ${resolvedRingColor}`,
                boxShadow: `0 0 12px ${colors.ringRgba}`,
                transition: "width 0.016s linear",
              }}
            />
          )}
          <span className="relative z-10">{label}</span>
        </button>
      </div>

      {/* Sub-label / holding micro-text */}
      {(sublabel || holding) && (
        <p
          className="mt-1 text-[9px] font-semibold tracking-wide text-center pointer-events-none"
          style={{ color: holding ? resolvedRingColor : "rgba(148,163,184,0.7)" }}
        >
          {holding ? "Suelta para cancelar" : sublabel}
        </p>
      )}
    </div>
  );
}
