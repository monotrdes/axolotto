"use client";
import React, { useState, useEffect, useRef, useCallback } from 'react';
import { X, Trophy, Zap, Timer, Coins, Medal, ArrowLeft } from 'lucide-react';
import { useToast } from '@/context/ToastContext';
import { submitArcadeScore, fetchArcadeLeaderboard } from '@/services/santuarioService';

// ── Types ──────────────────────────────────────────────────
interface InteractiveArcadeProps {
  isOpen: boolean;
  onClose: () => void;
  token: string | null;
  userId: string;
}

type ArcadePhase = 'menu' | 'playing' | 'gameover' | 'leaderboard';

interface Bubble {
  id: number;
  x: number;        // 0-100 (percent of game area width)
  y: number;        // 0-100 (percent, 0 = bottom)
  speed: number;    // percent per frame
  color: string;
  size: number;     // px
  opacity: number;
}

interface LeaderboardEntry {
  id: number;
  user_id: string;
  cave_name: string | null;
  score: number;
  played_at: string;
}

// ── Bubble colors ──────────────────────────────────────────
const BUBBLE_COLORS = [
  '#FF6B6B', '#FFE66D', '#4ECDC4', '#45B7D1',
  '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8',
  '#F7DC6F', '#BB8FCE', '#85C1E9', '#F1948A',
];

// ── GAME CONSTANTS ─────────────────────────────────────────
const GAME_DURATION_SEC = 30;
const BUBBLE_BASE_POINTS = 10;
const COMBO_TIMEOUT_MS = 500;
const MIN_SPAWN_INTERVAL_MS = 300;
const MAX_SPAWN_INTERVAL_MS = 800;
const MAX_BUBBLES = 35;
const COST_AXF = 1;

