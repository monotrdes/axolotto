"use client";
import React, { forwardRef, useImperativeHandle, useRef, useEffect } from "react";
import type { WorldScene } from "./WorldScene";
import type { AxolotitoData } from "./entities/AxolotitoSprite";
import type { DecorationItem } from "./zones/NidoZone";
import PaperCurtain, { type PaperCurtainHandle } from "@/components/play/PaperCurtain";
import type { WorldEngine } from "./engine/WorldEngine";
import type { ZoneManager } from "./zones/ZoneManager";
import type { SantuarioScene } from "./zones/santuario/SantuarioScene";
import type { PiramideScene } from "./zones/piramide/PiramideScene";

/**
 * Mundo 2.5D de papel picado (plan task-84). Detrás del flag
 * NEXT_PUBLIC_PAPER_WORLD=1: monta PixiJS (import dinámico — sin flag no se
 * descarga el chunk) con 3 macrozonas y cortina de papel. Sin flag, conserva
 * el comportamiento stub original intacto.
 */

const PAPER_WORLD_ENABLED = process.env.NEXT_PUBLIC_PAPER_WORLD === "1";

export interface GameCanvasHandle {
  setAxolotitos(data: AxolotitoData[]): void;
  setCaveDecorations(caveIndex: number, decorations: DecorationItem[]): void;
  focusZone(zoneId: string): void;
  navigateToZone(zoneId: string): void;
  /** Top-3 del ranking para el podio de la Pirámide (mundo papel picado). */
  setPodio?(data: AxolotitoData[]): void;
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
    onCaveClick: _onCaveClick,
    onAxolotitoClick: _onAxolotitoClick,
    onStallClick,
    initialZone = "nido",
  },
  ref,
) {
  const hostRef = useRef<HTMLDivElement>(null);
  const curtainRef = useRef<PaperCurtainHandle>(null);
  const engineRef = useRef<WorldEngine | null>(null);
  const zonesRef = useRef<ZoneManager | null>(null);
  const santuarioRef = useRef<SantuarioScene | null>(null);
  const piramideRef = useRef<PiramideScene | null>(null);
  const axolotitosRef = useRef<AxolotitoData[]>([]);
  const podioRef = useRef<AxolotitoData[]>([]);
  // Ref para evitar closures viejos dentro del listener del bridge.
  const onStallClickRef = useRef(onStallClick);
  onStallClickRef.current = onStallClick;

  useImperativeHandle(ref, () => ({
    setAxolotitos(data: AxolotitoData[]) {
      axolotitosRef.current = data;
      if (santuarioRef.current && !santuarioRef.current.destroyed) {
        santuarioRef.current.setAxolotitos(data);
      }
    },
    setCaveDecorations(_caveIndex: number, _decorations: DecorationItem[]) {
      // TODO(Fase 1): decoraciones reales en el diorama del Santuario.
    },
    focusZone(zoneId: string) {
      zonesRef.current?.navigate(zoneId, null);
    },
    navigateToZone(zoneId: string) {
      zonesRef.current?.navigate(zoneId, curtainRef.current);
    },
    setPodio(data: AxolotitoData[]) {
      podioRef.current = data;
      if (piramideRef.current && !piramideRef.current.destroyed) {
        piramideRef.current.setPodio(data);
      }
    },
  }));

  // Contrato legacy hacia play/page.tsx (worldSceneRef) — sin cambios.
  useEffect(() => {
    if (!onReady) return;
    const scene: WorldScene = {
      setAxolotitos: (data) => {
        axolotitosRef.current = data;
      },
      setCaveDecorations: () => {},
      focusZone: (zoneId) => {
        zonesRef.current?.navigate(zoneId, null);
      },
    };
    onReady(null, scene);
  }, [onReady]);

  // Montaje del motor Pixi (solo con flag).
  useEffect(() => {
    if (!PAPER_WORLD_ENABLED || !hostRef.current) return;
    let cancelled = false;

    (async () => {
      const [
        { WorldEngine },
        { ZoneManager },
        { SantuarioScene },
        { TianguisScene },
        { PiramideScene },
      ] = await Promise.all([
        import("./engine/WorldEngine"),
        import("./zones/ZoneManager"),
        import("./zones/santuario/SantuarioScene"),
        import("./zones/tianguis/TianguisScene"),
        import("./zones/piramide/PiramideScene"),
      ]);
      if (cancelled || !hostRef.current) return;

      const engine = await WorldEngine.create(hostRef.current);
      if (cancelled) {
        engine.destroy();
        return;
      }
      const zones = new ZoneManager(engine);
      // Dioramas reales (la Pirámide sigue placeholder hasta Fase 2b).
      zones.registerBuilder("santuario", (e) => {
        const scene = new SantuarioScene(e);
        santuarioRef.current = scene;
        scene.setAxolotitos(axolotitosRef.current);
        return scene;
      });
      zones.registerBuilder("tianguis", (e) => new TianguisScene(e));
      zones.registerBuilder("piramide", (e) => {
        const scene = new PiramideScene(e);
        piramideRef.current = scene;
        scene.setPodio(podioRef.current);
        return scene;
      });
      engine.bridge.on("hotspot", ({ kind, id }) => {
        onStallClickRef.current?.(id ? `${kind}:${id}` : kind);
      });
      engineRef.current = engine;
      zonesRef.current = zones;
      await zones.enter(initialZone);
    })().catch((err) => {
      console.error("PaperWorld: error inicializando el motor", err);
    });

    return () => {
      cancelled = true;
      zonesRef.current?.destroy();
      zonesRef.current = null;
      engineRef.current?.destroy();
      engineRef.current = null;
    };
    // initialZone solo aplica al primer mount.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (PAPER_WORLD_ENABLED) {
    return (
      <>
        <div ref={hostRef} className="fixed inset-0 z-0" aria-hidden />
        <PaperCurtain ref={curtainRef} />
      </>
    );
  }

  // ── Comportamiento stub original (flag apagado) ────────────────────────
  if (!visible) return null;

  return (
    <div className="fixed inset-0 z-0 pointer-events-none" style={{ background: "transparent" }}>
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
