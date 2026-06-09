"use client";
import { API_BASE } from "@/lib/api";

import React, { useState } from 'react';
import { Zap } from 'lucide-react';
import BottomSheet from './ui/BottomSheet';

interface AxoStatusBarProps {
  axo: any;
  getSleepTimeLeft: (expires: string) => number;
  onAction: (action: 'feed-pellet' | 'feed-shrimp' | 'sleep' | 'wake') => void;
}

const RARITY_COLOR: Record<string, string> = {
  'Legendaria': '#FBBF24',
  'Épica':      '#C084FC',
  'Rara':       '#22D3EE',
  'Poco Común': '#10B981',
  'Común':      '#475569',
};

export default function AxoStatusBar({ axo, getSleepTimeLeft, onAction }: AxoStatusBarProps) {
  const [open, setOpen] = useState(false);

  const sleepLeft   = getSleepTimeLeft(axo.sleep_expires_at ?? '');
  const isSleeping  = axo.status === 'sleeping' || sleepLeft > 0;
  const isPlaying   = axo.status === 'playing';
  const isSettling  = axo.status === 'waiting_settlement';
  const energyMax   = axo.stat_stamina || 100;
  const energyPct   = Math.min(100, Math.round((axo.energy_current / energyMax) * 100));
  const isLowEnergy = energyPct < 25;

  const borderColor = RARITY_COLOR[axo.rarity as string] ?? RARITY_COLOR['Común'];
  const energyColor = energyPct < 25 ? 'bg-red-500' : energyPct < 50 ? 'bg-yellow-500' : 'bg-emerald-500';

  let badge: React.ReactNode;
  if (isSleeping) {
    const mins = Math.ceil(sleepLeft / 60);
    badge = (
      <span className="text-[9px] font-black text-blue-300 bg-blue-950/40 border border-blue-500/20 px-1.5 py-0.5 rounded-full animate-pulse shrink-0">
        💤 {mins > 0 ? `${mins}m` : 'Listo'}
      </span>
    );
  } else if (isPlaying) {
    badge = (
      <span className="text-[9px] font-black text-amber-300 bg-amber-950/40 border border-amber-500/20 px-1.5 py-0.5 rounded-full shrink-0">
        🎮 En cancha
      </span>
    );
  } else if (isLowEnergy) {
    badge = (
      <span className="text-[9px] font-black text-red-300 bg-red-950/40 border border-red-500/20 px-1.5 py-0.5 rounded-full animate-pulse shrink-0">
        ⚠️ Alimentar
      </span>
    );
  } else {
    badge = (
      <span className="text-[9px] font-black text-emerald-300 bg-emerald-950/40 border border-emerald-500/20 px-1.5 py-0.5 rounded-full shrink-0">
        • Listo
      </span>
    );
  }

  const name = axo.name?.length > 12 ? axo.name.slice(0, 11) + '…' : (axo.name ?? '');

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-2xl border transition-all mb-4 text-left ${
          isLowEnergy && !isSleeping && !isPlaying
            ? 'bg-red-950/20 border-red-500/20 animate-pulse'
            : 'bg-slate-900/40 border-slate-800 hover:border-slate-700'
        }`}
      >
        {/* Avatar */}
        <div
          className="w-7 h-7 shrink-0 rounded-full overflow-hidden border-2"
          style={{ borderColor }}
        >
          <img
            src={`${API_BASE}/metadata/axolotito/${axo.blockchain_token_id}.svg`}
            alt={axo.name}
            className="w-full h-full object-contain"
            loading="lazy"
          />
        </div>

        {/* Name + level */}
        <span className="text-xs font-black text-white uppercase truncate max-w-[80px]">{name}</span>
        <span className="text-[9px] text-slate-500 font-bold shrink-0">Nv.{axo.level}</span>

        {/* Energy bar */}
        <div className="flex-1 h-1.5 rounded-full bg-slate-800 overflow-hidden min-w-[40px]">
          <div className={`h-full ${energyColor} transition-all`} style={{ width: `${energyPct}%` }} />
        </div>
        <span className="text-[9px] font-black text-slate-400 shrink-0">{energyPct}%</span>

        {badge}
        <Zap size={13} className="text-slate-500 shrink-0" />
      </button>

      {/* BottomSheet with full controls */}
      <BottomSheet open={open} onClose={() => setOpen(false)} title={axo.name} accent="var(--brand-hot)">
        <div className="px-5 py-4 space-y-4 pb-8">
          {/* Header */}
          <div className="flex gap-4 items-center">
            <div
              className="w-16 h-16 rounded-2xl overflow-hidden border-2 shrink-0 bg-slate-950/80"
              style={{ borderColor }}
            >
              <img
                src={`${API_BASE}/metadata/axolotito/${axo.blockchain_token_id}.svg`}
                alt={axo.name}
                className="w-full h-full object-contain"
              />
            </div>
            <div className="flex-1 min-w-0">
              <h3 className="text-sm font-black text-white uppercase tracking-tight truncate">{axo.name}</h3>
              <div className="flex flex-wrap gap-1.5 mt-1.5">
                {badge}
                <span className="text-[9px] font-black text-indigo-300 bg-indigo-950/40 border border-indigo-500/20 px-1.5 py-0.5 rounded-full">
                  Nv.{axo.level}
                </span>
              </div>
            </div>
          </div>

          {/* Energy */}
          <div>
            <div className="flex justify-between text-[10px] font-black mb-1.5">
              <span className="text-slate-400">⚡ ENERGÍA</span>
              <span className={energyPct < 25 ? 'text-red-400' : energyPct < 50 ? 'text-yellow-400' : 'text-emerald-400'}>
                {axo.energy_current} / {energyMax}
              </span>
            </div>
            <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
              <div className={`h-full ${energyColor} transition-all`} style={{ width: `${energyPct}%` }} />
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 gap-1.5">
            {[
              { emoji: '✨', label: 'SUERTE', val: axo.stat_luck,     color: '#fbbf24' },
              { emoji: '👁️', label: 'OJO',    val: axo.stat_focus,    color: '#2dd4bf' },
              { emoji: '🔋', label: 'PILA',   val: axo.stat_stamina,  color: '#60a5fa' },
              { emoji: '🧂', label: 'SAL',    val: axo.stat_salinity, color: '#f87171', inverted: true },
            ].map(({ emoji, label, val, color, inverted }) => (
              <div key={label} className="flex items-center justify-between bg-slate-950/50 rounded-xl px-2.5 py-1.5 text-[10px]">
                <span className="text-slate-400">{emoji} {label}{inverted && <span className="ml-1 text-[8px] text-red-400">↓ mejor</span>}</span>
                <span className="font-black" style={{ color }}>{val?.toFixed(1) ?? '—'}</span>
              </div>
            ))}
            <div className="flex items-center justify-between bg-slate-950/50 rounded-xl px-2.5 py-1.5 text-[10px]">
              <span className="text-slate-400">🏆 XP</span>
              <span className="font-black text-indigo-300">{axo.experience ?? 0}</span>
            </div>
            <div className="flex items-center justify-between bg-slate-950/50 rounded-xl px-2.5 py-1.5 text-[10px]">
              <span className="text-slate-400">💎 Loyalty</span>
              <span className="font-black text-amber-300">{axo.loyalty_points ?? 0}</span>
            </div>
          </div>

          {/* Actions */}
          {!isPlaying && !isSettling ? (
            <div className="grid grid-cols-2 gap-2">
              <button
                onClick={() => { onAction('feed-pellet'); setOpen(false); }}
                disabled={isSleeping}
                className="py-3 bg-slate-900 hover:bg-slate-800 border border-slate-700 text-green-300 text-[10px] font-black uppercase tracking-widest rounded-2xl transition-all disabled:opacity-40 disabled:cursor-not-allowed text-center"
              >
                🌿 Alga Pellet<br />
                <span className="text-[9px] text-slate-500 font-bold">2 FRJ · +15 E</span>
              </button>
              <button
                onClick={() => { onAction('feed-shrimp'); setOpen(false); }}
                disabled={isSleeping}
                className="py-3 bg-slate-900 hover:bg-slate-800 border border-slate-700 text-emerald-300 text-[10px] font-black uppercase tracking-widest rounded-2xl transition-all disabled:opacity-40 disabled:cursor-not-allowed text-center"
              >
                🦐 Camarón<br />
                <span className="text-[9px] text-slate-500 font-bold">10 FRJ · +60 E</span>
              </button>
              {isSleeping ? (
                <button
                  onClick={() => { onAction('wake'); setOpen(false); }}
                  disabled={sleepLeft > 0}
                  className="col-span-2 py-3 bg-amber-950/30 border border-amber-500/30 text-amber-300 text-[10px] font-black uppercase tracking-widest rounded-2xl transition-all disabled:opacity-40"
                >
                  ☀️ Despertar {sleepLeft > 0 ? `(${Math.ceil(sleepLeft / 60)}m restantes)` : ''}
                </button>
              ) : (
                <button
                  onClick={() => { onAction('sleep'); setOpen(false); }}
                  className="col-span-2 py-3 bg-blue-950/30 hover:bg-blue-900/40 border border-blue-500/20 text-blue-300 text-[10px] font-black uppercase tracking-widest rounded-2xl transition-all"
                >
                  🌙 Enviar a Dormir
                </button>
              )}
            </div>
          ) : (
            <p className="text-[10px] text-slate-500 text-center py-2">
              El Axolotito está en juego — alimentación deshabilitada.
            </p>
          )}
        </div>
      </BottomSheet>
    </>
  );
}
