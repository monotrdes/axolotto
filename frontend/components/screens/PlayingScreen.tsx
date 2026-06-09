"use client";

import React from 'react';
import { X, Sparkles } from 'lucide-react';

interface PlayingScreenProps {
  selectedAxo: any;
  budget: number;
  recallRequested: boolean;
  recalling: boolean;
  onRecall: () => void;
  escrowNotifs: { id: number; amount: number }[];
}

export default function PlayingScreen({
  selectedAxo,
  budget,
  recallRequested,
  recalling,
  onRecall,
  escrowNotifs,
}: PlayingScreenProps) {
  const escrow   = selectedAxo.escrow_balance_gal ?? 0;
  const diff     = escrow - (selectedAxo.bot_budget_axf ?? budget);
  const diffPos  = diff >= 0;

  // Limit bar calculation
  const lossLimit  = selectedAxo.bot_loss_limit_axf  ?? 0;
  const profitLimit= selectedAxo.bot_profit_limit_axf ?? 0;
  const initBudget = selectedAxo.bot_budget_axf ?? budget;
  const rangeTotal = lossLimit + profitLimit;
  const escrowOffset = escrow - (initBudget - lossLimit);
  const markerPct  = rangeTotal > 0
    ? Math.min(100, Math.max(0, Math.round((escrowOffset / rangeTotal) * 100)))
    : 50;

  return (
    <div className="space-y-4 animate-slide-step">
      {/* Header */}
      <div className="flex items-center gap-3 p-4 bg-gradient-to-r from-purple-950/30 to-slate-900/40 rounded-2xl border border-purple-500/20">
        <div className="w-10 h-10 bg-purple-950/60 rounded-full border border-purple-500/20 flex items-center justify-center text-purple-400 animate-pulse shrink-0">
          <Sparkles className="h-5 w-5" />
        </div>
        <div>
          <h4 className="font-extrabold text-sm text-purple-200">🕹️ {selectedAxo.name} está en las canchas</h4>
          <p className="text-[10px] text-purple-400/60 mt-0.5">Jugando en el lobby — se re-inscribe automáticamente</p>
        </div>
      </div>

      {/* Floating earnings */}
      {escrowNotifs.length > 0 && (
        <div className="relative h-8 pointer-events-none overflow-visible">
          {escrowNotifs.map((n) => (
            <div
              key={n.id}
              style={{ '--x': '-50%', animation: 'floatUp 2.5s ease-out forwards' } as React.CSSProperties}
              className={`absolute left-1/2 text-sm font-black drop-shadow-lg ${n.amount >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}
            >
              {n.amount >= 0 ? '+' : ''}{n.amount.toFixed(2)} FRJ
            </div>
          ))}
        </div>
      )}

      {/* Metrics */}
      <div className="grid grid-cols-3 gap-2">
        {[
          { label: 'Entró con',  value: (selectedAxo.bot_budget_axf ?? budget).toFixed(2), color: 'text-white' },
          { label: 'En custodia', value: escrow.toFixed(2), color: 'text-amber-400' },
          { label: 'Diferencia',  value: `${diffPos ? '+' : ''}${diff.toFixed(2)}`, color: diffPos ? 'text-emerald-400' : 'text-rose-400' },
        ].map(({ label, value, color }) => (
          <div key={label} className="bg-slate-950/80 border border-white/5 p-3 rounded-2xl text-center">
            <p className="text-[9px] text-slate-500 uppercase tracking-widest font-black mb-1">{label}</p>
            <p key={value} className={`text-base font-black ${color}`}>{value}</p>
            <p className="text-[9px] text-slate-500">FRJ</p>
          </div>
        ))}
      </div>

      {/* Limits bar */}
      <div className="space-y-1">
        <div className="flex justify-between text-[9px] font-black text-slate-500">
          <span className="text-rose-400">−{lossLimit.toFixed(0)} FRJ</span>
          <span className="text-slate-400 uppercase tracking-widest">Zona de juego</span>
          <span className="text-emerald-400">+{profitLimit.toFixed(0)} FRJ</span>
        </div>
        <div className="relative h-3 rounded-full overflow-hidden flex">
          <div className="flex-1 bg-rose-900/40" />
          <div className="flex-1 bg-emerald-900/40" />
          {/* Marker */}
          <div
            className="absolute top-0.5 bottom-0.5 w-1.5 rounded-full bg-white shadow transition-all duration-700"
            style={{ left: `calc(${markerPct}% - 3px)` }}
          />
        </div>
      </div>

      {/* Recall */}
      {recallRequested ? (
        <div className="bg-amber-950/30 border border-amber-500/20 rounded-2xl p-4 flex items-center justify-center gap-2">
          <div className="w-4 h-4 border-2 border-amber-400 border-t-transparent rounded-full animate-spin" />
          <span className="text-xs text-amber-300 font-bold">Regresará al terminar esta partida...</span>
        </div>
      ) : (
        <button
          onClick={onRecall}
          disabled={recalling}
          className="w-full py-3 bg-slate-800 hover:bg-red-900/30 border border-slate-700 hover:border-red-500/40 text-slate-300 hover:text-red-300 font-bold text-xs uppercase tracking-widest rounded-2xl transition-all flex items-center justify-center gap-2 disabled:opacity-60"
        >
          {recalling
            ? <><div className="w-4 h-4 border-2 border-slate-400 border-t-transparent rounded-full animate-spin" /> Llamando...</>
            : <><X size={14} /> 📣 Llamar de Regreso</>}
        </button>
      )}
    </div>
  );
}
