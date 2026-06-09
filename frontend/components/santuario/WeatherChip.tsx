"use client";
import React, { useState } from 'react';

export default function WeatherChip({ clima }: { clima: any }) {
  const [open, setOpen] = useState(false);
  if (!clima) return null;
  return (
    <div className="mb-3 flex justify-center">
      <button
        onClick={() => setOpen(p => !p)}
        className="bg-[#060F1A]/90 backdrop-blur-md border border-white/8 rounded-2xl px-4 py-2 flex items-center gap-3 shadow-lg transition-all hover:border-white/15 active:scale-95"
      >
        <span className="text-xl">{clima.emoji_time}</span>
        <div>
          <div className="text-[8px] font-black text-[#E4007C] uppercase tracking-widest leading-none">Xochimilco</div>
          <div className="text-xs font-black text-white leading-tight">{clima.name}</div>
        </div>
        <div className="flex gap-2 ml-2 pl-2 border-l border-white/10">
          <div className="text-center">
            <div className="text-[7px] text-slate-500">❄️</div>
            <div className="text-[10px] font-black text-cyan-400">{clima.loss_rate}%/h</div>
          </div>
          <div className="text-center">
            <div className="text-[7px] text-slate-500">🔥</div>
            <div className="text-[10px] font-black text-amber-400">{clima.heat_multiplier}x</div>
          </div>
        </div>
      </button>

      {open && (
        <div className="fixed inset-0 z-[200] flex items-end justify-center p-4 pb-24" onClick={() => setOpen(false)}>
          <div
            className="bg-[#060F1A]/95 backdrop-blur-xl border border-white/10 rounded-3xl p-5 max-w-sm w-full shadow-2xl"
            onClick={e => e.stopPropagation()}
          >
            <div className="flex items-center gap-3 mb-3">
              <span className="text-3xl">{clima.emoji_time}</span>
              <div>
                <div className="text-[9px] font-black text-[#E4007C] uppercase tracking-widest">Clima · {clima.time_label}</div>
                <div className="text-base font-black text-white">{clima.name}</div>
              </div>
            </div>
            <p className="text-slate-400 text-xs leading-relaxed mb-4">{clima.desc}</p>
            <div className="grid grid-cols-4 gap-2 text-center">
              {[
                { l: 'Frío',  v: `${clima.loss_rate}%/h`,                    c: 'text-cyan-400'   },
                { l: 'Calor', v: `${clima.heat_multiplier}x`,                 c: 'text-amber-400'  },
                { l: 'ADN',   v: `${clima.stats_multiplier}x`,                c: 'text-emerald-400'},
                { l: 'Freeze',v: `${Math.round(clima.freeze_chance * 100)}%`, c: 'text-red-400'    },
              ].map(s => (
                <div key={s.l} className="bg-black/40 rounded-xl p-2 border border-white/5">
                  <div className={`text-sm font-black ${s.c}`}>{s.v}</div>
                  <div className="text-[7px] text-slate-600 uppercase mt-0.5">{s.l}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
