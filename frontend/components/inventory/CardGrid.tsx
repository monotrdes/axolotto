"use client";
import React, { useState } from 'react';
import { createPortal } from 'react-dom';
import { X, Flame } from 'lucide-react';
import LoteriaCard from '@/components/ui/LoteriaCard';
import type { CardRarityFilter, CardShinyFilter, CardOwnedFilter } from '@/types/inventory';

function renderPortal(content: React.ReactNode) {
  if (typeof window === 'undefined') return null;
  return createPortal(content, document.body);
}

interface CardGridProps {
  allCards: any[];
  ownedItems: any[];
  catalogItems: any[];
  cardRarityFilter: CardRarityFilter;
  cardShinyFilter: CardShinyFilter;
  cardOwnedFilter: CardOwnedFilter;
  setCardRarityFilter: (f: CardRarityFilter) => void;
  setCardShinyFilter: (f: CardShinyFilter) => void;
  setCardOwnedFilter: (f: CardOwnedFilter) => void;
  onOpenSellModal: (item: any, name?: string) => void;
  cambiarTab?: (tab: string) => void;
}

export default function CardGrid({
  allCards, ownedItems, catalogItems,
  cardRarityFilter, cardShinyFilter, cardOwnedFilter,
  setCardRarityFilter, setCardShinyFilter, setCardOwnedFilter,
  onOpenSellModal, cambiarTab,
}: CardGridProps) {
  // ── Internal UI States ──
  const [hoveredCard, setHoveredCard] = useState<any | null>(null);
  const [tooltipPos, setTooltipPos] = useState({ x: 0, y: 0 });
  const [selectedCardForAction, setSelectedCardForAction] = useState<any | null>(null);

  const handleMouseMove = (e: React.MouseEvent) => {
    const tooltipWidth = 240;
    const tooltipHeight = 320;
    let x = e.clientX + 15;
    let y = e.clientY + 15;

    if (typeof window !== 'undefined') {
      if (x + tooltipWidth > window.innerWidth) {
        x = e.clientX - tooltipWidth - 15;
      }
      if (y + tooltipHeight > window.innerHeight) {
        y = e.clientY - tooltipHeight - 15;
      }
    }
    setTooltipPos({ x, y });
  };

  return (
    <>
      <div className="mb-4">
        <h3 className="text-xs font-black uppercase text-slate-400 tracking-wider flex items-center gap-1.5">
          <span>🃏</span> ÁLBUM DE CARTAS
        </h3>
      </div>

      {/* FILTROS DE CARTAS */}
      <div className="flex flex-col gap-2.5 bg-slate-950/30 border border-slate-900/60 p-3.5 rounded-2xl mb-5">
        <div className="flex gap-2 items-center flex-wrap">
          <span className="text-[9px] font-black uppercase text-slate-500 tracking-wider">Rareza:</span>
          <div className="flex gap-1 flex-wrap">
            {[
              { key: 'all' as const, label: 'Todos' },
              { key: 'comun' as const, label: 'Común' },
              { key: 'poco_comun' as const, label: 'Poco Común' },
              { key: 'rara' as const, label: 'Rara' },
              { key: 'epica' as const, label: 'Épica' },
              { key: 'legendaria' as const, label: 'Legendaria' },
            ].map((r) => (
              <button
                key={r.key}
                onClick={() => setCardRarityFilter(r.key)}
                className={`px-2.5 py-1 rounded-full text-[9px] font-black uppercase tracking-wider transition-all active:scale-95 ${
                  cardRarityFilter === r.key
                    ? 'bg-amber-400/10 border border-amber-400/40 text-amber-400'
                    : 'bg-white/[0.02] border border-white/[0.05] text-slate-500 hover:text-slate-300'
                }`}
              >
                {r.label}
              </button>
            ))}
          </div>
        </div>

        <div className="flex gap-4 items-center flex-wrap">
          <div className="flex gap-2 items-center">
            <span className="text-[9px] font-black uppercase text-slate-500 tracking-wider">Brillo:</span>
            <div className="flex gap-1">
              {[
                { key: 'all' as const, label: 'Todos' },
                { key: 'shiny' as const, label: 'Brillante ✨' },
                { key: 'normal' as const, label: 'Mate' },
              ].map((s) => (
                <button
                  key={s.key}
                  onClick={() => setCardShinyFilter(s.key)}
                  className={`px-2.5 py-1 rounded-full text-[9px] font-black uppercase tracking-wider transition-all active:scale-95 ${
                    cardShinyFilter === s.key
                      ? 'bg-fuchsia-500/10 border border-fuchsia-500/40 text-fuchsia-400'
                      : 'bg-white/[0.02] border border-white/[0.05] text-slate-500 hover:text-slate-300'
                  }`}
                >
                  {s.label}
                </button>
              ))}
            </div>
          </div>

          <div className="flex gap-2 items-center">
            <span className="text-[9px] font-black uppercase text-slate-500 tracking-wider">Propiedad:</span>
            <div className="flex gap-1">
              {[
                { key: 'all' as const, label: 'Todos' },
                { key: 'owned' as const, label: 'Obtenidas' },
                { key: 'not_owned' as const, label: 'No Obtenidas' },
              ].map((o) => (
                <button
                  key={o.key}
                  onClick={() => setCardOwnedFilter(o.key)}
                  className={`px-2.5 py-1 rounded-full text-[9px] font-black uppercase tracking-wider transition-all active:scale-95 ${
                    cardOwnedFilter === o.key
                      ? 'bg-teal-400/10 border border-teal-400/40 text-teal-400'
                      : 'bg-white/[0.02] border border-white/[0.05] text-slate-500 hover:text-slate-300'
                  }`}
                >
                  {o.label}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* CARD GRID */}
      <div className="grid grid-cols-3 sm:grid-cols-6 lg:grid-cols-9 gap-3 sm:gap-4 mt-4 animate-in fade-in duration-300">
        {allCards
          .filter((card: any) => {
            if (cardRarityFilter === 'comun' && card.dynamic_rarity !== 'Común') return false;
            if (cardRarityFilter === 'poco_comun' && card.dynamic_rarity !== 'Poco Común') return false;
            if (cardRarityFilter === 'rara' && card.dynamic_rarity !== 'Rara') return false;
            if (cardRarityFilter === 'epica' && card.dynamic_rarity !== 'Épica') return false;
            if (cardRarityFilter === 'legendaria' && card.dynamic_rarity !== 'Legendaria') return false;

            const ownedCopies = ownedItems.filter((oi) => oi.id === card.id);
            const totalOwnedQty = ownedCopies.reduce((acc: number, curr: any) => acc + curr.quantity, 0);
            const hasIt = totalOwnedQty > 0;
            const hasShiny = ownedCopies.some((oi: any) => oi.is_shiny);

            if (cardOwnedFilter === 'owned' && !hasIt) return false;
            if (cardOwnedFilter === 'not_owned' && hasIt) return false;
            if (cardShinyFilter === 'shiny' && !hasShiny) return false;
            if (cardShinyFilter === 'normal' && hasShiny && totalOwnedQty === ownedCopies.filter((oi: any) => oi.is_shiny).reduce((acc: number, curr: any) => acc + curr.quantity, 0)) {
              return false;
            }
            return true;
          })
          .map((card: any) => {
            const ownedCopies = ownedItems.filter((oi: any) => oi.id === card.id);
            const totalOwnedQty = ownedCopies.reduce((acc: number, curr: any) => acc + curr.quantity, 0);
            const hasIt = totalOwnedQty > 0;
            const hasFirstEdition = ownedCopies.some((oi: any) => oi.is_first_edition);
            const hasShiny = ownedCopies.some((oi: any) => oi.is_shiny);

            return (
              <div
                key={card.id}
                onMouseEnter={() => setHoveredCard(card)}
                onMouseMove={handleMouseMove}
                onMouseLeave={() => setHoveredCard(null)}
                onClick={() => { if (hasIt) setSelectedCardForAction(card); }}
                className={`relative cursor-pointer transition-all duration-300 hover:scale-105 hover:z-30 ${!hasIt ? 'opacity-40 grayscale' : ''}`}
              >
                <LoteriaCard
                  card={{
                    ...card,
                    availableQty: totalOwnedQty,
                    is_first_edition: hasFirstEdition,
                    is_shiny: hasShiny,
                  }}
                  size="sm"
                  interactive={hasIt}
                  isFirstEdition={hasFirstEdition}
                  showQty={false}
                />
              </div>
            );
          })}
      </div>

      {/* Hover Tooltip */}
      {hoveredCard && renderPortal(
        <div
          style={{
            left: tooltipPos.x,
            top: tooltipPos.y,
            position: 'fixed',
          }}
          className="w-60 bg-slate-950/95 border border-slate-800/80 rounded-2xl p-4 backdrop-blur-md shadow-[0_12px_40px_rgba(0,0,0,0.9)] z-[9999] pointer-events-none animate-in fade-in zoom-in-95 duration-150 flex flex-col gap-3"
        >
          <div className={`absolute -inset-px rounded-2xl opacity-15 blur-lg pointer-events-none transition-all duration-300
            ${hoveredCard.dynamic_rarity === 'Legendaria' ? 'bg-amber-500' : ''}
            ${hoveredCard.dynamic_rarity === 'Épica' ? 'bg-fuchsia-500' : ''}
            ${hoveredCard.dynamic_rarity === 'Rara' ? 'bg-cyan-500' : ''}
            ${hoveredCard.dynamic_rarity === 'Poco Común' ? 'bg-emerald-500' : ''}
            ${hoveredCard.dynamic_rarity === 'Común' ? 'bg-slate-500' : ''}
          `} />

          <div className="flex justify-between items-center z-10">
            <span className="text-[9px] font-black text-slate-500 uppercase tracking-widest leading-none">
              Colección Lotería
            </span>
            <span className="text-[10px] font-black text-slate-400 bg-slate-900/90 px-2 py-0.5 rounded-full border border-white/5 leading-none">
              #{hoveredCard.item_metadata?.numero_loteria || '?'}
            </span>
          </div>

          <div className="flex flex-col items-center justify-center py-4 bg-slate-900/50 rounded-xl border border-white/5 backdrop-blur-sm z-10 relative overflow-hidden">
            <div className="text-6xl drop-shadow-[0_4px_8px_rgba(0,0,0,0.55)]">🃏</div>
            <div className="mt-3 text-center px-2">
              <h4 className="text-sm font-black text-white uppercase tracking-tight leading-tight">
                {hoveredCard.name}
              </h4>
              <p className="text-[9px] text-slate-400 mt-1 leading-normal max-h-[40px] overflow-hidden text-ellipsis">
                {hoveredCard.description}
              </p>
            </div>
          </div>

          <div className="flex flex-col gap-2 z-10 mt-1">
            <div className="flex items-center justify-between">
              <span className="text-[9px] font-bold text-slate-500 uppercase tracking-wider">Rareza Escasez</span>
              <span className={`text-[8px] font-black uppercase tracking-wider px-2 py-0.5 rounded-md border leading-none
                ${hoveredCard.dynamic_rarity === 'Legendaria' ? 'bg-amber-500/10 border-amber-500/60 text-amber-300 shadow-[0_0_8px_rgba(245,158,11,0.2)]' : ''}
                ${hoveredCard.dynamic_rarity === 'Épica' ? 'bg-fuchsia-500/10 border-fuchsia-500/60 text-fuchsia-300' : ''}
                ${hoveredCard.dynamic_rarity === 'Rara' ? 'bg-cyan-500/10 border-cyan-500/60 text-cyan-300' : ''}
                ${hoveredCard.dynamic_rarity === 'Poco Común' ? 'bg-emerald-500/10 border-emerald-500/60 text-emerald-300' : ''}
                ${hoveredCard.dynamic_rarity === 'Común' ? 'bg-slate-500/10 border-slate-500/60 text-slate-300' : ''}
              `}>
                {hoveredCard.dynamic_rarity || 'Común'}
              </span>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-[9px] font-bold text-slate-500 uppercase tracking-wider">Circulación Global</span>
              <span className="text-[9px] font-black text-slate-200">
                {hoveredCard.circulation !== undefined ? `${hoveredCard.circulation} copias` : '0 copias'}
              </span>
            </div>

            {(() => {
              const ownedCopies = ownedItems.filter((oi: any) => oi.id === hoveredCard.id);
              const totalOwned = ownedCopies.reduce((acc: number, curr: any) => acc + curr.quantity, 0);
              const firstEdShinyCopies = ownedCopies.filter((oi: any) => oi.is_first_edition && oi.is_shiny).reduce((acc: number, curr: any) => acc + curr.quantity, 0);
              const shinyCopies = ownedCopies.filter((oi: any) => !oi.is_first_edition && oi.is_shiny).reduce((acc: number, curr: any) => acc + curr.quantity, 0);
              const firstEditionCopies = ownedCopies.filter((oi: any) => oi.is_first_edition && !oi.is_shiny).reduce((acc: number, curr: any) => acc + curr.quantity, 0);
              const normalCopies = ownedCopies.filter((oi: any) => !oi.is_first_edition && !oi.is_shiny).reduce((acc: number, curr: any) => acc + curr.quantity, 0);

              return (
                <div className="border-t border-white/5 pt-2 flex flex-col gap-1.5 mt-1">
                  <div className="flex items-center justify-between">
                    <span className="text-[9px] font-bold text-slate-500 uppercase tracking-wider">Tu Posesión</span>
                    <span className={`text-[9px] font-black ${totalOwned > 0 ? 'text-[#E4007C]' : 'text-slate-500'}`}>
                      {totalOwned > 0 ? `Tienes x${totalOwned}` : 'No la tienes'}
                    </span>
                  </div>
                  {totalOwned > 0 && (
                    <div className="flex flex-col gap-1 pl-1.5 border-l border-slate-800">
                      {firstEdShinyCopies > 0 && (
                        <div className="flex items-center justify-between text-[8px] leading-none py-0.5">
                          <span className="font-black flex items-center gap-0.5" style={{ background: 'linear-gradient(90deg,#fbbf24,#f472b6)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                            ✨⭐ 1st Ed. Brillante
                          </span>
                          <span className="text-slate-300 font-black">x{firstEdShinyCopies}</span>
                        </div>
                      )}
                      {shinyCopies > 0 && (
                        <div className="flex items-center justify-between text-[8px] leading-none py-0.5">
                          <span className="font-black flex items-center gap-0.5" style={{ background: 'linear-gradient(90deg,#c084fc,#f472b6)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                            ✨ Brillante
                          </span>
                          <span className="text-slate-300 font-black">x{shinyCopies}</span>
                        </div>
                      )}
                      {firstEditionCopies > 0 && (
                        <div className="flex items-center justify-between text-[8px] leading-none py-0.5">
                          <span className="text-amber-400 font-black flex items-center gap-0.5">⭐ 1st Edition</span>
                          <span className="text-slate-300 font-black">x{firstEditionCopies}</span>
                        </div>
                      )}
                      {normalCopies > 0 && (
                        <div className="flex items-center justify-between text-[8px] leading-none py-0.5">
                          <span className="text-slate-400 font-bold">Edición Normal</span>
                          <span className="text-slate-300 font-black">x{normalCopies}</span>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })()}
          </div>
        </div>,
      )}

      {/* CARD DETAIL MODAL */}
      {selectedCardForAction && renderPortal(
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-md p-4 animate-in fade-in duration-200"
          onClick={(e) => { if (e.target === e.currentTarget) setSelectedCardForAction(null); }}
        >
          {(() => {
            const rarity = selectedCardForAction.dynamic_rarity || 'Común';
            let rarityStyles = 'border-slate-800 shadow-[0_0_30px_rgba(148,163,184,0.1)]';
            let titleColor = 'text-slate-400';
            if (rarity === 'Legendaria') {
              rarityStyles = 'border-amber-500/60 shadow-[0_0_50px_rgba(251,191,36,0.35)]';
              titleColor = 'text-amber-400';
            } else if (rarity === 'Épica') {
              rarityStyles = 'border-fuchsia-500/50 shadow-[0_0_50px_rgba(217,70,239,0.3)]';
              titleColor = 'text-fuchsia-400';
            } else if (rarity === 'Rara') {
              rarityStyles = 'border-cyan-500/50 shadow-[0_0_50px_rgba(6,182,212,0.3)]';
              titleColor = 'text-cyan-400';
            } else if (rarity === 'Poco Común') {
              rarityStyles = 'border-emerald-500/50 shadow-[0_0_40px_rgba(16,185,129,0.25)]';
              titleColor = 'text-emerald-400';
            }

            return (
              <div className={`bg-[#0D0D1F] border-2 rounded-[2.5rem] p-6 w-full max-w-sm flex flex-col gap-4 animate-in zoom-in-95 duration-150 relative ${rarityStyles}`}>
                <button onClick={() => setSelectedCardForAction(null)}
                  className="absolute top-4 right-4 text-slate-500 hover:text-white transition-colors">
                  <X size={16} />
                </button>

                <div className="text-center border-b border-white/5 pb-3">
                  <span className={`text-[9px] font-black uppercase tracking-widest ${titleColor}`}>
                    {rarity} · Colección Lotería #{selectedCardForAction.item_metadata?.numero_loteria || '?'}
                  </span>
                  <h3 className="text-white font-black text-lg leading-tight mt-1">{selectedCardForAction.name}</h3>
                </div>

                <div className="flex flex-col items-center justify-center py-6 bg-slate-900/40 rounded-2xl border border-white/5">
                  <div className="scale-125 mb-4">
                    <LoteriaCard card={selectedCardForAction} size="md" interactive={false} />
                  </div>
                  <p className="text-xs text-slate-400 px-4 text-center leading-normal">
                    {selectedCardForAction.description}
                  </p>
                </div>

                <div className="flex flex-col gap-2">
                  <p className="text-[10px] font-black text-slate-500 uppercase tracking-wider">Tus Copias Disponibles:</p>
                  {(() => {
                    const ownedCopies = ownedItems.filter((oi: any) => oi.id === selectedCardForAction.id && oi.quantity > 0);
                    if (ownedCopies.length === 0) return <p className="text-xs text-slate-500 italic">No tienes copias libres.</p>;
                    return ownedCopies.map((copy: any) => {
                      let copyLabel = "Edición Normal";
                      if (copy.is_first_edition && copy.is_shiny) copyLabel = "✨⭐ 1st Ed. Brillante";
                      else if (copy.is_shiny) copyLabel = "✨ Brillante";
                      else if (copy.is_first_edition) copyLabel = "⭐ 1st Edition";

                      return (
                        <div key={copy.inventory_id} className="flex items-center justify-between bg-white/[0.03] border border-white/5 rounded-2xl px-4 py-2 gap-2">
                          <div className="flex flex-col min-w-0 flex-1">
                            <span className="text-[10px] font-bold text-white leading-tight truncate">{copyLabel}</span>
                            <span className="text-[8px] text-slate-500 mt-0.5 font-mono">Posees: x{copy.quantity}</span>
                          </div>
                          <div className="flex items-center gap-1.5 shrink-0">
                            {copy.quantity >= 5 && !copy.is_shiny && (
                              <button
                                onClick={() => {
                                  setSelectedCardForAction(null);
                                  cambiarTab?.('tienda');
                                }}
                                className="px-3 py-1.5 rounded-xl bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-[9px] font-black uppercase text-white tracking-wider transition-all active:scale-95 shadow-md flex items-center gap-1"
                                title="Fundir 5 copias en el Cenote Místico"
                              >
                                <Flame size={10} />
                                Fundir
                              </button>
                            )}
                            <button
                              onClick={() => onOpenSellModal(copy, selectedCardForAction.name)}
                              className="px-3 py-1.5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-500 hover:from-emerald-500 hover:to-teal-400 text-[9px] font-black uppercase text-white tracking-wider transition-all active:scale-95 shadow-md"
                            >
                              Vender
                            </button>
                          </div>
                        </div>
                      );
                    });
                  })()}
                </div>
              </div>
            );
          })()}
        </div>,
      )}
    </>
  );
}
