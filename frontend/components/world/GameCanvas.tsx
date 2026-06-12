"use client";
import React, { forwardRef, useImperativeHandle, useRef, useEffect } from "react";
import type { AxolotitoData } from "@/types/axolotito";
import type { AmigoData } from "@/services/mapBackendAxolotito";
import type { CaveStatusData, DecoracionesData } from "./zones/santuario/santuarioTypes";
import PaperCurtain, { type PaperCurtainHandle } from "@/components/play/PaperCurtain";
import type { ThreeWorldEngine, World3DScene } from "@/components/world3d/ThreeWorldEngine";

/**
 * Mundo-diorama 3D de papel (three.js). Reemplaza por completo al motor Pixi
 * legacy. Cada macrozona (santuario, tianguis, piramide) es una escena 3D
 * construida bajo demanda con cortina de papel entre transiciones.
 */

export interface GameCanvasHandle {
  setAxolotitos(data: AxolotitoData[]): void;
  navigateToZone(zoneId: string): void;
  focusStall(stallId: string): void;
  resetFocus(): void;
  setPodio?(data: AxolotitoData[]): void;
  setAmigos?(amigos: AmigoData[]): void;
  setCaveStatus?(status: CaveStatusData): void;
  setDecoraciones?(data: DecoracionesData): void;
  setLunarPhase?(phase: number): void;
  playMeltAnimation?(): void;
}

interface GameCanvasProps {
  onReady?: (app: null, scene: null) => void;
  onStallClick?: (stallType: string) => void;
  initialZone?: string;
}

/** Mapea un id de zona legacy a su macrozona 3D. */
function zoneToMacro(zoneId: string): string {
  switch (zoneId) {
    case "nido": case "santuario": case "criadero": case "axolotitos":
      return "santuario";
    case "tianguis": case "tienda":
      return "tianguis";
    case "piramide": case "rankings": case "capsulas": case "gashapon":
    case "sala": case "salas": case "jugar":
      return "piramide";
    default:
      return "tianguis";
  }
}

