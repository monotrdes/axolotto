import { API_BASE } from "@/lib/api";
import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface RentalMarketProps {
  userId: string;
  token: string | null;
  onRented?: () => void;
}

export default function RentalMarket({ userId, token, onRented }: RentalMarketProps) {
  const [boards, setBoards] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [rentando, setRentando] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [filtroCSR, setFiltroCSR] = useState<'all' | 'lucky' | 'normal' | 'salty'>('all');

  const cargarMercado = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await axios.get(`${API_BASE}/board/rent/market`);
      setBoards(res.data);
    } catch (err) {
      console.error('Error cargando mercado de rentas:', err);
      setError('No se pudo cargar el mercado. Intenta de nuevo.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarMercado();
  }, []);

  const handleRent = async (boardId: number, boardName: string, fee: number) => {
    if (!token) { setError('Debes iniciar sesión para rentar.'); return; }
    setRentando(boardId);
    setError(null);
    setSuccess(null);
    try {
      const headers = { Authorization: `Bearer ${token}` };
      await axios.post(`${API_BASE}/board/${boardId}/rent`, {}, { headers });
      setSuccess(`¡Rentaste "${boardName}" por 24h! Ahora aparece en Mis Tablas.`);
      cargarMercado();
      onRented?.();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'No se pudo completar la renta.');
    } finally {
      setRentando(null);
    }
  };

  const boardsFiltrados = boards.filter(b => {
    if (filtroCSR === 'lucky') return b.csr >= 35;
    if (filtroCSR === 'normal') return b.csr > 15 && b.csr < 35;
    if (filtroCSR === 'salty') return b.csr <= 15;
    return true;
  }).filter(b => b.owner_id !== userId); // No mostrar propias al usuario

  const getCsrBadge = (csr: number, tag: string) => {
    if (csr >= 35) return { bg: 'bg-emerald-950/80 border-emerald-500/40', text: 'text-emerald-300', label: tag };
    if (csr <= 15) return { bg: 'bg-orange-950/80 border-orange-500/40', text: 'text-orange-300', label: tag };
    return { bg: 'bg-slate-800/80 border-slate-600/40', text: 'text-slate-300', label: tag };
  };

  const getLevelColor = (level: number) => {
    if (level >= 10) return 'text-amber-400';
    if (level >= 5) return 'text-sky-400';
    return 'text-slate-400';
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-20 gap-4">
        <div className="w-12 h-12 border-4 border-teal-500 border-t-transparent rounded-full animate-spin" />
        <p className="text-teal-400 font-black text-xs uppercase tracking-widest animate-pulse">
          Cargando Mercado...
        </p>
      </div>
    );
  }

  return (
    <div className="w-full animate-in fade-in duration-300">

      {/* Header del Mercado */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
        <div>
          <h3 className="text-2xl font-black italic text-transparent bg-clip-text bg-gradient-to-r from-teal-400 to-cyan-300 tracking-tight">
            MERCADO DE RENTAS
          </h3>
          <p className="text-slate-400 text-xs mt-0.5">
            {boards.length} tabla{boards.length !== 1 ? 's' : ''} disponible{boards.length !== 1 ? 's' : ''} para rentar por 24h
          </p>
        </div>
        <button
          onClick={cargarMercado}
          className="px-4 py-2 bg-slate-900 border border-slate-700 hover:border-teal-500 text-slate-400 hover:text-teal-300 rounded-xl text-xs font-black uppercase tracking-wider transition-all active:scale-95"
        >
          🔄 Actualizar
        </button>
      </div>

      {/* Filtros de CSR */}
      <div className="flex flex-wrap gap-2 mb-6">
        {[
          { key: 'all', label: '🌐 Todas' },
          { key: 'lucky', label: '🍀 Suertudas' },
          { key: 'normal', label: '⚙️ Normales' },
          { key: 'salty', label: '🧂 Saladas' },
        ].map(f => (
          <button
            key={f.key}
            onClick={() => setFiltroCSR(f.key as any)}
            className={`px-4 py-1.5 rounded-xl text-xs font-black uppercase tracking-wider transition-all border ${
              filtroCSR === f.key
                ? 'bg-teal-600 border-teal-400 text-white shadow-[0_0_10px_rgba(20,184,166,0.3)]'
                : 'bg-slate-900 border-slate-700 text-slate-400 hover:border-slate-500 hover:text-slate-200'
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      {/* Mensajes de estado */}
      {error && (
        <div className="mb-4 bg-red-950/60 border border-red-500/30 text-red-200 text-xs font-bold rounded-2xl p-4 text-center animate-pulse">
          ❌ {error}
        </div>
      )}
      {success && (
        <div className="mb-4 bg-teal-950/60 border border-teal-500/30 text-teal-200 text-xs font-bold rounded-2xl p-4 text-center animate-pulse">
          ✅ {success}
        </div>
      )}

      {/* Listado de tablas */}
      {boardsFiltrados.length === 0 ? (
        <div className="py-16 flex flex-col items-center justify-center text-center">
          <span className="text-5xl mb-4">🏪</span>
          <h4 className="text-lg font-black text-white uppercase tracking-tight mb-2">
            No hay tablas disponibles
          </h4>
          <p className="text-slate-400 text-sm max-w-sm">
            {filtroCSR !== 'all'
              ? 'Cambia el filtro para ver más tablas.'
              : 'Por ahora no hay tablas listadas en el mercado. ¡Vuelve pronto!'}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {boardsFiltrados.map((board) => {
            const csrBadge = getCsrBadge(board.csr, board.suerte_tag);
            const isRenting = rentando === board.id;
            const xpToNext = 100 - (board.xp % 100);
            const xpPct = (board.xp % 100);

            return (
              <div
                key={board.id}
                className="relative overflow-hidden bg-slate-900/60 border border-slate-800 hover:border-teal-500/50 rounded-3xl p-5 flex flex-col gap-4 transition-all duration-300 hover:shadow-[0_0_20px_rgba(20,184,166,0.1)] group"
              >
                {/* Corner Ribbon for VIP Owner */}
                {board.owner_vip_tier && (
                  <div className="absolute top-0 right-0 overflow-hidden w-16 h-16 pointer-events-none z-10">
                    <div className={`absolute top-2.5 -right-6 w-20 py-0.5 text-[7px] font-black uppercase text-center rotate-45 text-black shadow-sm ${
                      board.owner_vip_tier === 'coral'
                        ? 'bg-teal-400'
                        : board.owner_vip_tier === 'dorado'
                          ? 'bg-yellow-400'
                          : 'bg-gradient-to-r from-yellow-400 via-pink-400 to-purple-400'
                    }`}>
                      {board.owner_vip_tier === 'coral' && '🪸'}
                      {board.owner_vip_tier === 'dorado' && '✨'}
                      {board.owner_vip_tier === 'axolite' && '🌟'}
                    </div>
                  </div>
                )}
                {/* Top row: nombre + nivel */}
                <div className="flex justify-between items-start">
                  <div className="flex-1 min-w-0 pr-3">
                    <h4 className="text-sm font-black text-white uppercase tracking-tight truncate">
                      {board.name}
                    </h4>
                    <p className="text-[10px] text-slate-500 font-mono mt-0.5 truncate">
                      Owner: {board.owner_id?.slice(0, 12)}...
                    </p>
                  </div>
                  <div className={`text-right shrink-0`}>
                    <div className={`text-lg font-black ${getLevelColor(board.level)}`}>
                      Nv.{board.level}
                    </div>
                    <div className="text-[9px] text-slate-600 uppercase tracking-wider">
                      {board.xp} XP
                    </div>
                  </div>
                </div>

                {/* Barra de XP */}
                <div className="space-y-1">
                  <div className="h-1 bg-slate-800 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-teal-500 to-cyan-400 transition-all duration-500"
                      style={{ width: `${xpPct}%` }}
                    />
                  </div>
                  <div className="text-[8px] text-slate-600 text-right">{xpToNext} XP para siguiente nivel</div>
                </div>

                {/* Stats de partidas */}
                <div className="grid grid-cols-3 gap-2 text-center">
                  <div className="bg-slate-950/60 rounded-xl p-2 border border-white/5">
                    <div className="text-sm font-black text-white">{board.games_played}</div>
                    <div className="text-[8px] text-slate-500 uppercase tracking-wider">Jugados</div>
                  </div>
                  <div className="bg-slate-950/60 rounded-xl p-2 border border-white/5">
                    <div className="text-sm font-black text-emerald-400">{board.games_won}</div>
                    <div className="text-[8px] text-slate-500 uppercase tracking-wider">Ganados</div>
                  </div>
                  <div className="bg-slate-950/60 rounded-xl p-2 border border-white/5">
                    <div className="text-sm font-black text-amber-400">{board.win_rate}%</div>
                    <div className="text-[8px] text-slate-500 uppercase tracking-wider">Win Rate</div>
                  </div>
                </div>

                {/* Badge CSR */}
                <div className={`flex items-center justify-between px-3 py-2 rounded-xl border ${csrBadge.bg}`}>
                  <span className={`text-xs font-black ${csrBadge.text}`}>
                    {csrBadge.label}
                  </span>
                  <span className={`text-xs font-mono font-black ${csrBadge.text}`}>
                    CSR {board.csr}%
                  </span>
                </div>

                {/* Precio de renta */}
                <div className="bg-slate-950/60 border border-white/5 rounded-2xl p-3 space-y-1.5">
                  <div className="flex justify-between items-center text-xs">
                    <span className="text-slate-400 font-bold">💰 Cuota (24h)</span>
                    <span className="text-amber-500 font-black">{board.rent_fee_gal} FRJ</span>
                  </div>
                  <div className="flex justify-between items-center text-xs">
                    <span className="text-slate-400 font-bold">🏆 Split victorias</span>
                    <span className="text-amber-400 font-black">
                      {board.rent_share_owner_pct}% Owner / {100 - board.rent_share_owner_pct}% tú
                    </span>
                  </div>
                </div>

                {/* Botón rentar */}
                <button
                  onClick={() => handleRent(board.id, board.name, board.rent_fee_gal)}
                  disabled={isRenting || !token}
                  className={`w-full py-3 rounded-xl text-xs font-black uppercase tracking-widest transition-all active:scale-95 flex items-center justify-center gap-2 ${
                    isRenting
                      ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
                      : 'bg-gradient-to-r from-amber-600 to-yellow-500 hover:from-amber-500 hover:to-yellow-400 text-slate-950 shadow-[0_0_15px_rgba(245,158,11,0.2)] hover:shadow-[0_0_20px_rgba(245,158,11,0.4)]'
                  }`}
                >
                  {isRenting ? (
                    <>
                      <span className="w-3 h-3 border-2 border-slate-400 border-t-transparent rounded-full animate-spin" />
                      Procesando...
                    </>
                  ) : (
                    `🤝 Rentar por ${board.rent_fee_gal} FRJ`
                  )}
                </button>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
