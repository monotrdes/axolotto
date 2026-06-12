"use client";
import React, { useState, useEffect, useRef } from 'react';
import { useToast } from '@/context/ToastContext';
import BottomSheet from '@/components/ui/BottomSheet';
import HostingSetupModal from '@/components/HostingSetupModal';
import { SpotSlot, SelectedSlot } from '@/types/santuario';
import type { StakingStatus } from '@/types/economy';
import {
  fetchCaveStatus, fetchIncubaciones, fetchAxolotitos, hatchEgg as hatchEggApi,
  fetchLegacyStatus, claimLegacy,
  fetchStakingStatus, claimAllStaking, expandCave, accelerateCave,
  startImprinting,
} from '@/services/santuarioService';
import ZonaInferior from '@/components/santuario/ZonaInferior';
import { useSocial } from '@/hooks/useSocial';
import EggSheet from '@/components/santuario/EggSheet';
import AxoSheet from '@/components/santuario/AxoSheet';
import CaveRoomModal from '@/components/santuario/CaveRoomModal';
import HatchSheet from '@/components/santuario/HatchSheet';

// ═══════════════════════════════════════════════════════
// MAIN: SANTUARIO
// ═══════════════════════════════════════════════════════
export default function Santuario({
  userId,
  token,
  cambiarTab,
  vipTier,
  initialSelectedSlotId,
  onClearSelectedSlot,
}: {
  userId: string;
  token: string | null;
  cambiarTab?: (tab: string) => void;
  vipTier?: string | null;
  initialSelectedSlotId?: { type: 'egg' | 'axo' | 'empty'; id?: number | string } | null;
  onClearSelectedSlot?: () => void;
}) {
  const { toast } = useToast();
  // ── Data states ──────────────────────────────────────
  const [incubaciones, setIncubaciones] = useState<any[]>([]);
  const [axolotitos,   setAxolotitos]   = useState<any[]>([]);
  const [clima,        setClima]        = useState<any>(null);
  const [cargando,     setCargando]     = useState(true);

  // ── Cave expansion state ─────────────────────────────
  const [caveLevel,   setCaveLevel]   = useState(1);
  const [hasTable,    setHasTable]    = useState(false);
  const [tableSeats,  setTableSeats]  = useState(0);
  const [caveName,    setCaveName]    = useState<string | null>(null);
  const [viewMode,    setViewMode]    = useState<'libre' | 'gestion'>('libre');
  const [caveExpansion, setCaveExpansion] = useState<any>(null);
  const [nextLevel,     setNextLevel]     = useState<any>(null);
  const [allLevels,     setAllLevels]     = useState<any[]>([]);
  const [passiveBonuses, setPassiveBonuses] = useState<any>({});
  const [caveStats,       setCaveStats]       = useState<any>({});
  const [caveWallet,      setCaveWallet]      = useState<any>({});



  // ── Interaction states ───────────────────────────────
  const [interactuando, setInteractuando] = useState<number | null>(null);
  const [particulas,    setParticulas]    = useState<{ id: number; incId: number; tipo: string; x: number; y: number; cLeft?: number; cBottom?: number }[]>([]);

  // ── Hatch states ─────────────────────────────────────
  const [hatchingId,     setHatchingId]     = useState<number | null>(null);
  const [nuevoAxolotito, setNuevoAxolotito] = useState<any | null>(null);



  // ── Legacy ───────────────────────────────────────────
  const [legacyStatus, setLegacyStatus] = useState<any | null>(null);
  const [reclamando,   setReclamando]   = useState(false);

  // ── Staking ──────────────────────────────────────────
  const [stakingData,   setStakingData]   = useState<StakingStatus | null>(null);
  const [claimingAll,   setClaimingAll]   = useState(false);

  // ── Selected slot (for bottom sheets) ────────────────
  const [selectedSlot, setSelectedSlot] = useState<SelectedSlot | null>(null);

  // ── Cave room modal ───────────────────────────────────
  const [activeCaveAxo, setActiveCaveAxo] = useState<any | null>(null);

  // ── Expansion panel ───────────────────────────────────
  const [cavesPanelOpen, setCavesPanelOpen] = useState(false);
  const [expandingCave, setExpandingCave] = useState(false);
  const [acceleratingCave, setAcceleratingCave] = useState(false);
  const [caveShaking, setCaveShaking] = useState(false);
  const [caveMuddy, setCaveMuddy] = useState(false);

  // ── Decoration mode ───────────────────────────────────
  const [decoMode, setDecoMode] = useState(false);

  // ── Hosting modal ─────────────────────────────────────
  const [hostingModalOpen, setHostingModalOpen] = useState(false);

  // ── Social (friends) ──
  const { fetchTopFriends, sendLike } = useSocial(token);
  const [amigosActivos, setAmigosActivos] = useState<any[]>([]);

  useEffect(() => {
    if (!token) return;
    fetchTopFriends(4).then(setAmigosActivos).catch(() => {});
  }, [token, fetchTopFriends]);

  // ── Reload trigger & cooldown tick ───────────────────
  const [recargaTrigger, setRecargaTrigger] = useState(0);
  const [, setTickCooldown] = useState(0);

  // ── Click queue ref ──────────────────────────────────
  const clicksPendientes = useRef<Record<number, number>>({});

  // ── Cave expand handler ──────────────────────────────
  const handleExpandCave = async () => {
    if (!token || expandingCave) return;
    setExpandingCave(true);
    try {
      const res = await expandCave(token);
      // Shake leve al iniciar excavación
      setCaveShaking(true);
      setTimeout(() => setCaveShaking(false), 700);
      setRecargaTrigger(t => t + 1);
      toast.ok(res.message || '¡Cenote expandido!');
    } catch (e: any) {
      toast.error(e.response?.data?.detail || 'No se pudo expandir el Cenote.');
    } finally {
      setExpandingCave(false);
    }
  };

  // ── Cave accelerate handler ──────────────────────────
  const handleAccelerateCave = async () => {
    if (!token || acceleratingCave) return;
    setAcceleratingCave(true);
    try {
      const res = await accelerateCave(token);
      if (res.completed) {
        setCaveShaking(true);
        setCaveMuddy(true);
        setTimeout(() => setCaveShaking(false), 700);
        setTimeout(() => setCaveMuddy(false), 1900);
      }
      toast.ok(res.message || '¡Excavación acelerada!');
      setRecargaTrigger(t => t + 1);
    } catch (e: any) {
      toast.error(e.response?.data?.detail || 'No se pudo acelerar la excavación.');
    } finally {
      setAcceleratingCave(false);
    }
  };

  // ── Fetch cave status ────────────────────────────────
  useEffect(() => {
    if (!userId) return;
    const load = async () => {
      try {
        const d = await fetchCaveStatus(userId, token);
        setCaveLevel(d.current?.level ?? 1);
        setHasTable(d.current?.has_table ?? false);
        setTableSeats(d.current?.table_seats ?? 0);
        setCaveName(d.cave_name ?? null);
        setCaveExpansion(d.expansion ?? null);
        setNextLevel(d.next_level ?? null);
        setAllLevels(d.all_levels ?? []);
        setPassiveBonuses(d.passive_bonuses ?? {});
        setCaveStats(d.stats ?? {});
        setCaveWallet(d.wallet ?? {});
      } catch (e) {
        console.warn('Cave status fetch failed, using defaults:', e);
      }
    };
    load();
  }, [userId, token, recargaTrigger]);

  // ── Fetch incubaciones ───────────────────────────────
  useEffect(() => {
    if (!userId) return;
    const load = async () => {
      setCargando(true);
      try {
        const data = await fetchIncubaciones(userId, token);
        setIncubaciones(data);
      } catch (e) { console.error('Error cargando El Nido:', e); }
      finally { setCargando(false); }
    };
    load();
  }, [userId, token, recargaTrigger]);

  // ── Fetch axolotitos ─────────────────────────────────
  useEffect(() => {
    if (!userId) return;
    const load = async () => {
      try {
        const data = await fetchAxolotitos(userId, token);
        setAxolotitos(data || []);
      } catch (e) { console.error('Error cargando axolotitos:', e); }
    };
    load();
  }, [userId, token, recargaTrigger]);

  // ── Auto-open bottom sheet for 2.5D diorama (initialSelectedSlotId prop) ──
  useEffect(() => {
    if (!initialSelectedSlotId) return;
    const { type, id } = initialSelectedSlotId;
    if (type === 'egg' && id && incubaciones.length > 0) {
      const inc = incubaciones.find(i => String(i.id) === String(id));
      if (inc) {
        setSelectedSlot({ type: 'egg', data: inc });
      }
    } else if (type === 'axo' && id && axolotitos.length > 0) {
      const axo = axolotitos.find(a => String(a.id) === String(id));
      if (axo) {
        setSelectedSlot({ type: 'axo', data: axo });
      }
    } else if (type === 'empty') {
      setSelectedSlot({ type: 'empty', data: null });
    }
  }, [initialSelectedSlotId, incubaciones, axolotitos]);

  // ── Fetch staking status ──────────────────────────────
  useEffect(() => {
    if (!userId) return;
    const load = async () => {
      try {
        const data = await fetchStakingStatus(userId, token);
        setStakingData(data);
      } catch (e) { console.error('Error cargando staking:', e); }
    };
    load();
  }, [userId, token, recargaTrigger]);

  // ── Fetch legacy status ─────────────────────────────
  useEffect(() => {
    if (!userId) return;
    const load = async () => {
      try {
        const legacyData = await fetchLegacyStatus(userId, token);
        setLegacyStatus(legacyData);
      } catch (e) { console.error('Error en datos legacy:', e); }
    };
    load();
  }, [userId, token, recargaTrigger]);

  // ── Cooldown UI tick (30s) ───────────────────────────
  useEffect(() => {
    const t = setInterval(() => setTickCooldown(p => p + 1), 30_000);
    return () => clearInterval(t);
  }, []);

  // ── ACTIONS ──────────────────────────────────────────
  const handleHatchEgg = async (incId: number) => {
    setHatchingId(incId);
    try {
      const res = await hatchEggApi(incId, token);
      setNuevoAxolotito(res.axolotito);
      setIncubaciones(prev => prev.filter(inc => inc.id !== incId));
      setSelectedSlot(null);
    } catch (e: any) {
      toast.error(e.response?.data?.detail || 'Error al eclosionar');
    } finally {
      setHatchingId(null);
    }
  };

  const handleStartImprinting = async (incId: number, padrinoId: number) => {
    try {
      const res = await startImprinting(incId, padrinoId, token);
      toast.ok(res.message || '🐾 ¡Apadrinamiento iniciado!');
      setSelectedSlot(null);
      setRecargaTrigger(p => p + 1);
    } catch (e: any) {
      toast.error(e.response?.data?.detail || 'Error al iniciar apadrinamiento');
    }
  };

  const reclamarLegacy = async () => {
    setReclamando(true);
    try {
      const res = await claimLegacy(userId, token);
      toast.ok(`🥚 ${res.mensaje}`);
      setLegacyStatus((prev: any) => prev
        ? { ...prev, eggs_pending: prev.eggs_pending - 1, eggs_claimed: prev.eggs_claimed + 1 }
        : prev
      );
      setRecargaTrigger(p => p + 1);
    } catch (e: any) {
      toast.error(e.response?.data?.detail || 'Error al reclamar el huevo.');
    } finally {
      setReclamando(false);
    }
  };

  const handleClaimAllStaking = async () => {
    if (!token || claimingAll || !stakingData || stakingData.total_accrued < 0.01) return;
    setClaimingAll(true);
    try {
      const res = await claimAllStaking(token);
      const amount = res.amount_claimed || stakingData.total_accrued;
      toast.ok(`🪙 ¡Cobraste ${amount.toFixed(2)} FRJ de staking de todos tus Axolotitos!`);
      setRecargaTrigger(p => p + 1);
    } catch (e: any) {
      toast.error(e.response?.data?.detail || 'Error al cobrar staking');
    } finally {
      setClaimingAll(false);
    }
  };

  // ── BUILD SPOTS: bedrooms (axolotitos) + nests (eggs) ──
  // Cada axolotito tiene su dormitorio fijo. Los spots restantes (caveLevel)
  // son para incubar webitos. Así los axos nunca se quedan sin habitación.
  const axoBedrooms = axolotitos.length;
  const nestSlots = Math.max(caveLevel, 1);
  const totalSpots = axoBedrooms + nestSlots;
  const spots: SpotSlot[] = Array.from({ length: totalSpots }, (_, i) => {
    // ── Primeros slots: dormitorios de axolotitos (fijos, uno por axo) ──
    if (i < axoBedrooms) {
      const axo = axolotitos[i];
      if (viewMode === 'gestion') {
        return { type: 'axo', data: axo };
      }
      return { type: 'bed', data: axo };
    }
    // ── Slots restantes: nidos de incubación (hasta caveLevel) ──
    const eggIndex = i - axoBedrooms;
    if (eggIndex < incubaciones.length) {
      return { type: 'egg', data: incubaciones[eggIndex] };
    }
    return { type: 'empty', data: null };
  });

  // ── LOADING ──────────────────────────────────────────
  if (cargando) {
    return (
      <div className="flex items-center justify-center h-screen gap-3 flex-col">
        <span className="text-4xl animate-bounce">🪺</span>
        <p className="text-[#E4007C] font-black uppercase tracking-widest text-sm animate-pulse">
          Preparando el Nido…
        </p>
      </div>
    );
  }

  // ── RENDER ───────────────────────────────────────────
  return (
    <div className={`flex flex-col h-screen w-full max-w-[430px] mx-auto overflow-hidden${caveShaking ? ' animate-cave-shake' : ''} pointer-events-none`}>

      {/* === ESCENA CENTRAL === */}
      {/* Ya no renderizamos la escena 2D de React (ZonaCentral), permitiendo ver e interactuar con la escena 3D/Pixi de fondo */}
      <div className="flex-1 relative pointer-events-none" />

      {/* Expand cave button — flotando top-left */}
      <button
        onClick={() => setCavesPanelOpen(true)}
        className="absolute top-3 left-3 z-[90] px-2.5 py-1 rounded-full bg-black/60 backdrop-blur-sm border border-white/10 text-[8px] font-black text-slate-400 hover:text-amber-300 hover:border-amber-500/30 transition-all pointer-events-auto"
      >
        ⛏️ {caveExpansion ? '⏳' : 'Nv.' + caveLevel}
      </button>

      {/* Staking chip — flotando bottom-left cuando activo */}
      {stakingData && stakingData.total_accrued > 0 && (
        <div className="absolute bottom-3 left-3 z-[90] flex items-center gap-2 px-3 py-1.5 rounded-full bg-amber-950/90 border border-amber-500/30 backdrop-blur-sm shadow-lg pointer-events-auto">
          <span className="text-[9px] font-black text-amber-300">
            🪙 +{stakingData.total_accrued.toFixed(2)} FRJ
          </span>
          <button
            onClick={handleClaimAllStaking}
            disabled={claimingAll || stakingData.total_accrued < 0.01}
            className="px-2 py-0.5 rounded-full font-black text-[8px] bg-amber-600 hover:bg-amber-500 text-white transition-all active:scale-95 disabled:opacity-40 pointer-events-auto"
          >
            {claimingAll ? '…' : 'Cobrar'}
          </button>
        </div>
      )}

      {/* === ZONA INFERIOR — SOCIAL BAR === */}
      <div className="pointer-events-auto">
        <ZonaInferior
          amigos={amigosActivos.map((f: any) => ({
            id: f.friend_id,
            name: f.nickname || "Jugador",
            avatarEmoji: f.vip_tier === "axolite" ? "👑" : f.vip_tier === "dorado" ? "💛" : "🦎",
            isOnline: f.is_online,
            isBestFriend: f.is_best_friend,
          }))}
          onOpenAmigos={() => cambiarTab && cambiarTab('amigos')}
          onLike={async (amigoId: string) => {
            try {
              await sendLike(amigoId);
              fetchTopFriends(4).then(setAmigosActivos).catch(() => {});
            } catch {}
          }}
          onInvite={(_amigoId: string) => {
            cambiarTab && cambiarTab('jugar');
          }}
          onVisit={(_amigoId: string) => {
            cambiarTab && cambiarTab('amigos');
          }}
        />
      </div>

      {/* caveMuddy overlay — fixed overlay */}
      {caveMuddy && <div className="cave-muddy-overlay fixed inset-0 pointer-events-none z-[200]" />}

      {/* ── LEGACY BACKERS BANNER — fixed overlay ── */}
      {legacyStatus?.is_legacy_backer && legacyStatus?.eggs_pending > 0 && (
        <div className="fixed inset-0 z-[115] flex items-end justify-center bg-black/60 pointer-events-auto">
          <div className="w-full max-w-[430px] bg-gradient-to-r from-amber-950/90 via-yellow-900/80 to-amber-950/90 border-2 border-amber-500/60 rounded-t-3xl p-5 shadow-[0_0_30px_rgba(245,158,11,0.2)] flex flex-col items-center gap-2 text-center">
            <div className="text-xl">🥚✨</div>
            <h3 className="text-sm font-black text-amber-300 uppercase tracking-wider">¡Eres un Fundador Original!</h3>
            <p className="text-amber-200/70 text-[11px]">
              Tienes <span className="font-black text-amber-300">{legacyStatus.eggs_pending}</span> Webito(s) Fundador(es) esperándote.
            </p>
            <button
              onClick={reclamarLegacy}
              disabled={reclamando}
              className="mt-1 px-6 py-2.5 bg-gradient-to-r from-amber-500 to-yellow-400 hover:from-amber-400 hover:to-yellow-300 text-slate-900 font-black rounded-full uppercase tracking-widest text-[11px] shadow-amber-500/40 shadow-lg active:scale-95 transition-all disabled:opacity-50"
            >
              {reclamando ? 'Reclamando…' : '🎁 Reclamar Webito Fundador Gratis'}
            </button>
          </div>
        </div>
      )}

      {/* ── BOTTOM SHEETS & MODALS ── */}
      <div className="pointer-events-auto">
        {selectedSlot?.type === 'egg' && (
          <EggSheet
            inc={selectedSlot.data}
            axolotitos={axolotitos}
            onClose={() => {
              setSelectedSlot(null);
              onClearSelectedSlot?.();
            }}
            onHatch={handleHatchEgg}
            onStartImprinting={handleStartImprinting}
            hatchingId={hatchingId}
          />
        )}

        {(selectedSlot?.type === 'axo' || selectedSlot?.type === 'bed') && (
          <AxoSheet
            axo={selectedSlot.data}
            onClose={() => {
              setSelectedSlot(null);
              onClearSelectedSlot?.();
            }}
            token={token}
            onSetMain={() => setRecargaTrigger(prev => prev + 1)}
            onOpenCave={(axo) => setActiveCaveAxo(axo)}
            stakingInfo={
              stakingData?.axolotitos?.find((s) => s.id === selectedSlot.data.id) ?? null
            }
            onStakingClaimed={() => setRecargaTrigger(p => p + 1)}
          />
        )}

        <BottomSheet
          open={selectedSlot?.type === 'empty'}
          onClose={() => {
            setSelectedSlot(null);
            onClearSelectedSlot?.();
          }}
        >
          <div className="p-6 flex flex-col items-center gap-4">
            <span className="text-4xl">🪺</span>
            <div className="text-center">
              <h3 className="text-lg font-black text-white uppercase tracking-tighter">Nido Vacío</h3>
              <p className="text-slate-400 text-sm mt-1 max-w-xs leading-relaxed">
                Consigue un Webito en la Tienda y tráelo aquí para comenzar la incubación.
              </p>
            </div>
            <button
              onClick={() => {
                setSelectedSlot(null);
                onClearSelectedSlot?.();
                cambiarTab && cambiarTab('tienda');
              }}
              className="w-full py-3.5 bg-gradient-to-r from-[#E4007C] to-purple-600 text-white font-black rounded-2xl uppercase tracking-widest text-xs shadow-lg shadow-pink-500/20 active:scale-95 transition-all"
            >
              🏪 Ir a la Tienda
            </button>
            <button onClick={() => setSelectedSlot(null)} className="text-slate-600 text-[10px] font-bold uppercase tracking-widest">
              Cerrar
            </button>
          </div>
        </BottomSheet>

        {/* ── HATCH SHEET ── */}
        {nuevoAxolotito && (
          <HatchSheet
            axolotito={nuevoAxolotito}
            onClose={() => { setNuevoAxolotito(null); setRecargaTrigger(p => p + 1); }}
          />
        )}

        {/* ── CAVE ROOM MODAL ── */}
        {activeCaveAxo && (
          <CaveRoomModal
            axo={activeCaveAxo}
            token={token}
            userId={userId}
            onClose={() => setActiveCaveAxo(null)}
          />
        )}
      </div>

      {/* ── EXPANSION PANEL V3: Camino del Cenote ── */}
      {cavesPanelOpen && (() => {
        const stats = caveStats;
        const wal = caveWallet;
        const checkLogro = (label: string): boolean => {
          let ok = true;
          // Partidas jugadas — extrae número exacto antes de la palabra "partidas"
          const gamesMatch = label.match(/(\d+)\s*partidas/);
          if (gamesMatch) {
            ok = ok && (stats.total_games || 0) >= parseInt(gamesMatch[1]);
          }
          // FRJ acumulados — extrae número exacto antes de " FRJ"
          const frjMatch = label.match(/(\d+)\s*FRJ/);
          if (frjMatch) {
            ok = ok && (wal.frijolitos || 0) >= parseInt(frjMatch[1]);
          }
          // Victorias
          if (label.includes('victorias') || label.match(/Gana \d+ partidas/)) {
            const m = label.match(/Gana (\d+)/);
            ok = ok && (stats.total_wins || 0) >= parseInt(m?.[1] || '3');
          }
          // Racha diaria
          const rachaMatch = label.match(/racha de (\d+)/);
          if (rachaMatch) {
            ok = ok && (stats.current_streak || 0) >= parseInt(rachaMatch[1]);
          }
          // Jackpot
          if (label.toLowerCase().includes('jackpot')) ok = ok && (stats.jackpots_won || 0) >= 1;
          // Nivel axolotito
          const nivelMatch = label.match(/nivel (\d+)/i);
          if (nivelMatch) ok = ok && (stats.main_axo_level || 0) >= parseInt(nivelMatch[1]);
          // VIP
          if (label.includes('VIP')) ok = ok && !!vipTier;
          // Si ninguna condición se aplicó, indeterminado → false
          if (!gamesMatch && !frjMatch && !label.includes('victorias') && !label.match(/Gana \d+/) &&
              !rachaMatch && !label.toLowerCase().includes('jackpot') && !nivelMatch && !label.includes('VIP')) {
            return false;
          }
          return ok;
        };
        return (
        <div className="fixed inset-0 z-[110] flex items-end justify-center bg-black/60" onClick={() => setCavesPanelOpen(false)}>
          <div className="bg-slate-900 rounded-t-3xl w-full max-w-md max-h-[80vh] overflow-y-auto flex flex-col" onClick={e => e.stopPropagation()}>
            <div className="flex justify-center pt-2 pb-1 shrink-0">
              <div className="w-10 h-1 rounded-full bg-slate-700" />
            </div>
            <div className="px-4 pb-5 pt-1 space-y-2.5">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-base font-black text-white">⛏️ Camino del Cenote</h3>
                  <p className="text-[9px] text-slate-500 font-bold uppercase tracking-wider">{caveName || 'Tu Cenote'} · Nivel {caveLevel}/8</p>
                </div>
                {caveExpansion && <span className="text-[8px] font-black text-amber-400 bg-amber-950/60 px-2 py-0.5 rounded-full animate-pulse border border-amber-500/30 shrink-0">⛏️ Excavando…</span>}
              </div>

              {/* CURRENT LEVEL */}
              <div className="bg-gradient-to-br from-teal-900/30 to-slate-800/40 border-2 border-teal-500/30 rounded-2xl p-3">
                <div className="flex items-center gap-2.5">
                  <div className="w-10 h-10 rounded-xl bg-teal-900/50 border-2 border-teal-500/40 flex items-center justify-center text-xl shrink-0 ring-2 ring-teal-500/10">{caveLevel === 1 ? '🪺' : caveLevel >= 7 ? '✨' : caveLevel >= 4 ? '💎' : '🪨'}</div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2"><span className="text-sm font-black text-teal-300">{caveLevel === 1 ? 'El Nicho' : allLevels.find(l => l.level === caveLevel)?.name || `Nv.${caveLevel}`}</span><span className="text-[7px] font-black text-teal-500 bg-teal-950/60 px-1.5 py-0.5 rounded border border-teal-500/20">ACTUAL</span></div>
                    <div className="text-[8px] text-slate-500 font-bold mt-0.5">🪺 {nestSlots} nido{nestSlots !== 1 ? 's' : ''} · 🛏️ {axoBedrooms} dormitorio{axoBedrooms !== 1 ? 's' : ''} · 🪸 {caveLevel > 1 ? caveLevel * 2 : 2} decor · {hasTable ? `🎴 ${tableSeats}p` : 'Sin mesa'}</div>
                  </div>
                </div>
                {Object.keys(passiveBonuses).length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-2 pt-2 border-t border-teal-500/10">
                    {passiveBonuses.frj_multiplier > 1 && <span className="text-[7px] font-black text-emerald-400 bg-emerald-950/50 px-1.5 py-0.5 rounded-full border border-emerald-500/20">+{Math.round((passiveBonuses.frj_multiplier-1)*100)}% FRJ</span>}
                    {passiveBonuses.extra_starting_card && <span className="text-[7px] font-black text-indigo-400 bg-indigo-950/50 px-1.5 py-0.5 rounded-full border border-indigo-500/20">+1 Carta</span>}
                    {passiveBonuses.sobrecito_chance_bonus > 0 && <span className="text-[7px] font-black text-purple-400 bg-purple-950/50 px-1.5 py-0.5 rounded-full border border-purple-500/20">+{Math.round(passiveBonuses.sobrecito_chance_bonus*100)}% Boosters</span>}
                    {passiveBonuses.axf_multiplier > 1 && <span className="text-[7px] font-black text-amber-300 bg-amber-950/50 px-1.5 py-0.5 rounded-full border border-amber-500/20">+{Math.round((passiveBonuses.axf_multiplier-1)*100)}% AXF</span>}
                  </div>
                )}
              </div>

              {/* EXCAVATION */}
              {caveExpansion && (() => {
                const hrs = Math.floor(caveExpansion.remaining_seconds / 3600);
                const mins = Math.floor((caveExpansion.remaining_seconds % 3600) / 60);
                const secs = caveExpansion.remaining_seconds % 60;
                const timeStr = hrs > 0
                  ? `${hrs}:${String(mins).padStart(2,'0')}:${String(secs).padStart(2,'0')}`
                  : `${mins}:${String(secs).padStart(2,'0')}`;
                const progressPct = Math.min(100, Math.max(0,
                  100 - (caveExpansion.remaining_seconds / (caveExpansion.total_hours * 3600)) * 100
                ));
                const axfCost = Math.ceil(caveExpansion.remaining_seconds / 3600 * 4);
                return (
                <div className="bg-amber-900/20 border border-amber-500/30 rounded-2xl p-3 animate-excavate">
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-[10px] font-black text-amber-300">⛏️ Excavando: {caveExpansion.target_name}</span>
                    <span className="text-[9px] font-black text-amber-400 font-mono tabular-nums">{timeStr}</span>
                  </div>
                  <div className="h-1.5 bg-slate-800 rounded-full overflow-hidden">
                    <div className="h-full bg-gradient-to-r from-amber-600 to-amber-400 rounded-full animate-pulse" style={{width:`${progressPct}%`}}/>
                  </div>
                  {/* Botón acelerar */}
                  {caveExpansion.can_accelerate && (
                    <button
                      disabled={acceleratingCave}
                      onClick={handleAccelerateCave}
                      className="w-full mt-2 py-1.5 rounded-lg bg-gradient-to-r from-amber-700 to-yellow-700 hover:from-amber-600 hover:to-yellow-600 disabled:opacity-50 text-white font-black text-[9px] uppercase tracking-wider transition-all active:scale-95"
                    >
                      {acceleratingCave
                        ? '⚡ Acelerando...'
                        : `⚡ Acelerar (${axfCost} AXF)`}
                    </button>
                  )}
                </div>
              )})()}

              {/* NEXT LEVEL */}
              {caveLevel < 8 && nextLevel ? (<>
                <div className="flex items-center gap-2">
                  <div className="w-7 h-7 rounded-full bg-teal-600 border-2 border-teal-400 flex items-center justify-center text-[9px] font-black text-white shrink-0">{caveLevel}</div>
                  <div className="flex-1 h-1 bg-slate-800 rounded-full overflow-hidden"><div className="h-full bg-gradient-to-r from-teal-500 to-amber-500 rounded-full" style={{width:caveExpansion?'65%':'8%'}}/></div>
                  <div className={`w-7 h-7 rounded-full border-2 flex items-center justify-center text-[9px] font-black shrink-0 ${caveExpansion?'bg-amber-900/60 border-amber-500 text-amber-300':'bg-slate-800 border-amber-500/30 text-amber-400'}`}>{caveLevel+1}</div>
                </div>
                <div className="bg-slate-800/60 border-2 border-amber-500/30 rounded-2xl p-3">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-lg shrink-0">{caveLevel+1===3?'🌿':caveLevel+1===4?'🎴':caveLevel+1===5?'💎':caveLevel+1===6?'🔮':caveLevel+1===7?'✨':'👑'}</span>
                    <div className="min-w-0"><div className="flex items-center gap-1.5"><span className="text-xs font-black text-amber-300">{nextLevel.name}</span><span className="text-[7px] font-black text-amber-500 bg-amber-950/60 px-1 py-0.5 rounded border border-amber-500/20">PRÓXIMO</span></div><p className="text-[8px] text-slate-500 italic truncate">"{nextLevel.lore?.slice(0,50)}…"</p></div>
                  </div>

                  <div className="text-[7px] font-black text-slate-500 uppercase tracking-widest mb-1.5">Al expandir ganas</div>
                  <div className="grid grid-cols-3 gap-1.5 mb-2.5">
                    <div className="bg-slate-900/60 rounded-xl p-2 text-center border border-white/5">
                      <div className="text-xl mb-0.5">🪺</div>
                      <div className="flex items-center justify-center gap-1">
                        <span className="text-[10px] font-black text-white">{nextLevel.spots}</span>
                        <span className="text-[8px] font-black text-teal-400">+{nextLevel.spots - nestSlots}</span>
                      </div>
                      <div className="text-[7px] text-slate-500 font-bold">Nidos</div>
                    </div>
                    <div className="bg-slate-900/60 rounded-xl p-2 text-center border border-white/5">
                      <div className="text-xl mb-0.5">🪸</div>
                      <div className="flex items-center justify-center gap-1">
                        <span className="text-[10px] font-black text-white">{nextLevel.decor_slots}</span>
                        <span className="text-[8px] font-black text-teal-400">+{nextLevel.decor_slots - (caveLevel > 1 ? caveLevel * 2 : 2)}</span>
                      </div>
                      <div className="text-[7px] text-slate-500 font-bold">Decoración</div>
                    </div>
                    <div className="bg-slate-900/60 rounded-xl p-2 text-center border border-white/5">
                      <div className="text-xl mb-0.5">{nextLevel.has_table?'🎴':'—'}</div>
                      <div className="flex items-center justify-center gap-1">
                        <span className="text-[10px] font-black text-white">{nextLevel.has_table?`${nextLevel.table_seats}p`:'—'}</span>
                        {nextLevel.has_table && (
                          <span className="text-[8px] font-black text-teal-400">
                            {hasTable ? `+${nextLevel.table_seats - tableSeats}` : '+nueva'}
                          </span>
                        )}
                      </div>
                      <div className="text-[7px] text-slate-500 font-bold">Mesa</div>
                    </div>
                  </div>

                  <div className="text-[7px] font-black text-slate-500 uppercase tracking-widest mb-1.5">Requisito de expansión</div>
                  <div className="space-y-1.5">
                    {nextLevel.paths?.filter((p:any)=>p.type==='logro').map((p:any,i:number)=>{
                      const met = nextLevel.achievement_met ?? checkLogro(p.label);
                      const subConditions = p.label.split(/\s*\+\s*/).map((s: string) => s.trim()).filter(Boolean);
                      return (
                        <div key={i} className={`flex flex-col gap-1.5 p-2 rounded-xl text-[9px] font-bold border ${met?'bg-emerald-900/20 border-emerald-500/30':'bg-slate-900/40 border-white/5'}`}>
                          {subConditions.length > 1 ? (
                            <div className="space-y-1">
                              {subConditions.map((cond: string, ci: number) => {
                                const condMet = checkLogro(cond);
                                return (
                                  <div key={ci} className={`flex items-center gap-2 ${condMet ? 'text-emerald-300' : 'text-slate-400'}`}>
                                    <span className="text-[11px] shrink-0">{condMet ? '✅' : '⬜'}</span>
                                    <span className="leading-tight flex-1">{cond}</span>
                                  </div>
                                );
                              })}
                            </div>
                          ) : (
                            <div className={`flex items-center gap-2 ${met ? 'text-emerald-300' : 'text-slate-400'}`}>
                              <span className="text-[11px] shrink-0">{met ? '✅' : '⬜'}</span>
                              <span className="leading-tight flex-1">{p.label}</span>
                            </div>
                          )}
                          {met && !caveExpansion && (
                            <>
                              {/* Costo FRJ para iniciar */}
                              <div className="flex items-center justify-between text-[8px] font-bold mt-1.5 mb-1">
                                <span className="text-slate-500">💧 Costo de excavación:</span>
                                <div className="flex items-center gap-1">
                                  {nextLevel.cost_frj_effective < nextLevel.cost_frj && (
                                    <span className="text-slate-600 line-through">{nextLevel.cost_frj?.toLocaleString()}</span>
                                  )}
                                  <span className={`font-black ${(wal.frijolitos || 0) >= (nextLevel.cost_frj_effective ?? nextLevel.cost_frj ?? 0) ? 'text-emerald-400' : 'text-red-400'}`}>
                                    {(nextLevel.cost_frj_effective ?? nextLevel.cost_frj ?? 0).toLocaleString()} FRJ
                                  </span>
                                  {nextLevel.cost_frj_effective < nextLevel.cost_frj && (
                                    <span className="text-[7px] text-amber-400 bg-amber-950/50 px-1 py-0.5 rounded border border-amber-500/20 font-black">VIP -50%</span>
                                  )}
                                </div>
                              </div>
                              <button
                                disabled={expandingCave || (wal.frijolitos || 0) < (nextLevel.cost_frj_effective ?? nextLevel.cost_frj ?? 0)}
                                onClick={() => handleExpandCave()}
                                className="w-full py-1.5 rounded-lg bg-gradient-to-r from-emerald-700 to-teal-700 hover:from-emerald-600 hover:to-teal-600 disabled:opacity-50 text-white font-black text-[9px] uppercase tracking-wider transition-all"
                              >
                                {expandingCave ? '⛏️ Iniciando…' : '⛏️ Iniciar Excavación'}
                              </button>
                            </>
                          )}
                        </div>
                      );
                    })}
                  </div>
                  {nextLevel.excavation_hours && (
                    <div className="text-center text-[8px] text-slate-600 font-bold mt-2 pt-2 border-t border-white/5">
                      ⏱️ {nextLevel.excavation_hours_effective && nextLevel.excavation_hours_effective < nextLevel.excavation_hours
                        ? <><span className="line-through mr-1">{nextLevel.excavation_hours}h</span><span className="text-amber-400">{nextLevel.excavation_hours_effective}h VIP</span></>
                        : `${nextLevel.excavation_hours}h`
                      } · acelera con AXF (4 AXF/h)
                    </div>
                  )}
                </div>
              </>) : caveLevel>=8 ? (
                <div className="bg-gradient-to-br from-amber-900/30 to-yellow-900/20 border border-amber-500/30 rounded-2xl p-4 text-center"><div className="text-2xl mb-1">👑</div><p className="text-xs font-black text-amber-300">¡Palacio Astral! Nivel máximo.</p></div>
              ) : null}

              {/* TIMELINE */}
              <div>
                <div className="text-[7px] font-black text-slate-600 uppercase tracking-widest mb-1.5">Todos los niveles</div>
                <div className="flex gap-1.5 overflow-x-auto pb-1 -mx-1 px-1 scrollbar-hide">
                  {allLevels.map((lvl:any)=>{
                    const isCurrent=lvl.level===caveLevel;
                    const isNext=lvl.level===caveLevel+1;
                    const isUnlocked=lvl.unlocked;
                    return (
                      <div key={lvl.level} className={`shrink-0 w-[72px] rounded-xl p-2 text-center transition-all group cursor-default ${
                        isCurrent?'bg-teal-900/50 border-2 border-teal-500/50 ring-1 ring-teal-500/20':
                        isNext?'bg-amber-900/30 border-2 border-amber-500/40':
                        isUnlocked?'bg-slate-800/40 border border-white/5':
                        'bg-slate-800/10 border border-white/3 opacity-40'}`}>
                        <div className={`w-7 h-7 rounded-full flex items-center justify-center text-[9px] font-black mx-auto mb-1 ${
                          isCurrent?'bg-teal-600 text-white':isUnlocked?'bg-teal-900/60 text-teal-400':'bg-slate-800 text-slate-600'}`}>
                          {isUnlocked?'✓':lvl.level}
                        </div>
                        <div className={`text-[7px] font-black leading-tight mb-0.5 ${isCurrent?'text-teal-300':isNext?'text-amber-300':isUnlocked?'text-slate-300':'text-slate-600'}`}>{lvl.name}</div>
                        <div className="flex justify-center gap-1 text-[7px] text-slate-500 font-bold">
                          <span>🪺{lvl.spots}</span>
                          {lvl.has_table&&<span>🎴</span>}
                        </div>
                        {!isUnlocked && !isCurrent && (
                          <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-1 w-36 bg-slate-800 border border-slate-700 rounded-xl p-2 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-50 shadow-xl">
                            <p className="text-[7px] font-black text-slate-300 mb-0.5">{lvl.name}</p>
                            <p className="text-[6px] text-slate-500 leading-tight">🪺 {lvl.spots} spots · 🪸 {lvl.decor_slots} decor</p>
                            {lvl.has_table&&<p className="text-[6px] text-slate-500 leading-tight">🎴 Mesa {lvl.table_seats} jugadores</p>}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>

              <button onClick={()=>setCavesPanelOpen(false)} className="w-full py-2 rounded-xl bg-slate-800 text-slate-400 hover:text-white font-bold text-[10px] transition-all shrink-0">Cerrar</button>
            </div>
          </div>
        </div>
      )})()}

      {/* ── HOSTING SETUP MODAL ── */}
      <HostingSetupModal
        token={token}
        isOpen={hostingModalOpen}
        onClose={() => setHostingModalOpen(false)}
        onCreated={() => {
          toast.ok('🎴 ¡Sala creada! Revisa el lobby.');
          setRecargaTrigger(p => p + 1);
        }}
        tableSeats={tableSeats}
      />
    </div>
  );
}
