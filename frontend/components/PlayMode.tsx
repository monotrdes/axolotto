"use client";
import { API_BASE } from "@/lib/api";

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { createPortal } from 'react-dom';
import axios from 'axios';
import { X, CheckCircle, AlertCircle, Sparkles, Coins } from 'lucide-react';

// ── Sub-components ────────────────────────────────────────────────────────────
import WizardDots          from './WizardDots';
import AxoStatusBar        from './AxoStatusBar';
import ModeSelectScreen    from './screens/ModeSelectScreen';
import AxoSelectScreen     from './screens/AxoSelectScreen';
import BoardSelectScreen   from './screens/BoardSelectScreen';
import BudgetScreen        from './screens/BudgetScreen';
import SalaSelectScreen    from './screens/SalaSelectScreen';
import CpuGameWrapper      from './CpuGameWrapper';
import AutoGameWrapper     from './multiplayer/AutoGameWrapper';
import SettlingScreen      from './screens/SettlingScreen';
import ManualGameWrapper   from './multiplayer/ManualGameWrapper';

// ── Types ─────────────────────────────────────────────────────────────────────

type GameView =
  | 'mode-select'
  | 'axo-select'
  | 'board-select'
  | 'budget'
  | 'sala-select'
  | 'game'
  | 'playing'
  | 'settling';

type GameMode = 'cpu' | 'multi';

interface SavedBudget {
  budget: number;
  lossLimitPct: number;
  profitLimitPct: number;
}

// ── localStorage helpers ──────────────────────────────────────────────────────

function saveBudget(userId: string, axoId: number, data: SavedBudget) {
  try {
    localStorage.setItem(`axolotto_budget_${userId}_${axoId}`, JSON.stringify(data));
  } catch { /* ignore */ }
}

function loadBudget(userId: string, axoId: number): SavedBudget {
  try {
    const raw = localStorage.getItem(`axolotto_budget_${userId}_${axoId}`);
    if (raw) return JSON.parse(raw) as SavedBudget;
  } catch { /* ignore */ }
  return { budget: 100, lossLimitPct: 30, profitLimitPct: 50 };
}

// ── Component ─────────────────────────────────────────────────────────────────

