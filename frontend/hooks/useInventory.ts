"use client";
import { useState, useEffect, useCallback } from 'react';
import { useToast } from '@/context/ToastContext';
import {
  fetchInventory, fetchCardsCatalog, fetchAxolotitos, fetchShopItems,
  fetchPlayerBoards, fetchSlotsStatus, openBooster, listInventoryItem,
  equipAccessory, unequipAccessory, createRandomBoard, unlockNewSlot,
  claimAllStaking, deleteBoard, claimBoardStaking, listBoardForRent, cancelRentalListing,
} from '@/services/inventoryService';
import type { CardRarityFilter, CardShinyFilter, CardOwnedFilter, InventoryMode } from '@/types/inventory';

export function useInventory(
  userId: string,
  token: string | null,
  mode: InventoryMode = 'cartas',
  cambiarTab?: any,
  recargarSaldos?: () => void,
) {
  const { toast } = useToast();

  // ── Data states ────────────────────────────────────────────
  const [ownedItems, setOwnedItems] = useState<any[]>([]);
  const [allCards, setAllCards] = useState<any[]>([]);
  const [axolotitos, setAxolotitos] = useState<any[]>([]);
  const [playerBoards, setPlayerBoards] = useState<any[]>([]);
  const [cargando, setCargando] = useState(true);
  const [catalogItems, setCatalogItems] = useState<any[]>([]);
  const [slotsStatus, setSlotsStatus] = useState<any>(null);

  // ── Filter states ──────────────────────────────────────────
  const [cardRarityFilter, setCardRarityFilter] = useState<CardRarityFilter>('all');
  const [cardShinyFilter, setCardShinyFilter] = useState<CardShinyFilter>('all');
  const [cardOwnedFilter, setCardOwnedFilter] = useState<CardOwnedFilter>('all');

  // ── Axolotito interaction states ───────────────────────────
  const [selectedAxo, setSelectedAxo] = useState<any | null>(null);
  const [equippingSlot, setEquippingSlot] = useState<string | null>(null);
  const [equipError, setEquipError] = useState<string | null>(null);

  // ── Unboxing states ────────────────────────────────────────
  const [unboxingOpen, setUnboxingOpen] = useState(false);
  const [cartasObtenidasObjects, setCartasObtenidasObjects] = useState<any[]>([]);
  const [currentOpeningPack, setCurrentOpeningPack] = useState<any | null>(null);
  const [txHash, setTxHash] = useState("");
  const [sobrecitosSheetOpen, setSobrecitosSheetOpen] = useState(false);

  // ── P2P sell modal states ──────────────────────────────────
  const [selectedBoosterForAction, setSelectedBoosterForAction] = useState<any | null>(null);
  const [showListModal, setShowListModal] = useState(false);
  const [listInventoryId, setListInventoryId] = useState<number | null>(null);
  const [listQuantity, setListQuantity] = useState(1);
  const [listPrice, setListPrice] = useState(10);
  const [listError, setListError] = useState<string | null>(null);
  const [listSuccess, setListSuccess] = useState(false);
  const [listLoading, setListLoading] = useState(false);

  // ── Board management states ────────────────────────────────
  const [showBoardEditor, setShowBoardEditor] = useState(false);
  const [boardToEdit, setBoardToEdit] = useState<any | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newBoardName, setNewBoardName] = useState('Mi Tabla Aleatoria');
  const [creandoAleatorio, setCreandoAleatorio] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);
  const [createSuccess, setCreateSuccess] = useState<string | null>(null);
  const [desarmando, setDesarmando] = useState<number | null>(null);
  const [boardToDelete, setBoardToDelete] = useState<any | null>(null);
  const [deleteConfirmName, setDeleteConfirmName] = useState<string>('');
  const [reclamando, setReclamando] = useState<number | null>(null);
  const [boardMsg, setBoardMsg] = useState<{ id: number; type: 'ok' | 'err'; msg: string } | null>(null);
  const [showRentForm, setShowRentForm] = useState<number | null>(null);
  const [rentFee, setRentFee] = useState<string>('10');
  const [rentSplit, setRentSplit] = useState<string>('30');
  const [listando, setListando] = useState<number | null>(null);
  const [cancelando, setCancelando] = useState<number | null>(null);
  const [unlockingSlot, setUnlockingSlot] = useState(false);
  const [reclamandoTodo, setReclamandoTodo] = useState(false);
  const [selectedBoard, setSelectedBoard] = useState<any | null>(null);

  // ── Derived data ───────────────────────────────────────────
  const sealedSobrecitos = ownedItems.filter(
    (i) => i.item_type?.toUpperCase() === 'BOOSTER' && i.quantity > 0,
  );

  const cartasUnicas = new Set(
    ownedItems
      .filter((i) => i.item_type?.toLowerCase() === 'card' && i.quantity > 0)
      .map((i) => i.id),
  ).size;

  // ── loadInventory ──────────────────────────────────────────
  const loadInventory = useCallback(async () => {
    try {
      const requests: Promise<any>[] = [
        fetchInventory(userId, token),
        fetchCardsCatalog(),
        fetchAxolotitos(userId, token),
        fetchShopItems(),
      ];
      requests.push(
        fetchPlayerBoards(userId, token),
        fetchSlotsStatus(token),
      );
      const results = await Promise.all(requests);
      setOwnedItems(results[0]);
      setAllCards(results[1]);
      setAxolotitos(results[2]);
      setCatalogItems(results[3]);
      setPlayerBoards(results[4]);
      setSlotsStatus(results[5]);
      return {
        inventory: results[0],
        axolotitos: results[2],
      };
    } catch (error) {
      console.error("Error cargando inventario:", error);
      return null;
    } finally {
      setCargando(false);
    }
  }, [userId, token, mode]);

  // ── Initial load ───────────────────────────────────────────
  useEffect(() => {
    if (userId) loadInventory();
  }, [userId, token, loadInventory]);

  // ── Helper functions ───────────────────────────────────────
  const getBoosterStyles = (name: string) => {
    const n = name.toLowerCase();
    if (n.includes('foil') || n.includes('brillante')) {
      return {
        gradient: 'from-amber-600 via-yellow-400 to-amber-700',
        borderColor: 'border-yellow-300',
        glowColor: 'rgba(251,191,36,0.3)',
        cardBackSymbol: '✨',
        titleText: 'text-yellow-400 shadow-[0_0_20px_rgba(251,191,36,0.5)]',
      };
    }
    if (n.includes('fiesta')) {
      return {
        gradient: 'from-pink-600 via-rose-500 to-purple-600',
        borderColor: 'border-pink-400',
        glowColor: 'rgba(236,72,153,0.3)',
        cardBackSymbol: '🎈',
        titleText: 'text-pink-400',
      };
    }
    if (n.includes('nido')) {
      return {
        gradient: 'from-emerald-600 via-teal-500 to-cyan-600',
        borderColor: 'border-teal-400',
        glowColor: 'rgba(20,184,166,0.3)',
        cardBackSymbol: '🪺',
        titleText: 'text-teal-400',
      };
    }
    if (n.includes('cosmos')) {
      return {
        gradient: 'from-indigo-900 via-purple-700 to-pink-800',
        borderColor: 'border-purple-500',
        glowColor: 'rgba(168,85,247,0.3)',
        cardBackSymbol: '🌌',
        titleText: 'text-purple-400',
      };
    }
    return {
      gradient: 'from-slate-700 via-slate-600 to-slate-800',
      borderColor: 'border-slate-500',
      glowColor: 'rgba(148,163,184,0.15)',
      cardBackSymbol: '🎰',
      titleText: 'text-slate-400',
    };
  };

  const getCsrStyle = (csr: number) => {
    if (csr >= 35) return { border: 'border-emerald-500/50', badge: 'bg-emerald-950/80 border-emerald-500/40 text-emerald-300' };
    if (csr <= 15) return { border: 'border-orange-500/30', badge: 'bg-orange-950/80 border-orange-500/40 text-orange-300' };
    return { border: 'border-slate-700', badge: 'bg-slate-800 border-slate-600 text-slate-300' };
  };

  const boardToNums = (board: any, allCardsList: any[]): number[] => {
    return Array(16).fill(0).map((_, i) => {
      const cid = board.card_ids?.[i];
      if (!cid) return 0;
      const c = allCardsList.find(
        (ac: any) => Number(ac.id) === Number(cid) || Number(ac.item_id) === Number(cid),
      );
      return c ? (Number(c.item_metadata?.numero_loteria) || 0) : 0;
    });
  };

  // ── Handlers: Unboxing ─────────────────────────────────────
  const handleStartUnboxing = async (booster: any) => {
    if (!token) return;
    try {
      const data = await openBooster(token, booster.id);

      let matched: any[] = [];
      if (data.cards) {
        matched = data.cards;
      } else {
        const nombresCartas = (data.mensaje as string)
          .replace("¡Sobre abierto! Conseguiste: ", "")
          .split(", ");
        matched = nombresCartas.map((nombre: string) => {
          const found = allCards.find(
            (c) => c.name.toLowerCase().trim() === nombre.toLowerCase().trim(),
          );
          return found || {
            name: nombre.trim(),
            dynamic_rarity: "Común",
            item_metadata: { numero_loteria: "?" },
          };
        });
      }

      const rarityRank: Record<string, number> = {
        'Común': 1,
        'Poco Común': 2,
        'Rara': 3,
        'Épica': 4,
        'Legendaria': 5,
      };
      matched.sort((a: any, b: any) => {
        const rA = rarityRank[a.dynamic_rarity] || 1;
        const rB = rarityRank[b.dynamic_rarity] || 1;
        if (rA === rB) {
          return (a.is_shiny ? 1 : 0) - (b.is_shiny ? 1 : 0);
        }
        return rA - rB;
      });

      setCartasObtenidasObjects(matched);
      setCurrentOpeningPack(booster);
      setTxHash(data.tx_blockchain || "");
      setUnboxingOpen(true);
      setSobrecitosSheetOpen(false);

      loadInventory();
      if (recargarSaldos) recargarSaldos();
    } catch (err: any) {
      console.error("Error al abrir sobre:", err);
      toast.error(err.response?.data?.detail || "No se pudo abrir el sobre.");
    }
  };

  const cerrarModalUnboxing = () => {
    setUnboxingOpen(false);
  };

  // ── Handlers: P2P Sell ─────────────────────────────────────
  const handleOpenSellModal = (inventoryItem: any, itemName?: string) => {
    setListInventoryId(inventoryItem.inventory_id || inventoryItem.id);
    setListQuantity(1);
    setListPrice(10);
    setListError(null);
    setListSuccess(false);
    setListLoading(false);

    const name = itemName || inventoryItem.name;
    const isFE = inventoryItem.is_first_edition;
    const isShiny = inventoryItem.is_shiny;
    let label = "";
    if (inventoryItem.item_type === 'BOOSTER') {
      label = `Sobre: ${name}`;
    } else {
      let copyLabel = "Normal";
      if (isFE && isShiny) copyLabel = "1st Ed. Brillante";
      else if (isShiny) copyLabel = "Brillante";
      else if (isFE) copyLabel = "1st Edition";
      label = `Carta: ${name} (${copyLabel})`;
    }

    setSelectedBoosterForAction({
      label,
      maxQty: inventoryItem.quantity,
      rawItem: inventoryItem,
    });

    setShowListModal(true);
  };

  const handleCreateList = async () => {
    if (!token || !listInventoryId) return;
    if (listQuantity <= 0 || listQuantity > (selectedBoosterForAction?.maxQty || 1)) {
      setListError("Cantidad inválida.");
      return;
    }
    if (listPrice <= 0) {
      setListError("El precio debe ser mayor a 0 FRJ.");
      return;
    }

    setListLoading(true);
    setListError(null);
    try {
      await listInventoryItem(token, listInventoryId, listQuantity, listPrice);
      setListSuccess(true);
      setTimeout(() => {
        setShowListModal(false);
        setSelectedBoosterForAction(null);
        loadInventory();
      }, 1500);
    } catch (err: any) {
      console.error("Error al listar ítem:", err);
      setListError(err.response?.data?.detail || "No se pudo crear la publicación.");
    } finally {
      setListLoading(false);
    }
  };

  // ── Handlers: Equipment ────────────────────────────────────
  const handleEquip = async (axolotitoId: number, itemId: number, slot: string) => {
    if (!token) return;
    setEquippingSlot(slot);
    setEquipError(null);
    try {
      await equipAccessory(token, axolotitoId, itemId, slot);
      const freshData = await loadInventory();
      if (freshData?.axolotitos) {
        const updated = freshData.axolotitos.find((a: any) => a.id === axolotitoId);
        if (updated) setSelectedAxo(updated);
      }
    } catch (err: any) {
      console.error("Error al equipar accesorio:", err);
      setEquipError(err.response?.data?.detail || "No se pudo equipar el accesorio.");
    } finally {
      setEquippingSlot(null);
    }
  };

  const handleUnequip = async (axolotitoId: number, slot: string) => {
    if (!token) return;
    setEquippingSlot(slot);
    setEquipError(null);
    try {
      await unequipAccessory(token, axolotitoId, slot);
      const freshData = await loadInventory();
      if (freshData?.axolotitos) {
        const updated = freshData.axolotitos.find((a: any) => a.id === axolotitoId);
        if (updated) setSelectedAxo(updated);
      }
    } catch (err: any) {
      console.error("Error al desequipar accesorio:", err);
      setEquipError(err.response?.data?.detail || "No se pudo desequipar el accesorio.");
    } finally {
      setEquippingSlot(null);
    }
  };

  // ── Handlers: Board management ─────────────────────────────
  const handleCrearAleatorio = async () => {
    if (!token) return;
    setCreandoAleatorio(true);
    setCreateError(null);
    try {
      await createRandomBoard(token, newBoardName || 'Mi Tabla Aleatoria');
      setCreateSuccess('¡Tabla aleatoria creada con éxito!');
      setShowCreateModal(false);
      setNewBoardName('Mi Tabla Aleatoria');
      setCargando(true);
      await loadInventory();
    } catch (err: any) {
      setCreateError(err.response?.data?.detail || 'Error al crear la tabla.');
    } finally {
      setCreandoAleatorio(false);
    }
  };

  const handleUnlockSlot = async () => {
    if (!token || !slotsStatus) return;
    setUnlockingSlot(true);
    setCreateError(null);
    setCreateSuccess(null);
    try {
      const res = await unlockNewSlot(token);
      setCreateSuccess(res.mensaje);
      setCargando(true);
      await loadInventory();
    } catch (err: any) {
      setCreateError(err.response?.data?.detail || 'Error al desbloquear el espacio.');
    } finally {
      setUnlockingSlot(false);
    }
  };

  const handleClaimAllStaking = async () => {
    if (!token) return;
    setReclamandoTodo(true);
    setCreateError(null);
    setCreateSuccess(null);
    try {
      const res = await claimAllStaking(token);
      setCreateSuccess(res.mensaje);
      setCargando(true);
      await loadInventory();
    } catch (err: any) {
      setCreateError(err.response?.data?.detail || 'Error al reclamar las recompensas de todas las tablas.');
    } finally {
      setReclamandoTodo(false);
    }
  };

  const handleDesarmar = (board: any) => {
    if (board.is_rented) {
      setCreateError("No puedes desarmar una tabla que está rentada.");
      return;
    }
    if (board.is_listed_for_rent) {
      setCreateError("No puedes desarmar una tabla publicada en el mercado de rentas. Retírala primero.");
      return;
    }
    if (board.is_tutorial) {
      setCreateError("La Tabla inicial del tutorial no se puede desarmar.");
      return;
    }
    setBoardToDelete(board);
    setDeleteConfirmName('');
    setCreateError(null);
    setCreateSuccess(null);
  };

  const executeDesarmar = async () => {
    if (!boardToDelete || !token) return;
    if (deleteConfirmName.trim() !== boardToDelete.name) {
      setCreateError("El nombre ingresado no coincide.");
      return;
    }
    const boardId = boardToDelete.id;
    setDesarmando(boardId);
    setCreateError(null);
    try {
      const res = await deleteBoard(token, boardId);
      setCreateSuccess(res.mensaje || '✅ Tabla desarmada.');
      setBoardToDelete(null);
      setDeleteConfirmName('');
      setCargando(true);
      await loadInventory();
    } catch (err: any) {
      setCreateError(err.response?.data?.detail || 'Error al desarmar.');
    } finally {
      setDesarmando(null);
    }
  };

  const handleReclamarStaking = async (boardId: number) => {
    if (!token) return;
    setReclamando(boardId);
    try {
      const boardObj = playerBoards.find((b: any) => b.id === boardId);
      const accrued = boardObj ? Number(boardObj.accrued_staking_gal || 0).toFixed(2) : '0.00';

      const res = await claimBoardStaking(token, boardId);
      toast.reward(`🪙 +${accrued} FRJ`);
      setBoardMsg({ id: boardId, type: 'ok', msg: `✅ ${res.mensaje}` });
      setCargando(true);
      await loadInventory();
    } catch (err: any) {
      setBoardMsg({ id: boardId, type: 'err', msg: err.response?.data?.detail || 'Error al reclamar.' });
    } finally {
      setReclamando(null);
    }
  };

  const handleListarRenta = async (boardId: number) => {
    if (!token) return;
    const fee = parseFloat(rentFee);
    const split = parseInt(rentSplit);
    if (isNaN(fee) || fee < 0) {
      setBoardMsg({ id: boardId, type: 'err', msg: 'La cuota debe ser un número positivo.' });
      return;
    }
    if (isNaN(split) || split < 0 || split > 100) {
      setBoardMsg({ id: boardId, type: 'err', msg: 'El split debe ser entre 0 y 100.' });
      return;
    }
    setListando(boardId);
    try {
      await listBoardForRent(token, boardId, fee, split);
      setBoardMsg({ id: boardId, type: 'ok', msg: '✅ Tabla publicada en el Mercado de Rentas.' });
      setShowRentForm(null);
      setCargando(true);
      await loadInventory();
    } catch (err: any) {
      setBoardMsg({ id: boardId, type: 'err', msg: err.response?.data?.detail || 'Error al publicar.' });
    } finally {
      setListando(null);
    }
  };

  const handleCancelarListado = async (boardId: number) => {
    if (!token) return;
    setCancelando(boardId);
    try {
      await cancelRentalListing(token, boardId);
      setBoardMsg({ id: boardId, type: 'ok', msg: '✅ Tabla retirada del mercado.' });
      setCargando(true);
      await loadInventory();
    } catch (err: any) {
      setBoardMsg({ id: boardId, type: 'err', msg: err.response?.data?.detail || 'Error al cancelar.' });
    } finally {
      setCancelando(null);
    }
  };

  return {
    // Data
    ownedItems, allCards, axolotitos, playerBoards, catalogItems, slotsStatus,
    cargando, setCargando, sealedSobrecitos, cartasUnicas,

    // Filters
    cardRarityFilter, setCardRarityFilter,
    cardShinyFilter, setCardShinyFilter,
    cardOwnedFilter, setCardOwnedFilter,

    // Axolotito
    selectedAxo, setSelectedAxo, equippingSlot, equipError,

    // Unboxing
    unboxingOpen, cartasObtenidasObjects, currentOpeningPack, txHash,
    sobrecitosSheetOpen, setSobrecitosSheetOpen, cerrarModalUnboxing,

    // P2P Sell
    selectedBoosterForAction, showListModal, setShowListModal,
    listInventoryId, listQuantity, setListQuantity, listPrice, setListPrice,
    listError, listSuccess, listLoading,

    // Board
    showBoardEditor, setShowBoardEditor, boardToEdit, setBoardToEdit,
    showCreateModal, setShowCreateModal, newBoardName, setNewBoardName,
    creandoAleatorio, createError, setCreateError, createSuccess, setCreateSuccess,
    desarmando, boardToDelete, setBoardToDelete, deleteConfirmName, setDeleteConfirmName,
    reclamando, boardMsg, setBoardMsg,
    showRentForm, setShowRentForm, rentFee, setRentFee, rentSplit, setRentSplit,
    listando, cancelando, unlockingSlot, reclamandoTodo, selectedBoard, setSelectedBoard,

    // Handlers
    loadInventory,
    handleStartUnboxing,
    handleOpenSellModal, handleCreateList,
    handleEquip, handleUnequip,
    handleCrearAleatorio, handleUnlockSlot, handleClaimAllStaking,
    handleDesarmar, executeDesarmar,
    handleReclamarStaking, handleListarRenta, handleCancelarListado,

    // Helpers
    getBoosterStyles, getCsrStyle, boardToNums,
  };
}
