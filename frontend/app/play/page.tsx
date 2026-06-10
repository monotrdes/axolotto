"use client";
import { API_BASE } from "@/lib/api";
import { RealtimeProvider, useRealtime } from '@/context/RealtimeContext';
import axios from "axios";

import { usePrivy } from "@privy-io/react-auth";
import { useEffect, useState, useCallback, useRef } from "react";
import { LogOut, Settings } from "lucide-react";
import { useBlockchainEvents } from "@/hooks/useBlockchainEvents";
import { useToast } from "@/context/ToastContext";

import DailyClaim from "@/components/DailyClaim";
import AxolottoStore from "@/components/Store";
import Inventory from "@/components/Inventory";
import Santuario from "@/components/Santuario";
import PlayMode from "@/components/PlayMode";
import Rankings from "@/components/Rankings";
import Gashapon from "@/components/Gashapon";
import AmigosPage from "@/components/social/AmigosPage";
import VipModal, { type VipNotification } from "@/components/VipModal";
import SettingsModal from "@/components/SettingsModal";
import { GameCanvas } from "@/components/world/GameCanvas";
import type { GameCanvasHandle } from "@/components/world/GameCanvas";
import type { WorldScene } from "@/components/world/WorldScene";
import type { AxolotitoData } from "@/components/world/entities/AxolotitoSprite";
import type { DecorationItem } from "@/components/world/zones/NidoZone";
import { CuevaDecorPanel } from "@/components/world/hud/CuevaDecorPanel";
import { MochilaFloating } from "@/components/world/hud/MochilaFloating";
import WebitoIntroAnimation from "@/components/onboarding/WebitoIntroAnimation";
import PostTutorialBranch from "@/components/onboarding/PostTutorialBranch";
import { TutorialFlow } from "@/components/tutorial/TutorialFlow";
import TutorialResetButton from "@/components/dev/TutorialResetButton";
import VipChip from "@/components/play/VipChip";
import WorldOrbs from "@/components/play/WorldOrbs";
import ZoneDock from "@/components/play/ZoneDock";
import type { TabId, OnboardingPhase, SyncData } from '@/types/play';
import type { MochilaTab } from '@/types/inventory';

// Legacy tab IDs 'criadero'/'axolotitos' kept for backwards compat — redirect to santuario

// New 5-zone dock matching the paper world
const ZONE_TABS = [
  { id: 'santuario' as TabId, label: 'Nido',     emoji: '🪺', color: '#E4007C', glow: 'rgba(228,0,124,0.5)',   zone: 'nido' },
  { id: 'tienda'    as TabId, label: 'Tianguis',  emoji: '🏪', color: '#FF6B35', glow: 'rgba(255,107,53,0.5)',  zone: 'tianguis' },
  { id: 'jugar'     as TabId, label: 'Sala',      emoji: '🎲', color: '#34D399', glow: 'rgba(52,211,153,0.5)',  zone: 'sala' },
  { id: 'rankings'  as TabId, label: 'Pirámide',  emoji: '🏆', color: '#FBBF24', glow: 'rgba(251,191,36,0.5)',  zone: 'piramide' },
  { id: 'gashapon'  as TabId, label: 'Cápsulas',  emoji: '🎰', color: '#A855F7', glow: 'rgba(168,85,247,0.5)',  zone: 'capsulas' },
] as const;

