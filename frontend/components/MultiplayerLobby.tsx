import { API_BASE } from "@/lib/api";
import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import {
  Trophy,
  Coins,
  Users,
  Sparkles,
  Info,
  UserCheck,
  Lock,
  Unlock,
  Search,
  Zap,
  Shield,
  RefreshCw,
} from 'lucide-react';

type ActiveTab = 'official' | 'hosted';

export default function MultiplayerLobby({
  userId,
  token,
  balances,
  recargarSaldos
}: {
  userId: string;
  token: string | null;
  balances: any;
  recargarSaldos: () => void;
}) {
  const [activeTab, setActiveTab]           = useState<ActiveTab>('official');
  const [salas, setSalas]                   = useState<any[]>([]);
  const [jackpot, setJackpot]               = useState<any>({ current_amount: 1000, history: [] });
  const [cargando, setCargando]             = useState(true);

  // Hosted rooms state
  const [hostedRooms, setHostedRooms]       = useState<any[]>([]);
  const [cargandoHosted, setCargandoHosted] = useState(false);
  const [busqueda, setBusqueda]             = useState('');
  const [passwords, setPasswords]           = useState<Record<number, string>>({});
  const [joinError, setJoinError]           = useState<Record<number, string>>({});
  const [joiningRoom, setJoiningRoom]       = useState<number | null>(null);

  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const fetchOfficialData = async () => {
    try {
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      const [lobbyRes, jackpotRes] = await Promise.all([
        axios.get(`${API_BASE}/multiplayer/lobby`, { headers }),
        axios.get(`${API_BASE}/multiplayer/jackpot`, { headers })
      ]);
      setSalas(lobbyRes.data.salas_espera || []);
      setJackpot(jackpotRes.data || { current_amount: 1000, history: [] });
      setErrorMsg(null);
    } catch (err) {
      console.error("Error cargando lobby oficial:", err);
      setErrorMsg("Error de sincronización con el servidor de salas.");
    } finally {
      setCargando(false);
    }
  };

  const fetchHostedRooms = async (search?: string) => {
    setCargandoHosted(true);
    try {
      const params = search ? `?search=${encodeURIComponent(search)}` : '';
      const res = await axios.get(`${API_BASE}/multiplayer/player-rooms${params}`);
      setHostedRooms(res.data.rooms || []);
    } catch (err) {
      console.error("Error cargando salas de anfitriones:", err);
    } finally {
      setCargandoHosted(false);
    }
  };

  useEffect(() => {
    fetchOfficialData();
    pollingRef.current = setInterval(fetchOfficialData, 5000);
    return () => { if (pollingRef.current) clearInterval(pollingRef.current); };
  }, [token]);

  useEffect(() => {
    if (activeTab === 'hosted') {
      fetchHostedRooms(busqueda);
    }
  }, [activeTab]);

  // Debounced search
  useEffect(() => {
    if (activeTab !== 'hosted') return;
    const t = setTimeout(() => fetchHostedRooms(busqueda), 350);
    return () => clearTimeout(t);
  }, [busqueda]);

  const getSkinColorClass = (color: string) => {
    switch (color) {
      case 'pink':       return 'bg-pink-400 shadow-[0_0_10px_rgba(244,114,182,0.6)]';
      case 'gold':       return 'bg-yellow-400 shadow-[0_0_10px_rgba(250,204,21,0.6)]';
      case 'blue':       return 'bg-blue-400 shadow-[0_0_10px_rgba(96,165,250,0.6)]';
      case 'purple':     return 'bg-purple-400 shadow-[0_0_10px_rgba(192,132,252,0.6)]';
      case 'green':      return 'bg-green-400 shadow-[0_0_10px_rgba(74,222,128,0.6)]';
      case 'gray_light': return 'bg-gray-300 shadow-[0_0_10px_rgba(209,213,219,0.6)]';
      case 'gray_dark':  return 'bg-gray-600 shadow-[0_0_10px_rgba(75,85,99,0.6)]';
      default:           return 'bg-pink-300 shadow-[0_0_10px_rgba(244,114,182,0.4)]';
    }
  };

  const speedLabel = (speed: string) => {
    if (speed === 'fast') return '⚡ Rápido';
    if (speed === 'slow') return '🐢 Lento';
    return '⏱ Normal';
  };

  const patternLabel = (p: string) => {
    if (p === 'line')    return 'Línea';
    if (p === 'corners') return 'Esquinas';
    if (p === 'full')    return 'Llena';
    return p;
  };

  return (
    <div className="w-full flex flex-col gap-6 text-left">
      {/* ERROR BANNER */}
      {errorMsg && (
        <div className="bg-red-950/60 border border-red-500/50 p-4 rounded-xl text-red-300 text-sm flex items-center gap-2">
          <Info className="h-5 w-5 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* === GOLDEN JACKPOT PANEL === */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-amber-950/80 via-yellow-950/60 to-amber-950/80 p-6 sm:p-8 border border-yellow-500/40 shadow-[0_0_40px_rgba(234,179,8,0.15)] flex flex-col md:flex-row gap-6 items-center justify-between">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-yellow-500/10 rounded-full blur-[80px] pointer-events-none" />
        <div className="flex flex-col gap-2 text-center md:text-left z-10">
          <div className="flex items-center justify-center md:justify-start gap-2 text-yellow-400 font-extrabold text-sm uppercase tracking-widest">
            <Sparkles className="h-5 w-5 animate-pulse text-yellow-300" />
            <span>Jackpot de Oro Axolotto</span>
          </div>
          <h2 className="text-4xl sm:text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-yellow-300 via-amber-200 to-yellow-400 drop-shadow-[0_2px_10px_rgba(234,179,8,0.3)] animate-pulse">
            {jackpot.current_amount?.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} <span className="text-xl sm:text-2xl text-yellow-300/80 font-bold">FRJ</span>
          </h2>
          <p className="text-yellow-200/60 text-xs mt-1">
            Requisito: ¡Haz Línea o Cuadrito en las primeras 4-6 cartas! (Min. 5 tablas de humanos y 2 jugadores)
          </p>
        </div>
        <div className="w-full md:w-80 bg-gray-950/80 rounded-2xl border border-yellow-600/30 p-4 z-10 shadow-inner">
          <div className="flex items-center gap-1.5 text-yellow-400 font-bold text-xs uppercase tracking-wider mb-2 border-b border-yellow-600/20 pb-2">
            <Trophy className="h-3.5 w-3.5" />
            <span>Últimos Ganadores</span>
          </div>
          <div className="flex flex-col gap-2 max-h-28 overflow-y-auto pr-1 text-xs">
            {jackpot.history && jackpot.history.length > 0 ? (
              jackpot.history.map((win: any) => (
                <div key={win.id} className="flex justify-between items-center gap-2 border-b border-gray-900 pb-1.5 last:border-b-0">
                  <div className="flex flex-col truncate">
                    <span className="font-bold text-pink-200 truncate">{win.axo_name}</span>
                    <span className="text-[10px] text-gray-500 truncate">de {win.user_nickname}</span>
                  </div>
                  <div className="text-right shrink-0">
                    <span className="font-bold text-amber-400">+{win.amount_won?.toFixed(1)} FRJ</span>
                    <p className="text-[9px] text-gray-400">Turno {win.cards_drawn_count}</p>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-gray-500 italic text-center py-4">Nadie ha ganado el Jackpot todavía.</p>
            )}
          </div>
        </div>
      </div>

      {/* === TAB BAR === */}
      <div className="flex rounded-2xl overflow-hidden border border-white/5 bg-slate-900/60">
        <button
          onClick={() => setActiveTab('official')}
          className={`flex-1 py-3 text-xs font-black uppercase tracking-wider transition-all flex items-center justify-center gap-1.5 ${
            activeTab === 'official'
              ? 'bg-emerald-900/50 text-emerald-300 border-b-2 border-emerald-500'
              : 'text-slate-500 hover:text-slate-300'
          }`}
        >
          <Shield className="h-3.5 w-3.5" />
          Salas Oficiales
        </button>
        <button
          onClick={() => setActiveTab('hosted')}
          className={`flex-1 py-3 text-xs font-black uppercase tracking-wider transition-all flex items-center justify-center gap-1.5 ${
            activeTab === 'hosted'
              ? 'bg-indigo-900/50 text-indigo-300 border-b-2 border-indigo-500'
              : 'text-slate-500 hover:text-slate-300'
          }`}
        >
          <Users className="h-3.5 w-3.5" />
          Salas de Anfitriones
        </button>
      </div>

      {/* === OFFICIAL ROOMS TAB === */}
      {activeTab === 'official' && (
        cargando ? (
          <div className="flex flex-col items-center justify-center py-20 gap-3 text-pink-300">
            <div className="w-12 h-12 border-4 border-pink-500/25 border-t-pink-500 rounded-full animate-spin" />
            <p className="text-sm font-semibold">Cargando salas en tiempo real...</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {renderOfficialRoomCard(
              "Charco de Novatos",
              "rookie",
              10.0,
              salas.find(s => s.room_type === "rookie")
            )}
            {renderOfficialRoomCard(
              "Fosa del Campeón",
              "champion",
              50.0,
              salas.find(s => s.room_type === "champion")
            )}
          </div>
        )
      )}

      {/* === HOSTED ROOMS TAB === */}
      {activeTab === 'hosted' && (
        <div className="flex flex-col gap-4">
          {/* Search bar */}
          <div className="flex items-center gap-2 bg-slate-800/60 border border-white/10 rounded-2xl px-4 py-2.5">
            <Search className="h-4 w-4 text-slate-500 shrink-0" />
            <input
              type="text"
              value={busqueda}
              onChange={e => setBusqueda(e.target.value)}
              placeholder="Buscar por nombre de sala o anfitrión..."
              className="flex-1 bg-transparent text-sm text-white placeholder-slate-600 outline-none font-medium"
            />
            {cargandoHosted && (
              <RefreshCw className="h-3.5 w-3.5 text-indigo-400 animate-spin shrink-0" />
            )}
          </div>

          {cargandoHosted && hostedRooms.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16 gap-3 text-indigo-300">
              <div className="w-10 h-10 border-4 border-indigo-500/25 border-t-indigo-500 rounded-full animate-spin" />
              <p className="text-sm font-semibold">Buscando salas de anfitriones...</p>
            </div>
          ) : hostedRooms.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16 gap-3 text-slate-600">
              <Users className="h-10 w-10 stroke-1" />
              <p className="text-sm font-semibold">No hay salas de anfitriones activas</p>
              <p className="text-xs text-slate-700">Crea tu propia sala desde "Mi Cenote" (Nv.3+)</p>
            </div>
          ) : (
            <div className="flex flex-col gap-3">
              {hostedRooms.map(room => renderHostedRoomCard(room))}
            </div>
          )}
        </div>
      )}
    </div>
  );

  function renderOfficialRoomCard(title: string, type: string, entryFee: number, roomData: any) {
    const totalTables   = roomData ? roomData.total_boards : 0;
    const axoList       = roomData ? roomData.axolotitos : [];
    const roomName      = roomData ? roomData.name : `${title} #1`;
    const fillPercent   = Math.min(100, (totalTables / 30) * 100);
    const secsUntilStart: number = roomData?.seconds_until_start ?? 60;

    return (
      <div className={`rounded-2xl p-6 border flex flex-col gap-4 shadow-xl transition-all hover:scale-[1.01] ${
        type === "champion"
          ? "bg-gradient-to-b from-indigo-950/40 to-slate-900/60 border-indigo-500/30 shadow-[0_0_20px_rgba(99,102,241,0.05)]"
          : "bg-gradient-to-b from-emerald-950/30 to-slate-900/60 border-emerald-500/20 shadow-[0_0_20px_rgba(16,185,129,0.05)]"
      }`}>
        <div className="flex justify-between items-start">
          <div className="flex flex-col">
            <span className={`text-xs font-bold uppercase tracking-widest mb-1 ${
              type === "champion" ? "text-indigo-400" : "text-emerald-400"
            }`}>
              {type === "champion" ? "Fosa del Campeón" : "Charco de Novatos"}
            </span>
            <h3 className="text-xl font-extrabold text-white">{roomName}</h3>
          </div>
          <div className="flex flex-col items-end">
            <div className="flex items-center gap-1 text-amber-400 font-bold bg-amber-950/50 px-2.5 py-1 rounded-full border border-amber-500/20 text-sm">
              <Coins className="h-4 w-4" />
              <span>{entryFee} FRJ</span>
            </div>
            <span className="text-[10px] text-gray-500 mt-1">Costo por Tabla</span>
          </div>
        </div>

        <div className="flex flex-col gap-1.5 mt-2">
          <div className="flex justify-between text-xs font-semibold text-gray-300">
            <div className="flex items-center gap-1">
              <Users className="h-3.5 w-3.5" />
              <span>{totalTables} / 30 Tablas</span>
            </div>
            <span>{Math.round(fillPercent)}% lleno</span>
          </div>
          <div className="w-full bg-gray-950 h-2.5 rounded-full overflow-hidden border border-gray-800 shadow-inner">
            <div
              style={{ width: `${fillPercent}%` }}
              className={`h-full rounded-full transition-all duration-500 ${
                type === "champion" ? "bg-indigo-500" : "bg-emerald-500"
              }`}
            />
          </div>
          <p className="text-[10px] text-gray-500 italic mt-0.5">
            {totalTables >= 30
              ? '🚀 ¡Sala llena! Iniciando…'
              : totalTables >= 1
                ? `⏱ Inicia en ~${secsUntilStart}s · o al llegar a 30 tablas`
                : 'Inicia en ~60s con la primera tabla inscrita'}
          </p>
        </div>

        <div className="flex flex-col gap-2 mt-2 flex-grow">
          <span className="text-xs font-bold text-gray-400 uppercase tracking-wider">Axolotitos en Espera:</span>
          <div className="bg-gray-950/70 rounded-xl p-3 border border-gray-900 min-h-24 max-h-48 overflow-y-auto flex flex-col gap-2">
            {axoList.length > 0 ? (
              axoList.map((axo: any) => (
                <div key={axo.id} className="flex items-center justify-between gap-3 text-xs bg-gray-900/50 p-2 rounded-lg border border-gray-800">
                  <div className="flex items-center gap-2 truncate">
                    <div className={`w-3.5 h-3.5 rounded-full ${getSkinColorClass(axo.skin_color)}`} />
                    <span className="font-bold text-gray-200 truncate">{axo.name}</span>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <span className="text-[10px] text-gray-400 bg-gray-950 px-2 py-0.5 rounded border border-gray-800 font-medium">
                      {axo.boards_count} {axo.boards_count === 1 ? 'Tabla' : 'Tablas'}
                    </span>
                    {axo.owner_id === userId && (
                      <span className="text-[9px] text-pink-400 bg-pink-950/40 border border-pink-500/25 px-1.5 py-0.5 rounded font-bold flex items-center gap-0.5">
                        <UserCheck className="h-2.5 w-2.5" />
                        <span>Tuyo</span>
                      </span>
                    )}
                  </div>
                </div>
              ))
            ) : (
              <div className="flex flex-col items-center justify-center py-6 text-gray-600 gap-1">
                <Users className="h-6 w-6 stroke-1" />
                <p className="italic">Esperando axolotitos...</p>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  function renderHostedRoomCard(room: any) {
    const isFull      = room.current_players >= room.max_players;
    const hasPassword = room.has_password;
    const pw          = passwords[room.id] ?? '';
    const err         = joinError[room.id];
    const isJoining   = joiningRoom === room.id;

    const fillPct = Math.min(100, (room.current_players / room.max_players) * 100);

    return (
      <div
        key={room.id}
        className="bg-gradient-to-b from-indigo-950/30 to-slate-900/60 border border-indigo-500/20 rounded-2xl p-4 flex flex-col gap-3"
      >
        {/* Header row */}
        <div className="flex items-start justify-between gap-2">
          <div className="min-w-0">
            <div className="flex items-center gap-1.5 flex-wrap">
              <h4 className="text-sm font-black text-white truncate">{room.name}</h4>
              {hasPassword && <Lock className="h-3 w-3 text-amber-400 shrink-0" />}
              {!hasPassword && <Unlock className="h-3 w-3 text-emerald-500 shrink-0" />}
            </div>
            <div className="flex items-center gap-1 mt-0.5">
              <span className="text-[10px] text-slate-500 font-bold">Anfitrión:</span>
              <span className="text-[10px] text-indigo-300 font-black">{room.host_name}</span>
              {room.host_vip_tier && (
                <span className={`text-[7px] font-black px-1 py-0.5 rounded border ${
                  room.host_vip_tier === 'axolite' ? 'text-purple-300 bg-purple-950/50 border-purple-500/30' :
                  room.host_vip_tier === 'dorado'  ? 'text-amber-300 bg-amber-950/50 border-amber-500/30' :
                  'text-teal-300 bg-teal-950/50 border-teal-500/30'
                }`}>
                  VIP {room.host_vip_tier}
                </span>
              )}
            </div>
          </div>
          <div className="flex flex-col items-end shrink-0">
            <div className="flex items-center gap-1 text-amber-400 font-black text-sm bg-amber-950/40 px-2 py-0.5 rounded-full border border-amber-500/20">
              <Coins className="h-3.5 w-3.5" />
              {room.buy_in_frj} FRJ
            </div>
          </div>
        </div>

        {/* Config chips */}
        <div className="flex flex-wrap gap-1.5">
          <span className="text-[9px] font-black text-slate-400 bg-slate-800/60 px-2 py-0.5 rounded-full border border-white/5">
            {speedLabel(room.speed)}
          </span>
          {(room.win_patterns || []).map((p: string) => (
            <span key={p} className="text-[9px] font-black text-indigo-300 bg-indigo-950/40 px-2 py-0.5 rounded-full border border-indigo-500/20">
              {patternLabel(p)}
            </span>
          ))}
          <span className="text-[9px] font-black text-slate-500 bg-slate-800/40 px-2 py-0.5 rounded-full border border-white/5">
            {room.game_type || 'Lotería Clásica'}
          </span>
        </div>

        {/* Players bar */}
        <div className="flex flex-col gap-1">
          <div className="flex justify-between text-[10px] font-bold text-slate-400">
            <div className="flex items-center gap-1">
              <Users className="h-3 w-3" />
              <span>{room.current_players} / {room.max_players} jugadores</span>
            </div>
            {isFull && <span className="text-red-400 font-black">LLENA</span>}
          </div>
          <div className="h-1.5 bg-slate-800 rounded-full overflow-hidden">
            <div
              style={{ width: `${fillPct}%` }}
              className={`h-full rounded-full transition-all ${isFull ? 'bg-red-500' : 'bg-indigo-500'}`}
            />
          </div>
        </div>

        {/* Password field + join button */}
        {!isFull && (
          <div className="flex flex-col gap-2">
            {hasPassword && (
              <div className="flex items-center gap-2 bg-slate-800/60 border border-amber-500/20 rounded-xl px-3 py-2">
                <Lock className="h-3.5 w-3.5 text-amber-400 shrink-0" />
                <input
                  type="password"
                  value={pw}
                  onChange={e => setPasswords(prev => ({ ...prev, [room.id]: e.target.value }))}
                  placeholder="Contraseña de la sala..."
                  className="flex-1 bg-transparent text-xs text-white placeholder-slate-600 outline-none font-medium"
                />
              </div>
            )}
            {err && (
              <p className="text-[10px] text-red-400 font-bold flex items-center gap-1">
                <Info className="h-3 w-3 shrink-0" />
                {err}
              </p>
            )}
            <button
              disabled={isJoining || (hasPassword && !pw.trim())}
              onClick={() => handleJoinHostedRoom(room.id, hasPassword ? pw : undefined)}
              className="w-full py-2 rounded-xl font-black text-[11px] uppercase tracking-wider transition-all active:scale-95 flex items-center justify-center gap-1.5 bg-gradient-to-r from-indigo-700 to-purple-700 hover:from-indigo-600 hover:to-purple-600 text-white disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {isJoining ? (
                <><RefreshCw className="h-3.5 w-3.5 animate-spin" /> Uniéndose…</>
              ) : (
                <><Zap className="h-3.5 w-3.5" /> Configurar entrada</>
              )}
            </button>
          </div>
        )}
        {isFull && (
          <div className="text-center text-[10px] text-red-400 font-bold py-1">
            Sala llena — no acepta más jugadores
          </div>
        )}
      </div>
    );
  }

  async function handleJoinHostedRoom(roomId: number, password?: string) {
    if (!token) {
      setJoinError(prev => ({ ...prev, [roomId]: 'Necesitas iniciar sesión para unirte.' }));
      return;
    }
    setJoiningRoom(roomId);
    setJoinError(prev => ({ ...prev, [roomId]: '' }));

    // If room has password, validate it first via a quick GET probe
    if (password) {
      try {
        // HEAD/GET probe: try joining with minimal params just to check password validity
        await axios.post(
          `${API_BASE}/multiplayer/join-room/${roomId}`,
          {
            axolotito_id: 0,
            boards: [],
            budget_gal: 0,
            loss_limit_pct: 1.0,
            profit_limit_pct: 2.0,
            password,
          },
          { headers: { Authorization: `Bearer ${token}` } }
        );
        // If we get here (unlikely with axolotito_id=0), clear password
        setPasswords(prev => ({ ...prev, [roomId]: '' }));
      } catch (err: any) {
        const detail: string = err?.response?.data?.detail || '';
        // Password errors return 403 or mention "contraseña"
        if (
          err?.response?.status === 403 ||
          detail.toLowerCase().includes('contraseña') ||
          detail.toLowerCase().includes('password') ||
          detail.toLowerCase().includes('incorrecta')
        ) {
          setJoinError(prev => ({ ...prev, [roomId]: detail || 'Contraseña incorrecta.' }));
          setJoiningRoom(null);
          return;
        }
        // Other errors (axolotito/boards) mean password was accepted
        // Store room_id so PlayMode can pick it up
      }
    }

    // Password OK (or not required) — store selected room for PlayMode
    sessionStorage.setItem('pending_room_id', String(roomId));
    setJoinError(prev => ({ ...prev, [roomId]: '' }));
    setJoiningRoom(null);
    setPasswords(prev => ({ ...prev, [roomId]: '' }));
    // Show info — full registration happens in PlayMode
    alert(`✅ Sala seleccionada. Ve a la pestaña "Jugar" para configurar tu entrada a "${hostedRooms.find(r => r.id === roomId)?.name || 'esta sala'}".`);
  }
}
