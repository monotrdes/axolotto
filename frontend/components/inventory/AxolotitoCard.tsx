"use client";
import React from 'react';
import { API_BASE } from '@/lib/api';

interface AxolotitoCardProps {
  axolotito: any;
  onClick: () => void;
}

export default function AxolotitoCard({ axolotito, onClick }: AxolotitoCardProps) {
  let borderClass = "border-slate-800/80 hover:border-[#E4007C]/50 hover:scale-105 hover:z-10";
  if (axolotito.stat_luck > 99.0) borderClass = "border-cyan-500 shadow-[0_0_15px_rgba(6,182,212,0.3)] hover:scale-105 hover:z-10";
  else if (axolotito.stat_luck > 80.0) borderClass = "border-amber-400 shadow-[0_0_15px_rgba(245,158,11,0.3)] hover:scale-105 hover:z-10";

  return (
    <div
      key={axolotito.id}
      onClick={onClick}
      className={`bg-slate-950 rounded-3xl p-4 border transition-all duration-300 flex flex-col cursor-pointer ${borderClass}`}
    >
      <div className="relative aspect-square w-full rounded-2xl bg-slate-900/60 border border-white/5 flex items-center justify-center p-2 mb-3">
        <img
          src={`${API_BASE}/metadata/axolotito/${axolotito.blockchain_token_id}.svg`}
          alt={axolotito.name}
          className="w-full h-full object-contain"
        />
        <div className="absolute top-2 left-2 bg-black/60 px-2 py-0.5 rounded text-[8px] font-black text-slate-400 uppercase tracking-widest border border-white/5">
          Nivel {axolotito.level}
        </div>
      </div>
      <h4 className="text-xs font-black text-white uppercase tracking-tight truncate mb-1">{axolotito.name}</h4>
      <div className="flex justify-between items-center text-[9px] text-slate-500">
        <span>Token #{axolotito.blockchain_token_id}</span>
        <span className="font-bold text-pink-400 uppercase">{axolotito.skin_color.replace(/_/g, ' ')}</span>
      </div>
      <div className="mt-3 space-y-1">
        <div className="flex justify-between text-[8px] font-black uppercase text-slate-400">
          <span>Energía</span><span>{axolotito.energy_current} / {axolotito.stat_stamina}</span>
        </div>
        <div className="h-1 bg-black rounded-full overflow-hidden">
          <div className="h-full bg-green-500 transition-all duration-300" style={{ width: `${(axolotito.energy_current / axolotito.stat_stamina) * 100}%` }} />
        </div>
      </div>
      <button className="w-full mt-4 py-1.5 bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-white font-bold rounded-lg text-[9px] uppercase tracking-wider transition-colors border border-slate-800">
        Ver Detalles
      </button>
    </div>
  );
}
