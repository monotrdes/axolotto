"use client";
import { API_BASE } from "@/lib/api";




import { useEffect, useState, useCallback, useRef } from "react";
import axios from "axios";
import { usePrivy } from "@privy-io/react-auth";



const API = `${API_BASE}`;
const LS_KEY = "axolotto_sim_params_v1";

interface SimParams {
  players: number;
  games: number;
  incubation: number;
  multi_wait: number;
  skip_reset: boolean;
  skip_imprinting: boolean;
  create_test_event: boolean;
  max_boosters: string;
  max_boards: string;
  max_webitos: string;
  include_user: string;
  initial_axf: string;
  initial_frj: string;
}

function NumInput({ label, field, value, onChange, placeholder }: {
  label: string; field: string; value: string | number; onChange: (f: string, v: string) => void; placeholder?: string;
}) {
  return (
    <div className="flex flex-col gap-1">
      <label className="text-[10px] text-gray-500 uppercase tracking-wider font-semibold">{label}</label>
      <input
        type="number"
        value={value}
        onChange={e => onChange(field, e.target.value)}
        placeholder={placeholder}
        min={0}
        className="px-3 py-2 rounded-lg bg-[#1C1C35] border border-white/10 text-sm text-white placeholder-gray-700 focus:outline-none focus:border-[#E4007C]/50 tabular-nums"
      />
    </div>
  );
}

const DEFAULT_PARAMS: SimParams = {
  players: 4,
  games: 5,
  incubation: 45,
  multi_wait: 35,
  skip_reset: false,
  skip_imprinting: false,
  create_test_event: false,
  max_boosters: "",
  max_boards: "",
  max_webitos: "",
  include_user: "",
  initial_axf: "",
  initial_frj: "",
};

interface SimStatus {
  running: boolean;
  started_at: string | null;
  progress?: number;
  current_step?: string;
  live_details?: string;
}

