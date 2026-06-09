'use client';
import { API_BASE } from "@/lib/api";
import { useState, useEffect, useCallback, useRef } from 'react';
import { RefreshCw, X } from 'lucide-react';
import axios from 'axios';
import BoardCardGrid from '@/components/ui/BoardCardGrid';
import HoldButton from '@/components/ui/HoldButton';
import { deriveBoardRarity, isBoardShiny } from '@/lib/boardRarity';

const API = `${API_BASE}`;
const PAGE_SIZE = 20;

type AssetFilter = 'all' | 'board' | 'axolotito' | 'booster' | 'card';
type ModeFilter  = 'all' | 'sale' | 'rent';
type SortKey     = 'price_asc' | 'price_desc';

interface MarketItem {
  key: string;
  itemType: 'board' | 'axolotito' | 'booster' | 'card';
  marketType: 'sale' | 'rent';
  id: number;
  name: string;
  ownerId: string;
  price: number;
  level: number;
  // board
  winRate?: number;
  gamesPlayed?: number;
  csr?: number;
  suerte_tag?: string;
  splitPct?: number;
  cardIds?: number[];
  // axolotito
  skinColor?: string;
  statLuck?: number;
  statFocus?: number;
  statStamina?: number;
  statSalinity?: number;
  blockchainTokenId?: number | null;
  ownerVipTier?: string | null;
  // inventory listing (booster / card)
  quantity?: number;
  isFirstEdition?: boolean;
  isShiny?: boolean;
  raw: any;
}

const SKIN_GRADIENT: Record<string, string> = {
  pink:    'from-pink-900 to-rose-800',
  blue:    'from-blue-900 to-indigo-800',
  golden:  'from-amber-800 to-yellow-700',
  purple:  'from-purple-900 to-violet-800',
  green:   'from-green-900 to-emerald-800',
  white:   'from-slate-600 to-slate-500',
  black:   'from-slate-900 to-slate-800',
  red:     'from-red-900 to-rose-800',
  orange:  'from-orange-800 to-amber-700',
  teal:    'from-teal-900 to-cyan-800',
};
const skinGradient = (color: string) =>
  SKIN_GRADIENT[color?.toLowerCase().split('_')[0]] ?? 'from-slate-800 to-slate-700';

