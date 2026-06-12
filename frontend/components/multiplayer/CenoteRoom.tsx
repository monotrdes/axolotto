"use client";

import React, { useCallback, useEffect, useRef, useState } from "react";
import CenoteBackground from "./CenoteBackground";
import CircularTable from "./CircularTable";
import TableSeat from "./TableSeat";
import QuickReactionWheel from "../chat/QuickReactionWheel";
import CasiCanto from "./CasiCanto";
import { PAPER_WORLD } from "@/lib/paperWorld";
import type { TensionLevel } from "../ui/TensionEffects";
import GritonCharacter from "./GritonCharacter";

// ── Types ─────────────────────────────────────────────────────────────────────

export interface ChatBubbleData {
  text: string;
  vipTier?: string | null;
  nature?: string | null;
  stickerId?: string | null;
  megaphone?: boolean;
  visible: boolean;
}

interface SeatInfo {
  index: number;
  axoName: string;
  nature?: import("@/data/personality-config").Nature | null;
  reaction?: string;
  isPlayer?: boolean;
  isNPC?: boolean;
  isHot?: boolean;
  /** Rendered content node */
  content?: React.ReactNode;
}

interface CenoteRoomProps {
  /** Game screen content (boards, banners, action bar) */
  children: React.ReactNode;
  /** Number of active players around table (2-8) */
  playerCount: number;
  /** Tension level for water-depth overlay + table glow */
  tensionLevel: TensionLevel;
  /** Game mode */
  mode: "auto" | "manual";
  /** Seat configuration (if provided, overrides default empty seats) */
  seats?: SeatInfo[];
  /** Table diameter in px */
  tableDiameter?: number;
  /** Chat messages keyed by seat index */
  chatBubbles?: Map<number, ChatBubbleData>;
  /** Called when a chat bubble expires */
  onBubbleHide?: (seatIndex: number) => void;
  /** WebSocket send function for the QuickReactionWheel */
  chatSend?: ((msg: any) => void) | null;
  /** Chat disabled (during active manual game) */
  chatDisabled?: boolean;
  /** Player VIP tier */
  playerVipTier?: string | null;
  /** Player nature */
  playerNature?: import("@/data/personality-config").Nature | null;
  /** Current card called (for GritonCharacter) */
  currentCard?: any;
  /** Card catalog */
  allCards?: any[];
}

// ── Tension → water depth CSS custom property mapping ─────────────────────────

const WATER_DEPTH_MAP: Record<TensionLevel, number> = {
  low:      0.08,
  medium:   0.15,
  high:     0.25,
  critical: 0.35,
};

// ── Component ─────────────────────────────────────────────────────────────────

