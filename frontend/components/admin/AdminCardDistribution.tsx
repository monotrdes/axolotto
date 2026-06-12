"use client";
import { API_BASE } from "@/lib/api";

import { useEffect, useState } from "react";
import axios from "axios";
import {
  PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip,
  BarChart, Bar, XAxis, YAxis, CartesianGrid
} from "recharts";
import { Search, Sparkles, Star, Award, Layers } from "lucide-react";

const API = `${API_BASE}`;

const RARITY_COLORS: Record<string, string> = {
  "Legendaria": "#F59E0B", // amber-500
  "Épica":      "#D946EF", // fuchsia-500
  "Rara":       "#06B6D4", // cyan-500
  "Poco Común": "#10B981", // emerald-500
  "Común":      "#64748B", // slate-500
};

const RARITY_BG_CLASSES: Record<string, string> = {
  "Legendaria": "bg-amber-500/10 text-amber-400 border border-amber-500/20",
  "Épica":      "bg-fuchsia-500/10 text-fuchsia-400 border border-fuchsia-500/20",
  "Rara":       "bg-cyan-500/10 text-cyan-400 border border-cyan-500/20",
  "Poco Común": "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20",
  "Común":      "bg-slate-500/10 text-slate-400 border border-slate-500/20",
};

const TOOLTIP_STYLE = {
  contentStyle: { background: "#0D0D1F", border: "1px solid #1C1C35", borderRadius: 8 },
  labelStyle: { color: "#9CA3AF", fontSize: 11 },
  itemStyle: { color: "#E5E7EB", fontSize: 11 },
};

const cardClass = "rounded-2xl p-5 border border-white/5 bg-[#0D0D1F] shadow-lg shadow-black/30";

interface CardMetric {
  id: number;
  name: string;
  numero_loteria: number | null;
  dynamic_rarity: string;
  total_circulation: number;
  inventory_circulation: number;
  board_circulation: number;
  shiny_circulation: number;
  first_edition_circulation: number;
  times_called: number;
}

interface DistributionData {
  total_unique_cards: number;
  total_copies_in_circulation: number;
  total_shiny_in_circulation: number;
  total_first_edition_in_circulation: number;
  catalog_rarity_distribution: Record<string, number>;
  circulation_rarity_distribution: Record<string, number>;
  cards: CardMetric[];
}

