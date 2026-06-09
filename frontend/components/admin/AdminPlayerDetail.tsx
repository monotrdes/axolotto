"use client";
import { API_BASE } from "@/lib/api";




import { useEffect, useState } from "react";
import axios from "axios";



const API = `${API_BASE}`;

const TX_BADGE: Record<string, string> = {
  deposit: "bg-green-500/20 text-green-400",
  reward: "bg-teal-500/20 text-teal-400",
  p2p_send: "bg-orange-500/20 text-orange-400",
  p2p_receive: "bg-blue-500/20 text-blue-400",
  market_buy: "bg-purple-500/20 text-purple-400",
  market_sell: "bg-purple-500/20 text-purple-400",
  burn: "bg-red-500/20 text-red-400",
  vip_gal_expired: "bg-gray-500/20 text-gray-400",
};

function StatBar({ label, value, max = 100 }: { label: string; value: number; max?: number }) {
  return (
    <div className="flex items-center gap-2">
      <span className="text-gray-600 text-[10px] w-16 text-right capitalize">{label}</span>
      <div className="flex-1 h-1.5 bg-white/5 rounded-full overflow-hidden">
        <div
          className="h-full rounded-full"
          style={{ width: `${Math.min(100, (value / max) * 100)}%`, background: "#E4007C" }}
        />
      </div>
      <span className="text-gray-400 text-[10px] w-8 text-right tabular-nums">{value}</span>
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div>
      <h3 className="text-[10px] font-bold text-gray-500 uppercase tracking-wider mb-2">{title}</h3>
      {children}
    </div>
  );
}

