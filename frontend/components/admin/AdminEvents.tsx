"use client";
import { API_BASE } from "@/lib/api";
import { useEffect, useState, useCallback } from "react";
import axios from "axios";
import { Calendar, Trash2, Megaphone, Plus, Clock, Settings, Users, Trophy } from "lucide-react";

const API = `${API_BASE}/admin/events`;

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

const EMPTY_FORM: EventFormData = {
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

export default function AdminEvents({ token }: { token: string | null }) {
  const [events, setEvents] = useState<any[]>([]);
  const [form, setForm] = useState<EventFormData>(EMPTY_FORM);
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState("");
  const [showCreate, setShowCreate] = useState(false);

  const authHeaders = useCallback(() => ({
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    }
  }), [token]);

  const loadEvents = useCallback(async () => {
    if (!token) return;
    try {
      const res = await axios.get(API, authHeaders());
      setEvents(res.data);
    } catch (err: any) {
      console.error("Error loading events", err);
    }
  }, [token, authHeaders]);

  useEffect(() => {
    loadEvents();
  }, [loadEvents]);

  const handleSave = async () => {
    if (!form.name || !form.start_date || !form.end_date) {
      setMsg("❌ Nombre y fechas de inicio/fin son requeridos.");
      return;
    }
    setSaving(true);
    setMsg("");
    try {
      const res = await axios.post(API, form, authHeaders());
      setMsg(`✅ Evento "${res.data.name}" creado con éxito.`);
      setForm(EMPTY_FORM);
      setShowCreate(false);
      loadEvents();
    } catch (err: any) {
      const detail = err.response?.data?.detail || "Error al crear el evento.";
      setMsg(`❌ ${detail}`);
    } finally {
      setSaving(false);
    }
  };

  const handleBroadcast = async (id: number) => {
    setMsg("");
    try {
      const res = await axios.post(`${API}/${id}/broadcast`, {}, authHeaders());
      setMsg(`📣 ${res.data.mensaje}`);
      loadEvents();
    } catch (err: any) {
      const detail = err.response?.data?.detail || "Error al enviar convocatoria.";
      setMsg(`❌ ${detail}`);
    }
  };

  const handleCancel = async (id: number) => {
    if (!confirm("¿Seguro que deseas cancelar/desactivar este evento?")) return;
    setMsg("");
    try {
      await axios.delete(`${API}/${id}`, authHeaders());
      setMsg("✅ Evento cancelado correctamente.");
      loadEvents();
    } catch (err: any) {
      const detail = err.response?.data?.detail || "Error al cancelar el evento.";
      setMsg(`❌ ${detail}`);
    }
  };

  const setField = (key: keyof EventFormData, val: any) => {
    setForm((prev) => ({ ...prev, [key]: val }));
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-black text-white flex items-center gap-2">
            <span>🎮</span> Eventos de Modo Manual
          </h2>
          <p className="text-gray-400 text-xs mt-1">
            Crea, programa y convoca a torneos especiales con modificadores de recompensa y reglas personalizadas.
          </p>
        </div>
        <button
          onClick={() => setShowCreate(!showCreate)}
          className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold bg-[#E4007C]/20 border border-[#E4007C]/40 text-[#FF8DA1] hover:bg-[#E4007C]/30 transition-all duration-200"
        >
          {showCreate ? "Ver listado" : <><Plus size={14} /> Crear Evento</>}
        </button>
      </div>

      {msg && (
        <div className="p-3 rounded-xl border border-white/5 bg-[#141428] text-xs font-semibold">
          {msg}
        </div>
      )}

      {showCreate ? (
        <div className="rounded-xl border border-white/5 bg-[#141428] p-5 space-y-4">
          <h3 className="text-xs font-black text-white uppercase tracking-wider mb-2 flex items-center gap-1.5">
            <Settings size={14} className="text-pink-400" /> Configuración del Evento
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="md:col-span-3">
              <label className="text-[10px] text-gray-500 uppercase tracking-wider font-semibold">Nombre del evento</label>
              <input
                type="text"
                placeholder="Ej. Torneo de Fin de Semana Bioluminiscente"
                value={form.name}
                onChange={(e) => setField("name", e.target.value)}
                className="w-full mt-1 px-3 py-2 rounded-lg bg-[#1C1C35] border border-white/10 text-xs text-white placeholder-gray-600 focus:outline-none focus:border-[#E4007C]/50"
              />
            </div>

            <div>
              <label className="text-[10px] text-gray-500 uppercase tracking-wider font-semibold">Fecha inicio</label>
              <input
                type="date"
                value={form.start_date}
                onChange={(e) => setField("start_date", e.target.value)}
                className="w-full mt-1 px-3 py-2 rounded-lg bg-[#1C1C35] border border-white/10 text-xs text-white focus:outline-none focus:border-[#E4007C]/50"
              />
            </div>

            <div>
              <label className="text-[10px] text-gray-500 uppercase tracking-wider font-semibold">Fecha fin</label>
              <input
                type="date"
                value={form.end_date}
                onChange={(e) => setField("end_date", e.target.value)}
                className="w-full mt-1 px-3 py-2 rounded-lg bg-[#1C1C35] border border-white/10 text-xs text-white focus:outline-none focus:border-[#E4007C]/50"
              />
            </div>

            <div>
              <label className="text-[10px] text-gray-500 uppercase tracking-wider font-semibold">Condición de victoria</label>
              <select
                value={form.win_condition}
                onChange={(e) => setField("win_condition", e.target.value)}
                className="w-full mt-1 px-3 py-2 rounded-lg bg-[#1C1C35] border border-white/10 text-xs text-white focus:outline-none focus:border-[#E4007C]/50 cursor-pointer"
              >
                <option value="tabla_llena">Tabla Llena (Lotería clásica)</option>
                <option value="linea_h">Línea Horizontal</option>
                <option value="linea_v">Línea Vertical</option>
                <option value="esquinas">Cuatro Esquinas</option>
                <option value="cruz">Cruz</option>
              </select>
            </div>

            <div>
              <label className="text-[10px] text-gray-500 uppercase tracking-wider font-semibold">Hora de apertura diaria</label>
              <input
                type="time"
                value={form.daily_open_time}
                onChange={(e) => setField("daily_open_time", e.target.value)}
                className="w-full mt-1 px-3 py-2 rounded-lg bg-[#1C1C35] border border-white/10 text-xs text-white focus:outline-none"
              />
            </div>

            <div>
              <label className="text-[10px] text-gray-500 uppercase tracking-wider font-semibold">Hora de cierre diaria</label>
              <input
                type="time"
                value={form.daily_close_time}
                onChange={(e) => setField("daily_close_time", e.target.value)}
                className="w-full mt-1 px-3 py-2 rounded-lg bg-[#1C1C35] border border-white/10 text-xs text-white focus:outline-none"
              />
            </div>

            <div>
              <label className="text-[10px] text-gray-500 uppercase tracking-wider font-semibold">Costo por tabla (FRJ)</label>
              <input
                type="number"
                value={form.tabla_cost_gal}
                onChange={(e) => setField("tabla_cost_gal", Number(e.target.value))}
                className="w-full mt-1 px-3 py-2 rounded-lg bg-[#1C1C35] border border-white/10 text-xs text-white focus:outline-none font-mono"
              />
            </div>

            <div>
              <label className="text-[10px] text-gray-500 uppercase tracking-wider font-semibold">Tablas máx por jugador</label>
              <input
                type="number"
                value={form.max_tablas_per_player}
                onChange={(e) => setField("max_tablas_per_player", Number(e.target.value))}
                className="w-full mt-1 px-3 py-2 rounded-lg bg-[#1C1C35] border border-white/10 text-xs text-white focus:outline-none font-mono"
              />
            </div>

            <div>
              <label className="text-[10px] text-gray-500 uppercase tracking-wider font-semibold">Bonus FRJ al ganar</label>
              <input
                type="number"
                value={form.bonus_gal_on_win}
                onChange={(e) => setField("bonus_gal_on_win", Number(e.target.value))}
                className="w-full mt-1 px-3 py-2 rounded-lg bg-[#1C1C35] border border-white/10 text-xs text-white focus:outline-none font-mono"
              />
            </div>

            <div>
              <label className="text-[10px] text-gray-500 uppercase tracking-wider font-semibold">Multiplicador de drops</label>
              <input
                type="number"
                step="0.1"
                value={form.drop_multiplier}
                onChange={(e) => setField("drop_multiplier", Number(e.target.value))}
                className="w-full mt-1 px-3 py-2 rounded-lg bg-[#1C1C35] border border-white/10 text-xs text-white focus:outline-none font-mono"
              />
            </div>

            <div>
              <label className="text-[10px] text-gray-500 uppercase tracking-wider font-semibold">Bono de XP (%)</label>
              <input
                type="number"
                value={form.xp_bonus_pct}
                onChange={(e) => setField("xp_bonus_pct", Number(e.target.value))}
                className="w-full mt-1 px-3 py-2 rounded-lg bg-[#1C1C35] border border-white/10 text-xs text-white focus:outline-none font-mono"
              />
            </div>

            <div>
              <label className="text-[10px] text-gray-500 uppercase tracking-wider font-semibold">Delay del Gritón (ms)</label>
              <input
                type="number"
                value={form.griton_delay_ms}
                onChange={(e) => setField("griton_delay_ms", Number(e.target.value))}
                className="w-full mt-1 px-3 py-2 rounded-lg bg-[#1C1C35] border border-white/10 text-xs text-white focus:outline-none font-mono"
              />
            </div>

            <div>
              <label className="text-[10px] text-gray-500 uppercase tracking-wider font-semibold">Mín jugadores para iniciar</label>
              <input
                type="number"
                value={form.min_players_to_start}
                onChange={(e) => setField("min_players_to_start", Number(e.target.value))}
                className="w-full mt-1 px-3 py-2 rounded-lg bg-[#1C1C35] border border-white/10 text-xs text-white focus:outline-none font-mono"
              />
            </div>

            <div>
              <label className="text-[10px] text-gray-500 uppercase tracking-wider font-semibold">Máx jugadores por sala</label>
              <input
                type="number"
                value={form.max_players_per_room}
                onChange={(e) => setField("max_players_per_room", Number(e.target.value))}
                className="w-full mt-1 px-3 py-2 rounded-lg bg-[#1C1C35] border border-white/10 text-xs text-white focus:outline-none font-mono"
              />
            </div>

            <div>
              <label className="text-[10px] text-gray-500 uppercase tracking-wider font-semibold">Modos permitidos</label>
              <select
                value={form.allowed_modes}
                onChange={(e) => setField("allowed_modes", e.target.value)}
                className="w-full mt-1 px-3 py-2 rounded-lg bg-[#1C1C35] border border-white/10 text-xs text-white focus:outline-none cursor-pointer"
              >
                <option value="both">Ambos (Manual y Bot)</option>
                <option value="manual">Solo Jugadores Manuales</option>
                <option value="bot">Solo Bots</option>
              </select>
            </div>

            <div className="md:col-span-3">
              <label className="text-[10px] text-gray-500 uppercase tracking-wider font-semibold">Mensaje de Convocatoria (Broadcast)</label>
              <textarea
                placeholder="Ej. ¡Lotería Especial de Fin de Semana! Doble drop y 20% XP extra en salas de modo manual. ¡Entra ya!"
                value={form.broadcast_message}
                onChange={(e) => setField("broadcast_message", e.target.value)}
                rows={2}
                className="w-full mt-1 px-3 py-2 rounded-lg bg-[#1C1C35] border border-white/10 text-xs text-white placeholder-gray-600 focus:outline-none focus:border-[#E4007C]/50 resize-none"
              />
            </div>
          </div>

          <button
            onClick={handleSave}
            disabled={saving}
            className="w-full mt-4 py-2 rounded-xl text-xs font-black bg-gradient-to-r from-purple-600 to-pink-600 text-white hover:from-purple-500 hover:to-pink-500 transition-all duration-200 disabled:opacity-40"
          >
            {saving ? "Guardando evento..." : "💾 Guardar y Activar Evento"}
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-3">
          {events.map(({ event: e, status }: { event: any; status: string }) => {
            const isCancelled = !e.is_active;
            return (
              <div
                key={e.id}
                className="rounded-xl border border-white/5 bg-[#141428] p-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4"
              >
                <div className="flex items-center gap-3">
                  <div className={`w-2.5 h-2.5 rounded-full shrink-0 ${
                    status === "active" ? "bg-emerald-500 animate-pulse" :
                    status === "upcoming" ? "bg-cyan-500" :
                    "bg-gray-600"
                  }`} />
                  <div className="space-y-1">
                    <h4 className="text-sm font-bold text-white flex items-center gap-1.5">
                      {e.name}
                      {status === "active" && (
                        <span className="px-1.5 py-0.5 bg-emerald-500/10 text-emerald-400 text-[9px] font-black rounded uppercase tracking-wider">
                          En Vivo
                        </span>
                      )}
                    </h4>
                    <p className="text-[11px] text-gray-400 flex items-center gap-2">
                      <Calendar size={12} className="text-slate-500" />
                      {new Date(e.start_date).toLocaleDateString("es-MX")} → {new Date(e.end_date).toLocaleDateString("es-MX")}
                      {" · "}
                      <Clock size={12} className="text-slate-500" />
                      {e.daily_open_time.slice(0,5)} - {e.daily_close_time.slice(0,5)}
                    </p>
                    <div className="flex flex-wrap gap-1.5 mt-1">
                      <span className="px-1.5 py-0.5 rounded bg-slate-900 border border-white/5 text-[9px] text-gray-500 font-bold font-mono">
                        Cost: {e.tabla_cost_gal} FRJ
                      </span>
                      {e.bonus_gal_on_win > 0 && (
                        <span className="px-1.5 py-0.5 rounded bg-amber-500/10 border border-amber-500/20 text-[9px] text-amber-400 font-bold">
                          🏆 +{e.bonus_gal_on_win} FRJ
                        </span>
                      )}
                      {e.drop_multiplier > 1 && (
                        <span className="px-1.5 py-0.5 rounded bg-pink-500/10 border border-pink-500/20 text-[9px] text-pink-400 font-bold">
                          ✨ {e.drop_multiplier}x Drops
                        </span>
                      )}
                      <span className="px-1.5 py-0.5 rounded bg-purple-500/10 border border-purple-500/20 text-[9px] text-purple-400 font-bold uppercase tracking-wider">
                        Rule: {e.win_condition.replace("_", " ")}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2 self-end sm:self-auto">
                  {!e.broadcast_sent && e.broadcast_message && (
                    <button
                      onClick={() => handleBroadcast(e.id)}
                      title="Enviar Convocatoria (Broadcast)"
                      className="p-2 rounded-lg bg-green-500/10 border border-green-500/20 text-green-400 hover:bg-green-500/20 transition-all duration-200"
                    >
                      <Megaphone size={14} />
                    </button>
                  )}
                  {status !== "past" && !isCancelled && (
                    <button
                      onClick={() => handleCancel(e.id)}
                      title="Cancelar Evento"
                      className="p-2 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 hover:bg-red-500/20 transition-all duration-200"
                    >
                      <Trash2 size={14} />
                    </button>
                  )}
                </div>
              </div>
            );
          })}
          {events.length === 0 && (
            <div className="text-center py-12 border border-white/5 bg-[#141428] rounded-xl text-gray-500 text-xs">
              No se han programado eventos manuales todavía.
            </div>
          )}
        </div>
      )}
    </div>
  );
}