export default function AdminCardDistribution({ token }: { token: string | null }) {
  const [data, setData] = useState<DistributionData | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [rarityFilter, setRarityFilter] = useState("all");
  const [sortKey, setSortKey] = useState<keyof CardMetric>("total_circulation");
  const [sortDirection, setSortDirection] = useState<"asc" | "desc">("desc");

  useEffect(() => {
    if (!token) return;
    setLoading(true);
    axios
      .get(`${API}/admin/cards/distribution`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      .then((r) => setData(r.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [token]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-16 gap-2">
        <div className="w-10 h-10 border-4 border-pink-500/30 border-t-pink-500 rounded-full animate-spin"></div>
        <p className="text-gray-500 text-sm font-semibold animate-pulse mt-2">Cargando distribución de cartas…</p>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="text-center py-12">
        <p className="text-red-400 font-bold">Error al cargar la distribución de cartas.</p>
        <p className="text-gray-500 text-xs mt-1">Verifica tus permisos de administrador o la consola del servidor.</p>
      </div>
    );
  }

  // Formatting chart data
  const circulationRarityData = Object.entries(data.circulation_rarity_distribution).map(
    ([rarity, value]) => ({
      name: rarity,
      value,
    })
  );

  const catalogRarityData = Object.entries(data.catalog_rarity_distribution).map(
    ([rarity, count]) => ({
      name: rarity,
      count,
    })
  );

  // Filter & Sort cards
  const filteredCards = data.cards.filter((card) => {
    const matchesSearch =
      card.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (card.numero_loteria !== null && card.numero_loteria.toString() === searchTerm);
    const matchesRarity = rarityFilter === "all" || card.dynamic_rarity === rarityFilter;
    return matchesSearch && matchesRarity;
  });

  const sortedCards = [...filteredCards].sort((a, b) => {
    let aVal = a[sortKey];
    let bVal = b[sortKey];

    // Handle null values
    if (aVal === null) return sortDirection === "asc" ? -1 : 1;
    if (bVal === null) return sortDirection === "asc" ? 1 : -1;

    if (aVal < bVal) return sortDirection === "asc" ? -1 : 1;
    if (aVal > bVal) return sortDirection === "asc" ? 1 : -1;
    return 0;
  });

  const toggleSort = (key: keyof CardMetric) => {
    if (sortKey === key) {
      setSortDirection((prev) => (prev === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(key);
      setSortDirection("desc");
    }
  };

  const renderSortIcon = (key: keyof CardMetric) => {
    if (sortKey !== key) return <span className="opacity-30 ml-1 text-[9px]">⇅</span>;
    return sortDirection === "asc" ? (
      <span className="text-[#FF8DA1] ml-1 text-[9px]">▲</span>
    ) : (
      <span className="text-[#FF8DA1] ml-1 text-[9px]">▼</span>
    );
  };

  const shinyPct = data.total_copies_in_circulation > 0
    ? ((data.total_shiny_in_circulation / data.total_copies_in_circulation) * 100).toFixed(1)
    : "0";

  const firstEdPct = data.total_copies_in_circulation > 0
    ? ((data.total_first_edition_in_circulation / data.total_copies_in_circulation) * 100).toFixed(1)
    : "0";

  const totalCalls = data ? data.cards.reduce((sum, c) => sum + (c.times_called || 0), 0) : 0;
  const avgCalls = data && data.cards.length > 0 ? totalCalls / data.cards.length : 0;

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-black text-white flex items-center gap-2">
            <span>🃏</span> Distribución de Cartas y Rarezas
          </h2>
          <p className="text-gray-400 text-xs mt-1">
            Visualiza el suministro global, las rarezas dinámicas asignadas, estadísticas de cartas cantadas (suertes/saladas) y las copias especiales.
          </p>
        </div>
      </div>

      {/* METRIC CARDS */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className={cardClass}>
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-gray-400 uppercase tracking-wider">Cartas en Circulación</span>
            <div className="p-2 bg-pink-500/10 rounded-lg text-pink-400">
              <Layers size={16} />
            </div>
          </div>
          <h4 className="text-2xl font-black text-white mt-2 font-mono">
            {data.total_copies_in_circulation.toLocaleString()}
          </h4>
          <p className="text-[10px] text-gray-500 mt-1">Total de copias en manos de jugadores</p>
        </div>

        <div className={cardClass}>
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-gray-400 uppercase tracking-wider">Cartas en el Catálogo</span>
            <div className="p-2 bg-purple-500/10 rounded-lg text-purple-400">
              <Award size={16} />
            </div>
          </div>
          <h4 className="text-2xl font-black text-white mt-2 font-mono">
            {data.total_unique_cards}
          </h4>
          <p className="text-[10px] text-gray-500 mt-1">Cartas base de la Lotería Axolotto</p>
        </div>

        <div className={cardClass}>
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-gray-400 uppercase tracking-wider">Copias Especiales Shiny</span>
            <div className="p-2 bg-amber-500/10 rounded-lg text-amber-400">
              <Sparkles size={16} />
            </div>
          </div>
          <h4 className="text-2xl font-black text-white mt-2 font-mono">
            {data.total_shiny_in_circulation.toLocaleString()}
          </h4>
          <p className="text-[10px] text-amber-400/80 mt-1 flex items-center gap-1 font-semibold">
            ✨ {shinyPct}% del total circulante
          </p>
        </div>

        <div className={cardClass}>
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-gray-400 uppercase tracking-wider">1ra Edición (1st Ed.)</span>
            <div className="p-2 bg-emerald-500/10 rounded-lg text-emerald-400">
              <Star size={16} />
            </div>
          </div>
          <h4 className="text-2xl font-black text-white mt-2 font-mono">
            {data.total_first_edition_in_circulation.toLocaleString()}
          </h4>
          <p className="text-[10px] text-emerald-400/80 mt-1 flex items-center gap-1 font-semibold">
            ⭐ {firstEdPct}% del total circulante
          </p>
        </div>
      </div>

      {/* CHARTS GRAPHICS */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Circulation Rarity Pie Chart */}
        <div className={cardClass}>
          <h3 className="text-sm font-black text-gray-200 mb-4 flex items-center gap-2">
            <span className="w-2.5 h-2.5 bg-pink-500 rounded-full"></span>
            Rareza Dinámica del Circulante (Copias de Cartas)
          </h3>
          <div className="h-[250px] w-full flex items-center justify-center">
            {data.total_copies_in_circulation === 0 ? (
              <p className="text-gray-500 text-sm">No hay cartas en circulación todavía.</p>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={circulationRarityData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={90}
                    paddingAngle={3}
                    dataKey="value"
                  >
                    {circulationRarityData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={RARITY_COLORS[entry.name] || "#FFF"} />
                    ))}
                  </Pie>
                  <Tooltip {...TOOLTIP_STYLE} />
                  <Legend
                    verticalAlign="bottom"
                    iconSize={10}
                    formatter={(value) => <span className="text-xs text-gray-400 font-bold">{value}</span>}
                  />
                </PieChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        {/* Catalog Rarity Bar Chart */}
        <div className={cardClass}>
          <h3 className="text-sm font-black text-gray-200 mb-4 flex items-center gap-2">
            <span className="w-2.5 h-2.5 bg-blue-500 rounded-full"></span>
            Asignación de Rareza en el Catálogo (# de Modelos de Cartas)
          </h3>
          <div className="h-[250px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={catalogRarityData} margin={{ top: 10, right: 10, left: -25, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1C1C35" />
                <XAxis dataKey="name" tick={{ fill: "#6B7280", fontSize: 10, fontWeight: "bold" }} />
                <YAxis tick={{ fill: "#6B7280", fontSize: 10 }} allowDecimals={false} />
                <Tooltip {...TOOLTIP_STYLE} />
                <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                  {catalogRarityData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={RARITY_COLORS[entry.name] || "#FFF"} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* DETAILED CARD CIRCULATION TABLE */}
      <div className={cardClass + " overflow-hidden"}>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-5">
          <h3 className="text-sm font-black text-gray-200">
            📊 Inventario e Historial de Suministro por Carta
          </h3>

          {/* Filters Bar */}
          <div className="flex flex-wrap items-center gap-2">
            {/* Search Input */}
            <div className="relative">
              <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
              <input
                type="text"
                placeholder="Buscar por nombre o #"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-48 bg-slate-900 border border-white/5 rounded-xl py-2 pl-9 pr-4 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-pink-500/50 transition-colors"
              />
            </div>

            {/* Rarity Select */}
            <select
              value={rarityFilter}
              onChange={(e) => setRarityFilter(e.target.value)}
              className="bg-slate-900 border border-white/5 rounded-xl py-2 px-3 text-xs text-white focus:outline-none focus:border-pink-500/50 cursor-pointer"
            >
              <option value="all">Todas las Rarezas</option>
              <option value="Legendaria">Legendaria</option>
              <option value="Épica">Épica</option>
              <option value="Rara">Rara</option>
              <option value="Poco Común">Poco Común</option>
              <option value="Común">Común</option>
            </select>
          </div>
        </div>

        {/* Table Container */}
        <div className="overflow-x-auto rounded-xl border border-white/5">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-900/60 border-b border-white/5 text-[10px] font-extrabold uppercase text-slate-400 tracking-wider">
                <th className="py-3 px-4 w-16 cursor-pointer hover:text-white" onClick={() => toggleSort("numero_loteria")}>
                  # {renderSortIcon("numero_loteria")}
                </th>
                <th className="py-3 px-4 cursor-pointer hover:text-white" onClick={() => toggleSort("name")}>
                  Carta {renderSortIcon("name")}
                </th>
                <th className="py-3 px-4 w-28 cursor-pointer hover:text-white" onClick={() => toggleSort("dynamic_rarity")}>
                  Rareza {renderSortIcon("dynamic_rarity")}
                </th>
                <th className="py-3 px-4 w-28 cursor-pointer hover:text-white text-right" onClick={() => toggleSort("inventory_circulation")}>
                  Inventario {renderSortIcon("inventory_circulation")}
                </th>
                <th className="py-3 px-4 w-28 cursor-pointer hover:text-white text-right" onClick={() => toggleSort("board_circulation")}>
                  En Tablas {renderSortIcon("board_circulation")}
                </th>
                <th className="py-3 px-4 w-28 cursor-pointer hover:text-white text-right" onClick={() => toggleSort("total_circulation")}>
                  Gran Total {renderSortIcon("total_circulation")}
                </th>
                <th className="py-3 px-4 w-28 cursor-pointer hover:text-white text-right" onClick={() => toggleSort("times_called")}>
                  Cantada {renderSortIcon("times_called")}
                </th>
                <th className="py-3 px-4 w-28 cursor-pointer hover:text-white text-right" onClick={() => toggleSort("shiny_circulation")}>
                  Shiny {renderSortIcon("shiny_circulation")}
                </th>
                <th className="py-3 px-4 w-28 cursor-pointer hover:text-white text-right" onClick={() => toggleSort("first_edition_circulation")}>
                  1st Ed. {renderSortIcon("first_edition_circulation")}
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5 text-xs text-slate-300 font-semibold font-mono">
              {sortedCards.length === 0 ? (
                <tr>
                  <td colSpan={9} className="py-8 text-center text-gray-500 italic bg-slate-950/20">
                    No se encontraron cartas que coincidan con la búsqueda.
                  </td>
                </tr>
              ) : (
                sortedCards.map((card) => {
                  const isLucky = totalCalls > 0 && card.times_called > avgCalls * 1.15;
                  const isSalty = totalCalls > 0 && card.times_called < avgCalls * 0.85;
                  return (
                    <tr key={card.id} className="hover:bg-white/[0.02] transition-colors">
                      <td className="py-3 px-4 text-slate-500 font-bold">#{card.numero_loteria || "?"}</td>
                      <td className="py-3 px-4 text-white font-bold">{card.name}</td>
                      <td className="py-3 px-4">
                        <span className={`px-2 py-0.5 rounded-[4px] text-[9px] font-black uppercase tracking-wider ${
                          RARITY_BG_CLASSES[card.dynamic_rarity] || "bg-gray-500/10 text-gray-400"
                        }`}>
                          {card.dynamic_rarity}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-right text-slate-300">
                        {card.inventory_circulation?.toLocaleString() || "0"}
                      </td>
                      <td className="py-3 px-4 text-right text-purple-400">
                        {card.board_circulation?.toLocaleString() || "0"}
                      </td>
                      <td className="py-3 px-4 text-right font-bold text-white bg-white/[0.01]">
                        {card.total_circulation.toLocaleString()}
                      </td>
                      <td className="py-3 px-4 text-right">
                        <div className="flex flex-col items-end">
                          <span className="font-bold text-pink-400">
                            📢 {card.times_called?.toLocaleString() || "0"}
                          </span>
                          {isLucky && (
                            <span className="text-[9px] text-amber-400 font-extrabold uppercase tracking-tight flex items-center gap-0.5">
                              🔥 Suertuda
                            </span>
                          )}
                          {isSalty && (
                            <span className="text-[9px] text-cyan-400 font-extrabold uppercase tracking-tight flex items-center gap-0.5">
                              🧂 Salada
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="py-3 px-4 text-right text-amber-400">
                        {card.shiny_circulation > 0 ? `✨ ${card.shiny_circulation.toLocaleString()}` : "0"}
                      </td>
                      <td className="py-3 px-4 text-right text-emerald-400">
                        {card.first_edition_circulation > 0 ? `⭐ ${card.first_edition_circulation.toLocaleString()}` : "0"}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
