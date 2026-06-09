"use client";
import { useEffect, useState } from "react";

interface BirthStats {
  suerte: number;
  ojo: number;
  pila: number;
  sal: number;
}

interface Props {
  axolotitoName: string;
  nature: string;
  natureIcon: string;
  stats: BirthStats;
  rarity: "common" | "rare" | "legendary";
  padrinoName: string;
  gamesWon: number;
  totalGames: number;
  onComplete: () => void;
}

const NATURE_COLORS: Record<string, string> = {
  suertudo: "#fbbf24",
  metodico: "#2dd4bf",
  gloton: "#f97316",
  timido: "#a78bfa",
  hiperactivo: "#f87171",
  sabio: "#60a5fa",
};

const STAT_CONFIG = [
  { key: "suerte" as const, icon: "✨", label: "SUERTE", color: "#fbbf24" },
  { key: "ojo" as const, icon: "👁️", label: "OJO", color: "#2dd4bf" },
  { key: "pila" as const, icon: "🔋", label: "PILA", color: "#60a5fa" },
  { key: "sal" as const, icon: "🧂", label: "SAL", color: "#f87171" },
];

type Step = "dark" | "crack" | "name" | "nature" | "stats" | "flavor" | "done";

export function BirthCeremony({
  axolotitoName,
  nature,
  natureIcon,
  stats,
  rarity,
  padrinoName,
  gamesWon,
  totalGames,
  onComplete,
}: Props) {
  const [step, setStep] = useState<Step>("dark");
  const [revealedStats, setRevealedStats] = useState<number>(0);
  const [displayName, setDisplayName] = useState("");

  const STEPS: Step[] = [
    "dark",
    "crack",
    "name",
    "nature",
    "stats",
    "flavor",
    "done",
  ];
  const stepDelay: Record<Step, number> = {
    dark: 1800,
    crack: 1500,
    name: 2000,
    nature: 2000,
    stats: 4 * 800 + 1200,
    flavor: 2500,
    done: 0,
  };

  useEffect(() => {
    if (step === "done") return;
    const idx = STEPS.indexOf(step);
    const delay = stepDelay[step];
    const timer = setTimeout(
      () => setStep(STEPS[idx + 1] as Step),
      delay
    );
    return () => clearTimeout(timer);
  }, [step]);

  // Typewriter for name
  useEffect(() => {
    if (step !== "name") return;
    let i = 0;
    setDisplayName("");
    const interval = setInterval(() => {
      setDisplayName(axolotitoName.slice(0, i + 1));
      i++;
      if (i >= axolotitoName.length) clearInterval(interval);
    }, 120);
    return () => clearInterval(interval);
  }, [step, axolotitoName]);

  // Stats reveal one by one
  useEffect(() => {
    if (step !== "stats") return;
    setRevealedStats(0);
    let i = 0;
    const interval = setInterval(() => {
      setRevealedStats(i + 1);
      i++;
      if (i >= 4) clearInterval(interval);
    }, 800);
    return () => clearInterval(interval);
  }, [step]);

  const natureColor = NATURE_COLORS[nature?.toLowerCase()] ?? "#a78bfa";
  const isLegendary = rarity === "legendary";

  return (
    <div
      className="fixed inset-0 flex flex-col items-center justify-center z-50"
      style={{
        background:
          step === "dark"
            ? "#000"
            : `radial-gradient(ellipse at 50% 80%, ${natureColor}18 0%, #050508 70%)`,
        transition: "background 1s ease",
      }}
    >
      {/* Steps 1-2: Egg */}
      {(step === "dark" || step === "crack") && (
        <div
          className="text-8xl transition-all duration-700"
          style={{
            filter:
              step === "crack"
                ? `drop-shadow(0 0 30px ${natureColor})`
                : "none",
            transform: step === "crack" ? "scale(1.15)" : "scale(1)",
          }}
        >
          {step === "dark" ? "🥚" : "✨"}
        </div>
      )}

      {/* Steps 3+: Full reveal */}
      {step !== "dark" && step !== "crack" && (
        <div className="flex flex-col items-center gap-5 px-6 max-w-sm w-full">
          {/* Axolotito */}
          <div
            className="text-7xl"
            style={{
              filter: `drop-shadow(0 0 ${isLegendary ? 40 : 20}px ${natureColor})`,
            }}
          >
            🦎
          </div>

          {/* Name */}
          <div className="text-3xl font-black text-white tracking-wide min-h-[2.5rem]">
            {displayName}
            {step === "name" && (
              <span className="animate-pulse">|</span>
            )}
          </div>

          {/* Nature */}
          {["nature", "stats", "flavor", "done"].includes(step) && (
            <div
              className="text-sm font-bold uppercase tracking-widest px-4 py-1.5 rounded-full"
              style={{
                background: `${natureColor}20`,
                color: natureColor,
                border: `1px solid ${natureColor}40`,
              }}
            >
              {natureIcon} Naturaleza {nature}
            </div>
          )}

          {/* Stats as lotería cards */}
          {["stats", "flavor", "done"].includes(step) && (
            <div className="flex gap-3 justify-center w-full">
              {STAT_CONFIG.map((s, i) => (
                <div
                  key={s.key}
                  className="flex-1 flex flex-col items-center gap-1 py-3 rounded-2xl transition-all duration-500"
                  style={{
                    background:
                      i < revealedStats
                        ? `${s.color}18`
                        : "rgba(255,255,255,0.03)",
                    border: `1.5px solid ${
                      i < revealedStats
                        ? s.color + "40"
                        : "rgba(255,255,255,0.08)"
                    }`,
                    opacity: i < revealedStats ? 1 : 0.2,
                    transform:
                      i < revealedStats ? "scale(1)" : "scale(0.9)",
                  }}
                >
                  <span className="text-xl">{s.icon}</span>
                  <span className="text-[10px] font-bold uppercase opacity-50">
                    {s.label}
                  </span>
                  <span
                    className="text-xl font-black"
                    style={{
                      color:
                        i < revealedStats ? s.color : "transparent",
                    }}
                  >
                    {stats[s.key]}
                  </span>
                  {s.key === "sal" &&
                    i < revealedStats &&
                    stats.sal < 15 && (
                      <span className="text-[9px] text-green-400 font-bold">
                        ¡Bajo!
                      </span>
                    )}
                </div>
              ))}
            </div>
          )}

          {/* Flavor text */}
          {(step === "flavor" || step === "done") && (
            <p className="text-sm text-white/35 italic text-center leading-relaxed">
              "Aprendió jugando con {padrinoName}. Ganaron {gamesWon} de{" "}
              {totalGames} partidas."
            </p>
          )}

          {/* Final button */}
          {step === "done" && (
            <button
              onClick={onComplete}
              className="mt-2 px-8 py-3 rounded-2xl font-bold text-sm transition-all"
              style={{
                background: `${natureColor}20`,
                border: `1.5px solid ${natureColor}40`,
                color: natureColor,
              }}
            >
              Conocer a {axolotitoName} →
            </button>
          )}
        </div>
      )}
    </div>
  );
}
