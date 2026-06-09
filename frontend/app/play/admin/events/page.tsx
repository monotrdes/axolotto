"use client";
import { useEffect, useState } from "react";
import { usePrivy } from "@privy-io/react-auth";

interface EventFormData {
  name: string;
  start_date: string;
  end_date: string;
  daily_open_time: string;
  daily_close_time: string;
  tabla_cost_gal: number;
  max_tablas_per_player: number;
  bonus_gal_on_win: number;
  drop_multiplier: number;
  xp_bonus_pct: number;
  griton_delay_ms: number;
  max_players_per_room: number;
  min_players_to_start: number;
  broadcast_message: string;
  win_condition: string;
  allowed_modes: string;
}

const EMPTY: EventFormData = {
  name: "",
  start_date: "",
  end_date: "",
  daily_open_time: "15:00",
  daily_close_time: "23:00",
  tabla_cost_gal: 10,
  max_tablas_per_player: 3,
  bonus_gal_on_win: 0,
  drop_multiplier: 1,
  xp_bonus_pct: 0,
  griton_delay_ms: 2000,
  max_players_per_room: 10,
  min_players_to_start: 2,
  broadcast_message: "",
  win_condition: "tabla_llena",
  allowed_modes: "both",
};

export default function AdminEventsPage() {
  const { getAccessToken } = usePrivy();
  const [events, setEvents] = useState<any[]>([]);
  const [form, setForm] = useState<EventFormData>(EMPTY);
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState("");

  const authHeaders = async () => ({
    "Content-Type": "application/json",
    Authorization: `Bearer ${await getAccessToken()}`,
  });

  const loadEvents = async () => {
    const res = await fetch("/api/v1/admin/events", {
      headers: await authHeaders(),
    });
    if (res.ok) setEvents(await res.json());
  };

  useEffect(() => { loadEvents(); }, []);

  const handleSave = async () => {
    setSaving(true);
    try {
      const res = await fetch("/api/v1/admin/events", {
        method: "POST",
        headers: await authHeaders(),
        body: JSON.stringify(form),
      });
      const data = await res.json();
      if (res.ok) {
        setMsg(`✅ Evento "${data.name}" creado`);
        setForm(EMPTY);
        loadEvents();
      } else {
        setMsg(`❌ ${data.detail ?? "Error al crear evento"}`);
      }
    } finally {
      setSaving(false);
    }
  };

  const handleBroadcast = async (id: number) => {
    const res = await fetch(`/api/v1/admin/events/${id}/broadcast`, {
      method: "POST",
      headers: await authHeaders(),
    });
    const data = await res.json();
    setMsg(res.ok ? `📣 ${data.mensaje}` : `❌ ${data.detail}`);
    loadEvents();
  };

  const handleCancel = async (id: number) => {
    if (!confirm("¿Cancelar este evento?")) return;
    await fetch(`/api/v1/admin/events/${id}`, {
      method: "DELETE",
      headers: await authHeaders(),
    });
    loadEvents();
  };

  const setField =
    (key: keyof EventFormData) =>
    (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
      const val =
        e.target.type === "number" ? Number(e.target.value) : e.target.value;
      setForm((prev) => ({ ...prev, [key]: val }));
    };

  return (
    <div className="max-w-3xl mx-auto p-6 text-white">
      <h1 className="text-2xl font-black mb-6">🎮 Eventos de Modo Manual</h1>

      {msg && (
        <div className="mb-4 p-3 rounded-xl bg-white/5 text-sm">{msg}</div>
      )}

      {/* CREATE FORM */}
      <div className="bg-white/3 border border-white/8 rounded-2xl p-6 mb-8">
        <h2 className="text-sm font-bold uppercase tracking-widest text-white/40 mb-4">
          Crear evento
        </h2>
        <div className="grid grid-cols-2 gap-4">
          {(
            [
              ["name", "Nombre del evento", "text", true],
              ["start_date", "Fecha inicio", "date", false],
              ["end_date", "Fecha fin", "date", false],
              ["daily_open_time", "Hora apertura", "time", false],
              ["daily_close_time", "Hora cierre", "time", false],
              ["tabla_cost_gal", "Costo por tabla (FRJ)", "number", false],
              ["max_tablas_per_player", "Tablas por jugador", "number", false],
              ["bonus_gal_on_win", "Bonus FRJ al ganar", "number", false],
              ["drop_multiplier", "Multiplicador drops", "number", false],
              ["griton_delay_ms", "Delay gritón (ms)", "number", false],
              ["max_players_per_room", "Máx jugadores/sala", "number", false],
              ["min_players_to_start", "Mín para iniciar", "number", false],
            ] as [keyof EventFormData, string, string, boolean][]
          ).map(([key, label, type, full]) => (
            <div key={key} className={full ? "col-span-2" : ""}>
              <label className="text-[10px] font-bold uppercase text-white/30 block mb-1">
                {label}
              </label>
              <input
                type={type}
                value={String(form[key])}
                onChange={setField(key)}
                className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white/70 font-mono"
              />
            </div>
          ))}
          <div className="col-span-2">
            <label className="text-[10px] font-bold uppercase text-white/30 block mb-1">
              Mensaje de convocatoria
            </label>
            <textarea
              value={form.broadcast_message}
              onChange={setField("broadcast_message")}
              rows={3}
              className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white/70 resize-none"
            />
          </div>
        </div>
        <div className="flex gap-3 mt-5">
          <button
            onClick={handleSave}
            disabled={saving}
            className="px-6 py-2 rounded-xl text-sm font-bold bg-purple-400/20 border border-purple-400/40 text-purple-300 disabled:opacity-40"
          >
            {saving ? "Guardando..." : "💾 Guardar"}
          </button>
        </div>
      </div>

      {/* EVENTS LIST */}
      <div className="flex flex-col gap-3">
        {events.map(({ event: e, status }: { event: any; status: string }) => (
          <div
            key={e.id}
            className="flex items-center gap-4 p-4 rounded-xl bg-white/2 border border-white/7"
          >
            <div
              className={`w-2 h-2 rounded-full flex-shrink-0 ${
                status === "active"
                  ? "bg-green-400"
                  : status === "upcoming"
                  ? "bg-blue-400"
                  : "bg-white/20"
              }`}
            />
            <div className="flex-1 min-w-0">
              <div className="font-bold text-sm truncate">{e.name}</div>
              <div className="text-xs text-white/35">
                {e.start_date} → {e.end_date} · {e.daily_open_time}–
                {e.daily_close_time}
                {e.bonus_gal_on_win > 0 && ` · +${e.bonus_gal_on_win} FRJ`}
              </div>
            </div>
            <div className="flex gap-2 flex-shrink-0">
              {!e.broadcast_sent && e.broadcast_message && (
                <button
                  onClick={() => handleBroadcast(e.id)}
                  aria-label="Enviar broadcast"
                  className="px-3 py-1 text-xs font-bold rounded-lg bg-green-400/12 border border-green-400/25 text-green-400"
                >
                  📣
                </button>
              )}
              {status !== "past" && status !== "cancelled" && (
                <button
                  onClick={() => handleCancel(e.id)}
                  aria-label="Cancelar evento"
                  className="px-3 py-1 text-xs font-bold rounded-lg bg-red-400/10 border border-red-400/20 text-red-400"
                >
                  ✕
                </button>
              )}
            </div>
          </div>
        ))}
        {events.length === 0 && (
          <div className="text-center text-white/25 text-sm py-8">
            Sin eventos creados
          </div>
        )}
      </div>
    </div>
  );
}
