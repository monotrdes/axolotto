"use client";

import React, { useState } from "react";
import { Send, Megaphone } from "lucide-react";
import { useProductPolicy } from "@/hooks/useProductPolicy";

// ── Types ─────────────────────────────────────────────────────────────────────

interface MegaphoneButtonProps {
  frjBalance: number;
  onSendMegaphone: (text: string) => void;
  disabled?: boolean;
}

const MEGAPHONE_COST = 10;

// ── Component ──────────────────────────────────────────────────────────────────

export default function MegaphoneButton({
  frjBalance,
  onSendMegaphone,
  disabled = false,
}: MegaphoneButtonProps) {
  const { capabilities } = useProductPolicy();
  const fixedSpendingEnabled = capabilities.gameplay.fixed_spending;
  const [showInput, setShowInput] = useState(false);
  const [text, setText] = useState("");

  const canAfford = frjBalance >= MEGAPHONE_COST;
  const isDisabled = disabled || !fixedSpendingEnabled || !canAfford;

  const handleSend = () => {
    if (!fixedSpendingEnabled) return;
    const trimmed = text.trim();
    if (!trimmed) return;
    onSendMegaphone(trimmed);
    setText("");
    setShowInput(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleSend();
    }
  };

  if (showInput && fixedSpendingEnabled) {
    return (
      <div className="flex items-center gap-1.5 bg-amber-950/40 border border-amber-500/30 rounded-lg px-2 py-1.5">
        <input
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Mensaje destacado..."
          maxLength={140}
          autoFocus
          className="flex-1 bg-transparent text-xs text-amber-100 placeholder-amber-700 outline-none w-24"
        />
        <button
          onClick={handleSend}
          disabled={!text.trim()}
          className="text-amber-400 hover:text-amber-200 disabled:text-amber-700 transition-colors"
        >
          <Send size={12} />
        </button>
      </div>
    );
  }

  return (
    <button
      onClick={() => !isDisabled && fixedSpendingEnabled && setShowInput(true)}
      disabled={isDisabled}
      className="flex items-center gap-1 px-2 py-1 rounded-lg text-[10px] font-black uppercase tracking-wider
                 transition-all duration-200
                 bg-amber-950/40 border border-amber-500/30 text-amber-400
                 hover:bg-amber-900/60 hover:border-amber-400/50 hover:text-amber-200
                 disabled:bg-slate-800/40 disabled:border-slate-700/30 disabled:text-slate-600 disabled:cursor-not-allowed"
      title={
        !fixedSpendingEnabled
          ? "Megáfono en revisión"
          : !canAfford
            ? `Necesitas ${MEGAPHONE_COST} FRJ para usar el megáfono`
            : "Megáfono (10 FRJ)"
      }
    >
      <Megaphone size={10} />
      <span>{fixedSpendingEnabled ? `📢 ${MEGAPHONE_COST} FRJ` : "📢 En revisión"}</span>
    </button>
  );
}
