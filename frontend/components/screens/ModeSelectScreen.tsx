"use client";

import React from 'react';
import { Coins } from 'lucide-react';

interface ModeSelectScreenProps {
  onSelect: (mode: 'cpu' | 'multi') => void;
  /** The axo that was selected in the previous step — shown in the subtitle */
  selectedAxo?: any | null;
}

export default function ModeSelectScreen({ onSelect, selectedAxo }: ModeSelectScreenProps) {
  return (
    <div className="space-y-6">
      {/* Title */}
      <div className="text-center pt-2">
        <h2 className="text-3xl sm:text-5xl font-black italic text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-pink-400 to-[#E4007C] drop-shadow-[0_0_15px_rgba(99,102,241,0.3)] tracking-tighter uppercase">
          ¿Cómo jugamos?
        </h2>
        <p className="text-slate-400 text-xs mt-2">
          {selectedAxo
            ? <><span className="text-white font-black">{selectedAxo.name}</span> está listo · Elige el modo</>
            : 'Elige cómo quieres jugar hoy'
          }
        </p>
      </div>

      {/* Mode cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">

        {/* CPU Card */}
        <button
          onClick={() => onSelect('cpu')}
          className="relative overflow-hidden text-center p-8 border border-indigo-500/30 bg-gradient-to-b from-indigo-950 to-[var(--world-void)] hover:border-indigo-500/70 hover:shadow-[0_0_30px_rgba(99,102,241,0.35)] transition-all duration-300 group"
          style={{
            minHeight: '180px',
            borderRadius: '50% 50% 12px 12px / 55% 55% 12px 12px',
          }}
        >
          {/* Bubbles */}
          {[0.2, 0.7, 1.2, 1.8, 2.4].map((delay, i) => (
            <div
              key={i}
              className="absolute bottom-3 animate-bubble opacity-25 rounded-full bg-indigo-400"
              style={{
                width: `${5 + i * 2}px`,
                height: `${5 + i * 2}px`,
                left: `${12 + i * 17}%`,
                animationDelay: `${delay}s`,
              }}
            />
          ))}
          {/* Glow hover */}
          <div className="absolute inset-0 bg-indigo-500/0 group-hover:bg-indigo-500/5 transition-colors duration-300 pointer-events-none" />
          {/* Icon */}
          <div className="text-5xl mb-3 animate-axo-bob relative z-10">🤖</div>
          <h4 className="text-3xl font-black uppercase tracking-tighter text-white relative z-10">VS CPU</h4>
          <p className="text-xs text-slate-400 mt-1.5 relative z-10">
            Partida rápida · Resultado en segundos
          </p>
          <div className="mt-5 flex items-center justify-center gap-1.5 text-[10px] font-black text-indigo-300 bg-indigo-950/60 border border-indigo-500/20 px-3 py-1 rounded-full mx-auto w-fit relative z-10">
            <Coins size={10} /> Consumes FRJ
          </div>
        </button>

        {/* Multiplayer Card */}
        <button
          onClick={() => onSelect('multi')}
          className="relative overflow-hidden text-center p-8 border border-[var(--brand-hot)]/25 bg-gradient-to-b from-pink-950 to-[var(--world-void)] hover:border-[var(--brand-hot)]/60 hover:shadow-[0_0_30px_var(--brand-glow)] transition-all duration-300 group"
          style={{
            minHeight: '180px',
            borderRadius: '50% 50% 12px 12px / 55% 55% 12px 12px',
          }}
        >
          {/* Bubbles */}
          {[0.4, 0.9, 1.4, 2.0, 2.6].map((delay, i) => (
            <div
              key={i}
              className="absolute bottom-3 animate-bubble opacity-25 rounded-full bg-pink-400"
              style={{
                width: `${5 + i * 2}px`,
                height: `${5 + i * 2}px`,
                left: `${10 + i * 18}%`,
                animationDelay: `${delay}s`,
              }}
            />
          ))}
          {/* Glow hover */}
          <div className="absolute inset-0 bg-pink-500/0 group-hover:bg-pink-500/5 transition-colors duration-300 pointer-events-none" />
          {/* Icon */}
          <div className="text-5xl mb-3 animate-axo-wander relative z-10">👥</div>
          <h4 className="text-3xl font-black uppercase tracking-tighter text-white relative z-10">MULTIJUGADOR</h4>
          <p className="text-xs text-slate-400 mt-1.5 relative z-10">
            Compite contra otros jugadores en tiempo real
          </p>
          <div className="mt-5 flex items-center justify-center gap-1.5 text-[10px] font-black text-pink-300 bg-pink-950/60 border border-pink-500/20 px-3 py-1 rounded-full mx-auto w-fit relative z-10">
            💰 Presupuesto por partida
          </div>
        </button>
      </div>
    </div>
  );
}
