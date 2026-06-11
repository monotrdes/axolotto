"use client";
import type { VipTier, VipPresentation } from "@/lib/vip";
import { VIP_PRESENTATION, getTierBenefits } from "@/lib/vip";
import type { VipStatus } from "@/types/vip";
import { Star } from "lucide-react";
import { API_BASE } from "@/lib/api";
import BenefitRow from "./BenefitRow";
import TierBadge from "./TierBadge";
import StreakRoadmap from "./StreakRoadmap";
import UpgradePanel from "./UpgradePanel";
import HoldButton from "@/components/ui/HoldButton";
import type { HoldButtonProps } from "@/components/ui/HoldButton";

const TIER_VARIANT: Record<string, HoldButtonProps["variant"]> = {
  coral: "teal",
  dorado: "amber",
  axolite: "primary",
};

const API = `${API_BASE}`;

const TIER_ORDER: Record<string, number> = {
  coral: 1,
  dorado: 2,
  axolite: 3,
};

interface ModeBProps {
  vipStatus: VipStatus;
  tiers: VipTier[];
  balances: Record<string, number> | null;
  mainAxolotito: Record<string, unknown> | null;
  claiming: boolean;
  claimSuccess: boolean;
  purchasing: boolean;
  autoRenew: boolean;
  togglingAutoRenew: boolean;
  expandedUpgradeTier: string | null;
  setExpandedUpgradeTier: (v: string | null) => void;
  onClaimFrj: () => void;
  onPurchase: (tierId: string) => void;
  onToggleAutoRenew: () => void;
}

/**
 * Modo B — Dashboard VIP activo: claim diario, suscripcion, beneficios,
 * auto-renovacion, upgrade de nivel e historial.
 */
