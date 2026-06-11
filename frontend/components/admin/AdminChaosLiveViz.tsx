"use client";
import { useEffect, useState, useRef } from "react";

// ── Zone definitions ──────────────────────────────────────────────────────────
interface ZoneInfo {
  id: string;
  name: string;
  emoji: string;
  row: number;
  col: number;
  isAttack?: boolean;
}

const ZONES: ZoneInfo[] = [
  { id: "shop",        name: "Tienda",       emoji: "🛒", row: 1, col: 1 },
  { id: "tutorial",    name: "Tutorial",     emoji: "📖", row: 1, col: 2 },
  { id: "incubation",  name: "Incubación",   emoji: "🥚", row: 1, col: 3 },
  { id: "solo_game",   name: "Partida Solo", emoji: "🎮", row: 2, col: 1 },
  { id: "multiplayer", name: "Multiplayer",  emoji: "⚔️", row: 2, col: 2 },
  { id: "gashapon",    name: "Gashapon",     emoji: "🎰", row: 2, col: 3 },
  { id: "cave",        name: "Cueva",        emoji: "🏠", row: 3, col: 1 },
  { id: "care",        name: "Cuidado",      emoji: "💤", row: 3, col: 2 },
  { id: "daily",       name: "Daily Rewards",emoji: "🌙", row: 3, col: 3 },
  { id: "idle",        name: "Idle / Think", emoji: "⏳", row: 4, col: 1 },
];

const ATTACK_ZONES: ZoneInfo[] = [
  { id: "replay",    name: "Replay",    emoji: "🔄", row: 0, col: 1, isAttack: true },
  { id: "spoof",     name: "ID Spoof",  emoji: "👤", row: 0, col: 2, isAttack: true },
  { id: "race",      name: "Race Cond", emoji: "⚡", row: 0, col: 3, isAttack: true },
  { id: "booking",   name: "Dbl Book",  emoji: "🎯", row: 0, col: 4, isAttack: true },
  { id: "injection", name: "Injection", emoji: "💉", row: 0, col: 5, isAttack: true },
  { id: "cooldown",  name: "Cooldown",  emoji: "⏱️", row: 0, col: 6, isAttack: true },
];

// ── Activity type from API ────────────────────────────────────────────────────
interface Activity {
  action: string;
  zone: string;
  timestamp?: number;
  color: string;
  type: string;
  personality: string;
  thread_id: string;
}

interface ActivitiesData {
  activities: Record<string, Activity>;
  counters: Record<string, number>;
  stats: Record<string, number>;
}

// ── Dot component ─────────────────────────────────────────────────────────────
function BotDot({ color, label, index }: { color: string; label: string; index: number }) {
  const delay = (index * 0.15) % 2;
  return (
    <div
      className="relative group"
      style={{
        animation: `bounce 0.8s ease-in-out ${delay}s infinite`,
      }}
    >
      <div
        className="w-2.5 h-2.5 rounded-full shadow-lg transition-transform group-hover:scale-150"
        style={{
          backgroundColor: color,
          boxShadow: `0 0 6px ${color}80, 0 0 12px ${color}40`,
        }}
      />
      {/* Tooltip */}
      <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-1 hidden group-hover:block z-50">
        <span className="text-[9px] bg-[#080814] border border-white/10 rounded px-1.5 py-0.5 text-gray-300 whitespace-nowrap">
          {label}
        </span>
      </div>
    </div>
  );
}

// ── Zone component ────────────────────────────────────────────────────────────
function ZoneCard({
  zone,
  bots,
  isAttack,
}: {
  zone: ZoneInfo;
  bots: Activity[];
  isAttack?: boolean;
}) {
  const count = bots.length;
  const isActive = count > 0;

  return (
    <div
      className={`
        relative rounded-xl border p-2.5 transition-all duration-300 min-h-[64px]
        ${isAttack
          ? "border-red-400/20 bg-red-400/5"
          : "border-white/5 bg-[#141428]/60"
        }
        ${isActive && !isAttack ? "border-[#E4007C]/30 bg-[#E4007C]/5" : ""}
        ${isActive && isAttack ? "border-red-400/50 bg-red-400/10 animate-pulse" : ""}
      `}
    >
      {/* Zone header */}
      <div className="flex items-center justify-between mb-1.5">
        <span className="text-[10px] text-gray-500 font-semibold uppercase tracking-wider">
          {zone.emoji} {zone.name}
        </span>
        {count > 0 && (
          <span className={`text-[10px] font-black tabular-nums ${isAttack ? "text-red-400" : "text-[#FF8DA1]"}`}>
            {count}
          </span>
        )}
      </div>

      {/* Dots container */}
      <div className="flex flex-wrap gap-1 items-center min-h-[20px]">
        {bots.slice(0, 40).map((bot, i) => (
          <BotDot
            key={bot.thread_id}
            color={bot.color}
            label={`${bot.thread_id}: ${bot.action}`}
            index={i}
          />
        ))}
        {count > 40 && (
          <span className="text-[9px] text-gray-600 ml-1">+{count - 40}</span>
        )}
        {count === 0 && (
          <span className="text-[9px] text-gray-700">—</span>
        )}
      </div>
    </div>
  );
}

