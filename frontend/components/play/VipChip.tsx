"use client";
import { VIP_TIER_CONFIG } from '@/constants/play';

interface VipChipProps {
  vipTier?: string | null;
  daysRemaining?: number | null;
  pendingGal?: number;
  onClick: () => void;
}

export default function VipChip({ vipTier, daysRemaining, pendingGal, onClick }: VipChipProps) {
  const cfg = vipTier ? VIP_TIER_CONFIG[vipTier] : null;
  const isUrgent = daysRemaining != null && daysRemaining <= 5;
  const hasClaim = (pendingGal ?? 0) > 0;

  if (!cfg) {
    // No VIP — shimmer invite chip
    return (
      <button
        onClick={onClick}
        title="Beneficios exclusivos para miembros VIP 👑"
        className="relative flex items-center gap-1 px-2 py-1.5 rounded-full overflow-hidden border border-yellow-400/30 text-yellow-300 font-black text-[10px] tracking-widest transition-all hover:scale-105 active:scale-95"
        style={{ background: "linear-gradient(135deg, #1a1000, #2a1a00)" }}
      >
        <span
          className="absolute inset-0 opacity-0 hover:opacity-100 transition-opacity duration-300"
          style={{ background: "linear-gradient(105deg, transparent 40%, rgba(251,191,36,0.15) 50%, transparent 60%)", backgroundSize: "200% 100%", animation: "shimmer-vip 2s linear infinite" }}
        />
        <span>👑</span>
        <span className="hidden sm:inline">VIP</span>
        <span className="text-yellow-500">›</span>
      </button>
    );
  }

  // VIP activo
  const borderColor = isUrgent ? "#EF4444" : hasClaim ? cfg.color : cfg.color + "66";
  const bgColor = isUrgent ? "rgba(239,68,68,0.12)" : "rgba(0,0,0,0.4)";

  return (
    <button
      onClick={onClick}
      className="flex items-center gap-1 px-2 py-1.5 rounded-full font-black text-[10px] tracking-wide transition-all hover:scale-105 active:scale-95"
      style={{
        border: `1px solid ${borderColor}`,
        background: bgColor,
        color: isUrgent ? "#EF4444" : cfg.color,
        boxShadow: hasClaim ? `0 0 10px ${cfg.glow}` : "none",
        animation: hasClaim ? "pulse 2s ease-in-out infinite" : isUrgent ? "pulse 1.5s ease-in-out infinite" : "none",
      }}
    >
      <span>{cfg.emoji}</span>
      <span className="hidden sm:inline">{cfg.label}</span>
      {hasClaim ? (
        <span className="text-amber-400 font-black">· {pendingGal!.toFixed(0)} FRJ</span>
      ) : (
        <span>{isUrgent ? `⚠️ ${daysRemaining}d` : `${daysRemaining}d`}</span>
      )}
    </button>
  );
}
