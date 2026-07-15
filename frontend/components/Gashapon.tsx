"use client";
import { API_BASE } from "@/lib/api";

import React, { useState, useEffect, useRef, useCallback } from 'react';
import axios from 'axios';
import { Coins, ShieldAlert, Star, Info, X, ChevronRight } from 'lucide-react';
import HoldButton from './ui/HoldButton';
import { fetchLunarStatus } from '@/services/rewardsService';
import type { LunarStatus } from '@/types/economy';
// Gashapon sub-components (task-49 extraction)
import type { Tier } from './gashapon/tierConfig';
import { TIER_CONFIG, TRIPLE_COST } from './gashapon/tierConfig';
import { mapResultToRarity } from './gashapon/rarityConfig';
import LegendaryOverlay from './gashapon/LegendaryOverlay';
import RevealSequence from './gashapon/RevealSequence';
import { useProductPolicy } from '@/hooks/useProductPolicy';

const API = `${API_BASE}`;

interface GashaponProps {
  userId: string;
  token: string | null;
  recargarSaldos: () => void;
  balances: any;
}

// RollResult interface — kept local since shared between MachineCard, ResultOverlay, and RevealSequence
interface RollResult {
  type?: string; name?: string; amount?: number;
  rarity?: string; description?: string;
  item_metadata?: Record<string, any>; guaranteed?: boolean;
  is_legendary?: boolean; legendary_type?: string;
  tier?: Tier; // which machine tier produced this result
}

// ── Machine card component ──────────────────────────────────────────────────
interface MachineCardProps {
  tier: Tier;
  pityCounts: { bronce: number; plata: number; oro: number };
  balances: any;
  token: string | null;
  userId: string;
  onResult: (r: RollResult[]) => void;
  onError: (m: string) => void;
  onReload: () => void;
}

