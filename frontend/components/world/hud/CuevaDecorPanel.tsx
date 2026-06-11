"use client";
import React, { useState } from "react";
import type { DecorationItem } from "../zones/NidoZone";

/** Máximo de decoraciones por cueva (espejo de DECOR_OFFSETS en SantuarioScene). */
const MAX_DECOR = 6;

interface CuevaDecorPanelProps {
  isOpen: boolean;
  onClose: () => void;
  caveIndex: number;
  axolotitoName: string;
  placedDecorations: DecorationItem[];
  availableDecorations: DecorationItem[];
  onSave: (caveIndex: number, decorations: DecorationItem[]) => void;
}

/** Montaje condicional: cada apertura remonta el panel con lo ya colocado. */
const CuevaDecorPanel: React.FC<CuevaDecorPanelProps> = (props) => {
  if (!props.isOpen) return null;
  return <CuevaDecorPanelInner key={props.caveIndex} {...props} />;
};

const CuevaDecorPanelInner: React.FC<CuevaDecorPanelProps> = ({
  onClose,
  caveIndex,
  axolotitoName,
  placedDecorations,
  availableDecorations,
  onSave,
}) => {
  const [selection, setSelection] = useState<DecorationItem[]>(placedDecorations);

  const toggle = (d: DecorationItem) => {
    setSelection((prev) => {
      if (prev.some((p) => p.id === d.id)) return prev.filter((p) => p.id !== d.id);
      if (prev.length >= MAX_DECOR) return prev;
      return [...prev, d];
    });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/60 backdrop-blur-sm">
      <div className="bg-[#12122A] border border-white/10 rounded-t-2xl w-full max-w-md max-h-[70vh] overflow-y-auto p-5 animate-slide-up">
        <div className="flex items-center justify-between mb-1">
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

        <p className="text-gray-500 text-sm mb-4">
          Toca para colocar o quitar ({selection.length}/{MAX_DECOR}). Se verán
          alrededor del nido.
        </p>

        <div className="grid grid-cols-4 gap-2 mb-4">
          {availableDecorations.map((d) => {
            const placed = selection.some((p) => p.id === d.id);
            return (
              <button
                key={d.id}
                onClick={() => toggle(d)}
                className={`relative aspect-square rounded-xl flex flex-col items-center justify-center p-1 transition-all border ${
                  placed
                    ? "bg-[#E4007C]/20 border-[#E4007C]/60"
                    : "bg-[#1C1C35] border-white/5 hover:bg-[#2A2A4A] hover:border-white/10"
                }`}
                title={d.label}
              >
                {placed && (
                  <span className="absolute top-1 right-1 text-[10px] text-[#FF8DA1]">
                    ✓
                  </span>
                )}
                <span className="text-2xl">{d.emoji}</span>
                <span className="text-[10px] text-gray-500 truncate w-full text-center">
                  {d.label}
                </span>
              </button>
            );
          })}
        </div>

        <div className="flex gap-2">
          <button
            onClick={() => onSave(caveIndex, selection)}
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
