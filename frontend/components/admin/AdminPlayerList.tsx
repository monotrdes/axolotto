"use client";
import { API_BASE } from "@/lib/api";




import { useEffect, useState, useCallback } from "react";
import axios from "axios";
import AdminPlayerDetail from "./AdminPlayerDetail";



const API = `${API_BASE}`;

const VIP_BADGE: Record<string, { bg: string; text: string; label: string }> = {
  coral:   { bg: "bg-orange-500/20", text: "text-orange-400", label: "🪸 Coral"   },
  dorado:  { bg: "bg-yellow-500/20", text: "text-yellow-400", label: "✨ Dorado"  },
  axolite: { bg: "bg-purple-500/20", text: "text-purple-400", label: "🌟 Axolite" },
};

type SortKey = "nickname" | "email" | "frj" | "axf" | "axo_count" | "board_count" | "total_games" | "win_rate" | "created_at";
type SortDir = "asc" | "desc";

const COLUMNS: { label: string; key: SortKey | null }[] = [
  { label: "Nickname",   key: "nickname"    },
  { label: "Email",      key: "email"       },
  { label: "VIP",        key: null          },
  { label: "FRJ",        key: "frj"         },
  { label: "AXF",        key: "axf"         },
  { label: "Axolotitos", key: "axo_count"   },
  { label: "Tablas",     key: "board_count" },
  { label: "Partidas",   key: "total_games" },
  { label: "Win%",       key: "win_rate"    },
  { label: "Registro",   key: "created_at"  },
  { label: "",           key: null          },
];

export default function AdminPlayerList({ token }: { token: string | null }) {
  const [players, setPlayers] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState("");
  const [sortKey, setSortKey] = useState<SortKey>("created_at");
  const [sortDir, setSortDir] = useState<SortDir>("desc");
  const [page, setPage] = useState(1);
  const [selectedDid, setSelectedDid] = useState<string | null>(null);

  const sort = `${sortKey}_${sortDir}`;

  function handleSortClick(key: SortKey | null) {
    if (!key) return;
    if (sortKey === key) {
      setSortDir(d => d === "asc" ? "desc" : "asc");
    } else {
      setSortKey(key);
      setSortDir("desc");
    }
    setPage(1);
  }

  const fetchPlayers = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    try {
      const params = new URLSearchParams({ sort, page: String(page), limit: "50" });
      if (search) params.set("search", search);
      const r = await axios.get(`${API}/admin/players?${params}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setPlayers(r.data.players);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, [token, search, sort, page]);

  useEffect(() => { fetchPlayers(); }, [fetchPlayers]);

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-black text-white">👥 Jugadores</h2>

      <div className="flex flex-wrap gap-2">
        <input
          type="text"
          placeholder="Buscar por nickname, email o DID…"
          value={search}
          onChange={e => { setSearch(e.target.value); setPage(1); }}
          className="flex-1 min-w-[200px] px-3 py-2 rounded-lg bg-[#1C1C35] border border-white/10 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-[#E4007C]/50"
        />
      </div>

      <div className="overflow-x-auto rounded-xl border border-white/5">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-[#141428] text-gray-500 text-[11px] uppercase tracking-wider">
              {COLUMNS.map((col, i) => {
                const isActive = col.key && sortKey === col.key;
                return (
                  <th
                    key={i}
                    onClick={() => handleSortClick(col.key)}
                    className={`px-3 py-2 text-left font-semibold whitespace-nowrap select-none ${
                      col.key ? "cursor-pointer hover:text-gray-300 transition-colors" : ""
                    } ${isActive ? "text-[#FF8DA1]" : ""}`}
                  >
                    {col.label}
                    {isActive && (
                      <span className="ml-1 opacity-80">{sortDir === "asc" ? "↑" : "↓"}</span>
                    )}
                  </th>
                );
              })}
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={11} className="text-center py-8 text-gray-600 animate-pulse">Cargando…</td></tr>
            ) : players.length === 0 ? (
              <tr><td colSpan={11} className="text-center py-8 text-gray-700">Sin resultados.</td></tr>
            ) : players.map(p => {
              const vip = p.vip_tier ? VIP_BADGE[p.vip_tier] : null;
              return (
                <tr key={p.privy_did} className="border-t border-white/5 hover:bg-white/[0.02] transition-colors">
                  <td className="px-3 py-2 font-semibold text-white whitespace-nowrap">
                    {p.nickname || <span className="text-gray-700">—</span>}
                    {!p.is_active && (
                      <span className="ml-1.5 px-1.5 py-0.5 rounded bg-red-500/20 text-red-400 text-[9px] font-black uppercase tracking-wider">
                        Susp
                      </span>
                    )}
                  </td>
                  <td className="px-3 py-2 text-gray-400 text-xs">{p.email || <span className="text-gray-700">—</span>}</td>
                  <td className="px-3 py-2">
                    {vip ? (
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-black ${vip.bg} ${vip.text}`}>{vip.label}</span>
                    ) : <span className="text-gray-700 text-xs">—</span>}
                  </td>
                  <td className="px-3 py-2 tabular-nums text-amber-400 font-semibold">{p.frj.toLocaleString()}</td>
                  <td className="px-3 py-2 tabular-nums text-[#E4007C] font-semibold">{p.axf.toLocaleString()}</td>
                  <td className="px-3 py-2 tabular-nums text-teal-400">{p.axo_count}</td>
                  <td className="px-3 py-2 tabular-nums text-indigo-400">{p.board_count}</td>
                  <td className="px-3 py-2 tabular-nums text-gray-300">{p.total_games}</td>
                  <td className="px-3 py-2 tabular-nums text-gray-300">{p.win_rate}%</td>
                  <td className="px-3 py-2 text-gray-600 text-xs whitespace-nowrap">
                    {p.created_at ? new Date(p.created_at).toLocaleDateString("es-MX") : "—"}
                  </td>
                  <td className="px-3 py-2">
                    <button
                      onClick={() => setSelectedDid(p.privy_did)}
                      className="px-2 py-1 text-xs rounded-md bg-[#E4007C]/20 text-[#FF8DA1] hover:bg-[#E4007C]/40 transition-colors"
                    >
                      Ver
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <div className="flex gap-2 justify-end items-center">
        <button
          onClick={() => setPage(p => Math.max(1, p - 1))}
          disabled={page === 1}
          className="px-3 py-1 text-sm rounded-lg bg-[#1C1C35] border border-white/10 disabled:opacity-30 hover:border-white/20 transition-colors"
        >
          ← Anterior
        </button>
        <span className="px-3 py-1 text-sm text-gray-500">Página {page}</span>
        <button
          onClick={() => setPage(p => p + 1)}
          disabled={players.length < 50}
          className="px-3 py-1 text-sm rounded-lg bg-[#1C1C35] border border-white/10 disabled:opacity-30 hover:border-white/20 transition-colors"
        >
          Siguiente →
        </button>
      </div>

      {selectedDid && (
        <AdminPlayerDetail
          privy_did={selectedDid}
          token={token}
          onClose={() => setSelectedDid(null)}
        />
      )}
    </div>
  );
}
