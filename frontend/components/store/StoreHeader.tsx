"use client";
import React from 'react';
import { ChevronLeft } from 'lucide-react';
import type { StoreTab } from '@/types/store';

interface StoreHeaderProps {
  storeTab: StoreTab;
  onBack: () => void;
  onHelp: () => void;
}

export default function StoreHeader({ storeTab, onBack, onHelp }: StoreHeaderProps) {
  return (
    <div className="flex items-center justify-between mb-8 sm:mb-12">
      <button
        onClick={onBack}
        className="w-10 h-10 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-slate-700 flex items-center justify-center text-slate-350 hover:text-white active:scale-95 transition-all cursor-pointer shadow-md"
        title="Atrás"
      >
        <ChevronLeft size={20} />
      </button>

      <div className="text-center flex-1">
        {storeTab === 'official' ? (
          <>
            <h2 className="text-2xl sm:text-4xl font-extrabold italic text-yellow-400 tracking-tighter uppercase drop-shadow-[0_0_12px_rgba(234,179,8,0.5)]">
              EL TIANGUIS
            </h2>
            <p className="text-[9px] sm:text-[10px] text-slate-400 tracking-widest mt-0.5 uppercase font-black">
              Tienda Axolot.to
            </p>
          </>
        ) : storeTab === 'market' ? (
          <>
            <h2 className="text-2xl sm:text-4xl font-extrabold italic text-teal-400 tracking-tighter uppercase drop-shadow-[0_0_12px_rgba(45,212,191,0.5)]">
              EL TRUEQUE
            </h2>
            <p className="text-[9px] sm:text-[10px] text-slate-400 tracking-widest mt-0.5 uppercase font-black">
              Mercado entre Marchantes
            </p>
          </>
        ) : storeTab === 'reciclon' ? (
          <>
            <h2 className="text-2xl sm:text-4xl font-extrabold italic text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-teal-400 tracking-tighter uppercase drop-shadow-[0_0_12px_rgba(45,212,191,0.4)]">
              EL RECICLÓN
            </h2>
            <p className="text-[9px] sm:text-[10px] text-slate-400 tracking-widest mt-0.5 uppercase font-black">
              Recicla y Obten Cartas
            </p>
          </>
        ) : (
          <>
            <h2 className="text-2xl sm:text-4xl font-extrabold italic text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400 tracking-tighter uppercase drop-shadow-[0_0_12px_rgba(168,85,247,0.4)]">
              EL CENOTE
            </h2>
            <p className="text-[9px] sm:text-[10px] text-slate-400 tracking-widest mt-0.5 uppercase font-black">
              Fusión y Forja
            </p>
          </>
        )}
      </div>

      <button
        onClick={onHelp}
        className="w-10 h-10 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-slate-700 flex items-center justify-center text-slate-350 hover:text-white active:scale-95 transition-all cursor-pointer shadow-md"
        title="Ayuda"
      >
        <span className="font-extrabold text-lg leading-none">?</span>
      </button>
    </div>
  );
}
