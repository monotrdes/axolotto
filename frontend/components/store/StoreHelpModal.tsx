"use client";
import React from 'react';
import { createPortal } from 'react-dom';
import { X } from 'lucide-react';

interface StoreHelpModalProps {
  open: boolean;
  onClose: () => void;
}

export default function StoreHelpModal({ open, onClose }: StoreHelpModalProps) {
  if (!open) return null;
  if (typeof window === 'undefined') return null;

  return createPortal(
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/85 backdrop-blur-md p-4 animate-in fade-in duration-200">
      <div className="bg-slate-950 border-2 border-yellow-500/30 rounded-[2.5rem] p-6 max-w-md w-full relative max-h-[85vh] overflow-y-auto">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-white p-2 rounded-full hover:bg-slate-800 cursor-pointer"
        >
          <X size={20} />
        </button>
        <div className="text-center mb-6">
          <span className="text-4xl">🦎</span>
          <h3 className="text-2xl font-black text-yellow-400 mt-2 uppercase tracking-tight">
            Guía de El Tianguis
          </h3>
        </div>
        <div className="space-y-4 text-xs text-slate-350 leading-relaxed">
          <div>
            <h4 className="font-extrabold text-sm text-white mb-1 uppercase tracking-wider flex items-center gap-1">
              <span>💎</span> Axofichas (AXF)
            </h4>
            <p>
              Moneda premium obtenida mediante compras o recompensas especiales. Úsala para adoptar Webitos y comprar boosters
              temáticos.
            </p>
          </div>
          <div>
            <h4 className="font-extrabold text-sm text-amber-500 mb-1 uppercase tracking-wider flex items-center gap-1">
              <span>🪙</span> Frijolitos (FRJ)
            </h4>
            <p>
              Moneda del juego que generas con tus tablas. Úsala en El Trueque (Mercado P2P) y para jugar en las cápsulas sorpresa o
              comprar boosters.
            </p>
          </div>
          <div>
            <h4 className="font-extrabold text-sm text-purple-400 mb-1 uppercase tracking-wider flex items-center gap-1">
              <span>📦</span> Los Sobres
            </h4>
            <p>
              Contienen 7 cartas de Lotería Mexicana. Elige entre packs temáticos (Fiesta, Nido, Cosmos) o el pack Mezclado (más
              económico).
            </p>
          </div>
          <div>
            <h4 className="font-extrabold text-sm text-pink-400 mb-1 uppercase tracking-wider flex items-center gap-1">
              <span>🥚</span> Los Webitos
            </h4>
            <p>
              Adopta un huevo para que nazca un Axolotito con rareza y estadísticas únicas, listo para competir en las salas de
              juego.
            </p>
          </div>
          <div>
            <h4 className="font-extrabold text-sm text-cyan-400 mb-1 uppercase tracking-wider flex items-center gap-1">
              <span>🎰</span> La Suertuda (Gashapon)
            </h4>
            <p>
              Prueba tu suerte rodando la máquina para conseguir accesorios estéticos que puedes equipar a tus Axolotitos.
            </p>
          </div>
        </div>
      </div>
    </div>,
    document.body,
  );
}
