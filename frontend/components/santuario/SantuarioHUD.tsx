interface SantuarioHUDProps {
  axfRaw: number;
  frjRaw: number;
  ticketCount?: number;
  boostActive?: boolean;
}

export default function SantuarioHUD({
  axfRaw,
  frjRaw,
  ticketCount = 0,
  boostActive = false,
}: SantuarioHUDProps) {
  const axfDisplay = Math.floor(axfRaw / 1_000_000).toLocaleString();
  const frjDisplay = Math.floor(frjRaw / 10_000).toLocaleString();

  return (
    <div className="flex items-center gap-3 px-4 py-2 bg-slate-900/95 border-b border-slate-700/60 h-12 shrink-0">
      {/* AXF balance */}
      <div className="flex items-center gap-1.5 rounded-md bg-slate-800/80 px-3 py-1 border border-amber-500/30">
        <span className="text-amber-400 text-sm">🪙</span>
        <span className="text-amber-300 text-xs font-semibold tracking-wide">$AXO</span>
        <span className="text-white text-sm font-bold tabular-nums">{axfDisplay}</span>
      </div>

      {/* FRJ balance */}
      <div className="flex items-center gap-1.5 rounded-md bg-slate-800/80 px-3 py-1 border border-teal-500/30">
        <span className="text-teal-400 text-sm">💎</span>
        <span className="text-teal-300 text-xs font-semibold tracking-wide">$MILCO</span>
        <span className="text-white text-sm font-bold tabular-nums">{frjDisplay}</span>
      </div>

      {/* Ticket count */}
      <div className="flex items-center gap-1.5 rounded-md bg-slate-800/80 px-3 py-1 border border-slate-600/50">
        <span className="text-sm">🎫</span>
        <span className="text-white text-sm font-bold tabular-nums">{ticketCount}</span>
      </div>

      {/* Spacer */}
      <div className="flex-1" />

      {/* Boost indicator */}
      <div
        className={`flex items-center justify-center rounded-md px-3 py-1 border transition-colors ${
          boostActive
            ? "bg-yellow-500/20 border-yellow-400/60 shadow-[0_0_8px_rgba(234,179,8,0.4)]"
            : "bg-slate-800/80 border-slate-600/40 opacity-40"
        }`}
      >
        <span
          className={`text-sm ${boostActive ? "text-yellow-300" : "text-slate-400"}`}
        >
          ⚡
        </span>
      </div>
    </div>
  );
}
