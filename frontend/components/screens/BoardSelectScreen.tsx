"use client";

import React from 'react';
import { Play, Coins } from 'lucide-react';
import { createPortal } from 'react-dom';
import BoardCardGrid from '../ui/BoardCardGrid';
import { useProductPolicy } from '@/hooks/useProductPolicy';

interface BoardSelectScreenProps {
  mode: 'cpu' | 'multi';
  playerBoards: any[];
  allCards: any[];
  axolotitos: any[];
  selectedAxo: any;
  // CPU: single board ID
  singleBoardId: number | null;
  onSelectSingle: (id: number | null) => void;
  // Multi: array of board IDs
  multiBoards: number[];
  onToggleMulti: (id: number) => void;
  // Room selection (CPU mode)
  selectedRoom: 'rookie' | 'champion';
  onRoomChange: (r: 'rookie' | 'champion') => void;
  // Multiplier / Stakes selection
  multiplier: number;
  onMultiplierChange: (m: number) => void;
  // Navigation
  onPlay: () => void;       // CPU → cpu-sim
  onContinue: () => void;   // Multi → budget
  error: string | null;
  onClearError: () => void;
}

// ── CpuStatsPanel ─────────────────────────────────────────────────────────────
// Shows per-axo combat stats for the selected CPU room. Pure frontend math.

function CpuStatsPanel({ axo, showEconomicBonuses }: { axo: any; showEconomicBonuses: boolean }) {
  const [expanded, setExpanded] = React.useState(false);

  // Core formulas (mirror game.py)
  const missChance   = Math.max(0, Math.min(0.3, (100 - (axo?.stat_focus ?? 50)) * 0.003));
  const accuracy     = Math.round((1 - missChance) * 100);
  const luckBonusPct = ((axo?.stat_luck ?? 0) / 10).toFixed(1);           // max +10% at luck=100
  const salVal       = axo?.stat_salinity ?? 0;
  const streak       = axo?.cpu_win_streak ?? 0;
  const streakBonus  = streak >= 1 ? Math.min(50, streak * 15) : 0;

  const accuracyColor =
    accuracy >= 90 ? 'text-emerald-400' :
    accuracy >= 75 ? 'text-amber-400'   :
                     'text-rose-400';

  return (
    <div className="bg-slate-950/40 border border-slate-800/50 rounded-2xl overflow-hidden">

      {/* Header row — tap to toggle on mobile, static label on sm+ */}
      <button
        type="button"
        onClick={() => setExpanded(e => !e)}
        className="w-full flex items-center justify-between px-3 py-2 sm:cursor-default"
      >
        <span className="text-[9px] font-black text-slate-400 uppercase tracking-widest">
          📊 Tus stats en esta sala
        </span>
        <span className="sm:hidden text-[9px] text-slate-500 font-bold">
          {expanded ? '▲' : '▼'}
        </span>
      </button>

      {/* Stats grid — hidden on mobile until expanded; always visible on sm+ */}
      <div className={`sm:block ${expanded ? '' : 'hidden'}`}>
        <div className="px-3 pb-3 grid grid-cols-2 gap-2">

          {/* Accuracy */}
          <div className="bg-slate-900/60 rounded-xl p-2">
            <p className="text-[8px] text-slate-500 font-bold uppercase tracking-wider mb-0.5">👁️ OJO (Precisión)</p>
            <p className={`text-sm font-black leading-none ${accuracyColor}`}>{accuracy}%</p>
            <p className="text-[7px] text-slate-600 mt-0.5">miss {(missChance * 100).toFixed(0)}%</p>
          </div>

          {/* Luck bonus */}
          <div className="bg-slate-900/60 rounded-xl p-2">
            <p className="text-[8px] text-slate-500 font-bold uppercase tracking-wider mb-0.5">✨ SUERTE</p>
            <p className="text-sm font-black leading-none text-emerald-400">
              {showEconomicBonuses ? `+${luckBonusPct}%` : (axo?.stat_luck ?? 0)}
            </p>
            <p className="text-[7px] text-slate-600 mt-0.5">
              {showEconomicBonuses ? 'sobre el premio' : 'atributo de juego'}
            </p>
          </div>

          {/* SAL */}
          <div className="bg-slate-900/60 rounded-xl p-2">
            <p className="text-[8px] text-slate-500 font-bold uppercase tracking-wider mb-0.5">🧂 SAL</p>
            <p className="text-sm font-black leading-none" style={{ color: '#f87171' }}>{salVal.toFixed(0)}</p>
            <p className="text-[7px] text-slate-600 mt-0.5">↓ mejor</p>
          </div>

          {/* Streak */}
          <div className="bg-slate-900/60 rounded-xl p-2">
            <p className="text-[8px] text-slate-500 font-bold uppercase tracking-wider mb-0.5">🔥 Racha</p>
            {streak >= 1 ? (
              <>
                <p className="text-sm font-black leading-none text-amber-400">×{streak}</p>
                <p className="text-[7px] text-slate-600 mt-0.5">
                  {showEconomicBonuses ? `+${streakBonus}% si ganas` : 'victorias seguidas'}
                </p>
              </>
            ) : (
              <>
                <p className="text-sm font-black leading-none text-slate-600">Sin racha</p>
                <p className="text-[7px] text-slate-600 mt-0.5">gana para iniciarla</p>
              </>
            )}
          </div>

        </div>
      </div>
    </div>
  );
}

