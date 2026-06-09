"use client";
import { API_BASE } from "@/lib/api";

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Play, Users, Coins, Lock, Home } from 'lucide-react';

interface SalaSelectScreenProps {
  token: string | null;
  selectedRoom: 'rookie' | 'champion';
  onRoomSelect: (r: 'rookie' | 'champion') => void;
  onPlay: () => void;
  registering: boolean;
  error: string | null;
  budget: number;
  multiBoards: number[];
}

interface SalaData {
  room_type: string;
  jugadores_actuales: number;
  max_jugadores: number;
  jackpot_actual?: number;
  acumulado?: number;
}

interface PlayerRoom {
  id: number;
  name: string;
  host_name: string;
  host_vip_tier: string | null;
  buy_in_frj: number;
  max_players: number;
  current_players: number;
  speed: string;
  win_patterns: string[];
  game_type: string;
  has_password: boolean;
}

export default function SalaSelectScreen({
  token,
  selectedRoom,
  onRoomSelect,
  onPlay,
  registering,
  error,
  budget,
  multiBoards,
}: SalaSelectScreenProps) {
  const [salas, setSalas] = useState<SalaData[]>([]);
  const [jackpot, setJackpot] = useState<number>(0);
  const [playerRooms, setPlayerRooms] = useState<PlayerRoom[]>([]);

  const fetchLobby = async () => {
    try {
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      const [lobbyRes, jackpotRes, playerRes] = await Promise.all([
        axios.get(`${API_BASE}/multiplayer/lobby`, { headers }),
        axios.get(`${API_BASE}/multiplayer/jackpot`, { headers }),
        axios.get(`${API_BASE}/multiplayer/player-rooms`, { headers }),
      ]);
      setSalas(lobbyRes.data.salas_espera || []);
      setJackpot(jackpotRes.data?.current_amount ?? 0);
      setPlayerRooms(playerRes.data?.rooms || []);
    } catch {
      // Silently fail — keep showing last data
    }
  };

  useEffect(() => {
    fetchLobby();
    const interval = setInterval(fetchLobby, 10_000);
    return () => clearInterval(interval);
  }, [token]);

  const getSala = (type: 'rookie' | 'champion'): SalaData | undefined =>
    salas.find((s) => s.room_type === type);

  const RoomCard = ({
    type,
    label,
    sublabel,
    entryFee,
    prize,
    accentActive,
    accentBorder,
    accentText,
    accentBg,
  }: {
    type: 'rookie' | 'champion';
    label: string;
    sublabel: string;
    entryFee: number;
    prize: number;
    accentActive: string;
    accentBorder: string;
    accentText: string;
    accentBg: string;
  }) => {
    const sala   = getSala(type);
    const cur    = sala?.jugadores_actuales ?? 0;
    const max    = sala?.max_jugadores ?? 0;
    const fillPct= max > 0 ? Math.round((cur / max) * 100) : 0;
    const almostFull = fillPct >= 80;
    const isSelected = selectedRoom === type;

    return (
      <button
        onClick={() => onRoomSelect(type)}
        className={`w-full text-left p-5 rounded-3xl border transition-all relative overflow-hidden ${
          isSelected ? `bg-slate-900 ${accentActive}` : `bg-slate-900/40 ${accentBorder} hover:bg-slate-900/60`
        }`}
      >
        {/* Almost full pulse */}
        {almostFull && (
          <div className="absolute inset-0 border-2 border-amber-400/40 rounded-3xl animate-pulse pointer-events-none" />
        )}

        <div className="flex items-start justify-between gap-2">
          <div>
            <span className={`text-[9px] font-black uppercase tracking-widest px-2 py-0.5 rounded-full border ${accentBg} ${accentText}`}>
              {label}
            </span>
            <h4 className="text-base font-black text-white uppercase mt-1.5">{sublabel}</h4>
          </div>
          {isSelected && (
            <div className="w-6 h-6 rounded-full bg-[var(--brand-hot)] flex items-center justify-center shrink-0">
              <span className="text-white text-[10px] font-black">✓</span>
            </div>
          )}
        </div>

        {/* Player fill bar */}
        <div className="mt-3 space-y-1">
          <div className="flex items-center justify-between text-[9px] font-black">
            <div className="flex items-center gap-1 text-slate-400">
              <Users size={10} /> {cur} / {max || '?'} jugadores
            </div>
            {almostFull && (
              <span className="text-amber-400 animate-pulse">¡Sale pronto!</span>
            )}
          </div>
          <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-700 ${
                almostFull ? 'bg-amber-400' : type === 'rookie' ? 'bg-indigo-500' : 'bg-pink-500'
              }`}
              style={{ width: `${fillPct}%` }}
            />
          </div>
        </div>

        {/* Fees */}
        <div className="mt-3 flex items-center justify-between border-t border-slate-800/60 pt-2.5">
          <div>
            <p className="text-[8px] text-slate-500 uppercase tracking-wider">Entrada/tabla</p>
            <p className="text-sm font-black text-amber-400 flex items-center gap-0.5">
              <Coins size={11} /> {entryFee} FRJ
            </p>
          </div>
          <div className="text-right">
            <p className="text-[8px] text-slate-500 uppercase tracking-wider">Premio victoria</p>
            <p className="text-sm font-black text-[var(--brand-hot)]">{prize} FRJ</p>
          </div>
        </div>
      </button>
    );
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-black text-slate-400 uppercase tracking-widest">Elige tu Sala</h3>
        {jackpot > 0 && (
          <div className="text-[9px] font-black text-amber-400 animate-pulse">
            🏆 Jackpot: {jackpot.toLocaleString()} FRJ
          </div>
        )}
      </div>

      {/* Summary pill */}
      <div className="bg-slate-950/60 border border-slate-800 rounded-xl px-3 py-2 text-[10px] text-slate-400 flex flex-wrap gap-x-3 gap-y-1">
        <span>📋 <strong className="text-white">{multiBoards.length}</strong> tabla(s)</span>
        <span>💰 Presupuesto: <strong className="text-amber-400">{budget} FRJ</strong></span>
      </div>

      {error && (
        <div className="bg-red-950/50 border border-red-500/30 text-red-300 text-[10px] font-bold rounded-xl p-2.5">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <RoomCard
          type="rookie"
          label="Rango Novatos"
          sublabel="Charco de Novatos"
          entryFee={10}
          prize={35}
          accentActive="border-indigo-500/80 shadow-[0_0_20px_rgba(99,102,241,0.2)]"
          accentBorder="border-slate-800"
          accentText="text-indigo-300"
          accentBg="bg-indigo-950/60 border-indigo-500/30"
        />
        <RoomCard
          type="champion"
          label="Rango Pro"
          sublabel="Fosa del Campeón"
          entryFee={50}
          prize={200}
          accentActive="border-pink-500/80 shadow-[0_0_20px_rgba(244,63,94,0.2)]"
          accentBorder="border-slate-800"
          accentText="text-pink-300"
          accentBg="bg-pink-950/60 border-pink-500/30"
        />
      </div>

      {/* Player-Hosted Rooms */}
      {playerRooms.length > 0 && (
        <div className="mt-2">
          <div className="flex items-center gap-2 mb-2">
            <h3 className="text-[10px] font-black text-amber-400 uppercase tracking-widest">
              <Home size={10} className="inline mr-1" /> Salas de Jugadores
            </h3>
            <span className="text-[8px] text-slate-600 font-bold">{playerRooms.length} activa(s)</span>
          </div>
          <div className="space-y-2">
            {playerRooms.slice(0, 3).map(room => (
              <div
                key={room.id}
                className="bg-slate-900/40 border border-amber-500/15 hover:border-amber-500/30 rounded-xl p-3 transition-all"
              >
                <div className="flex items-start justify-between mb-1.5">
                  <div>
                    <div className="flex items-center gap-1.5">
                      <span className="text-xs font-black text-white">{room.name}</span>
                      {room.has_password && <Lock size={8} className="text-amber-400" />}
                      {room.host_vip_tier && (
                        <span className="text-[7px] font-black text-yellow-400 bg-yellow-950/50 px-1 py-0.5 rounded">
                          {room.host_vip_tier.toUpperCase()}
                        </span>
                      )}
                    </div>
                    <span className="text-[9px] text-slate-500">por {room.host_name}</span>
                  </div>
                  <span className={`text-[8px] font-black px-2 py-0.5 rounded-full ${
                    room.speed === 'turbo' ? 'bg-purple-900/50 text-purple-300' :
                    room.speed === 'rápido' ? 'bg-amber-900/50 text-amber-300' :
                    'bg-slate-800 text-slate-400'
                  }`}>
                    {room.speed === 'normal' ? '🐢' : room.speed === 'rápido' ? '🐇' : '⚡'} {room.speed}
                  </span>
                </div>
                <div className="flex items-center justify-between text-[9px]">
                  <div className="flex items-center gap-3">
                    <span className="text-amber-400 font-black flex items-center gap-0.5">
                      <Coins size={9} /> {room.buy_in_frj} FRJ
                    </span>
                    <span className="text-slate-400 flex items-center gap-0.5">
                      <Users size={9} /> {room.current_players}/{room.max_players}
                    </span>
                  </div>
                  <span className="text-slate-600 text-[8px] font-bold uppercase">
                    {room.win_patterns.map(p => {
                      const icons: Record<string, string> = {
                        line: '📏', cuadrito: '🟫', pocito: '🧿',
                        esquinas: '🔲', cruz: '✝️', cruz_diagonal: '✖️',
                        l_shape: '🔡', z_shape: '🅿️', full_board: '🏆',
                      };
                      return icons[p] ?? '🎴';
                    }).join(' ')}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* CTA */}
      <div className="pt-1">
        <button
          onClick={onPlay}
          disabled={registering}
          className="w-full py-4 bg-gradient-to-r from-[var(--brand-hot)] to-indigo-600 hover:from-pink-500 hover:to-indigo-500 disabled:from-slate-800 disabled:to-slate-900 disabled:text-slate-500 text-white font-black text-xl uppercase tracking-widest rounded-2xl transition-all shadow-[0_0_30px_var(--brand-glow)] active:scale-[0.97] flex items-center justify-center gap-3 animate-sheet-up border border-white/5"
          style={{ borderRadius: '20px' }}
        >
          {registering ? (
            <>
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              Inscribiendo...
            </>
          ) : (
            <>
              <Play size={20} fill="currentColor" /> JUGAR
            </>
          )}
        </button>
      </div>
    </div>
  );
}
