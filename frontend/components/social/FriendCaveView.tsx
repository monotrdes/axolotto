"use client";

import { useState, useEffect } from "react";
import { useSocial, type FriendInfo, type FriendCave } from "@/hooks/useSocial";

interface FriendCaveViewProps {
  friend: FriendInfo;
  token: string | null;
  onBack: () => void;
  onLike: (friendId: string) => void;
  onNavigate?: (tab: string) => void;
}

export default function FriendCaveView({
  friend,
  token,
  onBack,
  onLike,
  onNavigate,
}: FriendCaveViewProps) {
  const { getFriendCave, sendLike } = useSocial(token);
  const [cave, setCave] = useState<FriendCave | null>(null);
  const [likeSent, setLikeSent] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      const caveData = await getFriendCave(friend.friend_id);
      setCave(caveData);
      setLoading(false);
    };
    load();
  }, [friend.friend_id, getFriendCave]);

  const handleLike = async () => {
    try {
      await sendLike(friend.friend_id);
      setLikeSent(true);
      onLike(friend.friend_id);
      setTimeout(() => setLikeSent(false), 2000);
    } catch (e: any) {
      // Already liked today — silently ignore
      console.log("Like failed:", e?.response?.data?.detail);
    }
  };

  const handleInvite = () => {
    // Navigate to play and suggest creating a room
    onNavigate?.("jugar");
  };

  if (loading) {
    return (
      <div className="h-screen w-full max-w-[430px] mx-auto bg-[#0a0a0f] flex items-center justify-center">
        <div className="text-center">
          <span className="text-4xl animate-bounce block mb-3">🦎</span>
          <p className="text-slate-400 text-sm font-bold">Visitando la cueva…</p>
        </div>
      </div>
    );
  }

  if (!cave) {
    return (
      <div className="h-screen w-full max-w-[430px] mx-auto bg-[#0a0a0f] flex items-center justify-center">
        <div className="text-center">
          <span className="text-4xl block mb-3">🚫</span>
          <p className="text-slate-400 text-sm font-bold">No se pudo cargar la cueva</p>
          <button
            onClick={onBack}
            className="mt-4 px-4 py-2 rounded-xl bg-slate-800 text-white text-sm font-bold hover:bg-slate-700 transition-colors"
          >
            ← Volver
          </button>
        </div>
      </div>
    );
  }

  const decorations = (() => {
    try {
      return JSON.parse(cave.cave_decorations || "{}");
    } catch {
      return {};
    }
  })();

  const decoCount = Object.keys(decorations).length;

  return (
    <div className="h-screen w-full max-w-[430px] mx-auto bg-[#0a0a0f] flex flex-col overflow-hidden">
      {/* Header */}
      <div className="shrink-0 px-4 pt-6 pb-3 border-b border-white/5">
        <div className="flex items-center gap-3">
          <button
            onClick={onBack}
            className="w-8 h-8 rounded-xl bg-slate-800 flex items-center justify-center text-sm hover:bg-slate-700 transition-colors shrink-0"
          >
            ←
          </button>
          <div>
            <h2 className="text-sm font-black text-white flex items-center gap-1.5">
              {cave.nickname || "Jugador"}
              {cave.vip_tier && (
                <span>{cave.vip_tier === "axolite" ? "👑" : cave.vip_tier === "dorado" ? "💛" : "🪸"}</span>
              )}
            </h2>
            <p className="text-[9px] text-slate-500">
              {cave.cave_name || "Cenote"} · Nivel {cave.cave_level}
              {cave.is_online ? " · 🟢 En línea" : ""}
            </p>
          </div>
        </div>
      </div>

      {/* Cave preview */}
      <div className="flex-1 flex flex-col items-center justify-center p-6 relative overflow-hidden">
        {/* Background gradient */}
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(20,83,45,0.2)_0%,transparent_70%)]" />

        {/* Cave level display */}
        <div className="relative z-10 text-center">
          <div className="text-7xl mb-4">
            {cave.cave_level <= 1 ? "🪺" : cave.cave_level <= 3 ? "🪨" : cave.cave_level <= 5 ? "💎" : cave.cave_level <= 7 ? "✨" : "👑"}
          </div>
          <h3 className="text-xl font-black text-white mb-1">
            {cave.cave_name || "Cenote Misterioso"}
          </h3>
          <p className="text-slate-400 text-sm mb-4">
            Nivel {cave.cave_level} · {decoCount} decoraciones
          </p>
        </div>

        {/* Decoration count bar */}
        <div className="relative z-10 flex gap-3 mb-6">
          <div className="bg-slate-800/60 rounded-xl px-4 py-2 text-center border border-white/5">
            <span className="text-xs font-black text-teal-400">🪸</span>
            <p className="text-[8px] text-slate-500">{decoCount} decor</p>
          </div>
          <div className="bg-slate-800/60 rounded-xl px-4 py-2 text-center border border-white/5">
            <span className="text-xs font-black text-teal-400">🪺</span>
            <p className="text-[8px] text-slate-500">Nv. {cave.cave_level}</p>
          </div>
          <div className="bg-slate-800/60 rounded-xl px-4 py-2 text-center border border-white/5">
            <span className="text-xs font-black text-teal-400">{cave.is_online ? "🟢" : "⚫"}</span>
            <p className="text-[8px] text-slate-500">{cave.is_online ? "Online" : "Offline"}</p>
          </div>
        </div>

        {/* Decorations list if any */}
        {decoCount > 0 && (
          <div className="relative z-10 w-full max-w-[280px] mb-4">
            <h4 className="text-[9px] font-black text-slate-500 uppercase tracking-wider mb-2 text-center">
              Decoraciones
            </h4>
            <div className="flex flex-wrap justify-center gap-2">
              {Object.keys(decorations).slice(0, 6).map((decoId) => (
                <div
                  key={decoId}
                  className="w-10 h-10 rounded-xl bg-slate-800/60 border border-white/5 flex items-center justify-center"
                >
                  <span className="text-lg">🪸</span>
                </div>
              ))}
              {decoCount > 6 && (
                <div className="w-10 h-10 rounded-xl bg-slate-800/60 border border-white/5 flex items-center justify-center">
                  <span className="text-[9px] text-slate-500">+{decoCount - 6}</span>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Action buttons */}
      <div className="shrink-0 border-t border-white/5 px-4 py-3 space-y-2">
        <button
          onClick={handleLike}
          disabled={likeSent}
          className={`w-full py-3 rounded-2xl font-black text-xs uppercase tracking-wider transition-all active:scale-95 ${
            likeSent
              ? "bg-pink-900/30 border border-pink-500/20 text-pink-400"
              : "bg-gradient-to-r from-pink-600 to-rose-600 text-white shadow-lg shadow-pink-500/20 hover:from-pink-500 hover:to-rose-500"
          }`}
        >
          {likeSent ? "❤️ ¡Like enviado!" : "❤️ Dar Like (+1 FRJ ambos)"}
        </button>

        <button
          onClick={handleInvite}
          className="w-full py-3 rounded-2xl bg-teal-900/40 border border-teal-500/20 text-teal-300 font-black text-xs uppercase tracking-wider hover:bg-teal-800/40 transition-colors"
        >
          🎲 Invitar a Jugar
        </button>
      </div>
    </div>
  );
}
