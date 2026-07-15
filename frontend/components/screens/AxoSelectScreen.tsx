"use client";
import { API_BASE } from "@/lib/api";

import React from 'react';
import { Clock, Play, Coins, CheckCircle } from 'lucide-react';
import { useProductPolicy } from '@/hooks/useProductPolicy';

interface AxoSelectScreenProps {
  axolotitos: any[];
  selectedAxo: any | null;
  onSelect: (axo: any) => void;
  onContinue: () => void;
  getSleepTimeLeft: (expires: string) => number;
  onFeed: (type: 'pellet' | 'shrimp') => void;
  onSleep: () => void;
  onWake: () => void;
  /** Settle a waiting_settlement axo inline without navigating away */
  onSettleInline: (axo: any) => Promise<void>;
  /** ID of the axo currently being settled (shows spinner) */
  settlingAxoId: number | null;
}

export default function AxoSelectScreen({
  axolotitos,
  selectedAxo,
  onSelect,
  onContinue,
  getSleepTimeLeft,
  onFeed,
  onSleep,
  onWake,
  onSettleInline,
  settlingAxoId,
}: AxoSelectScreenProps) {
  const { capabilities } = useProductPolicy();
  const fixedSpendingEnabled = capabilities.gameplay.fixed_spending;
  const tokenRewardsEnabled = capabilities.gameplay.token_rewards;

  const header = (
    <div className="text-center pt-2 pb-2">
      <h2 className="text-3xl sm:text-5xl font-black italic text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-pink-400 to-[#E4007C] drop-shadow-[0_0_15px_rgba(99,102,241,0.3)] tracking-tighter uppercase">
        🎮 Centro de Partidas
      </h2>
      <p className="text-slate-400 text-xs mt-2">Elige tu Axolotito para comenzar</p>
    </div>
  );

  if (axolotitos.length === 0) {
    return (
      <div className="space-y-4">
        {header}
        <div className="bg-slate-900/40 border border-dashed border-slate-800 rounded-3xl p-12 text-center">
          <p className="text-3xl mb-3">🥚</p>
          <p className="text-sm font-black text-slate-400 uppercase">Sin Axolotitos eclosionados</p>
          <p className="text-[11px] text-slate-600 mt-2">Ve al Criadero para eclosionar tus Webitos.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {header}

      <div className="space-y-2 max-h-[65vh] overflow-y-auto pr-1 scrollbar-hide">
        {axolotitos.map((axo) => {
          const isSelected   = selectedAxo?.id === axo.id;
          const sleepLeft    = getSleepTimeLeft(axo.sleep_expires_at ?? '');
          const isSleeping   = axo.status === 'sleeping' || sleepLeft > 0;
          const isPlaying    = axo.status === 'playing';
          const isSettling   = axo.status === 'waiting_settlement';
          const energyMax    = axo.stat_stamina || 100;
          const energyPct    = Math.min(100, Math.round((axo.energy_current / energyMax) * 100));
          const energyColor  = energyPct < 25 ? 'bg-red-500' : energyPct < 50 ? 'bg-yellow-500' : 'bg-emerald-500';
          // Only block if actively playing — settling axos are now clickable for inline settlement
          const isBlocked    = isPlaying;
          const isSettlingThis = settlingAxoId === axo.id;

          return (
            <div
              key={axo.id}
              className={`rounded-2xl border transition-all duration-200 overflow-hidden ${
                isSelected && isSettling
                  ? 'bg-slate-900 border-amber-500/50 shadow-[0_0_20px_rgba(245,158,11,0.3)]'
                  : isSelected
                    ? 'bg-slate-900 border-[var(--brand-hot)]/50 shadow-[0_0_20px_var(--brand-glow)]'
                    : isSettling
                      ? 'bg-slate-900/60 border-amber-500/30 hover:border-amber-500/60 cursor-pointer'
                      : isBlocked
                        ? 'bg-slate-950/50 border-slate-900/60 opacity-60 cursor-not-allowed'
                        : 'bg-slate-900/40 border-slate-800 hover:border-slate-700 hover:bg-slate-900/60 cursor-pointer'
              }`}
            >
              {/* Main row — 72px */}
              <button
                className="w-full text-left p-3 flex items-center gap-3 h-[72px]"
                onClick={() => !isBlocked && onSelect(isSelected ? null : axo)}
                disabled={isBlocked}
              >
                {/* Avatar */}
                <div className="w-10 h-10 shrink-0 bg-slate-950/80 rounded-xl border border-white/5 flex items-center justify-center p-0.5 relative">
                  <img
                    src={`${API_BASE}/metadata/axolotito/${axo.blockchain_token_id}.svg`}
                    alt={axo.name}
                    className="w-full h-full object-contain"
                    loading="lazy"
                  />
                  {isSleeping && (
                    <div className="absolute -top-1 -right-1 bg-amber-500 text-slate-950 rounded-full text-[9px] w-4 h-4 flex items-center justify-center">
                      😴
                    </div>
                  )}
                </div>

                {/* Name + status */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-2">
                    <h4 className="font-black text-sm text-white uppercase truncate">{axo.name}</h4>
                    <span className="text-[9px] font-black px-1.5 py-0.5 rounded-md bg-indigo-950/60 border border-indigo-500/30 text-indigo-300 shrink-0">
                      Nv.{axo.level}
                    </span>
                  </div>
                  <div className="flex items-center gap-1.5 mt-1">
                    {isSleeping ? (
                      <span className="text-[10px] font-bold text-amber-400 bg-amber-950/30 border border-amber-500/20 px-2 py-0.5 rounded-full flex items-center gap-1">
                        <Clock size={8} /> Durmiendo {sleepLeft > 0 ? `(${Math.ceil(sleepLeft / 60)}m)` : ''}
                      </span>
                    ) : isPlaying ? (
                      <span className="text-[10px] font-bold text-purple-400 bg-purple-950/30 border border-purple-500/20 px-2 py-0.5 rounded-full flex items-center gap-1">
                        <Play size={8} /> En Juego
                      </span>
                    ) : isSettling ? (
                      <span className="text-[10px] font-bold text-amber-400 bg-amber-950/30 border border-amber-500/30 px-2 py-0.5 rounded-full animate-pulse flex items-center gap-1">
                        🏆 Listo para Cobrar · Toca aquí
                      </span>
                    ) : (
                      <span className="text-[10px] font-bold text-emerald-400 bg-emerald-950/30 border border-emerald-500/20 px-2 py-0.5 rounded-full">
                        Disponible
                      </span>
                    )}
                  </div>
                  {/* Mini energy bar */}
                  <div className="mt-1.5 h-1 rounded-full bg-slate-800 overflow-hidden w-full">
                    <div className={`h-full ${energyColor} transition-all`} style={{ width: `${energyPct}%` }} />
                  </div>
                </div>

                {/* Selection indicator */}
                {isSelected && (
                  <div className="w-5 h-5 rounded-full bg-[var(--brand-hot)] flex items-center justify-center shrink-0">
                    <span className="text-white text-[10px] font-black">✓</span>
                  </div>
                )}
              </button>

              {/* Expanded accordion */}
              {isSelected && (
                <div className="px-3 pb-3 pt-0 border-t border-slate-800/60" style={{ animation: 'slide-step 150ms ease-out both' }}>

                  {/* ── Settlement inline UI (for waiting_settlement axos) ── */}
                  {isSettling ? (
                    <div className="space-y-3 mt-3">
                      <p className="text-[10px] font-black text-amber-400 uppercase tracking-widest text-center">
                        🏆 Jornada Terminada
                      </p>

                      {/* Budget metrics */}
                      <div className="grid grid-cols-3 gap-1.5">
                        <div className="bg-slate-950/60 border border-white/5 rounded-xl p-2 text-center">
                          <p className="text-[8px] text-slate-500 uppercase tracking-widest mb-0.5">Entró con</p>
                          <p className="text-xs font-black text-white flex items-center justify-center gap-0.5">
                            <Coins size={9} className="text-amber-400" />
                            {axo.bot_budget_axf ?? '—'}
                          </p>
                        </div>
                        <div className="bg-slate-950/60 border border-white/5 rounded-xl p-2 text-center">
                          <p className="text-[8px] text-slate-500 uppercase tracking-widest mb-0.5">En custodia</p>
                          <p className="text-xs font-black text-white flex items-center justify-center gap-0.5">
                            <Coins size={9} className="text-amber-400" />
                            {axo.escrow_balance_gal ?? '—'}
                          </p>
                        </div>
                        <div className="bg-slate-950/60 border border-white/5 rounded-xl p-2 text-center">
                          <p className="text-[8px] text-slate-500 uppercase tracking-widest mb-0.5">Diferencia</p>
                          {(() => {
                            const init = axo.bot_budget_axf ?? 0;
                            const escrow = axo.escrow_balance_gal ?? 0;
                            const diff = escrow - init;
                            return (
                              <p className={`text-xs font-black ${diff >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                                {diff >= 0 ? '+' : ''}{diff}
                              </p>
                            );
                          })()}
                        </div>
                      </div>

                      {/* Confirm button */}
                      <button
                        onClick={() => onSettleInline(axo)}
                        disabled={isSettlingThis}
                        className="w-full py-3 bg-gradient-to-r from-emerald-700 to-emerald-600 hover:from-emerald-600 hover:to-emerald-500 text-white text-xs font-black uppercase tracking-widest rounded-xl transition-all shadow-[0_0_15px_rgba(52,211,153,0.25)] active:scale-[0.98] disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                      >
                        {isSettlingThis ? (
                          <>
                            <div className="w-3 h-3 border-2 border-white/40 border-t-white rounded-full animate-spin" />
                            Confirmando...
                          </>
                        ) : (
                          <>
                            <CheckCircle size={13} />
                            ✅ Confirmar Retorno y Cobrar
                          </>
                        )}
                      </button>

                      <p className="text-[9px] text-slate-600 text-center">
                        El FRJ regresará a tu saldo al confirmar.
                      </p>
                    </div>

                  ) : (
                    /* ── Normal stats + feed/sleep (available axos) ── */
                    <>
                      {/* Stats grid */}
                      <div className="grid grid-cols-4 gap-1.5 mt-2.5">
                        {[
                          { emoji: '✨', label: 'SUERTE', val: axo.stat_luck,     color: '#fbbf24' },
                          { emoji: '👁️', label: 'OJO',    val: axo.stat_focus,    color: '#2dd4bf' },
                          { emoji: '🔋', label: 'PILA',   val: axo.stat_stamina,  color: '#60a5fa' },
                          { emoji: '🧂', label: 'SAL',    val: axo.stat_salinity, color: '#f87171', inverted: true },
                        ].map(({ emoji, label, val, color }) => (
                          <div key={label} className="bg-slate-950/60 rounded-xl p-1.5 text-center">
                            <div className="text-sm leading-none">{emoji}</div>
                            <div className="text-[8px] text-slate-500 font-bold mt-0.5">{label}</div>
                            <div className="text-[10px] font-black" style={{ color }}>{val?.toFixed(0) ?? '—'}</div>
                          </div>
                        ))}
                      </div>

                      {/* XP + Loyalty */}
                      <div className="grid grid-cols-2 gap-1.5 mt-1.5">
                        <div className="bg-slate-950/60 rounded-xl px-2.5 py-1.5 flex items-center justify-between text-[10px]">
                          <span className="text-slate-400">🏆 XP</span>
                          <span className="font-black text-indigo-300">{axo.experience ?? 0}</span>
                        </div>
                        <div className="bg-slate-950/60 rounded-xl px-2.5 py-1.5 flex items-center justify-between text-[10px]">
                          <span className="text-slate-400">💎 Loyalty</span>
                          <span className="font-black text-amber-300">{axo.loyalty_points ?? 0}</span>
                        </div>
                      </div>

                      {/* Win streak badge */}
                      {(axo.cpu_win_streak ?? 0) >= 1 && (
                        <div className="flex items-center gap-1.5 mt-1.5 bg-amber-950/40 border border-amber-500/20 rounded-xl px-2.5 py-1.5">
                          <span className="text-sm">🔥</span>
                          <div>
                            <span className="text-[10px] font-black text-amber-300">
                              Racha ×{axo.cpu_win_streak}
                            </span>
                            {tokenRewardsEnabled && (axo.cpu_win_streak ?? 0) >= 2 && (
                              <span className="text-[9px] text-slate-400 ml-1.5">
                                (+{Math.min(50, axo.cpu_win_streak * 15)}% próximo premio)
                              </span>
                            )}
                          </div>
                        </div>
                      )}

                      {/* Feed/sleep buttons */}
                      <div className="flex flex-wrap gap-1.5 mt-2.5">
                        <button
                          onClick={() => fixedSpendingEnabled && onFeed('pellet')}
                          disabled={isSleeping || !fixedSpendingEnabled}
                          title={!fixedSpendingEnabled ? 'Alimentación en revisión' : undefined}
                          className="px-2.5 py-1.5 bg-slate-900 hover:bg-slate-800 text-green-300 text-[9px] font-black uppercase tracking-widest rounded-xl border border-slate-800 transition-all disabled:opacity-40 disabled:cursor-not-allowed"
                        >
                          {fixedSpendingEnabled ? '🌿 Alga (2 FRJ)' : '🌿 Alga · En revisión'}
                        </button>
                        <button
                          onClick={() => fixedSpendingEnabled && onFeed('shrimp')}
                          disabled={isSleeping || !fixedSpendingEnabled}
                          title={!fixedSpendingEnabled ? 'Alimentación en revisión' : undefined}
                          className="px-2.5 py-1.5 bg-slate-900 hover:bg-slate-800 text-emerald-300 text-[9px] font-black uppercase tracking-widest rounded-xl border border-slate-800 transition-all disabled:opacity-40 disabled:cursor-not-allowed"
                        >
                          {fixedSpendingEnabled ? '🦐 Camarón (10 FRJ)' : '🦐 Camarón · En revisión'}
                        </button>
                        {isSleeping ? (
                          <button
                            onClick={onWake}
                            disabled={sleepLeft > 0}
                            className="px-2.5 py-1.5 bg-amber-600/30 text-amber-300 text-[9px] font-black uppercase tracking-widest rounded-xl border border-amber-500/30 transition-all disabled:opacity-40"
                          >
                            ☀️ Despertar
                          </button>
                        ) : (
                          <button
                            onClick={onSleep}
                            className="px-2.5 py-1.5 bg-blue-950/30 hover:bg-blue-900/40 text-blue-300 text-[9px] font-black uppercase tracking-widest rounded-xl border border-blue-500/20 transition-all"
                          >
                            🌙 Dormir
                          </button>
                        )}
                      </div>
                    </>
                  )}
                </div>
              )}

              {/* Overlay for actively-playing axos only */}
              {isBlocked && (
                <div className="absolute inset-0 bg-slate-950/80 rounded-2xl flex items-center justify-center text-center p-2 pointer-events-none">
                  <div>
                    <p className="text-[9px] font-black text-amber-400 uppercase tracking-wider">
                      🎮 En Juego
                    </p>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Footer CTA */}
      {selectedAxo && !selectedAxo.status?.includes('playing') && !selectedAxo.status?.includes('settlement') && (
        <div className="pt-2">
          <button
            onClick={onContinue}
            className="w-full py-4 bg-gradient-to-r from-[var(--brand-hot)] to-indigo-600 hover:from-pink-500 hover:to-indigo-500 text-white font-black text-sm uppercase tracking-widest rounded-2xl transition-all shadow-[0_0_20px_var(--brand-glow)] active:scale-[0.98] animate-sheet-up"
          >
            Continuar →
          </button>
        </div>
      )}
    </div>
  );
}
