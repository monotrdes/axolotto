"use client";
import React, { useState, useEffect, useRef, useCallback } from 'react';
import { X, Coins, Sparkles, Heart } from 'lucide-react';
import { playWishingWell } from '@/services/santuarioService';

// ── Types ──────────────────────────────────────────────────
interface WishingWellProps {
  isOpen: boolean;
  onClose: () => void;
  token: string | null;
  userId: string;
}

type GamePhase = 'idle' | 'falling' | 'qte' | 'result';

interface WellResult {
  outcome: 'perfect' | 'good' | 'okay' | 'miss';
  frj_spent: number;
  frj_won: number;
  item_won: string | null;
  net_frj: number;
}

// ── QTE Constants ──────────────────────────────────────────
const QTE_DURATION_MS = 2000;
const PERFECT_ZONE = 0.20;   // Top 20% = perfect
const GOOD_ZONE    = 0.50;   // 20-50% = good
const OKAY_ZONE    = 0.80;   // 50-80% = okay
const COST_FRJ     = 20;

// ── OUTCOME DATA ───────────────────────────────────────────
const OUTCOME_META: Record<string, {
  title: string;
  subtitle: string;
  emoji: string;
  glowClass: string;
  particleClass: string;
  frjMin: number;
  frjMax: number;
}> = {
  perfect: {
    title: '¡Ofrenda Perfecta!',
    subtitle: 'Los espíritus del cenote te sonríen',
    emoji: '🌟',
    glowClass: 'shadow-[0_0_30px_rgba(255,215,0,0.6)] border-amber-400',
    particleClass: 'bg-amber-300',
    frjMin: 30,
    frjMax: 50,
  },
  good: {
    title: '¡Buena Onda!',
    subtitle: 'El cenote acepta tu ofrenda',
    emoji: '✨',
    glowClass: 'shadow-[0_0_20px_rgba(0,170,255,0.5)] border-cyan-400',
    particleClass: 'bg-cyan-300',
    frjMin: 15,
    frjMax: 25,
  },
  okay: {
    title: 'Algo es algo…',
    subtitle: 'El eco apenas responde',
    emoji: '💧',
    glowClass: 'shadow-[0_0_12px_rgba(100,200,255,0.3)] border-blue-400/50',
    particleClass: 'bg-blue-300',
    frjMin: 5,
    frjMax: 10,
  },
  miss: {
    title: 'El cenote guarda silencio…',
    subtitle: 'Tal vez la próxima vez',
    emoji: '🌑',
    glowClass: 'shadow-none border-slate-600',
    particleClass: 'bg-slate-500',
    frjMin: 0,
    frjMax: 0,
  },
};

