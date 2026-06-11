"use client";
import React from 'react';
import { Clock, X, Star, Sparkles } from 'lucide-react';
import BottomSheet from '@/components/ui/BottomSheet';
import { obtenerEstiloHuevo, obtenerFaseHuevo } from '@/utils/santuario';
import { ImprintingProgress } from '../ImprintingProgress';
import PadrinoSelectSheet from './PadrinoSelectSheet';

interface EggSheetProps {
  inc: any;
  axolotitos: any[];
  onClose: () => void;
  onHatch: (id: number) => void;
  onStartImprinting: (incId: number, padrinoId: number) => void;
  hatchingId: number | null;
}

export default function EggSheet({
  inc,
  axolotitos,
  onClose,
  onHatch,
  onStartImprinting,
  hatchingId,
}: EggSheetProps) {
  const estilos  = obtenerEstiloHuevo(inc.name);
  const faseInfo = obtenerFaseHuevo(inc);
  const purity   = inc.genetic_purity ?? 100.0;

  const [showPadrinoSelect, setShowPadrinoSelect] = React.useState(false);

  const isTutorial = (inc.tutorial_phase ?? 0) > 0;
  const isReady = isTutorial ? inc.horasRestantes === 0 : !!inc.imprinting_complete;

  const totalBonos = [
    inc.bonus_focus, inc.bonus_stamina, inc.bonus_luck,
  ].reduce((s: number, v: number) => s + (v || 0), 0);

  return (
    <>
    <BottomSheet open={true} onClose={onClose}>
          <div className="px-5 pb-6 pt-3">
            {/* Header */}
            <div className="flex items-start justify-between mb-4">
              <div>
                <span className="text-[9px] font-black uppercase tracking-widest px-2 py-0.5 rounded-full border text-[#E4007C] border-[#E4007C]/30 bg-pink-950/30">
                  {isReady ? '🐣 ¡Listo!' : `Fase ${faseInfo.fase}`}
                </span>
                <h3 className="text-lg font-black text-white mt-1 leading-tight">{inc.name}</h3>
                {isReady
                  ? <div className="text-[10px] text-pink-400 font-black mt-0.5 animate-pulse">¡Listo para eclosionar!</div>
                  : <div className="flex items-center gap-1 mt-0.5"><Clock size={9} className="text-slate-500" /><span className="text-[10px] text-slate-400 font-bold">{inc.horasRestantes}h restantes</span></div>
                }
              </div>
              <button onClick={onClose} className="p-2 rounded-full bg-slate-800/60 border border-white/5 text-slate-500 hover:text-white transition-colors mt-1">
                <X size={14} />
              </button>
            </div>

            {/* Egg */}
            <div className="relative flex justify-center mb-5">
              <button
                onClick={() => { if (isReady) onHatch(inc.id); }}
                disabled={isReady && hatchingId === inc.id}
                className={`relative text-7xl leading-none select-none transition-transform active:scale-90 ${faseInfo.clase}`}
                style={{
                  '--egg-shadow': estilos.shadow,
                  filter: `drop-shadow(0 0 12px ${estilos.aura})`,
                } as React.CSSProperties}
              >
                {isReady ? '🐣' : '🥚'}
              </button>
            </div>

            {/* Hint */}
            <p className="text-center text-[9px] text-slate-600 font-bold uppercase tracking-widest mb-4">
              {isReady
                ? '¡Toca el huevo para eclosionar!'
                : isTutorial
                  ? 'El webito eclosionará solo al cumplir su tiempo de incubación.'
                  : inc.imprinting_padrino_id
                    ? 'Juega partidas con el Padrino seleccionado para imprimir el huevo.'
                    : 'Toca "Seleccionar Padrino" para iniciar el imprinting.'}
            </p>

            {/* Bars */}
            <div className="space-y-3 mb-5">
              <div>
                <div className="flex justify-between text-[9px] font-black text-slate-400 uppercase mb-1">
                  <span>🧬 Pureza</span>
                  <span className={
                    purity >= 100 ? 'text-cyan-400' : purity >= 90 ? 'text-emerald-400' :
                    purity >= 70  ? 'text-amber-400' : 'text-rose-500 animate-pulse'
                  }>{purity.toFixed(1)}%</span>
                </div>
                <div className="h-2 bg-slate-800 rounded-full overflow-hidden relative">
                  <div className="absolute left-[83.3%] top-0 bottom-0 w-px bg-white/20 z-10" />
                  <div
                    className={`h-full rounded-full transition-all duration-300 ${
                      purity >= 100 ? 'bg-gradient-to-r from-teal-400 to-indigo-500' :
                      purity >= 90  ? 'bg-emerald-500' : purity >= 70 ? 'bg-amber-500' : 'bg-rose-600 animate-pulse'
                    }`}
                    style={{ width: `${(purity / 120) * 100}%` }}
                  />
                </div>
              </div>

              {totalBonos > 0 && (
                <div className="flex items-center gap-1 justify-center">
                  <Star size={9} className="text-emerald-400" />
                  <span className="text-[9px] text-emerald-400 font-black">+{totalBonos.toFixed(1)} ADN acumulado</span>
                </div>
              )}
            </div>

            {/* Godfather selection trigger for non-tutorial eggs */}
            {!isReady && !isTutorial && !inc.imprinting_padrino_id && (
              <div className="mb-5">
                <button
                  type="button"
                  onClick={() => setShowPadrinoSelect(true)}
                  className="w-full p-4 rounded-2xl bg-gradient-to-br from-purple-950/30 to-slate-950/40 border border-purple-500/20 hover:border-purple-500/50 transition-all group text-left"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-purple-900/30 border border-purple-500/30 flex items-center justify-center text-xl shrink-0 group-hover:scale-110 transition-transform">
                      🐾
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="text-xs font-black text-purple-300 group-hover:text-purple-200 transition-colors">
                        Seleccionar Padrino
                      </div>
                      <div className="text-[9px] text-slate-500 font-bold mt-0.5">
                        Elige un Axolotito para guiar el imprinting
                      </div>
                    </div>
                    <Sparkles size={16} className="text-purple-500 shrink-0 group-hover:text-purple-400 transition-colors" />
                  </div>
                </button>
              </div>
            )}

            {/* Imprinting progress for non-tutorial eggs */}
            {!isReady && !isTutorial && inc.imprinting_padrino_id && (() => {
              const statusObj = {
                incubation_id: inc.id,
                imprinting_started: true,
                imprinting_complete: !!inc.imprinting_complete,
                games_played: inc.imprinting_games_played ?? 0,
                required_games: inc.required_games || (inc.rarity === "common" ? 3 : inc.rarity === "rare" ? 5 : 7),
                padrino_name: inc.padrino_name || `Padrino #${inc.imprinting_padrino_id}`,
                current_stats: {
                  suerte_delta: inc.bonus_luck ?? 0,
                  ojo_delta: inc.bonus_focus ?? 0,
                  pila_delta: inc.bonus_stamina ?? 0,
                  sal_delta: inc.bonus_salinity_adj ?? 0,
                }
              };
              return (
                <div className="mb-5">
                  <ImprintingProgress status={statusObj} />
                </div>
              );
            })()}

            {/* Action */}
            {isReady ? (
              <button
                onClick={() => onHatch(inc.id)}
                disabled={hatchingId === inc.id}
                className="w-full py-3.5 rounded-2xl font-black uppercase text-sm tracking-widest bg-gradient-to-r from-[#E4007C] to-amber-500 hover:from-[#FF1493] hover:to-amber-400 text-white border-none animate-pulse shadow-lg shadow-pink-500/30 active:scale-95 transition-all disabled:opacity-60"
              >
                {hatchingId === inc.id ? 'Eclosionando…' : '✨ ¡Eclosionar! ✨'}
              </button>
            ) : (
              <div className="text-center text-[10px] text-slate-500 font-bold py-2">
                {isTutorial
                  ? 'Vuelve cuando el webito esté listo. 🥚'
                  : inc.imprinting_padrino_id
                    ? 'El webito estará listo tras jugar las partidas requeridas con su padrino. 🐾'
                    : 'Asigna un padrino para iniciar el imprinting. 🥚'}
              </div>
            )}
          </div>
    </BottomSheet>

    {/* ── Padrino Selection Sheet ── */}
    {showPadrinoSelect && (
      <PadrinoSelectSheet
        inc={inc}
        axolotitos={axolotitos}
        onClose={() => setShowPadrinoSelect(false)}
        onConfirm={(incId, padrinoId) => {
          onStartImprinting(incId, padrinoId);
          setShowPadrinoSelect(false);
        }}
      />
    )}
  </>
  );
}
