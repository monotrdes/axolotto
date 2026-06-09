"use client";

/**
 * ActGame — Tutorial game wrapper. Fixes the "stuck controls" bug.
 *
 * When the game finishes, CpuSimScreen's result screen appears underneath.
 * ActGame overlays an absolute div with:
 *   - Webito's post-game dialogue
 *   - A single "¡Siguiente! →" button that calls onComplete()
 *
 * The original CpuSimScreen buttons (play again / change board / change all)
 * are visually covered and functionally blocked during tutorial mode.
 *
 * Calls POST /api/v1/tutorial/next-step/{id} with the completed backendPhase
 * when the player taps "¡Siguiente!".
 */

import React, { useState, useCallback, useRef } from "react";
import CpuSimScreen from "@/components/screens/CpuSimScreen";
import WebitoDialogue from "../WebitoDialogue";
import type { WebitoData, StatFocus } from "../TutorialScript";
import {
  getActSalPreGame,
  getActOjoPreGame,
  getActSuertePilaPreGame,
  getTutorialDialogue,
} from "../dialogues";
import { API_BASE } from "@/lib/api";

// Distraction config
const DISTRACTION_DELAY_MS = 5000;

interface Props {
  statFocus: StatFocus;
  backendPhase: 1 | 2 | 3;
  webito: WebitoData;
  energyBefore: number; // 0 | 1 | 2
  onComplete: (karma?: "lucky" | "salty") => void;
  onStatsUpdate?: (updates: { bonusStamina?: number; bonusFocus?: number; bonusLuck?: number; bonusSalinityAdj?: number }) => void;
}