// ── COMPONENT ──────────────────────────────────────────────
export default function InteractiveArcade({ isOpen, onClose, token, userId }: InteractiveArcadeProps) {
  const { toast } = useToast();

  // ── State ────────────────────────────────────────────────
  const [phase, setPhase] = useState<ArcadePhase>('menu');
  const [bubbles, setBubbles] = useState<Bubble[]>([]);
  const [score, setScore] = useState(0);
  const [timeLeft, setTimeLeft] = useState(GAME_DURATION_SEC);
  const [comboCount, setComboCount] = useState(0);
  const [comboMultiplier, setComboMultiplier] = useState(1);
  const [finalScore, setFinalScore] = useState(0);
  const [personalBest, setPersonalBest] = useState<number | null>(null);
  const [isNewRecord, setIsNewRecord] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [loadingLB, setLoadingLB] = useState(false);
  const [poppingBubbles, setPoppingBubbles] = useState<Set<number>>(new Set());
  const [countdown, setCountdown] = useState<number | null>(null);

  // ── Refs ─────────────────────────────────────────────────
  const bubblesRef      = useRef<Bubble[]>([]);
  const scoreRef        = useRef(0);
  const timeLeftRef     = useRef(GAME_DURATION_SEC);
  const gameActiveRef   = useRef(false);
  const animFrameRef    = useRef<number>(0);
  const spawnTimerRef   = useRef<ReturnType<typeof setTimeout> | null>(null);
  const comboRef        = useRef({ count: 0, lastTime: 0, multiplier: 1 });
  const bubbleIdRef     = useRef(0);
  const gameAreaRef     = useRef<HTMLDivElement>(null);
  const nextSpawnRef    = useRef(0);
  const startTimeRef    = useRef(0);
  const timerIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // ── Cleanup ──────────────────────────────────────────────
  useEffect(() => {
    return () => {
      gameActiveRef.current = false;
      if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);
      if (spawnTimerRef.current) clearTimeout(spawnTimerRef.current);
      if (timerIntervalRef.current) clearInterval(timerIntervalRef.current);
    };
  }, []);

  // ── Generate random bubble ───────────────────────────────
  const createBubble = useCallback((): Bubble => {
    const size = 28 + Math.random() * 24; // 28-52px
    return {
      id: bubbleIdRef.current++,
      x: 8 + Math.random() * 84,          // 8-92%
      y: -size,                            // start below visible area (negative since we use bottom-based positioning now)
      speed: 0.15 + Math.random() * 0.25,  // % per frame
      color: BUBBLE_COLORS[Math.floor(Math.random() * BUBBLE_COLORS.length)],
      size,
      opacity: 0.7 + Math.random() * 0.3,
    };
  }, []);

  // ── Spawn a bubble ───────────────────────────────────────
  const spawnBubble = useCallback(() => {
    if (!gameActiveRef.current) return;
    const newBubble = createBubble();
    bubblesRef.current = [...bubblesRef.current, newBubble];
    setBubbles([...bubblesRef.current]);

    // Schedule next spawn
    const delay = MIN_SPAWN_INTERVAL_MS + Math.random() * (MAX_SPAWN_INTERVAL_MS - MIN_SPAWN_INTERVAL_MS);
    nextSpawnRef.current = performance.now() + delay;
  }, [createBubble]);

  // ── Game loop ────────────────────────────────────────────
  const gameLoop = useCallback((now: number) => {
    if (!gameActiveRef.current) return;

    // Update bubble positions (move up)
    const updated = bubblesRef.current
      .map(b => ({
        ...b,
        y: b.y + b.speed,
      }))
      .filter(b => b.y < 120); // Remove if off screen top

    bubblesRef.current = updated;

    // Spawn new bubbles on schedule
    if (now >= nextSpawnRef.current) {
      spawnBubble();
    }

    // Sync to React state for rendering
    setBubbles([...updated]);

    animFrameRef.current = requestAnimationFrame(gameLoop);
  }, [spawnBubble]);

  // ── Timer tick ───────────────────────────────────────────
  const startTimer = useCallback(() => {
    timerIntervalRef.current = setInterval(() => {
      timeLeftRef.current -= 1;
      setTimeLeft(timeLeftRef.current);

      if (timeLeftRef.current <= 0) {
        endGameRef.current();
      }
    }, 1000);
  }, []);

  // Keep endGame accessible to timer
  const endGameRef = useRef<() => void>(() => {});
  const endGame = useCallback(() => {
    gameActiveRef.current = false;
    if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);
    if (spawnTimerRef.current) clearTimeout(spawnTimerRef.current);
    if (timerIntervalRef.current) clearInterval(timerIntervalRef.current);

    setFinalScore(scoreRef.current);
    setPhase('gameover');

    // Submit score
    setSubmitting(true);
    submitArcadeScore(scoreRef.current, token)
      .then(res => {
        if (res.is_new_record) {
          setIsNewRecord(true);
        }
        if (res.personal_best != null) {
          setPersonalBest(res.personal_best);
        } else {
          setPersonalBest(scoreRef.current);
        }
      })
      .catch(() => {
        // Fallback — score saved locally
        setPersonalBest(prev => Math.max(prev ?? 0, scoreRef.current));
      })
      .finally(() => setSubmitting(false));
  }, [token]);

  endGameRef.current = endGame;

  // ── Pop bubble handler ────────────────────────────────────
  const handlePopBubble = useCallback((bubbleId: number, e: React.MouseEvent | React.TouchEvent) => {
    e.stopPropagation();
    if (!gameActiveRef.current) return;

    // Check if bubble still exists
    const idx = bubblesRef.current.findIndex(b => b.id === bubbleId);
    if (idx === -1) return;

    // Remove bubble
    bubblesRef.current.splice(idx, 1);
    setBubbles([...bubblesRef.current]);

    // Visual pop
    setPoppingBubbles(prev => new Set(prev).add(bubbleId));
    setTimeout(() => {
      setPoppingBubbles(prev => {
        const next = new Set(prev);
        next.delete(bubbleId);
        return next;
      });
    }, 200);

    // Combo logic
    const now = performance.now();
    const combo = comboRef.current;
    if (now - combo.lastTime < COMBO_TIMEOUT_MS) {
      combo.count += 1;
      combo.multiplier = Math.min(10, 1 + Math.floor(combo.count / 3));
    } else {
      combo.count = 1;
      combo.multiplier = 1;
    }
    combo.lastTime = now;
    setComboCount(combo.count);
    setComboMultiplier(combo.multiplier);

    // Score
    const points = BUBBLE_BASE_POINTS * combo.multiplier;
    scoreRef.current += points;
    setScore(scoreRef.current);
  }, []);

  // ── Start game with countdown ────────────────────────────
  const handleStartGame = () => {
    // Reset game state
    bubblesRef.current = [];
    scoreRef.current = 0;
    timeLeftRef.current = GAME_DURATION_SEC;
    comboRef.current = { count: 0, lastTime: 0, multiplier: 1 };
    bubbleIdRef.current = 0;
    setIsNewRecord(false);

    setBubbles([]);
    setScore(0);
    setTimeLeft(GAME_DURATION_SEC);
    setComboCount(0);
    setComboMultiplier(1);
    setFinalScore(0);
    setPoppingBubbles(new Set());

    // 3-2-1 countdown
    setCountdown(3);
    let cd = 3;
    const cdInterval = setInterval(() => {
      cd -= 1;
      if (cd <= 0) {
        clearInterval(cdInterval);
        setCountdown(null);
        // Actually start game
        gameActiveRef.current = true;
        startTimeRef.current = performance.now();
        nextSpawnRef.current = performance.now() + 500;
        setPhase('playing');
        animFrameRef.current = requestAnimationFrame(gameLoop);
        startTimer();
      } else {
        setCountdown(cd);
      }
    }, 800);
  };

  // ── Leaderboard fetch ────────────────────────────────────
  const handleOpenLeaderboard = async () => {
    setPhase('leaderboard');
    setLoadingLB(true);
    try {
      const data = await fetchArcadeLeaderboard(token);
      setLeaderboard(data || []);
    } catch {
      setLeaderboard([]);
      toast.error('No se pudo cargar la tabla de clasificación');
    } finally {
      setLoadingLB(false);
    }
  };

  // ── Score animation ──────────────────────────────────────
  const [animatedDisplayScore, setAnimatedDisplayScore] = useState(0);
  useEffect(() => {
    if (phase !== 'gameover') return;
    // Count-up animation
    const target = finalScore;
    let current = 0;
    const step = Math.max(1, Math.floor(target / 30));
    const interval = setInterval(() => {
      current = Math.min(target, current + step);
      setAnimatedDisplayScore(current);
      if (current >= target) clearInterval(interval);
    }, 40);
    return () => clearInterval(interval);
  }, [phase, finalScore]);

  if (!isOpen) return null;

  // ── RENDER: MENU ─────────────────────────────────────────
  const renderMenu = () => (
    <div className="flex flex-col items-center gap-3">
      {/* Marquee */}
      <div className="w-full text-center py-2">
        <h3 className="text-lg font-black text-white uppercase tracking-tighter"
            style={{ textShadow: '0 0 10px rgba(0,255,136,0.5)' }}>
          <span className="text-[#00ff88]">ALGAS</span> ARCADE
        </h3>
        <p className="text-[9px] text-slate-500 font-bold uppercase tracking-widest mt-0.5">
          1 AXF por partida · Burbujas y diversión
        </p>
      </div>

      {/* Cabinet screen mockup */}
      <div className="w-full rounded-2xl overflow-hidden border-2 border-slate-700 bg-slate-950/80">
        <div className="p-6 flex flex-col items-center gap-3">
          <div className="text-5xl mb-1">🕹️</div>
          <p className="text-[10px] text-slate-400 font-bold text-center leading-relaxed max-w-xs">
            ¡Atrapa burbujas mágicas en el cenote!<br />
            Combos y reflejos — ¿cuántos puntos harás?
          </p>

          <div className="flex items-center gap-4 text-[9px] font-bold text-slate-500">
            <span className="flex items-center gap-1"><Timer size={11} /> {GAME_DURATION_SEC}s</span>
            <span className="flex items-center gap-1"><Zap size={11} /> Combos x10</span>
            <span className="flex items-center gap-1"><Coins size={11} /> {COST_AXF} AXF</span>
          </div>

          <button
            onClick={handleStartGame}
            className="w-full py-3.5 bg-gradient-to-r from-[#00ff88] to-emerald-600 hover:from-[#33ff99] hover:to-emerald-500 text-slate-900 font-black rounded-xl uppercase tracking-widest text-xs shadow-lg shadow-[#00ff88]/20 active:scale-95 transition-all animate-pulse"
          >
            ▶ INSERTAR AXF
          </button>
        </div>
      </div>

      {/* Leaderboard button */}
      <button
        onClick={handleOpenLeaderboard}
        className="w-full py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 font-black rounded-xl uppercase tracking-widest text-[10px] border border-white/5 transition-all active:scale-95 flex items-center justify-center gap-1.5"
      >
        <Trophy size={12} /> 🏆 Records
      </button>

      {/* Footer */}
      <p className="text-[7px] text-slate-700 font-bold text-center">
        Los puntos se registran automáticamente al finalizar
      </p>
    </div>
  );

  // ── RENDER: PLAYING ──────────────────────────────────────
  const renderPlaying = () => (
    <div className="flex flex-col gap-2">
      {/* HUD: Timer + Score + Combo */}
      <div className="flex items-center justify-between px-1">
        {/* Timer bar */}
        <div className="flex-1 mr-3">
          <div className="flex items-center justify-between mb-0.5">
            <span className="text-[8px] font-black text-slate-400 uppercase tracking-wider flex items-center gap-1">
              <Timer size={10} /> Tiempo
            </span>
            <span className={`text-[10px] font-black tabular-nums ${timeLeft <= 5 ? 'text-red-400 animate-pulse' : 'text-slate-300'}`}>
              {timeLeft}s
            </span>
          </div>
          <div className="h-1.5 bg-slate-800 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-1000 ${
                timeLeft <= 5 ? 'bg-red-500' : timeLeft <= 10 ? 'bg-yellow-500' : 'bg-[#00ff88]'
              }`}
              style={{ width: `${(timeLeft / GAME_DURATION_SEC) * 100}%` }}
            />
          </div>
        </div>

        {/* Score */}
        <div className="text-right">
          <div className="text-[8px] font-black text-slate-500 uppercase tracking-wider">Puntaje</div>
          <div className="text-lg font-black text-white tabular-nums">{score}</div>
        </div>
      </div>

      {/* Combo indicator */}
      {comboMultiplier > 1 && (
        <div className="text-center -mt-1 mb-0.5">
          <span className="inline-flex items-center gap-1 text-[10px] font-black text-amber-400 bg-amber-950/60 px-2 py-0.5 rounded-full border border-amber-500/30 animate-pulse">
            <Zap size={10} /> x{comboMultiplier} COMBO! ({comboCount})
          </span>
        </div>
      )}

      {/* Game area */}
      <div
        ref={gameAreaRef}
        className="relative w-full h-72 rounded-2xl overflow-hidden border-2 border-slate-700 bg-gradient-to-b from-slate-950 via-blue-950/30 to-slate-950 cursor-crosshair select-none"
        style={{
          backgroundImage: `
            repeating-linear-gradient(
              0deg,
              transparent,
              transparent 2px,
              rgba(0,0,0,0.08) 2px,
              rgba(0,0,0,0.08) 4px
            ),
            radial-gradient(ellipse at 50% 100%, rgba(0,170,255,0.05) 0%, transparent 70%)
          `,
        }}
      >
        {/* Bubbles */}
        {bubbles.map(bubble => (
          <div
            key={bubble.id}
            className="absolute rounded-full cursor-pointer transition-opacity select-none"
            style={{
              left: `${bubble.x}%`,
              bottom: `${bubble.y}%`,
              width: `${bubble.size}px`,
              height: `${bubble.size}px`,
              opacity: poppingBubbles.has(bubble.id) ? 0 : bubble.opacity,
              background: `radial-gradient(circle at 35% 35%, ${bubble.color}dd, ${bubble.color}66)`,
              boxShadow: `0 0 ${Math.floor(bubble.size / 4)}px ${bubble.color}88, inset 0 -2px 4px rgba(0,0,0,0.2)`,
              transform: poppingBubbles.has(bubble.id) ? 'scale(1.5)' : 'scale(1)',
              transition: poppingBubbles.has(bubble.id) ? 'opacity 150ms, transform 150ms' : 'none',
            }}
            onMouseDown={e => handlePopBubble(bubble.id, e)}
            onTouchStart={e => handlePopBubble(bubble.id, e)}
          />
        ))}

        {/* Floor glow */}
        <div className="absolute bottom-0 left-0 right-0 h-8 bg-gradient-to-t from-[#00aaff]/10 to-transparent pointer-events-none" />
      </div>

      <p className="text-[7px] text-slate-600 font-bold text-center">
        Toca las burbujas para reventarlas · Combos = más puntos
      </p>
    </div>
  );

  // ── RENDER: COUNTDOWN ────────────────────────────────────
  const renderCountdown = () => (
    <div className="flex flex-col items-center justify-center py-12 gap-3">
      <div className="text-6xl font-black text-[#00ff88] animate-bounce"
           style={{ textShadow: '0 0 30px rgba(0,255,136,0.5)' }}>
        {countdown}
      </div>
      <p className="text-[10px] text-slate-400 font-black uppercase tracking-widest animate-pulse">
        Prepara tus dedos…
      </p>
    </div>
  );

  // ── RENDER: GAMEOVER ─────────────────────────────────────
  const renderGameOver = () => (
    <div className="flex flex-col items-center gap-4">
      <div className="text-4xl">{isNewRecord ? '🏆' : '🎮'}</div>

      <div className="text-center">
        <h3 className="text-base font-black text-white uppercase tracking-tight">
          {isNewRecord ? '¡NUEVO RECORD!' : 'Juego Terminado'}
        </h3>
        <p className="text-[9px] text-slate-500 font-bold mt-0.5">
          {isNewRecord ? 'Eres el amo del arcade' : '¿Podrás superarlo?'}
        </p>
      </div>

      {/* Score */}
      <div className="text-center">
        <div className="text-[9px] font-black text-slate-500 uppercase tracking-wider mb-0.5">Puntaje Final</div>
        <div className="text-4xl font-black text-white tabular-nums"
             style={{ textShadow: isNewRecord ? '0 0 20px rgba(255,215,0,0.5)' : 'none' }}>
          {animatedDisplayScore}
        </div>
        {submitting && (
          <div className="text-[8px] text-slate-500 font-bold mt-1 animate-pulse">Guardando puntaje…</div>
        )}
      </div>

      {/* Personal best */}
      {personalBest != null && !submitting && (
        <div className="flex items-center gap-1.5 text-[9px] font-bold text-slate-400 bg-slate-800/50 px-3 py-1 rounded-full border border-white/5">
          <Medal size={10} /> Mejor: {personalBest}
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-2 w-full pt-1">
        <button
          onClick={handleStartGame}
          className="flex-1 py-2.5 bg-gradient-to-r from-[#00ff88] to-emerald-600 hover:from-[#33ff99] hover:to-emerald-500 text-slate-900 font-black rounded-xl uppercase tracking-widest text-[10px] shadow-lg active:scale-95 transition-all"
          disabled={submitting}
        >
          ▶ Jugar Otra Vez
        </button>
        <button
          onClick={() => setPhase('menu')}
          className="flex-1 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 font-black rounded-xl uppercase tracking-widest text-[10px] transition-all active:scale-95 flex items-center justify-center gap-1"
          disabled={submitting}
        >
          🏠 Menú
        </button>
      </div>

      {/* Share/retry hint */}
      <p className="text-[7px] text-slate-600 font-bold">
        Invita a tus amigos a batir tu récord
      </p>
    </div>
  );

  // ── RENDER: LEADERBOARD ──────────────────────────────────
  const renderLeaderboard = () => (
    <div className="flex flex-col gap-2.5">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-black text-white uppercase tracking-tighter flex items-center gap-1.5">
          <Trophy size={14} className="text-amber-400" /> Records
        </h3>
        <button
          onClick={() => setPhase('menu')}
          className="text-[9px] font-bold text-slate-400 hover:text-white flex items-center gap-1 transition-colors"
        >
          <ArrowLeft size={12} /> Volver
        </button>
      </div>

      <div className="rounded-2xl border border-slate-700 bg-slate-950/50 overflow-hidden">
        {loadingLB ? (
          <div className="p-8 text-center">
            <p className="text-[10px] text-slate-400 font-black uppercase tracking-widest animate-pulse">
              Cargando records…
            </p>
          </div>
        ) : leaderboard.length === 0 ? (
          <div className="p-8 text-center">
            <p className="text-2xl mb-2">🎮</p>
            <p className="text-[10px] text-slate-500 font-bold">
              No hay records aún. ¡Sé el primero!
            </p>
          </div>
        ) : (
          <div className="max-h-56 overflow-y-auto scrollbar-hide">
            {/* Header */}
            <div className="flex items-center px-4 py-2 text-[7px] font-black text-slate-600 uppercase tracking-wider border-b border-slate-800">
              <span className="w-8 shrink-0">#</span>
              <span className="flex-1">Jugador</span>
              <span className="w-20 text-right">Puntaje</span>
            </div>
            {/* Rows */}
            {leaderboard.slice(0, 20).map((entry, i) => {
              const isMe = entry.user_id === userId;
              return (
                <div
                  key={entry.id}
                  className={`flex items-center px-4 py-2.5 border-b border-slate-800/50 last:border-b-0 transition-colors ${
                    isMe ? 'bg-[#00ff88]/5' : 'hover:bg-slate-800/30'
                  }`}
                >
                  <span className="w-8 shrink-0 font-black text-xs">
                    {i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : (
                      <span className={isMe ? 'text-[#00ff88]' : 'text-slate-500'}>{i + 1}</span>
                    )}
                  </span>
                  <span className={`flex-1 text-[10px] font-bold truncate ${
                    isMe ? 'text-[#00ff88]' : 'text-slate-300'
                  }`}>
                    {entry.cave_name || `Jugador #${entry.user_id.slice(0, 6)}`}
                    {isMe && (
                      <span className="text-[7px] text-[#00ff88]/60 ml-1">(tú)</span>
                    )}
                  </span>
                  <span className={`w-20 text-right font-black text-xs tabular-nums ${
                    i === 0 ? 'text-amber-400' : isMe ? 'text-[#00ff88]' : 'text-white'
                  }`}>
                    {entry.score.toLocaleString()}
                  </span>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );

  // ── MAIN RENDER ──────────────────────────────────────────
  return (
    <div
      className="fixed inset-0 z-[70] flex items-center justify-center bg-black/70 backdrop-blur-sm p-4"
      onClick={onClose}
    >
      <div
        className="bg-slate-900 border-2 border-slate-800 rounded-[2.5rem] p-6 sm:p-8 max-w-md w-full shadow-2xl relative overflow-hidden"
        onClick={e => e.stopPropagation()}
      >
        {/* CRT scanline overlay */}
        <div
          className="absolute inset-0 pointer-events-none z-0 opacity-[0.04]"
          style={{
            background: `repeating-linear-gradient(
              0deg,
              transparent,
              transparent 2px,
              rgba(0,0,0,1) 2px,
              rgba(0,0,0,1) 4px
            )`,
          }}
        />
        {/* Green phosphor tint */}
        <div className="absolute inset-0 pointer-events-none z-0 bg-[rgba(0,255,136,0.02)]" />

        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 w-8 h-8 rounded-full bg-slate-800 hover:bg-slate-700 flex items-center justify-center text-slate-400 hover:text-white transition-all z-10"
          aria-label="Cerrar Algas Arcade"
        >
          <X size={14} />
        </button>

        {/* Cabinet frame decoration */}
        <div className="relative z-0">
          {/* Top marquee glow */}
          <div className="absolute -top-6 left-1/2 -translate-x-1/2 w-3/4 h-1 bg-gradient-to-r from-transparent via-[#00ff88]/30 to-transparent rounded-full blur-sm" />

          {countdown !== null && renderCountdown()}
          {countdown === null && phase === 'menu' && renderMenu()}
          {phase === 'playing' && renderPlaying()}
          {phase === 'gameover' && renderGameOver()}
          {phase === 'leaderboard' && renderLeaderboard()}
        </div>

        {/* Cabinet footer art */}
        <div className="relative z-0 mt-4 flex justify-center gap-6 text-[7px] font-black text-slate-700 uppercase tracking-widest">
          <span>◀ ►</span>
          <span>🦎 Axolotto 2026</span>
          <span>▶ ◀</span>
        </div>
      </div>
    </div>
  );
}