function MachineCard({ tier, pityCounts, balances, token, userId, onResult, onError, onReload }: MachineCardProps) {
  const [rolling, setRolling]         = useState(false);
  const [showProbs, setShowProbs]     = useState(false);
  const [showInfo, setShowInfo]       = useState(false);

  const cfg = TIER_CONFIG[tier];
  const pityCount = pityCounts[tier] ?? 0;
  const pityPct   = Math.min(100, (pityCount / cfg.pityLimit) * 100);
  const karmaFull = pityPct >= 100;
  const karmaHot  = pityPct >= 70;
  const canAfford = (balances?.frijolitos || 0) >= cfg.cost;

  const handleRoll = async () => {
    if (!token) { onError('Inicia sesión para lanzar.'); return; }
    if (!canAfford) { onError(`Necesitas ${cfg.cost} FRJ. Tienes ${(balances?.frijolitos || 0).toFixed(0)} FRJ.`); return; }
    setRolling(true);
    try {
      const res = await axios.post(`${API}/shop/capsule/roll`, { user_id: userId, tier }, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const item: RollResult = {
        ...res.data.item,
        is_legendary: res.data.is_legendary ?? false,
        legendary_type: res.data.legendary_type ?? null,
        tier,
      };
      onResult([item]);
      onReload();
    } catch (e: any) {
      onError(e.response?.data?.detail || 'Error al lanzar la cápsula.');
    } finally {
      setRolling(false);
    }
  };

  return (
    <div
      className="relative flex flex-col rounded-3xl border overflow-hidden transition-all duration-300"
      style={{
        borderColor: cfg.border,
        background: 'linear-gradient(180deg, rgba(5,8,20,0.97) 0%, rgba(2,5,15,0.99) 100%)',
        boxShadow: `0 0 ${karmaHot ? 28 : 16}px ${cfg.glow}`,
      }}
    >
      {/* Karma "casi lleno" badge */}
      {karmaHot && !karmaFull && (
        <div
          className="absolute top-2 right-2 z-10 text-[7px] font-black uppercase tracking-wider px-2 py-0.5 rounded-full animate-pulse"
          style={{ background: cfg.color + '30', color: cfg.color, border: `1px solid ${cfg.border}` }}
        >
          ⚡ KARMA HOT
        </div>
      )}
      {karmaFull && (
        <div
          className="absolute top-2 right-2 z-10 text-[7px] font-black uppercase tracking-wider px-2 py-0.5 rounded-full animate-bounce"
          style={{ background: cfg.color + '40', color: cfg.color, border: `1px solid ${cfg.border}` }}
        >
          🌀 GARANTIZADO
        </div>
      )}

      <div className="p-4 flex flex-col gap-3 flex-1">
        {/* Header */}
        <div className="text-center">
          <div className="text-[8px] font-black uppercase tracking-widest mb-1.5" style={{ color: cfg.color }}>
            Cápsula {cfg.label}
          </div>

          {/* Machine sphere */}
          <div className="relative flex items-center justify-center h-20 my-1">
            <div
              className="absolute inset-0 rounded-full blur-2xl pointer-events-none"
              style={{ background: cfg.glow, opacity: 0.4 }}
            />
            <div
              className={`relative w-16 h-16 rounded-full flex items-center justify-center text-3xl border-2 shadow-xl select-none ${rolling ? 'animate-spin' : 'hover:scale-110 transition-transform cursor-pointer'}`}
              style={{
                borderColor: cfg.border,
                background: `radial-gradient(circle at 38% 35%, rgba(30,20,50,0.9) 0%, rgba(5,2,15,0.98) 100%)`,
                boxShadow: `inset 0 3px 12px rgba(0,0,0,0.7), 0 0 20px ${cfg.glow}`,
              }}
              onClick={!rolling ? handleRoll : undefined}
            >
              {rolling ? (
                <div
                  className="w-7 h-7 border-[3px] border-t-transparent rounded-full animate-spin"
                  style={{ borderColor: `${cfg.color} transparent transparent transparent` }}
                />
              ) : (
                cfg.emoji
              )}
            </div>
          </div>

          <div className="text-[10px] font-black" style={{ color: cfg.color }}>
            🪙 {cfg.cost} FRJ
          </div>
        </div>

        {/* Karma bar */}
        <div>
          <div className="flex items-center justify-between mb-1">
            <div className="flex items-center gap-1">
              <span className="text-[8px] font-black text-slate-500 uppercase tracking-wider">Karma</span>
              <button onClick={() => setShowInfo(p => !p)} className="text-slate-700 hover:text-slate-400 transition-colors">
                <Info size={9} />
              </button>
            </div>
            <span className="text-[8px] font-black text-slate-500">{pityCount}/{cfg.pityLimit}</span>
          </div>
          {showInfo && (
            <div className="mb-1.5 bg-slate-900/90 border border-white/8 rounded-xl p-2 text-[9px] text-slate-400 leading-relaxed">
              🌀 Cada tirada sin raro suma karma. Al llegar a {cfg.pityLimit}, el <span className="text-amber-400 font-bold">siguiente drop está garantizado</span>.
            </div>
          )}
          <div className="h-1.5 bg-slate-800 rounded-full overflow-hidden">
            <div
              className="h-full rounded-full transition-all duration-500"
              style={{
                width: `${pityPct}%`,
                background: `linear-gradient(90deg, ${cfg.color}99, ${cfg.color})`,
                boxShadow: karmaHot ? `0 0 6px ${cfg.glow}` : undefined,
              }}
            />
          </div>
        </div>

        {/* Probabilities (collapsible) */}
        <button
          onClick={() => setShowProbs(p => !p)}
          className="text-[8px] text-slate-600 hover:text-slate-400 font-bold uppercase tracking-wider transition-colors text-left"
        >
          {showProbs ? '▲ Ocultar probabilidades' : '▼ Ver probabilidades'}
        </button>
        {showProbs && (
          <div className="bg-slate-950/80 border border-white/5 rounded-xl overflow-hidden divide-y divide-white/5">
            {cfg.probs.map((p, i) => (
              <div key={i} className="flex justify-between items-center px-3 py-1.5">
                <span className="text-[9px] text-slate-500 font-bold">{p.label}</span>
                <span className={`text-[9px] font-black ${p.color}`}>{p.pct}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Roll button */}
      <div className="px-3 pb-4">
        <HoldButton
          onConfirm={handleRoll}
          disabled={rolling || !canAfford}
          duration={1000}
          ringColor={cfg.color}
          className="w-full"
          style={{
            width: '100%',
            background: canAfford
              ? `linear-gradient(135deg, ${cfg.color}30, rgba(5,10,20,0.9))`
              : 'rgba(15,20,35,0.8)',
            border: `1.5px solid ${cfg.border}`,
            boxShadow: canAfford ? `0 0 14px ${cfg.glow}` : undefined,
            color: canAfford ? 'white' : '#475569',
            borderRadius: '1rem',
            padding: '12px',
            fontWeight: '900',
            textTransform: 'uppercase',
            fontSize: '10px',
            letterSpacing: '0.1em',
          }}
          label={
            rolling
              ? <><span className="inline-block w-3 h-3 border-2 border-current border-t-transparent rounded-full animate-spin mr-1" /> Abriendo…</>
              : canAfford
              ? `${cfg.emoji} Lanzar ${cfg.label}`
              : 'FRJ insuficientes'
          }
        />
      </div>
    </div>
  );
}

// ── Result overlay (single + triple carousel) ──────────────────────────────
function ResultOverlay({ results, isTriple, onClose }: { results: RollResult[]; isTriple: boolean; onClose: () => void }) {
  const [idx, setIdx] = useState(0);
  const current = results[idx];
  const isLast  = idx === results.length - 1;

  const handleNext = () => {
    if (isLast) onClose();
    else setIdx(i => i + 1);
  };

  const isCurrentLegendary = current?.is_legendary === true;

  return (
    <div className="relative w-full max-w-md mx-auto flex flex-col items-center gap-4 py-4 px-2 animate-in fade-in duration-300">
      {/* Fullscreen legendary celebration — rendered via fixed positioning */}
      {isCurrentLegendary && <LegendaryOverlay legendaryType={current.legendary_type} />}

      <div className="text-center relative z-10">
        <h3 className={`text-xl font-black uppercase tracking-tight ${isCurrentLegendary ? 'text-transparent bg-clip-text bg-gradient-to-r from-amber-300 via-pink-300 to-purple-400 animate-pulse' : 'text-white'}`}>
          {isCurrentLegendary
            ? '🏆 ¡PREMIO MÍTICO! 🏆'
            : isTriple
            ? `🎰 Triple Suerte · ${idx + 1} de ${results.length}`
            : '🎁 ¡Tu resultado!'}
        </h3>
        {isTriple && !isCurrentLegendary && (
          <p className="text-[9px] text-slate-500 uppercase tracking-widest font-bold mt-0.5">
            {TRIPLE_COST} FRJ total · ahorras 400 FRJ
          </p>
        )}
      </div>

      {/* RevealSequence — three-phase animation: drop → open → prize */}
      {current && (
        <div className="relative z-10 w-full">
          <RevealSequence
            key={idx}
            result={current}
            tier={current.tier ?? 'bronce'}
            rarity={mapResultToRarity(current.rarity)}
            onClose={handleNext}
            closeLabel={isTriple ? (isLast ? '¡Listo!' : `Siguiente →`) : '¡Aceptar!'}
          />
        </div>
      )}

      {/* Dot indicators for triple */}
      {isTriple && (
        <div className="flex items-center gap-2 relative z-10">
          {results.map((_, i) => (
            <div
              key={i}
              className={`rounded-full transition-all duration-300 ${
                i === idx ? 'w-4 h-2 bg-pink-400' : i < idx ? 'w-2 h-2 bg-slate-600' : 'w-2 h-2 bg-slate-700'
              }`}
            />
          ))}
        </div>
      )}
    </div>
  );
}

// ── Main component ──────────────────────────────────────────────────────────
export default function Gashapon({ userId, token, recargarSaldos, balances }: GashaponProps) {
  const { capabilities, loading: policyLoading } = useProductPolicy();
  const randomRewardsEnabled = capabilities.commerce.purchased_random_rewards;
  const passiveRewardsEnabled = capabilities.gameplay.passive_token_rewards;
  const [results,        setResults]        = useState<RollResult[] | null>(null);
  const [error,          setError]          = useState<string | null>(null);
  const [pityData,       setPityData]       = useState<{ bronce: number; plata: number; oro: number }>({ bronce: 0, plata: 0, oro: 0 });
  const [lunarStatus,    setLunarStatus]    = useState<LunarStatus | null>(null);
  const [feed,           setFeed]           = useState<string[]>([]);
  const [rollingTriple,  setRollingTriple]  = useState(false);
  const [mobileTier,     setMobileTier]     = useState<Tier>('bronce');
  const headers = token ? { Authorization: `Bearer ${token}` } : {};

  const loadStatus = useCallback(async () => {
    if (!randomRewardsEnabled && !passiveRewardsEnabled) {
      setPityData({ bronce: 0, plata: 0, oro: 0 });
      setFeed([]);
      setLunarStatus(null);
      return;
    }
    try {
      const [resPity, resFeed, resLunar] = await Promise.allSettled([
        randomRewardsEnabled
          ? axios.get(`${API}/shop/capsule/pity`, { headers: token ? { Authorization: `Bearer ${token}` } : {} })
          : Promise.resolve({ data: { pity: { bronce: 0, plata: 0, oro: 0 } } }),
        randomRewardsEnabled
          ? axios.get(`${API}/shop/capsule/feed`)
          : Promise.resolve({ data: [] }),
        passiveRewardsEnabled && token
          ? fetchLunarStatus(token).catch(() => null)
          : Promise.resolve(null),
      ]);
      if (resPity.status === 'fulfilled') {
        setPityData(resPity.value.data?.pity || { bronce: 0, plata: 0, oro: 0 });
      }
      if (resFeed.status === 'fulfilled') {
        const raw = resFeed.value.data || [];
        setFeed(raw.map((e: any) =>
          typeof e === 'string' ? e : `${e.nickname} ${e.outcome_text}`
        ));
      }
      if (resLunar.status === 'fulfilled' && resLunar.value) {
        setLunarStatus(resLunar.value as LunarStatus);
      } else if (passiveRewardsEnabled && token) {
        // Fallback: direct axios call if fetchLunarStatus didn't work
        try {
          const lr = await axios.get(`${API}/rewards/lunar/status`, { headers });
          setLunarStatus(lr.data);
        } catch { /* ignore */ }
      }
    } catch { /* ignore */ }
  }, [randomRewardsEnabled, passiveRewardsEnabled, token]);

  useEffect(() => { loadStatus(); }, [loadStatus]);

  const handleTriple = async () => {
    if (!randomRewardsEnabled) {
      setError('Las recompensas aleatorias compradas están deshabilitadas.');
      return;
    }
    if (!token) { setError('Inicia sesión para lanzar.'); return; }
    if ((balances?.frijolitos || 0) < TRIPLE_COST) {
      setError(`Necesitas ${TRIPLE_COST} FRJ para Triple Suerte.`); return;
    }
    setRollingTriple(true); setError(null);
    try {
      const res = await axios.post(`${API}/shop/capsule/triple-suerte`, { user_id: userId }, { headers });
      const TIERS: Tier[] = ['bronce', 'plata', 'oro'];
      const results: RollResult[] = (res.data.results || []).map((item: any, i: number) => ({
        ...item,
        is_legendary: item.is_legendary ?? false,
        legendary_type: item.legendary_type ?? null,
        tier: TIERS[i] ?? 'bronce',
      }));
      setResults(results);
      recargarSaldos(); loadStatus();
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Error en Triple Suerte.');
    } finally { setRollingTriple(false); }
  };

  const frj = (balances?.frijolitos || 0);
  const lunarWeek = lunarStatus?.lunar_week || 0;
  const lunarDay = (lunarStatus?.streak_day || 0) + 1;
  const lunarCanClaim = lunarStatus?.can_claim || false;
  const lunarDay7Label = lunarStatus?.day7_reward?.label || '';
  const lunarEmoji = ['', '🌑', '🌒', '🌓', '🌔', '🌕', '🌟'][lunarWeek] || '🌙';

  if (!randomRewardsEnabled) {
    return (
      <div className="w-full max-w-2xl mx-auto py-14 px-6 text-center rounded-3xl border border-amber-500/20 bg-amber-950/20">
        <div className="text-5xl mb-3">🛟</div>
        <h2 className="text-xl font-black text-amber-200 uppercase tracking-tight">Cápsulas en pausa</h2>
        <p className="mt-2 text-xs text-slate-400 max-w-md mx-auto">
          {policyLoading
            ? 'Verificando la política de producto…'
            : 'No vendemos recompensas aleatorias. No se realizará ningún cargo ni lanzamiento.'}
        </p>
      </div>
    );
  }

  // ── Result overlay ─────────────────────────────────────────────────────
  if (results) {
    const isTriple = results.length > 1;
    return (
      <ResultOverlay
        results={results}
        isTriple={isTriple}
        onClose={() => setResults(null)}
      />
    );
  }

  // ── Main UI ────────────────────────────────────────────────────────────
  return (
    <div className="w-full max-w-2xl mx-auto flex flex-col gap-4 pb-6 animate-in fade-in duration-300">
      <style>{`
        @keyframes gasha-marquee { from { transform: translateX(0); } to { transform: translateX(-50%); } }
        .gasha-marquee { animation: gasha-marquee 32s linear infinite; will-change: transform; }
        .gasha-marquee:hover { animation-play-state: paused; }
      `}</style>

      {/* ── Live feed marquee — siempre arriba ── */}
      {feed.length > 0 && (
        <div className="overflow-hidden rounded-2xl border border-white/5 bg-slate-900/40 py-2 -mx-1">
          <div className="flex whitespace-nowrap gasha-marquee">
            {[...feed, ...feed].map((item, i) => (
              <span key={i} className="text-[10px] text-slate-400 font-bold px-5 shrink-0">
                <span className="text-[#E4007C]">✦</span> {item}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* ── Header ── */}
      <div className="text-center pt-1">
        <h2 className="text-2xl sm:text-3xl font-black italic text-transparent bg-clip-text bg-gradient-to-r from-amber-400 via-pink-400 to-purple-400 tracking-tight uppercase">
          La Suertuda 🎰
        </h2>
        <p className="text-[9px] text-slate-500 uppercase tracking-widest font-bold mt-0.5">
          Cápsulas Sorpresa · Saldo: <span className="text-amber-400">{frj.toFixed(0)} FRJ</span>
        </p>
      </div>

      {/* ── Ciclo Lunar banner ── */}
      {passiveRewardsEnabled && lunarWeek > 0 && (
        <div
          className={`rounded-2xl border px-4 py-3 transition-all cursor-pointer ${
            lunarCanClaim
              ? 'bg-purple-950/30 border-purple-500/30 shadow-[0_0_16px_rgba(168,85,247,0.15)] hover:border-purple-400/50'
              : 'bg-slate-900/30 border-white/5 hover:border-purple-500/20'
          }`}
          onClick={() => {
            // Dispatch custom event to open the DailyClaim bottom sheet
            window.dispatchEvent(new CustomEvent('open-lunar-sheet'));
          }}
        >
          <div className="flex items-center justify-between gap-3">
            <div className="flex items-center gap-2.5">
              <span className={`text-xl ${lunarCanClaim ? 'animate-pulse' : ''}`}>
                {lunarCanClaim ? '🎁' : lunarEmoji}
              </span>
              <div>
                <span className="text-[11px] font-black text-purple-300 uppercase tracking-wide">
                  Ciclo Lunar · Luna {lunarWeek}, Día {lunarDay}/7
                </span>
                <p className="text-[9px] text-slate-500 font-bold mt-0.5">
                  {lunarCanClaim
                    ? lunarDay === 7
                      ? `🎰 ¡Día 7! Reclama: ${lunarDay7Label}`
                      : `¡Reclama tu recompensa diaria!`
                    : lunarDay === 7
                    ? `Día 7 te espera: ${lunarDay7Label}`
                    : `Vuelve mañana para seguir tu racha`}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-1.5 shrink-0">
              {lunarCanClaim && (
                <span className="bg-purple-500 text-white text-[8px] font-black px-2 py-0.5 rounded-full animate-pulse">
                  ¡RECLAMA!
                </span>
              )}
              <ChevronRight size={14} className="text-slate-600" />
            </div>
          </div>
        </div>
      )}

      {/* ── 3 Machines grid ── */}
      {/* ── Mobile: tier tab selector ── */}
      <div className="flex sm:hidden gap-1.5 rounded-2xl bg-slate-900/60 border border-white/6 p-1">
        {(['bronce', 'plata', 'oro'] as Tier[]).map(tier => {
          const cfg = TIER_CONFIG[tier];
          const active = mobileTier === tier;
          return (
            <button
              key={tier}
              onClick={() => setMobileTier(tier)}
              className={`flex-1 py-2 rounded-xl text-[11px] font-black uppercase tracking-wide transition-all active:scale-95 ${
                active ? 'text-white' : 'text-slate-500 hover:text-slate-300'
              }`}
              style={active ? { background: cfg.color + '25', color: cfg.color, boxShadow: `0 0 10px ${cfg.glow}` } : {}}
            >
              {cfg.emoji} {cfg.label}
            </button>
          );
        })}
      </div>

      {/* ── Mobile: single machine card ── */}
      <div className="sm:hidden">
        <MachineCard
          key={mobileTier}
          tier={mobileTier}
          pityCounts={pityData}
          balances={balances}
          token={token}
          userId={userId}
          onResult={(r) => { setResults(r); recargarSaldos(); }}
          onError={setError}
          onReload={loadStatus}
        />
      </div>

      {/* ── Desktop: 3-column grid ── */}
      <div className="hidden sm:grid grid-cols-3 gap-3">
        {(['bronce', 'plata', 'oro'] as Tier[]).map(tier => (
          <MachineCard
            key={tier}
            tier={tier}
            pityCounts={pityData}
            balances={balances}
            token={token}
            userId={userId}
            onResult={(r) => { setResults(r); recargarSaldos(); }}
            onError={setError}
            onReload={loadStatus}
          />
        ))}
      </div>

      {/* ── Triple Suerte promo ── */}
      <div className="relative rounded-3xl border-2 border-yellow-500/40 overflow-hidden">
        {/* Glow background */}
        <div className="absolute inset-0 bg-gradient-to-r from-slate-950 via-yellow-950/20 to-slate-950 pointer-events-none" />
        <div className="absolute top-0 right-0 text-8xl opacity-[0.04] select-none pointer-events-none leading-none translate-x-4 -translate-y-2">🍀</div>

        <div className="relative p-5 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="text-left space-y-1.5">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="bg-yellow-500 text-slate-950 font-black text-[8px] px-2 py-0.5 rounded-full uppercase tracking-wide shadow">
                COMBO OFERTA
              </span>
              <span className="text-lg font-black text-yellow-400 uppercase tracking-tight flex items-center gap-1.5">
                <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" /> Triple Suerte
              </span>
            </div>
            <p className="text-[10px] text-slate-400 max-w-xs leading-relaxed">
              Abre <span className="text-yellow-400 font-bold">Bronce + Plata + Oro</span> simultáneamente. Ahorra 400 FRJ vs abrirlas por separado.
            </p>
            <div className="flex items-center gap-2">
              <span className="text-slate-600 line-through text-[10px]">🪙 2,650 FRJ</span>
              <span className="text-amber-400 font-black text-sm">🪙 {TRIPLE_COST} FRJ</span>
              <span className="bg-amber-950 border border-amber-500/30 text-amber-400 text-[8px] font-black px-2 py-0.5 rounded-full">-15%</span>
            </div>
          </div>

          <HoldButton
            onConfirm={handleTriple}
            disabled={rollingTriple || frj < TRIPLE_COST}
            duration={1000}
            variant="amber"
            style={{
              background: frj >= TRIPLE_COST
                ? 'linear-gradient(135deg, #EAB308, #D97706)'
                : 'rgba(15,20,35,0.8)',
              color: frj >= TRIPLE_COST ? '#0c0a00' : '#475569',
              boxShadow: frj >= TRIPLE_COST ? '0 0 20px rgba(234,179,8,0.35)' : undefined,
              borderRadius: '1rem',
              padding: '12px 24px',
              fontWeight: '900',
              textTransform: 'uppercase',
              fontSize: '12px',
              letterSpacing: '0.1em',
            }}
            label={rollingTriple ? '⏳ Abriendo…' : frj >= TRIPLE_COST ? '🍀 ¡Tirar Triple!' : 'FRJ Insuficientes'}
          />
        </div>
      </div>

      {/* ── Error ── */}
      {error && (
        <div className="bg-red-950/50 border border-red-500/30 p-4 rounded-2xl text-red-200 text-xs font-bold flex items-start gap-2">
          <ShieldAlert className="h-4 w-4 text-red-400 shrink-0 mt-0.5" />
          <p className="leading-relaxed">{error}</p>
          <button onClick={() => setError(null)} className="ml-auto text-red-500 hover:text-red-300 shrink-0">
            <X size={14} />
          </button>
        </div>
      )}
    </div>
  );
}
