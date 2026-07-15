"use client";
import React, { useState } from 'react';
import { createPortal } from 'react-dom';
import { X } from 'lucide-react';
import { API_BASE } from '@/lib/api';
import BoardEditor from './BoardEditor';
import { deriveBoardRarity, isBoardShiny } from '@/lib/boardRarity';
import BottomSheet from '@/components/ui/BottomSheet';
import BoardCardGrid from '@/components/ui/BoardCardGrid';
import UnboxingModal from '@/components/ui/UnboxingModal';
import HoldButton from '@/components/ui/HoldButton';
import { useInventory } from '@/hooks/useInventory';
import CardGrid from '@/components/inventory/CardGrid';
import AxolotitoCard from '@/components/inventory/AxolotitoCard';
import ItemList from '@/components/inventory/ItemList';
import type { MochilaTab } from '@/types/inventory';
import { PAPER_WORLD } from '@/lib/paperWorld';
import { useProductPolicy } from '@/hooks/useProductPolicy';

function renderPortal(content: React.ReactNode) {
  if (typeof window === 'undefined') return null;
  return createPortal(content, document.body);
}

function toRoman(n: number): string {
  const vals: [number, string][] = [[10,'X'],[9,'IX'],[5,'V'],[4,'IV'],[1,'I']];
  let result = '';
  for (const [val, sym] of vals) {
    while (n >= val) { result += sym; n -= val; }
  }
  return result;
}

