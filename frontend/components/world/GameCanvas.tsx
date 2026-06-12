"use client";
import React, { forwardRef, useImperativeHandle, useRef, useEffect } from "react";
import type { WorldScene } from "./WorldScene";
import type { AxolotitoData } from "./entities/AxolotitoSprite";
import PaperCurtain, { type PaperCurtainHandle } from "@/components/play/PaperCurtain";
import type { WorldEngine } from "./engine/WorldEngine";
import type { ZoneManager } from "./zones/ZoneManager";
import type {
  SantuarioScene,
  CaveStatusData,
  DecoracionesData,
} from "./zones/santuario/SantuarioScene";
import type { PiramideScene } from "./zones/piramide/PiramideScene";
import type { TianguisScene } from "./zones/tianguis/TianguisScene";
import type { AmigoData } from "./mapBackendAxolotito";
import { TIANGUIS_STALL_FRAMINGS, framingFor } from "./zones/zoneConfig";
import type { ThreeWorldEngine, World3DScene } from "@/components/world3d/ThreeWorldEngine";

/**
 * Mundo 2.5D de papel picado (plan task-84). Detrás del flag
 * NEXT_PUBLIC_PAPER_WORLD=1: monta PixiJS (import dinámico — sin flag no se
 * descarga el chunk) con 3 macrozonas y cortina de papel. Sin flag, conserva
 * el comportamiento stub original intacto.
 */

const PAPER_WORLD_ENABLED = process.env.NEXT_PUBLIC_PAPER_WORLD === "1";
/**
 * Mundo-diorama 3D de papel (decisión 2026-06-12): zonas migradas se renderizan
 * con three.js (hoy: Tianguis); el resto sigue en Pixi. El swap de canvas
 * ocurre bajo la cortina de papel, en zoneSettled.
 */
const WORLD3D_ENABLED =
  PAPER_WORLD_ENABLED && process.env.NEXT_PUBLIC_WORLD3D === "1";

export interface GameCanvasHandle {
  setAxolotitos(data: AxolotitoData[]): void;
  focusZone(zoneId: string): void;
  navigateToZone(zoneId: string): void;
  focusStall(stallId: string): void;
  resetFocus(): void;
  /** Top-3 del ranking para el podio de la Pirámide (mundo papel picado). */
  setPodio?(data: AxolotitoData[]): void;
  /** Amigos para el embarcadero del Santuario (mundo papel picado). */
  setAmigos?(amigos: AmigoData[]): void;
  /** Nivel/spots/mesa de la cueva (GET /cave/status) para nidos dinámicos. */
  setCaveStatus?(status: CaveStatusData): void;
  /** Decoraciones equipadas + layout de slots (GET /cave/decorations). */
  setDecoraciones?(data: DecoracionesData): void;
  /** Fase lunar 1-6 (🌑→🌟) — tiñe la luz superficial de las 3 macrozonas. */
  setLunarPhase?(phase: number): void;
  /** Lanza la animación de fuegos/estrellas en la forja del Tianguis. */
  playMeltAnimation?(): void;
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
  const host3dRef = useRef<HTMLDivElement>(null);
  const curtainRef = useRef<PaperCurtainHandle>(null);
  const engineRef = useRef<WorldEngine | null>(null);
  const engine3dRef = useRef<ThreeWorldEngine | null>(null);
  const scene3dRef = useRef<World3DScene | null>(null);
  const active3dRef = useRef(false);
  const zonesRef = useRef<ZoneManager | null>(null);
  const santuarioRef = useRef<SantuarioScene | null>(null);
  const tianguisRef = useRef<TianguisScene | null>(null);
  const piramideRef = useRef<PiramideScene | null>(null);
  const axolotitosRef = useRef<AxolotitoData[]>([]);
  const podioRef = useRef<AxolotitoData[]>([]);
  const amigosRef = useRef<AmigoData[]>([]);
  const caveStatusRef = useRef<CaveStatusData | null>(null);
  const decoracionesRef = useRef<DecoracionesData | null>(null);
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
    setCaveStatus(status: CaveStatusData) {
      caveStatusRef.current = status;
      if (santuarioRef.current && !santuarioRef.current.destroyed) {
        santuarioRef.current.setCaveStatus(status);
      }
    },
    setDecoraciones(data: DecoracionesData) {
      decoracionesRef.current = data;
      if (santuarioRef.current && !santuarioRef.current.destroyed) {
        santuarioRef.current.setDecoraciones(data);
      }
    },
    setLunarPhase(phase: number) {
      if (engineRef.current) engineRef.current.lunarPhase = phase;
    },
    focusZone(zoneId: string) {
      zonesRef.current?.navigate(zoneId, null);
    },
    navigateToZone(zoneId: string) {
      zonesRef.current?.navigate(zoneId, curtainRef.current);
    },
    focusStall(stallId: string) {
      if (active3dRef.current) {
        engine3dRef.current?.focusStall(stallId);
        return;
      }
      const framing = TIANGUIS_STALL_FRAMINGS[stallId];
      if (framing && engineRef.current) {
        engineRef.current.camera.panTo(framing);
      }
    },
    resetFocus() {
      if (active3dRef.current) {
        engine3dRef.current?.resetFocus();
        return;
      }
      if (!engineRef.current || !zonesRef.current) return;
      const activeTarget = zonesRef.current.activeTarget;
      if (!activeTarget) return;
      engineRef.current.camera.panTo(framingFor(activeTarget));
    },
    setPodio(data: AxolotitoData[]) {
      podioRef.current = data;
      if (piramideRef.current && !piramideRef.current.destroyed) {
        piramideRef.current.setPodio(data);
      }
    },
    setAmigos(amigos: AmigoData[]) {
      amigosRef.current = amigos;
      if (santuarioRef.current && !santuarioRef.current.destroyed) {
        santuarioRef.current.setAmigos(amigos);
      }
    },
    playMeltAnimation() {
      if (active3dRef.current) {
        scene3dRef.current?.playMelt?.();
        return;
      }
      if (tianguisRef.current && !tianguisRef.current.destroyed) {
        tianguisRef.current.playMeltAnimation();
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
        if (caveStatusRef.current) scene.setCaveStatus(caveStatusRef.current);
        if (decoracionesRef.current) scene.setDecoraciones(decoracionesRef.current);
        scene.setAxolotitos(axolotitosRef.current);
        scene.setAmigos(amigosRef.current);
        return scene;
      });
      zones.registerBuilder("tianguis", (e) => {
        const scene = new TianguisScene(e);
        tianguisRef.current = scene;
        return scene;
      });
      zones.registerBuilder("piramide", (e) => {
        const scene = new PiramideScene(e);
        piramideRef.current = scene;
        scene.setPodio(podioRef.current);
        return scene;
      });
      engine.bridge.on("hotspot", ({ kind, id }) => {
        onStallClickRef.current?.(id ? `${kind}:${id}` : kind);
      });

