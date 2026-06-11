"use client";
import { API_BASE } from "@/lib/api";
import { RealtimeProvider, useRealtime } from '@/context/RealtimeContext';
import axios from "axios";

import { usePrivy } from "@privy-io/react-auth";
import { useEffect, useState, useCallback, useRef } from "react";
import { Settings } from "lucide-react";
import { useBlockchainEvents } from "@/hooks/useBlockchainEvents";
import { useToast } from "@/context/ToastContext";

import AxolottoStore from "@/components/Store";
import Inventory from "@/components/Inventory";
import Santuario from "@/components/Santuario";
import PlayMode from "@/components/PlayMode";
import Rankings from "@/components/Rankings";
import Gashapon from "@/components/Gashapon";
import AmigosPage from "@/components/social/AmigosPage";
import VipModal, { type VipNotification } from "@/components/VipModal";
import SettingsModal from "@/components/SettingsModal";
import HostingSetupModal from "@/components/HostingSetupModal";
import { GameCanvas } from "@/components/world/GameCanvas";
import type { GameCanvasHandle } from "@/components/world/GameCanvas";
import type { WorldScene } from "@/components/world/WorldScene";
import type { AxolotitoData } from "@/components/world/entities/AxolotitoSprite";
import { DecorSlotPanel } from "@/components/world/hud/DecorSlotPanel";
import { MochilaFloating } from "@/components/world/hud/MochilaFloating";
import LunarFloating from "@/components/world/hud/LunarFloating";
import WebitoIntroAnimation from "@/components/onboarding/WebitoIntroAnimation";
import PostTutorialBranch from "@/components/onboarding/PostTutorialBranch";
import { TutorialFlow } from "@/components/tutorial/TutorialFlow";
import TutorialResetButton from "@/components/dev/TutorialResetButton";
import VipChip from "@/components/play/VipChip";
import WorldOrbs from "@/components/play/WorldOrbs";
import ZoneDock from "@/components/play/ZoneDock";
import ZoneDockMacro from "@/components/play/ZoneDockMacro";
import { fetchAxolotitos, fetchIncubaciones, fetchCaveStatus } from "@/services/santuarioService";
import {
  mapBackendAxolotito,
  mapIncubationToEgg,
  mapFriendInfo,
  type AmigoData,
  type BackendAxolotito,
  type BackendIncubation,
  type BackendFriendInfo,
} from "@/components/world/mapBackendAxolotito";
import type { TabId, OnboardingPhase, SyncData } from '@/types/play';
import type { MochilaTab } from '@/types/inventory';

// Legacy tab IDs 'criadero'/'axolotitos' kept for backwards compat — redirect to santuario

// Mundo papel picado (plan task-84): con flag se usa el dock de 3 macrozonas.
const PAPER_WORLD = process.env.NEXT_PUBLIC_PAPER_WORLD === "1";

