"use client";
import type { TabId } from "@/types/play";

/**
 * Dock v2 del mundo papel picado (plan task-84 §3.2): 3 macrozonas.
 * La Pirámide (FAB central) despliega sub-pills 🏆🎲🎰 al estar activa.
 * Solo se renderiza con NEXT_PUBLIC_PAPER_WORLD=1; el dock legacy de 5
 * botones (ZoneDock) sigue siendo el default sin flag.
 */

interface ZoneDockMacroProps {
  tabActiva: TabId;
  dailyClaimAvailable: boolean;
  /** tab HTML a activar + zona canónica para GameCanvas.navigateToZone. */
  onNavigate: (tab: TabId, zone: string) => void;
}

type MacroId = "santuario" | "piramide" | "tianguis";

function activeMacro(tab: TabId): MacroId | null {
  if (tab === "santuario" || tab === "criadero" || tab === "axolotitos" || tab === "amigos")
    return "santuario";
  if (tab === "tienda") return "tianguis";
  if (tab === "jugar" || tab === "rankings" || tab === "gashapon") return "piramide";
  return null; // mochila/cartas/tablas — overlay sin macrozona propia
}

export default function ZoneDockMacro({
  tabActiva,
  dailyClaimAvailable,
  onNavigate,
}: ZoneDockMacroProps) {
  const macro = activeMacro(tabActiva);
  const piramideActive = macro === "piramide";

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-40 overflow-visible bg-[#060610]/90 backdrop-blur-xl border-t border-white/5">
      <div className="flex items-end justify-around px-1 pt-1 pb-2.5 max-w-xl mx-auto">
        {/* Santuario */}
        <MacroButton
          emoji="🪺"
          label="Santuario"
          color="#E4007C"
          glow="rgba(228,0,124,0.5)"
          isActive={macro === "santuario"}
          onClick={() => onNavigate("santuario", "santuario")}
        />

        {/* Pirámide — FAB central */}
        <div className="flex flex-col items-center flex-1 -translate-y-5">
          <button
            onClick={() => onNavigate("rankings", "rankings")}
            className="relative w-14 h-14 rounded-full flex items-center justify-center transition-all duration-200"
            style={
              piramideActive
                ? {
                    background: "linear-gradient(135deg, #FBD38D, #F59E0B, #C2410C)",
                    boxShadow:
                      "0 0 0 3px rgba(245,158,11,0.25), 0 0 28px 4px rgba(245,158,11,0.7)",
                    transform: "scale(1.1)",
                  }
                : {
                    background: "linear-gradient(135deg, #F59E0B, #C2410C)",
                    boxShadow:
                      "0 0 0 2px rgba(245,158,11,0.15), 0 0 20px 2px rgba(245,158,11,0.4)",
                  }
            }
          >
            <span className="text-2xl leading-none select-none">🗿</span>
            {dailyClaimAvailable && !piramideActive && (
              <span className="absolute top-0 right-0 w-2.5 h-2.5 rounded-full bg-red-500 shadow-[0_0_6px_2px_rgba(239,68,68,0.7)] animate-pulse" />
            )}
          </button>
          <span
            className="text-[9px] sm:text-[10px] font-black leading-none tracking-widest mt-1.5 transition-colors duration-200 uppercase"
            style={{ color: piramideActive ? "#FBD38D" : "#F59E0B" }}
          >
            Pirámide
          </span>
        </div>

        {/* Tianguis */}
        <MacroButton
          emoji="🏪"
          label="Tianguis"
          color="#FF6B35"
          glow="rgba(255,107,53,0.5)"
          isActive={macro === "tianguis"}
          onClick={() => onNavigate("tienda", "tianguis")}
        />
      </div>
    </nav>
  );
}

function MacroButton({
  emoji,
  label,
  color,
  glow,
  isActive,
  onClick,
}: {
  emoji: string;
  label: string;
  color: string;
  glow: string;
  isActive: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className="flex flex-col items-center gap-0.5 px-1 py-0.5 rounded-xl transition-all duration-200 min-w-0 flex-1 relative"
    >
      {isActive && (
        <span
          className="absolute -top-1.5 left-1/2 -translate-x-1/2 w-5 h-0.5 rounded-full"
          style={{ backgroundColor: color, boxShadow: `0 0 6px 2px ${glow}` }}
        />
      )}
      <span
        className="text-xl leading-none transition-all duration-200"
        style={{
          transform: isActive ? "scale(1.2) translateY(-1px)" : "scale(1)",
          filter: isActive ? `drop-shadow(0 0 6px ${glow})` : "none",
        }}
      >
        {emoji}
      </span>
      <span
        className="text-[9px] sm:text-[10px] font-semibold leading-none truncate max-w-[60px] transition-colors duration-200"
        style={{ color: isActive ? color : "#4B5563" }}
      >
        {label}
      </span>
    </button>
  );
}
