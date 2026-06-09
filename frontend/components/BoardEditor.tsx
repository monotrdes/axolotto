import { API_BASE } from "@/lib/api";
import { useState, useEffect, useMemo } from 'react';
import { X, Shuffle, Sparkles, Save, Undo2, Plus, Trash2, ShoppingCart } from 'lucide-react';
import axios from 'axios';
import LoteriaCard from '@/components/ui/LoteriaCard';

interface BoardEditorProps {
  userId: string;
  token: string | null;
  boardToEdit?: any | null;
  onClose: () => void;
  onSaved: () => void;
  cambiarTab: (tab: string) => void;
}

/* ─── Hueco vacío ────────────────────────────────────────────── */
function EmptySlot({ size, state, idx, onClick }: {
  size: number; state: 'empty' | 'target' | 'source'; idx: number; onClick?: () => void;
}) {
  const w = size;
  const h = Math.round(size * 1.5);
  return (
    <div
      onClick={onClick}
      className="relative cursor-pointer flex items-center justify-center transition-all"
      style={{
        width: w, height: h,
        borderRadius: Math.max(6, w*.12),
        border: state === 'target'
          ? '2px dashed rgba(52,211,153,0.9)'
          : state === 'source'
            ? '2px dashed rgba(251,191,36,0.7)'
            : '1.5px dashed rgba(148,163,184,0.18)',
        background: state === 'target' ? 'rgba(52,211,153,0.08)'
          : state === 'source' ? 'rgba(251,191,36,0.06)' : 'rgba(15,15,35,0.5)',
        animation: state === 'target' ? 'targetPulse 1s ease-in-out infinite' : undefined,
      }}
    >
      <span className="font-black italic" style={{
        fontSize: Math.max(11, w*.3),
        color: state === 'target' ? '#34d399' : 'rgba(148,163,184,0.25)',
      }}>
        {state === 'target' ? '+' : String(idx + 1).padStart(2, '0')}
      </span>
    </div>
  );
}

/* ─── Grid del tablero (reutilizable) ────────────────────────── */
function BoardGrid({ grid, pickedCard, pickedFromGridIdx, onTap, slotSize, gap = 6 }: {
  grid: (any|null)[]; pickedCard: any; pickedFromGridIdx: number|null;
  onTap: (i: number) => void; slotSize: number; gap?: number;
}) {
  return (
    <div className="grid" style={{ gridTemplateColumns: `repeat(4,${slotSize}px)`, gap }}>
      {grid.map((c, i) => {
        const isSource = pickedFromGridIdx === i;
        const isTarget = !!pickedCard && !isSource;
        if (c && !isSource) {
          return (
            <div key={i} onClick={() => onTap(i)}>
              <LoteriaCard card={c} size={slotSize} onClick={() => onTap(i)} showQty={false} />
            </div>
          );
        }
        return (
          <EmptySlot key={i} size={slotSize} idx={i}
            state={isSource ? 'source' : isTarget ? 'target' : 'empty'}
            onClick={() => onTap(i)} />
        );
      })}
    </div>
  );
}