export default function ModeB({
  vipStatus,
  tiers,
  balances,
  mainAxolotito,
  claiming,
  claimSuccess,
  purchasing,
  autoRenew,
  togglingAutoRenew,
  expandedUpgradeTier,
  setExpandedUpgradeTier,
  onClaimFrj,
  onPurchase,
  onToggleAutoRenew,
}: ModeBProps) {
  const activeTier = tiers.find((t) => t.id === vipStatus.vip_tier) ?? null;
  const activePres = activeTier ? VIP_PRESENTATION[activeTier.id] : null;

  if (!activeTier || !activePres) {
    return (
      <div className="py-8 text-center">
        <p className="text-sm text-gray-400">No se encontro informacion del tier activo.</p>
      </div>
    );
  }

  const activeBenefits = getTierBenefits(activeTier);
  const daysRemaining = vipStatus?.days_remaining ?? 0;
  const expiresDate = vipStatus?.vip_expires_at
    ? new Date(vipStatus.vip_expires_at).toLocaleDateString("es-MX", {
        day: "numeric",
        month: "short",
        year: "numeric",
      })
    : null;
  const progressPct = Math.round((daysRemaining / 30) * 100);
  const isUrgent = daysRemaining <= 5;

  const currentTierId = vipStatus.vip_tier ?? "";

  return (
    <>
      {/* 1. CLAIM DIARIO */}
      {vipStatus.vip_pending_gal > 0 ? (
        <div
          className="rounded-xl p-4 border"
          style={{
            background:
              "linear-gradient(135deg, rgba(245,158,11,0.12), transparent)",
            borderColor: "rgba(245,158,11,0.35)",
            boxShadow: claimSuccess
              ? "none"
              : "0 0 16px rgba(245,158,11,0.25)",
          }}
        >
          <div className="flex items-center justify-between gap-3">
            <div>
              <p className="text-sm font-bold text-white">
                Frijolitos Diarios
              </p>
              <p className="text-[10px] text-amber-400/90 font-semibold">
                {vipStatus.vip_pending_gal.toFixed(0)} FRJ disponibles. Expira a la medianoche UTC si no se reclama.
              </p>
            </div>
            <button
              onClick={onClaimFrj}
              disabled={claiming}
              className="px-4 py-2.5 rounded-xl bg-amber-500 hover:bg-amber-400 disabled:opacity-50 text-slate-950 font-black text-sm transition-all active:scale-95 min-h-[44px]"
              style={{
                boxShadow: claiming
                  ? "none"
                  : "0 0 16px rgba(245,158,11,0.5)",
              }}
            >
              {claiming
                ? "..."
                : claimSuccess
                ? "Reclamado!"
                : `+${vipStatus.vip_pending_gal.toFixed(0)} FRJ`}
            </button>
          </div>
          {claimSuccess && (
            <p className="text-xs text-amber-400 font-bold mt-2">
              FRJ anadidos a tu cartera
            </p>
          )}
        </div>
      ) : (
        <div className="rounded-xl p-4 bg-white/5 border border-white/10">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-bold text-white">
                Frijolitos Diarios
              </p>
              <p className="text-xs text-gray-400">
                Ya reclamaste el dia de hoy
              </p>
            </div>
            <span className="text-xs text-gray-600 font-bold">Reclamado</span>
          </div>
        </div>
      )}

      {/* 2. Axolotito principal con marco */}
      {mainAxolotito ? (
        <div className="flex flex-col items-center justify-center p-4 bg-white/5 rounded-2xl border border-white/10">
          <p className="text-xs text-gray-400 font-bold uppercase tracking-wider mb-2">
            Axolotito Principal
          </p>
          <div className="relative w-20 h-20 flex items-center justify-center">
            <div
              className={`absolute inset-0 pointer-events-none vip-frame-${vipStatus.vip_tier}`}
            />
            <img
              src={`${API}/metadata/axolotito/${mainAxolotito.blockchain_token_id as string}.svg`}
              alt={mainAxolotito.name as string}
              className="w-16 h-16 object-contain animate-axo-bob"
            />
          </div>
          <p className="text-sm font-black text-white mt-2 flex items-center gap-1.5">
            {mainAxolotito.name as string}
            <span className="text-xs text-gray-500 font-mono">
              #{mainAxolotito.blockchain_token_id as string}
            </span>
          </p>
        </div>
      ) : (
        <div className="p-4 bg-white/5 rounded-2xl border border-white/10 text-center">
          <p className="text-xs text-gray-400">
            No tienes un Axolotito Principal designado.
          </p>
          <p className="text-xs text-gray-500 mt-1">
            Visita El Nido para designarlo.
          </p>
        </div>
      )}

      {/* 3. Suscripcion activa + renovar */}
      <div
        className="rounded-xl p-4 border"
        style={{
          background: `linear-gradient(135deg, ${activePres.color}15, transparent)`,
          borderColor: activePres.color + "33",
        }}
      >
        <div className="flex items-center justify-between mb-3">
          <div>
            <p className="text-xs text-gray-400 font-medium">
              Suscripcion activa
            </p>
            <p className="text-sm font-bold text-white">
              Vence el{" "}
              <span style={{ color: activePres.color }}>{expiresDate}</span>
            </p>
          </div>
          <div className="text-right">
            <p
              className="text-2xl font-black"
              style={{ color: isUrgent ? "#EF4444" : activePres.color }}
            >
              {daysRemaining}d
            </p>
            <p className="text-xs text-gray-500">restantes</p>
          </div>
        </div>

        {/* Barra de progreso */}
        <div className="w-full h-1.5 bg-white/10 rounded-full overflow-hidden mb-2">
          <div
            className="h-full rounded-full transition-all duration-700"
            style={{
              width: `${progressPct}%`,
              background: isUrgent
                ? "linear-gradient(90deg, #EF4444, #F97316)"
                : `linear-gradient(90deg, ${activePres.color}, ${activePres.color}99)`,
            }}
          />
        </div>

        {isUrgent && (
          <p className="text-xs text-amber-400 font-bold mb-2">
            Tu suscripcion esta por vencer
          </p>
        )}

        {/* Racha */}
        {(vipStatus.vip_streak_months ?? 0) > 0 && (
          <div className="flex items-center gap-1.5 mt-2">
            <Star size={12} style={{ color: activePres.color }} />
            <span className="text-xs text-gray-300 font-medium">
              {vipStatus.vip_streak_months}{" "}
              {vipStatus.vip_streak_months === 1 ? "mes" : "meses"} de racha
            </span>
          </div>
        )}

        {/* Boton de renovacion — hold para confirmar */}
        <HoldButton
          className="w-full mt-3"
          variant={TIER_VARIANT[activeTier.id] ?? "primary"}
          disabled={purchasing || (balances?.axofichas ?? 0) < activeTier.price_axf}
          onConfirm={() => onPurchase(activeTier.id)}
          label={purchasing ? "Procesando..." : `Renovar ${activePres.label} — ${activeTier.price_axf} AXF`}
          sublabel="Manten presionado para renovar"
        />
        {(balances?.axofichas ?? 0) < activeTier.price_axf && (
          <p className="text-xs text-amber-400 mt-1.5">
            Saldo AXF insuficiente para renovar
          </p>
        )}
      </div>

      {/* 4. Beneficios activos */}
      <div>
        <p className="text-xs text-gray-500 font-bold uppercase tracking-wider mb-2">
          Tus beneficios activos
        </p>
        <div className="grid grid-cols-2 gap-1.5">
          {activeBenefits.map((b, i) => (
            <BenefitRow
              key={i}
              icon={b.icon}
              label={b.label}
              tooltip={b.tooltip}
            />
          ))}
        </div>
      </div>

      {/* 5. Roadmap de hitos */}
      <StreakRoadmap streakMonths={vipStatus.vip_streak_months ?? 0} />

      {/* 6. Auto-renovacion */}
      <div className="flex items-center justify-between rounded-xl p-3.5 bg-white/5 border border-white/10">
        <div className="flex-1 min-w-0 mr-3">
          <p className="text-sm font-bold text-white">Auto-renovacion</p>
          <p className="text-xs text-gray-400">
            {autoRenew
              ? `Se cobrara ${activeTier.price_axf} AXF ~3 dias antes de vencer`
              : "Renueva manualmente cada mes"}
          </p>
          {autoRenew &&
            (balances?.axofichas ?? 0) < activeTier.price_axf && (
              <p className="text-xs text-amber-400 mt-0.5">
                Saldo AXF insuficiente para la proxima auto-renovacion
              </p>
            )}
        </div>
        <button
          onClick={onToggleAutoRenew}
          disabled={togglingAutoRenew}
          aria-label={
            autoRenew
              ? "Desactivar auto-renovacion"
              : "Activar auto-renovacion"
          }
          aria-checked={autoRenew}
          role="switch"
          className="relative shrink-0 min-w-[44px] min-h-[44px] flex items-center justify-center"
        >
          <span
            className={`relative w-11 h-6 rounded-full transition-colors duration-200 ${
              autoRenew ? "bg-green-500" : "bg-gray-700"
            }`}
          >
            <span
              className={`absolute top-0.5 left-0.5 w-5 h-5 rounded-full bg-white shadow transition-transform duration-200 ${
                autoRenew ? "translate-x-5" : "translate-x-0"
              }`}
            />
          </span>
        </button>
      </div>

      {/* 7. Subir de nivel */}
      <UpgradePanel
        tiers={tiers}
        currentTierId={currentTierId}
        balances={balances}
        purchasing={purchasing}
        expandedUpgradeTier={expandedUpgradeTier}
        setExpandedUpgradeTier={setExpandedUpgradeTier}
        onPurchase={onPurchase}
        TIER_ORDER={TIER_ORDER}
      />

      {/* 8. Historial de tiers */}
      {vipStatus.vip_tiers_activated?.length > 0 && (
        <div>
          <p className="text-xs text-gray-500 font-bold uppercase tracking-wider mb-2">
            Historial de tiers
          </p>
          <div className="flex gap-2 flex-wrap">
            {vipStatus.vip_tiers_activated.map((t) => (
              <TierBadge key={t} tierId={t} size="xs" />
            ))}
          </div>
        </div>
      )}
    </>
  );
}
