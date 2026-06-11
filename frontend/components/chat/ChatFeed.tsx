"use client";

import React, { useState, useRef, useEffect, useCallback } from "react";
import { MessageCircle, X, Send, ChevronUp, ChevronDown } from "lucide-react";

// ── Types ─────────────────────────────────────────────────────────────────────

export interface ChatMessage {
  id: string;
  playerId: string;
  username: string;
  text: string;
  vipTier?: string | null;
  nature?: string | null;
  stickerId?: string | null;
  megaphone?: boolean;
  timestamp: number;
}

interface ChatFeedProps {
  messages: ChatMessage[];
  send: ((msg: any) => void) | null;
  phase: "lobby" | "countdown" | "playing" | "result";
  playMode?: "manual" | "auto";
  collapsed: boolean;
  onToggleCollapse: () => void;
}

// ── Helpers ────────────────────────────────────────────────────────────────────

function relativeTime(ts: number): string {
  const diff = Math.floor((Date.now() - ts * 1000) / 1000);
  if (diff < 5) return "ahora";
  if (diff < 60) return `${diff}s`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m`;
  return `${Math.floor(diff / 3600)}h`;
}

function usernameClass(vipTier?: string | null): string {
  switch (vipTier) {
    case "axolite":
      return "text-transparent bg-clip-text bg-gradient-to-r from-pink-400 to-purple-400 font-black";
    case "dorado":
      return "text-amber-400 font-bold";
    case "coral":
      return "text-cyan-400";
    default:
      return "text-slate-300";
  }
}

// ── Component ──────────────────────────────────────────────────────────────────

export default function ChatFeed({
  messages,
  send,
  phase,
  playMode = "manual",
  collapsed,
  onToggleCollapse,
}: ChatFeedProps) {
  const [input, setInput] = useState("");
  const feedRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    if (feedRef.current && !collapsed) {
      feedRef.current.scrollTop = feedRef.current.scrollHeight;
    }
  }, [messages, collapsed]);

  const handleSend = useCallback(() => {
    const text = input.trim();
    if (!text || !send) return;
    send({
      action: "chat_message",
      data: { text, is_reaction: false, sticker_id: null, megaphone: false },
    });
    setInput("");
    inputRef.current?.focus();
  }, [input, send]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const chatDisabled = phase === "playing" && playMode === "manual";
  const showInput = (phase === "lobby" || phase === "result" || (phase === "playing" && playMode === "auto"));

  // Unread count
  const unread = messages.length;

  return (
    <div className="fixed bottom-4 right-4 z-40">
      {/* Collapsed state */}
      {collapsed ? (
        <button
          onClick={onToggleCollapse}
          className="relative w-12 h-12 rounded-full bg-indigo-950/80 border border-indigo-500/30
                     text-white flex items-center justify-center shadow-[0_0_12px_rgba(99,102,241,0.2)]
                     hover:scale-110 active:scale-95 transition-all"
        >
          <MessageCircle size={20} />
          {unread > 0 && (
            <span className="absolute -top-1 -right-1 w-5 h-5 rounded-full bg-[var(--brand-hot)]
                             text-white text-[9px] font-black flex items-center justify-center">
              {unread > 99 ? "99" : unread}
            </span>
          )}
        </button>
      ) : (
        /* Expanded state */
        <div className="w-72 max-h-[320px] rounded-2xl bg-slate-950/80 backdrop-blur-md border border-white/10
                        shadow-[0_8px_32px_rgba(0,0,0,0.4)] flex flex-col overflow-hidden">
          {/* Header */}
          <div className="flex items-center justify-between px-3 py-2 border-b border-white/5">
            <span className="text-[9px] font-black uppercase tracking-widest text-slate-400">
              Chat de Sala
            </span>
            <button
              onClick={onToggleCollapse}
              className="text-slate-500 hover:text-slate-300 transition-colors"
            >
              <X size={14} />
            </button>
          </div>

          {/* Messages feed */}
          <div
            ref={feedRef}
            className="flex-1 overflow-y-auto px-3 py-2 space-y-2 scrollbar-hide"
            style={{ maxHeight: 200 }}
          >
            {messages.length === 0 && (
              <p className="text-[9px] text-slate-600 text-center py-4 italic">
                Sin mensajes aún. ¡Sé el primero en saludar!
              </p>
            )}
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`text-xs leading-relaxed ${
                  msg.megaphone
                    ? "bg-amber-950/20 border-l-2 border-amber-500/60 pl-2 pr-1 py-1 rounded-r"
                    : ""
                }`}
              >
                {msg.stickerId ? (
                  <span className="text-3xl leading-none block text-center py-1">
                    {msg.stickerId}
                  </span>
                ) : (
                  <>
                    <span className="flex items-center gap-1.5 flex-wrap">
                      <span className={`text-[10px] font-black ${usernameClass(msg.vipTier)}`}>
                        {msg.username}
                      </span>
                      <span className="text-[8px] text-slate-600">{relativeTime(msg.timestamp)}</span>
                      {msg.megaphone && (
                        <span className="text-[8px] text-amber-400 font-black">📢 Megáfono</span>
                      )}
                    </span>
                    <p className="text-slate-300 mt-0.5 break-words">{msg.text}</p>
                  </>
                )}
              </div>
            ))}
          </div>

          {/* Input area */}
          {chatDisabled ? (
            <div className="px-3 py-2 border-t border-white/5 bg-slate-900/60">
              <p className="text-[9px] text-slate-500 text-center italic">
                Chat desactivado durante el juego. Usa la Rueda de Reacciones 🦎
              </p>
            </div>
          ) : showInput && send ? (
            <div className="flex items-center gap-1.5 px-2 py-1.5 border-t border-white/5 bg-slate-900/60">
              <input
                ref={inputRef}
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Escribe un mensaje..."
                maxLength={280}
                className="flex-1 bg-slate-800/60 border border-white/5 rounded-lg px-2.5 py-1.5
                           text-xs text-white placeholder-slate-500 outline-none
                           focus:border-indigo-500/40 transition-colors"
              />
              <button
                onClick={handleSend}
                disabled={!input.trim()}
                className="w-8 h-8 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-700
                           text-white flex items-center justify-center transition-colors"
              >
                <Send size={12} />
              </button>
            </div>
          ) : null}
        </div>
      )}
    </div>
  );
}