export default function CenoteRoom({
  children,
  playerCount,
  tensionLevel = "low",
  mode,
  seats,
  tableDiameter = 440,
  chatBubbles,
  onBubbleHide,
  chatSend,
  chatDisabled = false,
  playerVipTier,
  playerNature,
  currentCard = null,
  allCards = [],
}: CenoteRoomProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [mouseX, setMouseX] = useState(0);
  const [mouseY, setMouseY] = useState(0);

  // Water depth CSS custom property value
  const waterDepth = WATER_DEPTH_MAP[tensionLevel] ?? 0.08;

  // Mouse parallax tracking (relative to container center)
  const handleMouseMove = useCallback((e: React.MouseEvent<HTMLDivElement>) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    // Values range from roughly -1 to +1 based on distance from center
    setMouseX((e.clientX - centerX) / (rect.width / 2));
    setMouseY((e.clientY - centerY) / (rect.height / 2));
  }, []);

  const handleMouseLeave = useCallback(() => {
    setMouseX(0);
    setMouseY(0);
  }, []);

  // Generate seats if not provided
  const resolvedSeats: SeatInfo[] = React.useMemo(() => {
    if (seats) return seats;
    const clamped = Math.max(2, Math.min(8, playerCount));
    return Array.from({ length: clamped }, (_, i) => ({
      index: i,
      axoName: "",
      nature: null,
      isPlayer: i === 0,
      isHot: false,
    }));
  }, [seats, playerCount]);

  // Number of players around the table
  const seatCount = resolvedSeats.length;

  return (
    <div
      ref={containerRef}
      className="relative w-full h-full overflow-hidden rounded-3xl"
      style={{
        // Set CSS custom property for water depth
        "--water-depth": waterDepth,
        minHeight: "520px",
      } as React.CSSProperties}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
    >
      {/* ── Background layers (z-index 0) ───────────────────────────────── */}
      <CenoteBackground mouseX={mouseX} mouseY={mouseY} />

      {/* ── Circular table (z-index 1) ──────────────────────────────────── */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none" style={{ zIndex: 1 }}>
        <CircularTable diameter={tableDiameter} tensionLevel={tensionLevel}>
          <div className="pointer-events-auto">
            <GritonCharacter
              currentCard={currentCard}
              isUrgent={tensionLevel === "high" || tensionLevel === "critical"}
              tensionLevel={tensionLevel}
              allCards={allCards}
            />
          </div>
        </CircularTable>
      </div>

      {/* ── Table seats (z-index 2) ──────────────────────────────────────── */}
      <div className="absolute inset-0" style={{ zIndex: 2 }}>
        {resolvedSeats.map((seat) => {
          const bubble = chatBubbles?.get(seat.index);
          return (
            <TableSeat
              key={`seat-${seat.index}`}
              index={seat.index}
              total={seatCount}
              tableRadius={tableDiameter / 2}
              axoName={seat.axoName}
              nature={seat.nature}
              reaction={seat.reaction}
              isPlayer={seat.isPlayer}
              isNPC={seat.isNPC}
              isHot={seat.isHot}
              speechBubble={bubble ? {
                text: bubble.text,
                vipTier: bubble.vipTier,
                nature: bubble.nature,
                stickerId: bubble.stickerId,
                megaphone: bubble.megaphone,
                visible: bubble.visible,
              } : null}
              onSpeechBubbleHide={() => onBubbleHide?.(seat.index)}
            >
              {seat.content}
              {/* Quick Reaction Wheel trigger on player's seat */}
              {seat.isPlayer && chatSend && (
                <div className="absolute -right-2 -top-2 z-50">
                  <QuickReactionWheel
                    send={chatSend}
                    nature={seat.nature ?? playerNature ?? "hyperactive"}
                    vipTier={playerVipTier}
                    disabled={chatDisabled}
                  />
                </div>
              )}
            </TableSeat>
          );
        })}
      </div>

      {/* ── Game content overlay (z-index 3) — boards, banners, action bar */}
      <div className="relative" style={{ zIndex: 3 }}>
        {children}
      </div>

      {/* ── Water depth overlay (z-index 4) — intensifies with tension ──── */}
      <div
        className="absolute inset-0 pointer-events-none transition-opacity duration-700"
        style={{
          zIndex: 4,
          background: `
            radial-gradient(
              ellipse at 50% 30%,
              rgba(20,60,120,${waterDepth * 0.3}) 0%,
              rgba(10,30,80,${waterDepth * 0.5}) 40%,
              rgba(5,15,50,${waterDepth * 0.7}) 100%
            )
          `,
          opacity: 0.4 + waterDepth * 1.5,
        }}
      />

      {/* ── Tension vignette (z-index 5) — visible at high/critical ────── */}
      {(tensionLevel === "high" || tensionLevel === "critical") && (
        <div
          className="absolute inset-0 pointer-events-none transition-opacity duration-500"
          style={{
            zIndex: 5,
            background: `
              radial-gradient(
                ellipse at center,
                transparent 50%,
                rgba(239,68,68,${tensionLevel === "critical" ? 0.12 : 0.06}) 100%
              )
            `,
          }}
        />
      )}

      {/* ── CasiCanto overlay (plan task-84 §5): anticipación cuando alguien está
           a 1-2 cartas de ganar ────────────────────────────────────────────── */}
      <CasiCanto
        active={
          PAPER_WORLD &&
          seats != null &&
          seats.some((s) => s.isHot) &&
          (tensionLevel === "high" || tensionLevel === "critical")
        }
        nearWinPlayerName={seats?.find((s) => s.isHot)?.axoName}
        intensity={
          tensionLevel === "critical" ? "high"
          : tensionLevel === "high" ? "medium"
          : "low"
        }
      />
    </div>
  );
}
