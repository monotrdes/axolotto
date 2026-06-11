"use client";

/* ─── ToastContext — sistema de notificaciones unificado ──────────────────────
   Reemplaza los 3 sistemas ad-hoc que existían:
     • alert() en Store.tsx / Inventory.tsx  → toast.error()
     • vipToasts state en page.tsx            → toast.vip()
     • gameToasts state en page.tsx           → toast.game()

   Zonas de render:
     • Top-center      — ok · error · info · reward  (auto-dismiss 4s)
     • Bottom-izquierda — vip                         (auto-dismiss 8s/5s)
     • Bottom-derecha   — game                        (dismiss manual + "Limpiar")
─────────────────────────────────────────────────────────────────────────────── */

import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
} from 'react';
import { createPortal } from 'react-dom';
import { X } from 'lucide-react';
import type { VipNotification } from '@/components/VipModal';

// ── Tipos ─────────────────────────────────────────────────────────────────────

export type SimpleVariant = 'ok' | 'error' | 'info' | 'reward';

export interface SimpleToast {
  id: string;
  variant: SimpleVariant;
  message: string;
}

export interface VipToast {
  id: string;
  variant: 'vip';
  notif: VipNotification;
}

export interface PrizeBreakdownItem {
  prize_type: string;   // "premio_1" | "premio_2" | "jackpot"
  label: string;        // "Primer Patrón" | "Tabla Llena" | "Jackpot Global"
  gross_gal: number;
  luck_bonus: number;
  vip_bonus: number;
}

export interface GameResult {
  id: string | number;
  outcome: string;
  axo_name: string;
  room_name: string;
  net_gal?: number;
  xp_gained?: number;
  // Prize breakdown (2026-06 — multiplayer prize clarity)
  prize_breakdown?: PrizeBreakdownItem[];
  won_premio_1?: boolean;
  won_premio_2?: boolean;
  won_jackpot?: boolean;
  entry_fee_paid?: number;
  gross_prize_gal?: number;
}

export interface GameToast {
  id: string;
  variant: 'game';
  result: GameResult;
}

type ToastItem = SimpleToast | VipToast | GameToast;

interface ToastContextValue {
  toast: {
    ok(message: string): void;
    error(message: string): void;
    info(message: string): void;
    reward(message: string): void;
    vip(notif: VipNotification): void;
    game(result: GameResult): void;
  };
}

// ── Contexto ──────────────────────────────────────────────────────────────────

const ToastContext = createContext<ToastContextValue | null>(null);

export function useToast(): ToastContextValue {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error('useToast debe usarse dentro de <ToastProvider>');
  return ctx;
}

// ── Config visual VIP tiers ───────────────────────────────────────────────────

const VIP_TIER_CONFIG: Record<string, { emoji: string; color: string; glow: string }> = {
  coral:   { emoji: '🪸', color: '#2DD4BF', glow: 'rgba(45,212,191,0.3)'  },
  dorado:  { emoji: '✨', color: '#FBBF24', glow: 'rgba(251,191,36,0.3)'  },
  axolite: { emoji: '🌟', color: '#C084FC', glow: 'rgba(192,132,252,0.3)' },
};

// ── Config visual variantes simples ───────────────────────────────────────────

const SIMPLE_STYLE: Record<SimpleVariant, { border: string; icon: string; glow: string }> = {
  ok:     { border: '#10B981', icon: '✓',  glow: 'rgba(16,185,129,0.25)' },
  error:  { border: '#EF4444', icon: '✕',  glow: 'rgba(239,68,68,0.25)'  },
  info:   { border: '#60A5FA', icon: 'ℹ',  glow: 'rgba(96,165,250,0.25)' },
  reward: { border: '#FBBF24', icon: '🪙', glow: 'rgba(251,191,36,0.3)'  },
};

// ── Helper — id único ─────────────────────────────────────────────────────────

let _seq = 0;
function uid() { return `t-${Date.now()}-${++_seq}`; }

// ── Sub-componentes de render ─────────────────────────────────────────────────

