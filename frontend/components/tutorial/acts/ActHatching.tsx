"use client";

/**
 * ActHatching — Egg burst → Axolotito birth.
 * Calls POST /api/v1/tutorial/complete before animation.
 * Shows birth cry per nature after hatching, then the axolotito name.
 */

import React, { useState, useEffect, useCallback } from "react";
import WebitoDialogue from "../WebitoDialogue";
import type { WebitoData } from "../TutorialScript";
import { ACT9_BIRTH_CRY, ACT9_STATS_LOCKED } from "../dialogues";
import { API_BASE } from "@/lib/api";

type HatchPhase = "bursting" | "born" | "cry" | "stats";

interface Props {
  webito: WebitoData;
  onComplete: (axoName: string) => void;
}

interface FinalStats {
  suerte: number;
  ojo: number;
  pila: number;
  sal: number;
}

export default function ActHatching({ webito, onComplete }: Props) {
  const [phase, setPhase] = useState<HatchPhase>("bursting");
  const [axolotitoName, setAxolotitoName] = useState<string | null>(null);
  const axoNameRef = React.useRef<string>("Axolotito");
  const [apiOk, setApiOk] = useState<boolean | null>(null);
  const [finalStats, setFinalStats] = useState<FinalStats | null>(null);

  useEffect(() => {
    let cancelled = false;
    // Complete tutorial in backend → auto-eclosiona y devuelve el nombre del axolotito
    const complete = async () => {
      try {
        console.log("🥚 ActHatching: llamando POST /tutorial/complete/", webito.tutorialId);
        const headers: Record<string, string> = { "Content-Type": "application/json" };
        if (webito.token) headers["Authorization"] = `Bearer ${webito.token}`;
        const res = await fetch(`${API_BASE}/tutorial/complete/${webito.tutorialId}`, {
          method: "POST",
          headers,
        });

        // ✅ Verificar respuesta del backend
        if (!res.ok) {
          const errText = await res.text().catch(() => "Unknown error");
          console.error(`❌ Tutorial complete falló (${res.status}): ${errText}`);
          if (!cancelled) setApiOk(false);
          return;
        }

        const data = await res.json();
        console.log("✅ Tutorial complete respuesta:", JSON.stringify(data));

        if (!cancelled && data?.axolotito_name) {
          axoNameRef.current = data.axolotito_name;
          setAxolotitoName(data.axolotito_name);
          setApiOk(true);
          // Extract final stats from hatch response
          if (data.axolotito?.stats) {
            setFinalStats({
              suerte: data.axolotito.stats.suerte,
              ojo: data.axolotito.stats.ojo,
              pila: data.axolotito.stats.pila,
              sal: data.axolotito.stats.sal,
            });
          }
          console.log("🐣 Axolotito eclosionado:", data.axolotito_name);
        } else if (!cancelled) {
          console.warn("⚠️ complete no devolvió axolotito_name. Data:", data);
          setApiOk(false);
        }
      } catch (e) {
        console.error("❌ Error de red en tutorial complete:", e);
        if (!cancelled) setApiOk(false);
      }
    };
    complete();

    // Burst animation → born
    const t1 = setTimeout(() => setPhase("born"), 2000);
    // After born, show cry
    const t2 = setTimeout(() => setPhase("cry"), 2800);
    return () => { clearTimeout(t1); clearTimeout(t2); };
  }, [webito.token, webito.tutorialId]);

  const handleCryDismiss = useCallback(() => setPhase("stats"), []);
  const handleStatsDismiss = useCallback(() => onComplete(axoNameRef.current), [onComplete]);

  // ── Helper: axolotito name display ──────────────────────────────────────────
  const nameDisplay = axolotitoName || axoNameRef.current;
  const nameKnown = axolotitoName !== null;

  return (
    <div className="flex flex-col items-center justify-center gap-6 py-16 text-center px-3">
      {/* Animated egg / axolotito */}
      <div className="relative flex items-center justify-center w-40 h-40">
        {phase === "bursting" && (
          <div
            aria-hidden="true"
            className="text-8xl leading-none select-none absolute"
            style={{ animation: "egg-hatch-burst 2s cubic-bezier(0.36,0.07,0.19,0.97) forwards" }}
          >
            🥚
          </div>
        )}
        {(phase === "born" || phase === "cry" || phase === "stats") && (
          <div
            aria-label="¡Tu Axolotito ha nacido!"
            role="img"
            className="text-8xl leading-none select-none"
            style={{
              animation: "axolotito-appear 0.7s cubic-bezier(0.34,1.56,0.64,1) both",
              filter: "drop-shadow(0 0 24px rgba(52,211,153,0.7))",
            }}
          >
            🦎
          </div>
        )}
      </div>

      {/* Title + name */}
      <div className="space-y-2">
        <h2
          className="text-3xl font-black uppercase tracking-tighter"
          style={{
            background: phase === "bursting"
              ? "linear-gradient(135deg, #fbbf24, #f97316)"
              : "linear-gradient(135deg, #34d399, #00e5ff)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
          }}
        >
          {phase === "bursting" ? "Eclosionando..." : "¡Tu Axolotito ha nacido!"}
        </h2>
        {phase === "bursting" && (
          <p className="text-slate-500 text-xs animate-pulse">Preparando al nuevo ser...</p>
        )}
        {/* Show axolotito name once known */}
        {phase !== "bursting" && nameKnown && (
          <p
            className="text-xl font-black tracking-tight animate-fade-in"
            style={{
              background: "linear-gradient(135deg, #fbbf24, #34d399)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
              filter: "drop-shadow(0 0 8px rgba(52,211,153,0.4))",
            }}
          >
            ✨ {nameDisplay} ✨
          </p>
        )}
        {/* API failed warning */}
        {phase !== "bursting" && apiOk === false && (
          <p className="text-amber-400 text-xs font-bold animate-pulse">
            ⚠️ No se pudo conectar con el servidor. El nombre se asignará al reconectar.
          </p>
        )}
      </div>

      {/* Dialogues */}
      {phase === "cry" && (
        <div className="w-full max-w-sm">
          <WebitoDialogue
            text={ACT9_BIRTH_CRY[webito.nature]}
            speaker="axo"
            onDismiss={handleCryDismiss}
          />
        </div>
      )}

      {phase === "stats" && (
        <div className="w-full max-w-sm space-y-4">
          {/* Final Stats Card */}
          {finalStats && (
            <div
              className="w-full rounded-2xl overflow-hidden animate-fade-in"
              style={{
                background: "rgba(6,6,20,0.85)",
                border: "1px solid rgba(52,211,153,0.25)",
                boxShadow: "0 0 30px rgba(52,211,153,0.1)",
              }}
            >
              <div
                className="px-4 py-2 flex items-center gap-2"
                style={{ borderBottom: "1px solid rgba(255,255,255,0.06)" }}
              >
                <span className="text-lg">🦎</span>
                <p className="text-xs font-black uppercase tracking-widest" style={{ color: "#34d399" }}>
                  Stats Finales
                </p>
              </div>
              <div className="p-4 space-y-3">
                {[
                  { emoji: "🧂", label: "SAL",    value: finalStats.sal,    color: "#00e5ff", glow: "rgba(0,229,255,0.4)" },
                  { emoji: "👁️",  label: "OJO",    value: finalStats.ojo,    color: "#818cf8", glow: "rgba(129,140,248,0.4)" },
                  { emoji: "🔋", label: "PILA",   value: finalStats.pila,   color: "#34d399", glow: "rgba(52,211,153,0.4)" },
                  { emoji: "✨", label: "SUERTE", value: finalStats.suerte,  color: "#fbbf24", glow: "rgba(251,191,36,0.4)" },
                ].map((stat) => {
                  const maxVal = stat.label === "PILA" ? 200 : 100;
                  const pct = Math.min(100, Math.round((stat.value / maxVal) * 100));
                  return (
                    <div key={stat.label}>
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-sm">{stat.emoji}</span>
                        <span className="text-[10px] font-black uppercase tracking-widest" style={{ color: stat.color }}>
                          {stat.label}
                        </span>
                        <span className="ml-auto text-sm font-black tabular-nums" style={{ color: stat.color }}>
                          {Math.round(stat.value)}
                        </span>
                      </div>
                      <div className="h-1.5 rounded-full overflow-hidden" style={{ background: "rgba(255,255,255,0.06)" }}>
                        <div
                          className="h-full rounded-full transition-all duration-700"
                          style={{
                            width: `${pct}%`,
                            background: `linear-gradient(90deg, ${stat.color}88, ${stat.color})`,
                            boxShadow: `0 0 6px ${stat.glow}`,
                          }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Dialogue + dismiss */}
          <WebitoDialogue
            text={ACT9_STATS_LOCKED[webito.nature]}
            speaker="axo"
            onDismiss={handleStatsDismiss}
          />
        </div>
      )}
    </div>
  );
}