// ── Stats bar ─────────────────────────────────────────────────────────────────
function StatsBar({ counters, stats }: { counters: Record<string, number>; stats: Record<string, number> }) {
  const attackKeys = ["replay", "spoof", "race", "booking", "injection", "cooldown"];
  const totalLaunched = attackKeys.reduce((s, k) => s + (counters[`${k}_launched`] || 0), 0);
  const totalBlocked = attackKeys.reduce((s, k) => s + (counters[`${k}_blocked`] || 0), 0);
  const totalSucceeded = attackKeys.reduce((s, k) => s + (counters[`${k}_succeeded`] || 0), 0);
  const mitigation = totalLaunched > 0 ? ((1 - totalSucceeded / totalLaunched) * 100).toFixed(1) : "—";

  return (
    <div className="flex flex-wrap items-center gap-3 text-[10px] tabular-nums">
      <div className="flex items-center gap-1.5 rounded-lg bg-[#141428] border border-white/5 px-2.5 py-1">
        <span className="text-gray-500">Acciones:</span>
        <span className="text-white font-semibold">{stats?.bot_actions || 0}</span>
      </div>
      <div className="flex items-center gap-1.5 rounded-lg bg-[#141428] border border-white/5 px-2.5 py-1">
        <span className="text-gray-500">Ataques:</span>
        <span className="text-red-400 font-semibold">{totalLaunched}</span>
      </div>
      <div className="flex items-center gap-1.5 rounded-lg bg-[#141428] border border-white/5 px-2.5 py-1">
        <span className="text-gray-500">Bloqueados:</span>
        <span className="text-green-400 font-semibold">{totalBlocked}</span>
      </div>
      {totalSucceeded > 0 && (
        <div className="flex items-center gap-1.5 rounded-lg bg-red-400/10 border border-red-400/20 px-2.5 py-1">
          <span className="text-red-400">Exitosos:</span>
          <span className="text-red-300 font-black">{totalSucceeded}</span>
        </div>
      )}
      <div className="flex items-center gap-1.5 rounded-lg bg-[#141428] border border-white/5 px-2.5 py-1">
        <span className="text-gray-500">Mitigación:</span>
        <span className="text-[#FF8DA1] font-semibold">{mitigation}%</span>
      </div>
      <div className="flex items-center gap-1.5 rounded-lg bg-[#141428] border border-white/5 px-2.5 py-1">
        <span className="text-gray-500">500s:</span>
        <span className={stats?.bot_500s > 0 ? "text-yellow-400 font-semibold" : "text-green-400 font-semibold"}>
          {stats?.bot_500s || 0}
        </span>
      </div>
    </div>
  );
}

// ── Main Viz component ────────────────────────────────────────────────────────
interface Props {
  activities: Record<string, Activity>;
  counters: Record<string, number>;
  stats: Record<string, number>;
}

export default function AdminChaosLiveViz({ activities, counters, stats }: Props) {
  const activityList = Object.values(activities || {});

  // Group bots by zone
  function getBotsInZone(zoneId: string): Activity[] {
    return activityList.filter(a => a.zone === zoneId);
  }

  // Total active bots
  const botCount = activityList.filter(a => a.type === "bot").length;
  const attackCount = activityList.filter(a => a.type === "attack").length;

  return (
    <div className="space-y-3">
      {/* CSS animation for dot bounce */}
      <style>{`
        @keyframes bounce {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-2px); }
        }
        @keyframes pulse-glow {
          0%, 100% { box-shadow: 0 0 5px rgba(239,68,68,0.3); }
          50% { box-shadow: 0 0 15px rgba(239,68,68,0.6); }
        }
      `}</style>

      {/* Header with live counters */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="relative flex h-2.5 w-2.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#E4007C] opacity-75" />
            <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-[#E4007C]" />
          </div>
          <h3 className="text-xs font-black text-white uppercase tracking-wider">Mapa de Actividad</h3>
        </div>
        <div className="flex items-center gap-3 text-[10px]">
          <span className="text-gray-500">
            <span className="text-white font-semibold">{botCount}</span> bots activos
          </span>
          {attackCount > 0 && (
            <span className="text-red-400">
              <span className="font-semibold">{attackCount}</span> ataques
            </span>
          )}
        </div>
      </div>

      {/* Stats bar */}
      <StatsBar counters={counters} stats={stats} />

      {/* Attack zones row */}
      <div className="grid grid-cols-6 gap-2">
        {ATTACK_ZONES.map(zone => (
          <ZoneCard
            key={zone.id}
            zone={zone}
            bots={getBotsInZone(zone.id)}
            isAttack
          />
        ))}
      </div>

      {/* Main zones grid — 3 columns */}
      <div className="grid grid-cols-3 gap-2">
        {ZONES.filter(z => z.id !== "idle").map(zone => (
          <ZoneCard
            key={zone.id}
            zone={zone}
            bots={getBotsInZone(zone.id)}
          />
        ))}
      </div>

      {/* Idle zone — full width */}
      <div>
        <ZoneCard
          zone={ZONES.find(z => z.id === "idle")!}
          bots={getBotsInZone("idle")}
        />
      </div>

      {/* Legend */}
      <div className="flex items-center gap-4 text-[9px] text-gray-600 flex-wrap">
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 rounded-full bg-[#6366F1]" /> Whale
        </span>
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 rounded-full bg-[#10B981]" /> Collector
        </span>
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 rounded-full bg-[#9CA3AF]" /> Free2Play
        </span>
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 rounded-full bg-[#EF4444] animate-pulse" /> Attack Agent
        </span>
      </div>
    </div>
  );
}
