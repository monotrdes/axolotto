"use client";
import { API_BASE } from "@/lib/api";
import { useEffect, useState, useCallback } from "react";
import axios from "axios";
import { QrCode, Plus, Download, Tag, Settings, Percent, Calendar } from "lucide-react";

const API = `${API_BASE}/admin/promo/batches`;

interface Batch {
  name: string;
  total_codes: number;
  redeemed_codes: number;
  created_at: string | null;
}

interface BatchForm {
  name: string;
  quantity: number;
  axf_amount: number;
  frj_amount: number;
  reward_item_id: string;
}

const EMPTY_FORM: BatchForm = {
  name: "",
  quantity: 50,
  axf_amount: 139,
  frj_amount: 1000,
  reward_item_id: "",
};

export default function AdminPromos({ token }: { token: string | null }) {
  const [batches, setBatches] = useState<Batch[]>([]);
  const [form, setForm] = useState<BatchForm>(EMPTY_FORM);
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState("");
  const [showCreate, setShowCreate] = useState(false);

  const authHeaders = useCallback(() => ({
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    }
  }), [token]);

  const loadBatches = useCallback(async () => {
    if (!token) return;
    try {
      const res = await axios.get(API, authHeaders());
      setBatches(res.data.batches || []);
    } catch (err: any) {
      console.error("Error loading batches", err);
    }
  }, [token, authHeaders]);

  useEffect(() => {
    loadBatches();
  }, [loadBatches]);

  const handleCreate = async () => {
    if (!form.name || form.quantity <= 0) {
      setMsg("❌ Nombre del lote y cantidad de códigos son requeridos.");
      return;
    }
    setSaving(true);
    setMsg("");
    try {
      const body = {
        name: form.name.trim(),
        quantity: form.quantity,
        axf_amount: form.axf_amount,
        frj_amount: form.frj_amount,
        reward_item_id: form.reward_item_id ? Number(form.reward_item_id) : null,
      };
      const res = await axios.post(API, body, authHeaders());
      setMsg(`✅ ${res.data.message}`);
      setForm(EMPTY_FORM);
      setShowCreate(false);
      loadBatches();
    } catch (err: any) {
      const detail = err.response?.data?.detail || "Error al crear el lote.";
      setMsg(`❌ ${detail}`);
    } finally {
      setSaving(false);
    }
  };

  const handleExport = (batchName: string) => {
    if (!token) return;
    // Download directly via window.open using the bearer token in query parameter or browser-native download
    // Since API requires authentication header, we can fetch it via axios and trigger a client-side download blob!
    axios.get(`${API}/${batchName}/export`, {
      headers: { Authorization: `Bearer ${token}` },
      responseType: "blob",
    })
    .then((res) => {
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `lote_promo_${batchName}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    })
    .catch((err) => {
      console.error("Error exporting CSV", err);
      alert("Error al exportar códigos.");
    });
  };

  const setField = (key: keyof BatchForm, val: any) => {
    setForm((prev) => ({ ...prev, [key]: val }));
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-black text-white flex items-center gap-2">
            <span>🪅</span> Promociones y Corcholatas
          </h2>
          <p className="text-gray-400 text-xs mt-1">
            Genera lotes de códigos alfanuméricos únicos para campañas físicas e imprime/graba en corcholatas.
          </p>
        </div>
        <button
          onClick={() => setShowCreate(!showCreate)}
          className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold bg-[#E4007C]/20 border border-[#E4007C]/40 text-[#FF8DA1] hover:bg-[#E4007C]/30 transition-all duration-200"
        >
          {showCreate ? "Ver Lotes" : <><Plus size={14} /> Generar Nuevo Lote</>}
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
            <Settings size={14} className="text-pink-400" /> Parámetros del Kit de Bienvenida
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="md:col-span-2">
              <label className="text-[10px] text-gray-500 uppercase tracking-wider font-semibold">Nombre del Lote (Campaña)</label>
              <input
                type="text"
                placeholder="Ej. corcholata-lanzamiento-2026"
                value={form.name}
                onChange={(e) => setField("name", e.target.value)}
                className="w-full mt-1 px-3 py-2 rounded-lg bg-[#1C1C35] border border-white/10 text-xs text-white placeholder-gray-600 focus:outline-none focus:border-[#E4007C]/50 font-mono"
              />
            </div>

            <div>
              <label className="text-[10px] text-gray-500 uppercase tracking-wider font-semibold">Cantidad de códigos a generar</label>
              <input
                type="number"
                value={form.quantity}
                onChange={(e) => setField("quantity", Number(e.target.value))}
                className="w-full mt-1 px-3 py-2 rounded-lg bg-[#1C1C35] border border-white/10 text-xs text-white focus:outline-none font-mono"
              />
            </div>

            <div>
              <label className="text-[10px] text-gray-500 uppercase tracking-wider font-semibold">Obsequio AXF (Axofichas)</label>
              <input
                type="number"
                value={form.axf_amount}
                onChange={(e) => setField("axf_amount", Number(e.target.value))}
                className="w-full mt-1 px-3 py-2 rounded-lg bg-[#1C1C35] border border-white/10 text-xs text-white focus:outline-none font-mono"
              />
            </div>

            <div>
              <label className="text-[10px] text-gray-500 uppercase tracking-wider font-semibold">Obsequio FRJ (Frijolitos)</label>
              <input
                type="number"
                value={form.frj_amount}
                onChange={(e) => setField("frj_amount", Number(e.target.value))}
                className="w-full mt-1 px-3 py-2 rounded-lg bg-[#1C1C35] border border-white/10 text-xs text-white focus:outline-none font-mono"
              />
            </div>

            <div>
              <label className="text-[10px] text-gray-500 uppercase tracking-wider font-semibold">ID del Item especial (Opcional)</label>
              <input
                type="text"
                placeholder="ID de ItemCatalog (ej. 3)"
                value={form.reward_item_id}
                onChange={(e) => setField("reward_item_id", e.target.value)}
                className="w-full mt-1 px-3 py-2 rounded-lg bg-[#1C1C35] border border-white/10 text-xs text-white focus:outline-none font-mono"
              />
            </div>
          </div>

          <button
            onClick={handleCreate}
            disabled={saving}
            className="w-full mt-4 py-2 rounded-xl text-xs font-black bg-gradient-to-r from-purple-600 to-pink-600 text-white hover:from-purple-500 hover:to-pink-500 transition-all duration-200 disabled:opacity-40"
          >
            {saving ? "Generando lote..." : "⚡ Generar y Guardar Lote de Códigos"}
          </button>
        </div>
      ) : (
        <div className="overflow-x-auto rounded-xl border border-white/5">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-[#141428] text-gray-500 text-[11px] uppercase tracking-wider">
                <th className="px-4 py-2 text-left font-semibold">Lote</th>
                <th className="px-4 py-2 text-left font-semibold">Fecha de Creación</th>
                <th className="px-4 py-2 text-right font-semibold">Códigos Generados</th>
                <th className="px-4 py-2 text-right font-semibold">Códigos Canjeados</th>
                <th className="px-4 py-2 text-right font-semibold">Tasa de Canje</th>
                <th className="px-4 py-2 w-20"></th>
              </tr>
            </thead>
            <tbody>
              {batches.length === 0 ? (
                <tr>
                  <td colSpan={6} className="text-center py-8 text-gray-600">
                    No se han creado lotes de códigos promocionales todavía.
                  </td>
                </tr>
              ) : (
                batches.map((b) => {
                  const redeemRate = b.total_codes > 0 
                    ? ((b.redeemed_codes / b.total_codes) * 100).toFixed(1) 
                    : "0";
                  return (
                    <tr key={b.name} className="border-t border-white/5 hover:bg-white/[0.02] transition-colors">
                      <td className="px-4 py-2.5 font-bold text-white font-mono">{b.name}</td>
                      <td className="px-4 py-2.5 text-gray-400 text-xs">
                        {b.created_at ? new Date(b.created_at).toLocaleDateString("es-MX") : "—"}
                      </td>
                      <td className="px-4 py-2.5 text-right font-mono text-gray-200">{b.total_codes.toLocaleString()}</td>
                      <td className="px-4 py-2.5 text-right font-mono text-[#E4007C] font-semibold">{b.redeemed_codes.toLocaleString()}</td>
                      <td className="px-4 py-2.5 text-right">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-black font-mono ${
                          b.redeemed_codes > 0 ? "bg-pink-500/10 text-[#FF8DA1]" : "bg-white/5 text-gray-500"
                        }`}>
                          {redeemRate}%
                        </span>
                      </td>
                      <td className="px-4 py-2.5 text-right">
                        <button
                          onClick={() => handleExport(b.name)}
                          className="flex items-center gap-1 px-2.5 py-1 text-[10px] font-bold rounded-lg bg-[#E4007C]/10 border border-[#E4007C]/20 text-[#FF8DA1] hover:bg-[#E4007C]/20 transition-all duration-200"
                        >
                          <Download size={10} /> CSV
                        </button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