export default function MarketP2P({ userId, token, recargarSaldos }: {
  userId: string;
  token: string | null;
  recargarSaldos: () => void;
}) {
  const [items,       setItems]       = useState<MarketItem[]>([]);
  const [loading,     setLoading]     = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [hasMore,     setHasMore]     = useState(true);
  const [error,       setError]       = useState<string | null>(null);
  const pageRef = useRef(0);
  const exhaustedRef = useRef<Set<string>>(new Set());
  const sentinelRef = useRef<HTMLDivElement | null>(null);
  const [assetFilter, setAssetFilter] = useState<AssetFilter>('all');
  const [modeFilter,  setModeFilter]  = useState<ModeFilter>('all');
  const [sort,        setSort]        = useState<SortKey>('price_asc');
  const [rarityFilter, setRarityFilter] = useState<'all' | 'common' | 'rare' | 'epic' | 'legendary'>('all');
  const [shinyFilter,  setShinyFilter]  = useState<'all' | 'shiny' | 'normal'>('all');
  const [confirmItem, setConfirmItem] = useState<MarketItem | null>(null);
  const [txLoading,   setTxLoading]   = useState(false);
  const [txMsg,       setTxMsg]       = useState<{ type: 'ok' | 'err'; text: string } | null>(null);
  const [allCards,    setAllCards]    = useState<any[]>([]);

  useEffect(() => {
    axios.get(`${API}/shop/cards`).then(r => setAllCards(r.data)).catch(() => {});
  }, []);

  /* ── data mappers ── */
  const mapBoardRent = (b: any): MarketItem => ({
    key: `board-rent-${b.id}`, itemType: 'board', marketType: 'rent',
    id: b.id, name: b.name, ownerId: b.owner_id, price: b.rent_fee_gal,
    level: b.level, winRate: b.win_rate, gamesPlayed: b.games_played,
    csr: b.csr, suerte_tag: b.suerte_tag, splitPct: b.rent_share_owner_pct,
    cardIds: b.card_ids, ownerVipTier: b.owner_vip_tier, raw: b,
  });
  const mapBoardSale = (b: any): MarketItem => ({
    key: `board-sale-${b.id}`, itemType: 'board', marketType: 'sale',
    id: b.id, name: b.name, ownerId: b.owner_id, price: b.sale_price_gal,
    level: b.level, winRate: b.win_rate, gamesPlayed: b.games_played,
    csr: b.csr, suerte_tag: b.suerte_tag, cardIds: b.card_ids, ownerVipTier: b.owner_vip_tier, raw: b,
  });
  const mapAxoRent = (a: any): MarketItem => ({
    key: `axo-rent-${a.id}`, itemType: 'axolotito', marketType: 'rent',
    id: a.id, name: a.name, ownerId: a.user_id, price: a.rent_fee_gal,
    level: a.level, skinColor: a.skin_color, statLuck: a.stat_luck,
    statFocus: a.stat_focus, statStamina: a.stat_stamina, statSalinity: a.stat_salinity,
    blockchainTokenId: a.blockchain_token_id, splitPct: a.rent_share_owner_pct, ownerVipTier: a.owner_vip_tier, raw: a,
  });
  const mapAxoSale = (a: any): MarketItem => ({
    key: `axo-sale-${a.id}`, itemType: 'axolotito', marketType: 'sale',
    id: a.id, name: a.name, ownerId: a.user_id, price: a.sale_price_gal,
    level: a.level, skinColor: a.skin_color, statLuck: a.stat_luck,
    statFocus: a.stat_focus, statStamina: a.stat_stamina, statSalinity: a.stat_salinity,
    blockchainTokenId: a.blockchain_token_id, ownerVipTier: a.owner_vip_tier, raw: a,
  });
  const mapInv = (l: any): MarketItem => ({
    key: `inv-${l.id}`,
    itemType: l.item.item_type.toLowerCase() as 'booster' | 'card',
    marketType: 'sale',
    id: l.id, name: l.item.name, ownerId: l.seller_id,
    price: l.price_gal, level: 1, quantity: l.quantity,
    isFirstEdition: l.is_first_edition, isShiny: l.is_shiny, raw: l,
  });

  const ENDPOINTS: [string, string, (d: any) => MarketItem][] = [
    ['br', `${API}/board/rent/market`,           mapBoardRent],
    ['bs', `${API}/board/sale/market`,           mapBoardSale],
    ['ar', `${API}/auth/axolotitos/market/rent`, mapAxoRent],
    ['as', `${API}/auth/axolotitos/market/sale`, mapAxoSale],
    ['inv',`${API}/market/inventory/listings`,   mapInv],
  ];

  /* ── fetch one page, accumulate ── */
  const loadPage = useCallback(async (page: number) => {
    const skip = page * PAGE_SIZE;
    const active = ENDPOINTS.filter(([key]) => !exhaustedRef.current.has(key));

    if (active.length === 0) {
      setHasMore(false);
      return;
    }

    const results = await Promise.all(
      active.map(([key, url, mapper]) =>
        axios.get(url, { params: { skip, limit: PAGE_SIZE } })
          .then(res => ({ key, items: res.data.map(mapper) }))
          .catch(() => ({ key, items: [] as MarketItem[] }))
      )
    );

    for (const { key, items: chunk } of results) {
      if (chunk.length < PAGE_SIZE) exhaustedRef.current.add(key);
    }

    if (ENDPOINTS.every(([key]) => exhaustedRef.current.has(key))) {
      setHasMore(false);
    }

    const merged = results.flatMap(r => r.items);
    setItems(prev => [...prev, ...merged]);
    return merged.length;
  }, []);

  /* ── reset + reload from page 0 ── */
  const resetAndReload = useCallback(async () => {
    setLoading(true);
    setError(null);
    setItems([]);
    setHasMore(true);
    pageRef.current = 0;
    exhaustedRef.current = new Set();
    try {
      const count = await loadPage(0);
      if (count === 0) setHasMore(false);
    } catch {
      setError('No se pudo cargar el mercado. Revisa tu conexión.');
    } finally {
      setLoading(false);
    }
  }, [loadPage]);

  /* ── load on mount + clear/reload on any filter change ── */
  const mountRef = useRef(true);
  useEffect(() => {
    if (mountRef.current) {
      mountRef.current = false;
      resetAndReload();
      return;
    }
    resetAndReload();
  }, [assetFilter, modeFilter, rarityFilter, shinyFilter]); // eslint-disable-line react-hooks/exhaustive-deps

  /* ── infinite scroll sentinel ── */
  useEffect(() => {
    const sentinel = sentinelRef.current;
    if (!sentinel) return;

    const observer = new IntersectionObserver(
      entries => {
        const [entry] = entries;
        if (entry.isIntersecting && hasMore && !loading && !loadingMore) {
          setLoadingMore(true);
          const nextPage = pageRef.current + 1;
          pageRef.current = nextPage;
          loadPage(nextPage).finally(() => setLoadingMore(false));
        }
      },
      { rootMargin: '200px' }
    );

    observer.observe(sentinel);
    return () => observer.disconnect();
  }, [hasMore, loading, loadingMore, loadPage]);

  const openConfirm = (item: MarketItem) => {
    setTxMsg(null);
    setConfirmItem(item);
  };

  const executeAction = async () => {
    if (!confirmItem || !token) return;
    setTxLoading(true);
    setTxMsg(null);
    const h = { Authorization: `Bearer ${token}` };
    const { itemType, marketType, id } = confirmItem;
    const isOwn = confirmItem.ownerId === userId;
    try {
      if (isOwn) {
        if (itemType === 'booster' || itemType === 'card') {
          await axios.post(`${API}/market/inventory/${id}/cancel`, {}, { headers: h });
        } else {
          const ep = itemType === 'board'
            ? (marketType === 'sale' ? `/board/${id}/cancel-sale` : `/board/${id}/cancel-rent`)
            : (marketType === 'sale' ? `/auth/axolotitos/${id}/cancel-sale` : `/auth/axolotitos/${id}/cancel-rent`);
          await axios.post(`${API}${ep}`, {}, { headers: h });
        }
        setTxMsg({ type: 'ok', text: 'Retirado del mercado.' });
      } else {
        if (itemType === 'booster' || itemType === 'card') {
          await axios.post(`${API}/market/inventory/${id}/buy`, {}, { headers: h });
        } else {
          const ep = itemType === 'board'
            ? (marketType === 'sale' ? `/board/${id}/buy` : `/board/${id}/rent`)
            : (marketType === 'sale' ? `/auth/axolotitos/${id}/buy` : `/auth/axolotitos/${id}/rent`);
          await axios.post(`${API}${ep}`, {}, { headers: h });
        }
        setTxMsg({ type: 'ok', text: `¡${confirmItem.name} comprado con éxito!` });
        recargarSaldos();
      }
      setConfirmItem(null);
      await resetAndReload();
    } catch (e: any) {
      setTxMsg({ type: 'err', text: e.response?.data?.detail || 'Error en la transacción.' });
    } finally {
      setTxLoading(false);
    }
  };

  const checkRarity = (i: MarketItem) => {
    if (rarityFilter === 'all') return true;
    const item = i.raw.item || i.raw;
    const r = (item?.dynamic_rarity || item?.rarity || '').toLowerCase();
    
    if (rarityFilter === 'common') return r.includes('común') || r === 'common';
    if (rarityFilter === 'rare') return r.includes('rara') || r === 'rare';
    if (rarityFilter === 'epic') return r.includes('épica') || r === 'epic';
    if (rarityFilter === 'legendary') return r.includes('legendaria') || r === 'legendary';
    return false;
  };

  const checkShiny = (i: MarketItem) => {
    if (shinyFilter === 'all') return true;
    const isFoilPack = i.itemType === 'booster' && i.name.toLowerCase().includes('foil');
    const isShinyCard = i.itemType === 'card' && i.isShiny;
    const isShiny = isFoilPack || isShinyCard;
    if (shinyFilter === 'shiny') return isShiny;
    if (shinyFilter === 'normal') return !isShiny;
    return true;
  };

  const filtered = items
    .filter(i => assetFilter === 'all' || i.itemType === assetFilter)
    .filter(i => modeFilter  === 'all' || i.marketType === modeFilter)
    .filter(checkRarity)
    .filter(checkShiny)
    .sort((a, b) => sort === 'price_asc' ? a.price - b.price : b.price - a.price);

  /* ── chips helpers ── */
  const chip = (active: boolean, label: string, onClick: () => void, color = '#2DD4BF') => (
    <button onClick={onClick}
      className="px-3 py-1.5 rounded-full font-black text-[10px] uppercase tracking-wider transition-all active:scale-95"
      style={active
        ? { background: `${color}20`, border: `1.5px solid ${color}60`, color }
        : { background: 'rgba(255,255,255,0.03)', border: '1.5px solid rgba(255,255,255,0.06)', color: '#6B7280' }}>
      {label}
    </button>
  );

  /* ── mini board grid ── */
  const MiniGrid = ({ cardIds }: { cardIds?: number[] }) => {
    const filled  = (cardIds || []).map((id, i) => id ? i : -1).filter(i => i >= 0);
    const rarity  = deriveBoardRarity(cardIds || [], allCards);
    const shiny   = isBoardShiny(cardIds || [], allCards);
    return (
      <BoardCardGrid
        boardNums={Array(16).fill(0)}
        cardSize={14}
        priorityLine={filled}
        frameRarity={rarity}
        isShiny={shiny}
      />
    );
  };

  /* ── single card ── */
  const Card = ({ item }: { item: MarketItem }) => {
    const isOwn   = item.ownerId === userId;
    const isBoard = item.itemType === 'board';
    const isAxo = item.itemType === 'axolotito';
    const isBooster = item.itemType === 'booster';
    const isCard = item.itemType === 'card';
    const isRent  = item.marketType === 'rent';

    const accentColor = isBoard ? '#2DD4BF' : isAxo ? '#E4007C' : isBooster ? '#A855F7' : '#F59E0B';
    const accentGlow  = isBoard ? 'rgba(45,212,191,0.15)' : isAxo ? 'rgba(228,0,124,0.15)' : isBooster ? 'rgba(168,85,247,0.15)' : 'rgba(245,158,11,0.15)';

    return (
      <div className="relative rounded-2xl border bg-[#0D0D1F] flex flex-col overflow-hidden transition-all duration-200 hover:brightness-110"
        style={{ borderColor: `${accentColor}22`, boxShadow: `0 0 20px ${accentGlow}` }}>

        {/* Holographic sweeping style if card is shiny */}
        <style jsx global>{`
          @keyframes shine-sweep-market {
            0% { background-position: -200% 0; }
            100% { background-position: 200% 0; }
          }
          .holo-overlay {
            position: absolute;
            inset: 0;
            background: linear-gradient(
              115deg,
              transparent 30%,
              rgba(255, 255, 255, 0.25) 45%,
              rgba(244, 114, 182, 0.3) 50%,
              rgba(192, 132, 252, 0.3) 55%,
              rgba(251, 191, 36, 0.25) 60%,
              transparent 75%
            );
            background-size: 200% 100%;
            animation: shine-sweep-market 4s infinite linear;
            pointer-events: none;
            mix-blend-mode: color-dodge;
            z-index: 10;
          }
        `}</style>

        {/* Corner Ribbon for VIP Owner */}
        {item.ownerVipTier && (
          <div className="absolute top-0 right-0 overflow-hidden w-16 h-16 pointer-events-none z-10">
            <div className={`absolute top-2.5 -right-6 w-20 py-0.5 text-[7px] font-black uppercase text-center rotate-45 text-black shadow-sm ${
              item.ownerVipTier === 'coral'
                ? 'bg-teal-400'
                : item.ownerVipTier === 'dorado'
                  ? 'bg-yellow-400'
                  : 'bg-gradient-to-r from-yellow-400 via-pink-400 to-purple-400'
            }`}>
              {item.ownerVipTier === 'coral' && '🪸'}
              {item.ownerVipTier === 'dorado' && '✨'}
              {item.ownerVipTier === 'axolite' && '🌟'}
            </div>
          </div>
        )}

        {/* top bar */}
        <div className="flex items-center justify-between px-3 pt-3 pb-2">
          <div className="flex items-center gap-1.5">
            <span className="text-base leading-none">
              {isBoard ? '📋' : isAxo ? '🦎' : isBooster ? '📦' : '🃏'}
            </span>
            <span className="text-[9px] font-black uppercase tracking-widest" style={{ color: accentColor }}>
              {isBoard ? 'Tablero' : isAxo ? 'Axolotito' : isBooster ? 'Sobre' : 'Carta'}
            </span>
            <span className="text-slate-700 text-[9px]">·</span>
            <span className="text-[9px] font-black uppercase tracking-widest"
              style={{ color: isRent ? '#A78BFA' : '#34D399' }}>
              {isRent ? '🤝 Renta' : '🛍️ Venta'}
            </span>
          </div>
          {isOwn && (
            <span className="text-[8px] font-black uppercase tracking-widest px-2 py-0.5 rounded-full"
              style={{ background: `${accentColor}15`, border: `1px solid ${accentColor}40`, color: accentColor }}>
              TUYO
            </span>
          )}
        </div>

        {/* body */}
        <div className="px-3 pb-3 flex flex-col gap-2 flex-1">
          <p className="text-[13px] font-black text-white leading-tight truncate">{item.name}</p>

          {isBoard && (
            <>
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-[9px] text-slate-500 font-bold">Nv.{item.level}</span>
                {item.suerte_tag && (
                  <span className="text-[9px] font-black px-1.5 py-px rounded border border-white/10 bg-white/5 text-slate-300">
                    {item.suerte_tag}
                  </span>
                )}
                <span className="text-[9px] text-slate-500 font-bold ml-auto">
                  {item.winRate?.toFixed(0)}% WR
                </span>
                <span className="text-[9px] text-slate-600">
                  {item.gamesPlayed} partidas
                </span>
              </div>
              <MiniGrid cardIds={item.cardIds} />
              {isRent && item.splitPct !== undefined && (
                <p className="text-[9px] text-slate-600 text-right">
                  Dueño recibe {item.splitPct}% de victorias
                </p>
              )}
            </>
          )}

          {isAxo && (
            <>
              <div className="flex items-center gap-3">
                {item.blockchainTokenId ? (
                  <img
                    src={`${API}/metadata/axolotito/${item.blockchainTokenId}.svg`}
                    alt={item.name}
                    className={`w-16 h-16 rounded-xl border border-white/10 bg-gradient-to-br ${skinGradient(item.skinColor || '')} object-contain p-1 shrink-0`}
                  />
                ) : (
                  <div className={`w-16 h-16 rounded-xl border border-white/10 bg-gradient-to-br ${skinGradient(item.skinColor || '')} flex items-center justify-center text-3xl shrink-0`}>
                    🦎
                  </div>
                )}
                <div className="flex flex-col gap-1 text-[9px] font-bold flex-1">
                  <div className="flex justify-between text-slate-400">
                    <span>Nivel</span><span className="text-white font-black">{item.level}</span>
                  </div>
                  <div className="flex justify-between text-slate-400">
                    <span>✨ SUERTE</span><span className="font-black" style={{ color: '#fbbf24' }}>{item.statLuck?.toFixed(1)}</span>
                  </div>
                  <div className="flex justify-between text-slate-400">
                    <span>👁️ OJO</span><span className="font-black" style={{ color: '#2dd4bf' }}>{item.statFocus?.toFixed(1)}</span>
                  </div>
                  <div className="flex justify-between text-slate-400">
                    <span>🔋 PILA</span><span className="font-black" style={{ color: '#60a5fa' }}>{item.statStamina?.toFixed(0)}</span>
                  </div>
                  <div className="flex justify-between text-slate-400">
                    <span>🧂 SAL</span><span className="font-black" style={{ color: '#f87171' }}>{item.statSalinity?.toFixed(1)}</span>
                  </div>
                  {item.skinColor && (
                    <div className="flex justify-between text-slate-400">
                      <span>🎨 Color</span>
                      <span className="text-slate-300 font-black capitalize">{item.skinColor.replace(/_/g, ' ')}</span>
                    </div>
                  )}
                </div>
              </div>
              {isRent && item.splitPct !== undefined && (
                <p className="text-[9px] text-slate-600 text-right">
                  Dueño recibe {item.splitPct}% de victorias
                </p>
              )}
            </>
          )}

          {isBooster && (() => {
            const getBoosterStyles = (name: string) => {
              const n = name.toLowerCase();
              if (n.includes('foil') || n.includes('brillante')) {
                return { gradient: 'from-amber-600 via-yellow-400 to-amber-700', symbol: '✨' };
              } else if (n.includes('fiesta')) {
                return { gradient: 'from-pink-600 via-rose-500 to-purple-600', symbol: '🎈' };
              } else if (n.includes('nido')) {
                return { gradient: 'from-emerald-600 via-teal-500 to-cyan-600', symbol: '🪺' };
              } else if (n.includes('cosmos')) {
                return { gradient: 'from-indigo-900 via-purple-700 to-pink-800', symbol: '🌌' };
              } else {
                return { gradient: 'from-slate-700 via-slate-600 to-slate-800', symbol: '🎰' };
              }
            };
            const theme = getBoosterStyles(item.name);
            return (
              <div className="flex items-center gap-3">
                <div className={`w-14 h-20 rounded-xl border border-white/10 bg-gradient-to-br ${theme.gradient} flex items-center justify-center text-3xl shadow-md shrink-0 relative overflow-hidden`}>
                  {(item.name.toLowerCase().includes('foil') || item.name.toLowerCase().includes('brillante')) && (
                    <div className="holo-overlay rounded-xl opacity-60" />
                  )}
                  {theme.symbol}
                </div>
                <div className="flex flex-col gap-1 text-[9px] font-bold flex-1">
                  <div className="flex justify-between text-slate-400">
                    <span>Fase</span><span className="text-white font-black">{item.raw.item?.item_metadata?.fase || 1}</span>
                  </div>
                  <div className="flex justify-between text-slate-400">
                    <span>Cantidad</span><span className="text-pink-400 font-black">x{item.quantity}</span>
                  </div>
                  <div className="flex justify-between text-slate-400">
                    <span>Límite</span><span className="text-slate-400 font-black">{item.raw.item?.max_supply || "Ilimitado"}</span>
                  </div>
                </div>
              </div>
            );
          })()}

          {isCard && (
            <div className="flex items-center gap-3">
              <div className="w-14 h-20 rounded-xl border border-slate-700 bg-slate-900 flex flex-col items-center justify-center text-3xl relative overflow-hidden shrink-0">
                {item.isShiny && <div className="holo-overlay rounded-xl opacity-85" />}
                <span>🃏</span>
              </div>
              <div className="flex flex-col gap-1 text-[9px] font-bold flex-1">
                <div className="flex justify-between text-slate-400">
                  <span>Edición</span>
                  <span className="text-white font-black">{item.isFirstEdition ? "1ra Edición" : "Normal"}</span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>Brillo</span>
                  <span className="text-white font-black">{item.isShiny ? "Brillante ✨" : "Mate"}</span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>Rareza</span>
                  <span className="text-amber-400 font-black capitalize">{item.raw.item?.dynamic_rarity || "Común"}</span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>Cantidad</span>
                  <span className="text-pink-400 font-black">x{item.quantity}</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* footer: price + action */}
        <div className="border-t border-white/[0.05] px-3 py-2.5 flex items-center gap-2">
          <div className="flex items-center gap-1">
            <span className="text-base leading-none">🪙</span>
            <span className="text-[15px] font-black text-amber-500 tabular-nums">{item.price}</span>
            <span className="text-[9px] text-slate-600 font-bold ml-0.5">
              FRJ{isRent ? '/día' : ''}
            </span>
          </div>
          <div className="flex-1" />
          {!token ? (
            <span className="text-[9px] text-slate-600 font-bold italic">Conecta wallet</span>
          ) : isOwn ? (
            <button onClick={() => openConfirm(item)}
              className="px-3 py-1.5 rounded-lg border border-red-500/30 bg-red-950/30 text-red-300 hover:bg-red-950/50 text-[9px] font-black uppercase tracking-wide transition-all active:scale-95">
              Retirar
            </button>
          ) : isRent ? (
            <button onClick={() => openConfirm(item)}
              className="px-3 py-1.5 rounded-lg text-[9px] font-black uppercase tracking-wide transition-all active:scale-95 text-white"
              style={{ background: 'rgba(167,139,250,0.25)', border: '1px solid #7C3AED55' }}>
              Rentar
            </button>
          ) : (
            <HoldButton
              variant={item.itemType === 'axolotito' ? 'primary' : 'teal'}
              label="Comprar"
              sublabel="Mantén para confirmar"
              duration={1000}
              onConfirm={() => openConfirm(item)}
            />
          )}
        </div>
      </div>
    );
  };

  /* ── confirm modal ── */
  const ConfirmModal = () => {
    if (!confirmItem) return null;
    const isOwn  = confirmItem.ownerId === userId;
    const isRent = confirmItem.marketType === 'rent';
    const action = isOwn ? 'Retirar del mercado' : isRent ? 'Rentar' : 'Comprar';
    const accentColor = isOwn ? '#EF4444' : isRent ? '#A78BFA' : '#34D399';

    return (
      <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black/70 backdrop-blur-sm p-4 animate-in fade-in duration-200"
        onClick={e => { if (e.target === e.currentTarget && !txLoading) setConfirmItem(null); }}>
        <div className="bg-[#0D0D1F] rounded-2xl border border-white/10 p-5 w-full max-w-sm flex flex-col gap-4 animate-in slide-in-from-bottom-4 duration-200">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-[10px] font-black uppercase tracking-widest mb-1" style={{ color: accentColor }}>
                {action}
              </p>
              <p className="text-white font-black text-base leading-tight">{confirmItem.name}</p>
              <p className="text-slate-500 text-[11px] mt-0.5">
                {confirmItem.itemType === 'board' ? 'Tablero' : 'Axolotito'} · Nv.{confirmItem.level}
              </p>
            </div>
            <button onClick={() => !txLoading && setConfirmItem(null)}
              className="text-slate-600 hover:text-white transition-colors shrink-0 mt-0.5">
              <X size={16} />
            </button>
          </div>

          {!isOwn && (
            <div className="flex items-center justify-between bg-white/[0.04] rounded-xl px-4 py-3 border border-white/[0.06]">
              <span className="text-slate-400 text-sm font-bold">{isRent ? 'Costo de renta' : 'Precio'}</span>
              <div className="flex items-center gap-1.5">
                <span className="text-lg leading-none">🪙</span>
                <span className="text-white font-black text-lg tabular-nums">{confirmItem.price}</span>
                <span className="text-slate-500 text-xs">FRJ{isRent ? '/día' : ''}</span>
              </div>
            </div>
          )}

          {txMsg && (
            <div className={`text-xs font-bold rounded-xl p-3 text-center ${
              txMsg.type === 'ok'
                ? 'bg-emerald-950/60 border border-emerald-500/30 text-emerald-200'
                : 'bg-red-950/60 border border-red-500/30 text-red-200'
            }`}>
              {txMsg.text}
            </div>
          )}

          <div className="flex gap-2">
            <button onClick={() => !txLoading && setConfirmItem(null)}
              className="flex-1 py-2.5 bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.06] text-slate-400 hover:text-white rounded-xl text-xs font-black uppercase tracking-wider transition-all disabled:opacity-50"
              disabled={txLoading}>
              Cancelar
            </button>
            <button onClick={executeAction} disabled={txLoading}
              className="flex-1 py-2.5 rounded-xl text-xs font-black uppercase tracking-wider transition-all active:scale-95 disabled:opacity-50 text-white"
              style={{ background: `${accentColor}30`, border: `1px solid ${accentColor}60` }}>
              {txLoading ? '...' : action}
            </button>
          </div>
        </div>
      </div>
    );
  };

  /* ── skeleton ── */
  const Skeleton = () => (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
      {Array(4).fill(null).map((_, i) => (
        <div key={i} className="rounded-2xl border border-white/[0.05] bg-[#0D0D1F] h-48 animate-pulse" />
      ))}
    </div>
  );

  return (
    <div className="flex flex-col gap-4">

      {/* ── header + refresh ── */}
      <div className="flex items-center justify-between">
        <div>
          <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Mercado P2P</p>
          {!loading && (
            <p className="text-[11px] text-slate-600 font-bold mt-0.5">
              {filtered.length} publicacion{filtered.length !== 1 ? 'es' : ''} disponible{filtered.length !== 1 ? 's' : ''}
            </p>
          )}
        </div>
        <button onClick={resetAndReload} disabled={loading}
          className="p-2 rounded-xl bg-white/[0.04] border border-white/[0.06] text-slate-500 hover:text-white transition-all active:scale-95 disabled:opacity-40">
          <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
        </button>
      </div>

      {/* ── global tx success toast ── */}
      {txMsg?.type === 'ok' && !confirmItem && (
        <div className="bg-emerald-950/60 border border-emerald-500/30 text-emerald-200 text-xs font-bold rounded-xl p-3 text-center">
          ✅ {txMsg.text}
        </div>
      )}

      {/* ── filters ── */}
      <div className="flex flex-col gap-2">
        {/* asset filter */}
        <div className="flex gap-1.5 flex-wrap">
          {chip(assetFilter === 'all',        '🌐 Todos',      () => setAssetFilter('all'))}
          {chip(assetFilter === 'board',      '📋 Tableros',   () => setAssetFilter('board'))}
          {chip(assetFilter === 'axolotito',  '🦎 Axolotitos', () => setAssetFilter('axolotito'))}
          {chip(assetFilter === 'booster',    '📦 Sobres',     () => setAssetFilter('booster'), '#A855F7')}
          {chip(assetFilter === 'card',       '🃏 Cartas',     () => setAssetFilter('card'), '#F59E0B')}
        </div>

        {/* rarity filter (only relevant if card/booster is selected or all) */}
        {(assetFilter === 'all' || assetFilter === 'card' || assetFilter === 'booster') && (
          <div className="flex gap-1.5 items-center flex-wrap">
            <span className="text-[8px] font-black text-slate-600 uppercase tracking-widest mr-1">Rareza:</span>
            {chip(rarityFilter === 'all',        'Todos',        () => setRarityFilter('all'),       '#F59E0B')}
            {chip(rarityFilter === 'common',     'Común',        () => setRarityFilter('common'),    '#F59E0B')}
            {chip(rarityFilter === 'rare',       'Rara',         () => setRarityFilter('rare'),      '#F59E0B')}
            {chip(rarityFilter === 'epic',       'Épica',        () => setRarityFilter('epic'),      '#F59E0B')}
            {chip(rarityFilter === 'legendary',  'Legendaria',   () => setRarityFilter('legendary'), '#F59E0B')}
          </div>
        )}

        {/* shiny filter (only relevant if card/booster/all) */}
        {(assetFilter === 'all' || assetFilter === 'card' || assetFilter === 'booster') && (
          <div className="flex gap-1.5 items-center flex-wrap">
            <span className="text-[8px] font-black text-slate-600 uppercase tracking-widest mr-1">Brillo:</span>
            {chip(shinyFilter === 'all',    'Todos',          () => setShinyFilter('all'),    '#A855F7')}
            {chip(shinyFilter === 'shiny',  'Brillante ✨',   () => setShinyFilter('shiny'),  '#A855F7')}
            {chip(shinyFilter === 'normal', 'Mate',           () => setShinyFilter('normal'), '#A855F7')}
          </div>
        )}

        {/* mode + sort */}
        <div className="flex gap-1.5 flex-wrap">
          {chip(modeFilter === 'all',  '🛒 Todos',   () => setModeFilter('all'),  '#2DD4BF')}
          {chip(modeFilter === 'sale', '🛍️ Venta',   () => setModeFilter('sale'), '#34D399')}
          {chip(modeFilter === 'rent', '🤝 Renta',   () => setModeFilter('rent'), '#A78BFA')}
          <div className="flex-1" />
          {chip(sort === 'price_asc',  '🪙 Precio ↑', () => setSort('price_asc'),  '#F59E0B')}
          {chip(sort === 'price_desc', '🪙 Precio ↓', () => setSort('price_desc'), '#F59E0B')}
        </div>
      </div>

      {/* ── content ── */}
      {loading ? <Skeleton /> : error ? (
        <div className="flex flex-col items-center gap-3 py-12 text-center">
          <span className="text-3xl">⚠️</span>
          <p className="text-slate-500 text-sm font-bold">{error}</p>
          <button onClick={resetAndReload}
            className="px-5 py-2 bg-teal-700/60 hover:bg-teal-600/60 text-teal-200 font-black text-xs uppercase rounded-xl transition-all active:scale-95">
            Reintentar
          </button>
        </div>
      ) : filtered.length === 0 ? (
        <div className="flex flex-col items-center gap-3 py-16 text-center">
          <span className="text-4xl">🏪</span>
          <p className="text-slate-400 font-black text-sm">No hay publicaciones</p>
          <p className="text-slate-600 text-xs max-w-xs leading-relaxed">
            {assetFilter !== 'all' || modeFilter !== 'all'
              ? 'Prueba cambiando los filtros para ver más listados.'
              : 'El mercado está vacío. Publica tablas o Axolotitos desde tus perfiles.'}
          </p>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {filtered.map(item => <Card key={item.key} item={item} />)}
          </div>

          {/* infinite scroll sentinel + loading indicator */}
          <div ref={sentinelRef} className="flex justify-center py-6">
            {loadingMore && (
              <div className="flex items-center gap-2 text-slate-500 text-xs font-bold">
                <RefreshCw size={14} className="animate-spin" />
                Cargando más...
              </div>
            )}
            {!hasMore && !loading && items.length > 0 && (
              <p className="text-[10px] text-slate-600 font-bold uppercase tracking-wider">
                — Fin del mercado —
              </p>
            )}
          </div>
        </>
      )}

      <ConfirmModal />
    </div>
  );
}