      // Zonas migradas al diorama 3D: swap de canvas bajo la cortina.
      if (WORLD3D_ENABLED) {
        const setWorld3DActive = async (active: boolean) => {
          if (active === active3dRef.current) return;
          active3dRef.current = active;
          const host3d = host3dRef.current;
          const hostPixi = hostRef.current;
          if (!host3d || !hostPixi) return;
          if (active) {
            const [{ ThreeWorldEngine }, { buildTianguisScene3D }] = await Promise.all([
              import("@/components/world3d/ThreeWorldEngine"),
              import("@/components/world3d/TianguisScene3D"),
            ]);
            if (cancelled || !active3dRef.current) return;
            if (!engine3dRef.current) {
              engine3dRef.current = ThreeWorldEngine.create(host3d);
              engine3dRef.current.onHotspot = (stallId) => onStallClickRef.current?.(stallId);
            }
            const scene3d = buildTianguisScene3D();
            scene3dRef.current = scene3d;
            engine3dRef.current.setScene(scene3d);
            host3d.style.display = "";
            hostPixi.style.display = "none";
            engine3dRef.current.setUiPaused(false);
            engine.setUiPaused(true);
          } else {
            engine3dRef.current?.setUiPaused(true);
            engine3dRef.current?.clearScene();
            scene3dRef.current = null;
            host3d.style.display = "none";
            hostPixi.style.display = "";
            engine.setUiPaused(false);
          }
        };
        engine.bridge.on("zoneSettled", ({ macro }) => {
          void setWorld3DActive(macro === "tianguis").catch((err) =>
            console.error("World3D: error montando la escena", err),
          );
        });
      }

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
      active3dRef.current = false;
      scene3dRef.current = null;
      engine3dRef.current?.destroy();
      engine3dRef.current = null;
    };
    // initialZone solo aplica al primer mount.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (PAPER_WORLD_ENABLED) {
    return (
      <>
        <div ref={hostRef} className="fixed inset-0 z-0" aria-hidden />
        {WORLD3D_ENABLED && (
          <div ref={host3dRef} className="fixed inset-0 z-0" style={{ display: "none" }} aria-hidden />
        )}
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
