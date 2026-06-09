"use client";
import React, { forwardRef, useImperativeHandle, useRef, useEffect } from "react";
import type { WorldScene } from "./WorldScene";
import type { AxolotitoData } from "./entities/AxolotitoSprite";
import type { DecorationItem } from "./zones/NidoZone";

export interface GameCanvasHandle {
  setAxolotitos(data: AxolotitoData[]): void;
  setCaveDecorations(caveIndex: number, decorations: DecorationItem[]): void;
  focusZone(zoneId: string): void;
  navigateToZone(zoneId: string): void;
}

interface GameCanvasProps {
  visible?: boolean;
  onReady?: (app: unknown, scene: WorldScene) => void;
  onZoneClick?: (zoneId: string) => void;
  onCaveClick?: (caveIndex: number) => void;
  onAxolotitoClick?: (axoId: string) => void;
  onStallClick?: (stallType: string) => void;
  initialZone?: string;
}

const ZONES = [
  { id: "nido", label: "El Nido", emoji: "🏠" },
  { id: "tianguis", label: "Tianguis", emoji: "🛒" },
  { id: "sala", label: "Sala", emoji: "🎴" },
  { id: "piramide", label: "Pirámide", emoji: "🏆" },
  { id: "capsulas", label: "Cápsulas", emoji: "🎰" },
];

const GameCanvas = forwardRef<GameCanvasHandle, GameCanvasProps>(function GameCanvas(
  {
    visible = false,
    onReady,
    onZoneClick,
    onCaveClick,
    onAxolotitoClick,
    onStallClick,
    initialZone = "nido",
  },
  ref,
) {
  const sceneRef = useRef<WorldScene | null>(null);
  const canvasRef = useRef<HTMLDivElement>(null);

  useImperativeHandle(ref, () => ({
    setAxolotitos(_data: AxolotitoData[]) {
      // TODO: Phase 2 — render axolotitos in the paper world
    },
    setCaveDecorations(_caveIndex: number, _decorations: DecorationItem[]) {
      // TODO: Phase 2 — update cave decorations
    },
    focusZone(_zoneId: string) {
      // TODO: Phase 2 — camera/scroll to zone
    },
    navigateToZone(_zoneId: string) {
      // TODO: Phase 2 — animate transition to zone
    },
  }));

  useEffect(() => {
    if (!onReady) return;
    const scene: WorldScene = {
      setAxolotitos: () => {},
      setCaveDecorations: () => {},
      focusZone: () => {},
    };
    sceneRef.current = scene;
    onReady(null, scene);
  }, [onReady]);

  if (!visible) return null;

  return (
    <div
      ref={canvasRef}
      className="fixed inset-0 z-0 pointer-events-none"
      style={{ background: "transparent" }}
    >
      {/* Phase 2: 2.5D paper world rendered here */}
      <div className="absolute bottom-24 left-1/2 -translate-x-1/2 flex gap-3 pointer-events-auto">
        {ZONES.map((z) => (
          <button
            key={z.id}
            onClick={() => onZoneClick?.(z.id)}
            className={`
              px-3 py-2 rounded-xl text-xs font-bold transition-all
              border border-white/10 bg-black/40 backdrop-blur-sm
              hover:bg-white/10 hover:border-white/20
              ${z.id === initialZone ? "ring-2 ring-[#E4007C]/50 border-[#E4007C]/30" : ""}
            `}
          >
            <span className="mr-1">{z.emoji}</span>
            {z.label}
          </button>
        ))}
      </div>
    </div>
  );
});

export { GameCanvas };
export default GameCanvas;
