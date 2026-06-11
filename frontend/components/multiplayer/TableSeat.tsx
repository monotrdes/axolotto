"use client";

import React from "react";
import SpeechBubble, { type SpeechBubbleProps } from "../chat/SpeechBubble";

// ── Types ─────────────────────────────────────────────────────────────────────

interface TableSeatProps {
  /** Seat index (0 to total-1) */
  index: number;
  /** Total number of seats around table */
  total: number;
  /** Radius of the circular table in px */
  tableRadius: number;
  /** Axolotito name */
  axoName: string;
  /** Personality nature for animation style (6 naturalezas reales del backend) */
  nature?: import("@/data/personality-config").Nature | null;
  /** Current reaction state */
  reaction?: string;
  /** Is this the current player's seat? */
  isPlayer?: boolean;
  /** Is this an NPC/bot? (Robo-Axolote, plan task-84 §6.5) */
  isNPC?: boolean;
  /** Does this seat have a hot board (14+ marks)? */
  isHot?: boolean;
  /** Mini board or avatar content */
  children?: React.ReactNode;
  /** Speech bubble data — shown above the pedestal */
  speechBubble?: {
    text: string;
    vipTier?: string | null;
    nature?: string | null;
    stickerId?: string | null;
    megaphone?: boolean;
    visible: boolean;
  } | null;
  /** Called when speech bubble auto-hides */
  onSpeechBubbleHide?: () => void;
}

// ── Nature animation classes ──────────────────────────────────────────────────

const NATURE_CLASS: Record<string, string> = {
  methodical:   "animate-nest-idle",
  lucky:        "animate-axo-wander",
  hyperactive:  "animate-axo-bob",
  glutton:      "animate-axo-bob",
  shy:          "animate-nest-idle",
  wise:         "animate-nest-idle",
};

// ── Seat-to-axo distance (how far from table center the pedestal sits) ────────

const SEAT_RING_RADIUS_FACTOR = 1.35; // seats sit outside the table edge

// ── Component ─────────────────────────────────────────────────────────────────

export default function TableSeat({
  index,
  total,
  tableRadius,
  axoName,
  nature,
  reaction,
  isPlayer = false,
  isNPC = false,
  isHot = false,
  children,
  speechBubble,
  onSpeechBubbleHide,
}: TableSeatProps) {
  // Radial position: start from top, go clockwise
  const angle = (index / total) * Math.PI * 2 - Math.PI / 2;
  const seatRingRadius = tableRadius * SEAT_RING_RADIUS_FACTOR;

  // Position the pedestal center at the seat ring
  const x = seatRingRadius * Math.cos(angle);
  const y = seatRingRadius * Math.sin(angle);

  // Depth illusion: seats at the bottom (higher y) get higher z-index
  // Normalize y offset for z-index: -seatRingRadius to +seatRingRadius → z 1 to 50
  const zIndex = Math.round(((y + seatRingRadius) / (seatRingRadius * 2)) * 49 + 1);

  // Scale: seats at the top (furthest away visually) smaller
  // y ranges from -seatRingRadius to +seatRingRadius
  // farthest (top, y = -radius): scale 0.75
  // closest (bottom, y = +radius): scale 1.0
  const scale = 0.75 + ((y + seatRingRadius) / (seatRingRadius * 2)) * 0.25;

  // Opacity: further seats slightly dimmer
  const opacity = 0.65 + ((y + seatRingRadius) / (seatRingRadius * 2)) * 0.35;

  // Pedestal dimensions scale with seat scale
  const pedestalW = 80 * scale;
  const pedestalH = 64 * scale;

  const natureAnimClass = nature ? NATURE_CLASS[nature] ?? "" : "";

  return (
    <div
      className="absolute flex flex-col items-center"
      style={{
        left: `calc(50% + ${x}px)`,
        top: `calc(50% + ${y}px)`,
        transform: `translate(-50%, -50%) scale(${scale})`,
        zIndex: zIndex,
        opacity: opacity,
        transition: "transform 0.3s ease, opacity 0.3s ease, box-shadow 0.3s ease",
      }}
    >
      {/* Speech bubble above the seat */}
      {speechBubble && (
        <div className="relative w-full flex justify-center">
          <SpeechBubble
            text={speechBubble.text}
            vipTier={speechBubble.vipTier}
            nature={speechBubble.nature}
            stickerId={speechBubble.stickerId}
            megaphone={speechBubble.megaphone}
            visible={speechBubble.visible}
            onHide={onSpeechBubbleHide}
          />
        </div>
      )}

      {/* ── Cartón pedestal (papel picado, plan task-84 §5) ──────────── */}
      <div
        className={`
          relative flex items-center justify-center rounded-xl border-2
          transition-all duration-300
          ${natureAnimClass}
          ${isPlayer ? "border-[var(--papel-bugambilia)]/50 shadow-[0_0_12px_rgba(228,0,124,0.25)]" : "border-[var(--papel-amate-sombra)]/40"}
          ${isHot ? "animate-seat-glow" : ""}
        `}
        style={{
          width: pedestalW,
          height: pedestalH,
          background: "linear-gradient(180deg, #C49A6C 0%, #A9743F 40%, #8B5E34 100%)",
          boxShadow: isHot
            ? "0 0 18px rgba(245,158,11,0.5), inset 0 1px 0 rgba(255,247,236,0.15), 0 3px 0 rgba(0,0,0,0.2)"
            : isPlayer
              ? "0 4px 0 rgba(0,0,0,0.2), inset 0 1px 0 rgba(255,247,236,0.1)"
              : "0 3px 0 rgba(0,0,0,0.2), inset 0 1px 0 rgba(255,247,236,0.06)",
          animationDuration: isHot ? "1.2s" : "2.4s",
        }}
      >
        {/* Inner content (avatar / mini board / Robo-Axolote NPC) */}
        <div className="flex items-center justify-center w-full h-full px-1 gap-0.5">
          {children ?? (
            isNPC ? (
              <span className="text-base leading-none select-none" title="Robo-Axolote (CPU)">🤖</span>
            ) : (
              <span className="text-[9px] font-black text-[var(--papel-amate)]/50 uppercase tracking-wider select-none">
                ?
              </span>
            )
          )}
        </div>

        {/* Player highlight ring — papel bugambilia */}
        {isPlayer && (
          <div
            className="absolute inset-0 rounded-xl border-2 border-[var(--papel-bugambilia)]/30 pointer-events-none"
            style={{
              boxShadow: "0 0 8px rgba(228,0,124,0.12)",
            }}
          />
        )}

        {/* Hot indicator — papel dorado pulsante */}
        {isHot && (
          <div
            className="absolute -top-1 -right-1 w-3 h-3 rounded-full animate-pulse"
            style={{
              background: "#F59E0B",
              boxShadow: "0 0 8px rgba(245,158,11,0.6)",
            }}
          />
        )}
      </div>

      {/* Name label below pedestal */}
      {axoName && (
        <span
          className={`
            text-[8px] font-black uppercase tracking-wider mt-1
            ${isPlayer ? "text-indigo-300" : "text-slate-400"}
            ${reaction === "won" ? "text-amber-400" : ""}
          `}
          style={{
            maxWidth: pedestalW * 1.4,
            overflow: "hidden",
            textOverflow: "ellipsis",
            whiteSpace: "nowrap",
          }}
        >
          {axoName}
        </span>
      )}
    </div>
  );
}
