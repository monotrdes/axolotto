"use client";
import React from 'react';
import BottomSheet from '@/components/ui/BottomSheet';

interface ItemListProps {
  sealedSobrecitos: any[];
  sobrecitosSheetOpen: boolean;
  setSobrecitosSheetOpen: (open: boolean) => void;
  onStartUnboxing: (booster: any) => void;
  onOpenSellModal: (item: any, name?: string) => void;
  getBoosterStyles: (name: string) => {
    gradient: string;
    borderColor: string;
    glowColor: string;
    cardBackSymbol: string;
    titleText: string;
  };
}

export default function ItemList({
  sealedSobrecitos, sobrecitosSheetOpen, setSobrecitosSheetOpen,
  onStartUnboxing, onOpenSellModal, getBoosterStyles,
}: ItemListProps) {
  if (sealedSobrecitos.length === 0) return null;

  return (
    <>
      {/* SOBRES SELLADOS (BOOSTERS) BANNER */}
      <div className="mb-6 p-5 rounded-2xl bg-gradient-to-r from-pink-500/20 via-purple-500/10 to-indigo-500/20 border border-pink-500/30 flex flex-col sm:flex-row items-center justify-between gap-4 shadow-[0_0_20px_rgba(244,63,94,0.15)] animate-in fade-in duration-300">
        <div className="flex items-center gap-3">
          <span className="text-3xl animate-bounce">📦</span>
          <div className="text-left">
            <h4 className="text-white font-black text-sm uppercase tracking-wider">¡Tienes sobres listos para abrir!</h4>
            <p className="text-slate-400 text-xs mt-0.5">
              Dispones de {sealedSobrecitos.reduce((acc: number, curr: any) => acc + curr.quantity, 0)} sobre(s) esperándote en tu mochila.
            </p>
          </div>
        </div>
        <button
          onClick={() => setSobrecitosSheetOpen(true)}
          className="w-full sm:w-auto px-6 py-2.5 bg-gradient-to-r from-[#E4007C] to-purple-600 hover:from-[#FF1493] hover:to-purple-500 text-white font-black rounded-xl uppercase tracking-widest text-xs transition-all shadow-lg active:scale-95 cursor-pointer whitespace-nowrap"
        >
          Abrir Sobres ⚡
        </button>
      </div>

      {/* BOTTOM SHEET FOR SEALED BOOSTERS */}
      <BottomSheet
        open={sobrecitosSheetOpen}
        onClose={() => setSobrecitosSheetOpen(false)}
        title="📦 Sobres Sellados"
      >
        <div className="p-5 flex flex-col gap-4">
          <p className="text-slate-400 text-xs">Elige qué sobre deseas abrir. Al abrirlo, se añadirán 7 nuevas cartas a tu colección.</p>

          <div className="flex flex-col gap-3 max-h-[50dvh] overflow-y-auto pr-1">
            {sealedSobrecitos.map((booster: any) => {
              const themeStyles = getBoosterStyles(booster.name);
              return (
                <div
                  key={booster.inventory_id}
                  className="flex items-center justify-between bg-white/[0.03] border border-white/5 hover:border-pink-500/30 rounded-2xl p-4 transition-all hover:bg-white/[0.05]"
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-12 h-16 rounded-lg bg-gradient-to-br ${themeStyles.gradient} border ${themeStyles.borderColor} flex items-center justify-center text-2xl shadow-md`}>
                      {themeStyles.cardBackSymbol}
                    </div>
                    <div>
                      <h4 className="text-white font-black text-xs uppercase tracking-wide">{booster.name}</h4>
                      <p className="text-[10px] text-slate-500 mt-0.5">Posees: <span className="text-white font-black">x{booster.quantity}</span></p>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => onStartUnboxing(booster)}
                      className="px-4 py-2 bg-gradient-to-r from-[#E4007C] to-purple-600 hover:from-[#FF1493] hover:to-purple-500 text-white text-[10px] font-black uppercase tracking-wider rounded-xl transition-all active:scale-95 cursor-pointer"
                    >
                      Abrir ahora ⚡
                    </button>
                    <button
                      onClick={() => onOpenSellModal(booster)}
                      className="px-3 py-2 border border-emerald-500/30 bg-emerald-950/20 text-emerald-300 hover:bg-emerald-950/40 text-[10px] font-black uppercase tracking-wider rounded-xl transition-all active:scale-95 cursor-pointer"
                    >
                      Vender
                    </button>
                  </div>
                </div>
              );
            })}
            {sealedSobrecitos.length === 0 && (
              <div className="text-center py-6 text-slate-500 text-xs italic">
                No te quedan sobres por abrir. ¡Compra más en la tienda!
              </div>
            )}
          </div>
        </div>
      </BottomSheet>
    </>
  );
}