function SimpleCard({ item, onDismiss }: { item: SimpleToast; onDismiss: () => void }) {
  const s = SIMPLE_STYLE[item.variant];
  const isReward = item.variant === 'reward';
  return (
    <div
      className={`flex items-center gap-3 px-4 py-3 rounded-2xl bg-[#0D0D1F] border-2 shadow-2xl
        animate-toast-in
        ${isReward ? 'animate-pulse' : ''}`}
      style={{ borderColor: s.border, boxShadow: `0 0 20px ${s.glow}` }}
    >
      <span
        className="shrink-0 text-base font-black leading-none"
        style={{ color: s.border }}
      >
        {s.icon}
      </span>
      <span className="text-white text-sm font-bold flex-1 min-w-0">{item.message}</span>
      <button
        onClick={onDismiss}
        className="shrink-0 text-slate-600 hover:text-white transition-colors p-1 rounded-full hover:bg-white/10"
      >
        <X size={12} />
      </button>
    </div>
  );
}

function VipCard({ item }: { item: VipToast }) {
  const { notif } = item;
  const tierCfg = notif.tier ? VIP_TIER_CONFIG[notif.tier] : null;

  if (notif.type === 'activation') {
    return (
      <div
        className="relative flex items-start gap-3 p-4 rounded-2xl bg-[#0D0D1F] border-2 shadow-2xl
          animate-toast-left pointer-events-auto"
        style={{
          borderColor: tierCfg?.color ?? '#FBBF24',
          boxShadow: `0 0 24px ${tierCfg?.glow ?? 'rgba(251,191,36,0.3)'}`,
        }}
      >
        <div className="text-3xl shrink-0 animate-bounce">{tierCfg?.emoji ?? '👑'}</div>
        <div className="flex-1 min-w-0">
          <p
            className="text-[10px] font-black uppercase tracking-widest mb-0.5"
            style={{ color: tierCfg?.color ?? '#FBBF24' }}
          >
            ¡Bienvenido al VIP {notif.tier?.toUpperCase()}!
          </p>
          {notif.is_first_activation && notif.welcome_gal && notif.welcome_gal > 0 ? (
            <p className="text-white text-sm font-bold">🎁 +{notif.welcome_gal.toFixed(0)} FRJ de regalo</p>
          ) : (
            <p className="text-white text-sm font-bold">Suscripción activada ✓</p>
          )}
          <p className="text-slate-500 text-xs mt-0.5">30 días de beneficios activos</p>
        </div>
      </div>
    );
  }

  // claim
  return (
    <div
      className="relative flex items-center gap-3 p-3.5 rounded-2xl bg-[#0D0D1F] border-2
        border-amber-500/60 shadow-2xl animate-toast-left pointer-events-auto"
      style={{ boxShadow: '0 0 16px rgba(245,158,11,0.25)' }}
    >
      <div className="text-2xl shrink-0 animate-bounce">🪙</div>
      <div className="flex-1 min-w-0">
        <p className="text-[10px] font-black uppercase tracking-widest text-amber-400 mb-0.5">
          FRJ Diario Reclamado
        </p>
        <p className="text-white text-sm font-black">+{(notif.claimed_gal ?? 0).toFixed(0)} FRJ</p>
      </div>
    </div>
  );
}

