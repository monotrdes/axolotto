"use client";
import React from "react";
import type { DecorationItem } from "../zones/NidoZone";

interface CuevaDecorPanelProps {
  isOpen: boolean;
  onClose: () => void;
  caveIndex: number;
  axolotitoName: string;
  placedDecorations: DecorationItem[];
  availableDecorations: DecorationItem[];
  onSave: (caveIndex: number, decorations: DecorationItem[]) => void;
}

const CuevaDecorPanel: React.FC<CuevaDecorPanelProps> = ({
  isOpen,
  onClose,
  caveIndex,
  axolotitoName,
  placedDecorations,
  availableDecorations,
  onSave,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/60 backdrop-blur-sm">
      <div className="bg-[#12122A] border border-white/10 rounded-t-2xl w-full max-w-md max-h-[70vh] overflow-y-auto p-5 animate-slide-up">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-white font-bold text-lg">
            Decorar Cueva {axolotitoName ? `— ${axolotitoName}` : ""}
          </h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white text-xl leading-none"
          >
            ✕
          </button>
        </div>

        {/* Phase 2: drag-and-drop decoration grid */}
        <p className="text-gray-500 text-sm mb-4">
          Decoraciones disponibles. Fase 2 — grid interactivo próximamente.
        </p>

        <div className="grid grid-cols-4 gap-2 mb-4">
          {availableDecorations.map((d) => (
            <button
              key={d.id}
              className="aspect-square bg-[#1C1C35] border border-white/5 rounded-xl flex flex-col items-center justify-center p-1 hover:bg-[#2A2A4A] hover:border-white/10 transition-all"
              title={d.label}
            >
              <span className="text-2xl">{d.emoji}</span>
              <span className="text-[10px] text-gray-500 truncate w-full text-center">
                {d.label}
              </span>
            </button>
          ))}
        </div>

        <div className="flex gap-2">
          <button
            onClick={() => onSave(caveIndex, placedDecorations)}
            className="flex-1 py-2 rounded-xl bg-[#E4007C] text-white font-bold text-sm hover:bg-[#ff1a8c] transition-all"
          >
            Guardar
          </button>
          <button
            onClick={onClose}
            className="flex-1 py-2 rounded-xl bg-[#1C1C35] text-gray-400 text-sm hover:text-white transition-all"
          >
            Cancelar
          </button>
        </div>
      </div>
    </div>
  );
};

export { CuevaDecorPanel };
export default CuevaDecorPanel;
