"use client";

import React, { useEffect, useState } from "react";

export type ToastVariant = "gain" | "loss" | "purchase" | "legendary";

export interface ToastItem {
  id: number;
  variant: ToastVariant;
  message: string;
}

interface ToastRowProps {
  item: ToastItem;
  onDone: (id: number) => void;
}

const VARIANT_CONFIG: Record<
  ToastVariant,
  { icon: string; borderColor: string; bgColor: string; textColor: string; glowColor: string }
> = {
  gain: {
    icon: "✅",
    borderColor: "border-emerald-500",
    bgColor: "bg-emerald-950/80",
    textColor: "text-emerald-200",
    glowColor: "rgba(16,185,129,0.25)",
  },
  loss: {
    icon: "💸",
    borderColor: "border-rose-500",
    bgColor: "bg-rose-950/80",
    textColor: "text-rose-200",
    glowColor: "rgba(239,68,68,0.25)",
  },
  purchase: {
    icon: "🛒",
    borderColor: "border-blue-500",
    bgColor: "bg-blue-950/80",
    textColor: "text-blue-200",
    glowColor: "rgba(59,130,246,0.25)",
  },
  legendary: {
    icon: "⚔️",
    borderColor: "border-amber-400",
    bgColor: "bg-amber-950/80",
    textColor: "text-amber-200",
    glowColor: "rgba(245,158,11,0.25)",
  },
};

const DISMISS_MS = 2500;
const FADE_MS    = 300;

function ToastRow({ item, onDone }: ToastRowProps) {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    // Trigger slide-in on next frame
    const enterTimer = requestAnimationFrame(() => setVisible(true));

    // Start fade-out before full dismiss
    const fadeTimer = setTimeout(() => setVisible(false), DISMISS_MS - FADE_MS);

    // Remove from list after fade completes
    const doneTimer = setTimeout(() => onDone(item.id), DISMISS_MS);

    return () => {
      cancelAnimationFrame(enterTimer);
      clearTimeout(fadeTimer);
      clearTimeout(doneTimer);
    };
  // onDone is stable (useCallback in parent), item.id never changes
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const cfg = VARIANT_CONFIG[item.variant];
  const isLegendary = item.variant === "legendary";

  return (
    <div
      className={[
        "flex items-center gap-2.5 px-4 py-2.5 rounded-xl border backdrop-blur-sm",
        "text-xs font-bold shadow-lg",
        cfg.borderColor,
        cfg.bgColor,
        cfg.textColor,
        isLegendary ? "animate-pulse" : "",
        "transition-all duration-300 ease-out",
      ].join(" ")}
      style={{
        opacity: visible ? 1 : 0,
        transform: visible ? "translateY(0)" : "translateY(-10px)",
        boxShadow: `0 4px 20px ${cfg.glowColor}`,
        borderWidth: isLegendary ? "1.5px" : "1px",
      }}
      role="status"
      aria-live="polite"
    >
      <span className="text-base leading-none shrink-0">{cfg.icon}</span>
      <span className="leading-tight">{item.message}</span>
    </div>
  );
}

interface EconomyToastProps {
  toasts: ToastItem[];
  onDismiss: (id: number) => void;
}

export default function EconomyToast({ toasts, onDismiss }: EconomyToastProps) {
  if (toasts.length === 0) return null;

  return (
    <div
      className="fixed top-4 left-1/2 z-[9999] flex flex-col items-center gap-2 pointer-events-none"
      style={{ transform: "translateX(-50%)" }}
      aria-label="Notificaciones de economía"
    >
      {toasts.map((t) => (
        <ToastRow key={t.id} item={t} onDone={onDismiss} />
      ))}
    </div>
  );
}
