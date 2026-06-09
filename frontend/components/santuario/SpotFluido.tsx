"use client";
import React from 'react';
import { SpotSlot } from '@/types/santuario';
import { obtenerEstiloHuevo, obtenerFaseHuevo } from '@/utils/santuario';
import { API_BASE } from '@/lib/api';

const API = `${API_BASE}`;

interface SpotFluidoProps {
  slot: SpotSlot;
  index: number;
  totalSpots: number;
  isManagementMode: boolean;
  onOpen: () => void;
  isPadrino?: boolean;
}

export default function SpotFluido({ slot, index, totalSpots, isManagementMode, onOpen, isPadrino }: SpotFluidoProps) {
  const W = 70, H = 84;

  // Position spots in a row along the life zone
  const spacing = 90 / (totalSpots + 1);
  const left = `${spacing * (index + 1) - 4}%`;
  const bottom = isManagementMode ? '18%' : '22%';

  // ── GLOW STATE ──
  let glowColor = 'transparent';
  let archBorder = 'rgba(80,50,20,0.25)';
  let archGlow = '';
  let modeLabel = '';

  if (slot.type === 'egg') {
    const isTutorial = (slot.data.tutorial_phase ?? 0) > 0;
    const isReady = isTutorial ? slot.data.horasRestantes === 0 : !!slot.data.imprinting_complete;
    const hasPadrino = slot.data.imprinting_padrino_id !== null;
    if (isReady) {
      glowColor = 'rgba(228,0,124,0.65)';
      archBorder = 'rgba(228,0,124,0.5)';
      archGlow = '0 0 18px rgba(228,0,124,0.4)';
      modeLabel = '🐣';
    } else if (hasPadrino) {
      glowColor = 'rgba(167,139,250,0.45)';
      archBorder = 'rgba(167,139,250,0.5)';
      archGlow = '0 0 14px rgba(167,139,250,0.3)';
      modeLabel = '🧬';
    } else {
      glowColor = 'rgba(251,146,60,0.3)';
      archBorder = 'rgba(251,146,60,0.3)';
      modeLabel = '🔥';
    }
  } else if (slot.type === 'axo' || slot.type === 'bed') {
    if (isPadrino) {
      glowColor = 'rgba(167,139,250,0.5)';
      archBorder = 'rgba(167,139,250,0.6)';
      archGlow = '0 0 16px rgba(167,139,250,0.4)';
      modeLabel = slot.type === 'axo' ? '🐾 Padrino' : '🛏️ Padrino';
    } else {
      glowColor = 'rgba(45,212,191,0.35)';
      archBorder = 'rgba(45,212,191,0.3)';
      archGlow = '0 0 12px rgba(45,212,191,0.25)';
      modeLabel = slot.type === 'axo' ? '🦎' : '🛏️';
    }
  }

  // ── INNER RENDER ──
  const renderInner = () => {
    if (slot.type === 'empty') {
      return (
        <div className="w-full h-full flex flex-col items-center justify-center opacity-20 group-hover:opacity-40 transition-opacity">
          <span className="text-base leading-none">🪺</span>
        </div>
      );
    }

    if (slot.type === 'bed') {
      const axo = slot.data;
      return (
        <button
          onClick={(e) => { e.stopPropagation(); onOpen(); }}
          className="relative w-full h-full flex flex-col items-center justify-center focus:outline-none cursor-pointer"
          aria-label={`Cama de ${axo.name}`}
        >
          <span className="text-xl leading-none select-none z-10 transition-transform duration-150">🛏️</span>
          <span className="text-[6px] font-black text-white/50 mt-1 truncate max-w-full px-1 z-10 animate-pulse">
            {axo.name.length > 8 ? axo.name.slice(0, 7) + '…' : axo.name}
          </span>
        </button>
      );
    }

    if (slot.type === 'axo') {
      const axo = slot.data;
      return (
        <div className="relative w-full h-full flex flex-col items-center justify-center">
          <img
            src={`${API}/metadata/axolotito/${axo.blockchain_token_id}.svg`}
            alt={axo.name}
            className="w-10 h-10 object-contain drop-shadow-[0_0_6px_rgba(45,212,191,0.5)]"
            draggable={false}
          />
          {axo.status === 'sleeping' && (
            <span className="absolute -top-1 right-1 text-[8px]">💤</span>
          )}
          <span className="text-[6px] font-black text-white/50 mt-0.5 truncate max-w-full px-1">
            {axo.name.length > 8 ? axo.name.slice(0, 7) + '…' : axo.name}
          </span>
        </div>
      );
    }

    // egg
    const inc = slot.data;
    const estilos = obtenerEstiloHuevo(inc.name);
    const faseInfo = obtenerFaseHuevo(inc);
    const isTutorial = (inc.tutorial_phase ?? 0) > 0;
    const isReady = isTutorial ? inc.horasRestantes === 0 : !!inc.imprinting_complete;

    return (
      <button
        onClick={(e) => { e.stopPropagation(); onOpen(); }}
        className="relative w-full h-full flex flex-col items-center justify-center focus:outline-none cursor-pointer"
        aria-label={`Webito ${inc.name}`}
      >
        <span
          className={`text-xl leading-none select-none z-10 transition-transform duration-150 ${faseInfo.clase}`}
          style={{
            '--egg-shadow': estilos.shadow,
            filter: `drop-shadow(0 0 6px ${estilos.aura})`,
          } as React.CSSProperties}
        >
          {isReady ? '🐣' : '🥚'}
        </span>
        {!isReady && isTutorial && (
          <div className="absolute top-0.5 right-0.5 text-[7px] text-white/55 font-black">
            {inc.horasRestantes}h
          </div>
        )}
        {!isReady && !isTutorial && inc.imprinting_games_played !== undefined && (
          <div className="absolute top-0.5 right-0.5 text-[7px] text-white/55 font-black bg-black/40 px-0.5 rounded">
            {inc.imprinting_games_played}/{inc.required_games || (inc.rarity === "common" ? 3 : inc.rarity === "rare" ? 5 : 7)}
          </div>
        )}
      </button>
    );
  };

  // Badge above
  const isTutorialEgg = slot.type === 'egg' && (slot.data.tutorial_phase ?? 0) > 0;
  const isEggReady = slot.type === 'egg' && (isTutorialEgg ? slot.data.horasRestantes === 0 : !!slot.data.imprinting_complete);

  let badge = null;
  if (isEggReady) {
    badge = (
      <div
        className="absolute -top-3 left-1/2 -translate-x-1/2 bg-[#E4007C] text-[5px] font-black text-white px-2 py-0.5 rounded-full animate-pulse whitespace-nowrap"
        style={{ zIndex: 2, pointerEvents: 'none' }}
      >
        ¡Listo!
      </div>
    );
  } else if (isPadrino) {
    badge = (
      <div
        className="absolute -top-3 left-1/2 -translate-x-1/2 bg-purple-600 text-[5px] font-black text-white px-1.5 py-0.5 rounded-full whitespace-nowrap shadow-sm border border-purple-400/30 animate-pulse"
        style={{ zIndex: 2, pointerEvents: 'none' }}
      >
        🐾 Padrino
      </div>
    );
  } else if (slot.type === 'egg' && slot.data.imprinting_padrino_id !== null) {
    badge = (
      <div
        className="absolute -top-3 left-1/2 -translate-x-1/2 bg-indigo-600 text-[5px] font-black text-white px-1.5 py-0.5 rounded-full whitespace-nowrap shadow-sm border border-indigo-400/30"
        style={{ zIndex: 2, pointerEvents: 'none' }}
      >
        🧬 Imprint
      </div>
    );
  }

  return (
    <div
      role="button"
      tabIndex={0}
      onClick={onOpen}
      onKeyDown={(e) => e.key === 'Enter' && onOpen()}
      className="absolute cursor-pointer group select-none transition-all duration-500"
      style={{
        left, bottom,
        width: `${W}px`,
        height: `${H}px`,
        transformOrigin: 'bottom center',
        zIndex: slot.type === 'empty' ? 35 : 40,
      }}
      aria-label={slot.type === 'egg' ? `Incubando: ${slot.data.name}` : slot.type === 'axo' ? `Descansando: ${slot.data.name}` : slot.type === 'bed' ? `Cama de: ${slot.data.name}` : 'Spot vacío'}
    >
      {badge}

      {/* Ambient glow halo */}
      <div
        className="absolute inset-0 pointer-events-none transition-all duration-700"
        style={{
          borderRadius: '50% 50% 8px 8px / 70% 70% 8px 8px',
          background: `radial-gradient(ellipse at 50% 40%, ${glowColor}, transparent 65%)`,
          transform: 'scale(1.5)',
          zIndex: -1,
        }}
      />

      {/* Cave arch */}
      <div
        className="absolute inset-0 overflow-hidden group-hover:brightness-110 transition-all duration-200"
        style={{
          borderRadius: '50% 50% 8px 8px / 68% 68% 8px 8px',
          background: 'linear-gradient(180deg, #1E1008 0%, #0A0501 100%)',
          border: `1.5px solid ${archBorder}`,
          boxShadow: `inset 0 6px 20px rgba(0,0,0,0.85)${archGlow ? `, ${archGlow}` : ''}`,
        }}
      >
        {renderInner()}
      </div>

      {/* Rock ledge below arch */}
      <div
        className="absolute pointer-events-none"
        style={{
          bottom: '-9px', left: '-10px', right: '-10px', height: '18px',
          background: 'linear-gradient(180deg, #2D1A08 0%, #1A0D04 100%)',
          borderRadius: '0 0 6px 6px',
          zIndex: -1,
        }}
      />

      {/* Spot number badge */}
      <div
        className="absolute -bottom-5 left-1/2 -translate-x-1/2 text-[6px] font-black text-slate-600 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap"
        style={{ zIndex: 2 }}
      >
        {modeLabel || `Spot ${index + 1}`}
      </div>
    </div>
  );
}
