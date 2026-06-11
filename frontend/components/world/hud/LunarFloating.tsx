"use client";
import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useToast } from '@/context/ToastContext';
import BottomSheet from '@/components/ui/BottomSheet';
import { fetchLunarStatus, claimLunarDay } from '@/services/rewardsService';
import type { LunarStatus } from '@/types/economy';

interface LunarFloatingProps {
  token: string | null;
  onSuccess?: () => void;
}

// ── Lunar phase config ─────────────────────────────────────────────
const LUNA_EMOJI: Record<number, string> = {
  1: '🌑', 2: '🌒', 3: '🌓', 4: '🌔', 5: '🌕', 6: '🌟',
};
const LUNA_NAME: Record<number, string> = {
  1: 'Luna Nueva', 2: 'Creciente', 3: 'Cuarto',
  4: 'Gibosa', 5: 'Llena', 6: 'Axoluna ✨',
};
const LUNA_COLOR: Record<number, string> = {
  1: '#94A3B8', 2: '#A78BFA', 3: '#818CF8',
  4: '#C084FC', 5: '#E879F9', 6: '#FACC15',
};
const DAILY_FRJ = [50, 65, 80, 95, 110, 130];

export default function LunarFloating({ token, onSuccess }: LunarFloatingProps) {
  const { toast } = useToast();
  const [status, setStatus] = useState<LunarStatus | null>(null);
  const [claiming, setClaiming] = useState(false);
  const [sheetOpen, setSheetOpen] = useState(false);
  const [countdown, setCountdown] = useState('');
  const countdownRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const loadStatus = useCallback(async () => {
    if (!token) return;
    try {
      const data = await fetchLunarStatus(token);
      setStatus(data);
    } catch { /* silent */ }
  }, [token]);

  useEffect(() => { loadStatus(); }, [loadStatus]);

  // Listen for open-lunar-sheet from gashapon
  useEffect(() => {
    const handler = () => setSheetOpen(true);
    window.addEventListener('open-lunar-sheet', handler);
    return () => window.removeEventListener('open-lunar-sheet', handler);
  }, []);

  // Countdown
  useEffect(() => {
    if (countdownRef.current) clearInterval(countdownRef.current);
    if (!status || status.can_claim || !status.next_claim_at) {
      setCountdown('');
      return;
    }
    const tick = () => {
      const diff = new Date(status.next_claim_at!).getTime() - Date.now();
      if (diff <= 0) { setCountdown(''); loadStatus(); return; }
      const h = Math.floor(diff / 3_600_000);
      const m = Math.floor((diff % 3_600_000) / 60_000);
      const s = Math.floor((diff % 60_000) / 1000);
      setCountdown(`${h}h ${m}m ${s}s`);
    };
    tick();
    countdownRef.current = setInterval(tick, 1000);
    return () => { if (countdownRef.current) clearInterval(countdownRef.current); };
  }, [status?.can_claim, status?.next_claim_at, loadStatus]);

  const handleClaim = async () => {
    if (!token || claiming || !status?.can_claim) return;
    setClaiming(true);
    try {
      const res = await claimLunarDay(token);
      if (res.type === 'frj') {
        toast.ok(`🪙 +${res.amount?.toFixed(0)} FRJ — ¡Día ${res.streak_day} de 7!`);
      } else {
        const rolls = res.rolls as any[] | undefined;
        const summary = rolls?.map((r: any) => r.name || r.tier || '🎁').join(', ') || 'Cápsula';
        toast.ok(`🎰 ¡${summary}! — Luna ${res.lunar_week} ${res.cycle_complete ? '· ¡Ciclo completado! 🌟' : ''}`);
      }
      if (onSuccess) onSuccess();
      await loadStatus();
    } catch (e: any) {
      const detail = e.response?.data?.detail || 'Error al reclamar recompensa diaria';
      toast.error(detail);
    } finally { setClaiming(false); }
  };

  if (!token || !status) return null;

  // Only show floating button when there's something to claim
  if (!status.can_claim) return null;

  const { lunar_week, streak_day, today_reward, day7_reward, luna_track, cycles_completed } = status;
  const lunaEmoji = LUNA_EMOJI[lunar_week] || '🌑';
  const lunaColor = LUNA_COLOR[lunar_week] || '#A855F7';
  const nextDay = streak_day + 1;
  const isCapsuleDay = nextDay === 7;

  return (
    <>
      {/* Floating claim button — only visible when can_claim */}
      <div className="fixed bottom-36 right-4 z-40">
        <button
          onClick={() => setSheetOpen(true)}
          className="rounded-full flex items-center justify-center text-2xl
                     bg-gradient-to-br from-purple-600 via-indigo-600 to-violet-600
                     border-2 border-purple-400/40 backdrop-blur-sm
                     hover:scale-110 hover:rotate-[6deg] active:scale-95
                     transition-all duration-200 shadow-lg shadow-purple-500/40
                     animate-pulse"
          title="¡Recompensa lunar disponible!"
          aria-label="Reclamar recompensa del ciclo lunar"
          style={{ width: '52px', height: '52px' }}
        >
          <span className="relative">
            {lunaEmoji}
            <span className="absolute -top-0.5 -right-0.5 w-3 h-3 rounded-full bg-purple-400 animate-ping" />
            <span className="absolute -top-0.5 -right-0.5 w-3 h-3 rounded-full bg-purple-400" />
          </span>
        </button>
      </div>

      {/* Bottom sheet — same detail view as DailyClaim */}
      <BottomSheet open={sheetOpen} onClose={() => setSheetOpen(false)} accent={lunaColor}>
        <div className="p-5">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <span className="text-2xl">{'🎁'}</span>
              <div>
                <h3 className="text-base font-black text-purple-300 uppercase tracking-tight">Ciclo Lunar</h3>
                <p className="text-[10px] text-slate-500 font-bold">
                  {isCapsuleDay
                    ? '🎰 ¡Día de Cápsula! Reclama tu premio.'
                    : `¡Hoy puedes reclamar +${today_reward.amount?.toFixed(0)} FRJ!`}
                </p>
              </div>
            </div>
            {cycles_completed > 0 && (
              <div className="text-center bg-purple-950/50 border border-purple-500/30 rounded-xl px-2.5 py-1">
                <span className="text-[7px] text-purple-400 font-black uppercase tracking-wider block">Ciclos</span>
                <span className="text-sm font-black text-purple-300">🏆 {cycles_completed}</span>
              </div>
            )}
          </div>

          {/* Luna track */}
          <div className="flex items-center justify-center gap-2 sm:gap-3 mb-3">
            {(luna_track || []).map((luna: any) => {
              const isCompleted = luna.completed;
              const isCurrent = luna.is_current;
              return (
                <div key={luna.luna} className={`flex flex-col items-center gap-0.5 transition-all ${isCurrent ? 'scale-125' : ''}`}
                  title={`Luna ${luna.luna}: ${luna.reward_label}`}>
                  <span className={`text-sm sm:text-base transition-all ${isCompleted || isCurrent ? '' : 'opacity-20 grayscale'} ${isCurrent ? 'animate-pulse drop-shadow-[0_0_8px_rgba(168,85,247,0.8)]' : ''}`}>
                    {LUNA_EMOJI[luna.luna]}
                  </span>
                  <div className={`w-1.5 h-1.5 rounded-full transition-all ${
                    isCompleted ? 'bg-emerald-500 shadow-[0_0_6px_rgba(52,211,153,0.6)]'
                    : isCurrent ? 'bg-purple-400 shadow-[0_0_6px_rgba(168,85,247,0.6)]'
                    : 'bg-slate-700'}`} />
                  <span className="text-[7px] font-bold text-slate-600">{luna.reward_label.split(' ')[0]}</span>
                </div>
              );
            })}
          </div>

          <p className="text-center text-[9px] text-slate-600 font-bold uppercase tracking-wider mb-4">
            {LUNA_EMOJI[lunar_week]} {LUNA_NAME[lunar_week]} · Día {nextDay} de 7
          </p>

          {/* 7-day week grid */}
          <div className="flex gap-1.5 mb-5 justify-center">
            {Array.from({ length: 7 }, (_, i) => {
              const dayNum = i + 1;
              const isCompleted = dayNum <= streak_day;
              const isToday = dayNum === nextDay;
              const isCapsule = dayNum === 7;
              let bgClass = 'bg-slate-900/60 text-slate-500 border-slate-800';
              let glowStyle: React.CSSProperties = {};
              let content: React.ReactNode = null;
              let subLabel = '';
              if (isToday) {
                bgClass = 'bg-purple-500 text-white border-purple-300/50';
                glowStyle = { boxShadow: '0 0 18px rgba(168,85,247,0.5)' };
                content = <span className="text-sm">★</span>;
                subLabel = isCapsule ? day7_reward?.label || 'Cápsula' : `${DAILY_FRJ[i]} FRJ`;
              } else if (isCompleted) {
                bgClass = 'bg-emerald-600/80 text-white border-emerald-400/30';
                content = <span className="text-xs">✓</span>;
                subLabel = isCapsule ? '🎁' : `${DAILY_FRJ[i]}`;
              } else if (isCapsule) {
                bgClass = 'bg-cyan-950/60 text-cyan-300 border-cyan-500/40';
                glowStyle = { boxShadow: '0 0 10px rgba(34,211,238,0.2)' };
                content = <span className="text-base">🎰</span>;
                subLabel = day7_reward?.label || '???';
              } else {
                content = <span className="text-[10px]">{dayNum}</span>;
                subLabel = isCapsule ? '🎁' : `${DAILY_FRJ[i]}`;
              }
              return (
                <div key={dayNum}
                  className={`flex-1 aspect-square rounded-xl border flex flex-col items-center justify-center font-black transition-all relative ${bgClass}`}
                  style={glowStyle}>
                  {content}
                  <span className={`text-[7px] font-bold mt-0.5 ${isToday ? 'text-white/80' : isCompleted ? 'text-white/60' : 'text-current opacity-50'}`}>
                    {subLabel}
                  </span>
                  <span className="absolute -top-1.5 -right-1.5 w-4 h-4 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-[7px] font-black text-slate-400">
                    {dayNum}
                  </span>
                </div>
              );
            })}
          </div>

          {/* Today reward */}
          <div className="text-center mb-5">
            {today_reward.type === 'frj' ? (
              <div>
                <p className="text-[11px] text-slate-400 font-bold mb-1">
                  Hoy reclamas <span className="text-purple-300 font-black text-sm">+{today_reward.amount?.toFixed(0)} FRJ</span>
                </p>
                {!isCapsuleDay && (
                  <p className="text-[9px] text-slate-600 font-bold">
                    El día 7 te espera: <span className="text-cyan-400">{day7_reward?.label}</span>
                  </p>
                )}
              </div>
            ) : (
              <p className="text-[11px] text-slate-400 font-bold">
                ¡Día 7! Reclamas <span className="text-cyan-300 font-black text-sm">{day7_reward?.label}</span>
              </p>
            )}
          </div>

          {/* Claim button */}
          <button
            onClick={handleClaim}
            disabled={claiming}
            className="w-full py-3.5 bg-gradient-to-r from-purple-600 via-indigo-600 to-purple-600 hover:from-purple-500 hover:via-indigo-500 hover:to-purple-500 text-white font-black rounded-2xl uppercase tracking-widest text-xs shadow-lg shadow-purple-600/30 active:scale-95 transition-all disabled:opacity-50 mb-3"
          >
            {claiming ? (
              <span className="flex items-center justify-center gap-2">
                <span className="inline-block w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Reclamando…
              </span>
            ) : today_reward.type === 'frj' ? (
              `🎁 ¡Reclamar +${today_reward.amount?.toFixed(0)} FRJ!`
            ) : (
              `🎰 ¡Reclamar ${day7_reward?.label || 'Cápsula'}!`
            )}
          </button>

          <button
            onClick={() => setSheetOpen(false)}
            className="w-full py-3 rounded-xl font-black text-[10px] uppercase tracking-widest text-slate-500 hover:text-slate-300 transition-all"
          >
            Cerrar
          </button>
        </div>
      </BottomSheet>
    </>
  );
}
