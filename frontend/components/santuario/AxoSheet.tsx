"use client";
import React, { useState } from 'react';
import { X, Zap, Crown, Star, Package } from 'lucide-react';
import BottomSheet from '@/components/ui/BottomSheet';
import { useToast } from '@/context/ToastContext';
import { traitNames, statNames, statColors } from '@/constants/santuario';
import { setMainAxolotito, feedAxolotito, sleepAxolotito, wakeAxolotito, claimAxolotitoStaking, stakeAxolotito, unstakeAxolotito } from '@/services/santuarioService';
import { API_BASE } from '@/lib/api';
import type { StakingAxolotitoInfo } from '@/types/economy';

const API = `${API_BASE}`;

interface AxoSheetProps {
  axo: any;
  onClose: () => void;
  token: string | null;
  onSetMain?: () => void;
  onOpenCave?: (axo: any) => void;
  /** Staking info for this specific axolotito, if available */
  stakingInfo?: StakingAxolotitoInfo | null;
  /** Triggered after claiming staking rewards */
  onStakingClaimed?: () => void;
}

export default function AxoSheet({ axo, onClose, token, onSetMain, onOpenCave, stakingInfo, onStakingClaimed }: AxoSheetProps) {
  const { toast } = useToast();
  const [settingMain, setSettingMain] = useState(false);
  const [claimingStaking, setClaimingStaking] = useState(false);
  const [staking, setStaking] = useState(false);
  const [unstaking, setUnstaking] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [remainingLock, setRemainingLock] = useState<number>(stakingInfo?.lock_remaining_seconds || 0);

  React.useEffect(() => {
    if (remainingLock <= 0) return;
    const interval = setInterval(() => {
      setRemainingLock((prev) => Math.max(0, prev - 1));
    }, 1000);
    return () => clearInterval(interval);
  }, [remainingLock]);

  const handleStake = async (status: 'studying' | 'resting') => {
    if (!token || staking) return;
    setStaking(true);
    setError(null);
    try {
      await stakeAxolotito(axo.id, status, token);
      toast.ok(`📈 Axolotito puesto en staking (${status === 'studying' ? 'Trabajar en el Tianguis' : 'Limpiar el Cenote'})`);
      if (onStakingClaimed) onStakingClaimed();
      onClose();
    } catch (e: any) {
      setError(e.response?.data?.detail || "Error al poner en staking.");
    } finally {
      setStaking(false);
    }
  };

  const handleUnstake = async () => {
    if (!token || unstaking) return;
    setUnstaking(true);
    setError(null);
    try {
      const res = await unstakeAxolotito(axo.id, token);
      toast.ok(`🪙 Axolotito retirado de staking. Reclamado ${res.claimed_frj.toFixed(2)} FRJ`);
      if (onStakingClaimed) onStakingClaimed();
      onClose();
    } catch (e: any) {
      setError(e.response?.data?.detail || "Error al retirar de staking.");
    } finally {
      setUnstaking(false);
    }
  };

  const energyPct = Math.min(100, (axo.energy_current / (axo.stat_stamina || 100)) * 100);

  const allStats: { key: string; maxVal: number }[] = [
    { key: 'luck',     maxVal: 100 },
    { key: 'focus',    maxVal: 100 },
    { key: 'stamina',  maxVal: 200 },
    { key: 'salinity', maxVal: 100 },
  ];

  const handleSetMain = async () => {
    if (!token) return;
    setSettingMain(true);
    setError(null);
    try {
      await setMainAxolotito(axo.id, token);
      if (onSetMain) onSetMain();
      onClose();
    } catch (e: any) {
      console.error(e);
      setError(e.response?.data?.detail || "Error al designar principal.");
    } finally {
      setSettingMain(false);
    }
  };

  return (
    <BottomSheet open={true} onClose={onClose}>
          <div className="px-5 pb-8 pt-3">
            {/* Header */}
            <div className="flex items-start justify-between mb-4">
              <div>
                <div className="flex items-center gap-2 mb-0.5">
                  <span className="text-[9px] font-black text-purple-400 border border-purple-500/30 bg-purple-950/40 px-2 py-0.5 rounded-full uppercase tracking-widest">
                    Nivel {axo.level}
                  </span>
                  <span className="text-[8px] text-slate-500 font-bold">#{axo.blockchain_token_id}</span>
                  {axo.is_main && (
                    <span className="text-[8px] font-black text-yellow-400 border border-yellow-500/30 bg-yellow-950/40 px-2 py-0.5 rounded-full uppercase tracking-widest flex items-center gap-0.5">
                      <Crown size={8} /> Principal
                    </span>
                  )}
                </div>
                <h3 className="text-lg font-black text-white leading-tight">{axo.name}</h3>
                <div className="text-[9px] text-pink-400 font-bold uppercase tracking-wide mt-0.5">
                  {axo.skin_color?.replace(/_/g, ' ')}
                </div>
              </div>
              <button onClick={onClose} className="p-2 rounded-full bg-slate-800/60 border border-white/5 text-slate-500 hover:text-white transition-colors mt-1">
                <X size={14} />
              </button>
            </div>

            {/* SVG + energy */}
            <div className="flex gap-4 mb-4">
              <div className="w-20 h-20 shrink-0 rounded-2xl bg-slate-900/60 border border-white/5 flex items-center justify-center p-1.5 shadow-inner">
                <img
                  src={`${API}/metadata/axolotito/${axo.blockchain_token_id}.svg`}
                  alt={axo.name}
                  className="w-full h-full object-contain animate-axo-bob"
                />
              </div>
              <div className="flex-1 flex flex-col justify-center gap-2">
                <div>
                  <div className="flex justify-between text-[8px] font-black text-slate-400 uppercase mb-1">
                    <span className="flex items-center gap-1"><Zap size={8} /> Energía actual</span>
                    <span className="text-green-400">{axo.energy_current} / {axo.stat_stamina}</span>
                  </div>
                  <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                    <div className="h-full bg-green-500 rounded-full transition-all" style={{ width: `${energyPct}%` }} />
                  </div>
                </div>
                {axo.stat_luck > 80 && (
                  <div className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl border text-[8px] font-black uppercase tracking-widest ${
                    axo.stat_luck > 99
                      ? 'bg-cyan-950/40 border-cyan-500/30 text-cyan-300'
                      : 'bg-amber-950/40 border-amber-500/30 text-amber-300'
                  }`}>
                    <Star size={9} className={axo.stat_luck > 99 ? 'text-cyan-400' : 'text-amber-400'} />
                    {axo.stat_luck > 99 ? '¡Aura Legendaria!' : '¡Alta Suerte!'}
                    <span className="ml-auto font-black">{axo.stat_luck.toFixed(1)}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Stats */}
            <div className="mb-4">
              <div className="text-[9px] font-black text-slate-500 uppercase tracking-widest mb-2">Estadísticas</div>
              <div className="grid grid-cols-2 gap-x-4 gap-y-2.5">
                {allStats.map(({ key, maxVal }) => {
                  const val = axo[`stat_${key}`] ?? 0;
                  const pct = Math.min(100, (val / maxVal) * 100);
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
                        <div className={`h-full rounded-full transition-all duration-500 ${statColors[key] || 'bg-teal-500'}`} style={{ width: `${pct}%` }} />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Traits */}
            {axo.traits && Object.keys(axo.traits).length > 0 && (
              <div className="mb-5">
                <div className="text-[9px] font-black text-slate-500 uppercase tracking-widest mb-2">Rasgos físicos</div>
                <div className="flex flex-wrap gap-1.5">
                  {Object.entries(axo.traits).map(([key, val]: [string, any]) => (
                    <span key={key} className="text-[8px] font-bold text-pink-300 bg-pink-950/40 border border-pink-500/20 px-2 py-0.5 rounded-full uppercase tracking-wide">
                      {traitNames[key] ? `${traitNames[key]}: ` : ''}{String(val).replace(/_/g, ' ')}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* ── STAKING SECTION ── */}
            {stakingInfo && (axo.status === 'studying' || axo.status === 'resting') && (
              <div className="mb-4 rounded-2xl bg-gradient-to-br from-amber-950/20 to-slate-900/60 border border-amber-500/25 p-4">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-1.5">
                    <span className="text-sm">🪙</span>
                    <span className="text-[10px] font-black text-amber-400 uppercase tracking-wider">
                      Staking FRJ ({axo.status === 'studying' ? 'Trabajando en Tianguis' : 'Limpiando Cenote'})
                    </span>
                  </div>
                  <span className="text-[9px] font-bold text-amber-300">
                    {axo.status === 'studying' ? `+${stakingInfo.hourly_rate.toFixed(2)} FRJ/h` : `~${stakingInfo.hourly_rate.toFixed(2)} FRJ/h (Variable)`}
                  </span>
                </div>

                {/* Progress bar toward 12h cap */}
                <div className="mb-1.5">
                  <div className="flex justify-between text-[8px] font-bold text-slate-500 mb-0.5">
                    <span>Acumulado estimado</span>
                    <span>
                      {stakingInfo.accrued_unclaimed.toFixed(2)} FRJ
                      {stakingInfo.cap_reached && (
                        <span className="text-red-400 ml-1">(¡Tope 12h!)</span>
                      )}
                    </span>
                  </div>
                  <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all duration-500 ${
                        stakingInfo.cap_reached
                          ? 'bg-gradient-to-r from-amber-500 to-red-500'
                          : 'bg-gradient-to-r from-amber-600 to-amber-400'
                      }`}
                      style={{
                        width: `${Math.min(100, (stakingInfo.accrued_unclaimed / (stakingInfo.hourly_rate * 12)) * 100)}%`,
                      }}
                    />
                  </div>
                </div>

                {/* Play-to-stake warning */}
                {!stakingInfo.play_to_stake_active && (
                  <div className="mb-2 rounded-lg bg-red-950/40 border border-red-500/20 p-2 text-center">
                    <span className="text-[9px] font-black text-red-300">
                      ⏸️ Juega una partida para reactivar el staking
                    </span>
                  </div>
                )}

                {/* Claim button */}
                <button
                  onClick={async () => {
                    if (!token || claimingStaking) return;
                    setClaimingStaking(true);
                    try {
                      const res = await claimAxolotitoStaking(axo.id, token);
                      const multText = res.multiplier && res.multiplier !== 1.0 ? ` (¡Encontraste un bono de ${res.multiplier}x!)` : '';
                      toast.ok(`🪙 Reclamaste ${res.claimed_frj.toFixed(2)} FRJ de staking${multText}`);
                      if (onStakingClaimed) onStakingClaimed();
                      onClose();
                    } catch (e: any) {
                      toast.error(e.response?.data?.detail || 'Error al reclamar staking');
                    } finally {
                      setClaimingStaking(false);
                    }
                  }}
                  disabled={claimingStaking || stakingInfo.accrued_unclaimed <= 0.01}
                  className="w-full py-2.5 rounded-xl font-black text-[9px] uppercase tracking-wider bg-gradient-to-r from-amber-600 to-orange-600 hover:from-amber-500 hover:to-orange-500 text-white transition-all active:scale-95 disabled:opacity-50 flex items-center justify-center gap-1"
                >
                  {claimingStaking ? 'Reclamando…' : `🪙 Reclamar ${stakingInfo.accrued_unclaimed.toFixed(2)} FRJ`}
                </button>

                {/* Unstake button */}
                <button
                  onClick={handleUnstake}
                  disabled={unstaking || remainingLock > 0}
                  className="w-full mt-2 py-2 rounded-xl font-black text-[9px] uppercase tracking-wider bg-slate-800/80 border border-slate-700/60 text-slate-300 hover:text-white hover:bg-slate-700/80 transition-all active:scale-95 disabled:opacity-50 flex items-center justify-center gap-1"
                >
                  {unstaking
                    ? 'Retirando…'
                    : remainingLock > 0
                      ? `⏳ Ocupado (${Math.floor(remainingLock / 60)}:${String(remainingLock % 60).padStart(2, '0')})`
                      : 'Hacer que vuelva a la Cueva'}
                </button>
              </div>
            )}

            {/* Invite to stake when idle */}
            {stakingInfo && axo.status === 'idle' && (
              <div className="mb-4 rounded-2xl bg-gradient-to-br from-slate-900/60 to-slate-950/40 border border-slate-800 p-4">
                <div className="flex items-center gap-1.5 mb-2.5">
                  <span className="text-sm">📈</span>
                  <span className="text-[10px] font-black text-slate-300 uppercase tracking-wider">
                    Actividades Pasivas (FRJ)
                  </span>
                </div>
                <p className="text-[10px] text-slate-500 mb-3 font-medium leading-relaxed">
                  Envía a tu Axolotito a una actividad en el Cenote. Tasa base: <span className="text-amber-400 font-bold">+{stakingInfo.hourly_rate.toFixed(2)} FRJ/h</span>.
                </p>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleStake('studying')}
                    disabled={staking}
                    className="flex-1 py-2.5 rounded-xl font-black text-[9px] uppercase tracking-wider bg-purple-950/40 border border-purple-500/30 text-purple-300 hover:bg-purple-900/30 transition-all active:scale-95 disabled:opacity-50 flex items-center justify-center gap-1"
                  >
                    🏪 Tianguis
                  </button>
                  <button
                    onClick={() => handleStake('resting')}
                    disabled={staking}
                    className="flex-1 py-2.5 rounded-xl font-black text-[9px] uppercase tracking-wider bg-teal-950/40 border border-teal-500/30 text-teal-300 hover:bg-teal-900/30 transition-all active:scale-95 disabled:opacity-50 flex items-center justify-center gap-1"
                  >
                    🧹 Limpiar Cenote
                  </button>
                </div>
              </div>
            )}

            {/* En Juego banner — axolotito está en partida multijugador */}
            {axo.status === 'playing' && (
              <div className="mb-4 rounded-2xl bg-red-950/50 border-2 border-red-500/40 p-4 animate-pulse">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">⚔️</span>
                  <div>
                    <div className="text-[11px] font-black text-red-300 uppercase tracking-wider">
                      En Juego — Multijugador
                    </div>
                    <p className="text-[9px] text-red-400/80 mt-0.5 leading-relaxed">
                      Este Axolotito está participando en una partida multijugador.
                      Las acciones están bloqueadas hasta que termine.
                    </p>
                  </div>
                </div>
              </div>
            )}

            {error && (
              <div className="mb-3 rounded-xl p-3 bg-red-900/30 border border-red-500/30 text-xs text-red-400 font-medium">
                {error}
              </div>
            )}

            {/* Quick actions: feed + sleep — bloqueadas si está en juego */}
            <div className="grid grid-cols-2 gap-2 mb-2">
              <button
                onClick={async () => {
                  if (axo.status === 'playing') return;
                  try {
                    await feedAxolotito(axo.id, 'pellet', token);
                    toast.ok('🍥 +15 energía (Alga Pellet)');
                    onSetMain?.();
                    onClose();
                  } catch (e: any) { toast.error(e.response?.data?.detail || 'Error al alimentar'); }
                }}
                disabled={axo.status === 'playing' || axo.status === 'sleeping'}
                className="py-2.5 rounded-xl font-black text-[9px] uppercase tracking-wider bg-emerald-900/40 hover:bg-emerald-800/40 border border-emerald-500/30 text-emerald-300 transition-all active:scale-95 disabled:opacity-30 disabled:cursor-not-allowed flex items-center justify-center gap-1"
              >
                🍥 Alimentar
              </button>
              {axo.status === 'sleeping' ? (
                <button
                  onClick={async () => {
                    if (axo.status === 'playing') return;
                    try {
                      await wakeAxolotito(axo.id, token);
                      toast.ok('☀️ Axolotito despierto con energía completa!');
                      onSetMain?.();
                      onClose();
                    } catch (e: any) { toast.error(e.response?.data?.detail || 'Error al despertar'); }
                  }}
                  disabled={axo.status === 'playing'}
                  className="py-2.5 rounded-xl font-black text-[9px] uppercase tracking-wider bg-amber-900/40 hover:bg-amber-800/40 border border-amber-500/30 text-amber-300 transition-all active:scale-95 disabled:opacity-30 disabled:cursor-not-allowed flex items-center justify-center gap-1 animate-pulse"
                >
                  ☀️ Despertar
                </button>
              ) : (
                <button
                  onClick={async () => {
                    if (axo.status === 'playing') return;
                    try {
                      await sleepAxolotito(axo.id, token);
                      toast.ok('💤 Axolotito durmiendo');
                      onSetMain?.();
                      onClose();
                    } catch (e: any) { toast.error(e.response?.data?.detail || 'Error al dormir'); }
                  }}
                  disabled={axo.status === 'playing'}
                  className="py-2.5 rounded-xl font-black text-[9px] uppercase tracking-wider bg-indigo-900/40 hover:bg-indigo-800/40 border border-indigo-500/30 text-indigo-300 transition-all active:scale-95 disabled:opacity-30 disabled:cursor-not-allowed flex items-center justify-center gap-1"
                >
                  💤 Dormir
                </button>
              )}
            </div>

            {/* Enter cave CTA */}
            {onOpenCave && (
              <button
                onClick={() => { onClose(); onOpenCave(axo); }}
                className="w-full mb-2 py-3 rounded-2xl font-black uppercase text-xs tracking-widest bg-gradient-to-r from-slate-800 to-slate-700 hover:from-slate-700 hover:to-slate-600 border border-[#2DD4BF]/40 text-[#2DD4BF] transition-all active:scale-95 flex items-center justify-center gap-1.5 shadow-[0_0_12px_rgba(45,212,191,0.15)]"
              >
                <Package size={12} />
                Entrar a la Cueva
              </button>
            )}

            {!axo.is_main && token && (
              <button
                onClick={handleSetMain}
                disabled={settingMain}
                className="w-full mb-2 py-3 rounded-2xl font-black uppercase text-xs tracking-widest bg-teal-600 hover:bg-teal-500 disabled:opacity-50 border border-teal-500 text-white transition-all active:scale-95 flex items-center justify-center gap-1.5"
              >
                <Crown size={12} />
                {settingMain ? 'Cargando...' : 'Designar como Principal'}
              </button>
            )}

            <button onClick={onClose} className="w-full py-3 rounded-2xl font-black uppercase text-xs tracking-widest bg-slate-800/80 hover:bg-slate-700 border border-slate-700 text-slate-300 hover:text-white transition-all active:scale-95">
              Cerrar
            </button>
          </div>
    </BottomSheet>
  );
}
