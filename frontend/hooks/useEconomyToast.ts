"use client";

import { useState, useCallback } from "react";
import { createPortal } from "react-dom";
import React from "react";
import EconomyToast, { ToastItem, ToastVariant } from "@/components/ui/EconomyToast";
import {
  playGainSound,
  playLossSound,
  playPurchaseSound,
  playLegendarySound,
} from "@/lib/audioUtils";

let _nextId = 1;

export function useEconomyToast() {
  const [toasts, setToasts] = useState<ToastItem[]>([]);

  const dismiss = useCallback((id: number) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const show = useCallback((variant: ToastVariant, message: string) => {
    const id = _nextId++;
    setToasts((prev) => [...prev, { id, variant, message }]);
  }, []);

  const showGain = useCallback(
    (msg: string) => { playGainSound(); show("gain", msg); },
    [show]
  );

  const showLoss = useCallback(
    (msg: string) => { playLossSound(); show("loss", msg); },
    [show]
  );

  const showPurchase = useCallback(
    (msg: string) => { playPurchaseSound(); show("purchase", msg); },
    [show]
  );

  const showLegendary = useCallback(
    (msg: string) => { playLegendarySound(); show("legendary", msg); },
    [show]
  );

  // JSX value (not a component function) — stable identity across renders so
  // React never unmounts/remounts the portal and its child toasts.
  // Consumer writes: {ToastContainer}  (no angle brackets, no parens)
  const ToastContainer =
    typeof document !== "undefined"
      ? createPortal(
          React.createElement(EconomyToast, { toasts, onDismiss: dismiss }),
          document.body
        )
      : null;

  return {
    toasts,
    showGain,
    showLoss,
    showPurchase,
    showLegendary,
    ToastContainer,
  };
}
