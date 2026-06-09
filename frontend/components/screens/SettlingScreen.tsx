"use client";

import React, { useState, useEffect } from 'react';
import { Trophy, Coins, ChevronDown, ChevronRight } from 'lucide-react';

export interface MatchSummary {
  outcome: string;
  room_name: string;
  gross_prize: number;
  entry_fee: number;
  net_gal: number;
  xp_gained: number;
  prize_labels: string[];
  won_jackpot: boolean;
}

interface SettlingScreenProps {
  selectedAxo: any;
  settling: boolean;
  onSettle: () => void;
  error: string | null;
  matchSummaries?: MatchSummary[];
}

const MATCH_LOGS_KEY = 'axolotto_match_logs_';

export default function SettlingScreen({
  selectedAxo,
  settling,
  onSettle,
  error,
  matchSummaries: propSummaries,
}: SettlingScreenProps) {
  const initBudget = selectedAxo.bot_budget_axf ?? 0;
  const escrow     = selectedAxo.escrow_balance_gal ?? 0;
  const netPerf    = escrow - initBudget;
  const netPos     = netPerf >= 0;

  // Loyalty bonus calculation
  const loyaltyBonus = 5 + (netPerf > 0 ? Math.floor(netPerf / 10) : 0);

  // Read match summaries from sessionStorage (accumulated by polling loop)
  const [storageSummaries, setStorageSummaries] = useState<MatchSummary[]>([]);
  useEffect(() => {
    try {
      // Try to find stored logs for any user
      for (let i = 0; i < sessionStorage.length; i++) {
        const key = sessionStorage.key(i);
        if (key?.startsWith(MATCH_LOGS_KEY)) {
          const raw = sessionStorage.getItem(key);
          if (raw) {
            const parsed = JSON.parse(raw) as MatchSummary[];
            setStorageSummaries(parsed);
            // Clear after reading to avoid stale data on next settle
            sessionStorage.removeItem(key);
            break;
          }
        }
      }
    } catch { /* ignore */ }
  }, []);

  const allSummaries = propSummaries ?? storageSummaries;

  const [showMatches, setShowMatches] = useState(false);
  const hasMatches = allSummaries.length > 0;
  const wins = hasMatches ? allSummaries.filter(m => m.outcome === 'Victoria').length : 0;
  const losses = hasMatches ? allSummaries.filter(m => m.outcome === 'Derrota').length : 0;

  return (
    <div className="space-y-5 animate-slide-step">
      {/* Header */}
      <div className="flex items-center gap-2.5 p-5 bg-gradient-to-b from-pink-950/20 to-slate-900/40 border border-pink-500/30 rounded-3xl">
        <Trophy className="h-6 w-6 text-pink-400 shrink-0" />
        <div>
          <h4 className="text-base font-extrabold text-pink-100 uppercase tracking-tight">🏆 Jornada Terminada</h4>
          <p className="text-[11px] text-pink-300/60 leading-none mt-1">{selectedAxo.name} ha terminado su jornada de juego.</p>
        </div>
      </div>

      {error && (
        <div className="bg-red-950/50 border border-red-500/30 text-red-300 text-[10px] font-bold rounded-xl p-2.5">
          {error}
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-2 gap-3">
        <div className="bg-slate-950/80 border border-white/5 p-4 rounded-2xl">
          <span className="text-[10px] text-slate-500 uppercase tracking-wider font-bold block">Presupuesto Inicial</span>
          <span className="text-lg font-black text-white mt-1 block">{initBudget.toFixed(2)} FRJ</span>
        </div>
        <div className="bg-slate-950/80 border border-white/5 p-4 rounded-2xl">
          <span className="text-[10px] text-slate-500 uppercase tracking-wider font-bold block">Saldo de Custodia</span>
          <span className="text-lg font-black text-amber-400 mt-1 block flex items-center gap-1">
            <Coins size={14} /> {escrow.toFixed(2)} FRJ
          </span>
        </div>
      </div>

      {/* Net performance */}
      <div className="bg-slate-950/60 border border-white/5 p-4 rounded-2xl flex justify-between items-center">
        <div>
          <span className="text-[10px] text-slate-500 uppercase tracking-wider font-bold block">Desempeño Neto</span>
          <span className={`text-lg font-black mt-1 block ${netPos ? 'text-emerald-400' : 'text-rose-400'}`}>
            {netPos ? '+' : ''}{netPerf.toFixed(2)} FRJ
          </span>
        </div>
        <div className="text-right">
          <span className="text-[10px] text-slate-500 uppercase tracking-wider font-bold block">Bono de Afecto</span>
          <span className="text-lg font-black text-pink-400 mt-1 block">+{loyaltyBonus} Ptos</span>
        </div>
      </div>

      {/* Match history */}
      {hasMatches && (
        <div className="bg-slate-950/60 border border-white/5 rounded-2xl overflow-hidden">
          <button
            onClick={() => setShowMatches(!showMatches)}
            className="w-full p-4 flex items-center justify-between text-left hover:bg-slate-900/40 transition-colors"
          >
            <div>
              <span className="text-[10px] text-slate-400 uppercase tracking-wider font-bold block">
                Detalle de Partidas
              </span>
              <span className="text-xs text-slate-500 mt-0.5 block">
                {allSummaries.length} partidas · {wins} 🏆 {losses} 💀
              </span>
            </div>
            {showMatches
              ? <ChevronDown size={16} className="text-slate-500" />
              : <ChevronRight size={16} className="text-slate-500" />
            }
          </button>

          {showMatches && (
            <div className="border-t border-white/5 divide-y divide-white/5 max-h-60 overflow-y-auto">
              {allSummaries.map((m, i) => {
                const isWin = m.outcome === 'Victoria';
                return (
                  <div key={i} className="px-4 py-2.5 flex items-center justify-between gap-2">
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-1.5">
                        <span className="text-xs font-bold text-white truncate">{m.room_name}</span>
                        {m.won_jackpot && (
                          <span className="text-[8px] font-black text-purple-400 bg-purple-950/60 px-1.5 py-0.5 rounded-full">
                            JACKPOT
                          </span>
                        )}
                      </div>
                      <div className="flex items-center gap-1.5 mt-0.5">
                        {m.prize_labels.length > 0 ? (
                          m.prize_labels.map((label, j) => (
                            <span key={j} className="text-[8px] font-bold text-amber-400 bg-amber-950/40 px-1.5 py-0.5 rounded-full">
                              {label}
                            </span>
                          ))
                        ) : (
                          <span className={`text-[9px] font-bold ${isWin ? 'text-emerald-400' : 'text-slate-500'}`}>
                            {isWin ? 'Victoria' : 'Derrota'}
                          </span>
                        )}
                        <span className="text-[9px] text-indigo-400 font-bold">+{m.xp_gained} XP</span>
                      </div>
                    </div>
                    <div className="text-right shrink-0">
                      <span className={`text-xs font-black ${m.net_gal >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                        {m.net_gal >= 0 ? '+' : ''}{m.net_gal.toFixed(0)} FRJ
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* CTA */}
      <button
        onClick={onSettle}
        disabled={settling}
        className="w-full py-4 bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 disabled:from-slate-800 disabled:to-slate-900 disabled:text-slate-500 text-white font-black text-xl uppercase tracking-widest rounded-2xl transition-all shadow-[0_0_20px_rgba(52,211,153,0.3)] active:scale-[0.97] flex items-center justify-center gap-2 border border-white/5"
        style={{ borderRadius: '20px' }}
      >
        {settling ? (
          <><div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" /> Procesando...</>
        ) : (
          <>✅ Confirmar Retorno y Cobrar</>
        )}
      </button>
      <p className="text-[9px] text-slate-600 text-center">
        El FRJ regresará a tu saldo una vez confirmado.
      </p>
    </div>
  );
}