const GameCanvas = forwardRef<GameCanvasHandle, GameCanvasProps>(function GameCanvas(
  {
    onReady,
    onStallClick,
    initialZone = "tianguis",
  },
  ref,
) {
  const host3dRef = useRef<HTMLDivElement>(null);
  const curtainRef = useRef<PaperCurtainHandle>(null);
  const engine3dRef = useRef<ThreeWorldEngine | null>(null);
  const scene3dRef = useRef<World3DScene | null>(null);
  const axolotitosRef = useRef<AxolotitoData[]>([]);
  const podioRef = useRef<AxolotitoData[]>([]);
  const amigosRef = useRef<AmigoData[]>([]);
  const caveStatusRef = useRef<CaveStatusData | null>(null);
  const decoracionesRef = useRef<DecoracionesData | null>(null);
  const onStallClickRef = useRef(onStallClick);
  onStallClickRef.current = onStallClick;

  useImperativeHandle(ref, () => ({
    setAxolotitos(data: AxolotitoData[]) {
      axolotitosRef.current = data;
      if (scene3dRef.current && "setAxolotitos" in scene3dRef.current) {
        (scene3dRef.current as any).setAxolotitos(data);
      }
    },
    setCaveStatus(status: CaveStatusData) {
      caveStatusRef.current = status;
      if (scene3dRef.current && "setCaveStatus" in scene3dRef.current) {
        (scene3dRef.current as any).setCaveStatus(status);
      }
    },
    setDecoraciones(data: DecoracionesData) {
      decoracionesRef.current = data;
      if (scene3dRef.current && "setDecoraciones" in scene3dRef.current) {
        (scene3dRef.current as any).setDecoraciones(data);
      }
    },
    setLunarPhase(_phase: number) {
      // TODO: implementar tinte lunar en escenas 3D
    },
    navigateToZone(zoneId: string) {
      const macro = zoneToMacro(zoneId);
      void navigateToMacro(macro);
    },
    focusStall(stallId: string) {
      engine3dRef.current?.focusStall(stallId);
    },
    resetFocus() {
      engine3dRef.current?.resetFocus();
    },
    setPodio(data: AxolotitoData[]) {
      podioRef.current = data;
      if (scene3dRef.current && "setPodio" in scene3dRef.current) {
        (scene3dRef.current as any).setPodio(data);
      }
    },
    setAmigos(amigos: AmigoData[]) {
      amigosRef.current = amigos;
      if (scene3dRef.current && "setAmigos" in scene3dRef.current) {
        (scene3dRef.current as any).setAmigos(amigos);
      }
    },
    playMeltAnimation() {
      scene3dRef.current?.playMelt?.();
    },
  }));

  // Legacy contract — page.tsx espera onReady para setCanvasReady(true).
  useEffect(() => {
    onReady?.(null, null);
  }, [onReady]);

  /** Construye una escena 3D para la macrozona dada y la monta en el motor. */
  const buildSceneForMacro = async (macro: string): Promise<World3DScene> => {
    const { configurePaperStyle } = await import("@/components/world3d/paperPrimitives");
    configurePaperStyle({ grain: engine3dRef.current!.quality !== "ligera" });

    if (macro === "tianguis") {
      const { buildTianguisScene3D } = await import("@/components/world3d/TianguisScene3D");
      const visitantes = axolotitosRef.current
        .filter((a) => !a.isEgg)
        .slice(0, 4)
        .map((a) => ({
          skinColor: a.skinColor,
          seed: [...a.id].reduce((h, ch) => (h * 31 + ch.charCodeAt(0)) % 9973, 7),
        }));
      const scene3d = buildTianguisScene3D({ visitantes });
      scene3d.group.userData = { macro: "tianguis" };
      return scene3d;
    }

    if (macro === "santuario") {
      const { buildSantuarioScene3D } = await import("@/components/world3d/SantuarioScene3D");
      const scene3d = buildSantuarioScene3D();
      scene3d.group.userData = { macro: "santuario" };

      if (caveStatusRef.current) scene3d.setCaveStatus(caveStatusRef.current);
      if (decoracionesRef.current) scene3d.setDecoraciones(decoracionesRef.current);
      scene3d.setAxolotitos(axolotitosRef.current);
      scene3d.setAmigos(amigosRef.current);

      return scene3d;
    }

    // piramide (y fallback)
    const { buildPiramideScene3D } = await import("@/components/world3d/PiramideScene3D");
    const scene3d = buildPiramideScene3D();
    scene3d.group.userData = { macro: "piramide" };

    scene3d.setPodio(podioRef.current);
    scene3d.setAxolotitos(axolotitosRef.current);

    return scene3d;
  };

  /** Navega a una macrozona con cortina de papel. */
  const navigateToMacro = async (macro: string) => {
    const current = scene3dRef.current?.group.userData?.macro as string | undefined;
    if (current === macro) return;

    const curtain = curtainRef.current;
    if (!curtain) {
      // Sin cortina (primera carga): construir y montar directo.
      const scene3d = await buildSceneForMacro(macro);
      scene3dRef.current = scene3d;
      engine3dRef.current?.setScene(scene3d);
      return;
    }

    await curtain.cover();
    const scene3d = await buildSceneForMacro(macro);
    scene3dRef.current = scene3d;
    engine3dRef.current?.setScene(scene3d);
    await curtain.reveal();
  };

  // Montaje del motor 3D (única vez).
  useEffect(() => {
    if (!host3dRef.current) return;
    let cancelled = false;

    (async () => {
      const { ThreeWorldEngine } = await import("@/components/world3d/ThreeWorldEngine");
      if (cancelled || !host3dRef.current) return;

      const engine = ThreeWorldEngine.create(host3dRef.current);
      engine.onHotspot = (stallId) => {
        if (stallId.startsWith("trajinera:")) {
          const friendId = stallId.slice("trajinera:".length);
          if (scene3dRef.current && "toggleActionBubbles" in scene3dRef.current) {
            (scene3dRef.current as any).toggleActionBubbles(friendId);
          }
          return;
        }
        onStallClickRef.current?.(stallId);
      };

      engine3dRef.current = engine;

      // Construir escena inicial.
      const initialMacro = zoneToMacro(initialZone);
      const scene3d = await buildSceneForMacro(initialMacro);
      scene3dRef.current = scene3d;
      engine.setScene(scene3d);
    })().catch((err) => {
      console.error("GameCanvas: error inicializando el motor 3D", err);
    });

    return () => {
      cancelled = true;
      scene3dRef.current = null;
      engine3dRef.current?.destroy();
      engine3dRef.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <>
      <div ref={host3dRef} className="fixed inset-0 z-0" aria-hidden>
        {/* Viñeta del diorama */}
        <div
          className="pointer-events-none absolute inset-0 z-10"
          style={{
            background:
              "radial-gradient(ellipse 105% 88% at 50% 42%, transparent 58%, rgba(16, 8, 36, 0.55) 100%)",
          }}
        />

        {/* CSS animations */}
        <style>{`
          @keyframes sway {
            0% { transform: rotate(-3deg); }
            100% { transform: rotate(3deg); }
          }
        `}</style>

        {/* Guirnalda de Papel Picado (Top Border) */}
        <div className="absolute top-0 left-0 right-0 z-20 pointer-events-none flex justify-center gap-0.5 overflow-hidden h-20 px-2 select-none">
          {Array.from({ length: 24 }).map((_, i) => {
            const colors = ["#e04a7a", "#2fb8b0", "#e8893a", "#f2c23e", "#f08aac", "#6cc06a"];
            const color = colors[i % colors.length];
            const delay = (i * 0.12).toFixed(2);
            return (
              <svg
                key={i}
                width="54"
                height="68"
                viewBox="0 0 60 76"
                className="flex-shrink-0 drop-shadow-sm"
                style={{
                  fill: color,
                  transformOrigin: "top center",
                  animation: "sway 2.5s ease-in-out infinite alternate",
                  animationDelay: `${delay}s`,
                }}
              >
                <path
                  d="M 0 8 H 60 V 68 L 50 58 L 40 68 L 30 58 L 20 68 L 10 58 L 0 68 Z M 30 20 L 42 32 L 30 44 L 18 32 Z M 15 16 L 19 20 L 15 24 L 11 20 Z M 45 16 L 49 20 L 45 24 L 41 20 Z M 15 42 L 19 46 L 15 50 L 11 46 Z M 45 42 L 49 46 L 45 50 L 41 46 Z"
                  fillRule="evenodd"
                />
              </svg>
            );
          })}
        </div>
      </div>
      <PaperCurtain ref={curtainRef} />
    </>
  );
});

export { GameCanvas };
export default GameCanvas;
