"use client";
import { API_BASE } from "@/lib/api";



import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { Hammer, Sparkles, Coins, Flame, Info, Search, X, Loader2, ArrowRight, ChevronLeft } from 'lucide-react';
import LoteriaCard from '@/components/ui/LoteriaCard';
import { useToast } from '@/context/ToastContext';
import { useProductPolicy } from '@/hooks/useProductPolicy';



const API = `${API_BASE}`;

interface CardMelterProps {
  userId: string;
  token: string | null;
  recargarSaldos: () => void;
  balances: any;
  onBack?: () => void;
  onNavigateToMarket?: () => void;
  onMeltSuccess?: () => void;
}

export default function CardMelter({
  userId,
  token,
  recargarSaldos,
  balances,
  onBack,
  onNavigateToMarket,
  onMeltSuccess,
}: CardMelterProps) {
  const { toast } = useToast();
  const { capabilities } = useProductPolicy();
  const cardCraftingEnabled = capabilities.assets.card_crafting;
  const [subTab, setSubTab] = useState<'melt' | 'forge'>('melt');
  const [wallet, setWallet] = useState<any>(null);
  const [inventory, setInventory] = useState<any[]>([]);
  const [allCards, setAllCards] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // States for Melt
  const [selectedMeltCard, setSelectedMeltCard] = useState<any | null>(null);
  const [melting, setMelting] = useState(false);
  const [meltResult, setMeltResult] = useState<any | null>(null);

  // States for Forge
  const [selectedForgeCard, setSelectedForgeCard] = useState<any | null>(null);
  const [forging, setForging] = useState(false);
  const [forgeResult, setForgeResult] = useState<any | null>(null);
  const [forgeSearch, setForgeSearch] = useState('');
  const [forgeRarityFilter, setForgeRarityFilter] = useState<'all' | 'common' | 'rare' | 'epic' | 'legendary'>('all');

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
      console.error("Error loading melter data:", err);
      toast.error("Error al cargar datos del Cenote Místico");
    } finally {
      setLoading(false);
    }
  }, [userId, token, toast]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  useEffect(() => {
    if (!cardCraftingEnabled && subTab === 'forge') setSubTab('melt');
  }, [cardCraftingEnabled, subTab]);

  // Candidates for melting (Quantity >= 5 of the same card catalog id & first_edition status)
  const meltCandidates = React.useMemo(() => {
    // Filter inventory items that are cards and have quantity >= 5
    return inventory.filter(
      (item) => item.item_type === 'CARD' && item.quantity >= 5 && !item.is_shiny
    );
  }, [inventory]);

  const handleMelt = async () => {
    if (!token || !selectedMeltCard) return;
    setMelting(true);
    try {
      const headers = { Authorization: `Bearer ${token}` };
      const res = await axios.post(
        `${API}/shop/melter/melt`,
        {
          card_id: selectedMeltCard.id,
          is_first_edition: selectedMeltCard.is_first_edition,
        },
        { headers }
      );

      setMeltResult(res.data.new_card);
      // Update local wallet and inventory
      await loadData();
      recargarSaldos();
      setSelectedMeltCard(null);
      toast.ok("¡Carta fundida con éxito en el Cenote Místico! 🌌");
      onMeltSuccess?.();
    } catch (err: any) {
      console.error("Error melting card:", err);
      toast.error(err.response?.data?.detail || "Error al fundir la carta");
    } finally {
      setMelting(false);
    }
  };

  const handleForge = async (cardId: number) => {
    if (!cardCraftingEnabled || !token) return;
    setForging(true);
    try {
      const headers = { Authorization: `Bearer ${token}` };
      const res = await axios.post(
        `${API}/shop/melter/forge`,
        { target_card_id: cardId },
        { headers }
      );

      setForgeResult(res.data.forged_card);
      // Update local wallet and inventory
      await loadData();
      recargarSaldos();
      toast.ok("¡Carta forjada con éxito! 🔨");
    } catch (err: any) {
      console.error("Error forging card:", err);
      toast.error(err.response?.data?.detail || "Error al forjar la carta");
    } finally {
      setForging(false);
    }
  };

  const getRarityConfig = (rarity: string) => {
    switch (rarity?.toLowerCase()) {
      case 'legendary':
      case 'legendaria':
        return { label: 'Legendaria', fee: 3000, fragCost: 500, fragKey: 'legendarios', color: 'text-amber-400 border-amber-400/30 bg-amber-950/20 shadow-amber-500/20' };
      case 'epic':
      case 'épica':
        return { label: 'Épica', fee: 1000, fragCost: 250, fragKey: 'epicos', color: 'text-fuchsia-400 border-fuchsia-500/30 bg-fuchsia-950/20 shadow-fuchsia-500/20' };
      case 'rare':
      case 'rara':
        return { label: 'Rara', fee: 500, fragCost: 100, fragKey: 'raros', color: 'text-cyan-400 border-cyan-500/30 bg-cyan-950/20 shadow-cyan-500/20' };
      case 'common':
      case 'común':
      default:
        return { label: 'Común', fee: 100, fragCost: 50, fragKey: 'comunes', color: 'text-slate-300 border-slate-500/30 bg-slate-900/40 shadow-slate-500/10' };
    }
  };

  const getNextRarity = (rarity: string) => {
    switch (rarity?.toLowerCase()) {
      case 'common':
      case 'común':
        return { name: 'Rara 🔷', color: 'text-cyan-400' };
      case 'rare':
      case 'rara':
        return { name: 'Épica ✨', color: 'text-fuchsia-400' };
      case 'epic':
      case 'épica':
        return { name: 'Legendaria ⭐', color: 'text-amber-400' };
      default:
        return { name: 'Desconocido', color: 'text-slate-400' };
    }
  };

  if (loading && !wallet) {
    return (
      <div className="flex flex-col items-center justify-center py-20 gap-4">
        <Loader2 className="w-10 h-10 text-purple-500 animate-spin" />
        <p className="text-slate-400 text-xs font-black uppercase tracking-widest animate-pulse">
          Accediendo al Cenote Místico...
        </p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6 max-w-4xl mx-auto">
      {/* --- BACK BUTTON + TITLE --- */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => onBack?.()}
          className="w-10 h-10 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-purple-500/30 flex items-center justify-center text-slate-400 hover:text-white active:scale-95 transition-all cursor-pointer shadow-md"
          title="Volver al Tianguis"
        >
          <ChevronLeft size={20} />
        </button>
        <div className="text-center flex-1">
          <h2 className="text-2xl sm:text-3xl font-extrabold italic text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400 tracking-tighter uppercase drop-shadow-[0_0_12px_rgba(168,85,247,0.4)]">
            EL CENOTE MÍSTICO
          </h2>
          <p className="text-[9px] sm:text-[10px] text-slate-500 tracking-widest mt-0.5 uppercase font-black">
            Fusión y Forja de Cartas
          </p>
        </div>
        {/* Spacer to balance the back button */}
        <div className="w-10 h-10" />
      </div>

      {/* --- TOP HEADER BAR: FRAGMENTS & BALANCES --- */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 bg-slate-950/60 border border-purple-500/20 rounded-3xl p-4 shadow-[0_0_20px_rgba(147,51,234,0.05)]">
        <div className="flex flex-col items-center justify-center p-2 rounded-2xl bg-slate-900/40 border border-white/5">
          <span className="text-[8px] font-black text-slate-500 uppercase tracking-widest mb-0.5">Saldo FRJ</span>
          <div className="flex items-center gap-1">
            <Coins className="w-3.5 h-3.5 text-yellow-500" />
            <span className="text-sm font-black text-white">{wallet?.frijolitos?.toFixed(1) || 0}</span>
          </div>
        </div>
        <div className="flex flex-col items-center justify-center p-2 rounded-2xl bg-slate-900/40 border border-slate-650/10">
          <span className="text-[8px] font-black text-slate-500 uppercase tracking-widest mb-0.5">Frags Comunes</span>
          <div className="flex items-center gap-1.5">
            <span className="text-xs">🟢</span>
            <span className="text-sm font-black text-slate-300">{wallet?.fragmentos?.comunes || 0}</span>
          </div>
        </div>
        <div className="flex flex-col items-center justify-center p-2 rounded-2xl bg-slate-900/40 border border-slate-650/10">
          <span className="text-[8px] font-black text-slate-500 uppercase tracking-widest mb-0.5">Frags Raros</span>
          <div className="flex items-center gap-1.5">
            <span className="text-xs">🔷</span>
            <span className="text-sm font-black text-cyan-400">{wallet?.fragmentos?.raros || 0}</span>
          </div>
        </div>
        <div className="flex flex-col items-center justify-center p-2 rounded-2xl bg-slate-900/40 border border-slate-650/10">
          <span className="text-[8px] font-black text-slate-500 uppercase tracking-widest mb-0.5">Frags Épicos</span>
          <div className="flex items-center gap-1.5">
            <span className="text-xs">✨</span>
            <span className="text-sm font-black text-fuchsia-400">{wallet?.fragmentos?.epicos || 0}</span>
          </div>
        </div>
        <div className="col-span-2 sm:col-span-1 flex flex-col items-center justify-center p-2 rounded-2xl bg-slate-900/40 border border-slate-650/10">
          <span className="text-[8px] font-black text-slate-500 uppercase tracking-widest mb-0.5">Frags Legendarios</span>
          <div className="flex items-center gap-1.5">
            <span className="text-xs">⭐</span>
            <span className="text-sm font-black text-amber-400">{wallet?.fragmentos?.legendarios || 0}</span>
          </div>
        </div>
      </div>

      {/* --- SUB-TABS SELECTOR --- */}
      <div className="flex gap-2 p-1.5 bg-slate-950/80 border border-purple-500/20 rounded-2xl self-center">
        <button
          onClick={() => { setSubTab('melt'); setSelectedForgeCard(null); }}
          className={`px-5 py-2 rounded-xl text-xs font-black uppercase tracking-wider transition-all flex items-center gap-2 cursor-pointer ${
            subTab === 'melt'
              ? 'bg-purple-600 text-white shadow-[0_0_12px_rgba(147,51,234,0.5)]'
              : 'text-slate-400 hover:text-white'
          }`}
        >
          <Flame size={14} className={subTab === 'melt' ? 'animate-pulse' : ''} />
          Fundidor de Cartas
        </button>
        {cardCraftingEnabled && <button
          onClick={() => { setSubTab('forge'); setSelectedMeltCard(null); }}
          className={`px-5 py-2 rounded-xl text-xs font-black uppercase tracking-wider transition-all flex items-center gap-2 cursor-pointer ${
            subTab === 'forge'
              ? 'bg-purple-600 text-white shadow-[0_0_12px_rgba(147,51,234,0.5)]'
              : 'text-slate-400 hover:text-white'
          }`}
        >
          <Hammer size={14} />
          Forjar Cartas
        </button>}
      </div>

      {/* ──────────────────────────────────────────────────────── */}
      {/* SUBTAB: MELT (FUNDIDOR ALTAR) */}
      {/* ──────────────────────────────────────────────────────── */}
      {subTab === 'melt' && (
        <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-start">
          {/* Candidates Inventory Selection */}
          <div className="md:col-span-5 flex flex-col bg-slate-950/40 border border-white/5 rounded-3xl p-5 h-[500px]">
            <h3 className="text-xs font-black uppercase text-slate-400 tracking-wider mb-3">
              Duplicadas Disponibles (min. 5)
            </h3>
            {meltCandidates.length === 0 ? (
              <div className="flex-1 flex flex-col items-center justify-center p-6 text-center">
                <span className="text-3xl mb-2">🃏</span>
                <p className="text-slate-500 text-xs font-semibold">
                  No tienes ninguna carta repetida 5 o más veces de la misma edición.
                </p>
                <p className="text-[10px] text-slate-600 mt-1">
                  ¡Abre más sobres en el Tianguis para conseguir duplicadas!
                </p>
              </div>
            ) : (
              <div className="flex-1 overflow-y-auto pr-1 space-y-2.5">
                {meltCandidates.map((item) => {
                  const isSelected = selectedMeltCard?.id === item.id && selectedMeltCard?.is_first_edition === item.is_first_edition;
                  const rar = getRarityConfig(item.rarity);
                  return (
                    <button
                      key={`${item.id}-${item.is_first_edition}`}
                      onClick={() => setSelectedMeltCard(item)}
                      className={`w-full text-left p-3.5 rounded-2xl border transition-all flex items-center justify-between cursor-pointer ${
                        isSelected
                          ? 'bg-purple-950/20 border-purple-500 shadow-[0_0_15px_rgba(147,51,234,0.2)]'
                          : 'bg-slate-900/30 border-white/5 hover:border-white/10 hover:bg-slate-900/50'
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-14 bg-slate-950 rounded-lg flex items-center justify-center border border-white/10 overflow-hidden relative p-0.5">
                          <img
                            src={`${typeof window !== 'undefined' ? (window.location.hostname.endsWith('axolot.to') ? 'https://api.axolot.to' + '/api/v1' : (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' ? 'http://localhost:8001' + '/api/v1' : 'http://' + window.location.hostname + ':8001' + '/api/v1')) : 'http://localhost:8001' + '/api/v1'}/metadata/cards/${item.id}.jpg`}
                            alt={item.name}
                            className="w-full h-full object-cover"
                            onError={(e) => {
                              (e.target as HTMLElement).style.display = 'none';
                            }}
                          />
                          <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent"></div>
                          <span className="absolute bottom-0.5 left-0.5 text-[8px] font-black text-white">
                            #{item.item_metadata?.numero_loteria || '?'}
                          </span>
                        </div>
                        <div>
                          <h4 className="text-xs font-black text-white uppercase tracking-tight leading-tight">
                            {item.name}
                          </h4>
                          <div className="flex items-center gap-1.5 mt-1">
                            <span className={`text-[8px] font-extrabold px-1.5 py-0.5 rounded border uppercase tracking-wider ${rar.color}`}>
                              {rar.label}
                            </span>
                            {item.is_first_edition && (
                              <span className="text-[7px] font-black bg-amber-500/10 text-amber-400 border border-amber-500/20 px-1 py-0.5 rounded">
                                1ra Ed
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <span className="text-xs font-black text-purple-400 bg-purple-950/40 px-2.5 py-1 rounded-full border border-purple-500/20">
                          {item.quantity} copias
                        </span>
                      </div>
                    </button>
                  );
                })}
              </div>
            )}
          </div>

          {/* The Mystical Cenote Altar */}
          <div className="md:col-span-7 flex flex-col items-center justify-between bg-slate-950/40 border border-white/5 rounded-3xl p-6 h-[500px] relative overflow-hidden shadow-inner">
            <div className="absolute inset-0 bg-gradient-to-b from-purple-500/5 via-transparent to-pink-500/5 pointer-events-none" />

            {/* Title / Description */}
            <div className="text-center relative z-10">
              <h3 className="text-lg font-black italic text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400 uppercase tracking-wide">
                Cenote Místico de Fusión
              </h3>
              <p className="text-[10px] text-slate-400 uppercase tracking-widest mt-0.5">
                Funde 5 cartas duplicadas y desata su esencia
              </p>
            </div>

            {/* Altar Slots View */}
            <div className="relative w-64 h-64 flex items-center justify-center my-4 z-10">
              {/* Central Glowing Cenote Pool */}
              <div className="absolute w-28 h-28 rounded-full bg-gradient-to-tr from-purple-600/30 to-pink-600/30 border border-purple-500/40 flex flex-col items-center justify-center shadow-[0_0_40px_rgba(168,85,247,0.3)] animate-pulse">
                <span className="text-2xl animate-spin-slow">🌌</span>
                <span className="text-[8px] font-black text-purple-300 uppercase tracking-widest mt-1">CENOTE</span>
              </div>

              {/* Orbiting slots (Trig Position) */}
              {[0, 72, 144, 216, 288].map((angle, index) => {
                const radius = 95; // px
                const rad = (angle * Math.PI) / 180;
                const x = Math.round(radius * Math.sin(rad));
                const y = Math.round(-radius * Math.cos(rad));

                return (
                  <div
                    key={angle}
                    className="absolute w-12 h-16 rounded-xl border border-dashed border-purple-500/30 bg-slate-900/60 flex items-center justify-center overflow-hidden transition-all duration-500"
                    style={{
                      transform: `translate(${x}px, ${y}px)`,
                      boxShadow: selectedMeltCard ? '0 0 15px rgba(168,85,247,0.15)' : 'none',
                    }}
                  >
                    {selectedMeltCard ? (
                      <div className="w-full h-full p-0.5 relative group animate-float-up" style={{ animationDelay: `${index * 150}ms` }}>
                        <img
                          src={`${typeof window !== 'undefined' ? (window.location.hostname.endsWith('axolot.to') ? 'https://api.axolot.to' + '/api/v1' : (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' ? 'http://localhost:8001' + '/api/v1' : 'http://' + window.location.hostname + ':8001' + '/api/v1')) : 'http://localhost:8001' + '/api/v1'}/metadata/cards/${selectedMeltCard.id}.jpg`}
                          alt={selectedMeltCard.name}
                          className="w-full h-full object-cover rounded-lg"
                        />
                        <div className="absolute inset-0 bg-purple-950/20"></div>
                      </div>
                    ) : (
                      <span className="text-[10px] text-purple-500/40 font-bold">Slot</span>
                    )}
                  </div>
                );
              })}
            </div>

            {/* Melt Actions Panel */}
            <div className="w-full space-y-4 relative z-10 text-center">
              {selectedMeltCard ? (
                <>
                  {/* Cost & Output details */}
                  <div className="flex flex-col items-center gap-1.5">
                    <div className="flex items-center gap-6 justify-center">
                      <div className="flex flex-col items-center bg-slate-900/80 px-4 py-1.5 rounded-2xl border border-white/5 shadow-md">
                        <span className="text-[8px] font-black text-slate-500 uppercase tracking-widest mb-0.5">Costo de Fusión</span>
                        <div className="flex items-center gap-1 text-sm font-black text-yellow-400">
                          <Coins className="w-3.5 h-3.5" />
                          <span>{getRarityConfig(selectedMeltCard.rarity).fee} FRJ</span>
                        </div>
                      </div>

                      <ArrowRight className="text-slate-500" size={16} />

                      <div className="flex flex-col items-center bg-slate-900/80 px-4 py-1.5 rounded-2xl border border-white/5 shadow-md">
                        <span className="text-[8px] font-black text-slate-500 uppercase tracking-widest mb-0.5">Esencia de Retorno</span>
                        <div className="flex flex-col items-center gap-0.5 text-xs font-black">
                          <span className="text-emerald-400">+10 Fragmentos {selectedMeltCard.rarity.toUpperCase()}</span>
                          <span className="text-purple-300">
                            y 1 Carta <span className={getNextRarity(selectedMeltCard.rarity).color}>{getNextRarity(selectedMeltCard.rarity).name}</span>
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <button
                    onClick={handleMelt}
                    disabled={melting}
                    className="w-full py-3.5 bg-gradient-to-r from-purple-600 via-pink-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 disabled:opacity-50 text-white text-xs font-black rounded-2xl uppercase tracking-widest transition-all hover:shadow-[0_0_25px_rgba(168,85,247,0.6)] shadow-lg active:scale-[0.98] flex items-center justify-center gap-2 cursor-pointer"
                  >
                    {melting ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        Canalizando Energía...
                      </>
                    ) : (
                      <>
                        <Flame size={16} className="animate-pulse" />
                        Fundir en el Cenote 🌌
                      </>
                    )}
                  </button>
                </>
              ) : (
                <div className="py-5 text-slate-500 text-xs font-bold uppercase tracking-wider border border-dashed border-white/5 rounded-2xl bg-slate-900/10">
                  Selecciona una carta del inventario para iniciar el altar
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* ──────────────────────────────────────────────────────── */}
      {/* SUBTAB: FORGE (FORJA) */}
      {/* ──────────────────────────────────────────────────────── */}
      {cardCraftingEnabled && subTab === 'forge' && (
        <div className="flex flex-col gap-5">
          {/* Search & Filter Bar */}
          <div className="flex flex-col sm:flex-row gap-3 bg-slate-950/40 border border-white/5 rounded-3xl p-4 shadow-sm items-center">
            <div className="flex-1 w-full relative">
              <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" size={16} />
              <input
                type="text"
                placeholder="Buscar carta para forjar..."
                value={forgeSearch}
                onChange={(e) => setForgeSearch(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 rounded-2xl bg-slate-900/60 border border-white/5 text-white placeholder-slate-500 text-xs font-semibold focus:outline-none focus:border-purple-500/50 transition-colors"
              />
            </div>
            <div className="flex gap-1.5 overflow-x-auto w-full sm:w-auto">
              {[
                { key: 'all', label: 'Todas' },
                { key: 'common', label: '🟢 Comunes' },
                { key: 'rare', label: '🔷 Raras' },
                { key: 'epic', label: '✨ Épicas' },
                { key: 'legendary', label: '⭐ Legendarias' },
              ].map((filter) => (
                <button
                  key={filter.key}
                  onClick={() => setForgeRarityFilter(filter.key as any)}
                  className={`px-3 py-1.5 rounded-xl text-[10px] font-black uppercase tracking-wider whitespace-nowrap transition-all border cursor-pointer ${
                    forgeRarityFilter === filter.key
                      ? 'bg-purple-600/80 border-purple-500/30 text-white shadow-md'
                      : 'bg-slate-900/35 border-white/5 text-slate-400 hover:text-white'
                  }`}
                >
                  {filter.label}
                </button>
              ))}
            </div>
          </div>

          {/* Cards Catalog Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-5 gap-4">
            {allCards
              .filter((card) => {
                if (forgeSearch && !card.name.toLowerCase().includes(forgeSearch.toLowerCase())) return false;
                if (forgeRarityFilter !== 'all' && card.rarity?.toLowerCase() !== forgeRarityFilter) return false;
                return true;
              })
              .map((card) => {
                const isOwned = inventory.some((item) => item.id === card.id);
                const rConfig = getRarityConfig(card.rarity);
                const fragBalance = wallet?.fragmentos?.[rConfig.fragKey] || 0;
                const canAfford = fragBalance >= rConfig.fragCost && wallet?.frijolitos >= rConfig.fee;

                return (
                  <div
                    key={card.id}
                    className="bg-slate-950/60 border border-white/5 hover:border-purple-500/20 rounded-3xl p-3 flex flex-col justify-between items-center transition-all duration-300 hover:scale-105 group relative overflow-hidden"
                  >
                    {/* Catalog Image */}
                    <div className="relative w-full aspect-[3/4] rounded-2xl bg-slate-900/60 border border-white/5 overflow-hidden p-1 flex items-center justify-center mb-3">
                      <img
                        src={`${typeof window !== 'undefined' ? (window.location.hostname.endsWith('axolot.to') ? 'https://api.axolot.to' + '/api/v1' : (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' ? 'http://localhost:8001' + '/api/v1' : 'http://' + window.location.hostname + ':8001' + '/api/v1')) : 'http://localhost:8001' + '/api/v1'}/metadata/cards/${card.id}.jpg`}
                        alt={card.name}
                        className="w-full h-full object-cover rounded-xl"
                      />
                      <div className="absolute top-2 left-2 bg-black/60 px-1.5 py-0.5 rounded text-[8px] font-black text-slate-400 border border-white/5">
                        #{card.item_metadata?.numero_loteria || '?'}
                      </div>
                      {isOwned && (
                        <div className="absolute top-2 right-2 bg-emerald-500/20 border border-emerald-500/30 text-emerald-400 px-1.5 py-0.5 rounded text-[7px] font-black uppercase tracking-wider">
                          Posees ✓
                        </div>
                      )}
                    </div>

                    {/* Metadata & Requirements */}
                    <div className="w-full text-center space-y-1 mb-3">
                      <h4 className="text-[11px] font-black text-white uppercase tracking-tight leading-tight truncate px-1">
                        {card.name}
                      </h4>
                      <span className={`inline-block text-[7px] font-black px-1.5 py-0.5 rounded border uppercase tracking-wider ${rConfig.color}`}>
                        {rConfig.label}
                      </span>

                      {/* Forge Cost Requirements */}
                      <div className="bg-slate-900/40 rounded-xl p-1.5 border border-white/5 space-y-1 mt-2 text-left">
                        <div className="flex justify-between text-[8px] font-bold">
                          <span className="text-slate-500">Frags Req:</span>
                          <span className={fragBalance >= rConfig.fragCost ? 'text-emerald-400' : 'text-rose-400'}>
                            {fragBalance} / {rConfig.fragCost}
                          </span>
                        </div>
                        <div className="flex justify-between text-[8px] font-bold">
                          <span className="text-slate-500">FRJ Cost:</span>
                          <span className={wallet?.frijolitos >= rConfig.fee ? 'text-yellow-400' : 'text-rose-400'}>
                            {rConfig.fee}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Action Button */}
                    <button
                      onClick={() => handleForge(card.id)}
                      disabled={forging || !canAfford}
                      className={`w-full py-2 rounded-xl text-[9px] font-black uppercase tracking-wider transition-all flex items-center justify-center gap-1.5 ${
                        canAfford
                          ? 'bg-purple-600 hover:bg-purple-500 text-white cursor-pointer active:scale-95 hover:shadow-[0_0_10px_rgba(147,51,234,0.3)]'
                          : 'bg-slate-900 text-slate-500 border border-slate-800 cursor-not-allowed'
                      }`}
                    >
                      {forging ? (
                        <Loader2 className="w-3 h-3 animate-spin" />
                      ) : (
                        <>
                          <Hammer size={10} />
                          Forjar
                        </>
                      )}
                    </button>
                  </div>
                );
              })}
          </div>
        </div>
      )}

      {/* ──────────────────────────────────────────────────────── */}
      {/* CELEBRATION MODALS */}
      {/* ──────────────────────────────────────────────────────── */}
      {/* MELT FUSION SUCCESS CELEBRATION */}
      {meltResult && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/90 backdrop-blur-xl p-4 overflow-y-auto animate-in fade-in duration-300">
          <div className="bg-slate-950 border-4 border-purple-500/50 rounded-[3rem] p-6 max-w-sm w-full text-center shadow-[0_0_50px_rgba(147,51,234,0.4)] relative">
            <div className="absolute inset-0 bg-gradient-to-b from-purple-500/10 to-pink-500/10 pointer-events-none"></div>

            <span className="text-4xl animate-bounce inline-block mb-3">🔮</span>
            <h2 className="text-2xl font-black italic text-white uppercase tracking-tight mb-1">
              ¡Fusión Completada!
            </h2>
            <p className="text-[9px] text-slate-400 uppercase tracking-widest mb-6">
              El Cenote Místico ha entregado una nueva carta
            </p>

            {/* Glowing Card Preview */}
            <div className="relative w-44 aspect-[3/4] mx-auto mb-6 bg-slate-900/60 rounded-3xl border border-purple-500/50 flex items-center justify-center p-1.5 shadow-[0_0_30px_rgba(168,85,247,0.3)]">
              <img
                src={`${typeof window !== 'undefined' ? (window.location.hostname.endsWith('axolot.to') ? 'https://api.axolot.to' + '/api/v1' : (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' ? 'http://localhost:8001' + '/api/v1' : 'http://' + window.location.hostname + ':8001' + '/api/v1')) : 'http://localhost:8001' + '/api/v1'}/metadata/cards/${meltResult.id}.jpg`}
                alt={meltResult.name}
                className="w-full h-full object-cover rounded-2xl"
              />
              <div className="absolute top-3 left-3 bg-black/60 px-1.5 py-0.5 rounded text-[8px] font-black text-slate-400 border border-white/5">
                #{meltResult.item_metadata?.numero_loteria || '?'}
              </div>
            </div>

            <h3 className="text-base font-black text-white uppercase tracking-tight leading-tight mb-1">
              {meltResult.name}
            </h3>
            <span className={`inline-block text-[8px] font-black px-2 py-0.5 rounded border uppercase tracking-wider mb-6 ${getRarityConfig(meltResult.rarity).color}`}>
              {getRarityConfig(meltResult.rarity).label}
            </span>

            <button
              onClick={() => setMeltResult(null)}
              className="w-full py-3 bg-purple-600 hover:bg-purple-500 text-white text-xs font-black rounded-xl uppercase tracking-widest transition-all cursor-pointer shadow-md"
            >
              Reclamar Carta
            </button>
          </div>
        </div>
      )}

      {/* FORGE SUCCESS CELEBRATION */}
      {forgeResult && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/90 backdrop-blur-xl p-4 overflow-y-auto animate-in fade-in duration-300">
          <div className="bg-slate-950 border-4 border-emerald-500/50 rounded-[3rem] p-6 max-w-sm w-full text-center shadow-[0_0_50px_rgba(16,185,129,0.4)] relative">
            <div className="absolute inset-0 bg-gradient-to-b from-emerald-500/10 to-teal-500/10 pointer-events-none"></div>

            <span className="text-4xl animate-bounce inline-block mb-3">🔨</span>
            <h2 className="text-2xl font-black italic text-white uppercase tracking-tight mb-1">
              ¡Carta Forjada!
            </h2>
            <p className="text-[9px] text-slate-400 uppercase tracking-widest mb-6">
              Has moldeado una nueva carta en la forja
            </p>

            {/* Glowing Card Preview */}
            <div className="relative w-44 aspect-[3/4] mx-auto mb-6 bg-slate-900/60 rounded-3xl border border-emerald-500/50 flex items-center justify-center p-1.5 shadow-[0_0_30px_rgba(16,185,129,0.3)]">
              <img
                src={`${typeof window !== 'undefined' ? (window.location.hostname.endsWith('axolot.to') ? 'https://api.axolot.to' + '/api/v1' : (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' ? 'http://localhost:8001' + '/api/v1' : 'http://' + window.location.hostname + ':8001' + '/api/v1')) : 'http://localhost:8001' + '/api/v1'}/metadata/cards/${forgeResult.id}.jpg`}
                alt={forgeResult.name}
                className="w-full h-full object-cover rounded-2xl"
              />
              <div className="absolute top-3 left-3 bg-black/60 px-1.5 py-0.5 rounded text-[8px] font-black text-slate-400 border border-white/5">
                #{forgeResult.item_metadata?.numero_loteria || '?'}
              </div>
            </div>

            <h3 className="text-base font-black text-white uppercase tracking-tight leading-tight mb-1">
              {forgeResult.name}
            </h3>
            <span className={`inline-block text-[8px] font-black px-2 py-0.5 rounded border uppercase tracking-wider mb-6 ${getRarityConfig(forgeResult.rarity).color}`}>
              {getRarityConfig(forgeResult.rarity).label}
            </span>

            <button
              onClick={() => setForgeResult(null)}
              className="w-full py-3 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-black rounded-xl uppercase tracking-widest transition-all cursor-pointer shadow-md"
            >
              Reclamar Carta
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
