"use client";
import { API_BASE } from "@/lib/api";

import { useEffect, useState, useCallback, useRef } from "react";
import axios from "axios";
import AdminChaosLiveViz from "./AdminChaosLiveViz";

const API = `${API_BASE}`;
const LS_KEY = "axolotto_chaos_params_v1";

interface ChaosParams {
  total_players: number;
  duration: number;
  skip_reset: boolean;
  enable_replay_attack: boolean;
  enable_id_spoofing: boolean;
  enable_race_condition: boolean;
  enable_double_booking: boolean;
  enable_boundary_injection: boolean;
  enable_cooldown_bypass: boolean;
}

function NumInput({ label, field, value, onChange, min, max, hint }: {
  label: string; field: string; value: number; onChange: (f: string, v: string) => void;
  min?: number; max?: number; hint?: string;
}) {
  return (
    <div className="flex flex-col gap-1">
      <label className="text-[10px] text-gray-500 uppercase tracking-wider font-semibold">{label}</label>
      <input
        type="number"
        value={value}
        onChange={e => onChange(field, e.target.value)}
        min={min}
        max={max}
        className="px-3 py-2 rounded-lg bg-[#1C1C35] border border-white/10 text-sm text-white placeholder-gray-700 focus:outline-none focus:border-[#E4007C]/50 tabular-nums"
      />
      {hint && <span className="text-[10px] text-gray-600">{hint}</span>}
    </div>
  );
}

function ToggleInput({ label, emoji, field, value, onChange, description }: {
  label: string; emoji: string; field: string; value: boolean;
  onChange: (f: string, v: boolean) => void; description: string;
}) {
  return (
    <label className="flex items-center gap-3 cursor-pointer group">
      <div className="relative">
        <input
          type="checkbox"
          checked={value}
          onChange={e => onChange(field, e.target.checked)}
          className="sr-only peer"
        />
        <div className="w-10 h-5 rounded-full bg-[#1C1C35] border border-white/10 peer-checked:bg-[#E4007C]/30 peer-checked:border-[#E4007C]/50 transition-all duration-200" />
        <div className="absolute top-0.5 left-0.5 w-4 h-4 rounded-full bg-gray-500 peer-checked:bg-[#E4007C] peer-checked:translate-x-5 transition-all duration-200 shadow-sm" />
      </div>
      <div className="flex flex-col">
        <span className="text-sm text-gray-300 group-hover:text-white transition-colors">
          {emoji} {label}
        </span>
        <span className="text-[10px] text-gray-600">{description}</span>
      </div>
    </label>
  );
}

const DEFAULT_PARAMS: ChaosParams = {
  total_players: 100,
  duration: 120,
  skip_reset: false,
  enable_replay_attack: true,
  enable_id_spoofing: true,
  enable_race_condition: true,
  enable_double_booking: true,
  enable_boundary_injection: true,
  enable_cooldown_bypass: true,
};

interface ChaosStatus {
  running: boolean;
  started_at: string | null;
  progress?: number;
  current_phase?: string;
  live_details?: string;
  activities?: Record<string, { action: string; zone: string; color: string; type: string; personality: string; thread_id: string; timestamp?: number }>;
  counters?: Record<string, number>;
  stats?: Record<string, number>;
}

