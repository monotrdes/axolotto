"use client";

import React from 'react';

// ── Types ───────────────────────────────────────────────────────────────────────

interface RollResult {
  type?: string; name?: string; amount?: number;
  rarity?: string; description?: string;
  item_metadata?: Record<string, any>; guaranteed?: boolean;
  is_legendary?: boolean; legendary_type?: string;
}

interface ResultCardProps {
  result: RollResult;
  onClose: () => void;
  closeLabel?: string;
}

// ── Helpers ─────────────────────────────────────────────────────────────────────

function getRarityStyle(rarity?: string) {
  switch (rarity?.toLowerCase()) {
    case 'legendary': return { border: 'border-yellow-400/70', bg: 'bg-yellow-950/50', text: 'text-yellow-400', label: '⭐ LEGENDARIO' };
    case 'epic':      return { border: 'border-purple-400/70', bg: 'bg-purple-950/50', text: 'text-purple-400', label: '✨ ÉPICO' };
    case 'rare':      return { border: 'border-cyan-400/70',   bg: 'bg-cyan-950/50',   text: 'text-cyan-400',  label: '🔷 RARO' };
    default:          return { border: 'border-teal-400/60',   bg: 'bg-teal-950/50',   text: 'text-teal-400',  label: '🟢 COMÚN' };
  }
}

// ── Component ───────────────────────────────────────────────────────────────────

export default function ResultCard({ result, onClose, closeLabel = '¡Aceptar!' }: ResultCardProps) {
  if (!result) return null;
  const rar = getRarityStyle(result.rarity);
  const isLegendary = result.is_legendary;
  const isAstral = result.legendary_type === 'webito_astral';
  const typeIcon =
    isAstral                    ? '🌌' :
    result.type === 'axolotito' ? '🦎' :
    result.type === 'carta'     ? '🃏' :
    result.type === 'accesorio' ? '💎' :
    result.type === 'sobre'     ? '📦' :
    result.type === 'gal'       ? '💰' : '🎁';

  if (isLegendary) {
    const cardBg = isAstral
      ? 'bg-gradient-to-br from-purple-950/90 via-indigo-950/90 to-slate-900'
      : 'bg-gradient-to-br from-amber-950/90 via-yellow-900/50 to-slate-900';
    const cardBorder = isAstral
      ? 'border-purple-400 shadow-[0_0_40px_rgba(192,132,252,0.8),0_0_80px_rgba(129,140,248,0.4)]'
      : 'border-amber-400 shadow-[0_0_40px_rgba(245,158,11,0.9),0_0_80px_rgba(251,191,36,0.5)]';
    const titleColor = isAstral
      ? 'text-transparent bg-clip-text bg-gradient-to-r from-purple-300 via-indigo-300 to-pink-300'
      : 'text-transparent bg-clip-text bg-gradient-to-r from-amber-300 via-yellow-200 to-orange-300';

    return (
      <div className={`relative w-full rounded-2xl border-2 ${cardBorder} ${cardBg} p-6 flex flex-col items-center gap-4 animate-in zoom-in duration-500`}>
        <div className={`text-[10px] font-black tracking-widest px-4 py-1 rounded-full border-2 uppercase animate-pulse ${
          isAstral ? 'text-purple-300 border-purple-400/60 bg-purple-950/60' : 'text-amber-300 border-amber-400/60 bg-amber-950/60'
        }`}>
          {isAstral ? '🌌 ¡WEBITO ASTRAL MÍTICO!' : '✨ ¡BOOSTER BRILLANTE LEGENDARIO!'}
        </div>
        <div className="text-7xl sm:text-8xl leading-none select-none drop-shadow-[0_0_30px_rgba(255,255,255,0.6)] animate-bounce">
          {typeIcon}
        </div>
        <div className="text-center space-y-2">
          <h4 className={`text-xl font-black uppercase tracking-tight ${titleColor}`}>
            {result.name || (result.legendary_type === 'webito_astral' ? 'Webito Astral' : 'Sobre Brillante')}
          </h4>
          <p className={`text-xs leading-relaxed max-w-[240px] ${isAstral ? 'text-purple-300' : 'text-amber-300'}`}>
            {isAstral
              ? '¡Una rarísima criatura cósmica! Ha ido directo a tu criadero sellada y lista para incubarse.'
              : '¡Un sobre con garantía de calidad superior! Guardado sellado en tu inventario.'}
          </p>
        </div>
        <button
          onClick={onClose}
          className={`w-full py-3 rounded-xl text-sm font-black uppercase tracking-wider transition-all active:scale-95 cursor-pointer ${
            isAstral
              ? 'bg-gradient-to-r from-purple-700 to-indigo-700 hover:from-purple-600 hover:to-indigo-600 text-white shadow-[0_5px_20px_rgba(168,85,247,0.5)]'
              : 'bg-gradient-to-r from-amber-600 to-yellow-600 hover:from-amber-500 hover:to-yellow-500 text-white shadow-[0_5px_20px_rgba(245,158,11,0.5)]'
          }`}
        >
          {closeLabel}
        </button>
      </div>
    );
  }

  return (
    <div className={`w-full rounded-2xl border ${rar.border} ${rar.bg} p-5 flex flex-col items-center gap-3 animate-in zoom-in duration-300`}>
      {result.guaranteed && (
        <div className="text-[9px] font-black text-amber-400 bg-amber-950/60 border border-amber-500/30 px-3 py-0.5 rounded-full uppercase tracking-widest animate-pulse">
          🌀 ¡Karma activado! Garantizado
        </div>
      )}
      <span className={`text-[9px] font-black tracking-widest px-3 py-0.5 rounded-full border ${rar.border} ${rar.text} uppercase`}>
        {rar.label}
      </span>
      <div className="text-5xl leading-none select-none">{typeIcon}</div>
      <div className="text-center space-y-1">
        <h4 className="text-base font-black text-white uppercase tracking-tight">
          {result.type === 'gal' ? `+${result.amount?.toFixed(0)} FRJ` : result.name || (result.type ?? '').toUpperCase()}
        </h4>
        {result.description && (
          <p className="text-slate-400 text-[11px] leading-relaxed max-w-[220px]">{result.description}</p>
        )}
      </div>
      {result.item_metadata && Object.keys(result.item_metadata).length > 0 && (
        <div className="w-full bg-slate-950/60 rounded-xl p-2.5 border border-white/5 space-y-1 text-left">
          {Object.entries(result.item_metadata).map(([key, val]: [string, any]) => {
            if (key.startsWith('bonus_') && typeof val === 'number') {
              return (
                <div key={key} className="flex justify-between items-center font-mono text-[11px]">
                  <span className="capitalize text-slate-400">{key.replace('bonus_', '')}</span>
                  <span className={`font-black ${val >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                    {val >= 0 ? '+' : ''}{val.toFixed(1)}
                  </span>
                </div>
              );
            }
            if (key === 'slot') {
              return (
                <div key={key} className="flex justify-between items-center text-[9px] uppercase font-bold text-slate-500 border-t border-white/5 pt-1 mt-1">
                  <span>Ranura</span><span className="text-white">{val}</span>
                </div>
              );
            }
            return null;
          })}
        </div>
      )}
      <button
        onClick={onClose}
        className="w-full py-2.5 bg-slate-950 hover:bg-slate-900 border border-white/10 rounded-xl text-[11px] font-black uppercase tracking-wider transition-all active:scale-95 flex items-center justify-center gap-1.5 text-slate-300 hover:text-white"
      >
        {closeLabel}
      </button>
    </div>
  );
}
