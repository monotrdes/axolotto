import { API_BASE } from "@/lib/api";
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import BoardCardGrid from '@/components/ui/BoardCardGrid';
import { useProductPolicy } from '@/hooks/useProductPolicy';

interface RankingsProps {
  userId: string;
  token: string | null;
  cambiarTab: (tab: any) => void;
}

const handleImageError = (e: React.SyntheticEvent<HTMLImageElement, Event>, size: number) => {
  e.currentTarget.onerror = null;
  e.currentTarget.src = `data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 ${size} ${size}' width='100%' height='100%'><rect width='${size}' height='${size}' fill='%231e293b' rx='10'/><text x='50%' y='50%' dominant-baseline='middle' text-anchor='middle' font-family='sans-serif' font-size='${size < 50 ? 14 : 12}' fill='%2364748b'>${size < 50 ? '👾' : '👾 Axolotito'}</text></svg>`;
};

export default function Rankings({ userId, token, cambiarTab }: RankingsProps) {
  const { capabilities } = useProductPolicy();
  const playerMarketplaceEnabled = capabilities.commerce.player_marketplace;
  const [activeTab, setActiveTab] = useState<'axolotitos' | 'boards' | 'forjadas'>('axolotitos');
  const [forjadas, setForjadas] = useState<any[]>([]);
  const [loadingForjadas, setLoadingForjadas] = useState(false);
  const [sortBy, setSortBy] = useState<string>('level');
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  // Control de expansión del Top (por defecto 10, expandible a 20)
  const [showAll, setShowAll] = useState<boolean>(false);
  const [rentingId, setRentingId] = useState<number | null>(null);
  const [showRentModal, setShowRentModal] = useState<any | null>(null);

  // Cargar datos del ranking
  const cargarRankings = async () => {
    setLoading(true);
    setError(null);
    try {
      const endpoint = activeTab === 'axolotitos' ? 'axolotitos' : 'boards';
      const res = await axios.get(`${API_BASE}/ranking/${endpoint}?sort_by=${sortBy}&limit=20`);
      setData(res.data);
    } catch (err) {
      console.error('Error al cargar rankings:', err);
      setError('No se pudieron cargar los datos del Salón de la Gloria.');
    } finally {
      setLoading(false);
    }
  };

  // Recargar al cambiar de tab o criterio de ordenamiento
  useEffect(() => {
    cargarRankings();
    setShowAll(false); // Resetear expansión al cambiar
  }, [activeTab, sortBy]);

  // Al cambiar la pestaña principal, resetear el sortBy por defecto
  const cargarForjadas = async () => {
    setLoadingForjadas(true);
    try {
      const res = await axios.get(`${API_BASE}/ranking/boards/forjadas`);
      setForjadas(res.data);
    } catch { /* silent */ } finally {
      setLoadingForjadas(false);
    }
  };

  const handleTabChange = (tab: 'axolotitos' | 'boards' | 'forjadas') => {
    setActiveTab(tab);
    if (tab === 'forjadas') { cargarForjadas(); return; }
    setSortBy(tab === 'axolotitos' ? 'level' : 'wins');
  };

  // Procesar renta directa de tabla
  const handleRentarDirecto = async () => {
    if (!playerMarketplaceEnabled || !showRentModal || !token) return;
    const board = showRentModal;
    setRentingId(board.id);
    setError(null);
    setSuccess(null);
    try {
      const headers = { Authorization: `Bearer ${token}` };
      await axios.post(`${API_BASE}/board/${board.id}/rent`, {}, { headers });
      setSuccess(`🤝 ¡Has rentado exitosamente la tabla "${board.name}"! Ahora puedes usarla para jugar.`);
      setShowRentModal(null);
      // Recargar datos para actualizar estado del botón en el ranking
      cargarRankings();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'No se pudo procesar la renta de la tabla.');
      setShowRentModal(null);
    } finally {
      setRentingId(null);
    }
  };

  // Separar el Top 3 (Podio) del resto de la lista
  const top3 = data.slice(0, 3);
  const restOfList = showAll ? data.slice(3) : data.slice(3, 10);

  // Obtener el color del nivel
  const getLevelColor = (level: number) => {
    if (level >= 15) return 'text-purple-400 font-extrabold';
    if (level >= 10) return 'text-amber-400 font-bold';
    if (level >= 5) return 'text-cyan-400';
    return 'text-slate-400';
  };

  // Obtener estilo CSR
  const getCsrStyle = (csr: number) => {
    if (csr >= 35) return { text: 'text-emerald-400 font-black', bg: 'bg-emerald-950/40 border-emerald-500/30', label: '🍀 Muy Suertuda' };
    if (csr <= 15) return { text: 'text-orange-400 font-black', bg: 'bg-orange-950/40 border-orange-500/30', label: '🧂 Salada' };
    return { text: 'text-slate-300', bg: 'bg-slate-800/40 border-slate-700/30', label: '⚙️ Normal' };
  };

  return (
    <div className="w-full max-w-5xl mx-auto p-2 sm:p-4 text-left animate-in fade-in duration-300">
      
      {/* Título de la sección */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
        <div>
          <h2 className="text-3xl font-black italic tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-amber-400 via-pink-500 to-purple-600">
            🏆 EL SALÓN DE LA GLORIA
          </h2>
          <p className="text-slate-400 text-xs sm:text-sm mt-1">
            Contempla a las leyendas vivientes y las tablas más poderosas del pantano.
          </p>
        </div>
        <button
          onClick={cargarRankings}
          className="px-4 py-2 bg-slate-900 border border-slate-800 hover:border-amber-500 text-slate-400 hover:text-amber-300 rounded-xl text-xs font-black uppercase tracking-wider transition-all active:scale-95 shrink-0"
        >
          🔄 Sincronizar Ranking
        </button>
      </div>

      {/* Tabs Principales */}
      <div className="flex bg-slate-950 border border-slate-800 p-1.5 rounded-2xl w-full max-w-md mb-6 shadow-2xl">
        <button
          onClick={() => handleTabChange('axolotitos')}
          className={`flex-1 py-3 text-center rounded-xl text-xs sm:text-sm font-black uppercase tracking-wider transition-all flex items-center justify-center gap-2 ${
            activeTab === 'axolotitos'
              ? 'bg-gradient-to-r from-purple-700 to-pink-600 text-white shadow-lg'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          👾 Axolotitos de Leyenda
        </button>
        <button
          onClick={() => handleTabChange('boards')}
          className={`flex-1 py-3 text-center rounded-xl text-xs sm:text-sm font-black uppercase tracking-wider transition-all flex items-center justify-center gap-2 ${
            activeTab === 'boards'
              ? 'bg-gradient-to-r from-teal-700 to-cyan-600 text-white shadow-lg'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          📋 Tablas Supremas
        </button>
        <button
          onClick={() => handleTabChange('forjadas')}
          className={`flex-1 py-3 text-center rounded-xl text-xs sm:text-sm font-black uppercase tracking-wider transition-all flex items-center justify-center gap-2 ${
            activeTab === 'forjadas'
              ? 'bg-gradient-to-r from-amber-700 to-yellow-600 text-white shadow-lg'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          ⚔️ Forjadas
        </button>
      </div>

      {/* Tablas Forjadas section */}
      {activeTab === 'forjadas' && (
        <div className="w-full max-w-2xl space-y-4">
          <div className="text-center mb-4">
            <p className="text-[10px] text-amber-400/70 uppercase tracking-widest font-bold">Solo obtenibles con Bola de Oro</p>
            <p className="text-[10px] text-slate-500 mt-1">Tablas que sobrevivieron cientos de batallas esperando al Gashapon</p>
          </div>
          {loadingForjadas ? (
            <div className="flex justify-center py-10">
              <div className="w-8 h-8 border-2 border-amber-500 border-t-transparent rounded-full animate-spin" />
            </div>
          ) : forjadas.length === 0 ? (
            <div className="text-center py-12 bg-slate-900/40 rounded-2xl border border-amber-900/30">
              <div className="text-4xl mb-3">🔥</div>
              <p className="text-slate-400 text-sm font-bold">Aún no hay tablas forjadas</p>
              <p className="text-slate-600 text-xs mt-1">Las primeras se están forjando en batalla. ¡Juega más partidas CPU!</p>
            </div>
          ) : forjadas.map((b) => (
            <div key={b.id} className="bg-gradient-to-br from-amber-950/40 to-slate-900 border border-amber-700/40 rounded-2xl p-4 shadow-lg">
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-amber-300 font-black text-sm">⚔️ {b.name}</span>
                    <span className="bg-amber-900/60 border border-amber-600/40 text-amber-300 text-[9px] font-black uppercase tracking-widest px-2 py-0.5 rounded-full">Nv.{b.level}</span>
                    <span className={`text-[9px] font-black uppercase tracking-widest px-2 py-0.5 rounded-full border ${b.npc_room === 'champion' ? 'bg-purple-900/50 border-purple-600/40 text-purple-300' : 'bg-slate-800 border-slate-600/40 text-slate-400'}`}>{b.npc_room}</span>
                  </div>
                  {b.origin_story && (
                    <p className="text-slate-400 text-[10px] italic mt-1.5 leading-relaxed">&ldquo;{b.origin_story}&rdquo;</p>
                  )}
                  <div className="flex gap-4 mt-2">
                    <span className="text-[10px] text-slate-500">⚔️ <span className="text-slate-300">{b.games_played}</span> batallas</span>
                    <span className="text-[10px] text-slate-500">🏆 <span className="text-slate-300">{b.win_rate}%</span> victorias</span>
                  </div>
                </div>
                <div className="flex flex-col items-end gap-1 shrink-0">
                  <span className="bg-yellow-900/60 border border-yellow-600/40 text-yellow-300 text-[9px] font-black uppercase tracking-widest px-2 py-1 rounded-full">🔮 Bola de Oro</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Filtros de Ordenamiento — oculto en tab forjadas */}
      {activeTab !== 'forjadas' && <div className="flex flex-wrap gap-2 mb-8 bg-slate-900/40 p-3 rounded-2xl border border-slate-800/60">
        <span className="text-[10px] text-slate-500 uppercase tracking-widest font-bold self-center mr-2">Ordenar por:</span>
        {activeTab === 'axolotitos' ? (
          <>
            <button
              onClick={() => setSortBy('level')}
              className={`px-4 py-2 rounded-xl text-xs font-black uppercase tracking-wide transition-all border ${
                sortBy === 'level'
                  ? 'bg-pink-600 border-pink-400 text-white shadow-[0_0_12px_rgba(219,39,119,0.3)]'
                  : 'bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700'
              }`}
            >
              👑 Nivel / Experiencia
            </button>
            <button
              onClick={() => setSortBy('power')}
              className={`px-4 py-2 rounded-xl text-xs font-black uppercase tracking-wide transition-all border ${
                sortBy === 'power'
                  ? 'bg-purple-600 border-purple-400 text-white shadow-[0_0_12px_rgba(147,51,234,0.3)]'
                  : 'bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700'
              }`}
            >
              🔥 Poder de Combate
            </button>
          </>
        ) : (
          <>
            <button
              onClick={() => setSortBy('wins')}
              className={`px-4 py-2 rounded-xl text-xs font-black uppercase tracking-wide transition-all border ${
                sortBy === 'wins'
                  ? 'bg-teal-600 border-teal-400 text-white shadow-[0_0_12px_rgba(20,184,166,0.3)]'
                  : 'bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700'
              }`}
            >
              🏆 Victorias Totales
            </button>
            <button
              onClick={() => setSortBy('level')}
              className={`px-4 py-2 rounded-xl text-xs font-black uppercase tracking-wide transition-all border ${
                sortBy === 'level'
                  ? 'bg-cyan-600 border-cyan-400 text-white shadow-[0_0_12px_rgba(6,182,212,0.3)]'
                  : 'bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700'
              }`}
            >
              📈 Nivel de Tabla
            </button>
            <button
              onClick={() => setSortBy('lucky')}
              className={`px-4 py-2 rounded-xl text-xs font-black uppercase tracking-wide transition-all border ${
                sortBy === 'lucky'
                  ? 'bg-emerald-600 border-emerald-400 text-white shadow-[0_0_12px_rgba(16,185,129,0.3)]'
                  : 'bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700'
              }`}
            >
              🍀 Más Suertudas (CSR)
            </button>
            <button
              onClick={() => setSortBy('salty')}
              className={`px-4 py-2 rounded-xl text-xs font-black uppercase tracking-wide transition-all border ${
                sortBy === 'salty'
                  ? 'bg-orange-600 border-orange-400 text-white shadow-[0_0_12px_rgba(249,115,22,0.3)]'
                  : 'bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700'
              }`}
            >
              🧂 Más Saladas (CSR Min)
            </button>
            <button
              onClick={() => setSortBy('streak')}
              className={`px-4 py-2 rounded-xl text-xs font-black uppercase tracking-wide transition-all border ${
                sortBy === 'streak'
                  ? 'bg-violet-600 border-violet-400 text-white shadow-[0_0_12px_rgba(139,92,246,0.3)]'
                  : 'bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700'
              }`}
            >
              🔥 Mejor Racha
            </button>
          </>
        )}
      </div>}

      {/* Alertas de Status */}
      {error && (
        <div className="mb-6 bg-red-950/60 border border-red-500/30 text-red-200 text-xs sm:text-sm font-bold rounded-2xl p-4 text-center">
          ❌ {error}
        </div>
      )}
      {success && (
        <div className="mb-6 bg-emerald-950/60 border border-emerald-500/30 text-emerald-200 text-xs sm:text-sm font-bold rounded-2xl p-4 text-center animate-bounce">
          🎉 {success}
        </div>
      )}

      {activeTab !== 'forjadas' && loading ? (
        <div className="flex flex-col items-center justify-center py-24 gap-4">
          <div className="w-12 h-12 border-4 border-amber-500 border-t-transparent rounded-full animate-spin" />
          <p className="text-amber-400 font-black text-xs uppercase tracking-widest animate-pulse">
            Consultando el Oráculo del Fango...
          </p>
        </div>
      ) : data.length === 0 ? (
        <div className="py-20 flex flex-col items-center justify-center text-center">
          <span className="text-6xl mb-4">🌪️</span>
          <h4 className="text-xl font-black text-white uppercase tracking-tight mb-2">Salón Vacío</h4>
          <p className="text-slate-400 text-sm max-w-sm">
            Nadie ha calificado aún para este ranking. ¡Juega unas partidas o sube de nivel para inaugurar la tabla!
          </p>
        </div>
      ) : (
        <div className="space-y-10">
          
          {/* PODIO DEL TOP 3 */}
          <div className="grid grid-cols-3 gap-3 sm:gap-6 items-end pt-12 pb-6 max-w-3xl mx-auto">
            
            {/* 2DO LUGAR (Izquierda) */}
            {top3[1] && (
              <div className="flex flex-col items-center">
                <div className="relative group w-full">
                  <div className="absolute inset-0 bg-slate-400/10 rounded-3xl blur transition-all group-hover:blur-md" />
                  <div className="relative bg-slate-900/80 border-2 border-slate-400/40 rounded-3xl p-3 sm:p-5 flex flex-col items-center text-center transition-all hover:scale-105">
                    <span className="absolute -top-6 text-3xl">🥈</span>
                    {activeTab === 'axolotitos' ? (
                      <img 
                        src={`${API_BASE}/metadata/axolotito/${top3[1].blockchain_token_id}.svg`} 
                        className="w-16 h-16 sm:w-24 sm:h-24 object-contain mb-3 drop-shadow-[0_0_10px_rgba(255,255,255,0.1)]"
                        alt={top3[1].name}
                        onError={(e) => handleImageError(e, 120)}
                      />
                    ) : (
                      <div className="w-16 h-20 sm:w-20 sm:h-24 bg-slate-800/80 border border-slate-700/80 rounded-2xl flex items-center justify-center mb-3">
                        <BoardCardGrid boardNums={Array(16).fill(0)} cardSize={11} />
                      </div>
                    )}
                    <h4 className="text-xs sm:text-sm font-black text-white truncate max-w-full uppercase">
                      {top3[1].name}
                    </h4>
                    {activeTab === 'boards' && top3[1].is_npc_pool && (
                      top3[1].npc_retired ? (
                        <span className="mt-1 inline-block px-2 py-0.5 rounded-full bg-amber-900/60 border border-amber-600/40 text-amber-300 text-[7px] font-black uppercase tracking-wider animate-pulse">
                          ⚔️ Gashapon
                        </span>
                      ) : (
                        <span className="mt-1 inline-block px-2 py-0.5 rounded-full bg-slate-800 border border-slate-600/40 text-slate-400 text-[7px] font-black uppercase tracking-wider">
                          🤖 En Arena
                        </span>
                      )
                    )}
                    <p className="text-[9px] text-slate-400 mt-0.5 truncate max-w-full font-bold flex items-center justify-center gap-1">
                      <span>👤 {activeTab === 'boards' && top3[1].is_npc_pool ? '🤖 Sistema' : top3[1].owner_nickname}</span>
                      {!top3[1].is_npc_pool && top3[1].owner_vip_tier === 'coral' && <span>🪸</span>}
                      {!top3[1].is_npc_pool && top3[1].owner_vip_tier === 'dorado' && <span>✨</span>}
                      {!top3[1].is_npc_pool && top3[1].owner_vip_tier === 'axolite' && <span>🌟</span>}
                    </p>
                    <div className="mt-3 px-3 py-1 bg-slate-950 border border-slate-800 rounded-full">
                      <span className="text-[10px] text-slate-300 font-extrabold uppercase">
                        {sortBy === 'level' && `Nivel ${top3[1].level}`}
                        {sortBy === 'power' && `${top3[1].power_rating} PODER`}
                        {sortBy === 'wins' && `${top3[1].games_won} Wins`}
                        {sortBy === 'lucky' && `${top3[1].csr}% CSR`}
                        {sortBy === 'salty' && `${top3[1].csr}% CSR`}
                        {sortBy === 'streak' && `${top3[1].streak} 🔥 Racha`}
                      </span>
                    </div>
                  </div>
                </div>
                {/* Pilar del podio */}
                <div className="w-full h-16 sm:h-24 bg-gradient-to-b from-slate-700 to-slate-900 rounded-t-2xl mt-4 flex items-center justify-center shadow-xl border-t border-slate-500/20">
                  <span className="text-2xl font-black text-slate-400">2</span>
                </div>
              </div>
            )}

            {/* 1ER LUGAR (Centro - Más Alto y con Aura brillante) */}
            {top3[0] && (
              <div className="flex flex-col items-center z-10">
                <div className="relative group w-full">
                  {/* Aura brillante dorada/rosa animada */}
                  <div className="absolute inset-0 bg-gradient-to-r from-amber-500 to-pink-500 rounded-[32px] blur-xl opacity-40 animate-pulse group-hover:opacity-60 transition-all duration-1000" />
                  
                  <div className="relative bg-slate-900/90 border-2 border-amber-400 rounded-[32px] p-4 sm:p-6 flex flex-col items-center text-center shadow-[0_0_30px_rgba(251,191,36,0.2)] transition-all hover:scale-105 transform -translate-y-2">
                    <span className="absolute -top-7 text-4xl animate-bounce">👑</span>
                    <span className="absolute -top-3 text-3xl">🥇</span>
                    
                    {activeTab === 'axolotitos' ? (
                      <img 
                        src={`${API_BASE}/metadata/axolotito/${top3[0].blockchain_token_id}.svg`} 
                        className="w-20 h-20 sm:w-28 sm:h-28 object-contain mb-3 drop-shadow-[0_0_15px_rgba(251,191,36,0.3)]"
                        alt={top3[0].name}
                        onError={(e) => handleImageError(e, 120)}
                      />
                    ) : (
                      <div className="w-20 h-24 sm:w-24 sm:h-28 bg-slate-800/90 border-2 border-amber-500/40 rounded-2xl flex items-center justify-center mb-3">
                        <BoardCardGrid boardNums={Array(16).fill(0)} cardSize={13} />
                      </div>
                    )}
                    
                    <h4 className="text-xs sm:text-base font-black text-amber-300 truncate max-w-full uppercase tracking-tight">
                      {top3[0].name}
                    </h4>
                    {activeTab === 'boards' && top3[0].is_npc_pool && (
                      top3[0].npc_retired ? (
                        <span className="mt-1 inline-block px-2 py-0.5 rounded-full bg-amber-900/60 border border-amber-600/40 text-amber-300 text-[7px] font-black uppercase tracking-wider animate-pulse">
                          ⚔️ Gashapon
                        </span>
                      ) : (
                        <span className="mt-1 inline-block px-2 py-0.5 rounded-full bg-slate-800 border border-slate-600/40 text-slate-400 text-[7px] font-black uppercase tracking-wider">
                          🤖 En Arena
                        </span>
                      )
                    )}
                    <p className="text-[10px] text-slate-300 mt-0.5 truncate max-w-full font-black flex items-center justify-center gap-1">
                      <span>👤 {activeTab === 'boards' && top3[0].is_npc_pool ? '🤖 Sistema' : top3[0].owner_nickname}</span>
                      {!top3[0].is_npc_pool && top3[0].owner_vip_tier === 'coral' && <span>🪸</span>}
                      {!top3[0].is_npc_pool && top3[0].owner_vip_tier === 'dorado' && <span>✨</span>}
                      {!top3[0].is_npc_pool && top3[0].owner_vip_tier === 'axolite' && <span>🌟</span>}
                    </p>
                    
                    <div className="mt-3 px-4 py-1.5 bg-gradient-to-r from-amber-500 to-pink-500 rounded-full shadow-inner">
                      <span className="text-[10px] sm:text-xs text-white font-black uppercase">
                        {sortBy === 'level' && `Nivel ${top3[0].level}`}
                        {sortBy === 'power' && `${top3[0].power_rating} PODER`}
                        {sortBy === 'wins' && `${top3[0].games_won} Wins`}
                        {sortBy === 'lucky' && `${top3[0].csr}% CSR`}
                        {sortBy === 'salty' && `${top3[0].csr}% CSR`}
                        {sortBy === 'streak' && `${top3[0].streak} 🔥 Racha`}
                      </span>
                    </div>
                  </div>
                </div>
                {/* Pilar del podio */}
                <div className="w-full h-24 sm:h-36 bg-gradient-to-b from-amber-600 via-amber-700 to-amber-900 rounded-t-2xl mt-4 flex items-center justify-center shadow-2xl border-t-2 border-amber-400/40">
                  <span className="text-3xl font-black text-amber-200">1</span>
                </div>
              </div>
            )}

            {/* 3ER LUGAR (Derecha) */}
            {top3[2] && (
              <div className="flex flex-col items-center">
                <div className="relative group w-full">
                  <div className="absolute inset-0 bg-amber-800/10 rounded-3xl blur transition-all group-hover:blur-md" />
                  <div className="relative bg-slate-900/80 border-2 border-amber-700/40 rounded-3xl p-3 sm:p-5 flex flex-col items-center text-center transition-all hover:scale-105">
                    <span className="absolute -top-6 text-3xl">🥉</span>
                    {activeTab === 'axolotitos' ? (
                      <img 
                        src={`${API_BASE}/metadata/axolotito/${top3[2].blockchain_token_id}.svg`} 
                        className="w-16 h-16 sm:w-24 sm:h-24 object-contain mb-3 drop-shadow-[0_0_10px_rgba(180,83,9,0.1)]"
                        alt={top3[2].name}
                        onError={(e) => handleImageError(e, 120)}
                      />
                    ) : (
                      <div className="w-16 h-20 sm:w-20 sm:h-24 bg-slate-800/80 border border-slate-700/80 rounded-2xl flex items-center justify-center mb-3">
                        <BoardCardGrid boardNums={Array(16).fill(0)} cardSize={11} />
                      </div>
                    )}
                    <h4 className="text-xs sm:text-sm font-black text-white truncate max-w-full uppercase">
                      {top3[2].name}
                    </h4>
                    {activeTab === 'boards' && top3[2].is_npc_pool && (
                      top3[2].npc_retired ? (
                        <span className="mt-1 inline-block px-2 py-0.5 rounded-full bg-amber-900/60 border border-amber-600/40 text-amber-300 text-[7px] font-black uppercase tracking-wider animate-pulse">
                          ⚔️ Gashapon
                        </span>
                      ) : (
                        <span className="mt-1 inline-block px-2 py-0.5 rounded-full bg-slate-800 border border-slate-600/40 text-slate-400 text-[7px] font-black uppercase tracking-wider">
                          🤖 En Arena
                        </span>
                      )
                    )}
                    <p className="text-[9px] text-slate-400 mt-0.5 truncate max-w-full font-bold flex items-center justify-center gap-1">
                      <span>👤 {activeTab === 'boards' && top3[2].is_npc_pool ? '🤖 Sistema' : top3[2].owner_nickname}</span>
                      {!top3[2].is_npc_pool && top3[2].owner_vip_tier === 'coral' && <span>🪸</span>}
                      {!top3[2].is_npc_pool && top3[2].owner_vip_tier === 'dorado' && <span>✨</span>}
                      {!top3[2].is_npc_pool && top3[2].owner_vip_tier === 'axolite' && <span>🌟</span>}
                    </p>
                    <div className="mt-3 px-3 py-1 bg-slate-950 border border-slate-800 rounded-full">
                      <span className="text-[10px] text-slate-300 font-extrabold uppercase">
                        {sortBy === 'level' && `Nivel ${top3[2].level}`}
                        {sortBy === 'power' && `${top3[2].power_rating} PODER`}
                        {sortBy === 'wins' && `${top3[2].games_won} Wins`}
                        {sortBy === 'lucky' && `${top3[2].csr}% CSR`}
                        {sortBy === 'salty' && `${top3[2].csr}% CSR`}
                        {sortBy === 'streak' && `${top3[2].streak} 🔥 Racha`}
                      </span>
                    </div>
                  </div>
                </div>
                {/* Pilar del podio */}
                <div className="w-full h-12 sm:h-16 bg-gradient-to-b from-amber-800 to-amber-950 rounded-t-2xl mt-4 flex items-center justify-center shadow-xl border-t border-amber-700/20">
                  <span className="text-2xl font-black text-amber-600">3</span>
                </div>
              </div>
            )}

          </div>

          {/* TABLA DE POSICIONES (RANGO 4 EN ADELANTE) */}
          {data.length > 3 && (
            <div className="space-y-4">
              <h3 className="text-lg font-black italic tracking-wider text-slate-400 uppercase">Clasificación General</h3>
              <div className="bg-slate-950/80 border border-slate-900 rounded-3xl overflow-hidden shadow-2xl">
                
                {/* Header de la Tabla */}
                <div className="grid grid-cols-12 gap-2 p-4 bg-slate-900/60 border-b border-slate-800 font-black text-[10px] text-slate-500 uppercase tracking-widest">
                  <div className="col-span-1 text-center">Rank</div>
                  <div className="col-span-4 sm:col-span-3">Mascota / Dueño</div>
                  <div className="col-span-3 sm:col-span-2 text-center">Nivel</div>
                  
                  {activeTab === 'axolotitos' ? (
                    <>
                      <div className="col-span-2 text-center">Poder</div>
                      <div className="col-span-2 text-center">Estado</div>
                    </>
                  ) : (
                    <>
                      <div className="col-span-2 text-center">Wins / Partidas</div>
                      <div className="col-span-2 text-center">CSR %</div>
                    </>
                  )}
                  <div className="col-span-2 text-center">Acción</div>
                </div>

                {/* Lista de Filas */}
                <div className="divide-y divide-slate-900/60">
                  {restOfList.map((item, index) => {
                    const rank = index + 4;
                    const esPropio = item.owner_id === userId;
                    const csrBadge = activeTab === 'boards' ? getCsrStyle(item.csr) : null;

                    return (
                      <div
                        key={item.id}
                        className={`grid grid-cols-12 gap-2 p-4 items-center transition-all ${
                          esPropio 
                            ? 'bg-pink-950/20 border-y border-pink-500/20 shadow-[inset_0_0_15px_rgba(228,0,124,0.05)]' 
                            : 'hover:bg-slate-900/30'
                        }`}
                      >
                        {/* Rank */}
                        <div className="col-span-1 text-center font-mono font-black text-sm text-slate-400">
                          #{rank}
                        </div>

                        {/* Nombre y Dueño */}
                        <div className="col-span-4 sm:col-span-3 min-w-0">
                          <div className="flex items-center gap-2">
                            {activeTab === 'axolotitos' && (
                              <div className="w-8 h-8 rounded-lg bg-slate-900 border border-slate-800 flex items-center justify-center shrink-0">
                                <img 
                                  src={`${API_BASE}/metadata/axolotito/${item.blockchain_token_id}.svg`} 
                                  className="w-7 h-7 object-contain"
                                  alt=""
                                  onError={(e) => handleImageError(e, 30)}
                                />
                              </div>
                            )}
                            <div className="truncate">
                              <div className="flex items-center gap-1.5 flex-wrap">
                                <h4 className="text-xs font-black text-white uppercase truncate">
                                  {item.name}
                                </h4>
                                {esPropio && (
                                  <span className="px-1.5 py-0.5 rounded bg-pink-600/90 text-[7px] text-white font-black uppercase tracking-wider animate-pulse shrink-0 shadow-[0_0_6px_rgba(219,39,119,0.5)]">
                                    🏆 TUYO
                                  </span>
                                )}
                                {activeTab === 'boards' && item.is_npc_pool && (
                                  item.npc_retired ? (
                                    <span className="px-1.5 py-0.5 rounded-full bg-amber-900/60 border border-amber-600/40 text-amber-300 text-[7px] font-black uppercase tracking-wider animate-pulse shrink-0">
                                      ⚔️ Gashapon
                                    </span>
                                  ) : (
                                    <span className="px-1.5 py-0.5 rounded-full bg-slate-800 border border-slate-600/40 text-slate-400 text-[7px] font-black uppercase tracking-wider shrink-0">
                                      🤖 En Arena
                                    </span>
                                  )
                                )}
                              </div>
                              <p className="text-[9px] text-slate-500 truncate flex items-center gap-1">
                                <span>👤 {activeTab === 'boards' && item.is_npc_pool ? '🤖 Sistema' : item.owner_nickname}</span>
                                {!item.is_npc_pool && item.owner_vip_tier === 'coral'   && <span title="VIP Coral">🪸</span>}
                                {!item.is_npc_pool && item.owner_vip_tier === 'dorado'  && <span title="VIP Dorado">✨</span>}
                                {!item.is_npc_pool && item.owner_vip_tier === 'axolite' && <span title="VIP Axolite">🌟</span>}
                              </p>
                            </div>
                          </div>
                        </div>

                        {/* Nivel */}
                        <div className="col-span-3 sm:col-span-2 text-center">
                          <span className={`text-xs ${getLevelColor(item.level)}`}>
                            Nv. {item.level}
                          </span>
                          {activeTab === 'boards' && item.streak > 0 && (
                            <div className="text-[8px] text-violet-400 font-extrabold uppercase mt-0.5">
                              🔥 {item.streak} Racha
                            </div>
                          )}
                        </div>

                        {/* Columnas específicas */}
                        {activeTab === 'axolotitos' ? (
                          <>
                            {/* Poder */}
                            <div className="col-span-2 text-center font-mono font-black text-xs text-slate-300">
                              {item.power_rating}
                            </div>
                            {/* Estado */}
                            <div className="col-span-2 text-center">
                              <span className={`px-2 py-0.5 rounded-full text-[8px] font-black uppercase tracking-wider ${
                                item.status === 'idle' ? 'bg-emerald-950 text-emerald-400 border border-emerald-500/20' :
                                item.status === 'sleeping' ? 'bg-indigo-950 text-indigo-400 border border-indigo-500/20 animate-pulse' :
                                'bg-pink-950 text-pink-400 border border-pink-500/20'
                              }`}>
                                {item.status === 'idle' && 'Disponible'}
                                {item.status === 'sleeping' && '😴 Durmiendo'}
                                {item.status === 'playing' && '⚔️ Jugando'}
                                {item.status !== 'idle' && item.status !== 'sleeping' && item.status !== 'playing' && item.status}
                              </span>
                            </div>
                          </>
                        ) : (
                          <>
                            {/* Partidas */}
                            <div className="col-span-2 text-center truncate">
                              <span className="text-xs font-bold text-slate-300">
                                {item.games_won}
                              </span>
                              <span className="text-[9px] text-slate-600"> / {item.games_played}</span>
                              <div className="text-[8px] text-emerald-400 font-semibold mt-0.5">{item.win_rate}% WR</div>
                            </div>
                            {/* CSR */}
                            <div className="col-span-2 text-center">
                              <span className={`px-2 py-0.5 rounded-md text-[9px] font-mono border ${csrBadge?.bg} ${csrBadge?.text}`}>
                                CSR {item.csr}%
                              </span>
                            </div>
                          </>
                        )}

                        {/* Acción */}
                        <div className="col-span-2 text-center">
                          {activeTab === 'boards' ? (
                            item.is_npc_pool ? (
                              <span className="text-[9px] text-slate-600 uppercase font-bold tracking-wider">NPC</span>
                            ) : item.is_listed_for_rent ? (
                              item.is_rented ? (
                                <span className="text-[9px] text-slate-500 font-bold uppercase tracking-wider">Alquilada 🤝</span>
                              ) : esPropio ? (
                                <span className="text-[9px] text-teal-400 font-bold uppercase tracking-wider">Publicada</span>
                              ) : !playerMarketplaceEnabled ? (
                                <span className="text-[9px] text-slate-600 uppercase font-bold tracking-wider">Rentas en pausa</span>
                              ) : (
                                <button
                                  onClick={() => setShowRentModal(item)}
                                  className="px-2.5 py-1 bg-gradient-to-r from-teal-600 to-cyan-500 hover:from-teal-500 hover:to-cyan-400 text-white rounded-lg text-[9px] font-black uppercase tracking-wider transition-all active:scale-95 shadow-[0_0_8px_rgba(20,184,166,0.2)]"
                                >
                                  🤝 Rentar
                                </button>
                              )
                            ) : (
                              <span className="text-[9px] text-slate-600 uppercase font-bold tracking-wider">Privada</span>
                            )
                          ) : (
                            <button 
                              onClick={() => cambiarTab('axolotitos')}
                              className="px-2.5 py-1 bg-slate-900 border border-slate-800 hover:border-pink-500 hover:text-pink-400 text-slate-500 rounded-lg text-[9px] font-black uppercase tracking-wider transition-all"
                            >
                              🔍 Ver
                            </button>
                          )}
                        </div>

                      </div>
                    );
                  })}
                </div>

              </div>

              {/* Botón Ver Más */}
              {data.length > 10 && (
                <div className="text-center pt-2">
                  <button
                    onClick={() => setShowAll(!showAll)}
                    className="px-8 py-3 bg-slate-950 border border-slate-850 hover:border-amber-500 hover:text-amber-300 text-slate-400 rounded-2xl text-xs font-black uppercase tracking-widest transition-all active:scale-95 shadow-lg"
                  >
                    {showAll ? '🔼 Mostrar Menos' : `🔽 Mostrar Top 20 (${data.length - 10} más)`}
                  </button>
                </div>
              )}

            </div>
          )}

        </div>
      )}

      {/* MODAL DE CONFIRMACIÓN DE RENTA RÁPIDA */}
      {playerMarketplaceEnabled && showRentModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 max-w-md w-full animate-in zoom-in duration-200">
            <div className="flex justify-between items-start mb-4">
              <h3 className="text-xl font-black italic text-teal-400 uppercase">Confirmar Contrato de Renta</h3>
              <button 
                onClick={() => setShowRentModal(null)}
                className="text-slate-500 hover:text-slate-300 font-bold"
              >
                ✕
              </button>
            </div>
            
            <p className="text-slate-300 text-xs sm:text-sm mb-5 leading-relaxed">
              ¿Estás seguro de que deseas rentar la tabla <strong className="text-white">"{showRentModal.name}"</strong> por las próximas <strong className="text-white">24 horas</strong>?
            </p>

            <div className="bg-slate-950/80 border border-slate-800/80 rounded-2xl p-4 mb-6 space-y-2">
              <div className="flex justify-between text-xs sm:text-sm">
                <span className="text-slate-400 font-bold">💰 Cuota de Renta:</span>
                <span className="text-amber-500 font-black">{showRentModal.rent_fee_gal} FRJ</span>
              </div>
              <div className="flex justify-between text-xs sm:text-sm">
                <span className="text-slate-400 font-bold">🏆 Distribución de Victorias:</span>
                <span className="text-amber-400 font-black">
                  {showRentModal.rent_share_owner_pct}% Propietario / {100 - showRentModal.rent_share_owner_pct}% Tú
                </span>
              </div>
              <div className="flex justify-between text-xs sm:text-sm">
                <span className="text-slate-400 font-bold">🍀 CSR de la Tabla:</span>
                <span className="text-emerald-400 font-black">{showRentModal.csr}%</span>
              </div>
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => setShowRentModal(null)}
                className="flex-1 py-3 bg-slate-950 border border-slate-800 hover:border-slate-750 text-slate-400 rounded-xl text-xs font-black uppercase tracking-wider transition-all"
              >
                Cancelar
              </button>
              <button
                onClick={handleRentarDirecto}
                disabled={rentingId !== null}
                className="flex-1 py-3 bg-gradient-to-r from-teal-600 to-cyan-500 hover:from-teal-500 hover:to-cyan-400 text-white rounded-xl text-xs font-black uppercase tracking-wider transition-all active:scale-95 flex items-center justify-center gap-2"
              >
                {rentingId ? (
                  <>
                    <span className="w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Procesando...
                  </>
                ) : (
                  '🤝 Confirmar Renta'
                )}
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
