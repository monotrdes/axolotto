"use client";

import { useState, useEffect, useCallback } from "react";
import { useSocial, type FriendInfo, type PlayerResult } from "@/hooks/useSocial";
import { useReferrals } from "@/hooks/useReferrals";
import FriendCaveView from "./FriendCaveView";

interface AmigosPageProps {
  userId: string;
  token: string | null;
  onNavigate?: (tab: string) => void;
  /** Visita directa: burbuja 👁 de una trajinerita del embarcadero (mundo papel). */
  visitFriendId?: string | null;
  /** Avisar que la visita directa ya se atendió (para limpiar el estado arriba). */
  onVisitHandled?: () => void;
}

export default function AmigosPage({
  userId,
  token,
  onNavigate,
  visitFriendId,
  onVisitHandled,
}: AmigosPageProps) {
  const {
    friends,
    pendingRequests,
    sentRequests,
    loading,
    fetchFriends,
    fetchPendingRequests,
    fetchSentRequests,
    sendFriendRequest,
    acceptFriendRequest,
    rejectFriendRequest,
    removeFriend,
    searchPlayers,
    getRecentPlayers,
    getSuggestions,
    sendLike,
    visitCave,
    blockUser,
  } = useSocial(token);

  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<PlayerResult[]>([]);
  const [searching, setSearching] = useState(false);
  const [recentPlayers, setRecentPlayers] = useState<PlayerResult[]>([]);
  const [suggestions, setSuggestions] = useState<PlayerResult[]>([]);
  const { fetchCode, fetchDashboard, dashboard: refDashboard } = useReferrals(token);
  const [referralCode, setReferralCode] = useState<string | null>(null);
  const [shareSheetOpen, setShareSheetOpen] = useState(false);

  const [activeTab, setActiveTab] = useState<"friends" | "pending" | "discover" | "referidos">("friends");
  const [visitingFriend, setVisitingFriend] = useState<FriendInfo | null>(null);
  const [toastMsg, setToastMsg] = useState<string | null>(null);

  const toast = useCallback((msg: string) => {
    setToastMsg(msg);
    setTimeout(() => setToastMsg(null), 2500);
  }, []);

  // Load initial data
  useEffect(() => {
    if (!token) return;
    fetchFriends();
    fetchPendingRequests();
    fetchSentRequests();
    getRecentPlayers().then(setRecentPlayers);
    getSuggestions().then(setSuggestions);
    fetchCode().then((data) => {
      if (data) setReferralCode(data.code);
    });
    fetchDashboard();
  }, [token]);

  // Debounced search
  useEffect(() => {
    if (searchQuery.length < 2) {
      setSearchResults([]);
      return;
    }
    const timer = setTimeout(async () => {
      setSearching(true);
      const results = await searchPlayers(searchQuery);
      setSearchResults(results);
      setSearching(false);
    }, 400);
    return () => clearTimeout(timer);
  }, [searchQuery, searchPlayers]);

  const handleSendRequest = async (targetUserId: string) => {
    try {
      await sendFriendRequest(targetUserId);
      toast("¡Solicitud enviada! 🦎");
      await fetchSentRequests();
    } catch (e: any) {
      toast(e.response?.data?.detail || "Error al enviar solicitud");
    }
  };

  const handleAccept = async (requestId: number) => {
    try {
      await acceptFriendRequest(requestId);
      toast("¡Ahora son amigos! 🎉");
    } catch (e: any) {
      toast(e.response?.data?.detail || "Error al aceptar");
    }
  };

  const handleReject = async (requestId: number) => {
    try {
      await rejectFriendRequest(requestId);
      toast("Solicitud rechazada");
    } catch (e: any) {
      toast(e.response?.data?.detail || "Error al rechazar");
    }
  };

  const handleLike = async (friendId: string) => {
    try {
      const res = await sendLike(friendId);
      toast(res.message || "❤️ Like enviado");
      fetchFriends();
    } catch (e: any) {
      toast(e.response?.data?.detail || "Error al dar like");
    }
  };

  const handleVisit = async (friend: FriendInfo) => {
    const cave = await visitCave(friend.friend_id);
    if (cave) {
      setVisitingFriend(friend);
    }
  };

  // Visita directa desde el embarcadero del mundo (burbuja 👁 de la trajinerita).
  useEffect(() => {
    if (!visitFriendId || !token) return;
    let cancelled = false;
    (async () => {
      const list = friends.length > 0 ? friends : await fetchFriends();
      const amigo = list.find((f) => f.friend_id === visitFriendId);
      if (cancelled) return;
      if (amigo) await handleVisit(amigo);
      if (!cancelled) onVisitHandled?.();
    })();
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [visitFriendId, token]);

  const handleRemoveFriend = async (relationId: number, name: string) => {
    if (!window.confirm(`¿Eliminar a ${name || "este amigo"} de tu lista?`)) return;
    try {
      await removeFriend(relationId);
      toast("Amigo eliminado");
    } catch (e: any) {
      toast(e.response?.data?.detail || "Error al eliminar");
    }
  };

  const handleShareCode = async () => {
    if (!referralCode) {
      const data = await fetchCode();
      if (data) setReferralCode(data.code);
    }
    setShareSheetOpen(true);
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text).then(() => toast("¡Link copiado! 📋"));
  };

  // ── Visiting a friend's cave ──
  if (visitingFriend) {
    return (
      <FriendCaveView
        friend={visitingFriend}
        token={token}
        onBack={() => setVisitingFriend(null)}
        onLike={handleLike}
        onNavigate={onNavigate}
      />
    );
  }

  return (
    <div className="h-screen w-full max-w-[430px] mx-auto bg-[#0a0a0f] flex flex-col overflow-hidden">
      {/* Header */}
      <div className="shrink-0 px-4 pt-6 pb-3 border-b border-white/5">
        <div className="flex items-center justify-between">
          <h1 className="text-lg font-black text-white">👥 Amigos</h1>
          <span className="text-[10px] text-slate-500 font-bold">
            {friends.length}/100
          </span>
        </div>

        {/* Search bar */}
        <div className="mt-3 relative">
          <input
            type="text"
            placeholder="Buscar jugador por nickname…"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full px-4 py-2.5 rounded-xl bg-slate-800/60 border border-white/10 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-teal-500/40 transition-colors"
          />
          {searching && (
            <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-slate-500 animate-pulse">
              🔍
            </span>
          )}
        </div>

        {/* Tabs */}
        <div className="flex gap-1 mt-3 bg-slate-800/40 rounded-xl p-1">
          {([
            ["friends", "Amigos", friends.length],
            ["pending", "Solicitudes", pendingRequests.length],
            ["discover", "Descubrir", null],
            ["referidos", "Referidos", refDashboard?.active_referrals ?? null],
          ] as const).map(([key, label, count]) => (
            <button
              key={key}
              onClick={() => setActiveTab(key)}
              className={`flex-1 py-2 rounded-lg text-[10px] font-bold transition-all ${
                activeTab === key
                  ? "bg-teal-600 text-white shadow-lg"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              {label}
              {count !== null && count > 0 && (
                <span className="ml-1 px-1.5 py-0.5 rounded-full bg-white/20 text-[8px]">
                  {count}
                </span>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto px-4 py-3">
        {/* ── Friends Tab ── */}
        {activeTab === "friends" && (
          <>
            {/* Search results */}
            {searchQuery.length >= 2 && (
              <div className="mb-4">
                <h3 className="text-[9px] font-black text-slate-500 uppercase tracking-wider mb-2">
                  Resultados ({searchResults.length})
                </h3>
                {searchResults.length === 0 ? (
                  <p className="text-[10px] text-slate-600 text-center py-4">
                    Sin resultados para &quot;{searchQuery}&quot;
                  </p>
                ) : (
                  <div className="space-y-1.5">
                    {searchResults.map((player) => (
                      <PlayerRow
                        key={player.user_id}
                        player={player}
                        onAdd={handleSendRequest}
                      />
                    ))}
                  </div>
                )}
              </div>
            )}

            {!searchQuery && (
              <>
                {/* Friends list */}
                {friends.length === 0 ? (
                  <div className="text-center py-12">
                    <span className="text-5xl block mb-4">🦎</span>
                    <p className="text-slate-400 font-bold text-sm mb-1">
                      Aún no tienes amigos
                    </p>
                    <p className="text-slate-600 text-[10px] max-w-[240px] mx-auto">
                      Busca jugadores por nickname o juega en salas públicas para conocer gente.
                    </p>
                  </div>
                ) : (
                  <div className="space-y-1">
                    {friends.map((f) => (
                      <FriendRow
                        key={f.relation_id}
                        friend={f}
                        onLike={() => handleLike(f.friend_id)}
                        onVisit={() => handleVisit(f)}
                        onRemove={() => handleRemoveFriend(f.relation_id, f.nickname || "")}
                      />
                    ))}
                  </div>
                )}
              </>
            )}
          </>
        )}

        {/* ── Pending Tab ── */}
        {activeTab === "pending" && (
          <div className="space-y-4">
            {/* Incoming */}
            <div>
              <h3 className="text-[9px] font-black text-slate-500 uppercase tracking-wider mb-2">
                Recibidas ({pendingRequests.length})
              </h3>
              {pendingRequests.length === 0 ? (
                <p className="text-[10px] text-slate-600 text-center py-4">
                  Sin solicitudes pendientes
                </p>
              ) : (
                <div className="space-y-2">
                  {pendingRequests.map((req) => (
                    <div
                      key={req.id}
                      className="flex items-center gap-3 p-3 rounded-xl bg-slate-800/40 border border-white/5"
                    >
                      <div className="w-9 h-9 rounded-full bg-teal-800 flex items-center justify-center text-sm shrink-0">
                        {req.from_avatar_url ? (
                          <img src={req.from_avatar_url} className="w-full h-full rounded-full" alt="" />
                        ) : (
                          req.from_nickname?.charAt(0).toUpperCase() || "?"
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-xs font-bold text-white truncate">
                          {req.from_nickname || "Jugador"}
                        </p>
                        <p className="text-[9px] text-slate-500">Quiere ser tu amigo</p>
                      </div>
                      <button
                        onClick={() => handleAccept(req.id)}
                        className="px-3 py-1.5 rounded-lg bg-teal-600 text-white text-[10px] font-bold hover:bg-teal-500 transition-colors"
                      >
                        Aceptar
                      </button>
                      <button
                        onClick={() => handleReject(req.id)}
                        className="px-3 py-1.5 rounded-lg bg-slate-700 text-slate-300 text-[10px] font-bold hover:bg-slate-600 transition-colors"
                      >
                        Rechazar
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Sent */}
            {sentRequests.length > 0 && (
              <div>
                <h3 className="text-[9px] font-black text-slate-500 uppercase tracking-wider mb-2">
                  Enviadas ({sentRequests.length})
                </h3>
                <div className="space-y-1.5">
                  {sentRequests.map((req) => (
                    <div
                      key={req.id}
                      className="flex items-center gap-3 p-2.5 rounded-xl bg-slate-800/20 border border-white/5"
                    >
                      <div className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center text-xs shrink-0">
                        {req.to_nickname?.charAt(0).toUpperCase() || "?"}
                      </div>
                      <span className="text-xs text-slate-400 truncate flex-1">
                        {req.to_nickname || "Jugador"}
                      </span>
                      <span className="text-[9px] text-slate-600">Pendiente…</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* ── Discover Tab ── */}
        {activeTab === "discover" && (
          <div className="space-y-4">
            {/* Recent Players */}
            {recentPlayers.length > 0 && (
              <div>
                <h3 className="text-[9px] font-black text-slate-500 uppercase tracking-wider mb-2">
                  Jugadores Recientes
                </h3>
                <div className="space-y-1.5">
                  {recentPlayers.slice(0, 5).map((player) => (
                    <PlayerRow
                      key={player.user_id}
                      player={player}
                      onAdd={handleSendRequest}
                    />
                  ))}
                </div>
              </div>
            )}

            {/* Suggestions */}
            {suggestions.length > 0 && (
              <div>
                <h3 className="text-[9px] font-black text-slate-500 uppercase tracking-wider mb-2">
                  Quizás Conozcas
                </h3>
                <div className="space-y-1.5">
                  {suggestions.map((player) => (
                    <PlayerRow
                      key={player.user_id}
                      player={player}
                      onAdd={handleSendRequest}
                      mutualInfo={
                        player.mutual_friends
                          ? `${player.mutual_friends} amigo${player.mutual_friends > 1 ? "s" : ""} en común`
                          : undefined
                      }
                    />
                  ))}
                </div>
              </div>
            )}

            {recentPlayers.length === 0 && suggestions.length === 0 && (
              <div className="text-center py-12">
                <span className="text-5xl block mb-4">🔍</span>
                <p className="text-slate-400 font-bold text-sm mb-1">
                  Nada por descubrir aún
                </p>
                <p className="text-slate-600 text-[10px] max-w-[240px] mx-auto">
                  Juega en salas públicas para que aparezcan jugadores aquí.
                </p>
              </div>
            )}
          </div>
        )}

        {/* ── Referidos Tab ── */}
        {activeTab === "referidos" && (
          <div className="space-y-4">
            {/* Share code card */}
            <div className="bg-gradient-to-br from-teal-900/30 to-emerald-900/20 border-2 border-teal-500/30 rounded-2xl p-4 text-center">
              <h3 className="text-[10px] font-black text-teal-300 uppercase tracking-wider mb-2">
                💌 Tu Código de Referido
              </h3>
              <p className="text-2xl font-black text-white font-mono tracking-wider mb-3">
                {referralCode || "---"}
              </p>
              <div className="flex gap-2">
                <button
                  onClick={handleShareCode}
                  className="flex-1 py-2.5 rounded-xl bg-teal-600 text-white font-black text-[10px] uppercase tracking-wider hover:bg-teal-500 active:scale-95 transition-all"
                >
                  📤 Compartir Código
                </button>
                <button
                  onClick={() =>
                    copyToClipboard(`https://axolot.to/join/${referralCode}`)
                  }
                  className="py-2.5 px-3 rounded-xl bg-slate-800 border border-white/10 text-slate-400 font-bold text-xs hover:text-white hover:border-white/20 transition-all"
                >
                  📋
                </button>
              </div>
            </div>

            {/* Stats */}
            {refDashboard && (
              <div className="grid grid-cols-3 gap-2">
                <div className="bg-slate-800/40 rounded-xl p-3 text-center border border-white/5">
                  <p className="text-xl font-black text-teal-400">
                    {refDashboard.total_uses}
                  </p>
                  <p className="text-[8px] text-slate-500 font-bold uppercase tracking-wider">
                    Total
                  </p>
                </div>
                <div className="bg-slate-800/40 rounded-xl p-3 text-center border border-white/5">
                  <p className="text-xl font-black text-emerald-400">
                    {refDashboard.active_referrals}
                  </p>
                  <p className="text-[8px] text-slate-500 font-bold uppercase tracking-wider">
                    Activos
                  </p>
                </div>
                <div className="bg-slate-800/40 rounded-xl p-3 text-center border border-white/5">
                  <p className="text-xl font-black text-amber-400">
                    {Math.floor((refDashboard.rewards_earned_frj || 0) / 10000)}
                  </p>
                  <p className="text-[8px] text-slate-500 font-bold uppercase tracking-wider">
                    FRJ ganados
                  </p>
                </div>
              </div>
            )}

            {/* Referred users list */}
            {refDashboard && refDashboard.referred_users.length > 0 && (
              <div>
                <h3 className="text-[9px] font-black text-slate-500 uppercase tracking-wider mb-2">
                  Personas que invitaste ({refDashboard.referred_users.length})
                </h3>
                <div className="space-y-1">
                  {refDashboard.referred_users.map((u) => (
                    <div
                      key={u.referred_id}
                      className="flex items-center gap-2 p-2.5 rounded-xl bg-slate-800/30 border border-white/5"
                    >
                      <span className="text-sm">
                        {u.status === "converted"
                          ? "💎"
                          : u.status === "d7_retained"
                          ? "⭐"
                          : u.status === "tutorial_done"
                          ? "🎓"
                          : "🌱"}
                      </span>
                      <span className="flex-1 text-xs text-white font-bold truncate">
                        {u.nickname || "Jugador"}
                      </span>
                      <span className="text-[9px] text-slate-500">
                        {u.status === "converted"
                          ? "Comprador"
                          : u.status === "d7_retained"
                          ? "7 días"
                          : u.status === "tutorial_done"
                          ? "Tutorial ✓"
                          : "Nuevo"}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {refDashboard && refDashboard.referred_users.length === 0 && (
              <div className="text-center py-8">
                <span className="text-5xl block mb-3">💌</span>
                <p className="text-slate-400 font-bold text-sm mb-1">
                  Aún no has invitado a nadie
                </p>
                <p className="text-slate-600 text-[10px] max-w-[240px] mx-auto">
                  Comparte tu código y gana recompensas cuando tus amigos jueguen.
                </p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Leaderboard mini */}
      {friends.length >= 2 && activeTab === "friends" && !searchQuery && (
        <div className="shrink-0 border-t border-white/5 px-4 py-3">
          <h3 className="text-[9px] font-black text-slate-500 uppercase tracking-wider mb-2">
            🏆 Top Amigos (Interacciones)
          </h3>
          <div className="space-y-1">
            {friends
              .slice()
              .sort((a, b) => b.interaction_count - a.interaction_count)
              .slice(0, 5)
              .map((f, i) => (
                <div
                  key={f.relation_id}
                  className="flex items-center gap-2 text-[10px]"
                >
                  <span className="w-4 text-center font-black text-slate-500">
                    {i === 0 ? "🥇" : i === 1 ? "🥈" : i === 2 ? "🥉" : `${i + 1}.`}
                  </span>
                  <span className="flex-1 text-white truncate font-bold">
                    {f.nickname || "Jugador"}
                  </span>
                  <span className="text-slate-500">
                    {f.interaction_count} ❤️
                  </span>
                </div>
              ))}
          </div>
        </div>
      )}

      {/* Share Code Sheet */}
      {shareSheetOpen && (
        <div
          className="fixed inset-0 z-[150] flex items-end justify-center bg-black/60"
          onClick={() => setShareSheetOpen(false)}
        >
          <div
            className="w-full max-w-[430px] bg-slate-900 rounded-t-3xl p-5 border-t border-slate-700"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex justify-center mb-3">
              <div className="w-10 h-1 rounded-full bg-slate-700" />
            </div>
            <h3 className="text-sm font-black text-white text-center mb-4">
              📤 Compartir Código
            </h3>

            {/* Code display */}
            <div className="bg-slate-800 rounded-2xl p-4 text-center mb-4 border border-white/5">
              <p className="text-[9px] text-slate-500 uppercase tracking-wider mb-1">
                Tu código
              </p>
              <p className="text-2xl font-black text-teal-400 font-mono tracking-widest">
                {referralCode}
              </p>
              <p className="text-[9px] text-slate-600 mt-1">
                axolot.to/join/{referralCode}
              </p>
            </div>

            {/* Share buttons */}
            <div className="space-y-2 mb-3">
              <button
                onClick={() =>
                  copyToClipboard(
                    `¡Juega Axolotto conmigo! 🦎 Usa mi código ${referralCode} y gana 50 FRJ 🎁 https://axolot.to/join/${referralCode}`
                  )
                }
                className="w-full py-3 rounded-xl bg-teal-600 text-white font-bold text-xs uppercase tracking-wider hover:bg-teal-500 active:scale-95 transition-all"
              >
                📋 Copiar Mensaje + Link
              </button>
              <button
                onClick={() =>
                  copyToClipboard(`https://axolot.to/join/${referralCode}`)
                }
                className="w-full py-3 rounded-xl bg-slate-800 border border-white/10 text-slate-300 font-bold text-xs uppercase tracking-wider hover:bg-slate-700 transition-all"
              >
                🔗 Solo Copiar Link
              </button>
            </div>

            <button
              onClick={() => setShareSheetOpen(false)}
              className="w-full py-2.5 rounded-xl bg-transparent text-slate-500 font-bold text-[10px] hover:text-white transition-colors"
            >
              Cerrar
            </button>
          </div>
        </div>
      )}

      {/* Toast */}
      {toastMsg && (
        <div className="fixed top-4 left-1/2 -translate-x-1/2 z-[200] px-4 py-2.5 rounded-full bg-teal-900/95 border border-teal-500/40 text-white text-xs font-bold shadow-xl backdrop-blur-sm animate-bounce">
          {toastMsg}
        </div>
      )}
    </div>
  );
}

// ── Sub-components ──────────────────────────────────────────────────────────

function FriendRow({
  friend,
  onLike,
  onVisit,
  onRemove,
}: {
  friend: FriendInfo;
  onLike: () => void;
  onVisit: () => void;
  onRemove: () => void;
}) {
  return (
    <div className="flex items-center gap-2.5 p-2.5 rounded-xl bg-slate-800/30 border border-white/5 hover:bg-slate-800/50 transition-colors group">
      {/* Avatar + online indicator */}
      <div className="relative shrink-0">
        <div className="w-9 h-9 rounded-full bg-teal-800 flex items-center justify-center text-sm">
          {friend.avatar_url ? (
            <img src={friend.avatar_url} className="w-full h-full rounded-full" alt="" />
          ) : (
            (friend.nickname || "?").charAt(0).toUpperCase()
          )}
        </div>
        <span
          className={`absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full border-2 border-slate-900 ${
            friend.is_online ? "bg-emerald-400" : "bg-slate-600"
          }`}
        />
      </div>

      {/* Info */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-1.5">
          <span className="text-xs font-bold text-white truncate">
            {friend.nickname || "Jugador"}
          </span>
          {friend.is_best_friend && (
            <span className="text-[8px]" title="Mejor Amigo">⭐</span>
          )}
          {friend.vip_tier && (
            <span className="text-[8px]">{friend.vip_tier === "axolite" ? "👑" : friend.vip_tier === "dorado" ? "💛" : "🪸"}</span>
          )}
        </div>
        <p className="text-[9px] text-slate-500">
          {friend.is_online ? "🟢 En línea" : "⚫ Desconectado"}{" "}
          · {friend.interaction_count} interacciones
        </p>
      </div>

      {/* Action buttons */}
      <div className="flex gap-1 shrink-0">
        <button
          onClick={onLike}
          className="w-8 h-8 rounded-lg bg-pink-900/30 border border-pink-500/20 text-pink-400 text-xs hover:bg-pink-800/40 transition-colors flex items-center justify-center"
        >
          ❤️
        </button>
        <button
          onClick={onVisit}
          className="w-8 h-8 rounded-lg bg-teal-900/30 border border-teal-500/20 text-teal-400 text-xs hover:bg-teal-800/40 transition-colors flex items-center justify-center"
        >
          👁
        </button>
        <button
          onClick={onRemove}
          className="w-8 h-8 rounded-lg bg-transparent border border-transparent text-slate-700 hover:text-red-400 hover:border-red-500/20 opacity-0 group-hover:opacity-100 transition-all flex items-center justify-center text-xs"
        >
          ✕
        </button>
      </div>
    </div>
  );
}

function PlayerRow({
  player,
  onAdd,
  mutualInfo,
}: {
  player: PlayerResult;
  onAdd: (userId: string) => void;
  mutualInfo?: string;
}) {
  const isAlreadyFriend = player.friendship_status === "active";
  const isPending = player.friendship_status === "pending";

  return (
    <div className="flex items-center gap-2.5 p-2.5 rounded-xl bg-slate-800/30 border border-white/5">
      <div className="w-9 h-9 rounded-full bg-slate-700 flex items-center justify-center text-sm shrink-0">
        {player.avatar_url ? (
          <img src={player.avatar_url} className="w-full h-full rounded-full" alt="" />
        ) : (
          (player.nickname || "?").charAt(0).toUpperCase()
        )}
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-1.5">
          <span className="text-xs font-bold text-white truncate">
            {player.nickname || "Jugador"}
          </span>
          {player.vip_tier && (
            <span className="text-[8px]">{player.vip_tier === "axolite" ? "👑" : player.vip_tier === "dorado" ? "💛" : "🪸"}</span>
          )}
        </div>
        <p className="text-[9px] text-slate-500">
          {mutualInfo || (player.cave_level ? `Cenote Nv.${player.cave_level}` : "Jugador de Axolotto")}
        </p>
      </div>
      {isAlreadyFriend ? (
        <span className="text-[9px] text-teal-400 font-bold bg-teal-950/40 px-2 py-1 rounded-lg">
          ✅ Amigos
        </span>
      ) : isPending ? (
        <span className="text-[9px] text-amber-400 font-bold bg-amber-950/40 px-2 py-1 rounded-lg">
          ⏳ Pendiente
        </span>
      ) : (
        <button
          onClick={() => onAdd(player.user_id)}
          className="px-3 py-1.5 rounded-lg bg-teal-600 text-white text-[10px] font-bold hover:bg-teal-500 transition-colors"
        >
          ➕ Agregar
        </button>
      )}
    </div>
  );
}
