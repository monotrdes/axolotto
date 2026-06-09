/**
 * lib/vip.ts — Fuente unica de datos y presentacion VIP.
 *
 * Contrato del backend (GET /shop/vip/tiers):
 *   { id, price_axf, frj_daily, frj_monthly, discount, capsulas_mensuales,
 *     p2p_commission, table_bonus_slots, axolotito_bonus_slots, jackpot_bonus,
 *     multiplayer_discount, welcome_frj, welcome_boosters, popular }
 *
 * Contrato (GET /shop/vip/stats):
 *   { active_vip_count }
 */

import { API_BASE } from "@/lib/api";

// ─── Tipos del contrato ───────────────────────────────────────────────────────

export interface VipTier {
  id: string;
  price_axf: number;
  frj_daily: number;
  frj_monthly: number;
  discount: number;          // fraccion, ej. 0.12 = 12%
  capsulas_mensuales: Record<string, number>;
  p2p_commission: number;    // fraccion, ej. 0.04 = 4%
  table_bonus_slots: number;
  axolotito_bonus_slots: number;
  jackpot_bonus: number;     // fraccion, ej. 0.05 = 5%
  multiplayer_discount: number; // fraccion
  welcome_frj: number;
  welcome_boosters: string[];
  popular: boolean;
}

export interface VipStats {
  active_vip_count: number;
}

// ─── Datos de presentacion (colores, emoji, copys no numericos) ───────────────

export interface VipPresentation {
  emoji: string;
  label: string;
  color: string;
  glow: string;
  gradient: string;
  border: string;
  buttonClass: string;
  /** Copys NO numericos — cosas que no vienen del backend */
  perks: string[];
}

export const VIP_PRESENTATION: Record<string, VipPresentation> = {
  coral: {
    emoji: "🪸",
    label: "Coral",
    color: "#2DD4BF",
    glow: "rgba(45,212,191,0.4)",
    gradient: "from-teal-900/30 to-slate-900/60",
    border: "border-teal-400/40",
    buttonClass: "bg-teal-500 hover:bg-teal-400",
    perks: [
      "Acceso anticipado 12h a eventos especiales",
    ],
  },
  dorado: {
    emoji: "✨",
    label: "Dorado",
    color: "#FBBF24",
    glow: "rgba(251,191,36,0.4)",
    gradient: "from-yellow-900/30 to-slate-900/60",
    border: "border-yellow-400/50",
    buttonClass: "bg-yellow-500 hover:bg-yellow-400",
    perks: [
      "Acceso anticipado 24h a eventos especiales",
    ],
  },
  axolite: {
    emoji: "🌟",
    label: "Axolite",
    color: "#C084FC",
    glow: "rgba(192,132,252,0.4)",
    gradient: "from-purple-900/30 to-slate-900/60",
    border: "border-purple-400/50",
    buttonClass:
      "bg-gradient-to-r from-yellow-500 via-pink-500 to-purple-500 hover:opacity-90",
    perks: [
      "Nombre dorado en rankings",
      "Acceso anticipado 48h a eventos especiales",
      "Emblema Axolite exclusivo en perfil",
    ],
  },
};

// ─── Beneficio canonico ───────────────────────────────────────────────────────

export interface TierBenefit {
  icon: string;
  label: string;
  /** Si true, muestra un tooltip explicativo */
  tooltip?: string;
}

/**
 * Construye la lista canonica de beneficios de un tier.
 * Mezcla los numeros del backend con los perks de presentacion.
 * Esta es la UNICA funcion que construye la lista — Modo A, Modo B y acordeon la usan.
 */
