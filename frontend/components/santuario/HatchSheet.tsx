"use client";
import React, { useState } from 'react';
import { X } from 'lucide-react';
import BottomSheet from '@/components/ui/BottomSheet';
import { statNames, statColors, traitNames } from '@/constants/santuario';
import { API_BASE } from '@/lib/api';

const API = `${API_BASE}`;

export default function HatchSheet({ axolotito, onClose }: { axolotito: any; onClose: () => void }) {
  const [showTech, setShowTech] = useState(false);

  const mutType = axolotito.mutation_type;
  const mut = mutType === 'mítica'
    ? { emoji: '✨', label: 'Mutación Mítica',    bg: 'bg-indigo-950/70', border: 'border-indigo-400/40', text: 'text-indigo-300', desc: '¡Rasgo cosmético místico raro!' }
    : mutType === 'inestable'
    ? { emoji: '⚠️', label: 'Mutación Inestable', bg: 'bg-rose-950/70',   border: 'border-rose-400/40',   text: 'text-rose-300',   desc: '¡Degradación genética detectada!' }
    : { emoji: '🧬', label: 'Incubación Exitosa', bg: 'bg-emerald-950/70',border: 'border-emerald-400/40',text: 'text-emerald-300',desc: 'Bonos de ADN transferidos con éxito.' };

  const purity = axolotito.genetic_purity ?? 100;
  const purityColor = purity >= 100 ? 'text-cyan-400' : purity >= 90 ? 'text-emerald-400' : purity >= 70 ? 'text-amber-400' : 'text-rose-500';

  return (
    <BottomSheet open={true} onClose={onClose} accent="#E4007C">
      <div className="px-5 pb-8 pt-3">

        {/* ── Header ── */}
        <div className="flex items-start justify-between mb-4">
          <div>
            <div className="flex items-center gap-1.5 mb-1">
              <span className="text-base">🎉</span>
              <span className="text-[9px] font-black text-pink-400 uppercase tracking-widest">¡Nuevo Axolotito!</span>
              <span className="text-base">🐣</span>
            </div>
            <h3 className="text-xl font-black leading-tight"
              style={{ background: 'linear-gradient(90deg,#f472b6,#c084fc)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              {axolotito.name}
            </h3>
          </div>
          <button onClick={onClose} className="p-2 rounded-full bg-slate-800/60 border border-white/5 text-slate-500 hover:text-white transition-colors mt-1">
            <X size={14} />
          </button>
        </div>

        {/* ── Mutation banner ── */}
        <div className={`w-full ${mut.bg} border ${mut.border} rounded-2xl px-4 py-3 flex items-center gap-3 mb-4`}>
          <span className="text-2xl shrink-0">{mut.emoji}</span>
          <div className="flex-1 min-w-0">
            <div className={`text-xs font-black uppercase tracking-widest ${mut.text}`}>{mut.label}</div>
            <div className="text-[9px] text-slate-400 mt-0.5 leading-snug">{mut.desc}</div>
          </div>
          <div className="text-right shrink-0 border-l border-white/10 pl-3">
            <div className="text-[7px] font-black text-slate-500 uppercase">Pureza</div>
            <div className={`text-sm font-black ${purityColor}`}>{purity.toFixed(1)}%</div>
            <div className="text-[8px] font-black text-amber-400 mt-0.5">×{(purity / 100).toFixed(2)}</div>
          </div>
        </div>

        {/* ── Hero row: SVG + key numbers ── */}
        <div className="flex gap-4 mb-5">
          <div className="w-24 h-24 shrink-0 rounded-2xl border border-white/8 flex items-center justify-center p-2 shadow-inner overflow-hidden relative"
            style={{ background: 'linear-gradient(160deg,#1a0d2e,#0d1a14)' }}>
            <div className="absolute inset-0 bg-gradient-to-t from-pink-500/15 via-transparent to-purple-500/10 pointer-events-none" />
            <img
              src={`${API}/metadata/axolotito/${axolotito.blockchain_token_id}.svg`}
              alt={axolotito.name}
              className="w-full h-full object-contain animate-axo-bob relative z-10"
            />
          </div>
          <div className="flex-1 flex flex-col justify-center gap-2.5">
            <div className="flex items-center justify-between">
              <span className="text-[8px] font-black text-slate-500 uppercase tracking-widest">Mult. ADN</span>
              <span className="text-sm font-black text-amber-400">×{(purity / 100).toFixed(2)}</span>
            </div>
            {axolotito.salinity_penalty > 0 && (
              <div className="flex items-center justify-between">
                <span className="text-[8px] font-black text-slate-500 uppercase tracking-widest">Salinidad extra</span>
                <span className="text-sm font-black text-rose-400">+{axolotito.salinity_penalty.toFixed(1)}</span>
              </div>
            )}
            <div className="h-px bg-white/5" />
            <div className="text-[8px] font-black text-slate-600 uppercase tracking-widest">
              #{axolotito.blockchain_token_id}
            </div>
          </div>
        </div>

        {/* ── Stats 2-col ── */}
        {axolotito.stats && (
          <div className="mb-4">
            <div className="text-[9px] font-black text-slate-500 uppercase tracking-widest mb-2">📊 Estadísticas</div>
            <div className="grid grid-cols-2 gap-x-5 gap-y-2.5">
              {(['luck','focus','stamina','salinity'] as const)
                .filter(k => axolotito.stats[k] !== undefined)
                .map((k) => {
                const value = Number(axolotito.stats[k]);
                const maxVal = k === 'stamina' ? 200 : 100;
                const pct = Math.min(100, (value / maxVal) * 100);
                const isSal = k === 'salinity';
                return (
                  <div key={k}>
                    <div className="flex justify-between text-[8px] font-black text-slate-500 uppercase mb-0.5">
                      <span>{statNames[k] || k}{isSal && <span className="ml-1 text-red-400 normal-case">↓ mejor</span>}</span>
                      <span className={isSal ? 'text-red-400' : 'text-white'}>{value.toFixed(1)}</span>
                    </div>
                    <div className="h-1.5 bg-slate-800 rounded-full overflow-hidden">
                      <div className={`h-full ${statColors[k] || 'bg-teal-500'} rounded-full transition-all duration-700`}
                        style={{ width: `${pct}%` }} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* ── Traits chips ── */}
        {axolotito.traits && Object.keys(axolotito.traits).length > 0 && (
          <div className="mb-4">
            <div className="text-[9px] font-black text-slate-500 uppercase tracking-widest mb-2">🧬 Rasgos físicos</div>
            <div className="flex flex-wrap gap-1.5">
              {Object.entries(axolotito.traits).map(([key, val]: [string, any]) => (
                <span key={key} className="text-[8px] font-bold text-pink-300 bg-pink-950/40 border border-pink-500/20 px-2 py-0.5 rounded-full uppercase tracking-wide">
                  {traitNames[key] ? `${traitNames[key]}: ` : ''}{String(val).replace(/_/g, ' ')}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* ── Tech data collapsible ── */}
        <button
          onClick={() => setShowTech(p => !p)}
          className="w-full flex items-center justify-between text-[9px] font-black text-slate-600 uppercase tracking-widest py-2 hover:text-slate-400 transition-colors"
        >
          <span>🔗 Datos técnicos (tx · DNA)</span>
          <span className="text-[8px]">{showTech ? '▲' : '▼'}</span>
        </button>
        {showTech && (
          <div className="bg-slate-900/80 border border-white/5 rounded-xl p-3 font-mono mb-4">
            <div className="text-[8px] font-black text-slate-500 uppercase tracking-widest mb-1">TX Hash</div>
            <div className="text-slate-400 select-all text-[9px] break-all">{axolotito.tx_hash}</div>
            <div className="text-[8px] font-black text-slate-500 uppercase tracking-widest mt-2 mb-1">DNA Packed</div>
            <div className="text-[#FF8DA1] select-all text-[9px] font-bold break-all">{axolotito.dna}</div>
          </div>
        )}

        {/* ── CTA ── */}
        <button
          onClick={onClose}
          className="w-full py-4 bg-gradient-to-r from-purple-600 to-[#E4007C] text-white font-black rounded-2xl uppercase tracking-widest text-xs shadow-[0_0_20px_rgba(228,0,124,0.35)] active:scale-95 transition-all mt-1"
        >
          🪺 ¡Al Hábitat!
        </button>
      </div>
    </BottomSheet>
  );
}
