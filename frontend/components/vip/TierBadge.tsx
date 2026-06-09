"use client";
import { VIP_PRESENTATION } from "@/lib/vip";

/**
 * Badge de tier reutilizable en header, historial, etc.
 */
export default function TierBadge({
  tierId,
  size = "sm",
}: {
  tierId: string;
  size?: "sm" | "xs";
}) {
  const pres = VIP_PRESENTATION[tierId];
  if (!pres) return null;
  const textSize = size === "xs" ? "text-[10px]" : "text-xs";
  return (
    <span
      className={`${textSize} font-bold px-2 py-0.5 rounded-full`}
      style={{
        background: pres.color + "22",
        color: pres.color,
        border: `1px solid ${pres.color}44`,
      }}
    >
      {pres.emoji} {pres.label.toUpperCase()}
    </span>
  );
}