export default function Home() {
  const { ready, authenticated, user, login, logout, getAccessToken } = usePrivy();
  const [datosBanco, setDatosBanco]       = useState<any>(null);
  const [mensajeBackend, setMensajeBackend] = useState("Sincronizando con la red de Axolotto...");
  const [accessToken, setAccessToken]     = useState<string | null>(null);
  const [tabActiva, setTabActiva]         = useState<TabId>('tienda');
  const [mochilaInitialTab, setMochilaInitialTab] = useState<MochilaTab>('cartas');

  const [onboardingPhase, setOnboardingPhase] = useState<OnboardingPhase>("loading");
  const [syncData, setSyncData] = useState<SyncData | null>(null);
  const [tutorialKarma, setTutorialKarma] = useState<"lucky" | "salty">("lucky");
  const [tutorialAxoName, setTutorialAxoName] = useState("Axolotito Bebé");
  const [hasPendingReward, setHasPendingReward] = useState(false);
  const [dailyClaimAvailable, setDailyClaimAvailable] = useState(false);
  const [syncTrigger, setSyncTrigger] = useState(0);

  // Dev: reset handler for TutorialResetButton (used in all phase returns)
  const handleDevReset = () => {
    setOnboardingPhase("loading");
    setSyncData(null);
    setSyncTrigger(prev => prev + 1);
  };

  const [lastGameEvent, setLastGameEvent] = useState(0);
  const [lastShopEvent, setLastShopEvent] = useState(0);
  const [earningsQueue, setEarningsQueue] = useState<number[]>([]);
  const [openBancoCount, setOpenBancoCount] = useState(0);
  const [vipModalOpen, setVipModalOpen] = useState(false);
  const [settingsModalOpen, setSettingsModalOpen] = useState(false);
  const [tickerFeed, setTickerFeed]     = useState<any[]>([]);
  const worldSceneRef = useRef<WorldScene | null>(null);
  const gameCanvasRef = useRef<GameCanvasHandle | null>(null);

  // Decoration panel state
  const [caveDecorOpen, setCaveDecorOpen] = useState(false);
  const [caveDecorIndex, setCaveDecorIndex] = useState(0);
  const [caveDecorAxoName, setCaveDecorAxoName] = useState("");
  const [placedDecorations, setPlacedDecorations] = useState<DecorationItem[]>([]);
  const [availableDecorations, setAvailableDecorations] = useState<DecorationItem[]>([]);
  const [axolotitosData, setAxolotitosData] = useState<AxolotitoData[]>([]);

  // Poll global capsule feed for ticker
  useEffect(() => {
    if (!accessToken || !authenticated) return;
    const fetchFeed = async () => {
      try {
        const res = await axios.get(`${API_BASE}/shop/capsule/feed`, {
          headers: { Authorization: `Bearer ${accessToken}` }
        });
        setTickerFeed(res.data);
      } catch (err) {
        console.error("Error cargando feed del ticker:", err);
      }
    };
    fetchFeed();
    const interval = setInterval(fetchFeed, 30000);
    return () => clearInterval(interval);
  }, [accessToken, authenticated]);

  // Punto rojo en dock Cápsulas cuando hay recompensa lunar disponible.
  // Se refresca al cambiar de tab (cubre reclamar dentro de Gashapon → salir del tab).
  useEffect(() => {
    if (!accessToken || !authenticated) { setDailyClaimAvailable(false); return; }
    axios.get(`${API_BASE}/rewards/lunar/status`, {
      headers: { Authorization: `Bearer ${accessToken}` }
    })
      .then(res => setDailyClaimAvailable(res.data?.can_claim === true))
      .catch(() => {});
  }, [accessToken, authenticated, tabActiva]);

  // Floating rewards states & tracking
  const [floatingGal, setFloatingGal] = useState<{ id: string; amount: string; x: number }[]>([]);
  const [floatingAxg, setFloatingAxg] = useState<{ id: string; amount: string; x: number }[]>([]);
  const prevBalancesRef = useRef<{ frijolitos: number; axofichas: number } | null>(null);

  // Sync axolotito data to the paper world
  useEffect(() => {
    if (!datosBanco?.axolotitos || !gameCanvasRef.current) return;

    const axolotitos: AxolotitoData[] = (datosBanco.axolotitos as any[]).map(
      (axo: any, idx: number) => ({
        id: axo.id ?? `axo-${idx}`,
        name: axo.name ?? axo.nombre ?? `Axolotito ${idx + 1}`,
        level: axo.level ?? axo.nivel ?? 1,
        energy: axo.energy ?? axo.energia ?? 100,
        stats: {
          suerte: axo.stats?.suerte ?? axo.suerte ?? 50,
          ojo: axo.stats?.ojo ?? axo.ojo ?? 50,
          pila: axo.stats?.pila ?? axo.pila ?? 50,
          sal: axo.stats?.sal ?? axo.sal ?? 50,
        },
        state: axo.state ?? (axo.energia === 0 ? "sleeping" : "idle"),
        caveIndex: axo.cave_index ?? axo.slot ?? idx,
        isEgg: axo.is_egg ?? axo.es_huevo ?? false,
        eggProgress: axo.egg_progress ?? axo.progreso_huevo ?? undefined,
        skinColor: axo.skin_color ?? axo.color_piel ?? undefined,
      }),
    );

    setAxolotitosData(axolotitos);
    gameCanvasRef.current.setAxolotitos(axolotitos);
  }, [datosBanco]);

  useEffect(() => {
    if (!datosBanco) return;
    const currentGal = Number(datosBanco.frijolitos || 0);
    const currentAxg = Number(datosBanco.axofichas || 0);

    if (prevBalancesRef.current) {
      const prevGal = prevBalancesRef.current.frijolitos;
      const prevAxg = prevBalancesRef.current.axofichas;

      if (currentGal > prevGal) {
        const diff = currentGal - prevGal;
        const numFloaters = 4;
        const newFloaters = Array.from({ length: numFloaters }).map((_, i) => ({
          id: `gal-${Date.now()}-${i}-${Math.random()}`,
          amount: `+${(diff / numFloaters).toFixed(2)} 🪙`,
          x: (Math.random() - 0.5) * 50,
        }));
        setFloatingGal(prev => [...prev, ...newFloaters]);
      }

      if (currentAxg > prevAxg) {
        const diff = currentAxg - prevAxg;
        const numFloaters = 3;
        const newFloaters = Array.from({ length: numFloaters }).map((_, i) => ({
          id: `axg-${Date.now()}-${i}-${Math.random()}`,
          amount: `+${Math.round(diff / numFloaters)} 💎`,
          x: (Math.random() - 0.5) * 50,
        }));
        setFloatingAxg(prev => [...prev, ...newFloaters]);
      }
    }

    prevBalancesRef.current = { frijolitos: currentGal, axofichas: currentAxg };
  }, [datosBanco]);

  const { toast } = useToast();

  const actualizarSaldosSilencioso = async () => {
    if (!user || !accessToken) return;
    try {
      const respuesta = await fetch(`${API_BASE}/auth/sync`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "Authorization": `Bearer ${accessToken}` },
        body: JSON.stringify({
          privy_did: user.id,
          wallet_address: user.wallet?.address,
        }),
      });
      const datos = await respuesta.json();
      setDatosBanco(datos.wallet);
    } catch (e) {
      console.error("Error actualizando saldo:", e);
    }
  };

  const walletAddress = (() => {
    if (!user) return undefined;
    if (user.wallet?.address) return user.wallet.address;
    const linked = user.linkedAccounts?.find((a: any) => a.type === 'wallet');
    return (linked as any)?.address as string | undefined;
  })();

  useBlockchainEvents(walletAddress, {
    onBalanceChange: useCallback((diff: number) => {
      actualizarSaldosSilencioso();
      setEarningsQueue(prev => [...prev, diff]);
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []),
    onGameEvent: useCallback(() => setLastGameEvent(Date.now()), []),
    onShopEvent: useCallback(() => setLastShopEvent(Date.now()), []),
  });

  // Hook must be called at component top level, not inside effects
  const { enablePolling } = useRealtime();

  // Poll for multiplayer game results with exponential backoff and visibility guard
  useEffect(() => {
    if (!accessToken || !authenticated || !enablePolling) return;
    let backoff = 4_000; // start at 4 seconds
    let cancelled = false;
    const pollLogs = async () => {
      try {
        const res = await fetch(`${API_BASE}/multiplayer/unread-logs`, {
          headers: { Authorization: `Bearer ${accessToken}` },
        });
        if (!res.ok) {
          // keep current backoff, will retry later
          return;
        }
        const logs = await res.json();
        if (logs && logs.length > 0) {
          logs.forEach((log: any) => {
            toast.game(log);
            // Accumulate for SettlingScreen match history
            try {
              const key = `axolotto_match_logs_${user?.id ?? 'anon'}`;
              const prev = JSON.parse(sessionStorage.getItem(key) || '[]');
              prev.push({
                outcome: log.outcome,
                room_name: log.room_name,
                gross_prize: log.gross_prize_gal ?? 0,
                entry_fee: log.entry_fee_paid ?? 0,
                net_gal: log.net_gal ?? 0,
                xp_gained: log.xp_gained ?? 0,
                prize_labels: (log.prize_breakdown || []).map((pb: any) => pb.label),
                won_jackpot: log.won_jackpot ?? false,
              });
              sessionStorage.setItem(key, JSON.stringify(prev.slice(-20))); // keep last 20
            } catch { /* ignore */ }
          });
          backoff = 4_000; // reset on success
        } else {
          // no new logs, increase backoff up to 30s
          backoff = Math.min(backoff * 2, 30_000);
        }
      } catch (e) {
        console.error('Polling unread-logs failed', e);
      } finally {
        if (!cancelled) {
          setTimeout(pollLogs, backoff);
        }
      }
    };
    // start first poll immediately
    pollLogs();
    return () => {
      cancelled = true;
    };
  }, [accessToken, authenticated, enablePolling]);

  useEffect(() => {
    const sincronizarConBackend = async () => {
      if (authenticated && user) {
        try {
          const token = await getAccessToken();
          setAccessToken(token);

          let email = user.email?.address || user.google?.email || user.discord?.email || null;
          let walletAddress = user.wallet?.address || null;

          if (user.linkedAccounts) {
            if (!email) {
              const cuentaEmail = user.linkedAccounts.find(
                acc => acc.type === 'email' || acc.type === 'google_oauth' || acc.type === 'discord_oauth'
              );
              // @ts-ignore
              email = cuentaEmail ? (cuentaEmail.address || cuentaEmail.email) : null;
            }
            if (!walletAddress) {
              const cuentaWallet = user.linkedAccounts.find(acc => acc.type === 'wallet');
              // @ts-ignore
              walletAddress = cuentaWallet ? cuentaWallet.address : null;
            }
          }

          const respuesta = await fetch(`${API_BASE}/auth/sync`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "Authorization": `Bearer ${token}`,
            },
            body: JSON.stringify({ privy_did: user.id, email, wallet_address: walletAddress }),
          });
          const datos = await respuesta.json();
          setMensajeBackend(datos.mensaje);
          setDatosBanco(datos.wallet);

          // Guardar datos de onboarding
          const newSyncData = {
            is_new_user: datos.is_new_user ?? false,
            tutorial_completed: datos.tutorial_completed ?? false,
            cave_level: datos.cave_level ?? 1,
            cave_name: datos.cave_name ?? null,
          };
          setSyncData(newSyncData);

          // Check for pending corcholata reward
          if (datos.has_pending_corcholata_reward) {
            setHasPendingReward(true);
          }

          // Decidir fase de onboarding
          if (newSyncData.is_new_user) {
            setOnboardingPhase("intro");
          } else if (!newSyncData.tutorial_completed) {
            setOnboardingPhase("tutorial");
          } else {
            setOnboardingPhase("done");
          }
        } catch (error) {
          console.error(error);
          setMensajeBackend("El servidor está dormido 😴");
        }
      }
    };
    sincronizarConBackend();
  }, [authenticated, user, getAccessToken, syncTrigger]);

  // ─── Privy not ready yet ───────────────────────────────────────────────────
  if (!ready) {
    return (
      <div className="world-bg flex h-screen items-center justify-center overflow-hidden">
        <WorldOrbs />
        <p className="relative z-10 text-[#FF8DA1] text-xl font-bold animate-pulse tracking-wide">
          Despertando Axolotto…
        </p>
      </div>
    );
  }

  // ─── Onboarding flow ─────────────────────────────────────────────────────────
  if (authenticated && onboardingPhase === "loading") {
    return (
      <div className="world-bg flex h-screen items-center justify-center overflow-hidden">
        <WorldOrbs />
        <p className="relative z-10 text-[#FF8DA1] text-xl font-bold animate-pulse tracking-wide">
          Sincronizando…
        </p>
        <TutorialResetButton onReset={handleDevReset} />
      </div>
    );
  }

  if (authenticated && onboardingPhase === "intro") {
    return (
      <>
        <WebitoIntroAnimation onComplete={() => setOnboardingPhase("tutorial")} />
        <TutorialResetButton onReset={handleDevReset} />
      </>
    );
  }

  if (authenticated && onboardingPhase === "tutorial") {
    return (
      <div className="world-bg min-h-screen text-white flex items-center justify-center">
        <WorldOrbs />
        <div className="relative z-10 w-full max-w-5xl px-3 sm:px-6">
          <TutorialFlow
            userId={user?.id ?? ""}
            token={accessToken}
            hasPendingReward={hasPendingReward}
            onComplete={(resolvedKarma, axoName) => {
              if (resolvedKarma) {
                setTutorialKarma(resolvedKarma);
              }
              if (axoName) {
                setTutorialAxoName(axoName);
              }
              // Si abrió tesoro por corcholata, saltar branch e ir directo al juego
              if (hasPendingReward) {
                setOnboardingPhase("done");
                setTabActiva("jugar");
              } else {
                setOnboardingPhase("branch");
              }
              // Refrescar wallet tras el tutorial (ActTreasureChest pudo entregar premio)
              actualizarSaldosSilencioso();
            }}
          />
          <TutorialResetButton onReset={handleDevReset} />
        </div>
      </div>
    );
  }

  if (authenticated && onboardingPhase === "branch") {
    return (
      <>
        <PostTutorialBranch
          axoName={tutorialAxoName}
          karma={tutorialKarma}
          onPayAndPlay={() => {
            setOnboardingPhase("done");
            setTabActiva("tienda");
          }}
          onPlayFree={() => {
            setOnboardingPhase("done");
            setTabActiva("jugar");
          }}
        />
        <TutorialResetButton onReset={handleDevReset} />
      </>
    );
  }
  // ─────────────────────────────────────────────────────────────────────────────

  // ─── Main render ──────────────────────────────────────────────────────────
  return (
    <RealtimeProvider>
      <div className="world-bg min-h-screen text-white overflow-x-hidden">
      <WorldOrbs />

      {/* ── Authenticated + data loaded ─────────────────────────────────── */}
      {authenticated && datosBanco ? (
        <>
          {/* ── 2.5D Paper World background ──────────────────────────── */}
          <GameCanvas
            ref={gameCanvasRef}
            onReady={(_app, scene) => {
              worldSceneRef.current = scene;
            }}
            onZoneClick={(zoneId) => {
              const zoneToTab: Record<string, TabId> = {
                nido: "santuario",
                tianguis: "tienda",
                sala: "jugar",
                piramide: "rankings",
                capsulas: "gashapon",
              };
              const tab = zoneToTab[zoneId];
              if (tab) setTabActiva(tab);
            }}
            onCaveClick={(caveIndex: number) => {
              const axo = axolotitosData.find((a) => a.caveIndex === caveIndex);
              setCaveDecorIndex(caveIndex);
              setCaveDecorAxoName(axo?.name ?? "");
              // Load existing decorations for this cave
              setPlacedDecorations(
                axolotitosData
                  .filter((a) => a.caveIndex === caveIndex)
                  .flatMap(() => []), // TODO: load from backend
              );
              // Mock available decorations for now
              setAvailableDecorations(getMockDecorations());
              setCaveDecorOpen(true);
            }}
            onAxolotitoClick={(axoId: string) => {
              setTabActiva("santuario");
            }}
            onStallClick={(stallType) => {
              // Map stall type to tab/action
              if (stallType === "fountain") {
                // Open bank/currency conversion (navigate to store with bank flag)
                setTabActiva("tienda");
                setOpenBancoCount((c) => c + 1);
              } else {
                // Navigate to store section
                setTabActiva("tienda");
              }
            }}
            visible={false}
            initialZone="nido"
          />

          {/* HUD TOP BAR */}
          <header className="fixed top-0 left-0 right-0 z-40 h-14 flex items-center justify-between px-4 sm:px-6 bg-[#060610]/80 backdrop-blur-xl border-b border-white/5">
            {/* Brand */}
            <div className="flex items-center gap-2 select-none">
              <span className="text-xl">🦎</span>
              <span className="font-extrabold text-base sm:text-lg text-[#FF8DA1] tracking-tight drop-shadow-[0_0_8px_rgba(255,141,161,0.4)]">
                AXOLOTTO
              </span>
            </div>

            {/* VIP chip + Currencies + logout */}
            <div className="flex items-center gap-1.5 sm:gap-2">
              {/* VIP Chip */}
              <VipChip
                vipTier={datosBanco.vip_tier}
                daysRemaining={datosBanco.vip_days_remaining}
                pendingGal={datosBanco.vip_pending_gal}
                onClick={() => setVipModalOpen(true)}
              />

              <div className="relative flex items-center gap-1.5 bg-[#1C1C35]/80 px-2.5 sm:px-3 py-1.5 rounded-full border border-[#E4007C]/20">
                <span className="text-sm select-none">💎</span>
                <span className="text-[#E4007C] font-bold text-sm tabular-nums">{datosBanco.axofichas}</span>
                <span className="text-gray-600 text-[10px] font-medium hidden sm:inline">AXF</span>
                {floatingAxg.map(f => (
                  <span
                    key={f.id}
                    style={{ '--x': `${f.x}px` } as React.CSSProperties}
                    className="absolute pointer-events-none text-xs font-black text-[#E4007C] animate-float-up z-50 whitespace-nowrap"
                    onAnimationEnd={() => {
                      setFloatingAxg(prev => prev.filter(item => item.id !== f.id));
                    }}
                  >
                    {f.amount}
                  </span>
                ))}
              </div>
              <button
                onClick={() => { setTabActiva('tienda'); setOpenBancoCount(c => c + 1); }}
                className="relative flex items-center gap-1.5 bg-[#1C1C35]/80 px-2.5 sm:px-3 py-1.5 rounded-full border border-amber-500/20 hover:border-amber-400/50 hover:bg-amber-900/20 transition-all active:scale-95"
                title="Mis Frijolitos"
              >
                <span className="text-sm select-none">🪙</span>
                <span className="text-amber-500 font-bold text-sm tabular-nums">
                  {Number(datosBanco.frijolitos || 0).toFixed(2)}
                </span>
                <span className="text-gray-600 text-[10px] font-medium hidden sm:inline">FRJ</span>
                {floatingGal.map(f => (
                  <span
                    key={f.id}
                    style={{ '--x': `${f.x}px` } as React.CSSProperties}
                    className="absolute pointer-events-none text-xs font-black text-amber-500 animate-float-up z-50 whitespace-nowrap"
                    onAnimationEnd={() => {
                      setFloatingGal(prev => prev.filter(item => item.id !== f.id));
                    }}
                  >
                    {f.amount}
                  </span>
                ))}
              </button>
              {/* Daily FRJ Claim */}
              <DailyClaim
                token={accessToken}
                onSuccess={actualizarSaldosSilencioso}
              />

              <button
                onClick={() => setSettingsModalOpen(true)}
                className="p-2 rounded-full bg-[#1C1C35]/80 border border-white/5 text-gray-500 hover:text-[#FF8DA1] hover:bg-[#FF8DA1]/15 hover:border-[#FF8DA1]/30 transition-all"
                title="Ajustes"
              >
                <Settings size={13} />
              </button>
              <button
                onClick={logout}
                className="p-2 rounded-full bg-[#1C1C35]/80 border border-white/5 text-gray-500 hover:text-red-400 hover:bg-red-900/20 hover:border-red-500/30 transition-all"
                title="Desconectar"
              >
                <LogOut size={13} />
              </button>
            </div>
          </header>

          {/* Cave Decoration Panel */}
          <CuevaDecorPanel
            isOpen={caveDecorOpen}
            onClose={() => setCaveDecorOpen(false)}
            caveIndex={caveDecorIndex}
            axolotitoName={caveDecorAxoName}
            placedDecorations={placedDecorations}
            availableDecorations={availableDecorations}
            onSave={(caveIdx, decorations) => {
              gameCanvasRef.current?.setCaveDecorations(caveIdx, decorations);
              setPlacedDecorations(decorations);
              // TODO: persist to backend
            }}
          />

          {/* VIP Modal */}
          <VipModal
            isOpen={vipModalOpen}
            onClose={() => setVipModalOpen(false)}
            token={accessToken}
            userId={user?.id || ""}
            balances={datosBanco}
            recargarSaldos={actualizarSaldosSilencioso}
            onVipSuccess={toast.vip}
          />

          {/* Settings Modal */}
          <SettingsModal
            isOpen={settingsModalOpen}
            onClose={() => setSettingsModalOpen(false)}
            onLogout={logout}
            onResetTutorial={handleDevReset}
          />

          {/* Ticker de Actividad Global */}
          {tickerFeed.length > 0 && (
            <div className="fixed top-14 left-0 right-0 z-30 h-6 bg-[#080816]/90 backdrop-blur-md border-b border-white/5 flex items-center overflow-hidden text-[10px] select-none">
              <div className="flex whitespace-nowrap ticker-track gap-8 py-1">
                {[...tickerFeed, ...tickerFeed].map((f, i) => {
                  const isBronze = f.tier === 'cobre';
                  const isSilver = f.tier === 'plata';
                  const tierBadge = isBronze ? '🍀 Cobre' : isSilver ? '🛡️ Plata' : '👑 Oro';
                  const badgeColor = isBronze ? 'text-orange-400' : isSilver ? 'text-cyan-400' : 'text-yellow-400';
                  return (
                    <span key={i} className="flex items-center gap-1.5 font-mono text-slate-350">
                      <span className={`font-black ${badgeColor}`}>{tierBadge}</span>
                      <span className="text-white font-extrabold">@{f.nickname}</span>
                      <span>{f.outcome_text}</span>
                      <span className="text-slate-600 text-[8px]">
                        ({new Date(f.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})})
                      </span>
                      <span className="text-slate-700 mx-2">·</span>
                    </span>
                  );
                })}
              </div>
            </div>
          )}

          {/* CONTENT AREA — padded away from HUD and dock */}
          <main className={`relative z-10 ${tickerFeed.length > 0 ? 'pt-20' : 'pt-14'} pb-20 min-h-screen`}>
            <div key={tabActiva} className="max-w-5xl mx-auto px-3 sm:px-6 py-4 animate-tab-fade">
              {tabActiva === 'tienda' && (
                <AxolottoStore
                  userId={user?.id || ""}
                  balances={datosBanco}
                  token={accessToken}
                  cambiarTab={setTabActiva}
                  recargarSaldos={actualizarSaldosSilencioso}
                  lastShopEvent={lastShopEvent}
                  openBanco={openBancoCount}
                />
              )}
              {tabActiva === 'jugar' && (
                <PlayMode
                  userId={user?.id || ""}
                  token={accessToken}
                  balances={datosBanco}
                  recargarSaldos={actualizarSaldosSilencioso}
                  lastGameEvent={lastGameEvent}
                  earningsQueue={earningsQueue}
                  onEarningsSeen={() => setEarningsQueue([])}
                />
              )}
              {/* Mochila unificada: tabs cartas/tablas/items en un solo componente */}
              {(tabActiva === 'mochila' || tabActiva === 'cartas' || tabActiva === 'tablas') && (
                <Inventory
                  userId={user?.id || ""}
                  token={accessToken}
                  cambiarTab={(tab: string) => setTabActiva(tab as TabId)}
                  initialTab={tabActiva === 'tablas' ? 'tablas' : tabActiva === 'cartas' ? 'cartas' : mochilaInitialTab}
                  recargarSaldos={actualizarSaldosSilencioso}
                />
              )}
              {/* santuario = El Nido (merged webitos + axolotitos). Legacy criadero/axolotitos ids redirect here */}
              {(tabActiva === 'santuario' || tabActiva === 'criadero' || tabActiva === 'axolotitos') && (
                <Santuario userId={user?.id || ""} token={accessToken} cambiarTab={(tab) => setTabActiva(tab as TabId)} vipTier={datosBanco?.vip_tier} />
              )}
              {tabActiva === 'rankings'   && <Rankings  userId={user?.id || ""} token={accessToken} cambiarTab={setTabActiva}                   />}
{tabActiva === 'amigos'    && <AmigosPage userId={user?.id || ""} token={accessToken} onNavigate={(tab) => setTabActiva(tab as TabId)} />}
              {tabActiva === 'gashapon'   && (
                <Gashapon
                  userId={user?.id || ""}
                  token={accessToken}
                  recargarSaldos={actualizarSaldosSilencioso}
                  balances={datosBanco || { frijolitos: 0 }}
                />
              )}
            </div>
          </main>

          {/* Mochila flotante — abre el dashboard unificado en la sección seleccionada */}
          <MochilaFloating
            onOpenSection={(section) => {
              setMochilaInitialTab(section);
              setTabActiva("mochila");
            }}
          />

          {/* BOTTOM DOCK — 5 zone buttons matching the paper world */}
          <ZoneDock
            zoneTabs={ZONE_TABS}
            tabActiva={tabActiva}
            dailyClaimAvailable={dailyClaimAvailable}
            onTabChange={(tab, zone) => {
              setTabActiva(tab);
              gameCanvasRef.current?.navigateToZone(zone);
            }}
          />
        </>
      ) : authenticated ? (
        /* ── Authenticated but wallet data still loading ────────────────── */
        <div className="relative z-10 flex h-screen items-center justify-center">
          <div className="text-center">
            <p className="text-[#FF8DA1] text-2xl font-black tracking-tight animate-pulse">🦎 AXOLOTTO</p>
            <p className="text-gray-600 text-sm mt-2">{mensajeBackend}</p>
          </div>
        </div>
      ) : (
        /* ── Login screen ───────────────────────────────────────────────── */
        <div className="relative z-10 flex flex-col min-h-screen items-center justify-center gap-8 px-6">
          <div className="text-center">
            <h1 className="text-6xl sm:text-8xl font-black text-[#FF8DA1] drop-shadow-[0_0_24px_rgba(255,141,161,0.5)] tracking-tighter">
              AXOLOTTO
            </h1>
            <p className="text-gray-500 text-lg mt-3">🦎 Tu mascota digital en la vida real.</p>
          </div>
          <button
            onClick={login}
            className="px-12 py-4 bg-gradient-to-r from-[#E4007C] to-[#B30062] hover:from-[#FF1493] hover:to-[#E4007C] rounded-full font-black text-xl shadow-[0_0_30px_rgba(228,0,124,0.5)] transition-all transform hover:scale-105 active:scale-95 tracking-wide"
          >
            Entrar al Juego
          </button>
        </div>
      )}

      <TutorialResetButton onReset={handleDevReset} />

    </div>
  </RealtimeProvider>
  );
}

