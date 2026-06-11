"use client";
import { useState, useEffect, useCallback } from "react";
import type { VipTier } from "@/lib/vip";
import type { VipStatus, VipNotification } from "@/types/vip";
import {
  fetchVipTiers,
  fetchVipStats,
  fetchVipStatusAPI,
  fetchMainAxolotitoAPI,
  toggleAutoRenewAPI,
  purchaseVIPAPI,
  claimDailyFrjAPI,
} from "@/services/vipService";

// ═══════════════════════════════════════════════════════
// HOOK — useVip
// ═══════════════════════════════════════════════════════

export interface UseVipParams {
  isOpen: boolean;
  token: string | null;
  userId: string;
  recargarSaldos: () => Promise<void>;
  onVipSuccess?: (notif: VipNotification) => void;
}

export interface UseVipReturn {
  // State
  tiers: VipTier[];
  tiersLoading: boolean;
  tiersError: boolean;
  activeVipCount: number | null;
  vipStatus: VipStatus | null;
  mainAxolotito: Record<string, unknown> | null;
  purchasing: boolean;
  purchaseSuccess: boolean;
  claiming: boolean;
  claimSuccess: boolean;
  selectedTierId: string;
  autoRenew: boolean;
  togglingAutoRenew: boolean;
  expandedUpgradeTier: string | null;
  error: string | null;

  // Setters
  setSelectedTierId: (id: string) => void;
  setExpandedUpgradeTier: (v: string | null) => void;
  setPurchaseSuccess: (v: boolean) => void;
  setClaimSuccess: (v: boolean) => void;
  setError: (v: string | null) => void;

  // Actions
  loadTiers: () => Promise<void>;
  loadStats: () => Promise<void>;
  fetchVipStatus: () => Promise<void>;
  handleToggleAutoRenew: () => Promise<void>;
  handlePurchase: (tierId: string) => Promise<void>;
  handleClaimFrj: () => Promise<void>;
}