// Etiquetas del botón "abrir panel" del mundo papel picado
const PANEL_LABELS: Partial<Record<TabId, string>> = {
  tienda: 'Abrir Tienda',
  jugar: 'Abrir Salas',
  rankings: 'Ver Rankings',
  gashapon: 'Abrir Cápsulas',
  santuario: 'Gestionar Nido',
  criadero: 'Gestionar Nido',
  axolotitos: 'Gestionar Nido',
  amigos: 'Abrir Amigos',
  mochila: 'Abrir Mochila',
  cartas: 'Abrir Mochila',
  tablas: 'Abrir Mochila',
};

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
  // Mundo papel picado: los paneles HTML viven ocultos y se abren como overlay
  // (hotspots del diorama o botón 📜). Sin flag siempre visibles (legacy).
  const [panelVisible, setPanelVisible]   = useState(!PAPER_WORLD);
  // Sección del Store a abrir según el puesto tocado en el Tianguis
  const [storeSection, setStoreSection]   = useState<'official' | 'melter' | 'market' | undefined>(undefined);
  const [storeSectionNonce, setStoreSectionNonce] = useState(0);
  const [mochilaInitialTab, setMochilaInitialTab] = useState<MochilaTab>('cartas');
  // Burbuja 👁 del embarcadero: amigo cuya cueva se abre al entrar a AmigosPage
  const [visitaAmigoId, setVisitaAmigoId] = useState<string | null>(null);
  // Hostear sala desde el mundo (mesa de amigos / burbuja 🎲 de la trajinerita)
  const [amigosData, setAmigosData] = useState<AmigoData[]>([]);
  const [hostingOpen, setHostingOpen] = useState(false);
  const [hostingInvite, setHostingInvite] = useState<string | null>(null);
  const [hostingSeats, setHostingSeats] = useState(0);
  const caveSeatsRef = useRef<number | null>(null); // cache: asientos de la mesa de la cueva
  const [activeGame, setActiveGame] = useState<any>(null);

  // ── Game session locking (from PlayMode — covers CPU games and backend status) ──
  const [gameSessionActive, setGameSessionActive] = useState(false);
  const [tabBlocked, setTabBlocked] = useState(false);

  // Combined lock: activeGame (multiplayer from /active-check) OR gameSessionActive (CPU/animation)
  const isGameLocked = !!(activeGame?.active) || gameSessionActive;

  // Force tab to 'jugar' when game becomes active
  useEffect(() => {
    if (isGameLocked && tabActiva !== 'jugar') {
      setTabActiva('jugar');
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isGameLocked]);

  // Clear tab blocked message after 3 seconds
  useEffect(() => {
    if (!tabBlocked) return;
    const t = setTimeout(() => setTabBlocked(false), 3000);
    return () => clearTimeout(t);
  }, [tabBlocked]);

  // Guarded tab switcher: blocks non-jugar tabs during active game session
  const safeSetTab = useCallback((tab: TabId) => {
    if (isGameLocked && tab !== 'jugar') {
      setTabBlocked(true);
      return;
    }
    setTabActiva(tab);
  }, [isGameLocked]);

  // Poll active game status to lock navigation and UI controls
  useEffect(() => {
    if (!accessToken || !authenticated) {
      setActiveGame(null);
      return;
    }
    const checkActiveGame = async () => {
      try {
        const headers = { Authorization: `Bearer ${accessToken}` };
        const res = await axios.get(`${API_BASE}/multiplayer/active-check`, { headers });
        setActiveGame(res.data);
        if (res.data?.active && tabActiva !== 'jugar') {
          setTabActiva('jugar'); // Force to jugar — direct set, not safeSetTab
        }
      } catch (err) {
        console.error("Error checking active game in Home:", err);
      }
    };
    checkActiveGame();
    const interval = setInterval(checkActiveGame, 5000);
    return () => clearInterval(interval);
  }, [accessToken, authenticated, tabActiva]);

  const [onboardingPhase, setOnboardingPhase] = useState<OnboardingPhase>("loading");
  const isInTutorial = onboardingPhase === "tutorial" || onboardingPhase === "intro" || onboardingPhase === "branch";
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
  // GameCanvas solo se monta con datosBanco + onboarding terminado: los fetch
  // del mundo deben esperar a que exista o sus set* caen al vacío.
  const [canvasReady, setCanvasReady] = useState(false);

  // Panel de decoración de la sala (slot tipado tocado en el diorama)
  const [decorSlotId, setDecorSlotId] = useState<string | null>(null);
  const [decorNonce, setDecorNonce] = useState(0);
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

  // Mundo papel picado: los axolotitos reales viven en /auth/axolotitos/{userId},
  // no en el payload de /auth/sync — cargarlos directo para el canvas.
  useEffect(() => {
    if (!PAPER_WORLD || !canvasReady || !accessToken || !user?.id) return;
    let cancelled = false;
    Promise.all([
      fetchAxolotitos(user.id, accessToken),
      fetchIncubaciones(user.id, accessToken).catch(() => []),
    ])
      .then(([axos, incubaciones]: [BackendAxolotito[], BackendIncubation[]]) => {
        if (cancelled || !Array.isArray(axos)) return;
        const data = [
          ...axos.map(mapBackendAxolotito),
          ...(Array.isArray(incubaciones)
            ? incubaciones.map((inc, i) => mapIncubationToEgg(inc, axos.length + i))
            : []),
        ];
        setAxolotitosData(data);
        gameCanvasRef.current?.setAxolotitos(data);
      })
      .catch((e) => console.error("PaperWorld: error cargando axolotitos", e));
    return () => {
      cancelled = true;
    };
  }, [accessToken, user?.id, canvasReady]);

  // Mundo papel picado: amigos para el embarcadero del Santuario.
  useEffect(() => {
    if (!PAPER_WORLD || !canvasReady || !accessToken) return;
    let cancelled = false;
    axios
      .get(`${API_BASE}/social/friends`, { headers: { Authorization: `Bearer ${accessToken}` } })
      .then((res) => {
        if (cancelled || !Array.isArray(res.data)) return;
        const amigos = (res.data as BackendFriendInfo[]).map(mapFriendInfo);
        setAmigosData(amigos);
        gameCanvasRef.current?.setAmigos?.(amigos);
      })
      .catch((e) => console.error("PaperWorld: error cargando amigos", e));
    return () => {
      cancelled = true;
    };
  }, [accessToken, canvasReady]);

  // Mundo papel picado: estado de la cueva (nivel/spots/mesa) → nidos
  // dinámicos del diorama; de paso cachea los asientos para hostear.
  useEffect(() => {
    if (!PAPER_WORLD || !canvasReady || !accessToken || !user?.id) return;
    let cancelled = false;
    fetchCaveStatus(user.id, accessToken)
      .then((d) => {
        if (cancelled || !d?.current) return;
        caveSeatsRef.current = d.current.has_table ? (d.current.table_seats ?? 0) : 0;
        gameCanvasRef.current?.setCaveStatus?.({
          level: d.current.level ?? 1,
          spots: d.current.spots ?? 1,
          hasTable: !!d.current.has_table,
          tableSeats: d.current.table_seats ?? 0,
        });
      })
      .catch((e) => console.error("PaperWorld: error cargando estado de cueva", e));
    return () => {
      cancelled = true;
    };
  }, [accessToken, user?.id, canvasReady]);

  // Mundo papel picado: decoraciones equipadas + layout de slots → sala del diorama.
  useEffect(() => {
    if (!PAPER_WORLD || !canvasReady || !accessToken) return;
    let cancelled = false;
    axios
      .get(`${API_BASE}/cave/decorations`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      })
      .then((res) => {
        if (cancelled || !Array.isArray(res.data?.slots)) return;
        gameCanvasRef.current?.setDecoraciones?.(res.data);
      })
      .catch((e) => console.error("PaperWorld: error cargando decoraciones", e));
    return () => {
      cancelled = true;
    };
  }, [accessToken, canvasReady, decorNonce]);

  // Mundo papel picado: top-3 del ranking para el podio de la Pirámide (endpoint público).
  useEffect(() => {
    if (!PAPER_WORLD || !canvasReady) return;
    let cancelled = false;
    axios
      .get(`${API_BASE}/ranking/axolotitos?sort_by=level&limit=3`)
      .then((res) => {
        if (cancelled || !Array.isArray(res.data)) return;
        gameCanvasRef.current?.setPodio?.(res.data.map(mapBackendAxolotito));
      })
      .catch((e) => console.error("PaperWorld: error cargando podio", e));
    return () => {
      cancelled = true;
    };
  }, [canvasReady]);

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

  // Mesa de amigos / burbuja 🎲 del embarcadero: hostear sala desde el mundo.
  // Requiere mesa de juego en la cueva (cave status, cacheado por sesión).
  const abrirHostingMundo = async (inviteNickname: string | null) => {
    if (caveSeatsRef.current === null && user?.id) {
      try {
        const d = await fetchCaveStatus(user.id, accessToken);
        caveSeatsRef.current = d?.current?.has_table ? (d.current.table_seats ?? 0) : 0;
      } catch (e) {
        console.error("PaperWorld: error consultando la mesa de la cueva", e);
      }
    }
    const seats = caveSeatsRef.current ?? 0;
    if (seats < 2) {
      toast.info("Tu cueva aún no tiene mesa de juego — expándela en el Santuario 🪨");
      setTabActiva("santuario");
      setPanelVisible(true);
      return;
    }
    setHostingSeats(seats);
    setHostingInvite(inviteNickname);
    setHostingOpen(true);
  };

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
        <TutorialResetButton onReset={handleDevReset} inTutorial={isInTutorial} />
      </div>
    );
  }

  if (authenticated && onboardingPhase === "intro") {
    return (
      <>
        <WebitoIntroAnimation onComplete={() => setOnboardingPhase("tutorial")} />
        <TutorialResetButton onReset={handleDevReset} inTutorial={isInTutorial} />
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
          <TutorialResetButton onReset={handleDevReset} inTutorial={isInTutorial} />
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
        <TutorialResetButton onReset={handleDevReset} inTutorial={isInTutorial} />
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
              setCanvasReady(true);
            }}
            onZoneClick={(zoneId) => {
              if (isGameLocked) {
                setTabBlocked(true);
                return;
              }
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
            onAxolotitoClick={(_axoId: string) => {
              if (isGameLocked) {
                setTabBlocked(true);
                return;
              }
              setTabActiva("santuario");
              setPanelVisible(true);
            }}
            onStallClick={(stallType) => {
              if (isGameLocked) {
                setTabBlocked(true);
                return;
              }
              // Hotspots del diorama → abrir el panel HTML correspondiente
              if (stallType.startsWith("decor:")) {
                // Slot de decoración de la sala → panel filtrado a su categoría
                setDecorSlotId(stallType.slice("decor:".length));
                return; // panel sobre el mundo, sin abrir pergamino
              }
              if (stallType.startsWith("nido-")) {
                // Zona de crianza: huevo/camita → gestión en el panel
                // Santuario (EggSheet/AxoSheet); bloqueado → invitar a expandir.
                if (stallType === "nido-bloqueado") {
                  toast.info("Este nido sigue enterrado — expande tu cueva para excavarlo 🪨");
                }
                setTabActiva("santuario");
                setPanelVisible(true);
                return;
              }
              if (stallType === "mesa-amigos") {
                // Mesa del Santuario: hostear sala para jugar con amigos
                void abrirHostingMundo(null);
                return; // modal sobre el mundo, sin abrir panel
              } else if (stallType.startsWith("amigo-")) {
                // Burbujas de la trajinerita: "amigo-<accion>:<friendId>"
                const [accion, amigoId] = stallType.split(":");
                if (!amigoId) return;
                if (accion === "amigo-like") {
                  axios
                    .post(`${API_BASE}/social/like/${amigoId}`, null, {
                      headers: { Authorization: `Bearer ${accessToken}` },
                    })
                    .then((res) => toast.ok(res.data?.message || "❤️ Like enviado"))
                    .catch((e) => toast.error(e.response?.data?.detail || "Error al dar like"));
                  return; // el like se queda en el mundo, sin abrir panel
                }
                if (accion === "amigo-visita") {
                  setVisitaAmigoId(amigoId);
                  setTabActiva("amigos");
                } else {
                  // amigo-invita → hostear sala con el amigo preseleccionado
                  const amigo = amigosData.find((a) => a.id === amigoId);
                  void abrirHostingMundo(amigo?.nickname ?? null);
                  return; // modal sobre el mundo, sin abrir panel
                }
              } else if (stallType === "canasta-amigos") {
                // Canasta de mimbre → pergamino de amigos (4 sub-tabs)
                setTabActiva("amigos");
              } else if (stallType === "podio") {
                setTabActiva("rankings");
              } else if (stallType === "gashapon") {
                setTabActiva("gashapon");
              } else if (stallType === "salas") {
                setTabActiva("jugar");
              } else if (stallType === "fountain") {
                // Fuente-banco: conversión FRJ↔AXF
                setTabActiva("tienda");
                setOpenBancoCount((c) => c + 1);
              } else {
                // Puestos del Tianguis → tienda en su sección
                const seccion =
                  stallType === "forja" ? "melter" : stallType === "p2p" ? "market" : "official";
                setStoreSection(seccion);
                setStoreSectionNonce((n) => n + 1);
                setTabActiva("tienda");
              }
              setPanelVisible(true);
            }}
            visible={false}
            initialZone={PAPER_WORLD ? "tianguis" : "nido"}
          />

          {/* HUD TOP BAR — brand (desktop only) → tokens → VIP → settings */}
          <header className="fixed top-0 left-0 right-0 z-40 h-14 flex items-center justify-between px-4 sm:px-6 bg-[#060610]/80 backdrop-blur-xl border-b border-white/5">
            {/* Brand — solo visible en desktop */}
            <div className="hidden sm:flex items-center gap-2 select-none">
              <span className="text-xl">🦎</span>
              <span className="font-extrabold text-base sm:text-lg text-[#FF8DA1] tracking-tight drop-shadow-[0_0_8px_rgba(255,141,161,0.4)]">
                AXOLOTTO
              </span>
            </div>

            <div className="flex items-center gap-1.5 sm:gap-2">
              {/* AXF pill */}
              <div className="relative flex items-center gap-1.5 bg-[#1C1C35]/80 px-2.5 sm:px-3 py-1.5 rounded-full border border-[#E4007C]/20">
                <span className="text-sm select-none">💎</span>
                <span className="text-[#E4007C] font-bold text-sm tabular-nums">{Math.floor(Number(datosBanco.axofichas || 0))}</span>
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

              {/* FRJ pill — no decimals */}
              <button
                onClick={() => {
                  if (isGameLocked) {
                    setTabBlocked(true);
                    return;
                  }
                  setTabActiva('tienda');
                  setOpenBancoCount(c => c + 1);
                }}
                className="relative flex items-center gap-1.5 bg-[#1C1C35]/80 px-2.5 sm:px-3 py-1.5 rounded-full border border-amber-500/20 hover:border-amber-400/50 hover:bg-amber-900/20 transition-all active:scale-95"
                title="Mis Frijolitos"
              >
                <span className="text-sm select-none">🪙</span>
                <span className="text-amber-500 font-bold text-sm tabular-nums">
                  {Number(datosBanco.frijolitos || 0).toFixed(0)}
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
 
              {/* VIP Chip */}
              <VipChip
                vipTier={datosBanco.vip_tier}
                daysRemaining={datosBanco.vip_days_remaining}
                pendingGal={datosBanco.vip_pending_gal}
                onClick={() => {
                  if (isGameLocked) {
                    setTabBlocked(true);
                    return;
                  }
                  setVipModalOpen(true);
                }}
              />
 
              {/* Settings */}
              <button
                onClick={() => {
                  if (isGameLocked) {
                    setTabBlocked(true);
                    return;
                  }
                  setSettingsModalOpen(true);
                }}
                className="p-2 rounded-full bg-[#1C1C35]/80 border border-white/5 text-gray-500 hover:text-[#FF8DA1] hover:bg-[#FF8DA1]/15 hover:border-[#FF8DA1]/30 transition-all"
                title="Ajustes"
              >
                <Settings size={13} />
              </button>
            </div>
          </header>

          {/* Panel de decoración de la sala (slot tipado del diorama) */}
          <DecorSlotPanel
            isOpen={decorSlotId !== null}
            onClose={() => setDecorSlotId(null)}
            slotId={decorSlotId}
            token={accessToken}
            userId={user?.id || ""}
            onChanged={() => {
              setDecorNonce((n) => n + 1); // re-fetch /cave/decorations → diorama
              actualizarSaldosSilencioso(); // la compra gasta FRJ
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

          {/* Hostear sala desde el mundo (mesa de amigos / burbuja 🎲).
              Montaje condicional: cada apertura remonta el modal para que
              tome la visibilidad/invitado preconfigurados. */}
          {hostingOpen && (
            <HostingSetupModal
              token={accessToken}
              isOpen
              onClose={() => setHostingOpen(false)}
              onCreated={() => {
                // Quedarse en el mundo: el wizard de PlayMode no lista salas
                // hosteadas (eso llega en Fase 3 con el Cenote de las Salas).
                toast.ok("🎴 ¡Tu mesa quedó abierta! Tus amigos ya pueden unirse.");
              }}
              tableSeats={hostingSeats}
              initialVisibility="friends"
              inviteNickname={hostingInvite}
            />
          )}

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

          {/* CONTENT AREA — padded away from HUD and dock.
              Con el mundo activo y panel cerrado, el main queda vacío y con
              pointer-events-none para que los taps lleguen al diorama. */}
          <main
            className={`relative z-10 ${tickerFeed.length > 0 ? 'pt-20' : 'pt-14'} pb-20 min-h-screen ${
              PAPER_WORLD && !panelVisible ? 'pointer-events-none' : ''
            }`}
          >
            {/* Tab-lock banner */}
            {tabBlocked && (
              <div className="fixed top-14 left-1/2 -translate-x-1/2 z-50 px-5 py-2 bg-amber-950/90 border border-amber-500/40 text-amber-300 text-xs font-bold rounded-full shadow-[0_0_20px_rgba(245,158,11,0.25)] animate-toast-in">
                🔒 Termina tu partida actual antes de cambiar de zona
              </div>
            )}
            {(!PAPER_WORLD || panelVisible) && (
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
                  initialSection={storeSection}
                  sectionNonce={storeSectionNonce}
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
                  onGameSessionChange={setGameSessionActive}
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
              {/* santuario = El Nido (merged webitos + axolotitos). Legacy criadero/axolotitos ids redirect here.
                  Con el mundo activo solo aparece como panel (gestión: alimentar/eclosionar/expandir). */}
              {(tabActiva === 'santuario' || tabActiva === 'criadero' || tabActiva === 'axolotitos') && (
                <Santuario userId={user?.id || ""} token={accessToken} cambiarTab={(tab) => setTabActiva(tab as TabId)} vipTier={datosBanco?.vip_tier} />
              )}
              {tabActiva === 'rankings'   && <Rankings  userId={user?.id || ""} token={accessToken} cambiarTab={setTabActiva}                   />}
{tabActiva === 'amigos'    && <AmigosPage userId={user?.id || ""} token={accessToken} onNavigate={(tab) => setTabActiva(tab as TabId)} visitFriendId={visitaAmigoId} onVisitHandled={() => setVisitaAmigoId(null)} />}
              {tabActiva === 'gashapon'   && (
                <Gashapon
                  userId={user?.id || ""}
                  token={accessToken}
                  recargarSaldos={actualizarSaldosSilencioso}
                  balances={datosBanco || { frijolitos: 0 }}
                />
              )}
            </div>
            )}
          </main>

          {/* Mundo papel picado: botón flotante para abrir/cerrar el panel de la zona */}
          {PAPER_WORLD && (
            <button
              onClick={() => setPanelVisible((v) => !v)}
              className={`fixed bottom-24 left-1/2 -translate-x-1/2 z-40 px-4 py-2 rounded-full text-sm font-bold border transition-all active:scale-95 ${
                panelVisible
                  ? 'bg-[#1C1C35]/90 text-gray-300 border-white/15 hover:border-white/40'
                  : 'bg-[var(--papel-cempasuchil)] text-black border-transparent shadow-[0_0_18px_rgba(245,158,11,0.45)]'
              }`}
            >
              {panelVisible ? '🌊 Ver mundo' : `📜 ${PANEL_LABELS[tabActiva] ?? 'Abrir panel'}`}
            </button>
          )}

          {/* Mochila flotante — abre el dashboard unificado en la sección seleccionada */}
          <MochilaFloating
            isInventoryOpen={(tabActiva === 'mochila' || tabActiva === 'cartas' || tabActiva === 'tablas') && panelVisible}
            onCloseInventory={() => setPanelVisible(false)}
            onOpenSection={(section) => {
              if (isGameLocked) {
                setTabBlocked(true);
                return;
              }
              // Toggle: if inventory panel is already open, close it
              if ((tabActiva === 'mochila' || tabActiva === 'cartas' || tabActiva === 'tablas') && panelVisible) {
                setPanelVisible(false);
              } else {
                setMochilaInitialTab(section);
                setTabActiva("mochila");
                setPanelVisible(true);
              }
            }}
          />

          {/* Lunar claim floating button — only visible when reward available */}
          {!activeGame?.active && (
            <LunarFloating
              token={accessToken}
              onSuccess={actualizarSaldosSilencioso}
            />
          )}

          {/* BOTTOM DOCK — 3 macrozonas (flag) o 5 zonas legacy */}
          {PAPER_WORLD ? (
            <ZoneDockMacro
              tabActiva={tabActiva}
              dailyClaimAvailable={dailyClaimAvailable}
              onNavigate={(tab, zone) => {
                if (isGameLocked && tab !== 'jugar') {
                  setTabBlocked(true);
                  return;
                }
                setTabActiva(tab);
                setPanelVisible(false); // navegar muestra el mundo limpio
                gameCanvasRef.current?.navigateToZone(zone);
              }}
            />
          ) : (
            <ZoneDock
              zoneTabs={ZONE_TABS}
              tabActiva={tabActiva}
              dailyClaimAvailable={dailyClaimAvailable}
              gameSessionActive={isGameLocked}
              onTabChange={(tab, zone) => {
                if (isGameLocked && tab !== 'jugar') {
                  setTabBlocked(true);
                  return;
                }
                setTabActiva(tab);
                gameCanvasRef.current?.navigateToZone(zone);
              }}
            />
          )}
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

      <TutorialResetButton onReset={handleDevReset} inTutorial={isInTutorial} />

    </div>
  </RealtimeProvider>
  );
}

