"use client";
import React from 'react';
import { Shield, Snowflake, Clock, Zap, Flame, Droplets, Plus } from 'lucide-react';
import { useToast } from '@/context/ToastContext';
import { ShieldModalProps } from '@/types/santuario';
import { useIncubationItem, buyAndUseIncubationItem } from '@/services/santuarioService';

export default function ShieldModal({ incId, incubaciones, userId, token, cantidadGotas, cantidadLamparas, precioGotas, precioLamparas, onClose, onSuccess, cambiarTab }: ShieldModalProps) {
  const { toast } = useToast();
  const inc = incubaciones.find(i => i.id === incId);
  const esCongelado = inc?.is_frozen;
  const headers = token ? { Authorization: `Bearer ${token}` } : {};

  const useItem = async (itemId: number, label: string) => {
    try {
      await useIncubationItem(incId, itemId, userId, token);
      toast.ok(`¡${label} aplicado con éxito!`);
      onClose(); onSuccess();
    } catch {
      toast.error(`Error al usar ${label}`);
    }
  };

  const buyAndUse = async (itemId: number, label: string) => {
    try {
      await buyAndUseIncubationItem(incId, itemId, userId, token);
      toast.ok(`¡${label} comprado y aplicado!`);
      onClose(); onSuccess();
    } catch (e: any) {
      const go = window.confirm(`${e.response?.data?.detail || 'Sin recursos'}. ¿Ir a la Tienda?`);
      if (go && cambiarTab) { onClose(); cambiarTab('tienda'); }
    }
  };

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/85 backdrop-blur-md p-4 animate-in fade-in duration-300">
      <div className="bg-slate-900 border-2 border-slate-800 rounded-[2.5rem] p-6 sm:p-8 max-w-md w-full shadow-2xl">
        <div className="flex flex-col items-center">
          <Shield size={28} className="text-amber-500 mb-2 animate-pulse" />
          <h3 className="text-lg font-black text-white uppercase tracking-tighter mb-1">
            Protección del <span className="text-[#E4007C]">Nido</span>
          </h3>
          <p className="text-slate-500 text-[10px] uppercase tracking-widest font-black mb-5">
            {esCongelado ? '❄️ Huevo congelado — requiere calor' : '🛡️ Previene la congelación climática'}
          </p>

          <div className="flex flex-col w-full gap-3 mb-5">
            <div className={`p-4 rounded-2xl bg-slate-950/50 border ${esCongelado ? 'border-cyan-500/40' : 'border-slate-800'}`}>
              <div className="flex justify-between items-center mb-2">
                <span className="text-xs font-black text-cyan-400 flex items-center gap-1"><Droplets size={12} /> Gotas Anti-Escarcha</span>
                <span className="text-[9px] bg-slate-800 text-slate-300 px-2 py-0.5 rounded-full border border-white/5">
                  Mochila: <span className="text-cyan-400 font-bold">{cantidadGotas}</span>
                </span>
              </div>
              <p className="text-slate-400 text-[10px] mb-3 leading-tight">
                {esCongelado ? 'Descongela e inyecta escudo 12h. −6h eclosión.' : 'Campo térmico 12h. +50% calor, −6h eclosión.'}
              </p>
              {cantidadGotas > 0 ? (
                <button onClick={() => useItem(61, 'Gotas')} className="w-full py-2 bg-gradient-to-r from-cyan-600 to-blue-500 text-white font-black rounded-xl text-[9px] uppercase tracking-widest active:scale-95 flex items-center justify-center gap-1.5">
                  <Shield size={11} /> Aplicar desde mochila (x{cantidadGotas})
                </button>
              ) : (
                <button onClick={() => buyAndUse(61, 'Gotas')} className="w-full py-2 bg-slate-800 hover:bg-slate-700 text-cyan-200 font-black rounded-xl text-[9px] uppercase tracking-widest active:scale-95 border border-cyan-500/20 flex items-center justify-center gap-1.5">
                  <Plus size={11} /> Comprar y Aplicar ({precioGotas} FRJ)
                </button>
              )}
            </div>

            <div className={`p-4 rounded-2xl bg-slate-950/50 border ${!esCongelado ? 'border-orange-500/40' : 'border-slate-800'}`}>
              <div className="flex justify-between items-center mb-2">
                <span className="text-xs font-black text-orange-400 flex items-center gap-1"><Flame size={12} /> Lámpara Infrarroja Pro</span>
                <span className="text-[9px] bg-slate-800 text-slate-300 px-2 py-0.5 rounded-full border border-white/5">
                  Mochila: <span className="text-orange-400 font-bold">{cantidadLamparas}</span>
                </span>
              </div>
              <p className="text-slate-400 text-[10px] mb-3 leading-tight">
                {esCongelado ? 'Descongela + calor 100% + escudo 24h. −18h eclosión.' : 'Calefacción 24h. Calor 100%, −18h eclosión.'}
              </p>
              {cantidadLamparas > 0 ? (
                <button onClick={() => useItem(62, 'Lámpara')} className="w-full py-2 bg-gradient-to-r from-orange-600 to-amber-500 text-white font-black rounded-xl text-[9px] uppercase tracking-widest active:scale-95 flex items-center justify-center gap-1.5">
                  <Shield size={11} /> Instalar desde mochila (x{cantidadLamparas})
                </button>
              ) : (
                <button onClick={() => buyAndUse(62, 'Lámpara')} className="w-full py-2 bg-slate-800 hover:bg-slate-700 text-orange-200 font-black rounded-xl text-[9px] uppercase tracking-widest active:scale-95 border border-orange-500/20 flex items-center justify-center gap-1.5">
                  <Zap size={11} /> Comprar e Instalar ({precioLamparas} AXF)
                </button>
              )}
            </div>
          </div>

          <button onClick={onClose} className="text-slate-500 hover:text-slate-300 text-[10px] font-bold uppercase tracking-widest">
            Tal vez después
          </button>
        </div>
      </div>
    </div>
  );
}