// ── COMPONENT ──────────────────────────────────────────────
export default function WishingWell({ isOpen, onClose, token, userId }: WishingWellProps) {
  // ── State machine ────────────────────────────────────────
  const [phase, setPhase] = useState<GamePhase>('idle');
  const [qteProgress, setQteProgress] = useState(0);      // 0→1 over QTE duration
  const [qteActive, setQteActive] = useState(false);       // true while ring is shrinking
  const [result, setResult] = useState<WellResult | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [particles, setParticles] = useState<{ id: number; x: number; delay: number }[]>([]);

  // ── Refs ─────────────────────────────────────────────────
  const qteStartRef = useRef<number>(0);
  const qteRafRef   = useRef<number>(0);
  const fallTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const accuracyRef  = useRef<number>(0);
  const resultRef    = useRef<WellResult | null>(null);
  const particleIdRef = useRef(0);

  // ── Generate ambient particles ───────────────────────────
  useEffect(() => {
    if (phase !== 'idle' && phase !== 'result') return;
    const interval = setInterval(() => {
      setParticles(prev => [
        ...prev.slice(-8),
        { id: particleIdRef.current++, x: Math.random() * 80 + 10, delay: Math.random() * 2 },
      ]);
    }, 600);
    return () => clearInterval(interval);
  }, [phase]);

  // ── Cleanup QTE on unmount ───────────────────────────────
  useEffect(() => {
    return () => {
      if (qteRafRef.current) cancelAnimationFrame(qteRafRef.current);
      if (fallTimerRef.current) clearTimeout(fallTimerRef.current);
    };
  }, []);

  // ── Determine outcome from accuracy ──────────────────────
  const getOutcome = useCallback((accuracy: number): WellResult['outcome'] => {
    if (accuracy >= 1 - PERFECT_ZONE) return 'perfect';
    if (accuracy >= 1 - GOOD_ZONE)    return 'good';
    if (accuracy >= 1 - OKAY_ZONE)    return 'okay';
    return 'miss';
  }, []);

  // ── Start falling phase ──────────────────────────────────
  const handleThrow = () => {
    setPhase('falling');
    setQteProgress(0);
    setResult(null);
    resultRef.current = null;
    fallTimerRef.current = setTimeout(() => {
      // After falling animation completes, start QTE
      setPhase('qte');
      startQTE();
    }, 1500);
  };

  // ── QTE loop: shrinking ring ────────────────────────────
  const startQTE = () => {
    setQteActive(true);
    qteStartRef.current = performance.now();

    const loop = (now: number) => {
      const elapsed = now - qteStartRef.current;
      const progress = Math.min(elapsed / QTE_DURATION_MS, 1);
      setQteProgress(progress);

      if (progress >= 1) {
        // Timeout = miss
        setQteActive(false);
        accuracyRef.current = 1;
        resolveQTE(1);
        return;
      }

      qteRafRef.current = requestAnimationFrame(loop);
    };

    qteRafRef.current = requestAnimationFrame(loop);
  };

  // ── Player taps during QTE ───────────────────────────────
  const handleQTETap = () => {
    if (!qteActive) return;
    setQteActive(false);
    if (qteRafRef.current) cancelAnimationFrame(qteRafRef.current);
    const elapsed = performance.now() - qteStartRef.current;
    const accuracy = Math.min(elapsed / QTE_DURATION_MS, 1);
    accuracyRef.current = accuracy;
    resolveQTE(accuracy);
  };

  // ── Resolve QTE outcome ──────────────────────────────────
  const resolveQTE = async (accuracy: number) => {
    const outcome = getOutcome(accuracy);
    const meta = OUTCOME_META[outcome];

    // Determine won FRJ (with some random variance)
    const wonFrj = outcome === 'miss'
      ? 0
      : Math.floor(meta.frjMin + Math.random() * (meta.frjMax - meta.frjMin + 1));

    // Build local result
    const localResult: WellResult = {
      outcome,
      frj_spent: COST_FRJ,
      frj_won: wonFrj,
      item_won: null,
      net_frj: wonFrj - COST_FRJ,
    };
    resultRef.current = localResult;

    // Call backend
    setSubmitting(true);
    try {
      const serverResult = await playWishingWell(accuracy, outcome, token);
      if (serverResult) {
        setResult({
          outcome: serverResult.outcome || outcome,
          frj_spent: serverResult.frj_spent ?? COST_FRJ,
          frj_won: serverResult.frj_won ?? wonFrj,
          item_won: serverResult.item_won ?? null,
          net_frj: serverResult.net_frj ?? (wonFrj - COST_FRJ),
        });
      } else {
        setResult(localResult);
      }
    } catch {
      // Fallback to local result
      setResult(localResult);
    } finally {
      setSubmitting(false);
      // Brief delay before showing result
      setTimeout(() => {
        setPhase('result');
      }, 300);
    }
  };

  // ── Play again ───────────────────────────────────────────
  const handlePlayAgain = () => {
    setPhase('idle');
    setResult(null);
    setQteProgress(0);
    setParticles([]);
  };

  // ── Close handler ────────────────────────────────────────
  const handleClose = () => {
    if (qteRafRef.current) cancelAnimationFrame(qteRafRef.current);
    if (fallTimerRef.current) clearTimeout(fallTimerRef.current);
    onClose();
  };

  // ── Render: QTE ring transform ──────────────────────────
  const ringScale = 1 - qteProgress;
  const isPerfect   = ringScale <= PERFECT_ZONE / 1;
  const isGood      = !isPerfect && ringScale <= GOOD_ZONE / 1;
  const isOkay      = !isPerfect && !isGood && ringScale <= OKAY_ZONE / 1;

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-[70] flex items-center justify-center bg-black/70 backdrop-blur-sm p-4"
      onClick={handleClose}
    >
      <div
        className="bg-slate-900 border-2 border-slate-800 rounded-[2.5rem] p-6 sm:p-8 max-w-md w-full shadow-2xl relative overflow-hidden"
        onClick={e => e.stopPropagation()}
      >
        {/* ── Close button ── */}
        <button
          onClick={handleClose}
          className="absolute top-4 right-4 w-8 h-8 rounded-full bg-slate-800 hover:bg-slate-700 flex items-center justify-center text-slate-400 hover:text-white transition-all z-10"
          aria-label="Cerrar Pozo de los Deseos"
        >
          <X size={14} />
        </button>

        {/* ── TITLE ── */}
        <div className="text-center mb-4">
          <div className="text-3xl mb-1">🪙</div>
          <h3 className="text-lg font-black text-white uppercase tracking-tighter">
            Pozo de los <span className="text-[#00aaff]">Deseos</span>
          </h3>
          <p className="text-[9px] text-slate-500 font-bold uppercase tracking-widest mt-0.5">
            Ofrenda al cenote · 20 FRJ
          </p>
        </div>

        {/* ── WELL AREA ── */}
        <div className="relative w-48 h-48 mx-auto mb-5">
          {/* Well pool */}
          <div className="absolute inset-0 rounded-full bg-gradient-to-b from-slate-900 via-blue-950/80 to-slate-900 border-2 border-blue-500/30 shadow-[0_0_30px_rgba(0,170,255,0.2)] overflow-hidden">
            {/* Bioluminescent glow */}
            <div className="absolute inset-2 rounded-full bg-gradient-radial from-[#00aaff]/20 via-transparent to-transparent animate-pulse" />

            {/* Concentric ripple rings */}
            {[1, 2, 3].map(i => (
              <div
                key={i}
                className="absolute inset-0 rounded-full border border-[#00aaff]/20"
                style={{
                  animation: `ripple-expand 3s ease-out ${i * 0.8}s infinite`,
                  '--ripple-from': 'rgba(0,170,255,0.15)',
                } as React.CSSProperties}
              />
            ))}

            {/* Ambient rising particles */}
            {phase === 'idle' && particles.map(p => (
              <div
                key={p.id}
                className="absolute w-1.5 h-1.5 rounded-full bg-[#00aaff]/40"
                style={{
                  left: `${p.x}%`,
                  bottom: '10%',
                  animation: `particle-float ${3 + p.delay}s ease-out infinite`,
                  animationDelay: `${p.delay}s`,
                }}
              />
            ))}

            {/* FALLING state: Bean falls into well */}
            {phase === 'falling' && (
              <>
                <div
                  className="absolute left-1/2 -translate-x-1/2 text-2xl z-10"
                  style={{
                    animation: 'bean-fall 1.5s cubic-bezier(0.22, 1, 0.36, 1) forwards',
                  }}
                >
                  🫘
                </div>
                {/* Water splash ripples */}
                <div
                  className="absolute left-1/2 -translate-x-1/2 bottom-[35%] w-8 h-2 rounded-full bg-[#00aaff]/30"
                  style={{
                    animation: 'splash-ripple 0.6s ease-out 1.3s forwards',
                    opacity: 0,
                  }}
                />
              </>
            )}

            {/* QTE state: glowing ring indicator */}
            {phase === 'qte' && (
              <div className="absolute inset-0 flex items-center justify-center">
                {/* Shrinking ring */}
                <div
                  className={`absolute rounded-full border-4 transition-colors duration-100 ${
                    isPerfect
                      ? 'border-amber-400 shadow-[0_0_20px_rgba(255,215,0,0.6)]'
                      : isGood
                      ? 'border-[#00ff88] shadow-[0_0_15px_rgba(0,255,136,0.4)]'
                      : isOkay
                      ? 'border-blue-400 shadow-[0_0_10px_rgba(100,200,255,0.3)]'
                      : 'border-red-500/50 shadow-[0_0_8px_rgba(255,0,0,0.2)]'
                  }`}
                  style={{
                    width: `${ringScale * 100}%`,
                    height: `${ringScale * 100}%`,
                    maxWidth: '90%',
                    maxHeight: '90%',
                    transition: 'none',
                  }}
                />
                {/* Target center point */}
                <div className="w-1.5 h-1.5 rounded-full bg-amber-400 shadow-[0_0_10px_rgba(255,215,0,0.8)]" />
                {/* "¡TOCA!" indicator */}
                <div className="absolute -bottom-8 left-1/2 -translate-x-1/2 animate-bounce">
                  <span className="text-[10px] font-black text-amber-400 uppercase tracking-widest bg-slate-900/80 px-3 py-1 rounded-full border border-amber-500/30">
                    ¡TOCA!
                  </span>
                </div>
                {/* Zone labels */}
                <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-6 flex gap-2 text-[7px] font-black uppercase tracking-wider">
                  <span className={isPerfect ? 'text-amber-400' : 'text-slate-600'}>Perfecto</span>
                  <span className={isGood ? 'text-[#00ff88]' : 'text-slate-600'}>Bueno</span>
                  <span className={isOkay ? 'text-blue-400' : 'text-slate-600'}>Regular</span>
                </div>
              </div>
            )}

            {/* RESULT state: visual feedback */}
            {phase === 'result' && result && (
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                {/* Gold particle burst for perfect */}
                {result.outcome === 'perfect' && (
                  <div className="absolute inset-0 flex items-center justify-center">
                    {Array.from({ length: 8 }).map((_, i) => (
                      <div
                        key={i}
                        className="absolute w-2 h-2 rounded-full bg-amber-400"
                        style={{
                          animation: `burst-particle 0.8s ease-out ${i * 0.05}s forwards`,
                          '--burst-x': `${Math.cos((i / 8) * Math.PI * 2) * 60}px`,
                          '--burst-y': `${Math.sin((i / 8) * Math.PI * 2) * 60}px`,
                        } as React.CSSProperties}
                      />
                    ))}
                  </div>
                )}
                {/* Blue glow for good */}
                {result.outcome === 'good' && (
                  <div className="absolute inset-0 rounded-full shadow-[0_0_40px_rgba(0,170,255,0.4)] animate-pulse" />
                )}
                {/* Dim glow for okay */}
                {result.outcome === 'okay' && (
                  <div className="absolute inset-0 rounded-full shadow-[0_0_15px_rgba(100,200,255,0.15)]" />
                )}
                {/* Dark splash for miss */}
                {result.outcome === 'miss' && (
                  <div className="absolute inset-0 rounded-full bg-black/30" />
                )}
              </div>
            )}
          </div>
        </div>

        {/* ── IDLE state: info + button ── */}
        {phase === 'idle' && (
          <div className="text-center space-y-4">
            <div className="flex items-center justify-center gap-3 text-[10px] font-bold text-slate-400">
              <span className="flex items-center gap-1"><Coins size={12} /> Costo: 20 FRJ</span>
              <span className="text-slate-600">|</span>
              <span className="flex items-center gap-1"><Sparkles size={12} /> Premios: FRJ + objetos</span>
            </div>
            <button
              onClick={handleThrow}
              className="w-full py-3.5 bg-gradient-to-r from-[#00aaff] to-blue-600 hover:from-[#22bbff] hover:to-blue-500 text-white font-black rounded-2xl uppercase tracking-widest text-xs shadow-lg shadow-[#00aaff]/20 active:scale-95 transition-all"
            >
              🎯 Lanzar Frijolito (20 FRJ)
            </button>
            <p className="text-[8px] text-slate-600 font-bold">
              Sincroniza tu toque con el anillo para una ofrenda perfecta
            </p>
          </div>
        )}

        {/* ── FALLING state ── */}
        {phase === 'falling' && (
          <div className="text-center">
            <p className="text-[10px] text-[#00aaff] font-black uppercase tracking-widest animate-pulse">
              El frijolito se hunde en el cenote…
            </p>
          </div>
        )}

        {/* ── QTE state ── */}
        {phase === 'qte' && (
          <div className="text-center">
            <button
              onClick={handleQTETap}
              className="w-full py-4 bg-gradient-to-r from-amber-600 to-yellow-500 hover:from-amber-500 hover:to-yellow-400 text-white font-black rounded-2xl uppercase tracking-widest text-sm shadow-lg active:scale-95 transition-all"
            >
              👆 ¡TOCA!
            </button>
            <p className="text-[8px] text-slate-500 font-bold mt-1.5">
              Toca cuando el anillo esté en el centro
            </p>
          </div>
        )}

        {/* ── SUBMITTING ── */}
        {submitting && (
          <div className="text-center">
            <p className="text-[10px] text-slate-400 font-black uppercase tracking-widest animate-pulse">
              El cenote responde…
            </p>
          </div>
        )}

        {/* ── RESULT state ── */}
        {phase === 'result' && result && (
          <div className={`text-center space-y-3 p-4 rounded-2xl border ${OUTCOME_META[result.outcome].glowClass} bg-slate-800/50`}>
            <div className="text-3xl">{OUTCOME_META[result.outcome].emoji}</div>
            <div>
              <h4 className="text-sm font-black text-white uppercase tracking-tight">
                {OUTCOME_META[result.outcome].title}
              </h4>
              <p className="text-[9px] text-slate-400 font-bold mt-0.5">
                {OUTCOME_META[result.outcome].subtitle}
              </p>
            </div>

            {/* Net FRJ change */}
            <div className="flex items-center justify-center gap-3 text-xs font-black">
              <span className="text-slate-500">-{result.frj_spent} FRJ</span>
              <span className="text-slate-600">→</span>
              <span className={`${result.net_frj >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                {result.net_frj >= 0 ? '+' : ''}{result.net_frj} FRJ
              </span>
            </div>

            {/* Item won */}
            {result.item_won && (
              <div className="inline-flex items-center gap-1.5 bg-amber-950/40 border border-amber-500/30 rounded-full px-3 py-1 text-[9px] font-black text-amber-300">
                <Heart size={10} /> ¡{result.item_won}!
              </div>
            )}

            {/* Win amount detail */}
            {result.frj_won > 0 && (
              <p className="text-[9px] text-slate-500 font-bold">
                Ganaste {result.frj_won} FRJ
              </p>
            )}

            <div className="flex gap-2 pt-1">
              <button
                onClick={handlePlayAgain}
                className="flex-1 py-2.5 bg-gradient-to-r from-[#00aaff] to-blue-600 hover:from-[#22bbff] hover:to-blue-500 text-white font-black rounded-xl uppercase tracking-widest text-[10px] shadow-lg active:scale-95 transition-all"
              >
                🎯 Otra Vez
              </button>
              <button
                onClick={handleClose}
                className="flex-1 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 font-black rounded-xl uppercase tracking-widest text-[10px] transition-all active:scale-95"
              >
                Cerrar
              </button>
            </div>
          </div>
        )}

        {/* ── INLINE STYLES FOR CUSTOM ANIMATIONS ────────── */}
        <style jsx>{`
          @keyframes bean-fall {
            0%   { transform: translate(-50%, -80px) rotate(-15deg); opacity: 0; }
            20%  { transform: translate(-50%, -20px) rotate(5deg);   opacity: 1; }
            60%  { transform: translate(-50%, 5px)   rotate(-3deg);  opacity: 1; }
            80%  { transform: translate(-50%, -3px)  rotate(2deg);   opacity: 1; }
            100% { transform: translate(-50%, 8px)   rotate(0deg);   opacity: 1; }
          }
          @keyframes splash-ripple {
            0%   { transform: translate(-50%, 0) scale(0.3); opacity: 0.7; }
            100% { transform: translate(-50%, 0) scale(2);   opacity: 0; }
          }
          @keyframes burst-particle {
            0%   { transform: translate(0, 0) scale(0);   opacity: 1; }
            100% { transform: translate(var(--burst-x, 40px), var(--burst-y, -40px)) scale(1); opacity: 0; }
          }
          @keyframes particle-float {
            0%   { transform: translateY(0) translateX(0);   opacity: 0; }
            20%  { opacity: 0.6; }
            80%  { opacity: 0.3; }
            100% { transform: translateY(-80px) translateX(10px); opacity: 0; }
          }
          @keyframes ripple-expand {
            0%   { transform: scale(0.9); opacity: 0.4; }
            100% { transform: scale(1.15); opacity: 0; }
          }
        `}</style>
      </div>
    </div>
  );
}
