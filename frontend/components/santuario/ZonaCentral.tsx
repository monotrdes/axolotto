"use client";
import React from 'react';
import { SpotSlot } from '@/types/santuario';
import NidoScene from './NidoScene';

interface PlacedDeco {
  item_id: number;
  emoji: string;
  name: string;
  subcategory: string;
  rarity?: string;
}

interface ZonaCentralProps {
  // NidoScene props (forwarded)
  spots: SpotSlot[];
  axolotitos: any[];
  clima: any;
  caveLevel: number;
  viewMode: 'libre' | 'gestion';
  hasTable: boolean;
  tableSeats: number;
  onSelectSpot: (slot: SpotSlot) => void;
  onSelectAxo: (axo: any) => void;
  onToggleViewMode: () => void;
  onOpenHosting?: () => void;
  selectedAxoId: number | null;
  particulas: { id: number; incId: number; tipo: string; x: number; y: number; cLeft?: number; cBottom?: number }[];
  vipTier?: string | null;
  // Decoration mode
  decoMode?: boolean;
  onToggleDecoMode?: () => void;
  placedDecos?: Record<string, PlacedDeco>;
}

const ADORNO_SLOTS = [
  { key: 'ADORNOS_FIJOS-1', position: 'left-2 top-1/3' },
  { key: 'ADORNOS_FIJOS-2', position: 'left-2 bottom-1/4' },
  { key: 'ADORNOS_FIJOS-3', position: 'right-2 top-1/3' },
  { key: 'ADORNOS_FIJOS-4', position: 'right-2 bottom-1/4' },
] as const;

export default function ZonaCentral({
  spots, axolotitos, clima, caveLevel, viewMode, hasTable, tableSeats,
  onSelectSpot, onSelectAxo, onToggleViewMode, onOpenHosting, selectedAxoId, particulas, vipTier,
  decoMode = false, onToggleDecoMode,
  placedDecos = {},
}: ZonaCentralProps) {
  return (
    <div className="relative w-full h-full">
      {/* Scene fills the full container */}
      <div className="absolute inset-0">
        <NidoScene
          spots={spots}
          axolotitos={axolotitos}
          clima={clima}
          caveLevel={caveLevel}
          viewMode={viewMode}
          hasTable={hasTable}
          tableSeats={tableSeats}
          onSelectSpot={onSelectSpot}
          onSelectAxo={onSelectAxo}
          onToggleViewMode={onToggleViewMode}
          onOpenHosting={onOpenHosting}
          selectedAxoId={selectedAxoId}
          particulas={particulas}
          vipTier={vipTier}
          className="h-full rounded-none border-0"
        />
      </div>

      {/* Decoration slot indicators — visible only in decoMode */}
      {decoMode && ADORNO_SLOTS.map(({ key, position }) => {
        const deco = placedDecos[key];
        return (
          <div
            key={key}
            className={`absolute ${position} z-[80] cursor-pointer`}
          >
            {deco ? (
              <div className="flex items-center gap-0.5 bg-black/70 backdrop-blur-sm border border-teal-400/40 rounded-full px-1.5 py-0.5 shadow-[0_0_8px_rgba(45,212,191,0.3)]">
                <span className="text-[10px]">{deco.emoji}</span>
                <span className="text-[7px] font-black text-white/80 leading-none">{deco.name}</span>
              </div>
            ) : (
              <div className="flex items-center justify-center w-8 h-8 rounded-full bg-black/50 border-2 border-dashed border-teal-400/40 backdrop-blur-sm shadow-[0_0_8px_rgba(45,212,191,0.2)] animate-pulse">
                <span className="text-sm opacity-60">🏺</span>
              </div>
            )}
          </div>
        );
      })}

      {/* Decoration mode toggle button — bottom-right above census chip */}
      {onToggleDecoMode && (
        <button
          onClick={onToggleDecoMode}
          className={`absolute bottom-14 right-2 z-[85] flex items-center gap-1.5 px-3 py-1.5 rounded-full text-[9px] font-black uppercase tracking-wide transition-all backdrop-blur-sm border ${
            decoMode
              ? 'bg-teal-900/80 border-teal-500/50 text-teal-300 shadow-[0_0_12px_rgba(45,212,191,0.35)]'
              : 'bg-black/60 border-white/10 text-slate-400 hover:text-teal-300 hover:border-teal-500/30'
          }`}
        >
          <span className="text-[11px]">{decoMode ? '✕' : '🎨'}</span>
          <span>{decoMode ? 'Cerrar' : 'Adornos'}</span>
        </button>
      )}

      {/* Compact friends pill — bottom-left, above where staking chip floats */}
      <div className="absolute bottom-14 left-2 z-[75] flex items-center gap-1.5 px-2.5 py-1.5 rounded-full bg-black/50 backdrop-blur-sm border border-white/8">
        <span className="text-[10px]">👥</span>
        <span className="text-[9px] font-black text-slate-400">0 amigos</span>
      </div>
    </div>
  );
}
