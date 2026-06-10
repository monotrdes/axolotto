'use client';

import { useEffect, useState } from 'react';
import { usePWAInstall } from '@/hooks/usePWAInstall';
import { X, Download, Share, PlusSquare } from 'lucide-react';

export default function PwaInstallBanner() {
  const {
    isInstallable,
    isStandalone,
    isIOS,
    showInstallPrompt,
    installApp,
    dismissPrompt,
  } = usePWAInstall();

  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted || !showInstallPrompt || isStandalone) return null;

  return (
    <div className="fixed bottom-20 left-1/2 -translate-x-1/2 z-[9999] w-full max-w-sm px-4 animate-toast-in">
      <div className="relative overflow-hidden rounded-3xl bg-[#0e0e1f]/90 border border-[#E4007C]/30 backdrop-blur-xl p-5 shadow-[0_0_30px_rgba(228,0,124,0.3)] text-white">
        {/* Neon Glow decoration */}
        <div className="absolute top-0 right-0 w-32 h-32 bg-[#E4007C]/10 rounded-full blur-3xl pointer-events-none" />

        {/* Dismiss Button */}
        <button
          onClick={dismissPrompt}
          className="absolute top-3 right-3 p-1.5 rounded-full text-slate-400 hover:text-white hover:bg-white/5 transition-all active:scale-90"
        >
          <X size={16} />
        </button>

        {/* Content */}
        <div className="flex gap-4 items-start">
          <div className="w-12 h-12 shrink-0 rounded-2xl bg-gradient-to-tr from-[#E4007C] to-[#FF8DA1] flex items-center justify-center text-2xl shadow-lg shadow-[#E4007C]/20">
            🦎
          </div>
          <div className="flex-1 space-y-1">
            <h3 className="font-black text-[#FF8DA1] tracking-tight">🦎 Juega en tu Celular</h3>
            <p className="text-xs text-slate-300 leading-relaxed">
              Agrega Axolotto a tu pantalla de inicio para jugar a pantalla completa y sin barra de navegación.
            </p>
          </div>
        </div>

        {/* Action / Guide */}
        {isIOS ? (
          <div className="mt-4 pt-3 border-t border-white/5 space-y-3">
            <p className="text-[11px] text-slate-400 font-medium">
              Sigue estos sencillos pasos en Safari:
            </p>
            <div className="flex flex-col gap-2 text-xs">
              <div className="flex items-center gap-2.5 bg-[#1C1C35]/50 px-3 py-2 rounded-xl border border-white/5">
                <Share size={14} className="text-[#FF8DA1]" />
                <span>1. Toca el botón <b>Compartir</b> en Safari</span>
              </div>
              <div className="flex items-center gap-2.5 bg-[#1C1C35]/50 px-3 py-2 rounded-xl border border-white/5">
                <PlusSquare size={14} className="text-[#FF8DA1]" />
                <span>2. Selecciona <b>Añadir a pantalla de inicio</b></span>
              </div>
            </div>
            <button
              onClick={dismissPrompt}
              className="w-full py-2.5 bg-gradient-to-r from-[#E4007C] to-[#B30062] hover:from-[#FF1493] hover:to-[#E4007C] rounded-xl font-bold text-xs shadow-md shadow-[#E4007C]/20 transition-all active:scale-95 text-white"
            >
              ¡Entendido!
            </button>
          </div>
        ) : (
          <div className="mt-4 pt-3 border-t border-white/5 flex gap-2">
            <button
              onClick={dismissPrompt}
              className="flex-1 py-2.5 bg-white/5 hover:bg-white/10 rounded-xl text-slate-300 font-bold text-xs border border-white/10 transition-all active:scale-95"
            >
              Luego
            </button>
            <button
              onClick={async () => {
                const installed = await installApp();
                if (installed) {
                  console.log('App install started');
                }
              }}
              className="flex-1 py-2.5 bg-gradient-to-r from-[#E4007C] to-[#B30062] hover:from-[#FF1493] hover:to-[#E4007C] rounded-xl font-black text-xs shadow-md shadow-[#E4007C]/20 flex items-center justify-center gap-1.5 transition-all active:scale-95 text-white"
            >
              <Download size={13} />
              <span>Instalar Juego</span>
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
