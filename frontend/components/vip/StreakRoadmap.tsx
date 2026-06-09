"use client";

const STREAK_MILESTONES = [
  { months: 3, label: "Constante", emoji: "🎖️" },
  { months: 6, label: "Veterano", emoji: "🏅" },
  { months: 12, label: "Original", emoji: "🥇" },
  { months: 24, label: "Leyenda", emoji: "👑" },
];

export default function StreakRoadmap({ streakMonths }: { streakMonths: number }) {
  return (
    <div className="rounded-xl p-3.5 bg-white/5 border border-white/10">
      <p className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3">
        Hitos de racha
      </p>
      <div className="flex items-center gap-0">
        {STREAK_MILESTONES.map((m, i) => {
          const reached = streakMonths >= m.months;
          const isNext =
            !reached &&
            (i === 0 || streakMonths >= STREAK_MILESTONES[i - 1].months);
          return (
            <div key={m.months} className="flex items-center flex-1">
              <div className="flex flex-col items-center flex-1">
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center text-sm border-2 transition-all ${
                    reached
                      ? "border-yellow-400 bg-yellow-400/20"
                      : isNext
                      ? "border-yellow-400/50 bg-yellow-400/10 animate-pulse"
                      : "border-white/20 bg-white/5"
                  }`}
                >
                  {reached ? (
                    m.emoji
                  ) : (
                    <span className="text-gray-600 text-xs font-bold">
                      {m.months}m
                    </span>
                  )}
                </div>
                <p
                  className={`text-[10px] font-bold mt-1 leading-tight text-center ${
                    reached
                      ? "text-yellow-400"
                      : isNext
                      ? "text-gray-400"
                      : "text-gray-600"
                  }`}
                  style={{ fontSize: "11px" }}
                >
                  {m.label}
                </p>
              </div>
              {i < STREAK_MILESTONES.length - 1 && (
                <div
                  className={`h-0.5 flex-1 -mt-4 ${
                    streakMonths > m.months ? "bg-yellow-400/60" : "bg-white/10"
                  }`}
                />
              )}
            </div>
          );
        })}
      </div>
      {streakMonths > 0 && (
        <p className="text-xs text-gray-400 mt-2.5">
          Llevas{" "}
          <span className="text-yellow-400 font-bold">
            {streakMonths} {streakMonths === 1 ? "mes" : "meses"}
          </span>{" "}
          de racha.
          {streakMonths < 3 && (
            <span className="text-gray-500">
              {" "}
              {3 - streakMonths} {3 - streakMonths === 1 ? "mes" : "meses"} para
              el siguiente hito.
            </span>
          )}
        </p>
      )}
    </div>
  );
}