export default function ActGame({
  statFocus,
  backendPhase,
  webito,
  energyBefore,
  onComplete,
  onStatsUpdate,
}: Props) {
  const [gameKey]         = useState(0);
  const [gameFinished, setGameFinished] = useState(false);
  const [gameWon, setGameWon]           = useState<boolean | null>(null);
  const [advancing, setAdvancing]       = useState(false);

  // Pre/post dialogue state
  const [preGameDone, setPreGameDone]   = useState(() => statFocus === "SAL");
  const [postGameText, setPostGameText] = useState("");

  // Phase-2 distraction
  const [showDistraction, setShowDistraction] = useState(false);
  const [distractionDone, setDistractionDone] = useState(false);
  const distractionTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // ── Pre-game dialogue ────────────────────────────────────────────────────────
  const salValue = Math.round(Math.max(0, Math.min(100, webito.baseStatSalinity + webito.bonusSalinityAdj)));
  const preGameText =
    statFocus === "SAL"
      ? getActSalPreGame(webito.nature, salValue)
      : statFocus === "OJO"
        ? getActOjoPreGame(webito.nature, webito.bonusFocus)
        : getActSuertePilaPreGame(webito.nature, webito.bonusLuck, webito.bonusStamina);

  // ── CpuSimScreen callbacks ───────────────────────────────────────────────────

  // onDone fires when backend result arrives (BEFORE animation ends) — cancel timers only.
  const handleDone = useCallback(() => {
    console.log(`[ActGame:${statFocus}] backend result received, animation starting`);
    if (distractionTimerRef.current) {
      clearTimeout(distractionTimerRef.current);
      setShowDistraction(false);
    }
  }, [statFocus]);

  // onResultReady fires when CpuSimScreen animation ends (phase→'result'). NOW we overlay.
  // Delay overlay so the player sees the winning/losing board animation briefly first.
  const handleResultReady = useCallback((won: boolean) => {
    console.log(`[ActGame:${statFocus}] animation done, won=${won} → mostrando overlay tutorial`);
    setGameWon(won);
    setPostGameText(getTutorialDialogue(backendPhase, webito.nature, won ? "phase_win" : "phase_lose"));
    const delay = won ? 2000 : 1500;
    setTimeout(() => setGameFinished(true), delay);
  }, [statFocus, backendPhase, webito.nature]);

  // Make action buttons no-ops — our overlay intercepts via onResultReady
  const handlePlayAgain   = useCallback(() => {}, []);
  const handleChangeBoard = useCallback(() => {}, []);
  const handleChangeAll   = useCallback(() => {}, []);

  // ── Advance to next act ──────────────────────────────────────────────────────
  const handleAdvance = useCallback(async () => {
    if (advancing) return;
    console.log(`[ActGame:${statFocus}] ¡Siguiente! → llamando next-step phase=${backendPhase} won=${gameWon}`);
    setAdvancing(true);
    try {
      const headers: Record<string, string> = { "Content-Type": "application/json" };
      if (webito.token) headers["Authorization"] = `Bearer ${webito.token}`;
      const res = await fetch(`${API_BASE}/tutorial/next-step/${webito.tutorialId}`, {
        method: "POST",
        headers,
        body: JSON.stringify({ won: gameWon ?? false }),
      });

      // ✅ Verificar respuesta del backend
      if (!res.ok) {
        const errText = await res.text().catch(() => "Unknown error");
        console.error(`❌ Tutorial next-step falló (${res.status}): ${errText}`);
        setAdvancing(false);
        return; // ⛔ NO avanzar si falló
      }

      const data: { bonus_stamina?: number; bonus_focus?: number; bonus_luck?: number; bonus_salinity_adj?: number } =
        await res.json();
      console.log("✅ Tutorial next-step OK — fase:", (data as any)?.phase);

      if (onStatsUpdate) {
        const updates: { bonusStamina?: number; bonusFocus?: number; bonusLuck?: number; bonusSalinityAdj?: number } = {};
        if (data.bonus_stamina      != null) updates.bonusStamina     = data.bonus_stamina;
        if (data.bonus_focus        != null) updates.bonusFocus       = data.bonus_focus;
        if (data.bonus_luck         != null) updates.bonusLuck        = data.bonus_luck;
        if (data.bonus_salinity_adj != null) updates.bonusSalinityAdj = data.bonus_salinity_adj;
        if (Object.keys(updates).length > 0) onStatsUpdate(updates);
      }
    } catch (e) {
      console.error("❌ Error de red al avanzar fase del tutorial:", e);
      setAdvancing(false);
      return; // ⛔ NO avanzar en el catch
    } finally {
      setAdvancing(false);
    }
    onComplete();
  }, [advancing, webito, backendPhase, onComplete, onStatsUpdate, gameWon]);

  // ── Phase-specific interactions setup after pre-game ────────────────────────
  const handlePreGameDismiss = useCallback(() => {
    console.log(`[ActGame:${statFocus}] pre-game diálogo OK → iniciando juego`);
    setPreGameDone(true);

    // Phase 2: schedule distraction if OJO is low
    if (statFocus === "OJO" && webito.bonusFocus < 50) {
      distractionTimerRef.current = setTimeout(() => {
        setShowDistraction(true);
      }, DISTRACTION_DELAY_MS);
    }
  }, [statFocus, webito.bonusFocus]);

  // ── Distraction dismiss ──────────────────────────────────────────────────────
  const handleDistractionDismiss = useCallback(() => {
    setShowDistraction(false);
    setDistractionDone(true);
  }, []);
  const distractionText  = getTutorialDialogue(2, webito.nature, "distracted");

  // ── Energy bar ───────────────────────────────────────────────────────────────
  const energyPct = (energyBefore / 3) * 100;

  // ── Render: pre-game dialogue ─────────────────────────────────────────────────
  if (!preGameDone) {
    return (
      <div className="flex flex-col items-center gap-4 pt-4 pb-6 px-3">
        <EnergyBar value={energyBefore} />
        <StatBadge statFocus={statFocus} phase={backendPhase} />

        <div className="text-[80px] leading-none" style={{ animation: "axo-bob 2s ease-in-out infinite" }}>
          🥚
        </div>

        {/* Stat display — shows the relevant stat value so the player understands the dialogue */}
        <StatDisplay statFocus={statFocus} webito={webito} salValue={salValue} />

        <div className="w-full max-w-sm">
          <WebitoDialogue
            text={preGameText}
            speaker="webito"
            onDismiss={handlePreGameDismiss}
          />
        </div>

        <p className="text-[10px] font-bold uppercase tracking-widest animate-pulse" style={{ color: "#334155" }}>
          Toca el diálogo para continuar
        </p>
      </div>
    );
  }

  // ── Render: game in progress ──────────────────────────────────────────────────
  return (
    <div className="relative">

      {/* Energy bar floating above game */}
      <div className="px-3 pt-2 pb-1">
        <EnergyBar value={energyBefore} />
      </div>

      {/* CpuSimScreen */}
      <div style={{ opacity: showDistraction ? 0.45 : 1, transition: "opacity 0.3s" }}>
        <CpuSimScreen
          key={gameKey}
          userId={webito.userId}
          token={webito.token}
          selectedAxo={{ id: 0, name: "Webito", cpu_win_streak: 0 }}
          selectedBoardId={0}
          playerBoards={[]}
          allCards={[]}
          selectedRoom="rookie"
          onPlayAgainInPlace={handlePlayAgain}
          onChangeBoard={handleChangeBoard}
          onChangeAll={handleChangeAll}
          onDone={handleDone}
          onResultReady={handleResultReady}
        />
      </div>

      {/* Phase 2: distraction overlay */}
      {showDistraction && !gameFinished && (
        <div className="absolute inset-0 z-50 flex flex-col items-end justify-start p-3 gap-3">
          <div
            className="self-center px-4 py-2 rounded-full text-[11px] font-black uppercase tracking-widest animate-pulse"
            style={{
              background: "rgba(6,6,20,0.9)",
              border: "2px solid #f97316",
              color: "#f97316",
              boxShadow: "0 0 16px rgba(249,115,22,0.5)",
            }}
          >
            ¡Toca la carta resaltada!
          </div>
          <div className="w-full mt-auto">
            <WebitoDialogue text={distractionText} speaker="webito" onDismiss={handleDistractionDismiss} />
          </div>
        </div>
      )}

      {/* ── RESULT OVERLAY — reemplaza el panel de CpuSimScreen ── */}
      {gameFinished && (
        <div
          className="absolute inset-0 z-50 flex flex-col items-center justify-center gap-3 px-4 py-6"
          style={{ background: "rgba(6,6,20,0.92)", backdropFilter: "blur(4px)" }}
        >
          {/* Victoria / Derrota */}
          <div
            className="text-4xl font-black uppercase tracking-tighter"
            style={{
              color: gameWon ? "#34d399" : "#f87171",
              textShadow: gameWon
                ? "0 0 30px rgba(52,211,153,0.8)"
                : "0 0 30px rgba(248,113,113,0.8)",
            }}
          >
            {gameWon ? "✨ ¡VICTORIA!" : "💀 Derrota"}
          </div>

          {/* Stat afectado */}
          <ResultStatDisplay statFocus={statFocus} webito={webito} salValue={salValue} won={gameWon ?? false} />

          {/* Webito dialogue — colored by result */}
          <div className="w-full max-w-sm">
            <WebitoDialogue
              text={postGameText}
              speaker="axo"
              mood={gameWon ? "victory" : "defeat"}
            />
          </div>

          <button
            onClick={handleAdvance}
            disabled={advancing}
            className="w-full max-w-sm py-4 rounded-2xl font-black text-base uppercase tracking-widest text-white transition-all active:scale-95 disabled:opacity-60"
            style={{
              background: gameWon
                ? "linear-gradient(135deg, #34d399, #059669)"
                : "linear-gradient(135deg, #f87171, #dc2626)",
              boxShadow: gameWon
                ? "0 0 28px rgba(52,211,153,0.4)"
                : "0 0 28px rgba(248,113,113,0.4)",
            }}
          >
            {advancing
              ? "Guardando..."
              : backendPhase === 3
                ? "¡Ver mi karma! →"
                : "Siguiente partida →"}
          </button>
        </div>
      )}
    </div>
  );
}

