"use client";
import React, { useState, useEffect } from 'react';
import { X, Zap, Crown, Package, Plus } from 'lucide-react';
import { useToast } from '@/context/ToastContext';
import { CaveData, InventoryItem } from '@/types/santuario';
import { rarityColor, rarityClass, statNames, statColors, traitNames } from '@/constants/santuario';
import { fetchCaveData, fetchInventory, equipCaveItem, unequipCaveItem } from '@/services/santuarioService';
import { API_BASE } from '@/lib/api';

const API = `${API_BASE}`;

interface CaveRoomModalProps {
  axo: any;
  token: string | null;
  userId: string;
  onClose: () => void;
}

export default function CaveRoomModal({ axo, token, userId, onClose }: CaveRoomModalProps) {
  const { toast } = useToast();
  const headers = token ? { Authorization: `Bearer ${token}` } : {};

  const [caveData,    setCaveData]    = useState<CaveData | null>(null);
  const [loadingCave, setLoadingCave] = useState(false);
  const [inventory,   setInventory]   = useState<InventoryItem[]>([]);
  const [loadingInv,  setLoadingInv]  = useState(false);
  const [pickerSlot,  setPickerSlot]  = useState<number | null>(null);
  const [actioningId, setActioningId] = useState<number | null>(null);
  const [isClosing, setIsClosing] = useState(false);

  const loadCaveData = async () => {
    setLoadingCave(true);
    try {
      const data = await fetchCaveData(axo.id, token);
      setCaveData(data);
    } catch (e) {
      console.error('Error loading cave data:', e);
    } finally {
      setLoadingCave(false);
    }
  };

  const loadInventory = async () => {
    setLoadingInv(true);
    try {
      const data = await fetchInventory(userId, token);
      setInventory(data || []);
    } catch (e) {
      console.error('Error loading inventory:', e);
    } finally {
      setLoadingInv(false);
    }
  };

  useEffect(() => {
    loadCaveData();
    loadInventory();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [axo.id]);

  const handleEquip = async (itemId: number) => {
    setActioningId(itemId);
    try {
      await equipCaveItem(axo.id, itemId, token);
      toast.ok('Objeto equipado en la cueva');
      setPickerSlot(null);
      await loadCaveData();
      await loadInventory();
    } catch (e: any) {
      toast.error(e.response?.data?.detail || 'Error al equipar');
    } finally {
      setActioningId(null);
    }
  };

  const handleUnequip = async (itemId: number) => {
    setActioningId(itemId);
    try {
      await unequipCaveItem(axo.id, itemId, token);
      toast.ok('Objeto desequipado');
      await loadCaveData();
      await loadInventory();
    } catch (e: any) {
      toast.error(e.response?.data?.detail || 'Error al desequipar');
    } finally {
      setActioningId(null);
    }
  };

  // Cave items in player inventory
  const caveInventoryItems = inventory.filter(item => {
    const meta = item.item_metadata ?? {};
    const type = (item.item_type ?? meta.category ?? meta.type ?? '').toString().toUpperCase();
    return type.includes('CAVE') || meta.cave_item === true;
  });

  // Already-equipped item IDs
  const equippedIds = new Set((caveData?.cave_items ?? []).map(i => i.id));

  const energyPct = Math.min(100, (axo.energy_current / (axo.stat_stamina || 100)) * 100);

  const handleClose = () => {
    setIsClosing(true);
    setTimeout(onClose, 280);
  };

  return (
    <>
      <style>{`
        @keyframes cave-zoom-in {
          0%   { opacity: 0; transform: scale(0.85); }
          100% { opacity: 1; transform: scale(1); }
        }
        @keyframes cave-zoom-out {
          0%   { opacity: 1; transform: scale(1); }
          100% { opacity: 0; transform: scale(0.85); }
        }
      `}</style>

      <div
        className="fixed inset-0 z-[120] flex flex-col overflow-hidden"
        style={{
          background: 'radial-gradient(ellipse at 50% 0%, #1a0a05 0%, #0a0702 40%, #050402 100%)',
          animation: isClosing ? 'cave-zoom-out 280ms ease-in forwards' : 'cave-zoom-in 320ms ease-out forwards',
        }}
      >
        {/* Stone texture overlay */}
        <div
          className="absolute inset-0 pointer-events-none opacity-[0.03]"
          style={{
            backgroundImage: `repeating-linear-gradient(
              45deg, #fff 0px, #fff 1px, transparent 0, transparent 50%
            )`,
            backgroundSize: '12px 12px',
          }}
        />

        {/* Top ambient glow */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-80 h-40 rounded-full blur-[60px] pointer-events-none"
          style={{ background: 'rgba(45,212,191,0.06)' }} />

        {/* Header bar */}
        <div className="relative z-10 flex items-center justify-between px-5 pb-3 border-b border-white/5" style={{ paddingTop: 'max(1rem, env(safe-area-inset-top))' }}>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl border border-white/10 bg-slate-900/60 flex items-center justify-center overflow-hidden p-1">
              <img
                src={`${API}/metadata/axolotito/${axo.blockchain_token_id}.svg`}
                alt={axo.name}
                className="w-full h-full object-contain"
              />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="text-[9px] font-black text-purple-400 border border-purple-500/30 bg-purple-950/40 px-2 py-0.5 rounded-full uppercase tracking-widest">
                  Nv. {axo.level}
                </span>
                {axo.is_main && (
                  <span className="text-[8px] font-black text-yellow-400 border border-yellow-500/30 bg-yellow-950/40 px-1.5 py-0.5 rounded-full flex items-center gap-0.5">
                    <Crown size={7} /> Principal
                  </span>
                )}
              </div>
              <h2 className="text-sm font-black text-white leading-tight">{axo.name}</h2>
            </div>
          </div>
          <button
            onClick={handleClose}
            className="p-2 rounded-full bg-slate-800/80 border border-white/8 text-slate-400 hover:text-white transition-colors active:scale-90"
            aria-label="Cerrar cueva"
          >
            <X size={16} />
          </button>
        </div>

        {/* Scrollable content */}
        <div className="relative z-10 flex-1 overflow-y-auto px-5 py-4 space-y-5">

          {/* Energy bar */}
          <div className="bg-slate-900/50 border border-white/6 rounded-2xl p-4">
            <div className="flex justify-between text-[8px] font-black text-slate-400 uppercase mb-1.5">
              <span className="flex items-center gap-1"><Zap size={8} /> Energía</span>
              <span className="text-green-400">{axo.energy_current} / {axo.stat_stamina}</span>
            </div>
            <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
              <div className="h-full bg-green-500 rounded-full transition-all" style={{ width: `${energyPct}%` }} />
            </div>
          </div>

          {/* Stats grid */}
          <div className="bg-slate-900/50 border border-white/6 rounded-2xl p-4">
            <div className="text-[9px] font-black text-slate-500 uppercase tracking-widest mb-3">Estadisticas</div>
            <div className="grid grid-cols-2 gap-x-4 gap-y-2.5">
              {(['luck','focus','stamina','salinity'] as const).map(key => {
                const val  = axo[`stat_${key}`] ?? 0;
                const maxV = key === 'stamina' ? 200 : 100;
                const pct  = Math.min(100, (val / maxV) * 100);
                const isSal = key === 'salinity';
                return (
                  <div key={key}>
                    <div className="flex justify-between text-[8px] font-black text-slate-500 uppercase mb-0.5">
                      <span>{statNames[key]}{isSal && <span className="ml-1 text-red-400 normal-case">↓ mejor</span>}</span>
                      <span className={isSal ? 'text-red-400' : 'text-white'}>
                        {Number.isInteger(val) ? val : val.toFixed(1)}
                      </span>
                    </div>
                    <div className="h-1.5 bg-slate-800 rounded-full overflow-hidden">
                      <div className={`h-full rounded-full transition-all duration-500 ${statColors[key] || 'bg-teal-500'}`}
                        style={{ width: `${pct}%` }} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Cave equipment section */}
          <div className="bg-slate-900/50 border border-white/6 rounded-2xl p-4">
            <div className="flex items-center justify-between mb-3">
              <div className="text-[9px] font-black text-[#2DD4BF] uppercase tracking-widest flex items-center gap-1.5">
                <Package size={10} /> Equipamiento de la Cueva
              </div>
              {loadingCave && (
                <span className="text-[8px] text-slate-500 animate-pulse">Cargando...</span>
              )}
            </div>

            {!loadingCave && caveData && (
              <div className="space-y-2">
                {Array.from({ length: caveData.max_slots }, (_, i) => {
                  const item = caveData.cave_items[i];
                  return (
                    <div key={i} className={`rounded-xl border p-3 flex items-center gap-3 transition-all ${
                      item
                        ? `${rarityClass(item.rarity)} border`
                        : 'bg-slate-800/30 border-dashed border-slate-700/50'
                    }`}>
                      {item ? (
                        <>
                          <div className="w-8 h-8 rounded-lg bg-black/30 border border-white/8 flex items-center justify-center text-base shrink-0">
                            {item.item_metadata?.emoji ?? '🪨'}
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="text-xs font-black text-white truncate">{item.name}</div>
                            {item.rarity && (
                              <div className={`text-[8px] font-black uppercase tracking-widest ${rarityClass(item.rarity).split(' ')[0]}`}>
                                {item.rarity}
                              </div>
                            )}
                          </div>
                          <button
                            onClick={() => handleUnequip(item.id)}
                            disabled={actioningId === item.id}
                            className="shrink-0 px-2.5 py-1 rounded-lg bg-slate-800 border border-slate-700 text-[8px] font-black text-slate-400 hover:text-rose-400 hover:border-rose-500/40 transition-colors uppercase tracking-widest disabled:opacity-50 active:scale-95"
                          >
                            {actioningId === item.id ? '...' : 'Quitar'}
                          </button>
                        </>
                      ) : (
                        <>
                          <div className="w-8 h-8 rounded-lg bg-slate-700/30 border border-dashed border-slate-600/50 flex items-center justify-center text-slate-600 shrink-0">
                            <Plus size={14} />
                          </div>
                          <div className="flex-1">
                            <div className="text-[10px] font-black text-slate-600 uppercase tracking-widest">Slot vacio</div>
                          </div>
                          <button
                            onClick={() => setPickerSlot(i)}
                            className="shrink-0 px-2.5 py-1 rounded-lg bg-teal-900/40 border border-teal-600/40 text-[8px] font-black text-teal-400 hover:bg-teal-800/50 transition-colors uppercase tracking-widest active:scale-95"
                          >
                            Equipar
                          </button>
                        </>
                      )}
                    </div>
                  );
                })}
              </div>
            )}

            {!loadingCave && !caveData && (
              <div className="text-center py-4 text-[10px] text-slate-600 font-bold uppercase tracking-widest">
                No hay datos de la cueva
              </div>
            )}
          </div>

          {/* Item picker for empty slot */}
          {pickerSlot !== null && (
            <div className="bg-slate-900/80 border border-teal-600/30 rounded-2xl p-4">
              <div className="flex items-center justify-between mb-3">
                <div className="text-[9px] font-black text-teal-400 uppercase tracking-widest">Elegir objeto</div>
                <button
                  onClick={() => setPickerSlot(null)}
                  className="text-slate-600 hover:text-slate-300 transition-colors"
                  aria-label="Cerrar selector"
                >
                  <X size={14} />
                </button>
              </div>

              {loadingInv ? (
                <div className="text-center py-3 text-[10px] text-slate-500 animate-pulse">Cargando inventario...</div>
              ) : caveInventoryItems.length === 0 ? (
                <div className="text-center py-4">
                  <div className="text-2xl mb-2">🪨</div>
                  <div className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">
                    No tienes objetos para la cueva
                  </div>
                  <div className="text-[9px] text-slate-600 mt-1">
                    Consigue objetos tipo CAVE en la tienda
                  </div>
                </div>
              ) : (
                <div className="space-y-1.5 max-h-48 overflow-y-auto">
                  {caveInventoryItems
                    .filter(item => {
                      const iid = item.id ?? item.item_id ?? -1;
                      return !equippedIds.has(iid);
                    })
                    .map(item => {
                      const iid = item.id ?? item.item_id ?? -1;
                      return (
                        <button
                          key={iid}
                          onClick={() => handleEquip(iid)}
                          disabled={actioningId === iid}
                          className={`w-full flex items-center gap-3 p-2.5 rounded-xl border transition-all active:scale-95 disabled:opacity-50 ${rarityClass(item.rarity)}`}
                        >
                          <div className="w-7 h-7 rounded-lg bg-black/30 flex items-center justify-center text-sm shrink-0">
                            {item.item_metadata?.emoji ?? '🪨'}
                          </div>
                          <div className="flex-1 text-left min-w-0">
                            <div className="text-xs font-black text-white truncate">{item.name ?? `Objeto #${iid}`}</div>
                            {item.rarity && (
                              <div className={`text-[7px] font-black uppercase tracking-widest ${rarityClass(item.rarity).split(' ')[0]}`}>
                                {item.rarity}
                              </div>
                            )}
                          </div>
                          <span className="shrink-0 text-[8px] font-black text-teal-400 uppercase tracking-widest">
                            {actioningId === iid ? '...' : 'Equipar'}
                          </span>
                        </button>
                      );
                    })}
                </div>
              )}
            </div>
          )}

          {/* Traits */}
          {axo.traits && Object.keys(axo.traits).length > 0 && (
            <div className="bg-slate-900/50 border border-white/6 rounded-2xl p-4">
              <div className="text-[9px] font-black text-slate-500 uppercase tracking-widest mb-2">Rasgos fisicos</div>
              <div className="flex flex-wrap gap-1.5">
                {Object.entries(axo.traits).map(([key, val]: [string, any]) => (
                  <span key={key} className="text-[8px] font-bold text-pink-300 bg-pink-950/40 border border-pink-500/20 px-2 py-0.5 rounded-full uppercase tracking-wide">
                    {traitNames[key] ? `${traitNames[key]}: ` : ''}{String(val).replace(/_/g, ' ')}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Bottom spacer for safe area */}
          <div className="h-6" />
        </div>
      </div>
    </>
  );
}