export default function AdminChaosSimV2({ token }: { token: string | null }) {
  const [params, setParams] = useState<ChaosParams>(DEFAULT_PARAMS);
  const [status, setStatus] = useState<ChaosStatus>({
    running: false, started_at: null, progress: 0, current_phase: "", live_details: "",
    activities: {}, counters: {}, stats: {},
  });
  const [report, setReport] = useState<{ content: string; modified_at: string } | null>(null);
  const [loadingReport, setLoadingReport] = useState(true);
  const wasRunningRef = useRef(false);

  // Load saved params from localStorage
  useEffect(() => {
    try {
      const raw = localStorage.getItem(LS_KEY);
      if (raw) {
        const saved = JSON.parse(raw) as Partial<ChaosParams>;
        setParams(p => ({ ...p, ...saved }));
      }
    } catch { /* ignore */ }
  }, []);

  const setParam = (field: string, val: string | boolean) => {
    setParams(p => ({ ...p, [field]: val }));
  };

  const fetchStatus = useCallback(async () => {
    if (!token) return;
    try {
      const r = await axios.get(`${API}/admin/simulation/chaos/status`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setStatus(r.data);
    } catch { /* ignore */ }
  }, [token]);

  const fetchReport = useCallback(async () => {
    if (!token) return;
    try {
      const r = await axios.get(`${API}/admin/simulation/chaos/report`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setReport(r.data);
    } catch { /* ignore */ }
    finally { setLoadingReport(false); }
  }, [token]);

  useEffect(() => {
    fetchStatus();
    fetchReport();
  }, [fetchStatus, fetchReport]);

  // Poll status while running
  useEffect(() => {
    if (!status.running) return;
    const interval = setInterval(fetchStatus, 2000);
    return () => clearInterval(interval);
  }, [status.running, fetchStatus]);

  // Auto-refresh report when running→stopped
  useEffect(() => {
    if (status.running) {
      wasRunningRef.current = true;
    } else if (wasRunningRef.current) {
      wasRunningRef.current = false;
      fetchReport();
    }
  }, [status.running, fetchReport]);

  // Compute derived values
  const whaleCount = Math.max(1, Math.floor(params.total_players * 0.20));
  const collectorCount = Math.max(1, Math.floor(params.total_players * 0.30));
  const free2playCount = Math.max(1, params.total_players - whaleCount - collectorCount);
  const attackCount = [
    params.enable_replay_attack, params.enable_id_spoofing,
    params.enable_race_condition, params.enable_double_booking,
    params.enable_boundary_injection, params.enable_cooldown_bypass,
  ].filter(Boolean).length;
  const totalThreads = params.total_players + attackCount;

  const handleRun = async () => {
    if (!token || status.running) return;

    // Confirmation for large runs
    if (params.total_players > 50) {
      if (!confirm(
        `⚠️ Vas a lanzar ${params.total_players} bots + ${attackCount} agentes de ataque simultáneos.\n\n` +
        `Esto generará ~${totalThreads} conexiones a PostgreSQL.\n\n` +
        `¿Confirmar?`
      )) return;
    }

    const body: Record<string, unknown> = {
      total_players: params.total_players,
      duration: params.duration,
      skip_reset: params.skip_reset,
      enable_replay_attack: params.enable_replay_attack,
      enable_id_spoofing: params.enable_id_spoofing,
      enable_race_condition: params.enable_race_condition,
      enable_double_booking: params.enable_double_booking,
      enable_boundary_injection: params.enable_boundary_injection,
      enable_cooldown_bypass: params.enable_cooldown_bypass,
    };

    try {
      localStorage.setItem(LS_KEY, JSON.stringify(params));
      await axios.post(`${API}/admin/simulation/chaos/run`, body, {
        headers: { Authorization: `Bearer ${token}` },
      });
      await fetchStatus();
    } catch (e: unknown) {
      const err = e as { response?: { data?: { detail?: string } } };
      const detail = err.response?.data?.detail || "Error iniciando simulación caótica.";
      alert(detail);
    }
  };

  // Poll report while running every 10s
  useEffect(() => {
    if (!status.running) return;
    const interval = setInterval(fetchReport, 10000);
    return () => clearInterval(interval);
  }, [status.running, fetchReport]);

  return (
    <div className="space-y-6">
      <h2 className="text-lg font-black text-white">
        ⚡ Simulación Caótica <span className="text-[#FF8DA1] text-sm font-normal">v2</span>
      </h2>

      {/* Stress Test Badge */}
      <div className="flex items-center gap-3 flex-wrap">
        <div className="rounded-lg bg-[#E4007C]/10 border border-[#E4007C]/20 px-3 py-1.5 text-xs text-[#FF8DA1] font-semibold">
          🧪 Stress Test PostgreSQL
        </div>
        <div className="rounded-lg bg-[#1C1C35]/60 border border-white/5 px-3 py-1.5 text-xs text-gray-500">
          Hasta {totalThreads} conexiones concurrentes
        </div>
        {params.total_players >= 100 && (
          <div className="rounded-lg bg-yellow-400/10 border border-yellow-400/20 px-3 py-1.5 text-xs text-yellow-400 font-semibold">
            ⚠️ Test de alto estrés
          </div>
        )}
      </div>

      {/* Progress Panel */}
      {status.running && (
        <div className="rounded-xl border border-[#E4007C]/20 bg-[#1C1C35]/40 backdrop-blur-md p-5 space-y-4 shadow-[0_0_15px_rgba(228,0,124,0.1)]">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="relative flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#E4007C] opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-[#E4007C]"></span>
              </div>
              <h3 className="text-xs font-black text-white uppercase tracking-wider">
                Simulación Caótica en Progreso
              </h3>
            </div>
            {status.started_at && (
              <span className="text-gray-500 text-[10px] tabular-nums">
                Iniciada a las {new Date(status.started_at + "Z").toLocaleTimeString("es-MX")}
              </span>
            )}
          </div>

          {/* Progress Bar */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs font-semibold">
              <span className="text-[#FF8DA1]">{status.current_phase || "Ejecutando..."}</span>
              <span className="text-white tabular-nums">{status.progress ?? 0}%</span>
            </div>
            <div className="w-full h-3 bg-black/40 rounded-full overflow-hidden border border-white/5">
              <div
                className="h-full rounded-full bg-gradient-to-r from-[#E4007C] to-[#FF8DA1] shadow-[0_0_10px_rgba(228,0,124,0.5)] transition-all duration-1000 ease-out"
                style={{ width: `${status.progress ?? 0}%` }}
              />
            </div>
          </div>

          {/* Live Activity Dashboard */}
          <AdminChaosLiveViz
            activities={status.activities || {}}
            counters={status.counters || {}}
            stats={status.stats || {}}
          />

          {/* Live Details */}
          {status.live_details && (
            <div className="space-y-1.5">
              <span className="text-[10px] text-gray-500 uppercase tracking-wider font-semibold">
                Actividad Reciente
              </span>
              <div className="rounded-lg bg-[#080814] border border-white/5 p-3 overflow-x-auto">
                <pre className="text-[11px] text-pink-400 font-mono whitespace-pre leading-relaxed">
                  {status.live_details}
                </pre>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Runner Form */}
      <div className="rounded-xl border border-white/5 bg-[#141428] p-5 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-gray-300">▶ Nueva Simulación Caótica</h3>
          <div className="flex items-center gap-2">
            {status.running ? (
              <>
                <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
                <span className="text-red-400 text-xs font-semibold">Ejecutando…</span>
              </>
            ) : (
              <>
                <span className="w-2 h-2 rounded-full bg-green-500" />
                <span className="text-green-400 text-xs font-semibold">Libre</span>
              </>
            )}
          </div>
        </div>

        {/* Main params */}
        <div className="grid grid-cols-2 gap-3">
          <NumInput
            label="Total Jugadores"
            field="total_players"
            value={params.total_players}
            onChange={(f, v) => setParam(f, v)}
            min={1} max={500}
            hint={`≈${whaleCount} whales, ${collectorCount} collectors, ${free2playCount} free2play`}
          />
          <NumInput
            label="Duración (segundos)"
            field="duration"
            value={params.duration}
            onChange={(f, v) => setParam(f, v)}
            min={10} max={600}
            hint="Tiempo de la fase concurrente"
          />
        </div>

        {/* Attack toggles */}
        <div className="space-y-2">
          <label className="text-[10px] text-gray-500 uppercase tracking-wider font-semibold">
            Agentes de Caos ({attackCount} activos)
          </label>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <ToggleInput
              emoji="🔄" label="Replay Attack" field="enable_replay_attack"
              value={params.enable_replay_attack}
              onChange={(f, v) => setParam(f, v)}
              description="Envía mismo tx_hash repetidamente (espera 409)"
            />
            <ToggleInput
              emoji="👤" label="ID Spoofing" field="enable_id_spoofing"
              value={params.enable_id_spoofing}
              onChange={(f, v) => setParam(f, v)}
              description="Intenta usar recursos de otro jugador (espera 403)"
            />
            <ToggleInput
              emoji="⚡" label="Race Condition" field="enable_race_condition"
              value={params.enable_race_condition}
              onChange={(f, v) => setParam(f, v)}
              description="10 compras simultáneas con saldo para 1 (espera 1 éxito)"
            />
            <ToggleInput
              emoji="🎯" label="Double Booking" field="enable_double_booking"
              value={params.enable_double_booking}
              onChange={(f, v) => setParam(f, v)}
              description="Registra mismo axo en múltiples salas (espera 400)"
            />
            <ToggleInput
              emoji="💉" label="Boundary Injection" field="enable_boundary_injection"
              value={params.enable_boundary_injection}
              onChange={(f, v) => setParam(f, v)}
              description="Valores negativos, overflow, null bytes (espera 400/422)"
            />
            <ToggleInput
              emoji="⏱️" label="Cooldown Bypass" field="enable_cooldown_bypass"
              value={params.enable_cooldown_bypass}
              onChange={(f, v) => setParam(f, v)}
              description="Double-claim daily, manipula sleep time (espera 400)"
            />
          </div>
        </div>

        {/* Skip reset checkbox */}
        <div className="flex flex-col gap-1">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={params.skip_reset}
              onChange={e => setParams(p => ({ ...p, skip_reset: e.target.checked }))}
              className="w-4 h-4 rounded accent-[#E4007C]"
            />
            <span className="text-sm text-gray-400">Omitir reset de BD</span>
          </label>
          <p className="text-[10px] text-yellow-600 leading-snug max-w-[280px]">
            Sin marcar: borra TODOS los datos de TODOS los usuarios incluyendo admin. ¡Usar con precaución!
          </p>
        </div>

        {/* Run button */}
        <button
          onClick={handleRun}
          disabled={status.running}
          className="w-full py-2.5 rounded-xl font-black text-sm transition-all disabled:opacity-40 disabled:cursor-not-allowed"
          style={{
            background: status.running
              ? "#1C1C35"
              : "linear-gradient(135deg, #9333EA, #E4007C)",
            color: status.running ? "#6B7280" : "#fff",
          }}
        >
          {status.running
            ? "⏳ Simulación Caótica en Curso…"
            : `⚡ Ejecutar Simulación Caótica (${params.total_players} bots)`}
        </button>
      </div>

      {/* Report Viewer */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-gray-300">
            📄 Último Reporte de Auditoría
          </h3>
          <button
            onClick={fetchReport}
            className="text-xs text-gray-600 hover:text-gray-400 transition-colors"
          >
            ↻ Refrescar
          </button>
        </div>
        {loadingReport ? (
          <p className="text-gray-600 animate-pulse text-sm">Cargando reporte…</p>
        ) : !report ? (
          <p className="text-gray-700 text-sm">
            Sin reporte generado aún. Ejecuta una simulación caótica para generar uno.
          </p>
        ) : (
          <div>
            {report.modified_at && (
              <p className="text-[10px] text-gray-700 mb-1">
                Generado: {new Date(report.modified_at + "Z").toLocaleString("es-MX")}
              </p>
            )}
            <div className="rounded-xl border border-white/5 bg-[#080814] p-4 overflow-x-auto max-h-[70vh]">
              <pre className="text-[11px] text-green-400 font-mono whitespace-pre leading-relaxed">
                {report.content}
              </pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
