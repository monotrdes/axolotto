"use client";
import { Crown, X } from "lucide-react";
import { VIP_PRESENTATION } from "@/lib/vip";
import type { VipNotification } from "@/types/vip";
import { useVip } from "@/hooks/useVip";
import ModeA from "@/components/vip/ModeA";
import ModeB from "@/components/vip/ModeB";
import TierBadge from "@/components/vip/TierBadge";

// Re-export for backward compatibility (used by app/play/page.tsx and ToastContext.tsx)
export type { VipNotification };

interface VipModalProps {
  isOpen: boolean;
  onClose: () => void;
  token: string | null;
  userId: string;
  balances: Record<string, number> | null;
  recargarSaldos: () => Promise<void>;
  onVipSuccess?: (notif: VipNotification) => void;
}

export default function VipModal({
  isOpen,
  onClose,
  token,
  userId,
  balances,
  recargarSaldos,
  onVipSuccess,
}: VipModalProps) {
  const vip = useVip({
    isOpen,
    token,
    userId,
    recargarSaldos,
    onVipSuccess,
  });

  if (!isOpen) return null;

  // ── Datos derivados ──
  const activeTier = vip.vipStatus?.is_vip
    ? vip.tiers.find((t) => t.id === vip.vipStatus?.vip_tier) ?? null
    : null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/70 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative z-10 w-full max-w-lg max-h-[92vh] overflow-y-auto rounded-2xl bg-[#0A0A1A] border border-white/10 shadow-2xl">
        {/* Header sticky */}
        <div className="sticky top-0 z-10 flex items-center justify-between px-5 pt-5 pb-3 bg-[#0A0A1A] border-b border-white/5">
          <div className="flex items-center gap-2">
            <Crown size={18} className="text-yellow-400" />
            <span className="font-black text-base text-white tracking-tight">
              VIP CLUB
            </span>
            {activeTier && <TierBadge tierId={activeTier.id} />}
          </div>
          <button
            onClick={onClose}
            aria-label="Cerrar panel VIP"
            className="flex items-center justify-center w-11 h-11 rounded-full text-gray-500 hover:text-white hover:bg-white/10 transition-all"
          >
            <X size={18} />
          </button>
        </div>

        <div className="px-5 pb-6 space-y-5 mt-4">
          {/* ═══ MODO EXITO ═══ */}
          {vip.purchaseSuccess ? (
            <div className="py-8 text-center space-y-3">
              <div className="text-5xl">🎉</div>
              <p className="text-xl font-black text-white">
                Bienvenido al VIP Club!
              </p>
              <p className="text-sm text-gray-400">
                Tu suscripcion ya esta activa. Revisa tus beneficios.
              </p>
              <button
                onClick={() => {
                  vip.setPurchaseSuccess(false);
                  vip.fetchVipStatus();
                }}
                className="mt-2 px-6 py-3 rounded-xl bg-yellow-500 hover:bg-yellow-400 text-slate-950 font-black text-sm transition-all min-h-[44px]"
              >
                Ver mi dashboard VIP →
              </button>
            </div>
          ) : vip.vipStatus?.is_vip ? (
            /* ═══ MODO B: VIP ACTIVO ═══ */
            <ModeB
              vipStatus={vip.vipStatus}
              tiers={vip.tiers}
              balances={balances}
              mainAxolotito={vip.mainAxolotito}
              claiming={vip.claiming}
              claimSuccess={vip.claimSuccess}
              purchasing={vip.purchasing}
              autoRenew={vip.autoRenew}
              togglingAutoRenew={vip.togglingAutoRenew}
              expandedUpgradeTier={vip.expandedUpgradeTier}
              setExpandedUpgradeTier={vip.setExpandedUpgradeTier}
              onClaimGal={vip.handleClaimGal}
              onPurchase={vip.handlePurchase}
              onToggleAutoRenew={vip.handleToggleAutoRenew}
            />
          ) : (
            /* ═══ MODO A: VENTAS ═══ */
            <ModeA
              tiers={vip.tiers}
              tiersLoading={vip.tiersLoading}
              tiersError={vip.tiersError}
              onRetry={vip.loadTiers}
              selectedTierId={vip.selectedTierId}
              setSelectedTierId={vip.setSelectedTierId}
              activeVipCount={vip.activeVipCount}
              balances={balances}
              purchasing={vip.purchasing}
              onPurchase={vip.handlePurchase}
            />
          )}

          {/* Error global */}
          {vip.error && (
            <div className="rounded-xl p-3 bg-red-900/30 border border-red-500/30 text-sm text-red-400 font-medium">
              {vip.error}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
