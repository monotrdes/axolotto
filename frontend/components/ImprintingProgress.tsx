"use client";

interface ImprintingStatus {
  incubation_id: number;
  imprinting_started: boolean;
  imprinting_complete: boolean;
  games_played: number;
  required_games: number;
  padrino_name: string | null;
  current_stats: {
    suerte_delta: number;
    ojo_delta: number;
    pila_delta: number;
    sal_delta: number;
  } | null;
}

interface Props {
  status: ImprintingStatus;
  onSelectPadrino?: () => void;
}

function DeltaChip({
  value,
  label,
}: {
  value: number;
  label: string;
}) {
  const positive = value >= 0;
  const bg = positive ? "rgba(74,222,128,0.12)" : "rgba(239,68,68,0.1)";
  const textColor = positive ? "#4ade80" : "#f87171";
  return (
    <div
      className="flex flex-col items-center gap-1 px-3 py-2 rounded-xl"
      style={{ background: bg }}
    >
      <span className="text-xs font-bold" style={{ color: textColor }}>
        {positive ? "+" : ""}
        {value}
      </span>
      <span className="text-[10px] font-semibold opacity-50">{label}</span>
    </div>
  );
}

export function ImprintingProgress({ status, onSelectPadrino }: Props) {
  const dots = Array.from({ length: status.required_games });

  if (!status.imprinting_started) {
    return (
      <div className="flex flex-col items-center gap-3 p-4 rounded-2xl bg-white/3 border border-white/8">
        <div className="text-sm font-bold text-white/60">🥚 ADN incompleto</div>
        <div className="text-xs text-white/30 text-center">
          Elige un padrino para iniciar el imprinting
        </div>
        {onSelectPadrino && (
          <button
            onClick={onSelectPadrino}
            aria-label="Elegir padrino para imprinting"
            className="px-5 py-2 rounded-xl text-xs font-bold bg-purple-400/15 border border-purple-400/30 text-purple-300"
          >
            Elegir padrino
          </button>
        )}
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-3 p-4 rounded-2xl bg-white/3 border border-white/8">
      <div className="flex items-center justify-between">
        <div className="text-xs font-bold text-white/50 uppercase tracking-widest">
          Imprinting
        </div>
        {status.padrino_name && (
          <div className="text-xs text-purple-300 font-semibold">
            🐾 Padrino: {status.padrino_name}
          </div>
        )}
      </div>

      {/* Progress dots */}
      <div className="flex gap-2 justify-center">
        {dots.map((_, i) => (
          <div
            key={i}
            className="w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold border-2 transition-all"
            style={{
              background:
                i < status.games_played
                  ? "rgba(167,139,250,0.3)"
                  : "rgba(255,255,255,0.05)",
              borderColor:
                i < status.games_played
                  ? "rgba(167,139,250,0.6)"
                  : "rgba(255,255,255,0.1)",
              color:
                i < status.games_played
                  ? "#c084fc"
                  : "rgba(255,255,255,0.2)",
            }}
          >
            {i < status.games_played ? "✓" : i + 1}
          </div>
        ))}
      </div>

      <div className="text-center text-xs text-white/40">
        {status.games_played}/{status.required_games} partidas
        {status.imprinting_complete && (
          <span className="ml-2 text-green-400 font-bold">
            Listo para nacer!
          </span>
        )}
      </div>

      {/* Accumulated deltas */}
      {status.games_played > 0 && status.current_stats && (
        <div className="flex gap-2 justify-center flex-wrap">
          <DeltaChip value={status.current_stats.suerte_delta} label="SUERTE" />
          <DeltaChip value={status.current_stats.ojo_delta} label="OJO" />
          <DeltaChip value={status.current_stats.pila_delta} label="PILA" />
          <DeltaChip value={status.current_stats.sal_delta} label="SAL" />
        </div>
      )}
    </div>
  );
}
