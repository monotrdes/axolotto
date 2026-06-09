"use client";
import { useEffect, useState } from "react";

interface EventInfo {
  id: number;
  name: string;
  start_date: string;
  end_date: string;
  daily_open_time: string | null;
  daily_close_time: string | null;
  bonus_gal_on_win: number;
  drop_multiplier: number;
}

interface ManualModeStatus {
  active_event: EventInfo | null;
  next_event: EventInfo | null;
}

interface Props {
  onPlay: () => void;
}

export function ManualModeButton({ onPlay }: Props) {
  const [status, setStatus] = useState<ManualModeStatus | null>(null);
  const [timeLeft, setTimeLeft] = useState<string>("");

  useEffect(() => {
    fetch("/api/v1/events/manual-mode")
      .then((r) => r.json())
      .then(setStatus)
      .catch(() => setStatus({ active_event: null, next_event: null }));
  }, []);

  // Countdown to next event
  useEffect(() => {
    if (!status?.next_event) return;
    const interval = setInterval(() => {
      const target = new Date(
        `${status.next_event!.start_date}T${status.next_event!.daily_open_time ?? "00:00:00"}`
      );
      const diff = target.getTime() - Date.now();
      if (diff <= 0) {
        setTimeLeft("¡Abriendo!");
        clearInterval(interval);
        return;
      }
      const d = Math.floor(diff / 86400000);
      const h = Math.floor((diff % 86400000) / 3600000);
      const m = Math.floor((diff % 3600000) / 60000);
      setTimeLeft(d > 0 ? `${d}d ${h}h` : `${h}h ${m}m`);
    }, 1000);
    return () => clearInterval(interval);
  }, [status?.next_event]);

  if (!status) {
    return (
      <button
        disabled
        className="opacity-40 px-6 py-3 rounded-2xl bg-white/5 text-white/30 font-bold text-sm"
      >
        Cargando...
      </button>
    );
  }

  const { active_event, next_event } = status;

  if (active_event) {
    return (
      <div className="flex flex-col items-center gap-2">
        <div className="text-xs font-bold text-green-400 uppercase tracking-widest">
          🎉 {active_event.name}
        </div>
        {active_event.bonus_gal_on_win > 0 && (
          <div className="text-xs text-yellow-400 font-semibold">
            +{active_event.bonus_gal_on_win} FRJ al ganar
            {active_event.drop_multiplier > 1 &&
              ` · ${active_event.drop_multiplier}× drops`}
          </div>
        )}
        <button
          onClick={onPlay}
          className="px-8 py-3 rounded-2xl bg-green-400/20 border border-green-400/40 text-green-400 font-bold text-sm hover:bg-green-400/30 transition-all"
        >
          Jugar modo manual →
        </button>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center gap-2">
      <button
        disabled
        className="px-8 py-3 rounded-2xl bg-white/5 border border-white/10 text-white/30 font-bold text-sm cursor-not-allowed"
      >
        🌙 Modo manual cerrado
      </button>
      {next_event ? (
        <div className="text-center">
          <div className="text-2xl font-black text-blue-400">{timeLeft}</div>
          <div className="text-xs text-white/30 mt-1">
            {next_event.name} ·{" "}
            {new Date(next_event.start_date).toLocaleDateString("es-MX", {
              month: "short",
              day: "numeric",
            })}
          </div>
        </div>
      ) : (
        <div className="text-xs text-white/25">Próximamente</div>
      )}
    </div>
  );
}
