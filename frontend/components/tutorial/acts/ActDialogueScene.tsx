"use client";

/**
 * ActDialogueScene — Pure dialogue act.
 * Shows a sequence of WebitoDialogue lines (tap to advance).
 * Calls onComplete() when the last line is dismissed.
 */

import React, { useState, useCallback } from "react";
import WebitoDialogue from "../WebitoDialogue";
import type { WebitoData } from "../TutorialScript";
import {
  ACT1_INTRO_LINES,
  getAct4PactoLines,
  getAct1RefreshLines,
} from "../dialogues";

export type DialogueSceneId =
  | "acto-1-presentacion"
  | "acto-4-pacto";

interface Props {
  actId: DialogueSceneId;
  webito: WebitoData;
  refreshCount?: number;
  onComplete: () => void;
}

export default function ActDialogueScene({ actId, webito, refreshCount = 0, onComplete }: Props) {
  const [lineIndex, setLineIndex] = useState(0);

  const salValue = Math.round((1 - webito.bonusStamina / 100) * 100);
  const lines: string[] = actId === "acto-1-presentacion"
    ? (refreshCount > 0 ? getAct1RefreshLines(webito.nature, refreshCount) : [...ACT1_INTRO_LINES[webito.nature]])
    : getAct4PactoLines(webito.nature, salValue);

  const handleDismiss = useCallback(() => {
    if (lineIndex < lines.length - 1) {
      console.log(`[ActDialogueScene:${actId}] línea ${lineIndex} → ${lineIndex + 1}`);
      setLineIndex(i => i + 1);
    } else {
      console.log(`[ActDialogueScene:${actId}] última línea → onComplete()`);
      onComplete();
    }
  }, [lineIndex, lines.length, onComplete, actId]);

  // Acto 4 has the energy bar at 0%
  const showEnergyBar = actId === "acto-4-pacto";

  return (
    <div className="flex flex-col items-center justify-end min-h-[60vh] gap-6 pb-4">
      {/* Webito egg visual */}
      <div
        className="text-[96px] leading-none select-none"
        aria-label="Webito"
        role="img"
        style={{
          filter: "drop-shadow(0 0 24px rgba(0,229,255,0.5))",
          animation: "axo-bob 2.2s ease-in-out infinite",
        }}
      >
        🥚
      </div>

      {/* Energy bar for Acto 4 */}
      {showEnergyBar && (
        <div className="flex flex-col items-center gap-2">
          <p className="text-[10px] font-black uppercase tracking-widest" style={{ color: "#64748b" }}>
            Energía de nacimiento
          </p>
          <div
            className="w-48 h-3 rounded-full overflow-hidden"
            style={{ background: "rgba(255,255,255,0.08)", border: "1px solid rgba(255,255,255,0.12)" }}
          >
            <div
              className="h-full rounded-full transition-all duration-500"
              style={{ width: "0%", background: "linear-gradient(90deg, #00e5ff, #818cf8)" }}
            />
          </div>
          <p className="text-[11px]" style={{ color: "#475569" }}>0 / 3 partidas</p>
        </div>
      )}

      {/* Dialogue */}
      <div className="w-full max-w-sm px-3">
        <WebitoDialogue
          key={lineIndex}
          text={lines[lineIndex]}
          speaker="webito"
          onDismiss={handleDismiss}
        />
      </div>

      {/* Line indicator dots */}
      {lines.length > 1 && (
        <div className="flex gap-1.5">
          {lines.map((_, i) => (
            <div
              key={i}
              className="w-1.5 h-1.5 rounded-full transition-all duration-200"
              style={{
                background: i === lineIndex ? "#00e5ff" : "rgba(100,116,139,0.4)",
                boxShadow: i === lineIndex ? "0 0 6px #00e5ff" : "none",
              }}
            />
          ))}
        </div>
      )}
    </div>
  );
}
