"use client";
import { useState, useEffect, useRef } from "react";
import { Info } from "lucide-react";

/**
 * Fila canonica de beneficio — unico renderizador.
 * Usa icono, label y tooltip opcional.
 */
export default function BenefitRow({
  icon,
  label,
  tooltip,
}: {
  icon: string;
  label: string;
  tooltip?: string;
}) {
  const [showTip, setShowTip] = useState(false);
  const tipRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!showTip) return;
    const handler = (e: MouseEvent) => {
      if (tipRef.current && !tipRef.current.contains(e.target as Node)) {
        setShowTip(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, [showTip]);

  return (
    <div className="flex items-center gap-2 bg-white/5 rounded-lg px-3 py-2 min-h-[44px]">
      <span className="text-sm leading-none shrink-0">{icon}</span>
      <span className="text-xs text-gray-300 font-medium flex-1 leading-tight">
        {label}
      </span>
      {tooltip && (
        <div ref={tipRef} className="relative shrink-0">
          <button
            aria-label={`Informacion sobre: ${label}`}
            onClick={() => setShowTip((v) => !v)}
            className="flex items-center justify-center min-w-[44px] min-h-[44px] -mr-2 text-gray-500 hover:text-gray-300 transition-colors"
          >
            <Info size={13} />
          </button>
          {showTip && (
            <div
              className="absolute right-0 bottom-full mb-2 w-52 rounded-lg p-2.5 text-xs text-gray-200 leading-snug z-50 shadow-xl"
              style={{ background: "#1a1a2e", border: "1px solid rgba(255,255,255,0.12)" }}
            >
              {tooltip}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