function boardToNums(board: any, allCards: any[]): number[] {
  return Array(16).fill(0).map((_, i) => {
    const cid = board.card_ids?.[i];
    if (!cid) return 0;
    const c = allCards.find((ac: any) => Number(ac.id) === Number(cid));
    return c ? (Number(c.item_metadata?.numero_loteria) || 0) : 0;
  });
}

export default function BoardSelectScreen({
  mode,
  playerBoards,
  allCards,
  axolotitos,
  selectedAxo,
  singleBoardId,
  onSelectSingle,
  multiBoards,
  onToggleMulti,
  selectedRoom,
  onRoomChange,
  multiplier,
  onMultiplierChange,
  onPlay,
  onContinue,
  error,
  onClearError,
}: BoardSelectScreenProps) {
  const [hoveredBoard, setHoveredBoard] = React.useState<any | null>(null);
  const [mousePos, setMousePos] = React.useState({ x: 0, y: 0 });
  const { capabilities, loading } = useProductPolicy();
  const paidEntriesEnabled = capabilities.gameplay.paid_entries;
  const freePlayEnabled = capabilities.gameplay.free_play;
  const modeAllowed = mode === 'multi'
    ? paidEntriesEnabled
    : paidEntriesEnabled || freePlayEnabled;

  if (!modeAllowed) {
    return (
      <div className="py-10 text-center rounded-3xl border border-amber-500/20 bg-amber-950/20 px-6">
        <div className="text-4xl mb-3">🛟</div>
        <h3 className="text-sm font-black text-amber-200 uppercase tracking-widest">
          {mode === 'multi' ? 'Multijugador no disponible' : 'Juego en pausa segura'}
        </h3>
        <p className="mt-2 text-xs text-slate-400">
          {loading
            ? 'Verificando la política de producto…'
            : mode === 'multi'
              ? 'Las salas con presupuesto, cuotas o premios están deshabilitadas.'
              : 'El servidor todavía no confirmó una partida gratuita.'}
        </p>
      </div>
    );
  }

  // Map boards occupied by OTHER axolotitos
  const occupiedMap = new Map<number, string>();
  axolotitos.forEach((a) => {
    if (selectedAxo && a.id !== selectedAxo.id && a.assigned_board_id && a.status === 'playing') {
      occupiedMap.set(a.assigned_board_id, a.name);
    }
  });

  const handleMouseMove = (e: React.MouseEvent) => setMousePos({ x: e.clientX, y: e.clientY });

  const isBoardSelected = (id: number) =>
    mode === 'cpu' ? singleBoardId === id : multiBoards.includes(id);

  const handleClick = (board: any) => {
    if (!modeAllowed) return;
    if (occupiedMap.has(board.id)) return;
    if (mode === 'cpu') {
      onSelectSingle(singleBoardId === board.id ? null : board.id);
    } else {
      onToggleMulti(board.id);
    }
    onClearError();
  };

  const hasSelection = mode === 'cpu' ? singleBoardId !== null : multiBoards.length > 0;

  if (playerBoards.length === 0) {
    return (
      <div className="space-y-4">
        <h3 className="text-xs font-black text-slate-400 uppercase tracking-widest">
          {mode === 'cpu' ? 'Elige tu Tabla' : 'Elige tus Tablas (1–3)'}
        </h3>
        <div className="bg-slate-950/40 border border-dashed border-amber-500/20 rounded-2xl p-10 text-center">
          <p className="text-xs font-black text-amber-400">⚠️ Sin tablas disponibles</p>
          <p className="text-[10px] text-slate-500 mt-1">Crea una tabla en "Mis Tablas" primero.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-black text-slate-400 uppercase tracking-widest">
          {mode === 'cpu' ? 'Elige tu Tabla' : `Elige tus Tablas (${multiBoards.length}/3)`}
        </h3>
        {mode === 'multi' && (
          <span className="text-[9px] font-black text-amber-400">
            {multiBoards.length}/3 seleccionadas
          </span>
        )}
      </div>

      {error && (
        <div className="bg-red-950/50 border border-red-500/30 text-red-300 text-[10px] font-bold rounded-xl p-2.5">
          {error}
        </div>
      )}

      {/* Board Grid */}
      <div
        className="grid grid-cols-2 sm:grid-cols-3 gap-3"
        onMouseLeave={() => setHoveredBoard(null)}
      >
        {playerBoards.map((board) => {
          const selected      = isBoardSelected(board.id);
          const occupiedBy    = occupiedMap.get(board.id);
          const isOccupied    = !!occupiedBy;
          const selectionIdx  = mode === 'multi' ? multiBoards.indexOf(board.id) + 1 : 0;

          const boardNums    = boardToNums(board, allCards);
          const filledSlots  = boardNums.map((n, i) => n > 0 ? i : -1).filter(i => i >= 0);

          return (
            <div
              key={board.id}
              onMouseEnter={() => setHoveredBoard(board)}
              onMouseLeave={() => setHoveredBoard(null)}
              onMouseMove={handleMouseMove}
              onClick={() => handleClick(board)}
              className={`relative p-3 rounded-2xl border transition-all duration-200 select-none flex flex-col gap-2 cursor-pointer ${
                selected
                  ? 'bg-slate-900 border-emerald-500 shadow-[0_0_15px_rgba(16,185,129,0.3)] ring-1 ring-emerald-500/30'
                  : isOccupied
                    ? 'bg-slate-950/50 border-slate-900/60 opacity-40 cursor-not-allowed'
                    : 'bg-slate-900/20 border-slate-800 hover:border-slate-700 hover:bg-slate-900/40'
              }`}
            >
              {/* Board name + level */}
              <div className="flex justify-between items-start gap-1">
                <span className="text-[9px] font-black uppercase text-slate-200 truncate max-w-[80px]">
                  {board.name}
                </span>
                <span className="text-[8px] font-black px-1 py-0.5 rounded bg-slate-950 text-slate-400 shrink-0">
                  Nv.{board.level}
                </span>
              </div>

              {/* Mini board */}
              <div className="mx-auto w-fit shrink-0">
                <BoardCardGrid
                  boardNums={boardNums}
                  cardSize={16}
                  priorityLine={filledSlots}
                />
              </div>

              {/* Stats */}
              <div className="flex justify-between text-[7px] text-slate-500 font-bold">
                <span>J: {board.games_played}</span>
                <span>G: {board.games_won}</span>
              </div>

              {/* Checkmark number for multi */}
              {selected && mode === 'multi' && selectionIdx > 0 && (
                <div className="absolute top-1.5 right-1.5 w-5 h-5 rounded-full bg-emerald-500 text-white text-[10px] font-black flex items-center justify-center shadow">
                  {selectionIdx}
                </div>
              )}

              {/* Occupied overlay */}
              {isOccupied && (
                <div className="absolute inset-0 bg-slate-950/90 rounded-2xl flex flex-col items-center justify-center p-2 text-center pointer-events-none">
                  <span className="text-[8px] text-amber-400 font-black uppercase tracking-wider">En Juego 🎮</span>
                  <span className="text-[7px] text-slate-400 font-bold truncate max-w-full px-1">{occupiedBy}</span>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Room selector (CPU mode only) */}
      {mode === 'cpu' && (
        <div className="space-y-2">
          <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Sala de juego</p>
          <div className="grid grid-cols-2 gap-3">
            {/* ── Rookie ── */}
            <button
              onClick={() => onRoomChange('rookie')}
              className={`p-3 rounded-2xl border text-left transition-all ${
                selectedRoom === 'rookie'
                  ? 'bg-slate-900 border-indigo-500/80 shadow-[0_0_15px_rgba(99,102,241,0.25)]'
                  : 'bg-slate-900/30 border-slate-800 hover:border-slate-700'
              }`}
            >
              <span className="text-[9px] font-black uppercase tracking-widest text-indigo-300 block">Novatos</span>
              <span className="text-xs font-black text-white">Charco de Novatos</span>
              {/* Opponent count badge */}
              <div className="mt-1.5 inline-flex items-center gap-1 text-[8px] font-black bg-indigo-950/60 border border-indigo-500/20 px-1.5 py-0.5 rounded-full text-indigo-300">
                ⚔️ 1v1 · 1 bot
              </div>
              <div className="flex items-center justify-between gap-1 mt-1.5">
                {paidEntriesEnabled ? (
                  <>
                    <span className="flex items-center gap-1 text-[9px] text-amber-400 font-black">
                      <Coins size={9} /> {100 * multiplier} FRJ
                    </span>
                    <span className="text-[9px] text-emerald-400 font-black">🏆 +{160 * multiplier}</span>
                  </>
                ) : (
                  <span className="text-[9px] text-emerald-400 font-black">✓ Gratis · Sin premio FRJ</span>
                )}
              </div>
            </button>

            {/* ── Champion ── */}
            <button
              onClick={() => onRoomChange('champion')}
              className={`p-3 rounded-2xl border text-left transition-all ${
                selectedRoom === 'champion'
                  ? 'bg-slate-900 border-pink-500/80 shadow-[0_0_15px_rgba(244,63,94,0.25)]'
                  : 'bg-slate-900/30 border-slate-800 hover:border-slate-700'
              }`}
            >
              <span className="text-[9px] font-black uppercase tracking-widest text-pink-300 block">Pro</span>
              <span className="text-xs font-black text-white">Fosa del Campeón</span>
              {/* Opponent count badge */}
              <div className="mt-1.5 inline-flex items-center gap-1 text-[8px] font-black bg-pink-950/60 border border-pink-500/20 px-1.5 py-0.5 rounded-full text-pink-300">
                ⚔️ 1v5 · 5 bots
              </div>
              <div className="flex items-center justify-between gap-1 mt-1.5">
                {paidEntriesEnabled ? (
                  <>
                    <span className="flex items-center gap-1 text-[9px] text-amber-400 font-black">
                      <Coins size={9} /> {500 * multiplier} FRJ
                    </span>
                    <span className="text-[9px] text-emerald-400 font-black">🏆 +{2900 * multiplier}</span>
                  </>
                ) : (
                  <span className="text-[9px] text-emerald-400 font-black">✓ Gratis · Sin premio FRJ</span>
                )}
              </div>
            </button>
          </div>

          {/* ── Multiplier / Stakes Selector ── */}
          {paidEntriesEnabled && <div className="space-y-2 mt-4 animate-fade-in">
            <div className="flex justify-between items-center mt-3">
              <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Multiplicador de Apuesta (Stakes)</p>
              <span className="text-[9px] font-black text-indigo-300 bg-indigo-950/60 border border-indigo-500/20 px-2 py-0.5 rounded-full">
                x{multiplier} Stakes
              </span>
            </div>
            <div className="grid grid-cols-4 gap-2">
              {[1, 2, 5, 10].map((m) => (
                <button
                  key={m}
                  type="button"
                  onClick={() => onMultiplierChange(m)}
                  className={`py-2 text-center rounded-xl border text-xs font-black transition-all ${
                    multiplier === m
                      ? 'bg-gradient-to-r from-indigo-600 to-pink-600 border-indigo-500/50 text-white shadow-[0_0_15px_rgba(99,102,241,0.25)]'
                      : 'bg-slate-900/30 border-slate-800/80 text-slate-400 hover:border-slate-700 hover:text-white'
                  }`}
                >
                  {m}x
                </button>
              ))}
            </div>
          </div>}
        </div>
      )}

      {/* Stats panel — CPU mode only, below room selector */}
      {mode === 'cpu' && selectedAxo && (
        <CpuStatsPanel axo={selectedAxo} showEconomicBonuses={paidEntriesEnabled} />
      )}

      {/* CTA footer */}
      {hasSelection && (
        <div className="pt-2">
          {mode === 'cpu' ? (
            <button
              onClick={onPlay}
              className="w-full py-4 bg-gradient-to-r from-[var(--brand-hot)] to-indigo-600 hover:from-pink-500 hover:to-indigo-500 text-white font-black text-xl uppercase tracking-widest rounded-2xl transition-all shadow-[0_0_30px_var(--brand-glow)] active:scale-[0.97] animate-sheet-up flex items-center justify-center gap-3 border border-white/5"
              style={{ borderRadius: '20px' }}
              onMouseEnter={e => { (e.currentTarget as HTMLButtonElement).style.boxShadow = '0 0 40px var(--brand-glow)'; }}
              onMouseLeave={e => { (e.currentTarget as HTMLButtonElement).style.boxShadow = '0 0 30px var(--brand-glow)'; }}
            >
              <Play size={20} fill="currentColor" /> {paidEntriesEnabled ? 'JUGAR' : 'JUGAR GRATIS'}
            </button>
          ) : (
            <button
              onClick={onContinue}
              className="w-full py-4 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-white font-black text-sm uppercase tracking-widest rounded-2xl transition-all active:scale-[0.98] animate-sheet-up"
            >
              Continuar →
            </button>
          )}
        </div>
      )}

      {/* Floating cursor tooltip */}
      {hoveredBoard && typeof window !== 'undefined' && createPortal(
        <div
          className="fixed pointer-events-none z-[999] bg-slate-950/95 border border-indigo-500/35 rounded-3xl p-3.5 shadow-[0_15px_30px_rgba(0,0,0,0.8)] backdrop-blur-md w-56 space-y-2 text-white"
          style={{ top: mousePos.y + 15, left: mousePos.x + 15 }}
        >
          <div className="flex justify-between items-center border-b border-white/5 pb-1.5">
            <span className="text-[10px] font-black uppercase text-indigo-300 truncate max-w-[120px]">
              {hoveredBoard.name}???
            </span>
            <span className="text-[8px] font-black bg-indigo-950 border border-indigo-500/20 text-indigo-200 px-1.5 py-0.5 rounded shrink-0">
              Nv.{hoveredBoard.level}
            </span>
          </div>
          <BoardCardGrid
            boardNums={boardToNums(hoveredBoard, allCards)}
            cardSize={44}
          />
          <div className="flex justify-between text-[7px] text-slate-500 font-bold pt-1 border-t border-white/5">
            <span>Partidas: {hoveredBoard.games_played}</span>
            <span>Ganadas: {hoveredBoard.games_won}</span>
          </div>
        </div>,
        document.body
      )}
    </div>
  );
}
