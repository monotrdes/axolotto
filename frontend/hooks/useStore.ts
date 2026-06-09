// ═══════════════════════════════════════════════════════
// HOOK — Store (Tianguis): 30+ useState colapsados
// ═══════════════════════════════════════════════════════
import { useState, useEffect, useCallback } from 'react';
import type { StoreTab, StoreItem, AdoptionParticle, CapsuleTier } from '@/types/store';
import { useToast } from '@/context/ToastContext';
import { useUnboxing } from '@/hooks/useUnboxing';

// Service imports
import * as storeService from '@/services/storeService';
import { fetchCaveStatus } from '@/services/santuarioService';

interface UseStoreOptions {
  userId: string;
  token: string | null;
  recargarSaldos: () => void;
  cambiarTab: (tab: string) => void;
}

export function useStore({ userId, token, recargarSaldos, cambiarTab }: UseStoreOptions) {
  const { toast } = useToast();

  // ── Unboxing state machine ──
  const unboxing = useUnboxing();

  // ── Shop data ──
  const [items, setItems] = useState<StoreItem[]>([]);
  const [cargando, setCargando] = useState(true);
  const [allCards, setAllCards] = useState<any[]>([]);
  const [ownedCardIds, setOwnedCardIds] = useState<Set<number>>(new Set());

  // ── UI state: tab ──
  const [storeTab, setStoreTab] = useState<StoreTab>('official');

  // ── Drawers / Modals ──
  const [sobresDrawerAbierto, setSobresDrawerAbierto] = useState(false);
  const [webitosDrawerAbierto, setWebitosDrawerAbierto] = useState(false);
  const [suertudaOpen, setSuertudaOpen] = useState(false);
  const [cryptoCheckoutOpen, setCryptoCheckoutOpen] = useState(false);
  const [helpOpen, setHelpOpen] = useState(false);

  // ── Adoption / purchase modal ──
  const [modalAdopcionAbierto, setModalAdopcionAbierto] = useState(false);
  const [mensajeAdopcion, setMensajeAdopcion] = useState('');
  const [itemComprado, setItemComprado] = useState<any | null>(null);
  const [abrirAhoraLoading, setAbrirAhoraLoading] = useState(false);
  const [itemCompradoInventoryId, setItemCompradoInventoryId] = useState<number | null>(null);
  const [adopcionParticles, setAdopcionParticles] = useState<AdoptionParticle[]>([]);

  // ── Capsule / Gashapon ──
  const [capsuleLoading, setCapsuleLoading] = useState(false);
  const [capsuleError, setCapsuleError] = useState<string | null>(null);
  const [capsuleResult, setCapsuleResult] = useState<any | null>(null);
  const [unboxingCapsule, setUnboxingCapsule] = useState(false);
  const [capsuleFeed, setCapsuleFeed] = useState<any[]>([]);

  // ── Particles (general) ──
  const [particles, setParticles] = useState<any[]>([]);

  // ── Cenote Nidos State ──
  const [maxNidos, setMaxNidos] = useState(1);
  const [totalEggsInInventory, setTotalEggsInInventory] = useState(0);
  const [totalAxolotitosHatched, setTotalAxolotitosHatched] = useState(0);
  const [nextCaveLevel, setNextCaveLevel] = useState<any | null>(null);
  const [expandingCave, setExpandingCave] = useState(false);

  // ═══════════════════════════════════════════
  // Data fetching functions
  // ═══════════════════════════════════════════

  const fetchItems = useCallback(async () => {
    try {
      const data = await storeService.fetchShopItems(userId);
      setItems(data);
    } catch (error) {
      console.error('Error cargando la tienda:', error);
    } finally {
      setCargando(false);
    }
  }, [userId]);

  const fetchCards = useCallback(async () => {
    try {
      const data = await storeService.fetchShopCards();
      setAllCards(data);
    } catch (error) {
      console.error('Error cargando las cartas del catálogo:', error);
    }
  }, []);

  const fetchInventory = useCallback(async () => {
    if (!userId || !token) return;
    try {
      const data = await storeService.fetchUserInventory(userId, token);
      const cardIds = new Set<number>(data.map((item: any) => item.id));
      setOwnedCardIds(cardIds);

      // Contar huevos en el inventario
      const eggsCount = data.reduce((acc: number, item: any) => {
        if (item.item_type?.toLowerCase() === 'egg') {
          return acc + (item.quantity || 0);
        }
        return acc;
      }, 0);
      setTotalEggsInInventory(eggsCount);
    } catch (error) {
      console.error('Error cargando el inventario:', error);
    }
  }, [userId, token]);

  const fetchCaveNidos = useCallback(async () => {
    if (!userId || !token) return;
    try {
      const caveData = await fetchCaveStatus(userId, token);
      const level = caveData.current?.level || 1;
      const globalIncSlot = caveData.passive_bonuses?.global_incubation_slot || 0;
      setMaxNidos(level + globalIncSlot);
      setNextCaveLevel(caveData.next_level || null);
      setTotalAxolotitosHatched(caveData.axolotito_count || 0);
    } catch (error) {
      console.error('Error cargando slots de cenote:', error);
    }
  }, [userId, token]);

  const fetchCapsuleFeed = useCallback(async () => {
    try {
      const data = await storeService.fetchCapsuleFeed();
      setCapsuleFeed(data);
    } catch (e) {
      console.error('Error fetching capsule feed:', e);
    }
  }, []);

  // ═══════════════════════════════════════════
  // Initial data loading
  // ═══════════════════════════════════════════

  useEffect(() => {
    if (suertudaOpen) {
      fetchCapsuleFeed();
    }
  }, [suertudaOpen, fetchCapsuleFeed]);

  useEffect(() => {
    if (userId) {
      fetchItems();
      fetchCards();
      fetchInventory();
      fetchCaveNidos();
    }
  }, [userId, token, fetchItems, fetchCards, fetchInventory, fetchCaveNidos]);

  // Refrescar conteo de nidos/axolotitos cada vez que el drawer de webitos se abre
  useEffect(() => {
    if (webitosDrawerAbierto && userId) {
      fetchCaveNidos();
    }
  }, [webitosDrawerAbierto, userId, fetchCaveNidos]);

  // ═══════════════════════════════════════════
  // Adoption particles effect
  // ═══════════════════════════════════════════

  useEffect(() => {
    if (!modalAdopcionAbierto) {
      setAdopcionParticles([]);
      return;
    }
    const itype = itemComprado?.item_type?.toLowerCase();
    if (itype !== 'booster') {
      setAdopcionParticles([]);
      return;
    }
    const isFoil = itemComprado?.item_metadata?.pack_theme === 'foil';
    const count = isFoil ? 28 : 14;
    const foilSyms = ['✨', '💎', '🌟', '👑', '💫', '🔥', '⭐', '🌈', '🏆', '⚡'];
    const purpleSyms = ['✨', '💎', '🃏', '⚡', '🔮', '💜'];
    const foilColors = ['#fbbf24', '#f472b6', '#c084fc', '#60a5fa', '#fb923c', '#a78bfa'];
    const purpleColors = ['#a78bfa', '#818cf8', '#e879f9', '#c026d3'];
    const pts: AdoptionParticle[] = [];
    for (let i = 0; i < count; i++) {
      const syms = isFoil ? foilSyms : purpleSyms;
      const colors = isFoil ? foilColors : purpleColors;
      pts.push({
        id: i,
        content: syms[Math.floor(Math.random() * syms.length)],
        color: colors[Math.floor(Math.random() * colors.length)],
        size: Math.random() * 10 + 8,
        left: Math.random() * 100,
        delay: Math.random() * 3,
        duration: Math.random() * 2 + 2,
        drift: (Math.random() - 0.5) * 120,
        rot: Math.random() * 360,
      });
    }
    setAdopcionParticles(pts);
  }, [modalAdopcionAbierto, itemComprado]);

  // ═══════════════════════════════════════════
  // Capsule actions
  // ═══════════════════════════════════════════

  const handleRollCapsule = useCallback(
    async (tier: CapsuleTier) => {
      if (!token) return;
      setCapsuleLoading(true);
      setCapsuleError(null);
      setCapsuleResult(null);
      setUnboxingCapsule(true);
      try {
        const res = await storeService.rollCapsule(tier, token);

        setTimeout(() => {
          setCapsuleResult(res);
          setCapsuleLoading(false);
          recargarSaldos();
        }, 1500);
      } catch (error: any) {
        console.error('Error al rodar cápsula:', error);
        setCapsuleError(error.response?.data?.detail || 'No se pudo comprar la cápsula.');
        setCapsuleLoading(false);
        setUnboxingCapsule(false);
      }
    },
    [token, recargarSaldos],
  );

  const handleRollTripleSuerte = useCallback(async () => {
    if (!token) return;
    setCapsuleLoading(true);
    setCapsuleError(null);
    setCapsuleResult(null);
    setUnboxingCapsule(true);
    try {
      const res = await storeService.rollTripleSuerte(token);

      setTimeout(() => {
        setCapsuleResult(res);
        setCapsuleLoading(false);
        recargarSaldos();
      }, 1800);
    } catch (error: any) {
      console.error('Error en triple suerte:', error);
      setCapsuleError(error.response?.data?.detail || 'No se pudo comprar el combo Triple Suerte.');
      setCapsuleLoading(false);
      setUnboxingCapsule(false);
    }
  }, [token, recargarSaldos]);

  // ═══════════════════════════════════════════
  // Purchase / Unboxing actions
  // ═══════════════════════════════════════════

  const comprarItem = useCallback(
    async (itemId: number, moneda: string) => {
      const itemToBuy = items.find((i: any) => i.id === itemId);
      if (itemToBuy && itemToBuy.item_type?.toLowerCase() === 'egg') {
        if ((totalEggsInInventory + totalAxolotitosHatched) >= maxNidos) {
          toast.error("❌ Sin nidos disponibles. Tu cenote está lleno — eclosiona un webito o expande tu Cenote.");
          return;
        }
      }
      try {
        const res = await storeService.buyItem(userId, itemId, moneda, token);

        const { mensaje, tx_blockchain, tipo } = res;
        const comprado =
          items.find((i: any) => i.id === res.item_id) ||
          items.find((i: any) => i.id === itemId);
        setItemComprado(comprado);

        if (tipo === 'instant_open') {
          let matched: any[] = [];
          const nombresCartas = mensaje
            .replace('¡Sobre abierto! Conseguiste: ', '')
            .split(', ');
          if (res.cards) {
            matched = res.cards;
          } else {
            matched = nombresCartas.map((nombre: string) => {
              const found = allCards.find(
                (c) => c.name.toLowerCase().trim() === nombre.toLowerCase().trim(),
              );
              return (
                found || {
                  name: nombre.trim(),
                  dynamic_rarity: 'Común',
                  item_metadata: { numero_loteria: '?' },
                }
              );
            });
          }

          unboxing.startUnboxing(matched, comprado, tx_blockchain || '');
          recargarSaldos();
          fetchItems();
          fetchInventory();
          fetchCaveNidos();
        } else {
          setMensajeAdopcion(mensaje);
          unboxing.setTxHash(tx_blockchain || '');
          setItemCompradoInventoryId(res.inventory_item_id || null);
          setModalAdopcionAbierto(true);
          recargarSaldos();
          fetchItems();
          fetchInventory();
          fetchCaveNidos();
        }
      } catch (error: any) {
        console.error('Error completo:', error);
        const errorMsg =
          error.response?.data?.detail || 'Error de conexión con el criadero.';
        toast.error(`❌ ¡Huy! Algo salió mal: ${errorMsg}`);
      }
    },
    [userId, token, recargarSaldos, items, allCards, fetchItems, fetchInventory, fetchCaveNidos, unboxing, toast, totalEggsInInventory, totalAxolotitosHatched, maxNidos],
  );

  const expandCaveNido = useCallback(async () => {
    if (!token || expandingCave) return;
    setExpandingCave(true);
    try {
      const res = await storeService.expandCave(token);
      await fetchCaveNidos();
      await fetchItems();
      toast.ok(`¡${res.level_name || 'Cenote'} desbloqueado! Ahora tienes más nidos.`);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'No se pudo expandir el Cenote.');
    } finally {
      setExpandingCave(false);
    }
  }, [token, expandingCave, fetchCaveNidos, fetchItems, toast]);

  const abrirSobreDesdeModal = useCallback(async () => {
    if (abrirAhoraLoading || !itemComprado) return;
    setAbrirAhoraLoading(true);
    try {
      const res = await storeService.openBooster(itemComprado.id, token);

      setModalAdopcionAbierto(false);

      let matched: any[] = [];
      if (res.cards) {
        matched = res.cards;
      }

      unboxing.startUnboxing(matched, itemComprado, res.tx_blockchain || '');
      recargarSaldos();
      fetchItems();
    } catch (error: any) {
      console.error('Error abriendo sobre:', error);
      toast.error(error.response?.data?.detail || 'No se pudo abrir el sobre.');
    } finally {
      setAbrirAhoraLoading(false);
    }
  }, [
    abrirAhoraLoading,
    itemComprado,
    token,
    recargarSaldos,
    fetchItems,
    unboxing,
    toast,
  ]);

  const cerrarModalUnboxing = useCallback(
    (tabDestino?: string) => {
      unboxing.setModalAbierto(false);
      fetchInventory();
      if (tabDestino) {
        cambiarTab(tabDestino);
      }
    },
    [unboxing, fetchInventory, cambiarTab],
  );

  // ═══════════════════════════════════════════
  // Return
  // ═══════════════════════════════════════════

  return {
    // From useUnboxing
    ...unboxing,

    // Shop data
    items,
    cargando,
    allCards,
    ownedCardIds,

    // Tab
    storeTab,
    setStoreTab,

    // Drawers / Modals
    sobresDrawerAbierto,
    setSobresDrawerAbierto,
    webitosDrawerAbierto,
    setWebitosDrawerAbierto,
    suertudaOpen,
    setSuertudaOpen,
    cryptoCheckoutOpen,
    setCryptoCheckoutOpen,
    helpOpen,
    setHelpOpen,

    // Adoption modal
    modalAdopcionAbierto,
    setModalAdopcionAbierto,
    mensajeAdopcion,
    setMensajeAdopcion,
    itemComprado,
    setItemComprado,
    abrirAhoraLoading,
    setAbrirAhoraLoading,
    itemCompradoInventoryId,
    setItemCompradoInventoryId,
    adopcionParticles,
    setAdopcionParticles,

    // Capsules
    capsuleLoading,
    capsuleError,
    capsuleResult,
    unboxingCapsule,
    capsuleFeed,

    // Particles
    particles,
    setParticles,

    // Cenote slots
    maxNidos,
    totalEggsInInventory,
    totalAxolotitosHatched,
    nextCaveLevel,
    expandingCave,

    // API functions
    fetchItems,
    fetchCards,
    fetchInventory,
    fetchCapsuleFeed,

    // Actions
    handleRollCapsule,
    handleRollTripleSuerte,
    comprarItem,
    expandCaveNido,
    abrirSobreDesdeModal,
    cerrarModalUnboxing,
  };
}
