"use client";

import React from 'react';
import { Coins } from 'lucide-react';

interface BudgetScreenProps {
  balances: any;
  budget: number;
  lossLimitPct: number;
  profitLimitPct: number;
  onBudgetChange: (v: number) => void;
  onLossChange: (v: number) => void;
  onProfitChange: (v: number) => void;
  onContinue: () => void;
  error: string | null;
}

export default function BudgetScreen({
  balances,
  budget,
  lossLimitPct,
  profitLimitPct,
  onBudgetChange,
  onLossChange,
  onProfitChange,
  onContinue,
  error,
}: BudgetScreenProps) {
  const saldo      = Math.floor(balances?.frijolitos ?? 0);
  const maxBudget  = Math.max(100, saldo);
  const lossValue  = Math.round((budget * lossLimitPct) / 100);
  const profitValue= Math.round((budget * profitLimitPct) / 100);
  const overBudget = budget > saldo;

  // Budget slider track color
  const ratio = saldo > 0 ? budget / saldo : 0;
  const budgetTrackColor = ratio < 0.5 ? 'accent-emerald-500' : ratio < 0.8 ? 'accent-yellow-500' : 'accent-red-500';

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-black text-slate-400 uppercase tracking-widest">Presupuesto</h3>
        <div className="flex items-center gap-1.5 text-[10px] font-black text-amber-400">
          <Coins size={11} /> Tu saldo: {saldo.toLocaleString()} FRJ
        </div>
      </div>

      {error && (
        <div className="bg-red-950/50 border border-red-500/30 text-red-300 text-[10px] font-bold rounded-xl p-2.5">
          {error}
        </div>
      )}

      {/* Budget slider */}
      <div className="space-y-1.5">
        <div className="flex justify-between text-[10px] font-black">
          <span className="text-slate-400 uppercase tracking-wider">💰 Presupuesto para Escrow</span>
          <span className={overBudget ? 'text-red-400' : 'text-amber-400'}>{budget} FRJ</span>
        </div>
        <div className="bg-slate-950/80 rounded-2xl border border-slate-800/80 p-3.5 flex items-center gap-4">
          <input
            type="range"
            min="10"
            max={maxBudget}
            step="5"
            value={budget}
            onChange={(e) => onBudgetChange(Number(e.target.value))}
            className={`flex-1 ${budgetTrackColor} cursor-pointer h-1.5 bg-slate-800 rounded-lg appearance-none`}
          />
          <input
            type="number"
            min="10"
            max={maxBudget}
            step="5"
            value={budget}
            onChange={(e) => onBudgetChange(Math.min(maxBudget, Math.max(10, Number(e.target.value))))}
            className="w-20 bg-slate-900 border border-slate-700 text-amber-400 font-black text-sm text-right px-2 py-1 rounded-xl appearance-none"
          />
        </div>
        {overBudget && (
          <p className="text-[10px] text-red-400 font-bold">⚠️ Presupuesto supera tu saldo disponible</p>
        )}
      </div>

      {/* Loss limit */}
      <div className="space-y-1.5">
        <div className="flex justify-between text-[10px] font-black">
          <span className="text-slate-400 uppercase tracking-wider">📉 Detener en Pérdida de</span>
          <span className="text-rose-400">{lossLimitPct}% ≈ {lossValue} FRJ</span>
        </div>
        <div className="bg-slate-950/80 rounded-2xl border border-slate-800/80 p-3.5 flex items-center gap-4">
          <input
            type="range"
            min="5"
            max="80"
            step="5"
            value={lossLimitPct}
            onChange={(e) => onLossChange(Number(e.target.value))}
            className="flex-1 accent-rose-500 cursor-pointer h-1.5 bg-slate-800 rounded-lg appearance-none"
          />
          <span className="w-16 text-right font-mono font-black text-rose-400 text-sm shrink-0">
            {lossLimitPct}%
          </span>
        </div>
      </div>

      {/* Profit limit */}
      <div className="space-y-1.5">
        <div className="flex justify-between text-[10px] font-black">
          <span className="text-slate-400 uppercase tracking-wider">📈 Detener en Ganancia de</span>
          <span className="text-emerald-400">{profitLimitPct}% ≈ +{profitValue} FRJ</span>
        </div>
        <div className="bg-slate-950/80 rounded-2xl border border-slate-800/80 p-3.5 flex items-center gap-4">
          <input
            type="range"
            min="10"
            max="300"
            step="10"
            value={profitLimitPct}
            onChange={(e) => onProfitChange(Number(e.target.value))}
            className="flex-1 accent-emerald-500 cursor-pointer h-1.5 bg-slate-800 rounded-lg appearance-none"
          />
          <span className="w-16 text-right font-mono font-black text-emerald-400 text-sm shrink-0">
            {profitLimitPct}%
          </span>
        </div>
      </div>

      {/* Live summary */}
      <div className="bg-slate-950/60 border border-slate-800 rounded-2xl p-4 space-y-1.5">
        <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2">Resumen</p>
        <div className="flex justify-between text-[11px]">
          <span className="text-slate-400">Presupuesto:</span>
          <span className="font-black text-white">{budget} FRJ</span>
        </div>
        <div className="flex justify-between text-[11px]">
          <span className="text-slate-400">Si pierde el {lossLimitPct}%:</span>
          <span className="font-black text-rose-400">sale con ≥ {budget - lossValue} FRJ</span>
        </div>
        <div className="flex justify-between text-[11px]">
          <span className="text-slate-400">Si gana el {profitLimitPct}%:</span>
          <span className="font-black text-emerald-400">sale con ≥ {budget + profitValue} FRJ</span>
        </div>
      </div>

      {/* CTA */}
      <button
        onClick={onContinue}
        disabled={overBudget}
        className="w-full py-4 bg-gradient-to-r from-[var(--brand-hot)] to-indigo-600 hover:from-pink-500 hover:to-indigo-500 disabled:from-slate-800 disabled:to-slate-900 disabled:text-slate-500 text-white font-black text-sm uppercase tracking-widest rounded-2xl transition-all shadow-[0_0_20px_var(--brand-glow)] active:scale-[0.98] disabled:cursor-not-allowed disabled:shadow-none animate-sheet-up"
      >
        Continuar →
      </button>
    </div>
  );
}
