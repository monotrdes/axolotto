"use client";

/**
 * SleepingEgg
 *
 * Displayed for F2P players who are accumulating fragments.
 * Shows the egg's dream state, a progress bar, and a hatch button when ready.
 *
 * Data:
 *   GET  /api/v1/f2p/egg-status           — initial + polling
 *   POST /api/v1/f2p/watch-reward?won=false — credit for watching a game
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { usePrivy } from '@privy-io/react-auth';

// ── Types ──────────────────────────────────────────────────────────────────────

interface EggStatus {
  fragments: number;
  max_fragments: number;
  reaction_stage: 0 | 1 | 2 | 3 | 4 | 5;
  dream_bubble: string | null;
  ready_to_hatch: boolean;
}

export interface SleepingEggProps {
  /** When true the parent wants to credit "watched a game" fragments */
  justWatchedGame?: boolean;
  onReadyToHatch?: () => void;
}

// ── Reaction stages: 0-5 ─────────────────────────────────────────────────────

const STAGE_EMOJI: Record<number, string> = {
  0: "🥚",
  1: "🥚💤",
  2: "🥚💭",
  3: "🥚✨",
  4: "🥚🌟",
  5: "🐣🌊",
};

const STAGE_LABEL: Record<number, string> = {
  0: "Durmiendo",
  1: "Soñando",
  2: "Pensando",
  3: "Brillando",
  4: "Casi listo",
  5: "Listo para nacer",
};

// ── Component ──────────────────────────────────────────────────────────────────