function GameCard({ item, onDismiss }: { item: GameToast; onDismiss: () => void }) {
  const { result } = item;
  const isVictory = result.outcome === 'Victoria';
  const netGal = result.net_gal ?? 0;
  const hasBreakdown = result.prize_breakdown && result.prize_breakdown.length > 0;
  const entryFee = result.entry_fee_paid ?? 0;
  const grossPrize = result.gross_prize_gal ?? 0;

  // Color mapping for prize types
  const prizeColors: Record<string, { border: string; bg: string; text: string }> = {
    premio_1:  { border: 'border-amber-500/40',  bg: 'bg-amber-950/30',  text: 'text-amber-300' },
    premio_2:  { border: 'border-yellow-400/50', bg: 'bg-yellow-950/30', text: 'text-yellow-300' },
    jackpot:   { border: 'border-purple-400/50', bg: 'bg-purple-950/30', text: 'text-purple-300' },
  };

  const isAFK = result.outcome && result.outcome.includes("AFK");

  return (
    <div
      className={`relative flex items-start gap-3 p-4 rounded-2xl bg-[#0D0D1F] border-2 shadow-2xl
        animate-toast-right ${
          result.won_jackpot
            ? 'border-[#C084FC] shadow-[0_0_30px_rgba(192,132,252,0.35)]'
            : isVictory
            ? 'border-[#10B981] shadow-[0_0_20px_rgba(16,185,129,0.25)]'
            : 'border-[#E4007C] shadow-[0_0_20px_rgba(228,0,124,0.25)]'
        }`}
    >
      <div className={`text-2xl shrink-0 ${result.won_jackpot ? 'animate-bounce' : isVictory ? 'animate-bounce' : ''}`}>
        {result.won_jackpot ? '💰' : isVictory ? '🏆' : '🎮'}
      </div>
      <div className="flex-1 min-w-0">
        {/* Outcome header */}
        <p className={`text-[10px] font-black uppercase tracking-widest mb-0.5 ${
          result.won_jackpot ? 'text-[#C084FC]' : isVictory ? 'text-[#10B981]' : 'text-[#E4007C]'
        }`}>
          {result.won_jackpot ? '🎉 ¡JACKPOT!' : isVictory ? '¡Victoria!' : isAFK ? '⚠️ Penalización AFK' : 'Partida Terminada'}
        </p>
        <p className="text-white text-sm font-bold truncate">{result.axo_name}</p>
        <p className="text-slate-500 text-xs truncate">{result.room_name}</p>

        {isAFK && (
          <div className="mt-2 px-2 py-1.5 rounded-lg border border-red-500/40 bg-red-950/30 text-[10px] font-black text-red-400 flex items-center gap-1.5 animate-pulse">
            <span>⚠️</span>
            <span>Penalización AFK aplicada: −30% premio y −5 Lealtad</span>
          </div>
        )}

        {/* Prize breakdown */}
        {hasBreakdown && (
          <div className="mt-2 space-y-1">
            {result.prize_breakdown!.map((pb, i) => {
              const colors = prizeColors[pb.prize_type] ?? prizeColors.premio_1;
              const total = pb.gross_gal + pb.luck_bonus + pb.vip_bonus;
              return (
                <div
                  key={i}
                  className={`flex items-center justify-between px-2 py-1 rounded-lg border ${colors.border} ${colors.bg} text-[9px]`}
                >
                  <span className={`font-black ${colors.text}`}>{pb.label}</span>
                  <span className={`font-black ${colors.text}`}>
                    +{total.toFixed(0)} FRJ
                    {pb.luck_bonus > 0 && <span className="text-teal-400 ml-0.5">🍀</span>}
                    {pb.vip_bonus > 0 && <span className="text-purple-400 ml-0.5">🌟</span>}
                  </span>
                </div>
              );
            })}
          </div>
        )}

        {/* Financial summary */}
        <div className="flex items-center gap-2 mt-1.5 flex-wrap">
          {hasBreakdown && grossPrize > 0 && (
            <span className="text-[9px] font-bold text-emerald-400">
              +{grossPrize.toFixed(0)} bruto
            </span>
          )}
          {hasBreakdown && entryFee > 0 && (
            <span className="text-[9px] font-bold text-rose-400">
              −{entryFee.toFixed(0)} cuota
            </span>
          )}
          <span className={`text-xs font-black ${netGal >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {netGal >= 0 ? `+${netGal.toFixed(2)}` : netGal.toFixed(2)} FRJ neto
          </span>
          <span className="text-[#E4007C] text-xs font-bold">+{result.xp_gained ?? 0} XP</span>
        </div>
      </div>
      <button
        onClick={onDismiss}
        className="absolute top-2 right-2 text-slate-700 hover:text-white transition-colors p-1 rounded-full hover:bg-gray-800"
      >
        <X size={12} />
      </button>
    </div>
  );
}

// ── Provider principal ────────────────────────────────────────────────────────

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [simpleToasts, setSimpleToasts] = useState<SimpleToast[]>([]);
  const [vipToasts,    setVipToasts]    = useState<VipToast[]>([]);
  const [gameToasts,   setGameToasts]   = useState<GameToast[]>([]);
  const [mounted,      setMounted]      = useState(false);

  useEffect(() => { setMounted(true); }, []);

  // ── Dismiss helpers ──────────────────────────────────────────────────────────

  const dismissSimple = useCallback((id: string) => {
    setSimpleToasts(prev => prev.filter(t => t.id !== id));
  }, []);

  const dismissGame = useCallback((id: string) => {
    setGameToasts(prev => prev.filter(t => t.id !== id));
  }, []);

  const dismissAllGames = useCallback(() => {
    setGameToasts([]);
  }, []);

  // ── Auto-dismiss para toasts simples ─────────────────────────────────────────

  const timersRef = useRef<Map<string, ReturnType<typeof setTimeout>>>(new Map());

  const scheduleAutoDismiss = useCallback((id: string, ms: number, fn: (id: string) => void) => {
    const existing = timersRef.current.get(id);
    if (existing) clearTimeout(existing);
    const timer = setTimeout(() => {
      fn(id);
      timersRef.current.delete(id);
    }, ms);
    timersRef.current.set(id, timer);
  }, []);

  useEffect(() => {
    return () => {
      timersRef.current.forEach(t => clearTimeout(t));
    };
  }, []);

  // ── API pública ───────────────────────────────────────────────────────────────

  const addSimple = useCallback((variant: SimpleVariant, message: string) => {
    const id = uid();
    setSimpleToasts(prev => [...prev.slice(-3), { id, variant, message }]);
    scheduleAutoDismiss(id, 4000, dismissSimple);
  }, [scheduleAutoDismiss, dismissSimple]);

  const toast: ToastContextValue['toast'] = {
    ok:     (msg) => addSimple('ok',     msg),
    error:  (msg) => addSimple('error',  msg),
    info:   (msg) => addSimple('info',   msg),
    reward: (msg) => addSimple('reward', msg),

    vip: (notif) => {
      const id = uid();
      const duration = notif.type === 'activation' ? 8000 : 5000;
      setVipToasts(prev => [...prev, { id, variant: 'vip', notif }]);
      scheduleAutoDismiss(id, duration, (tid) => {
        setVipToasts(prev => prev.filter(t => t.id !== tid));
      });
    },

    game: (result) => {
      const id = uid();
      setGameToasts(prev => [...prev, { id, variant: 'game', result }]);
    },
  };

  // ── Render ────────────────────────────────────────────────────────────────────

  const stacks = mounted ? createPortal(
    <>
      {/* Top-center — simples */}
      {simpleToasts.length > 0 && (
        <div className="fixed top-4 left-1/2 -translate-x-1/2 z-[9999] flex flex-col gap-2 w-80 max-w-[calc(100vw-2rem)] pointer-events-auto">
          {simpleToasts.map(item => (
            <SimpleCard key={item.id} item={item} onDismiss={() => dismissSimple(item.id)} />
          ))}
        </div>
      )}

      {/* Bottom-izquierda — VIP */}
      {vipToasts.length > 0 && (
        <div className="fixed bottom-[76px] left-4 z-50 flex flex-col gap-2 w-72 sm:w-80 max-w-[calc(100vw-2rem)] pointer-events-none">
          {vipToasts.map(item => (
            <VipCard key={item.id} item={item} />
          ))}
        </div>
      )}

      {/* Bottom-derecha — game results */}
      {gameToasts.length > 0 && (
        <div className="fixed bottom-[76px] right-4 z-50 flex flex-col gap-3 w-72 sm:w-80 max-w-[calc(100vw-2rem)]">
          {gameToasts.slice(-4).map(item => (
            <GameCard key={item.id} item={item} onDismiss={() => dismissGame(item.id)} />
          ))}
          {gameToasts.length > 1 && (
            <button
              onClick={dismissAllGames}
              className="w-full py-1.5 bg-[#0D0D1F]/80 hover:bg-[#1C1C35] text-slate-600 hover:text-white text-xs font-bold rounded-xl transition-colors border border-slate-800"
            >
              Limpiar ({gameToasts.length})
            </button>
          )}
        </div>
      )}
    </>,
    document.body
  ) : null;

  return (
    <ToastContext.Provider value={{ toast }}>
      {children}
      {stacks}
    </ToastContext.Provider>
  );
}
