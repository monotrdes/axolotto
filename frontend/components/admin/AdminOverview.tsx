"use client";
import { API_BASE } from "@/lib/api";

import { useEffect, useState } from "react";
import axios from "axios";

const API = `${API_BASE}`;

function KpiCard({ emoji, label, value, sub, color = "#FF8DA1" }: {
  emoji: string; label: string; value: string | number; sub?: string; color?: string;
}) {
  return (
    <div className="rounded-xl p-4 border border-white/5" style={{ background: "linear-gradient(135deg, #141428, #1C1C35)" }}>
      <div className="text-xl mb-1">{emoji}</div>
      <div className="text-2xl font-black tabular-nums" style={{ color }}>{value}</div>
      <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider mt-0.5">{label}</div>
      {sub && <div className="text-[10px] text-gray-600 mt-0.5">{sub}</div>}
    </div>
  );
}

export default function AdminOverview({ token }: { token: string | null }) {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [poolBalance, setPoolBalance] = useState<string>("");

  useEffect(() => {
    if (!token) return;
    axios.get(`${API}/admin/overview`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => {
        setData(r.data);
        // Default pool balance input to the simulated balance from backend
        if (r.data?.financials?.simulated_pool_balance_mxn) {
          setPoolBalance(r.data.financials.simulated_pool_balance_mxn.toString());
        } else if (r.data?.financials?.devex_70_gross?.required_reserve_mxn) {
          setPoolBalance(r.data.financials.devex_70_gross.required_reserve_mxn.toString());
        }
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [token]);

  if (loading) return <p className="text-gray-500 animate-pulse py-8">Cargando resumen…</p>;
  if (!data) return <p className="text-red-400 py-8">Error cargando datos.</p>;

  const vipActive = Object.values(data.vip_counts as Record<string, number>).reduce((a: number, b) => a + b, 0);

  const numericPoolBalance = parseFloat(poolBalance) || 0;

  // Health Calculator Helper
  const getReserveHealth = (requiredReserve: number) => {
    if (requiredReserve <= 0) return { pct: 100, color: "emerald", label: "Excelente (Sin pasivos)", badgeClass: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20" };
    const pct = Math.round((numericPoolBalance / requiredReserve) * 100);
    if (pct >= 100) {
      return { pct, color: "emerald", label: "Sólido (100%+ Solvente)", badgeClass: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20" };
    } else if (pct >= 85) {
      return { pct, color: "amber", label: "Aceptable (Reserva parcial)", badgeClass: "bg-amber-500/10 text-amber-400 border-amber-500/20" };
    } else {
      return { pct, color: "red", label: "Riesgo de Insolvencia", badgeClass: "bg-red-500/10 text-red-400 border-red-500/20" };
    }
  };

  return (
    <div className="space-y-6">
      <h2 className="text-lg font-black text-white">📊 Resumen General</h2>

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
        <KpiCard emoji="👥" label="Jugadores" value={data.total_users.toLocaleString()} />
        <KpiCard emoji="🪙" label="FRJ en circulación" value={Math.round(data.total_frj_in_circulation ?? data.total_gal_in_circulation ?? 0).toLocaleString()} color="#F59E0B" sub={`≈ $${(data.total_frj_in_circulation_mxn ?? data.total_gal_in_circulation_mxn ?? 0).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})} MXN`} />
        <KpiCard emoji="💎" label="AXF en circulación" value={Math.round(data.total_axf_in_circulation ?? data.total_axg_in_circulation ?? 0).toLocaleString()} color="#E4007C" sub={`≈ $${(data.total_axf_in_circulation_mxn ?? data.total_axg_in_circulation_mxn ?? 0).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})} MXN`} />
        <KpiCard emoji="🏦" label="Tesorería" value={Math.round(data.treasury_balance).toLocaleString()} sub="FRJ (comisiones)" />
        <KpiCard emoji="🎰" label="Jackpot actual" value={Math.round(data.jackpot_current).toLocaleString()} color="#A78BFA" />
        <KpiCard emoji="🪆" label="Tablas activas" value={data.total_boards.toLocaleString()} />
        <KpiCard emoji="🦎" label="Axolotitos" value={data.total_axolotitos.toLocaleString()} color="#34D399" />
        <KpiCard emoji="🎮" label="Partidas Lotería" value={data.total_loteria_games.toLocaleString()} sub={`Win rate: ${data.global_loteria_win_rate_pct}%`} />
        <KpiCard emoji="⚔️" label="Partidas Multi" value={data.total_multiplayer_games.toLocaleString()} />
        <KpiCard emoji="🟢" label="Salas activas" value={data.active_rooms} />
      </div>

      {/* Corcholatas + Crypto */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {/* Corcholatas */}
        <div className="rounded-xl p-4 border border-white/5 bg-[#141428]">
          <h3 className="text-xs font-black text-gray-400 uppercase tracking-wider mb-3 flex items-center gap-1.5">
            🪅 Tokens obsequiados por Corcholata
          </h3>
          {data.corcholatas ? (
            <div className="grid grid-cols-3 gap-3">
              <div>
                <div className="text-xl font-black tabular-nums text-white">{data.corcholatas.total_claimed.toLocaleString()}</div>
                <div className="text-[10px] text-gray-500 uppercase tracking-wider mt-0.5">Codes reclamados</div>
              </div>
              <div>
                <div className="text-xl font-black tabular-nums text-amber-400">{Math.round(data.corcholatas.total_frj_gifted).toLocaleString()}</div>
                <div className="text-[10px] text-gray-500 uppercase tracking-wider mt-0.5">FRJ regalados</div>
              </div>
              <div>
                <div className="text-xl font-black tabular-nums text-pink-400">{Math.round(data.corcholatas.total_axf_gifted).toLocaleString()}</div>
                <div className="text-[10px] text-gray-500 uppercase tracking-wider mt-0.5">AXF regalados</div>
              </div>
            </div>
          ) : <p className="text-xs text-gray-600">Sin datos</p>}
        </div>

        {/* Crypto */}
        <div className="rounded-xl p-4 border border-white/5 bg-[#141428]">
          <h3 className="text-xs font-black text-gray-400 uppercase tracking-wider mb-3 flex items-center gap-1.5">
            🔗 Compras AXF con cripto (USDC on-chain)
          </h3>
          {data.crypto_purchases ? (
            <div className="grid grid-cols-3 gap-3">
              <div>
                <div className="text-xl font-black tabular-nums text-white">{data.crypto_purchases.completed_orders.toLocaleString()}</div>
                <div className="text-[10px] text-gray-500 uppercase tracking-wider mt-0.5">Órdenes completadas</div>
              </div>
              <div>
                <div className="text-xl font-black tabular-nums text-pink-400">{Math.round(data.crypto_purchases.total_axf_sold).toLocaleString()}</div>
                <div className="text-[10px] text-gray-500 uppercase tracking-wider mt-0.5">AXF vendidos</div>
              </div>
              <div>
                <div className="text-xl font-black tabular-nums text-emerald-400">${data.crypto_purchases.total_usd_received.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</div>
                <div className="text-[10px] text-gray-500 uppercase tracking-wider mt-0.5">USD recibidos</div>
              </div>
            </div>
          ) : <p className="text-xs text-gray-600">Sin datos</p>}
          {data.crypto_purchases?.completed_orders === 0 && (
            <p className="text-[10px] text-gray-600 mt-2">Ninguna orden crypto completada aún (flujo distinto al fiat)</p>
          )}
        </div>
      </div>

      <div>
        <h3 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">👑 VIP Activos — {vipActive} total</h3>
        <div className="grid grid-cols-3 gap-3">
          <KpiCard emoji="🪸" label="Coral" value={data.vip_counts.coral ?? 0} color="#F97316" />
          <KpiCard emoji="✨" label="Dorado" value={data.vip_counts.dorado ?? 0} color="#EAB308" />
          <KpiCard emoji="🌟" label="Axolite" value={data.vip_counts.axolite ?? 0} color="#8B5CF6" />
        </div>
      </div>

      {data.financials && (
        <div className="mt-8 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <h3 className="text-sm font-black text-white flex items-center gap-2">
              <span>💵</span> Estado de Caja y Utilidad Real (Pesos MXN)
            </h3>
            
            {/* Input para el balance real del fondo */}
            <div className="flex flex-col items-end gap-1">
              <div className="flex items-center gap-2 bg-[#141428] border border-white/5 px-3 py-1.5 rounded-xl">
                <span className="text-[10px] font-black text-slate-400 uppercase tracking-wider">Tu Liquidez Real:</span>
                <div className="relative flex items-center">
                  <span className="absolute left-1.5 text-xs text-slate-400 font-mono">$</span>
                  <input
                    type="number"
                    placeholder="Ej. 50000"
                    value={poolBalance}
                    onChange={(e) => setPoolBalance(e.target.value)}
                    className="w-28 bg-slate-900/60 border border-white/10 rounded-lg py-1 pl-4 pr-1.5 text-xs text-emerald-400 font-bold font-mono focus:outline-none focus:border-pink-500/50"
                  />
                </div>
              </div>
              <span className="text-[9px] text-gray-500 font-semibold italic mr-1">
                🤖 Resguardo real simulado (Caja menos retiros mock)
              </span>
            </div>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div className="rounded-xl p-4 border border-white/5 bg-[#141428]">
              <div className="text-xs font-bold text-gray-400 uppercase tracking-wider">Recaudación Bruta</div>
              <div className="text-xl font-black text-white font-mono mt-1">${data.financials.total_purchased_mxn.toLocaleString()}</div>
              <div className="text-[10px] text-gray-500 mt-1">Total cobrado en pasarelas</div>
            </div>
            
            <div className="rounded-xl p-4 border border-white/5 bg-[#141428]">
              <div className="text-xs font-bold text-gray-400 uppercase tracking-wider">IVA Estimado (16%)</div>
              <div className="text-xl font-black text-red-400 font-mono mt-1">-${data.financials.total_iva_mxn.toLocaleString()}</div>
              <div className="text-[10px] text-gray-500 mt-1">Impuesto retenido SAT</div>
            </div>

            <div className="rounded-xl p-4 border border-white/5 bg-[#141428]">
              <div className="text-xs font-bold text-gray-400 uppercase tracking-wider">Pasarela (4.5%)</div>
              <div className="text-xl font-black text-red-400 font-mono mt-1">-${data.financials.total_gateway_fees_mxn.toLocaleString()}</div>
              <div className="text-[10px] text-gray-500 mt-1">Costo pasarela de pago</div>
            </div>

            <div className="rounded-xl p-4 border border-white/5 bg-[#141428]">
              <div className="text-xs font-bold text-gray-400 uppercase tracking-wider">Ingreso Neto Real</div>
              <div className="text-xl font-black text-emerald-400 font-mono mt-1">${data.financials.total_net_revenue_mxn.toLocaleString()}</div>
              <div className="text-[10px] text-gray-500 mt-1">Dinero neto en caja</div>
            </div>
          </div>

          <div className="bg-[#0D0D1F] border border-white/5 rounded-xl p-5 mt-4">
            <h4 className="text-xs font-black text-white uppercase tracking-wider mb-4 flex items-center gap-2">
              ⚖️ Escenarios de DevEx / Retiros y Semáforo de Solvencia
            </h4>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Escenario A: 70% Bruto */}
              {(() => {
                const required = data.financials.devex_70_gross.required_reserve_mxn;
                const health = getReserveHealth(required);
                return (
                  <div className={`rounded-xl p-4 border flex flex-col justify-between transition-colors ${
                    health.color === "emerald" ? "border-emerald-500/20 bg-emerald-500/[0.01]" :
                    health.color === "amber" ? "border-amber-500/20 bg-amber-500/[0.01]" :
                    "border-red-500/20 bg-red-500/[0.01]"
                  }`}>
                    <div>
                      <div className="flex justify-between items-center gap-2">
                        <span className="px-2 py-0.5 bg-amber-500/10 text-amber-400 text-[9px] font-black rounded uppercase tracking-wider">
                          70% Bruto
                        </span>
                        <div className="relative group cursor-help">
                          <span className={`px-2 py-0.5 border text-[9px] font-bold rounded ${health.badgeClass}`}>
                            {health.pct}% Solvente
                          </span>
                          <div className="absolute right-0 bottom-full mb-2 hidden group-hover:block w-48 bg-[#0D0D1F] border border-white/10 text-[9.5px] text-gray-400 p-2.5 rounded-lg shadow-xl z-30 leading-normal pointer-events-none">
                            <p className="font-extrabold text-white mb-1">Solvencia (70% Bruto)</p>
                            Mide si tu <strong>Liquidez Real</strong> cubre la recompra del 100% de las AXF en circulación a una tasa del 70% del valor bruto ($1.40 MXN por AXF).
                          </div>
                        </div>
                      </div>
                      <p className="text-xs font-semibold text-gray-400 mt-3">
                        Tasa: **$1.40 MXN** por AXF
                      </p>
                    </div>

                    <div className="mt-4 pt-3 border-t border-white/5 space-y-2">
                      <div className="flex justify-between text-xs">
                        <span className="text-gray-500">Reserva Requerida:</span>
                        <span className="font-mono text-white">${required.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between text-xs">
                        <span className="text-gray-500">Ganancia Libre:</span>
                        <span className="font-mono font-bold text-emerald-400">${data.financials.devex_70_gross.unlocked_profit_mxn.toLocaleString()}</span>
                      </div>
                      
                      {/* Barra de progreso visual */}
                      <div className="w-full bg-slate-950 rounded-full h-1.5 overflow-hidden mt-1.5">
                        <div className={`h-full rounded-full transition-all duration-300 ${
                          health.color === "emerald" ? "bg-emerald-500" :
                          health.color === "amber" ? "bg-amber-500" :
                          "bg-red-500"
                        }`} style={{ width: `${Math.min(100, health.pct)}%` }} />
                      </div>
                      <div className="text-[9px] text-gray-500 font-bold uppercase mt-1 text-center tracking-wider">
                        {health.label}
                      </div>
                    </div>
                  </div>
                );
              })()}

              {/* Escenario B: 70% Neto */}
              {(() => {
                const required = data.financials.devex_70_net.required_reserve_mxn;
                const health = getReserveHealth(required);
                return (
                  <div className={`rounded-xl p-4 border flex flex-col justify-between transition-colors ${
                    health.color === "emerald" ? "border-emerald-500/20 bg-emerald-500/[0.01]" :
                    health.color === "amber" ? "border-amber-500/20 bg-amber-500/[0.01]" :
                    "border-red-500/20 bg-red-500/[0.01]"
                  }`}>
                    <div>
                      <div className="flex justify-between items-center gap-2">
                        <span className="px-2 py-0.5 bg-cyan-500/10 text-cyan-400 text-[9px] font-black rounded uppercase tracking-wider">
                          70% Neto
                        </span>
                        <div className="relative group cursor-help">
                          <span className={`px-2 py-0.5 border text-[9px] font-bold rounded ${health.badgeClass}`}>
                            {health.pct}% Solvente
                          </span>
                          <div className="absolute right-0 bottom-full mb-2 hidden group-hover:block w-48 bg-[#0D0D1F] border border-white/10 text-[9.5px] text-gray-400 p-2.5 rounded-lg shadow-xl z-30 leading-normal pointer-events-none">
                            <p className="font-extrabold text-white mb-1">Solvencia (70% Neto)</p>
                            Mide si tu <strong>Liquidez Real</strong> cubre la recompra del 100% de las AXF en circulación a una tasa del 70% del valor neto ($1.14 MXN por AXF).
                          </div>
                        </div>
                      </div>
                      <p className="text-xs font-semibold text-gray-400 mt-3">
                        Tasa: **$1.14 MXN** por AXF
                      </p>
                    </div>

                    <div className="mt-4 pt-3 border-t border-white/5 space-y-2">
                      <div className="flex justify-between text-xs">
                        <span className="text-gray-500">Reserva Requerida:</span>
                        <span className="font-mono text-white">${required.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between text-xs">
                        <span className="text-gray-500">Ganancia Libre:</span>
                        <span className="font-mono font-bold text-emerald-400">${data.financials.devex_70_net.unlocked_profit_mxn.toLocaleString()}</span>
                      </div>
                      
                      {/* Barra de progreso visual */}
                      <div className="w-full bg-slate-950 rounded-full h-1.5 overflow-hidden mt-1.5">
                        <div className={`h-full rounded-full transition-all duration-300 ${
                          health.color === "emerald" ? "bg-emerald-500" :
                          health.color === "amber" ? "bg-amber-500" :
                          "bg-red-500"
                        }`} style={{ width: `${Math.min(100, health.pct)}%` }} />
                      </div>
                      <div className="text-[9px] text-gray-500 font-bold uppercase mt-1 text-center tracking-wider">
                        {health.label}
                      </div>
                    </div>
                  </div>
                );
              })()}

              {/* Escenario C: DevEx Base (50%) */}
              {(() => {
                const required = data.financials.devex_50_gross.required_reserve_mxn;
                const health = getReserveHealth(required);
                return (
                  <div className={`rounded-xl p-4 border flex flex-col justify-between transition-colors ${
                    health.color === "emerald" ? "border-emerald-500/20 bg-emerald-500/[0.01]" :
                    health.color === "amber" ? "border-amber-500/20 bg-amber-500/[0.01]" :
                    "border-red-500/20 bg-red-500/[0.01]"
                  }`}>
                    <div>
                      <div className="flex justify-between items-center gap-2">
                        <span className="px-2 py-0.5 bg-emerald-500/10 text-emerald-400 text-[9px] font-black rounded uppercase tracking-wider">
                          DevEx Base (50%)
                        </span>
                        <div className="relative group cursor-help">
                          <span className={`px-2 py-0.5 border text-[9px] font-bold rounded ${health.badgeClass}`}>
                            {health.pct}% Solvente
                          </span>
                          <div className="absolute right-0 bottom-full mb-2 hidden group-hover:block w-48 bg-[#0D0D1F] border border-white/10 text-[9.5px] text-gray-400 p-2.5 rounded-lg shadow-xl z-30 leading-normal pointer-events-none">
                            <p className="font-extrabold text-white mb-1">Solvencia (50% DevEx)</p>
                            Mide si tu <strong>Liquidez Real</strong> cubre la recompra del 100% de las AXF en circulación a la tasa base del 50% del valor bruto ($1.00 MXN por AXF).
                          </div>
                        </div>
                      </div>
                      <p className="text-xs font-semibold text-gray-400 mt-3">
                        Tasa: **$1.00 MXN** por AXF
                      </p>
                    </div>

                    <div className="mt-4 pt-3 border-t border-white/5 space-y-2">
                      <div className="flex justify-between text-xs">
                        <span className="text-gray-500">Reserva Requerida:</span>
                        <span className="font-mono text-white">${required.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between text-xs">
                        <span className="text-gray-500">Ganancia Libre:</span>
                        <span className="font-mono font-bold text-emerald-400">${data.financials.devex_50_gross.unlocked_profit_mxn.toLocaleString()}</span>
                      </div>
                      
                      {/* Barra de progreso visual */}
                      <div className="w-full bg-slate-950 rounded-full h-1.5 overflow-hidden mt-1.5">
                        <div className={`h-full rounded-full transition-all duration-300 ${
                          health.color === "emerald" ? "bg-emerald-500" :
                          health.color === "amber" ? "bg-amber-500" :
                          "bg-red-500"
                        }`} style={{ width: `${Math.min(100, health.pct)}%` }} />
                      </div>
                      <div className="text-[9px] text-gray-500 font-bold uppercase mt-1 text-center tracking-wider">
                        {health.label}
                      </div>
                    </div>
                  </div>
                );
              })()}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}