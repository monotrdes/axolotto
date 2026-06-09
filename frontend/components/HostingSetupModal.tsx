"use client";

import React, { useState } from 'react';
import axios from 'axios';
import { X, Lock, Users, Zap, Gamepad2, Hash } from 'lucide-react';
import { API_BASE } from '@/lib/api';

const API = `${API_BASE}`;

interface HostingSetupModalProps {
  token: string | null;
  isOpen: boolean;
  onClose: () => void;
  onCreated: () => void;
  tableSeats: number;
}

export default function HostingSetupModal({
  token,
  isOpen,
  onClose,
  onCreated,
  tableSeats,
}: HostingSetupModalProps) {
  const [name, setName] = useState('Mi Sala');
  const [buyIn, setBuyIn] = useState(50);
  const [maxPlayers, setMaxPlayers] = useState(Math.min(4, tableSeats));
  const [visibility, setVisibility] = useState<'public' | 'friends' | 'private'>('public');
  const [speed, setSpeed] = useState<'normal' | 'rápido' | 'turbo'>('normal');
  const [winPatterns, setWinPatterns] = useState<string[]>(['line', 'cuadrito']);
  const [password, setPassword] = useState('');
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const togglePattern = (p: string) => {
    setWinPatterns(prev =>
      prev.includes(p) ? prev.filter(x => x !== p) : [...prev, p]
    );
  };

  const handleCreate = async () => {
    if (!name.trim() || name.trim().length < 2) {
      setError('El nombre debe tener al menos 2 caracteres.');
      return;
    }
    if (winPatterns.length === 0) {
      setError('Selecciona al menos un patrón de victoria.');
      return;
    }

    setCreating(true);
    setError(null);
    try {
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      await axios.post(`${API}/multiplayer/create-room`, {
        name: name.trim(),
        game_type: 'lotería_clásica',
        buy_in_frj: buyIn,
        max_players: maxPlayers,
        visibility,
        speed,
        win_patterns: winPatterns,
        password: password || null,
      }, { headers });
      onCreated();
      onClose();
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Error al crear sala.');
    } finally {
      setCreating(false);
    }
  };

  // Buy-in suggestions
  const buyInOptions = [
    { label: 'Casual', value: 25 },
    { label: 'Normal', value: 50 },
    { label: 'Alto', value: 100 },
    { label: 'VIP', value: 250 },
  ];

  return (
    <div className="fixed inset-0 z-[130] flex items-end justify-center bg-black/70" onClick={onClose}>
      <div
        className="bg-slate-900 rounded-t-3xl w-full max-w-md max-h-[85vh] overflow-y-auto"
        onClick={e => e.stopPropagation()}
      >
        {/* Handle */}
        <div className="flex justify-center pt-3 pb-1">
          <div className="w-10 h-1 rounded-full bg-slate-700" />
        </div>

        <div className="px-5 pb-8 pt-2">
          {/* Header */}
          <div className="flex items-center justify-between mb-5">
            <div>
              <h3 className="text-lg font-black text-white">🎴 Hostear Partida</h3>
              <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider mt-0.5">
                Configura las reglas de tu sala
              </p>
            </div>
            <button onClick={onClose} className="p-2 rounded-full bg-slate-800 text-slate-400 hover:text-white">
              <X size={16} />
            </button>
          </div>

          {/* Error */}
          {error && (
            <div className="mb-4 p-3 rounded-xl bg-red-900/30 border border-red-500/30 text-red-400 text-xs font-bold">
              {error}
            </div>
          )}

          {/* Room Name */}
          <div className="mb-4">
            <label className="text-[9px] font-black text-slate-500 uppercase tracking-widest mb-1.5 block">
              <Hash size={10} className="inline mr-1" /> Nombre de la sala
            </label>
            <input
              type="text"
              value={name}
              onChange={e => setName(e.target.value)}
              maxLength={30}
              placeholder="Ej: La Cueva del Lotero"
              className="w-full bg-slate-800/80 border border-white/10 rounded-xl px-3 py-2.5 text-white text-sm font-bold placeholder:text-slate-600 focus:outline-none focus:border-amber-500/40 transition-colors"
            />
          </div>

          {/* Buy-in */}
          <div className="mb-4">
            <label className="text-[9px] font-black text-slate-500 uppercase tracking-widest mb-1.5 block">
              💰 Buy-in (FRJ)
            </label>
            <div className="grid grid-cols-4 gap-1.5 mb-2">
              {buyInOptions.map(opt => (
                <button
                  key={opt.value}
                  onClick={() => setBuyIn(opt.value)}
                  className={`py-2 rounded-lg text-[10px] font-black transition-all ${
                    buyIn === opt.value
                      ? 'bg-amber-600 text-white border border-amber-400'
                      : 'bg-slate-800 text-slate-400 border border-white/5 hover:border-amber-500/20'
                  }`}
                >
                  {opt.label}
                  <span className="block text-[8px] opacity-70">{opt.value} FRJ</span>
                </button>
              ))}
            </div>
            <input
              type="range"
              min={10}
              max={1000}
              step={5}
              value={buyIn}
              onChange={e => setBuyIn(Number(e.target.value))}
              className="w-full accent-amber-500"
            />
            <div className="flex justify-between text-[8px] text-slate-600 font-bold mt-1">
              <span>10 FRJ</span>
              <span className="text-amber-400 font-black">{buyIn} FRJ</span>
              <span>1000 FRJ</span>
            </div>
          </div>

          {/* Players */}
          <div className="mb-4">
            <label className="text-[9px] font-black text-slate-500 uppercase tracking-widest mb-1.5 block">
              <Users size={10} className="inline mr-1" /> Jugadores (máx {tableSeats} en tu mesa)
            </label>
            <div className="flex gap-1.5">
              {[2, 4, 6, 8].filter(n => n <= tableSeats).map(n => (
                <button
                  key={n}
                  onClick={() => setMaxPlayers(n)}
                  className={`flex-1 py-2 rounded-lg text-[10px] font-black transition-all ${
                    maxPlayers === n
                      ? 'bg-teal-600 text-white border border-teal-400'
                      : 'bg-slate-800 text-slate-400 border border-white/5 hover:border-teal-500/20'
                  }`}
                >
                  {n}
                </button>
              ))}
            </div>
          </div>

          {/* Speed */}
          <div className="mb-4">
            <label className="text-[9px] font-black text-slate-500 uppercase tracking-widest mb-1.5 block">
              <Zap size={10} className="inline mr-1" /> Velocidad
            </label>
            <div className="flex gap-1.5">
              {(['normal', 'rápido', 'turbo'] as const).map(s => (
                <button
                  key={s}
                  onClick={() => setSpeed(s)}
                  className={`flex-1 py-2 rounded-lg text-[10px] font-black uppercase transition-all ${
                    speed === s
                      ? 'bg-indigo-600 text-white border border-indigo-400'
                      : 'bg-slate-800 text-slate-400 border border-white/5 hover:border-indigo-500/20'
                  }`}
                >
                  {s === 'normal' ? '🐢 Normal' : s === 'rápido' ? '🐇 Rápido' : '⚡ Turbo'}
                </button>
              ))}
            </div>
          </div>

          {/* Win Patterns */}
          <div className="mb-4">
            <label className="text-[9px] font-black text-slate-500 uppercase tracking-widest mb-1.5 block">
              <Gamepad2 size={10} className="inline mr-1" /> Patrones de victoria
            </label>
            <div className="flex flex-wrap gap-1.5">
              {[
                { id: 'line', label: '📏 Línea' },
                { id: 'cuadrito', label: '🟫 Cuadrito 2x2' },
                { id: 'pocito', label: '🧿 El Pocito' },
                { id: 'esquinas', label: '🔲 4 Esquinas' },
                { id: 'cruz', label: '✝️ La Cruz' },
                { id: 'full_board', label: '🏆 Full Board' },
              ].map(p => (
                <button
                  key={p.id}
                  onClick={() => togglePattern(p.id)}
                  className={`px-3 py-1.5 rounded-full text-[9px] font-black transition-all ${
                    winPatterns.includes(p.id)
                      ? 'bg-purple-600 text-white border border-purple-400'
                      : 'bg-slate-800 text-slate-500 border border-white/5 hover:border-purple-500/20'
                  }`}
                >
                  {p.label}
                </button>
              ))}
            </div>
          </div>

          {/* Visibility + Password */}
          <div className="mb-5">
            <label className="text-[9px] font-black text-slate-500 uppercase tracking-widest mb-1.5 block">
              👁️ Visibilidad
            </label>
            <div className="flex gap-1.5 mb-2">
              {([
                { id: 'public' as const, label: '🌍 Pública' },
                { id: 'friends' as const, label: '👥 Amigos' },
                { id: 'private' as const, label: '🔒 Privada' },
              ]).map(v => (
                <button
                  key={v.id}
                  onClick={() => setVisibility(v.id)}
                  className={`flex-1 py-2 rounded-lg text-[10px] font-black transition-all ${
                    visibility === v.id
                      ? 'bg-slate-600 text-white border border-slate-400'
                      : 'bg-slate-800 text-slate-400 border border-white/5 hover:border-slate-500/20'
                  }`}
                >
                  {v.label}
                </button>
              ))}
            </div>
            {visibility === 'private' && (
              <div className="flex items-center gap-2 bg-slate-800/60 rounded-xl p-2.5 border border-amber-500/20">
                <Lock size={12} className="text-amber-400 shrink-0" />
                <input
                  type="text"
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  placeholder="Contraseña de la sala"
                  className="flex-1 bg-transparent text-white text-xs font-bold placeholder:text-slate-600 focus:outline-none"
                />
              </div>
            )}
          </div>

          {/* Create Button */}
          <button
            onClick={handleCreate}
            disabled={creating}
            className="w-full py-3.5 rounded-2xl font-black uppercase text-sm tracking-widest bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-400 hover:to-orange-400 text-white border-none shadow-lg shadow-amber-500/20 active:scale-95 transition-all disabled:opacity-60 flex items-center justify-center gap-2"
          >
            {creating ? 'Creando...' : `🎴 Abrir Sala — ${buyIn} FRJ buy-in`}
          </button>
        </div>
      </div>
    </div>
  );
}