export default function Inventory({
  userId,
  token,
  cambiarTab,
  mode = 'cartas',
  initialTab,
  recargarSaldos,
}: {
  userId: string;
  token: string | null;
  cambiarTab?: any;
  mode?: 'cartas' | 'axolotitos' | 'tablas';
  initialTab?: MochilaTab;
  recargarSaldos?: () => void;
}) {
  const { capabilities } = useProductPolicy();
  const passiveRewardsEnabled = capabilities.gameplay.passive_token_rewards;
  const playerMarketplaceEnabled = capabilities.commerce.player_marketplace;
  const randomRewardsEnabled = capabilities.commerce.purchased_random_rewards;
  const boardMutationsEnabled = capabilities.assets.board_mutations;
  const randomBoardCreationEnabled = boardMutationsEnabled && randomRewardsEnabled;
  const resolvedInitial: MochilaTab = initialTab ?? (mode === 'tablas' ? 'tablas' : 'cartas');
  const [activeTab, setActiveTab] = useState<MochilaTab>(resolvedInitial);

  const inv = useInventory(userId, token, mode, cambiarTab, recargarSaldos);

  const {
    ownedItems, allCards, axolotitos, playerBoards, catalogItems, slotsStatus,
    cargando, setCargando, sealedSobrecitos, cartasUnicas,
    cardRarityFilter, setCardRarityFilter, cardShinyFilter, setCardShinyFilter,
    cardOwnedFilter, setCardOwnedFilter,
    selectedAxo, setSelectedAxo, equippingSlot, equipError,
    unboxingOpen, cartasObtenidasObjects, currentOpeningPack, txHash,
    sobrecitosSheetOpen, setSobrecitosSheetOpen, cerrarModalUnboxing,
    selectedBoosterForAction, showListModal, setShowListModal,
    listQuantity, setListQuantity, listPrice, setListPrice,
    listError, listSuccess, listLoading,
    showBoardEditor, setShowBoardEditor, boardToEdit, setBoardToEdit,
    showCreateModal, setShowCreateModal, newBoardName, setNewBoardName,
    creandoAleatorio, createError, setCreateError, createSuccess, setCreateSuccess,
    desarmando, boardToDelete, setBoardToDelete, deleteConfirmName, setDeleteConfirmName,
    reclamando, boardMsg, setBoardMsg,
    showRentForm, setShowRentForm, rentFee, setRentFee, rentSplit, setRentSplit,
    listando, cancelando, unlockingSlot, reclamandoTodo, selectedBoard, setSelectedBoard,
    loadInventory, handleStartUnboxing, handleOpenSellModal, handleCreateList,
    handleEquip, handleUnequip, handleCrearAleatorio, handleUnlockSlot,
    handleClaimAllStaking, handleDesarmar, executeDesarmar,
    handleReclamarStaking, handleListarRenta, handleCancelarListado,
    getBoosterStyles, getCsrStyle, boardToNums,
  } = inv;

  // ── Loading state ──
  if (cargando) {
    return (
      <div className="text-center text-[#E4007C] animate-pulse mt-10 font-bold tracking-widest">
        BUSCANDO EN TU MOCHILA...
      </div>
    );
  }

  // ── Header info — driven by activeTab ──
  const getHeaderInfo = () => {
    switch (activeTab) {
      case 'tablas':
        return {
          title: "MIS TABLAS",
          desc: passiveRewardsEnabled
            ? "Tus tablas 4×4 de Lotería. Armadas con tus cartas, generan FRJ pasivos."
            : "Tus tablas 4×4 de Lotería para jugar, organizar y personalizar tus cartas.",
          gradient: "from-emerald-400 to-teal-500",
          shadow: "shadow-[0_0_40px_rgba(16,185,129,0.15)]",
          border: "border-emerald-500/30",
        };
      case 'cartas':
      default:
        return {
          title: `MIS CARTAS (${cartasUnicas}/54)`,
          desc: "Colecciona las 54 cartas de la Lotería Axolotto.",
          gradient: "from-indigo-400 to-[#E4007C]",
          shadow: "shadow-[0_0_40px_rgba(99,102,241,0.15)]",
          border: "border-indigo-500/30",
        };
    }
  };

  const headerInfo = getHeaderInfo();

  const TAB_DEFS: { id: MochilaTab; label: string; emoji: string; active: string; inactive: string }[] = [
    { id: 'cartas', label: 'Cartas', emoji: '🃏', active: 'bg-indigo-600 text-white', inactive: 'text-slate-400 hover:text-slate-200' },
    { id: 'tablas', label: 'Tablas', emoji: '📋', active: 'bg-emerald-600 text-white', inactive: 'text-slate-400 hover:text-slate-200' },
  ];

  // ── Computed values for tablas ──
  const totalAccrued = passiveRewardsEnabled
    ? playerBoards.reduce((sum: number, b: any) => sum + (b.accrued_staking_gal || 0), 0)
    : 0;
  const numUnlocked = slotsStatus ? Number(slotsStatus.unlocked_slots || 0) : 0;
  const numBoards = playerBoards.length;
  const emptySlotsCount = Math.max(0, numUnlocked - numBoards);

  return (
    <div
      className={
        PAPER_WORLD
          ? 'w-full mt-4 papel-panel papel-codice backdrop-blur-xl rounded-[2.5rem] p-6 sm:p-10 transition-all duration-300'
          : `w-full mt-4 bg-slate-950/80 backdrop-blur-xl rounded-[2.5rem] p-6 sm:p-10 border ${headerInfo.border} ${headerInfo.shadow} transition-all duration-300`
      }
    >

      {/* ── HEADER ── */}
      <div className="flex flex-col xl:flex-row justify-between items-start xl:items-center mb-6 gap-4">
        <div>
          <h2 className={`text-4xl sm:text-5xl font-black italic text-transparent bg-clip-text bg-gradient-to-r ${headerInfo.gradient} tracking-tighter drop-shadow-md pr-2 pb-1`}>
            {headerInfo.title}
          </h2>
          <p className="text-slate-400 text-sm mt-1">{headerInfo.desc}</p>
        </div>
      </div>

      {/* ── TAB NAV ── */}
      <div className="flex gap-2 mb-7 bg-slate-900/60 p-1.5 rounded-2xl border border-white/5 w-full max-w-xs">
        {TAB_DEFS.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex-1 py-2 rounded-xl text-xs font-black uppercase tracking-wider transition-all ${
              activeTab === tab.id ? tab.active + ' shadow-md' : tab.inactive
            }`}
          >
            {tab.emoji} {tab.label}
          </button>
        ))}
      </div>

      {/* ══════════════════════════════════════════════════════════ */}
      {/* TAB: CARTAS */}
      {/* ══════════════════════════════════════════════════════════ */}
      {activeTab === 'cartas' && (
        <>
          {/* Cartas header actions */}
          <div className="flex justify-end mb-4">
            <button
              onClick={() => cambiarTab?.('tienda')}
              className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-indigo-900/50 hover:bg-indigo-800/70 border border-indigo-500/30 hover:border-indigo-400/50 text-indigo-300 hover:text-indigo-100 text-xs font-black uppercase tracking-widest transition-all active:scale-95 shadow-[0_0_12px_rgba(99,102,241,0.15)]"
              aria-label="Ver Mercado de Cartas"
            >
              🏪 Mercado de Cartas
            </button>
          </div>
          <ItemList
            sealedSobrecitos={sealedSobrecitos}
            sobrecitosSheetOpen={sobrecitosSheetOpen}
            setSobrecitosSheetOpen={setSobrecitosSheetOpen}
            onStartUnboxing={(booster) => {
              if (randomRewardsEnabled) handleStartUnboxing(booster);
            }}
            onOpenSellModal={handleOpenSellModal}
            marketplaceEnabled={playerMarketplaceEnabled}
            randomRewardsEnabled={randomRewardsEnabled}
            getBoosterStyles={getBoosterStyles}
          />
          <CardGrid
            allCards={allCards}
            ownedItems={ownedItems}
            catalogItems={catalogItems}
            cardRarityFilter={cardRarityFilter}
            cardShinyFilter={cardShinyFilter}
            cardOwnedFilter={cardOwnedFilter}
            setCardRarityFilter={setCardRarityFilter}
            setCardShinyFilter={setCardShinyFilter}
            setCardOwnedFilter={setCardOwnedFilter}
            onOpenSellModal={handleOpenSellModal}
            marketplaceEnabled={playerMarketplaceEnabled}
            cambiarTab={cambiarTab}
          />
        </>
      )}

      {/* ══════════════════════════════════════════════════════════ */}
      {/* TAB: TABLAS */}
      {/* ══════════════════════════════════════════════════════════ */}
      {activeTab === 'tablas' && (
        <div className="animate-in fade-in duration-300">

          {/* Tablas header actions */}
          <div className="flex justify-end mb-6">
            <button
              onClick={() => cambiarTab?.('tienda')}
              className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-emerald-900/50 hover:bg-emerald-800/70 border border-emerald-500/30 hover:border-emerald-400/50 text-emerald-300 hover:text-emerald-100 text-xs font-black uppercase tracking-widest transition-all active:scale-95 shadow-[0_0_12px_rgba(16,185,129,0.15)]"
              aria-label="Ver Mercado de Tablas"
            >
              🏪 Mercado de Tablas
            </button>
          </div>

          {/* ── MIS TABLAS ── */}
          {(
            playerBoards.length === 0 && !slotsStatus ? (
              <div className="py-16 flex flex-col items-center justify-center text-center">
                <span className="text-6xl mb-4 animate-bounce">📋</span>
                <h3 className="text-xl font-black text-white uppercase tracking-tight mb-2">No tienes Tablas</h3>
                <p className="text-slate-400 text-sm max-w-sm mb-6 leading-relaxed">
                  {passiveRewardsEnabled
                    ? 'Crea tu primera tabla de Lotería para empezar a generar FRJ pasivos con tus cartas.'
                    : 'Crea tu primera tabla de Lotería para jugar y organizar tus cartas.'}
                </p>
                <div className="flex flex-wrap gap-3 justify-center">
                  <button onClick={() => { if (randomBoardCreationEnabled) { setShowCreateModal(true); setCreateError(null); } }}
                    disabled={!randomBoardCreationEnabled}
                    title={!randomBoardCreationEnabled ? 'Creación aleatoria en revisión' : undefined}
                    className="px-6 py-3 bg-slate-800 hover:bg-slate-700 border border-slate-600 hover:border-emerald-500 text-slate-200 hover:text-emerald-300 font-black rounded-xl text-xs uppercase tracking-widest transition-all active:scale-95 disabled:opacity-40 disabled:cursor-not-allowed">
                    {randomBoardCreationEnabled ? '🎲 Crear Aleatoria (25 FRJ)' : '🎲 Aleatoria · En revisión'}
                  </button>
                  <button onClick={() => { if (boardMutationsEnabled) { setBoardToEdit(null); setShowBoardEditor(true); } }}
                    disabled={!boardMutationsEnabled}
                    title={!boardMutationsEnabled ? 'Diseño de tablas en revisión' : undefined}
                    className="px-6 py-3 bg-gradient-to-r from-emerald-700 to-teal-600 hover:from-emerald-600 hover:to-teal-500 text-white font-black rounded-xl text-xs uppercase tracking-widest transition-all shadow-md active:scale-95 disabled:opacity-40 disabled:cursor-not-allowed">
                    {boardMutationsEnabled ? '🎨 Diseñar Manual (50 FRJ)' : '🎨 Diseño · En revisión'}
                  </button>
                </div>
              </div>
            ) : (
              <>
                {/* ── HUD strip ── */}
                <div className="flex flex-wrap items-center gap-2 mb-4 bg-slate-900/50 border border-white/5 rounded-2xl px-3 py-2.5">
                  {passiveRewardsEnabled && <div className="flex items-center gap-2 flex-1 min-w-0">
                    <span className="text-[10px] font-black text-amber-500 uppercase tracking-widest whitespace-nowrap">🪙 FRJ</span>
                    <span className="text-sm font-black text-white tabular-nums">{totalAccrued.toFixed(2)}</span>
                    <button
                      onClick={handleClaimAllStaking}
                      disabled={reclamandoTodo || totalAccrued <= 0}
                      className={`px-2.5 py-1 rounded-lg text-[9px] font-black uppercase tracking-wider transition-all active:scale-95 whitespace-nowrap ${
                        totalAccrued <= 0 ? 'bg-slate-800/40 text-slate-600 cursor-not-allowed' : 'bg-amber-700/80 hover:bg-amber-600 text-white'
                      }`}
                    >
                      {reclamandoTodo ? '...' : 'Cobrar todo'}
                    </button>
                  </div>}
                  {slotsStatus && (
                    <div className="flex items-center gap-2 shrink-0">
                      <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Espacios</span>
                      <span className="text-xs font-black text-slate-200">{slotsStatus.used_slots}/{slotsStatus.unlocked_slots}</span>
                    </div>
                  )}
                </div>

                {/* Global messages */}
                {createSuccess && (
                  <div className="mb-4 bg-emerald-950/60 border border-emerald-500/30 text-emerald-200 text-xs font-bold rounded-xl p-3 text-center">✅ {createSuccess}</div>
                )}
                {createError && (
                  <div className="mb-4 bg-red-950/60 border border-red-500/30 text-red-200 text-xs font-bold rounded-xl p-3 text-center">❌ {createError}</div>
                )}

                {/* ── COMPACT BOARD GRID ── */}
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                  {playerBoards.map((board: any) => {
                    const csrStyle = getCsrStyle(board.csr);
                    const xpPct = board.xp % 100;
                    return (
                      <button
                        key={board.id}
                        onClick={() => { setSelectedBoard(board); setShowRentForm(null); setBoardMsg(null); }}
                        className={`relative bg-slate-900/70 border rounded-2xl p-3 flex flex-col gap-2 text-left transition-all duration-200 hover:scale-[1.02] hover:brightness-110 active:scale-[0.98] ${csrStyle.border}`}
                      >
                        {board.is_rented && <span className="absolute top-2 right-2 w-2 h-2 rounded-full bg-amber-400 shadow-[0_0_6px_rgba(251,191,36,0.8)]" title="En renta activa" />}
                        {board.is_listed_for_rent && !board.is_rented && <span className="absolute top-2 right-2 w-2 h-2 rounded-full bg-indigo-400 shadow-[0_0_6px_rgba(129,140,248,0.8)]" title="Publicada" />}
                        {board.user_id !== userId && <span className="absolute top-2 right-2 w-2 h-2 rounded-full bg-teal-400 shadow-[0_0_6px_rgba(45,212,191,0.8)]" title="Rentada por ti" />}

                        <div className="pr-4">
                          <p className="text-[11px] font-black text-white uppercase tracking-tight truncate leading-tight">{board.name}</p>
                          <div className="flex items-center gap-1.5 mt-0.5 flex-wrap">
                            <span className="text-[8px] text-slate-500 font-bold">Nv.{board.level}</span>
                            <span className={`text-[8px] font-black px-1.5 py-px rounded border ${csrStyle.badge}`}>{board.suerte_tag}</span>
                            {board.slot_generation > 1 && (
                              <span className="text-[9px] font-black uppercase tracking-widest px-1.5 py-0.5 rounded bg-violet-900/60 text-violet-300 border border-violet-700/40 ml-1">
                                GEN {toRoman(board.slot_generation)}
                              </span>
                            )}
                          </div>
                        </div>

                        <div className="h-1 bg-slate-800 rounded-full overflow-hidden w-full">
                          <div className="h-full bg-gradient-to-r from-emerald-500 to-teal-400 rounded-full" style={{ width: `${xpPct}%` }} />
                        </div>

                        <BoardCardGrid
                          boardNums={Array(16).fill(0)}
                          cardSize={14}
                          priorityLine={(board.card_ids || []).map((id: any, i: number) => id ? i : -1).filter((i: number) => i >= 0)}
                          frameRarity={deriveBoardRarity(board.card_ids || [], allCards)}
                          isShiny={isBoardShiny(board.card_ids || [], allCards)}
                        />

                        {passiveRewardsEnabled && board.user_id === userId && board.accrued_staking_gal > 0 && (
                          <div className="flex items-center gap-1 bg-amber-950/60 border border-amber-500/20 rounded-lg px-2 py-1">
                            <span className="text-[9px] text-amber-500 font-black">🪙 {board.accrued_staking_gal} FRJ</span>
                          </div>
                        )}

                        <p className="text-[8px] text-slate-600 font-bold text-center">Toca para ver detalles</p>
                      </button>
                    );
                  })}

                  {/* Empty unlocked slots */}
                  {Array(emptySlotsCount).fill(null).map((_, idx: number) => (
                    <div
                      key={`empty-${idx}`}
                      className="bg-slate-950/30 border-2 border-dashed border-emerald-500/20 rounded-2xl p-3 flex flex-col items-center justify-center gap-2.5 min-h-[160px]"
                    >
                      <span className="text-xl select-none">✨</span>
                      <span className="text-[9px] font-black text-emerald-500/70 uppercase tracking-wide">Espacio libre</span>
                      {(slotsStatus?.slots_xp?.[numBoards + idx]?.preserved_xp ?? 0) > 0 && (
                        <span className="text-xs text-amber-400 font-mono">
                          ⚡ Nivel {slotsStatus.slots_xp[numBoards + idx].preserved_level} guardado
                        </span>
                      )}
                      <button
                        onClick={() => { if (randomBoardCreationEnabled) { setShowCreateModal(true); setCreateError(null); setCreateSuccess(null); } }}
                        disabled={!randomBoardCreationEnabled}
                        className="w-full py-1.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 hover:border-emerald-500 text-slate-300 hover:text-emerald-300 rounded-lg text-[9px] font-black uppercase tracking-wide transition-all active:scale-95 disabled:opacity-40 disabled:cursor-not-allowed"
                      >
                        {randomBoardCreationEnabled ? '🎲 Aleatoria' : '🎲 En revisión'}
                      </button>
                      <button
                        onClick={() => { if (boardMutationsEnabled) { setBoardToEdit(null); setShowBoardEditor(true); } }}
                        disabled={!boardMutationsEnabled}
                        className="w-full py-1.5 bg-emerald-800/60 hover:bg-emerald-700/80 text-emerald-200 hover:text-white rounded-lg text-[9px] font-black uppercase tracking-wide transition-all active:scale-95 border border-emerald-600/30 disabled:opacity-40 disabled:cursor-not-allowed"
                      >
                        {boardMutationsEnabled ? '🎨 Manual' : '🎨 En revisión'}
                      </button>
                    </div>
                  ))}

                  {/* Locked slot */}
                  {slotsStatus && slotsStatus.next_slot_requirements && (() => {
                    const req = slotsStatus.next_slot_requirements;
                    const canAffordGal = slotsStatus.current_gal >= req.cost_gal;
                    const metPlayed = !req.games_played_required || slotsStatus.total_games_played >= req.games_played_required;
                    const metWon = !req.games_won_required || slotsStatus.total_games_won >= req.games_won_required;
                    return (
                      <div className="bg-slate-950/30 border-2 border-dashed border-amber-500/20 rounded-2xl p-3 flex flex-col gap-2 min-h-[160px]">
                        <div className="flex items-center gap-1.5">
                          <span className="text-base select-none">🔒</span>
                          <span className="text-[10px] font-black text-amber-400/70 uppercase tracking-wide">Espacio #{req.slot_number}</span>
                        </div>
                        <div className="flex flex-col gap-1 flex-1">
                          <div className="flex items-center justify-between text-[9px] font-bold">
                            <span className="text-slate-500">🪙 FRJ</span>
                            <span className={canAffordGal ? 'text-emerald-400' : 'text-red-400'}>{req.cost_gal}</span>
                          </div>
                          {req.games_played_required > 0 && (
                            <div className="flex items-center justify-between text-[9px] font-bold">
                              <span className="text-slate-500">🎮 Partidas</span>
                              <span className={metPlayed ? 'text-emerald-400' : 'text-amber-400'}>{slotsStatus.total_games_played}/{req.games_played_required}</span>
                            </div>
                          )}
                          {req.games_won_required > 0 && (
                            <div className="flex items-center justify-between text-[9px] font-bold">
                              <span className="text-slate-500">🏆 Victorias</span>
                              <span className={metWon ? 'text-emerald-400' : 'text-amber-400'}>{slotsStatus.total_games_won}/{req.games_won_required}</span>
                            </div>
                          )}
                          {req.reasons?.length > 0 && (
                            <div className="mt-0.5 space-y-0.5">
                              {req.reasons.map((r: string, i: number) => (
                                <p key={i} className="text-[8px] text-amber-700 leading-tight">· {r}</p>
                              ))}
                            </div>
                          )}
                        </div>
                        <HoldButton
                          onConfirm={handleUnlockSlot}
                          disabled={!boardMutationsEnabled || unlockingSlot || !req.can_unlock}
                          variant="amber"
                          duration={1200}
                          className="w-full mt-auto"
                          label={!boardMutationsEnabled ? 'En revisión' : unlockingSlot ? '...' : req.can_unlock ? '🔓 Desbloquear' : 'Bloqueado'}
                          sublabel={boardMutationsEnabled && req.can_unlock ? 'Mantén pulsado' : undefined}
                          style={{ width: '100%', padding: '0.375rem 0.5rem', borderRadius: '0.5rem', fontSize: '9px' }}
                        />
                      </div>
                    );
                  })()}
                </div>

                {/* ── BOTTOM SHEET — Board Detail ── */}
                {selectedBoard && (
                  <BottomSheet
                    open={true}
                    onClose={() => { setSelectedBoard(null); setShowRentForm(null); }}
                  >
                    <div className="px-4 pb-8 pt-2 space-y-4">
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <h3 className="text-lg font-black text-white uppercase tracking-tight leading-tight">{selectedBoard.name}</h3>
                          <div className="flex items-center gap-2 mt-1 flex-wrap">
                            <span className="text-[9px] font-black text-slate-500 uppercase">Nivel {selectedBoard.level} · {selectedBoard.xp} XP</span>
                            {selectedBoard.user_id !== userId && <span className="text-[8px] bg-teal-950 border border-teal-500/30 text-teal-400 px-2 py-px rounded-full font-black uppercase">Rentada</span>}
                            {selectedBoard.is_rented && <span className="text-[8px] bg-amber-950 border border-amber-500/30 text-amber-400 px-2 py-px rounded-full font-black uppercase">En renta</span>}
                            {selectedBoard.is_listed_for_rent && !selectedBoard.is_rented && <span className="text-[8px] bg-indigo-950 border border-indigo-500/30 text-indigo-400 px-2 py-px rounded-full font-black uppercase">Publicada</span>}
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <div className={`px-2.5 py-1 rounded-xl border text-xs font-black ${getCsrStyle(selectedBoard.csr).badge}`}>{selectedBoard.suerte_tag}</div>
                          <button onClick={() => { setSelectedBoard(null); setShowRentForm(null); }} className="p-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition-all">
                            <X size={14} />
                          </button>
                        </div>
                      </div>

                      <div className="space-y-1">
                        <div className="h-1.5 bg-slate-800 rounded-full overflow-hidden">
                          <div className="h-full bg-gradient-to-r from-emerald-500 to-teal-400 rounded-full transition-all" style={{ width: `${selectedBoard.xp % 100}%` }} />
                        </div>
                        <div className="text-[8px] text-slate-600 text-right">{100 - (selectedBoard.xp % 100)} XP para nv.{selectedBoard.level + 1}</div>
                      </div>

                      <div className="grid grid-cols-3 gap-2 text-center">
                        <div className="bg-slate-900/60 rounded-xl p-2 border border-white/5">
                          <div className="text-sm font-black text-white">{selectedBoard.games_played}</div>
                          <div className="text-[8px] text-slate-500 uppercase">Jugados</div>
                        </div>
                        <div className="bg-slate-900/60 rounded-xl p-2 border border-white/5">
                          <div className="text-sm font-black text-emerald-400">{selectedBoard.games_won}</div>
                          <div className="text-[8px] text-slate-500 uppercase">Ganados</div>
                        </div>
                        <div className="bg-slate-900/60 rounded-xl p-2 border border-white/5">
                          <div className="text-sm font-black text-amber-400">{selectedBoard.win_rate}%</div>
                          <div className="text-[8px] text-slate-500 uppercase">Racha de Suerte</div>
                        </div>
                      </div>

                      <BoardCardGrid
                        boardNums={boardToNums(selectedBoard, allCards)}
                        cardSize={68}
                        frameRarity={deriveBoardRarity(selectedBoard.card_ids || [], allCards)}
                        isShiny={isBoardShiny(selectedBoard.card_ids || [], allCards)}
                      />

                      {passiveRewardsEnabled && selectedBoard.user_id === userId && (
                        <div className="bg-slate-950/60 border border-white/5 rounded-2xl p-3">
                          <div className="flex justify-between items-center mb-1">
                            <span className="text-[10px] font-black text-slate-400 uppercase tracking-wider">🪙 Frijolitos acumulados</span>
                            <span className="text-[10px] font-black text-slate-500">Generación: {selectedBoard.hourly_yield_gal} FRJ/h</span>
                          </div>
                          <div className="flex justify-between items-center">
                            <span className="text-lg font-black text-amber-500">{selectedBoard.accrued_staking_gal} FRJ</span>
                            <button
                              onClick={() => handleReclamarStaking(selectedBoard.id)}
                              disabled={reclamando === selectedBoard.id || selectedBoard.accrued_staking_gal <= 0}
                              className={`px-4 py-1.5 rounded-xl text-[10px] font-black uppercase tracking-wider transition-all active:scale-95 ${
                                selectedBoard.accrued_staking_gal <= 0 ? 'bg-slate-800 text-slate-600 cursor-not-allowed' : 'bg-amber-700 hover:bg-amber-600 text-white shadow-md'
                              }`}
                            >
                              {reclamando === selectedBoard.id ? '...' : '💰 Cobrar'}
                            </button>
                          </div>
                        </div>
                      )}

                      {boardMsg && boardMsg.id === selectedBoard.id && (
                        <div className={`text-xs font-bold rounded-xl p-3 text-center ${boardMsg.type === 'ok' ? 'bg-emerald-950/60 border border-emerald-500/30 text-emerald-200' : 'bg-red-950/60 border border-red-500/30 text-red-200'}`}>
                          {boardMsg.msg}
                        </div>
                      )}

                      {playerMarketplaceEnabled && showRentForm === selectedBoard.id && (
                        <div className="bg-slate-950/80 border border-emerald-500/20 rounded-2xl p-4 space-y-3 animate-in fade-in duration-200">
                          <h5 className="text-xs font-black text-slate-300 uppercase tracking-widest">📢 Publicar en Mercado de Rentas</h5>
                          <p className="text-[10px] text-slate-500">Mercado actual: <span className="text-amber-500 font-bold">~10 FRJ/día</span> · <span className="text-amber-400 font-bold">~30% split</span></p>
                          <div className="grid grid-cols-2 gap-3">
                            <div>
                              <label className="block text-[9px] font-black text-slate-400 uppercase tracking-widest mb-1">Cuota FRJ/día</label>
                              <input type="number" min="0" step="0.5" value={rentFee} onChange={e => setRentFee(e.target.value)}
                                className="w-full bg-slate-900 border border-slate-700 focus:border-teal-500 rounded-xl px-3 py-2 text-xs text-white font-bold focus:outline-none" />
                            </div>
                            <div>
                              <label className="block text-[9px] font-black text-slate-400 uppercase tracking-widest mb-1">Split Owner %</label>
                              <input type="number" min="0" max="100" step="1" value={rentSplit} onChange={e => setRentSplit(e.target.value)}
                                className="w-full bg-slate-900 border border-slate-700 focus:border-amber-500 rounded-xl px-3 py-2 text-xs text-white font-bold focus:outline-none" />
                            </div>
                          </div>
                          <div className="text-[9px] text-slate-500 bg-slate-900/40 rounded-xl p-2 border border-white/5">
                            El Renter se lleva el <span className="text-white font-bold">{Math.max(0, 100 - parseInt(rentSplit || '0'))}%</span> de victorias.
                          </div>
                          <div className="flex gap-2">
                            <button onClick={() => setShowRentForm(null)} className="flex-1 py-2 bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white rounded-xl text-xs font-black uppercase tracking-wider transition-all">Cancelar</button>
                            <button onClick={() => handleListarRenta(selectedBoard.id)} disabled={listando === selectedBoard.id}
                              className="flex-1 py-2 bg-gradient-to-r from-emerald-600 to-teal-500 text-white rounded-xl text-xs font-black uppercase tracking-wider transition-all active:scale-95 disabled:opacity-50">
                              {listando === selectedBoard.id ? '...' : '📢 Publicar'}
                            </button>
                          </div>
                        </div>
                      )}

                      {selectedBoard.is_rented && selectedBoard.rent_expires_at && (
                        <div className="text-[10px] text-amber-400 bg-amber-950/40 border border-amber-500/20 rounded-xl p-2.5 text-center font-bold">
                          🔒 Bajo contrato hasta {new Date(selectedBoard.rent_expires_at).toLocaleString()}
                        </div>
                      )}

                      {selectedBoard.user_id === userId && !selectedBoard.is_rented && (
                        <div className="flex flex-wrap gap-2 w-full">
                          <button onClick={() => { if (boardMutationsEnabled) { setBoardToEdit(selectedBoard); setShowBoardEditor(true); setSelectedBoard(null); } }}
                            disabled={!boardMutationsEnabled}
                            title={!boardMutationsEnabled ? 'Edición de tablas en revisión' : undefined}
                            className="flex-1 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white rounded-xl text-[10px] font-black uppercase tracking-wider transition-all active:scale-95 border border-slate-700 disabled:opacity-40 disabled:cursor-not-allowed">
                            {boardMutationsEnabled ? '✏️ Editar' : '✏️ En revisión'}
                          </button>
                          {selectedBoard.is_tutorial ? (
                            <div className="flex-1 py-2.5 flex items-center justify-center bg-amber-950/20 text-amber-500 rounded-xl text-[10px] font-black uppercase tracking-wider border border-amber-800/30">
                              🔒 Inicial (No Transferible)
                            </div>
                          ) : (
                            <>
                              {!selectedBoard.is_listed_for_rent && playerMarketplaceEnabled ? (
                                <button onClick={() => { setShowRentForm(selectedBoard.id); setRentFee('10'); setRentSplit('30'); }}
                                  className="flex-1 py-2.5 bg-indigo-900/60 hover:bg-indigo-800/60 text-indigo-300 rounded-xl text-[10px] font-black uppercase tracking-wider transition-all active:scale-95 border border-indigo-700/50">
                                  📢 Publicar
                                </button>
                              ) : selectedBoard.is_listed_for_rent ? (
                                <button onClick={() => handleCancelarListado(selectedBoard.id)} disabled={cancelando === selectedBoard.id}
                                  className="flex-1 py-2.5 bg-orange-900/60 hover:bg-orange-800/60 text-orange-300 rounded-xl text-[10px] font-black uppercase tracking-wider transition-all active:scale-95 border border-orange-700/50 disabled:opacity-50">
                                  {cancelando === selectedBoard.id ? '...' : '❌ Retirar'}
                                </button>
                              ) : (
                                <div className="flex-1 py-2.5 flex items-center justify-center bg-slate-900/60 text-slate-500 rounded-xl text-[10px] font-black uppercase tracking-wider border border-slate-800">
                                  Rentas en pausa
                                </div>
                              )}
                              <button onClick={() => { if (boardMutationsEnabled) { handleDesarmar(selectedBoard); setSelectedBoard(null); } }} disabled={!boardMutationsEnabled || desarmando === selectedBoard.id}
                                title={!boardMutationsEnabled ? 'Desarmado de tablas en revisión' : undefined}
                                className="py-2.5 px-3 bg-red-950/40 hover:bg-red-900/40 text-red-400 hover:text-red-200 rounded-xl text-[10px] font-black uppercase tracking-wider transition-all active:scale-95 border border-red-800/30 disabled:opacity-50">
                                {desarmando === selectedBoard.id ? '...' : '🗑️'}
                              </button>
                            </>
                          )}
                        </div>
                      )}
                    </div>
                  </BottomSheet>
                )}
              </>
            )
          )}
        </div>
      )}

      {/* ══════════════════════════════════════════════════════════ */}
      {/* MODAL: CREAR ALEATORIA */}
      {/* ══════════════════════════════════════════════════════════ */}
      {randomBoardCreationEnabled && showCreateModal && renderPortal(
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/90 backdrop-blur-md p-4 animate-in fade-in duration-200">
          <div className="bg-[#0D0D1F] border-2 border-emerald-500/50 rounded-[2.5rem] p-6 sm:p-8 max-w-sm w-full shadow-[0_0_50px_rgba(16,185,129,0.3)] flex flex-col gap-5 animate-in zoom-in-95 duration-150">
            <div>
              <h3 className="text-xl font-black italic text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-teal-500 tracking-tight">
                🎲 Tabla Aleatoria
              </h3>
              <p className="text-xs text-slate-400 mt-1">
                El sistema elegirá 16 cartas únicas disponibles de tu mochila al azar. Costo: <span className="text-amber-500 font-black">25 FRJ</span>.
              </p>
            </div>
            <div>
              <label className="block text-[9px] font-black text-slate-400 uppercase tracking-widest mb-1.5">
                Nombre de tu Tabla
              </label>
              <input
                type="text"
                value={newBoardName}
                onChange={e => setNewBoardName(e.target.value)}
                className="w-full bg-slate-900/60 border-2 border-slate-800 focus:border-emerald-500 rounded-2xl px-4 py-2.5 text-sm text-white font-black focus:outline-none focus:shadow-[0_0_15px_rgba(16,185,129,0.3)] transition-all placeholder-slate-600"
                placeholder="Ej: La Suertuda de Xochi"
              />
            </div>
            {createError && (
              <div className="bg-red-950/60 border border-red-500/30 text-red-200 text-xs font-bold rounded-xl p-3 text-center">
                ❌ {createError}
              </div>
            )}
            <div className="flex gap-3">
              <button
                onClick={() => { setShowCreateModal(false); setCreateError(null); }}
                className="flex-1 py-3 bg-slate-900/80 hover:bg-slate-800 border-2 border-slate-800 text-slate-400 hover:text-white rounded-2xl text-xs font-black uppercase tracking-widest transition-all"
              >
                Cancelar
              </button>
              <button
                onClick={handleCrearAleatorio}
                disabled={creandoAleatorio}
                className="flex-1 py-3 bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-white rounded-2xl text-xs font-black uppercase tracking-widest transition-all active:scale-95 shadow-[0_0_20px_rgba(16,185,129,0.4)] disabled:opacity-50 disabled:shadow-none"
              >
                {creandoAleatorio ? '✨ Creando...' : '✨ Crear (25 FRJ)'}
              </button>
            </div>
          </div>
        </div>,
      )}

      {/* ══════════════════════════════════════════════════════════ */}
      {/* MODAL: CONFIRMAR ELIMINACIÓN DE TABLA */}
      {/* ══════════════════════════════════════════════════════════ */}
      {boardMutationsEnabled && boardToDelete && renderPortal(
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/90 backdrop-blur-md p-4 animate-in fade-in duration-200">
          <div className="bg-[#0D0D1F] border-2 border-red-500/60 rounded-[2.5rem] p-6 sm:p-8 max-w-md w-full shadow-[0_0_50px_rgba(239,68,68,0.3)] flex flex-col gap-5 relative overflow-hidden animate-in zoom-in-95 duration-150">
            <div className="absolute top-0 left-0 right-0 h-1.5 bg-gradient-to-r from-red-500 to-orange-500" />
            <div>
              <h3 className="text-xl font-black italic text-transparent bg-clip-text bg-gradient-to-r from-red-400 to-orange-500 tracking-tight flex items-center gap-2">
                🧪 Desarmar con Solvente
              </h3>
              <p className="text-xs text-slate-400 mt-2 leading-relaxed font-medium">
                Desarmar la tabla <span className="text-white font-black">&quot;{boardToDelete.name}&quot;</span> es una acción irreversible.
              </p>
            </div>

            <div className="bg-red-950/20 border border-red-500/20 rounded-2xl p-4 space-y-2">
              <span className="text-[10px] font-black text-red-400 uppercase tracking-widest block">Costos y Consecuencias (Solvente de Pegamento):</span>
              <ul className="text-[11px] text-slate-300 space-y-1.5 list-disc list-inside font-medium leading-relaxed font-mono">
                <li><span className="text-red-400 font-bold">Costo del Solvente:</span> Te costará <span className="text-white font-bold">1 AXF</span> para despegar las cartas.</li>
                <li><span className="text-emerald-400 font-bold">Protección de Cartas:</span> Ninguna carta se destruirá.</li>
                <li><span className="text-emerald-400 font-bold">Devolución:</span> Las <span className="text-emerald-400 font-bold">16 cartas</span> volverán intactas a tu inventario.</li>
                <li><span className="text-amber-400 font-bold">XP Preservado:</span> El <span className="text-white font-bold">80% del XP</span> (Nivel {boardToDelete.level}) queda guardado en el slot para tu próxima tabla.</li>
                <li><span className="text-slate-400 font-bold">Stats en blanco:</span> La nueva tabla inicia sin historial de partidas (CSR neutro).</li>
              </ul>
            </div>

            <div className="space-y-2">
              <label className="block text-[9px] font-black text-slate-400 uppercase tracking-widest">
                Escribe exactamente el nombre de la tabla para confirmar:
              </label>
              <input
                type="text"
                value={deleteConfirmName}
                onChange={e => setDeleteConfirmName(e.target.value)}
                className="w-full bg-slate-900/60 border-2 border-slate-800 focus:border-red-500 rounded-2xl px-4 py-2.5 text-sm text-white font-black focus:outline-none focus:shadow-[0_0_15px_rgba(239,68,68,0.3)] transition-all placeholder-slate-600"
                placeholder={boardToDelete.name}
              />
            </div>

            {createError && (
              <div className="bg-red-950/60 border border-red-500/30 text-red-200 text-xs font-bold rounded-xl p-3 text-center">
                ❌ {createError}
              </div>
            )}

            <div className="flex gap-3">
              <button
                onClick={() => { setBoardToDelete(null); setDeleteConfirmName(''); setCreateError(null); }}
                className="flex-1 py-3 bg-slate-900/80 hover:bg-slate-800 border-2 border-slate-800 text-slate-400 hover:text-white rounded-2xl text-xs font-black uppercase tracking-widest transition-all"
              >
                Cancelar
              </button>
              <button
                onClick={executeDesarmar}
                disabled={desarmando === boardToDelete.id || deleteConfirmName !== boardToDelete.name}
                className={`flex-1 py-3 rounded-2xl text-xs font-black uppercase tracking-widest transition-all active:scale-95 flex items-center justify-center gap-1.5 ${
                  deleteConfirmName === boardToDelete.name
                    ? 'bg-gradient-to-r from-red-500 to-orange-500 hover:from-red-400 hover:to-orange-400 text-white shadow-[0_0_20px_rgba(239,68,68,0.4)]'
                    : 'bg-slate-900/80 text-slate-500 border-2 border-slate-850 cursor-not-allowed opacity-50'
                }`}
              >
                {desarmando === boardToDelete.id ? 'Despegando...' : '💥 Desarmar (1 AXF)'}
              </button>
            </div>
          </div>
        </div>,
      )}

      {/* ══════════════════════════════════════════════════════════ */}
      {/* EDITOR DRAG & DROP */}
      {/* ══════════════════════════════════════════════════════════ */}
      {boardMutationsEnabled && showBoardEditor && (
        <BoardEditor
          userId={userId}
          token={token}
          boardToEdit={boardToEdit}
          onClose={() => { setShowBoardEditor(false); setBoardToEdit(null); }}
          onSaved={async () => {
            setShowBoardEditor(false);
            setBoardToEdit(null);
            setCargando(true);
            setCreateSuccess(boardToEdit ? '✅ Tabla editada con éxito.' : '✅ Tabla creada con éxito.');
            await loadInventory();
          }}
          cambiarTab={cambiarTab || (() => {})}
        />
      )}

      {/* ══════════════════════════════════════════════════════════ */}
      {/* MODAL DE DETALLE DE AXOLOTITO */}
      {/* ══════════════════════════════════════════════════════════ */}
      {selectedAxo && renderPortal(
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/90 backdrop-blur-lg p-4 overflow-y-auto animate-in fade-in duration-300">
          <div className="bg-slate-950 border-4 border-purple-500/50 rounded-[3rem] p-6 sm:p-8 max-w-2xl w-full shadow-[0_0_50px_rgba(147,51,234,0.3)] my-8 relative overflow-hidden">

            <div className="absolute inset-0 bg-gradient-to-b from-purple-500/10 via-transparent to-pink-500/10 pointer-events-none"></div>

            <button
              onClick={() => setSelectedAxo(null)}
              className="absolute top-6 right-6 text-slate-400 hover:text-white text-xs font-black uppercase tracking-widest border border-slate-800 bg-slate-900 hover:bg-slate-800 px-4 py-2 rounded-xl transition-all z-20"
            >
              Cerrar
            </button>

            <div className="flex flex-col items-center relative z-10 pt-8 sm:pt-4">
              <span className="text-[10px] sm:text-xs font-black text-purple-400 uppercase tracking-widest bg-purple-950/80 px-4 py-1.5 rounded-full border border-purple-500/30 mb-2">
                DETALLE DEL AXOLOTITO
              </span>
              <h2 className="text-3xl sm:text-4xl font-black italic text-white uppercase tracking-tighter mb-4 text-center pr-2">
                {selectedAxo.name}
              </h2>

              <div className="relative w-48 h-48 sm:w-56 sm:h-56 mx-auto mb-6 bg-slate-900/60 rounded-3xl border border-white/10 flex items-center justify-center p-2 shadow-inner">
                <img
                  src={`${API_BASE}/metadata/axolotito/${selectedAxo.blockchain_token_id}.svg`}
                  alt={selectedAxo.name}
                  className="w-full h-full object-contain"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full text-left mb-6">
                <div className="bg-slate-900/50 border border-white/5 rounded-2xl p-4 sm:p-5">
                  <h3 className="text-xs font-black text-slate-400 uppercase tracking-widest mb-3 pb-1.5 border-b border-white/5 flex items-center gap-1.5">
                    🧬 Rasgos Físicos
                  </h3>
                  <div className="space-y-2">
                    {[
                      ['Color de Piel', selectedAxo.skin_color],
                      ['Tipo de Branquias', selectedAxo.gill_type],
                      ['Tipo de Ojos', selectedAxo.eye_type],
                      ['Expresión', selectedAxo.mouth_type],
                      ['Aleta de Cola', selectedAxo.tail_type],
                      ['Marca de Frente', selectedAxo.forehead_type],
                      ['Extremidades', selectedAxo.limb_type],
                    ].map(([label, val]) => (
                      <div key={label} className="flex justify-between items-center text-xs">
                        <span className="text-slate-500 font-bold">{label}:</span>
                        <span className="text-purple-300 font-black uppercase tracking-wide bg-purple-950/20 px-2 py-0.5 rounded border border-purple-500/10">
                          {val.replace(/_/g, ' ')}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="bg-slate-900/50 border border-white/5 rounded-2xl p-4 sm:p-5">
                  <h3 className="text-xs font-black text-slate-400 uppercase tracking-widest mb-3 pb-1.5 border-b border-white/5 flex items-center gap-1.5">
                    📊 Estadísticas base
                  </h3>
                  <div className="space-y-3">
                    {[
                      { label: 'SUERTE ✨', val: selectedAxo.stat_luck, color: 'bg-amber-400', max: 100, inverted: false },
                      { label: 'OJO 👁️', val: selectedAxo.stat_focus, color: 'bg-teal-400', max: 100, inverted: false },
                      { label: 'PILA 🔋', val: selectedAxo.stat_stamina, color: 'bg-blue-400', max: 200, inverted: false },
                      { label: 'SAL 🧂', val: selectedAxo.stat_salinity, color: 'bg-red-500', max: 100, inverted: true },
                    ].map(({ label, val, color, max, inverted }) => (
                      <div key={label} className="space-y-1">
                        <div className="flex justify-between text-[10px] font-bold">
                          <span className="text-slate-400">{label}{inverted && <span className="ml-1 text-[9px] text-red-400">↓ mejor</span>}</span>
                          <span className={inverted ? 'text-red-400 font-black' : 'text-white font-black'}>{typeof val === 'number' ? val.toFixed(1) : val}</span>
                        </div>
                        <div className="h-2 bg-black rounded-full overflow-hidden">
                          <div className={`h-full ${color} transition-all`} style={{ width: `${(val / max) * 100}%` }} />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* 🛡️ ARMERÍA Y ACCESORIOS */}
              <div className="w-full bg-slate-900/40 border border-white/5 rounded-3xl p-5 text-left space-y-4 mb-6">
                <h3 className="text-xs font-black text-slate-400 uppercase tracking-widest pb-2 border-b border-white/5 flex items-center gap-2">
                  🛡️ Armería de Accesorios
                </h3>

                {equipError && (
                  <div className="p-3 bg-red-950/40 border border-red-500/20 text-red-200 text-xs rounded-xl text-center">
                    ⚠️ {equipError}
                  </div>
                )}

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  {['head', 'eyes', 'body'].map((slot) => {
                    const slotName = slot === 'head' ? 'Cabeza 👑' : slot === 'eyes' ? 'Ojos 🕶️' : 'Cuerpo 👕';
                    const equippedId = slot === 'head'
                      ? selectedAxo.equipped_head_item_id
                      : slot === 'eyes'
                        ? selectedAxo.equipped_eyes_item_id
                        : selectedAxo.equipped_body_item_id;

                    const equippedItem = equippedId ? catalogItems.find((item: any) => item.id === equippedId) : null;
                    const availableItems = ownedItems.filter((item: any) =>
                      item.item_type === 'ACCESSORY' &&
                      item.item_metadata?.slot === slot &&
                      item.quantity > 0,
                    );
                    const isSlotLoading = equippingSlot === slot;

                    return (
                      <div key={slot} className="bg-slate-950/80 border border-white/5 rounded-2xl p-4 flex flex-col justify-between min-h-[160px] relative overflow-hidden">
                        <div>
                          <div className="text-[10px] font-black text-slate-500 uppercase tracking-wider mb-2">{slotName}</div>
                          {equippedItem ? (
                            <div className="space-y-2">
                              <div className="text-xs font-black text-teal-400 uppercase tracking-tight line-clamp-1">{equippedItem.name}</div>
                              <div className="text-[10px] text-slate-400 leading-tight line-clamp-2">{equippedItem.description}</div>
                              <div className="text-[9px] font-mono text-emerald-400 space-y-0.5">
                                {Object.entries(equippedItem.item_metadata || {}).map(([key, val]: [string, any]) => {
                                  if (key.startsWith('bonus_') && typeof val === 'number') {
                                    const statName = key.replace('bonus_', '');
                                    return (
                                      <div key={key} className="flex justify-between">
                                        <span className="capitalize">{statName}:</span>
                                        <span>+{val}</span>
                                      </div>
                                    );
                                  }
                                  return null;
                                })}
                              </div>
                            </div>
                          ) : (
                            <div className="space-y-2 py-2">
                              <div className="text-[10px] text-slate-600 font-bold italic">Vacío</div>
                              {availableItems.length > 0 ? (
                                <select
                                  onChange={(e) => {
                                    const val = e.target.value;
                                    if (val) handleEquip(selectedAxo.id, parseInt(val), slot);
                                  }}
                                  disabled={isSlotLoading || !token}
                                  className="w-full bg-slate-900 border border-white/10 rounded-lg p-1.5 text-[10px] text-slate-300 font-bold focus:outline-none focus:border-teal-500"
                                  value=""
                                >
                                  <option value="">➕ Equipar...</option>
                                  {availableItems.map((item: any) => (
                                    <option key={item.id} value={item.id}>{item.name} ({item.quantity})</option>
                                  ))}
                                </select>
                              ) : (
                                <div className="text-[9px] text-slate-600 leading-tight">Sin accesorios en mochila</div>
                              )}
                            </div>
                          )}
                        </div>
                        {equippedItem && (
                          <button
                            onClick={() => handleUnequip(selectedAxo.id, slot)}
                            disabled={isSlotLoading || !token}
                            className="mt-3 w-full py-1 bg-slate-900 hover:bg-red-950/20 hover:border-red-500/30 text-slate-400 hover:text-red-400 border border-white/5 rounded-lg text-[9px] font-black uppercase tracking-wider transition-all"
                          >
                            {isSlotLoading ? 'Desequipando...' : 'Desequipar'}
                          </button>
                        )}
                        {isSlotLoading && (
                          <div className="absolute inset-0 bg-black/60 backdrop-blur-[1px] flex items-center justify-center">
                            <span className="w-4 h-4 border-2 border-teal-500 border-t-transparent rounded-full animate-spin" />
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>

              <div className="w-full bg-slate-900 border border-white/5 rounded-2xl p-4 text-xs font-mono break-all text-left">
                <div className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1.5">
                  🔗 Transacción de acuñación (Polygon Amoy)
                </div>
                <div className="text-slate-400 select-all text-[10px] sm:text-xs">
                  {selectedAxo.blockchain_token_id ? `Acuñado con Token ID #${selectedAxo.blockchain_token_id}` : "No acuñado"}
                </div>
                <div className="text-[10px] font-black text-slate-500 uppercase tracking-widest mt-2 mb-1.5">
                  🧬 Secuencia de ADN (DNA Packed)
                </div>
                <div className="text-[#FF8DA1] select-all text-xs font-bold font-mono">
                  {selectedAxo.dna_sequence}
                </div>
              </div>
            </div>
          </div>
        </div>,
      )}

      {/* ══════════════════════════════════════════════════════════ */}
      {/* MODAL: LISTAR ITEM EN MERCADO P2P */}
      {/* ══════════════════════════════════════════════════════════ */}
      {playerMarketplaceEnabled && showListModal && selectedBoosterForAction && renderPortal(
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-md p-4"
          onClick={(e) => { if (e.target === e.currentTarget && !listLoading) setShowListModal(false); }}>
          <div className="bg-[#0D0D1F] border-2 border-pink-500/50 rounded-[2.5rem] p-6 w-full max-w-sm flex flex-col gap-4 animate-in zoom-in-95 duration-150 shadow-[0_0_50px_rgba(244,63,94,0.25)]">
            <div className="flex justify-between items-start border-b border-white/5 pb-3">
              <div>
                <p className="text-[9px] font-black text-pink-400 uppercase tracking-widest">Publicar en Mercado P2P</p>
                <h4 className="text-white font-black text-sm mt-0.5">{selectedBoosterForAction.label}</h4>
              </div>
              <button onClick={() => !listLoading && setShowListModal(false)} className="text-slate-500 hover:text-white transition-colors">
                <X size={16} />
              </button>
            </div>

            {listSuccess ? (
              <div className="bg-emerald-950/60 border border-emerald-500/30 text-emerald-200 text-xs font-bold rounded-xl p-3 text-center">
                ✅ Publicación creada con éxito. Descontado de tu inventario.
              </div>
            ) : (
              <>
                <div className="flex flex-col gap-3">
                  {selectedBoosterForAction.maxQty > 1 && (
                    <div className="flex flex-col gap-1">
                      <label className="text-[9px] font-black text-slate-500 uppercase tracking-wider">Cantidad (Max: {selectedBoosterForAction.maxQty})</label>
                      <input
                        type="number"
                        min={1}
                        max={selectedBoosterForAction.maxQty}
                        value={listQuantity}
                        onChange={e => setListQuantity(Math.min(selectedBoosterForAction.maxQty, Math.max(1, parseInt(e.target.value) || 1)))}
                        className="w-full bg-slate-900/60 border-2 border-slate-800 focus:border-pink-500 rounded-2xl px-4 py-2.5 text-sm text-white font-black focus:outline-none focus:shadow-[0_0_15px_rgba(244,63,94,0.3)] transition-all placeholder-slate-600"
                      />
                    </div>
                  )}
                  <div className="flex flex-col gap-1">
                    <label className="text-[9px] font-black text-slate-500 uppercase tracking-wider">Precio de venta (FRJ)</label>
                    <div className="relative">
                      <span className="absolute left-4 top-3 text-xs">🪙</span>
                      <input
                        type="number"
                        min={1}
                        value={listPrice}
                        onChange={e => setListPrice(Math.max(1, parseInt(e.target.value) || 0))}
                        className="w-full bg-slate-900/60 border-2 border-slate-800 focus:border-pink-500 rounded-2xl pl-10 pr-4 py-2.5 text-sm text-white font-black focus:outline-none focus:shadow-[0_0_15px_rgba(244,63,94,0.3)] transition-all placeholder-slate-600"
                      />
                    </div>
                  </div>
                </div>

                {listError && (
                  <div className="text-red-400 bg-red-950/60 border border-red-500/30 rounded-xl p-2.5 text-center text-[10px] font-bold">
                    {listError}
                  </div>
                )}

                <div className="flex gap-2 mt-2">
                  <button
                    disabled={listLoading}
                    onClick={() => setShowListModal(false)}
                    className="flex-1 py-3 rounded-2xl bg-slate-900/80 hover:bg-slate-800 border-2 border-slate-800 text-slate-400 hover:text-white font-black text-xs uppercase tracking-wider transition-all"
                  >
                    Cancelar
                  </button>
                  <button
                    disabled={listLoading}
                    onClick={handleCreateList}
                    className="flex-1 py-3 rounded-2xl bg-gradient-to-r from-pink-500 to-rose-500 hover:from-pink-400 hover:to-rose-400 text-white font-black text-xs uppercase tracking-wider transition-all active:scale-95 shadow-[0_0_20px_rgba(244,63,94,0.4)] disabled:opacity-50 disabled:shadow-none"
                  >
                    {listLoading ? "Publicando..." : "Publicar"}
                  </button>
                </div>
              </>
            )}
          </div>
        </div>,
      )}

      {/* ══════════════════════════════════════════════════════════ */}
      {/* UNBOXING MODAL */}
      {/* ══════════════════════════════════════════════════════════ */}
      <UnboxingModal
        open={unboxingOpen}
        onClose={cerrarModalUnboxing}
        pack={currentOpeningPack}
        cards={cartasObtenidasObjects}
        txHash={txHash}
        ownedCardIds={new Set(ownedItems.filter((i: any) => i.item_type === 'card').map((i: any) => i.id))}
      />

    </div>
  );
}