// ── Sub-components ────────────────────────────────────────────────────────────

function EnergyBar({ value }: { value: number }) {
  const pct = (value / 3) * 100;
  return (
    <div className="flex items-center gap-2 px-1">
      <span className="text-sm">🥚</span>
      <div className="flex-1 h-2 rounded-full overflow-hidden" style={{ background: "rgba(255,255,255,0.08)" }}>
        <div
          className="h-full rounded-full transition-all duration-700"
          style={{
            width: `${pct}%`,
            background: "linear-gradient(90deg, #00e5ff, #818cf8)",
            boxShadow: pct > 0 ? "0 0 8px rgba(0,229,255,0.5)" : "none",
          }}
        />
      </div>
      <span className="text-[10px] font-black tabular-nums" style={{ color: "#475569" }}>
        {value}/3
      </span>
    </div>
  );
}

// ── StatDisplay — visual de stats relevantes en pre-game ─────────────────────

interface StatRow { emoji: string; label: string; value: number; color: string; glow: string; }

function StatBar({ emoji, label, value, color, glow }: StatRow) {
  return (
    <div className="flex items-center gap-2">
      <span className="text-sm w-5 text-center">{emoji}</span>
      <span className="text-[10px] font-black uppercase tracking-widest w-12" style={{ color }}>
        {label}
      </span>
      <div className="flex-1 h-1.5 rounded-full overflow-hidden" style={{ background: "rgba(255,255,255,0.06)" }}>
        <div
          className="h-full rounded-full transition-all duration-700"
          style={{
            width: `${Math.min(100, value)}%`,
            background: `linear-gradient(90deg, ${color}88, ${color})`,
            boxShadow: `0 0 6px ${glow}`,
          }}
        />
      </div>
      <span className="text-[11px] font-black tabular-nums w-7 text-right" style={{ color }}>
        {Math.round(value)}
      </span>
    </div>
  );
}

