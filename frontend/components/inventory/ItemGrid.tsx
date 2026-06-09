"use client";
import React from 'react';

interface ItemGridProps {
  ownedItems: any[];
  cambiarTab?: (tab: string) => void;
}

const CONSUMABLE_META: Record<string, { emoji: string; color: string; border: string; targetTab: string; targetLabel: string }> = {
  'gota de agua': { emoji: '💧', color: 'from-cyan-600/30 to-blue-500/20', border: 'border-cyan-500/30', targetTab: 'santuario', targetLabel: 'Ir al Santuario' },
  'gota de agua de cenote': { emoji: '💧', color: 'from-cyan-600/30 to-blue-500/20', border: 'border-cyan-500/30', targetTab: 'santuario', targetLabel: 'Ir al Santuario' },
  'lámpara de calor': { emoji: '🔆', color: 'from-amber-600/30 to-orange-500/20', border: 'border-amber-500/30', targetTab: 'santuario', targetLabel: 'Ir al Criadero' },
  'lampara de calor': { emoji: '🔆', color: 'from-amber-600/30 to-orange-500/20', border: 'border-amber-500/30', targetTab: 'santuario', targetLabel: 'Ir al Criadero' },
  'escudo del santuario': { emoji: '🛡️', color: 'from-purple-600/30 to-violet-500/20', border: 'border-purple-500/30', targetTab: 'santuario', targetLabel: 'Ir al Santuario' },
};

function getConsumableMeta(name: string) {
  const key = name.toLowerCase();
  return CONSUMABLE_META[key] ?? {
    emoji: '🎒',
    color: 'from-slate-700/30 to-slate-600/20',
    border: 'border-slate-600/30',
    targetTab: 'santuario',
    targetLabel: 'Usar',
  };
}

export default function ItemGrid({ ownedItems, cambiarTab }: ItemGridProps) {
  const consumables = ownedItems.filter(
    (i) => i.item_type?.toUpperCase() === 'CONSUMABLE' && i.quantity > 0,
  );

  if (consumables.length === 0) {
    return (
      <div className="py-16 flex flex-col items-center justify-center text-center animate-in fade-in duration-300">
        <span className="text-6xl mb-4">🎒</span>
        <h3 className="text-xl font-black text-white uppercase tracking-tight mb-2">Sin objetos</h3>
        <p className="text-slate-400 text-sm max-w-sm mb-4 leading-relaxed">
          Consigue consumibles en la tienda o como recompensas: Gotas de Agua, Lámparas de Calor, Escudos del Santuario y más.
        </p>
        {cambiarTab && (
          <button
            onClick={() => cambiarTab('tienda')}
            className="px-6 py-3 bg-gradient-to-r from-purple-600 to-amber-600 hover:from-purple-500 hover:to-amber-500 text-white font-black rounded-xl text-xs uppercase tracking-widest transition-all active:scale-95"
          >
            Ir a la Tienda
          </button>
        )}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3 animate-in fade-in duration-300">
      {consumables.map((item: any) => {
        const meta = getConsumableMeta(item.name);
        return (
          <div
            key={item.inventory_id}
            className={`relative bg-gradient-to-br ${meta.color} border ${meta.border} rounded-2xl p-4 flex flex-col gap-3`}
          >
            <div className="flex items-start justify-between">
              <span className="text-3xl">{meta.emoji}</span>
              <span className="bg-slate-900/60 text-white font-black text-xs px-2 py-0.5 rounded-full border border-white/10">
                x{item.quantity}
              </span>
            </div>
            <div className="flex-1">
              <p className="text-white font-black text-xs uppercase tracking-tight leading-tight">{item.name}</p>
              {item.description && (
                <p className="text-slate-400 text-[10px] mt-0.5 leading-tight line-clamp-2">{item.description}</p>
              )}
            </div>
            {cambiarTab && (
              <button
                onClick={() => cambiarTab(meta.targetTab)}
                className="w-full py-2 rounded-xl text-[10px] font-black uppercase tracking-wider bg-white/10 hover:bg-white/20 text-white border border-white/10 hover:border-white/25 transition-all active:scale-95"
              >
                {meta.targetLabel}
              </button>
            )}
          </div>
        );
      })}
    </div>
  );
}
