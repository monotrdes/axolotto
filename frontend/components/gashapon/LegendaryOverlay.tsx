"use client";

import React from 'react';

// ── Props ───────────────────────────────────────────────────────────────────────

interface LegendaryOverlayProps {
  legendaryType?: string;  // 'webito_astral' = astral, anything else = foil legendary
}

// ── Component ───────────────────────────────────────────────────────────────────

export default function LegendaryOverlay({ legendaryType }: LegendaryOverlayProps) {
  const isAstral = legendaryType === 'webito_astral';
  const SYMBOLS_ASTRAL = ['🌟','⭐','💫','🌀','🔮','🌌','💜','🦎','✨','🎆'];
  const SYMBOLS_FOIL   = ['✨','💎','👑','🏆','🔥','💛','🌈','⚡','💠','🌟'];
  const syms = isAstral ? SYMBOLS_ASTRAL : SYMBOLS_FOIL;
  const colors_astral = ['#c084fc','#818cf8','#e879f9','#a78bfa','#60a5fa','#f0abfc'];
  const colors_foil   = ['#fbbf24','#f472b6','#fb923c','#34d399','#60a5fa','#c084fc'];
  const colors = isAstral ? colors_astral : colors_foil;

  const pts = Array.from({ length: 60 }, (_, i) => ({
    id: i,
    sym: syms[i % syms.length],
    color: colors[i % colors.length],
    left: Math.random() * 100,
    size: Math.random() * 16 + 10,
    delay: Math.random() * 3,
    dur: Math.random() * 3 + 2.5,
    drift: (Math.random() - 0.5) * 200,
    rot: Math.random() * 720 - 360,
  }));

  return (
    <div className="fixed inset-0 pointer-events-none z-[200] overflow-hidden">
      <style dangerouslySetInnerHTML={{ __html: `
        @keyframes leg-particle {
          0%   { transform: translateY(60px) translateX(0) rotate(0deg); opacity: 0; }
          10%  { opacity: 1; }
          90%  { opacity: 0.9; }
          100% { transform: translateY(-500px) translateX(var(--lp-drift)) rotate(var(--lp-rot)); opacity: 0; }
        }
        @keyframes leg-ring {
          0%   { transform: scale(0); opacity: 1; border-width: 12px; }
          50%  { transform: scale(1.8); opacity: 0.8; }
          100% { transform: scale(4); opacity: 0; border-width: 2px; }
        }
        @keyframes leg-flash {
          0%, 100% { opacity: 0; }
          15%  { opacity: 0.35; }
          30%  { opacity: 0; }
        }
        .leg-particle-anim { animation: leg-particle var(--lp-dur) var(--lp-delay) infinite linear; }
        .leg-ring-anim { animation: leg-ring 1s ease-out forwards; }
        .leg-flash-anim { animation: leg-flash 0.6s ease-out forwards; }
      `}} />

      {/* White flash on appear */}
      <div className="leg-flash-anim absolute inset-0 bg-white rounded-none" />

      {/* Central golden ring burst */}
      <div
        className="leg-ring-anim absolute rounded-full pointer-events-none"
        style={{
          width: '200px', height: '200px',
          left: '50%', top: '50%',
          marginLeft: '-100px', marginTop: '-100px',
          border: `12px solid ${isAstral ? '#c084fc' : '#fbbf24'}`,
        }}
      />

      {/* Confetti particles */}
      {pts.map(p => (
        <div
          key={p.id}
          className="absolute bottom-0 text-center select-none leg-particle-anim"
          style={{
            left: `${p.left}%`,
            fontSize: `${p.size}px`,
            color: p.color,
            '--lp-delay': `${p.delay}s`,
            '--lp-dur': `${p.dur}s`,
            '--lp-drift': `${p.drift}px`,
            '--lp-rot': `${p.rot}deg`,
            opacity: 0,
          } as React.CSSProperties}
        >
          {p.sym}
        </div>
      ))}

      {/* Big center text */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
        <div
          className="text-center animate-in zoom-in duration-500"
          style={{ animationDelay: '0.2s' }}
        >
          <p className={`text-4xl sm:text-6xl font-black tracking-widest uppercase drop-shadow-[0_0_30px_rgba(245,158,11,1)] animate-pulse ${
            isAstral
              ? 'text-transparent bg-clip-text bg-gradient-to-b from-purple-300 to-indigo-500'
              : 'text-transparent bg-clip-text bg-gradient-to-b from-amber-300 to-yellow-600'
          }`}>
            {isAstral ? '🌌 MÍTICO 🌌' : '✨ LEGENDARIO ✨'}
          </p>
        </div>
      </div>
    </div>
  );
}