function StatDisplay({
  statFocus,
  webito,
  salValue,
}: {
  statFocus: StatFocus;
  webito: import("../TutorialScript").WebitoData;
  salValue: number;
}) {
  const rows: StatRow[] =
    statFocus === "SAL"
      ? [{ emoji: "🧂", label: "SAL", value: salValue,           color: "#00e5ff", glow: "rgba(0,229,255,0.5)" }]
      : statFocus === "OJO"
        ? [{ emoji: "👁️",  label: "OJO", value: webito.bonusFocus, color: "#818cf8", glow: "rgba(129,140,248,0.5)" }]
        : [
            { emoji: "✨", label: "SUERTE", value: webito.bonusLuck,    color: "#fbbf24", glow: "rgba(251,191,36,0.5)" },
            // PILA floored para igualar el valor del juego (int() en final_stats)
            { emoji: "🔋", label: "PILA",   value: Math.floor(Math.max(50, Math.min(200, webito.baseStatStamina + webito.bonusStamina))), color: "#34d399", glow: "rgba(52,211,153,0.5)" },
          ];

  return (
    <div
      className="w-full max-w-sm rounded-2xl px-4 py-3 space-y-2"
      style={{
        background: "rgba(6,6,20,0.85)",
        border: "1px solid rgba(255,255,255,0.07)",
      }}
    >
      {rows.map(r => <StatBar key={r.label} {...r} />)}
    </div>
  );
}

// ── ResultStatDisplay — muestra stat + efecto tras la partida ────────────────

const STAT_DELTA = 10;

