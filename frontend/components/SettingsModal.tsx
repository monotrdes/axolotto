'use client';

import { useState, useEffect } from 'react';
import { usePWAInstall } from '@/hooks/usePWAInstall';
import { X, Volume2, VolumeX, Download, Share, PlusSquare, HelpCircle, LogOut, Monitor } from 'lucide-react';
import { playPurchaseSound } from '@/lib/audioUtils';
import { PAPER_WORLD } from '@/lib/paperWorld';
import type { QualityTier } from '@/components/world/engine/qualityTier';

const QUALITY_STORAGE_KEY = 'axolotto_world_quality';

function storedQuality(): QualityTier | 'auto' {
  if (typeof window === 'undefined') return 'auto';
  const v = localStorage.getItem(QUALITY_STORAGE_KEY);
  if (v === 'alta' || v === 'media' || v === 'ligera') return v;
  return 'auto';
}

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  onLogout?: () => void;
  onResetTutorial?: () => void;
  /** Callback cuando el usuario cambia la calidad manualmente (plan task-84 §7). */
  onQualityChange?: (tier: QualityTier | 'auto') => void;
}

export default function SettingsModal({ isOpen, onClose, onLogout, onResetTutorial, onQualityChange }: SettingsModalProps) {
  const {
    isInstallable,
    isStandalone,
    isIOS,
    installApp,
  } = usePWAInstall();

  const [soundEnabled, setSoundEnabled] = useState(true);
  const [quality, setQuality] = useState<QualityTier | 'auto'>(storedQuality());
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem('sound_effects_enabled');
      setSoundEnabled(stored !== 'false');
      setQuality(storedQuality());
    }
  }, []);

  if (!mounted || !isOpen) return null;

  const toggleSound = () => {
    const newVal = !soundEnabled;
    setSoundEnabled(newVal);
    localStorage.setItem('sound_effects_enabled', newVal ? 'true' : 'false');

    // Play a test sound if enabling
    if (newVal) {
      // Small timeout to allow AudioContext to register state if needed
      setTimeout(() => {
        try {
          playPurchaseSound();
        } catch (e) {
          console.warn('AudioContext not allowed or not loaded yet', e);
        }
      }, 50);
    }
  };

  const handleQualityChange = (next: QualityTier | 'auto') => {
    setQuality(next);
    localStorage.setItem(QUALITY_STORAGE_KEY, next);
    onQualityChange?.(next);
  };

  return (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center p-4">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-[#06060c]/80 backdrop-blur-md transition-opacity" 
        onClick={onClose}
      />

      {/* Modal Card */}
      <div className="relative w-full max-w-md overflow-hidden rounded-3xl bg-[#0e0e1f]/90 border border-white/10 p-6 shadow-[0_0_40px_rgba(0,0,0,0.8)] text-white animate-toast-in">
        {/* Glow Effects */}
        <div className="absolute -top-20 -left-20 w-44 h-44 bg-[#E4007C]/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-20 -right-20 w-44 h-44 bg-[#B30062]/10 rounded-full blur-3xl pointer-events-none" />

        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-white/5 mb-6">
          <div className="flex items-center gap-2">
            <span className="text-xl">⚙️</span>
            <h2 className="text-xl font-black text-[#FF8DA1] tracking-tight">Ajustes del Juego</h2>
          </div>
          <button 
            onClick={onClose}
            className="p-1.5 rounded-full text-slate-400 hover:text-white hover:bg-white/5 transition-all active:scale-90"
          >
            <X size={20} />
          </button>
        </div>

        {/* Content Options */}
        <div className="space-y-6">
          
          {/* Audio Setting */}
          <div className="flex items-center justify-between p-4 bg-[#1C1C35]/40 rounded-2xl border border-white/5">
            <div className="flex items-center gap-3">
              <div className={`p-2.5 rounded-xl ${soundEnabled ? 'bg-[#E4007C]/10 text-[#FF8DA1]' : 'bg-slate-800 text-slate-500'}`}>
                {soundEnabled ? <Volume2 size={20} /> : <VolumeX size={20} />}
              </div>
              <div>
                <p className="font-bold text-sm">Efectos de Sonido</p>
                <p className="text-xs text-slate-400">Sonidos de botones y partida</p>
              </div>
            </div>

            {/* Toggle Switch */}
            <button 
              onClick={toggleSound}
              className={`relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${
                soundEnabled ? 'bg-[#E4007C]' : 'bg-slate-700'
              }`}
            >
              <span
                className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                  soundEnabled ? 'translate-x-5' : 'translate-x-0'
                }`}
              />
            </button>
          </div>

          {/* ── Calidad gráfica (solo mundo papel picado, plan task-84 §7) ──── */}
          {PAPER_WORLD && (
            <div className="p-4 bg-[#1C1C35]/40 rounded-2xl border border-white/5 space-y-3">
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-xl bg-purple-500/10 text-purple-400">
                  <Monitor size={20} />
                </div>
                <div>
                  <p className="font-bold text-sm">Calidad Gráfica</p>
                  <p className="text-xs text-slate-400">
                    {quality === 'auto'
                      ? 'Auto — se ajusta a tu dispositivo'
                      : quality === 'alta'
                        ? 'Alta — 60 FPS, agua animada, partículas'
                        : quality === 'media'
                          ? 'Media — 60 FPS, sin agua animada'
                          : 'Ligera — 30 FPS, pocas capas'}
                  </p>
                </div>
              </div>
              <div className="flex gap-2">
                {(['auto', 'alta', 'media', 'ligera'] as const).map((tier) => (
                  <button
                    key={tier}
                    onClick={() => handleQualityChange(tier)}
                    className={`flex-1 py-2 rounded-xl text-[10px] font-bold transition-all active:scale-95 border ${
                      quality === tier
                        ? 'bg-purple-600/40 border-purple-400/40 text-purple-200 shadow-[0_0_10px_rgba(168,85,247,0.25)]'
                        : 'bg-white/5 border-white/10 text-slate-400 hover:bg-white/10'
                    }`}
                  >
                    {tier === 'auto' ? 'Auto' : tier === 'alta' ? 'Alta' : tier === 'media' ? 'Media' : 'Ligera'}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* PWA / Installation Settings */}
          <div className="p-4 bg-[#1C1C35]/40 rounded-2xl border border-white/5 space-y-4">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-cyan-500/10 text-cyan-400">
                <Download size={20} />
              </div>
              <div>
                <p className="font-bold text-sm">Versión de App Móvil</p>
                <p className="text-xs text-slate-400">Instala el juego en tu teléfono</p>
              </div>
            </div>

            {isStandalone ? (
              <div className="text-center p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-xl text-emerald-400 text-xs font-bold">
                ✓ ¡Ya estás jugando desde la aplicación oficial!
              </div>
            ) : (
              <div className="space-y-3 pt-2">
                <p className="text-xs text-slate-300 leading-relaxed">
                  Para tener una experiencia libre de distracciones y con el máximo rendimiento, puedes instalar Axolotto en tu pantalla de inicio.
                </p>

                {isIOS ? (
                  <div className="space-y-2 border-t border-white/5 pt-3">
                    <p className="text-[11px] text-slate-400 font-bold flex items-center gap-1.5">
                      <HelpCircle size={12} /> Guía de instalación en iOS (Safari):
                    </p>
                    <div className="flex flex-col gap-1.5 text-xs text-slate-300">
                      <div className="flex items-center gap-2 bg-[#0e0e1f]/60 px-3 py-1.5 rounded-lg border border-white/5">
                        <Share size={12} className="text-[#FF8DA1]" />
                        <span>1. Pulsa el botón <b>Compartir</b></span>
                      </div>
                      <div className="flex items-center gap-2 bg-[#0e0e1f]/60 px-3 py-1.5 rounded-lg border border-white/5">
                        <PlusSquare size={12} className="text-[#FF8DA1]" />
                        <span>2. Selecciona <b>Añadir a pantalla de inicio</b></span>
                      </div>
                    </div>
                  </div>
                ) : (
                  <button
                    onClick={async () => {
                      const success = await installApp();
                      if (success) {
                        onClose();
                      }
                    }}
                    className="w-full py-3 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 rounded-xl font-black text-sm transition-all active:scale-95 shadow-md shadow-cyan-500/10 text-white flex items-center justify-center gap-2"
                  >
                    <Download size={16} />
                    <span>Instalar en mi Celular</span>
                  </button>
                )}
              </div>
            )}
          </div>

          {/* Dev/Reset Tutorial & Logout Actions */}
          <div className="grid grid-cols-2 gap-3 pt-2">
            {onResetTutorial && (
              <button
                onClick={() => {
                  onResetTutorial();
                  onClose();
                }}
                className="py-3 bg-white/5 hover:bg-white/10 rounded-xl text-xs font-bold text-slate-300 border border-white/10 transition-all active:scale-95 text-center"
              >
                Reiniciar Tutorial
              </button>
            )}
            
            {onLogout && (
              <button
                onClick={() => {
                  onLogout();
                  onClose();
                }}
                className={`py-3 bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/20 text-rose-400 rounded-xl text-xs font-bold transition-all active:scale-95 flex items-center justify-center gap-1.5 ${
                  onResetTutorial ? '' : 'col-span-2'
                }`}
              >
                <LogOut size={14} />
                <span>Cerrar Sesión</span>
              </button>
            )}
          </div>

        </div>
      </div>
    </div>
  );
}