export default function PlayMode({
  userId,
  token,
  balances,
  recargarSaldos,
  lastGameEvent,
  earningsQueue,
  onEarningsSeen,
  onGameSessionChange,
}: {
  userId: string;
  token: string | null;
  balances: any;
  recargarSaldos: () => void;
  lastGameEvent?: number;
  earningsQueue?: number[];
  onEarningsSeen?: () => void;
  onGameSessionChange?: (active: boolean) => void;
}) {
  // ── Data state ──────────────────────────────────────────────────────────────
  const [axolotitos,   setAxolotitos]   = useState<any[]>([]);
  const [playerBoards, setPlayerBoards] = useState<any[]>([]);
  const [allCards,     setAllCards]     = useState<any[]>([]);
  const [cargando,     setCargando]     = useState(true);

  // ── Navigation state ────────────────────────────────────────────────────────
  const [gameView,  setGameView]  = useState<GameView>('axo-select');
  const [gameMode,  setGameMode]  = useState<GameMode>('cpu');
  const directionRef = useRef<'forward' | 'back'>('forward');

  // ── Game wizard state ────────────────────────────────────────────────────────
  const [selectedAxo,      setSelectedAxo]      = useState<any | null>(null);
  const [singleBoardId,    setSingleBoardId]    = useState<number | null>(null);
  const [multiBoards,      setMultiBoards]      = useState<number[]>([]);
  const [selectedRoom,     setSelectedRoom]     = useState<'rookie' | 'champion'>('rookie');
  const [playMode,         setPlayMode]         = useState<'auto' | 'manual'>('auto');
  const [multiplier,       setMultiplier]       = useState<number>(1);
  const [budget,           setBudget]           = useState(100);
  const [lossLimitPct,     setLossLimitPct]     = useState(30);
  const [profitLimitPct,   setProfitLimitPct]   = useState(50);

  // ── UI state ─────────────────────────────────────────────────────────────────
  const [errorMsg,       setErrorMsg]       = useState<string | null>(null);
  const [successMsg,     setSuccessMsg]     = useState<string | null>(null);
  const [saving,         setSaving]         = useState(false);
  const [settling,       setSettling]       = useState(false);
  const [recalling,      setRecalling]      = useState(false);
  const [recallRequested,setRecallRequested]= useState(false);
  const [showReport,     setShowReport]     = useState(false);
  const [activeGame,     setActiveGame]     = useState<any>(null);
  const [settlementReport, setSettlementReport] = useState<any | null>(null);

  // CPU sim replay key — incrementing remounts CpuGameWrapper with fresh state
  const [cpuSimKey, setCpuSimKey] = useState(0);
  // Which axo is being settled inline (for loading spinner in AxoSelectScreen)
  const [settlingAxoId, setSettlingAxoId] = useState<number | null>(null);

  // ── Game session locking ────────────────────────────────────────────────────
  // Tracks whether a CPU game animation is currently active (set by CpuGameWrapper)
  const [cpuGameActive, setCpuGameActive] = useState(false);

  // isGameSessionActive: true when the user is in any active game session
  // — backend status playing/waiting_settlement OR cpu animation in progress
  const backendPlaying =
    selectedAxo?.status === 'playing' || selectedAxo?.status === 'waiting_settlement';
  const isGameSessionActive = backendPlaying || cpuGameActive;

  // Notify parent (play/page.tsx) about game session changes so it can lock tabs
  useEffect(() => {
    onGameSessionChange?.(isGameSessionActive);
  }, [isGameSessionActive, onGameSessionChange]);

  // Floating earnings
  type EscrowNotif = { id: number; amount: number };
  const [escrowNotifs, setEscrowNotifs] = useState<EscrowNotif[]>([]);

  // Ref that always reflects the latest selectedAxo (avoids stale closure in loadData)
  const selectedAxoRef = useRef<any>(null);
  useEffect(() => { selectedAxoRef.current = selectedAxo; }, [selectedAxo]);

  // Ref for onBack — avoids stale closure in popstate handler (onBack defined below)
  const onBackRef = useRef<() => void>(() => {});
  useEffect(() => { onBackRef.current = onBack; });

  // Clock for sleep timer
  const [now, setNow] = useState(new Date());
  const lastSleepRef  = useRef(0);
  useEffect(() => {
    const t = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(t);
  }, []);

  // ── Helpers ──────────────────────────────────────────────────────────────────

  const getSleepTimeLeft = (s: string) => {
    if (!s) return 0;
    const utc = /[Z+]/.test(s) ? s : s + 'Z';
    return Math.max(0, Math.floor((new Date(utc).getTime() - now.getTime()) / 1000));
  };

  const navigate = (view: GameView, direction: 'forward' | 'back' = 'forward') => {
    directionRef.current = direction;
    setGameView(view);
    setErrorMsg(null);
  };

  // ── Data loading ──────────────────────────────────────────────────────────────

  const loadData = useCallback(async () => {
    if (!userId) return;
    try {
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      const [axoRes, boardRes, cardsRes] = await Promise.all([
        axios.get(`${API_BASE}/auth/axolotitos/${userId}`, { headers }),
        axios.get(`${API_BASE}/board/user/${userId}`, { headers }),
        axios.get(`${API_BASE}/shop/cards`),
      ]);
      const sorted = [...axoRes.data].sort((a: any, b: any) =>
        b.level - a.level || b.xp - a.xp || a.id - b.id
      );
      setAxolotitos(sorted);
      setAllCards(cardsRes.data);
      setPlayerBoards(boardRes.data.filter((b: any) => !b.is_dead));
      // Update selectedAxo if it exists — use ref to avoid stale closure
      if (selectedAxoRef.current) {
        const updated = axoRes.data.find((a: any) => a.id === selectedAxoRef.current.id);
        if (updated) setSelectedAxo(updated);
      }
    } catch (err) {
      console.error('PlayMode: error loading data', err);
    } finally {
      setCargando(false);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [userId, token]);

  useEffect(() => { loadData(); }, [userId]);

  // Load last game mode preference from localStorage
  useEffect(() => {
    try {
      const saved = localStorage.getItem('axolotto_last_game_mode') as GameMode | null;
      if (saved === 'cpu' || saved === 'multi') setGameMode(saved);
    } catch { /* ignore */ }
  }, []);

  // Blockchain events
  useEffect(() => {
    if (!lastGameEvent) return;
    loadData(); recargarSaldos();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [lastGameEvent]);

  // Floating earnings
  useEffect(() => {
    if (!earningsQueue?.length) return;
    const t = Date.now();
    const notifs: EscrowNotif[] = earningsQueue.map((amt, i) => ({ id: t + i, amount: amt }));
    setEscrowNotifs(prev => [...prev, ...notifs]);
    notifs.forEach(n => setTimeout(() => setEscrowNotifs(prev => prev.filter(x => x.id !== n.id)), 2500));
    onEarningsSeen?.();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [earningsQueue?.length]);

  // Sleep timer auto-refresh
  useEffect(() => {
    const hasExpired = axolotitos.some(
      a => a.status === 'sleeping' && a.sleep_expires_at && getSleepTimeLeft(a.sleep_expires_at) <= 0
    );
    if (hasExpired && Date.now() - lastSleepRef.current > 5000) {
      lastSleepRef.current = Date.now();
      loadData();
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [now]);

  // Polling while axo is playing
  const hasPlayingAxo = axolotitos.some(a => a.status === 'playing' || a.status === 'playing_manual');
  useEffect(() => {
    if (!hasPlayingAxo) return;
    const id = setInterval(() => { loadData(); recargarSaldos(); }, 15_000);
    return () => clearInterval(id);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [hasPlayingAxo]);

  // Intercept browser back button during active game OR wizard to avoid losing state
  useEffect(() => {
    const wizardViews: GameView[] = ['mode-select', 'board-select', 'budget', 'sala-select', 'game'];
    // Always block back when a game session is active (any view)
    // Also block back inside wizard views (normal navigation)
    const shouldBlock = isGameSessionActive || wizardViews.includes(gameView);
    if (!shouldBlock) return;

    window.history.pushState({ playMode: true }, '');

    const handlePopState = () => {
      if (isGameSessionActive) {
        // Game is active — block back entirely, just re-push state
        window.history.pushState({ playMode: true }, '');
      } else {
        // Normal wizard navigation — go back one step
        onBackRef.current();
        window.history.pushState({ playMode: true }, '');
      }
    };

    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, [gameView, isGameSessionActive]);

  // Warn before leaving page during active game session
  useEffect(() => {
    if (!isGameSessionActive) return;
    const handler = (e: BeforeUnloadEvent) => {
      e.preventDefault();
      e.returnValue = ''; // Chrome requires returnValue to be set
    };
    window.addEventListener('beforeunload', handler);
    return () => window.removeEventListener('beforeunload', handler);
  }, [isGameSessionActive]);

  // Recall cleared when axo stops playing
  useEffect(() => {
    if (selectedAxo?.status !== 'playing') setRecallRequested(false);
  }, [selectedAxo?.status]);

  // Auto-navigate to playing/settling if selected axo changes status
  useEffect(() => {
    if (!selectedAxo) return;
    if ((selectedAxo.status === 'playing' || selectedAxo.status === 'playing_manual') && gameView !== 'playing' && gameView !== 'settling') {
      navigate('playing');
    }
    // Don't auto-navigate if on axo-select — user handles settlement inline there
    if (selectedAxo.status === 'waiting_settlement' && !['axo-select', 'settling'].includes(gameView)) {
      navigate('settling');
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedAxo?.status]);

  const checkActiveGame = useCallback(async () => {
    if (!userId || !token) return;
    try {
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      const res = await axios.get(`${API_BASE}/multiplayer/active-check`, { headers });
      setActiveGame(res.data);
      if (res.data?.active) {
        const axo = axolotitos.find(a => a.id === res.data.axolotito_id);
        if (axo) {
          setSelectedAxo(axo);
        }
      }
    } catch (err) {
      console.error("Error running active-check:", err);
    }
  }, [userId, token, axolotitos]);

  useEffect(() => {
    checkActiveGame();
    const id = setInterval(checkActiveGame, 5000);
    return () => clearInterval(id);
  }, [checkActiveGame]);

  // Navigate to playing if active game is detected
  useEffect(() => {
    if (activeGame?.active && gameView !== 'playing' && gameView !== 'settling') {
      navigate('playing');
    }
  }, [activeGame, gameView]);

  // ── Action handlers ────────────────────────────────────────────────────────

  const withError = async (fn: () => Promise<void>) => {
    setErrorMsg(null);
    try { await fn(); }
    catch (err: any) { setErrorMsg(err.response?.data?.detail ?? 'Error inesperado.'); }
  };

  const handleFeed = (type: 'pellet' | 'shrimp') => withError(async () => {
    if (!selectedAxo) return;
    const headers = token ? { Authorization: `Bearer ${token}` } : {};
    const res = await axios.post(
      `${API_BASE}/game/axolotitos/${selectedAxo.id}/feed`,
      { food_type: type },
      { headers }
    );
    setSuccessMsg(res.data.mensaje);
    recargarSaldos(); loadData();
    setTimeout(() => setSuccessMsg(null), 3000);
  });

  const handleSleep = () => withError(async () => {
    if (!selectedAxo) return;
    const headers = token ? { Authorization: `Bearer ${token}` } : {};
    await axios.post(`${API_BASE}/game/axolotitos/${selectedAxo.id}/sleep`, {}, { headers });
    loadData();
  });

  const handleWake = () => withError(async () => {
    if (!selectedAxo) return;
    const headers = token ? { Authorization: `Bearer ${token}` } : {};
    await axios.post(`${API_BASE}/game/axolotitos/${selectedAxo.id}/wake`, {}, { headers });
    loadData();
  });

  const handleAxoAction = (action: 'feed-pellet' | 'feed-shrimp' | 'sleep' | 'wake') => {
    if (action === 'feed-pellet') return handleFeed('pellet');
    if (action === 'feed-shrimp') return handleFeed('shrimp');
    if (action === 'sleep')       return handleSleep();
    if (action === 'wake')        return handleWake();
  };

  const handleRegisterMultiplayer = async () => {
    if (!selectedAxo || multiBoards.length === 0) {
      setErrorMsg('Selecciona al menos una tabla.');
      return;
    }
    setSaving(true);
    setErrorMsg(null);
    try {
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      saveBudget(userId, selectedAxo.id, { budget, lossLimitPct, profitLimitPct });
      const res = await axios.post(
        `${API_BASE}/multiplayer/register`,
        {
          axolotito_id: selectedAxo.id,
          room_type: selectedRoom,
          boards: multiBoards,
          budget_gal: budget,
          loss_limit_pct: lossLimitPct,
          profit_limit_pct: profitLimitPct,
          play_mode: playMode,
        },
        { headers }
      );
      setSuccessMsg(res.data.mensaje);
      recargarSaldos(); loadData();
      setTimeout(() => setSuccessMsg(null), 3000);
      navigate('playing');
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail ?? 'Error al inscribirse.');
    } finally {
      setSaving(false);
    }
  };

  const handleSettle = async () => {
    if (!selectedAxo) return;
    setSettling(true);
    setErrorMsg(null);
    try {
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      const res = await axios.post(
        `${API_BASE}/multiplayer/settle?axolotito_id=${selectedAxo.id}`,
        {},
        { headers }
      );
      setSettlementReport(res.data);
      setShowReport(true);
      recargarSaldos(); loadData();
      // After settle, go back to axo-select with updated axo
      setTimeout(() => navigate('axo-select'), 300);
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail ?? 'Error al liquidar.');
    } finally {
      setSettling(false);
    }
  };

  // Settle an axo directly from AxoSelectScreen without navigating away
  const handleSettleInline = async (axo: any) => {
    setSettlingAxoId(axo.id);
    setErrorMsg(null);
    try {
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      const res = await axios.post(
        `${API_BASE}/multiplayer/settle?axolotito_id=${axo.id}`,
        {},
        { headers }
      );
      setSettlementReport(res.data);
      setShowReport(true);
      recargarSaldos();
      loadData();
      // Deselect the axo so user picks fresh after settlement
      if (selectedAxo?.id === axo.id) setSelectedAxo(null);
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail ?? 'Error al liquidar.');
    } finally {
      setSettlingAxoId(null);
    }
  };

  const handleRecall = async () => {
    if (!selectedAxo) return;
    setRecalling(true);
    setErrorMsg(null);
    try {
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      await axios.post(`${API_BASE}/multiplayer/recall?axolotito_id=${selectedAxo.id}`, {}, { headers });
      setRecallRequested(true);
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail ?? 'Error al llamar.');
    } finally {
      setRecalling(false);
    }
  };

  const handleToggleMultiBoard = (id: number) => {
    if (multiBoards.includes(id)) {
      setMultiBoards(multiBoards.filter(x => x !== id));
    } else {
      if (multiBoards.length >= 3) {
        setErrorMsg('Máximo 3 tablas.');
        setTimeout(() => setErrorMsg(null), 3000);
        return;
      }
      setMultiBoards([...multiBoards, id]);
    }
  };

  // ── Wizard metadata ────────────────────────────────────────────────────────

  // axo-select is now the entry point — no dots there
  // dots start at mode-select (step 0) once axo is chosen
  const cpuSteps   = ['Modo', 'Tabla'];
  const multiSteps = ['Modo', 'Tablas', 'Presupuesto', 'Sala'];

  const wizardConfig: Record<GameView, { steps: string[]; current: number; showDots: boolean } | null> = {
    'axo-select':  null,
    'mode-select': { steps: gameMode === 'cpu' ? cpuSteps : multiSteps, current: 0, showDots: true },
    'board-select':{ steps: gameMode === 'cpu' ? cpuSteps : multiSteps, current: 1, showDots: true },
    'budget':      { steps: multiSteps, current: 2, showDots: true },
    'sala-select': { steps: multiSteps, current: 3, showDots: true },
    'game':        null,
    'playing':     null,
    'settling':    null,
  };

  const onBack = () => {
    // Block back navigation during active game session
    if (isGameSessionActive) return;
    if (gameView === 'mode-select')  return navigate('axo-select',  'back');
    if (gameView === 'board-select') return navigate('mode-select', 'back');
    if (gameView === 'budget')       return navigate('board-select','back');
    if (gameView === 'sala-select')  return navigate('budget',      'back');
    if (gameView === 'game')         return navigate('board-select','back');
  };

  // Show AxoStatusBar from mode-select onwards (axo already selected by then)
  const showAxoStatusBar = selectedAxo !== null && !['axo-select', 'game', 'playing', 'settling'].includes(gameView);

  // ── Animation class ────────────────────────────────────────────────────────
  const animClass = directionRef.current === 'back' ? 'animate-slide-step-back' : 'animate-slide-step';

  // ── Loading ────────────────────────────────────────────────────────────────
  if (cargando) {
    return (
      <div className="text-center py-20">
        <div className="w-16 h-16 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
        <p className="text-slate-400 font-bold tracking-widest animate-pulse uppercase">Cargando salas de lotería...</p>
      </div>
    );
  }

  // ── Render current screen ──────────────────────────────────────────────────
  const wiz = wizardConfig[gameView];

  return (
    <div className="w-full mt-6 bg-slate-950/80 backdrop-blur-md text-white rounded-[2rem] p-4 sm:p-8 border border-indigo-500/20 shadow-[0_0_40px_rgba(99,102,241,0.15)] relative">

      {/* Global notifications */}
      {errorMsg && (
        <div className="mb-4 bg-red-950/60 border border-red-500/30 text-red-200 text-xs font-bold rounded-2xl p-4 flex items-center gap-3">
          <AlertCircle className="text-red-400 shrink-0" size={18} />
          <span className="flex-1">{errorMsg}</span>
          <button onClick={() => setErrorMsg(null)} className="text-red-400 hover:text-white"><X size={14} /></button>
        </div>
      )}
      {successMsg && (
        <div className="mb-4 bg-indigo-950/60 border border-indigo-500/30 text-indigo-200 text-xs font-bold rounded-2xl p-4 flex items-center gap-3">
          <CheckCircle className="text-indigo-400 shrink-0" size={18} />
          <span>{successMsg}</span>
        </div>
      )}

      {/* WizardDots */}
      {wiz?.showDots && (
        <WizardDots steps={wiz.steps} current={wiz.current} onBack={onBack} />
      )}

      {/* AxoStatusBar (persistent from axo-select onwards, except cpu-sim/playing/settling) */}
      {showAxoStatusBar && (
        <AxoStatusBar
          axo={selectedAxo}
          getSleepTimeLeft={getSleepTimeLeft}
          onAction={handleAxoAction}
        />
      )}

      {/* Screen container with transition */}
      <div key={gameView} className={animClass}>

        {/* ── axo-select ────────────────────────────────────────────────────── */}
        {/* Entry point: choose your axolotito before anything else             */}
        {gameView === 'axo-select' && (
          <AxoSelectScreen
            axolotitos={axolotitos}
            selectedAxo={selectedAxo}
            onSelect={(axo) => {
              setSelectedAxo(axo);
              // Pre-load saved budget for any mode
              if (axo) {
                const saved = loadBudget(userId, axo.id);
                setBudget(saved.budget);
                setLossLimitPct(saved.lossLimitPct);
                setProfitLimitPct(saved.profitLimitPct);
              }
            }}
            onContinue={() => navigate('mode-select')}
            getSleepTimeLeft={getSleepTimeLeft}
            onFeed={(type) => handleFeed(type)}
            onSleep={handleSleep}
            onWake={handleWake}
            onSettleInline={handleSettleInline}
            settlingAxoId={settlingAxoId}
          />
        )}

        {/* ── mode-select ───────────────────────────────────────────────────── */}
        {/* Step 0: CPU or Multiplayer — axo is already chosen at this point    */}
        {gameView === 'mode-select' && (
          <ModeSelectScreen
            selectedAxo={selectedAxo}
            onSelect={(mode) => {
              setGameMode(mode);
              setSingleBoardId(null);
              setMultiBoards([]);
              setErrorMsg(null);
              try { localStorage.setItem('axolotto_last_game_mode', mode); } catch {}
              navigate('board-select');
            }}
          />
        )}

        {/* ── board-select ──────────────────────────────────────────────────── */}
        {gameView === 'board-select' && (
          <BoardSelectScreen
            mode={gameMode}
            playerBoards={playerBoards}
            allCards={allCards}
            axolotitos={axolotitos}
            selectedAxo={selectedAxo!}
            singleBoardId={singleBoardId}
            onSelectSingle={setSingleBoardId}
            multiBoards={multiBoards}
            onToggleMulti={handleToggleMultiBoard}
            selectedRoom={selectedRoom}
            onRoomChange={setSelectedRoom}
            multiplier={multiplier}
            onMultiplierChange={setMultiplier}
            onPlay={() => navigate('game')}
            onContinue={() => navigate('budget')}
            error={errorMsg}
            onClearError={() => setErrorMsg(null)}
          />
        )}

        {/* ── budget ────────────────────────────────────────────────────────── */}
        {gameView === 'budget' && (
          <BudgetScreen
            balances={balances}
            budget={budget}
            lossLimitPct={lossLimitPct}
            profitLimitPct={profitLimitPct}
            onBudgetChange={setBudget}
            onLossChange={setLossLimitPct}
            onProfitChange={setProfitLimitPct}
            onContinue={() => {
              if (selectedAxo) saveBudget(userId, selectedAxo.id, { budget, lossLimitPct, profitLimitPct });
              navigate('sala-select');
            }}
            error={errorMsg}
          />
        )}

        {/* ── sala-select ───────────────────────────────────────────────────── */}
        {gameView === 'sala-select' && (
          <SalaSelectScreen
            token={token}
            selectedRoom={selectedRoom}
            onRoomSelect={setSelectedRoom}
            playMode={playMode}
            onPlayModeChange={setPlayMode}
            onPlay={handleRegisterMultiplayer}
            registering={saving}
            error={errorMsg}
            budget={budget}
            multiBoards={multiBoards}
          />
        )}

        {/* ── game (CPU) ────────────────────────────────────────────────────── */}
        {/* key={cpuSimKey} causes a clean remount when "Jugar Otra Vez" is     */}
        {/* pressed — same axo/board/room, phase resets to 'loading'             */}
        {gameView === 'game' && selectedAxo && singleBoardId && (
          <CpuGameWrapper
            key={cpuSimKey}
            userId={userId}
            token={token}
            selectedAxo={selectedAxo}
            selectedBoardId={singleBoardId}
            playerBoards={playerBoards}
            allCards={allCards}
            selectedRoom={selectedRoom}
            multiplier={multiplier}
            onDone={() => { recargarSaldos(); loadData(); }}
            onPlayAgainInPlace={() => {
              setCpuGameActive(true);
              setCpuSimKey(k => k + 1);
            }}
            onChangeBoard={() => {
              setCpuGameActive(false);
              setSingleBoardId(null);
              navigate('board-select');
            }}
            onChangeAll={() => {
              setCpuGameActive(false);
              setSingleBoardId(null);
              setMultiBoards([]);
              setSelectedAxo(null);
              navigate('axo-select');
            }}
            onGameActiveChange={setCpuGameActive}
          />
        )}

        {/* ── playing ───────────────────────────────────────────────────────── */}
        {gameView === 'playing' && selectedAxo && (
          activeGame?.active && activeGame?.play_mode === "manual" ? (
            <ManualGameWrapper
              roomId={activeGame.room_id}
              axolotitoId={activeGame.axolotito_id}
              token={token}
              playMode={activeGame.play_mode}
              onDone={() => {
                setActiveGame(null);
                recargarSaldos();
                loadData();
                navigate('axo-select');
              }}
            />
          ) : (
            <AutoGameWrapper
              axolotitoId={selectedAxo.id}
              token={token}
              allCards={allCards}
              playerBoards={playerBoards}
              budget={budget}
              recallRequested={recallRequested}
              recalling={recalling}
              onRecall={handleRecall}
              escrowNotifs={escrowNotifs}
              onDone={() => {
                setActiveGame(null);
                recargarSaldos();
                loadData();
                navigate('axo-select');
              }}
            />
          )
        )}

        {/* ── settling ──────────────────────────────────────────────────────── */}
        {gameView === 'settling' && selectedAxo && (
          <SettlingScreen
            selectedAxo={selectedAxo}
            settling={settling}
            onSettle={handleSettle}
            error={errorMsg}
          />
        )}

      </div>

      {/* Settlement report modal */}
      {showReport && settlementReport && typeof window !== 'undefined' && createPortal(
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
          <div className="relative w-full max-w-md bg-slate-900/90 border border-emerald-500/30 rounded-[2.5rem] shadow-[0_0_50px_rgba(52,211,153,0.25)] p-6 animate-result-fade-in">
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-64 h-24 blur-3xl opacity-20 rounded-full bg-emerald-500 pointer-events-none" />
            <button
              onClick={() => setShowReport(false)}
              className="absolute top-5 right-5 text-slate-400 hover:text-white border border-slate-800 bg-slate-950 p-2 rounded-xl transition-all z-20"
            >
              <X size={15} />
            </button>
            <div className="text-center mb-5 relative z-10">
              <span className="text-[10px] font-black px-4 py-1.5 rounded-full border bg-emerald-950/80 border-emerald-500/30 text-emerald-300 uppercase tracking-widest">
                Liquidación Completada
              </span>
              <h3 className="text-2xl font-black italic mt-3 text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-teal-300">
                ❤️ ¡Gracias por el esfuerzo!
              </h3>
              {settlementReport.mensaje && (
                <p className="text-xs text-slate-400 mt-1">{settlementReport.mensaje}</p>
              )}
            </div>
            <div className="grid grid-cols-2 gap-3 relative z-10">
              <div className="bg-slate-950/80 border border-white/5 rounded-2xl p-3 text-center">
                <p className="text-[9px] text-slate-500 uppercase tracking-widest font-black mb-1">FRJ Devueltas</p>
                <p className="text-lg font-black text-amber-400 flex items-center justify-center gap-1">
                  <Coins size={13} /> {settlementReport.refunded_gal ?? '—'}
                </p>
              </div>
              <div className="bg-slate-950/80 border border-white/5 rounded-2xl p-3 text-center">
                <p className="text-[9px] text-slate-500 uppercase tracking-widest font-black mb-1">Rendimiento</p>
                <p className={`text-lg font-black ${(settlementReport.net_performance ?? 0) >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                  {(settlementReport.net_performance ?? 0) >= 0 ? '+' : ''}{settlementReport.net_performance ?? '—'}
                </p>
              </div>
              {settlementReport.loyalty_points_gained != null && (
                <div className="col-span-2 bg-indigo-950/40 border border-indigo-500/20 rounded-2xl p-3 text-center">
                  <p className="text-[9px] text-indigo-400 uppercase tracking-widest font-black mb-1">Puntos de Lealtad</p>
                  <p className="text-lg font-black text-indigo-300 flex items-center justify-center gap-1">
                    <Sparkles size={13} /> +{settlementReport.loyalty_points_gained}
                    <span className="text-[10px] text-slate-400 ml-1">({settlementReport.total_loyalty_points} total)</span>
                  </p>
                </div>
              )}
            </div>
            <div className="mt-5 text-center relative z-10">
              <button
                onClick={() => setShowReport(false)}
                className="px-8 py-3 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-black uppercase tracking-widest rounded-xl transition-all active:scale-95"
              >
                Cerrar
              </button>
            </div>
          </div>
        </div>,
        document.body
      )}
    </div>
  );
}
