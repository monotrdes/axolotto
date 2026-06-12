"use client";
import React from 'react';
import { SpotSlot } from '@/types/santuario';
import SpotFluido from './SpotFluido';
import { API_BASE } from '@/lib/api';
import { useSwimAnimation } from '@/hooks/useSwimAnimation';

const API = `${API_BASE}`;

interface NidoSceneProps {
  spots: SpotSlot[];
  axolotitos: any[];
  clima: any;
  caveLevel: number;
  viewMode: 'libre' | 'gestion';
  hasTable: boolean;
  tableSeats: number;
  onSelectSpot: (slot: SpotSlot) => void;
  onSelectAxo: (axo: any) => void;
  onToggleViewMode: () => void;
  onOpenHosting?: () => void;
  selectedAxoId: number | null;
  particulas: { id: number; incId: number; tipo: string; x: number; y: number; cLeft?: number; cBottom?: number }[];
  vipTier?: string | null;
  className?: string;
}

export default function NidoScene({
  spots, axolotitos, clima, caveLevel, viewMode, hasTable, tableSeats,
  onSelectSpot, onSelectAxo, onToggleViewMode, onOpenHosting, selectedAxoId, particulas, vipTier, className,
}: NidoSceneProps) {
  const periodTint =
    clima?.period === 'Madrugada' ? 'rgba(6,182,212,0.04)' :
    clima?.period === 'Mañana'    ? 'rgba(52,211,153,0.04)' :
    clima?.period === 'Tarde'     ? 'rgba(251,146,60,0.05)' :
    clima?.period === 'Noche'     ? 'rgba(139,92,246,0.06)' : null;
  const isManagement = viewMode === 'gestion';

  // Swim animation — bubbles, positions, dynamic CSS keyframes
  const { bubbles, axoPositions, positionsRef, cssBlock } = useSwimAnimation(axolotitos, isManagement);

  // Find connections between eggs and their godfather spots
  const connections: { fromIndex: number; toIndex: number; padrinoId: number }[] = [];
  spots.forEach((slot, i) => {
    if (slot.type === 'egg' && slot.data?.imprinting_padrino_id) {
      const padrinoId = slot.data.imprinting_padrino_id;
      const targetIndex = spots.findIndex(s => 
        (s.type === 'axo' || s.type === 'bed') && s.data?.id === padrinoId
      );
      if (targetIndex !== -1) {
        connections.push({
          fromIndex: i,
          toIndex: targetIndex,
          padrinoId
        });
      }
    }
  });

  const isFrost = (clima?.freeze_chance || 0) > 0.5;
  const isHot   = (clima?.heat_multiplier || 1) > 1.5;
  const isGood  = (clima?.stats_multiplier || 1) > 1 && !isFrost;

  return (
    <>
      <style>{cssBlock}</style>

      <div
        className={`relative w-full overflow-hidden rounded-3xl border border-white/5 shadow-2xl ${className ?? 'h-[340px] sm:h-[500px]'}`}
        style={{ background: 'linear-gradient(180deg, #020C16 0%, #050F1C 30%, #071018 55%, #0A0F08 85%, #0D1A0A 100%)' }}
      >
        {/* ═══ LAYER 0: SURFACE — Light rays from top ═══ */}
        {([
          { left: '16%',  rotate: '-5deg',  delay: '0s',   w: 55 },
          { left: '48%',  rotate: '4deg',   delay: '2.5s', w: 44 },
          { left: '78%',  rotate: '-8deg',  delay: '5s',   w: 50 },
        ] as const).map((r, i) => (
          <div
            key={i}
            className="absolute top-0 pointer-events-none"
            style={{
              left: r.left, width: `${r.w}px`, height: '60%',
              background: 'linear-gradient(180deg, rgba(45,212,191,0.15) 0%, transparent 100%)',
              transform: `rotate(${r.rotate})`,
              animation: `ray-flicker ${3 + i}s ${r.delay} infinite ease-in-out`,
              zIndex: 1,
            }}
          />
        ))}

        {/* ── Atmosphere tints ── */}
        {periodTint && (
          <div className="absolute inset-0 pointer-events-none transition-[background] duration-[2000ms]" style={{ background: periodTint, zIndex: 2 }} />
        )}
        {isFrost && (
          <div className="absolute inset-0 pointer-events-none" style={{ background: 'linear-gradient(180deg, rgba(6,182,212,0.07) 0%, rgba(6,182,212,0.03) 100%)', zIndex: 2 }} />
        )}
        {isHot && (
          <div className="absolute inset-0 pointer-events-none" style={{ background: 'linear-gradient(180deg, transparent 0%, rgba(251,146,60,0.06) 100%)', animation: 'shimmer-heat 2.5s infinite ease-in-out', zIndex: 2 }} />
        )}

        {/* ── Bubbles rising from bottom ── */}
        {bubbles.map((b, i) => (
          <div key={i} className="absolute rounded-full pointer-events-none"
            style={{
              left: `${b.left}%`, bottom: 0,
              width: `${b.size}px`, height: `${b.size}px`,
              background: 'rgba(45,212,191,0.45)',
              border: '0.5px solid rgba(45,212,191,0.3)',
              animation: `cenote-bubble ${b.duration}s ${b.delay}s infinite ease-in`,
              zIndex: 3,
            }}
          />
        ))}

        {/* ═══ LAYER 50-65: Axolotitos swimming (libre mode) ═══ */}
        {!isManagement && axolotitos.map(axo => {
          const pos = axoPositions[axo.id];
          if (!pos) return null;
          const size  = Math.round(40 + pos.depth * 24);
          const opac  = 0.55 + pos.depth * 0.45;
          const zIdx  = 50 + Math.round(pos.depth * 15);
          const statusIcon = axo.status === 'sleeping' ? '💤' : axo.status === 'expedition' ? '🧭' : null;
          const isSelected = selectedAxoId === axo.id;
          return (
            <div
              key={axo.id}
              role="button" tabIndex={0}
              onClick={() => onSelectAxo(axo)}
              onKeyDown={(e) => e.key === 'Enter' && onSelectAxo(axo)}
              className="absolute cursor-pointer group select-none"
              style={{
                left: `${pos.left}%`, bottom: `${pos.bottom}%`,
                width: `${size}px`, height: `${size}px`,
                opacity: opac, zIndex: zIdx,
                animation: isSelected ? 'none' : `axo-swim-${axo.id} ${pos.duration}s ${pos.delay}s infinite ease-in-out`,
                filter: axo.stat_luck > 99 ? 'drop-shadow(0 0 8px rgba(6,182,212,0.6))' :
                        axo.stat_luck > 80 ? 'drop-shadow(0 0 6px rgba(245,158,11,0.5))' : undefined,
              }}
              aria-label={axo.name}
            >
              {vipTier && <div className={`absolute inset-0 pointer-events-none vip-frame-${vipTier}`} />}
              {!vipTier && <div className="absolute inset-0 rounded-full border-2 border-[#E4007C]/0 group-hover:border-[#E4007C]/70 transition-colors pointer-events-none" />}
              <img src={`${API}/metadata/axolotito/${axo.blockchain_token_id}.svg`} alt={axo.name} className="w-full h-full object-contain" draggable={false} />
              {statusIcon && <div className="absolute -top-4 left-1/2 -translate-x-1/2 text-xs pointer-events-none select-none">{statusIcon}</div>}
              <div className="absolute -bottom-5 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap bg-black/80 px-1.5 py-0.5 rounded text-[7px] font-black text-white">{axo.name}</div>
            </div>
          );
        })}

        {/* ═══ LAYER 15: Life zone rocks (behind spots) ═══ */}
        <div className="absolute pointer-events-none" style={{ bottom: '13%', left: '-3%', width: '22%', height: '20%', background: 'linear-gradient(135deg, #1F1408 0%, #0C0700 100%)', borderRadius: '70% 30% 0 0 / 80% 40% 0 0', zIndex: 15, opacity: 0.5 }} />
        <div className="absolute pointer-events-none" style={{ bottom: '15%', right: '-2%', width: '20%', height: '18%', background: 'linear-gradient(225deg, #1F1408 0%, #0C0700 100%)', borderRadius: '30% 70% 0 0 / 40% 80% 0 0', zIndex: 15, opacity: 0.5 }} />

        {/* ═══ LAYER 40: LIFE ZONE — Spots fluidos ═══ */}
        {spots.map((slot, i) => {
          const isPadrino = (slot.type === 'axo' || slot.type === 'bed') && spots.some(s => 
            s.type === 'egg' && s.data?.imprinting_padrino_id === slot.data?.id
          );
          return (
            <SpotFluido
              key={`spot-${i}`}
              slot={slot}
              index={i}
              totalSpots={spots.length}
              isManagementMode={isManagement}
              onOpen={() => onSelectSpot(slot)}
              isPadrino={isPadrino}
            />
          );
        })}

        {/* ═══ LAYER 41: Imprinting Connection Links ═══ */}
        {connections.map((conn, idx) => {
          const spacing = 90 / (spots.length + 1);
          const x1 = spacing * (conn.fromIndex + 1) + 0.5;
          const x2 = spacing * (conn.toIndex + 1) + 0.5;
          const bottomVal = isManagement ? 18 : 22;
          const y = 100 - (bottomVal + 8.4);

          // control point for quadratic bezier curve (arches up slightly)
          const cx = (x1 + x2) / 2;
          const cy = y - 8;

          return (
            <svg
              key={`imprinting-link-${idx}`}
              viewBox="0 0 100 100"
              preserveAspectRatio="none"
              className="absolute inset-0 w-full h-full pointer-events-none"
              style={{ zIndex: 38 }}
            >
              <defs>
                <linearGradient id={`energy-grad-${idx}`} x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="#E4007C" stopOpacity="0.85" />
                  <stop offset="50%" stopColor="#A78BFA" stopOpacity="0.85" />
                  <stop offset="100%" stopColor="#2DD4BF" stopOpacity="0.85" />
                </linearGradient>
              </defs>
              {/* Glowing aura background line */}
              <path
                d={`M ${x1} ${y} Q ${cx} ${cy} ${x2} ${y}`}
                fill="none"
                stroke={`url(#energy-grad-${idx})`}
                strokeWidth="1.2"
                className="blur-[2px]"
              />
              {/* Core energy flow line */}
              <path
                d={`M ${x1} ${y} Q ${cx} ${cy} ${x2} ${y}`}
                fill="none"
                stroke="#FFFFFF"
                strokeWidth="0.4"
                className="energy-line"
                opacity="0.95"
              />
            </svg>
          );
        })}

        {/* ═══ LAYER 30: TABLE ZONE (visible from level 3+) ═══ */}
        {hasTable && (
          <div
            className="absolute left-1/2 -translate-x-1/2 pointer-events-auto cursor-pointer group"
            style={{ bottom: '2%', zIndex: 30 }}
            onClick={(e) => { e.stopPropagation(); onOpenHosting?.(); }}
          >
            {/* Table surface */}
            <div
              className="relative"
              style={{
                width: '120px', height: '28px',
                background: 'linear-gradient(180deg, #3D2810 0%, #2A1A08 100%)',
                borderRadius: '6px 6px 2px 2px',
                border: '1px solid rgba(180,130,60,0.3)',
                boxShadow: '0 0 10px rgba(180,130,60,0.15), inset 0 1px 0 rgba(255,255,255,0.05)',
              }}
            >
              {/* Table decorations */}
              <div className="absolute inset-0 flex items-center justify-center gap-2 opacity-60">
                <span className="text-[10px]">🎴</span>
                <span className="text-[6px] font-black text-amber-400/60 uppercase tracking-wider">Mesa</span>
                <span className="text-[10px]">🎴</span>
              </div>
            </div>
            {/* Table legs */}
            <div className="flex justify-between px-2" style={{ marginTop: '-1px' }}>
              <div style={{ width: '3px', height: '8px', background: '#2A1A08', borderRadius: '0 0 1px 1px' }} />
              <div style={{ width: '3px', height: '8px', background: '#2A1A08', borderRadius: '0 0 1px 1px' }} />
            </div>
            {/* Glow when group hover */}
            <div className="absolute inset-0 rounded-md opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none"
              style={{ boxShadow: '0 0 20px rgba(251,146,60,0.3)', zIndex: -1 }}
            />
          </div>
        )}

        {/* ═══ LAYER 20: ENTRANCE ZONE — Exhibition (bottom) ═══ */}
        <div
          className="absolute left-1/2 -translate-x-1/2 pointer-events-none"
          style={{ bottom: '-2%', zIndex: 10, width: '60%', height: '12%' }}
        >
          {/* Cave entrance arch */}
          <div
            style={{
              width: '100%', height: '100%',
              background: 'linear-gradient(180deg, transparent 0%, #0A0804 40%, #0D0A06 100%)',
              borderRadius: '50% 50% 0 0 / 90% 90% 0 0',
              border: '1px solid rgba(80,50,20,0.2)',
              boxShadow: 'inset 0 4px 12px rgba(0,0,0,0.7)',
            }}
          />
          {/* "Entrada" label */}
          <div className="absolute bottom-1 left-1/2 -translate-x-1/2 text-[7px] font-black text-slate-700 uppercase tracking-widest">
            Entrada
          </div>
        </div>

        {/* ═══ LAYER 60: Interaction particles ═══ */}
        {particulas.map(p => (
          <div key={p.id}
            className="absolute pointer-events-none text-xs font-black text-white bg-black/80 border border-white/15 px-2.5 py-1 rounded-lg whitespace-nowrap animate-float-up shadow-md"
            style={{ bottom: `${p.cBottom ?? 30}%`, left: `${p.cLeft ?? 50}%`, '--x': `${p.x}px`, zIndex: 70 } as React.CSSProperties}
          >
            {p.tipo}
          </div>
        ))}

        {/* ── Good weather sparkles ── */}
        {isGood && ([22, 47, 68, 34, 58] as const).map((l, i) => (
          <div key={i} className="absolute pointer-events-none text-xs"
            style={{ left: `${l}%`, bottom: '30%', animation: `golden-float ${3 + i * 0.9}s ${i * 1.4}s infinite ease-out`, opacity: 0, zIndex: 65 }}
          >✨</div>
        ))}

        {/* ═══ LAYER 72: View mode toggle ═══ */}
        <div className="absolute top-2 right-2" style={{ zIndex: 72 }}>
          <button
            onClick={(e) => { e.stopPropagation(); onToggleViewMode(); }}
            className="px-2.5 py-1 rounded-full text-[8px] font-black uppercase tracking-wider transition-all
              bg-black/60 backdrop-blur-sm border border-white/10 hover:border-white/25
              text-slate-400 hover:text-white"
          >
            {isManagement ? '🌊 Libre' : '🔧 Gestionar'}
          </button>
        </div>

        {/* ═══ LAYER 72: Census chip ═══ */}
        <div className="absolute bottom-2 right-2 pointer-events-none" style={{ zIndex: 72 }}>
          <div className="flex items-center gap-1.5 bg-black/50 backdrop-blur-sm border border-white/8 rounded-xl px-2.5 py-1.5">
            <span className="text-[8px] font-black text-slate-300">
              🥚 {spots.filter(s => s.type === 'egg' && !(s.data as any).is_frozen).length}
            </span>
            {spots.some(s => s.type === 'egg' && (s.data as any).is_frozen) && (
              <span className="text-[8px] font-black text-cyan-400">
                ❄️ {spots.filter(s => s.type === 'egg' && (s.data as any).is_frozen).length}
              </span>
            )}
            <span className="text-[8px] font-black text-[#2DD4BF]">
              🦎 {axolotitos.length}
            </span>
            <span className="text-[7px] font-black text-slate-500">
              Nv.{caveLevel}
            </span>
          </div>
        </div>
      </div>
    </>
  );
}
