"use client";
import React, { useState, useRef, useEffect, useCallback } from "react";
import type { MochilaTab } from "@/types/inventory";

interface MochilaFloatingProps {
  onOpenSection: (section: MochilaTab) => void;
}

const SECTIONS: { id: MochilaTab; emoji: string; label: string; glow: string }[] = [
  { id: 'cartas', emoji: '🃏', label: 'Cartas', glow: 'hover:shadow-[0_0_12px_rgba(99,102,241,0.6)]' },
  { id: 'tablas', emoji: '📋', label: 'Tablas', glow: 'hover:shadow-[0_0_12px_rgba(16,185,129,0.6)]' },
];

const MochilaFloating: React.FC<MochilaFloatingProps> = ({ onOpenSection }) => {
  const [open, setOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const handleClickOutside = useCallback((e: MouseEvent | TouchEvent) => {
    if (!containerRef.current) return;
    if (!containerRef.current.contains(e.target as Node)) setOpen(false);
  }, []);

  useEffect(() => {
    if (!open) return;
    document.addEventListener("mousedown", handleClickOutside);
    document.addEventListener("touchstart", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("touchstart", handleClickOutside);
    };
  }, [open, handleClickOutside]);

  const handleSectionClick = (section: MochilaTab) => {
    onOpenSection(section);
    setOpen(false);
  };

  return (
    <div ref={containerRef} className="fixed bottom-20 right-4 z-40 flex flex-col items-center gap-1.5">
      {/* Section buttons — slide up when open */}
      <div
        className={[
          "flex flex-col gap-1.5 transition-all duration-200 origin-bottom",
          open
            ? "opacity-100 scale-100 translate-y-0 pointer-events-auto"
            : "opacity-0 scale-75 translate-y-2 pointer-events-none",
        ].join(" ")}
      >
        {SECTIONS.map((s) => (
          <button
            key={s.id}
            onClick={() => handleSectionClick(s.id)}
            title={s.label}
            className={[
              "w-11 h-11 rounded-full bg-[#1C1C35]/95 border border-white/15 backdrop-blur-sm",
              "flex items-center justify-center text-lg",
              "hover:bg-[#2A2A4A] hover:border-white/25 hover:scale-110 active:scale-95",
              "transition-all shadow-lg shadow-black/40",
              s.glow,
            ].join(" ")}
          >
            {s.emoji}
          </button>
        ))}
      </div>

      {/* Main 2.5D backpack toggle */}
      <button
        onClick={() => setOpen((prev) => !prev)}
        className={[
          "w-13 h-13 rounded-full flex items-center justify-center text-2xl",
          "transition-all duration-200 shadow-lg shadow-black/50",
          // 2.5D gradient rosa-cyan
          "bg-gradient-to-br from-[#E4007C] via-[#9B2FE8] to-[#00B4D8]",
          "border-2 backdrop-blur-sm",
          // Jiggle on hover via scale + rotate
          "hover:scale-110 hover:rotate-[-6deg] active:scale-95",
          open
            ? "border-white/40 shadow-[0_0_20px_rgba(228,0,124,0.6),0_0_40px_rgba(0,180,216,0.3)] rotate-45"
            : "border-white/20 rotate-0",
        ].join(" ")}
        title="Mochila"
        style={{ width: '52px', height: '52px' }}
      >
        🎒
      </button>
    </div>
  );
};

export { MochilaFloating };
export default MochilaFloating;