/* ─── Componente principal ───────────────────────────────────── */
export default function BoardEditor({ userId, token, boardToEdit = null, onClose, onSaved, cambiarTab }: BoardEditorProps) {
  const [boardName, setBoardName] = useState(boardToEdit ? boardToEdit.name : 'Mi Tabla Lotería');
  const [grid, setGrid] = useState<(any|null)[]>(Array(16).fill(null));
  const [history, setHistory] = useState<(any|null)[][]>([]);
  const [inventory, setInventory] = useState<any[]>([]);
  const [allCards, setAllCards] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [guardando, setGuardando] = useState(false);
  const [error, setError] = useState<string|null>(null);
  const [pickedCard, setPickedCard] = useState<any|null>(null);
  const [pickedFromGridIdx, setPickedFromGridIdx] = useState<number|null>(null);
  const [deckFilter, setDeckFilter] = useState<'libres'|'enTablero'>('libres');

  /* ─── carga ────────────────────────────────────────────── */
  useEffect(() => {
    const load = async () => {
      try {
        const headers = token ? { Authorization: `Bearer ${token}` } : {};
        const [resInv, resCards] = await Promise.all([
          axios.get(`${API_BASE}/auth/inventory/${userId}`, { headers }),
          axios.get(`${API_BASE}/shop/cards`),
        ]);
        const cards: any[] = resCards.data;
        setInventory(resInv.data);
        setAllCards(cards);
        if (boardToEdit) {
          const loadedGrid = Array(16).fill(null);
          (boardToEdit.card_ids as (number|string)[]).forEach((rawId, idx) => {
            const cardObj = cards.find((c: any) => c.id === Number(rawId));
            if (cardObj) loadedGrid[idx] = cardObj;
          });
          setGrid(loadedGrid);
        }
      } catch {
        setError('Error al cargar cartas del inventario.');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [userId, token, boardToEdit]);

  /* ─── derivados ─────────────────────────────────────────── */
  const gridCardIds = useMemo(() => new Set(grid.filter(Boolean).map((c: any) => c.id)), [grid]);
  const filledCount = grid.filter(Boolean).length;
  const progress = filledCount / 16;
  const ready = filledCount === 16;

  const deck = useMemo(() => {
    const out: any[] = [];
    allCards.forEach(card => {
      // El inventario ya refleja el stake real: quantity = copias disponibles (no stakeadas en tablas)
      const copies = inventory.filter(i => i.id === card.id && i.item_type?.toLowerCase() === 'card');
      const qty = copies.reduce((s, i) => s + (i.quantity || 0), 0);
      if (qty > 0 && !gridCardIds.has(card.id)) out.push({ ...card, availableQty: qty });
    });
    out.sort((a,b) => (Number(a.item_metadata?.numero_loteria)||99) - (Number(b.item_metadata?.numero_loteria)||99));
    return out;
  }, [allCards, inventory, gridCardIds]);

  const gridCards = useMemo(() => grid.filter(Boolean), [grid]);

  // ¿Tiene el jugador suficientes cartas únicas para completar un tablero?
  const totalUniqueAvailable = deck.length + filledCount;
  const canCompleteBoard = totalUniqueAvailable >= 16;

  /* ─── helpers ───────────────────────────────────────────── */
  const cancelPick = () => { setPickedCard(null); setPickedFromGridIdx(null); };
  const pushHistory = (g: (any|null)[]) => setHistory(h => [...h.slice(-19), g]);
  const undo = () => {
    if (!history.length) return;
    setGrid(history[history.length - 1]);
    setHistory(h => h.slice(0,-1));
    cancelPick();
  };

  const handleGridTap = (index: number) => {
    const slotCard = grid[index];
    if (pickedCard) {
      if (pickedFromGridIdx === index) {
        // Segundo tap en la misma carta → sacarla del tablero
        pushHistory(grid);
        const next = [...grid];
        next[index] = null;
        setGrid(next);
        cancelPick();
        return;
      }
      pushHistory(grid);
      const next = [...grid];
      if (pickedFromGridIdx !== null) {
        next[pickedFromGridIdx] = slotCard ?? null;
        next[index] = pickedCard;
      } else {
        next[index] = pickedCard;
      }
      setGrid(next);
      cancelPick();
      setError(null);
    } else if (slotCard) {
      setPickedCard(slotCard);
      setPickedFromGridIdx(index);
    }
  };

  const handleDeckTap = (card: any) => {
    if (gridCardIds.has(card.id)) return;
    if (pickedCard?.id === card.id && pickedFromGridIdx === null) cancelPick();
    else { setPickedCard(card); setPickedFromGridIdx(null); }
  };

  /* ─── acciones desktop ──────────────────────────────────── */
  const handleVaciar = () => {
    if (!filledCount) return;
    pushHistory(grid);
    setGrid(Array(16).fill(null));
    cancelPick();
  };

  const handleRandomizeEmpty = () => {
    const empty = grid.reduce<number[]>((acc, c, i) => (c ? acc : [...acc, i]), []);
    if (!empty.length) return;
    if (deck.length < empty.length) {
      setError('No hay suficientes cartas libres para llenar los huecos.');
      setTimeout(() => setError(null), 3000);
      return;
    }
    const shuffled = [...deck].sort(() => Math.random() - .5);
    pushHistory(grid);
    const next = [...grid];
    empty.forEach((idx, i) => { next[idx] = shuffled[i]; });
    setGrid(next);
    cancelPick();
  };

  const handleReflect = () => {
    pushHistory(grid);
    const next = [...grid];
    for (let row = 0; row < 4; row++) {
      const r = row * 4;
      [next[r], next[r+3]] = [next[r+3], next[r]];
      [next[r+1], next[r+2]] = [next[r+2], next[r+1]];
    }
    setGrid(next);
    cancelPick();
  };

  /* ─── API ───────────────────────────────────────────────── */
  const handleSaveManual = async () => {
    setError(null);
    const cardIds = grid.map(c => c ? c.id : null);
    if (!boardToEdit && cardIds.includes(null)) {
      setError('Debes rellenar las 16 casillas antes de guardar.');
      return;
    }
    setGuardando(true);
    try {
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      if (boardToEdit) {
        await axios.put(`${API_BASE}/board/${boardToEdit.id}/edit`, { name: boardName }, { headers });
      } else {
        // Determinar si cada carta es Primera Edición o Normal
        // El backend valida por separado; si el usuario solo tiene copia FE, hay que indicarlo
        const cardFirstEditions = grid.map(c => {
          if (!c) return false;
          const normalCopies = inventory.filter(
            i => i.id === c.id && i.item_type?.toLowerCase() === 'card' && !i.is_first_edition
          );
          const hasNormal = normalCopies.some(i => (i.quantity || 0) > 0);
          return !hasNormal; // true = solo tiene FE, false = usa copia normal
        });
        await axios.post(
          `${API_BASE}/board/create/manual`,
          { name: boardName, card_ids: cardIds as number[], card_first_editions: cardFirstEditions },
          { headers }
        );
      }
      onSaved();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ocurrió un error al guardar tu tabla.');
    } finally {
      setGuardando(false);
    }
  };

  const handleCreateRandom = async () => {
    setError(null);
    setGuardando(true);
    try {
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      await axios.post(`${API_BASE}/board/create/random`, { name: boardName, card_ids: [] }, { headers });
      onSaved();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ocurrió un error al generar la tabla.');
    } finally {
      setGuardando(false);
    }
  };

  /* ─── Loading ───────────────────────────────────────────── */
  if (loading) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/95 backdrop-blur-md">
        <div className="flex flex-col items-center gap-3">
          <div className="w-10 h-10 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin" />
          <p className="text-teal-400 animate-pulse font-black text-xs uppercase tracking-widest">Cargando Editor...</p>
        </div>
      </div>
    );
  }

  /* ─── Modo renombrar ────────────────────────────────────── */
  if (boardToEdit) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/90 backdrop-blur-md p-4 animate-in fade-in duration-200">
        <div className="bg-slate-950 border-2 border-emerald-500/40 rounded-3xl p-6 max-w-sm w-full shadow-[0_0_40px_rgba(16,185,129,0.2)] flex flex-col gap-5">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-lg font-black italic text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-teal-400 tracking-tight flex items-center gap-2">
                <Sparkles size={16} className="text-emerald-400 animate-pulse" />
                Renombrar Tabla
              </h2>
              <p className="text-[10px] text-slate-500 mt-0.5">El cambio de nombre es gratuito.</p>
            </div>
            <button onClick={onClose} className="p-2 bg-slate-900 border border-slate-800 hover:bg-slate-800 text-slate-400 hover:text-white rounded-xl transition-all">
              <X size={14} />
            </button>
          </div>
          <div>
            <label className="block text-[9px] font-black text-slate-400 uppercase tracking-widest mb-1.5">Nombre de la Tabla</label>
            <input type="text" value={boardName} onChange={e => setBoardName(e.target.value)}
              className="w-full bg-slate-900 border border-slate-800 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 rounded-xl px-4 py-2.5 text-sm text-white font-bold focus:outline-none"
              placeholder="Ej. La Suertuda de Xochi" />
          </div>
          {error && <div className="bg-red-950/60 border border-red-500/20 text-red-200 text-xs font-bold rounded-xl p-3 text-center">⚠️ {error}</div>}
          <div className="flex gap-3">
            <button onClick={onClose} className="flex-1 py-2.5 bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-white rounded-xl text-xs font-black uppercase tracking-widest transition-all">Cancelar</button>
            <button onClick={handleSaveManual} disabled={guardando}
              className="flex-1 py-2.5 bg-gradient-to-r from-emerald-600 to-teal-500 hover:from-emerald-500 hover:to-teal-400 text-white rounded-xl text-xs font-black uppercase tracking-widest flex items-center justify-center gap-1.5 transition-all active:scale-95 disabled:opacity-50">
              <Save size={13} />
              {guardando ? 'Guardando...' : 'Guardar'}
            </button>
          </div>
        </div>
      </div>
    );
  }

  /* ══════════════════════════════════════════════════════════
   * MÓVIL — layout original limpio (solo click)
   * ══════════════════════════════════════════════════════════ */
  const SLOT = 62;
  const HAND_CARD = 92;

  const mobileLayout = (
    <div
      className="lg:hidden fixed inset-0 z-50 flex flex-col overflow-hidden text-white animate-in fade-in duration-200"
      style={{ background: 'radial-gradient(85% 55% at 50% 20%, #141428 0%, #060610 65%, #000 100%)' }}
    >
      {/* halo */}
      <div className="pointer-events-none absolute" style={{ top:80, left:'50%', transform:'translateX(-50%)', width:340, height:340, borderRadius:'50%', background:'radial-gradient(circle,rgba(52,211,153,0.13),transparent 60%)' }} />

      {/* HEADER */}
      <div className="relative z-10 flex items-start gap-2.5 px-3.5 pt-4 pb-1.5">
        <button onClick={onClose} className="w-9 h-9 rounded-xl bg-white/[0.06] border border-white/[0.08] text-slate-400 hover:text-white hover:bg-white/[0.1] flex items-center justify-center transition-all shrink-0">
          <X size={15} />
        </button>
        <div className="flex-1 min-w-0 pt-0.5">
          <div className="text-[8.5px] font-black text-slate-500 tracking-[0.18em]">DISEÑANDO</div>
          <input value={boardName} onChange={e => setBoardName(e.target.value)}
            placeholder="Nombre de tu tabla…"
            className="w-full bg-transparent border-0 outline-none text-[15px] font-black italic text-white placeholder:text-slate-600 p-0" />
        </div>
        {/* dial circular */}
        <div className="relative w-[54px] h-[54px] shrink-0">
          <svg width="54" height="54" viewBox="0 0 54 54" className="absolute inset-0 -rotate-90">
            <circle cx="27" cy="27" r="23" fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth="3.5" />
            <circle cx="27" cy="27" r="23" fill="none" stroke={ready ? '#34d399' : '#22d3ee'} strokeWidth="3.5"
              strokeLinecap="round" strokeDasharray={2*Math.PI*23} strokeDashoffset={2*Math.PI*23*(1-progress)}
              style={{ transition:'stroke-dashoffset .4s cubic-bezier(.2,.7,.3,1)', filter: ready ? 'drop-shadow(0 0 6px rgba(52,211,153,0.8))' : 'drop-shadow(0 0 4px rgba(34,211,238,0.5))' }} />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center leading-none">
            <span className={`text-[16px] font-black italic ${ready ? 'text-emerald-400' : 'text-white'}`}>{String(filledCount).padStart(2,'0')}</span>
            <span className="text-[7.5px] font-black italic text-slate-500 tracking-[0.1em] mt-0.5">/16</span>
          </div>
        </div>
      </div>

      {/* TABLERO */}
      <div className="relative z-10 mx-auto mt-3" style={{ width: SLOT*4 + 6*3 + 24 }}>
        <div className="relative p-3 rounded-2xl border-[1.5px] border-emerald-500/25"
          style={{ background:'rgba(0,0,0,0.45)', boxShadow:'0 0 30px rgba(52,211,153,0.15),inset 0 0 20px rgba(0,0,0,0.5)' }}>
          <div className="absolute -top-2.5 left-1/2 -translate-x-1/2 px-3 py-0.5 rounded-md text-[9px] font-black italic tracking-[0.2em] text-emerald-400 border border-emerald-500/40" style={{ background:'#060610' }}>
            TABLERO
          </div>
          <BoardGrid grid={grid} pickedCard={pickedCard} pickedFromGridIdx={pickedFromGridIdx} onTap={handleGridTap} slotSize={SLOT} gap={6} />
        </div>
      </div>

      {/* indicador picking */}
      {pickedCard && (
        <div className="absolute left-1/2 -translate-x-1/2 z-50 flex flex-col items-center gap-1"
          style={{ top:76 }}>
          <div className="px-3 py-1.5 rounded-full bg-emerald-500/20 border-[1.2px] border-emerald-400 text-[9.5px] font-black italic text-emerald-300 tracking-wider whitespace-nowrap"
            style={{ animation:'editorNeonPulse 1.2s ease-in-out infinite', boxShadow:'0 0 14px rgba(52,211,153,0.4)' }}>
            {pickedFromGridIdx !== null ? '▼ ELIGE DESTINO • TOCA DE NUEVO PARA QUITAR ▼' : '▼ TOCA UN HUECO DEL TABLERO ▼'}
          </div>
        </div>
      )}

      {/* MOCHILA */}
      <div className="relative z-10 mt-3 flex flex-col pb-[88px]">
        <div className="px-4 pb-1 text-[9px] font-black italic tracking-[0.2em] text-slate-500 flex items-center gap-2">
          <span style={{ color:'#E4007C' }}>♠</span>
          MOCHILA · {deck.length} CARTAS
          <span className="flex-1" />
          {deck.length > 4 && <span className="text-slate-400">DESLIZA →</span>}
        </div>
        <div className="relative" style={{ height:168, WebkitMaskImage:'linear-gradient(90deg,transparent 0%,#000 4%,#000 88%,transparent 100%)', maskImage:'linear-gradient(90deg,transparent 0%,#000 4%,#000 88%,transparent 100%)' }}>
          {deck.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center gap-3 px-6 text-center">
              <span className="text-4xl">📦</span>
              <p className="text-xs text-slate-500 font-semibold">
                {filledCount === 16 ? '¡Mochila vacía — todas tus cartas están en el tablero!' : 'No tienes cartas libres en tu mochila.'}
              </p>
              {filledCount < 16 && (
                <button onClick={() => { onClose(); cambiarTab('tienda'); }}
                  className="px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white font-black text-[10px] uppercase tracking-wider rounded-xl transition-all active:scale-95">
                  Comprar Sobres
                </button>
              )}
            </div>
          ) : (
            <div className="flex items-end h-full overflow-x-auto overflow-y-visible editor-hand-scroll px-4 pt-6 pb-2"
              style={{ scrollSnapType:'x mandatory', scrollPaddingLeft:16 }}>
              {deck.map((card, i) => {
                const isPicked = pickedCard?.id === card.id && pickedFromGridIdx === null;
                const tilt = ((i%2)*2-1)*2.5;
                const ty = (i%3)*1.5;
                return (
                  <div key={card.id} className="relative shrink-0" style={{
                    scrollSnapAlign:'start', marginLeft: i===0 ? 0 : -16,
                    zIndex: isPicked ? 100 : i%3===0 ? 1 : 2,
                    transform: isPicked ? 'translateY(-18px) scale(1.12) rotate(0deg)' : `translateY(${ty}px) rotate(${tilt}deg)`,
                    transformOrigin:'bottom center', transition:'transform .25s cubic-bezier(.2,.7,.3,1)',
                    filter: isPicked ? 'drop-shadow(0 12px 20px rgba(52,211,153,0.4))' : undefined,
                  }}>
                    <LoteriaCard card={card} size={HAND_CARD} picked={isPicked} showQty={false} onClick={() => handleDeckTap(card)} />
                  </div>
                );
              })}
            </div>
          )}
          {deck.length > 4 && (
            <div className="pointer-events-none absolute right-1 top-1/2 -translate-y-1/2 text-[16px] font-black text-slate-400/60"
              style={{ animation:'editorNeonPulse 1.8s ease-in-out infinite' }}>›</div>
          )}
        </div>
      </div>

      {/* error */}
      {error && (
        <div className="absolute bottom-[92px] left-3.5 right-3.5 bg-red-950/70 border border-red-500/30 text-red-200 text-[11px] font-bold rounded-xl p-2.5 text-center z-40">
          ⚠️ {error}
        </div>
      )}

      {/* HUB inferior */}
      <div className="absolute bottom-7 inset-x-0 px-3.5 flex items-center gap-2 z-30">
        <button onClick={undo} disabled={!history.length} title="Deshacer"
          className="h-11 w-11 rounded-xl bg-white/[0.06] border-[1.5px] border-white/[0.08] text-white flex items-center justify-center hover:bg-white/[0.1] disabled:opacity-40 disabled:cursor-not-allowed transition-all shrink-0">
          <Undo2 size={15} />
        </button>
        {!canCompleteBoard ? (
          /* CTA tienda cuando no hay suficientes cartas */
          <button onClick={() => { onClose(); cambiarTab('tienda'); }}
            className="flex-1 h-11 rounded-xl font-black italic text-[11px] tracking-wider flex items-center justify-center gap-1.5 transition-all active:scale-95 bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-[0_0_16px_rgba(168,85,247,0.4)]">
            <Plus size={13} />
            NECESITAS MÁS CARTAS · {totalUniqueAvailable}/16
          </button>
        ) : (
          <>
            <button onClick={handleCreateRandom} disabled={guardando} title="Tabla automática · 25 FRJ"
              className="h-11 px-3 rounded-xl border-[1.5px] flex items-center gap-1.5 text-white font-black italic text-[9px] tracking-widest disabled:opacity-50 transition-all active:scale-95"
              style={{ borderColor:'#E4007C', background:'rgba(228,0,124,0.15)' }}>
              <Shuffle size={13} /> AUTO
            </button>
            <button onClick={handleSaveManual} disabled={guardando || !ready}
              className={`flex-1 h-11 rounded-xl font-black italic text-[12px] tracking-[0.12em] flex items-center justify-center gap-1.5 transition-all active:scale-95 ${ready ? 'bg-gradient-to-r from-emerald-500 to-cyan-500 text-white shadow-[0_0_20px_rgba(16,185,129,0.5)]' : 'bg-white/5 text-slate-500 cursor-not-allowed'}`}>
              <Plus size={14} />
              {guardando ? 'GUARDANDO…' : 'CREAR · 50 FRJ'}
            </button>
          </>
        )}
      </div>

      <style>{`
        @keyframes editorNeonPulse { 0%,100%{opacity:.7} 50%{opacity:1} }
        @keyframes targetPulse { 0%,100%{box-shadow:0 0 0 0 rgba(52,211,153,0)} 50%{box-shadow:0 0 14px 2px rgba(52,211,153,0.4)} }
        .editor-hand-scroll::-webkit-scrollbar{display:none}
        .editor-hand-scroll{scrollbar-width:none}
      `}</style>
    </div>
  );

  /* ══════════════════════════════════════════════════════════
   * DESKTOP — 3 paneles (mockup "Taller de tablas")
   * ══════════════════════════════════════════════════════════ */
  const SLOT_D = 88;
  const DECK_CARD_D = 80;

  const visibleDeckDesktop = deckFilter === 'libres' ? deck : gridCards;

  const desktopLayout = (
    <div
      className="hidden lg:flex fixed inset-0 z-50 flex-col text-white animate-in fade-in duration-200"
      style={{ background:'radial-gradient(120% 60% at 50% 0%, #0d1a2e 0%, #060610 55%, #000 100%)' }}
    >
      {/* ── HEADER DESKTOP ── */}
      <div className="shrink-0 flex items-center gap-4 px-6 py-3 border-b border-white/[0.06]" style={{ background:'rgba(0,0,0,0.5)' }}>
        <button onClick={onClose} className="w-8 h-8 rounded-lg bg-white/[0.06] border border-white/[0.08] text-slate-400 hover:text-white hover:bg-white/[0.1] flex items-center justify-center transition-all">
          <X size={14} />
        </button>
        <div className="text-[10px] font-black text-slate-500 tracking-[0.2em] uppercase">axolot.to</div>
        <div className="w-px h-4 bg-white/10" />
        <div className="text-[11px] font-black italic text-emerald-400 tracking-widest">✦ DISEÑAR TABLA · 4×4</div>
        <div className="flex-1 flex justify-center">
          <input value={boardName} onChange={e => setBoardName(e.target.value)}
            placeholder="Nombre de tu tabla…"
            className="bg-transparent border-0 outline-none text-[17px] font-black italic text-white placeholder:text-slate-600 p-0 text-center w-80" />
        </div>
        <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-white/[0.08]" style={{ background:'rgba(255,255,255,0.04)' }}>
          <span className="text-[10px] font-black text-slate-500 tracking-widest uppercase">Saldo</span>
          <span className="text-[13px] font-black italic text-amber-500">— FRJ</span>
        </div>
        {!canCompleteBoard ? (
          <button onClick={() => { onClose(); cambiarTab('tienda'); }}
            className="h-9 px-5 rounded-lg font-black italic text-[11px] tracking-wider flex items-center gap-1.5 bg-gradient-to-r from-purple-600 to-pink-600 text-white hover:brightness-110 transition-all shadow-[0_0_16px_rgba(168,85,247,0.3)]">
            <ShoppingCart size={12} /> MÁS CARTAS · {totalUniqueAvailable}/16
          </button>
        ) : (
          <>
            <button onClick={handleCreateRandom} disabled={guardando}
              className="h-9 px-4 rounded-lg border flex items-center gap-1.5 font-black italic text-[11px] tracking-wider disabled:opacity-50 transition-all hover:brightness-110"
              style={{ borderColor:'#E4007C', background:'rgba(228,0,124,0.15)', color:'#fff' }}>
              <Shuffle size={12} /> AUTO · 25 FRJ
            </button>
            <button onClick={handleSaveManual} disabled={guardando || !ready}
              className={`h-9 px-5 rounded-lg font-black italic text-[11px] tracking-wider flex items-center gap-1.5 transition-all ${ready ? 'bg-gradient-to-r from-emerald-500 to-cyan-500 text-white shadow-[0_0_16px_rgba(16,185,129,0.4)] hover:brightness-110' : 'bg-white/5 text-slate-500 cursor-not-allowed'}`}>
              <Plus size={13} />
              {guardando ? 'GUARDANDO…' : 'CREAR · 50 FRJ'}
            </button>
          </>
        )}
      </div>

      {/* ── CUERPO 3 COLUMNAS ── */}
      <div className="flex-1 flex min-h-0">

        {/* ── PANEL IZQUIERDO: MOCHILA ── */}
        <div className="w-[380px] shrink-0 flex flex-col border-r border-white/[0.06]" style={{ background:'rgba(0,0,0,0.3)' }}>
          {/* header mochila */}
          <div className="px-4 pt-4 pb-2 shrink-0">
            <div className="text-[10px] font-black italic tracking-[0.2em] text-slate-400 mb-3 flex items-center gap-2">
              <span style={{ color:'#E4007C' }}>🎒</span>
              MOCHILA · {deck.length + gridCards.length} CARTAS
            </div>
            {/* filtros */}
            <div className="flex gap-1 mb-3">
              {([['libres', `SIN COLOCAR`, deck.length], ['enTablero', 'EN TABLERO', gridCards.length]] as const).map(([key, label, count]) => (
                <button key={key} onClick={() => setDeckFilter(key)}
                  className={`flex-1 py-1.5 rounded-lg text-[9px] font-black uppercase tracking-wider transition-all ${deckFilter === key ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40' : 'bg-white/[0.04] text-slate-500 border border-white/[0.06] hover:bg-white/[0.07]'}`}>
                  {label} <span className="opacity-60 ml-0.5">{count}</span>
                </button>
              ))}
            </div>
          </div>

          {/* grid de cartas */}
          <div className="flex-1 overflow-y-auto px-4 pb-4 editor-mochila-scroll">
            {visibleDeckDesktop.length === 0 ? (
              <div className="flex flex-col items-center justify-center gap-3 py-12 text-center">
                <span className="text-4xl">{deckFilter === 'libres' ? '📦' : '🃏'}</span>
                <p className="text-xs text-slate-500 font-semibold">
                  {deckFilter === 'libres' ? (filledCount === 16 ? '¡Todas tus cartas están en el tablero!' : 'No tienes cartas disponibles.') : 'El tablero está vacío.'}
                </p>
                {deckFilter === 'libres' && filledCount < 16 && (
                  <button onClick={() => { onClose(); cambiarTab('tienda'); }}
                    className="px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white font-black text-[10px] uppercase tracking-wider rounded-xl transition-all active:scale-95">
                    Comprar Sobres
                  </button>
                )}
              </div>
            ) : (
              <div className="grid gap-2" style={{ gridTemplateColumns: `repeat(4, ${DECK_CARD_D}px)` }}>
                {visibleDeckDesktop.map(card => {
                  const isPicked = pickedCard?.id === card.id && pickedFromGridIdx === null;
                  const isInGrid = deckFilter === 'enTablero';
                  return (
                    <div key={card.id} className="relative" style={{ transform: isPicked ? 'translateY(-6px) scale(1.05)' : undefined, transition:'transform .15s', filter: isPicked ? 'drop-shadow(0 8px 16px rgba(52,211,153,0.5))' : undefined }}>
                      <LoteriaCard card={card} size={DECK_CARD_D} picked={isPicked} showQty={!isInGrid}
                        onClick={isInGrid ? undefined : () => handleDeckTap(card)} />
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* ── PANEL CENTRAL: TABLERO ── */}
        <div className="flex-1 flex flex-col items-center justify-center gap-4 relative">
          {/* halo */}
          <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
            <div style={{ width:500, height:500, borderRadius:'50%', background:'radial-gradient(circle,rgba(52,211,153,0.07),transparent 65%)' }} />
          </div>

          {/* progreso */}
          <div className="relative z-10 flex items-center gap-3">
            <div className="relative w-[52px] h-[52px]">
              <svg width="52" height="52" viewBox="0 0 52 52" className="absolute inset-0 -rotate-90">
                <circle cx="26" cy="26" r="22" fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth="3" />
                <circle cx="26" cy="26" r="22" fill="none" stroke={ready ? '#34d399' : '#22d3ee'} strokeWidth="3"
                  strokeLinecap="round" strokeDasharray={2*Math.PI*22} strokeDashoffset={2*Math.PI*22*(1-progress)}
                  style={{ transition:'stroke-dashoffset .4s cubic-bezier(.2,.7,.3,1)', filter: ready ? 'drop-shadow(0 0 5px rgba(52,211,153,0.8))' : 'drop-shadow(0 0 4px rgba(34,211,238,0.5))' }} />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center leading-none">
                <span className={`text-[15px] font-black italic ${ready ? 'text-emerald-400' : 'text-white'}`}>{String(filledCount).padStart(2,'0')}</span>
                <span className="text-[7px] font-black italic text-slate-500 tracking-[0.1em]">/16</span>
              </div>
            </div>
            <div>
              <div className="text-[9px] font-black text-slate-500 tracking-[0.18em] uppercase">Tablero 4×4</div>
              <div className="text-[11px] font-black italic text-slate-300">{boardName || 'Sin nombre'}</div>
            </div>
          </div>

          {/* board */}
          <div className="relative z-10">
            <div className="relative p-3 rounded-2xl border border-emerald-500/20"
              style={{ background:'rgba(0,0,0,0.5)', boxShadow:'0 0 40px rgba(52,211,153,0.1),inset 0 0 30px rgba(0,0,0,0.6)' }}>
              <BoardGrid grid={grid} pickedCard={pickedCard} pickedFromGridIdx={pickedFromGridIdx} onTap={handleGridTap} slotSize={SLOT_D} gap={8} />
            </div>
          </div>

          {/* undo */}
          <div className="relative z-10">
            <button onClick={undo} disabled={!history.length}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white/[0.05] border border-white/[0.08] text-slate-400 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed text-[10px] font-black uppercase tracking-wider transition-all">
              <Undo2 size={12} /> Deshacer
            </button>
          </div>

          {/* error */}
          {error && (
            <div className="absolute bottom-6 left-6 right-6 bg-red-950/70 border border-red-500/30 text-red-200 text-xs font-bold rounded-xl p-3 text-center z-20">
              ⚠️ {error}
            </div>
          )}
        </div>

        {/* ── PANEL DERECHO: SELECCIÓN + ACCIONES ── */}
        <div className="w-[280px] shrink-0 flex flex-col border-l border-white/[0.06]" style={{ background:'rgba(0,0,0,0.3)' }}>

          {/* selección */}
          <div className="p-4 border-b border-white/[0.06]">
            <div className="text-[9px] font-black italic tracking-[0.2em] text-slate-500 mb-3 flex items-center gap-1.5">
              <span className="text-slate-400">⌕</span> SELECCIÓN
            </div>
            {pickedCard ? (
              <div className="flex flex-col items-center gap-3">
                <div className="relative">
                  <LoteriaCard card={pickedCard} size={110} picked showQty={false} />
                  <button onClick={cancelPick}
                    className="absolute -top-2 -right-2 w-5 h-5 rounded-full bg-slate-800 border border-slate-600 text-slate-400 hover:text-white flex items-center justify-center transition-all z-20">
                    <X size={10} />
                  </button>
                </div>
                <div className="text-center">
                  <div className="text-[11px] font-black italic text-white">
                    {(pickedCard.name||'').replace(/^(EL |LA |Las |Los |El |La )/i,'')}
                  </div>
                  <div className="text-[9px] text-slate-500 mt-0.5">{pickedCard.dynamic_rarity || 'Común'}</div>
                </div>
                <p className="text-[10px] text-emerald-400/80 text-center font-semibold leading-tight">
                  {pickedFromGridIdx !== null ? 'Haz clic en otro hueco para intercambiar' : 'Haz clic en un hueco del tablero para colocarla'}
                </p>
                {pickedFromGridIdx !== null && (
                  <button onClick={() => {
                    pushHistory(grid);
                    const next = [...grid];
                    next[pickedFromGridIdx] = null;
                    setGrid(next);
                    cancelPick();
                  }}
                    className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-red-950/40 border border-red-500/30 text-red-300 hover:bg-red-950/60 text-[10px] font-black uppercase tracking-wider transition-all active:scale-95">
                    <Trash2 size={12} /> Quitar del tablero
                  </button>
                )}
              </div>
            ) : (
              <div className="flex flex-col items-center gap-2 py-4 text-center">
                <div className="text-2xl">🃏</div>
                <p className="text-[10px] text-slate-500 leading-relaxed">Haz clic en una carta de la mochila para seleccionarla</p>
              </div>
            )}
          </div>

          {/* acciones */}
          <div className="p-4 flex flex-col gap-2">
            <div className="text-[9px] font-black italic tracking-[0.2em] text-slate-500 mb-1 flex items-center gap-1.5">
              <span>⚡</span> ACCIONES
            </div>

            <button onClick={handleRandomizeEmpty} disabled={!deck.length || ready || !canCompleteBoard}
              className="flex items-center gap-2.5 px-3 py-2.5 rounded-xl bg-white/[0.04] border border-white/[0.07] hover:bg-white/[0.08] hover:border-cyan-500/30 text-left text-white disabled:opacity-30 disabled:cursor-not-allowed transition-all group">
              <Shuffle size={14} className="text-cyan-400 shrink-0" />
              <div>
                <div className="text-[10px] font-black">Aleatorizar vacíos</div>
                <div className="text-[8.5px] text-slate-500">Rellena los huecos con cartas de tu mochila</div>
              </div>
            </button>

            <button onClick={handleReflect} disabled={!filledCount}
              className="flex items-center gap-2.5 px-3 py-2.5 rounded-xl bg-white/[0.04] border border-white/[0.07] hover:bg-white/[0.08] hover:border-purple-500/30 text-left text-white disabled:opacity-30 disabled:cursor-not-allowed transition-all">
              <span className="text-[14px] shrink-0">🪞</span>
              <div>
                <div className="text-[10px] font-black">Reflejar tablero</div>
                <div className="text-[8.5px] text-slate-500">Voltea horizontalmente las cartas colocadas</div>
              </div>
            </button>

            <button onClick={handleVaciar} disabled={!filledCount}
              className="flex items-center gap-2.5 px-3 py-2.5 rounded-xl bg-white/[0.04] border border-white/[0.07] hover:bg-red-950/40 hover:border-red-500/30 text-left text-white disabled:opacity-30 disabled:cursor-not-allowed transition-all">
              <Trash2 size={14} className="text-red-400/70 shrink-0" />
              <div>
                <div className="text-[10px] font-black">Vaciar tablero</div>
                <div className="text-[8.5px] text-slate-500">Devuelve todas las cartas a la mochila</div>
              </div>
            </button>

            <div className="mt-2 px-3 py-2 rounded-lg border border-white/[0.05] bg-white/[0.02]">
              <p className="text-[9px] text-slate-600 leading-relaxed">
                <span className="text-slate-500 font-bold">Tip:</span> Haz clic en una carta de la mochila, luego en el hueco destino. Para intercambiar, haz clic en una carta del tablero.
              </p>
            </div>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes targetPulse { 0%,100%{box-shadow:0 0 0 0 rgba(52,211,153,0)} 50%{box-shadow:0 0 14px 2px rgba(52,211,153,0.4)} }
        .editor-mochila-scroll::-webkit-scrollbar{width:4px}
        .editor-mochila-scroll::-webkit-scrollbar-track{background:transparent}
        .editor-mochila-scroll::-webkit-scrollbar-thumb{background:rgba(255,255,255,0.1);border-radius:2px}
        .editor-mochila-scroll{scrollbar-width:thin;scrollbar-color:rgba(255,255,255,0.1) transparent}
        .editor-hand-scroll::-webkit-scrollbar{display:none}
        .editor-hand-scroll{scrollbar-width:none}
      `}</style>
    </div>
  );

  return (
    <>
      {mobileLayout}
      {desktopLayout}
    </>
  );
}