export default function AdminPlayerDetail({
  privy_did, token, onClose,
}: { privy_did: string; token: string | null; onClose: () => void }) {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) return;
    axios.get(`${API}/admin/players/${privy_did}`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => setData(r.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [privy_did, token]);

  return (
    <>
      <div className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm" onClick={onClose} />
      <div className="fixed right-0 top-0 bottom-0 z-50 w-full max-w-lg bg-[#0D0D1F] border-l border-white/5 overflow-y-auto">
        <div className="sticky top-0 bg-[#0D0D1F]/95 backdrop-blur-md border-b border-white/5 flex items-center justify-between px-5 py-3">
          <span className="font-black text-white">Detalle de Jugador</span>
          <button onClick={onClose} aria-label="Cerrar panel" className="text-gray-500 hover:text-white text-xl leading-none transition-colors">✕</button>
        </div>

        {loading ? (
          <p className="text-center text-gray-600 mt-20 animate-pulse">Cargando datos…</p>
        ) : !data ? (
          <p className="text-center text-red-400 mt-20">Error cargando datos.</p>
        ) : (
          <div className="p-5 space-y-6">
            <Section title="Jugador">
              <div className="space-y-1">
                <p className="text-xl font-black text-white">{data.user.nickname || "Sin nickname"}</p>
                <p className="text-[10px] text-gray-600 font-mono break-all">{data.user.privy_did}</p>
                {data.user.email && <p className="text-xs text-gray-500">{data.user.email}</p>}
                {data.user.wallet_address && <p className="text-[10px] text-gray-700 font-mono break-all">{data.user.wallet_address}</p>}
                {data.user.vip_tier && (
                  <span className="inline-block px-2 py-0.5 rounded-full text-xs font-black bg-purple-500/20 text-purple-300">
                    👑 {data.user.vip_tier.toUpperCase()} — vence {new Date(data.user.vip_expires_at).toLocaleDateString("es-MX")}
                  </span>
                )}
                <p className="text-[10px] text-gray-600">Desde: {data.user.created_at ? new Date(data.user.created_at).toLocaleDateString("es-MX") : "—"}</p>
              </div>
            </Section>

            <Section title="💰 Economía">
              {data.wallet ? (
                <div className="grid grid-cols-2 gap-2">
                  <div className="bg-[#141428] rounded-lg p-3">
                    <div className="text-amber-400 font-black tabular-nums text-lg">{data.wallet.frj.toLocaleString()}</div>
                    <div className="text-gray-600 text-[10px]">FRJ (Frijolito)</div>
                  </div>
                  <div className="bg-[#141428] rounded-lg p-3">
                    <div className="text-[#E4007C] font-black tabular-nums text-lg">{data.wallet.axf.toLocaleString()}</div>
                    <div className="text-gray-600 text-[10px]">AXF (Axoficha)</div>
                  </div>
                  <div className="bg-[#141428] rounded-lg p-3 col-span-2 grid grid-cols-4 gap-1 text-center">
                    {["comun","raro","epico","legendario"].map(r => (
                      <div key={r}>
                        <div className="text-white font-semibold text-sm">{data.wallet[`frag_${r}`]}</div>
                        <div className="text-gray-700 text-[9px] capitalize">{r}</div>
                      </div>
                    ))}
                  </div>
                </div>
              ) : <p className="text-gray-600 text-sm">Sin wallet registrada.</p>}
            </Section>

            <Section title={`🦎 Axolotitos (${data.axolotitos.length})`}>
              <div className="space-y-3">
                {data.axolotitos.length === 0 ? (
                  <p className="text-gray-700 text-sm">Sin axolotitos.</p>
                ) : data.axolotitos.map((a: any) => (
                  <div key={a.id} className="bg-[#141428] rounded-xl p-3 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-white text-sm">{a.name}</span>
                      <span className="text-[10px] px-2 py-0.5 rounded-full bg-white/5 text-gray-400">
                        Nv {a.level} · {a.status}
                      </span>
                    </div>
                    <div className="space-y-1">
                      {Object.entries(a.stats as Record<string, number>).map(([k, v]) => (
                        <StatBar key={k} label={k} value={v} />
                      ))}
                    </div>
                    <div className="text-[10px] text-gray-600">
                      Escrow: {a.escrow_balance_gal} FRJ · Streak: {a.cpu_win_streak}
                    </div>
                  </div>
                ))}
              </div>
            </Section>

            <Section title={`🪆 Tablas (${data.boards.length})`}>
              {data.boards.length === 0 ? (
                <p className="text-gray-700 text-sm">Sin tablas.</p>
              ) : (
                <div className="grid grid-cols-2 gap-2">
                  {data.boards.map((b: any) => (
                    <div key={b.id} className="bg-[#141428] rounded-lg p-3">
                      <div className="font-semibold text-white text-sm truncate">{b.name}</div>
                      <div className="text-gray-500 text-[10px]">Nv {b.level} · {b.card_count} cartas</div>
                      <div className="text-gray-400 text-[11px] tabular-nums">{b.games_played} pts · {b.win_rate}% win</div>
                      {b.is_dead && <span className="text-red-400 text-[10px]">💀 Destruida</span>}
                    </div>
                  ))}
                </div>
              )}
            </Section>

            <Section title="📋 Últimas 50 Transacciones">
              <div className="space-y-0.5 max-h-64 overflow-y-auto">
                {data.recent_transactions.length === 0 ? (
                  <p className="text-gray-700 text-sm">Sin transacciones.</p>
                ) : data.recent_transactions.map((t: any) => (
                  <div key={t.id} className="flex items-center gap-2 text-[11px] py-1 border-b border-white/[0.03]">
                    <span className={`px-1.5 py-0.5 rounded text-[9px] font-black shrink-0 ${TX_BADGE[t.tx_type] || "bg-white/5 text-gray-400"}`}>
                      {t.tx_type}
                    </span>
                    <span className="flex-1 text-gray-600 truncate">{t.description || t.currency}</span>
                    <span className={`tabular-nums font-semibold shrink-0 ${t.amount >= 0 ? "text-green-400" : "text-red-400"}`}>
                      {t.amount > 0 ? "+" : ""}{t.amount}
                    </span>
                    <span className="text-gray-700 text-[9px] shrink-0">
                      {t.created_at ? new Date(t.created_at).toLocaleDateString("es-MX") : ""}
                    </span>
                  </div>
                ))}
              </div>
            </Section>

            <Section title="⚔️ Últimas 20 Partidas Multi">
              {data.multiplayer_history.length === 0 ? (
                <p className="text-gray-700 text-sm">Sin historial multijugador.</p>
              ) : (
                <div className="space-y-0.5">
                  {data.multiplayer_history.map((g: any) => (
                    <div key={g.id} className="flex items-center gap-2 text-[11px] py-1 border-b border-white/[0.03]">
                      <span className={g.outcome === "Victoria" ? "text-green-400" : "text-red-400"}>
                        {g.outcome === "Victoria" ? "🏆" : "💔"}
                      </span>
                      <span className="text-gray-500 flex-1 truncate">{g.room_name} · {g.axo_name}</span>
                      <span className={`tabular-nums font-semibold ${g.net_gal >= 0 ? "text-amber-400" : "text-red-400"}`}>
                        {g.net_gal > 0 ? "+" : ""}{g.net_gal} FRJ
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </Section>
          </div>
        )}
      </div>
    </>
  );
}