export function getTierBenefits(tier: VipTier): TierBenefit[] {
  const pres = VIP_PRESENTATION[tier.id];
  const benefits: TierBenefit[] = [];

  // FRJ diarios
  benefits.push({ icon: "🪙", label: `+${tier.frj_daily} FRJ/dia` });

  // Descuento tienda
  if (tier.discount > 0) {
    const pct = Math.round(tier.discount * 100);
    benefits.push({ icon: "🏷️", label: `${pct}% descuento en tienda` });
  }

  // Gashapones mensuales
  const capStr = formatCapsulas(tier.capsulas_mensuales);
  if (capStr) {
    benefits.push({ icon: "🎁", label: `${capStr}/mes` });
  }

  // Comision P2P
  if (tier.p2p_commission > 0) {
    const pct = (tier.p2p_commission * 100).toFixed(tier.p2p_commission * 100 % 1 === 0 ? 0 : 1);
    benefits.push({
      icon: "🔄",
      label: `Comision P2P ${pct}%`,
      tooltip:
        "Tarifa que pagas cuando vendes cartas o tablas en el mercado entre jugadores (P2P = Player to Player).",
    });
  }

  // Slots extra de tabla
  if (tier.table_bonus_slots > 0) {
    benefits.push({
      icon: "✦",
      label: `+${tier.table_bonus_slots} slot${tier.table_bonus_slots > 1 ? "s" : ""} de tabla`,
      tooltip:
        "Ranuras adicionales para guardar tablas de loteria en tu coleccion.",
    });
  }

  // Slots extra de Axolotito
  if (tier.axolotito_bonus_slots > 0) {
    benefits.push({
      icon: "✦",
      label: `+${tier.axolotito_bonus_slots} slot${tier.axolotito_bonus_slots > 1 ? "s" : ""} de Axolotito`,
      tooltip: "Ranuras adicionales para criar mas Axolotitos en tu cueva.",
    });
  }

  // Bonus de jackpot
  if (tier.jackpot_bonus > 0) {
    const pct = Math.round(tier.jackpot_bonus * 100);
    benefits.push({
      icon: "💰",
      label: `+${pct}% bonus en jackpots`,
      tooltip:
        "Porcentaje adicional sobre el premio cuando ganas un jackpot en cualquier sala.",
    });
  }

  // Descuento multijugador
  if (tier.multiplayer_discount > 0) {
    const pct = Math.round(tier.multiplayer_discount * 100);
    benefits.push({ icon: "🎲", label: `-${pct}% en salas multijugador` });
  }

  // Perks no numericos de presentacion
  if (pres?.perks) {
    for (const perk of pres.perks) {
      benefits.push({ icon: "⭐", label: perk });
    }
  }

  return benefits;
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

export function formatCapsulas(
  capsulas: Record<string, number> | undefined
): string {
  if (!capsulas) return "";
  const labels: Record<string, string> = {
    bronce: "Bronce",
    plata: "Plata",
    oro: "Oro",
  };
  const order: Record<string, number> = { bronce: 0, plata: 1, oro: 2 };
  return Object.entries(capsulas)
    .filter(([, qty]) => (qty ?? 0) > 0)
    .sort(([a], [b]) => (order[a] ?? 99) - (order[b] ?? 99))
    .map(([key, qty]) => `${qty}x Gashapon ${labels[key] || key}`)
    .join(", ");
}

/**
 * Calcula el "valor en AXF" de los FRJ mensuales para el anclaje de ROI.
 * TODO: sustituir por tasa de cambio real cuando el backend la exponga.
 * Por ahora se usa una tasa aproximada de 4 FRJ = 1 AXF (valor de referencia del equipo).
 */
export function calcRoiAxf(frjMonthly: number): number {
  const FRJ_PER_AXF = 4; // TODO: obtener del endpoint de precios cuando exista
  return Math.round(frjMonthly / FRJ_PER_AXF);
}

// ─── Fetchers ─────────────────────────────────────────────────────────────────

export async function fetchVipTiers(): Promise<VipTier[]> {
  const res = await fetch(`${API_BASE}/shop/vip/tiers`);
  if (!res.ok) throw new Error(`fetchVipTiers: ${res.status}`);
  return res.json();
}

export async function fetchVipStats(): Promise<VipStats> {
  const res = await fetch(`${API_BASE}/shop/vip/stats`);
  if (!res.ok) throw new Error(`fetchVipStats: ${res.status}`);
  return res.json();
}
