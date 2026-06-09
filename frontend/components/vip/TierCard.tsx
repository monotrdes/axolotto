"use client";
import type { VipTier } from "@/lib/vip";
import { VIP_PRESENTATION, getTierBenefits, calcRoiAxf } from "@/lib/vip";
import BenefitRow from "./BenefitRow";
import HoldButton from "@/components/ui/HoldButton";
import type { HoldButtonProps } from "@/components/ui/HoldButton";

const TIER_VARIANT: Record<string, HoldButtonProps["variant"]> = {
  coral: "teal",
  dorado: "amber",
  axolite: "primary",
};

interface TierCardProps {
  tier: VipTier;
  balances: Record<string, number> | null;
  purchasing: boolean;
  onPurchase: (tierId: string) => void;
}

/**
 * Tarjeta de tier individual — muestra precio, ROI, beneficios y CTA.
 * Usada en el modo ventas (ModeA).
 */
export default function TierCard({
  tier,
  balances,
  purchasing,
  onPurchase,
}: TierCardProps) {
  const pres = VIP_PRESENTATION[tier.id];
  if (!pres) return null;

  const roiAxf = calcRoiAxf(tier.frj_monthly);
  const benefits = getTierBenefits(tier);
  const hasEnoughBalance = (balances?.axofichas ?? 0) >= tier.price_axf;

  return (
    <div
      className={`rounded-2xl border bg-gradient-to-b ${pres.gradient} ${pres.border} transition-all duration-200`}
      style={tier.popular ? { boxShadow: `0 0 24px ${pres.glow}` } : {}}
    >
      <div className="p-4 space-y-3">
        {/* Cabecera del tier */}
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-1.5">
              <span className="text-xl">{pres.emoji}</span>
              <span className="font-black text-white text-base uppercase">
                {pres.label}
              </span>
              {tier.popular && (
                <span className="text-[11px] font-black px-1.5 py-0.5 rounded-full bg-yellow-500/20 text-yellow-400">
                  MAS POPULAR
                </span>
              )}
            </div>
          </div>
          <div className="text-right">
            <p className="text-2xl font-black" style={{ color: pres.color }}>
              {tier.price_axf}
            </p>
            <p className="text-xs text-gray-500 font-bold">AXF / mes</p>
          </div>
        </div>

        {/* Anclaje de ROI */}
        <div
          className="rounded-xl px-3 py-2.5"
          style={{
            background: pres.color + "12",
            border: `1px solid ${pres.color}30`,
          }}
        >
          <p className="text-xs font-black" style={{ color: pres.color }}>
            +{tier.frj_monthly.toLocaleString("es-MX")} FRJ/mes
          </p>
          <p className="text-xs text-gray-400">
            {" "}
            {roiAxf.toLocaleString("es-MX")} AXF de valor mensual{" "}
            <span className="text-gray-600">
              (por {tier.price_axf} AXF invertidos)
            </span>
          </p>
        </div>

        {/* Bono de bienvenida */}
        {tier.welcome_frj > 0 && (
          <div
            className="flex items-center gap-2.5 rounded-xl px-3 py-2.5"
            style={{
              background: "rgba(251,191,36,0.08)",
              border: "1px solid rgba(251,191,36,0.25)",
            }}
          >
            <span className="text-xl">🎁</span>
            <div>
              <p className="text-xs font-black text-yellow-300">
                +{tier.welcome_frj} FRJ de bienvenida
              </p>
              <p className="text-xs text-gray-500">
                Solo en tu primer mes de este nivel
              </p>
            </div>
          </div>
        )}

        {/* Lista de beneficios */}
        <div className="grid grid-cols-2 gap-1.5">
          {benefits.map((b, i) => (
            <BenefitRow key={i} icon={b.icon} label={b.label} tooltip={b.tooltip} />
          ))}
        </div>

        {/* Advertencia de saldo */}
        {!hasEnoughBalance && (
          <p className="text-xs text-amber-400">
            Te faltan{" "}
            {tier.price_axf - (balances?.axofichas ?? 0)} AXF para activar
          </p>
        )}

        {/* CTA — hold para confirmar */}
        <HoldButton
          className="w-full"
          variant={TIER_VARIANT[tier.id] ?? "primary"}
          disabled={purchasing || !hasEnoughBalance}
          onConfirm={() => onPurchase(tier.id)}
          label={purchasing ? "Procesando..." : `Activar ${pres.label} — ${tier.price_axf} AXF`}
          sublabel="Manten presionado para confirmar"
        />
      </div>
    </div>
  );
}
