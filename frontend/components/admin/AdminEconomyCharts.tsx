"use client";
import { API_BASE } from "@/lib/api";




import { useEffect, useState } from "react";
import axios from "axios";
import {


  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer,
  BarChart, Bar, PieChart, Pie, Cell, Legend, CartesianGrid,
} from "recharts";

const API = `${API_BASE}`;

const PIE_COLORS: Record<string, string> = {
  coral: "#f97316",
  dorado: "#eab308",
  axolite: "#8b5cf6",
  sin_vip: "#374151",
};

const TOOLTIP_STYLE = {
  contentStyle: { background: "#0D0D1F", border: "1px solid #1C1C35", borderRadius: 8 },
  labelStyle: { color: "#9CA3AF", fontSize: 11 },
  itemStyle: { color: "#E5E7EB", fontSize: 11 },
};

const cardClass = "rounded-xl p-4 border border-white/5 bg-[#141428]";

export default function AdminEconomyCharts({ token }: { token: string | null }) {
  const [charts, setCharts] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<string>("webitos");
  const [sortKey, setSortKey] = useState<string>("count");
  const [sortDirection, setSortDirection] = useState<"asc" | "desc">("desc");

  const handleSort = (key: string) => {
    if (sortKey === key) {
      setSortDirection(prev => (prev === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(key);
      setSortDirection("desc");
    }
  };

  const renderSortIcon = (key: string) => {
    let checkKey = key;
    if (key === "vol_axg") checkKey = "volume_axg";
    if (key === "vol_cor") checkKey = "volume_gal";
    
    if (sortKey !== checkKey) return <span className="opacity-30 ml-1 text-[9px]">⇅</span>;
    return sortDirection === "asc" ? (
      <span className="text-pink-500 ml-1 text-[9px]">▲</span>
    ) : (
      <span className="text-pink-500 ml-1 text-[9px]">▼</span>
    );
  };

  useEffect(() => {
    if (!token) return;
    axios.get(`${API}/admin/economy/charts`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => setCharts(r.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [token]);

  if (loading) return <p className="text-gray-500 animate-pulse py-8">Cargando gráficas…</p>;
  if (!charts) return <p className="text-red-400 py-8">Error cargando datos.</p>;

  return (
    <div className="space-y-6">
      <h2 className="text-lg font-black text-white">💹 Economía</h2>

      <div className={cardClass}>
        <h3 className="text-sm font-semibold text-gray-300 mb-3">🪙 Volumen FRJ diario (30 días)</h3>
        {charts.daily_gal_volume.length === 0 ? (
          <p className="text-gray-700 text-sm text-center py-8">Sin datos aún.</p>
        ) : (
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={charts.daily_gal_volume}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1C1C35" />
              <XAxis dataKey="day" tick={{ fill: "#4B5563", fontSize: 10 }} />
              <YAxis tick={{ fill: "#4B5563", fontSize: 10 }} />
              <Tooltip {...TOOLTIP_STYLE} />
              <Line type="monotone" dataKey="volume" stroke="#F59E0B" strokeWidth={2} dot={false} name="FRJ" />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>

      <div className={cardClass}>
        <h3 className="text-sm font-semibold text-gray-300 mb-3">⚔️ Partidas Multijugador diarias (30 días)</h3>
        {charts.daily_mp_games.length === 0 ? (
          <p className="text-gray-700 text-sm text-center py-8">Sin datos aún.</p>
        ) : (
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={charts.daily_mp_games}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1C1C35" />
              <XAxis dataKey="day" tick={{ fill: "#4B5563", fontSize: 10 }} />
              <YAxis tick={{ fill: "#4B5563", fontSize: 10 }} />
              <Tooltip {...TOOLTIP_STYLE} />
              <Line type="monotone" dataKey="games" stroke="#34D399" strokeWidth={2} dot={false} name="Partidas" />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className={cardClass}>
          <h3 className="text-sm font-semibold text-gray-300 mb-3">👑 Distribución VIP Activos</h3>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie
                data={charts.vip_distribution}
                dataKey="count"
                nameKey="tier"
                cx="50%"
                cy="50%"
                outerRadius={70}
              >
                {charts.vip_distribution.map((entry: any) => (
                  <Cell key={entry.tier} fill={PIE_COLORS[entry.tier] || "#6B7280"} />
                ))}
              </Pie>
              <Legend formatter={(val) => <span style={{ color: "#9CA3AF", fontSize: 11 }}>{val}</span>} />
              <Tooltip {...TOOLTIP_STYLE} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className={cardClass}>
          <h3 className="text-sm font-semibold text-gray-300 mb-3">📊 Tipos de Transacción</h3>
          {charts.tx_type_breakdown.length === 0 ? (
            <p className="text-gray-700 text-sm text-center py-8">Sin transacciones aún.</p>
          ) : (
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={charts.tx_type_breakdown} layout="vertical" margin={{ left: 10 }}>
                <XAxis type="number" tick={{ fill: "#4B5563", fontSize: 10 }} />
                <YAxis dataKey="tx_type" type="category" tick={{ fill: "#9CA3AF", fontSize: 10 }} width={100} />
                <Tooltip {...TOOLTIP_STYLE} />
                <Bar dataKey="count" fill="#E4007C" radius={[0, 4, 4, 0]} name="Cantidad" />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      {/* --- DETAILED SALES BREAKDOWN --- */}
      {(() => {
        const breakdown = charts?.detailed_breakdown || {
          webitos: [],
          boosters: [],
          gashapon: {},
          capsulas: {},
          vip: [],
          other_items: [],
          currency_exchange: {},
        };

        // Convert Gashapon to sortable array
        const gashaponData = [
          { name: "Gashapón Común (FRJ)", count: breakdown.gashapon?.common_gal?.count || 0, volume_gal: breakdown.gashapon?.common_gal?.volume || 0, volume_axg: 0, method: "FRJ" },
          { name: "Gashapón Común (Ficha)", count: breakdown.gashapon?.common_ticket?.count || 0, volume_gal: 0, volume_axg: 0, method: "Ficha" },
          { name: "Gashapón Premium (FRJ)", count: breakdown.gashapon?.premium_gal?.count || 0, volume_gal: breakdown.gashapon?.premium_gal?.volume || 0, volume_axg: 0, method: "FRJ" },
          { name: "Gashapón Premium (Ficha)", count: breakdown.gashapon?.premium_ticket?.count || 0, volume_gal: 0, volume_axg: 0, method: "Ficha" },
        ];

        // Convert Capsules to sortable array
        const capsulasData = [
          { name: "Cápsula de Bronce", count: breakdown.capsulas?.bronce?.count || 0, volume_gal: breakdown.capsulas?.bronce?.volume || 0, volume_axg: 0, method: "FRJ" },
          { name: "Cápsula de Plata", count: breakdown.capsulas?.plata?.count || 0, volume_gal: breakdown.capsulas?.plata?.volume || 0, volume_axg: 0, method: "FRJ" },
          { name: "Cápsula de Oro", count: breakdown.capsulas?.oro?.count || 0, volume_gal: breakdown.capsulas?.oro?.volume || 0, volume_axg: 0, method: "FRJ" },
          { name: "Cápsula Diaria Gratis", count: breakdown.capsulas?.diaria?.count || 0, volume_gal: 0, volume_axg: 0, method: "Gratis" },
        ];

        // Normalize lists to ensure consistent sorting attributes
        const normalizedWebitos = (breakdown.webitos || []).map((w: any) => ({
          name: w.name,
          count: w.count || 0,
          volume_axg: w.axg_vol || 0,
          volume_gal: w.gal_vol || 0,
        }));

        const normalizedBoosters = (breakdown.boosters || []).map((b: any) => ({
          name: b.name,
          count: b.count || 0,
          volume_axg: b.axg_vol || 0,
          volume_gal: b.gal_vol || 0,
        }));

        const normalizedVIP = (breakdown.vip || []).map((v: any) => ({
          name: `Pase VIP ${v.tier}`,
          count: v.count || 0,
          volume_axg: v.axg_vol || 0,
          volume_gal: 0,
        }));

        const normalizedOthers = (breakdown.other_items || []).map((o: any) => ({
          name: o.name,
          count: o.count || 0,
          volume_axg: o.axg_vol || 0,
          volume_gal: o.gal_vol || 0,
          type: o.type || "OTHER",
        }));

        // Pick dataset based on tab
        let currentDataset: any[] = [];
        if (activeTab === "webitos") currentDataset = normalizedWebitos;
        else if (activeTab === "boosters") currentDataset = normalizedBoosters;
        else if (activeTab === "gashapon") currentDataset = [...gashaponData, ...capsulasData];
        else if (activeTab === "vip") currentDataset = normalizedVIP;
        else if (activeTab === "others") currentDataset = normalizedOthers;

        // Sorting logic
        const sortedData = [...currentDataset].sort((a, b) => {
          let key = sortKey;
          if (key === "vol_axg") key = "volume_axg";
          if (key === "vol_cor") key = "volume_gal";

          let valA = a[key];
          let valB = b[key];
          if (valA === undefined) valA = 0;
          if (valB === undefined) valB = 0;

          if (typeof valA === "string") {
            return sortDirection === "asc" ? valA.localeCompare(valB) : valB.localeCompare(valA);
          }
          return sortDirection === "asc" ? valA - valB : valB - valA;
        });

        const maxCount = Math.max(...currentDataset.map(d => d.count), 1);

        return (
          <div className={`${cardClass} space-y-4`}>
            <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between border-b border-white/5 pb-3">
              <div>
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  🛒 Desglose Detallado de Ventas <span className="text-xs font-normal text-gray-500">(Histórico total)</span>
                </h3>
                <p className="text-xs text-gray-400">Analiza qué artículos se compran más y su volumen de ingresos.</p>
              </div>

              {/* Tab Selector */}
              <div className="flex flex-wrap gap-1 mt-3 lg:mt-0 bg-[#0d0d1f] p-1 rounded-lg border border-white/5">
                {[
                  { id: "webitos", label: "🥚 Webitos" },
                  { id: "boosters", label: "📦 Sobres" },
                  { id: "gashapon", label: "🎰 Gashapón / Cápsulas" },
                  { id: "vip", label: "👑 VIP" },
                  { id: "others", label: "🛠️ Consumibles / Tableros" },
                ].map(tab => (
                  <button
                    key={tab.id}
                    onClick={() => {
                      setActiveTab(tab.id);
                      setSortKey("count");
                      setSortDirection("desc");
                    }}
                    className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                      activeTab === tab.id
                        ? "bg-gradient-to-r from-pink-500 to-violet-600 text-white shadow-lg"
                        : "text-gray-400 hover:text-white hover:bg-white/5"
                    }`}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Table layout */}
            {sortedData.length === 0 ? (
              <p className="text-gray-500 text-sm text-center py-8">No hay registros de compras en esta categoría para los últimos 30 días.</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="border-b border-white/5 text-gray-400 font-semibold">
                      <th className="pb-2 cursor-pointer select-none hover:text-white" onClick={() => handleSort("name")}>
                        Artículo {renderSortIcon("name")}
                      </th>
                      {activeTab === "others" && <th className="pb-2">Tipo</th>}
                      <th className="pb-2 cursor-pointer select-none text-right hover:text-white" onClick={() => handleSort("count")}>
                        Ventas {renderSortIcon("count")}
                      </th>
                      <th className="pb-2 text-right px-4 w-32">Proporción</th>
                      {activeTab !== "gashapon" && (
                        <th className="pb-2 cursor-pointer select-none text-right hover:text-white font-mono" onClick={() => handleSort("vol_axg")}>
                          Volumen AXF {renderSortIcon("vol_axg")}
                        </th>
                      )}
                      {activeTab !== "vip" && (
                        <th className="pb-2 cursor-pointer select-none text-right hover:text-white font-mono" onClick={() => handleSort("vol_cor")}>
                          Volumen FRJ {renderSortIcon("vol_cor")}
                        </th>
                      )}
                    </tr>
                  </thead>
                  <tbody>
                    {sortedData.map((row, idx) => {
                      const pct = Math.min(100, Math.round((row.count / maxCount) * 100));
                      return (
                        <tr key={idx} className="border-b border-white/5 hover:bg-white/[0.02] transition-colors">
                          <td className="py-3 font-semibold text-gray-200">{row.name}</td>
                          {activeTab === "others" && (
                            <td className="py-3">
                              <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                                row.type === "BOARD"
                                  ? "bg-blue-500/10 text-blue-400 border border-blue-500/20"
                                  : "bg-purple-500/10 text-purple-400 border border-purple-500/20"
                              }`}>
                                {row.type}
                              </span>
                            </td>
                          )}
                          <td className="py-3 text-right font-mono font-bold text-white">{row.count.toLocaleString()}</td>
                          <td className="py-3 px-4 w-32">
                            <div className="w-full bg-white/5 rounded-full h-1.5 overflow-hidden">
                              <div
                                className="bg-gradient-to-r from-pink-500 to-violet-600 h-1.5 rounded-full"
                                style={{ width: `${pct}%` }}
                              />
                            </div>
                          </td>
                          {activeTab !== "gashapon" && (
                            <td className="py-3 text-right font-mono">
                              {row.volume_axg > 0 ? (
                                <span className="text-yellow-400 font-bold bg-yellow-400/5 px-2 py-1 rounded border border-yellow-400/10">
                                  {row.volume_axg.toLocaleString()} AXF
                                </span>
                              ) : (
                                <span className="text-gray-600">-</span>
                              )}
                            </td>
                          )}
                          {activeTab !== "vip" && (
                            <td className="py-3 text-right font-mono">
                              {row.volume_gal > 0 ? (
                                <span className="text-emerald-400 font-bold bg-emerald-400/5 px-2 py-1 rounded border border-emerald-400/10">
                                  {row.volume_gal.toLocaleString()} FRJ
                                </span>
                              ) : (
                                <span className="text-gray-600">-</span>
                              )}
                            </td>
                          )}
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}

            {/* Currency Exchange footer summary */}
            {breakdown.currency_exchange && breakdown.currency_exchange.count > 0 && (
              <div className="bg-[#0b0b17] border border-white/5 rounded-lg p-3 mt-4 text-[11px] text-gray-400 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                <span className="flex items-center gap-2">
                  🔀 <strong className="text-gray-200">Intercambio de divisas:</strong> Se realizaron {breakdown.currency_exchange.count} transacciones de recarga de FRJ usando AXF.
                </span>
                <div className="flex gap-3 font-mono">
                  <span className="text-yellow-400">Total AXF Gastado: {breakdown.currency_exchange.axg_spent.toLocaleString()} AXF</span>
                  <span className="text-emerald-400">Total FRJ Recibido: {breakdown.currency_exchange.gal_received.toLocaleString()} FRJ</span>
                </div>
              </div>
            )}
          </div>
        );
      })()}
    </div>
  );
}