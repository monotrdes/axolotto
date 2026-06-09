"use client";

/**
 * ActTreasureChest — Cofre del Tesoro (acto final del tutorial).
 *
 * Muestra un cofre animado que se abre al entrar y revela el premio Corcholata.
 * Llama POST /api/v1/rewards/claim para reclamar el premio pendiente.
 *
 * Si no hay hasPendingReward, salta automáticamente con onComplete().
 */

import React, { useState, useEffect, useCallback } from "react";
import { usePrivy } from "@privy-io/react-auth";
import { API_BASE } from "@/lib/api";

type ChestPhase = "chest_closed" | "chest_opening" | "rewards_revealed";

interface Props {
  hasPendingReward: boolean;
  token: string | null;
  onComplete: () => void;
}

export default function ActTreasureChest({ hasPendingReward, token, onComplete }: Props) {
  const { getAccessToken, authenticated } = usePrivy();
  const [phase, setPhase] = useState<ChestPhase>("chest_closed");
  const [reward, setReward] = useState<{
    axofichas: number;
    frijolitos: number;
    item_id: string | null;
  } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [claiming, setClaiming] = useState(false);

  // Auto-claim on mount if hasPendingReward
  useEffect(() => {
    if (!hasPendingReward) {
      // No pending reward — skip after short delay
      const t = setTimeout(() => onComplete(), 800);
      return () => clearTimeout(t);
    }

    // Start chest opening animation
    const t1 = setTimeout(() => setPhase("chest_opening"), 1200);
    const t2 = setTimeout(async () => {
      if (claiming) return;
      setClaiming(true);

      try {
        const t = token ?? (authenticated ? await getAccessToken() : null);
        const headers: Record<string, string> = { "Content-Type": "application/json" };
        if (t) headers["Authorization"] = `Bearer ${t}`;

        const res = await fetch(`${API_BASE}/rewards/claim`, {
          method: "POST",
          headers,
        });

        if (!res.ok) {
          const errData = await res.json().catch(() => ({}));
          console.error("❌ Error reclamando premio:", res.status, errData);
          setError(errData.detail ?? "Error al reclamar el premio");
          setPhase("rewards_revealed");
          return;
        }

        const data = await res.json();
        console.log("✅ Premio reclamado:", data);
        setReward(data.reward);
        setPhase("rewards_revealed");
      } catch (e) {
        console.error("❌ Error de red en claim:", e);
        setError("Error de conexión al reclamar");
        setPhase("rewards_revealed");
      }
    }, 2800);

    return () => { clearTimeout(t1); clearTimeout(t2); };
  }, [hasPendingReward]);

  const handleContinue = useCallback(() => {
    onComplete();
  }, [onComplete]);

  // ── No pending reward — brief placeholder ────────────────────────────────
  if (!hasPendingReward) {
    return (
      <div className="flex flex-col items-center justify-center gap-4 py-20">
        <p className="text-slate-500 text-sm">Preparando tu aventura...</p>
      </div>
    );
  }

  // ── Chest closed ─────────────────────────────────────────────────────────
  if (phase === "chest_closed") {
    return (
      <div className="flex flex-col items-center gap-6 py-16 text-center px-3">
        <div className="text-8xl animate-bounce select-none">🔒</div>
        <h2 className="text-3xl font-black uppercase tracking-tighter"
          style={{ background: "linear-gradient(135deg, #fbbf24, #f97316)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>
          Cofre del Tesoro
        </h2>
        <p className="text-slate-400 text-sm">Tu premio Corcholata está a punto de revelarse...</p>
        <div className="flex gap-1.5">
          {[0, 1, 2].map(i => (
            <div key={i} className="w-2 h-2 rounded-full animate-bounce bg-yellow-400"
              style={{ animationDelay: `${i * 200}ms` }} />
          ))}
        </div>
      </div>
    );
  }

  // ── Chest opening ────────────────────────────────────────────────────────
  if (phase === "chest_opening") {
    return (
      <div className="flex flex-col items-center gap-6 py-16 text-center px-3">
        <div className="text-8xl select-none"
          style={{ animation: "chest-open 1.6s cubic-bezier(0.34,1.56,0.64,1) forwards" }}>
          🎁
        </div>
        <h2 className="text-3xl font-black uppercase tracking-tighter text-yellow-400">
          Abriendo cofre...
        </h2>
        <div className="flex gap-1.5">
          {[0, 1, 2].map(i => (
            <div key={i} className="w-2.5 h-2.5 rounded-full animate-pulse bg-yellow-400"
              style={{ animationDelay: `${i * 150}ms` }} />
          ))}
        </div>
        {/* Gold particles */}
        <div aria-hidden="true" className="absolute inset-0 pointer-events-none overflow-hidden">
          {Array.from({ length: 12 }).map((_, i) => (
            <div key={i} className="absolute w-1.5 h-1.5 rounded-full bg-yellow-400/60"
              style={{
                left: `${20 + Math.random() * 60}%`,
                top: `${30 + Math.random() * 40}%`,
                animation: `particle-float ${1.5 + Math.random() * 2}s ease-out ${Math.random() * 0.8}s both`,
              }} />
          ))}
        </div>
      </div>
    );
  }

  // ── Rewards revealed ─────────────────────────────────────────────────────
  const hasError = error && !reward;

  return (
    <div className="flex flex-col items-center gap-5 py-10 text-center px-3">
      <div className="text-7xl select-none"
        style={{ filter: "drop-shadow(0 0 20px rgba(251,191,36,0.6))" }}>
        {hasError ? "😵" : "🎉"}
      </div>
      <h2 className="text-3xl font-black uppercase tracking-tighter"
        style={{ background: "linear-gradient(135deg, #fbbf24, #34d399)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>
        {hasError ? "Algo salió mal" : "¡Premio Revelado!"}
      </h2>

      {hasError ? (
        <p className="text-red-400 text-sm">{error}</p>
      ) : reward ? (
        <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-2xl p-5 space-y-3 w-full max-w-xs">
          <div className="flex justify-between items-center py-1">
            <span className="flex items-center gap-2 text-sm">🪙 Axofichas</span>
            <span className="font-black text-lg text-yellow-400">+{reward.axofichas} AXF</span>
          </div>
          <div className="flex justify-between items-center py-1 border-t border-yellow-500/10">
            <span className="flex items-center gap-2 text-sm">🌿 Frijolitos</span>
            <span className="font-black text-lg text-yellow-400">+{reward.frijolitos} FRJ</span>
          </div>
          {reward.item_id && (
            <div className="flex justify-between items-center py-1 border-t border-yellow-500/10">
              <span className="flex items-center gap-2 text-sm">🎁 Ítem exclusivo</span>
              <span className="font-black text-lg text-purple-400">1 und</span>
            </div>
          )}
        </div>
      ) : (
        <p className="text-slate-400 text-sm">Cargando recompensas...</p>
      )}

      <button
        onClick={handleContinue}
        className="w-full max-w-sm py-4 rounded-2xl font-black text-base uppercase tracking-widest text-white transition-all active:scale-95"
        style={{
          background: "linear-gradient(135deg, #fbbf24, #f97316)",
          boxShadow: "0 0 28px rgba(251,191,36,0.4)",
        }}
      >
        Continuar →
      </button>
    </div>
  );
}