export function useVip({
  isOpen,
  token,
  userId,
  recargarSaldos,
  onVipSuccess,
}: UseVipParams): UseVipReturn {
  // ── Estado de tiers ──
  const [tiers, setTiers] = useState<VipTier[]>([]);
  const [tiersLoading, setTiersLoading] = useState(false);
  const [tiersError, setTiersError] = useState(false);

  // ── Prueba social ──
  const [activeVipCount, setActiveVipCount] = useState<number | null>(null);

  // ── Estado de usuario VIP ──
  const [vipStatus, setVipStatus] = useState<VipStatus | null>(null);
  const [mainAxolotito, setMainAxolotito] = useState<Record<string, unknown> | null>(null);

  // ── Flujo de compra ──
  const [purchasing, setPurchasing] = useState(false);
  const [purchaseSuccess, setPurchaseSuccess] = useState(false);

  // ── Claim diario ──
  const [claiming, setClaiming] = useState(false);
  const [claimSuccess, setClaimSuccess] = useState(false);

  // ── Tab activo ──
  const [selectedTierId, setSelectedTierId] = useState<string>("");

  // ── Auto-renovacion ──
  const [autoRenew, setAutoRenew] = useState(false);
  const [togglingAutoRenew, setTogglingAutoRenew] = useState(false);

  // ── Acordeon de upgrade ──
  const [expandedUpgradeTier, setExpandedUpgradeTier] = useState<string | null>(null);

  // ── Error global ──
  const [error, setError] = useState<string | null>(null);

  // ── Fetchers ──

  const loadTiers = useCallback(async () => {
    setTiersLoading(true);
    setTiersError(false);
    try {
      const data = await fetchVipTiers();
      setTiers(data);
      const popular = data.find((t) => t.popular) ?? data[0];
      if (popular) setSelectedTierId(popular.id);
    } catch {
      setTiersError(true);
    } finally {
      setTiersLoading(false);
    }
  }, []);

  const loadStats = useCallback(async () => {
    try {
      const stats = await fetchVipStats();
      setActiveVipCount(stats.active_vip_count > 0 ? stats.active_vip_count : null);
    } catch {
      setActiveVipCount(null);
    }
  }, []);

  const fetchVipStatus = useCallback(async () => {
    if (!token) return;
    const status = await fetchVipStatusAPI(token);
    if (status) setVipStatus(status);
  }, [token]);

  const fetchMain = useCallback(async () => {
    if (!token || !userId) return;
    const main = await fetchMainAxolotitoAPI(token, userId);
    if (main) setMainAxolotito(main);
  }, [token, userId]);

  // ── Effects ──

  useEffect(() => {
    if (isOpen) {
      loadTiers();
      loadStats();
      fetchVipStatus();
      fetchMain();
      setError(null);
      setPurchaseSuccess(false);
      setClaimSuccess(false);
      setExpandedUpgradeTier(null);
    }
  }, [isOpen, loadTiers, loadStats, fetchVipStatus, fetchMain]);

  useEffect(() => {
    if (vipStatus) {
      setAutoRenew((vipStatus as Record<string, unknown> & VipStatus).vip_auto_renew as boolean ?? false);
    }
  }, [vipStatus]);

  // ── Handlers ──

  const handleToggleAutoRenew = useCallback(async () => {
    setTogglingAutoRenew(true);
    try {
      const ok = await toggleAutoRenewAPI(token, !autoRenew);
      if (ok) setAutoRenew((prev) => !prev);
    } finally {
      setTogglingAutoRenew(false);
    }
  }, [token, autoRenew]);

  const handlePurchase = useCallback(
    async (tierId: string) => {
      setPurchasing(true);
      setError(null);
      try {
        const result = await purchaseVIPAPI(token, userId, tierId);
        if (!result.success) {
          setError(result.error ?? "Error al procesar la compra.");
          return;
        }

        setPurchaseSuccess(true);
        await recargarSaldos();
        await fetchVipStatus();
        onVipSuccess?.({
          id: Date.now(),
          type: "activation",
          tier: tierId,
          welcome_gal: (result.data?.welcome_gal_bonus as number) ?? 0,
          is_first_activation: !!result.data?.welcome_gal_bonus,
        });
      } catch {
        setError("Error de conexion.");
      } finally {
        setPurchasing(false);
      }
    },
    [token, userId, recargarSaldos, fetchVipStatus, onVipSuccess]
  );

  const handleClaimFrj = useCallback(async () => {
    setClaiming(true);
    setError(null);
    try {
      const result = await claimDailyFrjAPI(token);
      if (!result.success) {
        setError(result.error ?? "Error al reclamar.");
        return;
      }
      const claimedAmount = vipStatus?.vip_pending_gal ?? 0;
      setClaimSuccess(true);
      await recargarSaldos();
      await fetchVipStatus();
      onVipSuccess?.({
        id: Date.now(),
        type: "claim",
        claimed_gal: claimedAmount,
      });
      setTimeout(() => setClaimSuccess(false), 3000);
    } catch {
      setError("Error de conexion.");
    } finally {
      setClaiming(false);
    }
  }, [token, vipStatus, recargarSaldos, fetchVipStatus, onVipSuccess]);

  return {
    tiers,
    tiersLoading,
    tiersError,
    activeVipCount,
    vipStatus,
    mainAxolotito,
    purchasing,
    purchaseSuccess,
    claiming,
    claimSuccess,
    selectedTierId,
    autoRenew,
    togglingAutoRenew,
    expandedUpgradeTier,
    error,
    setSelectedTierId,
    setExpandedUpgradeTier,
    setPurchaseSuccess,
    setClaimSuccess,
    setError,
    loadTiers,
    loadStats,
    fetchVipStatus,
    handleToggleAutoRenew,
    handlePurchase,
    handleClaimFrj,
  };
}
