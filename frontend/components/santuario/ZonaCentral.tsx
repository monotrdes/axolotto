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
  // Decoration slots
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
  placedDecos = {},
}: ZonaCentralProps) {
  return (
    <div className="flex flex-col flex-1 min-h-0">
      {/* Header strip */}
      <div
        className="w-full px-2 py-0.5 mb-1.5 text-center"
        style={{ border: '1px solid rgba(45,212,191,0.35)', borderRadius: '4px' }}
      >
        <span className="text-[8px] font-black uppercase tracking-widest text-teal-400/70">
          Zona Central (El Diorama del Cenote)
        </span>
      </div>

      {/* Scene + adorno overlays */}
      <div className="relative flex-1 min-h-0">
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
          className="h-full"
        />

        {/* Decoration slot indicators */}
        {ADORNO_SLOTS.map(({ key, position }) => {
          const deco = placedDecos[key];
          return (
            <div
              key={key}
              className={`absolute ${position} z-[80] pointer-events-none`}
            >
              {deco ? (
                <div className="flex items-center gap-0.5 bg-black/70 backdrop-blur-sm border border-white/15 rounded-full px-1.5 py-0.5">
                  <span className="text-[10px]">{deco.emoji}</span>
                  <span className="text-[7px] font-black text-white/80 leading-none">{deco.name}</span>
                </div>
              ) : (
                <div className="flex items-center justify-center w-6 h-6 rounded-full bg-black/40 border border-white/10">
                  <span className="text-[10px] opacity-30 animate-pulse">🏺</span>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
