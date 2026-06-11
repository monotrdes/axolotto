"use client";
import React, { useState } from 'react';
import { X, Sparkles, ArrowRight, Crown, Users } from 'lucide-react';
import BottomSheet from '@/components/ui/BottomSheet';
import { statColors } from '@/constants/santuario';
import { obtenerEstiloHuevo } from '@/utils/santuario';

interface PadrinoSelectSheetProps {
  inc: any;
  axolotitos: any[];
  onClose: () => void;
  onConfirm: (incId: number, padrinoId: number) => void;
}

const STAT_KEYS = [
  { key: 'luck', icon: '✨', label: 'Suerte' },
  { key: 'focus', icon: '👁️', label: 'Ojo' },
  { key: 'stamina', icon: '🔋', label: 'Pila' },
  { key: 'salinity', icon: '🧂', label: 'Sal' },
] as const;

export default function PadrinoSelectSheet({
  inc,
  axolotitos,
  onClose,
  onConfirm,
}: PadrinoSelectSheetProps) {
  const [chosenId, setChosenId] = useState<number | null>(null);
  const estilos = obtenerEstiloHuevo(inc.name);

  const eligibleAxos = (axolotitos || []).filter(axo =>
    !axo.is_frozen_by_vip &&
    axo.status !== "sleeping"
  );

  const chosenAxo = eligibleAxos.find(a => a.id === chosenId);
  const transferPct = (chosenAxo?.level ?? 1) >= 20 ? 15 : 10;

  return (
    <BottomSheet open={true} onClose={onClose} accent="#A78BFA">
      <div className="px-5 pb-8 pt-2">

        {/* ── Header ── */}
        <div className="flex items-start justify-between mb-4">
          <div>
            <span className="text-[9px] font-black uppercase tracking-widest px-2 py-0.5 rounded-full border text-purple-400 border-purple-500/30 bg-purple-950/30">
              🐾 Apadrinamiento
            </span>
            <h3 className="text-lg font-black text-white mt-1.5 leading-tight">
              Elige un Padrino
            </h3>
            <p className="text-[10px] text-slate-400 mt-0.5 max-w-xs leading-relaxed">
              Un Axolotito adulto que guiará a <span className="text-white font-bold">{inc.name}</span> durante {inc.required_games || (inc.rarity === "common" ? 3 : inc.rarity === "rare" ? 5 : 7)} partidas de imprinting.
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-full bg-slate-800/60 border border-white/5 text-slate-500 hover:text-white transition-colors mt-1 shrink-0"
          >
            <X size={14} />
          </button>
        </div>

        {/* ── Egg hero chip ── */}
        <div className="flex items-center gap-3 mb-5 p-3 rounded-2xl bg-slate-950/50 border border-white/5">
          <div
            className="text-4xl shrink-0 leading-none"
            style={{ filter: `drop-shadow(0 0 10px ${estilos.aura})` }}
          >
            🥚
          </div>
          <div className="min-w-0">
            <div className="text-xs font-black text-white">{inc.name}</div>
            <div className="text-[9px] text-slate-500 font-bold mt-0.5">
              {inc.rarity ? inc.rarity.charAt(0).toUpperCase() + inc.rarity.slice(1) : 'Común'} · Pureza {inc.genetic_purity?.toFixed(1) ?? '100.0'}%
            </div>
            <div className="text-[8px] text-purple-400/70 font-bold mt-0.5">
              El padrino transferirá ~{transferPct}% de sus stats como base genética
            </div>
          </div>
        </div>

        {/* ── Eligible axolotitos ── */}
        {eligibleAxos.length === 0 ? (
          <div className="flex flex-col items-center gap-3 py-8 text-center">
            <span className="text-5xl">🦎</span>
            <div>
              <p className="text-sm font-black text-slate-400">
                Sin Axolotitos elegibles
              </p>
              <p className="text-[10px] text-slate-600 mt-1 max-w-xs leading-relaxed">
                Necesitas un Axolotito despierto, sin congelamiento VIP, y con menos de 3 mentorías previas.
              </p>
            </div>
          </div>
        ) : (
          <div className="space-y-2 mb-5 max-h-[40vh] overflow-y-auto pr-1 scrollbar-thin scrollbar-thumb-slate-800">
            {eligibleAxos.map((axo) => {
              const isSelected = chosenId === axo.id;
              const canMentor = (axo.mentorship_count ?? 0) < 3;
              const energyPct = Math.min(100, ((axo.energy_current ?? 0) / (axo.stat_stamina || 100)) * 100);

              return (
                <button
                  key={axo.id}
                  type="button"
                  onClick={() => canMentor && setChosenId(axo.id)}
                  disabled={!canMentor}
                  className={`w-full text-left p-3 rounded-2xl border transition-all group ${
                    !canMentor
                      ? 'bg-slate-900/30 border-white/3 opacity-40 cursor-not-allowed'
                      : isSelected
                        ? 'bg-purple-950/50 border-purple-500/70 shadow-[0_0_18px_rgba(167,139,250,0.2)]'
                        : 'bg-slate-900/60 border-white/5 hover:border-purple-500/30 hover:bg-slate-900/80'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    {/* Avatar */}
                    <div
                      className="w-12 h-12 rounded-xl shrink-0 flex items-center justify-center text-2xl relative overflow-hidden"
                      style={{
                        background: isSelected
                          ? 'linear-gradient(135deg, rgba(167,139,250,0.3), rgba(139,92,246,0.15))'
                          : 'linear-gradient(135deg, rgba(30,20,8,0.8), rgba(10,5,1,0.9))',
                        border: isSelected ? '1.5px solid rgba(167,139,250,0.6)' : '1px solid rgba(255,255,255,0.06)',
                        boxShadow: isSelected ? '0 0 12px rgba(167,139,250,0.25)' : undefined,
                      }}
                    >
                      <span className="relative z-10">🐾</span>
                    </div>

                    {/* Info */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-1.5">
                        <span className="text-sm font-black text-white truncate">
                          {axo.name || `Axolotito #${axo.id}`}
                        </span>
                        {axo.is_main && (
                          <Crown size={10} className="text-amber-400 shrink-0" />
                        )}
                      </div>
                      <div className="flex items-center gap-2 mt-0.5">
                        <span className="text-[9px] font-bold text-slate-400">
                          Nv.{axo.level ?? 1}
                        </span>
                        <span className="text-[9px] font-bold text-purple-400/80">
                          <Users size={9} className="inline mr-0.5" />
                          {axo.mentorship_count ?? 0}/3 mentorías
                        </span>
                      </div>

                      {/* Energy bar */}
                      <div className="flex items-center gap-1.5 mt-1.5">
                        <span className="text-[7px] font-black text-slate-600 w-8 shrink-0">⚡ ENE</span>
                        <div className="flex-1 h-1 bg-slate-800 rounded-full overflow-hidden">
                          <div
                            className="h-full rounded-full transition-all duration-300"
                            style={{
                              width: `${energyPct}%`,
                              background: energyPct > 60
                                ? 'linear-gradient(90deg, #4ade80, #22c55e)'
                                : energyPct > 25
                                  ? 'linear-gradient(90deg, #fbbf24, #f59e0b)'
                                  : 'linear-gradient(90deg, #f87171, #ef4444)',
                            }}
                          />
                        </div>
                        <span className="text-[7px] font-black text-slate-500 w-7 text-right tabular-nums">
                          {energyPct.toFixed(0)}%
                        </span>
                      </div>
                    </div>

                    {/* Selection indicator */}
                    <div className="shrink-0">
                      {!canMentor ? (
                        <span className="text-[8px] font-black text-rose-500 bg-rose-950/50 px-1.5 py-0.5 rounded-full border border-rose-500/20">
                          Límite
                        </span>
                      ) : isSelected ? (
                        <div className="w-6 h-6 rounded-full bg-purple-500 flex items-center justify-center shadow-[0_0_10px_rgba(167,139,250,0.5)]">
                          <span className="text-white text-[10px] font-black">✓</span>
                        </div>
                      ) : (
                        <div className="w-5 h-5 rounded-full border-2 border-slate-700 group-hover:border-purple-500/50 transition-colors" />
                      )}
                    </div>
                  </div>

                  {/* Stat preview when selected */}
                  {isSelected && (
                    <div className="mt-3 pt-3 border-t border-purple-500/20">
                      <div className="text-[7px] font-black text-slate-500 uppercase tracking-widest mb-2">
                        Stats que heredará el webito (~{transferPct}%)
                      </div>
                      <div className="space-y-1.5">
                        {STAT_KEYS.map(({ key, icon, label }) => {
                          const statKey = key === 'luck' ? 'stat_luck' : key === 'focus' ? 'stat_focus' : key === 'stamina' ? 'stat_stamina' : 'stat_salinity';
                          const val = axo[statKey] ?? axo[key] ?? 0;
                          const maxVal = key === 'stamina' ? 200 : 100;
                          const inherited = (val * transferPct / 100).toFixed(1);
                          return (
                            <div key={key} className="flex items-center gap-1.5">
                              <span className="text-[9px] w-4 text-center shrink-0">{icon}</span>
                              <div className="flex-1 flex items-center gap-2">
                                <span className="text-[8px] font-bold text-slate-500 w-8 shrink-0">{label}</span>
                                <div className="flex-1 h-1 bg-slate-800/80 rounded-full overflow-hidden">
                                  <div
                                    className={`h-full ${statColors[key] || 'bg-purple-500'} rounded-full transition-all duration-500`}
                                    style={{ width: `${Math.min(100, (val / maxVal) * 100)}%` }}
                                  />
                                </div>
                                <span className="text-[8px] font-black text-slate-300 w-7 text-right tabular-nums">
                                  {val.toFixed(0)}
                                </span>
                                <ArrowRight size={8} className="text-purple-500 shrink-0" />
                                <span className="text-[8px] font-black text-purple-300 w-7 text-right tabular-nums">
                                  +{inherited}
                                </span>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  )}
                </button>
              );
            })}
          </div>
        )}

        {/* ── Info tip ── */}
        {eligibleAxos.length > 0 && !chosenId && (
          <div className="flex items-center gap-2 mb-4 p-2.5 rounded-xl bg-amber-950/20 border border-amber-500/15">
            <Sparkles size={12} className="text-amber-400 shrink-0" />
            <p className="text-[9px] text-amber-300/70 font-bold leading-snug">
              Elige un Padrino con buenos stats para maximizar el potencial genético del webito.
            </p>
          </div>
        )}

        {/* ── CTA ── */}
        {chosenId !== null && chosenAxo && (
          <button
            type="button"
            onClick={() => onConfirm(inc.id, chosenId)}
            className="w-full py-4 rounded-2xl font-black uppercase text-sm tracking-widest bg-gradient-to-r from-purple-600 to-[#E4007C] hover:from-purple-500 hover:to-[#FF1493] text-white shadow-[0_0_25px_rgba(167,139,250,0.4)] active:scale-95 transition-all flex items-center justify-center gap-2"
          >
            <span>🐾</span>
            Apadrinar con {chosenAxo.name || `#${chosenAxo.id}`}
            <span>🥚</span>
          </button>
        )}

        {/* Close when no eligible */}
        {eligibleAxos.length === 0 && (
          <button
            onClick={onClose}
            className="w-full py-3 rounded-xl bg-slate-800 text-slate-400 hover:text-white font-black text-xs uppercase tracking-widest transition-all"
          >
            Cerrar
          </button>
        )}
      </div>
    </BottomSheet>
  );
}
