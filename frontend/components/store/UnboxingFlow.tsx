"use client";
import React from 'react';
import { createPortal } from 'react-dom';
import type { AdoptionParticle } from '@/types/store';

interface UnboxingFlowProps {
  open: boolean;
  itemComprado: any | null;
  mensajeAdopcion: string;
  txHash: string;
  abrirAhoraLoading: boolean;
  adopcionParticles: AdoptionParticle[];

  onAbrirAhora: () => void;
  onCerrar: () => void;
  onIrAlInventario: () => void;
  onIrAlCriadero: () => void;
  onIrATablas: () => void;
  onSeguirComprando: () => void;
}

function renderPortal(content: React.ReactNode) {
  if (typeof window === 'undefined') return null;
  return createPortal(content, document.body);
}

export default function UnboxingFlow({
  open,
  itemComprado,
  mensajeAdopcion,
  txHash,
  abrirAhoraLoading,
  adopcionParticles,
  onAbrirAhora,
  onCerrar,
  onIrAlInventario,
  onIrAlCriadero,
  onIrATablas,
  onSeguirComprando,
}: UnboxingFlowProps) {
  if (!open) return null;

  const itemType = itemComprado?.item_type?.toLowerCase();
  const esTabla = itemType === 'board';
  const esFRJ = itemType === 'currency_pack';
  const esBooster = itemType === 'booster';
  const esFoil = esBooster && itemComprado?.item_metadata?.pack_theme === 'foil';

  let titulo = '¡Webito Adoptado!';
  let borderColorClass = 'border-[#E4007C] shadow-[0_0_50px_rgba(228,0,124,0.4)]';
  let titleTextColor = 'text-[#E4007C]';
  let emoji = '🥚';
  let dropShadowColor = 'drop-shadow-[0_0_30px_rgba(228,0,124,0.6)]';
  let btnBg =
    'bg-gradient-to-r from-[#E4007C] to-[#B30062] hover:from-[#FF1493] hover:to-[#E4007C] shadow-[0_5px_15px_rgba(228,0,124,0.4)]';
  let btnText = 'Ir al Criadero';

  if (esTabla) {
    titulo = '¡Tabla Adquirida!';
    borderColorClass = 'border-emerald-500 shadow-[0_0_50px_rgba(16,185,129,0.4)]';
    titleTextColor = 'text-emerald-400';
    emoji = '📋';
    dropShadowColor = 'drop-shadow-[0_0_30px_rgba(16,185,129,0.6)]';
    btnBg =
      'bg-gradient-to-r from-emerald-600 to-teal-500 hover:from-emerald-500 hover:to-teal-400 shadow-[0_5px_15px_rgba(16,185,129,0.4)]';
  } else if (esFRJ) {
    titulo = '¡Frijolitos Recargadas!';
    borderColorClass = 'border-amber-400 shadow-[0_0_50px_rgba(245,158,11,0.4)]';
    titleTextColor = 'text-amber-400';
    emoji = '🪙';
    dropShadowColor = 'drop-shadow-[0_0_30px_rgba(245,158,11,0.6)]';
    btnBg =
      'bg-gradient-to-r from-amber-500 to-yellow-400 hover:from-amber-400 hover:to-yellow-300 shadow-[0_5px_15px_rgba(245,158,11,0.4)]';
  } else if (esBooster) {
    titulo = esFoil ? '¡Sobre Brillante Sellado!' : '¡Sobre Guardado!';
    borderColorClass = esFoil
      ? 'border-amber-400 shadow-[0_0_60px_rgba(245,158,11,0.6),0_0_100px_rgba(168,85,247,0.25)]'
      : 'border-purple-500 shadow-[0_0_50px_rgba(168,85,247,0.4)]';
    titleTextColor = esFoil
      ? 'text-transparent bg-clip-text bg-gradient-to-r from-amber-400 via-pink-500 to-purple-500'
      : 'text-purple-400';
    emoji = esFoil ? '📦✨' : '📦';
    dropShadowColor = esFoil
      ? 'drop-shadow-[0_0_30px_rgba(245,158,11,0.8)]'
      : 'drop-shadow-[0_0_20px_rgba(168,85,247,0.6)]';
  }

  // Booster modal — special UI with two action buttons + particles
  if (esBooster) {
    return renderPortal(
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/85 backdrop-blur-md p-4 animate-in fade-in duration-300">
        <style
          dangerouslySetInnerHTML={{
            __html: `
              @keyframes adopcion-float {
                0% { transform: translateY(20px) translateX(0) rotate(0deg); opacity: 0; }
                12% { opacity: 0.9; }
                88% { opacity: 0.9; }
                100% { transform: translateY(-280px) translateX(var(--drift-x)) rotate(var(--rot-deg)); opacity: 0; }
              }
              .adopcion-particle { animation: adopcion-float var(--dur) var(--delay) infinite linear; }
              @keyframes pack-pulse {
                0%, 100% { transform: scale(1) rotate(-1deg); filter: drop-shadow(0 0 20px rgba(245,158,11,0.6)); }
                50% { transform: scale(1.07) rotate(1deg); filter: drop-shadow(0 0 40px rgba(245,158,11,1)); }
              }
              .foil-pack-anim { animation: pack-pulse 1.8s ease-in-out infinite; }
            `,
          }}
        />
        <div
          className={`relative bg-slate-900 border-2 rounded-3xl p-6 sm:p-10 max-w-md w-full text-center transform transition-all scale-100 animate-in zoom-in-95 overflow-hidden ${borderColorClass}`}
        >
          {/* Foil overlay shimmer */}
          {esFoil && (
            <div className="absolute inset-0 bg-gradient-to-br from-amber-900/15 via-transparent to-purple-900/15 pointer-events-none rounded-3xl" />
          )}

          {/* Floating particles */}
          <div className="absolute inset-0 pointer-events-none overflow-hidden rounded-3xl">
            {adopcionParticles.map((p) => (
              <div
                key={p.id}
                className="absolute bottom-0 adopcion-particle select-none text-center"
                style={{
                  left: `${p.left}%`,
                  fontSize: `${p.size}px`,
                  color: p.color,
                  '--delay': `${p.delay}s`,
                  '--dur': `${p.duration}s`,
                  '--drift-x': `${p.drift}px`,
                  '--rot-deg': `${p.rot}deg`,
                  opacity: 0,
                } as React.CSSProperties}
              >
                {p.content}
              </div>
            ))}
          </div>

          {/* Title */}
          <h2
            className={`text-3xl sm:text-4xl font-black italic mb-1 uppercase tracking-widest relative z-10 ${titleTextColor} ${esFoil ? 'animate-pulse' : ''}`}
          >
            {titulo}
          </h2>
          <p className="text-slate-400 text-xs mb-5 relative z-10">{mensajeAdopcion}</p>

          {/* Pack emoji */}
          <div
            className={`text-7xl sm:text-8xl mb-5 relative z-10 select-none ${esFoil ? 'foil-pack-anim' : 'animate-bounce'} ${dropShadowColor}`}
          >
            {emoji}
          </div>

          {/* Info box */}
          <div
            className={`rounded-2xl p-4 mb-6 border relative z-10 ${
              esFoil
                ? 'bg-amber-950/25 border-amber-500/30'
                : 'bg-purple-950/25 border-purple-500/30'
            }`}
          >
            <p
              className={`text-sm font-extrabold mb-1.5 uppercase tracking-wider ${esFoil ? 'text-amber-300' : 'text-purple-300'}`}
            >
              {esFoil ? '⚡ Sobre Brillante Premium' : '📦 Sobre sellado en inventario'}
            </p>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              {esFoil
                ? '¡Contiene cartas con garantía de calidad superior y posibles variantes brillantes! Ábrelo ahora o guárdalo para después.'
                : 'Tu sobre está seguro en el inventario. Ábrelo cuando quieras para revelar las 7 cartas escondidas.'}
            </p>
          </div>

          {/* Action buttons */}
          <div className="flex flex-col gap-3 relative z-10">
            <button
              onClick={onAbrirAhora}
              disabled={abrirAhoraLoading}
              className={`w-full px-8 py-4 text-white font-black rounded-xl uppercase tracking-widest text-sm transition-all active:scale-95 cursor-pointer disabled:opacity-60 disabled:cursor-not-allowed ${
                esFoil
                  ? 'bg-gradient-to-r from-amber-500 via-fuchsia-500 to-purple-600 hover:from-amber-400 hover:via-fuchsia-400 hover:to-purple-500 shadow-[0_5px_25px_rgba(245,158,11,0.45)]'
                  : 'bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 shadow-[0_5px_20px_rgba(168,85,247,0.4)]'
              }`}
            >
              {abrirAhoraLoading ? '⏳ Abriendo...' : '🎁 ¡Abrir Ahora!'}
            </button>

            <button
              onClick={onIrAlInventario}
              className="w-full px-8 py-3.5 bg-slate-800 hover:bg-slate-700 text-slate-200 font-black rounded-xl uppercase tracking-widest text-sm transition-all active:scale-95 border border-slate-700/60 cursor-pointer"
            >
              🎒 Ir al Inventario
            </button>

            {txHash && (
              <a
                href={`https://amoy.polygonscan.com/tx/${txHash}`}
                target="_blank"
                rel="noopener noreferrer"
                className="w-full px-6 py-2.5 bg-slate-800/80 hover:bg-slate-700 text-slate-400 hover:text-white font-bold rounded-xl text-xs transition-colors border border-slate-700/50 flex items-center justify-center gap-1.5"
              >
                🔗 Ver Transacción Web3
              </a>
            )}

            <button
              onClick={onSeguirComprando}
              className="text-slate-500 hover:text-slate-300 text-[11px] mt-1 underline underline-offset-4 cursor-pointer"
            >
              Seguir comprando
            </button>
          </div>
        </div>
      </div>,
    );
  }

  // Default modal (webito, tabla, FRJ)
  return renderPortal(
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 animate-in fade-in duration-300">
      <div
        className={`bg-slate-900 border-2 rounded-3xl p-6 sm:p-10 max-w-md w-full text-center transform transition-all scale-100 animate-in zoom-in-95 ${borderColorClass}`}
      >
        <h2 className={`text-4xl font-black italic mb-2 uppercase tracking-widest ${titleTextColor}`}>
          {titulo}
        </h2>
        <p className="text-slate-300 mb-6 font-medium">{mensajeAdopcion}</p>

        <div className={`text-8xl mb-8 animate-bounce ${dropShadowColor}`}>{emoji}</div>

        <div className="flex flex-col gap-4 justify-center">
          <button
            onClick={() => {
              if (esTabla) onIrATablas();
              else if (esFRJ) onSeguirComprando();
              else onIrAlCriadero();
            }}
            className={`w-full px-8 py-4 text-white font-black rounded-xl uppercase tracking-widest text-sm transition-all active:scale-95 ${btnBg}`}
          >
            {esTabla ? 'Ver mis Tablas' : esFRJ ? 'Volver a la Tienda' : btnText}
          </button>
          {txHash && (
            <a
              href={`https://amoy.polygonscan.com/tx/${txHash}`}
              target="_blank"
              rel="noopener noreferrer"
              className="w-full px-6 py-3 bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white font-bold rounded-xl text-sm transition-colors border border-slate-700"
            >
              Ver Transacción Web3
            </a>
          )}
          <button
            onClick={onSeguirComprando}
            className="text-slate-500 hover:text-slate-300 text-xs mt-2 underline underline-offset-4"
          >
            Seguir comprando
          </button>
        </div>
      </div>
    </div>,
  );
}