export default function AdminSimReport({ token }: { token: string | null }) {
  const { user } = usePrivy();
  const [params, setParams] = useState<SimParams>(DEFAULT_PARAMS);
  const [status, setStatus] = useState<SimStatus>({
    running: false,
    started_at: null,
    progress: 0,
    current_step: "",
    live_details: "",
  });
  const [report, setReport] = useState<{ content: string; modified_at: string } | null>(null);
  const [loadingReport, setLoadingReport] = useState(true);
  const wasRunningRef = useRef(false);
  const hydrated = useRef(false);
  const savedHadUser = useRef(false);

  // Effect A: load from localStorage on mount (runs once, before Privy resolves)
  useEffect(() => {
    try {
      const raw = localStorage.getItem(LS_KEY);
      if (raw) {
        const saved = JSON.parse(raw) as Partial<SimParams>;
        savedHadUser.current = !!saved.include_user;
        setParams(p => ({ ...p, ...saved }));
      }
    } catch {
      // ignore malformed localStorage data — defaults stay
    }
    hydrated.current = true;
  }, []);

  // Effect B: auto-fill include_user from Privy DID once user is available
  useEffect(() => {
    if (!hydrated.current) return;
    if (savedHadUser.current) return; // saved params already have a DID, don't overwrite
    if (!user?.id) return;
    setParams(p => p.include_user ? p : { ...p, include_user: user.id });
  }, [user]);

  const setParam = (field: string, val: string) => {
    setParams(p => ({ ...p, [field]: val }));
  };

  const fetchStatus = useCallback(async () => {
    if (!token) return;
    try {
      const r = await axios.get(`${API}/admin/simulation/status`, { headers: { Authorization: `Bearer ${token}` } });
      setStatus(r.data);
    } catch { /* ignore */ }
  }, [token]);

  const fetchReport = useCallback(async () => {
    if (!token) return;
    try {
      const r = await axios.get(`${API}/admin/simulation/report`, { headers: { Authorization: `Bearer ${token}` } });
      setReport(r.data);
    } catch { /* ignore */ }
    finally { setLoadingReport(false); }
  }, [token]);

  useEffect(() => {
    fetchStatus();
    fetchReport();
  }, [fetchStatus, fetchReport]);

  // Poll status while running (every 2s for responsive progress bar and activity logs)
  useEffect(() => {
    if (!status.running) return;
    const interval = setInterval(async () => {
      await fetchStatus();
    }, 2000);
    return () => clearInterval(interval);
  }, [status.running, fetchStatus]);

  // When status transitions running→stopped, auto-refresh report
  useEffect(() => {
    if (status.running) {
      wasRunningRef.current = true;
    } else if (wasRunningRef.current) {
      wasRunningRef.current = false;
      fetchReport();
    }
  }, [status.running, fetchReport]);

  const handleRun = async () => {
    if (!token || status.running) return;
    const body: Record<string, unknown> = {
      players: Number(params.players),
      games: Number(params.games),
      incubation: Number(params.incubation),
      multi_wait: Number(params.multi_wait),
      skip_reset: params.skip_reset,
      skip_imprinting: params.skip_imprinting,
      create_test_event: params.create_test_event,
    };
    if (params.max_boosters) body.max_boosters = Number(params.max_boosters);
    if (params.max_boards)   body.max_boards   = Number(params.max_boards);
    if (params.max_webitos)  body.max_webitos  = Number(params.max_webitos);
    if (params.include_user) body.include_user  = params.include_user;
    if (params.initial_axf)  body.initial_axf   = Number(params.initial_axf);
    if (params.initial_frj)  body.initial_frj   = Number(params.initial_frj);

    try {
      localStorage.setItem(LS_KEY, JSON.stringify(params));
      await axios.post(`${API}/admin/simulation/run`, body, { headers: { Authorization: `Bearer ${token}` } });
      await fetchStatus();
    } catch (e: unknown) {
      const err = e as { response?: { data?: { detail?: string } } };
      const detail = err.response?.data?.detail || "Error iniciando simulación.";
      alert(detail);
    }
  };

  // Poll report every 10s when running
  useEffect(() => {
    if (!status.running) return;
    const interval = setInterval(fetchReport, 10000);
    return () => clearInterval(interval);
  }, [status.running, fetchReport]);

  return (
    <div className="space-y-6">
      <h2 className="text-lg font-black text-white">🧪 Simulación</h2>

      {/* Progress Panel */}
      {status.running && (
        <div className="rounded-xl border border-[#E4007C]/20 bg-[#1C1C35]/40 backdrop-blur-md p-5 space-y-4 shadow-[0_0_15px_rgba(228,0,124,0.1)]">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="relative flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#E4007C] opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-[#E4007C]"></span>
              </div>
              <h3 className="text-xs font-black text-white uppercase tracking-wider">Simulación en progreso</h3>
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
              <span className="text-[#FF8DA1]">{status.current_step || "Ejecutando..."}</span>
              <span className="text-white tabular-nums">{status.progress ?? 0}%</span>
            </div>
            
            <div className="w-full h-3 bg-black/40 rounded-full overflow-hidden border border-white/5">
              <div 
                className="h-full rounded-full bg-gradient-to-r from-[#E4007C] to-[#FF8DA1] shadow-[0_0_10px_rgba(228,0,124,0.5)] transition-all duration-1000 ease-out"
                style={{ width: `${status.progress ?? 0}%` }}
              />
            </div>
          </div>

          {/* Console / Live Details Output */}
          {status.live_details && (
            <div className="space-y-1.5">
              <span className="text-[10px] text-gray-500 uppercase tracking-wider font-semibold">Actividad Reciente</span>
              <div className="rounded-lg bg-[#080814] border border-white/5 p-3 overflow-x-auto">
                <pre className="text-[11px] text-pink-400 font-mono whitespace-pre leading-relaxed animate-pulse">
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
          <h3 className="text-sm font-semibold text-gray-300">▶ Nueva Simulación</h3>
          <div className="flex items-center gap-2">
            {status.running ? (
              <>
                <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
                <span className="text-red-400 text-xs font-semibold">Ejecutando…</span>
                {status.started_at && (
                  <span className="text-gray-600 text-[10px]">desde {new Date(status.started_at + "Z").toLocaleTimeString("es-MX")}</span>
                )}
              </>
            ) : (
              <>
                <span className="w-2 h-2 rounded-full bg-green-500" />
                <span className="text-green-400 text-xs font-semibold">Libre</span>
              </>
            )}
          </div>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <NumInput label="Jugadores" field="players" value={params.players} onChange={setParam} />
          <NumInput label="Partidas/axo" field="games" value={params.games} onChange={setParam} />
          <NumInput label="Incubación (s)" field="incubation" value={params.incubation} onChange={setParam} />
          <NumInput label="Espera multi (s)" field="multi_wait" value={params.multi_wait} onChange={setParam} />
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
          <NumInput label="Max Boosters (opt)" field="max_boosters" value={params.max_boosters} onChange={setParam} placeholder="personalidad" />
          <NumInput label="Max Tablas (opt)" field="max_boards" value={params.max_boards} onChange={setParam} placeholder="personalidad" />
          <NumInput label="Max Webitos (opt)" field="max_webitos" value={params.max_webitos} onChange={setParam} placeholder="personalidad" />
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
          <NumInput label="AXF inicial / jugador (opt)" field="initial_axf" value={params.initial_axf} onChange={setParam} placeholder="auto" />
          <NumInput label="FRJ inicial / jugador (opt)" field="initial_frj" value={params.initial_frj} onChange={setParam} placeholder="auto" />
        </div>

        <div className="flex flex-wrap items-start gap-4">
          <div className="flex flex-col gap-1">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={params.skip_reset}
                onChange={e => setParams(p => ({ ...p, skip_reset: e.target.checked }))}
                className="w-4 h-4 rounded accent-[#E4007C]"
              />
              <span className="text-sm text-gray-400">Omitir reset</span>
            </label>
            <p className="text-[10px] text-yellow-600 leading-snug max-w-[220px]">
              Sin marcar: borra TODOS los datos (wallet, cartas, axolotitos, historial) de TODOS los usuarios incluyendo admin
            </p>
          </div>
          <div className="flex flex-col gap-1">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={params.skip_imprinting}
                onChange={e => setParams(p => ({ ...p, skip_imprinting: e.target.checked }))}
                className="w-4 h-4 rounded accent-[#E4007C]"
              />
              <span className="text-sm text-gray-400">Omitir imprinting</span>
            </label>
            <p className="text-[10px] text-gray-600 leading-snug max-w-[200px]">
              Salta las partidas de imprinting de huevos extra (más rápido). No afecta el tutorial.
            </p>
          </div>
          <div className="flex flex-col gap-1">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={params.create_test_event}
                onChange={e => setParams(p => ({ ...p, create_test_event: e.target.checked }))}
                className="w-4 h-4 rounded accent-[#E4007C]"
              />
              <span className="text-sm text-gray-400">Crear evento de prueba</span>
            </label>
            <p className="text-[10px] text-gray-600 leading-snug max-w-[200px]">
              Crea un ManualModeEvent de prueba (modo manual) durante la simulación.
            </p>
          </div>
          <div className="flex-1 min-w-[200px]">
            <label className="text-[10px] text-gray-500 uppercase tracking-wider font-semibold block mb-1">Include User (privy_did, opt)</label>
            <div className="flex gap-2">
              <input
                type="text"
                value={params.include_user}
                onChange={e => setParams(p => ({ ...p, include_user: e.target.value }))}
                placeholder="did:privy:xxxxx"
                className="flex-1 px-3 py-2 rounded-lg bg-[#1C1C35] border border-white/10 text-sm text-white placeholder-gray-700 focus:outline-none focus:border-[#E4007C]/50 font-mono"
              />
              <button
                type="button"
                onClick={() => setParams(p => ({ ...p, include_user: user?.id ?? "" }))}
                disabled={!user?.id}
                className="px-2 py-1.5 rounded-lg bg-[#1C1C35] border border-white/10 text-[10px] text-gray-400 hover:text-white hover:border-[#E4007C]/50 transition-colors disabled:opacity-40 disabled:cursor-not-allowed whitespace-nowrap"
              >
                Usar mi DID
              </button>
            </div>
          </div>
        </div>

        <button
          onClick={handleRun}
          disabled={status.running}
          className="w-full py-2.5 rounded-xl font-black text-sm transition-all disabled:opacity-40 disabled:cursor-not-allowed"
          style={{
            background: status.running ? "#1C1C35" : "linear-gradient(135deg, #E4007C, #FF8DA1)",
            color: status.running ? "#6B7280" : "#fff",
          }}
        >
          {status.running ? "⏳ Simulación en curso…" : "▶ Ejecutar Simulación"}
        </button>
      </div>

      {/* Report Viewer */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-gray-300">📄 Último Reporte</h3>
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
          <p className="text-gray-700 text-sm">Sin reporte generado aún.</p>
        ) : (
          <div>
            {report.modified_at && (
              <p className="text-[10px] text-gray-700 mb-1">Generado: {new Date(report.modified_at + "Z").toLocaleString("es-MX")}</p>
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