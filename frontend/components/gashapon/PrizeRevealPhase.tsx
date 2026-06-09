"use client";

import React from 'react';
import type { Tier } from './tierConfig';
import { TIER_CONFIG } from './tierConfig';
import type { GashaRarity } from './rarityConfig';
import { RARITY, rarityHsl, rarityGlow } from './rarityConfig';
import Particles from './Particles';

// ── RollResult type (subset used by Gashapon) ────────────────────────────────────

interface RollResult {
  type?: string; name?: string; amount?: number;
  rarity?: string; description?: string;
  item_metadata?: Record<string, any>;
  guaranteed?: boolean;
  is_legendary?: boolean; legendary_type?: string;
}

// ── Props ───────────────────────────────────────────────────────────────────────

interface PrizeRevealPhaseProps {
  result: RollResult;
  tier: Tier;
  rarity: GashaRarity;
  onClose: () => void;
  closeLabel?: string;
}

// ── Component ───────────────────────────────────────────────────────────────────

export default function PrizeRevealPhase({
  result,
  tier,
  rarity,
  onClose,
  closeLabel = '¡Aceptar!',
}: PrizeRevealPhaseProps) {
  const cfg = TIER_CONFIG[tier];
  const rar = RARITY[rarity];
  const isLegendary = result.is_legendary;
  const isAstral = result.legendary_type === 'webito_astral';
  const hsl = rarityHsl(rarity);
  const glow = rarityGlow(rarity);

  const typeIcon =
    isAstral                    ? '🌌' :
    result.type === 'axolotito' ? '🦎' :
    result.type === 'carta'     ? '🃏' :
    result.type === 'accesorio' ? '💎' :
    result.type === 'sobre'     ? '📦' :
    result.type === 'gal'       ? '💰' : '🎁';

  return (
    <div className="relative w-full max-w-sm mx-auto flex flex-col items-center gap-4 py-4 px-2">
      <style dangerouslySetInnerHTML={{ __html: `
        @keyframes prize-float {
          0%   { transform: translateY(30px) scale(0.5); opacity: 0; }
          40%  { transform: translateY(-8px) scale(1.05); opacity: 1; }
          60%  { transform: translateY(2px) scale(0.98); }
          100% { transform: translateY(0) scale(1); opacity: 1; }
        }
        @keyframes prize-hover {
          0%, 100% { transform: translateY(0) rotate(0deg); }
          25%  { transform: translateY(-6px) rotate(1deg); }
          75%  { transform: translateY(4px) rotate(-1deg); }
        }
        @keyframes shimmer-text {
          0%, 100% { background-position: 0% 50%; }
          50%  { background-position: 100% 50%; }
        }
        @keyframes fade-in-up {
          0%   { transform: translateY(12px); opacity: 0; }
          100% { transform: translateY(0); opacity: 1; }
        }
        .prize-float-anim  { animation: prize-float 0.6s ease-out both; }
        .prize-hover-anim  { animation: prize-hover 3s ease-in-out 0.6s infinite; }
        .shimmer-text-anim { animation: shimmer-text 2s linear infinite; background-size: 200% auto; }
        .fade-in-up-anim   { animation: fade-in-up 0.4s ease-out both; }
      `}} />

      {/* Ambient particles */}
      <Particles rarity={rarity} count={12} burst={false} durationMs={4000} />

      {/* Glow aura behind prize */}
      <div
        className="absolute top-16 w-48 h-48 rounded-full blur-3xl pointer-events-none"
        style={{ background: glow, opacity: 0.25 }}
      />

      {/* Prize icon — floats up */}
      <div className="prize-float-anim prize-hover-anim relative z-10">
        <div
          className="text-7xl sm:text-8xl leading-none select-none drop-shadow-lg"
          style={{
            filter: `drop-shadow(0 0 20px ${glow}) drop-shadow(0 0 40px ${glow})`,
          }}
        >
          {typeIcon}
        </div>
      </div>

      {/* Rarity badge */}
      <div
        className="fade-in-up-anim relative z-10 text-[10px] font-black tracking-widest px-4 py-1 rounded-full border uppercase"
        style={{
          animationDelay: '0.15s', animationFillMode: 'both',
          color: hsl, borderColor: hsl, background: `${hsl}20`,
        }}
      >
        {rar.emoji} {isLegendary ? (isAstral ? 'MÍTICO' : 'LEGENDARIO') : rar.label}
      </div>

      {/* Guaranteed karma badge */}
      {result.guaranteed && (
        <div
          className="fade-in-up-anim relative z-10 text-[9px] font-black text-amber-400 bg-amber-950/60 border border-amber-500/30 px-3 py-0.5 rounded-full uppercase tracking-widest"
          style={{ animationDelay: '0.2s', animationFillMode: 'both' }}
        >
          🌀 ¡Karma activado! Garantizado
        </div>
      )}

      {/* Prize name + quantity */}
      <div
        className="fade-in-up-anim relative z-10 text-center space-y-1"
        style={{ animationDelay: '0.25s', animationFillMode: 'both' }}
      >
        {isLegendary ? (
          <h4
            className="text-xl font-black uppercase tracking-tight shimmer-text-anim"
            style={{
              backgroundImage: isAstral
                ? 'linear-gradient(90deg, #C084FC, #A78BFA, #E879F9, #C084FC)'
                : 'linear-gradient(90deg, #FBBF24, #FCD34D, #FDE68A, #FBBF24)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              color: 'transparent',
            }}
          >
            {result.name || (isAstral ? 'Webito Astral' : 'Sobre Brillante')}
          </h4>
        ) : (
          <h4 className="text-lg font-black text-white uppercase tracking-tight">
            {result.type === 'gal' ? `+${result.amount?.toFixed(0) ?? '?'} FRJ` : result.name || (result.type ?? '').toUpperCase()}
          </h4>
        )}
        {result.description && (
          <p className="text-slate-400 text-[11px] leading-relaxed max-w-[240px] mx-auto">
            {result.description}
          </p>
        )}
      </div>

      {/* Bonus stats */}
      {result.item_metadata && Object.keys(result.item_metadata).length > 0 && (
        <div
          className="fade-in-up-anim relative z-10 w-full bg-slate-950/60 rounded-xl p-3 border border-white/5 space-y-1 text-left"
          style={{ animationDelay: '0.35s', animationFillMode: 'both' }}
        >
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

      {/* Cost info */}
      <p
        className="fade-in-up-anim relative z-10 text-[9px] text-slate-500 font-bold"
        style={{ animationDelay: '0.4s', animationFillMode: 'both' }}
      >
        {cfg.emoji} {cfg.cost} FRJ
      </p>

      {/* Tap to continue button */}
      <button
        onClick={onClose}
        className="fade-in-up-anim relative z-10 w-full py-3 rounded-xl text-sm font-black uppercase tracking-wider transition-all active:scale-95 cursor-pointer"
        style={{
          animationDelay: '0.5s', animationFillMode: 'both',
          background: `linear-gradient(135deg, ${hsl}40, rgba(5,10,20,0.9))`,
          border: `2px solid ${hsl}60`,
          color: 'white',
          boxShadow: `0 0 18px ${glow}`,
          letterSpacing: '0.1em',
        }}
      >
        {closeLabel}
      </button>
    </div>
  );
}