/** Mock available decorations for Phase 2 testing */
function getMockDecorations(): DecorationItem[] {
  return [
    { id: "deco-1", type: "bed", gridX: 0, gridY: 0, gridW: 2, gridH: 1, emoji: "🛏️", label: "Cama de Alga" },
    { id: "deco-2", type: "light", gridX: 0, gridY: 0, gridW: 1, gridH: 1, emoji: "🏮", label: "Lámpara Coral" },
    { id: "deco-3", type: "rug", gridX: 0, gridY: 0, gridW: 2, gridH: 2, emoji: "🟫", label: "Tapete Picado" },
    { id: "deco-4", type: "plant", gridX: 0, gridY: 0, gridW: 1, gridH: 2, emoji: "🪴", label: "Helecho Marino" },
    { id: "deco-5", type: "toy", gridX: 0, gridY: 0, gridW: 1, gridH: 1, emoji: "🎈", label: "Globo de Papel" },
    { id: "deco-6", type: "trophy", gridX: 0, gridY: 0, gridW: 1, gridH: 1, emoji: "🏅", label: "Medalla" },
    { id: "deco-7", type: "wall", gridX: 0, gridY: 0, gridW: 2, gridH: 1, emoji: "🖼️", label: "Cuadro Loteria" },
    { id: "deco-8", type: "bed", gridX: 0, gridY: 0, gridW: 1, gridH: 1, emoji: "🪹", label: "Nido Burbuja" },
  ];
}
