"use client";
import { API_BASE } from "@/lib/api";

import React, { useState, useEffect, useCallback, useRef } from 'react';
import axios from 'axios';
import { Search, Loader2, ChevronLeft, Ticket, RefreshCw, ShoppingCart, Trash2 } from 'lucide-react';
import { useToast } from '@/context/ToastContext';

const API = `${API_BASE}`;

// ── Ticket economy (mirrors backend settings) ──
const RECYCLE_TICKETS: Record<string, number> = {
  common: 3, rare: 9, epic: 30, legendary: 100,
};
const REDEEM_COST: Record<string, number> = {
  common: 15, rare: 45, epic: 150, legendary: 500,
};

interface ReciclonPanelProps {
  userId: string;
  token: string | null;
  recargarSaldos: () => void;
  onBack?: () => void;
}

export default function ReciclonPanel({
  userId,
  token,
  recargarSaldos,
  onBack,
}: ReciclonPanelProps) {
  const { toast } = useToast();
  const [wallet, setWallet] = useState<any>(null);
  const [inventory, setInventory] = useState<any[]>([]);
  const [allCards, setAllCards] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // Recycle state: key = `${cardId}-${isFirstEdition}`, value = quantity to recycle
  const [selectedRecycle, setSelectedRecycle] = useState<Record<string, number>>({});
  const [recycling, setRecycling] = useState(false);

  // Redeem state
  const [redeeming, setRedeeming] = useState<Set<number>>(new Set());
  const [shopSearch, setShopSearch] = useState('');
  const [shopRarityFilter, setShopRarityFilter] = useState<'all' | 'common' | 'rare' | 'epic' | 'legendary'>('all');

  // Ticket counter animation
  const [ticketAnim, setTicketAnim] = useState(false);
  const prevTicketsRef = useRef<number>(0);

  const loadData = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    try {
      const headers = { Authorization: `Bearer ${token}` };
      const [walletRes, invRes, cardsRes] = await Promise.all([
        axios.get(`${API}/bank/wallet/${userId}`, { headers }),
        axios.get(`${API}/auth/inventory/${userId}`, { headers }),
        axios.get(`${API}/shop/cards`),
      ]);
      setWallet(walletRes.data);
      setInventory(invRes.data);
      setAllCards(cardsRes.data);
    } catch (err) {
      console.error("Error loading reciclon data:", err);
      toast.error("Error al cargar datos de El Reciclón");
    } finally {
      setLoading(false);
    }
  }, [userId, token, toast]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Animate counter when tickets change
  useEffect(() => {
    const current = wallet?.tickets_reciclon ?? 0;
    if (current > prevTicketsRef.current) {
      setTicketAnim(true);
      const t = setTimeout(() => setTicketAnim(false), 600);
      prevTicketsRef.current = current;
      return () => clearTimeout(t);
    }
    prevTicketsRef.current = current;
  }, [wallet?.tickets_reciclon]);

  // ── Recycle helpers ──

  // All inventory items that are cards, non-shiny, with quantity >= 1
  const ownedCards = React.useMemo(() => {
    return inventory.filter(
      (item) => item.item_type === 'CARD' && item.quantity >= 1 && !item.is_shiny
    );
  }, [inventory]);

  const getSelectedCount = () => {
    return Object.values(selectedRecycle).reduce((sum, qty) => sum + qty, 0);
  };

  const getSelectedTickets = () => {
    return ownedCards.reduce((total, card) => {
      const key = `${card.id}-${card.is_first_edition ?? false}`;
      const qty = selectedRecycle[key] || 0;
      const rarity = card.rarity?.toLowerCase() || 'common';
      return total + qty * (RECYCLE_TICKETS[rarity] || 0);
    }, 0);
  };

  const setCardQuantity = (cardId: number, isFirstEdition: boolean, qty: number) => {
    const key = `${cardId}-${isFirstEdition}`;
    setSelectedRecycle((prev) => {
      const next = { ...prev };
      if (qty <= 0) {
        delete next[key];
      } else {
        next[key] = qty;
      }
      return next;
    });
  };

  const selectAllByRarity = (rarity: string) => {
    setSelectedRecycle((prev) => {
      const next = { ...prev };
      ownedCards.forEach((card) => {
        if (card.rarity?.toLowerCase() === rarity) {
          const key = `${card.id}-${card.is_first_edition ?? false}`;
          next[key] = card.quantity;
        }
      });
      return next;
    });
  };

  const clearSelection = () => {
    setSelectedRecycle({});
  };

  const handleRecycle = async () => {
    if (!token || getSelectedCount() === 0) return;
    setRecycling(true);
    try {
      const headers = { Authorization: `Bearer ${token}` };
      const items = Object.entries(selectedRecycle)
        .filter(([, qty]) => qty > 0)
        .map(([key, qty]) => {
          const [cardId, isFirstEdition] = key.split('-');
          return { card_id: parseInt(cardId), quantity: qty, is_first_edition: isFirstEdition === 'true' };
        });

      const res = await axios.post(
        `${API}/shop/reciclon/recycle`,
        { items },
        { headers }
      );

      const { tickets_earned, cards_recycled } = res.data;
      setSelectedRecycle({});
      await loadData();
      recargarSaldos();
      toast.ok(`¡${cards_recycled} cartas recicladas! +${tickets_earned} Tickets de Reciclón ♻️`);
    } catch (err: any) {
      console.error("Error recycling cards:", err);
      toast.error(err.response?.data?.detail || "Error al reciclar cartas");
    } finally {
      setRecycling(false);
    }
  };

  // ── Redeem helpers ──

  const handleRedeem = async (cardId: number) => {
    if (!token) return;
    setRedeeming((prev) => new Set(prev).add(cardId));
    try {
      const headers = { Authorization: `Bearer ${token}` };
      const res = await axios.post(
        `${API}/shop/reciclon/redeem`,
        { target_card_id: cardId },
        { headers }
      );

      const { redeemed_card, tickets_spent } = res.data;
      await loadData();
      recargarSaldos();
      toast.ok(`¡${redeemed_card.name} obtenida! -${tickets_spent} Tickets 🎫`);
    } catch (err: any) {
      console.error("Error redeeming card:", err);
      toast.error(err.response?.data?.detail || "Error al canjear tickets");
    } finally {
      setRedeeming((prev) => {
        const next = new Set(prev);
        next.delete(cardId);
        return next;
      });
    }
  };

  // ── Rarity helpers ──

  const getRarityColor = (rarity: string) => {
    switch (rarity?.toLowerCase()) {
      case 'legendary': case 'legendaria':
        return { label: 'Legendaria', color: 'text-amber-400 border-amber-400/30 bg-amber-950/20', emoji: '⭐' };
      case 'epic': case 'épica':
        return { label: 'Épica', color: 'text-fuchsia-400 border-fuchsia-500/30 bg-fuchsia-950/20', emoji: '✨' };
      case 'rare': case 'rara':
        return { label: 'Rara', color: 'text-cyan-400 border-cyan-500/30 bg-cyan-950/20', emoji: '🔷' };
      case 'common': case 'común':
      default:
        return { label: 'Común', color: 'text-slate-300 border-slate-500/30 bg-slate-900/40', emoji: '🟢' };
    }
  };

  // ── Loading state ──

  if (loading && !wallet) {
    return (
      <div className="flex flex-col items-center justify-center py-20 gap-4">
        <Loader2 className="w-10 h-10 text-emerald-500 animate-spin" />
        <p className="text-slate-400 text-xs font-black uppercase tracking-widest animate-pulse">
          Accediendo a El Reciclón...
        </p>
      </div>
    );
  }

  const ticketsBalance = wallet?.tickets_reciclon ?? 0;
  const selectedCount = getSelectedCount();
  const selectedTickets = getSelectedTickets();

  return (
    <div className="flex flex-col gap-6 max-w-4xl mx-auto">
      {/* ── HEADER ── */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => onBack?.()}
          className="w-10 h-10 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-emerald-500/30 flex items-center justify-center text-slate-400 hover:text-white active:scale-95 transition-all cursor-pointer shadow-md"
          title="Volver al Tianguis"
        >
          <ChevronLeft size={20} />
        </button>
        <div className="text-center flex-1">
          <h2 className="text-2xl sm:text-3xl font-extrabold italic text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-teal-400 tracking-tighter uppercase drop-shadow-[0_0_12px_rgba(45,212,191,0.4)]">
            EL RECICLÓN
          </h2>
          <p className="text-[9px] sm:text-[10px] text-slate-500 tracking-widest mt-0.5 uppercase font-black">
            Recicla y Obten Cartas
          </p>
        </div>
        <div className="w-10 h-10" />
      </div>

      {/* ── TICKET BALANCE BAR ── */}
      <div className="bg-slate-950/60 border border-emerald-500/20 rounded-3xl p-4 shadow-[0_0_20px_rgba(45,212,191,0.05)]">
        <div className="flex items-center justify-center gap-4">
          <div className="flex items-center gap-3 bg-slate-900/60 border border-emerald-500/20 rounded-2xl px-6 py-3">
            <span className="text-2xl">🎫</span>
            <div className="flex flex-col">
              <span className="text-[8px] font-black text-slate-500 uppercase tracking-widest">
                Tickets de Reciclón
              </span>
              <span
                className={`text-2xl font-black text-emerald-400 transition-all duration-300 ${
                  ticketAnim ? 'scale-125 text-emerald-300' : ''
                }`}
              >
                {ticketsBalance.toLocaleString()}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* ── SECTION 1: RECYCLE ── */}
      <div className="bg-slate-950/40 border border-white/5 rounded-3xl p-5">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-black uppercase text-slate-300 tracking-wider flex items-center gap-2">
              <RefreshCw size={16} className="text-emerald-400" />
              Reciclar Cartas Duplicadas
            </h3>
            <p className="text-[10px] text-slate-500 mt-0.5">
              Selecciona las cartas repetidas que quieras reciclar por Tickets
            </p>
          </div>

          {/* Quick-select buttons */}
          <div className="hidden sm:flex gap-1.5">
            {(['common', 'rare', 'epic', 'legendary'] as const).map((rarity) => (
              <button
                key={rarity}
                onClick={() => selectAllByRarity(rarity)}
                className={`px-2.5 py-1 rounded-lg text-[9px] font-black uppercase tracking-wider border transition-all cursor-pointer ${
                  getRarityColor(rarity).color
                }`}
              >
                {getRarityColor(rarity).emoji} Todas
              </button>
            ))}
            <button
              onClick={clearSelection}
              className="px-2.5 py-1 rounded-lg text-[9px] font-black uppercase tracking-wider border border-slate-600 text-slate-400 hover:text-white bg-slate-900/40 transition-all cursor-pointer"
            >
              ✕ Limpiar
            </button>
          </div>
        </div>

        {/* Quick-select mobile */}
        <div className="flex sm:hidden gap-1.5 mb-3 overflow-x-auto pb-1">
          {(['common', 'rare', 'epic', 'legendary'] as const).map((rarity) => (
            <button
              key={rarity}
              onClick={() => selectAllByRarity(rarity)}
              className={`px-2.5 py-1 rounded-lg text-[8px] font-black uppercase tracking-wider border whitespace-nowrap transition-all cursor-pointer ${
                getRarityColor(rarity).color
              }`}
            >
              {getRarityColor(rarity).emoji} {getRarityColor(rarity).label}
            </button>
          ))}
          <button
            onClick={clearSelection}
            className="px-2.5 py-1 rounded-lg text-[8px] font-black uppercase tracking-wider border border-slate-600 text-slate-400 bg-slate-900/40 whitespace-nowrap cursor-pointer"
          >
            ✕ Limpiar
          </button>
        </div>

        {/* Card list */}
        {ownedCards.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 text-center">
            <span className="text-4xl mb-3">🃏</span>
            <p className="text-slate-500 text-xs font-semibold">
              No tienes cartas duplicadas para reciclar.
            </p>
            <p className="text-[10px] text-slate-600 mt-1">
              ¡Abre sobres en el Tianguis para conseguir cartas!
            </p>
          </div>
        ) : (
          <div className="space-y-2 max-h-[360px] overflow-y-auto pr-1">
            {ownedCards.map((item) => {
              const key = `${item.id}-${item.is_first_edition ?? false}`;
              const selected = selectedRecycle[key] || 0;
              const rar = getRarityColor(item.rarity);
              const ticketsPerCard = RECYCLE_TICKETS[item.rarity?.toLowerCase()] || 0;

              return (
                <div
                  key={key}
                  className={`flex items-center gap-3 p-3 rounded-2xl border transition-all ${
                    selected > 0
                      ? 'bg-emerald-950/20 border-emerald-500/30 shadow-[0_0_10px_rgba(45,212,191,0.1)]'
                      : 'bg-slate-900/30 border-white/5 hover:border-white/10'
                  }`}
                >
                  {/* Card image */}
                  <div className="w-12 h-16 bg-slate-950 rounded-lg flex items-center justify-center border border-white/10 overflow-hidden shrink-0">
                    <img
                      src={`${typeof window !== 'undefined' ? (window.location.hostname.endsWith('axolot.to') ? 'https://api.axolot.to' : window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' ? 'http://localhost:8001' : 'http://' + window.location.hostname + ':8001') : 'http://localhost:8001'}/api/v1/metadata/cards/${item.id}.jpg`}
                      alt={item.name}
                      className="w-full h-full object-cover rounded-md"
                      onError={(e) => { (e.target as HTMLElement).style.display = 'none'; }}
                    />
                  </div>

                  {/* Info */}
                  <div className="flex-1 min-w-0">
                    <h4 className="text-xs font-black text-white uppercase tracking-tight truncate">
                      {item.name}
                    </h4>
                    <div className="flex items-center gap-2 mt-1">
                      <span className={`text-[7px] font-extrabold px-1.5 py-0.5 rounded border uppercase tracking-wider ${rar.color}`}>
                        {rar.label}
                      </span>
                      <span className="text-[9px] text-slate-500 font-bold">
                        Tienes: <span className="text-white">{item.quantity}</span>
                      </span>
                      <span className="text-[9px] text-emerald-400 font-bold">
                        +{ticketsPerCard}🎫 c/u
                      </span>
                    </div>
                  </div>

                  {/* Quantity selector */}
                  <div className="flex items-center gap-1.5 shrink-0">
                    <button
                      onClick={() => setCardQuantity(item.id, item.is_first_edition ?? false, Math.max(0, selected - 1))}
                      className="w-7 h-7 rounded-lg bg-slate-800 border border-slate-700 text-slate-300 hover:text-white text-sm font-black transition-all cursor-pointer"
                    >
                      −
                    </button>
                    <span className={`w-8 text-center text-sm font-black ${selected > 0 ? 'text-emerald-400' : 'text-slate-500'}`}>
                      {selected}
                    </span>
                    <button
                      onClick={() => setCardQuantity(item.id, item.is_first_edition ?? false, Math.min(item.quantity, selected + 1))}
                      className="w-7 h-7 rounded-lg bg-slate-800 border border-slate-700 text-slate-300 hover:text-white text-sm font-black transition-all cursor-pointer"
                    >
                      +
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Recycle button */}
        {selectedCount > 0 && (
          <div className="mt-4 flex items-center justify-between bg-emerald-950/20 border border-emerald-500/20 rounded-2xl p-4">
            <div className="text-sm">
              <span className="text-slate-400 text-xs">Total: </span>
              <span className="text-white font-black">{selectedCount} cartas</span>
              <span className="text-slate-400 text-xs"> → </span>
              <span className="text-emerald-400 font-black">+{selectedTickets} Tickets 🎫</span>
            </div>
            <button
              onClick={handleRecycle}
              disabled={recycling}
              className="px-6 py-2.5 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 disabled:opacity-50 text-white text-xs font-black rounded-xl uppercase tracking-widest transition-all hover:shadow-[0_0_20px_rgba(45,212,191,0.5)] shadow-lg active:scale-[0.98] flex items-center gap-2 cursor-pointer"
            >
              {recycling ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Reciclando...
                </>
              ) : (
                <>
                  <Trash2 size={14} />
                  Reciclar ({selectedCount})
                </>
              )}
            </button>
          </div>
        )}
      </div>

      {/* ── SECTION 2: SHOP — Canjear Tickets ── */}
      <div className="bg-slate-950/40 border border-white/5 rounded-3xl p-5">
        <div className="mb-4">
          <h3 className="text-sm font-black uppercase text-slate-300 tracking-wider flex items-center gap-2">
            <ShoppingCart size={16} className="text-teal-400" />
            Tienda del Reciclón
          </h3>
          <p className="text-[10px] text-slate-500 mt-0.5">
            Canjea tus Tickets por cartas específicas del catálogo
          </p>
        </div>

        {/* Search & Filter */}
        <div className="flex flex-col sm:flex-row gap-3 mb-5">
          <div className="flex-1 relative">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" size={16} />
            <input
              type="text"
              placeholder="Buscar carta..."
              value={shopSearch}
              onChange={(e) => setShopSearch(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 rounded-2xl bg-slate-900/60 border border-white/5 text-white placeholder-slate-500 text-xs font-semibold focus:outline-none focus:border-emerald-500/50 transition-colors"
            />
          </div>
          <div className="flex gap-1.5 overflow-x-auto">
            {[
              { key: 'all', label: 'Todas' },
              { key: 'common', label: '🟢 Comunes' },
              { key: 'rare', label: '🔷 Raras' },
              { key: 'epic', label: '✨ Épicas' },
              { key: 'legendary', label: '⭐ Legendarias' },
            ].map((filter) => (
              <button
                key={filter.key}
                onClick={() => setShopRarityFilter(filter.key as any)}
                className={`px-3 py-1.5 rounded-xl text-[10px] font-black uppercase tracking-wider whitespace-nowrap transition-all border cursor-pointer ${
                  shopRarityFilter === filter.key
                    ? 'bg-emerald-600/80 border-emerald-500/30 text-white shadow-md'
                    : 'bg-slate-900/35 border-white/5 text-slate-400 hover:text-white'
                }`}
              >
                {filter.label}
              </button>
            ))}
          </div>
        </div>

        {/* Card catalog grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-5 gap-4 max-h-[500px] overflow-y-auto pr-1">
          {allCards
            .filter((card) => {
              if (shopSearch && !card.name.toLowerCase().includes(shopSearch.toLowerCase())) return false;
              if (shopRarityFilter !== 'all' && card.rarity?.toLowerCase() !== shopRarityFilter) return false;
              return true;
            })
            .map((card) => {
              const rar = getRarityColor(card.rarity);
              const cost = REDEEM_COST[card.rarity?.toLowerCase()] || 999;
              const canAfford = ticketsBalance >= cost;
              const isRedeeming = redeeming.has(card.id);

              return (
                <div
                  key={card.id}
                  className="bg-slate-950/60 border border-white/5 hover:border-emerald-500/20 rounded-3xl p-3 flex flex-col justify-between items-center transition-all duration-300 group relative overflow-hidden"
                >
                  {/* Card image */}
                  <div className="relative w-full aspect-[3/4] rounded-2xl bg-slate-900/60 border border-white/5 overflow-hidden p-1 flex items-center justify-center mb-3">
                    <img
                      src={`${typeof window !== 'undefined' ? (window.location.hostname.endsWith('axolot.to') ? 'https://api.axolot.to' : window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' ? 'http://localhost:8001' : 'http://' + window.location.hostname + ':8001') : 'http://localhost:8001'}/api/v1/metadata/cards/${card.id}.jpg`}
                      alt={card.name}
                      className="w-full h-full object-cover rounded-xl"
                      onError={(e) => { (e.target as HTMLElement).style.display = 'none'; }}
                    />
                    <div className="absolute top-2 left-2 bg-black/60 px-1.5 py-0.5 rounded text-[8px] font-black text-slate-400 border border-white/5">
                      #{card.item_metadata?.numero_loteria || '?'}
                    </div>
                  </div>

                  {/* Name & rarity */}
                  <div className="w-full text-center space-y-1 mb-3">
                    <h4 className="text-[11px] font-black text-white uppercase tracking-tight leading-tight truncate">
                      {card.name}
                    </h4>
                    <span className={`inline-block text-[7px] font-black px-1.5 py-0.5 rounded border uppercase tracking-wider ${rar.color}`}>
                      {rar.label}
                    </span>

                    {/* Ticket cost */}
                    <div className="flex items-center justify-center gap-1.5 mt-1.5 bg-slate-900/40 rounded-lg py-1 px-2 border border-white/5">
                      <span className="text-[9px]">🎫</span>
                      <span className={`text-[10px] font-black ${canAfford ? 'text-emerald-400' : 'text-slate-500'}`}>
                        {cost} Tickets
                      </span>
                    </div>
                  </div>

                  {/* Redeem button */}
                  <button
                    onClick={() => handleRedeem(card.id)}
                    disabled={!canAfford || isRedeeming}
                    className={`w-full py-2 rounded-xl text-[9px] font-black uppercase tracking-wider transition-all flex items-center justify-center gap-1.5 ${
                      canAfford
                        ? 'bg-emerald-600 hover:bg-emerald-500 text-white cursor-pointer active:scale-95 hover:shadow-[0_0_10px_rgba(45,212,191,0.3)]'
                        : 'bg-slate-900 text-slate-500 border border-slate-800 cursor-not-allowed'
                    }`}
                  >
                    {isRedeeming ? (
                      <Loader2 className="w-3 h-3 animate-spin" />
                    ) : (
                      <>
                        <ShoppingCart size={10} />
                        Canjear
                      </>
                    )}
                  </button>
                </div>
              );
            })}
        </div>
      </div>
    </div>
  );
}
