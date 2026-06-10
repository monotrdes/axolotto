"use client";

import { useState } from "react";

type NavTab = "santuario" | "jugar" | "mercado" | "amigos" | "perfil";

interface Amigo {
  id: string;
  name: string;
  avatarEmoji?: string;
  isOnline?: boolean;
  isBestFriend?: boolean;
}

interface ZonaInferiorProps {
  amigos?: Amigo[];
  activeTab?: NavTab;
  // Called when user taps a nav tab
  onNavigate?: (tab: NavTab) => void;
  // Called when user taps action on a friend
  onLike?: (amigoId: string) => void;
  onInvite?: (amigoId: string) => void;
  onVisit?: (amigoId: string) => void;
}

const NAV_ITEMS: { tab: NavTab; icon: string; label: string }[] = [
  { tab: "santuario", icon: "🦎", label: "Santuario" },
  { tab: "jugar", icon: "🎲", label: "Jugar" },
  { tab: "amigos", icon: "👥", label: "Amigos" },
  { tab: "perfil", icon: "👤", label: "Perfil" },
];

export default function ZonaInferior({
  amigos = [],
  activeTab = "santuario",
  onNavigate,
  onLike,
  onInvite,
  onVisit,
}: ZonaInferiorProps) {
  const [expanded, setExpanded] = useState(false);
  const [showAllFriends, setShowAllFriends] = useState(false);

  const toggleExpand = () => setExpanded((prev) => !prev);

  const displayedFriends = showAllFriends ? amigos : amigos.slice(0, 4);

  return (
    <div className="shrink-0 border-t border-slate-700/60 bg-slate-900/95">
      {/* ── Expand handle ── */}
      <button
        onClick={toggleExpand}
        className="w-full flex items-center justify-center py-1 hover:bg-white/5 transition-colors"
        aria-label={expanded ? "Colapsar amigos" : "Expandir amigos"}
      >
        <span
          className={`text-[10px] text-slate-500 transition-transform duration-300 ${
            expanded ? "rotate-180" : ""
          }`}
        >
          {expanded ? "▲" : "▼"}
        </span>
        {!expanded && amigos.length > 0 && (
          <span className="text-[9px] text-slate-600 ml-1.5 font-bold">
            {amigos.length} amigo{amigos.length !== 1 ? "s" : ""}
            {amigos.filter((a) => a.isOnline).length > 0 && (
              <span className="text-emerald-500 ml-1">
                · {amigos.filter((a) => a.isOnline).length} online
              </span>
            )}
          </span>
        )}
      </button>

      {/* ── Expanded friends list ── */}
      {expanded && (
        <div className="overflow-hidden animate-in slide-in-from-bottom-2 duration-200">
          {displayedFriends.length === 0 ? (
            <p className="text-center text-[10px] text-slate-500 py-3">
              Sin amigos aún. ¡Invita a alguien con tu código de referido!
            </p>
          ) : (
            <>
              {displayedFriends.map((amigo) => (
                <div
                  key={amigo.id}
                  className="flex items-center gap-2 px-3 py-1.5 hover:bg-slate-800/40 transition-colors"
                >
                  {/* Avatar + online dot */}
                  <div className="relative shrink-0">
                    <div className="w-7 h-7 rounded-full bg-teal-800 flex items-center justify-center text-xs">
                      {amigo.avatarEmoji ?? amigo.name.charAt(0).toUpperCase()}
                    </div>
                    {amigo.isOnline !== undefined && (
                      <span
                        className={`absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full border border-slate-900 ${
                          amigo.isOnline ? "bg-emerald-400" : "bg-slate-600"
                        }`}
                      />
                    )}
                  </div>

                  {/* Name */}
                  <span className="flex-1 text-[11px] font-bold text-white truncate">
                    {amigo.name}
                    {amigo.isBestFriend && (
                      <span className="ml-1 text-[9px]" title="Mejor Amigo">
                        ⭐
                      </span>
                    )}
                  </span>

                  {/* Action buttons */}
                  <div className="flex gap-0.5 shrink-0">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onLike?.(amigo.id);
                      }}
                      className="text-[9px] px-2 py-0.5 rounded-full bg-pink-900/30 border border-pink-500/20 text-pink-400 hover:bg-pink-800/40 active:scale-90 transition-all"
                    >
                      ❤️
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onInvite?.(amigo.id);
                      }}
                      className="text-[9px] px-2 py-0.5 rounded-full bg-teal-900/30 border border-teal-500/20 text-teal-400 hover:bg-teal-800/40 active:scale-90 transition-all"
                    >
                      🎲
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onVisit?.(amigo.id);
                      }}
                      className="text-[9px] px-2 py-0.5 rounded-full bg-slate-800 border border-white/10 text-slate-400 hover:bg-slate-700 active:scale-90 transition-all"
                    >
                      👁
                    </button>
                  </div>
                </div>
              ))}

              {/* "Ver más" toggle when >4 friends */}
              {amigos.length > 4 && (
                <button
                  onClick={() => setShowAllFriends(!showAllFriends)}
                  className="w-full text-center py-1.5 text-[9px] text-teal-400 font-bold hover:text-teal-300 transition-colors"
                >
                  {showAllFriends
                    ? "▲ Mostrar menos"
                    : `▼ Ver todos (${amigos.length})`}
                </button>
              )}
            </>
          )}
        </div>
      )}

      {/* ── Nav bar (always visible) ── */}
      <div className="flex items-center border-t border-slate-700/60">
        {NAV_ITEMS.map(({ tab, icon, label }) => {
          const isActive = tab === activeTab;
          return (
            <button
              key={tab}
              onClick={() => onNavigate?.(tab)}
              className={`flex-1 flex flex-col items-center py-2.5 gap-0.5 ${
                isActive ? "text-white" : "text-slate-500"
              }`}
            >
              <span className="text-base leading-none">{icon}</span>
              <span className="text-[9px] leading-none font-bold">{label}</span>
              {isActive && (
                <span className="w-4 h-0.5 rounded-full bg-teal-400 mt-0.5" />
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}
