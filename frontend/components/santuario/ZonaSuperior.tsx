"use client";
import React from 'react';
import { obtenerEstiloHuevo } from '@/utils/santuario';

interface ZonaSuperiorProps {
  incubaciones: any[];
  maxSlots?: number;
  onSelectSlot: (incubacion: any | null) => void;
}

function NidoSlot({
  inc,
  slotIndex,
  locked,
  onSelectSlot,
}: {
  inc: any | null;
  slotIndex: number;
  locked?: boolean;
  onSelectSlot: (inc: any | null) => void;
}) {
  // ── DERIVE STATE ──
  const isEmpty = !inc;
  const isTutorial = inc ? (inc.tutorial_phase ?? 0) > 0 : false;
  const isReady = inc
    ? isTutorial
      ? inc.horasRestantes === 0
      : !!inc.imprinting_complete
    : false;

  // ── BORDER COLOR ──
  let archBorder = 'rgba(80,50,20,0.25)';
  let archGlow = '';
  if (!isEmpty) {
    if (isReady) {
      archBorder = 'rgba(228,0,124,0.5)';
      archGlow = '0 0 14px rgba(228,0,124,0.35)';
    } else if (inc.imprinting_padrino_id !== null) {
      archBorder = 'rgba(167,139,250,0.5)';
      archGlow = '0 0 10px rgba(167,139,250,0.25)';
    } else {
      archBorder = 'rgba(251,146,60,0.3)';
    }
  }

  // ── STATUS BADGE (top-right inside slot) ──
  const renderBadge = () => {
    if (!inc) return null;
    if (isReady) {
      return (
        <div className="absolute top-0.5 right-0.5 text-[6px] font-black text-[#E4007C] animate-pulse leading-none">
          ¡Listo!
        </div>
      );
    }
    if (isTutorial) {
      return (
        <div className="absolute top-0.5 right-0.5 text-[6px] font-black text-white/60 leading-none">
          {inc.horasRestantes}h
        </div>
      );
    }
    const played = inc.imprinting_games_played ?? 0;
    const required = inc.required_games ??
      (inc.rarity === 'common' ? 3 : inc.rarity === 'rare' ? 5 : 7);
    return (
      <div className="absolute top-0.5 right-0.5 text-[6px] font-black text-white/55 bg-black/40 px-0.5 rounded leading-none">
        {played}/{required}
      </div>
    );
  };

  // ── INNER CONTENT ──
  const renderInner = () => {
    if (locked) {
      return (
        <div className="w-full h-full flex items-center justify-center opacity-15">
          <span className="text-sm leading-none">🔒</span>
        </div>
      );
    }
    if (isEmpty) {
      return (
        <div className="w-full h-full flex items-center justify-center opacity-30 animate-pulse">
          <span className="text-sm leading-none">🪺</span>
        </div>
      );
    }
    const estilos = obtenerEstiloHuevo(inc.name);
    return (
      <>
        {/* Slot number badge */}
        <div className="absolute top-0.5 left-0.5 text-[6px] font-black text-white/40 leading-none z-10">
          {slotIndex + 1}
        </div>
        <span
          className="text-lg leading-none select-none z-10 transition-transform duration-150"
          style={{ filter: `drop-shadow(0 0 5px ${estilos.aura})` }}
        >
          {isReady ? '🐣' : '🥚'}
        </span>
        {renderBadge()}
      </>
    );
  };

  return (
    <button
      onClick={() => onSelectSlot(inc ?? null)}
      disabled={locked}
      className="relative aspect-square w-full overflow-hidden group focus:outline-none transition-all duration-200 disabled:cursor-not-allowed"
      style={{
        borderRadius: '50% 50% 8px 8px / 60% 60% 8px 8px',
        background: 'linear-gradient(180deg, #1E1008 0%, #0A0501 100%)',
        border: `1.5px solid ${archBorder}`,
        boxShadow: `inset 0 5px 16px rgba(0,0,0,0.85)${archGlow ? `, ${archGlow}` : ''}`,
      }}
      aria-label={inc ? `Nido: ${inc.name}` : locked ? 'Nido bloqueado' : `Nido vacío ${slotIndex + 1}`}
    >
      {/* Slot number badge for empty/non-egg slots */}
      {!locked && isEmpty && (
        <div className="absolute top-0.5 left-0.5 text-[6px] font-black text-white/20 leading-none z-10">
          {slotIndex + 1}
        </div>
      )}
      <div className="w-full h-full flex items-center justify-center relative">
        {renderInner()}
      </div>
    </button>
  );
}

export default function ZonaSuperior({
  incubaciones,
  maxSlots = 7,
  onSelectSlot,
}: ZonaSuperiorProps) {
  // Build 8-cell array (4+4 grid, last slot is locked placeholder when maxSlots=7)
  const cells = Array.from({ length: 8 }, (_, i) => ({
    index: i,
    inc: incubaciones[i] ?? null,
    locked: i >= maxSlots,
  }));

  return (
    <div className="w-full">
      {/* Header strip */}
      <div
        className="w-full px-2 py-0.5 mb-1.5 text-center"
        style={{ border: '1px solid rgba(251,191,36,0.35)', borderRadius: '4px' }}
      >
        <span className="text-[8px] font-black uppercase tracking-widest text-amber-400/70">
          Zona Superior (Crianza y Estados)
        </span>
      </div>

      {/* 4+4 grid */}
      <div className="grid grid-cols-4 gap-1.5">
        {cells.map(({ index, inc, locked }) => (
          <NidoSlot
            key={index}
            inc={inc}
            slotIndex={index}
            locked={locked}
            onSelectSlot={onSelectSlot}
          />
        ))}
      </div>
    </div>
  );
}