function ResultStatDisplay({
  statFocus,
  webito,
  salValue,
  won,
}: {
  statFocus: StatFocus;
  webito: import("../TutorialScript").WebitoData;
  salValue: number;
  won: boolean;
}) {
  // SAL: ganar partida baja SAL (bueno), perder la sube (malo).
  // Predicción anclada a salValue. La magnitud DEBE coincidir con el backend
  // (tutorial_service.py fase 1 sal_delta = ±STAT_DELTA) para que lo mostrado == lo persistido.
  const newSalValue = Math.max(0, Math.min(100, salValue + (won ? -STAT_DELTA : STAT_DELTA)));
  const salDelta = newSalValue - salValue;

  // OJO: delta sobre bonus_focus
  const newFocus = won
    ? Math.min(160, webito.bonusFocus + STAT_DELTA)
    : Math.max(40, webito.bonusFocus - STAT_DELTA);
  const ojoDelta = newFocus - webito.bonusFocus;

  // SUERTE_PILA: delta sobre bonus_luck (SUERTE)
  const newLuck = won
    ? Math.min(160, webito.bonusLuck + STAT_DELTA)
    : Math.max(40, webito.bonusLuck - STAT_DELTA);
  const suerteDelta = newLuck - webito.bonusLuck;

  const rows: (StatRow & { effect: string; delta?: number })[] =
    statFocus === "SAL"
      ? [{
          emoji: "🧂", label: "SAL", value: newSalValue, color: "#00e5ff", glow: "rgba(0,229,255,0.5)",
          delta: salDelta,
          effect: won
            ? "Tu resistencia al agua salada aumentó — el Cenote lo registró."
            : "El agua salada te afectó más esta vez — el Cenote lo registró.",
        }]
      : statFocus === "OJO"
        ? [{
            emoji: "👁️", label: "OJO", value: newFocus, color: "#818cf8", glow: "rgba(129,140,248,0.5)",
            delta: ojoDelta,
            effect: won
              ? "Tu OJO se afiló — el Cenote registró tu concentración."
              : "Tu OJO necesita más práctica — el Cenote lo registró.",
          }]
        : [
            {
              emoji: "✨", label: "SUERTE", value: newLuck, color: "#fbbf24", glow: "rgba(251,191,36,0.5)",
              delta: suerteDelta,
              effect: won ? "¡Tu SUERTE brilló — el Cenote lo registró!" : "La SUERTE no estuvo de tu lado — el Cenote lo registró.",
            },
            {
              // PILA no cambia en el tutorial. Floor(clamp(base+bonus)) para igualar el valor
              // persistido del juego (final_stats usa int()), no Math.round.
              emoji: "🔋", label: "PILA",
              value: Math.floor(Math.max(50, Math.min(200, webito.baseStatStamina + webito.bonusStamina))),
              color: "#34d399", glow: "rgba(52,211,153,0.5)",
              effect: won ? "Tu PILA aguantó todo el partido." : "Tu PILA acumuló experiencia.",
            },
          ];

  return (
    <div
      className="w-full max-w-sm rounded-2xl px-4 py-3 space-y-2"
      style={{
        background: won ? "rgba(52,211,153,0.06)" : "rgba(248,113,113,0.06)",
        border: `1px solid ${won ? "rgba(52,211,153,0.2)" : "rgba(248,113,113,0.2)"}`,
      }}
    >
      {rows.map(r => (
        <div key={r.label} className="space-y-1">
          <div className="flex items-center gap-2">
            <StatBar {...r} />
            {r.delta != null && r.delta !== 0 && (() => {
              // SAL inverso: ganar puntos es malo. Otros stats: ganar es bueno.
              const good = r.label === "SAL" ? r.delta < 0 : r.delta > 0;
              return (
                <span
                  className="text-[11px] font-black tabular-nums shrink-0"
                  style={{ color: good ? "#34d399" : "#f87171" }}
                >
                  {r.delta < 0 ? `▼ ${Math.abs(r.delta)}` : `▲ +${r.delta}`}
                </span>
              );
            })()}
          </div>
          <p className="text-[10px] leading-snug pl-7" style={{ color: "#64748b" }}>{r.effect}</p>
        </div>
      ))}
    </div>
  );
}

function StatBadge({ statFocus, phase }: { statFocus: StatFocus; phase: number }) {
  const labels: Record<StatFocus, string> = {
    SAL:         "🧂 Partida SAL",
    OJO:         "👁️ Partida OJO",
    SUERTE_PILA: "✨🔋 Partida SUERTE + PILA",
  };
  return (
    <div
      className="px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-widest"
      style={{
        background: "rgba(255,255,255,0.05)",
        border: "1px solid rgba(255,255,255,0.1)",
        color: "#94a3b8",
      }}
    >
      Partida {phase} de 3 — {labels[statFocus]}
    </div>
  );
}
