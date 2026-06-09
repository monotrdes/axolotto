"use client";
import type { VipTier, VipPresentation } from "@/lib/vip";
import { VIP_PRESENTATION, getTierBenefits, calcRoiAxf } from "@/lib/vip";
import { ChevronRight } from "lucide-react";
import BenefitRow from "./BenefitRow";
import HoldButton from "@/components/ui/HoldButton";
import type { HoldButtonProps } from "@/components/ui/HoldButton";

const TIER_VARIANT: Record<string, HoldButtonProps["variant"]> = {
  coral: "teal",
  dorado: "amber",
  axolite: "primary",
};

interface UpgradePanelProps {
  tiers: VipTier[];
  currentTierId: string;
  balances: Record<string, number> | null;
  purchasing: boolean;
  expandedUpgradeTier: string | null;
  setExpandedUpgradeTier: (v: string | null) => void;
  onPurchase: (tierId: string) => void;
  TIER_ORDER: Record<string, number>;
}

/**
 * Panel de upgrade — acordeon de tiers superiores al actual.
 */
export default function UpgradePanel({
  tiers,
  currentTierId,
  balances,
  purchasing,
  expandedUpgradeTier,
  setExpandedUpgradeTier,
  onPurchase,
  TIER_ORDER,
}: UpgradePanelProps) {
  const currentOrder = TIER_ORDER[currentTierId] ?? 0;
  const upgradeTiers = tiers.filter((t) => TIER_ORDER[t.id] > currentOrder);

  if (upgradeTiers.length === 0) return null;

  return (
    <div>
      <p className="text-xs text-gray-500 font-bold uppercase tracking-wider mb-3">
        Subir de nivel
      </p>
      <div className="space-y-2">
        {upgradeTiers.map((row) => {
          const rowPres = VIP_PRESENTATION[row.id];
          if (!rowPres) return null;
          const isExpanded = expandedUpgradeTier === row.id;
          const rowBenefits = getTierBenefits(row);
          const roiAxf = calcRoiAxf(row.frj_monthly);
          return (
            <div
              key={row.id}
              className="rounded-xl border overflow-hidden transition-all duration-200"
              style={{
                borderColor: isExpanded
                  ? rowPres.color + "66"
                  : rowPres.color + "33",
                boxShadow: isExpanded ? `0 0 18px ${rowPres.glow}` : "none",
              }}
            >
              {/* Header del acordeon */}
              <button
                className="w-full flex items-center justify-between px-4 py-3 transition-all min-h-[44px]"
                style={{
                  background: isExpanded ? rowPres.color + "12" : "transparent",
                }}
                onClick={() => {
                  setExpandedUpgradeTier(isExpanded ? null : row.id);
                }}
                aria-expanded={isExpanded}
              >
                <div className="flex items-center gap-2.5 text-left">
                  <span className="text-lg leading-none">{rowPres.emoji}</span>
                  <div>
                    <div className="flex items-center gap-1.5">
                      <span className="text-sm font-bold text-white">
                        {rowPres.label}
                      </span>
                      {row.popular && (
                        <span className="text-[10px] font-black px-1.5 py-0.5 rounded-full bg-yellow-500/20 text-yellow-400">
                          POPULAR
                        </span>
                      )}
                    </div>
                    {!isExpanded && (
                      <p className="text-xs text-gray-500 mt-0.5">
                        {row.price_axf} AXF/mes ·{" "}
                        <span style={{ color: rowPres.color }}>
                          Ver beneficios →
                        </span>
                      </p>
                    )}
                  </div>
                </div>
                <ChevronRight
                  size={16}
                  className="shrink-0 transition-transform duration-200"
                  style={{
                    color: isExpanded ? rowPres.color : "#6B7280",
                    transform: isExpanded ? "rotate(90deg)" : "rotate(0deg)",
                  }}
                />
              </button>

              {/* Contenido expandido */}
              {isExpanded && (
                <div
                  className="px-4 pb-4"
                  style={{ borderTop: `1px solid ${rowPres.color}22` }}
                >
                  {/* Bono de bienvenida */}
                  {row.welcome_frj > 0 && (
                    <div
                      className="flex items-center gap-2.5 rounded-lg px-3 py-2.5 mt-3 mb-3"
                      style={{
                        background: "rgba(251,191,36,0.08)",
                        border: "1px solid rgba(251,191,36,0.25)",
                      }}
                    >
                      <span className="text-xl leading-none">🎁</span>
                      <div>
                        <p className="text-xs font-black text-yellow-300">
                          +{row.welcome_frj} FRJ de bienvenida
                        </p>
                        <p className="text-xs text-gray-500">
                          Solo en tu primer mes de este nivel
                        </p>
                      </div>
                    </div>
                  )}

                  {/* ROI */}
                  <div
                    className="rounded-xl px-3 py-2.5 mt-3 mb-3"
                    style={{
                      background: rowPres.color + "12",
                      border: `1px solid ${rowPres.color}30`,
                    }}
                  >
                    <p
                      className="text-xs font-black"
                      style={{ color: rowPres.color }}
                    >
                      +{row.frj_monthly.toLocaleString("es-MX")} FRJ/mes
                    </p>
                    <p className="text-xs text-gray-400">
                      {" "}
                      {roiAxf.toLocaleString("es-MX")} AXF de valor mensual
                    </p>
                  </div>

                  {/* Beneficios */}
                  <div className="grid grid-cols-2 gap-1.5 mb-4">
                    {rowBenefits.map((b, i) => (
                      <BenefitRow
                        key={i}
                        icon={b.icon}
                        label={b.label}
                        tooltip={b.tooltip}
                      />
                    ))}
                  </div>

                  {/* Advertencia de saldo */}
                  {(balances?.axofichas ?? 0) < row.price_axf && (
                    <p className="text-xs text-amber-400 mb-2.5">
                      Te faltan{" "}
                      {row.price_axf - (balances?.axofichas || 0)} AXF para
                      activar
                    </p>
                  )}

                  {/* CTA — hold para confirmar */}
                  <HoldButton
                    className="w-full"
                    variant={TIER_VARIANT[row.id] ?? "primary"}
                    disabled={purchasing || (balances?.axofichas ?? 0) < row.price_axf}
                    onConfirm={() => onPurchase(row.id)}
                    label={purchasing ? "Procesando..." : `Activar ${rowPres.label} — ${row.price_axf} AXF`}
                    sublabel="Manten presionado para confirmar"
                  />
                  <p className="text-center text-xs text-gray-500 mt-1.5">
                    {row.price_axf} AXF / mes · Cancela cuando quieras
                  </p>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