export default function SleepingEgg({
  justWatchedGame = false,
  onReadyToHatch,
}: SleepingEggProps) {
  const { getAccessToken, authenticated } = usePrivy();

  const [status, setStatus]       = useState<EggStatus | null>(null);
  const [loading, setLoading]     = useState(true);
  const [hatching, setHatching]   = useState(false);
  const [error, setError]         = useState<string | null>(null);

  // Bubble visibility toggle
  const [bubbleVisible, setBubbleVisible] = useState(false);
  const bubbleTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // ── Fetch egg status ─────────────────────────────────────────────────────────

  const fetchStatus = useCallback(async () => {
    if (!authenticated) return;
    try {
      const token = await getAccessToken();
      const headers: HeadersInit = token ? { Authorization: `Bearer ${token}` } : {};
      const apiBase = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8001";
      const res = await fetch(`${apiBase}/api/v1/f2p/egg-status`, { headers });
      if (!res.ok) throw new Error(`Error ${res.status}`);
      const data: EggStatus = await res.json();
      setStatus(data);
      if (data.ready_to_hatch) onReadyToHatch?.();
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Error desconocido";
      setError(message);
    } finally {
      setLoading(false);
    }
  }, [authenticated, getAccessToken, onReadyToHatch]);

  useEffect(() => {
    fetchStatus();
  }, [fetchStatus]);

  // ── Credit watch reward when justWatchedGame changes to true ─────────────────

  const watchCreditedRef = useRef(false);

  useEffect(() => {
    if (!justWatchedGame || watchCreditedRef.current || !authenticated) return;
    watchCreditedRef.current = true;

    const creditWatch = async () => {
      try {
        const token = await getAccessToken();
        const headers: HeadersInit = {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        };
        const apiBase = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8001";
        await fetch(`${apiBase}/api/v1/f2p/watch-reward?won=false`, {
          method: "POST",
          headers,
        });
        // Re-fetch to reflect new fragment count
        await fetchStatus();
      } catch (err) {
        console.error("Error acreditando fragmento de observación:", err);
      }
    };

    creditWatch();
  // Reset the ref when justWatchedGame goes back to false so next watch credits too
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [justWatchedGame]);

  useEffect(() => {
    if (!justWatchedGame) {
      watchCreditedRef.current = false;
    }
  }, [justWatchedGame]);

  // ── Dream bubble pulse animation ─────────────────────────────────────────────

  useEffect(() => {
    if (!status?.dream_bubble) return;

    // Show bubble for 3s, hide for 4s, repeat
    let showPhase = true;
    setBubbleVisible(true);

    bubbleTimerRef.current = setInterval(() => {
      showPhase = !showPhase;
      setBubbleVisible(showPhase);
    }, showPhase ? 3000 : 4000);

    return () => {
      if (bubbleTimerRef.current) clearInterval(bubbleTimerRef.current);
    };
  }, [status?.dream_bubble]);

  // ── Hatch action ─────────────────────────────────────────────────────────────

  const handleHatch = useCallback(async () => {
    if (!status?.ready_to_hatch || hatching || !authenticated) return;
    setHatching(true);
    try {
      const token = await getAccessToken();
      const headers: HeadersInit = {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      };
      const apiBase = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8001";
      await fetch(`${apiBase}/api/v1/f2p/hatch`, { method: "POST", headers });
      onReadyToHatch?.();
    } catch (err) {
      console.error("Error al hacer eclosionar el huevo:", err);
      setError("No se pudo eclosionar el huevo. Intenta de nuevo.");
    } finally {
      setHatching(false);
    }
  }, [status?.ready_to_hatch, hatching, authenticated, getAccessToken, onReadyToHatch]);

  // ── Render ────────────────────────────────────────────────────────────────────

  if (!authenticated) {
    return (
      <div className="flex flex-col items-center gap-3 py-8 text-center">
        <p className="text-slate-500 text-sm">Inicia sesión para ver tu huevo.</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex flex-col items-center gap-4 py-10">
        <div className="w-10 h-10 border-4 border-[#00e5ff] border-t-transparent rounded-full animate-spin" />
        <p className="text-slate-400 text-xs font-black uppercase tracking-widest animate-pulse">
          Despertando tu huevo...
        </p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center gap-3 py-8 text-center">
        <p className="text-rose-400 text-sm font-bold">{error}</p>
        <button
          onClick={() => { setError(null); setLoading(true); fetchStatus(); }}
          className="px-4 py-2 bg-rose-900/40 border border-rose-500/30 rounded-xl text-rose-300 text-xs font-black uppercase tracking-widest hover:bg-rose-800/40 transition-colors"
        >
          Reintentar
        </button>
      </div>
    );
  }

  if (!status) return null;

  const { fragments, max_fragments, reaction_stage, dream_bubble, ready_to_hatch } = status;
  const pct = Math.min(100, Math.round((fragments / max_fragments) * 100));
  const stageEmoji = STAGE_EMOJI[reaction_stage] ?? "🥚";
  const stageLabel = STAGE_LABEL[reaction_stage] ?? "Durmiendo";

  return (
    <div className="flex flex-col items-center gap-5 py-6">

      {/* ── Egg with dream bubble ──────────────────────────────────────────── */}
      <div className="relative flex flex-col items-center">

        {/* Dream bubble */}
        {dream_bubble && (
          <div
            aria-live="polite"
            aria-label={`El huevo sueña: ${dream_bubble}`}
            className="absolute -top-12 left-1/2 -translate-x-1/2 whitespace-nowrap px-3 py-1.5 rounded-full text-xs font-bold text-white transition-all duration-700"
            style={{
              opacity: bubbleVisible ? 1 : 0,
              transform: `translateX(-50%) translateY(${bubbleVisible ? 0 : 4}px)`,
              background: "rgba(6,6,20,0.9)",
              border: "1.5px solid rgba(0,229,255,0.4)",
              boxShadow: "0 0 12px rgba(0,229,255,0.2)",
              pointerEvents: "none",
            }}
          >
            {dream_bubble}
            {/* Bubble tail */}
            <span
              aria-hidden="true"
              className="absolute -bottom-[9px] left-1/2 -translate-x-1/2 w-0 h-0"
              style={{
                borderLeft: "7px solid transparent",
                borderRight: "7px solid transparent",
                borderTop: "8px solid rgba(0,229,255,0.4)",
              }}
            />
          </div>
        )}

        {/* Egg emoji */}
        <div
          className={`text-7xl leading-none select-none ${ready_to_hatch ? "animate-egg-shake" : ""}`}
          style={{
            animation: ready_to_hatch
              ? undefined
              : "axo-bob 3s ease-in-out infinite",
            filter: ready_to_hatch
              ? "drop-shadow(0 0 18px rgba(0,229,255,0.8))"
              : "drop-shadow(0 0 6px rgba(0,229,255,0.3))",
          }}
          aria-label={stageEmoji}
          role="img"
        >
          {stageEmoji}
        </div>

        {/* Stage label */}
        <p
          className="mt-2 text-[10px] font-black uppercase tracking-widest"
          style={{ color: ready_to_hatch ? "#00e5ff" : "#64748b" }}
        >
          {stageLabel}
        </p>
      </div>

      {/* ── Fragment progress bar ──────────────────────────────────────────── */}
      <div className="w-full max-w-xs flex flex-col gap-1.5">
        <div className="flex justify-between items-center">
          <span className="text-[10px] text-slate-500 font-black uppercase tracking-widest">
            Fragmentos
          </span>
          <span className="text-[10px] font-black text-slate-300">
            {fragments} / {max_fragments}
          </span>
        </div>

        {/* Track */}
        <div
          className="relative h-3 rounded-full overflow-hidden"
          style={{
            background: "rgba(15,23,42,0.8)",
            border: "1px solid rgba(0,229,255,0.15)",
          }}
        >
          {/* Fill */}
          <div
            className="absolute inset-y-0 left-0 rounded-full transition-all duration-700"
            style={{
              width: `${pct}%`,
              background: ready_to_hatch
                ? "linear-gradient(90deg, #00e5ff, #67e8f9)"
                : "linear-gradient(90deg, #0284c7, #00e5ff)",
              boxShadow: ready_to_hatch
                ? "0 0 12px rgba(0,229,255,0.7)"
                : "0 0 6px rgba(0,229,255,0.3)",
            }}
          />
        </div>

        <p className="text-center text-[10px] text-slate-600">
          {pct}% completado — ve partidas para acumular fragmentos
        </p>
      </div>

      {/* ── Hatch button ───────────────────────────────────────────────────── */}
      {ready_to_hatch && (
        <button
          onClick={handleHatch}
          disabled={hatching}
          aria-label="Despertar al huevo"
          className="px-8 py-3.5 rounded-2xl font-black text-base uppercase tracking-widest text-white transition-all active:scale-95 disabled:opacity-60 disabled:cursor-not-allowed"
          style={{
            background: "linear-gradient(135deg, #00e5ff, #0284c7)",
            boxShadow: "0 0 28px rgba(0,229,255,0.55)",
            animation: "pulse 2s ease-in-out infinite",
          }}
        >
          {hatching ? "Despertando..." : "¡Despertar!"}
        </button>
      )}

      {/* ── Hint when not ready ────────────────────────────────────────────── */}
      {!ready_to_hatch && (
        <p className="text-slate-600 text-[10px] text-center max-w-[200px] leading-relaxed">
          Observa partidas de otros jugadores para acumular fragmentos y despertar a tu Webito.
        </p>
      )}
    </div>
  );
}
